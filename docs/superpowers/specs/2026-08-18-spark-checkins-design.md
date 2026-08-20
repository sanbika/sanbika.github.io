# Spark 打卡图片墙 设计 spec

**作者**：sanbika
**日期**：2026-08-18
**仓库**：`sanbika/sanbika.github.io`
**本地路径**：`C:/Dev/blog-site/`
**状态**：Draft（待用户最终审批）
**关联 spec**：`docs/superpowers/specs/2026-08-13-personal-blog-design.md`（项目根设计）

---

## 1. 目标与背景

### 1.1 目标

在博客站内（首页 + `/quests/` 列表页）展示 GitHub Discussions 里 Daily Spark 每日任务的打卡图片，让"已打卡"成为站点本身的一等公民，而不是埋在 giscus iframe 里。

### 1.2 现状（痛点）

1. **首页**：`layouts/index.html` → `layouts/_partials/spark_comments.html` 嵌入 giscus iframe + 一行 "在 GitHub 上评论 · 可传图 ↗" 链接。访客看到的是评论框 + fallback 链接，**没有任何"今天的打卡"预览**。
2. **`/quests/` 列表页**：`layouts/quests.html` 每条只显示「日期 + tag + 标题 + 任务 + 打卡讨论 ↗」四件套，**完全没有图片展示**。
3. giscus iframe 渲染包含 `<img>` 的评论是可行的，但：① 体验上像"藏在评论里"，不像"今天大家打卡了"那种墙；② iframe 自适应高度时内容溢出，访客可能根本没意识到里面有图。

### 1.3 成功标准

- 推送到 `main` → 在 `https://sanbika.github.io/quests/` 上能直接看到已打卡的图片墙（无需点击 iframe 或跳 GitHub）
- 新产生的打卡：最迟 1 小时内出现在站点上（每小时 cron 抓取 + Hugo 重新构建）
- 抓取脚本对"今天没人打卡"零写入（不产生空 commit、不触发 Pages 部署）
- 单次抓取 + 构建的 GitHub Actions 用时 < 90 秒

### 1.4 非目标

- 站内 lightbox 弹层放大（点击图片仍在 GitHub 评论页打开，保持社区归属）
- 实时增量更新（接受最迟 1 小时滞后）
- 表情包 / 文字打卡墙（只展示**带图的**评论；纯文字评论不展示）
- 多仓库 / 多源（仅本仓库 `sanbika/sanbika.github.io` 的 Discussions）
- 评论审核 / 反垃圾（依赖 GitHub Discussion 自身的权限/审核）
- **首页 spark 卡片底部不展示"今日 N 人已打卡"小条**（本期只展示 `/quests/` 列表里的图墙）

---

## 2. 设计方案

### 2.1 数据流

```
┌──────────────────────┐       ┌─────────────────────┐
│ GitHub Discussions   │       │ GitHub Discussions  │
│ (按 term: spark-     │ ───▶  │ API (GraphQL)       │
│  YYYY-MM-DD 分类)    │       │ via GITHUB_TOKEN    │
└──────────────────────┘       └─────────┬───────────┘
                                         │
                  ┌──────────────────────┴───────────────────────┐
                  │ scripts/fetch_spark_checkins.py             │
                  │   • 拉 N 天范围内的所有 spark discussion      │
                  │   • 抓 comments，提取 bodyHTML 里              │
                  │     https://github.com/user-attachments/      │
                  │     assets/* 的 <img>                          │
                  │   • 去重 + 按 date 分组 + 写 JSON               │
                  └──────────────────────┬───────────────────────┘
                                         │ 仅当新增图卡 > 0 时
                                         ▼
                  ┌──────────────────────────────────────┐
                  │ data/spark_checkins.json              │
                  │ (按 date 分组 + checkins[])            │
                  └──────────────────────┬───────────────┘
                                         │ hugo build
                                         ▼
                  ┌──────────────────────────────────────┐
                  │ public/quests/index.html              │
                  │ public/index.html (含 spark 小条)      │
                  └──────────────────────────────────────┘
```

### 2.2 三组件

| 组件 | 职责 | 文件 |
|---|---|---|
| **抓取脚本** | 拉 GitHub GraphQL、解析图片、写 JSON | `scripts/fetch_spark_checkins.py`（新增） |
| **数据文件** | 图片 URL 元数据存储 | `data/spark_checkins.json`（新增） |
| **模板** | 渲染图卡到 `/quests/` 列表页 | `layouts/quests.html`、CSS 扩展（新增） |
| **Workflow** | 定时拉取 + 触发部署 | `.github/workflows/spark-checkins.yml`（新增） |

