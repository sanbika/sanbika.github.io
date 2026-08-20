# Giscus 评论约定

Giscus 接入与多分类分流的稳定约定。学自 2026 年首页改版（HEAD 95757ff 起）+ 每日打卡评论迁移（HEAD 7339b19 起）。

## 1. 两套评论场景与分类

| 场景 | 渲染位置 | 分类 | mapping | term |
|------|---------|------|---------|------|
| 文章评论 | `themes/PaperMod/layouts/_default/single.html` → `layouts/_partials/comments.html` | `General` | `pathname` | 文章 permalink 路径 |
| 首页每日打卡 | `layouts/index.html` → `layouts/_partials/spark_comments.html` | `daily-spark` | `specific` | `spark-{YYYY-MM-DD}` |

- 两套分类在 giscus 仓库侧**物理隔离**：同一篇文章 URL 永远不会出现在 daily-spark 分类下；某天的 spark 评论也永远不会出现在 General 分类下。
- 这意味着切换分类是**单向、不可逆的**：迁移前的旧 discussion 留在原分类里，迁到新分类后无法回流（见 §4）。

## 2. 配置来源分工

`config/_default/params.toml` 的 `[params.comments]` 下：

```toml
[params.comments]
  enabled = true
  provider = "giscus"
  [params.comments.giscus]    # 通用字段：repo / repoId / mapping / lang / theme / reactions…
    repo = "…"
    repoId = "…"
    category = "General"       # 文章评论的默认分类
    categoryid = "DIC_…"
    mapping = "pathname"
    lightTheme = "light"
    darkTheme = "dark_dimmed"
    reactionsEnabled = true
  [params.comments.spark]      # 首页每日打卡专属：仅分类相关
    category = "daily-spark"
    categoryid = "DIC_kwDOT2zk8c4DDbVZ"
```

- **通用字段**（repo / repoId / lang / theme / reactions）只配在 `comments.giscus`，两个 partial 都从这里读。
- **`spark` 子表只放分类相关字段**（`category` / `categoryid`）；mapping / term 在 `spark_comments.html` 模板里硬编码为 `specific` + `spark-{date}`，不进配置——它是这一类评论的固有语义，没有第二套取值。
- `comments.giscus.category` 仍保留 `General` + `categoryid`，因为 `comments.html` 用它；不要因为 `spark` 已有专属分类就把 `comments.giscus.category` 改空。

## 3. 新增第三类评论场景的流程

需要引入新分类（如「读书笔记」「项目页反馈」等）时，按顺序：

1. **giscus 仓库侧建分类** — 在 sanbika.github.io 仓库的 Discussions 分类里新增分类，记下分类名 + `categoryId`（DIC_ 开头）。
2. **`params.toml` 加配置** — 在 `[params.comments]` 下新增子表，命名沿用 `<场景名>`（小写连字符）；只放 `category` / `categoryid`，通用字段继续从 `comments.giscus` 继承。
3. **新建 partial** — 复制 `spark_comments.html` 改名为 `<场景>_comments.html`；`data-mapping` / `data-term` 按场景语义定（特定 → `specific` + 自定义 term；通用 → `pathname`）；主题切换 JS 函数名加场景前缀（如 `setSparkGiscusTheme`）避免与 `comments.html` / 其它 partial 同页时冲突。
4. **接入调用点** — 在对应 Hugo 模板里 `partial "<场景>_comments.html" (...)` 调用。
5. **同步本约定文件** — 在 §1 表格新增一行，§2 代码块加新子表示例。

> 流程顺序不能错：**先建分类，再写配置**。在 giscus 仓库侧未建分类就写 `categoryid` 会得到无效的 Giscus 嵌入（iframe 静默失败，不报错但无评论）。

## 4. 迁移历史与卫生说明

- **HEAD 95757ff**：首页改版，spark 评论首次接入，走 `comments.giscus` 的 General 分类 + `specific` mapping + `spark-<date>` term。
- **HEAD 7339b19**：spark 评论迁到独立的 `daily-spark` 分类，与文章 General 物理隔离。
- **迁移副作用**：切换前（HEAD 95757ff ~ 7339b19 之间）若有人在旧 General 分类下对 `spark-<date>` 留过评论，迁到新分类后**不会显示**——giscus 按 `category + term` 检索，原 discussion 留在 GitHub General 里无法回流到首页。本仓侧无补救动作，这部分历史评论视为放弃。
- **空 discussion 不再累积**：giscus 是懒创建——term 未匹配到 discussion 时不会预创建，只有用户首次提交评论才真正建一条 discussion。新分类下空评论区不产生任何 GitHub 节点，本仓侧无需清理。
- 历史详见 [[current-state.md]] TODO 区（giscus spark-<date> 长期累积空 discussion 条目已标 [x]）。

## 5. 已知遗留

- **两个 giscus partial 不可同时渲染在同一页面**（`comments.html` + `spark_comments.html` 的 theme 切换 JS 各有 MutationObserver，同页会冲突）。当前 home 只用 spark_comments、single 只用 comments，无同页场景。如未来要同页混用，需合并函数与 observer。详见 [[current-state.md]] TODO。
- `comments.giscus` 的 `data-lang` 条件（`cond (eq .Lang "en") "en" "zh-CN"`）对未来第三语言不健壮，详见 [[current-state.md]] TODO。