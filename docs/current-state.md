# 当前状态

> 高频变更的工作看板。**开始任何任务前先读这里。** 由团队维护。保持轻量——它是看板，不是叙事。

## 活跃需求
- （无）

## 任务看板
| Task | 状态 | 备注 |
|------|------|------|
| 打卡图片墙：抓取脚本重写 + 首页当日打卡图片墙 + 模型升 MiniMax-M3 + workflow discussion 事件触发（reviewer 一轮修复）+ 追加 2 个线上修复（提取源 bodyHTML→body / 推送后显式触发 hugo） | done | HEAD fde7641 已推送上线验证；reviewer 4 项（2 Critical + W1 守卫 + W2 事件过滤）全部修复于 331809f，S4/S5 留 future；2097abc + fde7641 为实跑暴露的 2 个追加 fix |
| 双语国际化收尾（搜索标题 / Giscus 评论语言 / 语言切换标签 / 英文项目页 / 站点 i18n 副本） | done | 热修式迭代，无 PRD 拆分 |
| 前端样式优化（中文排版 / 首页简介 / 代码高亮 / 品牌色 / favicon / config 收敛 / 多语言 label 迁移） | done | 热修式迭代，无 PRD 拆分；HEAD commit 46e48b5 |
| 首页「今日小火花 Daily Spark」每日挑战卡片 | done | GH Actions cron + MiniMax API + bot push + 显式 `gh workflow run hugo.yml` 触部署；HEAD 6af78a1 |
| 首页改版（撤 home_info；`layouts/index.html` 双列布局；`spark_comments.html` giscus 按天独立话题 `spark-<date>`） | done | reviewer 一轮通过 + worker 小修（`time` 合法 ISO `datetime`、无数据隐藏评论区、`aria-label` 双语、CSS 清理）；HEAD 95757ff |
| 首页任务卡重设计（游戏任务风：靛紫任务条 / 类型徽章 / 接取按钮 / 撕票虚线） | done | 难度★/XP 实现后按用户要求移除（不会被记录，纯装饰无意义）；reviewer 一轮通过（对比度 AA / 空态无孤儿 giscus / 中英跨语言确定性）；HEAD 0769320 |
| 往期任务页 /quests/（按月倒序分组的历史存档 + 双语菜单第 6 项） | done | reviewer 一轮通过 + 防御加固（regex 日期 + 6 字段 isset 守卫；GitHub Discussions 搜索 URL 永不 404）；HEAD eefe0dd |
| 本轮批量优化（B 卫生修复：zh-cn `languageCode` / giscus `data-lang` 健壮化 / i18n 字节对齐 + C 体验优化：about 邮箱替换 / 打卡 `<img>` 加 `decoding="async"` + D 收尾：fetch 脚本 S4 fullmatch + S5 `JSON_INDENT` + CATEGORY_ID 同步契约注释 / theme-drift-check workflow 上线） | done | reviewer 两轮无 Critical，13 文件改动合并结论可执行；**未 commit 待用户确认**（含 1 新建 `.github/workflows/theme-drift-check.yml`） |
| Daily Spark prompt 重写 + 分类切换（社交/健康/探索/内省）+ 历史 8 条 + 当日卡 tag 一次性语义迁移 | done | HEAD 98fa5dd / 298197e / c3fdd39（本地未推送）；reviewer 两轮：首轮 0 Critical + W1（历史 8 条全探索太单调）已由 c3fdd39 修复（08-15→健康 / 08-17→内省，逐条判断后最终分布 探索×6 / 健康×1 / 内省×1；「社交」暂无历史条目属正常）+ W2（探索/内省定义重叠）已由 c3fdd39 修复（探索=外部世界、内省=落到自己身上且伴随纸面/手上动作）；S1-S5 不采纳或留 future（S5 长度硬校验是 pre-existing 设计选择，维持现状） |

