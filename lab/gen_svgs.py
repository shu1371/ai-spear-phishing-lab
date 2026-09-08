# -*- coding: utf-8 -*-
"""生成 4 张 SVG 示意图（与 Text2SQL / Slopsquatting 同风格：浅色、卡片、阴影、蓝/红/琥珀）。

运行：python gen_svgs.py  -> 生成 svg/fig1..fig4.svg
PNG 由 render_png.js（Node + playwright 无头 Chromium）渲染到 ../images/figN.png
"""
import os

os.makedirs("svg", exist_ok=True)

HEAD = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="780" '
    'viewBox="0 0 1280 780" font-family="\'Microsoft YaHei\',\'PingFang SC\',Arial,sans-serif">'
)
DEF = """
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#f8fafc"/><stop offset="1" stop-color="#eef2f7"/>
    </linearGradient>
    <linearGradient id="gBlue" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#3b82f6"/><stop offset="1" stop-color="#2563eb"/>
    </linearGradient>
    <linearGradient id="gGreen" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#22c55e"/><stop offset="1" stop-color="#16a34a"/>
    </linearGradient>
    <linearGradient id="gRed" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#ef4444"/><stop offset="1" stop-color="#dc2626"/>
    </linearGradient>
    <linearGradient id="gAmber" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#f59e0b"/><stop offset="1" stop-color="#d97706"/>
    </linearGradient>
    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="3" stdDeviation="5" flood-color="#0f172a" flood-opacity="0.16"/>
    </filter>
    <marker id="arrGray" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto">
      <path d="M0,0 L9,3 L0,6 Z" fill="#475569"/>
    </marker>
    <marker id="arrRed" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto">
      <path d="M0,0 L9,3 L0,6 Z" fill="#dc2626"/>
    </marker>
    <marker id="arrAmber" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto">
      <path d="M0,0 L9,3 L0,6 Z" fill="#d97706"/>
    </marker>
    <marker id="arrGreen" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto">
      <path d="M0,0 L9,3 L0,6 Z" fill="#16a34a"/>
    </marker>
  </defs>
"""


def card(x, y, w, h, title, body, color, title_fill="#ffffff", body_color="#334155"):
    lines = body.split("\n")
    cx = int(x + w / 2)
    body_svg = ""
    for i, ln in enumerate(lines):
        body_svg += '<text x="%d" y="%d" text-anchor="middle" font-size="13" fill="%s">%s</text>' % (
            cx, y + 50 + i * 22, body_color, ln)
    return (
        '<g filter="url(#shadow)">'
        '<rect x="%d" y="%d" width="%d" height="%d" rx="16" fill="#ffffff" stroke="%s" stroke-width="2.5"/>'
        '<rect x="%d" y="%d" width="%d" height="40" rx="16" fill="%s"/>'
        '<rect x="%d" y="%d" width="%d" height="20" fill="%s"/>'
        '<text x="%d" y="%d" text-anchor="middle" font-size="16" font-weight="700" fill="%s">%s</text>'
        '%s'
        '</g>'
    ) % (x, y, w, h, color, x, y, w, color, x, y + 20, w, color,
         cx, y + 27, title_fill, title, body_svg)


# ------------------------------------------------------------------ fig1 架构
fig1 = HEAD + DEF
fig1 += '<rect x="0" y="0" width="1280" height="780" fill="url(#bg)"/>'
fig1 += '<text x="640" y="44" text-anchor="middle" font-size="25" font-weight="700" fill="#0f172a">图1　AI 定向钓鱼杀伤链：从画像到点击</text>'

fig1 += card(70, 110, 230, 150, "攻击者 + LLM", "收集目标公开信息\n构造个性化画像\n驱动模型生成钓鱼邮件", "url(#gRed)", body_color="#7f1d1d")
fig1 += card(430, 100, 420, 150, "AI 钓鱼邮件生成器", "输入: 目标画像 + 任务\n输出: 高仿真个性化邮件\n(姓名/部门/近期事项)", "url(#gBlue)")
fig1 += card(980, 100, 230, 270, "投递通道", "发件域名仿冒\n链接域白名单绕过\n绕过邮件网关", "url(#gAmber)")

fig1 += '<path d="M300,185 C350,185 380,175 428,175" stroke="#475569" stroke-width="3.5" fill="none" marker-end="url(#arrGray)"/>'
fig1 += '<text x="358" y="165" text-anchor="middle" font-size="13.5" fill="#475569">画像</text>'
fig1 += '<path d="M850,175 C900,175 940,175 978,175" stroke="#475569" stroke-width="3.5" fill="none" marker-end="url(#arrGray)"/>'
fig1 += '<text x="915" y="160" text-anchor="middle" font-size="13.5" fill="#475569">发送</text>'

