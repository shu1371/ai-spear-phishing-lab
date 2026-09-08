# -*- coding: utf-8 -*-
"""AI 定向钓鱼（Spear Phishing）实战 PoC 核心模块（零第三方依赖）。

对应研究背景（见 article.md 参考文献）：
  - 2025-2026 年出现的 LLM 个性化钓鱼/ pretext 生成：模型根据目标画像
    生成高度可信、可绕过邮件网关检测的定制邮件；
  - 本文用本地的、确定性的「模拟攻击者模型」替代真实 LLM，演示完整链路：
      目标画像 -> 生成个性化钓鱼邮件 -> 邮件安全网关分类 -> 受害者决策

与以往"群发骗密码"不同，本文重点量化：
  (1) 个性化邮件相比模板邮件，对「邮件网关检测」的绕过率提升；
  (2) 个性化 + 上下文细节，对「受害者点击率」的提升。

所有数据均为本地虚构，仅用于防御研究与授权测试。
"""
import json
import os
import re
import time

LAB_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(LAB_DIR, "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# 1) 目标画像库（模拟 OSINT 收集到的公开信息；本地虚构，仅用于演示）
# ---------------------------------------------------------------------------
TARGETS = [
    {"name": "张伟", "role": "财务主管", "company": "宏图科技", "recent": "正在做 Q3 预算", "style": "严谨、看重流程"},
    {"name": "李娜", "role": "HR 经理", "company": "宏图科技", "recent": "校招季招聘", "style": "亲和、易被求助打动"},
    {"name": "王强", "role": "研发工程师", "company": "宏图科技", "recent": "上線一个新服务", "style": "技术导向、警惕性高"},
    {"name": "陈静", "role": "采购专员", "company": "宏图科技", "recent": "供应商对账", "style": "务实、关注截止日期"},
    {"name": "刘洋", "role": "销售总监", "company": "宏图科技", "recent": "冲刺季度业绩", "style": "结果导向、常在外"},
    {"name": "赵敏", "role": "法务顾问", "company": "宏图科技", "recent": "合同合规审查", "style": "谨慎、重条款"},
    {"name": "孙磊", "role": "IT 管理员", "company": "宏图科技", "recent": "迁移邮箱系统", "style": "技术、警惕可疑链接"},
    {"name": "周婷", "role": "市场专员", "company": "宏图科技", "recent": "筹备行业展会", "style": "外向、信息开放"},
]

# ---------------------------------------------------------------------------
# 2) 攻击者「生成模型」（确定性模拟；真实场景替换为本地/API LLM 即可）
#    - 模板邮件：无个性化，只做通用伪装
#    - 个性化邮件：注入目标画像中的真实细节（姓名/部门/近期事项）
# ---------------------------------------------------------------------------

def gen_template_email(target, sender="it-support@macro-it.com"):
    """基线：通用钓鱼模板，无个性化，发件域/链接域均不在白名单。"""
    subject = "您的邮箱将于 24 小时内停用，请尽快处理"
    body = (
        "尊敬的用户：\n"
        "为保障账户安全，您的企业邮箱将于 24 小时内停用。\n"
        "请点击下方链接完成身份验证，否则将无法收发邮件：\n"
        "http://mail-verify.macro-it.com/verify\n"
        "（系统自动发送，请勿回复）"
    )
    return subject, body, "template"


def gen_personalized_email(target, sender="hr-portal@partner-hr.com"):
    """攻击版：利用目标画像生成「看起来认识你」的定向邮件。

    为演示「绕过网关」：发件域在网关白名单内（partner-hr.com 是已知合作域的仿冒），
    链接指向白名单内看起来像内部的子域（forms.hongtu.com），且不出现高危词，
    从而把网关分数压到放行线以下——这正是个性化钓鱼相对模板钓鱼更危险的地方。
    """
    name = target["name"]
    role = target["role"]
    company = target["company"]
    recent = target["recent"]
    link_domain = "forms.hongtu.com"   # 在网关允许链接域白名单内
    subject = "关于%s的事宜，请查收" % recent
    body = (
        "%s 您好：\n"
        "我是%s行政部的同事。注意到您近期负责%s，\n"
        "按公司流程需要您补充一份确认单。\n"
        "为避免影响后续工作，请在今日下班前于此处在线填写：\n"
        "http://%s/form?u=%s\n"
        "如有疑问可先回复本邮件。\n"
        "——%s行政支持" % (name, company, recent, link_domain, name, company)
    )
    return subject, body, "personalized"


# ---------------------------------------------------------------------------
# 3) 邮件安全网关（模拟分类器：关键词 + 发件域 + 链接域打分）
#    真实环境是 ML 模型；这里用可解释的启发式，便于量化「绕过率」。
# ---------------------------------------------------------------------------
SUSPICIOUS_KEYWORDS = ["停用", "验证", "密码", "点击", "紧急", "否则", "立即", "账户", "链接", "验证", "过期"]
# 网关维护的「允许发件域」白名单（公司真实域 + 已知合作域）
ALLOWED_SENDER_DOMAINS = ["hongtu.com", "partner-hr.com"]
# 网关维护的「允许链接域」白名单（公司资源域）
ALLOWED_LINK_DOMAINS = ["hongtu.com", "macro-it.com", "forms.hongtu.com"]


def gateway_classify(subject, body, sender, link_domain):
    """返回 (label, score)  score 越高越可疑(0-100)。

    关键点：个性化邮件可以通过「不在高危词表 + 发件域仿冒进白名单 +
    链接域指向白名单内看起来像内部的子域」把分数压到放行线以下。
    """
    score = 0
    text = subject + "\n" + body
    for kw in SUSPICIOUS_KEYWORDS:
        if kw in text:
            score += 10
    # 发件域不在允许列表
    sender_domain = (sender.split("@")[-1].replace("[", "").replace("]", "")) if "@" in sender else ""
    if sender_domain not in ALLOWED_SENDER_DOMAINS:
        score += 25
    # 链接域不在允许列表
    if link_domain and link_domain not in ALLOWED_LINK_DOMAINS:
        score += 30
    # 链接使用了 IP 地址
    if re.search(r"\b\d{1,3}(\.\d{1,3}){3}\b", text):
        score += 20
    score = min(score, 100)
    label = "BLOCK" if score >= 60 else ("REVIEW" if score >= 30 else "PASS")
    return label, score


def extract_link_domain(text):
    m = re.search(r"https?://([^/\s]+)", text)
    return m.group(1) if m else ""


# ---------------------------------------------------------------------------
# 4) 受害者决策（模拟：基于邮件「可信度」与「角色警惕度」）
# ---------------------------------------------------------------------------
ROLE_WARINESS = {  # 越高越不容易点
    "财务主管": 0.42, "HR 经理": 0.30, "研发工程师": 0.48, "采购专员": 0.40,
    "销售总监": 0.42, "法务顾问": 0.52, "IT 管理员": 0.58, "市场专员": 0.28,
}


def victim_click(email_type, target, gateway_label):
    wariness = ROLE_WARINESS.get(target["role"], 0.5)
    if gateway_label == "BLOCK":
        return False  # 邮件被网关拦了，根本到不了收件箱
    # 个性化邮件显著降低警惕：base_click 高、且用「姓名哈希」保证确定性可复现
    base_click = 0.78 if email_type == "personalized" else 0.28
    prob = base_click * (1 - wariness)        # 最终点击倾向
    threshold = int(prob * 100)
    roll = (abs(hash(target["name"])) % 100)  # 确定性的「受害者本次是否上钩」
    return roll < threshold


# ---------------------------------------------------------------------------
# 5) 一次完整投递
# ---------------------------------------------------------------------------
def deliver(target, email_type, sender, gateway_override=None):
    if email_type == "personalized":
        subject, body, etype = gen_personalized_email(target, sender)
    else:
        subject, body, etype = gen_template_email(target, sender)
    link_domain = extract_link_domain(body)
    if gateway_override:
        label, score = gateway_override, 99
    else:
        label, score = gateway_classify(subject, body, sender, link_domain)
    clicked = victim_click(etype, target, label)
    return {
        "target": target["name"], "role": target["role"],
        "type": etype, "gateway": label, "score": score,
        "link_domain": link_domain, "clicked": clicked,
        "subject": subject,
    }
