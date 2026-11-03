# Hisabkar ERP — Documentation Index

> **Hisabkar** (حسابکار, "the one who keeps the accounts"): *Your one place to manage your entire
> business.* Chosen by the founder on 2026-11-03 (`00` B5). It replaces the working name "Kitaab".

Hisabkar is a multi-tenant, offline-capable retail ERP for small and mid-size shops in Pakistan.
It has a **generic retail core** (catalog, inventory, POS, purchasing, customers/khata, suppliers,
expenses, accounting, reports) plus **vertical packs** that add industry features.
The first vertical pack is **Pet Retail** (pet shops, groomers, small vet pharmacies).

## Reading order (humans and agents)
1. `AGENTS.md`: rules every coding agent must follow. Read first.
2. `00-assumptions-and-open-questions.md`: what is decided vs. provisional.
3. `01-business-case.md`: why this exists, who pays, what success means.
4. `02-prd.md`: personas, scope, phases, user stories.
5. `03-srs.md`: numbered functional + non-functional requirements (source of truth for "what").
6. `04-architecture.md`: system design, stack, module boundaries, offline sync (source of truth for "how").
7. `05-data-model.md`: entities, columns, invariants.
8. `06-api-spec.md`: REST conventions, endpoints, sync protocol.
9. `07-integrations.md`: WhatsApp, WooCommerce, Shopify, couriers, payments, FBR.
10. `08-ux-and-screens.md`: screen inventory and key flows.
11. `09-security-and-compliance.md`
12. `10-testing-and-quality.md`
13. `11-roadmap-and-agent-tasks.md`: phased build plan broken into agent-sized tasks.
14. `12-glossary.md`
15. `13-open-source-base-evaluation.md`: which open-source ERP/POS we build on, and the spike that gates it.

## Precedence when documents conflict
`03-srs.md` > `05-data-model.md` > `04-architecture.md` > `06-api-spec.md` > others.
If a conflict is found, do not guess: log it in `00-assumptions-and-open-questions.md` under "Conflicts found".

## Requirement IDs
Every requirement has an ID like `FR-INV-012` or `NFR-PERF-003`. Code, tests, PRs and commits
must reference the IDs they implement.
