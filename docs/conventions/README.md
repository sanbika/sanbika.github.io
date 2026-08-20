# 约定

编码、提交、命名等规范（稳定层）。

## 内容
- [[conventions/i18n.md|i18n]] — 双语内容、UI 文案、第三方组件语言、配置文件约定
- [[conventions/frontend-styling.md|前端样式]] — 品牌色、CSS override 落点、首页任务卡像素描边风
- [[conventions/giscus.md|Giscus 评论]] — 文章 / spark 双分类分流、`comments.giscus` / `comments.spark` 双配置源、新增评论场景的流程
- [[conventions/ci.md|CI / GitHub Actions]] — 跨 workflow 触发、permissions、workflow_dispatch
- （待补充，如 `commit-message.md`）

## 文档链接约定

文档间相互引用具体文件时，统一使用 wikilink 语法，路径相对 docs/ 根目录（例如指向 `[[architecture/overview.md]]`，从任意位置都写完整路径）。仅引用 docs/ 内已存在的文件，不留死链。文件名模式或占位符（如 `<feature>.md`、`NNNN-短标题.md`）使用行内代码，不写为 wikilink。

> 写法示例：`\[\[architecture/overview.md\]\]` 渲染为可见的 `[[architecture/overview.md]]`，避免在示例文本里被误判为真实链接。

## 清单
- （暂无）