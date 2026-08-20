#!/usr/bin/env python3
"""Spark check-ins fetcher.

Pulls GitHub Discussions from the `daily-spark` category (id
CATEGORY_ID; mirrors config/_default/params.toml
[params.comments.spark].categoryid) on sanbika/sanbika.github.io,
extracts user-uploaded images from both the discussion bodyHTML and
each comment's bodyHTML, buckets results by `spark-<date>` term parsed
out of the discussion title, writes data/spark_checkins.json. Stdlib
only.

Window: last 90 days from today (Shanghai). Single GraphQL call per
category page (vs. one per day in the previous implementation) — far
fewer round-trips, and `search()` was returning no rows for
`spark-<date>` queries against this repo anyway.

Images are accepted only from
  https://github.com/user-attachments/assets/
the URL GitHub rewrites uploaded attachments to; third-party <img>
sources are dropped to keep the surface area small and avoid
CDN/tracking drift.

Idempotent: byte-level compare against existing JSON; skip write if
nothing changed (so cron can run hourly without spamming commits).
Before comparing, `fetched_at` is stripped — the per-item timestamp
was the only thing churning commits on every cron tick when the
upstream image set was stable.

Reuses helpers from _lib.py.
"""
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import date, timedelta

from _lib import (
    BACKOFFS_SECONDS, MAX_ATTEMPTS,
    _http_error_log, _is_retryable_http,
    read_json, today_shanghai_date, utc_now_iso, write_json,
)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

REPO_OWNER = "sanbika"
REPO_NAME = "sanbika.github.io"
GRAPHQL_URL = "https://api.github.com/graphql"

# Must stay in sync with config/_default/params.toml
#   [params.comments.spark].categoryid
# Pulling the literal here (instead of reading the toml) keeps this
# script stdlib-only; the two values are reviewed together.
CATEGORY_ID = "DIC_kwDOT2zk8c4DDbVZ"
PAGE_SIZE = 100                                # GraphQL first:N for discussions page

DATA_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    os.pardir,
    "data",
)
OUTPUT_FILE = os.path.join(DATA_DIR, "spark_checkins.json")
HISTORY_FILE = os.path.join(DATA_DIR, "daily_spark_history.json")

WINDOW_DAYS = 90                                # backward window from today
COMMENTS_PER_DISCUSSION = 50                    # GraphQL first:N for comments
# Only accept images hosted on github.com/user-attachments/assets/ (the URL
# GitHub itself rewrites uploaded attachments to). External <img src=...> in
# comments is dropped — keeps the surface area small and avoids third-party
# tracking/CDN drift.
USER_ATTACHMENT_PREFIX = "https://github.com/user-attachments/assets/"
# Match `<img ... src="..." ... alt="...">` (alt optional / any order). Used
# to extract both src and alt from the rendered comment HTML.
#
# Implementation note: we split into two passes. First regex pulls the full
# `<img ...>` tag; second pass on the attribute string picks out src and
# (optionally) alt. The single-regex-with-optional-group approach can't
# distinguish "alt attr absent" from "alt attr present but empty" — both
# leave group 2 as the empty string — so we keep them as separate `re.search`
# calls where `None` means absent.
_IMG_TAG_RE = re.compile(r'<img\b([^>]*)>', re.IGNORECASE)
_IMG_SRC_RE = re.compile(r'src="([^"]+)"')
_IMG_ALT_RE = re.compile(r'\salt="([^"]*)"')


# ---------------------------------------------------------------------------
# Window / source-of-truth
# ---------------------------------------------------------------------------


def fetch_window():
    """Return (start_date, end_date) in Shanghai time.

    End = today Shanghai; start = end - (WINDOW_DAYS - 1). 90-day window
    is the spec default — old check-ins are kept in the existing JSON but
    not re-fetched every hour.
    """
    end = date.fromisoformat(today_shanghai_date())
    start = end - timedelta(days=WINDOW_DAYS - 1)
    return start, end


def fetch_history_dates():
    """Return set of YYYY-MM-DD strings present in daily_spark_history.json.

    Empty set on missing/malformed file. We only fetch check-ins for dates
    that actually have a quest (no point asking GitHub for a discussion
    that was never created).
    """
    history = read_json(HISTORY_FILE, default=[])
    if not isinstance(history, list):
        return set()
    return {
        item["date"]
        for item in history
        if isinstance(item, dict) and "date" in item
    }


def dates_in_window(history_dates, start, end):
    """Return sorted list of YYYY-MM-DD that fall inside [start, end].

    If `history_dates` is empty (no history file yet, or fresh repo),
    fall back to fetching every day in the window — better to over-fetch
    once than to silently skip days whose quest was never recorded.
    """
    if history_dates:
        return sorted(d for d in history_dates if start.isoformat() <= d <= end.isoformat())
    return [(start + timedelta(days=i)).isoformat() for i in range((end - start).days + 1)]


