# 个人博客与个人主页设计 spec

**作者**：sanbika
**日期**：2026-08-13
**仓库**：`sanbika/sanbika.github.io`
**本地路径**：`C:/Dev/blog-site/`
**状态**：Draft（待用户最终审批）

---

## 1. 目标与背景

### 1.1 目标

在 GitHub Pages 上搭建一个完整的个人博客与个人主页站点，承担以下职能：

- 个人品牌门户（头像 + 简介 + 联系方式）
- 长文 / 笔记的发布（Markdown）
- 项目与作品展示
- 双语支持（中文为主，少量英文）

### 1.2 非目标

- 不是社交 / 论坛（无用户登录、无私信）
- 不是 CMS（无数据库，所有内容源于 Git 仓库）
- 一期不接入自定义域名（先 `username.github.io`）
- 一期不做 SEO 深度优化（不接 Google Search Console、sitemap.xml 配置简化）

### 1.3 成功标准

- 推送到 `main` → 在 `https://sanbika.github.io` 上能看到站点且无 404
- 中英文切换路径正确，菜单 / 标签 / 归档对应无误
- 评论、搜索、暗色模式、Google Analytics 四项功能正常工作
- Lighthouse 移动端性能 ≥ 90

---

## 2. 技术选型

| 维度 | 选择 | 理由 |
|---|---|---|
| 静态站点生成器 | Hugo（extended 版） | 速度极快、模板生态丰富、双语原生 |
| 主题 | **PaperMod** | Hugo 生态最受欢迎主题，原生支持双语 / 搜索 / 暗色 / GA / RSS |
| 部署 | GitHub Actions + `peaceiris/actions-gh-pages@v4` | 自动构建、产物推到 `gh-pages` 分支 |
| 评论 | **Giscus**（基于 GitHub Discussions） | 零成本、无追踪、支持暗色 |
| 搜索 | PaperMod 内置 Fuse.js | 客户端索引，无后端 |
| 暗色模式 | PaperMod 内置（`env="auto"`） | 自动跟随系统 + 手动切换 |
| 统计 | Google Analytics 4 | 行业标准、免费、隐私模式支持 |
| RSS | PaperMod 默认输出 | 双语双 feed |

**已否决的备选**：
- Stack：项目展示页不原生，需要额外造 section
- hugo-Paper：搜索 / 暗色 / GA 都需手装，工作量不划算
- Astro + MDX：能更强但部署链与模板生态偏复杂，超出 MVP 范围

---

## 3. 仓库结构

```
C:/Dev/blog-site/                       ← 本地工作区
├── .github/workflows/hugo.yml          ← GitHub Actions 自动部署
├── config/                             ← Hugo 配置目录
│   ├── _default/
│   │   ├── config.toml                 ← 主配置
│   │   ├── languages.toml              ← 中英双语
│   │   ├── menus.toml                  ← 导航菜单
│   │   └── params.toml                 ← 主题参数 + Giscus / GA
│   └── production/                     ← 生产环境覆盖（baseURL 等）
├── content/                            ← 内容源
│   ├── posts/                          ← 博客文章
│   ├── projects/                       ← 项目展示
│   └── about/index.md                  ← 关于我
├── static/                             ← 直接复制到站点根目录
│   ├── images/                         ← 头像、封面图
│   └── favicon.ico
├── themes/PaperMod/                    ← 主题作为 git submodule
├── .gitignore                          ← 排除 public/、resources/
├── hugo.toml                           ← Hugo 版本声明（可选）
└── README.md                           ← 部署 / 编辑说明
```

**职责划分原则**：
- 配置 (`config/`) 与内容 (`content/`) 物理隔离
- 主题作为 submodule，独立升级
- 静态资源（图片、字体、favicon）直接放 `static/`，Hugo 不再处理

---

## 4. 信息架构

### 4.1 站点地图

