# Spark 打卡图片墙 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 `https://sanbika.github.io/quests/` 和首页直接展示 GitHub Discussions 里 Daily Spark 每日任务的打卡图片墙，让访客无需跳 GitHub 也能看到大家传的图片。

**Architecture:** 静态 Hugo 站 + 构建时拉 GitHub GraphQL。Python 脚本每小时 cron 拉取最近 90 天的 spark discussion 评论、提取图片 URL、写 `data/spark_checkins.json`。Hugo 模板读这个 JSON 渲染图卡。`hugo.yml` 已在监听 main push，新 workflow 写完 JSON 触发 deploy。

**Tech Stack:** Python 3.11 stdlib only, GitHub GraphQL API v4 (REST 兜底), GitHub Actions (`secrets.GITHUB_TOKEN`), Hugo templates, existing CSS overrides.

**Spec:** `docs/superpowers/specs/2026-08-18-spark-checkins-design.md`

---

## File Structure

被本计划创建或修改的文件：

```
C:/Dev/blog-site/
├── scripts/
│   └── fetch_spark_checkins.py        ← 新增：抓取脚本 (≈ 250 行)
│
├── data/
│   ├── .spark_checkins.example.json   ← 新增：fixture，用于本地测试模板
│   └── spark_checkins.json            ← 新增：实际产物（CI 写盘）
│
├── .github/workflows/
│   └── spark-checkins.yml             ← 新增：每小时 cron workflow
│
├── layouts/
│   ├── quests.html                    ← 修改：在每条 quest item 加图卡墙
│   └── index.html                     ← 修改：首页 spark 卡片加 "今日 N 人已打卡"
│
└── assets/css/extended/
    └── blank.css                      ← 修改：追加 .quests__checkins* 与
                                          .home-spark__checkins 样式
```

---

## 工作约定

1. **每个 task 结束都要 commit**（除有特殊说明的合并 commit）
2. **TDD 不强求**：本期为基础设施搭建 + 静态内容改版。验证改为：① 脚本可本地 dry-run ② workflow 可手动触发 ③ hugo build 成功 ④ 视觉走查
3. **每次失败的报错**保留日志，作为后续诊断材料
4. **HEAD 始终保持可用**：每个 commit 后 `hugo server` 仍可起，部署不会回退
5. **不要复制粘贴 daily_spark.py 的全部代码**：复用 `validate_payload` 不存在的逻辑（本期不验证模型输出）；只复用 `read_json` / `write_json` / `today_shanghai` / `BACKOFFS_SECONDS` 等纯工具函数，**抽到 `scripts/_lib.py` 后再 import**，避免两份脚本各自演进
6. **新增公共 lib 时**：抽到一个 `_lib.py` 文件是允许的，但**只抽纯工具**（读写 JSON、SHANGHAI_TZ、HTTP 重试），不引入类/包结构

---

## Phase 0 — 共用工具抽取（前置）

### Task 0.1: 把 daily_spark.py 的纯工具函数抽到 _lib.py

**Files:**
- Create: `C:/Dev/blog-site/scripts/_lib.py`
- Modify: `C:/Dev/blog-site/scripts/daily_spark.py`

**Why:** spark-checkins.py 需要 `read_json` / `write_json` / `BACKOFFS_SECONDS` 等工具。**不复制粘贴**而是抽到一个 `_lib.py` 模块供两个脚本共用，避免日后两处独立演进漂移。

**Steps:**

- [ ] **Step 1: 创建 `scripts/_lib.py`**

复制以下内容到 `scripts/_lib.py`：
- `SHANGHAI_TZ`
- `WEEKDAY_NAMES_ZH`
- `today_shanghai()` (改名 `today_shanghai_date()`，仅返回 date 字符串；weekday 留给 daily_spark 自己算)
- `read_json(path, default)`
- `write_json(path, obj)` (含原子写 + tmp + os.replace)
- `BACKOFFS_SECONDS`
- `_is_retryable_http(code)`
- `_http_error_log(e)`
- 新增：`MAX_ATTEMPTS = 4`（从 daily_spark.py 上移）
- 新增：`def utc_now_iso() -> str` 返回当前 UTC 时间 ISO8601 字符串（`datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")`）

