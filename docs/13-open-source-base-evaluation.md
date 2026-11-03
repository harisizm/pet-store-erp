# Open-Source Base Evaluation

- **Status:** the founder chose the recommendation, ERPNext v16 + POS Awesome V15, on 2026-11-03.
  Recorded as `adr/0002`; conditional on the §5 spike.
- **Date:** 2026-11-03.
- **Method:** three parallel research passes: full ERP suites, standalone POS/inventory, and
  vertical/regional add-ons.
- **Measurements:** stars, push dates, releases and licences were read from the GitHub API on the
  date above, not recalled. Claims that could not be checked are listed in §7.

## 1. Answer
No open-source project fits Pakistani pet shops out of the box. Nothing production-grade exists for
pet retail, grooming or boarding in any ecosystem, so the pet pack is ours to build whatever base
we pick.

The best base is **ERPNext v16 (Frappe)** with the **POS Awesome V15** POS app, plus open-source
Frappe apps for WhatsApp, Shopify/WooCommerce and FBR. It is the only candidate that covers our core
retail requirements out of the box:
- batches with FEFO;
- the khata/receivables ledger;
- pack→loose units;
- purchasing and payables;
- branches;
- double-entry accounting;
- multi-tenant sites;
- labels and receipts.

Its weak points are exactly our two hardest requirements:
- **offline POS for 72 h** depends on a one-maintainer fork;
- **Urdu** was dropped from v16.

Both must pass a short spike (§5) before we commit.

## 2. Candidates measured

