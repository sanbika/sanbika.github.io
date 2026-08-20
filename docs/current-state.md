# 当前状态

> 高频变更的工作看板。**开始任何任务前先读这里。** 由团队维护。保持轻量——它是看板，不是叙事。

## 活跃需求
- （无）

## 任务看板
| Task | 状态 | 备注 |
|------|------|------|
| 双语国际化收尾（搜索标题 / Giscus 评论语言 / 语言切换标签 / 英文项目页 / 站点 i18n 副本） | done | 热修式迭代，无 PRD 拆分 |
| 前端样式优化（中文排版 / 首页简介 / 代码高亮 / 品牌色 / favicon / config 收敛 / 多语言 label 迁移） | done | 热修式迭代，无 PRD 拆分；HEAD commit 46e48b5 |
| 首页「今日小火花 Daily Spark」每日挑战卡片 | done | GH Actions cron + MiniMax API + bot push + 显式 `gh workflow run hugo.yml` 触部署；HEAD 6af78a1 |
| 首页改版（撤 home_info；`layouts/index.html` 双列布局；`spark_comments.html` giscus 按天独立话题 `spark-<date>`） | done | reviewer 一轮通过 + worker 小修（`time` 合法 ISO `datetime`、无数据隐藏评论区、`aria-label` 双语、CSS 清理）；HEAD 95757ff |
| 首页任务卡重设计（游戏任务风：靛紫任务条 / 类型徽章 / 接取按钮 / 撕票虚线） | done | 难度★/XP 实现后按用户要求移除（不会被记录，纯装饰无意义）；reviewer 一轮通过（对比度 AA / 空态无孤儿 giscus / 中英跨语言确定性）；HEAD 0769320 |
| 往期任务页 /quests/（按月倒序分组的历史存档 + 双语菜单第 6 项） | done | reviewer 一轮通过 + 防御加固（regex 日期 + 6 字段 isset 守卫；GitHub Discussions 搜索 URL 永不 404）；HEAD eefe0dd |

## TODO / 阻塞
- [ ] **置顶：上线前置 — GitHub 仓库 Settings → Secrets and variables → Actions 必须新增 `MINIMAX_API_KEY` secret**，然后 Actions 页手动 Run 一次 `daily-spark` workflow 验证一次 — 未配置此 secret 则 schedule 调度每日失败；这是 GitHub Actions API 密钥推送的前置条件，本地文档无法代为操作
- [x] **`daily_spark.html` 的 `isset` 守卫未覆盖 `tag` 字段** — 已随任务卡重设计（HEAD 0769320）消化：守卫并入 `layouts/index.html` 的 `$sparkOK` 并升级覆盖 `date / tag / tag.zh|en / zh|en.{title,task}` 全字段，无效数据整段隐藏 `.spark-checkin` 而非空评论区
- [ ] **仓库 60 天无 push 会停用 schedule workflow（GitHub 安全策略）** — `.github/workflows/daily-spark.yml` 当前 `schedule: cron: '10 16 * * *'`；长期闲置仓库会被自动禁用 schedule，日常 push 自愈，长期闲置（≥60 天）需在 Actions 页确认并手动 Re-enable
- [ ] **about 页邮箱占位符待本人替换** — `content/about/index.md`（`<你的邮箱>`）与 `content/about/index.en.md`（`<your email>`）
- [x] **首页 `homeInfoParams.Content` 文案已定稿（本轮）** — 中文「这里是我的自留地…」/ 英文「My corner on the web…」；写入 `config/_default/languages.toml`，提交 5e46a90
- [ ] **favicon 4 件套是 `avatar.jpg` 直接缩放占位** — `static/{favicon.ico,favicon-16x16.png,favicon-32x32.png,apple-touch-icon.png,safari-pinned-tab.svg}`；待正式 logo（圆形裁剪 + 安全区 + 透明背景）
- [ ] **暗色品牌色 `#9B9BF5` 在 PaperMod 深底上的对比度待实机确认** — `assets/css/extended/blank.css`；若 AA 不达标可继续往紫色高亮方向上调（本轮已较初版 `#E15D68` 经蔓越莓红 `#ef7fa4` 提亮，仍需目测确认）
- [ ] **`layouts/_partials/header.html` 与 `translation_list.html` 是站点级主题模板覆盖** — 升级主题子模块后必须 `diff` 复核（PaperMod 上游改动不会被本地覆盖自动跟进），本轮已将 `.Language.Label` 显式写入
- [x] **英文站列表可能较空是预期状态** — 已明确策略：内容单语为主、不追求双语全覆盖；英文站内容稀疏属预期，不要把它当 TODO 去做补齐。约定见 [[conventions/i18n.md]] §1
- [ ] **`i18n/zh-cn.yaml` 与主题源 `themes/PaperMod/i18n/zh.yaml` 字节级不一致**（line 13 尾随空白差异）— 二选一：a) 与主题字节对齐；b) 文件头加注释声明 snapshot + 同步策略
- [ ] **giscus `data-lang` 条件对"未来第三语言"不健壮** — `layouts/_partials/comments.html:13` 当前 `cond (eq .Lang "en") "en" "zh-CN"`，可改 `cond (eq .Lang "en") "en" .Lang`（前提：值是 giscus 支持的语言码）
- [ ] **Entire CLI 注入的 `Entire-Checkpoint: ...` 提交 trailer 是工具噪音** — 可在使用 Entire CLI 时关闭以保持 git log 整洁
- [x] **giscus `spark-<date>` 每天建一个 discussion 长期累积空 discussion 的卫生问题已缓解** — HEAD 7339b19 起 spark 评论迁到独立 `daily-spark` 分类 + giscus 本身是**懒创建**（term 找不到对应 discussion 时不会预创建，只有用户首次提交评论才真正建 discussion；空评论区不会留痕迹）。切换前已有人在旧 General 分类下对 `spark-<date>` 留过评论的，新分类下不会显示（giscus 按 `category + term` 检索），原 discussion 留在 GitHub General 里不再回流——这部分历史评论视为放弃，无需迁移。本仓侧不再需要做任何清理动作
- [ ] **两个 giscus partial（`comments.html` / `spark_comments.html`）不可同时渲染在同一页面** — `comments.html` 用 `setGiscusTheme` + MutationObserver，`spark_comments.html` 用 `setSparkGiscusTheme` + 各自 observer；若同页同时渲染会冲突。当前 home 只用 spark_comments、single 只用 comments，无同页场景；如未来要同页混用需合并函数与 observer
- [ ] **本地 3 个 commit 待推送（1199969 + eefe0dd + 1aadc7d）** — `1199969` 任务卡微调（HEAD 963a608 像素描边风之后的小修） + `eefe0dd` 往期任务页 `/quests/` + `1aadc7d` 首页侧栏往期任务卡 + 打卡区 GitHub 评论入口（含图）+ quests 锚点 + `:focus-visible` 补齐；等用户 `hugo server` 本地预览确认无回归后一起 push。**本地预览流程**：`hugo server`（默认 `http://localhost:1313`）+ LiveReload 自动刷新；推送前可 `git log --oneline -5` 复核三 commit 内容，wiki 链接守卫、菜单项顺序、守卫字段定义、`:focus-visible` 键盘可达与本轮 `最近变更` 条目一致
- [x] **giscus iframe 不支持上传图片 → 带图打卡走 GitHub 原生评论 ↗ 入口（工作流决策）** — 已沉淀（HEAD 1aadc7d 起）：giscus iframe 没有 GitHub 上传权限（嵌入上下文不带 GitHub 会话），无法上传本地图片；带图打卡走首页评论区下方的「在 GitHub 上评论 · 可传图 ↗」链接（GitHub Discussions 搜索 URL `discussions_q=spark-<date>`，永不 404 + 懒创建无副作用），GitHub 网页本身支持拖拽上传图片，giscus 与 GitHub Discussions 是**双向同步**的（小卡片评论 ↔ 网页 discussion 同一节点），用户在网页上传图，giscus 这边也能看到。三处入口（首页打卡区 / 侧栏往期任务卡「打卡讨论」 / `/quests/` 月份存档「打卡讨论」）走同一个搜索 URL 模式

