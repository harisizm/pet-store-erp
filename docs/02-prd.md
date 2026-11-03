# Product Requirements Document (PRD)

## 1. Vision
"The register, the stock room and the website, in one book." A shop owner can see today's sales,
what's running low, what's expiring, and who owes money, from their phone.

## 2. Personas
### P-OWN: Owner (e.g., Zaryab, 32)
Runs one or two shops, handles purchasing and suppliers, often at the counter in the evening.
Uses WhatsApp all day, comfortable with Android, reads English and Urdu.
**Goals:** daily cash and profit, stock control, udhaar recovery, less staff theft.
**Pain:** no numbers; discovers stockouts late; disputes with credit customers.

### P-CSH: Cashier / sales staff (e.g., Basit, 22)
Bills customers, packs online orders, answers WhatsApp.
**Goals:** bill fast; not be blamed for mismatches.
**Pain:** writing bills by hand; checking stock means walking to the back.

### P-GRM: Groomer
**Goals:** know the day's appointments, record services done (for billing and commission).

### P-MSO: Multi-shop operator
**Goals:** consolidated sales and stock; move stock between shops.

### P-ACC: Accountant (part-time, optional)
**Goals:** ledgers, expenses, exportable reports.

## 3. Scope by phase
### Phase 1: MVP ("retire the register")
- Tenant, branch, user, role and device setup.
- Catalog: items, variants, units and conversions, barcodes, categories, brands, prices, Excel import.
- Inventory: stock ledger, batches + expiry, FEFO, adjustments, stock count, low-stock and near-expiry alerts.
- POS (offline): cart, barcode/search, discounts, multiple payment methods, split payment, credit (khata) sale, hold/resume, returns/exchanges, receipt print, WhatsApp receipt link.
- Cash management: shift open/close, cash in/out, day close (Z-report).
- Customers: profile, khata ledger, payments received, statement, WhatsApp reminder (link).
- Suppliers & purchasing: supplier ledger, purchase order (optional), goods receipt with batch/expiry, purchase bill, supplier payment, purchase return.
- Expenses: categories, recording, attachments.
- Reports: sales (day/item/category/staff), profit (gross), stock on hand and valuation, near-expiry, low stock, khata aging, supplier payables, cash book.
- Audit log.

### Phase 2: "Connect the channels" + Pet pack
- WooCommerce and Shopify connectors: product link, two-way stock sync, order import into an Orders inbox.
- Online/WhatsApp order management: order statuses, pick/pack, delivery assignment, COD tracking.
- WhatsApp Cloud API: automated receipts, khata reminders, restock reminders, order updates (opt-in).
- Pet pack: customer pets, live-animal inventory with health records, grooming/boarding appointments with service billing, restock reminder engine.
- Multi-branch: stock transfers, consolidated dashboards, branch-level pricing.
- Double-entry accounting UI (journal, trial balance, P&L, balance sheet). Posting engine exists from Phase 1.
- Loyalty points (simple).

### Phase 3: Scale
- Courier integrations (PostEx, Leopards, TCS, Trax) with COD reconciliation.
- Payment links/QR (Raast/JazzCash/Easypaisa) where APIs are accessible.
- FBR POS integration (opt-in, for Tier-1 tenants).
- Native mobile owner app (or polished PWA).
- Self-serve signup and billing.
- Additional vertical packs (pharmacy, grocery/kiryana, apparel).

### Explicitly out of scope (all phases unless revisited)
Payroll/HR beyond staff commission; manufacturing/BOM beyond simple repacking; full warehouse
management; marketplace (Daraz) integration (revisit Phase 3).

## 4. Key user stories (Phase 1)
Format: `US-<area>-<n>`, with acceptance criteria in SRS.

- **US-POS-1** As a cashier, I scan a barcode or type 2–3 letters of a product name and add it to the bill in under 2 seconds.
- **US-POS-2** As a cashier, I can complete a sale with no internet, and it syncs later without duplicates.
- **US-POS-3** As a cashier, I can sell 2.5 kg of loose cat food from an open bag.
- **US-POS-4** As a cashier, I can put a sale on a customer's khata, and their balance updates.
- **US-POS-5** As a cashier, I can process a return against a past receipt and refund cash or credit the khata.
- **US-POS-6** As a cashier, I can send the receipt to the customer's WhatsApp in one tap.
- **US-INV-1** As an owner, I see items expiring in the next 30/60/90 days with value at cost.
- **US-INV-2** As an owner, I see items below reorder level and create a purchase order from them.
- **US-INV-3** As staff, I perform a stock count by scanning items; the system shows variances and posts an adjustment on approval.
- **US-PUR-1** As an owner, I record goods received from a distributor with batch and expiry per line, and the supplier balance updates.
- **US-CUS-1** As an owner, I see all customers with outstanding balances, oldest first, and send a reminder.
- **US-RPT-1** As an owner, I see today's sales, gross profit, cash expected in drawer, and top items on my phone.
- **US-ADM-1** As an owner, I add a cashier with a PIN and restrict them from giving discounts above 5%.
- **US-ONB-1** As the founder onboarding a shop, I import 500 items from an Excel template and print barcode labels for items that lack barcodes.

## 5. UX principles
1. POS first: the most-used screen must be the fastest and simplest.
2. Big touch targets; works on a 10" Android tablet, a cheap Windows PC with Chrome, and a phone.
3. Every number on a report is drillable to the documents behind it.
4. Never block a sale because of bad data. Allow it, flag it, fix it later.
5. Urdu labels are first-class, not an afterthought.