**所有函数顶部加一行 docstring 说明归属**（例如 `# Exposed from daily_spark.py for shared use`）。

- [ ] **Step 2: 改 `scripts/daily_spark.py`**

删除上述函数定义（保留调用），顶部加：
```python
from _lib import (
    SHANGHAI_TZ, WEEKDAY_NAMES_ZH, today_shanghai_date,
    read_json, write_json, BACKOFFS_SECONDS, MAX_ATTEMPTS,
    _is_retryable_http, _http_error_log,
)
```

`today_shanghai` 改成 `today_shanghai_date()`；其他调用点按需替换。

- [ ] **Step 3: 本地 dry-run 验证 daily_spark.py 未破坏**

```bash
cd C:/Dev/blog-site
python3 -c "from _lib import *; print('lib OK')"
python3 scripts/daily_spark.py 2>&1 | head -20   # 不设 API key 会失败，但 import + 启动逻辑应正常
```

预期：`lib OK` 输出；daily_spark.py 打印 `[daily-spark] MINIMAX_API_KEY not set` 后 exit 1（**这是预期的，不算破坏**）。

**Verification:**
- `from _lib import *` 不抛 ImportError
- daily_spark.py 的 import 块不抛 ImportError
- daily_spark.py 缺 API key 时报熟悉的错（行为一致）

- [ ] **Step 4: Commit**

```bash
git add scripts/_lib.py scripts/daily_spark.py
git commit -m "refactor(scripts): extract shared utils to _lib.py"
```

---

## Phase 1 — 数据契约与 fixture

### Task 1.1: 创建 fixture

**Files:**
- Create: `C:/Dev/blog-site/data/.spark_checkins.example.json`

**Why:** 让本地 `hugo server` 在还没真数据时也能验证模板渲染。

**Steps:**

- [ ] **Step 1: 写 fixture JSON**

```json
[
  {
    "date": "2026-08-15",
    "fetched_at": "2026-08-18T10:00:00Z",
    "discussion_url": "https://github.com/sanbika/sanbika.github.io/discussions/42",
    "checkins": [
      {
        "author": "alice",
        "author_avatar": "https://avatars.githubusercontent.com/u/1?v=4",
        "image_url": "https://github.com/user-attachments/assets/example1",
        "alt": "水果拼盘 1",
        "comment_url": "https://github.com/sanbika/sanbika.github.io/discussions/42#discussioncomment-1",
        "posted_at": "2026-08-15T10:23:00Z"
      },
      {
        "author": "bob",
        "author_avatar": "https://avatars.githubusercontent.com/u/2?v=4",
        "image_url": "https://github.com/user-attachments/assets/example2",
        "alt": "水果拼盘 2",
        "comment_url": "https://github.com/sanbika/sanbika.github.io/discussions/43#discussioncomment-2",
        "posted_at": "2026-08-15T15:00:00Z"
      }
    ]
  },
  {
    "date": "2026-08-16",
    "fetched_at": "2026-08-18T10:00:00Z",
    "discussion_url": "https://github.com/sanbika/sanbika.github.io/discussions/44",
    "checkins": [
      {
        "author": "carol",
        "author_avatar": "https://avatars.githubusercontent.com/u/3?v=4",
        "image_url": "https://github.com/user-attachments/assets/example3",
        "alt": "今日发现的小角落",
        "comment_url": "https://github.com/sanbika/sanbika.github.io/discussions/44#discussioncomment-5",
        "posted_at": "2026-08-16T12:00:00Z"
      }
    ]
  },
  { "date": "2026-08-17", "fetched_at": "2026-08-18T10:00:00Z", "discussion_url": null, "checkins": [] },
  { "date": "2026-08-18", "fetched_at": "2026-08-18T10:00:00Z", "discussion_url": null, "checkins": [] }
]
```

- [ ] **Step 2: 本地起 hugo server 验证模板能读这个文件（占位）**

**这一步暂时只是确认 JSON 合法**。模板改造在 Phase 3 验证：
```bash
cd C:/Dev/blog-site
python3 -c "import json; json.load(open('data/.spark_checkins.example.json')); print('JSON valid')"
```

预期：`JSON valid`

