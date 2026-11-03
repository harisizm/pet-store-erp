# Software Requirements Specification (SRS)

Conventions: `MUST` = required for the phase; `SHOULD` = strongly desired; `MAY` = optional.
Each requirement: ID · Phase · Statement · Acceptance criteria (AC).

---
## 1. Tenancy, Branches, Users (ADM)

**FR-ADM-001 · P1** The system MUST support multiple tenants (businesses); all business data is isolated per tenant.
AC: RLS tests prove cross-tenant reads/writes fail for every table.

**FR-ADM-002 · P1** A tenant MUST have one or more branches (shops). Each branch has name, address, phone, timezone (default Asia/Karachi), receipt header/footer, and logo.

**FR-ADM-003 · P1** Users MUST be able to belong to one tenant with access to one or more branches.

**FR-ADM-004 · P1** Built-in roles: Owner, Manager, Cashier, Groomer, Accountant. Permissions are granular (see §12 matrix). Owners MAY create custom roles (P2).

**FR-ADM-005 · P1** Owner/Manager login MUST be phone number + OTP. Optional password MAY be set.

**FR-ADM-006 · P1** POS devices MUST be registered to a branch by an Owner/Manager. On a registered device, cashiers log in with a 4–6 digit PIN.
AC: PIN login fails on unregistered devices; 5 failed PINs lock that user on that device for 5 minutes.

**FR-ADM-007 · P1** Tenant settings: business name, NTN/STRN (optional), negative-stock policy, discount limits per role, rounding rule for cash totals (none / nearest 1 / 5 / 10 PKR), default tax settings.

**FR-ADM-008 · P1** Feature flags per tenant control vertical packs and Pro features.

**FR-ADM-009 · P1** Audit log MUST record who, when, which device, what entity, and before/after values for create/update/void/delete of business entities and settings.

---
## 2. Catalog (CAT)

**FR-CAT-001 · P1** Items have: name (en), name (ur, optional), SKU (auto or manual), category, brand, item type (`stock`, `service`, `non_stock`, `serialized`), tax class, active flag, images, description, custom attributes (JSON per vertical pack).

**FR-CAT-002 · P1** Items MAY have variants (e.g., flavor × size). Each variant is a sellable unit with its own SKU, barcode(s), price and stock.

**FR-CAT-003 · P1** Each sellable unit has a **base unit** (e.g., `kg`, `piece`, `ml`) and MAY have **pack units** with conversion factors (e.g., `bag 15kg = 15 kg`, `carton = 24 piece`). Stock is held in base units.

**FR-CAT-004 · P1** Multiple barcodes per sellable unit/pack unit MUST be supported. Scanning a pack barcode adds the pack unit.

**FR-CAT-005 · P1** The system MUST generate internal barcodes (Code128 / EAN-13 in-store range) for items without manufacturer barcodes, and print labels (50×25 mm and 38×25 mm templates) with name, price, and barcode.

**FR-CAT-006 · P1** Prices: retail price per unit; optional wholesale price; branch-level override (P2). Price history MUST be kept.

**FR-CAT-007 · P1** Flags per item: `track_batches` (requires batch + expiry on receipt), `track_serials`, `allow_loose_sale`, `reorder_level`, `reorder_qty`.

**FR-CAT-008 · P1** Excel/CSV import with a downloadable template, row-level validation report, dry run, and commit. 1,000 rows MUST import in < 30 s.

**FR-CAT-009 · P1** Search by name (en/ur), SKU, barcode, brand; fuzzy prefix search returns results in < 150 ms on the POS device for 10,000 items.

**FR-CAT-010 · P1** Services (grooming, bath, nail trim, boarding night) are items of type `service`: no stock, MAY have duration.

**FR-CAT-011 · P1** Bundles/kits (e.g., "Kitten Starter Kit") MAY be defined; selling a bundle deducts component stock. (SHOULD in P1, MUST in P2.)

---
## 3. Inventory (INV)

**FR-INV-001 · P1** All stock changes MUST be recorded as immutable stock movements with: branch, sellable unit, batch (nullable), quantity (+/-, base units), unit cost, movement type, source document reference, timestamp, user, device.
Movement types: `opening`, `purchase_receipt`, `purchase_return`, `sale`, `sale_return`, `adjustment`, `count_adjustment`, `transfer_out`, `transfer_in`, `repack_out`, `repack_in`, `wastage`, `expiry_writeoff`, `bundle_consume`.

**FR-INV-002 · P1** On-hand quantity per (branch, unit, batch) MUST equal the sum of movements. A cached balance table is maintained transactionally.
AC: nightly job verifies balances = sum(movements); mismatches raise an alert.

