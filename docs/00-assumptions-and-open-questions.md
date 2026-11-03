# Assumptions & Open Questions

Status legend: **DECIDED** (build on it) · **ASSUMED** (build on it, may change) · **OPEN** (needs founder decision)

## Business
| # | Item | Status |
|---|------|--------|
| B1 | First market: independent pet shops in Bank Square Market, Model Town, Lahore (~17–24 shops). Expansion: other Lahore pet markets, then other retail verticals. | DECIDED |
| B2 | Product is SaaS, billed monthly per branch. Hypothesis: PKR 2,000–3,500/branch/month, first month free, optional paid onboarding. | ASSUMED |
| B3 | Many target shops already have WooCommerce/Shopify websites; stock sync with those sites is a key differentiator. | ASSUMED (from research; verify per shop) |
| B4 | Founder sells and onboards in person; no self-serve signup in Phase 1. | ASSUMED |
| B5 | Product name **Hisabkar** (حسابکار, "the one who keeps the accounts"). Tagline: **"Your one place to manage your entire business."** It replaces the working name "Kitaab". Checked 2026-11-03: no existing product named Hisabkar was found. hisabkar.pk, .app, .co and .io show no DNS record (confirm at a registrar); hisabkar.com is registered. Same word family as the Pakistani competitors Hisaab.pk and HysabOne, so the visual identity must set it apart. Next steps: register a domain, and do a trademark search with IPO-Pakistan (`00` L4). | DECIDED 2026-11-03 (founder) |
| B7 | No trace of "Odoo" anywhere: hard fork with a scripted rebrand (ADR-0006). Only the legally required licence and copyright notices remain, in source and the legal-notices document. | DECIDED 2026-11-03 (founder) |
| B6 | Two deployment modes from one codebase: (a) **on-premise**, installed on a shop's own Windows PC and working without internet; (b) **cloud SaaS** in the browser for many shops. Founder, 2026-11-03. Refines B2. | DECIDED |

## Product
| # | Item | Status |
|---|------|--------|
| P1 | UI languages: English + Urdu (RTL). Default English, toggle per user. | DECIDED |
| P2 | Currency: PKR only in Phase 1. Multi-currency deferred. | DECIDED |
| P3 | Costing method: weighted average cost (WAC) per item per branch. | ASSUMED |
| P4 | Negative stock allowed at POS (configurable per tenant, default ON), flagged for review. Shops cannot stop a sale because data is wrong. | ASSUMED |
| P5 | Customer credit ("udhaar"/khata) is core, not optional. | DECIDED |
| P6 | Loose/repacked selling (e.g., cat food sold by kg from a 15 kg bag) is required. | ASSUMED (validate in field) |
| P7 | Live animal sales (kittens, puppies, birds) handled as serial-tracked items in the Pet pack. | ASSUMED |
| P8 | Tax: shops are likely not FBR Tier-1. Tax fields exist on documents from day one, but FBR POS integration is Phase 3 and optional. | ASSUMED |

## Technical
| # | Item | Status |
|---|------|--------|
| T1 | ~~Stack: TypeScript monorepo; NestJS API; PostgreSQL 16; Redis + BullMQ; Next.js admin web; React + Vite PWA for POS.~~ Superseded: Odoo 18 Community (Python, PostgreSQL, OWL) plus OCA modules and our `hisabkar_*` modules. | SUPERSEDED by ADR-0003 |
| T2 | POS must work offline for at least 72 hours (load-shedding, unstable internet). | DECIDED |
| T3 | Hosting region | OPEN (candidates: Singapore, Bahrain, Frankfurt; measure latency from Lahore) |
| T4 | Login: phone number + OTP for owners/managers; 4–6 digit PIN for cashiers on a registered device. | ASSUMED |
| T5 | SMS OTP provider | OPEN (local aggregator vs. Twilio; cost) |
| T6 | WhatsApp: Phase 1 uses `wa.me` share links (free, manual send). Phase 2 uses Meta WhatsApp Cloud API (paid, templates). | DECIDED |
| T7 | Receipt printing: browser print to 80 mm thermal printer in Phase 1; ESC/POS local bridge later if needed. | ASSUMED |
| T8 | The open-source base must run **natively on Windows**, with no WSL, Docker or Linux, for both development and on-premise installs. It must provide Urdu, free WhatsApp, free FBR integration, and FEFO batch selection at the POS bill. Founder, 2026-11-03. This rules out ERPNext (ADR-0002 superseded). | DECIDED → base is Odoo 18 Community (ADR-0003). SaaS server on a Linux cloud host; devs and shops on Windows. |

## Legal
| # | Item | Status |
|---|------|--------|
| L1 | Odoo trademark terms: Odoo's trademark page returned 404 on 2026-11-03, so the exact terms are unread. We comply by never showing the Odoo name or logo (`AGENTS.md` §1.14). A lawyer confirms before launch. | OPEN |
| L2 | Licence review of ADR-0004 (proprietary modules + AGPL glue), the EULA, and LGPL/AGPL source-offer duties for on-premise installs. Due before the first paid customer. | OPEN |
| L3 | Data privacy: zero egress to Odoo S.A. (ADR-0005, NFR-SEC-005). | DECIDED |
| L4 | "Hisabkar" trademark: search and register with the Intellectual Property Organisation of Pakistan (classes 9 and 42) before public launch; register a domain (hisabkar.pk / .app / .co / .io appear free). | OPEN (founder) |

## Conflicts found
_(Agents append here.)_

| # | Conflict | Status |
|---|---|---|
| C2 | FR-INV-003 asks for WAC per (branch, unit). Odoo's AVCO is per **company**, so every branch of a tenant shares one average cost. Decision: company-wide AVCO in Phase 1. Multi-branch operators who need per-branch cost get one company per branch in Phase 2. | DECIDED 2026-11-03 (founder) |
| C3 | FR-INV-031 specifies explicit `repack_out`/`repack_in` movements. In Odoo, stock is held in the base unit (kg): a bag bought as "Bag 15 kg" lands as 15 kg, and loose sales deduct kg directly, so no repack document is needed. Decision: no repack step. Stock is kept in the base unit; a sealed bag sells as 15 kg at the bag price, loose sells by kg. Sealed and opened bags are not tracked separately. | DECIDED 2026-11-03 (founder) |
| C4 | The POS works offline from IndexedDB, but reloading or reopening it offline needs its service worker. Browsers allow that only over HTTPS or on localhost. Tablets reaching the shop PC at `http://192.168.x.x` would lose offline reload. Decision: the on-premise installer creates a local CA and certificate. Each till trusts it at onboarding (about 2 min per device). Verified in spike P0-7. | DECIDED 2026-11-03 (founder) |
| C1 | 2026-11-03: the founder decided to build on an existing open-source ERP/POS instead of from scratch. This supersedes T1 / ADR-0001 (the NestJS + Drizzle + React stack) and `AGENTS.md` §2 tooling, pending the choice of base. The SRS requirements and the `AGENTS.md` §1 domain invariants still apply. Evaluation: `13-open-source-base-evaluation.md`. | DECIDED 2026-11-03: Odoo 18 Community (ADR-0003, evaluation `13` §8). ERPNext (ADR-0002) superseded by T8 and B6. |