## TODO / 阻塞
- [ ] **push 前置 — 本地 main 领先 4 commit、origin/main 领先 24 commit（后者为 daily-spark / spark-checkins 两个 bot workflow 每日 commit）** — push 前必须 `git pull --rebase`，预期冲突：`data/daily_spark.json` + `data/daily_spark_history.json`（bot 在分叉窗口内持续追加）。处理约定：**冲突时以远端为准**（bot 数据更新），然后把本地 tag 迁移逻辑**重放**到远端新增的旧 tag 条目上（这些条目是分叉期间旧 prompt 生成的，会带 生活/学习/创造/运动 旧 tag；直接复用本轮逐条判断标准即可）。rebase 后新 prompt 才对 cron 生效。push 后可 `gh workflow run daily-spark.yml --ref main` 手动触发验证新 prompt 首跑；注意本仓约定：`GITHUB_TOKEN` push 不触发其他 workflow，部署需显式 `gh workflow run hugo.yml --ref main`（见 [[conventions/ci.md]] §1）
- [x] **置顶：上线前置 — GitHub 仓库 Settings → Secrets and variables → Actions 必须新增 `MINIMAX_API_KEY` secret**（已确认用户配置成功；daily-spark 08-21 / 08-22 实跑验证均生成成功；secret 推送是 GitHub Actions API 操作，本地文档无法代为完成——此条后续不会再触发，仅作历史沉淀）
- [x] **`daily_spark.html` 的 `isset` 守卫未覆盖 `tag` 字段** — 已随任务卡重设计（HEAD 0769320）消化：守卫并入 `layouts/index.html` 的 `$sparkOK` 并升级覆盖 `date / tag / tag.zh|en / zh|en.{title,task}` 全字段，无效数据整段隐藏 `.spark-checkin` 而非空评论区
- [x] **仓库 60 天无 push 会停用 schedule workflow（GitHub 安全策略）** — 风险实际解除：本仓现每日都有 daily-spark / spark-checkins 两个 writer workflow bot push（最坏情况每天 ≥ 1 次 push），远低于 60 天停用阈值；此约定本身仍然成立（[[conventions/ci.md]] §2），但"长期闲置"在本仓语境下不再是一个需要单独盯的运维风险
- [x] **about 页邮箱占位符待本人替换** — 已替换为 `sanbika2719@gmail.com`（中英两版同步，本轮 B/C 体验优化）
- [x] **首页 `homeInfoParams.Content` 文案已定稿（本轮）** — 中文「这里是我的自留地…」/ 英文「My corner on the web…」；写入 `config/_default/languages.toml`，提交 5e46a90
- [ ] **favicon 4 件套是 `avatar.jpg` 直接缩放占位** — `static/{favicon.ico,favicon-16x16.png,favicon-32x32.png,apple-touch-icon.png,safari-pinned-tab.svg}`；待正式 logo（圆形裁剪 + 安全区 + 透明背景）
- [x] **暗色品牌色 `#9B9BF5` 在 PaperMod 深底上的对比度待实机确认** — 用户实机目测确认可接受（个人博客视觉语境，非企业级 WCAG 强制场景；本轮交付即定稿，不再列入 TODO）
- [x] **`layouts/_partials/header.html` 与 `translation_list.html` 是站点级主题模板覆盖** — 已自动化：`.github/workflows/theme-drift-check.yml`（本轮新建）每周一 02:30 UTC + `workflow_dispatch` 跑一次：fetch 上游 `themes/PaperMod` → diff pinned SHA vs `origin/HEAD` 中这两处覆盖 → 有 drift 开/评论 issue（带 100 行 diff 截断）→ 无 drift 自动关闭旧提醒 issue。约定见 [[conventions/ci.md]] §3。**升级子模块时仍需人工复核**（workflow 只盯这两处，theme 其他文件的改动由 PR review 流程兜底），但"忘记 diff 这两处"不再是纯人工记忆
- [x] **英文站列表可能较空是预期状态** — 已明确策略：内容单语为主、不追求双语全覆盖；英文站内容稀疏属预期，不要把它当 TODO 去做补齐。约定见 [[conventions/i18n.md]] §1
- [x] **`i18n/zh-cn.yaml` 与主题源 `themes/PaperMod/i18n/zh.yaml` 字节级不一致**（line 13 尾随空白差异）— 选 (a) 与主题字节对齐（line 13 尾随空格），现 `diff` 输出空；选 (a) 的理由是 diff 干净利于后续 theme-drift-check 检测 / 升级时一眼能看出站点 i18n 是否漂移；snapshot 注释方案不被采纳（YAML 不接受文件头注释，会被解析为文档起始或被编辑器误识别）
- [x] **giscus `data-lang` 条件对"未来第三语言"不健壮** — `layouts/_partials/comments.html` 与 `spark_comments.html` 已统一改 `cond (eq .Lang "en") "en" (default .Lang .Site.Language.LanguageCode)`：英文强制走 `en`（giscus 大小写敏感），其余语言优先 `.Lang`（页面级最准）、缺失则回退 `Site.Language.LanguageCode`（站点级配置兜底）。副产物：`config/_default/languages.toml` `[zh-cn]` 同步新增 `languageCode = "zh-CN"`，修正了此前中文页因 `languageCode` 缺失导致 Hugo 静默回退 `defaultContentLanguage = "en"` 的 `"en-US"`、错误发出 `<html lang="en-US">`/hreflang/RSS 的潜在 bug
- [ ] **Entire CLI 注入的 `Entire-Checkpoint: ...` 提交 trailer 是工具噪音** — 可在使用 Entire CLI 时关闭以保持 git log 整洁
- [x] **giscus `spark-<date>` 每天建一个 discussion 长期累积空 discussion 的卫生问题已缓解** — HEAD 7339b19 起 spark 评论迁到独立 `daily-spark` 分类 + giscus 本身是**懒创建**（term 找不到对应 discussion 时不会预创建，只有用户首次提交评论才真正建 discussion；空评论区不会留痕迹）。切换前已有人在旧 General 分类下对 `spark-<date>` 留过评论的，新分类下不会显示（giscus 按 `category + term` 检索），原 discussion 留在 GitHub General 里不再回流——这部分历史评论视为放弃，无需迁移。本仓侧不再需要做任何清理动作
- [ ] **两个 giscus partial（`comments.html` / `spark_comments.html`）不可同时渲染在同一页面** — `comments.html` 用 `setGiscusTheme` + MutationObserver，`spark_comments.html` 用 `setSparkGiscusTheme` + 各自 observer；若同页同时渲染会冲突。当前 home 只用 spark_comments、single 只用 comments，无同页场景；如未来要同页混用需合并函数与 observer
- [x] **追加验证：链式触发未真实贴图实测** — 用户已确认「贴图 → discussion 事件 → 抓取 → commit → 显式触发 hugo → 部署」全链路实测通过；约定见 [[conventions/ci.md]] §1（不假定 `hugo.yml` 自动跟；本仓两个 writer workflow 已对齐）
- [x] **MiniMax-M3 首次生成质量观察** — 用户确认生成质量达标（中英双语 / tag 域 / 标题与任务措辞均符合预期）；无需回退 `MiniMax-M2`；daily-spark 08-21 / 08-22 实跑验证通过（MINIMAX_API_KEY secret 同步配置成功）
- [x] **`CATEGORY_ID` 字面量双份存在，改分类时两处必须同步** — 双份字面量作为 stdlib-only 权衡保留（脚本**不读 toml** 是有意取舍：避免引入 `tomllib` 依赖）。本轮 D 收尾加同步契约注释：脚本顶部 `CATEGORY_ID` 上方与 `config/_default/params.toml` 的 `comments.spark.categoryid` 上方各加一段注释互相指向，注释内显式列出"另一处位置 + 改分类必须两处同步"的契约；未来若改 giscus 分类，**先**在 GitHub Discussions 建新分类 → 拿到新 `DIC_…` → **两处同时**替换（注释会提醒）；只换一处仍会导致打卡抓取与 giscus 嵌入走不同分类、抓取的图永远不显示——这是本仓 giscus 双分类设计 [[conventions/giscus.md]] §1 / §2 带来的必然代价
- [x] **giscus iframe 不支持上传图片 → 带图打卡走 GitHub 原生评论 ↗ 入口（工作流决策）** — 已沉淀（HEAD 1aadc7d 起）：giscus iframe 没有 GitHub 上传权限（嵌入上下文不带 GitHub 会话），无法上传本地图片；带图打卡走首页评论区下方的「在 GitHub 上评论 · 可传图 ↗」链接（GitHub Discussions 搜索 URL `discussions_q=spark-<date>`，永不 404 + 懒创建无副作用），GitHub 网页本身支持拖拽上传图片，giscus 与 GitHub Discussions 是**双向同步**的（小卡片评论 ↔ 网页 discussion 同一节点），用户在网页上传图，giscus 这边也能看到。三处入口（首页打卡区 / 侧栏往期任务卡「打卡讨论」 / `/quests/` 月份存档「打卡讨论」）走同一个搜索 URL 模式

