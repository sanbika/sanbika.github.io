"""Shared stdlib utilities for the blog's Python scripts.

Originally lived in scripts/daily_spark.py; extracted so other scripts
(notably scripts/fetch_spark_checkins.py) can reuse the same primitives
without copy-paste drift. Keep this module:

  * **stdlib only** — no pip dependencies (GitHub Actions runner is bare)
  * **side-effect free at import time** — `python3 -c "import _lib"` must
    never touch disk, network, or env
  * **no project-specific knowledge** — no API endpoints, no Giscus IDs, etc.

Adding new shared helpers here is fine; introducing classes or per-script
config is not — promote to a per-script module instead.
"""
import json
import os
import sys
import time
import urllib.error
from datetime import datetime, timezone, timedelta

# ---------------------------------------------------------------------------
# Time / TZ
# ---------------------------------------------------------------------------

SHANGHAI_TZ = timezone(timedelta(hours=8))
WEEKDAY_NAMES_ZH = (
    "星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日",
)


def today_shanghai_date():
    """Return today's date in Shanghai as a 'YYYY-MM-DD' string.

    Same string form `data/daily_spark.json` uses, so scripts comparing
    against it don't need a date.fromisoformat round-trip.
    """
    return datetime.now(SHANGHAI_TZ).strftime("%Y-%m-%d")


def utc_now_iso():
    """Return current UTC time as ISO8601 with trailing 'Z'.

    Used as `fetched_at` in data files so consumers can tell when the
    data was last refreshed without an extra timestamp column.
    """
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# HTTP retry
# ---------------------------------------------------------------------------

MAX_ATTEMPTS = 4                       # initial try + 3 retries
BACKOFFS_SECONDS = (10, 20, 40)        # sleeps between attempts
HTTP_BODY_PREVIEW_BYTES = 500


def _is_retryable_http(code):
    """429 (rate limit) and 5xx are retryable; other 4xx are not."""
    if code == 429:
        return True
    if isinstance(code, int) and 500 <= code < 600:
        return True
    return False


def _http_error_log(e):
    """Build a safe log line for HTTPError: status + body preview, never the API key."""
    code = getattr(e, "code", "?")
    body_preview = ""
    try:
        raw = e.read()
        body_preview = raw[:HTTP_BODY_PREVIEW_BYTES].decode("utf-8", errors="replace")
    except Exception:
        body_preview = "<unreadable body>"
    return f"HTTP {code}: {body_preview}"


# ---------------------------------------------------------------------------
# JSON I/O
# ---------------------------------------------------------------------------


def read_json(path, default):
    """Read JSON; on missing/corrupt/unreadable file, return default (do not crash)."""
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, ValueError, OSError) as e:
        print(
            f"[lib] failed to read {path}: {e}; falling back to default",
            file=sys.stderr,
            flush=True,
        )
        return default


def write_json(path, obj):
    """Atomic write via tmp + os.replace. Caller decides indent."""
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.replace(tmp, path)