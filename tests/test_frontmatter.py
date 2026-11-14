# -*- coding: utf-8 -*-
import unittest

from skillscope.frontmatter import parse


class TestFrontmatter(unittest.TestCase):
    def test_full_document(self):
        text = (
            "---\n"
            "name: my-skill\n"
            'description: "Use when the user asks for a review."\n'
            "version: 1.2.0\n"
            "allowed-tools: Bash,Read\n"
            "---\n"
            "# Body\nhello\n"
        )
        parsed = parse(text)
        self.assertIsNone(parsed.error)
        self.assertEqual(parsed.get("name"), "my-skill")
        self.assertEqual(parsed.get("description"), "Use when the user asks for a review.")
        self.assertEqual(parsed.get("allowed-tools"), ["Bash", "Read"])
        self.assertIn("# Body", parsed.body)

    def test_block_list_and_empty_value(self):
        text = "---\nname: x\ntags:\n  - alpha\n  - beta\nempty:\n---\nbody"
        parsed = parse(text)
        self.assertEqual(parsed.get("tags"), ["alpha", "beta"])
        self.assertEqual(parsed.get("empty"), [])

    def test_missing_frontmatter_is_reported_not_guessed(self):
        parsed = parse("# just a markdown file\n")
        self.assertEqual(parsed.error, "missing frontmatter")
        self.assertEqual(parsed.data, {})
        self.assertIn("just a markdown", parsed.body)

    def test_booleans_and_null(self):
        parsed = parse("---\nenabled: true\nnote: ~\n---\n")
        self.assertIs(parsed.get("enabled"), True)
        self.assertIsNone(parsed.get("note"))

    def test_bom_and_crlf(self):
        parsed = parse("\ufeff---\r\nname: crlf\r\n---\r\nbody")
        self.assertIsNone(parsed.error)
        self.assertEqual(parsed.get("name"), "crlf")


if __name__ == "__main__":
    unittest.main()