fig1 += card(70, 330, 300, 130, "目标员工(8人)", "收到邮件\n基于可信度/警惕度\n决策是否点击", "url(#gGreen)")
fig1 += '<path d="M980,370 C900,370 700,420 372,395" stroke="#dc2626" stroke-width="3" stroke-dasharray="7 5" fill="none" marker-end="url(#arrRed)"/>'
fig1 += '<text x="700" y="380" text-anchor="middle" font-size="13" fill="#dc2626">个性化邮件绕过网关直达收件箱</text>'

fig1 += card(70, 520, 300, 140, "受害者失陷", "凭证/内网入口泄露\n后续横向移动\n=A 链首环", "url(#gRed)", body_color="#7f1d1d")
fig1 += '<path d="M370,460 C420,460 460,500 460,540" stroke="#dc2626" stroke-width="3" fill="none" marker-end="url(#arrRed)"/>'

fig1 += card(430, 520, 420, 140, "邮件安全网关", "关键词 + 发件域 + 链接域\n启发式打分\nPASS / REVIEW / BLOCK", "url(#gAmber)")
fig1 += '<path d="M850,590 C900,590 940,560 978,430" stroke="#d97706" stroke-width="3" stroke-dasharray="7 5" fill="none" marker-end="url(#arrAmber)"/>'
fig1 += '<text x="960" y="520" text-anchor="middle" font-size="12.5" fill="#92400e">模板邮件 8/8 被拦</text>'

fig1 += '<text x="640" y="745" text-anchor="middle" font-size="15" font-weight="700" fill="#dc2626">▲ 个性化让「网关分数」与「受害者信任」同时下降——这正是 AI 钓鱼比群发更危险的根因</text>'
fig1 += "</svg>"
open("svg/fig1_architecture.svg", "w", encoding="utf-8").write(fig1)

# ------------------------------------------------------------------ fig2 时序
fig2 = HEAD + DEF
fig2 += '<rect x="0" y="0" width="1280" height="780" fill="url(#bg)"/>'
fig2 += '<text x="640" y="44" text-anchor="middle" font-size="25" font-weight="700" fill="#0f172a">图2　一次个性化钓鱼的端到端时序</text>'

actors = [("攻击者/LLM", 160, "url(#gRed)"), ("投递(网关)", 470, "url(#gAmber)"), ("目标员工", 760, "url(#gGreen)"), ("失陷/后续", 1080, "url(#gRed)")]
ax = []
for name, x, c in actors:
    bx = x - 80
    ax.append('<g filter="url(#shadow)"><rect x="%d" y="70" width="160" height="52" rx="14" fill="%s"/>'
              '<text x="%d" y="103" text-anchor="middle" font-size="15" font-weight="700" fill="#ffffff">%s</text></g>' % (bx, c, x, name))
fig2 += "".join(ax)
for name, x, c in actors:
    fig2 += '<line x1="%d" y1="122" x2="%d" y2="720" stroke="#cbd5e1" stroke-width="2" stroke-dasharray="4 4"/>' % (x, x)