## 最近变更

- **首页侧栏往期任务卡 + 打卡区 GitHub 评论入口（含图）+ quests 锚点 + `:focus-visible` 补齐（HEAD 1aadc7d）** `feat: 首页侧栏往期任务卡 + GitHub 评论入口（含图）+ quests 锚点 + :focus-visible 补齐`
  - ① `layouts/index.html` — 侧栏「最近文章」卡替换为「往期任务」卡：数据源 `site.Data.daily_spark_history`，与 `layouts/quests.html` 同一组预过滤（`findRE $datePattern .date` 验日期格式 + 6 字段 `isset` 全检 `date / tag / tag.{zh,en} / zh|en.{title,task}`），保证侧栏与 `/quests/` 页对脏数据的处理口径一致（任何一处数据脏两侧都安静忽略，不出现「侧栏显示了 quests 页却没有」或反之的撕裂）；`$sideItems` 在 `sort "date desc"` 后取前 7 条并排除今天（`$today := now.Format "2006-01-02"`；`where ... (ne .date $today)`），空态整卡隐藏（`{{- if $sideItems -}}` 包外层，仅 social icons 兜底，不展示空框架），每条链接走 `/quests/#spark-<date>` 锚点
  - ② `layouts/_partials/spark_comments.html` — 评论区下方新增 `<a class="spark-checkin__gh-link" href="...">在 GitHub 上评论 · 可传图 ↗ / Comment on GitHub · upload images ↗</a>`：URL 用 GitHub Discussions 搜索 `https://github.com/sanbika/sanbika.github.io/discussions?discussions_q=spark-<date>`（与 quests 页同源、永不 404、懒创建语义下空评论区无副作用），文本走模板 `cond on .Lang` 双语 fallback；这是 **giscus iframe 无 GitHub 上传权限**的替代入口——giscus 与 GitHub Discussions 双向同步，用户在 GitHub 网页拖拽传图，giscus 这边也能看到
  - ③ `layouts/quests.html` — 条目渲染改为 `<article id="spark-{{ .date }}" class="quests__item">`，配合 `assets/css/extended/blank.css` `.quests__item` 新增 `scroll-margin-top: calc(var(--header-height, 60px) + 1rem)`：sticky header 不挡锚点跳转（侧栏链接 `/quests/#spark-<date>` 精确落点）
  - ④ `assets/css/extended/blank.css` — 补齐新链接 `:focus-visible` 样式：`.spark-checkin__gh-link`（首页 GitHub 评论入口）+ `.home-side__quest-item`（侧栏往期任务链接）；沿用主题 token `--primary` `outline` + `2px offset`，与已有 `:focus-visible` 习惯一致；这是站点首次出现的「真链接」类（之前 `.spark-checkin__heading` 是 heading 不是链接），需要键盘可达轮廓
  - 关键决策：
    - **侧栏与 quests 页守卫同形** —— 同一组 `findRE` + 6 字段 `isset` 在两处模板重复声明而非抽 partial（数据小、模板逻辑已稳定），保证数据脏时两侧都安静忽略、不会出现撕裂
    - **GitHub Discussions 搜索 URL 而非直链 discussion** —— 继续走 eefe0dd 决策：搜索页永不 404 + giscus 懒创建语义下空评论区不留痕迹；同源链接到侧栏、quests 页、首页打卡区，三处入口统一收口到一个搜索 URL 模式
    - **giscus 不支持上传图片 → 走 GitHub 原生评论入口** —— giscus iframe 没有 GitHub 上传权限（嵌入上下文不带 GitHub 会话），无法上传本地图片；带图打卡走「GitHub 原生评论 ↗」链接，GitHub 网页本身支持拖拽上传图片，giscus 与 GitHub Discussions 是**双向同步**的（小卡片评论 ↔ 网页 discussion 同一节点）；这是工作流决策，详见 TODO 区 `[x]` 条目
    - **空态整卡隐藏** —— 与首页 spark 卡同形（数据无效就静默），不展示空框架，避免「侧栏永远在但内容经常空」的视觉噪音；纯 social icons 兜底
    - **`scroll-margin-top` 而非 padding-top hack** —— sticky header 的高度做安全偏移的标准做法，避免锚点跳转被 header 遮挡；用 CSS 自定义属性 `var(--header-height, 60px)` 与主题 `--header-height` 对齐
    - **侧栏「往期任务」复刻而非复引 quests 页** —— 任务卡风视觉语言（像素描边 / `--pix` token / 链接落点）已在 §4 稳定；侧栏卡片是迷你版（无标题无 meta，只日期 + 任务标题），不引入新视觉系统
  - reviewer 一轮通过 + worker 防御加固：脏数据守卫与 quests 页同形统一收口（`findRE` 日期 + 6 字段 `isset`）；`:focus-visible` 站点级真链接首次补齐（`.spark-checkin__gh-link` + `.home-side__quest-item`）；空态整卡隐藏不留框架
  - 范围严格收敛在 `layouts/index.html` / `layouts/_partials/spark_comments.html` / `layouts/quests.html` / `assets/css/extended/blank.css`；未触碰 themes 子模块 / `.gitmodules` / `.gitignore` / 数据生成（`data/daily_spark_history.json` 由现有 `daily-spark` workflow 继续维护） / 其他业务代码

