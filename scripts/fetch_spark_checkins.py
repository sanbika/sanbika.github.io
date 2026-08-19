#!/usr/bin/env python3
"""Spark check-ins fetcher.

Pulls GitHub Discussions whose term is `spark-<date>` from
sanbika/sanbika.github.io, extracts user-uploaded images from comment
bodyHTML, writes data/spark_checkins.json. Stdlib only.

Window: last 90 days from today (Shanghai). Per-day GraphQL call so a
single day failing doesn't lose the rest of the window.

Idempotent: byte-level compare against existing JSON; skip write if
nothing changed (so cron can run hourly without spamming commits).

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


def query_discussion(token, date_str):
    """Query GitHub for the discussion whose term is `spark-<date_str>`.

    Returns the Discussion node dict, or None if no matching discussion
    exists. Raises RuntimeError after MAX_ATTEMPTS on retryable errors.
    Non-retryable 4xx raises immediately.
    """
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
                # GraphQL returned 200 with errors[] — treat as retryable.
                raise RuntimeError(f"GraphQL errors: {data['errors']}")
            nodes = (data.get("data") or {}).get("search", {}).get("nodes") or []
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
            print(f"[spark-checkins] sleeping {sleep_for}s before next attempt", flush=True)
            time.sleep(sleep_for)

    raise RuntimeError(f"failed after {MAX_ATTEMPTS} attempts: {last_error}")


# ---------------------------------------------------------------------------
# Image extraction
# ---------------------------------------------------------------------------


def extract_checkins(discussion):
    """Given a Discussion node dict, return list of checkin dicts.

    Drops:
      * discussions with no comments
      * comments whose bodyHTML contains no <img> on github.com/user-attachments/assets/
      * duplicate (comment_id, image_url) pairs

    Each user-uploaded image becomes one checkin item, so a comment with
    two photos yields two items sharing the same author/comment_url.
    """
    if not discussion:
        return []
    checkins = []
    seen = set()                              # (comment_id, image_url)
    for comment in (discussion.get("comments") or {}).get("nodes") or []:
        body = comment.get("bodyHTML") or ""
        author_node = comment.get("author") or {}
        author = author_node.get("login") or "anonymous"
        avatar = author_node.get("avatarUrl") or ""
        comment_url = comment.get("url") or ""
        comment_id = comment.get("id") or comment_url

        for tag_match in _IMG_TAG_RE.finditer(body):
            attrs = tag_match.group(1)
            src_match = _IMG_SRC_RE.search(attrs)
            if not src_match:
                continue
            src = src_match.group(1)
            if not src.startswith(USER_ATTACHMENT_PREFIX):
                continue
            alt_match = _IMG_ALT_RE.search(attrs)
            # `None` = alt attr absent; "" = alt attr present but empty.
            # Both should trigger the fallback below so broken-image
            # tooltips always say *something* useful.
            alt = alt_match.group(1) if alt_match else None
            key = (comment_id, src)
            if key in seen:
                continue
            seen.add(key)
            if not alt:
                # Fall back to a short identifier derived from the URL hash.
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


# ---------------------------------------------------------------------------
# Per-day fetch (tolerates individual day failures)
# ---------------------------------------------------------------------------


def build_checkins(token, dates):
    """For each YYYY-MM-DD in dates, fetch discussion + extract checkins.

    Returns dict: date -> {"checkins": [...], "discussion_url": str|None}.
    A single day's failure is logged and yields empty checkins; doesn't
    abort the whole window.
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
            "discussion_url": discussion.get("url") if discussion else None,
        }
    return result


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
    # changed (an empty run still has a new `fetched_at`, so without this
    # we'd commit on every cron tick).
    #
    # We write the new payload via a tmp file then read it back, instead
    # of comparing in-memory `json.dumps().encode()` against the on-disk
    # file. Reason: text-mode `open(... "w")` on Windows adds CRLF and
    # non-`sort_keys=True` writes keep insertion order, so the in-memory
    # bytes never match what's actually on disk. Round-tripping through
    # a tmp file guarantees the bytes we're about to write are the
    # bytes we're comparing against.
    tmp = OUTPUT_FILE + ".tmp"
    write_json(tmp, new_data)
    with open(tmp, "rb") as f:
        new_bytes = f.read()
    try:
        with open(OUTPUT_FILE, "rb") as f:
            old_bytes = f.read()
    except FileNotFoundError:
        old_bytes = b""
    if new_bytes == old_bytes:
        os.remove(tmp)
        total_checkins = sum(len(v["checkins"]) for v in fresh.values())
        print(
            f"[spark-checkins] no changes ({len(dates)} days scanned, {total_checkins} checkins), skipping commit",
            flush=True,
        )
        return

    os.replace(tmp, OUTPUT_FILE)
    total_checkins = sum(len(v["checkins"]) for v in fresh.values())
    print(
        f"[spark-checkins] wrote {OUTPUT_FILE}: {len(dates)} days, {total_checkins} checkins",
        flush=True,
    )


if __name__ == "__main__":
    main()