### 2.3 为什么是构建时拉，而不是浏览器里 JS 拉

| 维度 | 构建时拉（本方案） | 浏览器 JS 拉 |
|---|---|---|
| GitHub API 配额 | 用 `secrets.GITHUB_TOKEN`，5000 点/h build 用 | 不带 PAT 60/h/visitor，5-10 个访客就把站点锁死 |
| Token 安全 | 仅在 GitHub Secrets | 必须不带 PAT，否则泄露 |
| 实时性 | 最迟 1 小时 | 实时 |
| 复杂度 | 中（脚本 + workflow） | 低（一个 JS 文件） |
| 适合 Hugo 静态站 | ⭐⭐⭐⭐⭐ | ⭐⭐ |

**结论**：静态 Hugo 站 + 已有 Actions 生态 → 构建时拉是天然搭档。1 小时滞后对每日任务的可接受。

---

## 3. 数据契约：`data/spark_checkins.json`

### 3.1 Schema

文件是 JSON 数组，按 `date` 升序排列，每条形如：

```json
[
  {
    "date": "2026-08-15",
    "fetched_at": "2026-08-18T03:17:23Z",
    "discussion_url": "https://github.com/sanbika/sanbika.github.io/discussions/42",
    "checkins": [
      {
        "author": "alice",
        "author_avatar": "https://avatars.githubusercontent.com/u/12345?v=4",
        "image_url": "https://github.com/user-attachments/assets/abc123def456",
        "alt": "水果拼盘",
        "comment_url": "https://github.com/sanbika/sanbika.github.io/discussions/42#discussioncomment-789",
        "posted_at": "2026-08-15T10:23:00Z"
      }
    ]
  },
  { "date": "2026-08-16", "fetched_at": "...", "discussion_url": null, "checkins": [] }
]
```

### 3.2 字段定义

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `date` | string `YYYY-MM-DD` | ✓ | 与 `data/daily_spark_history.json` 中的 `date` 对齐 |
| `fetched_at` | string ISO8601 UTC | ✓ | 抓取时间，用于调试 + 检测陈旧数据 |
| `discussion_url` | string \| null | ✓ | 该日期对应的 discussion 链接；找不到 discussion 时为 `null` |
| `checkins` | array | ✓ | 当日所有带图的评论（**已去重** + **仅含至少一张图**） |
| `checkins[].author` | string | ✓ | GitHub 登录名（`user.login`） |
| `checkins[].author_avatar` | string | ✓ | 头像 URL（80×80） |
| `checkins[].image_url` | string | ✓ | 用户上传图片的 URL（`github.com/user-attachments/assets/<hash>`） |
| `checkins[].alt` | string | ✓ | 图片 alt（`<img alt>` 字段或文件名回退） |
| `checkins[].comment_url` | string | ✓ | 评论锚链接（新标签页打开，跳到 GitHub） |
| `checkins[].posted_at` | string ISO8601 UTC | ✓ | 评论发布时间 |

### 3.3 边界情况

| 场景 | 处理 |
|---|---|
| 当天没有 discussion | `discussion_url: null`，`checkins: []` |
| discussion 存在但全部评论无图 | `checkins: []` |
| 同一条评论有多张图 | 拆成多条 `checkins` 项（一条评论多图），共享 author/comment_url |
| 用户删了评论/图 | 下次抓取自动消失（不报错；hugo build 重新生成产物） |
| 用户改了 GitHub 登录名 | `author` 用最新值；不保留历史映射 |
| `bodyHTML` 里有 `![...](http://evil.com/x.png)` 外链图 | **不抓取**；只接受 `github.com/user-attachments/assets/*` 域 |
| 表情包 / GitHub emoji `<img>` | 跳过（GitHub emoji URL 不在 user-attachments/assets 域） |

### 3.4 与现有 data 文件的关系

- `data/daily_spark_history.json` 是任务清单（哪一天有什么任务）
- `data/spark_checkins.json` 是打卡图片墙（那一天大家传了什么图）
- 两者**通过 `date` 字段对齐**，但**不合并** —— 它们是独立的数据源，由不同 workflow 维护：
  - `daily-spark.yml` 写 `daily_spark.json` + `daily_spark_history.json`
  - `spark-checkins.yml`（新）写 `spark_checkins.json`

### 3.5 文件大小估算

每条 checkin ≈ 200 字节（URL 主体），365 天 × 平均 3 人打卡 × 200B ≈ **220 KB**。远低于 Hugo 构建成本忽略线。

---

## 4. 抓取逻辑（`scripts/fetch_spark_checkins.py`）