- **往期任务页 /quests/（HEAD eefe0dd）** `feat: 往期任务页 /quests/ —— 历史小火花按月倒序分组存档`
  - `layouts/quests.html` (新建) — 站点级页面模板（与 `layouts/index.html` 同源覆盖逻辑），数据源 `site.Data.daily_spark_history`；**预过滤守卫**在 sort / 月份键抽取之前跑：`findRE $datePattern .date` 验日期格式（`^(19|20)\d{2}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$`，拦住 `2026-13-01` 这类宽松正则能过但 `time()` 仍崩的脏数据）+ `isset` 全检 `tag / tag.zh / tag.en / zh.title / zh.task / en.title / en.task` 六字段（与 `layouts/index.html` 的 `$sparkOK` 同形）；只有 `$clean` 入选才进入 sort + 月份键抽取
  - 渲染流程：`sort $clean "date" "desc"` → `substr .date 0 7` 抽 YYYY-MM 月份键（用 `slice` + `in` 而非 `dict` 保证 Go 迭代有序、月份天然 desc）→ 月份标题本地化（zh `2026年8月` / en `Jan 2006`，`time` 解析）→ 条目本地化日期（zh `M月D日` / en `Jan 2`，`<time datetime="...">` 保持 ISO）+ tag 徽章 + 标题（zh「」/ en 裸避免英文带引号违和）+ task 正文 + 「打卡讨论」链接
  - **「打卡讨论」链接为 GitHub Discussions 搜索 URL**：`https://github.com/sanbika/sanbika.github.io/discussions?discussions_q=spark-<date>` —— 永远命中（搜索页本身不存在该 discussion 时返回空结果、不是 404），比硬链 `https://github.com/.../discussions/<id>` 鲁棒很多；giscus 懒创建语义下空评论区本身不留痕迹，配合下来「点击 → 跳搜索」比硬链稳妥
  - `content/quests/_index.md` + `content/quests/_index.en.md` (新建) — 页面 front matter 三件套（title / `layout: quests` / description），两语共用同一 `layout` 名，不带任何正文内容
  - `config/_default/menus.zh-cn.toml` + `config/_default/menus.en.toml` — 主菜单各加第 6 项 `identifier = "quests"` / `weight = 15`（夹在 `posts=10` 与 `projects=20` 之间）；双语走各自 YAML 而非页面 i18n 副本（与 `posts` / `projects` 等其它双语页面同形）
  - `assets/css/extended/blank.css` — 新增 `/* --- Quests page --- */` 段：`.quests__title` / `__desc` / `__empty` / `__month` / `__month-title` / `__list` / `__item` / `__meta` / `__date` / `__tag` / `__item-title` / `__task` / `__discussion` 全套；`.quests__tag` 复用 `.home-spark__kicker` 的靖紫半透明色块（亮 14% / 暗 18%），全部沿用主题变量（`--primary` / `--secondary` / `--border` / `--theme`）亮暗自适应；`.quests__item` **不加 hover 背景**（整行不可点、只有「打卡讨论」链接可点，整行变色会误导）
  - 关键决策：
    - **预过滤在 sort 之前**而非渲染时跳过 —— 月份键通过 `substr .date 0 7` 抽 + `time()` 解析，Hugo 的 `time()` 对不可解析字符串**直接报错而非返回零值**；预过滤保证月份键也一定可解析，构建期不依赖 `time()` 容错
    - **GitHub Discussions 搜索 URL 而非 direct discussion URL** —— `discussions_q=spark-<date>` 是搜索查询、永不 404；giscus 懒创建语义下空评论区不留痕迹，配合下来无需任何 hydration 提前创建 discussion
    - **双语走菜单 YAML 而非页面 i18n 副本** —— 与 `posts` / `projects` 等其它双语页面同形（每语独立 `_index.md` + `layout` 同名），不专门为此页改 i18n 机制
    - **页面元文本用 `cond on .Lang` 站点级习惯** —— 「打卡讨论↗ / Check in↗」「还没有存档 / No archive yet」走模板 `cond` 不入 i18n yaml（与首页 spark 卡的「地球Online · 今日隐藏任务 / Daily Spark」「今日任务未刷新 / No quest today」同形）
  - empty 态：守卫无 `$clean` 通过时整段渲染 `<p class="quests__empty">还没有存档。 / No archive yet.</p>`，与首页 `.home-spark--empty` 风格一致
  - reviewer 一轮通过 + worker 防御加固：守卫升级覆盖 regex 日期格式 + 六字段 isset 双保险；构建期不再依赖 `time()` 容错
  - 无新增 convention —— 本轮 UI 字符串 / 菜单双语 / CSS 复用品全部走现有约定（菜单 YAML、站点级 `cond on .Lang`、theme tokens）；样式落点遵守 [[conventions/frontend-styling.md|前端样式约定]] §2（自定义 CSS override 落点 = `assets/css/extended/blank.css`）与 §1 品牌色；本页未覆写 `themes/PaperMod/` 子模块
  - 范围严格收敛在 `layouts/quests.html` / `content/quests/_index.{md,en.md}` / `config/_default/menus.{zh-cn,en}.toml` / `assets/css/extended/blank.css`；未触碰 themes 子模块 / `.gitmodules` / `.gitignore` / docs / scripts / 数据生成（`data/daily_spark_history.json` 由现有 `daily-spark` workflow 继续维护）

