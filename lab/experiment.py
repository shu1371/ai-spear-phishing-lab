# -*- coding: utf-8 -*-
"""AI 定向钓鱼 量化实验：模板 vs 个性化（绕过网关 + 受害者点击）。每场景 8 目标。"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from phish_core import TARGETS, deliver

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")

# 攻击者视角：用「看起来像内部域名」的发件人，挑战网关
SENDER_TEMPLATE = "it-support@macro-it[.]com"
SENDER_PERSONAL = "hr-portal@hongtu-hr[.]net"


def scenario(name, email_type, sender):
    n = len(TARGETS)
    block = click = reach = 0
    rows = []
    for t in TARGETS:
        r = deliver(t, email_type, sender)
        rows.append(r)
        if r["gateway"] == "BLOCK":
            block += 1
        else:
            reach += 1
            if r["clicked"]:
                click += 1
        print("[%s] %-4s %-12s gw=%-6s score=%-3d click=%-5s | %s" % (
            name[:4], r["type"][:4], r["target"], r["gateway"], r["score"], r["clicked"], r["subject"]))
    print("==> %s: 拦截 %d/%d | 到达 %d | 点击 %d/%d (点击率 %.0f%%)\n" % (
        name, block, n, reach, click, reach, 100.0 * click / reach if reach else 0))
    return {"scenario": name, "n": n, "blocked": block, "reached": reach, "clicked": click,
            "click_rate": round(100.0 * click / reach, 1) if reach else 0.0}


if __name__ == "__main__":
    print("===== 基线：模板钓鱼（通用伪装，无个性化）=====")
    a = scenario("template", "template", SENDER_TEMPLATE)
    print("===== 攻击：个性化钓鱼（注入目标画像）=====")
    b = scenario("personal", "personalized", SENDER_PERSONAL)

    print("===== 汇总 =====")
    print("模板钓鱼     : 网关拦截 %d/8 | 到达 %d | 点击 %d (点击率 %.1f%%)" % (
        a["blocked"], a["reached"], a["clicked"], a["click_rate"]))
    print("个性化钓鱼   : 网关拦截 %d/8 | 到达 %d | 点击 %d (点击率 %.1f%%)" % (
        b["blocked"], b["reached"], b["clicked"], b["click_rate"]))
    print("\n注：攻击方还可通过「发件域名仿冒 + 无高危关键词」进一步压低网关分数（见 article.md 讨论）。")