### Full ERP suites
| Repo | ★ | Last push | Latest | Licence | Stack |
|---|---|---|---|---|---|
| [frappe/erpnext](https://github.com/frappe/erpnext) | 40,879 | 2026-11-03 | v16.53.0 | GPL-3 (Frappe framework MIT) | Python, MariaDB, Vue |
| [defendicon/POS-Awesome-V15](https://github.com/defendicon/POS-Awesome-V15) | 117 | 2026-10-26 | 15.36.0 | GPL-3 | Vue/TS; ERPNext v15/v16 |
| [ucraft-com/POS-Awesome](https://github.com/ucraft-com/POS-Awesome) (original) | 518 | 2024-08-12 (stale) | n/a | GPL-3 | Vue |
| [odoo/odoo](https://github.com/odoo/odoo) | 55,506 | 2026-11-03 | 20.0 branch | LGPL-3 | Python, Postgres, OWL |
| [Dolibarr/dolibarr](https://github.com/Dolibarr/dolibarr) | 7,824 | 2026-11-03 | 24.0.2 | GPL-3 | PHP |
| [tryton/tryton](https://github.com/tryton/tryton) | 240 | 2026-11-02 | 8.0 | GPL-3 | Python |
| [idempiere/idempiere](https://github.com/idempiere/idempiere) | 675 | 2026-11-03 | n/a | GPL-2 | Java/OSGi |
| [apache/ofbiz-framework](https://github.com/apache/ofbiz-framework) | 1,148 | 2026-11-01 | 24.09.08 | Apache-2 | Java |
| [erxes/erxes](https://github.com/erxes/erxes) | 4,108 | 2026-11-03 | n/a | AGPL-3 + no-competing-SaaS rider | TypeScript |
| [akaunting/akaunting](https://github.com/akaunting/akaunting) | 10,271 | 2026-11-03 | 3.3.0 | BSL 1.1 | PHP/Laravel |

### Standalone POS / inventory
| Repo | ★ | Last push | Latest | Licence | Stack |
|---|---|---|---|---|---|
| [opensourcepos/opensourcepos](https://github.com/opensourcepos/opensourcepos) | 4,474 | 2026-11-02 | 3.4.3 | MIT + mandatory unmodifiable footer | PHP CI4, jQuery |
| [Blair2004/NexoPOS](https://github.com/Blair2004/NexoPOS) | 1,302 | 2026-11-02 | v6.3.0 | GPL-3 (paid add-ons) | Laravel, Vue |
| [inventree/InvenTree](https://github.com/inventree/InvenTree) | 7,800 | 2026-11-03 | 1.6.4 | MIT | Django, React |
| [lakasir/lakasir](https://github.com/lakasir/lakasir) | 917 | 2026-10-22 | 1.1.11 | GPL-3 | Laravel/Filament, Flutter |

### Excluded outright
| Project | Reason |
|---|---|
| Openbravo | Community Edition ended 2020; public repos withdrawn 2024 |
| Frappe Books | Archived 2026-10-02; successor is a 59★ rewrite on `develop` only |
| tngoman/Store-POS (1,052★) | No licence, so legally all rights reserved |
| uniCenta, Chromis | Java desktop apps; no web client, no tenancy |
| Akaunting | BSL forbids offering it as an accounting service |
| erxes | Licence rider forbids hosting it as competing SaaS |
| OpenVPMS | Clinic-only Java system, custom licence that requires a subscription; licence page 404 |
| Every "pet shop management system" repo | Student projects (best is 40★, 2020, no licence) |

## 3. Fit against the SRS
Key: Y = out of the box, P = partial or needs an add-on, N = absent.

| # | Requirement | ERPNext + POS Awesome | Odoo CE | Dolibarr | NexoPOS |
|---|---|---|---|---|---|
| 1 | Offline POS ≥ 72 h (FR-POS-002, NFR-AVL-002) | P: fork queues invoices offline; duration and reload survival unproven. Core offline POS dropped in v13. | P: open session keeps selling; a new session cannot open offline | N | N (paid Windows app, not PWA) |
| 2 | Batch + expiry, FEFO (FR-INV-010/011) | Y: batch sort by expiry, expired excluded | P: `product_expiry` FEFO removal; at-till FEFO unverified | P | P: expiry date only, no lots |
| 3 | Khata (FR-CUS-002..005) | Y: POS credit sale, AR aging, statements | P: aging needs OCA | P | P: customer account + credit limit |
| 4 | Pack→loose, decimal qty (FR-CAT-003, FR-INV-031) | Y: UoM conversions + Repack entry | Y | P | P: manual convert |
| 5 | GRN + payables (FR-PUR) | Y | Y | Y | P |
| 6 | Branches + transfers | Y | Y | Y | Paid add-on |
| 7 | Double-entry (FR-ACC-001) | Y | P: full reports need OCA | Y | P |
| 8 | Multi-tenant SaaS | Y: bench multi-site | Y: multi-DB | P: instance per tenant | N |
| 9 | Urdu + RTL (NFR-USE-002) | P: RTL works; `ur.po` about 56% in v15, **absent in v16** | P: RTL works; no Urdu at all | Y: `ur_PK`, RTL | N |
| 10 | WooCommerce/Shopify, WhatsApp | P: add-ons (§4) | P: paid apps; WhatsApp Enterprise-only | P | N |
| 11 | Labels + 80 mm receipts | Y | Y | P | Y (direct print paid) |
| 12 | Licence OK for modified SaaS | Y | Y | Y | Y (check paid add-on terms) |

## 4. Ecosystem add-ons (Frappe vs Odoo)
| Need | Frappe/ERPNext (open source) | Odoo |
|---|---|---|
| WhatsApp | [shridarpatil/frappe_whatsapp](https://github.com/shridarpatil/frappe_whatsapp) 495★ MIT; [frappe/whatsapp](https://github.com/frappe/whatsapp) 34★ MIT (official, new) | Enterprise-only module; [discuss_hub](https://github.com/discusshub/discuss_hub) 22★ AGPL |
| Shopify | [frappe/ecommerce_integrations](https://github.com/frappe/ecommerce_integrations) 211★ GPL-3 (official, no Woo) | Paid store apps |
| WooCommerce | [libracore/WooCommerceConnector](https://github.com/libracore/WooCommerceConnector) 113★ AGPL. [woocommerce_fusion](https://github.com/Starktail/woocommerce_fusion) 76★ has no licence file, so it is unusable. | OCA connector hollow on 14.0–18.0; paid apps $88–$613 |
| FBR (Phase 3) | [kodlyft/di](https://github.com/kodlyft/di) 9★ MIT, v16+; [ParaLogicTech/fbr_integration](https://github.com/ParaLogicTech/fbr_integration) 1★ GPL-3 | 43 store apps, mostly paid; core `l10n_pk` is accounting only |
| JazzCash/Easypaisa, couriers | None (build) | Paid store apps |
| Pet / grooming / boarding | None usable (build) | Paid third-party; Odoo's own vet module is Enterprise |

On Odoo, the Pakistan pieces mostly exist as paid apps licensed per database. That cost multiplies
in a multi-tenant SaaS. On Frappe, the pieces are open source, and the gaps are things we would
build anyway.

## 5. Recommendation and the gate before committing
**Base:** ERPNext v16 + POS Awesome V15. Kitaab work lives in our own Frappe apps:
- `kitaab_core`: khata UX, loose-sale UX, Urdu, Pakistani defaults;
- `kitaab_pet`: pets, live animals, grooming and boarding, restock reminders.

Integrate `frappe_whatsapp`, `ecommerce_integrations` and a WooCommerce connector, with `kodlyft/di`
for FBR later. Upstream stays unpatched (see `AGENTS.md` §0).

**Spike (about 3–5 days) with pass/fail criteria, run before any feature work:**

**Offline POS (POS Awesome V15 on v16):**
- Go offline for 72 h of simulated use.
- Ring up 500+ invoices, including batch items and a khata sale.
- Reload the browser and reboot the device mid-way.
- Reconnect.

*Pass:* zero lost invoices, zero duplicates, FEFO batches honoured or flagged, and a usable speed on
a 2 GB Android tablet.

**Urdu:**
- Carry the v15 `ur.po` forward onto v16.
- Measure coverage of the POS, stock and selling screens.
- Check the RTL layout of POS Awesome.

*Pass:* the plan to reach 100% coverage on Phase 1 screens is credible.

**Hosting:**
- Run one bench with 10 test sites on a 4 GB and an 8 GB VPS.
- Measure RAM, POS latency from Lahore, and cost per site against PKR 2,000–3,500/branch/month.

**Fallback if the offline test fails:** keep ERPNext as the back office and build our own offline
PWA POS. It would follow the design already in `04-architecture.md` §6: Dexie outbox, UUIDv7,
idempotent push, change-cursor pull. It would sync to ERPNext's REST API. More work, but the
offline design is already specified.

## 6. What changes if we adopt it
- The stack becomes Python/Frappe + MariaDB + Vue. ADR-0001 is superseded, and `docs/AGENTS.md` §2
  must be rewritten for Frappe:
  - bench;
  - custom apps;
  - DocTypes;
  - patches;
  - fixtures;
  - Frappe test runner.
- The §1 invariants map onto ERPNext's own mechanisms, which already work this way:
  - Currency fields with precision; integer paisa where we compute ourselves.
  - The Stock Ledger Entry table as the stock ledger.
  - Submitted documents immutable, with cancel and amend.
  - A site per tenant instead of RLS.
- Licences:
  - GPL-3 (ERPNext): hosting it as SaaS creates no obligation to publish our changes.
  - AGPL (libracore WooCommerce connector): if we modify it, we must offer its source to users.
  - Anything we ship to devices (an APK, or a bundled offline client) must come with source to
    whoever receives it.

## 7. Not verified
- No candidate has demonstrated multi-day offline selling, or survival across a reload, in docs or
  tests. The §5 spike exists for this reason.
- Odoo FEFO at the POS till.
- Performance of any candidate on a 2 GB Android tablet.
- Whether Urdu is enabled for v16 on Frappe's Crowdin.
- Feature claims of every paid Odoo App Store module (only listings read).
- G2/Reddit sentiment. Capterra shows ERPNext about 4.6 (139 reviews), Odoo 4.2 (about 1,300),
  Dolibarr 4.5 (106).
- Any Pakistani pet shop running any of these.
- Pakistan support exists: [Havenir](https://frappe.io/partners/pakistan/havenir-solutions-private-limited)
  (Lahore) is a listed Frappe partner.
