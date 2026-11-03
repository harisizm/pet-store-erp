# AGENTS.md — Kitaab ERP

Entry point for every coding agent (Claude Code, Codex, Cursor, Copilot, and others). Claude Code
also reads `CLAUDE.md`, which imports this file.

Kitaab is a multi-tenant, offline-first retail ERP for small shops in Pakistan, with pet retail as
the first vertical pack. The specs are in `docs/`. There is no code yet.

## 0. Build strategy: extend an open-source base, don't write from scratch
The founder's decision (2026-11-03): pick a mature open-source ERP/POS from GitHub that best fits
Pakistani pet shops, clone it, and build Kitaab on top of it.

- **Chosen base (2026-11-03):** ERPNext v16 + POS Awesome V15
  (`docs/adr/0002-build-on-erpnext-and-pos-awesome.md`, evaluation in
  `docs/13-open-source-base-evaluation.md`).
- **Next task:** the spike in `docs/13` §5 (offline 72 h, Urdu, hosting cost). No Kitaab feature
  work starts until it passes or the fallback is chosen. Then rewrite `docs/AGENTS.md` §2 for Frappe.
- **Effect on the specs.** `docs/03-srs.md` (what to build) still holds; the base is measured against
  it. The stack in `04-architecture.md` §2–3 and the tooling rules in `docs/AGENTS.md` §2 (NestJS,
  Drizzle, pnpm/Turborepo) are superseded by whatever the chosen base uses. The domain invariants in
  `docs/AGENTS.md` §1 still hold, translated into the base's idiom:
  - money never as float;
  - stock as a ledger;
  - posted documents immutable;
  - tenant isolation;
  - idempotent offline sync;
  - en+ur i18n.

  Logged as conflict C1 in `docs/00`.
- **How to build on the base:**
  - Upstream stays upgradable. Put Kitaab features in the base's extension mechanism (app, module,
    plugin) rather than editing its core.
  - Every unavoidable core patch is listed in `docs/upstream-patches.md`, with the reason.

## 1. Read before you touch anything
1. `LESSONS.md`: what earlier agents learned the hard way. Apply it.
2. `docs/AGENTS.md`: **the engineering rules and Definition of Done.** They are non-negotiable
   (paisa integers, decimal quantities, RLS on every tenant table, stock as a ledger, immutable
   financial documents, UUIDv7, idempotency keys, i18n en+ur from day one).
3. `docs/README.md`: reading order and the precedence rule when docs conflict
   (`03-srs` > `05-data-model` > `04-architecture` > `06-api-spec` > others).
4. The SRS sections (`docs/03-srs.md`) for the requirement IDs your task touches.
5. `DESIGN.md` (once it exists) before any UI work.

### Doc status (2026-11-03)
| Docs | State |
|---|---|
| `README`, `AGENTS`, `00`–`03` | complete |
| `04-architecture` | complete through §6.6; truncated at §6.7, later sections missing |
| `05`–`12` | **not received**: stubs only |
| `13-open-source-base-evaluation` | complete; base chosen (ADR-0002) |

Do not fill the missing docs from memory or by inference. If a task depends on them (data model,
API spec, UX screens, roadmap), log the gap in `docs/00-assumptions-and-open-questions.md` and ask.

## 2. The task loop
Every task, however small, runs this loop. Skipping a step is a reported deviation, not a shortcut.

1. **Orient.** Run `git status` (if this is a repo), read `LESSONS.md`, and pick the task: from
   `docs/11-roadmap-and-agent-tasks.md` once it exists, otherwise from the founder's request.
2. **Trace.** List the `FR-`/`NFR-` IDs you are implementing. None exist? Add them to `03-srs.md`
   with `status: proposed` first. Check `00` for OPEN items you would be building on.
3. **Plan.** Non-trivial or ambiguous work: read the relevant code and docs, then put the decision to
   the founder as a short multiple-choice question with options grounded in what you found. Build
   only after the answer. Small, unambiguous work: proceed and state your assumption.
4. **Build.** Contracts first (`packages/shared/contracts`), pure domain logic in `packages/domain`
   with tests written alongside, then IO layers. Match the surrounding code.