- [ ] **Step 3: 确认 `.spark_checkins.example.json` 不会被实际脚本读取**

文件名以 `.` 开头（隐藏文件），且抓取脚本只读 `spark_checkins.json`。无需额外 `.gitignore` 条目。

- [ ] **Step 4: 不 commit（fixture 在 `.gitignore` 里）**

⚠️ `data/.spark_checkins.example.json` 是给本地开发的，**不进 git**。

如果用户想保留 fixture 进 repo 作为模板，应放到 `docs/superpowers/specs/2026-08-18-spark-checkins-design.md` 里的 §3.1 而不是 `data/`。本 plan 默认走"不进 git"路线。

---

## Phase 2 — 抓取脚本

### Task 2.1: 写 `scripts/fetch_spark_checkins.py` 骨架

**Files:**
- Create: `C:/Dev/blog-site/scripts/fetch_spark_checkins.py`

**Steps:**

- [ ] **Step 1: 创建文件结构**

```python
#!/usr/bin/env python3
"""
Spark check-ins fetcher.

Pulls GitHub Discussions whose term is "spark-YYYY-MM-DD" from
sanbika/sanbika.github.io, extracts user-uploaded images from comment
bodyHTML, writes data/spark_checkins.json. Stdlib only.

Reuses helpers from _lib.py.
"""
import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import date, datetime, timedelta

from _lib import (
    BACKOFFS_SECONDS, MAX_ATTEMPTS,
    _http_error_log, _is_retryable_http,
    read_json, today_shanghai_date, write_json,
)

REPO_OWNER = "sanbika"
REPO_NAME = "sanbika.github.io"
GRAPHQL_URL = "https://api.github.com/graphql"
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data")
OUTPUT_FILE = os.path.join(DATA_DIR, "spark_checkins.json")
HISTORY_FILE = os.path.join(DATA_DIR, "daily_spark_history.json")
WINDOW_DAYS = 90
USER_ATTACHMENT_RE = re.compile(r"https://github\.com/user-attachments/assets/[A-Za-z0-9_-]+")
IMG_TAG_RE = re.compile(r'<img[^>]*src="([^"]+)"[^>]*alt="([^"]*)"', re.IGNORECASE)
COMMENT_FIELDS = "first: 50"


def fetch_window():
    """Return (start_date, end_date) tuple. End = today Shanghai, start = 90 days earlier."""
    end = date.fromisoformat(today_shanghai_date())
    start = end - timedelta(days=WINDOW_DAYS - 1)
    return start, end


def fetch_history_dates():
    """Return set of YYYY-MM-DD strings from daily_spark_history.json (empty if missing)."""
    history = read_json(HISTORY_FILE, default=[])
    if not isinstance(history, list):
        return set()
    return {item["date"] for item in history if isinstance(item, dict) and "date" in item}


# (其他函数在后续 Task 填入)


def main():
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("[spark-checkins] GITHUB_TOKEN not set", file=sys.stderr)
        sys.exit(1)
    print("[spark-checkins] OK start", flush=True)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: 验证骨架可启动**

```bash
cd C:/Dev/blog-site
GITHUB_TOKEN=fake python3 scripts/fetch_spark_checkins.py
```

预期：`[spark-checkins] OK start` 后退出 0。

- [ ] **Step 3: 不 commit（还要继续填函数）**

---

### Task 2.2: 实现 GraphQL 调用

**Files:**
- Modify: `C:/Dev/blog-site/scripts/fetch_spark_checkins.py`

**Steps:**

- [ ] **Step 1: 加 `query_discussion(token, date_str)`**

```python
def query_discussion(token, date_str):
    """Query GitHub for the discussion with term='spark-<date>' in our repo.
    Returns the Discussion node dict, or None if not found."""
    query = """
    query SparkDiscussion($q: String!) {
      search(query: $q, type: DISCUSSION, first: 1) {
        nodes {
          ... on Discussion {
            number
            url
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
    """
    variables = {"q": f"spark-{date_str} repo:{REPO_OWNER}/{REPO_NAME} type:discussion"}
    payload = json.dumps({"query": query, "variables": variables}).encode("utf-8")
    req = urllib.request.Request(
        GRAPHQL_URL,
        data=payload,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
            "User-Agent": "sanbika-spark-checkins-bot",
        },
    )
    last_error = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            if data.get("errors"):
                raise RuntimeError(f"GraphQL errors: {data['errors']}")
            nodes = data["data"]["search"]["nodes"]
            return nodes[0] if nodes else None
        except urllib.error.HTTPError as e:
            detail = _http_error_log(e)
            if _is_retryable_http(e.code):
                last_error = detail
                print(f"[spark-checkins] retryable {detail}", flush=True)
            else:
                raise RuntimeError(f"non-retryable {detail}") from e
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
            last_error = f"network/parse error: {e}"
            print(f"[spark-checkins] {last_error}", flush=True)

        if attempt < MAX_ATTEMPTS:
            sleep_for = BACKOFFS_SECONDS[attempt - 1]
            time.sleep(sleep_for)   # 顶部要 import time

    raise RuntimeError(f"failed after {MAX_ATTEMPTS} attempts: {last_error}")
