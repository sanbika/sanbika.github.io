# 个人博客与个人主页 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 `https://sanbika.github.io` 上部署一个 Hugo + PaperMod 的双语个人博客与个人主页，覆盖首页、文章、项目、关于四大版块，并接入 Giscus 评论、Fuse.js 搜索、暗色模式、Google Analytics、RSS。

**Architecture:** 单 Hugo 仓库 `sanbika/sanbika.github.io`，本地工作区 `C:/Dev/blog-site/`。Hugo extended 构建静态站点；GitHub Actions 在 push 到 `main` 时构建并把 `public/` 部署到 `gh-pages` 分支，由 GitHub Pages 服务。

**Tech Stack:** Hugo extended (0.142.0+), PaperMod theme (submodule), peaceiris/actions-hugo, peaceiris/actions-gh-pages, Giscus, Google Analytics 4, GitHub Pages.

**Spec:** `docs/superpowers/specs/2026-08-13-personal-blog-design.md`

---

## File Structure

被本计划创建或修改的文件及其职责：

```
C:/Dev/blog-site/
├── .gitignore                                     ← 排除 public/、resources/_gen/、docs/superpowers/
├── README.md                                      ← 项目说明（部署方式、写作方式）
├── hugo.toml                                      ← Hugo 模块声明（可选，用于指定 min version）
│
├── .github/workflows/hugo.yml                     ← GitHub Actions 部署工作流
│
├── config/
│   ├── _default/
│   │   ├── config.toml                            ← 主配置：baseURL、主题、默认语言、输出格式
│   │   ├── languages.toml                         ← 中英双语配置
│   │   ├── menus.toml                             ← 顶部主导航
│   │   └── params.toml                            ← 主题参数 + Giscus/GA4/socialIcons
│   └── production/
│       └── config.toml                            ← 生产环境覆盖（baseURL 等）
│
├── content/
│   ├── posts/
│   │   ├── hello-world.md                         ← 中文示范文章
│   │   └── hello-world.en.md                      ← 英文示范文章
│   ├── projects/
│   │   └── sample-project.md                      ← 示范项目
│   └── about/
│       ├── index.md                               ← 中文关于页
│       └── index.en.md                            ← 英文关于页
│
├── static/
│   ├── images/
│   │   └── avatar.png                             ← 头像占位（后替换）
│   └── favicon.ico                                ← favicon
│
└── themes/PaperMod/                               ← 主题作为 git submodule
```

**职责划分**：
- `config/_default/` 放跨环境通用配置
- `config/production/` 放仅生产环境生效的覆盖项
- `content/` 全部内容由用户维护、纯 Markdown
- `static/` 直接复制到站点根目录、不走 Hugo 解析
- `themes/PaperMod/` 不直接修改——定制通过 PaperMod 的 `assets/css/extended/` 局部覆盖

---

## 工作约定

1. **每个任务结束都要 commit**（除有特殊说明的合并 commit）
2. **TDD 不强求**：本计划为基础设施搭建 + 静态内容；不存在单元测试层。改用"验证步骤"：构建、URL 访问、视觉走查
3. **每次失败的报错**保留日志，作为后续诊断材料
4. **HEAD 始终保持可用**：每个 commit 后 `hugo server` 仍可起，部署不会回退

---

## Phase 0 — 仓库初始化与远程连接

### Task 1: 本地克隆远程仓库

**Files:**
- Create: `C:/Dev/blog-site/` 目录下的所有初始文件

- [ ] **Step 1: 克隆远程仓库**

```bash
cd C:/Dev
git clone https://github.com/sanbika/sanbika.github.io.git blog-site
```

Expected: 命令成功完成，目录内出现 `README.md`（来自远端初始内容）

- [ ] **Step 2: 进入仓库、查看状态**

```bash
cd C:/Dev/blog-site
git log --oneline | head -3
git remote -v
```

Expected: 至少 1 个 commit（远端的初始 README），remote 显示 `origin` 指向 `sanbika/sanbika.github.io`

- [ ] **Step 3: 清理远端的初始文件（如果存在非 README 内容）**

如果远端除 `README.md` 外还有 `index.html` / `_config.yml` 等属于 Jekyll/Pages 初始模板的文件，应该删掉。检查：

```bash
ls -la
```

如果没有非 README 文件则跳过本步。

- [ ] **Step 4: 增加 `.gitignore` 排除构建产物与开发文档**

```bash
cat > .gitignore <<'EOF'
public/
resources/_gen/
.hugo_build.lock
.DS_Store

# 开发与设计文档不进入 commit
docs/superpowers/
EOF
```

