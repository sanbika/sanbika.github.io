# Frontend Styling Conventions

The stable conventions for the visual layer. Learned from the 2026 frontend styling optimization round (from HEAD 46e48b5; iterated on by the later brand-color tweak rounds).

## 1. Brand color (Jing Purple)

- **Light**: `#5B5BD6` (quiet purple)
- **Dark**: `#9B9BF5` (lighter purple, AA-readable on PaperMod's dark background)
- Override PaperMod's default `--primary` with a CSS variable in `assets/css/extended/blank.css`:

  ```css
  :root { --primary: #5B5BD6; }
  :root[data-theme="dark"] { --primary: #9B9BF5; }
  ```

- Also declared in `config/_default/params.toml` under `[params.assets] theme_color`, for the browser PWA status bar / Android chrome.
- The dark value **has been confirmed acceptable by the user on a real device** (a personal blog's visual context, not an enterprise-grade WCAG enforcement scenario; it is no longer listed as a TODO, see the TODO section in [[current-state.md]]).
- The history chain (three iterations): `#9B1D20` / `#E15D68` (the initial Cranberry Red, from HEAD 46e48b5) → `#db5079` / `#ef7fa4` (Cranberry Red adjusted, from HEAD 2f660de) → `#5B5BD6` / `#9B9BF5` (Jing Purple, from HEAD c75c10c). The first two versions both sat in the red-pink range, repeatedly pushing saturation down and dark-mode contrast down to AA; this round switching to a purple family was meant to pull the color distance apart again and dodge the "red-pink" sameness in a personal blog's visual language.

## 2. Where custom styles land

- **Site-level CSS overrides always land in `assets/css/extended/`**, which PaperMod merges into the main style chain automatically.
- **Never edit `themes/PaperMod/assets/css/` directly** (it is a theme submodule and would be overwritten on upgrade).
- Naming habit: `blank.css` is a historical placeholder filename (it has already accumulated the brand color / fonts / line-height rhythm); new rules keep being appended rather than spawning several small files, which cuts down on HTTP requests and on mental overhead.
- After adding or removing an override, preview locally with `hugo` to confirm the PaperMod chain merges it correctly.

## 3. The homepage layout is taken over entirely by the site-level `layouts/index.html`

- The homepage redesign (from HEAD 77887e2) **dropped PaperMod's homepage branch of `list.html`** and handed the homepage layout entirely to the site-level `layouts/index.html` template (Hugo resolves the home kind → the site-level `index.html` takes priority over the theme's `list.html`).
- The theme's home_info rendering mechanism is no longer used: the `layouts/_partials/home_info.html` override was deleted, and the bilingual `homeInfoParams.Title/Content` cards in `config/_default/languages.toml` were cleared.
- **The current shape of the homepage** (after the daily board's retirement, 2026-10-20):
  - Main column `.home-main` = **the post list** (sourced from `mainSections` = `["posts"]`, newest first). The archive pages live in the `quests` section and are naturally excluded, so they never mix into the post list.
  - Sidebar `.home-side` = the **「有回响的日子」 / "Echoes"** pick card (the 7 most recent archive pages, linked through `.RelPermalink` so the zh and en sites each use their own path; the whole card is omitted when the list is empty) + a social icon card.
  - **The homepage no longer has a daily quest card, and no giscus at all.** Every comment area lives on the archive pages.
- Requirements touching the homepage (list styling / two-column layout / sidebar content) **go straight into `layouts/index.html`** and the matching `.home-*` rules in `assets/css/extended/blank.css`; do not fall back to `home_info.html`, and do not add `disableSpecial1stPost` back into `params.toml` (it is meaningless now).
- The remaining pages keep using the theme's own templates and are unaffected by this rework: `/about/` uses `themes/PaperMod/layouts/list.html`, and `/search/` uses the theme's search template. The `posts` and `projects` sections no longer exist — their placeholder content was removed on 2026-10-20.
- The conventions for the brand color / theme CSS variables / where site-level overrides land are unchanged (see §1 / §2 / §4).

## 4. The visual language of the archive page quest card (clean modern style)

> **This section used to describe the "pixel-stroked" style, and that description is now void.** The pixel stroke was deliberately dropped in HEAD `1199969` on 2026-08-15, 「style: 任务卡改清爽现代风（去像素描边，底边进度线 hover）」 — rounded corners + a 1px hairline stroke + restrained tinting replaced the `border-image` pixel jaggedness. What follows describes **the actual current state of the CSS**.

### 4.1 The division of labor of the three class families

`assets/css/extended/blank.css` has three easily-confused families of quest-related class names:

| Class family | Where it is used | Status |
|--------|--------|------|
| `.quest-card*` | the **quest card body** of the archive **single-day detail** page `layouts/quests/single.html` (frame / strip / title / task) | in use |
| `.quest__*` | the parts of the archive **single-day detail** page **outside** the card (photo wall / comment area / discussion link / back link) | in use |
| `.quests__*` | the archive **list** page `layouts/quests.html` | in use |

- **`.quest-card*` is the body of the quest card's visual language** (the CSS snippet in §4.3 below describes exactly it), the card header on the archive detail page uses it directly, and you must not start a parallel `.quest__header` style of your own — two parallel sets would leave dead CSS that nobody references.
- **`.quest__*` only carries the structure outside the card**, so do not stuff the card body's visuals (frame / rounded corners / hover tint) into it.
- **`.quests__*` belongs to the list page alone**. The two lists share the same class-name prefix (`.quests__`) but mean different things, so watch out when reusing it across pages.
- The comment area has two external links with different meanings: `.quest__ghlink` (giscus's own fallback, pointing at the GitHub Discussions search page, inheriting the secondary color of `.quest__comments p a`, **deliberately without a rule of its own**) and `.quest__discussion` (pointing at that specific year's discussion, distinguished with the brand color + a semibold weight). Do not merge them into one.
- **Three `.quests__*` classes carry semantics only — they have no visual rule of their own.** `.quests` (the list page's outer wrapper `<div>`), `.quests__intro` (the page header `<header>`) and `.quests__date` (the `<time>` element inside the `.quests__meta` flex row) are layout hooks: what you actually see is styled either by their children (`.quests__title` / `.quests__desc` for the header) or by their parent (`.quests__meta` for the date line). **This is intentional, not dead CSS** — do not add a rule for them just to make them "real", and do not delete the markup to tidy up the selector list. To change how the header or the date line looks, change the rule that already owns it.

> **Leftovers that were cleaned up** (deleted together with the 2026-10-20 retirement — do not add them back):
> - the `--pix` token — once the pixel stroke was dropped it became a dead token and was removed from `:root` and `:root[data-theme="dark"]`.
> - the `.quests__discussion` rule — the list page no longer renders a "check-in discussion" link (the title itself is already the link), so it was deleted.
> - the whole `.spark-checkin__*` family — the homepage check-in block was retired wholesale; among it, the class of the giscus fallback link was renamed to `.quest__ghlink` (see `layouts/_partials/spark_comments.html`).

### 4.2 Core principles (hard constraints)

- **No emoji** — no emoji anywhere in the card, and no emoji concatenated into the text. Emoji rendering depends on the system font stack (color emoji render noticeably differently across macOS / Windows / Linux), so an emoji next to a label only duplicates the label and reads differently on every machine.
- **No buttons without a function** — no accepting a quest, no ticking it off, no archiving, no favoriting, no liking. The quest card is a **read-only display card**, not an interaction entry point. "A button with no path to fulfillment should not appear" and "a badge with no persistence (difficulty★/XP/achievements) should not be added" are the same principle.
- **No decorative layers without a function** — the card keeps only the information hierarchy (title → quest body), and does not add atmosphere elements just to "look like a game panel". The pixel stroke / torn-ticket dashed line / quest-bar CTA were all things deleted under this principle.
### 4.3 The card frame and hover

```css
.quest-card {
  position: relative;
  overflow: hidden;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--theme);
  transition: border-color 0.25s ease, background-color 0.25s ease;
}

.quest-card:hover {
  border-color: var(--primary);
  background: rgba(91, 91, 214, 0.04);
}

[data-theme="dark"] .quest-card:hover {
  background: rgba(155, 155, 245, 0.06);
}
```

- **Rounded corners + a 1px hairline stroke**: `border-radius: var(--radius)` + `border: 1px solid var(--border)`, with the background color `var(--theme)`. The geometric premise is "rounded corners", no longer square corners — never add `border-radius: 0` to any `.quest-card*`.
- `overflow: hidden` makes the strip's bottom divider line align with the card's rounded corners (otherwise a child's border would overrun the parent's radius).
- **Hover only changes color, it does not shift and it does not add a shadow**: the border turns `--primary` and the background picks up a faint indigo tint (4% alpha in light mode / 6% in dark mode). This is a **change of hue**, not an animation.
- The hover background color **must be written as an explicit rgba pair**, it cannot be derived from `--theme` — `--theme` is white in light mode and dark grey in dark mode, the two bases are too far apart for the same mix to read as an effect on both sides.
- Because there is only a color transition and no movement, **no `prefers-reduced-motion` fallback is needed**. The media query exists only to cover motion that actually exists.

### 4.4 The card structure

- **`.quest-card__strip`** top bar: a flex row (`justify-content: space-between` + `flex-wrap: wrap`), with the brand copy on the left and the date + the `#MMDD` number on the right, followed by a 1px `var(--border)` divider line. `font-size: 0.75em` + `letter-spacing: 0.08em` + `color: var(--secondary)`; the English page goes all-caps via `:lang(en) { text-transform: uppercase }`.
- **`.quest-card__strip-right`** right group: inline-flex, `align-items: baseline` (so that the date and the number share a baseline), with `font-variant-numeric: tabular-nums` so the digits of the number line up.
- **`.quest-card__body`** main body: `padding: var(--gap)`, matching the rhythm of the outer grid.
- **`.quest-card__title`** title: `var(--primary)`, `font-size: 1.55em`, `font-weight: 700`, `line-height: 1.3`, `text-wrap: balance` (with `-webkit-text-wrap: balance` for older Safari) — this avoids a lone trailing character on long Chinese titles. The Chinese page has 「」 added by the template, the English page keeps the bare title.
- **`.quest-card__task`** quest body: `var(--secondary)`, `font-size: 1.02em`, `line-height: 1.65`.
- **There is no CTA / accept button / duration line** — see §4.2 "no buttons without a function".

### 4.5 The category badge was removed (2026-10-20)

- **The per-day category badge is gone.** Every archive page carried a category label (`spark_tag`: 探索 / 内省 / 健康 / 社交, en: Exploration / Introspection / Health / Social) rendered as a small Jing-purple chip. Once only 8 days survived, the label no longer carried any meaning, so the `spark_tag` front matter field was removed from every archive content page.
- **The badge had three render sites** — `.quest-card__kicker` (inside the card on the detail page), `.quests__tag` (on a list page entry) and `.home-side__tag` (in the homepage sidebar) — and all three shared one hard-coded color pair (`rgba(91, 91, 214, 0.14)` / `#5B5BD6` in light mode, `rgba(155, 155, 245, 0.18)` / `#9B9BF5` in dark mode). All three rule sets were deleted together with the `spark_tag` field; none of those class names is in use any more.
- **Do not bring the badge back.** A category chip over eight archived days is decoration without a function (§4.2), and a category label is a language-dependent front matter value (`docs/conventions/i18n.md` §1).

### 4.6 Cross-language determinism of the quest number

The quest number `#MMDD` is derived from the ISO date `YYYY-MM-DD` (strip the dashes and take the last 4 digits), **not from the display date**, so the result is consistent across languages and across builds. The visual anchor does not depend on emoji (already removed in §4.2).

> `#MMDD` is rendered by the archive detail page template `layouts/quests/single.html` (the `.quest-card__id` on the right of the strip), and the zh and en versions compute the same value. **Do not change it to "derive it from the display date"** — that would make the same content compute different numbers in the zh / en versions.

### 4.7 Empty states

- The data source of the archive page is a **controlled content page** (`content/quests/<date>.md`), so the "dirty data" problem is gone and the historical JSON approach (a regex plus multiple layers of `isset` guards) is no longer needed.
- The only thing that still needs a nil guard is `hugo.Data.spark_checkins` (in theory the data file may not exist, and `where <nil>` errors out directly): assign it first and then guard nil with `if $data`.
- When a given day has no check-in photos (an empty `checkins` array), the whole photo wall is not rendered — **no empty shell is left behind**.
- When the list is empty, `.quests__empty` is rendered (a single line of hint text); when the homepage sidebar pick is empty, **the whole card is omitted** and only the social icon card remains.

### 4.8 Things explicitly not to do

- **No emoji**: see §4.2
- **No buttons without a function** (accept / complete / favorite / like, etc.): see §4.2
- **Do not reintroduce a badge mechanism that is never recorded** (difficulty★ / XP / achievement systems, etc.): these have no persistence and no real path to fulfillment, and come from the same source as "no buttons without a function"
- **Do not reintroduce the pixel stroke** (`border-image` / `--pix` / `border-radius: 0` / square geometry): this set was deliberately abandoned in HEAD `1199969`, on the grounds that the pixel jaggedness is incompatible with rounded corners and that the hard outline is too harsh. The current rule is "rounded corners + a 1px hairline stroke + restrained tinting"
- **Do not reintroduce the torn-ticket dashed line / hover transform / box-shadow**: hover only changes color, and adding movement would mean reintroducing motion and the reduced-motion fallback
- **Do not leave dead tokens in the CSS**: when you change styles, confirm on the spot that the class names you reference are still in the templates (§4.1)

## 5. The homepage post list and the sidebar pick

- **Current state (2026-10-20)**: the placeholder "Hello World" post was deleted along with the other placeholder content, so `content/posts/` is empty and the main column renders the existing `.home-posts__empty` empty state (「还没有文章。」 / "No posts yet."). The sidebar's archive pick is therefore the homepage's only live content right now — that is the intended state, not a rendering bug.
- **`.home-posts*`** (the main column post list): the list has no bullet styling, `margin: 0`; each `.home-post` gets a bottom border line (`border-bottom: 1px solid var(--border)`, removed on the last one), and contains `.home-post__date` (`--secondary`, 0.8em, `tabular-nums`), `.home-post__title` (`--primary`, 1.2em, 700) and `.home-post__desc` (`--secondary`, 0.95em, `line-height: 1.6` to suit the breathing room of Chinese text). The title link falls back to `--secondary` on hover, and `:focus-visible` draws a 2px dashed outline with the theme token.
- **`.home-side__*`** (the sidebar card): `.home-side__card` is a small card with a 1px `--border` stroke and `--radius` rounded corners; `.home-side__heading-row` is the heading row with the title on the left and 「查看全部 →」 / "All →" on the right; `.home-side__link` is the link of each archived day (a dashed separator on top + `--primary` text color); `.home-side__meta` is a flex row (thumbnail + date); `.home-side__thumb` is a 28×28 decorative thumbnail (empty `alt`, `border-radius: 5px`).
- The sidebar `.home-side` uses `position: sticky` to follow the scroll (`top` overrides the theme's fixed header `--header-height`); below `<768px` the grid collapses into a single column and `sticky` is switched off at the same time (a single-column page has nothing to stick, and the inherited top offset would only leave a gap).

## 6. The check-in photo pipeline

- **The thumbnails are cropped by Hugo, not by the browser.** All three check-in photo walls — the 28×28 sidebar thumbnail, the 64×64 list-page thumbnail and the 96×96 detail-page thumbnail — go through `layouts/_partials/checkin_image.html`, which hands the repository-local copy (`assets/img/checkins/`) to Hugo's image pipeline and asks for a square **WebP at 2× the CSS size** (`Fill "<2*size>x<2*size> center webp q80"`). The 2× factor is what keeps them sharp on a retina screen; `center` reproduces what the stylesheet's `object-fit: cover` was doing in the browser.
- **Never point a thumbnail at the original.** The check-in photos were originally served straight from GitHub's attachment CDN, which redirects to an S3 bucket and serves the **full-resolution original** — the largest was a 3060×4080, 2.6 MB phone photo. A 28×28 sidebar thumbnail therefore pulled 2.6 MB, and on a slow or filtered network the request never completed, so the browser rendered a broken-image icon. Serving the crops from the site's own origin removed the third-party dependency and took the home page's image payload from ~2.9 MB to ~2 KB.
- **The committed copies are already shrunk.** `assets/img/checkins/*.jpg` holds copies at ≤800px wide (≈260 KB for all four) — the thumbnails never need more, and committing the originals would put a 2.6 MB phone photo in the repository for a 192px crop. The full-resolution original stays where it always was, on GitHub's CDN, reachable through the discussion comment link next to every thumbnail.
- **`data/spark_checkins.json` carries both.** `image_url` is the remote original (the source of truth, and the fallback when a local copy is missing); `local_image` is the path of the repository-local copy, relative to `assets/`. When a check-in has no `local_image`, the partial falls back to `image_url` and the photo still renders — just heavy, and dependent on the third-party host.
- **`resources/_gen/` is the image cache** and is gitignored; Hugo re-derives the crops on every clean build.