def msg(x1, x2, y, text, color, anchor="middle", dx=0):
    m = '<path d="M%d,%d C%d,%d %d,%d %d,%d" stroke="%s" stroke-width="3" fill="none" marker-end="url(#arrRed)"/>' % (
        x1, y, (x1 + x2) // 2, y - 14, (x1 + x2) // 2, y - 14, x2, y, color)
    t = '<text x="%d" y="%d" text-anchor="%s" font-size="13" font-weight="600" fill="%s">%s</text>' % ((x1 + x2) // 2 + dx, y - 18, anchor, color, text)
    return m + t

fig2 += msg(160, 470, 175, "构建画像: 张伟/财务/Q3预算", "#475569")
fig2 += msg(160, 470, 235, "生成个性化邮件(含姓名/近期事项)", "#475569")
fig2 += msg(470, 160, 295, "网关打分=25(PASS) 放行", "#16a34a")
fig2 += msg(470, 760, 360, "投递至收件箱(未被拦)", "#dc2626")
fig2 += msg(760, 470, 420, "阅读:『关于Q3预算,请查收』", "#475569")
fig2 += msg(760, 470, 480, "可信度高→点击链接", "#dc2626")
fig2 += msg(760, 1080, 540, "访问伪造表单(凭证外发)", "#dc2626")
fig2 += msg(1080, 760, 600, "入口失陷→横向移动", "#dc2626")
# 对照：模板邮件
fig2 += msg(160, 470, 660, "模板邮件: 停用/验证/链接→打分100", "#475569")
fig2 += msg(470, 160, 710, "网关 BLOCK 8/8 拦截", "#16a34a")

fig2 += '<text x="640" y="745" text-anchor="middle" font-size="15" font-weight="700" fill="#dc2626">▲ 同一目标，模板被拦、个性化直达——差距来自「像不像内部邮件」</text>'
fig2 += "</svg>"
open("svg/fig2_attack_chain.svg", "w", encoding="utf-8").write(fig2)

# ------------------------------------------------------------------ fig3 防御矩阵
fig3 = HEAD + DEF
fig3 += '<rect x="0" y="0" width="1280" height="780" fill="url(#bg)"/>'
fig3 += '<text x="640" y="44" text-anchor="middle" font-size="25" font-weight="700" fill="#0f172a">图3　AI 钓鱼防御矩阵</text>'

rows = [
    ("画像侧", 60, 110, "url(#gBlue)", "员工公开信息最小化\n社媒/官网脱敏\n高管(鲸鱼)重点保护"),
    ("邮件侧\n(网关)", 60, 250, "url(#gAmber)", "发件域强校验(DMARC)\n链接域实时比对\n行为/语义模型"),
    ("人员侧\n(意识)", 60, 390, "url(#gBlue)", "钓鱼演练常态化\n\"悬停看真域名\"\n可疑即报不点链"),
    ("响应侧", 60, 530, "url(#gAmber)", "一键举报+自动隔离\n同源邮件回溯\n凭据泄露速轮换"),
    ("技术侧\n(零信任)", 60, 670, "url(#gRed)", "MFA/防钓鱼令牌\n链接不直接给凭证\n微隔离限制横向"),
]
mid = 360
for t, x, y, c, body in rows:
    fig3 += card(x, y, 300, 120, t, body, c)
    fig3 += '<path d="M%s,%d C%s,%d %d,%d %d,%d" stroke="%s" stroke-width="3" fill="none" marker-end="url(#arrGreen)"/>' % (
        x + 300, y + 60, x + 330, y + 60, mid - 40, y + 60, mid - 40, y + 60, "#16a34a")
fig3 += card(mid, 110, 470, 680, "目标：把「到达+点击」两条线都打穿",
             "① 画像侧: 减少可被模型利用的公开素材\n② 邮件侧: 让个性化邮件也过不了网关\n③ 人员侧: 即便到达也不点(最后一公里)\n④ 响应侧: 点了也能快速止损\n⑤ 技术侧: 点了也拿不到核心凭据\n\n结论: 单点防御必漏——\n网关(邮件侧)+意识(人员侧)+零信任(技术侧)\n三层叠加才稳",
             "url(#gGreen)", body_color="#14532d")
fig3 += "</svg>"
open("svg/fig3_defense.svg", "w", encoding="utf-8").write(fig3)

# ------------------------------------------------------------------ fig4 结果
fig4 = HEAD + DEF
fig4 += '<rect x="0" y="0" width="1280" height="780" fill="url(#bg)"/>'
fig4 += '<text x="640" y="44" text-anchor="middle" font-size="25" font-weight="700" fill="#0f172a">图4　实战验证：模板 vs 个性化（8 目标）</text>'

# 两组对比条：到达率 / 点击率
def bar(x, label, val, total, color):
    bh = int(360 * val / total)
    y = 660 - bh
    return ('<rect x="%d" y="%d" width="90" height="%d" rx="6" fill="%s"/>'
            '<text x="%d" y="%d" text-anchor="middle" font-size="18" font-weight="700" fill="#0f172a">%d/%d</text>'
            '<text x="%d" y="%d" text-anchor="middle" font-size="13" fill="#334155">%s</text>') % (
        x, y, bh, color, x + 45, y - 12, val, total, x + 45, 690, label)

fig4 += '<text x="360" y="120" text-anchor="middle" font-size="16" font-weight="700" fill="#334155">到达收件箱(绕过网关)</text>'
fig4 += bar(300, "模板", 0, 8, "url(#gGreen)")
fig4 += bar(440, "个性化", 8, 8, "url(#gRed)")
fig4 += '<text x="860" y="120" text-anchor="middle" font-size="16" font-weight="700" fill="#334155">受害者点击数</text>'
fig4 += bar(800, "模板", 0, 8, "url(#gGreen)")
fig4 += bar(940, "个性化", 3, 8, "url(#gRed)")
fig4 += '<line x1="220" y1="660" x2="1040" y2="660" stroke="#94a3b8" stroke-width="2"/>'

fig4 += card(260, 180, 760, 200, "关键结论",
             "模板钓鱼: 网关拦截 8/8, 到达 0, 点击 0 —— 传统关键词网关即可压死\n"
             "个性化钓鱼: 网关放行 8/8, 到达 8, 点击 3 (点击率 37.5%)\n"
             "个性化让「网关放行率」从 0% 跳到 100%, 「点击率」从 0 到 37.5%\n"
             "——提升的不是技术, 而是「可信度」; 这正是 LLM 钓鱼研究的现实威胁",
             "url(#gBlue)", body_color="#0f172a")
fig4 += "</svg>"
open("svg/fig4_results.svg", "w", encoding="utf-8").write(fig4)

print("SVGs generated:")
for f in sorted(os.listdir("svg")):
    print(" ", f, os.path.getsize(os.path.join("svg", f)), "bytes")