## 最近变更

- **Daily Spark prompt 重写 + 分类切换 + 历史 8 条 + 当日卡 tag 一次性语义迁移（本地未推送，HEAD 98fa5dd / 298197e / c3fdd39）** `feat: daily-spark prompt 重写 + 历史回灌防重复 + 分类切换` + `chore: daily-spark 历史 tag 一次性迁移到新分类` + `fix: reviewer 修复——历史 tag 逐条重贴（08-15→健康、08-17→内省）+ prompt 探索/内省定义去重叠`
  - **用户痛点**（为什么这一轮要改）：① 任务脱离实际做不到（"去美术馆看一次展""挑战 30 分钟冥想"这类工具体验型不适合个人博客语境）；② **重复度高**——8 条历史里 4 条「出门拍照」结构、3 条「拼贴/折纸/口袋册」手工向；高频意象集中在日落×7 / 夏日×5 / 拍照×4 / 角落×4（同一意象在历史窗口内反复命中）
  - **根因**（reviewer 与用户共同归因）：① **生成冷启动无历史回灌**——`build_user_message` 原版只发日期 + 星期，模型看不到任何已生成内容；冷启动时容易回到熟悉的"拍照 / 户外观察 / 拼贴"套路；② **prompt 无多样性约束**——`temperature=0.9` 不够，原 SYSTEM_PROMPT 只规定人设与硬约束，没禁止具体意象；③ **「创造」类同质化引力**——「创造」在「生活/学习/创造/运动」四分类里对 LLM 是高熵诱惑（"做个小手工 / 拼贴 / 折纸 / 拍个照"都在它引力范围里），让模型反复回到"动手做点东西"这条路上
  - **本轮修**（三 commit）：
    - `98fa5dd` `scripts/daily_spark.py`（唯一改业务的脚本）：
      - **SYSTEM_PROMPT 重写**：人设从「极简挑战生成器」改为**温暖生活教练**（"像朋友随口安利一个小乐子，不像布置作业"——反作业感保留在原味上 + 措辞升级）；硬约束显式列举**15 分钟 / 零成本 / 无特殊工具 / 步行可达 / 不绑定天气时段 / 无需同伴 / 安全 / 不涉医疗政治宗教 / 禁止空洞鸡汤**（"多喝水""早点睡""深呼吸感恩"这类明确禁出）；具体可执行要求"明确动作动词 + 具体对象，让人读完就知道动手做什么"；**多样性硬约束**——"不与最近已生成过的任务在主题/场景/动作/核心意象上雷同 + 换着使用不同动词和生活场景 + 不要连续围绕同一类意象"（显式禁掉「拍照记录/日落天空/拼贴组合/手工折纸/给物件命名」这些历史高频意象）
      - **分类切换**：`ALLOWED_TAGS_ZH = ("社交", "健康", "探索", "内省")` / `ALLOWED_TAGS_EN = ("Social", "Health", "Exploration", "Introspection")`——元组索引对齐（`ALLOWED_TAGS_EN[ALLOWED_TAGS_ZH.index(tag_zh)]` 反查），`validate_payload` 的 index 映射逻辑不变；分类顺序按 **外向他律→身体本能→外部观察→内在整理** 排（社交 = 与人发生轻互动 / 健康 = 身体活动或照料 / 探索 = 外部世界新发现 / 内省 = 自我整理 + 具体动作）
      - **`build_user_message` 回灌最近 7 天任务清单**：`existing_history[-7:]` 取最近 7 条按日期倒序喂给模型（`date / tag.zh / title / task` 四字段），成为多样性约束的**显式 context**——model 看到最近做过的意象，新任务就能主动避雷；这是冷启动问题的最小补丁，不需要引入向量检索或 embedding
    - `298197e` `data/daily_spark.json` + `data/daily_spark_history.json` — **历史 8 条 + 当日卡一次性语义迁移**到新分类：第一遍 best-effort 贴标（机械映射 生活→社交 / 学习→健康 / 创造→探索 / 运动→健康 / 未匹配→探索），提交 `chore: daily-spark 历史 tag 一次性迁移到新分类`。**best-effort 而非人工精修**——理由：① 内容早于新分类体系产生，旧 prompt 根本没考虑新分类，机械映射已经覆盖 80%；② history JSON 的功能是数据可视化（首页/侧栏/quests 页的消费端只显示 tag 文字），轻微误贴不影响视觉；③ 后面 c3fdd39 会做一遍人工微调补漏
    - `c3fdd39` **reviewer 一轮 + 零轮修复**：
      - **W1（历史 8 条全探索太单调）** → 逐条重贴：
        - `2026-08-15` 「水果拼盘大作战」→ 健康（对象是饮食节律，符合健康的身体活动或照料）
        - `2026-08-17` 「观察生活的隐喻」→ 内省（核心是"通勤路上观察细节 + 写一句 20 字以内解读"，对象是"自身对生活的察觉"，伴随"写一句"的具体动作，符合内省 = 落到自己身上 + 伴随纸面动作的双重约束）
        - 其余 6 条（08-16 角落 / 08-18 日落 / 08-19 夕阳光影 / 08-20 云朵命名 / 08-21 夏日胶囊拼贴 / 08-22 口袋册）维持探索
        - **最终分布**：探索×6 / 健康×1 / 内省×1；**「社交」暂无历史条目属正常**（旧 prompt 没这条引力线 + history 只有 8 条样本，未触发社交是统计上的预期，不是缺失 bug）
      - **W2（探索 / 内省定义在 prompt 中重叠）** → **沉淀判定线**（这是本轮的核心约定之一）：
        - **探索**：对象必须是**外部世界**——不熟悉的空间 / 物件 / 路径 / 小实验
        - **内省**：对象必须**落在自己身上**（昨天的一个决定 / 一种惯常反应 / 一段对话留下的余味 / 近期反复出现的小情绪）**且伴随落到纸面或手上的具体动作**（划掉 / 写一句 / 挪一挪）——**非纯书写**，与「禁止作业感」**不冲突**：前者要求内省必须伴随动作，后者禁止纯文字产出型任务；两个约束互补而非重复
        - 该判定线写入 SYSTEM_PROMPT 探索/内省定义段，并在 c3fdd39 的 commit message 显式标注，便于将来 prompt 再迭代时不被误合并回重叠定义
      - **S1-S5 不采纳或留 future**：reviewer 给的 5 项小建议中，S5（任务长度硬校验）是 pre-existing 设计选择（SYSTEM_PROMPT 已有标题 ≤8 字 / 任务 ≤40 字的软约束，校验在 `validate_payload` 之外），本轮不动以避免 scope creep；S1-S4 同样留 future
    - **前端零改动**：`layouts/index.html` / `layouts/quests.html` 对 tag 是**裸透传**（无白名单、无 enum）——读 `$spark.tag.zh` / `$spark.tag.en` 直接渲染，新分类文本无需任何模板层适配；这是 daily-spark 早期设计（HEAD 6af78a1 起）就把 tag 当纯数据而非约定的回报
    - **关联约定更新**：`[[conventions/frontend-styling.md]] §4.5 任务编号的跨语言确定性` 一处改完——"标签文字本身走 `$langKey`：`zh` 显示 `生活/学习/创造/运动`，`en` 显示 `Life/Learning/Creating/Movement`" → `zh` 显示 `社交/健康/探索/内省`，`en` 显示 `Social/Health/Exploration/Introspection`（§4.5 是描述当前生效状态，所以同步；其它历史变更记录里的旧分类列举属 changelog 式历史，按约定保留原样）
  - **关键决策**：
    - **历史 tag 是新分类体系下的 best-effort 语义贴标，而非历史重写** —— history 里的任务是旧 prompt 在旧分类下生成的，最早可追溯到 HEAD 6af78a1 起；这些内容早于新分类产生，强行"重写任务措辞以匹配新分类"会变成编辑历史数据，违反 history 文件作为"每日挑战实际产出存档"的语义；best-effort 贴标 + 人类微调（08-15 → 健康 / 08-17 → 内省）是"承认数据来自旧时代 + 当前分类是后置理解"的最诚实的处理；最终分布 探索×6 / 健康×1 / 内省×1 + 「社交」暂无，是 8 条样本上的合理结果而非异常
    - **冷启动回灌用 last-7 列表而非 embedding** —— 引入 embedding + 向量库是 50 倍工程量级的过度设计；last-7 显式列表让模型"看见"最近意象就足以规避 80% 重复（reviewer 第一轮 W1 观察到的"4 条拍照 + 3 条拼贴"问题本质是冷启动没看见历史，并不是 embedding 解决不了的问题）；当 history 涨到 30+ 条时再考虑向量相似度或 BM25（届时 365 条上限窗口里 last-30 也仍是合理选择）；本轮选择最小补丁
    - **「创造」类被「探索」类吸收而非并入** —— 在新分类里动手做点小手工 / 拼贴 / 折纸这些原本属于「创造」的内容，归到「探索」（动手做点小作品是"尝试一点小实验"的具体形式）；「创造」分类被废止而非保留为"创造 = 探索的子集"，理由是分类体系 4 项 > 5 项（用户的认知带宽）+ 「创造」边界太模糊（「创造」与「探索」在新分类里高度重叠，留着会反复触发"这该归哪"的歧义）——选择**减法**
    - **W2 沉淀为 SYSTEM_PROMPT 内部约定**而非外置 ADR —— 探索/内省判定线是 prompt 工程层面的硬约束，会被 LLM 阅读 + 反复迭代；外置 ADR 写在哪都形不成"模型能看见"的契约；写入 SYSTEM_PROMPT 探索/内省定义段 + 在 commit message 标注，是约束离它约束的对象最近的方式；本仓 prompt 后续若改动探索/内省定义，commit message 需显式说明是否动到这条判定线
  - reviewer 两轮 — **第一轮 0 Critical + W1（8 条全探索）+ W2（两类定义重叠）**，已全部修复于 c3fdd39；**第二轮通过**；S1-S5 中 S5（长度硬校验）pre-existing 设计选择不采纳维持现状，其余留 future
  - **commit 链**：`98fa5dd` → `298197e` → `c3fdd39`（本地 main tip，**未推送**）；数据冲突处理与 push 前置见 TODO 区 `[ ]` 条目
  - **范围严格收敛**：`scripts/daily_spark.py`（业务改动）+ `data/daily_spark.json` + `data/daily_spark_history.json`（历史迁移）+ `docs/current-state.md` + `docs/conventions/frontend-styling.md`（约定同步）；未触碰 themes 子模块 / `.gitmodules` / `.gitignore` / 任何 layouts / 任何 workflows；新分类对前端零侵入（layouts 对 tag 是裸透传）

