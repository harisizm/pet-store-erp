# AGENTS.md — Rules for Coding Agents

> Adapted 2026-11-03 for the Odoo 18 Community base (ADR-0003). The founder's original rules were
> written for a NestJS stack. Their intent is kept and mapped onto Odoo mechanisms here. §1.13–15
> are new founder requirements (ADR-0004 licensing, ADR-0005 zero egress).

## 0. Before writing code
- Read `README.md`, this file, and the SRS sections for your task. Read their Odoo mapping in
  `05-data-model.md`.
- Find the requirement IDs you are implementing. If none exist, stop and add them to `03-srs.md`
  first, marked `status: proposed`.
- Check `00-assumptions-and-open-questions.md`. Do not build on an "OPEN" item without noting it in
  your commit or PR.
- Read the upstream code you are about to extend in `vendor/`. Configure before customising;
  customise before adding models.

## 1. Non-negotiable engineering rules
1. **Money is exact.**
   - Use `fields.Monetary` with a `currency_id` (stored as `numeric`).
   - Never compare or sum money with raw float operators. Use `currency.round()`,
     `currency.compare_amounts()`, `currency.is_zero()`, or `odoo.tools.float_compare` /
     `float_round` with the currency rounding.
   - Taxes round per line (`tax_calculation_rounding_method = 'round_per_line'`).
   - Cash totals round via `account.cash.rounding` (FR-ADM-007).
   - Arithmetic we do outside the ORM (reports, imports) uses `Decimal`, or integer paisa
     (1 PKR = 100 paisa).
2. **Quantities are exact.**
   - Use `fields.Float(digits='Product Unit of Measure')`, with that precision set to 3 decimals.
   - Compare with `float_compare(..., precision_rounding=uom.rounding)` and never with `==`.
3. **Tenant isolation is one database per shop.**
   - No code may read or write across databases.
   - SaaS runs with `dbfilter` and `list_db = False`.
   - Branch-level restrictions inside a shop use record rules, and each new rule gets a test.
4. **Stock is a ledger.**
   - On-hand quantity comes from done `stock.move` / `stock.move.line` records; `stock.quant` is the
     cached balance Odoo maintains.
   - Never write `quantity` on `stock.quant`, and never `UPDATE` stock tables with SQL.
   - Adjustments go through inventory adjustments (`action_apply_inventory`) or stock moves.
5. **Posted documents are immutable.**
   - Posted `account.move`, paid `pos.order` and done pickings are corrected by reversal, refund or
     return, never by `write` or `unlink`.
   - Respect lock dates.
   - Never override `unlink` or `write` to bypass Odoo's posted-state checks.
6. **Offline-created records carry a client `uuid`.**
   - `pos.order` already has one, and Odoo dedupes on it.
   - Any custom model the POS can create offline must have a unique `uuid` and dedupe on it.
7. **Every write endpoint we add is idempotent.** Custom controllers and RPC methods called by the
   POS or by integrations accept an idempotency key (the record uuid or an `Idempotency-Key`
   header). Replaying a call has no second effect.
8. **Time.**
   - Datetimes are stored in UTC (Odoo does this).
   - Show and bucket them in the branch timezone (default `Asia/Karachi`).
   - Business-day boundaries in reports use the branch timezone, never the server timezone.
9. **Module boundaries.**
   - All Kitaab code lives in `addons/kitaab_*` modules, and every dependency is declared in
     `__manifest__.py`.
   - Extend with `_inherit`, OWL `patch()` and view inheritance. Never edit `vendor/`.
   - No monkey-patching outside the one sanctioned place: the egress guard in `kitaab_privacy`
     (rule 15).
   - Raw SQL is allowed only in read-only reports, with a comment saying why the ORM was not used.
10. **Contracts.** POS↔server calls use Odoo's data service and RPC. Every custom route or RPC
    method is documented in `06-api-spec.md`, with its payload, idempotency key and error cases.
11. **i18n from day one.**
    - Python strings use `_()` or `_lt()`, OWL strings `_t()`, and XML is translatable.
    - Every module ships `i18n/<module>.pot` and `i18n/ur.po`.
    - The UI must survive RTL.
12. **No secrets in code or data files.**
    - API keys and tokens live in `odoo.conf`, environment variables, or system parameters set at
      deploy time.
    - Never put them in XML/CSV data or in commits.
    - Document each one in `.env.example` / `docs/09`.
13. **Licensing (ADR-0004).**
    - Kitaab business modules are proprietary (`'license': 'Other proprietary'`). They may depend
      only on Odoo core (LGPL-3) and LGPL-compatible modules.
    - **A proprietary module must never list an AGPL module in `depends`**, and must never import
      from one.
    - Anything that needs an OCA AGPL module goes in a separate thin glue module, licensed
      `AGPL-3`, whose source we publish.
    - Never copy, port or read-to-reimplement Odoo Enterprise code (OEEL-1).
