# Giscus Comment Conventions

The stable conventions for the Giscus integration and its multi-category routing. Learned from the 2026 homepage redesign (from HEAD 77887e2) and the daily check-in comment migration (from HEAD 7339b19).

The "Daily Spark" board was retired on 2026-10-20 (the generation and scraping mechanisms were deleted), but **the comment routing itself still holds**: the 10 surviving archive days (`content/quests/<date>.md`) keep using that year's `daily-spark` category and `spark-<date>` term, each hooking back to that year's discussion.

## 1. The two comment scenarios and their categories

| Scenario | Rendered at | Category | mapping | term |
|------|---------|------|---------|------|
| Article comments | `themes/PaperMod/layouts/_default/single.html` → `layouts/_partials/comments.html` | `General` | `pathname` | the article's permalink path |
| Daily quest on an archive page | `layouts/quests/single.html` → `layouts/_partials/spark_comments.html` | `daily-spark` | `specific` | `spark-{YYYY-MM-DD}` |

- The two categories are **physically isolated on the giscus repository side**: the URL of one article will never appear under the daily-spark category, and a given day's spark comments will never appear under the General category either.
- That means switching categories is **one-way and irreversible**: the old discussions stay in the original category, and once they have been moved to a new category they cannot flow back (see §4).
- **The homepage has no giscus.** After the daily board's retirement the homepage renders no comment area at all; every comment lives on its own archive page.

### 1.1 Comment hooking rules for archive pages (stable convention)

- **An archive page must use `specific` mapping + a `spark-<date>` term + the `daily-spark` category** to hook back that year's discussion. giscus looks up by `category + term`, and a difference in either one means **a different thread** — switching to `pathname` (the `comments.html` setup) would hook onto a new thread under the General category, and not a single old comment would show up.
- **The only source of the term is the front matter's `spark_date`**: the `$date` in `data-term="spark-{{ $date }}"` inside `layouts/quests/single.html` comes from `.Params.spark_date`. When `spark_date` is missing it falls back to the page's own `.Date`, which guarantees the term is never empty (an empty term would bleed into a different thread).
- **An archive page must not render `comments.html` at the same time.** The theme-switching JS of the two partials each carries a MutationObserver, and having them coexist on one page makes them fight each other (see §5). Article pages currently use only `comments.html` and archive pages only `spark_comments.html`, so there is no same-page case.
- **The category id lives in exactly one place**: `comments.spark.categoryid` in `config/_default/params.toml`. The scraping script was deleted along with the daily board's retirement, so the "two literals must stay in sync" problem is gone.
- **A rename does not change the key**: the board was renamed from 「每日隐藏任务」 to 「回响」 / "Echoes", but neither the `/quests/` URL nor the `spark-<date>` term changed — the former is depended on by old external links, the latter by the old comments, and neither may be touched.

## 2. Division of labor between configuration sources

Under `[params.comments]` in `config/_default/params.toml`:

```toml
[params.comments]
  enabled = true
  provider = "giscus"
  [params.comments.giscus]    # shared fields: repo / repoId / mapping / lang / theme / reactions…
    repo = "…"
    repoId = "…"
    category = "General"       # default category for article comments
    categoryid = "DIC_…"
    mapping = "pathname"
    lightTheme = "light"
    darkTheme = "dark_dimmed"
    reactionsEnabled = true
  [params.comments.spark]      # archive pages only: category-related fields
    category = "daily-spark"
    categoryid = "DIC_kwDOT2zk8c4DDbVZ"
```

- The **general fields** (repo / repoId / lang / theme / reactions) are configured only in `comments.giscus`, and both partials read them from there.
- The **`spark` sub-table holds only category-related fields** (`category` / `categoryid`); the mapping / term are hard-coded in the `spark_comments.html` template as `specific` + `spark-{date}` and do not enter the configuration — they are the inherent semantics of this comment scenario and have no second set of possible values.
- **`[params.comments.spark]` is now for the archive**: it is the **home** of the 10 historical discussions, not the companion configuration of "daily scraping". The daily generation and scraping mechanisms were deleted on 2026-10-20 (this repo no longer has a `scripts/` directory and no scraping workflow at all), so this sub-table only serves the giscus embed.
- `comments.giscus.category` still keeps `General` + `categoryid`, because `comments.html` uses it; do not empty out `comments.giscus.category` just because `spark` has a dedicated category of its own.