```

**记得顶部加 `import time`**。

- [ ] **Step 2: 验证骨架 + GraphQL 函数可加载**

```bash
cd C:/Dev/blog-site
GITHUB_TOKEN=fake python3 -c "
import sys; sys.path.insert(0, 'scripts')
from fetch_spark_checkins import query_discussion
print('import OK')
"
```

预期：`import OK`

- [ ] **Step 3: 用真实 token 测一次（用户手动）**

⚠️ **不要把真实 token commit 进任何文件**。

```bash
export GITHUB_TOKEN=$(gh auth token 2>/dev/null || echo "your-token-here")
cd C:/Dev/blog-site
python3 -c "
import sys; sys.path.insert(0, 'scripts')
from fetch_spark_checkins import query_discussion
result = query_discussion('$GITHUB_TOKEN', '2026-08-15')
print(type(result).__name__)
if result:
    print('comments:', result['comments']['totalCount'])
"
```

预期：返回一个 dict；comments totalCount ≥ 0。

- [ ] **Step 4: 不 commit**

---

### Task 2.3: 实现图片提取与去重

**Files:**
- Modify: `C:/Dev/blog-site/scripts/fetch_spark_checkins.py`

**Steps:**

- [ ] **Step 1: 加 `extract_checkins(discussion)`**

```python
def extract_checkins(discussion):
    """Given a Discussion node dict, return list of checkin dicts."""
    if not discussion:
        return []
    checkins = []
    seen = set()  # 去重：(comment_id, image_url) 组合
    for comment in discussion["comments"]["nodes"]:
        body = comment.get("bodyHTML") or ""
        author = (comment.get("author") or {}).get("login") or "anonymous"
        avatar = (comment.get("author") or {}).get("avatarUrl") or ""
        comment_url = comment.get("url") or ""
        comment_id = comment.get("id") or comment_url
        # 提取所有 <img src=... alt=...>
        matches = IMG_TAG_RE.findall(body)
        for src, alt in matches:
            # 白名单：只接受 user-attachments/assets
            if not src.startswith("https://github.com/user-attachments/assets/"):
                continue
            key = (comment_id, src)
            if key in seen:
                continue
            seen.add(key)
            if not alt:
                # 用 URL 末段 hash 前 8 位作为 alt 兜底
                hash_part = src.rsplit("/", 1)[-1][:8]
                alt = f"check-in by {author} ({hash_part})"
            checkins.append({
                "author": author,
                "author_avatar": avatar,
                "image_url": src,
                "alt": alt,
                "comment_url": comment_url,
                "posted_at": comment.get("createdAt") or "",
            })
    return checkins