- **首页任务卡像素风精简（HEAD 963a608）** `style: 任务卡去装饰改像素描边风（删emoji与接取按钮，hover虚线变实线）`
  - `layouts/index.html` — 删除全部 emoji（`.home-spark__badge` 不再拼接 emoji，只渲染 tag 文字；`emojiMap` 与中文标签键锁定代码一并清除）；删除 `.home-spark__cta` 接取按钮 + `id="checkin"` 锚点；`__body` 结构精简为 `__badge / __title / __task / __meta` 四件套；`.spark-checkin` 仍跟随 `$sparkOK` 守卫，不变
  - `assets/css/extended/blank.css` — 新增 `--pix` token（与 `--primary` 共色板但保持独立，便于像素描边单独调色）；`.home-spark` 改像素描边风：`border-image: repeating-linear-gradient(90deg, var(--pix) 0 6px, transparent 6px 11px) 2` 划 2px 像素描边（**6px 实 / 5px 空** 的重复节奏），`border: 2px solid transparent` 占位避免 hover 切换时布局抖动；hover 翻成实线 `border-image: linear-gradient(var(--pix), var(--pix)) 2`——**无 transform / 无 transition / 无 box-shadow**，原 `.home-spark:hover` 的 `translateY(-2px) + box-shadow` 规则删除；同步删除 `.home-spark` 的 `@media (prefers-reduced-motion: reduce)` 块（**没有 motion 就没有 reduced-motion 兜底**）
  - `.home-spark__strip` 撕票虚线 `border-bottom: 1px dashed rgba(255,255,255,0.4)` 删除（卡片像素描边已是 dashed 语言，叠两条互相稀释；保留外框像素描边作为唯一虚线语言）；`.home-spark__badge` 改为素净 chip：`border: 1px solid var(--pix)` + 文本色 `--primary`，**无背景填充**（与卡片外粗内细两层轮廓）
  - 全卡方角（`border-image` 与 `border-radius` 不兼容，圆角会把像素点切掉形成不可读的角）——`.home-spark / __strip / __badge` 三处显式 `border-radius: 0`，strip 与 badge 同步方角
  - 关键决策：
    - **删除 CTA** —— CTA 在游戏化语境下很自然，但本卡的"接取任务"对个人博客读者无任何实际兑现路径（无持久化、无状态记录、无成就系统）；和 HEAD 0769320 删除难度★/XP 是同源原则。"没有功能的按钮就不该出现"是任务卡的硬约束
    - **删除 emoji** —— emoji 与文字 tag 重复（`🏠生活` vs `生活` 二选一足够），且 emoji 渲染依赖系统字体栈（macOS / Windows / Linux 颜色 emoji 渲染差异明显），离开 emoji 让 badge 视觉更稳。删 emoji 后跨语言锚定问题随之消失（不再需要按中文标签键锁定 emoji map）
    - **删除撕票虚线** —— 卡片已有像素描边，strip 底部的撕票虚线与之形成两条 dashed 规则，互相稀释；保留外框像素描边作为唯一 dashed 语言
    - **删除 reduced-motion 兜底** —— hover 不再有任何 motion（无 transform / 无 transition / 无 box-shadow），删约 5 行 CSS 与一条 `@media` 块；遵循"无 motion 就无 reduced-motion 兜底"的减法原则（与 §4.3 同源）
    - **`--pix` 与 `--primary` 解耦** —— 两者当前值相同（亮 `#5B5BD6` / 暗 `#9B9BF5`），但保持独立 token；后续若想给像素描边单独调色（更深一点 / 偏中性灰），只动 `--pix` 不影响品牌色其他用法
  - 同步沉淀：[[conventions/frontend-styling.md|前端样式约定]] §4「首页任务卡视觉语言」**整段重写**——删徽章 emoji 映射 / CTA / hover 上浮等描述，改为像素描边语言 +「不用 emoji、不做无功能按钮、方形 = 默认、dashed 只用一处」四条核心原则 + §4.7 明确不要做的事
  - 范围严格收敛在 `layouts/index.html` 与 `assets/css/extended/blank.css`；未触碰 themes 子模块 / `.gitmodules` / `.gitignore` / docs 其他文件 / 数据生成（`scripts/daily_spark.py` 不动）；无 PRD 拆分，热修式迭代

