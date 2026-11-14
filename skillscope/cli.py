# -*- coding: utf-8 -*-
"""Command line entry point. Everything runs locally, offline, without credentials."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from . import __version__
from .report import write_report
from .rules import RULE_CATALOG, audit
from .scan import discover
from .tokens import DEFAULT_BUDGET, budget_remaining, reduce_candidates, total_cost

SAMPLES = Path(__file__).resolve().parent / "samples"


def _now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _payload(audited, root, budget, generated_at):
    costs = [a.info.tokens for a in audited]
    findings = sum(len(a.findings) for a in audited)
    return {
        "tool": "skillscope",
        "version": __version__,
        "generated_at": generated_at,
        "root": str(root),
        "budget": budget,
        "token_estimate": "heuristic: CJK ~1 char/token, others ~4 chars/token; NOT a tokenizer",
        "summary": {
            "skills": len(audited),
            "average_score": round(sum(a.score for a in audited) / len(audited), 1) if audited else 0,
            "estimated_tokens": total_cost(costs),
            "budget_remaining": budget_remaining(budget, costs),
            "findings": findings,
        },
        "slim_first": [
            {"name": i.name, "estimated_tokens": i.tokens}
            for i in reduce_candidates([a.info for a in audited])
        ],
        "skills": [
            {
                "name": a.info.name,
                "path": str(a.info.path),
                "score": a.score,
                "grade": a.grade,
                "estimated_tokens": a.info.tokens,
                "description": a.info.description,
                "findings": [
                    {"code": f.code, "severity": f.severity, "message": f.message, "fix": f.fix}
                    for f in a.findings
                ],
            }
            for a in audited
        ],
        "rule_catalog": RULE_CATALOG,
    }


def _print_terminal(audited, budget, generated_at):
    costs = [a.info.tokens for a in audited]
    total = total_cost(costs)
    remain = budget_remaining(budget, costs)
    print("skillscope %s  |  %s  |  %d 个 SKILL.md  |  预算 %s tok（估算）" % (
        __version__, generated_at, len(audited), format(budget, ","),
    ))
    print("-" * 78)
    print("%-3s %-5s %-30s %-12s %s" % ("级", "分", "Skill", "估算 tok", "问题"))
    for a in sorted(audited, key=lambda x: (x.score, x.info.name)):
        print("%-3s %-5d %-30s %-12s %d" % (
            a.grade, a.score, a.info.name[:30], format(a.info.tokens, ","), len(a.findings),
        ))
    print("-" * 78)
    print("合计估算常驻成本 %s tok  |  预算剩余 %s tok  |  问题 %d 条" % (
        format(total, ","), format(remain, ","), sum(len(a.findings) for a in audited),
    ))
    if remain < 0:
        print("! 已超预算：这些 skill 会在任务开始前吃掉全部上下文窗口。")
    for a in sorted(audited, key=lambda x: x.score)[:3]:
        for f in a.findings:
            if f.severity == "error":
                print("  [ERROR] %s %s -> %s" % (a.info.name, f.code, f.fix))
    print("提示：token 为启发式估算，不是 tokenizer 实测值。")


def _run(root: Path, args) -> int:
    generated_at = _now()
    infos = discover(root)
    audited = audit(infos)
    payload = _payload(audited, root, args.budget, generated_at)

    if args.json_path:
        Path(args.json_path).parent.mkdir(parents=True, exist_ok=True)
        Path(args.json_path).write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print("JSON -> %s" % args.json_path)
    if args.html_path:
        Path(args.html_path).parent.mkdir(parents=True, exist_ok=True)
        write_report(args.html_path, audited, root, args.budget, generated_at)
        print("HTML -> %s" % args.html_path)
    if not args.quiet:
        _print_terminal(audited, args.budget, generated_at)

    if args.fail_under is not None and audited:
        lowest = min(a.score for a in audited)
        if lowest < args.fail_under:
            print("FAIL: 最低分 %d < --fail-under %d" % (lowest, args.fail_under))
            return 1
    return 0


def _add_common(parser):
    parser.add_argument("--budget", type=int, default=DEFAULT_BUDGET,
                        help="上下文预算（估算 tokens），默认 8000")
    parser.add_argument("--json", dest="json_path", metavar="PATH", help="同时输出 JSON")
    parser.add_argument("--html", dest="html_path", metavar="PATH", help="同时输出 HTML 报告")
    parser.add_argument("--fail-under", type=int, metavar="SCORE",
                        help="任一 skill 低于该分数则退出码 1（用于 CI）")
    parser.add_argument("--quiet", action="store_true", help="只写文件，不打印表格")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="skillscope",
        description="Audit Agent Skills for quality and context cost. Offline, zero dependencies.",
    )
    parser.add_argument("--version", action="version", version="skillscope %s" % __version__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_scan = sub.add_parser("scan", help="扫描目录里的 SKILL.md")
    p_scan.add_argument("path", nargs="?", default=".", help="目录或单个 SKILL.md，默认当前目录")
    _add_common(p_scan)

    p_demo = sub.add_parser("demo", help="用内置示例跑一遍，无需任何真实 skill")
    _add_common(p_demo)

    sub.add_parser("rules", help="列出全部审计规则")

    args = parser.parse_args(argv)

    if args.command == "rules":
        print("%-8s %-6s %-18s %s" % ("规则", "级别", "检查项", "为什么"))
        for rule in RULE_CATALOG:
            print("%-8s %-6s %-18s %s" % (
                rule["code"], rule["severity"], rule["title"], rule["why"],
            ))
        return 0

    root = SAMPLES if args.command == "demo" else Path(args.path).resolve()
    if not root.exists():
        print("路径不存在：%s" % root, file=sys.stderr)
        return 2
    return _run(root, args)
