# CI / GitHub Actions 约定

本仓库使用 GitHub Actions 做定时任务与部署。本文件沉淀工作流编写中的稳定约定。学自 2026 年首页 Daily Spark 上线轮（HEAD 6af78a1）。

## 1. 跨 workflow 触发

- **`GITHUB_TOKEN` 触发的 push 事件不会触发其他 workflow**。这是 GitHub 平台安全策略，防止自动化链无限递归。例如 daily-spark 推 `data/` 后只跑本 workflow，`hugo.yml` 不会被动联动部署。
- **跨 workflow 触发必须显式调用 `gh workflow run <target>.yml --ref <branch>`**。示例（摘自 `.github/workflows/daily-spark.yml`）：

  ```yaml
  - name: Trigger Hugo deploy
    if: steps.push.outputs.pushed == 'true'
    env:
      GH_TOKEN: ${{ github.token }}
    run: gh workflow run hugo.yml --ref main
  ```

- **源 workflow 的 `permissions` 必须包含 `actions: write`**。本仓库 daily-spark 同时需要推 commit（`contents: write`）与触发部署（`actions: write`）：

  ```yaml
  permissions:
    contents: write   # 推 commit
    actions: write    # 显式触发其他 workflow
  ```

  默认 `GITHUB_TOKEN` 是 read-only，两项必须显式声明。

- **目标 workflow 必须在 `on:` 中声明 `workflow_dispatch`**。`gh workflow run` 通过 dispatch 触发，没有这一行命令会失败。本仓库 `hugo.yml` 已声明 `push` + `workflow_dispatch`，满足要求。

- 同事件（push 后部署）或跨事件（cron 后部署）的触发都使用同一模式；若目标还需要其他触发（如 `push: branches: [main]`），两种来源（人工 push vs workflow 触发）会同时生效，幂等性需在工作流内部保证（daily-spark 用 `if: steps.push.outputs.pushed == 'true'` 守卫避免重复触发）。

## 2. Cron 排程与停用

- 当前 `.github/workflows/daily-spark.yml` 使用 `cron: '10 16 * * *'`（UTC 16:10 = 北京 00:10）。
- **GitHub 会在仓库 60 天无活动后自动停用 schedule workflow**。日常 push 自愈，长期闲置需在 Actions 页手动 Re-enable。

## 3. theme-drift-check workflow（主题漂移检测）

学自 2026-08-22 批量优化轮（见 [[current-state.md]] 最近变更）。

- **存在性**：`.github/workflows/theme-drift-check.yml` 是**只读 + 提醒型** workflow——**不开 PR、不推 commit、不触发布署**。它只做一件事：盯 `themes/PaperMod` 子模块上游是否改动到了本站点级覆盖的两处主题模板，避免"升级子模块时忘 diff 导致覆盖静默失效"。
- **盯的两个文件**（站点级覆盖列表）：
  - `layouts/_partials/header.html` — PaperMod 顶栏
  - `layouts/_partials/translation_list.html` — PaperMod 语言切换列表
- **触发**：每周一 02:30 UTC（cron）+ `workflow_dispatch`（手动）。**非 push 触发**——push 触发会和升级子模块的 commit 撞车，造成噪声。
- **流程**：checkout 含子模块 → 在 `themes/PaperMod` 内 `git fetch` 上游 → diff pinned SHA vs `origin/HEAD` 中这两处覆盖 → 有 drift 开 issue（标题带短 hash、body 含站点级覆盖清单 + 100 行截断的 `diff` 输出、随机唯一 heredoc 分隔符防脚本注入），无 drift 自动关闭旧的同主题提醒 issue。
- **permissions 边界**：
  ```yaml
  permissions:
    contents: read    # checkout + diff
    issues: write     # 开/关 issue
  ```
  **没有** `contents: write`（不开 PR / 不推 commit）、**没有** `actions: write`（不触发布署）、**没有** `pull-requests: write`。这是有意取舍：workflow 只提醒、不修复，避免半自动改动 PR 混进正常 review 节奏。
- **issue 生命周期设计**：上游回到 pinned SHA → 无 drift → workflow 自动 close 旧 issue → 静默绿；上游继续漂移 → issue 保持 open 直到人工升级并复核。**失败 job 模式被舍弃**（每次失败红一次需要 mute 机制）；**PR 模式被舍弃**（单人博客仓库无 PR review 流程对接）。
- **不替代**：升级子模块时的全面 review。Workflow 只盯这两处，theme 其它文件的改动由 PR review 流程兜底。
