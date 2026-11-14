# -*- coding: utf-8 -*-
"""Heuristic context-cost estimation.

IMPORTANT: this is NOT a tokenizer. It is a cheap, deterministic heuristic used
only for *relative* comparison between skills and for a rough context budget.
Real token counts depend on the model's tokenizer; never present these numbers
as measured values.

Rule: CJK / kana / hangul ~ 1 token per character, everything else ~ 4 chars
per token. This is deliberately an upper-ish bound so the budget errs on the
safe side.
"""
from __future__ import annotations

import re
from typing import Iterable

_WIDE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\u3040-\u30ff\uac00-\ud7af]")

DEFAULT_BUDGET = 8000


def estimate_tokens(text: str) -> int:
    """Rough token estimate for one string. Returns 0 for empty input."""
    if not text:
        return 0
    wide = len(_WIDE.findall(text))
    other = max(0, len(text) - wide)
    return int(wide + other / 4.0 + 0.5)


def estimate_skill_cost(frontmatter: str, body: str) -> int:
    """Estimated context cost of loading one skill (frontmatter + body)."""
    return estimate_tokens(frontmatter) + estimate_tokens(body)


def total_cost(costs: Iterable[int]) -> int:
    return sum(costs)


def budget_remaining(budget: int, costs: Iterable[int]) -> int:
    """May be negative; a negative value means the budget is already blown."""
    return budget - total_cost(costs)


def reduce_candidates(skills, limit: int = 3):
    """Return the most expensive skills, for a 'what to slim first' hint."""
    return sorted(skills, key=lambda s: s.tokens, reverse=True)[:limit]
