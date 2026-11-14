# -*- coding: utf-8 -*-
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _run(*args):
    return subprocess.run(
        [sys.executable, "-m", "skillscope", *args],
        cwd=str(ROOT), capture_output=True, text=True,
    )


class TestCLI(unittest.TestCase):
    def test_rules_lists_catalog(self):
        result = _run("rules")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("SEC001", result.stdout)
        self.assertIn("SIZE001", result.stdout)

    def test_demo_writes_json_and_html(self):
        with tempfile.TemporaryDirectory() as tmp:
            j = Path(tmp) / "out.json"
            h = Path(tmp) / "out.html"
            result = _run("demo", "--json", str(j), "--html", str(h), "--quiet")
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(j.read_text(encoding="utf-8"))
            self.assertEqual(payload["tool"], "skillscope")
            self.assertEqual(payload["summary"]["skills"], 4)
            self.assertIn("budget_remaining", payload["summary"])
            html = h.read_text(encoding="utf-8")
            self.assertIn("<!doctype html>", html)
            self.assertIn("vague-helper", html)
            self.assertIn("SEC001", html)
            self.assertIn("启发式估算", html)

    def test_scan_single_file_dogfood(self):
        result = _run("scan", "SKILL.md")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("A", result.stdout)
        self.assertIn("100", result.stdout)

    def test_fail_under_exits_nonzero(self):
        result = _run("demo", "--fail-under", "101", "--quiet")
        self.assertEqual(result.returncode, 1)
        self.assertIn("FAIL:", result.stdout)

    def test_version(self):
        result = _run("--version")
        self.assertEqual(result.returncode, 0)
        self.assertIn("skillscope", result.stdout)


if __name__ == "__main__":
    unittest.main()
