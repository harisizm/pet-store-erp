# Architecture Decision Records

One file per decision: `NNNN-kebab-title.md`, copied from `0000-template.md`. Numbers are never reused.

| ADR | Title | Status |
|---|---|---|
| 0001 | Technology choices | superseded by 0002 (recorded inline in `../04-architecture.md` §2) |
| 0002 | Build on ERPNext v16 + POS Awesome V15 | superseded by 0003 (needs a Windows-native base, `../00` T8) |
| 0003 | Build on Odoo 18 Community | accepted |
| 0004 | Licensing: proprietary Kitaab modules, published AGPL glue | accepted, legal review pending |
| 0005 | Zero egress: no data to Odoo S.A. or unlisted third parties | accepted |
| 0006 | Hard fork of the core with a scripted, repeatable rebrand | accepted; runs once the name is chosen |

Pending ADRs already called for by the docs:
- Urdu font: Noto Nastaliq Urdu vs Noto Naskh Arabic for dense UI (NFR-USE-002).
- Hosting region (00 T3) and SMS OTP provider (00 T5), once the founder decides.
