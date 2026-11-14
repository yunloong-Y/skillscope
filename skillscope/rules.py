# -*- coding: utf-8 -*-
"""Pluggable audit rules for Agent Skill definitions.

Every finding carries a code, a severity and an actionable fix. Scores are a
transparent deduction from 100 - there is no hidden model or remote call.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List

from .scan import SkillInfo, _as_text

RULE_CATALOG = [
    {"code": "FM001", "severity": "error", "title": "Frontmatter 存在", "why": "Agent 靠 frontmatter 决定是否加载 skill"},
    {"code": "FM002", "severity": "error", "title": "name 字段", "why": "没有稳定标识，无法去重与引用"},
    {"code": "FM003", "severity": "error", "title": "description 字段", "why": "description 是唯一的触发依据"},
    {"code": "TRIG001", "severity": "warn", "title": "触发条件清晰", "why": "过短或不带触发词的描述会让 skill 永远不被唤起"},
    {"code": "TRIG002", "severity": "warn", "title": "description 不过长", "why": "描述越长，常驻上下文成本越高"},
    {"code": "SIZE001", "severity": "warn", "title": "正文可渐进披露", "why": "超长正文应拆到 references/ 按需加载"},
    {"code": "SIZE002", "severity": "info", "title": "正文偏长", "why": "提醒关注上下文占用"},
    {"code": "REF001", "severity": "warn", "title": "引用的文件存在", "why": "指向不存在脚本的 skill 会直接执行失败"},
    {"code": "SEC001", "severity": "error", "title": "无敏感凭据", "why": "skill 会被整体注入上下文，泄露风险最高；命中即封顶 D"},
    {"code": "DUP001", "severity": "warn", "title": "不与其它 skill 重复", "why": "近重复 skill 会互相抢触发、浪费预算"},
    {"code": "META001", "severity": "info", "title": "带 version 字段", "why": "便于跟踪规则变更"},
    {"code": "DEMO001", "severity": "info", "title": "有可运行示例", "why": "无需真实账号即可验证，决定冷启动转化"},
]

DEDUCTION = {"error": 14, "warn": 7, "info": 2}

_TRIGGER = re.compile(
    r"(use when|when (?:the )?user|trigger|触发|适用于|用于|当需要|当用户|if the user|helps? (?:you|to))",
    re.I,
)
_REF = re.compile(
    r"(?<![\w/])(?:scripts|tools|references|assets)/[A-Za-z0-9_.\-]+(?:/[A-Za-z0-9_.\-]+)*\.(?:py|sh|js|ts|mjs|md|json|yaml|yml)"
)
_HAS_DEMO = re.compile(r"(example|demo|示例|用法|quick ?start)", re.I)

_SECRET_RES = [
    ("GitHub token", re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}")),
    ("OpenAI/Anthropic style key", re.compile(r"sk-[A-Za-z0-9_\-]{20,}")),
    ("AWS access key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("private key block", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("inline credential", re.compile(r"(?i)\b(?:password|passwd|api[_-]?key|secret|token)\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{16,}['\"]?")),
]


@dataclass
class Finding:
    code: str
    severity: str
    message: str
    fix: str = ""


@dataclass
class AuditedSkill:
    info: SkillInfo
    findings: List[Finding]
    score: int
    grade: str


def _grams(text: str):
    lowered = text.lower()
    return set(re.findall(r"[a-z0-9_]+", lowered)) | set(re.findall(r"[\u4e00-\u9fff]", lowered))


def _audit_one(info: SkillInfo, all_infos: List[SkillInfo]) -> List[Finding]:
    findings: List[Finding] = []
    parsed = info.parsed

    if parsed.error:
        findings.append(Finding(
            "FM001", "error", "SKILL.md 缺少 YAML frontmatter 块（--- 包裹）",
            "在文件开头补上 --- / name / description / ---",
        ))
    if not _as_text(parsed.get("name")).strip():
        findings.append(Finding("FM002", "error", "缺少 name 字段", "补 name: <小写连字符标识>"))
    if not info.description.strip():
        findings.append(Finding(
            "FM003", "error", "缺少 description 字段",
            "补 description，写清『做什么』和『什么时候该用它』",
        ))
    else:
        desc = info.description
        if len(desc) < 40 or not _TRIGGER.search(desc):
            findings.append(Finding(
                "TRIG001", "warn", "description 过短或没有触发条件（当前 %d 字符）" % len(desc),
                "写成『Use when ... / 当用户 ... 时使用』，并说明输入与产出",
            ))
        if len(desc) > 400:
            findings.append(Finding(
                "TRIG002", "warn", "description 达 %d 字符，常驻成本偏高" % len(desc),
                "压到 1-2 句，细节移到正文或 references/",
            ))

    if info.tokens > 2000:
        findings.append(Finding(
            "SIZE001", "warn", "正文估算 %d tokens，超过 2000" % info.tokens,
            "把长规范拆到 references/，SKILL.md 只留索引与触发条件",
        ))
    elif info.tokens > 800:
        findings.append(Finding(
            "SIZE002", "info", "正文估算 %d tokens，超过 800" % info.tokens,
            "确认这些内容每次会话都真的需要",
        ))

    missing_refs = []
    for match in _REF.finditer(parsed.body):
        rel = match.group(0)
        if not (info.root / rel).exists():
            missing_refs.append(rel)
    for rel in sorted(set(missing_refs))[:5]:
        findings.append(Finding(
            "REF001", "warn", "正文引用了不存在的 %s" % rel,
            "补齐文件或改成真实相对路径",
        ))

    for label, pattern in _SECRET_RES:
        hit = pattern.search(info.text)
        if hit:
            findings.append(Finding(
                "SEC001", "error", "疑似 %s（命中位置 %d）" % (label, hit.start()),
                "删除凭据；若是占位符，改成 <YOUR_TOKEN> 这类不可执行写法",
            ))
            break

    own = _grams(info.name + " " + info.description)
    for other in all_infos:
        if other.path == info.path:
            continue
        their = _grams(other.name + " " + other.description)
        if not own or not their:
            continue
        overlap = len(own & their) / len(own | their)
        if overlap >= 0.75:
            findings.append(Finding(
                "DUP001", "warn", "与 %s 的描述高度相似（Jaccard %.2f）" % (other.name, overlap),
                "合并两个 skill，或把触发条件写得更互斥",
            ))
            break

    if not _as_text(parsed.get("version")).strip():
        findings.append(Finding("META001", "info", "缺少 version 字段", "补 version: 0.1.0"))

    has_example_dir = (info.root / "examples").is_dir() or (info.root / "demo").is_dir()
    if not has_example_dir and not _HAS_DEMO.search(parsed.body):
        findings.append(Finding(
            "DEMO001", "info", "没有示例或可运行 demo",
            "加 examples/ 或一段无需凭据即可复现的命令",
        ))

    return findings


def grade_for(score: int) -> str:
    if score >= 85:
        return "A"
    if score >= 70:
        return "B"
    if score >= 50:
        return "C"
    return "D"


def audit(infos: List[SkillInfo]):
    """Return AuditedSkill list. Pure function, no I/O beyond filesystem stat."""
    out = []
    for info in infos:
        findings = _audit_one(info, infos)
        score = max(0, 100 - sum(DEDUCTION[f.severity] for f in findings))
        # Hard gate: a credential leak can never be "mostly fine".
        if any(f.code == "SEC001" for f in findings):
            score = min(score, 35)
        out.append(AuditedSkill(info=info, findings=findings, score=score, grade=grade_for(score)))
    return out
