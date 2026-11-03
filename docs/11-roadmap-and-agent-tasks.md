# Roadmap and Agent Tasks

> **Re-authored 2026-11-03** for Odoo 18 (ADR-0003). The original was lost in transit. Tasks are
> agent-sized: one module or one concern, with clear requirement IDs and a done condition. Pick the
> first unticked task whose dependencies are ticked. Tick it, with the commit hash, when done.

## Phase 0 — Foundation (before any feature)
- [ ] **P0-0 Product name + tagline.** The founder supplies candidates; we check pronunciation,
  conflicts and domains (`00` B5). Then rename "Kitaab" and the `kitaab_*` prefix across this repo.
  Blocks P0-R.
- [ ] **P0-R Rebrand tool (ADR-0006).** Build `tools/rebrand/`:
  - inputs: pinned upstream (Odoo + OCA);
  - outputs: renamed forks;
  - a mapping table, preserving notices, adding modification notices;
  - the "no odoo outside the legal allowlist" gate over source, UI, PDFs, emails, HTTP responses
    and installer.

  Record the occurrence count it handles. Depends on P0-0 and P0-1. After it lands, point
  `repos.json` at the forks.
- [ ] **P0-1 First boot.** The founder creates the DB role:
  `scripts\setup-dev.ps1 -SkipPython -CreateDbRole` (needs the postgres superuser password).
  - Then create `kitaab_dev` with `point_of_sale, stock, purchase, account, product_expiry,
    pos_hr, l10n_pk, contacts`.
  - Record in `LESSONS.md` anything odd about Odoo 18 on Windows with PostgreSQL 18.
  - Done when: login works at `http://localhost:8069` and the installed-module list is quoted.
- [ ] **P0-2 `kitaab_privacy` (zero egress).** NFR-SEC-005..007, ADR-0005: remove and block the IAP
  family, neutralise publisher-warranty, disable Gravatar and link previews, add the egress guard
  and the CSP header, and `test_zero_egress`.
  - Depends on P0-1.
  - Done when: the test passes, and an hour of running shows nothing in the egress log outside the
    allowlist.
- [ ] **P0-3 Tooling and CI.** Add:
  - a `pre-commit` config (ruff, pylint-odoo, eslint, prettier);
  - `scripts/check-licences.py`;
  - the GitHub Actions workflow on `windows-latest` (`10` §3).

  Depends on P0-2.
