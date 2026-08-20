# 前端样式约定

视觉层的稳定约定。学自 2026 年前端样式优化轮（HEAD 46e48b5 起；品牌色后续微调轮迭代）。

## 1. 品牌色（靖紫）

- **亮色**：`#5B5BD6`（quiet purple）
- **暗色**：`#9B9BF5`（lighter purple，PaperMod 深底上 AA 可读）
- 在 `assets/css/extended/blank.css` 用 CSS 变量覆盖 PaperMod 默认 `--primary`：

  ```css
  :root { --primary: #5B5BD6; }
  :root[data-theme="dark"] { --primary: #9B9BF5; }
  ```

- 同步在 `config/_default/params.toml` 的 `[params.assets] theme_color` 声明，用于浏览器 PWA 状态栏 / Android chrome。
- 暗色色值需目测复核对比度；不达标可继续往紫色高亮方向上调（见 [[current-state.md]] TODO）。
- 历史链（三步迭代）：`#9B1D20` / `#E15D68`（蔓越莓红初版，HEAD 46e48b5 起）→ `#db5079` / `#ef7fa4`（蔓越莓红调整，HEAD 2f660de 起）→ `#5B5BD6` / `#9B9BF5`（靖紫，HEAD c75c10c 起）。前两版都跑在红粉区间，反复压低饱和度、压暗色对比度到 AA；本轮换紫色系是想再次拉开色彩距离，避开「红粉」在个人博客视觉上的同质感。

## 2. 自定义样式的落点

- **站点级 CSS override 一律落在 `assets/css/extended/`**，由 PaperMod 自动合入主样式链。
- **不直接编辑 `themes/PaperMod/assets/css/`**（主题子模块，升级会被覆盖）。
- 命名习惯：`blank.css` 是历史占位文件名（已沉淀品牌色 / 字体 / 行高节奏等），新规则继续追加而非新建多个小文件，减少 HTTP 请求与心智负担。
- 增删 override 后需 `hugo` 本地预览确认 PaperMod 链路正确合并。

## 3. 首页布局由站点级 `layouts/index.html` 全权接管

- 首页改版（HEAD 95757ff 起）**撤掉 PaperMod `list.html` 的首页分支**，改用站点级 `layouts/index.html` 模板全权接管首页布局（Hugo 解析 home kind → 站点级 `index.html` 优先于主题 `list.html`）。
- 不再使用主题 home_info 渲染机制：`layouts/_partials/home_info.html` 覆盖已删除，`config/_default/languages.toml` 的 `homeInfoParams.Title/Content` 双语卡片已清除。
- 首页相关需求（卡片样式 / 双列布局 / 评论区接入 / 侧栏内容）**直接改 `layouts/index.html`** 与配套 `assets/css/extended/blank.css` 的 `.home-*` / `.spark-checkin` 规则；不要回退到 `home_info.html`，也不要在 `params.toml` 加回 `disableSpecial1stPost`（已无意义）。
- 其它页面（`/posts/`、`/about/`、`/projects/` 等）继续走主题 `themes/PaperMod/layouts/list.html`，不受本次改造影响。
- 品牌色 / 主题 CSS 变量 / 站点级 override 落点约定不变（见 §1 / §2 / §4）。

## 4. 首页任务卡视觉语言（像素描边风）

首页 `.home-spark` 卡片采用**像素描边风**——一种"游戏任务条"的硬轮廓美学。HEAD 0769320 起为游戏任务风（任务条 + 徽章 + 接取 CTA + 撕票虚线），HEAD 963a608 起精简为像素风（删 emoji / 删 CTA / 删撕票虚线）。所有规则落在 `assets/css/extended/blank.css` 与 `layouts/index.html`。

### 4.1 核心原则（硬约束）

- **不用 emoji** —— 徽章只渲染 tag 文字（`生活` / `Life` 等），不再拼接 `🏠📚🎨🏃`。emoji 与文字 tag 重复（`🏠生活` vs `生活` 二选一足够），且渲染依赖系统字体栈（macOS / Windows / Linux 颜色 emoji 渲染差异明显）；删 emoji 后跨语言锚定问题随之消失（不再需要按中文标签键锁定 emoji map）
- **不做无功能的按钮** —— 不接取任务、不打钩、不存档、不收藏、不点赞。任务卡是**只读的展示卡片**，不是交互入口。"无兑现路径的按钮就不该出现"与"无持久化的徽章（难度★/XP/成就）就不该加"是同源原则
- **方形 = 默认** —— 卡片用 `border-image` 画像素描边，但 `border-image` 与 `border-radius` 不兼容（圆角会把像素点切掉形成不可读的角）；`.home-spark / __strip / __badge` 全部显式 `border-radius: 0`，方角是这套视觉语言的几何前提
- **dashed 只用一处** —— 卡片像素描边已经是 dashed 语言，strip 底部的撕票虚线已删除。同一卡上叠两条 dashed 规则互相稀释，保留外框的像素描边作为唯一虚线语言

### 4.2 像素描边 frame

`.home-spark` 用 `border-image` 画 2px 像素描边：

