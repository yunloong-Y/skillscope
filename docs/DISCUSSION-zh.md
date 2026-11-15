# 上游 Discussions 冷启动文案 · 中文

> **`--- 以下为正文 ---` 上方是发布说明，不要一起粘贴。**

**可发的上游**（逐个先看该仓库的 Discussion 分类与 CONTRIBUTING；一社区一稿，不要群发同一段）：

| 目标 | 为什么合适 | 既有贡献记录 |
|---|---|---|
| `amosblomqvist/learnharness` | 它的 CONTRIBUTING 明确要求「新功能/新集成先在 Discussions 对齐」，最合规的第一站 | 有（见账号 PR 记录） |
| `anthropics/skills` | Agent Skills 官方仓库 | 无 —— 不要自称贡献者 |
| `addyosmani/agent-skills` | 工程化 skills 合集 | 无 |
| `anthropics/claude-quickstarts` | agent 应用脚手架 | 无 |
| `vercel-labs/agent-browser` | agent CLI 工具 | 无 |
| `ChromeDevTools/chrome-devtools-mcp` | MCP 生态 | 无 |

**发布纪律**：发在 Show and tell / General（或对应分类）；若上游要求先开 Issue 或与维护者对齐，按它的来。不求 star、不刷屏、除仓库链接和 demo 外不加外链；社群不爱元讨论时可删掉「为什么是现在」那段。发之前把下面三条命令重跑一遍，确保引用的数字是你刚看到的。

**可选头图**（部分社群会过滤图片，省略也不影响）：
`https://github.com/yunloong-Y/skillscope/raw/main/assets/social-preview.png`

**状态**：2026-11-14 拟稿，**中文版仍未发布**。英文版已于 2026-11-15 10:08 发到 [amosblomqvist/learnharness #754](https://github.com/amosblomqvist/learnharness/discussions/754)（Show and tell），实际发布正文见 [`DISCUSSION-en.published.md`](DISCUSSION-en.published.md)。按「一社区一稿」原则，**不要再向 learnharness 发中文版**；中文版留给中文社区。

--- 以下为正文 ---

## 分享一个自己写的小工具：一条命令给 Agent Skill 做体检

你的 Agent 没变笨。是它的上下文窗口被 Skill 吃满了。

`SKILL.md` 说到底「只是个 Markdown」——没有编译器，没有 linter，也没人告诉你它到底占多少上下文。可每装一个 skill，它就会被整体注入上下文窗口。我自己反复踩到三个坑：

- 触发条件写得含糊的 skill，要么什么都触发，要么永远不触发；
- 本来该写成 200 字主文件 + `references/` 渐进披露的，被写成了 2,000 行常驻长文；
- 装到十几个 skill 之后，只觉得「Agent 变笨了」，却说不出该先删哪三个。

于是写了 **skillscope**：一个纯本地的 Agent Skill 体检工具。

- **12 条规则**：frontmatter、触发描述、渐进披露、引用文件是否存在、近重复、凭据泄露等。评分刻意做得透明且无聊：`100 − Σ(error 14 / warn 7 / info 2)`；命中凭据泄露直接封顶 D，不看分数。
- **上下文成本估算 + 预算**：`--budget 8000` 会告诉你还剩多少 token、最该先给哪几个 skill 瘦身。
- **可留存 HTML 报告**：能存档、能 diff、能贴在评审里 —— 和我给上游 PR 写汇总报告用的是同一套格式。
- **可进 CI**：`--fail-under 70` 不达标就非零退出。

**零第三方依赖、零网络请求、不需要任何账号或 token**。它同时是 CLI 和 Skill（仓库根目录自己的 `SKILL.md` 自举扫描拿到 A / 100 分 / 0 问题）。

```bash
git clone https://github.com/yunloong-Y/skillscope.git && cd skillscope
python3 -m skillscope demo --html report.html
python3 -m unittest discover -s tests -v          # 25 tests
```

`demo` 零配置，内置了几个故意写坏的样本。今天实测输出：

```
级   分     Skill                          估算 tok       问题
D   35    secret-leak                    103          3
C   68    vague-helper                   47           5
A   100   device-log-analyzer            288          0
A   100   git-commit-helper              177          0
------------------------------------------------------------------------------
合计估算常驻成本 615 tok  |  预算剩余 7,385 tok  |  问题 8 条
```

**边界先说清楚，毕竟这是个度量工具**：token 是*启发式估算*，不是 tokenizer 实测值，别拿去算钱；分数是规则扣分，不是模型判断；它只读本地文件，不抓也不生成任何 star 数字。你觉得哪条规则不合理，正是我最想要的 issue。

为什么是现在：我 2026-11-14 抓的 GitHub Trending 快照里，周榜 11 个有 8 个、日榜 15 个至少 9 个落在 agent / skills / MCP 生态，日榜里还有一个只讲「省 token」这一件事的工具。完整溯源（来源、抓取时间、逐仓库数字、冲突记录）在 [`docs/WHY-NOW.md`](https://github.com/yunloong-Y/skillscope/blob/main/docs/WHY-NOW.md) —— 这只说明时机，不代表采用量。

我给上游提过 128 个 PR、合并 47 个（GitHub search 可核），习惯的是「先读贡献指南、一个 PR 只解决一个问题」那套，所以这篇是来求拍砖的 show & tell，不是发布通告。中英双 README，MIT，永远离线。

**最想听到的三件事**：还缺哪条规则、你会不会真的把分数接进 CI、以及你们那边一个合理的「上下文预算」默认值大概是多少。

--- 正文结束 ---