- **批量优化（B 卫生修复 + C 体验优化 + D 收尾，待 commit，工作区 13 文件改动 / reviewer 两轮无 Critical）** `chore: docs/i18n/lang housekeeping + theme-drift-check workflow`
  - **B 卫生修复**（3 项，零行为变化或仅润色）：
    - `config/_default/languages.toml` — `[zh-cn]` 新增 `languageCode = "zh-CN"`（附注释：新语言须用 giscus 认识的语言码、大小写敏感、不认识会回退英文）。**副产物**：修正了中文页此前因 `languageCode` 缺失 → Hugo 静默回退 `defaultContentLanguage = "en"` → 错误发出 `<html lang="en-US">` / `hreflang="en-US"` / RSS `xml:lang="en-US"` 的潜在 bug；这一行新增顺带让中文页语言码正确
    - `layouts/_partials/comments.html` + `layouts/_partials/spark_comments.html` — giscus `data-lang` 统一改 `cond (eq .Lang "en") "en" (default .Lang .Site.Language.LanguageCode)`：英文强制 `en`（giscus 大小写敏感），其余优先 `.Lang`（页面级）、缺失回退 `Site.Language.LanguageCode`（站点级兜底）；第三语言开箱即用、giscus 认识的码走 `.Lang` 直接生效，不认识回退 `languageCode` 仍可能不被 giscus 接受——加注释提醒
    - `i18n/zh-cn.yaml` — 与主题 `themes/PaperMod/i18n/zh.yaml` **字节级对齐**（line 13 尾随空格），现 `diff` 输出空。选字节对齐而非 snapshot 注释的理由：diff 干净利于未来 theme-drift-check 检测 / 主题升级时一眼看出站点 i18n 是否漂移；YAML 不接受文件头注释，注释方案落地差
  - **C 体验优化**（2 项，肉眼可感但零行为变化）：
    - `content/about/index.md` + `content/about/index.en.md` — 邮箱占位符 `<你的邮箱>` / `<your email>` → `sanbika2719@gmail.com`（中英两版同步）
    - `layouts/index.html` + `layouts/quests.html` — 打卡 `<img>` 补 `decoding="async"`（`loading="lazy"` 与 `width`/`height` 原本已有；`decoding="async"` 让图片解码不阻塞主线程，缩略图墙场景下体验更顺）
  - **D 收尾**（3 项，spark-checkins reviewer 遗留 S4/S5 + 跨文件契约 + 新 workflow）：
    - `scripts/fetch_spark_checkins.py` —
      - **S4**：`USER_ATTACHMENT_URL_RE = re.compile(re.escape(USER_ATTACHMENT_PREFIX) + r"[0-9a-f-]+$", re.IGNORECASE)`，`fullmatch` 替代旧 `startswith` 白名单；`USER_ATTACHMENT_PREFIX` 成为全脚本**唯一真值源**（`re.escape` 防前缀里含 regex 元字符导致误匹配；字符类 `[0-9a-f-]+$` 收紧为合法 UUID/hex 末段，不再接受 `[A-Za-z0-9_-]+` 的宽松集——避免前缀后任意字符串都过，比如路径里 `assets/foo.png` 这种会被 startswith 误收但 fullmatch 直接拒掉）。reviewer 确认与 `canonical` 比对（剔除 `fetched_at` 的内容数组比较）交互正确；下次 cron 会把 JSON 里残留的脏图一次性清掉、产生一个 cleanup commit、之后恢复稳态
      - **S5**：`JSON_INDENT = 2` 抽公共常量（取代脚本各处 `indent=2` 字面量）
      - **CATEGORY_ID 同步契约注释扩写**：脚本顶部 `CATEGORY_ID` 上方新增注释显式说明"另一处在 `config/_default/params.toml` 的 `comments.spark.categoryid`、改分类必须两处同步"；`config/_default/params.toml` 的 `categoryid` 上方镜像一段反向注释
      - **新增修剪逻辑**：合并 `existing` 数组与窗口内新抓取数据时，丢弃**窗口外 + `checkins` 为空**的条目（带一行 `[spark-checkins] pruning N stale empty entries` 日志）；**窗口外且 `checkins` 非空**的条目保留（是 `/quests/` 图片墙的历史图数据源，不能误删）。reviewer 确认无副作用
    - `.github/workflows/theme-drift-check.yml`（新建）— 每周一 02:30 UTC + `workflow_dispatch`；`permissions: contents: read + issues: write`（无 push / 无 deploy）；流程：checkout 含子模块 → 在 `themes/PaperMod` 内 `git fetch` 上游 → diff pinned SHA vs `origin/HEAD` 中 `layouts/_partials/header.html` 与 `translation_list.html` 两处站点级覆盖 → 有 drift 时开 issue（标题带短 hash、body 包含站点级覆盖清单 + 100 行截断的 `diff` 输出、随机唯一 heredoc 分隔符防脚本注入），无 drift 时自动关闭旧的同主题提醒 issue；**issue 生命周期设计**（open on drift → close when upstream rebases back）而非失败 job / PR 模式，避免每次失败推 PR 噪音 + 对接无 PR review 流程
  - 关键决策：
    - **languageCode 顺带修正 en-US 潜在 bug** —— 中文页 `languageCode` 缺失时 Hugo 静默回退 `defaultContentLanguage = "en"` 的 `"en-US"`；这一轮加上 `"zh-CN"` 后，中文页 `<html lang>` / `hreflang` / RSS 全部正确发中文语言码，是 `languageCode` 顺手带来的副产物，不是显式 patch。**结论**：i18 配置里 `languageCode` 不可省（不只是 giscus 用，Hugo 整站语言码都依赖它）
    - **i18n 字节对齐而非 snapshot 注释声明** —— 选字节对齐是因为：(a) YAML 不接受文件头注释（会被解析为文档起始 / 编辑器误识别为 front matter），落地差；(b) diff 干净利于 theme-drift-check 检测 / 升级时一眼看出站点 i18n 是否漂移；(c) 字节级对齐 = 无差异 = 漂移检测零误报。snapshot 注释方案只在"主动要 drift"时才有意义（明确标记"本站有覆盖"），但本仓 i18n 是无覆盖场景（继承主题的完整 11 个 key）
    - **giscus `data-lang` 用 `default` 而非固定 zh-CN** —— 三段式 `cond (eq .Lang "en") "en" (default .Lang .Site.Language.LanguageCode)` 是"英文保底 en + 其它优先页 + 站点兜底"的最小健壮写法，未来加第三语言（ja / ko / fr…）无需再改模板、只要在 `languages.toml` 加 `languageCode` 且该码 giscus 支持即生效；不认识的语言码仍会被 giscus 静默回退英文（这是 giscus 行为，不是我们的责任）
    - **修剪只丢窗口外空条目** —— 窗口外"有人打过卡"的条目必须保留（是 `/quests/` 图片墙 / 侧栏往期任务卡的图数据源），只丢"窗口外 + 无图 + 无评论"的条目（对站点零可见影响）；合并时日志 `[spark-checkins] pruning N stale empty entries` 一次性告知运维下次 cron 会产生 cleanup commit，恢复稳态后无影响
    - **S4 fullmatch 而非 startswith** —— 旧 startswith 接受 `https://github.com/user-attachments/assets/foo.png`（前缀对了就行、`foo.png` 不是合法 hash 也会通过）；新 fullmatch `re.escape(PREFIX) + [0-9a-f-]+$` 要求前缀后必须是合法 hex/UUID 字符 + 必须以 hex/UUID 收尾，多余的 `.png` / query string / 路径片段都会被拒。`re.escape(PREFIX)` 让 PREFIX 成为唯一真值源（改一处前缀，全脚本同步）。reviewer 确认 canonical 比对交互正确
    - **theme-drift-check 用 issue 生命周期而非失败 job** —— 失败 job 模式会让 workflow 每周红一次（即使已有 issue 提醒）、需要额外 mute 机制；issue 生命周期模式：上游回到 pinned SHA → 无 drift → 自动 close 旧 issue → workflow 静默绿。无 PR review 流程对接（这是单人博客仓库），所以也不走 PR 模式
  - reviewer 两轮均无 Critical，**合并结论可执行**；本轮 13 文件改动（12 改 + 1 新建 workflow）**未 commit，待用户确认**
  - 范围严格收敛在 `config/_default/languages.toml` / `layouts/_partials/{comments,spark_comments}.html` / `i18n/zh-cn.yaml` / `scripts/fetch_spark_checkins.py` / `config/_default/params.toml` / `content/about/index.{md,en.md}` / `layouts/{index,quests}.html` / `.github/workflows/theme-drift-check.yml`；未触碰 themes 子模块 / `.gitmodules` / `.gitignore` / 其它业务代码
  - 关联：spec [[superpowers/specs/2026-08-18-spark-checkins-design.md]] §4.3 旁加注 S4 fullmatch + S5 `JSON_INDENT` 的本轮更新；plan [[superpowers/plans/2026-08-18-spark-checkins-implementation.md]] line 241 处加注 `USER_ATTACHMENT_URL_RE` fullmatch + `re.escape` 收紧。约定 [[conventions/ci.md]] 新增 §3「theme-drift-check workflow」一节记录用途 / 触发频率 / 权限边界

