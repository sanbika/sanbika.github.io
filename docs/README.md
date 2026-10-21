# Documentation

This is the project's knowledge layer. It follows **structure is navigation**: this file is the top-level map, and each area has its own `README.md` as its index page. Drill down on demand — do not load everything at once (progressive disclosure).

## Map

| Area | When to look here | Entry |
|------|-------------------|-------|
| Current state | Before starting any task — read the progress / TODO board first | [[current-state.md]] |
| Conventions | Encoding, commits, naming and the other stable rules | [[conventions/README.md]] |
| Historical archives | The design specs and implementation plans of past rounds | `superpowers/specs/` / `superpowers/plans/` |

## Conventions

`conventions/README.md` is the index of the stable rules:

- [[conventions/i18n.md]] — bilingual content, UI copy, third-party component language, configuration files
- [[conventions/frontend-styling.md]] — brand color, where CSS overrides land, the homepage two-column layout, the visual language of the archive quest card
- [[conventions/giscus.md]] — comment routing, the two categories, the hooking rules for the archive pages
- [[conventions/ci.md]] — the deployment workflow and the theme drift check

## Historical archives

`superpowers/specs/` and `superpowers/plans/` keep the design document and the implementation plan of each past round. The two documents dated 2026-08-18 describe the check-in image wall — that feature was retired on 2026-10-20, so both are kept purely as a historical archive rather than as current documentation.

The board in [[current-state.md]] records what each round actually changed; the documents under `superpowers/` are the archive behind that record.
