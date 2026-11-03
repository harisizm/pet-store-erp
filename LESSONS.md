# LESSONS.md — what agents have learned on this repo

Read at the start of every session; written at the end of every task. Protocol: `AGENTS.md` §4.

**Entry format**
```
### L-NNN · YYYY-MM-DD · <area> · confidence: high|medium|low
**Trigger:** what happened (the correction, failure or surprise).
**Lesson:** the general truth behind it.
**Do:** the concrete behaviour to apply next time.
**Evidence:** command, file:line, PR or quote that backs it.
```
Areas: `domain` · `db` · `sync` · `api` · `frontend` · `design` · `i18n` · `testing` · `tooling` · `process`.
Numbers are never reused. Superseded lessons stay in the Archive with a pointer to their replacement.

---

## Active

### L-001 · 2026-11-03 · process · confidence: high
**Trigger:** The founder's 15-document spec arrived as one paste that was cut at the 50,000-character
message limit. `docs/04-architecture.md` stops mid-§6.7 and docs 05–12 never arrived.
**Lesson:** A missing spec is a question for the founder, not a gap to fill by inference. Invented
data models or API shapes become "the spec" the moment code is built on them.
**Do:**
- The founder has no copies of the originals.
- Docs 05–12 were re-authored for Odoo 18 on 2026-11-03 from the SRS and are marked as such.
- Where they conflict with `03-srs.md`, the SRS wins. Log the gap in `00`; do not quietly follow
  05–12.
- `04` §6.7 onward remains lost.

**Evidence:** `docs/04-architecture.md` truncation marker; "Re-authored" banners in `docs/05`–`12`.


### L-003 · 2026-11-03 · tooling · confidence: high
**Trigger:** During the open-source base search, `gh` reported an invalid token for `harisizm`.
Research fell back to the unauthenticated GitHub API, which allows about 60 requests/hour shared
across parallel agents.
**Lesson:** GitHub facts (stars, licence, push date) must be measured. That budget runs out fast
when several agents query at once.
**Do:** Read each repo once (`curl -s https://api.github.com/repos/OWNER/REPO`) and reuse the
result. Re-authenticated 2026-11-03 (`gh auth login -w`, device code approved by the founder). Once
`gh auth status` is green, prefer `gh api repos/OWNER/REPO`: authenticated calls allow 5,000/hour.
If the token goes invalid again, rerun that flow. Pushing works regardless, through Git Credential
Manager.
**Evidence:** `gh auth status` output; `docs/13-open-source-base-evaluation.md` §2.

### L-004 · 2026-11-03 · process · confidence: high
**Trigger:** The base platform was decided three times in one day.
- ERPNext was picked on features, then ruled out: the founder required a Windows-native dev
  environment and on-premise Windows installs.
- Licensing and "no data to the vendor" surfaced only after Odoo was picked.

**Lesson:** For a platform-level choice, the founder's non-functional constraints decide the
outcome before feature fit does. Those constraints: OS and hosting, deployment model, licence
freedom, data privacy, budget.

**Do:** Before evaluating any platform, library or service, ask in one multiple-choice round:
- where does it run (dev, prod, customer site);
- may we modify and resell it;
- may it send data anywhere;
- what may it cost.

Then research.

**Evidence:** ADR-0002 (superseded), ADR-0003, ADR-0004, ADR-0005; `docs/00` B6, T8, L1–L3.

### L-005 · 2026-11-03 · tooling · confidence: high
**Trigger:** The Odoo 18 egress audit found that `iap`, `sms`, `snailmail`, `partner_autocomplete`,
`web_unsplash` and `pos_sms`/`stock_sms`/`sale_sms` are all `auto_install`. They land on every
database alongside POS, stock and sales, even though nothing we need depends on them.

**Lesson:** In Odoo, what you install is not what you get. `auto_install` modules arrive silently
whenever their dependencies are present. A new upstream version or a new dependency can add
outbound calls without anyone choosing them.

