# Status and Resume Point

> **Last updated:** 2026-11-03, end of session 1.
>
> Read this first when picking the work back up. It records what exists, what was verified and how,
> and the exact next steps. Update it at the end of every working session.

## 1. Where things stand

| Area | State |
|---|---|
| Product definition | Done. Name **Hisabkar**, tagline "Your one place to manage your entire business." Specs 00–13 written; 05–12 re-authored for the chosen base. |
| Platform decision | Done. Odoo 18 Community, hard-forked later by a rebrand tool (ADR-0003, ADR-0006). Proprietary modules + published AGPL glue (ADR-0004). Zero egress to the vendor (ADR-0005). |
| Agent setup | Done. `AGENTS.md`, `CLAUDE.md`, `LESSONS.md` (8 lessons, 1 promoted), review subagents `dod-reviewer` and `design-critic`, design skills referenced from `~/.claude/skills`. |
| Dev environment | Done. Native Windows, pinned upstream in `vendor/`, Python 3.12 `.venv`, PostgreSQL 18 with a C/C template database. |
| Product code | 1 module: `addons/hisabkar_privacy` (zero egress). 24 tests, all passing. |

### Phase 0 roadmap (`docs/11-roadmap-and-agent-tasks.md`)

| Task | State | Evidence |
|---|---|---|
| P0-0 Product name + tagline | **Done** | `docs/00` B5; commit `8a2bf53` |
| P0-1 First boot | **Done** | `hisabkar_dev` installed; login verified by browser test and live request; commits `8c95410`, `913850b` |
| P0-2 `hisabkar_privacy` | **Code done; soak partial** | 24/24 tests, 0 failed (`.odoo-data/p0-2-test.log`); `dod-reviewer` blockers fixed; live soak ran 5 min 18 s (11:07:37–11:12:55 UTC) with 0 blocked, 0 CSP violations, 0 errors. The task asks for 1 hour. |
| P0-R Rebrand tool | Not started | Sized in ADR-0006: 1,164,743 occurrences in 35,326 core files |
| P0-3 Tooling and CI | Not started | |
| P0-4 Design system (`DESIGN.md`) | Not started | |
| P0-5 `hisabkar_theme` | Not started | Depends on P0-4 and P0-R |
| P0-6 Urdu language module | Not started | |
| P0-7 On-premise spike | Not started | |
| P0-8 SaaS spike | Not started | |

Phase 1 (17 tasks): not started.

## 2. Resume here, in this order
1. **Finish P0-2's soak.** Start the server (`AGENTS.md` §6), leave it running for an hour, then
   run:

   ```bash
   grep -c -E 'Blocked outbound|Content-Security-Policy violation| (ERROR|CRITICAL|WARNING) ' .odoo-data/p0-2-soak.log
   ```

   Zero means done: tick P0-2 in the roadmap with the time window.
2. **P0-3 Tooling and CI.** Add:
   - `pre-commit` (ruff, pylint-odoo, eslint, prettier);
   - `scripts/check-licences.py` (no proprietary module may reach an AGPL module);
   - a GitHub Actions workflow on `windows-latest` running the two-step test procedure.
3. **P0-4 Design system.** Run `/design-consultation` to produce `DESIGN.md`. Needs the founder's
   approval before any UI work.
4. **P0-R Rebrand tool**, then **P0-5 theme**, **P0-6 Urdu**, and the **P0-7 / P0-8 spikes**.

## 3. Decisions still open (founder)
| Item | Where |
|---|---|
| Trademark terms of the base platform (page returned 404) | `docs/00` L1 |
| Legal review of licensing and the EULA before the first paid customer | `docs/00` L2 |
| Register "Hisabkar" (IPO Pakistan) and a domain (`hisabkar.pk` / `.app` / `.co` / `.io` looked free) | `docs/00` L4 |
| Hosting region for SaaS | `docs/00` T3 |
| SMS OTP provider | `docs/00` T5 |

## 4. Environment state on the founder's PC
| Thing | Value |
|---|---|
| Databases | `hisabkar_dev` (dev, privacy module installed); `hisabkar_test` (throwaway test database); `hisabkar_template` (C/C locale template, do not delete) |
| Dev login | `admin` / `admin`. Change it before using the database for anything real. |
| Server | Stopped. Start: `.venv\Scripts\python vendor\odoo\odoo-bin -c odoo.conf`, then open `http://localhost:8069`. |
| Browser tests | Playwright Chromium at `%LOCALAPPDATA%\ms-playwright\chromium-1234\chrome-win64\chrome.exe` (set `ODOO_BROWSER_BIN`). Not Edge. |
| Gotchas | From Git Bash, prefix `odoo-bin` with `MSYS_NO_PATHCONV=1`. If a server is already on 8069, tests need `--http-port 8070`. Judge test runs by the `odoo.tests.result` line, not the exit code. |

## 5. Known limits carried forward
These are recorded in ADR-0005 and `docs/upstream-patches.md`:
- The POS screen has not yet been exercised under the browser policy; that needs a configured till
  (P1-7).
- The egress guard under the Linux gevent worker is unverified until P0-8.
- Collateral blocking: `base_automation`, `hr_presence` and the Indian and Italian e-invoicing
  modules cannot be installed.
- The UI is still the stock base look and name until P0-R and P0-5.
