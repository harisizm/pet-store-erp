# CLAUDE.md — Kitaab ERP

The shared rules for every agent are imported below; this file only adds what is specific to Claude Code.

@AGENTS.md
@docs/AGENTS.md
@LESSONS.md

## Claude Code specifics

### Skills
The design skills are user-level skills in `~/.claude/skills/`. They are referenced here, not
copied into the repo, so there is one copy and it stays current. If one is missing on a machine,
ask the founder to install it there rather than vendoring it into the repo.

| Moment | Skill |
|---|---|
| Before the first screen, or to change the visual direction | `/design-consultation` → writes `DESIGN.md` |
| A screen spec or UI plan is ready, before building it | `/plan-design-review` |
| Key screens (POS, owner dashboard, receipt): compare directions | `/design-shotgun`, then `/design-html` for the chosen one |
| UI built and running locally | `/design-review` (taste, hierarchy, AI-slop score) and `/design-fix` (measured defects) |

`design-fix` reads its project overlay from `.claude/design-fix.md`. Create
`.claude/design-fix.json` (`baseUrl`, `startCommand`, `routes`, `appDir`) on its first real run,
once an app serves pages. Never start a dev server for it; ask the founder to run it.

The gstack skills (`design-consultation`, `plan-design-review`, `design-shotgun`, `design-html`,
`design-review`) call helper binaries under `~/.claude/skills/gstack/`. On a machine without gstack
installed, they lose those features but still run.

### Review subagents
- `dod-reviewer`: run on the diff before reporting any task done. It checks requirement tracing,
  the `docs/AGENTS.md` §1 invariants and the §3 Definition of Done. Give it the diff and the IDs,
  not your conclusion.
- `design-critic`: run on any UI change before `/design-review`. It checks the change against
  `DESIGN.md`, the blacklist in `AGENTS.md` §3 and the NFR-USE requirements.

### Memory
Project learnings go in `LESSONS.md`, where every agent and every machine sees them, not in
personal auto-memory. Personal memory is for facts about the founder's preferences only.