14. **Trademark.** The product is Kitaab. The "Odoo" name and logo appear nowhere a user sees:
    titles, login page, emails, receipts, PDFs, the about dialog, domains or marketing.
    Copyright and licence notices inside source files stay untouched.
15. **Zero egress to Odoo S.A. (ADR-0005, NFR-SEC-005..007).**
    - Nothing may send data to `*.odoo.com` or to any third party unless the integration is
      explicitly allowlisted.
    - `kitaab_privacy` must be installed on every database. It:
      - removes the IAP family and the usage-report (publisher-warranty) call;
      - enforces the outbound allowlist;
      - sets the Content-Security-Policy.
    - Never install or depend on `iap`, `iap_mail`, `sms`, `snailmail*`, `partner_autocomplete`,
      `web_unsplash`, `*_sms` or any `*_iap*` module.
    - A new outbound integration needs:
      - an allowlist entry;
      - a test;
      - a line in `docs/09` saying what data leaves and why.

## 2. Repository conventions (Odoo)
- **Layout:**
  - `addons/kitaab_<area>/` with the standard OCA layout: `__manifest__.py`, `models/`, `views/`,
    `security/ir.model.access.csv`, `data/`, `static/src/`, `i18n/`, `tests/`, `migrations/`.
  - One concern per module. `kitaab_pet` is the vertical pack and is switched on by installing it.
- **Manifest:**
  - `version` is `18.0.MAJOR.MINOR.PATCH`.
  - `license` follows §1.13.
  - `author` is `"Kitaab"`.
  - Explicit `depends`.
  - `installable: True`.
  - `auto_install` only for glue modules.
- **Python:** Python 3.12. Follow Odoo guidelines (model `_name` with dots, `_description` set,
  fields with `string`/`help`). Lint with `ruff` and `pylint-odoo` through `pre-commit` (set up in
  task P0-3).
- **JavaScript:** OWL components, ES modules with `/** @odoo-module */`, and `patch()` for upstream
  components. Lint with `eslint` and `prettier` via `pre-commit`.
- **Data:**
  - XML for views, actions, menus and security.
  - `noupdate="1"` only for records users are meant to edit.
  - Demo data lives under `demo/`, never `data/`.
- **Migrations:**
  - Bump the module version for every schema or data change.
  - Add `migrations/18.0.x.y.z/pre-` or `post-migrate.py` scripts when existing data must change.
  - Migrations run forward only.
- **Upstream:**
  - `repos.json` pins exact commits. Upgrade by editing it, rerunning `scripts/setup-dev.ps1`, and
    running every `kitaab_*` test.
  - Unavoidable upstream patches are listed in `docs/upstream-patches.md`.
- **Commits:** Conventional Commits with requirement IDs, for example
  `feat(kitaab_pos_fefo): pre-select earliest-expiry lot [FR-INV-011]`.
- **Feature flags:**
  - A pack is a module: installing `kitaab_pet` turns the pack on.
  - Finer switches are `res.config.settings` booleans backed by `ir.config_parameter`.
- **Commands:** `../AGENTS.md` §6.

## 3. Definition of Done (every task)
- [ ] Requirement IDs referenced in code comments at entry points and in test names or docstrings.
- [ ] Tests in `tests/`:
  - `TransactionCase` for model logic;
  - `HttpCase` with a tour for every POS or UI flow touched.
  - All pass via `--test-tags /<module>` on a fresh database (quote the output).
- [ ] Module installs on a fresh database and upgrades (`-u`) cleanly, with no new warnings or
      errors in the log.
- [ ] Record rules tested: a user restricted to branch A cannot read or write branch B's records,
      for every new model holding branch data.
- [ ] Money and quantity edge cases tested: zero, negative (returns/refunds), rounding at line level,
      loose decimals.
- [ ] If the POS can do it offline: a replay test (same uuid or idempotency key twice → one effect).
- [ ] i18n: `.pot` regenerated and `ur.po` updated; RTL checked on any screen touched.
- [ ] Audit: business fields `tracking=True` on `mail.thread` models; create/update/void captured
      by the audit-log glue (FR-ADM-009).
- [ ] Licensing (§1.13): no proprietary module depends on or imports an AGPL module. `license` set.
- [ ] Zero egress (§1.15): `kitaab_privacy`'s egress test still passes with the new module
      installed.
- [ ] `06-api-spec.md` updated for any new route or RPC method.
- [ ] Nothing under `vendor/` changed. No TODOs without a linked issue.

## 4. When unsure
Choose the simplest design that satisfies the SRS, preferring what Odoo already does. Write the
decision as an ADR in `docs/adr/NNNN-title.md` (context, decision, consequences), and continue.