| 路径（中 / 英） | 用途 | 来源 |
|---|---|---|
| `/` | 首页：头像 + 简介 + 最新文章 | `layouts/index.html`（PaperMod） |
| `/en/` | 英文首页 | 同上 |
| `/posts/` | 文章列表（含按时间倒序） | `content/posts/*.md` |
| `/en/posts/` | 英文文章列表 | `content/posts/*.md`（lang=en） |
| `/projects/` | 项目卡片列表 | `content/projects/*.md` |
| `/en/projects/` | 英文项目列表 | 同上 |
| `/about/` | 关于我（详细） | `content/about/index.md` |
| `/en/about/` | 英文关于我 | 同上 |
| `/tags/<tag>/` | 标签页 | 自动生成 |
| `/archives/` | 时间归档 | 自动生成 |
| `/index.xml` | 中文 RSS | 自动生成 |
| `/en/index.xml` | 英文 RSS | 自动生成 |

### 4.2 内容模型

**博客文章 front matter（content/posts/*.md）**
```yaml
---
title: "文章标题"
date: 2026-08-13T10:00:00+08:00
draft: false
tags: ["Hugo", "GitHub Pages"]
categories: ["技术笔记"]
description: "一句话摘要，给搜索引擎 + 列表用"
image: "cover.jpg"        # 可选；相对路径从 static/ 取
weight: 1                  # 用于置顶排序
lang: "zh"                 # 标识语言
---
```

**项目页 front matter（content/projects/*.md）**
```yaml
---
title: "项目名"
date: 2026-08-13
description: "项目简介"
tech: ["Hugo", "TypeScript"]            # 技术栈
github: "https://github.com/xxx/yyy"   # 可选
demo: "https://yoursite.com"            # 可选
cover: "project-cover.png"              # 可选封面
weight: 1
---
```

**关于页 front matter（content/about/index.md）**
```yaml
---
title: "关于我"
date: 2026-08-13
lang: "zh"
---
```

### 4.3 约定

- 文件名用英文或拼音短横线（如 `hugo-blog-setup.md`），URL 不带中文
- 中英文章用 `lang` 字段区分；`defaultContentLanguageInSubdir = false` 让中文放根路径
- 默认中文为隐式（无 `lang` 视为 `zh`）。Hugo 的 `defaultContentLanguage = "zh-cn"` 会让 `content/posts/*.md` 默认归到中文分组；写到 `/en/` 路径下的英文文章需要显式写 `lang: "en"`。
- 中文文章的 `lang: "zh"` 也可显式写出，便于阅读（见 §4.2 about 页示例）

---

## 5. 部署流水线

**触发条件**
- `push` 到 `main` 分支 → 自动构建 + 部署
- `workflow_dispatch` → 手动触发

**workflow 文件 `.github/workflows/hugo.yml` 关键步骤**

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
          submodules: true
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
          cname: ""
          keep_history: true
          enable_force_orphan: true
```

**权限与密钥**
- `Settings → Actions → General → Workflow permissions` 选 "Read and write permissions"（用户已设置）
- 一期不需要任何密钥

**部署产物**
- Actions 把 `public/` 推到 `gh-pages` 分支
- GitHub Pages 服务从 `gh-pages` 提供内容
- `main` 分支保留源码

**保护性约定**
- `public/`、`resources/_gen/` 进 `.gitignore`，构建在 Actions 里完成
- Hugo 版本在 workflow 写死，避免升级翻车
- 失败时 GH 显示红色 ✕，暂不做额外通知（一期）

---

## 6. 功能接入详细

### 6.1 评论：Giscus

**接入步骤**
1. GitHub 仓库 `sanbika/sanbika.github.io` → Settings → Discussions（默认已启用）
2. 访问 [giscus.app/zh-CN](https://giscus.app/zh-CN) → 输入 `sanbika/sanbika.github.io` 自动获取 repoId / categoryId
3. 在 `config/_default/params.toml` 配置：

```toml
[params.comments]
  enabled = true
  provider = "giscus"

  [params.comments.giscus]
    repo = "sanbika/sanbika.github.io"
    repoId = "R_xxx"          # 从 giscus.app 获取
    category = "General"
    categoryId = "DIC_xxx"    # 从 giscus.app 获取
    mapping = "pathname"
    lightTheme = "light"
    darkTheme = "dark_dimmed"
    reactionsEnabled = true
```

### 6.2 全站搜索

```toml
[params]
  enableSearch = true
  searchLimit = 10
```

无后端，纯客户端索引 + 模糊匹配（Fuse.js）。PaperMod 模板已默认集成。

### 6.3 暗色模式

```toml
[params]
  env = "auto"           # auto / light / dark
  defaultTheme = "auto"
  ShowReadingTime = true
  ShowShareButtons = false
```

PaperMod 默认在顶部按钮处提供切换，自动跟随系统。

### 6.4 访问统计：Google Analytics 4

注册 [analytics.google.com](https://analytics.google.com) → 新建 GA4 媒体资源 → 拿到 measurement ID（如 `G-XXXXXXXXXX`）：

```toml
[params.analytics.google]
  id = "G-XXXXXXXXXX"
```

### 6.5 RSS

PaperMod 默认输出 `index.xml`：
- 中文 RSS：`/index.xml`
- 英文 RSS：`/en/index.xml`

无需特殊配置。在顶部菜单里放 RSS 入口（见 §7.2 `menus.toml` 第四条），同时保留 §7.1 socialIcons 区域里的 RSS 图标用于页脚展示入口。

---

## 7. 配置骨架预览

### 7.1 `config/_default/config.toml`

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

### 7.2 `config/_default/menus.toml`

主导航菜单（顶部），按 weight 升序排列：

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

### 7.3 `.gitignore`

```
public/
resources/_gen/
.hugo_build.lock
.DS_Store
```

---

## 8. 实施分期与验收

| 阶段 | 内容 | 验收标准 |
|---|---|---|
| **P1 本地骨架** | 克隆仓库、装 PaperMod submodule、本地 `hugo server` 跑起来 | 浏览器 `localhost:1313` 看到 PaperMod 默认首页 |
| **P2 配置定稿** | 改 config.toml、languages.toml、params.toml、接入双语 | 中英切换正常、菜单对位 |
| **P3 Actions 部署** | 写 workflow、推 main、看到 GitHub Pages 上线 | `https://sanbika.github.io` 可访问 |
| **P4 内容填充** | 添加 about / 2 篇示范文章 / 1 个项目 | 列表、详情页都正常，标签 / 归档正确 |
| **P5 功能启用** | Giscus 接入、搜索 / 暗色 / GA4 验证 | 评论、搜索、暗色按钮、GA4 后台有数据 |
| **P6 打磨** | 头像上传、favicon、首页 hero 区定制 | 视觉符合预期 |

### 8.1 验收策略

- **P1-P3** 冒烟测试：`git push` 后 GitHub Pages URL 可见、浏览器 console 无错
- **P4-P5** 链接验证：每个菜单 / 标签 / 归档页都能点开；Giscus 评论组件渲染
- **P6** 视觉走查：用户和我一起过一遍预览

### 8.2 错误处理表

| 场景 | 处理 |
|---|---|
| 推送后 Actions 失败 | workflow 日志看步骤错误，Hugo 通常是 frontmatter 或模板报错 |
| 站点 404 | 检查 Pages 设置的分支是否指向 `gh-pages`；自定义域名检查 CNAME |
| 评论不显示 | 检查 Giscus 的 repoId / categoryId、讨论区是否开启、域名白名单 |
| 搜索不到文章 | Hugo 的 `outputs.section` 必须有 JSON 输出（PaperMod 默认已配） |
| 双语链接错乱 | `defaultContentLanguageInSubdir` 必须 false，否则中文会被推到 `/zh-cn/` |

### 8.3 测试范围

一期不做自动化测试（静态站点 + 提交频率低，性价比不高）；以冒烟测试 + 视觉走查为主。

---

## 9. 风险与限制

| 风险 | 缓解 |
|---|---|
| GitHub Pages 偶发不稳 | Hugo 部署纯静态产物，依赖极轻 |
| 主题升级引入 breaking change | 通过 submodule 锁定提交，升级前 diff 看变更日志 |
| 一期不做 i18n 完整 review，部分英文翻译缺失 | 接受 MVP，先从中文起步 |
| 评论需要 GitHub 账号登录 | Giscus 的固有局限，与目标用户群体匹配可接受 |
| GA4 在中国大陆可能被屏蔽 | 一期不解决；如未来加入百度统计可再配置 `analytics.baidu` |

---

## 10. 后续工作（明确不在本期范围）

- 自定义域名接入
- 邮件订阅（Newsletter）
- 全文 RSS 输出 / Atom feed
- 主题深度定制
- 评论反垃圾策略
- 访问统计升级（Plausible / Umami 自托管）