### 4.1 抓取范围

- **向后抓取窗口**：90 天（每天 task 大约产生 0-10 条评论带图）
- **窗口起点**：从 `data/daily_spark_history.json` 中最近的 `date` 倒推 90 天；如果 history 为空，从今天倒推 90 天
- **窗口终点**：今天（含）
- **理由**：窗口外的老图保留上次抓取结果，不重复拉（GraphQL search 限额宝贵）

### 4.2 GraphQL 查询

```graphql
query SparkDiscussions($query: String!, $first: Int!) {
  search(query: $query, type: DISCUSSION, first: $first) {
    nodes {
      ... on Discussion {
        number
        url
        bodyHTML
        createdAt
        comments(first: 50) {
          totalCount
          nodes {
            id
            url
            bodyHTML
            createdAt
            author { login avatarUrl(size: 80) }
          }
        }
      }
    }
  }
}
```

`$query` 模板：`"spark-YYYY-MM-DD repo:sanbika/sanbika.github.io type:discussion"` 多个日期**合并一次请求**（用 OR）以减少 API 节点消耗。**注意**：GitHub search 不支持 OR 日期精确匹配 → 改成"按日期分多次，每次 1 天"，90 天 = 90 次 GraphQL 调用，每次约 5 节点，仍在 5000 点/小时范围内。

> **实施时再优化**：先用"每天 1 次"实现，profile 后再考虑批量。

> **2026-08-20 实装更新**：spec §4.2 的 per-date search 在实装中**未生效**——`spark-YYYY-MM-DD repo:… type:discussion` GraphQL search 90 天 90 次调用全部 `nodes: []` 命中（`discussion_url` 全 `null`），GitHub search 索引对新开 discussion 不可靠是根因。实装改为「`categoryId: DIC_kwDOT2zk8c4DDbVZ` 一次拉全量分类 discussions + Python 侧 `title in {spark-YYYY-MM-DD}` 精确匹配 + `endCursor` 翻页」+「discussion body + 评论双源提图」（先扫 `discussion.bodyHTML`、再扫每条 `comment.bodyHTML`、按 `image_url` 去重）。Canonical 化对比（剔除 `fetched_at`）+ 失败保数据双层防护（partial 保留 / 全空且旧数据非空时拒写盘）一并加进。Spec §3 / §4.1 / §4.3 / §4.4 主体逻辑未变，本次只是把"per-date search + 仅评论 bodyHTML"的实现细节替换为上述方案。详见 [[current-state.md]] 最近变更「打卡图片墙」条目（HEAD 15b7aa4 / 未推送）。

### 4.3 图片提取规则

从 `comment.bodyHTML` 提取 `<img>`：
1. 正则匹配 `<img[^>]*src="([^"]+)"[^>]*>` 拿到 `src`
2. **白名单校验**：`src` 必须以 `https://github.com/user-attachments/assets/` 开头（GitHub 评论里 markdown 图片 `![](url)` 渲染时会被改成 user-uploaded 形式）
3. **去重**：`src` 在同一 `checkins` 数组内去重
4. `alt` 提取：`<img alt="...">`，否则用 URL 末段 hash 前 8 位
5. 每张图对应一条 `checkins` 项，`comment_url` 复用同一评论的 URL

### 4.4 写盘策略

- **原子写**：先写 `data/spark_checkins.json.tmp`，再 `os.replace` 覆盖
- **顺序**：始终按 `date` 升序写入（保证 JSON 稳定 → git diff 友好）
- **空态写入**：当天无图时**仍然写入**该日期的 `{checkins: []}` 项（让站点知道"今天没人打卡"，下次跳过抓取）
- **窗口外日期**：保留历史值（合并 `existing` 数组里窗口外的部分 + 新窗口内的部分）

### 4.5 错误处理与重试

- 网络/HTTP 错误：`MAX_ATTEMPTS = 4`，退避 10s/20s/40s（与 `daily_spark.py` 一致）
- GraphQL 200 但有 `errors`：抛错重试
- 单天抓取失败：跳过该日期、保留上次值（不阻塞其他日期）
- 全部失败：抛 RuntimeError，exit 2（CI 会标记为失败，但 `data/spark_checkins.json` 不变）

### 4.6 CLI 行为

```bash
python3 scripts/fetch_spark_checkins.py
# 读取 GITHUB_TOKEN env
# 拉取 → 写 JSON → exit 0 / 1 / 2

# 可选 flag（v2 再加，v1 不实现）：
#   --dry-run    拉取但不写文件
#   --since 7d   自定义窗口
```

### 4.7 依赖