- **首页任务卡重设计（HEAD 0769320）** `style: 首页任务卡重设计——游戏任务风（任务条/徽章/接取按钮）`
  - `layouts/index.html` — `.home-spark` 从博客摘要风（eyebrow + tag 胶囊 + 日期 + 标题 + task + 检查评论区）整体重构为游戏任务卡：顶部 `.home-spark__strip` 任务条（左侧品牌 `地球ONLINE · 每日任务` / `EARTH ONLINE · DAILY QUEST`，右侧 `<time>` 日期 + `#MMDD` 任务编号，`tabular-nums` 让编号"机器盖章"），中间 `.home-spark__body` 放 `.home-spark__badge` 类型徽章（emoji + tag 文字，emoji 按 `tag.zh` 映射：生活🏠/学习📚/创造🎨/运动🏃）+ `.home-spark__title` 标题（中文走「」包裹、英文裸标题避免英文带引号违和）+ `.home-spark__task` 任务正文 + `.home-spark__meta` 时长行（⏱ 约15-30分钟 / 15-30 min）+ `.home-spark__cta` 接取按钮（`href="#checkin"` 锚到 `.spark-checkin`，hover 填充 brand 色）
  - 模板新增的计算：`$idRaw := replace $spark.date "-" ""` → `substr $idRaw 4 4` 取末 4 位（MMDD），跨语言/跨构建结果确定；`$emojiMap := dict "生活" "🏠" "学习" "📚" "创造" "🎨" "运动" "🏃"` 显式映射（emoji 锁定中文标签键以保持视觉锚点，标签文字走 `$langKey` 让 en 页显示 `Life/Learning/Creating/Movement`）；空态卡 `.home-spark--empty` 保留 strip 框架但去掉右侧日期/编号（避免"无任务"时显得空洞）
  - `$sparkOK` 守卫升级——覆盖 `date / tag / tag.zh|en / zh|en.{title,task}` 全字段；TODO 区"未覆盖 tag"的遗留（HEAD 6af78a1 起的）一并消化
  - `assets/css/extended/blank.css` — 全部 `.home-spark*` 重写：`.home-spark` 加 `overflow: hidden`（让 strip 的圆角自动 clip 到卡片 `--radius`，免去 strip 自身的 `border-radius`）+ hover `translateY(-2px) + box-shadow + border-color: var(--primary)` + `prefers-reduced-motion` 下禁用 transform；`.home-spark__strip` 品牌色实底 + `var(--theme)` 文字（亮暗自适应，无需 dark override）+ `border-bottom: 1px dashed rgba(255, 255, 255, 0.4)` 撕票虚线分隔；`.home-spark__badge` 纯边框胶囊（`background: var(--theme)` + `border: 1px solid var(--border)`，暗色下用 PaperMod 近黑底保持轮廓美感）；`.home-spark__title` 继承 `--primary` 颜色 + `text-wrap: balance`（含 `-webkit-text-wrap: balance` 兼容旧 Safari）；`.home-spark__cta` 圆角描边按钮，hover 填充品牌色、hover 文字用 `var(--theme)` 让 `#9B9BF5` 上的暗色文字达对比度 AA 而非不可读的白字
  - 关键决策：**难度★/XP 机制曾实现后按用户要求删除**——它们不会被真实记录（无持久化、无成就系统、无使用价值），纯属装饰性"游戏化"对个人博客读者无实际意义；保留会制造「无法兑现的承诺」并增加视觉噪音。任务卡仍以「任务条 + 类型徽章 + 接取 CTA」传达游戏风的核心审美，不再引入不会落地的徽章机制
  - reviewer 一轮通过：对比度 AA（CTA hover 暗色文字用 `var(--theme)` 而非硬编白）、空态不渲染孤儿 giscus（`$sparkOK` 失败时 `.spark-checkin` 整段不输出）、中英跨语言确定性（编号 `substr` 与 emoji map 都基于 ISO 日期或中文 tag 键，不受 `.Lang` / 字体差异影响）
  - 同步沉淀：[[conventions/frontend-styling.md|前端样式约定]] 新增 §4「首页任务卡视觉语言」（游戏任务风稳定约定：strip + badge + 「」标题 + meta + CTA + 撕票 + 空态保留框架）
  - 范围严格收敛在 `layouts/index.html` 与 `assets/css/extended/blank.css`；未触碰 themes 子模块 / `.gitmodules` / `.gitignore` / docs 其他文件

