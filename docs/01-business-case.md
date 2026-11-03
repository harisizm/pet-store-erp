# Business Case

## 1. Problem
Independent retail shops in Pakistan, starting with the ~17–24 pet shops in Bank Square Market, Model Town, Lahore, run on paper:

1. **Sales are written by hand in a register.** No reliable daily total, no profit figure, no product-level history.
2. **Stock is unknown.** Owners discover stockouts when a customer asks. Several shops take advance payment, then find the item out of stock.
3. **Expiry is unmanaged.** Pet food, milk replacers, medicines and supplements expire. Public reviews of local shops mention customers receiving expired products. This is reputational and health risk.
4. **Channels are disconnected.** Many shops sell over the counter, on WhatsApp, on Instagram/Facebook, and on their own WooCommerce/Shopify site. Each channel has its own stock picture, or none. Online orders get lost or delayed, which also shows up in reviews.
5. **Credit (udhaar) is tracked in notebooks.** Regular customers and vets buy on credit; balances are disputed or forgotten.
6. **Supplier payables are untracked.** Shops buy from distributors on credit and lose track of what's owed.
7. **No repeat-purchase engine.** Pet food is a monthly repeat purchase, yet no shop reminds customers to restock.
8. **Multi-shop owners have no consolidated view.** Some operators appear to run more than one shop or brand in the same market.

## 2. Solution
A simple, Urdu/English, offline-first ERP that a cashier can learn in one hour:

| Problem | Kitaab capability |
|---|---|
| Hand-written register | Fast POS with barcode or search, receipts, day close (Z-report) |
| Unknown stock | Real-time stock ledger, low-stock alerts, purchase suggestions |
| Expiry | Batch + expiry tracking, FEFO selling, near-expiry alerts and reports |
| Disconnected channels | One stock count synced to WooCommerce/Shopify; WhatsApp order capture |
| Udhaar notebooks | Customer khata with balances, statements, WhatsApp payment reminders |
| Supplier payables | Supplier ledger, purchase bills, payment tracking |
| No repeat engine | Restock reminders based on purchase interval (Pet pack) |
| Multiple shops | Multi-branch with consolidated reports and stock transfers |

Pet-pack extras: customer pet profiles, live-animal records (vaccination, deworming, health notes),
grooming/boarding appointments.

## 3. Why now / why us
- Shops already invested in websites, so they are digitally willing, but the back office is paper.
- Generic Pakistani POS tools exist at PKR 500–3,000/month, but they are not built around expiry-heavy, repeat-purchase, live-animal, service-plus-retail pet businesses.
- Founder is physically present in the market. In-person onboarding and trust beats cold SaaS.

## 4. Competitive landscape (verify before pitching)
| Type | Examples | Weakness we exploit |
|---|---|---|
| Local cloud POS | Hulm, Mint POS, Granet Pro, Sum Cloud POS, Oscar, Howmuch POS, EloERP | Generic; no pet workflows; weak WooCommerce/Shopify stock sync |
| Global POS | Loyverse, Square, Lightspeed, Zoho | USD pricing, no Urdu, no khata, poor local payment/courier support |
| Spreadsheets / registers | Status quo | Everything above |

## 5. Target customers and personas (summary; detail in PRD)
- **Owner** (often also the main salesperson): wants daily cash, profit, and who owes what.
- **Cashier/staff**: wants fast billing and no blame for stock mismatches.
- **Groomer**: wants an appointment list.
- **Multi-shop operator**: wants consolidated numbers and transfers.

## 6. Revenue model (hypothesis)
- Subscription per branch: Basic (POS + inventory + khata) and Pro (+ e-commerce sync, WhatsApp automation, Pet pack, multi-branch).
- Paid onboarding: item list import, barcode labelling, staff training.
- Hardware resale (optional): thermal printer, barcode scanner, label printer.
- WhatsApp Cloud API message costs passed through or bundled.

## 7. Success metrics
**Pilot (first 3 shops, 60 days)**
- Register retired: ≥ 90% of sales entered in Kitaab by day 30.
- Daily active use: POS used on ≥ 26 of 30 days.
- Stock accuracy: physical count vs system within 5% of SKUs by day 45.
- Owner opens daily report ≥ 4 days/week.
- At least 1 pilot converts to paid.

**Business (12 months)**
- 15+ paying branches in Bank Square; 40+ across Lahore.
- Monthly logo churn < 3%.

## 8. Key risks
| Risk | Mitigation |
|---|---|
| Staff won't switch from register | 1-hour training, Urdu UI, fast POS, keep the register in parallel for 2 weeks |
| Internet/power outages | Offline POS (NFR-AVL-002) |
| Low willingness to pay | Lead with visible money wins: expiry losses avoided, udhaar recovered, restock reminders |
| Data entry burden at onboarding | Excel import, bulk barcode printing, founder-assisted setup |
| Tax fear ("software tells FBR my sales") | Clear data-ownership policy; FBR integration only on explicit opt-in |
| Competing on price | Compete on vertical fit and in-person support, not price |