Verify:
```bash
cat .gitignore
```

Expected: 看到上述 4 大类规则。

- [ ] **Step 5: 提交清理后的状态**

如果之前删过文件：

```bash
git add -A
git status
git commit -m "chore: 清理 Jekyll 初始化模板并加入 .gitignore"
```

Expected: commit 成功，工作区干净。

如果远端只有 README、没动任何文件，跳过本步的 commit。

---

### Task 2: 在 GitHub 上禁用默认 Jekyll 构建（关键）

**Files:**
- Modify: GitHub 仓库网站设置（不是本地文件）

GitHub Pages 默认按 Jekyll 处理，会尝试解析 Hugo 站点。Hugo 博客必须在仓库根放一个 `.nojekyll` 文件让 GitHub 跳过 Jekyll。

- [ ] **Step 1: 创建空 `.nojekyll` 文件**

```bash
cd C:/Dev/blog-site
touch .nojekyll
```

- [ ] **Step 2: 验证文件存在**

```bash
ls -la .nojekyll
```

Expected: 文件存在，0 字节。

- [ ] **Step 3: 提交并推送**

```bash
git add .nojekyll
git commit -m "chore: 添加 .nojekyll 禁用 Pages 的 Jekyll 处理"
git push origin main
```

Expected: push 成功。

---

## Phase 1 — 本地骨架（验证 Hugo + PaperMod 可运行）

### Task 3: 安装 Hugo Extended（本地工具链）

**Files:** — (本任务不动项目文件，只装本地工具)

Hugo 0.142.0+ Extended 是必需的（PaperMod 的某些特性用了 SCSS）。

- [ ] **Step 1: 检查是否已安装 Hugo**

```bash
hugo version
```

- **如果已安装且版本 ≥ 0.112 且带 extended**：跳到下一步
- **如果未安装或不是 extended**：先安装。下面给出 Windows 与 macOS/Linux 的两种方法

Windows（Chocolatey）：
```bash
choco install hugo-extended -y
```

macOS（Homebrew）：
```bash
brew install hugo
```

Linux（snap）：
```bash
sudo snap install hugo --channel=extended
```

安装完后再跑 `hugo version`，确认 `extended` 字样。

- [ ] **Step 2: 验证版本与扩展**

```bash
hugo version
```

Expected 输出形如：`hugo v0.142.0+extended ...`。

---

### Task 4: 初始化 Hugo 站点结构（不替换已有 README）

**Files:**
- Create: `config/_default/config.toml`、`content/.*`、`static/.*`、`archetypes/default.md`、`hugo.toml`

执行 `hugo init` 会保留已存在的 `README.md`（不会覆盖）但要小心处理 — 实际上 `hugo init` 不带 `--force` 不会覆盖已有同名文件。

- [ ] **Step 1: 运行 hugo init**

```bash
cd C:/Dev/blog-site
hugo init .
```

如果命令提示要覆盖文件，确认 README.md 不被覆盖（一般 Hugo init 不会创建 README.md）。

Verify:
```bash
ls -la
```

Expected: 看到 `config.toml`、`content/`、`static/`、`archetypes/`、`themes/`、`hugo.toml` 目录/文件加进来，且原有的 `README.md` 仍在。

- [ ] **Step 2: 删除 hugo init 默认 themes 目录**

hugo init 会建一个空 `themes/` 目录占位，我们用 submodule 方式添 PaperMod，留空目录会冲突。

```bash
rm -rf themes/
```

- [ ] **Step 3: 删除自带的默认 config.toml**

hugo init 创建的 `config.toml` 是单文件结构，我们要改成 `config/_default/` 目录结构。删除顶层 `config.toml`：

```bash
rm -f config.toml
```

- [ ] **Step 4: 提交骨架**

```bash
git add -A
git status
git commit -m "feat: hugo init 骨架结构（不含主题）"
```

Expected: 看到新增 `content/`、`static/`、`archetypes/`、`hugo.toml` 等。

---

### Task 5: 引入 PaperMod（git submodule）

**Files:**
- Create: `.gitmodules`、`themes/PaperMod/`

- [ ] **Step 1: 添加 PaperMod 作为 submodule**

```bash
cd C:/Dev/blog-site
git submodule add --depth=1 https://github.com/adityatelange/hugo-PaperMod.git themes/PaperMod
```

Expected: 主题被克隆到 `themes/PaperMod/`；根出现 `.gitmodules` 文件。

- [ ] **Step 2: 初始化 submodule（如果克隆时空）**

```bash
cd themes/PaperMod
git submodule update --init --recursive
cd ../..
```