**Do:** When adding a module dependency or upgrading upstream:
- compute the auto-install closure (the script pattern in ADR-0005's audit);
- re-run the egress grep over `vendor/`;
- keep `test_zero_egress` green.

Never assume "we didn't install X".

**Evidence:** ADR-0005 audit table; `__manifest__.py` `auto_install` flags in `vendor/odoo/addons`.

---
### L-006 · 2026-11-03 · db · confidence: high
**Trigger:** The first `odoo-bin -d hisabkar_dev -i ...` failed with "collations with different
collate and ctype values are not supported on this platform" (PostgreSQL 18, Windows).

**Lesson:**
- Upstream creates databases from `template0` with `LC_COLLATE 'C'`, while `template0`'s ctype is a
  Windows locale (`English_United States.1252`).
- PostgreSQL on Windows rejects that mismatch.
- If `db_template` is anything other than `template0`, upstream omits the collate clause.

**Do:**
- Every config (dev, test, on-premise installer) sets `db_template = hisabkar_template`, a database
  created once with `LC_COLLATE 'C' LC_CTYPE 'C'`. `scripts/setup-dev.ps1` does it.
- If a database fails to open with this error, drop it and recreate it through the template.
  Don't try to patch it.

**Evidence:** `.odoo-data/p0-1-install.log` (first run); `docs/upstream-patches.md` row 3.

### L-007 · 2026-11-03 · testing · confidence: high
**Trigger:** The first test run of `hisabkar_privacy` produced no test results. The egress guard had
blocked werkzeug resolving `0.0.0.0:8069` to *bind* the HTTP server, the server died, and
`odoo-bin` still exited 0.

**Lessons:**
- A socket-level guard sees binds as well as connects, because werkzeug resolves its listen address
  with `getaddrinfo`.
- `odoo-bin --test-enable` can exit 0 without running any test.

**Do:**
- In the guard, only host names are judged at resolution. IP literals, including `0.0.0.0` and
  LAN interface IPs, pass, and `connect()` makes the decision.
- Judge a test run by the `odoo.tests.stats` / "N tests" summary in the log, never by the exit code.
  A missing summary is a failure.

**Evidence:** `.odoo-data/p0-2-test.log` (first run); regression test
`test_server_can_resolve_its_listen_address`.

### L-008 · 2026-11-03 · tooling · confidence: high
**Trigger:** `hisabkar_privacy` uninstalled the IAP family from its own data file. That worked on an
existing database. On a fresh one-pass install, it left `iap` removed while `iap_mail`, `sms` and
others stayed installed, a broken database. It also logged "Some modules are not loaded".

**Lesson:**
- Inside a loading pass, modules load in dependency order.
- Marking modules `to remove` from one module's data affects only those already loaded. The
  loader then installs the queued ones over the mark.
- Uninstalling in a pass triggers a registry reload, which makes `--test-enable` run 0 post-install
  tests in that same command.

**Do:**
- Any "remove other modules" logic runs in `ir.model.data._process_end`, which fires after the
  whole pass and before the uninstall step.
- Test such modules in two commands: a fresh install, then
  `-u <module> --test-enable --test-tags /<module>`.

**Evidence:** `addons/hisabkar_privacy/models/ir_model_data.py`; `hisabkar_test` module states
after the first fresh-install attempt.

---

## Archive
_(Promoted or superseded lessons move here with `promoted → <where>` or `superseded by L-NNN`.)_

### L-002 · 2026-11-03 · tooling — promoted → `AGENTS.md` §6 "Rules for test runs"
Git Bash (MSYS) rewrites any argument starting with `/` into a filesystem path. It hit twice:
design-fix routes (documented in the skill), then `--test-tags /hisabkar_privacy`, which silently
selected 0 tests. Fix: prefix with `MSYS_NO_PATHCONV=1`, or use PowerShell.
