# AGENTS.md — Kitaab ERP

Entry point for every coding agent (Claude Code, Codex, Cursor, Copilot, and others). Claude Code
also reads `CLAUDE.md`, which imports this file.

Kitaab is a retail ERP + POS for small shops in Pakistan, with pet retail as the first vertical
pack. It is built on **Odoo 18 Community** and ships two ways:
- installed on a shop's own Windows PC, working offline;
- as cloud SaaS.

The specs are in `docs/`. Kitaab's own code is Odoo modules in `addons/` (none written yet).

## 0. Build strategy: extend Odoo, never fork it
- **Decision trail (2026-11-03):**
  - The founder chose to build on a mature open-source base, not from scratch.
  - Constraints: the base runs natively on Windows (`docs/00` T8), ships on-premise and as SaaS
    (`docs/00` B6), and covers Urdu, free WhatsApp, free FBR and FEFO at the POS bill.
  - ERPNext (ADR-0002) failed the Windows constraint.
  - **Odoo 18 Community** was chosen: `docs/adr/0003-build-on-odoo-18-community.md`, evaluation in
    `docs/13-open-source-base-evaluation.md` §8.
- **Upstream is referenced, not copied.**
  - `repos.json` pins Odoo and the OCA repos to exact commits.
  - `scripts/setup-dev.ps1` fetches them into `vendor/`, which is gitignored.
  - Never commit or edit anything under `vendor/`.
  - Kitaab behaviour goes in `addons/kitaab_*` modules: inherit, extend, override.
  - An unavoidable upstream patch is listed in `docs/upstream-patches.md` with its reason and the
    upstream issue.
- **Where it runs:**
  - Development and on-premise shop installs: native Windows.
  - Multi-shop SaaS: a Linux cloud server, provisioned and deployed by script. Nobody works on it
    by hand.
- **Specs after the switch:**
  - `docs/03-srs.md` (what to build) still holds.
  - `04-architecture.md` §2–3 (the NestJS stack) is superseded.
  - Docs 05–12 were written for Odoo.
  - The invariants in `docs/AGENTS.md` §1 are mapped onto Odoo mechanisms.
- **Next task:** `docs/11-roadmap-and-agent-tasks.md`, Phase 0, task P0-1.

## 1. Read before you touch anything
1. `LESSONS.md`: what earlier agents learned the hard way. Apply it.
2. `docs/AGENTS.md`: **the engineering rules, Odoo conventions and Definition of Done.**
   Non-negotiable.
3. `docs/README.md`: reading order and the precedence rule when docs conflict
   (`03-srs` > `05-data-model` > `04-architecture` > `06-api-spec` > others).
4. The SRS sections (`docs/03-srs.md`) for the requirement IDs your task touches, and their Odoo
   mapping in `docs/05-data-model.md`.
5. `DESIGN.md` (once it exists) before any UI work.
6. Before overriding anything, read the upstream code it touches in `vendor/`. Odoo's own code is
   the real documentation.

### Doc status (2026-11-03)
| Docs | State |
|---|---|
| `README`, `AGENTS`, `00`–`03` | founder originals, complete (`docs/AGENTS.md` §1–3 adapted for Odoo) |
| `04-architecture` | founder original; §2–3 superseded; truncated at §6.7 |
| `05`–`12` | originals lost in transit; **re-authored for Odoo 18** on 2026-11-03 from the SRS |
| `13-open-source-base-evaluation` | complete; base is Odoo 18 Community (ADR-0003) |

## 2. The task loop
Every task, however small, runs this loop. Skipping a step is a reported deviation, not a shortcut.