```

- [ ] **Step 2: 用一个 mock bodyHTML 验证解析**

```bash
cd C:/Dev/blog-site
python3 -c "
import sys; sys.path.insert(0, 'scripts')
from fetch_spark_checkins import extract_checkins
mock = {
    'comments': {'nodes': [
        {'id': 'c1', 'url': 'https://x/c1', 'createdAt': '2026-08-15T10:00:00Z',
         'bodyHTML': '<p>看 <img src=\"https://github.com/user-attachments/assets/abcdef1234567890\" alt=\"my photo\"/></p>',
         'author': {'login': 'alice', 'avatarUrl': 'https://avatars/1'}},
        {'id': 'c2', 'url': 'https://x/c2', 'createdAt': '2026-08-15T11:00:00Z',
         'bodyHTML': '<p>emoji 👋</p><p>我的图 <img src=\"https://evil.com/x.png\"/></p>',
         'author': {'login': 'bob', 'avatarUrl': 'https://avatars/2'}},
        {'id': 'c3', 'url': 'https://x/c3', 'createdAt': '2026-08-15T12:00:00Z',
         'bodyHTML': '<p>两张图:</p><img src=\"https://github.com/user-attachments/assets/aaa\"/><img src=\"https://github.com/user-attachments/assets/bbb\" alt=\"图二\"/>',
         'author': {'login': 'carol', 'avatarUrl': 'https://avatars/3'}},
    ]}
}
result = extract_checkins(mock)
print(f'count={len(result)}')
for c in result:
    print(f'  {c[\"author\"]} -> {c[\"image_url\"].rsplit(\"/\", 1)[-1]} alt={c[\"alt\"]!r}')
"
```

预期输出：
```
count=3
  alice -> abcdef12 my photo
  carol -> aaa alt='check-in by carol (aaa)'
  carol -> bbb alt='图二'
```

**断言**：bob 那条因 evil.com 被过滤；carol 两条都被收；alt 兜底逻辑生效。

- [ ] **Step 3: 不 commit**

---

### Task 2.4: 实现主流程 + 写盘逻辑

**Files:**
- Modify: `C:/Dev/blog-site/scripts/fetch_spark_checkins.py`

**Steps:**

- [ ] **Step 1: 加 `build_checkins(token, dates)` 与 `main()`**

```python
def build_checkins(token, dates):
    """For each YYYY-MM-DD in dates (list), fetch discussion + extract checkins.
    Returns dict: date -> {"checkins": [...], "discussion_url": str|None}.
    """
    result = {}
    for d in dates:
        try:
            discussion = query_discussion(token, d)
        except RuntimeError as e:
            print(f"[spark-checkins] {d} failed: {e}; skipping", file=sys.stderr, flush=True)
            result[d] = {"checkins": [], "discussion_url": None}
            continue
        checkins = extract_checkins(discussion)
        result[d] = {
            "checkins": checkins,
            "discussion_url": discussion["url"] if discussion else None,
        }
    return result


def main():
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("[spark-checkins] GITHUB_TOKEN not set", file=sys.stderr)
        sys.exit(1)

    os.makedirs(DATA_DIR, exist_ok=True)

    # 窗口 + 实际存在的日期
    start, end = fetch_window()
    history_dates = fetch_history_dates()
    # 只抓 history 中落在窗口内的日期；history 为空时退化为窗口内全部日期
    if history_dates:
        dates = sorted(d for d in history_dates if start.isoformat() <= d <= end.isoformat())
    else:
        dates = [(start + timedelta(days=i)).isoformat() for i in range((end - start).days + 1)]

    if not dates:
        print("[spark-checkins] window empty, nothing to do", flush=True)
        return

    print(f"[spark-checkins] fetching {len(dates)} days from {start} to {end}", flush=True)
    fresh = build_checkins(token, dates)
    fetched_at = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    # 合并：窗口外日期保留旧值；窗口内用 fresh
    existing = read_json(OUTPUT_FILE, default=[])
    if not isinstance(existing, list):
        existing = []
    existing_by_date = {item["date"]: item for item in existing if isinstance(item, dict) and "date" in item}

    new_data = []
    for d in dates:
        new_data.append({
            "date": d,
            "fetched_at": fetched_at,
            "discussion_url": fresh[d]["discussion_url"],
            "checkins": fresh[d]["checkins"],
        })
    # 窗口外的老数据保留
    out_of_window = [item for item in existing
                     if isinstance(item, dict) and "date" in item and item["date"] not in {x for d in dates for x in [d]}]
    new_data.extend(out_of_window)
    new_data.sort(key=lambda x: x["date"])

    # 字节级相等 → 跳过写盘
    new_bytes = json.dumps(new_data, ensure_ascii=False, indent=2, sort_keys=True).encode("utf-8")
    try:
        old_bytes = open(OUTPUT_FILE, "rb").read()
    except FileNotFoundError:
        old_bytes = b""
    if new_bytes == old_bytes:
        print(f"[spark-checkins] no changes ({len(dates)} days scanned, {sum(len(v['checkins']) for v in fresh.values())} checkins), skipping commit", flush=True)
        return

    write_json(OUTPUT_FILE, new_data)
    total_checkins = sum(len(v["checkins"]) for v in fresh.values())
    print(f"[spark-checkins] wrote {OUTPUT_FILE}: {len(dates)} days, {total_checkins} checkins", flush=True)