- **打卡图片墙 — 抓取脚本重写 + 首页当日图片墙 + 模型升 M3 + discussion 事件触发 + reviewer 一轮修复 + 2 个线上追加修复（HEAD fde7641 / 已推送 / 上线验证通过）** 最终 commit 链（远端 main tip = `fde7641`）：
  - rebase 后原 5 commit 的新 SHA：`d249c04`（fix: 抓取脚本重写）/ `07175ae`（feat: 首页打卡图片墙）/ `aede4c1`（chore: 模型 M3 + discussion 事件）/ `331809f`（fix: review 修复）/ `8d690fa`（docs: current-state 更新）；旧 SHA（`e381e18`/`60367d4`/`d82e996`/`15b7aa4`/`260b2eb`）已因 rebase 失效
  - 追加两个线上修复：`2097abc`（fix: 提取源 `bodyHTML`→`body`）+ `fde7641`（fix: spark-checkins 推送后显式触发 hugo 部署）
  - **根因（为什么之前图从来不显示）**：① 抓取脚本用 GraphQL per-date search（`spark-YYYY-MM-DD repo:… type:discussion`）90 天 90 次调用，**全部落空**（`discussion_url` 全 `null`）；GitHub search 索引对刚开的 discussion 不可靠，per-date 搜索命中率低；② 图实际贴在 discussion 的 markdown `body` 里（GitHub 把拖拽上传 inline 成 `<img src="https://github.com/user-attachments/assets/<uuid>">`），而脚本初版只读评论 `bodyHTML`；③ 首页 `layouts/index.html` **根本没消费 `data/spark_checkins.json`**，只有 `/quests/` 页消费 → 即使抓得到图也显示不出来
  - **本轮修**（七 commit，含两个线上追加）：
    - `d249c04` `scripts/fetch_spark_checkins.py`（旧 `e381e18`）— 整体重写抓取策略：
      - **按分类枚举**（`categoryId: DIC_kwDOT2zk8c4DDbVZ` 一次 GraphQL 调用拉全量）→ Python 侧按 `title in {spark-YYYY-MM-DD}` 精确匹配 + `endCursor` 翻页拿完所有 discussion，**彻底放弃 per-date search**
      - **discussion body + 评论双源提图**：先扫 `discussion.body` 拿 body 内的图，再扫每条 `comment.body` 拿评论里的图，合并去重（同一 `user-attachments/assets/<hash>` 只算一次）—— 初版用 `bodyHTML` 是错的，见 `2097abc` 坑
      - **canonical 化对比再写盘**：构造 `fetched_at = "1970-01-01T00:00:00Z"` 的副本与旧 JSON 比，**剔除抓取时间噪声**——只要内容数组无变化就**不写盘、不 commit**，消除每小时 cron 的「fetched_at 变了 → 部署一次」噪音风暴
      - **失败保数据双层防护**：单日期 partial 失败时保留旧 entries；全空 + 旧数据非空时直接拒绝写盘（`raise SystemExit`）；保持 `data/spark_checkins.json` 永远不为「已知比之前更糟」的状态
    - `07175ae` `layouts/index.html` + `assets/css/extended/blank.css`（旧 `60367d4`）— 首页 `.spark-checkin` 卡片**内**新增当日打卡缩略图墙：复用 `/quests/` 已有的 `.quests__checkins*` 类作视觉基底 + 新增 `.spark-checkin__photos` 修饰类做首页落点；**四层守卫**——`site.Data.spark_checkins` 是否存在数组 → 单条 `checkins` 字段是否存在 → 每条 `image_url` / `alt` / `comment_url` / `author` 类型守卫（必须是字符串、长度合理）→ 外链白名单校验（必须 `https://github.com/user-attachments/assets/` 开头）；任何一层失败该条静默隐藏、不打日志、不破坏页面
    - `aede4c1`（旧 `d82e996`）模型升级 + workflow 事件触发：
      - `scripts/daily_spark.py` 与 `.github/workflows/daily-spark.yml` 两处默认模型 `MiniMax-M2` → `MiniMax-M3`；repo variable `MINIMAX_MODEL` 仍可覆盖
      - `.github/workflows/spark-checkins.yml` 增加 `discussion` / `discussion_comment`（`created` / `edited` / `deleted`）事件触发；**job 级分类白名单**：仅 daily-spark 分类（`DIC_kwDOT2zk8c4DDbVZ`）触发，`issues` / 其它分类事件一律跳过——贴图后站点分钟级更新，每小时 cron 仍保留作兜底
    - `331809f`（旧 `15b7aa4`）reviewer 一轮 4 项全部修复：
      - **Critical 1**（失败清空数据）→ 双层防护（partial 保留 / 全空且旧数据非空时拒写盘）
      - **Critical 2**（索引覆盖语义）→ 抓取循环按"分类内全部 discussions → Python 标题匹配"重写，索引语义从「搜索结果必含目标」校正为「拉全量后 Python 侧过滤」
      - **W1**（模板守卫未覆盖）→ `.spark-checkin__photos` 加四层守卫含类型守卫
      - **W2**（事件过滤）→ job 级 `if: github.event.discussion.category.id == '...'` 仅 daily-spark 分类触发
      - **S1-S3**（小型代码卫生）→ 一并修复；**S4**（img 正则 hardening）/ **S5**（indent 常量抽公共）**明确跳过**，留作未来维护（reviewer 同意 scope-out）
    - `2097abc` **追加线上修复 1：GraphQL 取上传图必须用 `body` 不是 `bodyHTML`** —— 第一次实跑发现 `data/spark_checkins.json` 里 `checkins: []` 但 `discussion_url` 正常。根因：GraphQL `Discussion.bodyHTML`（渲染后 HTML）里上传图 src 是**JWT 签名的临时 URL**（`private-user-images.githubusercontent.com/...?jwt=...`，会过期），被 `user-attachments` 白名单 startswith 过滤掉；而**规范永久 URL `https://github.com/user-attachments/assets/<uuid>` 在 `body`（markdown 源）里**（GitHub 把拖拽上传 inline 成 `<img src="user-assets...">`）。修法：GraphQL selection 与 `.get()` 全部 `bodyHTML`→`body`（4 处实质 + docstring），regex 与白名单常量不变。
      - **值得沉淀的坑**：**GitHub GraphQL 取上传图要用 `body` 不是 `bodyHTML`**。`bodyHTML` 里的 `<img src>` 多半是 JWT 签名的 `private-user-images.githubusercontent.com/...` 临时 URL，过期即 404 且不在白名单；`body`（markdown 源）才是 GitHub 把上传图改写成 `user-attachments/assets/` 永久 URL 的地方。后续任何取 GitHub Discussion 图片的脚本默认走 `body`。
    - `fde7641` **追加线上修复 2：GITHUB_TOKEN push 断链需显式触发布署** —— spark-checkins 原注释错误假设「hugo.yml 监听 push 自动跟」。实跑证实 bot push 后 hugo.yml **不触发**——`GITHUB_TOKEN` push 不触发其他 workflow（这与 [[conventions/ci.md]] §1 记录的 daily-spark 约定一致，spark-checkins 当时漏用了）。修法：push 步骤输出 `pushed` 标记 + 新增 `Trigger Hugo deploy` step（`gh workflow run hugo.yml --ref main`，`GH_TOKEN: github.token`），与 daily-spark.yml 同形；无数据变化时不 commit 也不空触发部署（已 dispatch 实测：`no content changes (6 days scanned, 2 checkins), skipping commit` + 两个后续 step 正确 skipped）。
      - **值得沉淀的坑**：本仓现已**两个 writer workflow**（daily-spark + spark-checkins）都走 `gh workflow run hugo.yml --ref main` 链式触发布署；任何新增「写数据 → 推 main → 期望部署」型 workflow 都必须显式触发，**不要假定 `hugo.yml` 会自动跑**。约定见 [[conventions/ci.md]] §1
  - **上线验证结果**（HEAD `fde7641` 已推送，`hugo.yml` 已部署）：
    - 远端 `data/spark_checkins.json`：08-17 与 08-19 各 1 条 checkin（image_url 为 `8ca8afae-...` 与 `9ac5a8ef-...`，author=`sanbika`，alt 为照片文件名）
    - 线上 `/quests/` 已渲染两张 64px 缩略图（curl grep 证实 `user-attachments` 计数=2）
    - 首页 08-20 当日无带图讨论，图片墙按四层守卫静默隐藏——预期行为
    - 全链路：贴图 → discussion 事件 → 抓取 → commit → 显式触发 hugo → 部署（分钟级）；每小时 cron 兜底；无变化不产生 commit/部署
  - 关键决策：
    - **放弃 per-date search 改分类枚举** —— GitHub search 索引对刚开的 discussion 不可靠（最多滞后数小时甚至不入索引），per-date 90 次调用 0 命中；同时单次 GraphQL 调用省配额（一次拿全分类），后续窗口外的数据靠 canonical 比对天然保稳定。代价是**放弃 per-date 命中即停**的早退优化，但全量枚举的 `endCursor` 翻页 ≤ 100 条 discussion 在小仓库下成本可忽略
    - **图在 body 不在评论** —— 实测 discussion #4/#6 的图都贴在 discussion 自身的 markdown `body`（用户开 discussion 时直接拖图上传，绕过评论区上传限制），而评论里只有纯文字反馈；之前只读评论 `body` 是结构性的漏取。**双源提图**是 bug fix 而非 feature —— body 永远先扫，评论里如果有同 hash 再去重
    - **GraphQL 取图字段必须是 `body` 不是 `bodyHTML`** —— `bodyHTML` 里上传图 src 是 JWT 临时 URL（过期、不过白名单），`body`（markdown 源）才是永久 `user-attachments/assets/` URL 所在；后续任何取 GitHub Discussion 图片的脚本默认走 `body`。这是 `2097abc` 实跑暴露的、spec 与初版都未识别的坑
    - **复用 quests 视觉不新增设计语言** —— `.quests__checkins*` 系列已在 `/quests/` 跑通（HEAD 2026-08-18 起），首页 `.spark-checkin__photos` 只加修饰（页面尺寸、间距微调），不引入第二套图片/标签 CSS 变量。约定见 [[conventions/frontend-styling.md|前端样式约定]] §2（CSS override 落点 = `assets/css/extended/blank.css`）
    - **`no-change-no-commit` 让事件触发不产生部署风暴** —— canonical 化（剔除 `fetched_at`）后做内容数组比较，无变化不写盘；这是**事件触发 + 兜底 cron 共存**的关键：如果不做这层，事件触发每小时可能产 60 次内容相同的"伪变更" commit，触发 60 次 `hugo.yml` 部署。discussion event 触发 + 兜底 cron 的双轨设计见 [[conventions/ci.md|CI / GitHub Actions 约定]] §1
    - **失败宁可陈旧不清空** —— 双层防护中"全空且旧数据非空 → 拒写盘"是核心：抓取脚本失败 / GraphQL 限流 / 仓库权限失效时，**站点继续展示上一次成功抓取的图**（哪怕图已过期），总比"今天显示空"好；`fetched_at` 字段保留作为运维肉眼判断数据陈旧度的依据（不参与内容比）
    - **链式触发布署不要假定 hugo.yml 自动跟** —— `GITHUB_TOKEN` push 不触发其他 workflow 是 GitHub 平台策略（防递归），所有写数据 + 推 main 的 workflow 都必须显式 `gh workflow run hugo.yml --ref main`，且源 workflow `permissions` 含 `actions: write`。约定见 [[conventions/ci.md]] §1；本仓现两个 writer workflow（daily-spark + spark-checkins）已对齐
  - reviewer 一轮通过 + 4 项全部修复于 `331809f`（旧 `15b7aa4`）；S4/S5 明确 scope-out 留 future；`2097abc` + `fde7641` 为实跑暴露的两个追加 fix（不在原 reviewer 范围内）
  - 范围严格收敛在 `scripts/fetch_spark_checkins.py` / `layouts/index.html` / `assets/css/extended/blank.css` / `scripts/daily_spark.py` / `.github/workflows/daily-spark.yml` / `.github/workflows/spark-checkins.yml` / `docs/current-state.md`；未触碰 themes 子模块 / `.gitmodules` / `.gitignore` / 其它业务代码
  - 关联：spec [[superpowers/specs/2026-08-18-spark-checkins-design.md|2026-08-18 Spark 打卡图片墙设计 spec]] 在 §4.2 处有「实装改为 categoryId 枚举 + Python 标题匹配 + 双源提图」的更新标注（主体不动；`2097abc` body vs bodyHTML 坑见 spec 本轮的进一步说明）

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
  - `scripts/daily_spark.py`（新建） — 调用 MiniMax `chatcompletion_v2` 生成中英双语小挑战（领域 生活/学习/创造/运动 ↔ Life/Learning/Creating/Movement）；模型/地址可用 repo vars `MINIMAX_MODEL` / `MINIMAX_BASE_URL` 覆盖，默认 `MiniMax-M3` / `https://api.minimaxi.com`；`validate_payload` 严格（除日期强制覆盖为今天外，其余字段失配即 fail + retry）；4 次重试 + 指数退避；atomic write（tmp + `os.replace`）；history dedup-by-date + 滚动 365 条上限
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