**FR-INV-003 · P1** Costing: weighted average cost (WAC) per (branch, sellable unit), recalculated on each inbound movement with cost. COGS on sale = current WAC × qty.

**FR-INV-010 · P1** Batches have: batch number (optional; auto-generated if absent), expiry date (required if item `track_batches`), manufacture date (optional), received date, supplier.

**FR-INV-011 · P1** Sales of batch-tracked items MUST allocate from batches using **FEFO** (first-expiry-first-out). The cashier MAY override the batch.

**FR-INV-012 · P1** Selling an expired batch MUST show a blocking warning that requires Manager PIN to override (configurable).

**FR-INV-013 · P1** Near-expiry alerts at configurable thresholds (default 30/60/90 days) on the dashboard and in a daily digest.

**FR-INV-014 · P1** Expiry write-off: select expired batches, post `expiry_writeoff` movement with reason; value reported in loss reports.

**FR-INV-020 · P1** Manual adjustment with mandatory reason code (damage, theft, found, data correction, sample, internal use) and Manager permission.

**FR-INV-021 · P1** Stock count (stocktake): full or partial (by category/brand/location); count by scan or manual entry; multiple counters; variance report; approval posts `count_adjustment` movements. Sales during an open count MUST be handled using a snapshot-at-start + movements-during-count method.

**FR-INV-022 · P1** Negative stock: if tenant policy allows, sale proceeds and the balance goes negative; item is flagged in a "Negative stock" review list. If policy disallows, POS blocks with Manager override.

**FR-INV-030 · P1** Low-stock alerts when available qty ≤ reorder level. "Reorder suggestions" report proposes quantities (reorder_qty, or based on average daily sales × lead time days).

**FR-INV-031 · P1** Repacking/loose sale: open a pack unit into base units (e.g., 1 bag 15 kg → 15.000 kg loose) via `repack_out`/`repack_in` movements preserving cost and batch/expiry. POS MAY auto-open a pack when loose qty is insufficient (setting).

**FR-INV-040 · P2** Stock transfers between branches: request → dispatch (transfer_out) → receive (transfer_in) with discrepancy recording. In-transit stock is visible.

**FR-INV-050 · P2** Serialized items: each unit has a serial/identifier; sale must pick a specific serial. (Used by Pet pack live animals.)

---
## 4. Point of Sale (POS)

**FR-POS-001 · P1** POS runs as a PWA installable on Android tablets/phones and desktop Chrome/Edge.

**FR-POS-002 · P1 · Offline** POS MUST create sales, returns, khata payments, cash movements and shift closes while offline, using locally cached catalog, prices, customers, and balances. See NFR-AVL-002 and §Sync in architecture.

**FR-POS-003 · P1** Cart operations: add by scan/search/favorites grid; change qty (decimal for loose units); line discount (% or amount); bill discount; remove line; add note; select salesperson.

**FR-POS-004 · P1** Discounts beyond the role's limit require Manager PIN. All overrides are audited.

**FR-POS-005 · P1** Payment methods (configurable): Cash, Card (external terminal, record only), Bank transfer, JazzCash, Easypaisa, Raast, Khata (credit), Store credit, Other. Split payments across methods. Cash tendered → change due.

**FR-POS-006 · P1** Khata sale requires a selected customer; MAY enforce per-customer credit limit (warning or block, configurable).

**FR-POS-007 · P1** Hold/park a bill and resume later on the same device; held bills visible to the branch (P2, when online).

**FR-POS-008 · P1** Receipt: unique number per branch per day sequence (`BR1-20261103-0042`) generated offline-safely (device prefix allowed: `BR1-D2-20261103-0042`). Print to 80 mm/58 mm via browser print. Contents: header, items, qty × price, discounts, totals, tax (if any), payments, change, customer balance (if khata), footer, QR/link to e-receipt.

**FR-POS-009 · P1** WhatsApp receipt: generates a public, unguessable e-receipt URL and opens `wa.me/<phone>?text=...` with the link. P2: send automatically via Cloud API.

**FR-POS-010 · P1** Returns/exchanges: look up original receipt (scan QR, receipt no., or customer); select lines and quantities (≤ sold − already returned); refund to cash/original method/khata/store credit; restock to original batch or write off as damaged. Returns without a receipt require Manager PIN.

**FR-POS-011 · P1** Void: an unsaved cart can be cleared; a completed sale can only be reversed by a return (no deleting).

**FR-POS-012 · P1** Shifts: open shift with opening float; cash in/out with reason; close shift with counted cash by denomination (PKR 10/20/50/100/500/1000/5000 notes, coins); system shows expected vs counted and variance.