```

- [ ] **Step 2: 不带 token → exit 1**

```bash
cd C:/Dev/blog-site
unset GITHUB_TOKEN
python3 scripts/fetch_spark_checkins.py
```

预期：`[spark-checkins] GITHUB_TOKEN not set` 后 exit 1。

- [ ] **Step 3: 用真实 token 跑一次（用户手动验证）**

⚠️ **不要把真实 token 落到任何文件**。

```bash
cd C:/Dev/blog-site
export GITHUB_TOKEN=$(gh auth token 2>/dev/null || echo "your-token-here")
python3 scripts/fetch_spark_checkins.py
cat data/spark_checkins.json | head -40
```

预期：看到 `data/spark_checkins.json` 被创建，包含窗口内各日期的 `checkins`。

- [ ] **Step 4: 幂等性：再跑一次应该 "no changes"**

```bash
cd C:/Dev/blog-site
python3 scripts/fetch_spark_checkins.py
```

预期：第二次打印 `[spark-checkins] no changes (...)`，文件未被修改（`git diff` 静默）。

- [ ] **Step 5: Commit**

```bash
git add scripts/fetch_spark_checkins.py
git commit -m "feat(scripts): fetch spark check-ins from GitHub Discussions"
```

---

## Phase 3 — 模板改造

### Task 3.1: `layouts/quests.html` 加图卡墙

**Files:**
- Modify: `C:/Dev/blog-site/layouts/quests.html`

**Steps:**

- [ ] **Step 1: 定位插入点**

在文件内 `<a class="quests__discussion" href="{{ $discussionURL }}">` 这一行**之前**，插入图卡墙渲染块。

- [ ] **Step 2: 插入图卡墙**

```go-html-template
{{- /* 打卡图片墙: 仅当 site.Data.spark_checkins 包含该日期时渲染. site.Data 缺
       失 / spark_checkins.json 不存在时 where 返回空数组, 走 "无图" 分支.
       checkins 字段缺失同样视为空数组, 防止 nil panic. */ -}}
{{- $matchings := where site.Data.spark_checkins "date" .date -}}
{{- if gt (len $matchings) 0 -}}
  {{- $checkins := index (index $matchings 0) "checkins" -}}
  {{- if $checkins -}}
    {{- $checkinLabel := cond (eq $langKey "en") "Check-ins" "打卡" -}}
    <ul class="quests__checkins" aria-label="{{ $checkinLabel }}">
      {{- range $checkins -}}
        <li class="quests__checkin">
          <a href="{{ .comment_url }}" target="_blank" rel="noopener" aria-label="{{ .author }}">
            <img loading="lazy" src="{{ .image_url }}" alt="{{ .alt }}" width="64" height="64" />
            <span class="quests__checkin-author">{{ .author }}</span>
          </a>
        </li>
      {{- end -}}
    </ul>
  {{- end -}}
{{- end -}}
```

- [ ] **Step 3: 本地起 hugo server 验证**

```bash
cd C:/Dev/blog-site
# 把 fixture 拷贝成实际文件
cp data/.spark_checkins.example.json data/spark_checkins.json
hugo server --buildFuture
```

浏览器打开 `http://localhost:1313/quests/`：
- 检查 2026-08-15、2026-08-16 两条下面有图卡
- 检查 2026-08-17、2026-08-18 两条**没有**图卡（无 checkins）
- 切换语言 → en → 验证 aria-label 变化

⚠️ **不要 commit data/spark_checkins.json**（fixture 临时用，做完 Task 3.1 后 `rm data/spark_checkins.json`）。

- [ ] **Step 4: 删除临时 fixture 文件**

