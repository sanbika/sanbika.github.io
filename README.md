# 浆果丛林 / Berry Jungle

A personal blog and personal homepage. Built with [Hugo](https://gohugo.io/) + the [PaperMod](https://github.com/adityatelange/hugo-PaperMod) theme, hosted on GitHub Pages.

- Live site: <https://sanbika.github.io>
- Repository: <https://github.com/sanbika/sanbika.github.io>

## Tech stack

- **Static generation**: Hugo extended v0.164+
- **Theme**: PaperMod (git submodule)
- **Deployment**: GitHub Actions → the official [`actions/deploy-pages`](https://github.com/actions/deploy-pages) → GitHub Pages
- **Comments**: [Giscus](https://giscus.app/) (built on GitHub Discussions)
- **Search**: Fuse.js, built into PaperMod (client-side index)
- **Analytics**: Google Analytics 4

The site is **purely static**: no server, no database, no build-time scraping. The build output is the `public/` directory.

## Local development

```bash
hugo server -D
```

It serves at <http://localhost:1313/> by default.

### Installing Hugo

```bash
winget install --id=Hugo.Hugo.Extended
```

macOS: `brew install hugo`, Linux: `snap install hugo --channel=extended`.

## The Echoes archive (`/quests/`)

The site used to have a "Daily Spark" board —— every day the model generated one small life challenge together with a check-in comment area for that day. **That board was retired on 2026-10-20**: the daily generation and the hourly image scraping were deleted along with the entire `scripts/` directory, and the repository no longer contains any generation / scraping workflow.

The retirement kept **the days that got a response**: the 10 days on which a discussion was really opened in GitHub Discussions (giscus creates lazily —— the existence of a discussion means somebody did comment). 4 of those days additionally have check-in photos.

- **Entry point**: `/quests/` (「回响」 in Chinese / "Echoes" in English; the zh and en sites each have their own path, `/quests/` and `/en/quests/`)
- **Archive pages**: the 10 days exist as ordinary content pages under `content/quests/<date>.md` (one per language), and each one hooks back to **that year's GitHub Discussion thread** (the `daily-spark` category, term `spark-<date>`)
- **Photo wall**: the photo metadata lives in `data/spark_checkins.json` and is a **frozen snapshot** (4 entries: 2026-08-17 / 08-19 / 08-21 / 08-24) that no longer updates on its own. The photos are **also kept in the repository** under `assets/img/checkins/`, so Hugo crops and re-encodes them and the thumbnails are served from this site's own origin — the `image_url` in the data file still points at the full-resolution original on GitHub's CDN and is used only as a fallback
- **The key property**: comments and photos have always lived on GitHub (Discussions + the `user-attachments` CDN) and the site is only a viewer —— so changing the URL structure loses no comments, and freezing the site side does not stop people from replying in those 10 discussions

## Writing

Create Markdown under `content/posts/`:

```markdown
---
title: "标题"
date: 2026-08-13T10:00:00+08:00
tags: ["标签"]
categories: ["分类"]
description: "一句话摘要"
draft: false
comments: true
---

正文（Markdown 全语法支持）。
```

For the bilingual version: create `*.en.md` in the same directory, add `lang: "en"`, and write the English `title` in the front matter.

> The directory is currently empty —— the placeholder "Hello World" post was removed on 2026-10-20 —— but `mainSections` already points at it, so the first real post shows up on the home page and in the feed automatically.

### Adding an archived day

Add a pair of files under `content/quests/` (`<date>.md` + `<date>.en.md`) following this front matter contract:

```yaml
---
title: "观察生活的隐喻"        # 不带书名号，模板负责加「」
date: 2026-08-17T00:00:00+08:00
description: "任务正文"
spark_date: "2026-08-17"        # giscus term 的唯一来源
discussion: "https://github.com/sanbika/sanbika.github.io/discussions/4"
---
```

- **`spark_date` must line up with that discussion in GitHub Discussions** —— the term is exactly `spark-<spark_date>`. If it does not line up, giscus hooks onto an empty new thread and the old comments of that day are invisible.
- `discussion` holds the direct link to that year's discussion (filling it in adds a "View that day's GitHub discussion ↗" entry below the comment area).
- Dates are always parsed from the `spark_date` string —— the front matter `date` carries a `+08:00` offset, which rolls back a day when converted to UTC on the build machine.
- Photos do not go into the front matter: `data/spark_checkins.json` is matched on `spark_date`, photo metadata is language-neutral, and the zh and en versions need not repeat it.
- **Adding a photo means adding it to the repository too.** The site renders a small locally-generated WebP crop of each photo, never the GitHub CDN original: a 28×28 sidebar thumbnail pointing at the original would pull a 2.6 MB phone photo, and on a slow or filtered network the image never arrives (the browser shows a broken-image icon). So drop a copy under `assets/img/checkins/<date>.jpg` — **shrink it to ≤800px wide first**, the thumbnails never need more — and point the check-in entry's `local_image` at it. `layouts/_partials/checkin_image.html` then crops it to 2× the CSS size for whichever page asks (28px sidebar / 64px list / 96px detail).

See `docs/conventions/giscus.md` for the details of these conventions.

## Project pages

> The section currently has no content and no nav entry —— the 「项目」 / Projects menu item was removed along with the placeholder page. The front matter contract below is the format to follow when the section is filled.

Create a project page under `content/projects/`:

```markdown
---
title: "项目名"
date: 2026-08-13
description: "项目简介"
tech: ["Hugo", "TypeScript"]
github: "https://github.com/xxx/yyy"   # 可选
weight: 1
---
```

## Deployment

Pushing to `main` triggers the automatic deployment via Actions:

```bash
git push origin main
```

The workflow is `.github/workflows/hugo.yml` (`build` + `deploy`; the build output is uploaded via `actions/upload-pages-artifact`, and `actions/deploy-pages` drives the Pages service directly).

> Repository settings: Settings → Pages → Source must be **GitHub Actions** (not "Deploy from a branch"), otherwise the deploy job fails.

The repository has only two workflows: `hugo.yml` for deployment, and the read-only `theme-drift-check.yml` (every Monday it checks whether the PaperMod submodule has drifted the two templates this site overrides; if it has, it opens an issue to remind, and it never changes code on its own).

## Directory structure

```
.
├── content/                  ← all Markdown content
│   ├── quests/               ← Echoes archive (10 archived days, one page per language)
│   └── about/                ← about me
├── data/
│   └── spark_checkins.json   ← check-in photo metadata (frozen snapshot, 4 entries)
├── assets/                   ← processed by Hugo (images are resized and re-encoded)
│   ├── css/extended/blank.css ← the site's own styles
│   └── img/checkins/         ← local copies of the check-in photos (Hugo crops them)
├── static/                   ← static assets (copied verbatim to the site root)
│   ├── images/avatar.jpg     ← avatar
│   └── favicon.ico           ← browser tab icon
├── layouts/                  ← site-level template overrides of PaperMod
│   ├── index.html            ← home page (two columns: post list + "Echoes" sidebar pick)
│   ├── quests.html           ← Echoes list page
│   ├── quests/single.html    ← single archived day detail page
│   └── _partials/
│       ├── comments.html         ← Giscus comments (articles; General category)
│       ├── spark_comments.html   ← Giscus comments (archive pages; daily-spark category)
│       └── google_analytics.html ← GA4 gtag.js
├── config/_default/          ← Hugo configuration
├── themes/PaperMod/          ← theme (git submodule)
├── .github/workflows/        ← GitHub Actions (hugo.yml deploy + theme-drift-check.yml drift reminder)
└── docs/superpowers/         ← design and implementation documents (version controlled)
```

## Design references

- Check-in image wall design spec: `docs/superpowers/specs/2026-08-18-spark-checkins-design.md` —— **the feature was retired on 2026-10-20**, kept purely as a historical archive
- Check-in image wall implementation plan: `docs/superpowers/plans/2026-08-18-spark-checkins-implementation.md` —— same
