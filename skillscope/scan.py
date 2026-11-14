# -*- coding: utf-8 -*-
"""Discover SKILL.md files and turn them into comparable SkillInfo records."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

from .frontmatter import ParsedSkill, parse
from .tokens import estimate_skill_cost

SKIP_DIRS = {
    ".git", "node_modules", ".venv", "venv", "__pycache__",
    "dist", "build", ".idea", ".next", "target",
}


@dataclass
class SkillInfo:
    path: Path
    root: Path
    name: str
    description: str
    parsed: ParsedSkill
    text: str
    tokens: int

    @property
    def label(self) -> str:
        try:
            return str(self.path)
        except Exception:
            return self.name


def _as_text(value) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        return " ".join(str(item) for item in value)
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def discover(root: Path) -> List[SkillInfo]:
    """Find every SKILL.md under root (or a single file). Never raises on unreadable files."""
    root = Path(root).resolve()
    if root.is_file():
        files = [root]
    else:
        files = []
        for candidate in root.rglob("SKILL.md"):
            rel = candidate.relative_to(root)
            if any(part in SKIP_DIRS for part in rel.parts):
                continue
            files.append(candidate)

    result: List[SkillInfo] = []
    for path in sorted(files):
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        parsed = parse(text)
        name = _as_text(parsed.get("name")) or path.parent.name
        description = _as_text(parsed.get("description"))
        cost = estimate_skill_cost(parsed.raw_frontmatter, parsed.body)
        result.append(
            SkillInfo(
                path=path,
                root=path.parent,
                name=name,
                description=description,
                parsed=parsed,
                text=text,
                tokens=cost,
            )
        )
    return result