# ---------------------------------------------------------------------------
# GraphQL
# ---------------------------------------------------------------------------


def _query_category_discussions(token, after):
    """One page of `discussions(categoryId: ...)` ordered newest-first.

    `after=None` → first page. Caller drives the paginate loop.
    Returns (nodes, pageInfo-dict). The pageInfo dict carries
    `hasNextPage` + `endCursor`; we surface both so the caller can stop
    exactly when GitHub says "no more", not on a heuristic like "page
    wasn't full". Raises RuntimeError after MAX_ATTEMPTS on retryable
    errors. Non-retryable 4xx raises immediately.
    """
    query = """
    query SparkCategoryDiscussions($catId: ID!, $first: Int!, $after: String) {
      repository(owner: "%(owner)s", name: "%(name)s") {
        discussions(categoryId: $catId, first: $first, after: $after, orderBy: {field: CREATED_AT, direction: DESC}) {
          pageInfo { hasNextPage endCursor }
          nodes {
            number url title bodyHTML createdAt
            author { login avatarUrl(size: 80) }
            comments(first: %(comments_first)d) {
              totalCount
              nodes {
                id url bodyHTML createdAt
                author { login avatarUrl(size: 80) }
              }
            }
          }
        }
      }
    }
    """ % {"owner": REPO_OWNER, "name": REPO_NAME, "comments_first": COMMENTS_PER_DISCUSSION}
    variables = {"catId": CATEGORY_ID, "first": PAGE_SIZE}
    if after is not None:
        variables["after"] = after
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
                # GraphQL returned 200 with errors[] — treat as retryable.
                raise RuntimeError(f"GraphQL errors: {data['errors']}")
            repo = (data.get("data") or {}).get("repository") or {}
            discussions = repo.get("discussions") or {}
            return discussions.get("nodes") or [], (discussions.get("pageInfo") or {})
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
            print(f"[spark-checkins] sleeping {sleep_for}s before next attempt", flush=True)
            time.sleep(sleep_for)

    raise RuntimeError(f"failed after {MAX_ATTEMPTS} attempts: {last_error}")


def fetch_all_discussions(token):
    """Return flat list of every Discussion node in the spark category.

    Walks `pageInfo.hasNextPage`/`endCursor` until exhausted; each page
    uses PAGE_SIZE first:N. Two-layer failure policy so a transient
    API blip can't silently wipe the on-disk history:

      * Mid-pagination RuntimeError → if we already accumulated any
        nodes, keep them, WARN to stderr (with the count we did get),
        and break out of the loop. The caller's `index_by_date` then
        sees a partial-but-real window; only the dates we never reached
        get empty check-ins.
      * Same error before any node is collected → return [] and log
        to stderr. `main()` has its own guard against using this to
        overwrite a non-empty existing file (see top-level skip there).

    Hard ceiling on pages: 10 × PAGE_SIZE = 1000 discussions is far
    above any realistic 90-day window for this repo. Defensive only;
    a schema change that flips `hasNextPage` permanently on (instead of
    false on the last page) gets caught here and logged instead of
    pinning a workflow run.
    """
    nodes = []
    after = None
    max_pages = 10
    has_next = True
    for _ in range(max_pages):
        if not has_next:
            break
        try:
            page_nodes, page_info = _query_category_discussions(token, after)
        except RuntimeError as e:
            if nodes:
                # Partial result: keep what we already fetched so the
                # caller doesn't end up with a fully empty window on a
                # transient GitHub hiccup mid-pagination.
                print(
                    f"[spark-checkins] WARN category fetch aborted after {len(nodes)} nodes: {e}",
                    file=sys.stderr, flush=True,
                )
                break
            # Nothing collected yet — let the caller decide what to do.
            print(f"[spark-checkins] category fetch aborted: {e}", file=sys.stderr, flush=True)
            return []
        if not page_nodes:
            break
        nodes.extend(page_nodes)
        has_next = bool(page_info.get("hasNextPage"))
        after = page_info.get("endCursor")
        if not has_next or not after:
            break
    else:
        # Hit max_pages without `hasNextPage` flipping to false — log a
        # warning so an upstream schema change shows up. Include the
        # node count so on-call can sanity-check whether the ceiling
        # was reached on a half-full window or after a runaway loop.
        print(
            f"[spark-checkins] WARN pagination ceiling reached ({len(nodes)} nodes fetched)",
            file=sys.stderr, flush=True,
        )
    return nodes