```bash
cd C:/Dev/blog-site
rm data/spark_checkins.json
```

- [ ] **Step 5: 验证 `site.Data.spark_checkins` 缺失时不报错**

```bash
cd C:/Dev/blog-site
# 暂时把 data/spark_checkins.json 移走
mv data/spark_checkins.json /tmp/ 2>/dev/null || true
hugo server --buildFuture 2>&1 | head -50
```

预期：hugo 启动成功，`/quests/` 正常渲染（所有日期无图卡）。

- [ ] **Step 6: Commit**

```bash
git add layouts/quests.html
git commit -m "feat(layouts): render spark check-in image wall on /quests/"
```

---

## Phase 4 — CSS 样式

### Task 4.1: 在 `assets/css/extended/blank.css` 末尾追加

**Files:**
- Modify: `C:/Dev/blog-site/assets/css/extended/blank.css`

**Steps:**

- [ ] **Step 1: 追加章节**

在文件末尾（最后一个空行后）追加：

```css
/* --- Spark check-in image wall ---------------------------------------------
 * 出现在 /quests/ 每条 quest item 内部、__discussion 链接之前.
 * 设计目标: 64×64 缩略图 + 用户名, 与现有 .quests__tag 视觉重量匹配;
 * flex-wrap 在窄屏自动换行; 移动端通过缩小缩略图到 56×56 维持节奏.
 * loading="lazy" 由模板加, 这里只管布局; 图裂时 alt 文案兜底.
 * ------------------------------------------------------------------------- */
.quests__checkins {
  display: flex;
  flex-wrap: wrap;
  gap: 0.55em;
  margin: 0.55em 0 0.7em;
  padding: 0;
  list-style: none;
}

.quests__checkin a {
  display: inline-flex;
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
  font-variant-numeric: tabular-nums;
}

/* 小屏缩到 56×56 维持节奏, 不缩太小防止图看不清 */
@media (max-width: 480px) {
  .quests__checkin img {
    width: 56px;
    height: 56px;
  }
  .quests__checkin-author {
    max-width: 56px;
  }
}
```

- [ ] **Step 2: 本地 `hugo server` 视觉验证**

恢复 fixture → `hugo server` → `/quests/` → 看到缩略图整齐排布，hover 标题变 primary 色。

- [ ] **Step 3: 清理 fixture**

```bash
cd C:/Dev/blog-site
rm -f data/spark_checkins.json
```

- [ ] **Step 4: Commit**

```bash
git add assets/css/extended/blank.css
git commit -m "style: spark check-in image wall"
```

---
## Phase 5 — GitHub Actions workflow

### Task 5.1: 写 `.github/workflows/spark-checkins.yml`

**Files:**
- Create: `C:/Dev/blog-site/.github/workflows/spark-checkins.yml`

**Steps:**

- [ ] **Step 1: 写 workflow**

```yaml
name: Fetch Spark Check-ins

# Pulls user-uploaded images from GitHub Discussions (spark-<date> terms),
# writes data/spark_checkins.json, triggers Hugo deploy only when changed.
#
# Schedule: every hour at :17 (daily-spark.yml is :10; this avoids overlap).
# Manual: workflow_dispatch for one-off refresh after a notable check-in.

on:
  schedule:
    - cron: '17 * * * *'
  workflow_dispatch:

# Single writer — cancel-in-progress: false so two overlapping runs
# don't fight over the same JSON / push race.
concurrency:
  group: spark-checkins
  cancel-in-progress: false

permissions:
  contents: write
  actions: write

jobs:
  fetch:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          submodules: recursive
          fetch-depth: 0
          token: ${{ secrets.GITHUB_TOKEN }}

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Sync with main
        run: |
          git config user.name  "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git pull --rebase origin main || true

      - name: Fetch spark check-ins
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: python3 scripts/fetch_spark_checkins.py

      - name: Stage check-in file
        run: |
          git add data/spark_checkins.json
          git status --short

      - name: Check for changes
        id: check
        run: |
          if git diff --cached --quiet; then
            echo "changed=false" >> "$GITHUB_OUTPUT"
          else
            echo "changed=true" >> "$GITHUB_OUTPUT"
          fi

      - name: Commit and push
        if: steps.check.outputs.changed == 'true'
        env:
          GH_TOKEN: ${{ github.token }}
        run: |
          git commit -m "chore: refresh spark check-ins"
          if git push origin HEAD:main; then
            exit 0
          fi
          echo "[spark-checkins] push failed, retrying once after rebase..." >&2
          git pull --rebase origin main
          git push origin HEAD:main
```

