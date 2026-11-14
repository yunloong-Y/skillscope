---
name: device-log-analyzer
description: "Use when the user pastes device, BLE, firmware or app logs and wants a phased root-cause timeline. Produces a full command inventory, an HTML report and concrete next checks."
version: 1.0.0
allowed-tools: Bash,Read
---

# Device Log Analyzer

长日志不靠感觉下结论。按下面六步走，细节规范在 `references/six-steps.md`。

## Workflow

1. 先给一句话结论（bottom-line），再展开。
2. 分阶段还原时间轴：每阶段列出关键时间戳 + 事件 + message。
3. 完整列出所有指令/命令，包含原始字节、状态、reason、victim 等字段。
4. 原始数据能列全量就列全量，异常项高亮，不要只给摘要。
5. 生成可留存的 HTML 报告并打开预览。
6. 结尾给根因提示 + 下一步建议，并主动询问是否要整理成排查单。

## Example

```bash
python3 -m skillscope demo --html report.html
```

任何矛盾读数（例如上报 0% 却仍是满电）必须单独点出，不得替用户做关系假设。
