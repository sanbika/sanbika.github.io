#!/usr/bin/env python3
"""
Daily Spark generator.

Reads MiniMax API credentials from env, asks the model for a bilingual
"daily spark" challenge, writes:
  - data/daily_spark.json           (today's card)
  - data/daily_spark_history.json   (append-only, deduped by date,
                                     capped at MAX_HISTORY entries)

Stdlib only — no pip install required in GitHub Actions.
"""

import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone, timedelta

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

SHANGHAI_TZ = timezone(timedelta(hours=8))
ALLOWED_TAGS_ZH = ("生活", "学习", "创造", "运动")
ALLOWED_TAGS_EN = ("Life", "Learning", "Creating", "Movement")
WEEKDAY_NAMES_ZH = (
    "星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日",
)

MAX_ATTEMPTS = 4                       # initial try + 3 retries
BACKOFFS_SECONDS = (10, 20, 40)        # sleeps between attempts
MAX_HISTORY = 365                      # keep last N entries
HTTP_BODY_PREVIEW_BYTES = 500

DATA_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    os.pardir,
    "data",
)
TODAY_FILE = os.path.join(DATA_DIR, "daily_spark.json")
HISTORY_FILE = os.path.join(DATA_DIR, "daily_spark_history.json")


SYSTEM_PROMPT = """你是「地球Online 每日隐藏任务（Daily Spark）」生成器，为个人博客生成每日小挑战（Daily Spark），目标是给日常生活提亮。

要求：
1. 领域在 生活 / 学习 / 创造 / 运动 中轮换（按日期伪随机，不必均匀）
2. 任务必须：当天可完成、耗时 15-30 分钟、零成本或成本极低、无需特殊装备或同伴、安全、不涉及医疗/政治/宗教等敏感内容
3. 任务要具体可执行，带一点小巧思或新鲜感；禁止空洞鸡汤和老生常谈（如「多喝水」「早点睡」这类禁止出现）
4. 中英文语义一致，英文自然地道
5. 只输出 JSON，不要 markdown 代码块，不要任何其他文字，字段结构：
{"date":"YYYY-MM-DD","tag":{"zh":"生活","en":"Life"},"zh":{"title":"不超过8个字","task":"一句话，不超过40字，具体描述做什么"},"en":{"title":"不超过6个词","task":"one sentence, concrete"}}
tag 的 zh 固定为 生活/学习/创造/运动 之一，en 对应 Life/Learning/Creating/Movement。"""


def today_shanghai():
    now = datetime.now(SHANGHAI_TZ)
    return now.strftime("%Y-%m-%d"), WEEKDAY_NAMES_ZH[now.weekday()]


def build_user_message(date_str, weekday_zh):
    return f"今天是{date_str}（北京时间，{weekday_zh}）。请生成今天的挑战，可以结合季节/星期增加变化。"


# ---------------------------------------------------------------------------
# MiniMax API
# ---------------------------------------------------------------------------

def call_minimax(api_key, base_url, model, user_message):
    url = base_url.rstrip("/") + "/v1/text/chatcompletion_v2"
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        "temperature": 0.9,
    }
    payload = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + api_key,
        },
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        raw = resp.read().decode("utf-8")
    return json.loads(raw)


def extract_content(api_response):
    choices = api_response.get("choices") or []
    if not choices:
        raise ValueError("API response missing 'choices'")
    message = choices[0].get("message") or {}
    content = message.get("content")
    if not isinstance(content, str) or not content.strip():
        raise ValueError("API response missing message.content")
    return content


def strip_code_fence(text):
    s = text.strip()
    if s.startswith("```"):
        # strip first line (```json or ```) and trailing ```
        lines = s.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        s = "\n".join(lines).strip()
    return s


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


def validate_payload(obj, expected_date):
    if not isinstance(obj, dict):
        raise ValueError("payload is not an object")

    # Date mismatch is non-fatal: coerce to expected_date instead of retrying.
    # The model is told the date explicitly in the user message, so a mismatch
    # almost always reflects a harmless stragglers response. All other fields
    # are validated strictly.
    obj["date"] = expected_date

    tag = obj.get("tag")
    if not isinstance(tag, dict):
        raise ValueError("tag missing or not object")
    tag_zh = tag.get("zh")
    tag_en = tag.get("en")
    if tag_zh not in ALLOWED_TAGS_ZH:
        raise ValueError(f"invalid tag.zh: {tag_zh!r}")
    expected_en = ALLOWED_TAGS_EN[ALLOWED_TAGS_ZH.index(tag_zh)]
    if tag_en != expected_en:
        raise ValueError(f"tag.en mismatch: got {tag_en!r}, want {expected_en!r}")

    for lang_key in ("zh", "en"):
        lang = obj.get(lang_key)
        if not isinstance(lang, dict):
            raise ValueError(f"{lang_key} missing or not object")
        title = lang.get("title")
        task = lang.get("task")
        if not isinstance(title, str) or not title.strip():
            raise ValueError(f"{lang_key}.title empty")
        if not isinstance(task, str) or not task.strip():
            raise ValueError(f"{lang_key}.task empty")

    return obj


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------

def ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def read_json(path, default):
    """Read JSON; on missing/corrupt/unreadable file, return default (do not crash)."""
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, ValueError, OSError) as e:
        print(
            f"[daily-spark] failed to read {path}: {e}; falling back to default",
            file=sys.stderr,
            flush=True,
        )
        return default
    return data


def write_json(path, obj):
    """Atomic write via tmp + os.replace."""
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.replace(tmp, path)


def build_history(existing, payload):
    """Build deduped+sorted+trimmed history in-memory; never touch disk here."""
    history = list(existing) if isinstance(existing, list) else []
    history.append(payload)
    seen = set()
    deduped = []
    for item in history:
        d = item.get("date") if isinstance(item, dict) else None
        if d in seen:
            continue
        seen.add(d)
        deduped.append(item)
    deduped.sort(key=lambda x: x.get("date", "") if isinstance(x, dict) else "")
    if len(deduped) > MAX_HISTORY:
        deduped = deduped[-MAX_HISTORY:]
    return deduped


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

def generate(api_key, base_url, model):
    date_str, weekday_zh = today_shanghai()
    user_message = build_user_message(date_str, weekday_zh)
    last_error = None

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            print(f"[daily-spark] attempt {attempt}/{MAX_ATTEMPTS}", flush=True)
            response = call_minimax(api_key, base_url, model, user_message)
            content = extract_content(response)
            cleaned = strip_code_fence(content)
            obj = json.loads(cleaned)
            payload = validate_payload(obj, date_str)
            return payload

        except urllib.error.HTTPError as e:
            detail = _http_error_log(e)
            if _is_retryable_http(e.code):
                last_error = detail
                print(f"[daily-spark] retryable {detail}", flush=True)
            else:
                # Non-retryable 4xx: fail immediately, do not sleep, do not retry.
                raise RuntimeError(f"non-retryable {detail}") from e

        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            last_error = f"network error: {e}"
            print(f"[daily-spark] {last_error}", flush=True)

        except json.JSONDecodeError as e:
            last_error = f"JSON parse error: {e}"
            print(f"[daily-spark] {last_error}", flush=True)

        except ValueError as e:
            # Validation error: strict on every field except date (handled above).
            last_error = f"validation error: {e}"
            print(f"[daily-spark] {last_error}", flush=True)

        except Exception as e:  # pragma: no cover - defensive
            last_error = f"unexpected error: {e}"
            print(f"[daily-spark] {last_error}", flush=True)

        if attempt < MAX_ATTEMPTS:
            sleep_for = BACKOFFS_SECONDS[attempt - 1]
            print(f"[daily-spark] sleeping {sleep_for}s before next attempt", flush=True)
            time.sleep(sleep_for)

    raise RuntimeError(f"failed after {MAX_ATTEMPTS} attempts: {last_error}")


def main():
    api_key = os.environ.get("MINIMAX_API_KEY")
    base_url = os.environ.get("MINIMAX_BASE_URL") or "https://api.minimaxi.com"
    model = os.environ.get("MINIMAX_MODEL") or "MiniMax-M2"

    if not api_key:
        print("[daily-spark] MINIMAX_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    ensure_data_dir()

    try:
        payload = generate(api_key, base_url, model)
    except RuntimeError as e:
        print(f"[daily-spark] FAILED: {e}", file=sys.stderr)
        sys.exit(2)

    # Compute history fully in memory BEFORE writing anything to disk, so that
    # a write failure cannot leave behind a half-updated pair of files.
    existing_history = read_json(HISTORY_FILE, default=[])
    new_history = build_history(existing_history, payload)

    try:
        write_json(TODAY_FILE, payload)
        write_json(HISTORY_FILE, new_history)
    except OSError as e:
        print(f"[daily-spark] FAILED to write data files: {e}", file=sys.stderr)
        sys.exit(3)

    # Log the result without leaking the API key.
    print(
        "[daily-spark] OK date={date} tag_zh={tag_zh} zh_title={zh_title} en_title={en_title}".format(
            date=payload["date"],
            tag_zh=payload["tag"]["zh"],
            zh_title=payload["zh"]["title"],
            en_title=payload["en"]["title"],
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()