# Upstream Discussions post · English

> **Everything above the `--- COPY BELOW ---` line is publishing notes. Do NOT paste it.**

**Where to post** (check each repo's Discussion categories and CONTRIBUTING first; one post per community, never mass-post the same text):

| Target | Why it fits | Prior contribution record |
|---|---|---|
| `amosblomqvist/learnharness` | Its CONTRIBUTING explicitly asks to align in Discussions before new work — the most rule-compliant first stop | Yes (see the account's PR history) |
| `anthropics/skills` | Official Agent Skills repo | None — do not claim to be a contributor |
| `addyosmani/agent-skills` | Engineering-oriented skills collection | None |
| `anthropics/claude-quickstarts` | Agent app scaffolding | None |
| `vercel-labs/agent-browser` | Agent CLI tooling | None |
| `ChromeDevTools/chrome-devtools-mcp` | MCP ecosystem | None |

**Rules of engagement**: post under "Show and tell" / "General" (or the community's equivalent); if a repo requires an Issue or maintainer alignment first, follow that instead. No "please star", no cross-posting, no links beyond the repo and the demo. Trim the trend-data paragraph if a community dislikes meta discussion. Re-run the three commands below before posting so the numbers you quote are the ones you actually saw.

**Optional header image** (some communities strip images — it is safe to omit):
`https://github.com/yunloong-Y/skillscope/raw/main/assets/social-preview.png`

**Status**: English version **published** on 2026-11-15 10:08 CST to [amosblomqvist/learnharness discussions #754](https://github.com/amosblomqvist/learnharness/discussions/754) (category: Show and tell). The Chinese version is still an unpublished draft. The exact text that went out, plus the two adaptations made from the draft below, is archived in [`DISCUSSION-en.published.md`](DISCUSSION-en.published.md). Per the one-post-per-community rule, **do not post this English draft again to learnharness**.

--- COPY BELOW ---

## Show & tell: a one-command audit for Agent Skills (12 rules + a context budget)

Your agent didn't get dumber. Its context window got eaten.

A SKILL.md is "just Markdown", so nothing compiles it, nothing lints it, and nothing tells you what it costs. Meanwhile every skill you install gets injected into the context window. I kept running into the same three problems:

- A skill with vague triggers fires on everything, or never fires at all.
- A skill that could have been 200 lines plus a `references/` file is 2,000 lines of always-on prose.
- With ten skills loaded, I had no idea which three were worth trimming — only a vague feeling that the agent had gotten worse.

So I built **skillscope**, an offline auditor for Agent Skills:

- **12 rules** covering frontmatter, trigger descriptions, progressive disclosure, broken reference paths, near-duplicates, and leaked credentials. Scoring is transparent and boring on purpose: `100 − Σ(error 14 / warn 7 / info 2)`. A credential leak caps the grade at D regardless of score.
- **A context-cost estimate and a budget**: pass `--budget 8000` and it tells you how many tokens are left and which skills to trim first.
- **An HTML report** you can keep, diff, or attach to a review — the same format I use for upstream PR summaries.
- **CI-ready**: `--fail-under 70` exits non-zero.

It has **zero third-party dependencies, makes zero network calls, and needs no account or token**. It is both a CLI and a Skill (the repo's own `SKILL.md` passes its own audit at A/100).

```bash
git clone https://github.com/yunloong-Y/skillscope.git && cd skillscope
python3 -m skillscope demo --html report.html
python3 -m unittest discover -s tests -v          # 25 tests
```

`demo` needs no setup and ships deliberately bad sample skills. The output I get today:

```
secret-leak          D  35   3 findings
vague-helper         C  68   5 findings
device-log-analyzer  A 100   0 findings
git-commit-helper    A 100   0 findings

615 estimated tokens · 7,385 left of an 8,000 budget · 8 findings
```

**Honest limits, because this is a measurement tool**: the token count is a *heuristic estimate*, not tokenizer output — do not use it for billing. The score is rule-based deduction, not a model's judgment. It reads local files only; it does not fetch or invent star counts. If you think a rule is wrong, that is exactly the kind of issue I want.

For context on why now: on the 2026-11-14 GitHub Trending snapshot I pulled, 8 of 11 weekly and at least 9 of 15 daily entries sat in the agent / skills / MCP ecosystem, and one of the daily entries was a single-idea tool about cutting token usage. Full provenance (source, fetch time, per-repo numbers, conflicting observations) is in [`docs/WHY-NOW.md`](https://github.com/yunloong-Y/skillscope/blob/main/docs/WHY-NOW.md). That is evidence for the timing, not a claim about adoption.

I've sent 128 PRs upstream with 47 merged (verifiable via GitHub search), mostly in the "read the contributing guide first, one PR per problem" school — which is why this is a show-and-tell asking for critique rather than a launch announcement. Bilingual README, MIT, offline forever.

**What would help most**: which rule is missing, whether you'd actually gate CI on a score, and what a fair "context budget" default looks like for your setup.

--- END COPY ---
