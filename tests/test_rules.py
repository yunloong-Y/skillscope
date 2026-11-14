# -*- coding: utf-8 -*-
import unittest
from pathlib import Path

from skillscope.frontmatter import parse
from skillscope.rules import audit, grade_for
from skillscope.scan import SkillInfo, discover

SAMPLES = Path(__file__).resolve().parents[1] / "skillscope" / "samples"
ROOT_SKILL = Path(__file__).resolve().parents[1] / "SKILL.md"


def _codes(audited):
    return [f.code for f in audited.findings]


class TestRules(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.by_name = {a.info.name: a for a in audit(discover(SAMPLES))}
        cls.root = audit(discover(ROOT_SKILL))[0]

    def test_samples_are_all_found(self):
        self.assertEqual(len(self.by_name), 4)

    def test_good_samples_score_a_without_errors(self):
        for name in ("git-commit-helper", "device-log-analyzer"):
            a = self.by_name[name]
            self.assertEqual(a.grade, "A", "%s findings=%s" % (name, _codes(a)))
            self.assertFalse(any(f.severity == "error" for f in a.findings))

    def test_references_file_is_resolved(self):
        self.assertNotIn("REF001", _codes(self.by_name["device-log-analyzer"]))

    def test_vague_skill_hits_the_expected_rules(self):
        a = self.by_name["vague-helper"]
        codes = _codes(a)
        for expected in ("FM002", "TRIG001", "REF001", "DEMO001", "META001"):
            self.assertIn(expected, codes)
        self.assertEqual(a.grade, "C")

    def test_credential_leak_is_hard_gated_to_d(self):
        a = self.by_name["secret-leak"]
        self.assertIn("SEC001", _codes(a))
        self.assertEqual(a.grade, "D")
        self.assertLessEqual(a.score, 35)

    def test_duplicate_detection(self):
        desc = "Use when the user wants a commit message"
        text_a = "---\nname: alpha\nversion: 1.0.0\ndescription: %s\n---\nExample\n" % desc
        text_b = "---\nname: beta\nversion: 1.0.0\ndescription: %s\n---\nExample\n" % desc
        base = Path("/tmp/skillscope-dup-test")
        infos = [
            SkillInfo(base / "a" / "SKILL.md", base / "a", "alpha", desc, parse(text_a), text_a, 100),
            SkillInfo(base / "b" / "SKILL.md", base / "b", "beta", desc, parse(text_b), text_b, 100),
        ]
        results = audit(infos)
        self.assertIn("DUP001", _codes(results[0]))
        self.assertIn("DUP001", _codes(results[1]))

    def test_project_skill_dogfoods_clean(self):
        self.assertEqual(self.root.grade, "A", _codes(self.root))
        self.assertEqual(_codes(self.root), [])

    def test_grade_boundaries(self):
        self.assertEqual(grade_for(85), "A")
        self.assertEqual(grade_for(84), "B")
        self.assertEqual(grade_for(50), "C")
        self.assertEqual(grade_for(49), "D")


if __name__ == "__main__":
    unittest.main()