- [ ] **P0-4 Design system.** Run `/design-consultation` → `DESIGN.md`, approved by the founder.
  It must cover a Latin + Urdu type pairing (closes NFR-USE-002's ADR), tokens, the POS density
  rules and the anti-slop rules.
- [ ] **P0-5 `kitaab_theme`.** Turn the tokens into SCSS/CSS variables for the backend and the POS,
  with our logo, favicon and typography.
  - Depends on P0-4 and P0-R. Debranding itself is done by the rebrand tool.
  - Done when: P0-R's gate is green on rendered pages and PDFs, and `design-fix` is clean.
- [ ] **P0-6 `kitaab_l10n_ur`.** Add the `ur_PK` language (RTL) and set up the translation workflow
  and `scripts/check-i18n.py`. First target: 100% of the POS screen strings.
- [ ] **P0-7 On-premise spike.** Covers C4 and NFR-AVL-002.
  - Install on a clean Windows 10 PC as a service; add the local CA and TLS.
  - Connect two Android tablets over the LAN.
  - Pull the internet for 72 h and sell 500+ orders; reboot the PC and the tablets mid-way.
  - Measure on a 2 GB tablet.
  - Done when: the report in `docs/spikes/P0-7.md` shows no lost orders and no duplicates.
- [ ] **P0-8 SaaS spike.**
  - Write a provisioning script for a Linux cloud host: multi-worker, `dbfilter`, TLS,
    default-deny egress.
  - Load 10 tenant databases and measure RAM, POS latency from Lahore, and cost per tenant (`00`
    T3).
  - Report in `docs/spikes/P0-8.md`.

## Phase 1 — "Retire the register"
| ID | Task | Module | Requirements | Depends |
|---|---|---|---|---|
| P1-1 | Roles and groups (§12 matrix), branch record rules + tests | `kitaab_security`, `kitaab_branch` | FR-ADM-002..004 | P0-2 |
| P1-2 | Device registration, PIN lockout, revoke | `kitaab_pos_device` | FR-ADM-006, NFR-SEC-004, NFR-OBS-003 | P1-1 |
| P1-3 | Settings: negative-stock policy, discount limits, cash rounding | `kitaab_settings` | FR-ADM-007, FR-INV-022 | P1-1 |
| P1-4 | Catalog: multi-barcode, internal EAN-13, labels, import template, price history | `kitaab_catalog` | FR-CAT-001..010 | P0-5 |
| P1-5 | FEFO lot pre-select in POS + expiry display | `kitaab_pos_fefo` | FR-INV-011 | P1-4 |
| P1-6 | Expired-lot block + Manager PIN (glue to OCA `pos_product_expiry`) | `kitaab_pos_expiry_oca` (AGPL) | FR-INV-012 | P1-5 |
| P1-7 | POS core: payment methods, receipt number/layout, refunds to khata/store credit, quick-add customer, shortcuts, PKR denominations | `kitaab_pos` | FR-POS-003..016 | P1-2 |
| P1-8 | E-receipt token + WhatsApp share | `kitaab_receipt` | FR-POS-009 | P1-7 |
| P1-9 | Khata: credit sale limit, POS collect, statements, `wa.me` reminders | `kitaab_khata` | FR-CUS-001..008, FR-POS-006 | P1-7 |
| P1-10 | Aging reports (glue to OCA `account_financial_report`) | `kitaab_aging_oca` (AGPL) | FR-CUS-005, FR-RPT-008 | P1-9 |
| P1-11 | Inventory: adjustment reasons, count session with snapshot, expiry write-off, near-expiry alerts, negative-stock review, reorder suggestions, balance check job | `kitaab_inventory` | FR-INV-001..030 | P1-4 |
| P1-12 | Purchasing: GRN lot/expiry defaults, bonus qty, price-update prompt, PO share | `kitaab_purchase` | FR-PUR-001..007 | P1-4 |
| P1-13 | Expenses quick entry, cash book, bank/wallet journals | `kitaab_expense` | FR-EXP-001..003 | P1-1 |
| P1-14 | Audit log rules (glue to OCA `auditlog`) | `kitaab_audit_oca` (AGPL) | FR-ADM-009 | P1-1 |
| P1-15 | Reports + owner dashboard + Z-report + daily digest (email) | `kitaab_reports` | FR-RPT-001..011, FR-RPT-013, FR-POS-013 | P1-7, P1-11 |
| P1-16 | Urdu: 100% for every P1 screen | `kitaab_l10n_ur` | NFR-USE-002 | all P1 UI |
| P1-17 | On-premise installer (Windows): Odoo + PostgreSQL + Python + our modules, local CA, hosts/firewall egress rules, nightly backup, licence notices | `installer/` | B6, ADR-0004/0005, NFR-DAT-001 | P0-7 |

## Phase 2 — Channels + Pet pack
- WhatsApp Cloud API through `kitaab_whatsapp_oca` (AGPL glue): receipts, reminders, order updates.
- `kitaab_channel_woo`, `kitaab_channel_shopify`, and the Orders inbox (FR-ORD-001..007).
- `kitaab_pet`: pets, live animals, health events, appointments, boarding, restock reminders,
  commission (FR-PET-001..009).
- Multi-branch: transfers, consolidated reports, branch pricelists. Resolve `00` C2 first.
- Accounting UI and exports (FR-ACC-002/003).

## Phase 3 — Scale
- Couriers.
- Payment APIs.
- FBR POS (opt-in).
- Self-serve SaaS signup.
- Further vertical packs.
- Migration to the next Odoo LTS-equivalent version (ADR-0003).