- [ ] **Step 2: 本地 YAML 语法检查**

```bash
cd C:/Dev/blog-site
python3 -c "
import yaml
yaml.safe_load(open('.github/workflows/spark-checkins.yml'))
print('YAML valid')
"
```

预期：`YAML valid`

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/spark-checkins.yml
git commit -m "ci: hourly spark check-ins fetcher"
```

---

## Phase 6 — 端到端验证

### Task 6.1: 在 GitHub 上手动触发一次

**Why:** 验证 workflow 真实运行 / token 权限够用 / 触发 `hugo.yml` 重新部署。

**Steps:**

- [ ] **Step 1: 推 main → workflow 可被发现**

```bash
git push origin main
```

- [ ] **Step 2: 手动触发一次 workflow**

GitHub 仓库 → Actions → "Fetch Spark Check-ins" → Run workflow → 选 main 分支 → Run。

- [ ] **Step 3: 检查 workflow 输出**

- 是否 exit 0？
- `data/spark_checkins.json` 是否被 push 上来了？
- `hugo.yml` 是否被自动触发并部署？

- [ ] **Step 4: 验证线上**

打开 `https://sanbika.github.io/quests/`：
- 找到一条有 discussion 的日期 → 看到图卡（如果有讨论里传过图）
- 找到一条没 discussion 的日期 → 不显示图卡

打开 `https://sanbika.github.io/`：
- 首页保持现状（hero + giscus + fallback 链接），**不**展示打卡小条

- [ ] **Step 5: 一条新打卡的端到端测试**

1. 打开一条 spark discussion（比如 2026-08-18）→ 发一条带图的评论
2. GitHub Actions → 手动 Run workflow → 等 1 分钟
3. 刷新 `https://sanbika.github.io/quests/#spark-2026-08-18` → 应该看到刚才那张图

- [ ] **Step 6: 收尾**

如果一切 OK，把 spec/plan 链接加到 README 的"功能列表"（如果 README 有相关章节；目前看 README 没有，跳过）。

---

## 验收清单（汇总）

实施完成后，逐条对照 spec §9.2：

- [ ] Phase 6 Task 6.1 端到端测试通过（手动上传一张图 → 1 小时内显示）
- [ ] 边界 1：当天无 discussion → `/quests/` 该日期无图卡 ✓
- [ ] 边界 2：discussion 存在但无图 → 无图卡 ✓
- [ ] 边界 3：同条评论多图 → 多张图卡共享 author/comment_url ✓
- [ ] 性能：单次 fetch + build < 90 秒 ✓（日志确认）
- [ ] Lighthouse 移动端性能 ≥ 90（与根 spec §1.3 一致）✓
- [ ] hugo.yml 自动被触发 / 部署成功 ✓

---

## 回滚方案

如果出现严重问题：

1. **回滚 workflow**：删除 `.github/workflows/spark-checkins.yml` 即可，下次 cron 不会再触发
2. **回滚数据**：`git rm data/spark_checkins.json` + `git commit` → 下次 hugo build 不再渲染图卡
3. **回滚模板**：`git revert` 对应 Phase 3/5 的 commit
4. **回滚脚本**：`git revert` Phase 0 / Phase 2 的 commit

每个组件独立可回滚，**不耦合**。

---

## 工作约定（再强调）

1. **不要在 commit message / 代码注释 / 文档里泄露 GITHUB_TOKEN**
2. **fixture（`data/.spark_checkins.example.json`）不进 git**，只在本地开发用
3. **`data/spark_checkins.json` 在第一次正式 fetch 前**也不进 git — 由 CI 写入；如果你本地跑了一次想 commit 进 git 也行，但请清楚说明"这是 fixture"
4. **不要修改 `hugo.yml`**——它已经监听 main push，新 workflow 写完 JSON 后自然触发
5. **每次失败先看 workflow log**，不要凭直觉改代码