- [ ] **Step 3: 验证主题文件齐备**

```bash
ls themes/PaperMod/
```

Expected: 看到 `layouts/`、`assets/`、`static/`、`theme.toml` 等。

- [ ] **Step 4: 提交 submodule 引用**

```bash
git add .gitmodules themes/PaperMod
git commit -m "feat: 引入 PaperMod 主题作为 submodule"
```

Expected: commit 包含两个文件；`themes/PaperMod` 里大部分内容不在 git 历史（submodule 引用是 commit hash 而不是文件本身）。

---

### Task 6: 冒烟测试 — 本地起 Hugo server

**Files:** — (无文件改动)

- [ ] **Step 1: 临时配置主题 + baseURL 启动 server**

新建 `C:/Dev/blog-site/config/_default/config.toml`，先用最小内容让 server 能跑（Task 7 会替换为完整配置）：

```toml
baseURL = "http://localhost:1313/"
title = "sanbika 的小站"
theme = "PaperMod"

enableRobotsTXT = true

[params]
  env = "auto"
  description = "sanbika 的个人主页与博客"
  author = "sanbika"
  enableSearch = true
```

```bash
mkdir -p config/_default
```

写入 `config/_default/config.toml`（用 Write 工具），文件内容如上。

- [ ] **Step 2: 启动 hugo server**

```bash
cd C:/Dev/blog-site
hugo server -D
```

Expected: 输出 `Web Server is available at http://localhost:1313/`，且没有红色错误。

- [ ] **Step 3: 浏览器访问验证**

浏览器打开 `http://localhost:1313/`，看到 PaperMod 默认首页（无内容但有骨架与菜单区）。

- [ ] **Step 4: 停掉 server**

Ctrl+C 退出。临时配置保留，下个 task 会扩充。

---

## Phase 2 — 配置定稿（双语、菜单、主题参数）

### Task 7: 写入完整的 `config/_default/config.toml`

**Files:**
- Modify: `config/_default/config.toml`

> **关于 baseURL**：Task 6 临时配置里的 `baseURL = "http://localhost:1313/"` 仅用于本地 smoke test；本任务覆盖为生产值 `https://sanbika.github.io/`。本任务开始的所有开发都基于新 baseURL，后续不需要再改。

- [ ] **Step 1: 写入主配置**

用 Write 工具覆盖 `config/_default/config.toml`：

```toml
baseURL = "https://sanbika.github.io/"
title = "sanbika 的小站"
theme = "PaperMod"

defaultContentLanguage = "zh-cn"
defaultContentLanguageInSubdir = false

enableRobotsTXT = true

[outputs]
  home = ["HTML", "RSS"]
  section = ["HTML", "RSS"]

[params]
  env = "auto"
  description = "sanbika 的个人主页与博客"
  author = "sanbika"
  avatar = "images/avatar.png"
  enableSearch = true
  DateFormat = "2006-01-02"
  ShowReadingTime = true
  ShowShareButtons = false

[[params.socialIcons]]
  name = "github"
  url = "https://github.com/sanbika"

[[params.socialIcons]]
  name = "rss"
  url = "/index.xml"
```

- [ ] **Step 2: 验证语法**

```bash
cd C:/Dev/blog-site
hugo config | head -20
```

Expected: 无报错，打印配置。

---

### Task 8: 写入 `config/_default/languages.toml`

**Files:**
- Create: `config/_default/languages.toml`

- [ ] **Step 1: 写入双语配置**

```toml
[zh-cn]
  languageName = "中文"
  weight = 1
  title = "sanbika 的小站"
  [zh-cn.params]
    description = "sanbika 的个人主页与博客（中文）"

[en]
  languageName = "English"
  weight = 2
  title = "sanbika's Site"
  [en.params]
    description = "sanbika's personal site and blog"
```

- [ ] **Step 2: 验证 hugo 能解析**

```bash
hugo --printPathWarnings
```

Expected: 无 fatal 错误。

---

### Task 9: 写入 `config/_default/menus.toml`

**Files:**
- Create: `config/_default/menus.toml`

**设计决策**：PaperMod 在不同语言下共享同一份 `menus.toml` 的常见做法。所有条目共用 `[[main]]` 一组，跨语言也可点击（用户点击 `/posts/` 默认进中文版，后续如需严格分语言再拆 `zh-cn.toml` + `en.toml`）。

- [ ] **Step 1: 写入菜单**

