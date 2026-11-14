# Social preview（仓库分享卡片）

仓库在 X / LinkedIn / Slack / Discord 里被转发时显示的 Open Graph 图。

## 资产

| 文件 | 用途 | 规格 |
|---|---|---|
| `assets/social-preview.png` | **英文主图**（上传这张） | 1280×640 PNG，约 147 KB |
| `assets/social-preview.zh.png` | 中文备选 / 国内社区头图 | 1280×640 PNG，约 152 KB |
| `assets/gen_social_preview.py` | 维护者重生成脚本 | 需 Pillow + macOS 系统字体 |
| `assets/banner-{light,dark}.svg` | README 双主题横幅 | SVG |
| `assets/scorecard-{light,dark}.svg` | README demo 评分卡 | SVG |

`gen_social_preview.py` 是**构建期工具**，需要 Pillow；`skillscope` CLI 本身零第三方依赖，运行时不会用到它。重生成：

```bash
python3 assets/gen_social_preview.py
```

设计按分享卡片的通行规范做的：2:1、深色底（在信息流里对比度更好）、文字全部落在中间 1100×560 安全区内、无 star 数 / 版本号 / 完整 URL（这些会过期或在缩略图里读不清）。脚本同时输出 `*.thumb.png`（400×200）用于检查缩略尺寸下的可读性。

## 上传方式

**GitHub 没有公开的 social preview 上传接口。** REST `PATCH /repos/{owner}/{repo}` 不接受图片字段，GraphQL 也没有对应 mutation；官方路径只有仓库设置页，第三方的 `gh-social-preview` 之类的工具本质也是 Playwright 浏览器自动化（需要保存网页登录会话，属于凭据，本项目不默认引入）。

因此采用「生成 + 入仓 + 半自动上传」：双击桌面 `~/Desktop/skillscope-SocialPreview.command`，脚本会打开设置页并在 Finder 里选中图片，只需把图拖进上传框再点 Save。

手动路径：`https://github.com/yunloong-Y/skillscope/settings` → Social preview → Edit → Upload an image… → Save。

## 验证

上传后到 [opengraph.dev](https://opengraph.dev/) 或 [Facebook Sharing Debugger](https://developers.facebook.com/tools/debug/) 粘贴仓库链接，确认 `og:image` 指向新图。各平台对 OG 图有缓存，X / LinkedIn 可能要等几小时；Facebook 可用 "Scrape Again" 强制刷新。

> 状态记录（2026-11-14）：图片已生成并推送到仓库，**网页端上传动作需要人工完成**——接口层面做不到，这里不把「已生成」写成「已上线」。
