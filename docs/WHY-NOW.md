# 选题依据：为什么现在做 skillscope

> 本文件只回答一个问题：**「什么火」是怎么判断出来的，数据从哪来、什么时候抓的、哪些是事实、哪些是我的判断。**
> 所有 GitHub 数字都来自真实抓取，未做任何估算或补全。

## 1. 三种口径，不要混为一谈

本次同时用了三个技能，它们返回的是**三种不同口径**的数据：

| 口径 | 来源 | 抓到什么 | 本次落盘位置 |
|---|---|---|---|
| 官方增量榜 | `https://github.com/trending?since=daily` / `?since=weekly`（WebFetch 通道 A） | 仓库名、简介、语言、star 总数、fork、**官方 N stars today/this week** | `../trend-radar/snapshots/{daily,weekly}-trending-20261114-2232.json` |
| 仓库详情 | `https://api.github.com/repos/{owner}/{repo}`（本地脚本通道 B/C，25 个仓库） | license、topics、`pushed_at`、`created_at`、archived、is_fork、open_issues | `../trend-radar/snapshots/api-details-20261114-2235.json` |
| Search API 榜单 | `api.github.com/search/repositories`（另两个技能脚本） | 按 `pushed:>=DATE stars:>=10` + `sort=stars` 的**总星榜 / AI 主题总星榜**，不是增量 | `../trend-radar/data/{cn-daily,cn-weekly,ai-daily,ai-weekly}.json` |

**抓取时间（GMT+8，2026-11-14）**：Trending 页 `22:32:30`；REST 详情快照 meta 记录 `22:36:32`；Search API 榜单 `22:35` 左右。

## 2. 一次如实记录的失败

本地 `fetch_trending.py --source trending` 两次都返回「页面取到但未解析出仓库」（页面结构改版），脚本如实报失败并**未生成任何快照文件**。按流水线红线，没有退化成「凭印象列几个热门仓库」，而是改用通道 A（WebFetch 抓 Trending 页）+ 通道 B/C（REST 补详情）。`--probe` 显示本机 `api.github.com` 与 `github.com` 均可直连（HTTP 200），所以 REST 补齐走的是本地脚本，数据带 `source_url` 与 `fetched_at`。

## 3. 同一仓库的数字为什么会不一样

Trending 页与 REST 是**不同来源、不同时刻**，star 数存在真实漂移。例如：

| 仓库 | Trending 页 22:32:30 | REST 22:36:32 | 处理 |
|---|---:|---:|---|
| `backnotprop/plannotator` | 10,722 | 10,748 | 取较晚抓取时间的 10,748 |
| `ChromeDevTools/chrome-devtools-mcp` | 55,988 | 56,028 | 取 56,028 |
| `JuliusBrussee/caveman` | 119,819 | 119,838 | 取 119,838 |

引擎 `radar_engine.py` 把这些差异逐条写进 `report-daily.json` 的 `DATA_CONFLICT` 告警与每条记录的 `conflicts` 字段，**没有静默选一个**。增量 `delta_stars` 只认 Trending 页官方标注（`delta_source=trending-page`），没有出处的增量整字段剔除。

打分结果：日榜输入 40 条 → 通过 25 条、剔除 0 条、告警 15 条（全部是上述来源冲突），A=11 / B=6 / C=7 / D=1；周榜输入 36 条 → 通过 25 条，A=10。看板 DOM 桩检查 9 项全通过。完整报告见 `../trend-radar/report-daily.json`、`report-weekly.json`、`board-daily.html`、`board-weekly.html`。

## 4. 「什么火」的具体证据

**周榜（官方周增量，Trending 页 22:32:30）11 个里 8 个直接面向 AI 编码智能体 / Agent Skills / MCP 生态：**

| 仓库 | star 总数（REST 22:36:32） | 官方周增 | 方向 |
|---|---:|---:|---|
| `meta/astryx` | 27,771 | 13,375 | agent-ready 设计系统 |
| `anthropics/skills` | 194,421 | 6,169 | Agent Skills 官方仓库 |
| `milind-soni/OpenMausBot` | 22,569 | 7,763 | 带虚拟机的 bot 运行时 |
| `google/elephant-goldfish-model` | 18,894 | 5,560 | 用 agent 做设计/评审的插件 |
| `vercel-labs/agent-browser` | 50,995 | 4,360 | agent 浏览器自动化 CLI |
| `addyosmani/agent-skills` | 117,403 | 3,502 | 工程化 skills 合集 |
| `anthropics/claude-quickstarts` | 20,926 | 1,731 | agent 应用脚手架 |
| `backnotprop/plannotator` | 10,748 | 511 | agent 协作/批注工作台 |

另外 3 个不算本赛道：`sherlock-project/sherlock` 111,562 / 周增 13,364（用户名检索）、`ZhuLinsen/daily_stock_analysis` 72,138 / 周增 3,778（LLM 股票分析）、`google-deepmind/mujoco` 17,937 / 周增 1,764（物理仿真）。

**日榜（官方日增量）15 个里至少 9 个同类**：`modern-web-guidance-src` 日增 1,225、`alibaba/open-code-review` 日增 897、`chrome-devtools-mcp` 日增 673、`tradermonty/claude-trading-skills` 日增 556、`QwenLM/qwen-code` 日增 462、`backnotprop/plannotator` 日增 412、`JuliusBrussee/caveman` 日增 227、`Tencent/LoopForge` 日增 174、`ag-ui-protocol/ag-ui` 日增 9。边界较宽的 `dream-num/univer`（AI office SDK，日增 495）未计入。

**爆点特征**：`JuliusBrussee/caveman`（「省 65% token」的 skill + proxy）已达 119,838⭐，说明「agent 的上下文/成本」是能被大众立刻理解并传播的痛点，比再造一个 agent 框架更有杠杆。

## 5. 事实与判断的边界

以上第 1–4 节的数字与仓库名是**事实**（附来源与抓取时间）。下面全部是**我的判断，不是数据**：

1. skill 供给在爆炸，但「哪些 skill 值得常驻、哪些写坏了」缺一个轻量、离线、可放进 CI 的度量工具 —— 这是生态位，不是又一个 skill 合集。
2. 做 `skillscope`（治理/度量层）比做第 N 个 skill 合集更容易做出差异化；「省 token」是可传播的钩子，但用**估算 + 瘦身建议**切入，而不是和已占位的 `caveman` 正面竞争。
3. 形态选「零依赖 CLI + 自身即 Skill」：无需账号/密钥/网络、内置样本一键出报告，决定冷启动能否被复现；`--fail-under` 让它能进 CI，而不只是个一次性脚本。
4. 本工作区此前记录过「agent skills 且 star>1000 约 420 个仓库、claude code skills 且 star>500 约 383 个」的赛道拥挤度结论，那是 **2026-11-13 的 Search API 核实结果，不是本次抓取**，仅作背景参考，未当作今天的数字使用。

## 6. 决策记录

用户指令为「什么火做什么」。据此按第 4 节的最强信号（Agent Skills 生态）定选题，并按第 5 节的判断确定具体切口与形态。热度数据只用于**选题**，没有被写进工具运行时逻辑；`skillscope` 运行时不联网、不查 star。
