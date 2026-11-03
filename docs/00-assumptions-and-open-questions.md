# Assumptions & Open Questions

Status legend: **DECIDED** (build on it) · **ASSUMED** (build on it, may change) · **OPEN** (needs founder decision)

## Business
| # | Item | Status |
|---|------|--------|
| B1 | First market: independent pet shops in Bank Square Market, Model Town, Lahore (~17–24 shops). Expansion: other Lahore pet markets, then other retail verticals. | DECIDED |
| B2 | Product is SaaS, billed monthly per branch. Hypothesis: PKR 2,000–3,500/branch/month, first month free, optional paid onboarding. | ASSUMED |
| B3 | Many target shops already have WooCommerce/Shopify websites; stock sync with those sites is a key differentiator. | ASSUMED (from research; verify per shop) |
| B4 | Founder sells and onboards in person; no self-serve signup in Phase 1. | ASSUMED |
| B5 | Product name | OPEN |

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
| T1 | Stack: TypeScript monorepo; NestJS API; PostgreSQL 16; Redis + BullMQ; Next.js admin web; React + Vite PWA for POS. | DECIDED (see ADR-0001 in 04-architecture) |
| T2 | POS must work offline for at least 72 hours (load-shedding, unstable internet). | DECIDED |
| T3 | Hosting region | OPEN (candidates: Singapore, Bahrain, Frankfurt; measure latency from Lahore) |
| T4 | Login: phone number + OTP for owners/managers; 4–6 digit PIN for cashiers on a registered device. | ASSUMED |
| T5 | SMS OTP provider | OPEN (local aggregator vs. Twilio; cost) |
| T6 | WhatsApp: Phase 1 uses `wa.me` share links (free, manual send). Phase 2 uses Meta WhatsApp Cloud API (paid, templates). | DECIDED |
| T7 | Receipt printing: browser print to 80 mm thermal printer in Phase 1; ESC/POS local bridge later if needed. | ASSUMED |

## Conflicts found
_(Agents append here.)_

| # | Conflict | Status |
|---|---|---|
| C1 | 2026-11-03: the founder decided to build on an existing open-source ERP/POS instead of from scratch. This supersedes T1 / ADR-0001 (the NestJS + Drizzle + React stack) and `AGENTS.md` §2 tooling, pending the choice of base. The SRS requirements and the `AGENTS.md` §1 domain invariants still apply. Evaluation: `13-open-source-base-evaluation.md`. | OPEN (base not chosen) |
