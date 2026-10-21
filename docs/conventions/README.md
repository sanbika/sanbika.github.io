# Conventions

Conventions for encoding, commits, naming and the like (the stable layer).

## Contents
- [[conventions/i18n.md|i18n]] — bilingual content, UI copy, third-party component language, configuration file conventions
- [[conventions/frontend-styling.md|Frontend styling]] — brand color, where CSS overrides land, the homepage two-column layout, the visual language of the archive page quest card (clean modern style)
- [[conventions/giscus.md|Giscus comments]] — the two-category split between articles and archive pages, the comment hooking rules for archive pages, the two configuration sources `comments.giscus` / `comments.spark`, the process for adding a comment scenario
- [[conventions/ci.md|CI / GitHub Actions]] — the two workflows for deployment and theme drift detection, cross-workflow triggering, permissions, workflow_dispatch
- (To be added, e.g. `commit-message.md`)

## Document linking conventions

When documents reference a specific file from one another, always use the wikilink syntax, with the path relative to the docs/ root (for example pointing at `[[current-state.md]]` — always write the full path, from any location). Only reference files that actually exist inside docs/, and never leave a dead link. Filename patterns or placeholders (such as `<feature>.md` or `NNNN-short-title.md`) go in inline code and are not written as wikilinks.

> Writing example: `\[\[current-state.md\]\]` renders as the visible `[[current-state.md]]`, which avoids the example text being misread as a real link.

## Checklist
- (None yet)