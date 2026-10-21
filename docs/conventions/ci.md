# CI / GitHub Actions Conventions

This repository uses GitHub Actions for deployment and read-only drift detection. This file distills the stable conventions for writing workflows. Learned from the 2026 homepage Daily Spark launch round (HEAD 6af78a1).

**Current shape (after the daily board's retirement on 2026-10-20)**: the repository has only **2 workflows** —

| workflow | Trigger | Purpose |
|----------|------|------|
| `.github/workflows/hugo.yml` | `push` to `main` + `workflow_dispatch` | build + deploy to GitHub Pages |
| `.github/workflows/theme-drift-check.yml` | `schedule` (every Monday 02:30 UTC) + `workflow_dispatch` | read-only detection of PaperMod submodule drift, opens/closes the reminder issue |

There is no bot workflow that writes data or pushes commits, and no generation workflow of any kind (the whole `scripts/` directory was deleted along with the daily board's retirement).

## 1. Cross-workflow triggering (historical convention + current shape)

- **Push events triggered by `GITHUB_TOKEN` do not trigger other workflows.** This is a GitHub platform security policy that prevents automation chains from recursing infinitely. **This platform rule still holds**, and any new workflow of the "write data → push to main → expect a deployment" kind has to keep it in mind.
- **Cross-workflow triggering must call `gh workflow run <target>.yml --ref <branch>` explicitly.** The historical shape (deleted along with the daily board's retirement):

  ```yaml
  - name: Trigger Hugo deploy
    if: steps.push.outputs.pushed == 'true'
    env:
      GH_TOKEN: ${{ github.token }}
    run: gh workflow run hugo.yml --ref main
  ```

- **The `permissions` of the source workflow must include `actions: write`.** The historical shape (deleted):

  ```yaml
  permissions:
    contents: write   # push commits
    actions: write    # explicitly trigger other workflows
  ```

  The default `GITHUB_TOKEN` is read-only, so both have to be declared explicitly.

- **The target workflow must declare `workflow_dispatch` in its `on:`.** `gh workflow run` triggers through dispatch, and the command fails without that line. This repository's `hugo.yml` already declares `push` + `workflow_dispatch`, so the requirement is met.
- Both same-event (deploy after a push) and cross-event (deploy after a cron) triggering use the same pattern; if the target also needs other triggers (e.g. `push: branches: [main]`), the two sources (a manual push vs. a workflow trigger) both take effect, and idempotency has to be guaranteed inside the workflow (the historical shape guarded against a repeated trigger with `if: steps.push.outputs.pushed == 'true'`).
- **Current shape**: this repo has **no workflow that pushes commits**, so the "cross-workflow triggering" scenario has disappeared — `hugo.yml` only runs when triggered manually (or when some future writer workflow dispatches it explicitly). The rules above are kept as **accumulated history**: if an auto-writing workflow is ever reintroduced, these lines are a ready-made template to copy.

## 2. Cron scheduling and disabling

- **There is only one scheduled workflow**: `theme-drift-check.yml` (`cron: '30 2 * * 1'`, every Monday 02:30 UTC). The daily board's `daily-spark.yml` (`cron: '10 16 * * *'`) and `spark-checkins.yml` (`cron: '17 * * * *'`) were deleted along with the board's retirement.
- **GitHub automatically disables scheduled workflows after 60 days of inactivity in the repository.** Everyday pushes heal it; long-term inactivity requires manually hitting Re-enable on the Actions page. This rule **still applies** to `theme-drift-check.yml`.
- **The trigger precondition has changed**: before the daily board's retirement this repo had two bot writer workflows committing every day as a safety net, so "long-term inactivity" was never an ops risk worth watching on its own in this repo's context. The bot pushes are gone and the safety net with them — **"the repo sits still for a long time → the schedule gets silently disabled" is a real ops item again**, and it takes nothing more than glancing at the Actions page every now and then.
- **If scheduled jobs are ever reintroduced** (generating content / scraping data), keep in mind at the same time: ① a scheduled workflow is subject to the same 60-day disabling rule; ② the commits it pushes go through `GITHUB_TOKEN` and therefore **do not** automatically trigger `hugo.yml` — an explicit `gh workflow run hugo.yml --ref main` is required (see §1); ③ `permissions` needs `contents: write` + `actions: write`; ④ prefer "write nothing when nothing changed" to avoid empty commits triggering a deployment storm.

## 3. The theme-drift-check workflow (theme drift detection)

Learned from the 2026-08-22 bulk optimization round (see Recent Changes in [[current-state.md]]).

- **Existence**: `.github/workflows/theme-drift-check.yml` is a **read-only + reminder-style** workflow — **it opens no PR, pushes no commit, and triggers no deployment**. It does exactly one thing: watch whether the upstream of the `themes/PaperMod` submodule has changed the two theme templates that this site overrides, so that "upgrading the submodule and forgetting to diff makes the override fail silently" cannot happen.
- **The two files it watches** (the site-level override list):
  - `layouts/_partials/header.html` — PaperMod top bar
  - `layouts/_partials/translation_list.html` — PaperMod language switcher list
- **Trigger**: every Monday 02:30 UTC (cron) + `workflow_dispatch` (manual). **Not a push trigger** — a push trigger would collide with the commits that upgrade the submodule, producing noise.
  - **The rationale for the schedule has changed**: the earlier schedule existed to avoid the time slots of the two writer workflows `daily-spark` (daily at 16:10 UTC) and `spark-checkins` (hourly at :17), so that data file writes would not collide with the build. Both workflows were deleted along with the daily board's retirement, and **the only remaining reason for the schedule is to match PaperMod's release rhythm**.
- **Flow**: checkout including submodules → `git fetch` the upstream inside `themes/PaperMod` → diff the pinned SHA against `origin/HEAD` for those two overrides → if there is drift, open an issue (the title carries a short hash, the body carries the site-level override list + the `diff` output truncated to 100 lines, and a random unique heredoc separator to prevent script injection); if there is no drift, automatically close the old reminder issue on the same topic.
- **The permissions boundary**:
  ```yaml
  permissions:
    contents: read    # checkout + diff
    issues: write     # open / close issues
  ```
  There is **no** `contents: write` (no PR / no commit push), **no** `actions: write` (no deployment trigger), and **no** `pull-requests: write`. This is a deliberate trade-off: the workflow only reminds, it never fixes, so that semi-automatic change PRs cannot sneak into the normal review rhythm.
- **Issue lifecycle design**: the upstream returns to the pinned SHA → no drift → the workflow automatically closes the old issue → silent green; the upstream keeps drifting → the issue stays open until somebody upgrades manually and reviews. **The failing-job pattern was abandoned** (failing red every time would need a mute mechanism); **the PR pattern was abandoned** (a single-author blog repo has no PR review process to hook into).
- **Not a replacement** for a full review when upgrading the submodule. The workflow only watches those two files; changes to other theme files are covered by the PR review process.

## 4. The boundary of the deployment workflow's responsibilities

- **`hugo.yml` now only does build + deploy**: checkout (`submodules: recursive` + `fetch-depth: 0`) → Setup Hugo (`0.164.0` extended) → `hugo --minify --gc --buildFuture` → `actions/upload-pages-artifact` uploads `./public` → `actions/deploy-pages` drives Pages.
- **The former spark date validation steps were deleted along with the daily board's retirement.** Those steps validated the dates / structure of the card of the day and of the history entries — the corresponding data files (`data/daily_spark.json` / `data/daily_spark_history.json`) no longer exist, so the validation lost the thing it was supposed to validate.
  - **One convention distilled from that**: before adding a validation step to `hugo.yml`, first confirm the data being validated **still exists**; otherwise you end up writing a validation that always passes, which looks like it is guarding something while guarding nothing at all.
- **Least privilege**: the `build` job is `contents: read` + `pages: write` + `id-token: write`; the `deploy` job only has `pages: write` + `id-token: write`. The deployment workflow does not hold `contents: write` — it has no business writing to the repository.
- **Concurrency**: the global concurrency group is `pages` with `cancel-in-progress: false` — when a new push arrives mid-deployment, it waits for the in-flight run to finish instead of starting a parallel deployment from a stale artifact.
- **Repository settings**: Settings → Pages → Source must be **GitHub Actions**, otherwise the deploy job fails (see the header comment in `hugo.yml`).