1. **Orient.** Run `git status`, read `LESSONS.md`, and pick the next open task from
   `docs/11-roadmap-and-agent-tasks.md` (or take the founder's request).
2. **Trace.** List the `FR-`/`NFR-` IDs you are implementing. None exist? Add them to `03-srs.md`
   with `status: proposed` first. Check `00` for OPEN items you would be building on.
3. **Fit-gap.** Find out what Odoo or an OCA module already does for those IDs: read the code in
   `vendor/` and try it in a running instance. Configure before you customise, and customise before
   you write new models.
4. **Plan.** Non-trivial or ambiguous work: put the decision to the founder as a short
   multiple-choice question grounded in what you found. Build only after the answer. Small,
   unambiguous work: proceed and state your assumption.
5. **Build.** In a `kitaab_*` module, following `docs/AGENTS.md` §2. Tests are written alongside.
6. **Verify.** Run the module's tests (`docs/AGENTS.md` §2), upgrade the module on a fresh database,
   and for UI run the design audit. Quote the real output. "Should work" is not a result.
7. **Review.** Walk `docs/AGENTS.md` §3 Definition of Done line by line, or run the `dod-reviewer`
   subagent. Unticked items are either done or named in your report as left out, with the reason.
8. **Record.** Update `LESSONS.md` (see §4). Write an ADR for any decision the docs did not make
   (`docs/adr/`). Log doc conflicts in `00`. Tick the task in `11`.
9. **Report.** What changed, which IDs, the verification output, and anything left undone.

## 3. Design: no AI slop, from the first screen
Kitaab is a working tool used all day by cashiers on cheap Android tablets and old Windows PCs. It
should look like a well-made instrument, not stock Odoo and not a SaaS template.

- **No UI work before `DESIGN.md` exists** at the repo root, approved by the founder. It is produced
  with the `design-consultation` skill and is the design authority alongside `docs/08-ux-and-screens.md`.
- **Tokens only, in one place.** `DESIGN.md` tokens become SCSS variables and CSS custom properties
  in the `kitaab_theme` module:
  - Odoo's `primary_variables` overrides for the backend;
  - a POS stylesheet for the till.
  - OWL templates never carry raw hex values, ad-hoc font sizes or one-off radii.
- **Stock Odoo purple is not our look.** Restyle through the theme module; never ship Odoo's default
  palette, or Bootstrap defaults, untouched.
- **The blacklist.** Never ship:
  - purple/indigo gradients or blue-to-purple schemes;
  - the 3-column icon-in-circle feature grid;
  - icons in coloured circles as decoration;
  - centre-aligned everything;
  - the same large radius on every element;
  - decorative blobs or wavy dividers;
  - emoji as design elements;
  - coloured left-border cards;
  - generic copy ("Welcome to Kitaab", "all-in-one solution");
  - same-height cookie-cutter sections;
  - `system-ui` as the primary typeface.
- **What this product needs instead:**
  - Density and speed on the POS: it is the hero screen (PRD §5).
  - Tabular figures, right-aligned, for money and quantities.
  - A typeface pairing that covers both Latin and Urdu (NFR-USE-002).
  - CSS logical properties, so RTL works for free.
  - ≥ 44 px touch targets and WCAG AA contrast (NFR-USE-004).
  - Copy that says what to do next, not happy talk.
  - Every report number drillable to its documents (PRD §5.3).
- **Per screen:**
  1. spec in `08`;
  2. `plan-design-review`;
  3. for key screens (POS, owner dashboard, receipt), `design-shotgun` to compare directions;
  4. build;
  5. `design-review` and `design-fix` against the running Odoo (`http://localhost:8069`);
  6. a lesson if anything surprised you.

## 4. LESSONS.md: learning across sessions
`LESSONS.md` is shared memory for every agent on this repo. Agents read it at the start of a session
and write to it at the end of every task.

Add an entry when:
- the founder corrects you;
- a check fails for a non-obvious reason;
- Odoo, a library or the environment behaves unexpectedly;
- an approach works well enough that it should be repeated;
- you find a doc gap or conflict.

Do not add what the docs or code already say, or one-off trivia. Before finishing a task, either
add a lesson or state "no new lessons" in your report.

Lessons are meant to graduate. When one has been applied twice or is clearly a hard rule:
1. promote it to where it is enforced: preferably a test or a pre-commit check, otherwise
   `docs/AGENTS.md` or `DESIGN.md`;
2. mark it `promoted → <where>` and move it to the Archive section.

Keep the Active section under about 40 entries, because it is loaded into every session.

## 5. Where things live
| Path | Purpose |
|---|---|
| `docs/` | Specs, ADRs (`docs/adr/`). Source of truth for what and how. |
| `addons/kitaab_*` | Kitaab's own Odoo modules (all Kitaab code lives here). |
| `repos.json` | Upstream repos (Odoo, OCA) pinned to exact commits. |
| `scripts/setup-dev.ps1` | Fetches upstream into `vendor/`, builds `.venv`, writes `odoo.conf`. |
| `vendor/` | Upstream code, gitignored. Read it; never edit it. |
| `LESSONS.md` | Cross-session agent learnings. |
| `DESIGN.md` | Design system (created by the first design task). |
| `~/.claude/skills/` | Design skills (user-level, referenced not copied; see `CLAUDE.md`). |
| `.claude/agents/` | Review subagents (`dod-reviewer`, `design-critic`). |

## 6. Commands (Windows, PowerShell, from the repo root)
**One-time setup.** Prerequisites: PostgreSQL 12+ running locally, `uv` and Git. Run:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\setup-dev.ps1 -CreateDbRole
```

The script fetches the pinned repos, creates `.venv` with Python 3.12 and writes `odoo.conf`.

**Run Odoo:**

```powershell
.venv\Scripts\python vendor\odoo\odoo-bin -c odoo.conf
```

Then open `http://localhost:8069`.

**Fresh database with a module installed:**

```powershell
.venv\Scripts\python vendor\odoo\odoo-bin -c odoo.conf -d kitaab_dev -i <module> --stop-after-init
```

**Test a module.** Use a throwaway database, because Odoo tests write to it:

```powershell
.venv\Scripts\python vendor\odoo\odoo-bin -c odoo.conf -d kitaab_test -i <module> --test-enable --test-tags /<module> --stop-after-init
```

**Upgrade a module after changes:** run the same command as for a fresh database, with
`-u <module>` in place of `-i <module>`.

**Upgrade upstream:**
1. Edit the commit in `repos.json`.
2. Rerun the setup script.
3. Run every `kitaab_*` test.
4. Commit `repos.json`.

PDF reports (receipts, statements) need wkhtmltopdf: `winget install wkhtmltopdf.wkhtmltox`.
