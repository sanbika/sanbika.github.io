# 浆果丛林 / Berry Jungle

个人博客与个人主页。基于 [Hugo](https://gohugo.io/) + [PaperMod](https://github.com/adityatelange/hugo-PaperMod) 主题，托管在 GitHub Pages 上。

- 线上地址：<https://sanbika.github.io>
- 仓库：<https://github.com/sanbika/sanbika.github.io>

## 技术栈

- **静态生成**：Hugo extended v0.164+
- **主题**：PaperMod（git submodule）
- **部署**：GitHub Actions → 官方 [`actions/deploy-pages`](https://github.com/actions/deploy-pages) → GitHub Pages
- **评论**：[Giscus](https://giscus.app/)（基于 GitHub Discussions）
- **搜索**：PaperMod 内置 Fuse.js（客户端索引）
- **统计**：Google Analytics 4

## 本地开发

```bash
hugo server -D
```

默认访问 <http://localhost:1313/>。

### 安装 Hugo

```bash
winget install --id=Hugo.Hugo.Extended
```

macOS：`brew install hugo`，Linux：`snap install hugo --channel=extended`。

## 写作

在 `content/posts/` 下创建 Markdown：

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

中英双语版：在同目录创建 `*.en.md`，加 `lang: "en"`，并在 front matter 里写 `title` 为英文版本。

## 项目展示

在 `content/projects/` 下创建项目页：

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

## 部署

推送到 `main` 即触发 Actions 自动部署：

```bash
git push origin main
```

工作流：`.github/workflows/hugo.yml`（`build` + `deploy`，构建产物通过 `actions/upload-pages-artifact` 上传，`actions/deploy-pages` 直接驱动 Pages 服务）。

> 仓库设置：Settings → Pages → Source 必须为 **GitHub Actions**（不是 "Deploy from a branch"），否则 deploy job 会失败。

## 目录结构

```
.
├── content/                  ← 所有 Markdown 内容
│   ├── posts/                ← 博客文章
│   ├── projects/             ← 项目展示
│   └── about/                ← 关于我
├── static/                   ← 静态资源（直接复制到站点根目录）
│   ├── images/avatar.jpg     ← 头像
│   └── favicon.ico           ← 浏览器标签图标
├── layouts/_partials/        ← 自定义 partial 覆盖 PaperMod 默认
│   ├── comments.html         ← Giscus 评论
│   └── google_analytics.html ← GA4 gtag.js
├── config/_default/          ← Hugo 配置
├── themes/PaperMod/          ← 主题（git submodule）
├── .github/workflows/        ← GitHub Actions
└── docs/superpowers/         ← 设计与实施文档（gitignore）
```

## 设计参考

- 设计 spec：`docs/superpowers/specs/2026-08-13-personal-blog-design.md`
- 实施计划：`docs/superpowers/plans/2026-08-13-personal-blog-implementation.md`