```toml
[[main]]
  identifier = "posts"
  name = "文章"
  url = "/posts/"
  weight = 10

[[main]]
  identifier = "projects"
  name = "项目"
  url = "/projects/"
  weight = 20

[[main]]
  identifier = "about"
  name = "关于"
  url = "/about/"
  weight = 30

[[main]]
  identifier = "rss"
  name = "RSS"
  url = "/index.xml"
  weight = 40
```

- [ ] **Step 2: 启动 server 验证菜单**

```bash
hugo server -D
```

浏览器访问 `http://localhost:1313/`，顶部菜单出现"文章 / 项目 / 关于 / RSS"四项。

---

### Task 10: 写入 `config/_default/params.toml`（主题参数 + 评论占位 + GA 占位）

**Files:**
- Create: `config/_default/params.toml`

- [ ] **Step 1: 写入主题参数**

```toml
[params]
  env = "auto"
  defaultTheme = "auto"
  ShowReadingTime = true
  ShowShareButtons = false
  ShowPostNavLinks = true
  ShowBreadCrumbs = true
  enableSearch = true
  searchLimit = 10

# 评论（Giscus）
[params.comments]
  enabled = true
  provider = "giscus"
  [params.comments.giscus]
    repo = "sanbika/sanbika.github.io"
    repoId = "PLACEHOLDER_REPO_ID"
    category = "General"
    categoryId = "PLACEHOLDER_CATEGORY_ID"
    mapping = "pathname"
    lightTheme = "light"
    darkTheme = "dark_dimmed"
    reactionsEnabled = true

# Google Analytics（占位）
[params.analytics.google]
  id = "G-PLACEHOLDER"
```

**注**：Giscus 的 `repoId` / `categoryId` 与 GA 的 `id` 暂时是占位，下个 phase 替换。

- [ ] **Step 2: 验证**

```bash
hugo server -D
```

浏览器访问 `http://localhost:1313/`，看到暗色模式开关、搜索按钮存在；评论区因占位 ID 不显示（这是预期的）。

- [ ] **Step 3: 提交配置**

```bash
git add config/
git commit -m "feat: 完善 config：双语、菜单、主题参数（含评论/GA 占位）"
```

---

### Task 11: 提供头像与 favicon 占位

**Files:**
- Create: `static/images/avatar.png`、`static/favicon.ico`

- [ ] **Step 1: 创建静态资源目录**

```bash
mkdir -p static/images
```

- [ ] **Step 2: 放入临时头像**

可以从网上随便找一张 256×256 的 png 作为占位（比如 GitHub Avatar 默认），用 Write 工具或 Bash 下载到 `static/images/avatar.png`。最简单：

```bash
curl -L -o static/images/avatar.png "https://www.gravatar.com/avatar/?d=identicon&s=256"
```

如果不可用，跳到 Step 3 用 1x1 像素 PNG 占位。

- [ ] **Step 3:（备选）写入 1x1 PNG 占位**

如果无法下载外部头像，写一个 Base64 解码的 1×1 灰度 PNG：

```bash
python -c "import base64; open('static/images/avatar.png','wb').write(base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkAAIAAAoAAv/lxKUAAAAASUVORK5CYII='))"
```

- [ ] **Step 4: 创建 favicon.ico 占位**

浏览器请求 `/favicon.ico`，404 不影响功能但 console 会有警告。先放个空文件（**注**：0 字节文件浏览器可能报 parse 错误而非 404，console 会出现不同警告，但都不影响站点功能）：

```bash
touch static/favicon.ico
```

后续 Phase 6 再换正式图标。

- [ ] **Step 5: 提交资源**

```bash
git add static/
git commit -m "chore: 加入头像与 favicon 占位"
```

---

## Phase 3 — 部署流水线（GitHub Actions）

### Task 12: 写入 GitHub Actions workflow

**Files:**
- Create: `.github/workflows/hugo.yml`

- [ ] **Step 1: 创建目录与文件**

```bash
mkdir -p .github/workflows
```

写入 `.github/workflows/hugo.yml`：

```yaml
name: Deploy Hugo site

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  build-deploy:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4
        with:
          submodules: recursive
          fetch-depth: 0

      - name: Setup Hugo
        uses: peaceiris/actions-hugo@v3
        with:
          hugo-version: '0.142.0'
          extended: true

      - name: Build
        run: hugo --minify --gc --buildFuture

      - name: Deploy
        uses: peaceiris/actions-gh-pages@v4
        with:
          publish_branch: gh-pages
          cname: ''
          keep_history: true
          enable_force_orphan: true
```

- [ ] **Step 2: 语法检查**

可用 `yamllint`（如有）检查；没有就靠 push 后 Actions 日志诊断。