- **品牌色换为靖紫（HEAD c75c10c）** `style: 品牌色换为靖紫 #5B5BD6（暗色 #9B9BF5）`
  - `assets/css/extended/blank.css` — `--primary` 由 `#db5079` → `#5B5BD6`（亮）/ `#ef7fa4` → `#9B9BF5`（暗）；文件头注释同步改为「靖紫 / Quiet purple」并补全「亮色 quiet / 暗色 lighter, AA-readable on PaperMod dark background」描述
  - `config/_default/params.toml` — `[params.assets] theme_color` 由 `#db5079` → `#5B5BD6`
  - 背景：「蔓越莓红」路线经过两次迭代（`#9B1D20`/`#E15D68` → `#db5079`/`#ef7fa4` → `#5B5BD6`/`#9B9BF5`），不断压低饱和度、压暗色对比度到 AA；本轮换紫色系是想再次拉开色彩距离，避开「红粉」区间在个人博客视觉上的同质感
  - 同步沉淀：[[conventions/frontend-styling.md|前端样式约定]] §1（品牌色块整段重写为「靖紫」+ 历史链三步显式记录）；TODO 区暗色对比度色值同步更新为 `#9B9BF5`
  - 范围严格收敛在 `assets/css/extended/blank.css` 与 `config/_default/params.toml`；未触碰 themes 子模块 / `.gitmodules` / `.gitignore` / docs

- **今日小火花更名（HEAD e9c7954）** `chore: 今日小火花更名——地球Online · 今日隐藏任务`
  - `layouts/index.html` — 中文 headline 由「今日小火花」改为「地球Online · 今日隐藏任务」；英文 headline 仍为 `Daily Spark`（`{{- $headline := cond (eq $langKey "en") "Daily Spark" "地球Online · 今日隐藏任务" -}}`）
  - `scripts/daily_spark.py` — `SYSTEM_PROMPT` 开头从「你是「今日小火花」生成器」改为「你是「地球Online 每日隐藏任务（Daily Spark）」生成器」：把"小火花"作为别名，改成"地球Online 每日隐藏任务"作为主名、`Daily Spark` 作为括号内的英文别名；prompt 内部 "为个人博客生成每日小挑战（Daily Spark）" 措辞保留，含义不变
  - 空态文案游戏化（位于 `layouts/index.html` 的 `{{- else -}}` 分支）：标题改为「今日任务未刷新」/ `No quest today`，正文改为「今日任务打盹中，明天再来接单。」/ `The quest system is taking a day off — check back tomorrow.`
  - 关键决策：**英文名 `Daily Spark` 不变**——它是 CSS 类名（`.home-spark__*`）、数据文件名（`data/daily_spark.json`）、giscus 分类（`daily-spark`）、脚本名（`scripts/daily_spark.py`）等所有技术标识的共用基底；改英文名会引发跨文件大规模重命名，这次只动中文显示文案 + 生成器主名
  - 范围严格收敛在 `layouts/index.html` 与 `scripts/daily_spark.py`；未触碰 themes 子模块 / `.gitmodules` / `.gitignore` / docs / 其他业务代码

- **每日打卡评论迁独立 Giscus 分类（HEAD 7339b19）** `feat: 每日打卡评论迁移至独立 daily-spark discussion 分类`
  - `config/_default/params.toml` — `[params.comments]` 下新增 `[params.comments.spark]` 子表，配置 `category = "daily-spark"` / `categoryid = "DIC_kwDOT2zk8c4DDbVZ"`；`comments.giscus` 的 category/categoryId/mapping 保持 General（文章评论用）
  - `layouts/_partials/spark_comments.html` — `data-category` / `data-category-id` 改读 `$page.Site.Params.comments.spark.{category,categoryid}`（不再继承 `comments.giscus` 的 General）；`data-mapping="specific"` + `data-term="spark-{YYYY-MM-DD}"` 不变
  - **架构决策**：spark 评论从此走自己的 discussion 分类，与文章 General 分类物理隔离。两套 giscus partial（`comments.html` / `spark_comments.html`）配置来源明确分工——通用字段走 `comments.giscus`，spark 专属走 `comments.spark`；新增第三类评论场景需先在 giscus 仓库建分类、再在 `[params.comments]` 加配置
  - **卫生副作用（利好）**：giscus 是懒创建（term 未匹配到 discussion 时不预建，只有用户首次提交才建），新分类下空评论区不产生任何 GitHub discussion 节点；此前 TODO「spark-<date> 长期积累空 discussion」已缓解，无需手动清理
  - **迁移边界**：切换前（HEAD 95757ff 起的 spark-<date> 走 General 时期）若有人在旧 General 分类下对 spark 评论留过内容，迁到新分类后不会显示——giscus 按 `category + term` 检索，原 discussion 留在 GitHub General 里无法回流，视为放弃；本仓侧无补救动作
  - 同步沉淀：[[conventions/giscus.md|Giscus 评论约定]]（新建，文章 General + spark daily-spark 双分类、`comments.giscus` / `comments.spark` 双配置源、新增分类流程）
  - 范围严格收敛在 `config/_default/params.toml` 与 `layouts/_partials/spark_comments.html`；未触碰 themes 子模块 / `.gitmodules` / `.gitignore`

- **首页小火花卡片视觉打磨（HEAD 5fd24d0）** `style: 首页小火花卡片视觉打磨`
  - `layouts/index.html` — Hero 信息层级对调：每日挑战大标题（`.home-spark__title`）升为视觉主角，「今日小火花」降为 eyebrow 小标签（`.home-spark__eyebrow`）+ tag 胶囊（`.home-spark__tag`）+ 日期同排（`.home-spark__date`），删除中间层 `__sub`；日期本地化分支：`{{ if eq $langKey "en" }} {{ $dateParsed.Format "Jan 2" }} {{ else }} {{ printf "%d月%d日" $dateParsed.Month $dateParsed.Day }}`，`<time datetime="{{ $spark.date }}">` 保持 ISO 不变；「今日打卡」小标题化（`.spark-checkin__heading`）走 `.home-spark__head` 的分隔线 + eyebrow 风格
  - `assets/css/extended/blank.css` — `.home-spark__title` 加 `text-wrap: balance`（附 `-webkit-text-wrap: balance` 兼容旧 Safari）；`.home-spark__eyebrow` / `.spark-checkin__heading` 显式 `:lang(en) { text-transform: uppercase }`，中文不受影响；`.home-side` 加 `position: sticky; top: calc(var(--header-height, 60px) + var(--gap) + 0.5rem)`，`@media (max-width: 768px)` 内降级为 `position: static`（单列布局无 sticky 意义，且 top 偏移会留空白）
  - 关键决策：日期显示格式走模板分支而非 i18n key——日期是数据格式化（`time.Format` / `printf`），不属于 UI 文案翻译
  - 范围严格收敛在 `layouts/index.html` 与 `assets/css/extended/blank.css`；未触碰 themes 子模块 / `.gitmodules` / `.gitignore` / docs

