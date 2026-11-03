# Testing and Quality

> **Re-authored 2026-11-03** for Odoo 18 (ADR-0003). The original was lost in transit.

## 1. Test layers
| Layer | Tool | What it covers | Where |
|---|---|---|---|
| Model logic | `odoo.tests.TransactionCase` | Money/qty rounding, FEFO selection, khata balance, idempotency, record rules | `addons/kitaab_*/tests/` |
| UI and POS flows | `odoo.tests.HttpCase` + tours (`start_tour`; POS tours via `/pos/ui`) | The 8 key flows in `08` §4, including offline sale → sync | same |
| Zero egress | `kitaab_privacy/tests/test_zero_egress.py` | All `kitaab_*` installed, every `ir.cron` triggered, known flows exercised; asserts zero non-allowlisted connection attempts | `kitaab_privacy` |
| Licence boundaries | Script over all manifests | No `Other proprietary` module depends (transitively) on an AGPL module | `scripts/check-licences.py` (task P0-3) |
| Translations | Script over `i18n/ur.po` | Untranslated-term count per module; fails if a P1 screen's module drops below its target | `scripts/check-i18n.py` (task P0-6) |
| Performance | Scripted POS load with 10k products on a 2 GB Android tablet; API timing at volume | NFR-PERF-001..004 | manual + recorded in `docs/perf/` |
| Device matrix | Manual checklist per release | Android 9+ Chrome, Windows 10+ Chrome/Edge, iOS 16+ Safari (owner views), 80/58 mm printers, HID scanners (NFR-CMP-001/002) | release notes |

## 2. Rules
- **Tests are part of the module.** A task is not done until its tests pass on a fresh database
  (`docs/AGENTS.md` §3) and the output is quoted.
- **Use a throwaway database** (`kitaab_test`), never the dev database.
- **Every requirement ID has at least one test** naming it in its docstring.
- **Coverage:** at least 80% line coverage on `kitaab_*` domain code: khata, FEFO, inventory, POS
  sync (NFR-MNT-002). Measure with `coverage run vendor/odoo/odoo-bin ...`.
- **Offline replay:** for anything the POS can do offline, a test submits the same payload twice
  and asserts a single effect.
- **Bugs:** every fix starts with a failing test.

## 3. Continuous integration (task P0-3)
- **Runner:** GitHub Actions on `windows-latest`, matching the Windows-native target. The runner
  already has PostgreSQL.
- **Steps:**
  1. `scripts/setup-dev.ps1`;
  2. install all `kitaab_*` modules on a fresh database with `--test-enable`;
  3. the zero-egress test;
  4. the licence and i18n checks;
  5. `pre-commit` (ruff, pylint-odoo, eslint, prettier).
- A red CI blocks merge.

## 4. Quality gates per release
- All of CI green.
- The 8 key-flow tours green.
- A 24 h on-premise network capture with zero non-allowlisted hosts (ADR-0005).
- `design-review` and `design-fix` clean on the POS and dashboard (`AGENTS.md` §3).
- Device matrix checked.
- Release notes list the requirement IDs delivered.
