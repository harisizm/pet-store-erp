# ADR-0002: Build on ERPNext v16 + POS Awesome V15

- **Status:** accepted, conditional on the spike in `../13-open-source-base-evaluation.md` §5
- **Date:** 2026-11-03
- **Supersedes:** ADR-0001 stack choices (`../04-architecture.md` §2–3)
- **Requirements:** FR-POS-002, NFR-AVL-002, FR-INV-010/011, FR-CUS-002..005, FR-CAT-003,
  FR-INV-031, FR-ACC-001, FR-ADM-001, NFR-USE-002

## Context
The founder decided to extend a mature open-source ERP/POS rather than build from scratch (conflict
C1 in `00`). The evaluation in `13` measured 20+ candidates against the SRS. Only ERPNext covers
batches with FEFO, the khata/receivables ledger, pack→loose units, purchasing, branches,
double-entry accounting and multi-tenant sites out of the box. It also has open-source apps for
WhatsApp, Shopify, WooCommerce and FBR.

## Decision
- **Base:** ERPNext v16 on the Frappe framework.
- **POS:** POS Awesome V15 (`defendicon/POS-Awesome-V15`).
- **Kitaab features:**
  - live in our own Frappe apps (`kitaab_core`, `kitaab_pet`);
  - ERPNext and POS Awesome are not patched in place;
  - unavoidable patches are listed in `../upstream-patches.md`.
- **Tenancy:** one Frappe site per tenant.

**The decision holds only if the §5 spike passes:**
- 72 h offline with 500+ invoices, surviving reload and reboot, with no loss and no duplicates;
- a credible plan to full Urdu coverage on v16;
- acceptable cost per site.

**If the offline test fails:** keep ERPNext and build our own offline PWA POS against its REST API,
using the design in `../04-architecture.md` §6.

## Consequences
- **Stack:** Python/Frappe + MariaDB + Redis + Vue replaces the NestJS/Drizzle/React stack.
  `docs/AGENTS.md` §2 (tooling) must be rewritten for Frappe before feature work starts.
- **§1 invariants:** they survive, mapped onto ERPNext mechanisms:
  - the Stock Ledger as the stock ledger;
  - submitted documents immutable, with cancel and amend;
  - a site per tenant instead of RLS.
- **Main dependency risk:** offline selling hangs on a fork with essentially one maintainer. We may
  end up maintaining it ourselves.
- **Urdu:** must be carried forward from v15 and completed by us. Worth contributing upstream.
- **Upgrades:** ERPNext's annual major releases upgrade every site on a bench together. Plan an
  upgrade window per year.
- **Licences:** ERPNext and POS Awesome are GPL-3, so hosting them as SaaS creates no
  source-publication duty. Anything shipped to devices must come with source. The AGPL WooCommerce
  connector, if modified, must offer source to its users.