- **首页改版（HEAD 95757ff）** `feat: 首页改版（每日小火花主位+每日打卡评论+侧栏文章列表）`
  - `layouts/index.html`（新建覆盖）— 站点级首页模板，双列布局 `.home-layout`（`.home-main` 主区 + `.home-side` 侧栏）；主区放 `.home-spark`（每日小火花）+ `.spark-checkin`（每日打卡 giscus），侧栏放最近文章（前 5 篇）+ social icons。Hugo 解析 home kind → 站点级 `index.html` 优先于主题 `list.html`，其它页面（`/posts/`、`/about/` 等）继续走主题 `themes/PaperMod/layouts/list.html`
  - `layouts/_partials/spark_comments.html`（新建）— giscus 按天独立话题，`data-mapping="specific"` + `data-term="spark-{YYYY-MM-DD}"`；`setSparkGiscusTheme` 与 observer 显式重命名，避免与 `comments.html` 的 `setGiscusTheme` 冲突；repo/category/lang/theme 等其它字段从 site params 继承
  - `layouts/_partials/home_info.html`（删除覆盖）— 恢复主题默认，不再用主题 home_info 渲染机制
  - `layouts/_partials/daily_spark.html`（删除覆盖）— 卡片逻辑并入新 `layouts/index.html`；守卫升级，`isset` 覆盖 `date` / `tag` / `tag.zh|en` / `zh|en.title|task`，无效数据隐藏整段 `.spark-checkin` 而非留空评论区
  - `config/_default/languages.toml` — 移除中英 `homeInfoParams.Title/Content` 双语卡片
  - `config/_default/params.toml` — 移除 `disableSpecial1stPost`（首页不再走 list.html，无需该开关）
  - `assets/css/extended/blank.css`（追加）— `.home-layout` 双列 grid（main ≥700px / side 240px）、`.home-spark*` 卡片、`.spark-checkin` 评论区容器、`.home-side*` 侧栏；窄屏单列降级；全部沿用主题 token（`--primary` / `--secondary` / `--border` / `--radius` / `--code-bg`），亮暗自适应
  - reviewer 一轮「可合并」+ worker 小修：`time` 改合法 ISO `datetime="YYYY-MM-DD"`（移除非法 `T23:59+0800` 后缀）、无数据时整段 `.spark-checkin` 不渲染而非空评论区、所有 `aria-label` 改双语 fallback（`$langKey`）、清理遗留/冗余 CSS 规则
  - 关键决策：**首页改版彻底脱离 PaperMod home_info 链路**——不再使用主题 `list.html` 的首页模板分支；改首页相关需求直接改站点级 `layouts/index.html`，不要回退到 `home_info.html` 或加回 `disableSpecial1stPost`
  - 同步沉淀：[[conventions/frontend-styling.md|前端样式约定]] §3「首页布局由站点级 `layouts/index.html` 全权接管」；TODO 区新增两条遗留（giscus 空 discussion 累积 / 两 giscus partial 不可同页）
  - 范围严格收敛在 `layouts/` / `config/_default/` / `assets/css/extended/`；未触碰 themes 子模块 / `.gitmodules` / `.gitignore` / docs

- **首页 Daily Spark 卡片上线（HEAD 6af78a1）** `feat: 首页「今日小火花 Daily Spark」每日挑战卡片`
  - `.github/workflows/daily-spark.yml`（新建） — schedule 北京时间 00:10（`cron: '10 16 * * *'` UTC）+ `workflow_dispatch`；`permissions: { contents: write, actions: write }`，因含 `gh workflow run hugo.yml` 显式触发布署
  - `scripts/daily_spark.py`（新建） — 调用 MiniMax `chatcompletion_v2` 生成中英双语小挑战（领域 生活/学习/创造/运动 ↔ Life/Learning/Creating/Movement）；模型/地址可用 repo vars `MINIMAX_MODEL` / `MINIMAX_BASE_URL` 覆盖，默认 `MiniMax-M2` / `https://api.minimaxi.com`；`validate_payload` 严格（除日期强制覆盖为今天外，其余字段失配即 fail + retry）；4 次重试 + 指数退避；atomic write（tmp + `os.replace`）；history dedup-by-date + 滚动 365 条上限
  - `data/daily_spark.json` + `data/daily_spark_history.json`（新建） — 今日卡 + 滚动历史；由 workflow 写入、提交信息 `chore: daily spark YYYY-MM-DD`
  - `layouts/_partials/daily_spark.html`（新建） — 卡片 partial，`.Lang` 切换中英 headline / tag / title / task；守卫 `(isset $spark "date") (isset $spark "zh") (isset $spark "en")`（**未覆盖 `tag`，见 TODO**）
  - `layouts/_partials/home_info.html`（站点级 PaperMod 覆盖） — 在 `{{- end -}}` 前增加一行 `{{- partial "daily_spark.html" $ -}}`，把卡片插在 home-info 之后
  - `assets/css/extended/blank.css`（追加） — `.daily-spark*` 卡片样式，全部使用主题 token（`--primary` / `--border` / `--secondary` / `--radius`），自动适配亮/暗；`__tag` 胶囊沿用品牌色 `#db5079` 边框
  - 关键决策（reviewer 两轮挑出的 critical）：**`GITHUB_TOKEN` push 不会触发其他 workflow**，因此 daily-spark 推 commit 后用 `gh workflow run hugo.yml --ref main` 显式触发布署——而不是依赖 GITHUB_TOKEN push 联动部署
  - reviewer 结论：可合并；遗留 follow-up 见 TODO 区（`MINIMAX_API_KEY` 配置 / 守卫补 `tag` / 60 天闲置 schedule 停用）
  - 同步沉淀：[[conventions/ci.md|CI / GitHub Actions 约定]]（新文件，§1 跨 workflow 触发）