## 3. The process for adding a third comment scenario

When a new category has to be introduced (e.g. "reading notes", "project page feedback" etc.), follow this order:

1. **Create the category on the giscus repository side** — add a category to the Discussions categories of the sanbika.github.io repository, and note down the category name + `categoryId` (starting with DIC_).
2. **Add the configuration in `params.toml`** — add a sub-table under `[params.comments]`, named following the `<scenario name>` pattern (lowercase, hyphenated); put only `category` / `categoryid` in it, and keep inheriting the general fields from `comments.giscus`.
3. **Create a new partial** — copy `spark_comments.html` and rename it to `<scenario>_comments.html`; choose `data-mapping` / `data-term` according to the scenario's semantics (specific → `specific` + a custom term; generic → `pathname`); prefix the theme-switching JS function name with the scenario (e.g. `setSparkGiscusTheme`) so it does not collide with `comments.html` / other partials on the same page.
4. **Wire up the call site** — call it in the matching Hugo template with `partial "<scenario>_comments.html" (...)`.
5. **Update this conventions file** — add a row to the §1 table and a new sub-table example to the §2 code block.

> The order of the steps must not be changed: **create the category first, then write the configuration**. Writing a `categoryid` before the category exists on the giscus repository side yields an invalid Giscus embed (the iframe fails silently — no error, but no comments either).

## 4. Migration history and hygiene notes

- **HEAD 77887e2**: homepage redesign, spark comments integrated for the first time, using the General category of `comments.giscus` + `specific` mapping + a `spark-<date>` term.
- **HEAD 7339b19**: spark comments moved to a dedicated `daily-spark` category, physically isolated from the article General category.
- **Migration side effect**: before the switch (between HEAD 77887e2 and 7339b19), if somebody left a comment under `spark-<date>` in the old General category, it **will not show up** after the move — giscus looks up by `category + term`, and the original discussion stays behind in GitHub General with no way back. There is no remedial action on this repo's side; that part of the comment history is treated as abandoned.
- **Empty discussions are created lazily**: giscus creates lazily — when the term matches no discussion nothing is pre-created, and a discussion only really comes into being when a user submits their first comment. An empty comment area under a new category produces no GitHub node at all, so there is nothing to clean up on this repo's side.
  - **This property became the criterion for the survivor set at the 2026-10-20 retirement**: a discussion existing under the `daily-spark` category ⟺ somebody really did comment that day. The retirement used exactly this criterion to pick 10 days out of 67 and promote them to archive pages (4 of them also have check-in photos).
- **Board retirement (2026-10-20)**: the generation / scraping mechanisms were deleted, but the `daily-spark` category was **deliberately kept** — the 10 historical discussions live there, and deleting the category would mean deleting the comments themselves. `[params.comments.spark]` in `config/_default/params.toml` is kept accordingly.
- For the history see [[current-state.md]] (the retirement round in Recent Changes) and the TODO section.

## 5. Known leftovers

- **The two giscus partials must not render on the same page** (the theme-switching JS of `comments.html` + `spark_comments.html` each has a MutationObserver, and they conflict on one page). Article pages currently use only `comments.html` and archive pages only `spark_comments.html`, so there is no same-page case. If they ever have to be mixed on one page, the functions and observers need to be merged. See the TODO in [[current-state.md]].
- **The `data-lang` condition is not robust for a future third language — fixed.** `comments.html` and `spark_comments.html` are now unified to `cond (eq .Lang "en") "en" (default .Lang .Site.Language.LanguageCode)`: English is forced to `en` (giscus is case-sensitive), and for every other language the **site-level** `languageCode` is the value that gets emitted, with the page-level `.Lang` as the fallback. Note the argument order — Hugo's `default` returns its **second** argument when that argument is non-empty, so `default .Lang .Site.Language.LanguageCode` means "use `LanguageCode`, fall back to `.Lang`". This order is deliberate: the site-level `languageCode` is the code giscus recognises (`zh-CN`, case-sensitive), whereas the page-level `.Lang` is only the lowercased language key (`zh-cn`), which giscus does not recognise. Swapping the two arguments would silently downgrade the Chinese comment UI to English.
  - Residual edge (giscus behavior, not this repo's responsibility): a language code giscus does not know about silently falls back to English.