- Python 3.11 stdlib only（与 `daily_spark.py` 一致）
- 不引入 `requests` / `PyYAML` 等依赖

---

## 5. 模板与样式

### 5.1 `layouts/quests.html` 改动

在每个 `__item` 内、`<a class="quests__discussion">` **之前**插入图卡墙：

```go-html-template
{{- /* 打卡图片墙: 仅当 data.spark_checkins 中存在该日期时渲染. */ -}}
{{- $matching := where site.Data.spark_checkins "date" .date -}}
{{- if gt (len $matching) 0 -}}
  {{- $checkins := index (index $matching 0) "checkins" -}}
  {{- if gt (len $checkins) 0 -}}
    <ul class="quests__checkins" aria-label="{{ cond (eq $langKey "en") "Check-ins" "今日打卡" }}">
      {{- range $checkins -}}
        <li class="quests__checkin">
          <a href="{{ .comment_url }}" target="_blank" rel="noopener" aria-label="{{ .author }}">
            <img loading="lazy" src="{{ .image_url }}" alt="{{ .alt }}" />
            <span class="quests__checkin-author">{{ .author }}</span>
          </a>
        </li>
      {{- end -}}
    </ul>
  {{- end -}}
{{- end -}}
```

**安全约束**（与 `layouts/quests.html` 既有写法一致）：
- 字段守卫：`where` 找到的 `$matching` 必须 `len > 0` 才进入；`checkins` 字段缺失视为空数组
- 永远不假定 `spark_checkins.json` 存在 → Hugo 启动报错时 data 文件缺失会被 `where` 返回空数组，模板走"无图"分支

### 5.2 `layouts/index.html` 不做改动

本期仅在 `/quests/` 列表页展示图墙。首页 spark 卡片保持现状（hero + giscus + fallback 链接），不在卡片底部加"今日 N 人已打卡"小条。如未来需要，按 §10 后续工作加入。

### 5.3 样式（`assets/css/extended/blank.css` 新增章节）

```css
/* --- Spark check-in image wall ---------------------------------------------
 * Horizontal thumbnail strip on /quests/. Lazy-loaded via loading="lazy".
 * Click → opens the source GitHub comment in a new tab (keeps community
 * attribution). No hover scale/motion (prefers-reduced-motion friendly).
 * Avatar: 80×80 (matches the data field spec); rounded 6px to read as a
 * chip rather than a hard square.
 * ----------------------------------------------------------------------- */
.quests__checkins {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5em;
  margin: 0.5em 0 0.7em;
  padding: 0;
  list-style: none;
}

.quests__checkin a {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25em;
  text-decoration: none;
  color: var(--secondary);
  font-size: 0.75em;
  transition: color 0.15s ease;
}

.quests__checkin a:hover,
.quests__checkin a:focus-visible {
  color: var(--primary);
}

.quests__checkin img {
  width: 64px;
  height: 64px;
  object-fit: cover;
  border: 1px solid var(--border);
  border-radius: 6px;
  background: var(--theme);
}

.quests__checkin-author {
  max-width: 64px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
```

---

## 6. 自动化：`.github/workflows/spark-checkins.yml`

### 6.1 触发条件

```yaml
on:
  schedule:
    - cron: '17 * * * *'      # 每小时 17 分（daily-spark 是 16:10）
  workflow_dispatch:            # 手动触发
```

### 6.2 关键步骤

```yaml
jobs:
  fetch:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0, token: ${{ secrets.GITHUB_TOKEN }} }
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - name: Fetch check-ins
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: python3 scripts/fetch_spark_checkins.py
      - name: Commit if changed
        run: |
          git add data/spark_checkins.json
          git diff --cached --quiet || {
            git commit -m "chore: refresh spark check-ins"
            git push origin HEAD:main
            gh workflow run hugo.yml --ref main
          }
```

### 6.3 与其他 workflow 的关系

| Workflow | 触发 | 写哪些 |
|---|---|---|
| `daily-spark.yml` | cron `10 16 * * *` + 手动 | `daily_spark.json`、`daily_spark_history.json` → push 后触发 `hugo.yml` |
| `spark-checkins.yml`（新） | cron `17 * * * *` + 手动 | `spark_checkins.json` → push 后触发 `hugo.yml` |
| `hugo.yml` | push main + 手动 | `public/` → GitHub Pages |

- **互不耦合**：三个 workflow 各写各的 data 文件，谁先跑都行
- **依赖**：写 data 文件 → push → 触发 `hugo.yml` 重新构建
- **并发保护**：两个写 data 的 workflow 用 `concurrency: { group: <unique>, cancel-in-progress: false }`（避免两个并发 commit 互相 rebase）

