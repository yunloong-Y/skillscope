---
name: skillscope
description: "Use when auditing a collection of Agent Skills, or when a coding agent feels slow because too many skills are loaded. Scores each SKILL.md, estimates context cost and shows what to slim first."
version: 0.1.0
allowed-tools: Bash,Read
---

# skillscope

一行命令给 Agent Skill 做体检：质量规则 + 上下文成本估算 + 可留存的 HTML 报告。

## When to use

- 装了一堆 skill，agent 却总唤起错的那个。
- 上下文窗口被 skill 吃掉，还没开始干活就满了。
- 想在 CI 里卡住不合格的 SKILL.md。

## Example

```bash
python3 -m skillscope demo --html report.html
python3 -m skillscope scan . --budget 8000 --fail-under 70
python3 -m skillscope rules
```

零依赖、纯本地、不联网、不需要任何账号或密钥。token 数字是启发式估算，不是 tokenizer 实测值。