```css
:root { --pix: #5B5BD6; }                    /* 亮 */
:root[data-theme="dark"] { --pix: #9B9BF5; } /* 暗 */

.home-spark {
  border: 2px solid transparent;             /* 占位，避免 border-image 推动布局 */
  border-image: repeating-linear-gradient(
    90deg,
    var(--pix) 0 6px,
    transparent 6px 11px
  ) 2;
  border-radius: 0;
  overflow: hidden;
}
```

`6px 实 / 5px 空` 的重复节奏形成"机器盖章"的像素锯齿感；`overflow: hidden` 让 strip 的彩色背景被卡片边沿裁切整齐。

`--pix` 与 `--primary` 当前值相同（亮 `#5B5BD6` / 暗 `#9B9BF5`），但保持独立 token：像素描边后续可能想单独调色（更深一点 / 偏中性灰），只动 `--pix` 不影响品牌色其他用法。

### 4.3 hover —— 虚线变实线

```css
.home-spark:hover {
  border-image: linear-gradient(var(--pix), var(--pix)) 2;
}
```

只翻 border-image，不加 transform / transition / box-shadow —— hover 是"虚线 → 实线"的二态切换，不是动效。

**没有 motion 就没有 `prefers-reduced-motion` 兜底**。HEAD 963a608 起删了 `.home-spark` 的 `@media (prefers-reduced-motion: reduce)` 块（HEAD 0769320 时那条规则只为禁用 `translateY(-2px)` 而存在）。减法原则：媒体查询的代码开销应该只用来兜底真实存在的运动，无 motion 时连规则都不该保留。

### 4.4 卡片结构

- **`.home-spark__strip` 任务条**（顶部品牌色实底）：左侧固定品牌文案 `地球ONLINE · 每日任务` / `EARTH ONLINE · DAILY QUEST`；右侧 `<time>` 本地化日期（`Jan 2` / `M月D日`，`<time datetime="...">` 保持 ISO 不变）+ `#MMDD` 任务编号（从 `YYYY-MM-DD` 去横线后 `substr 4 4` 取末 4 位）；`font-variant-numeric: tabular-nums` 让编号"机器盖章"对齐；`border-radius: 0`（§4.1 原则）；`color: var(--theme)` 让亮暗自适应（亮色白、暗色近黑），保证 brand 紫色背景下 AA 对比度
- **`.home-spark__body` 主体**（白底继承 page bg）：
  - `.home-spark__badge` 类型徽章：**纯文本 + 1px `--pix` 边框 + `--primary` 文字色**（无背景填充、无 emoji）；与卡片像素描边形成"外粗内细"的两层轮廓；`padding: 0.12em 0.55em` 紧凑；`border-radius: 0`
  - `.home-spark__title` 标题：中文走「」包裹、英文裸标题（避免英文带引号违和）；继承 `--primary` 颜色 + `text-wrap: balance`（含 `-webkit-text-wrap: balance` 兼容旧 Safari）
  - `.home-spark__task` 任务正文
  - `.home-spark__meta` 时长行：`⏱ 约15-30分钟` / `⏱ 15-30 min`，纯 inline 流动、无 flex
- **不再有 `.home-spark__cta` / `id="checkin"`** —— §4.1「不做无功能按钮」原则；`body` 结构精简为 `__badge / __title / __task / __meta` 四件套

### 4.5 任务编号的跨语言确定性

任务编号 `#MMDD` 派生自 ISO 日期 `YYYY-MM-DD` 而非显示日期，**跨语言/跨构建结果一致**。标签文字本身走 `$langKey`：`zh` 显示 `生活/学习/创造/运动`，`en` 显示 `Life/Learning/Creating/Movement`。视觉锚点不再依赖 emoji（§4.1 已删），纯文字 tag 在两种语言下都稳定。

### 4.6 空态

- 无 `$spark` 数据时渲染 `.home-spark--empty`：**保留 strip 框架但只显示品牌**，去掉右侧日期/编号（避免"今日无任务"显得空洞）；标题字号降至 1.3em 不喧宾夺主
- 守卫 `$sparkOK` 必须覆盖 `date / tag / tag.zh|en / zh|en.{title,task}` 全字段；任一缺失整段 `.spark-checkin` 不渲染（不留孤儿 giscus 评论区）

### 4.7 明确不要做的事

- **不要 emoji**：见 §4.1
- **不要做无功能的按钮**（接取 / 完成 / 收藏 / 点赞 等）：见 §4.1
- **不要重新加不会被记录的徽章机制**（难度★/XP/成就系统等）：HEAD 0769320 删除这些是因为它们无持久化、无实际兑现路径；§4.1「不做无功能按钮」是同源原则
- **不要重新加圆角**：`border-image` 与 `border-radius` 不兼容，任何对 `.home-spark / __strip / __badge` 的圆角改动都会让像素点被裁切
- **不要加撕票虚线**：外框像素描边是唯一的 dashed 语言，strip 底部撕票虚线已删
- **不要重新加 hover transform / box-shadow / transition**：hover 只翻 border-image，加这些等于重新引入 motion 与 reduced-motion 兜底，违背 §4.3 减法原则
- **不要让 tag 文字锁中文键**：emoji 锚点已删，标签文字走 `$langKey` 切换 zh/en 没有视觉副作用
- **不要回退到博客摘要风**（eyebrow + 标题 + task 的扁平布局）：任务卡视觉语言是 §3「首页布局由站点级接管」之外的稳定约定，改卡片走 §4 流程，不要简化回摘要风