### 6.4 幂等保证

- 脚本检测"今天没人打卡 + 上次 JSON 已经有这一天的空 checkins" → **不写入、不 commit**
- 脚本检测"数据完全没变"（与现有 JSON 字节级相等）→ **不写入、不 commit**
- 任何"有变化"才 commit + push

### 6.5 失败行为

- 抓取失败 → 不写文件 → `git diff --cached --quiet` 返回 true → 不 commit → workflow 失败但 main 分支干净
- hugo.yml 触发失败 → 用户手动重跑 spark-checkins.yml（无需重抓数据，因为 JSON 已落盘）

---

## 7. 产品决策（已默认）

下列 5 项是这次设计需要的产品取舍。**默认值见下表**，用户审批 spec 时可一次性调整；不调整则按默认推进。

| # | 决策 | 默认值 | 理由 |
|---|---|---|---|
| 1 | 刷新频率 | 每小时 cron（17 分） | daily-spark 16:10、spark-checkins 17 分错峰；1 小时滞后对每日任务可接受 |
| 2 | 展示位置 | 仅 `/quests/` 每条下面挂图墙 | 主页保持克制（已有 hero + giscus + fallback 链接，再加小条会让卡片信息过载）；详情页是图墙的天然位置 |
| 3 | 缩略图密度 + 点击行为 | 64×64 缩略图 + 用户名；点击跳 GitHub 评论（新标签页）；**不做** 站内 lightbox | 保持社区归属（用户在 GitHub 上能继续互动）；64×64 与现有头像区视觉重量匹配 |
| 4 | 用户名展示 | 显示 GitHub 登录名（无 mask） | GitHub 打卡场景下登录名本身已是公开身份；mask 反倒显得不自然 |
| 5 | Fallback 链接 | 保留 `打卡讨论 ↗` / `Comment on GitHub · images supported ↗` | 不影响访客跳转路径；与图墙并存 |

---

## 8. 风险与限制

| 风险 | 缓解 |
|---|---|
| GitHub GraphQL schema 变化（节点重命名） | 抓取脚本内显式校验 `errors[].message`；失败时打 log 但不破坏现有 JSON |
| 用户撤回/删除评论 | 下次抓取自动反映（不报错） |
| 用户隐私（不愿公开 GitHub 登录名） | 一期不提供 mask 开关；如未来需要，按 §10 后续工作加入 |
| GITHUB_TOKEN 配额（5000/h） | 每小时一次 × 90 天窗口 × ~10 节点 = 900 节点/小时，< 20% 配额 |
| Hugo data 文件过大 | 220 KB 估算远低于阈值；如 > 1 MB 再做按需裁剪 |
| 用户上传图片被 GitHub CDN 清理 | 旧 image_url 404 → 缩略图显示 broken image；CSS 兜底 `background: var(--theme)` + alt 文案 |
| giscus 跨域 / 图片 lazy load 失败 | `<img loading="lazy">` + 显式 `width`/`height` 减小 CLS；broken image 不阻塞页面 |
| 时区：抓取"今天" vs 用户看到的"今天" | 抓取用 UTC；显示用 `data/daily_spark.json.date` 的字面值（已是上海时区的"今天"） |

---

## 9. 验收

### 9.1 Spec 评审

- [ ] 用户批准 §7 的 5 个默认值（或逐一调整）
- [ ] 数据契约 §3 双方对字段无歧义
- [ ] 抓取窗口 §4.1 的 90 天范围合理
- [ ] 模板位置 §5.1/§5.2 与视觉预期一致

### 9.2 Plan 执行验收（具体 step 见 plan）

- 端到端测试：手动在某条 spark discussion 评论里上传一张图片 → 等下一次 cron（或手动触发 workflow） → `/quests/#spark-<date>` 锚点能看到缩略图
- 边界测试：① 当天无 discussion ② discussion 存在但无图 ③ 同条评论多图 → 全部走"无图卡"分支
- 性能：单次抓取 + build < 90 秒
- Lighthouse 移动端性能 ≥ 90（与根 spec §1.3 一致）

---

## 10. 后续工作（明确不在本期范围）

- 站内 lightbox / 弹层放大
- 表情包 / 文字打卡墙（当前只展示带图评论）
- 用户名 mask 开关
- 用户屏蔽某个 GitHub 用户（不发某人图卡）
- 多 repo 共享打卡墙（私有源 repo）
- 实时增量更新（GraphQL Subscriptions）
- 按 tag 维度的聚合页（"所有创造类任务打卡墙"）