- **内容策略拍板（HEAD 5e46a90）** `chore: 首页简介定稿（读书笔记与项目方向）`
  - `config/_default/languages.toml` — `homeInfoParams.Content` 中英各一段定稿
  - `docs/conventions/i18n.md` — §1「内容页面」改写：内容语言由作者每篇自主决定、单语是常态；`.en.md` 配对仅用于确实需要双语的页面；front matter 对齐约定保留（仅针对成对的页面）
  - 内容结构决策：读书笔记不设独立 section，与随笔 / 技术文同在 posts（用 tags 区分），未来若量大再议
  - 同步：TODO 区「英文站内容翻译覆盖面待补」改 [x]「已澄清策略」；范围严格收敛，未触碰业务代码 / themes 子模块 / `.gitmodules` / `.gitignore`

- **品牌色微调（HEAD 2f660de）** `fix: 品牌色改为 #db5079（暗色 #ef7fa4）` — 蔓越莓红改用 `#db5079` / `#ef7fa4`
  - `assets/css/extended/blank.css` — `--primary` 由 `#9B1D20` → `#db5079`（亮）/ `#E15D68` → `#ef7fa4`（暗）；`config/_default/params.toml` 的 `theme_color` 同步更新
  - 背景：用户对初版色不满意（亮色饱和度过高、暗色对比度临界 AA）
  - 范围严格收敛在 `assets/css/extended/blank.css` 与 `config/_default/params.toml`；未触碰其他业务代码 / themes 子模块 / `.gitmodules` / `.gitignore`
  - 同步沉淀：[[conventions/frontend-styling.md|前端样式约定]]（品牌色块整段重写 + 历史链记录）；TODO 区暗色对比度色值同步更新

- **前端样式优化（HEAD 46e48b5）** `feat: 前端样式优化（中文排版/首页简介/代码高亮/品牌色）`
  - `assets/css/extended/blank.css`（新建）— 品牌色（亮 #9B1D20 / 暗 #E15D68）、CJK 字体栈、CJK 阅读宽度（`--main-width: 760px`）、标题行高 1.4、段落间距 1.1em
  - `config/_default/languages.toml` — `languageName` → `label`（Hugo 0.164 已弃用，迁移完成）；新增中英 `homeInfoParams.Title/Content` 双语卡片
  - `config/_default/params.toml` — 新增 `ShowCodeCopyButtons = true` / `assets.favicon` 4 件套路径 / `disableSpecial1stPost = true`；`searchLimit` 移除（无效字段）
  - `config/_default/config.toml` — 收敛 `[params]` 重复段到 `params.toml`；`[markup.highlight] noClasses = false`（开启 PaperMod 自带代码配色）
  - `layouts/_partials/header.html`、`translation_list.html`（新建覆盖）— 语言切换标签改用 `.Language.Label`，依赖 `params.displayFullLangName = true`
  - `static/{favicon.ico,favicon-16x16.png,favicon-32x32.png,apple-touch-icon.png,safari-pinned-tab.svg}`（新建）— 缩放自 `static/images/avatar.jpg`，占位
  - 范围严格收敛在 `assets/` / `config/` / `layouts/` / `static/`；未触碰 themes 子模块 / `.gitmodules` / `docs` / `.gitignore`
  - reviewer 结论：无需返工，可合并；遗留排版级 nits（文件末尾换行 / `header.html` 一处尾随空格差异）见 TODO
  - 同步沉淀：[[conventions/frontend-styling.md|前端样式约定]]（品牌色 / CSS 落点）

- **i18n 收尾** `fix: 收尾双语国际化遗漏（搜索页标题 / Giscus 评论语言 / 语言切换标签 / 英文项目页 / 站点 i18n 固定翻译）`
  - `config/_default/params.toml` — 新增 `mainSections = ["posts"]`、`displayFullLangName = true`
  - `content/search.md` — 中文搜索页标题确认
  - `content/projects/sample-project.en.md`（新建）— 与中文版 front matter 字段对齐（8 项），slug 不冲突
  - `i18n/zh-cn.yaml`（新建）— 11 个 key 与主题 `themes/PaperMod/i18n/zh.yaml` 一一对应，作为站点级固定翻译防主题升级破坏 fallback 链
  - `layouts/_partials/comments.html` — giscus `data-lang` 按 `.Lang` 条件切换 `en` / `zh-CN`
  - 范围严格收敛在 `config/` / `content/` / `i18n/` / `layouts/`，未触碰 themes 子模块 / `.gitmodules` / `docs` / `.gitignore`
  - reviewer 结论：无需返工，可合并；遗留警告见 TODO 区