```bash
yamllint .github/workflows/hugo.yml 2>/dev/null || echo "yamllint not installed, skipping"
```

- [ ] **Step 3: 提交 workflow**

```bash
git add .github/
git commit -m "feat: 添加 GitHub Actions 自动部署 workflow"
```

---

### Task 13: 写入生产环境配置覆盖

**Files:**
- Create: `config/production/config.toml`

- [ ] **Step 1: 创建文件**

```toml
[params]
  # 生产环境如有调整，加在这里
```

（目前生产环境不需要额外覆盖；如果以后要 defer analytics 或加 CDN 配置，在这里加。）

- [ ] **Step 2: 提交**

```bash
git add config/production/
git commit -m "chore: 加入生产环境配置目录骨架"
```

---

### Task 14: 推送到 main 触发第一次部署

**Files:**
- Modify: 远端 main 分支

- [ ] **Step 1: 推送**

```bash
cd C:/Dev/blog-site
git push origin main
```

Expected: push 成功，远端 HEAD 更新。

- [ ] **Step 2: 查看 Actions 运行**

浏览器打开 `https://github.com/sanbika/sanbika.github.io/actions`

Expected: 看到刚推送触发的 workflow，名称为 "Deploy Hugo site"。

- [ ] **Step 3: 等待 workflow 完成（1-3 分钟）**

刷新 Actions 页面，直到出现 ✅ 绿色对勾。

- [ ] **Step 4: 验证 Pages 设置正确**

进入仓库 → Settings → Pages：
- Source 应选 "Deploy from a branch"
- Branch 应为 `gh-pages` / `(root)`

如果是 `main` / `root` 或没有自动跳转，需要手动改。

- [ ] **Step 5: 浏览器访问 `https://sanbika.github.io`**

Expected:
- 看到 PaperMod 首页骨架
- URL 仍然是 `https://sanbika.github.io/`
- 没有 404

- [ ] **Step 6: 检查浏览器 console**

打开 DevTools → Console。Expected: 无红色 error；如果有 favicon 404，可忽略（Phase 6 处理）。

---

### Task 15: 处理 workflow 失败常见原因（如有）

**Files:** —

如果 Phase 3 第一步 Actions 失败，按以下诊断表处理：

- [ ] **Step 1: 查阅报错信息**

在 Actions 页面点击失败的 run，展开报错步骤，记下错误信息。

- [ ] **Step 2: 对照下表**

| 报错关键词 | 原因 | 修复 |
|---|---|---|
| `failed to fetch submodule` | submodule 拉取失败 | workflow 改用 `submodules: recursive`；或本地重跑 `git submodule update --init` |
| `hugo: command not found` | action 未生效 | 升级 `peaceiris/actions-hugo` 版本 |
| `theme not found: PaperMod` | submodule 路径不对 | 检查 `.gitmodules` 与 `themes/PaperMod/` |
| `yaml: line X` | 配置文件 TOML 语法错 | 对照 §7 的示例逐字段检查 |
| `defaultContentLanguage` warning | i18n 问题 | 检查 `languages.toml` 第一项 `[zh-cn]` 与 `defaultContentLanguage` 一致 |

- [ ] **Step 3: 修复后重新推送**

```bash
git add -A
git commit -m "fix: 修复 Actions 部署问题（描述）"
git push origin main
```

- [ ] **Step 4: 直到 Actions 转绿**

重复 Step 1-3，每次只修一个问题。

> ⚠️ **重要约定**：连续 3 次以上 push 仍未转绿，或部署后站点持续 404 / 出现样式崩溃，**停止自行尝试**，回到用户处一起排查基础设施状态（DNS、Pages 配置、token 权限等）。

---

## Phase 4 — 内容填充

### Task 16: 写中文关于页

**Files:**
- Create: `content/about/index.md`

- [ ] **Step 1: 创建目录与文件**

写入 `content/about/index.md`：

```markdown
---
title: "关于我"
date: 2026-08-13T10:00:00+08:00
lang: "zh"
draft: false
---

# 你好，我是 sanbika

这里写一段自我介绍。Markdown 全部支持：列表、引用、代码块、表格。

## 工作与兴趣

- 关注的技术方向
- 当前在做什么
- 业余项目

## 联系方式

- GitHub: [@sanbika](https://github.com/sanbika)
- Email: <你的邮箱>

![Avatar](/images/avatar.png)
```

- [ ] **Step 2: 验证渲染**

```bash
hugo server -D
```

访问 `http://localhost:1313/about/`，看到关于页正确渲染（不是 404）。

---

### Task 17: 写英文关于页

