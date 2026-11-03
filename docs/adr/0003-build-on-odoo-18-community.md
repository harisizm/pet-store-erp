# ADR-0003: Build on Odoo 18 Community

- **Status:** accepted
- **Date:** 2026-11-03
- **Supersedes:** ADR-0001 (stack), ADR-0002 (ERPNext)
- **Requirements:** `00` B6 and T8; FR-POS-002, NFR-AVL-002, FR-INV-010..012, FR-CUS-002..006,
  FR-CAT-003, FR-INV-031, FR-ACC-001, FR-ADM-001, NFR-USE-002

## Context
The founder's constraints:
- build on an open-source base, not from scratch;
- the base must run natively on Windows;
- ship as an on-premise Windows install and as cloud SaaS;
- provide Urdu, free WhatsApp, free FBR and FEFO at the POS bill.

`13-open-source-base-evaluation.md` §8 found that no Windows-native base meets all four
must-haves. Odoo 18 Community is the only one that already does the two hardest things to build:
a browser POS that queues sales offline, and multi-database SaaS. It also has a one-click Windows
installer that runs as a service.

## Decision
- **Base:** Odoo 18.0 Community. The upstream repos are pinned to exact commits in `repos.json`
  and fetched into `vendor/`. They are referenced, never copied into this repo.
- **OCA modules** (AGPL-3, free):
  - `mail_gateway_whatsapp` (WhatsApp);
  - `pos_product_expiry` (block expired lots);
  - `account_financial_report` (aging);
  - plus their dependencies `report_xlsx` and `date_range`.
- **Hisabkar's own code:** Odoo modules in `addons/`, named `hisabkar_*`. Odoo core and OCA code are
  never edited in place. An unavoidable patch is listed in `docs/upstream-patches.md` with its
  reason.
- **On-premise:** the shop's Windows PC runs Odoo as a Windows service through Odoo's official
  installer or our bundled equivalent, with `hisabkar_*` modules added. Tills on the shop LAN use the
  browser, so internet loss does not stop sales.
- **SaaS:** a Linux cloud server at a hosting provider runs multi-worker Odoo with one database per
  shop, selected by `db_filter`. Nobody on the team or at the shops works on Linux directly; it is
  provisioned and deployed by script. Windows-only SaaS was rejected because Windows Odoo runs a
  single process with no workers and no memory cap.
- **Development:** native Windows. Odoo runs from source in a project `.venv` (Python 3.12 via
  `uv`) against local PostgreSQL. Setup: `scripts/setup-dev.ps1`.

## Consequences
**Our own modules fill the gaps.** Sizes are in `13` §8.3.
- `hisabkar_l10n_ur`: Urdu, the largest item.
- `hisabkar_pos_fefo`: FEFO lot pre-selection at the till.
- `hisabkar_khata`: khata collection and statements.
- `hisabkar_fbr_pos`: FBR, Phase 3.
- `hisabkar_pet`: the pet pack.

**Architecture docs written for NestJS no longer apply.**
- `04-architecture.md` §2–3 and `docs/AGENTS.md` §2 are superseded.
- `docs/AGENTS.md` §2 has been rewritten for Odoo.
- The §1 invariants map onto Odoo mechanisms, set out in `docs/AGENTS.md` §1:
  - Monetary fields stay as they are.
  - `stock.move` / `stock.quant` is the stock ledger.
  - Posted journal entries are immutable.
  - A database per tenant replaces RLS.

**Upgrade.** `odoo/odoo` already defaults to 20.0. Plan one migration (18 → 20 or later) before 18
leaves support. Keep `hisabkar_*` modules free of core monkey-patches to make that cheap.

**Licences.**
- **Odoo core (LGPL-3):** our modules may stay proprietary.
- **OCA modules (AGPL-3):** shipping them to shop PCs is distribution, so we offer their source. If
  we modify them and serve them over the network, we offer the modified source.

**Other risks.**
- WhatsApp Cloud API messages are billed by Meta.
- FBR POS fiscalisation is either a $78 LGPL module we fork, or our own build.
