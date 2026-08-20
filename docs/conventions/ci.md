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
