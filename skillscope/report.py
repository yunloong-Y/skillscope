# -*- coding: utf-8 -*-
"""Self-contained light-theme HTML report. No CDN, no JS dependency, no network."""
from __future__ import annotations

from html import escape
from typing import List

from .rules import RULE_CATALOG
from .tokens import budget_remaining, reduce_candidates, total_cost

_CSS = """
:root{--bg:#f6f7f9;--card:#fff;--ink:#1b1f24;--muted:#6b7280;--line:#e5e7eb;
--red:#d93025;--amber:#e8890c;--blue:#1a73e8;--green:#1e8e3e;}
*{box-sizing:border-box}body{margin:0;padding:32px 20px 64px;background:var(--bg);
color:var(--ink);font:14px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif}
.wrap{max-width:1080px;margin:0 auto}h1{font-size:26px;margin:0 0 6px}h2{font-size:18px;margin:36px 0 14px}
.sub{color:var(--muted);font-size:13px;margin-bottom:24px}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:14px}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:18px}
.card .k{color:var(--muted);font-size:12px;letter-spacing:.03em}.card .v{font-size:26px;font-weight:650;margin-top:6px}
.card .n{color:var(--muted);font-size:12px;margin-top:4px}
table{width:100%;border-collapse:collapse;background:var(--card);border:1px solid var(--line);border-radius:12px;overflow:hidden}
th,td{padding:11px 14px;text-align:left;border-bottom:1px solid var(--line);vertical-align:top}
th{background:#f0f2f5;font-size:12px;color:var(--muted);font-weight:600}tr:last-child td{border-bottom:0}
.badge{display:inline-block;padding:2px 9px;border-radius:999px;font-weight:700;font-size:12px;color:#fff}
.g-A{background:var(--green)}.g-B{background:#4c9aff}.g-C{background:var(--amber)}.g-D{background:var(--red)}
.sev{display:inline-block;padding:1px 7px;border-radius:5px;font-size:11px;font-weight:700}
.s-error{background:#fde8e6;color:var(--red)}.s-warn{background:#fff2dd;color:#a35c00}.s-info{background:#e8f0fe;color:var(--blue)}
.bar{height:8px;background:#eceff3;border-radius:6px;overflow:hidden;min-width:110px;margin-top:5px}
.bar>i{display:block;height:100%;background:#5b8def;border-radius:6px}
.code{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:12px}
.muted{color:var(--muted)}.fix{color:#0b6b3a}
ul{padding-left:20px}li{margin:5px 0}
.note{background:#eef4ff;border:1px solid #d6e4ff;border-radius:10px;padding:14px 16px;color:#26436b;font-size:13px}
footer{margin-top:40px;color:var(--muted);font-size:12px;border-top:1px solid var(--line);padding-top:16px}
"""

_SEV_LABEL = {"error": "ERROR", "warn": "WARN", "info": "INFO"}


def _card(key, value, note):
    return '<div class="card"><div class="k">%s</div><div class="v">%s</div><div class="n">%s</div></div>' % (
        escape(key), escape(str(value)), escape(str(note)),
    )