**FR-POS-013 · P1** Day close / Z-report per branch: sales by method, returns, discounts, cash variance, khata given/received, expenses paid from drawer. Once closed, the business day is locked (late offline syncs dated that day are accepted but flagged).

**FR-POS-014 · P1** Customer quick-add at POS: name + phone (validated Pakistani mobile `03XXXXXXXXX` → stored E.164 `+923XXXXXXXXX`).

**FR-POS-015 · P2** Service lines (grooming) MAY be attached to an appointment and staff member for commission.

**FR-POS-016 · P1** Keyboard-first operation on desktop (F-keys: F2 search, F4 customer, F8 pay, F9 hold, Esc clear) and barcode-scanner HID input support.

---
## 5. Customers & Khata (CUS)

**FR-CUS-001 · P1** Customer profile: name, phone(s), WhatsApp opt-in flag + timestamp, address, area, tags, notes, credit limit, opening balance, custom fields.

**FR-CUS-002 · P1** Khata ledger per customer: debits (credit sales), credits (payments, returns to khata), adjustments (Manager). Running balance. Immutable entries; corrections via reversal.

**FR-CUS-003 · P1** Receive payment against khata at POS or back office, any payment method, with optional allocation to specific invoices (FIFO default).

**FR-CUS-004 · P1** Customer statement for a date range: PDF and shareable link; WhatsApp share.

**FR-CUS-005 · P1** Khata aging report: 0–30, 31–60, 61–90, 90+ days; total receivable.

**FR-CUS-006 · P1** Reminder: generate a polite bilingual reminder message with the balance and statement link via `wa.me` (P1) or Cloud API template (P2).

**FR-CUS-007 · P1** Customer purchase history and lifetime value.

**FR-CUS-008 · P1** Duplicate detection on phone number; merge customers (Manager), preserving ledgers.

---
## 6. Suppliers & Purchasing (PUR)

**FR-PUR-001 · P1** Supplier profile: name, contact, phone, NTN (optional), payment terms (days), opening balance.

**FR-PUR-002 · P1 (SHOULD)** Purchase order: lines, expected prices, expected date; status draft → sent → partially received → received → closed. Share PO via WhatsApp/PDF.

**FR-PUR-003 · P1** Goods receipt (GRN): from PO or direct; per line qty, unit (pack or base), cost price, batch no., expiry date (required for batch-tracked items), free/bonus qty (cost 0, affects WAC). Posting creates `purchase_receipt` movements.

**FR-PUR-004 · P1** Purchase bill: may equal GRN (default, combined) or be entered separately; supplier balance increases.

**FR-PUR-005 · P1** Supplier payment: amount, method, reference, allocation to bills. Supplier ledger and payables aging.

**FR-PUR-006 · P1** Purchase return: select batch, qty, reason; posts `purchase_return` movement and supplier credit.

**FR-PUR-007 · P1** Price update prompt: when received cost changes, suggest new retail price using the item's markup %.

---
## 7. Expenses & Cash (EXP)

**FR-EXP-001 · P1** Expense entry: date, branch, category (rent, electricity, salaries, transport, packaging, marketing, misc), amount, paid-from (drawer/bank/owner), note, photo attachment.

**FR-EXP-002 · P1** Cash book per branch: all cash in/out from sales, returns, khata receipts, supplier payments, expenses, owner drawings/injections.

**FR-EXP-003 · P1** Bank/wallet accounts (e.g., Meezan, JazzCash) with balances derived from transactions; transfers between accounts.

---
## 8. Accounting (ACC)

**FR-ACC-001 · P1 (engine) / P2 (UI)** Every financial document posts balanced double-entry journal entries automatically using posting rules (see data model §8). Default chart of accounts provided per vertical.

**FR-ACC-002 · P2** Manual journal entries (Accountant/Owner), trial balance, profit & loss, balance sheet, general ledger by account, period lock.

**FR-ACC-003 · P2** Export to Excel/CSV.

---
## 9. Reports & Dashboard (RPT)

All reports: filters (date range, branch, category, brand, staff), drill-down to documents, export CSV/XLSX/PDF, respect branch timezone.

