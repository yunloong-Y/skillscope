# 拟稿 · anthropics/skills「Show and tell」（**未发布**）

> 本页上半部分是发布说明，**不要粘贴到社区**；分隔线以下才是正文。

## 发布说明（勿粘贴）

- **目标**：`anthropics/skills` → Show and tell（分类 ID `DIC_kwDOP0wfhs4CwuU4`）。
- **状态**：2026-11-15 起草，**未发布**。对外发布前必须获得明确授权；本轮只做文案，不做任何发布动作。
- **为什么是这里**：195,079⭐、122 个 Discussions，Show and tell 开放；近期同类帖包括 #2197「Skill Lens」、#2106「skill-router-builder（带实测数据）」、#2143（macOS 同步小工具），说明「测量 + 小工具」在此分类不算跑题。
- **贡献记录**：在该仓库 **0 个 PR** → 正文里**不得自称贡献者**，只以「一个装了很多 Skill 的用户」的身份分享测量。
- **重复检查**：`repo:anthropics/skills skillscope` → 0 命中，无重复帖。
- **一社区一稿**：与已发布的 [learnharness #754](https://github.com/amosblomqvist/learnharness/discussions/754) 和 [HelloGitHub #4361](https://github.com/521xueweihan/HelloGitHub/discussions/4361) 角度完全不同 —— 那两篇是工具介绍/自荐，这一篇以**真实测量结果**为主，工具只是复现手段。若将来另找社区，需再换角度。
- **数据来源**：2026-11-15 22:0x CST 用 `skillscope` 扫本机 38 个真实 `SKILL.md` 得到的聚合统计（`/tmp/ss_real_skills.json`，临时快照）。**只公开聚合数字**，不列出任何本机私有 Skill 名称或路径。
- **发布纪律**：不求 star、不刷屏、失败不自动重试；发出后用 GraphQL 回读比对正文，并存档实际发布文本。

--- COPY BELOW ---

## Title

Show and tell: measuring what 38 installed SKILL.md files cost in context (and an offline auditor to reproduce it)

## Body

I keep installing Agent Skills and never checking what they cost. So I pointed a small offline auditor at the 38 `SKILL.md` files installed on my machine and wrote down what came back. Sharing the numbers first, because I suspect the shape of them is not unusual.

I'm not a contributor to this repo — just someone with too many skills installed.

**The measurement** (2026-11-15, 38 local `SKILL.md` files: a mix of first-party, built-in and community skills)

| | |
|---|---|
| Files scanned | 38 |
| Mean score | 87.6 / 100 |
| Grades | A 29 · B 6 · C 2 · D 1 |
| Findings | 89 |
| Estimated full-load cost | 222,102 tokens against a 20,000-token budget |

Most common findings: body too long for progressive disclosure (20), no `version` field (16), no runnable example (15), body on the long side (14), weak trigger description (11), reference paths pointing to files that don't exist (5). One file tripped the credential heuristic; on inspection it was a placeholder `api_key="..."` inside a code example — a false positive, since the rule is deliberately conservative.

**What I took from it**

- The distribution is skewed. Most skills are perfectly fine; a small handful are the ones eating the budget. A mean score is much less useful than a sorted list of the three most expensive files.
- "Long body" was the dominant issue, and it is the cheapest one to fix: move detail into `references/` and keep `SKILL.md` as a router. That is the whole progressive-disclosure idea, but it is easy to drift away from when a skill grows organically.
- Broken reference paths are quietly worse than long bodies. They don't cost context — they fail at execution time, and nothing in the score distribution warns you until the agent tries to open the file.
- A credential scanner on skill files needs to be conservative and still gets false positives. That is a reasonable trade, but it means a "D" grade is a prompt to look, not a verdict.

**Reproducing it**

[skillscope](https://github.com/yunloong-Y/skillscope) is the tool I used — a zero-dependency Python CLI that also ships as a Skill:

```bash
python3 -m skillscope demo                 # built-in sample skills, no setup
python3 -m skillscope scan ./skills --budget 20000 --html report.html
```

It applies 12 rules, computes a transparent score (`100 − Σ(error 14 / warn 7 / info 2)`), estimates context cost, names the three skills most worth slimming, and writes a standalone HTML report. `--fail-under` makes it usable in CI. MIT, offline, no telemetry.

**Honest limits**

- Token counts are a heuristic (CJK ≈ 1 token/char, everything else ≈ 4 chars/token), **not tokenizer output** and not suitable for billing. The 222k figure is a full-load upper bound: real agents keep frontmatter/description resident and load bodies on demand, so it is not what one request actually consumes.
- 38 files from one machine is a convenience sample, not a benchmark. Please don't generalize it to the ecosystem — the point is the method, not the number.
- The score is rule-based deduction, not a model judgement. The rules are opinionated and will produce false positives, as the credential example above shows.
- Nothing leaves the machine: no network calls, no accounts, no telemetry.

This is a standalone side tool, not a PR or a feature proposal for this repo. I'm mostly curious whether the shape holds on other people's collections — if you run it and get a very different distribution, I'd like to hear what your skills look like.