**Files:**
- Create: `content/about/index.en.md`

- [ ] **Step 1: 写入**

```markdown
---
title: "About"
date: 2026-08-13T10:00:00+08:00
lang: "en"
draft: false
---

# Hi, I'm sanbika

Brief self-introduction here.

## Work & Interests

- Tech directions I focus on
- Currently working on
- Side projects

## Contact

- GitHub: [@sanbika](https://github.com/sanbika)
- Email: <your email>

![Avatar](/images/avatar.png)
```

- [ ] **Step 2: 验证**

访问 `http://localhost:1313/en/about/`，能看到英文关于页。

---

### Task 18: 写中文示范文章

**Files:**
- Create: `content/posts/hello-world.md`

- [ ] **Step 1: 写入**

```markdown
---
title: "你好，世界"
date: 2026-08-13T10:00:00+08:00
draft: false
tags: ["Hugo", "博客"]
categories: ["技术笔记"]
description: "本站的第一篇文章，介绍搭建过程。"
weight: 1
---

这是 `sanbika 的小站` 的第一篇文章。

## 主要内容

- Markdown 基础语法
- Hugo front matter 字段说明
- 自动部署流程

```bash
echo "Hello, Hugo!"
```

> 这是一段引用，用于测试排版。
```

- [ ] **Step 2: 验证**

`hugo server`，访问 `http://localhost:1313/posts/`，列表页看到这篇文章标题。

---

### Task 19: 写英文示范文章

**Files:**
- Create: `content/posts/hello-world.en.md`

- [ ] **Step 1: 写入**

```markdown
---
title: "Hello, World"
date: 2026-08-13T10:00:00+08:00
lang: "en"
draft: false
tags: ["Hugo", "Blog"]
categories: ["Tech Notes"]
description: "First post on this site, explaining the setup."
weight: 1
---

This is the first post on `sanbika's site`.

## Sections

- Markdown basics
- Hugo front matter fields
- Auto deployment

```bash
echo "Hello, Hugo!"
```

> A blockquote to test formatting.
```

- [ ] **Step 2: 验证**

访问 `http://localhost:1313/en/posts/`。

---

### Task 20: 写示范项目页

**Files:**
- Create: `content/projects/sample-project.md`

- [ ] **Step 1: 写入**

```markdown
---
title: "示范项目"
date: 2026-08-13T10:00:00+08:00
draft: false
description: "这是一个示范项目页面，演示 front matter 字段。"
tech: ["Hugo", "TypeScript", "Python"]
github: "https://github.com/sanbika/sanbika.github.io"
weight: 1
---

# 示范项目

这里写项目详细介绍。

## 项目目标

- 目标 1
- 目标 2

## 技术栈

| 类型 | 技术 |
|---|---|
| 静态生成 | Hugo |
| 部署 | GitHub Actions |
| 主题 | PaperMod |

## 后续计划

列出 TODO。
```

- [ ] **Step 2: 验证**

访问 `http://localhost:1313/projects/`。

---

### Task 21: 提交内容 + 触发部署

**Files:**
- Modify: 远端 main 分支

- [ ] **Step 1: 检查所有 markdown**

```bash
cd C:/Dev/blog-site
ls content/posts content/projects content/about
```

Expected: 看到 4 个 .md 与 1 个 .en.md（about）。

- [ ] **Step 2: 提交**

```bash
git add content/
git commit -m "feat: 加入初始内容（关于页 + 示范文章 + 示范项目）"
git push origin main
```

- [ ] **Step 3: 等待 Actions 部署**

等 Actions 转绿。

- [ ] **Step 4: 验证线上站点**

`https://sanbika.github.io` 出现以下内容：
- 首页看到示范文章摘要
- 顶部菜单可点进 `/posts/`、`/projects/`、`/about/`
- 标签页 `https://sanbika.github.io/tags/hugo/` 出现示范文章的标签
- 英文版 `https://sanbika.github.io/en/` 也能访问（虽然风格不完全一致；这是 MVP 范围）

---

## Phase 5 — 功能启用

### Task 22: 获取 Giscus 配置（repoId / categoryId）

**Files:** —

- [ ] **Step 1: 访问 giscus 配置页**

打开 `https://giscus.app/zh-CN`

- [ ] **Step 2: 填写**

- 仓库：`sanbika/sanbika.github.io`
- 页面 ↔ discussion 映射：`pathname`
- Discussion 分类：`General`
- 启用反应：勾选
- 主题：`light` / `dark_dimmed`

- [ ] **Step 3: 复制生成的 script**