5. **Verify.** Run the real checks (typecheck, lint, tests, build; the design audit for UI) and
   quote their output. "Should work" is not a result.
6. **Review.** Walk `docs/AGENTS.md` §3 Definition of Done line by line. Unticked items are either
   done or named in your report as left out, with the reason.
7. **Record.** Update `LESSONS.md` (see §4), write an ADR for any decision the docs did not make
   (`docs/adr/`), log doc conflicts in `00`, and update requirement status in the SRS.
8. **Report.** What changed, which IDs, the verification output, and anything left undone.

## 3. Design: no AI slop, from the first screen
Kitaab is a working tool used all day by cashiers on cheap Android tablets. It should look like a
well-made instrument, not a SaaS template.

- **No UI code before `DESIGN.md` exists** at the repo root, approved by the founder. It is produced
  with the `design-consultation` skill and is the design authority alongside `docs/08-ux-and-screens.md`.
- **Tokens only.** `DESIGN.md` tokens become CSS custom properties in the shared Tailwind preset
  (`packages/config`). Components never use raw hex values, ad-hoc font sizes or one-off radii.
- **shadcn/ui is a parts bin, not a look.** Restyle it through the tokens. Never ship its default
  neutral theme, default radius and default type untouched.
- **The blacklist.** Never ship: purple/indigo gradients or blue-to-purple schemes; the 3-column
  icon-in-circle feature grid; icons in coloured circles as decoration; centre-aligned everything;
  the same large radius on every element; decorative blobs or wavy dividers; emoji as design
  elements; coloured left-border cards; generic copy ("Welcome to Kitaab", "all-in-one solution");
  same-height cookie-cutter sections; `system-ui` as the primary typeface.
- **What this product needs instead:**
  - Density and speed on the POS: it is the hero screen (PRD §5).
  - Tabular figures, right-aligned, for money and quantities.
  - A typeface pairing that covers both Latin and Urdu (NFR-USE-002).
  - CSS logical properties (`margin-inline-start`, not `margin-left`), so RTL is free.
  - ≥ 44 px touch targets and WCAG AA contrast (NFR-USE-004).
  - Copy that says what to do next, not happy talk.
  - Every report number drillable to its documents (PRD §5.3).
- **Per screen:** spec in `08` → `plan-design-review` → (key screens: POS, owner dashboard, receipt:
  `design-shotgun` to compare directions) → build → `design-review` and `design-fix` against the
  running app → lesson if anything surprised you.

## 4. LESSONS.md: learning across sessions
`LESSONS.md` is shared memory for every agent on this repo. Agents read it at the start of a session
and write to it at the end of every task.

Add an entry when:
- the founder corrects you;
- a check fails for a non-obvious reason;
- a library, tool or environment behaves unexpectedly;
- an approach works well enough that it should be repeated;
- you find a doc gap or conflict.

Do not add what the docs or code already say, or one-off trivia. Before finishing a task, either
add a lesson or state "no new lessons" in your report.

Lessons are meant to graduate. When one has been applied twice or is clearly a hard rule:
1. promote it to where it is enforced: preferably a lint rule or test, otherwise `docs/AGENTS.md`
   or `DESIGN.md`;
2. mark it `promoted → <where>` and move it to the Archive section.

Keep the Active section under about 40 entries, because it is loaded into every session.

## 5. Where things live
| Path | Purpose |
|---|---|
| `docs/` | Specs, ADRs (`docs/adr/`). Source of truth for what and how. |
| `LESSONS.md` | Cross-session agent learnings. |
| `DESIGN.md` | Design system (created by the first design task). |
| `~/.claude/skills/` | Design skills (user-level, referenced not copied; see `CLAUDE.md`). |
| `.claude/agents/` | Review subagents (`dod-reviewer`, `design-critic`). |

## 6. Commands
Not scaffolded yet. The first build task scaffolds the monorepo per `docs/04-architecture.md` §3
(pnpm + Turborepo) and must replace this section with the real install, dev, typecheck, lint, test
and build commands.