def build_report(audited, root, budget, generated_at) -> str:
    infos = [a.info for a in audited]
    tokens = total_cost(i.tokens for i in infos)
    remaining = budget_remaining(budget, (i.tokens for i in infos))
    findings = sum(len(a.findings) for a in audited)
    avg = round(sum(a.score for a in audited) / len(audited), 1) if audited else 0
    max_tokens = max((i.tokens for i in infos), default=1) or 1

    out = []
    out.append("<!doctype html><html lang=\"zh-CN\"><head><meta charset=\"utf-8\">")
    out.append("<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">")
    out.append("<title>skillscope · Agent Skill 审计报告</title><style>%s</style></head><body><div class=\"wrap\">" % _CSS)
    out.append("<h1>skillscope · Agent Skill 审计报告</h1>")
    out.append("<div class=\"sub\">扫描路径 %s ｜ 生成时间 %s ｜ 上下文预算 %s tokens（估算）</div>" % (
        escape(str(root)), escape(generated_at), escape(str(budget)),
    ))

    out.append('<div class="cards">')
    out.append(_card("SKILL 数量", len(audited), "发现的 SKILL.md 文件"))
    out.append(_card("平均得分", avg, "满分 100，按规则扣分"))
    out.append(_card("估算常驻成本", "%s tok" % format(tokens, ","), "frontmatter + 正文，启发式估算"))
    out.append(_card("预算剩余", format(remaining, ","), "为负数即已超预算"))
    out.append(_card("问题总数", findings, "error / warn / info 合计"))
    out.append("</div>")

    if infos:
        out.append("<h2>最该先瘦身的 3 个 skill</h2><ul>")
        for info in reduce_candidates(infos):
            out.append("<li><span class=\"code\">%s</span> — 估算 %s tokens（占本次合计 %.1f%%）</li>" % (
                escape(info.name), format(info.tokens, ","), info.tokens * 100.0 / (tokens or 1),
            ))
        out.append("</ul>")

    out.append("<h2>逐个评分</h2><table><thead><tr>"
               "<th>等级</th><th>Skill</th><th>得分</th><th>估算 tokens</th><th>问题数</th><th>路径</th>"
               "</tr></thead><tbody>")
    for a in sorted(audited, key=lambda x: (x.score, x.info.name)):
        width = max(2, int(a.info.tokens * 100 / max_tokens))
        out.append("<tr><td><span class=\"badge g-%s\">%s</span></td>"
                   "<td><strong>%s</strong></td><td>%d</td>"
                   "<td>%s<div class=\"bar\"><i style=\"width:%d%%\"></i></div></td>"
                   "<td>%d</td><td class=\"code muted\">%s</td></tr>" % (
                       escape(a.grade), escape(a.grade), escape(a.info.name), a.score,
                       format(a.info.tokens, ","), width, len(a.findings),
                       escape(str(a.info.path)),
                   ))
    out.append("</tbody></table>")

    out.append("<h2>问题明细</h2>")
    if not findings:
        out.append('<div class="note">本次扫描没有发现任何规则命中。</div>')
    for a in sorted(audited, key=lambda x: x.score):
        out.append('<h3 style="font-size:15px;margin:22px 0 8px">%s <span class="muted">(%d)</span></h3>' % (
            escape(a.info.name), len(a.findings),
        ))
        if not a.findings:
            out.append('<div class="muted">无</div>')
            continue
        out.append("<table><thead><tr><th>级别</th><th>规则</th><th>说明</th><th>建议动作</th></tr></thead><tbody>")
        for f in a.findings:
            out.append('<tr><td><span class="sev s-%s">%s</span></td><td class="code">%s</td>'
                       '<td>%s</td><td class="fix">%s</td></tr>' % (
                           escape(f.severity), _SEV_LABEL.get(f.severity, f.severity),
                           escape(f.code), escape(f.message), escape(f.fix),
                       ))
        out.append("</tbody></table>")

    out.append("<h2>规则目录</h2><table><thead><tr><th>规则</th><th>级别</th><th>检查项</th><th>为什么</th></tr></thead><tbody>")
    for rule in RULE_CATALOG:
        out.append('<tr><td class="code">%s</td><td><span class="sev s-%s">%s</span></td><td>%s</td><td class="muted">%s</td></tr>' % (
            escape(rule["code"]), escape(rule["severity"]), _SEV_LABEL.get(rule["severity"], ""),
            escape(rule["title"]), escape(rule["why"]),
        ))
    out.append("</tbody></table>")

    out.append('<div class="note" style="margin-top:24px"><strong>关于 token 数字</strong>：这里的 token '
               '是启发式估算（CJK 约 1 字 1 token，其余约 4 字符 1 token），<b>不是任何模型 tokenizer 的实测结果</b>，'
               '只用于 skill 之间的相对比较和粗略预算。star、fork、增量等 GitHub 数字不来自本工具。</div>')
    out.append("<footer>skillscope · 零依赖本地审计 · 全程不联网、不上传任何 skill 内容。"
               "评分 = 100 − Σ(error 14 / warn 7 / info 2)，A≥85 / B≥70 / C≥50 / D&lt;50。</footer>")
    out.append("</div></body></html>")
    return "\n".join(out)


def write_report(path, audited, root, budget, generated_at) -> str:
    html = build_report(audited, root, budget, generated_at)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(html)
    return html