向下滚动，giscus 会展示完整的 `<script>` 标签。从中提取：
- `data-repo-id`
- `data-category-id`

样例：
```
data-repo-id="R_kgDOK..."
data-category-id="DIC_kwDO..."
```

- [ ] **Step 4: 改 config 文件**

修改 `config/_default/params.toml`，把 `PLACEHOLDER_REPO_ID` 与 `PLACEHOLDER_CATEGORY_ID` 替换为真实值。

- [ ] **Step 5: 提交**

```bash
git add config/
git commit -m "feat: 填入 Giscus 真实 repoId 与 categoryId"
git push origin main
```

---

### Task 23: 验证评论组件

**Files:** —

- [ ] **Step 1: 访问线上文章**

打开 `https://sanbika.github.io/posts/hello-world/`，滚到底部。

- [ ] **Step 2: 看到 Giscus 组件**

Expected:
- 看到 "评论 powered by Giscus" 字样
- 可点击 "登录评论" 按钮登录 GitHub

- [ ] **Step 3:（可选）发送测试评论**

登录后写一句评论，确认 Discussions 已创建。

---

### Task 24: 验证搜索

- [ ] **Step 1: 浏览器打开站内搜索图标**

点击首页或文章页右上角的搜索图标（放大镜）。

- [ ] **Step 2: 输入关键词**

输入 `Hugo` 或 `示范`。

Expected: 下拉列表中至少出现一篇相关文章。

---

### Task 25: 验证暗色模式

- [ ] **Step 1: 切换主题**

点击顶部的太阳/月亮图标。

Expected: 整体配色从浅转深（或反之）。

- [ ] **Step 2: 刷新验证持久化**

F5 刷新页面，主题保持上次选择。

---

### Task 26: 接入 Google Analytics 4

**Files:**
- Modify: `config/_default/params.toml`

- [ ] **Step 1: 注册 GA4**

1. 打开 `https://analytics.google.com/`
2. 新建账号 → 新建媒体资源（选 "Web"）
3. 数据流：网站 → URL 填 `https://sanbika.github.io/`
4. 拿到 Measurement ID，形如 `G-XXXXXXXXXX`

- [ ] **Step 2: 修改配置**

```toml
[params.analytics.google]
  id = "G-XXXXXXXXXX"
```

- [ ] **Step 3: 提交与推送**

```bash
git add config/
git commit -m "feat: 启用 Google Analytics 4"
git push origin main
```

- [ ] **Step 4: 等待部署，访问首页**

打开首页（最好开多个页面 / 多次刷新），等 30 秒～2 分钟，然后在 GA 后台 `Reports → Realtime` 看是否有 1 个活跃用户。

---

### Task 27: 验证 RSS

- [ ] **Step 1: 浏览器访问 feed**

打开 `https://sanbika.github.io/index.xml`。

Expected: 看到 XML，包含至少一篇 `<item>` 节点。

- [ ] **Step 2:（可选）订阅测试**

用任意 RSS 阅读器订阅该 URL，确认能拉到全文。

---

## Phase 6 — 打磨

### Task 28: 替换头像

**Files:**
- Modify: `static/images/avatar.png`

- [ ] **Step 1: 准备图像**

- 尺寸 256×256 或更大（正方形）
- 格式 PNG 或 JPG
- 大小控制在 200KB 以内

- [ ] **Step 2: 替换文件**

```bash
cp /path/to/your/photo.png C:/Dev/blog-site/static/images/avatar.png
```

或拖拽替换。

- [ ] **Step 3: 验证**

`hugo server`，刷新首页与 about 页，看到新头像。

---

### Task 29: 自定义 favicon

**Files:**
- Modify: `static/favicon.ico`

- [ ] **Step 1: 生成 ico**