**FR-RPT-001 · P1** Owner dashboard (mobile-first): today/this week/month sales, gross profit, number of bills, average bill, cash expected, khata outstanding, low-stock count, near-expiry value, top 10 items, sales by hour.
**FR-RPT-002 · P1** Sales by day/item/category/brand/payment method/staff/customer.
**FR-RPT-003 · P1** Gross profit by item/category (revenue − COGS at WAC).
**FR-RPT-004 · P1** Stock on hand & valuation (at WAC) by branch/category, with batch detail.
**FR-RPT-005 · P1** Near-expiry and expired stock (qty, cost value, retail value).
**FR-RPT-006 · P1** Low stock & reorder suggestions.
**FR-RPT-007 · P1** Slow movers / dead stock (no sale in N days).
**FR-RPT-008 · P1** Khata aging; supplier payables aging.
**FR-RPT-009 · P1** Z-report history; cash variance by cashier.
**FR-RPT-010 · P1** Discounts and overrides report (fraud signal).
**FR-RPT-011 · P1** Stock movement history per item (item card).
**FR-RPT-012 · P2** Consolidated multi-branch versions of all the above.
**FR-RPT-013 · P1** Daily WhatsApp/email digest to Owner (P1 via email or in-app; P2 via WhatsApp template).

---
## 10. Online Orders & Channels (ORD) — Phase 2

**FR-ORD-001 · P2** Orders inbox unifying: website orders (WooCommerce/Shopify), manually entered WhatsApp/Instagram/phone orders.
**FR-ORD-002 · P2** Order lifecycle: `new → confirmed → picking → packed → out_for_delivery → delivered → closed`, plus `cancelled`, `returned`. Stock is **reserved** at confirmed and **issued** at packed.
**FR-ORD-003 · P2** Order confirmation call/WhatsApp step for COD orders (reduces fake orders); record confirmation result.
**FR-ORD-004 · P2** Delivery: own rider (name, phone, cash collected) or courier (Phase 3 API; P2 manual tracking number).
**FR-ORD-005 · P2** COD reconciliation: expected vs received cash per rider/courier settlement.
**FR-ORD-006 · P2** Channel stock sync: available qty (on hand − reserved − safety buffer) pushed to linked channels within 60 s of change.
**FR-ORD-007 · P2** Product linking: map channel products/variants to Hisabkar sellable units by SKU, barcode, or manual match UI.

---
## 11. Pet Vertical Pack (PET) — Phase 2 (behind flag `pack.pet`)

**FR-PET-001** Customer pets: name, species (cat, dog, bird, fish, rabbit, other), breed, sex, DOB/age, weight history, color/markings, neutered, allergies/diet notes, photo, vet name.
**FR-PET-002** Live animal inventory: serialized items with species, breed, sex, DOB, source (breeder/supplier), purchase cost, health records (vaccinations, deworming, vet checks with date, product, vet, next due date), photos/videos, status (`available`, `reserved`, `sold`, `deceased`, `returned`). Sale creates/links a customer pet profile automatically.
**FR-PET-003** Health/sale certificate PDF for live animal sale (details, vaccinations given, next due dates, shop terms). Shop-editable terms text.
**FR-PET-004** Health care reminders to customers (next vaccination/deworming due) via WhatsApp (opt-in).
**FR-PET-005** Appointments: grooming/bath/nail/boarding; resource (groomer, table, cage); date/time/duration; pet; services; status (`booked`, `checked_in`, `in_progress`, `done`, `no_show`, `cancelled`); deposit; convert to POS bill.
**FR-PET-006** Boarding: check-in/out dates, cage, feeding notes, daily charge, add-on services; bill on checkout.
**FR-PET-007** Restock reminders: for consumable items (flag `is_consumable`), compute each customer's typical repurchase interval per item (median of last 3 intervals, else default from item pack size and pet profile). Send reminder N days before expected date; one-tap reorder link (P2 with channel/Orders inbox).
**FR-PET-008** Staff commission on services (% or fixed per service) report.
**FR-PET-009** Item attributes for pet products: species, life stage (kitten/puppy/adult/senior), special diet (renal, urinary, gastro), pack weight. Used for search filters and reminders.

---
## 12. Permission matrix (Phase 1 defaults)
| Permission | Owner | Manager | Cashier | Groomer | Accountant |
|---|---|---|---|---|---|
| POS sell | ✔ | ✔ | ✔ | – | – |
| Discount ≤ role limit | ✔ (∞) | ✔ (20%) | ✔ (5%) | – | – |
| Returns with receipt | ✔ | ✔ | ✔ | – | – |
| Returns without receipt | ✔ | ✔ | PIN | – | – |
| Khata sale | ✔ | ✔ | ✔ | – | – |
| Stock adjust / count approve | ✔ | ✔ | – | – | – |
| Purchasing / GRN | ✔ | ✔ | GRN only (setting) | – | view |
| Supplier payments | ✔ | ✔ | – | – | ✔ |
| Expenses | ✔ | ✔ | drawer only | – | ✔ |
| Reports: sales | ✔ | ✔ | own shift | – | ✔ |
| Reports: profit/cost | ✔ | setting | – | – | ✔ |
| Cost price visible | ✔ | setting | – | – | ✔ |
| Users & settings | ✔ | – | – | – | – |
| Appointments (P2) | ✔ | ✔ | ✔ | own | – |

