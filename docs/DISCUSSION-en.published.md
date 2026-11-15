# Actually published text · learnharness Discussions #754

- **URL**: https://github.com/amosblomqvist/learnharness/discussions/754
- **Repository / category**: `amosblomqvist/learnharness` / Show and tell
- **Author**: `yunloong-Y`
- **Posted**: 2026-11-15T02:08:35Z (2026-11-15 10:08:35 CST, GMT+8)
- **Verified**: body fetched back via GraphQL is byte-identical to the text below (2,901 chars, 2 code blocks).

Two deliberate adaptations from the draft in `DISCUSSION-en.md`, both allowed by its publishing notes:

1. Dropped the "For context on why now" GitHub Trending paragraph — off-topic for this community and not needed to make the point.
2. Added one sentence near the top stating this is a standalone side tool with **no PR attached**, so maintainers do not read it as a feature proposal requiring alignment.

---

## Show & tell: a one-command audit for Agent Skills (12 rules + a context budget)

Your agent didn't get dumber. Its context window got eaten.

I've sent a handful of PRs here, so I'm posting this in Show and tell to ask for a critique rather than making a launch announcement. It's a small standalone side tool, not a LearnHarness change — there is no PR attached to this.

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

Across upstreams I've sent 128 PRs with 47 merged (verifiable via GitHub search), mostly in the "read the contributing guide first, one PR per problem" school. Bilingual README, MIT, offline forever.

**What would help most**: which rule is missing, whether you'd actually gate CI on a score, and what a fair "context budget" default looks like for your setup.