可用 [realfavicongenerator.net](https://realfavicongenerator.net/) 准备一套。把生成的 `favicon.ico` 复制到 `static/favicon.ico`。

- [ ] **Step 2: 验证**

浏览器访问 `https://sanbika.github.io/favicon.ico` 直接看到图标；标签栏小图标更新。

---

### Task 30: 自定义首页 hero 区（可选）

**Files:**
- Modify: `themes/PaperMod/layouts/index.html` 或新建 `layouts/index.html`

**重要警告**：不直接修改 themes/PaperMod 内部文件（升级会丢失）。而是用 Hugo 的 layouts 覆盖机制：在根 `layouts/index.html` 创建同名文件即可覆盖。

- [ ] **Step 1: 创建 layouts 目录**

```bash
mkdir -p layouts
```

- [ ] **Step 2: 创建 `layouts/index.html`（覆盖 PaperMod 默认）**

> ⚠️ **维护风险**：以下示例使用了 PaperMod 内部 CSS 类名（`home-info`、`avatar-section`、`home-section`）。PaperMod 升级时这些类名可能变更。若升级后样式异常，应回到上游 PaperMod 模板对照，或直接删除本文件改回 PaperMod 默认布局。

```html
{{- define "main" }}
<div class="first-entry home-info">
  <div class="avatar-section">
    <img src="{{ .Site.Params.avatar | absURL }}" alt="Avatar">
  </div>
  <h1>{{ .Site.Title }}</h1>
  <p>{{ .Site.Params.description }}</p>
</div>

<section class="home-section">
  {{ $pages := where site.RegularPages "Section" "in" (slice "posts" "projects") }}
  {{ range first 6 (where $pages ".Lang" .Language) }}
    {{ .Render "summary" }}
  {{ end }}
</section>
{{- end }}
```

这是 PaperMod 默认 hero 的简化版，仅在 title 与 description 上做了强调。要更大幅度的定制可参考 PaperMod 文档。

- [ ] **Step 3: 验证**

`hugo server`，看首页布局是否更突出个人简介。

- [ ] **Step 4: 提交**

```bash
git add layouts/
git commit -m "feat: 自定义首页 hero 区样式（覆盖 PaperMod 默认）"
```

---

### Task 31: 全站视觉走查

**Files:** —

- [ ] **Step 1: 创建走查清单**

进入 `https://sanbika.github.io`，与用户一起走查以下项：

| 检查项 | 期望 | 实际 |
|---|---|---|
| 首页头像显示 | 是 | — |
| 暗色按钮存在 | 是 | — |
| 菜单齐全（4 项） | 是 | — |
| 文章详情页 Giscus 显示 | 是 | — |
| 标签页访问 | 200 | — |
| 归档页访问 | 200 | — |
| 项目页访问 | 200 | — |
| 英文版可访问 | 是 | — |
| RSS feed 可访问 | 是 | — |
| Lighthouse 性能 | ≥ 90 | — |

- [ ] **Step 2: 修复发现的问题**

如有失败项，跳回相关 Task 修复。

---

### Task 32: 更新 README 与最终提交

**Files:**
- Modify: `README.md`

- [ ] **Step 1: 写新 README**

```markdown
# sanbika 的小站

个人博客与个人主页。基于 [Hugo](https://gohugo.io/) + [PaperMod](https://github.com/adityatelange/hugo-PaperMod) 主题。

## 本地开发

```bash
hugo server -D
```

默认访问 `http://localhost:1313/`。

## 写作

在 `content/posts/` 下创建新 Markdown：
```markdown
---
title: "标题"
date: 2026-08-13T10:00:00+08:00
tags: ["标签"]
draft: false
---
正文……
```

英文版同步：在同目录创建 `*.en.md`，加 `lang: "en"`。

## 部署

推送到 main 即触发 Actions 自动部署到 GitHub Pages：
```bash
git push origin main
```

详细部署结构见 `docs/superpowers/specs/2026-08-13-personal-blog-design.md`。
```

- [ ] **Step 2: 提交**

```bash
git add README.md
git commit -m "docs: 编写项目 README"
git push origin main
```

---

## 完成标准验收

全部 task 完成后，对照 spec 第 8 节验收：

| 检查 | 标准 | 验证方式 |
|---|---|---|
| 站点可访问 | `https://sanbika.github.io` 200 | 浏览器 |
| 双语切换 | `/` 与 `/en/` 内容不同 | 浏览器 |
| 菜单对位 | 文章/项目/关于/RSS 全部可点 | 浏览器 |
| 评论 | Giscus 渲染 | 打开文章详情页 |
| 搜索 | 输入关键词能命中 | 搜索框 |
| 暗色 | 切换按钮正常 | 顶部按钮 |
| GA4 | 实时报告有访问 | GA 后台 |
| RSS | `/index.xml` 是有效 feed | 浏览器 |
| Lighthouse 移动端性能 | ≥ 90 | Chrome DevTools |

全部通过后，本计划完成。

---

## 参考材料

- spec：`docs/superpowers/specs/2026-08-13-personal-blog-design.md`
- Hugo 文档：https://gohugo.io/documentation/
- PaperMod Wiki：https://github.com/adityatelange/hugo-PaperMod/wiki
- Giscus 配置：https://giscus.app/zh-CN
- peaceiris/actions-hugo：https://github.com/peaceiris/actions-hugo
- peaceiris/actions-gh-pages：https://github.com/peaceiris/actions-gh-pages