---
## 13. Non-Functional Requirements (NFR)

### Performance
- **NFR-PERF-001** POS add-to-cart from scan < 200 ms; complete sale (local commit) < 300 ms on a 2 GB RAM Android device.
- **NFR-PERF-002** POS catalog search < 150 ms for 10k sellable units.
- **NFR-PERF-003** API p95 < 400 ms for standard reads, < 800 ms for writes, at 200 tenants.
- **NFR-PERF-004** Dashboard loads < 2 s on 3G (~1 Mbps).

### Availability & offline
- **NFR-AVL-001** Cloud availability 99.5% monthly (Phase 1), 99.9% (Phase 3).
- **NFR-AVL-002** POS fully operational offline for ≥ 72 h and ≥ 5,000 offline transactions per device.
- **NFR-AVL-003** On reconnect, queued transactions sync within 60 s; duplicates impossible (idempotency).
- **NFR-AVL-004** Local data survives browser restart and device reboot (IndexedDB + persistent storage request).

### Data
- **NFR-DAT-001** Backups: continuous WAL archiving / point-in-time recovery 7 days; daily snapshots retained 30 days; restore tested monthly.
- **NFR-DAT-002** RPO ≤ 15 min, RTO ≤ 4 h for cloud.
- **NFR-DAT-003** Tenant data export (full, CSV/JSON zip) on request in < 24 h; self-serve in P2.

### Security (detail in 09)
- **NFR-SEC-001** TLS 1.2+ everywhere; HSTS.
- **NFR-SEC-002** RLS tenant isolation; automated tests.
- **NFR-SEC-003** OWASP ASVS Level 1 for P1, Level 2 targets for P2.
- **NFR-SEC-004** Device-bound refresh tokens for POS; remote device revoke.
- **NFR-SEC-005** *(added 2026-11-03, founder)* **Zero egress to Odoo S.A.** No component may send
  any data to `*.odoo.com`. This covers telemetry, publisher-warranty, IAP, SMS, snail mail, partner
  autocomplete and media library. It holds in every deployment (SaaS and on-premise), and no setting
  can turn it off.
  AC: the zero-egress test (ADR-0005) passes with all `hisabkar_*` modules installed and every cron
  triggered; a 24 h network capture of an on-premise build shows no Odoo host.
- **NFR-SEC-006** *(added 2026-11-03)* **Outbound allowlist.** The server connects only to loopback,
  its database, its SMTP relay, and hosts on the per-deployment allowlist. Each allowlisted
  integration is documented in `09-security-and-compliance.md` with the data it sends. Blocked
  attempts are logged.
- **NFR-SEC-007** *(added 2026-11-03)* **Browser containment.** Every web and POS response carries a
  Content-Security-Policy that limits scripts, styles, fonts, images and connections to the
  Hisabkar origin (plus `data:`/`blob:`). The client never loads from Odoo, Gravatar or third-party
  CDNs.

### Usability & localization
- **NFR-USE-001** A new cashier completes a 5-item sale with cash change unaided after ≤ 15 min training.
- **NFR-USE-002** All UI strings in English and Urdu; RTL layouts verified; Urdu font: Noto Nastaliq Urdu for headings or Noto Naskh Arabic for dense UI (decision in ADR).
- **NFR-USE-003** Number formatting: PKR with thousands separators (`Rs 12,500`); optional lakh grouping setting (`12,50,000`).
- **NFR-USE-004** Accessible contrast (WCAG AA) and minimum 44 px touch targets on POS.

### Compatibility
- **NFR-CMP-001** Chrome/Edge ≥ last 2 years on Android 9+ and Windows 10+. Safari iOS 16+ for owner dashboard (POS on iOS SHOULD work).
- **NFR-CMP-002** USB/Bluetooth HID barcode scanners; 80 mm and 58 mm thermal printers via OS print dialog.

### Observability
- **NFR-OBS-001** Structured logs with tenant_id, request_id, user_id; no PII in logs beyond IDs.
- **NFR-OBS-002** Error tracking (Sentry or equivalent) for API, web and POS (with offline buffering).
- **NFR-OBS-003** Sync health per device visible to platform admin and tenant owner (last sync time, queue length).

### Maintainability
- **NFR-MNT-001** Modular monolith with enforced module boundaries (lint rule).
- **NFR-MNT-002** ≥ 80% line coverage on domain modules (inventory, sales, ledger, sync).
