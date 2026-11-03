# Glossary

> **Re-authored 2026-11-03.** The original was lost in transit.

## Business terms
| Term | Meaning |
|---|---|
| **Khata** | Customer credit ledger. In Kitaab, the partner's receivable lines. |
| **Udhaar** | Buying on credit, "on the khata". |
| **Kiryana** | Neighbourhood grocery shop (a future vertical). |
| **FEFO** | First-Expiry-First-Out: sell the batch that expires soonest. |
| **WAC / AVCO** | Weighted average cost. Odoo calls it AVCO and computes it per company (`00` C2). |
| **GRN** | Goods receipt note: recording stock received from a supplier, with batch and expiry. |
| **Z-report** | End-of-day report of sales by payment method, returns, discounts and cash variance. |
| **Loose sale** | Selling part of a pack, e.g. 2.5 kg from a 15 kg bag. |
| **COD** | Cash on delivery. |
| **FBR** | Federal Board of Revenue (Pakistan tax authority). "FBR POS integration" fiscalises each sale. |
| **NTN / STRN** | National Tax Number / Sales Tax Registration Number. |
| **Tier-1 retailer** | FBR category obliged to integrate POS with FBR. |
| **Raast** | State Bank of Pakistan's instant payment system. |
| **JazzCash / Easypaisa** | Mobile wallets. |
| **E.164** | International phone format, e.g. `+923001234567`. |

## Odoo terms
| Term | Meaning |
|---|---|
| **Odoo CE / EE** | Community Edition (LGPL-3, what we use) / Enterprise Edition (proprietary, never used). |
| **OCA** | Odoo Community Association: publishes free modules, mostly AGPL-3. |
| **Module / addon** | Unit of Odoo functionality with a `__manifest__.py`. Kitaab's are `kitaab_*`. |
| **Glue module** | A thin AGPL module (`kitaab_*_oca`) that connects us to an OCA AGPL module (ADR-0004). |
| **IAP** | Odoo's paid in-app services that call `iap.odoo.com`. Excluded (ADR-0005). |
| **Publisher warranty** | Odoo's daily usage report to `services.odoo.com`. Neutralised (ADR-0005). |
| **Egress guard** | `kitaab_privacy`'s block on all outbound connections not on the allowlist. |
| **`pos.config` / `pos.session` / `pos.order`** | Till / shift / sale. |
| **`stock.move` / `stock.quant` / `stock.lot`** | Stock ledger entry / cached balance / batch or serial. |
| **`account.move`** | Journal entry, invoice or bill. Posted ones are immutable. |
| **Record rule** | Row-level access rule; used for branch isolation. |
| **Tour** | Scripted UI test run in a real browser (HttpCase). |
| **`dbfilter`** | Odoo setting that maps a hostname to a tenant database (SaaS). |
