# Data Model (Odoo 18 mapping)

> **Re-authored 2026-11-03.** The founder's original 05 was lost in transit and was written for a
> NestJS stack. This version maps every SRS entity onto Odoo 18 Community models (ADR-0003). Where
> Odoo has no model, it defines the `hisabkar_*` model to build. If the original turns up, reconcile
> against this; do not replace it blindly.
>
> Precedence: `03-srs.md` wins over this file. Where Odoo's behaviour differs from the SRS, the
> difference is logged in `00` (C2–C4) rather than silently accepted.

**Licence column:**
- **P**: proprietary `hisabkar_*` module, depending only on core (LGPL).
- **G**: AGPL glue module, because it touches an OCA AGPL module (ADR-0004).

## 1. Tenancy, branches, users (ADM)
| SRS concept | Odoo model / mechanism | Hisabkar addition | Module (licence) |
|---|---|---|---|
| Tenant (FR-ADM-001) | One **PostgreSQL database** per shop business. SaaS selects it with `dbfilter`; on-premise has one database on the shop PC. | none | (config) |
| Branch (FR-ADM-002) | `stock.warehouse` (stock, address) + one or more `pos.config` (tills) per branch. A single `res.company` per tenant. | `hisabkar_tz` (default `Asia/Karachi`), `hisabkar_code` (receipt prefix) and logo on `stock.warehouse`. Receipt header/footer use `pos.config` fields. | `hisabkar_branch` (P) |
| User + branch access (FR-ADM-003) | `res.users`; allowed warehouses and POS configs per user | Record rules limiting branch users to their warehouses, POS configs and sessions | `hisabkar_branch` (P) |
| Roles (FR-ADM-004, §12 matrix) | `res.groups` | Groups `hisabkar_owner`, `hisabkar_manager`, `hisabkar_cashier`, `hisabkar_groomer`, `hisabkar_accountant`, implying the matching Odoo groups | `hisabkar_security` (P) |
| Owner/Manager login (FR-ADM-005) | Odoo login + `auth_totp` (2FA, core) | Phone + OTP login is OPEN (`00` T5; Odoo's SMS is IAP and excluded by ADR-0005) | later |
| Cashier PIN (FR-ADM-006) | `pos_hr`: employees log into the POS with a PIN | 5-failure lockout per device | `hisabkar_pos_device` (P) |
| Registered POS device (FR-ADM-006) | none | `hisabkar.pos.device`: name, `device_code`, `pos_config_id`, `registered_by`, `active`, `revoked_at`, `last_sync_at`, `queue_length` | `hisabkar_pos_device` (P) |
| Tenant settings (FR-ADM-007) | `res.config.settings` / `ir.config_parameter`; `account.cash.rounding`; company tax settings | Negative-stock policy, discount limit per group | `hisabkar_settings` (P) |
| Feature flags (FR-ADM-008) | Installed modules (`hisabkar_pet` = pet pack) + settings booleans | none | none |
| Audit log (FR-ADM-009) | `mail.thread` tracking (`tracking=True`) + OCA `auditlog` (before/after values) | Auditlog rules for business models, created by data | `hisabkar_audit_oca` (G) |

## 2. Catalog (CAT)
| SRS concept | Odoo | Hisabkar addition | Module |
|---|---|---|---|
| Item / variant / sellable unit (FR-CAT-001/002) | `product.template` / `product.product` (attributes → variants) | `name` is translatable, so Urdu names live in its `ur_PK` translation; no extra field | none |
| Item type (FR-CAT-001) | `type`: `consu` + `is_storable` = stock, `service`, `consu` without storable = non-stock; `tracking='serial'` = serialized | none | none |
| Base unit + pack units (FR-CAT-003) | `uom.uom` within a `uom.category` (e.g. kg ← bag 15 kg, ratio 15). `uom_id` = stock/base unit, `uom_po_id` = purchase unit | none (see C3) | none |
| Multiple barcodes (FR-CAT-004) | `product.product.barcode` holds one; `product.packaging.barcode` holds one per packaging (scanning it adds the packaging qty in the POS) | `hisabkar.product.barcode` (one-to-many on product, unique per company) + POS barcode lookup patch | `hisabkar_catalog` (P) |
| Internal barcodes + labels (FR-CAT-005) | `barcodes` nomenclature; product label report | EAN-13 in-store range generator; 50×25 and 38×25 mm label templates | `hisabkar_catalog` (P) |
| Prices + history (FR-CAT-006) | `list_price`; `product.pricelist` (wholesale; per-branch pricelist on `pos.config` in P2) | `tracking=True` on `list_price` → history in chatter; price-history report | `hisabkar_catalog` (P) |
| Flags (FR-CAT-007) | `tracking='lot'` + `use_expiration_date` (`product_expiry`) = track_batches; `tracking='serial'`; `stock.warehouse.orderpoint` = reorder level/qty | `hisabkar_allow_loose_sale` boolean | `hisabkar_catalog` (P) |
| Excel import (FR-CAT-008) | `base_import` (CSV/XLSX, dry-run "Test", row errors) | Hisabkar import template (columns mapped to fields) | `hisabkar_catalog` (P) |
| POS search (FR-CAT-009) | POS in-browser product search | Urdu name and brand in the POS search index | `hisabkar_pos_search` (P) |
| Services (FR-CAT-010) | `type='service'` | `hisabkar_duration_min` | `hisabkar_catalog` (P) |
| Bundles (FR-CAT-011) | POS **combo** products (core 18) for sale-time bundles; `mrp` kit BoM for stock-deducting kits (P2) | none | P2 decision |

## 3. Inventory (INV)
| SRS concept | Odoo | Hisabkar addition | Module |
|---|---|---|---|
| Stock movements ledger (FR-INV-001) | `stock.move` / `stock.move.line` (done = immutable fact, with from/to locations, lot, qty, `picking_type`, origin); valuation layers `stock.valuation.layer` | Movement-type mapping report (Odoo locations/picking types → SRS movement types) | `hisabkar_reports` (P) |
| Balance = sum(movements) (FR-INV-002) | `stock.quant` (cached by Odoo) | Nightly job: quant qty vs Σ done move lines, alert on mismatch | `hisabkar_inventory` (P) |
| WAC costing (FR-INV-003) | Product category `property_cost_method='average'` (AVCO) + automated valuation. **AVCO is per company, not per branch.** | see C2 | none |
| Batches + expiry (FR-INV-010) | `stock.lot` + `product_expiry`: `expiration_date`, `use_date`, `removal_date`, `alert_date` | none | none |
| FEFO at sale (FR-INV-011) | `removal_strategy = fefo` on category/location orders reservations by `removal_date`. **The POS does not pre-select lots by expiry.** | POS patch that pre-selects the earliest-expiry lot with stock and shows its expiry; cashier may override | `hisabkar_pos_fefo` (P) |
| Expired-batch block (FR-INV-012) | OCA `pos_product_expiry` blocks an expired lot chosen in the POS | Manager-PIN override on top | `hisabkar_pos_expiry_oca` (G) |
| Near-expiry alerts (FR-INV-013) | `alert_date` on lots; activity scheduling | 30/60/90-day dashboard tiles + daily digest | `hisabkar_inventory` (P) |
| Expiry write-off (FR-INV-014) | Scrap (`stock.scrap`) with a scrap location | Reason "expiry"; loss report | `hisabkar_inventory` (P) |
| Manual adjustment + reason (FR-INV-020) | Physical inventory on `stock.quant` (`inventory_quantity`, apply) | Mandatory reason code (damage, theft, found, data correction, sample, internal use); manager-only apply | `hisabkar_inventory` (P) |
| Stock count (FR-INV-021) | Physical inventory filtered by location, category or product; counted quantities; apply. **Applies against the quantity at apply time, not at count start.** | `hisabkar.stock.count` session with a snapshot-at-start and movements-during-count correction | `hisabkar_inventory` (P) |
| Negative stock (FR-INV-022) | Odoo permits negative quants; POS sells regardless | Policy switch + "Negative stock" review list | `hisabkar_inventory` (P) |
| Low stock / reorder (FR-INV-030) | `stock.warehouse.orderpoint` + replenishment report | Average-daily-sales × lead-time suggestion | `hisabkar_inventory` (P) |
| Repack / loose (FR-INV-031) | Stock held in the base UoM (kg); a bag purchase converts to kg on receipt; selling 2.5 kg deducts 2.5 kg | see C3 | none |
| Transfers (FR-INV-040, P2) | Inter-warehouse transfer with transit location | Discrepancy on receive | P2 |
| Serials (FR-INV-050, P2) | `tracking='serial'`; POS asks for the serial | none | none |

## 4. POS, shifts, receipts (POS)
| SRS concept | Odoo | Hisabkar addition | Module |
|---|---|---|---|
| Till / PWA (FR-POS-001/002) | `pos.config`; POS runs in the browser and queues orders offline in IndexedDB | see C4 (HTTPS on the shop LAN) | `hisabkar_pos_device` (P) |
| Sale, lines, payments (FR-POS-003/005) | `pos.order`, `pos.order.line`, `pos.payment`, `pos.payment.method` (Cash, Bank, `pay_later` = customer account) | Payment methods JazzCash, Easypaisa, Raast, Store credit seeded as data | `hisabkar_pos` (P) |
| Discount limit + override (FR-POS-004) | Global/line discount; `pos_hr` manager approval | Per-group limit; Manager-PIN override; audit row | `hisabkar_pos` (P) |
| Khata sale + credit limit (FR-POS-006) | `pay_later` payment method needs a partner; `res.partner.credit_limit` | Warn or block per setting | `hisabkar_khata` (P) |
| Hold/park (FR-POS-007) | Several open orders per session (core) | none | none |
| Receipt number (FR-POS-008) | `pos.order.pos_reference` (offline-safe, session-based) | Format `{branch}-{device}-{yyyymmdd}-{seq4}` from `hisabkar_code` + `device_code`; receipt layout | `hisabkar_pos` (P) |
| WhatsApp e-receipt (FR-POS-009) | none | `hisabkar.receipt.token` (unguessable) + public route `/hisabkar/r/<token>` + `wa.me` link | `hisabkar_receipt` (P) |
| Returns (FR-POS-010) | POS refund against the original order (qty ≤ sold − refunded) | Refund to khata/store credit; restock vs damaged; Manager PIN without receipt | `hisabkar_pos` (P) |
| Void (FR-POS-011) | Paid orders cannot be deleted; refunds only | none | none |
| Shift (FR-POS-012) | `pos.session` with opening cash, cash in/out (`pos.session` cash moves), closing count by bills/coins (`pos.bill`) | PKR denominations seeded; variance per cashier | `hisabkar_pos` (P) |
| Day close / Z-report (FR-POS-013) | Session closing + "Sales Details" report | Branch Z-report (by method, returns, discounts, variance, khata given/received, drawer expenses); day lock | `hisabkar_reports` (P) |
| Quick-add customer (FR-POS-014) | POS partner creation | `03XXXXXXXXX` validation → E.164 via `phone_validation` | `hisabkar_pos` (P) |
| Shortcuts (FR-POS-016) | Partial | F2/F4/F8/F9/Esc bindings | `hisabkar_pos` (P) |

## 5. Customers & khata (CUS)
| SRS concept | Odoo | Hisabkar addition | Module |
|---|---|---|---|
| Customer (FR-CUS-001) | `res.partner` | `hisabkar_wa_opt_in` + timestamp, `hisabkar_area`; tags via `category_id` | `hisabkar_khata` (P) |
| Khata ledger (FR-CUS-002) | **Receivable `account.move.line`s on the partner**: credit sales post debit AR; payments and refunds post credit; posted lines are immutable and corrected by reversal | Khata view (running balance) over AR move lines | `hisabkar_khata` (P) |
| Receive payment (FR-CUS-003) | `account.payment` + reconciliation (FIFO by default via auto-reconcile). Collecting in the POS (`pos_settle_due`) is **Enterprise**, so not used. | POS "Collect khata" screen creating an `account.payment` | `hisabkar_khata` (P) |
| Statement (FR-CUS-004) | none in CE | Statement PDF + share link + `wa.me` | `hisabkar_khata` (P) |
| Aging (FR-CUS-005, FR-RPT-008) | OCA `account_financial_report` aged partner balance | Menu + filters | `hisabkar_aging_oca` (G) |
| Reminder (FR-CUS-006) | none | Bilingual message template + `wa.me` link (P1); WhatsApp API (P2) | `hisabkar_khata` (P) |
| History / LTV (FR-CUS-007) | Partner smart buttons (POS orders) | LTV field | `hisabkar_khata` (P) |
| Duplicates / merge (FR-CUS-008) | `base.partner.merge.automatic.wizard` (core) | Duplicate-phone warning | `hisabkar_khata` (P) |

## 6. Suppliers, purchasing, expenses, money (PUR / EXP)
| SRS concept | Odoo | Hisabkar addition |
|---|---|---|
| Supplier (FR-PUR-001) | `res.partner` (supplier rank), `property_supplier_payment_term_id` | none |
| PO (FR-PUR-002) | `purchase.order` (draft → sent → purchase → done) | WhatsApp share link |
| GRN with batch/expiry, bonus qty (FR-PUR-003) | Receipt `stock.picking`, lots with expiry on move lines | Bonus qty as a zero-price PO line (still affects AVCO) |
| Bill (FR-PUR-004) | Vendor bill `account.move` (`in_invoice`) | none |
| Supplier payment + aging (FR-PUR-005) | `account.payment`; aging via `hisabkar_aging_oca` (G) | none |
| Purchase return (FR-PUR-006) | Return picking + vendor credit note | none |
| Price-update prompt (FR-PUR-007) | none | Markup-based retail suggestion on receipt (`hisabkar_purchase`, P) |
| Expense (FR-EXP-001) | Vendor bill in an expense journal, or POS cash-out | Quick expense entry with category, paid-from and photo (`hisabkar_expense`, P) |
| Cash book (FR-EXP-002) | Cash journal + POS cash moves | Branch cash-book report (`hisabkar_reports`, P) |
| Bank/wallet accounts (FR-EXP-003) | `account.journal` type bank (Meezan, JazzCash) + internal transfers | Seeded journals |
| Double-entry (FR-ACC-001) | `account` (core) with `l10n_pk` chart of accounts | none |

## 7. Pet pack (PET, `hisabkar_pet`, P), Phase 2
New models (no base has them):
- `hisabkar.pet`: partner_id, name, species (selection), breed, sex, dob, weight lines, colour, neutered, allergies, photo, vet_name.
- `hisabkar.animal`: lot_id (`stock.lot`, serial), species, breed, sex, dob, source partner, cost, status (`available`/`reserved`/`sold`/`deceased`/`returned`), media.
- `hisabkar.health.event`: animal_id or pet_id, type (vaccination, deworming, vet_check), date, product_id, vet, next_due_date.
- `hisabkar.appointment`: pet_id, resource (`hisabkar.resource`: groomer, table, cage), start, duration, service lines, status, deposit, pos_order_id.
- `hisabkar.boarding.stay`: pet_id, cage, check-in/out, feeding notes, daily rate, add-ons.
- `hisabkar.restock.reminder`: partner_id, product_id, expected_date, sent_at.

## 8. Posting rules
Odoo posts journal entries automatically from:
- POS session closing;
- vendor bills;
- payments;
- stock valuation (automated AVCO);
- scrap.

The `l10n_pk` chart of accounts provides the accounts. Hisabkar adds no posting engine. It configures:
- POS payment-method journals;
- the khata receivable;
- a "Expiry write-off" expense account;
- a "Cash variance" account.
