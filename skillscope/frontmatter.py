# -*- coding: utf-8 -*-
"""Minimal, dependency-free YAML frontmatter parser for SKILL.md files.

Only the subset of YAML that Agent Skill definitions actually use is supported:
scalar keys, inline comma lists, and block ``- item`` lists. Unknown shapes are
kept as raw strings instead of raising, so a slightly unusual SKILL.md never
breaks a whole scan.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict

_FM = re.compile(r"\A\ufeff?---[ \t]*\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n|\Z)", re.S)
_KEY = re.compile(r"^[A-Za-z0-9_.\-]+$")


@dataclass
class ParsedSkill:
    data: Dict[str, Any] = field(default_factory=dict)
    raw_frontmatter: str = ""
    body: str = ""
    error: str | None = None

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)


def _scalar(value: str) -> Any:
    value = value.strip()
    if value == "" or value in ("~", "null", "Null", "NULL"):
        return None
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        return value[1:-1]
    if value.lower() in ("true", "false"):
        return value.lower() == "true"
    if "," in value:
        return [part.strip() for part in value.split(",") if part.strip()]
    return value


def parse(text: str) -> ParsedSkill:
    """Parse frontmatter + body. A missing/invalid block is reported, not guessed."""
    match = _FM.match(text)
    if not match:
        return ParsedSkill(body=text, error="missing frontmatter")

    raw = match.group(1)
    body = text[match.end():]
    data: Dict[str, Any] = {}
    list_key = None

    for line in raw.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        stripped = line.strip()
        if stripped == "-" or stripped.startswith("- "):
            if list_key is None:
                continue
            bucket = data.setdefault(list_key, [])
            if not isinstance(bucket, list):
                bucket = [bucket]
                data[list_key] = bucket
            bucket.append(_scalar(stripped[1:].strip()))
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        if not _KEY.match(key):
            continue
        list_key = key
        data[key] = [] if value.strip() == "" else _scalar(value)

    return ParsedSkill(data=data, raw_frontmatter=raw, body=body)