def index_by_date(nodes):
    """Return {YYYY-MM-DD: node} keyed by `spark-<date>` in title.

    Skips nodes whose title doesn't start with `spark-` or whose suffix
    can't be parsed as an ISO date. First iteration wins on duplicate
    dates — combined with newest-first ordering from the GraphQL query,
    that means the latest discussion for a given `spark-<date>` is the
    one we keep, which is what we want when Giscus lazy-creates
    multiple threads for the same term. The `if suffix not in bucket:`
    guard makes that intent explicit instead of relying on iteration
    order semantics.
    """
    bucket = {}
    for node in nodes or []:
        if not isinstance(node, dict):
            continue
        title = (node.get("title") or "").strip()
        if not title.lower().startswith("spark-"):
            continue
        suffix = title[6:].strip()  # len("spark-") == 6
        try:
            date.fromisoformat(suffix)
        except ValueError:
            continue
        if suffix not in bucket:
            bucket[suffix] = node
    return bucket


# ---------------------------------------------------------------------------
# Image extraction
# ---------------------------------------------------------------------------


def _extract_imgs_from_body(body, source_id, author, avatar, source_url,
                            posted_at, seen, out):
    """Append parsed checkin dicts for each <img> in `body` to `out`.

    Filters by USER_ATTACHMENT_PREFIX, dedups via `seen` keyed on
    `(source_id, src)`, and falls back to a synthetic alt of the form
    `check-in by {author} ({last-8-of-url})` when the <img> has no alt
    attribute. Body is HTML as GitHub returns it for comments/
    discussions — already escaped.
    """
    if not body:
        return
    for tag_match in _IMG_TAG_RE.finditer(body):
        attrs = tag_match.group(1)
        src_match = _IMG_SRC_RE.search(attrs)
        if not src_match:
            continue
        src = src_match.group(1)
        if not src.startswith(USER_ATTACHMENT_PREFIX):
            continue
        key = (source_id, src)
        if key in seen:
            continue
        seen.add(key)
        alt_match = _IMG_ALT_RE.search(attrs)
        # `None` = alt attr absent; "" = alt attr present but empty.
        # Both should trigger the fallback below so broken-image
        # tooltips always say *something* useful.
        alt = alt_match.group(1) if alt_match else None
        if not alt:
            # Fall back to a short identifier derived from the URL hash.
            hash_part = src.rsplit("/", 1)[-1][:8]
            alt = f"check-in by {author} ({hash_part})"
        out.append({
            "author": author,
            "author_avatar": avatar,
            "image_url": src,
            "alt": alt,
            "comment_url": source_url,
            "posted_at": posted_at or "",
        })


def extract_checkins(discussion):
    """Given a Discussion node dict, return list of checkin dicts.

    Dual source:
      1. discussion.bodyHTML — when the OP posts images directly in
         the thread (no separate comment). Authored by the discussion
         author; source_id = discussion number; source_url = the
         discussion url; posted_at = the discussion createdAt.
      2. comments[*].bodyHTML — same as before, source_id = comment id.

    Dedups across both sources via a shared `seen` set keyed on
    `(source_id, image_url)`. Returns [] on falsy input.
    """
    if not discussion:
        return []
    checkins = []
    seen = set()                              # (source_id, image_url)

    # 1) Discussion body itself.
    _disc_author = discussion.get("author") or {}
    body_author = _disc_author.get("login") or "anonymous"
    body_avatar = _disc_author.get("avatarUrl") or ""
    _extract_imgs_from_body(
        body=discussion.get("bodyHTML") or "",
        source_id=f"discussion:{discussion.get('number')}",
        author=body_author,
        avatar=body_avatar,
        source_url=discussion.get("url") or "",
        posted_at=discussion.get("createdAt") or "",
        seen=seen,
        out=checkins,
    )

    # 2) Comments.
    for comment in (discussion.get("comments") or {}).get("nodes") or []:
        author_node = comment.get("author") or {}
        author = author_node.get("login") or "anonymous"
        avatar = author_node.get("avatarUrl") or ""
        _extract_imgs_from_body(
            body=comment.get("bodyHTML") or "",
            source_id=comment.get("id") or comment.get("url") or "",
            author=author,
            avatar=avatar,
            source_url=comment.get("url") or "",
            posted_at=comment.get("createdAt") or "",
            seen=seen,
            out=checkins,
        )
    return checkins


# ---------------------------------------------------------------------------
# Per-window fetch (single category pull, in-memory bucket lookup)
# ---------------------------------------------------------------------------


