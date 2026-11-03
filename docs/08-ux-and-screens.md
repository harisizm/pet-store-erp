# UX and Screens

> **Re-authored 2026-11-03** for Odoo 18 (ADR-0003). The original was lost in transit. This is
> the screen **inventory** and key flows. Visual design comes from `DESIGN.md` (task P0-4), and no
> screen is restyled before it exists (`AGENTS.md` §3).
>
> "Stock Odoo" means Odoo's own screen, restyled by `kitaab_theme` and simplified (fields hidden by
> group). "Custom" means a new view or OWL component.

## 1. POS (till) — hero surface, tablet-first
| Screen | Persona | Source | Requirements |
|---|---|---|---|
| PIN login | Cashier | Stock (`pos_hr`) | FR-ADM-006 |
| Open shift (opening float) | Cashier | Stock | FR-POS-012 |
| Sell: search/scan, cart, favourites grid | Cashier | Stock + `kitaab_pos` (shortcuts, Urdu search, loose qty keypad) | FR-POS-003, FR-CAT-009, FR-POS-016 |
| Lot picker with expiry, FEFO pre-selected | Cashier | Custom (`kitaab_pos_fefo`) | FR-INV-011/012 |
| Customer pick / quick-add | Cashier | Stock + phone validation | FR-POS-014 |
| Payment (split, change due, khata) | Cashier | Stock + credit-limit check | FR-POS-005/006 |
| Manager PIN override | Manager | Custom | FR-POS-004 |
| Receipt + WhatsApp share | Cashier | Stock receipt (Kitaab layout) + custom share | FR-POS-008/009 |
| Refund / exchange | Cashier | Stock refund + destination choice | FR-POS-010 |
| Collect khata | Cashier | Custom | FR-CUS-003 |
| Cash in/out, close shift by denomination | Cashier | Stock | FR-POS-012 |
| Offline / sync status badge | All | Custom | NFR-OBS-003 |

## 2. Owner on phone
| Screen | Source | Requirements |
|---|---|---|
| Dashboard: today/week/month sales, gross profit, bills, average bill, cash expected, khata outstanding, low-stock count, near-expiry value, top 10 items, sales by hour | Custom (`kitaab_reports`) | FR-RPT-001 |
| Khata list (oldest first) → statement → reminder | Custom | FR-CUS-004..006 |
| Near-expiry list (30/60/90) | Custom | FR-INV-013, FR-RPT-005 |
| Low stock → create PO | Stock replenishment, simplified | FR-INV-030 |

## 3. Back office (desktop)
| Area | Screens | Source |
|---|---|---|
| Catalog | Items list/form (simplified), import with template, barcode labels, price history | Stock + `kitaab_catalog` |
| Stock | On hand by branch/lot, counts (session, variance, approve), adjustments with reason, expiry write-off, negative-stock review | Stock + `kitaab_inventory` |
| Purchasing | Suppliers, PO, receive with lot/expiry, bills, payments, returns, payables aging | Stock + aging glue |
| Customers | Customer list with balance, statement, merge duplicates | Stock + `kitaab_khata` |
| Money | Expenses quick entry, cash book, bank/wallet journals | Custom + stock |
| Reports | Sales by day/item/category/brand/method/staff/customer, gross profit, stock valuation, slow movers, Z-report history, discounts/overrides, item card | `kitaab_reports` |
| Settings | Users and roles, cashier PINs, devices, branches, discount limits, negative-stock policy, cash rounding, receipt header/footer | Stock settings + `kitaab_settings` |

## 4. Key flows
Each flow is an HttpCase tour, as required by the DoD.

1. **Cash sale, 5 items, change due.** Target: unaided after 15 min of training (NFR-USE-001).
2. **Loose sale.** 2.5 kg cat food (US-POS-3).
3. **Khata sale.** Balance updates and shows on the receipt (US-POS-4).
4. **Refund against a receipt.** Cash, or credit to khata (US-POS-5).
5. **Sale while offline, then sync.** No duplicates (US-POS-2).
6. **Goods receipt.** Lots and expiry per line; supplier balance updates (US-PUR-1).
7. **Stock count.** By scanning, then approve (US-INV-3).
8. **Close shift and day.** Z-report.

## 5. Constraints every screen meets
- **Touch and contrast:** ≥ 44 px touch targets on the POS; WCAG AA (NFR-USE-004).
- **Languages:** English and Urdu, RTL verified (NFR-USE-002).
- **Numbers:** `Rs 12,500` formatting, with an optional lakh grouping (NFR-USE-003).
- **Speed:** the dashboard loads in under 2 s on 3G (NFR-PERF-004).
- **Reports:** every number drills down to its documents (PRD §5.3).
