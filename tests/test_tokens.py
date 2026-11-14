# -*- coding: utf-8 -*-
import unittest
from pathlib import Path

from skillscope.scan import SkillInfo, discover
from skillscope.tokens import (
    budget_remaining,
    estimate_skill_cost,
    estimate_tokens,
    reduce_candidates,
    total_cost,
)


class TestTokens(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(estimate_tokens(""), 0)
        self.assertEqual(estimate_skill_cost("", ""), 0)

    def test_cjk_is_one_char_one_token(self):
        self.assertEqual(estimate_tokens("一二三四五六七八九十"), 10)

    def test_ascii_is_four_chars_one_token(self):
        self.assertEqual(estimate_tokens("a" * 40), 10)

    def test_mixed_is_deterministic(self):
        self.assertEqual(estimate_tokens("中文abcd"), 3)

    def test_budget_can_go_negative(self):
        self.assertEqual(total_cost([10, 20, 30]), 60)
        self.assertEqual(budget_remaining(100, [10, 20, 30]), 40)
        self.assertEqual(budget_remaining(50, [10, 20, 30]), -10)

    def test_reduce_candidates_orders_by_cost(self):
        infos = [
            SkillInfo(Path("a"), Path("a"), "a", "", None, "", 10),
            SkillInfo(Path("b"), Path("b"), "b", "", None, "", 500),
            SkillInfo(Path("c"), Path("c"), "c", "", None, "", 100),
        ]
        self.assertEqual([i.name for i in reduce_candidates(infos, 2)], ["b", "c"])

    def test_discover_skips_ignored_dirs(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "SKILL.md").write_text("---\nname: root\n---\n", encoding="utf-8")
            (root / "node_modules").mkdir()
            (root / "node_modules" / "SKILL.md").write_text(
                "---\nname: ignored\n---\n", encoding="utf-8"
            )
            found = discover(root)
            self.assertEqual([i.name for i in found], ["root"])


if __name__ == "__main__":
    unittest.main()