def build_checkins(token, dates):
    """For each YYYY-MM-DD in dates, return {"checkins": [...], "discussion_url": str|None}.

    One category pull via fetch_all_discussions() per run, then a
    single pass over `dates` index-lookups into the bucket. A category
    fetch that totally fails degrades to empty checkins for every day
    in the window (logged, not crash).
    """
    by_date = index_by_date(fetch_all_discussions(token))
    result = {}
    for d in dates:
        node = by_date.get(d)
        result[d] = {
            "checkins": extract_checkins(node) if node else [],
            "discussion_url": node.get("url") if node else None,
        }
    return result


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------


def _canonical_bytes(data):
    """Serialize `data` (list of window dicts) to canonical bytes for comparison.

    Strips per-item `fetched_at` so cron ticks don't churn commits when
    the only thing that changed since the last run is the timestamp.
    Same ensure_ascii=False / indent=2 / trailing newline as
    `write_json`; the caller still goes through write_json for the
    actual on-disk write (so the tmp+rename atomic-write path is
    preserved).
    """
    canonical = []
    for item in data:
        if not isinstance(item, dict):
            continue
        cleaned = {k: v for k, v in item.items() if k != "fetched_at"}
        canonical.append(cleaned)
    return (json.dumps(canonical, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("[spark-checkins] GITHUB_TOKEN not set", file=sys.stderr, flush=True)
        sys.exit(1)

    os.makedirs(DATA_DIR, exist_ok=True)

    start, end = fetch_window()
    history_dates = fetch_history_dates()
    dates = dates_in_window(history_dates, start, end)
    if not dates:
        print("[spark-checkins] window empty, nothing to do", flush=True)
        return

    print(f"[spark-checkins] fetching {len(dates)} days from {start} to {end}", flush=True)
    fresh = build_checkins(token, dates)
    fetched_at = utc_now_iso()

    # Top-level safety net: if the GitHub fetch came back with nothing
    # useful for every day in the window AND we already have a non-empty
    # data file on disk, refuse to overwrite. A transient API failure
    # would otherwise write a JSON full of empty check-ins, blow away
    # the commit history of the file, and (because hugo.yml watches main)
    # ship the empty version live. Stale data beats missing data.
    fresh_has_content = any(
        v["checkins"] or v["discussion_url"]
        for v in fresh.values()
    )
    existing_bytes = os.path.getsize(OUTPUT_FILE) if os.path.exists(OUTPUT_FILE) else 0
    if not fresh_has_content and existing_bytes > 0:
        print(
            "[spark-checkins] fetch came back empty while existing data is non-empty, "
            "skipping overwrite (likely transient API failure)",
            file=sys.stderr, flush=True,
        )
        return

    # Merge: window dates get the freshly fetched value; everything else in
    # the existing JSON (out-of-window) is preserved verbatim.
    existing = read_json(OUTPUT_FILE, default=[])
    if not isinstance(existing, list):
        existing = []
    existing_by_date = {
        item["date"]: item
        for item in existing
        if isinstance(item, dict) and "date" in item
    }
    in_window_dates = set(dates)

    new_data = []
    for d in dates:
        new_data.append({
            "date": d,
            "fetched_at": fetched_at,
            "discussion_url": fresh[d]["discussion_url"],
            "checkins": fresh[d]["checkins"],
        })
    for item in existing:
        d = item.get("date") if isinstance(item, dict) else None
        if d and d not in in_window_dates:
            new_data.append(item)
    new_data.sort(key=lambda x: x["date"])

    # Byte-level compare so hourly cron doesn't churn commits when nothing
    # changed. We canonicalize both sides (drop per-item `fetched_at`)
    # before comparing — that timestamp is the only thing that would
    # normally differ between an empty run and the previous one, so
    # without the canonicalization we'd commit on every cron tick
    # regardless of upstream content.
    #
    # Canonical comparison works in-memory because `_canonical_bytes`
    # re-serializes from the parsed JSON tree, ignoring whatever line
    # endings / ordering / trailing whitespace the on-disk file happened
    # to have (the previous code's text-mode CRLF workaround was a
    # workaround for the wrong comparison).
    old_data = read_json(OUTPUT_FILE, default=[])
    if _canonical_bytes(new_data) == _canonical_bytes(old_data):
        total_checkins = sum(len(v["checkins"]) for v in fresh.values())
        print(
            f"[spark-checkins] no content changes ({len(dates)} days scanned, {total_checkins} checkins), skipping commit",
            flush=True,
        )
        return

    # Atomic write preserved: tmp + os.replace so partial writes never
    # leave a half-finished JSON file for the workflow's next `git diff`
    # step to see.
    write_json(OUTPUT_FILE, new_data)
    total_checkins = sum(len(v["checkins"]) for v in fresh.values())
    print(
        f"[spark-checkins] wrote {OUTPUT_FILE}: {len(dates)} days, {total_checkins} checkins",
        flush=True,
    )


if __name__ == "__main__":
    main()
