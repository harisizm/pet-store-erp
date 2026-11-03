# Open-Source Base Evaluation

- **Status:**
  - Round 1 (§1–7) chose ERPNext. That choice was superseded the same day: the founder then required
    a Windows-native base and both on-premise and SaaS deployment (`00` T8, B6).
  - **Round 2 is §8** and is the current evaluation. The founder chose Odoo 18 Community with a
    Linux cloud SaaS host on 2026-11-03 (ADR-0003).
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

---

## 8. Round 2: Windows-native bases (2026-11-03)

### 8.1 New constraints
These come from `00` B6 and T8.
- **Windows-native.** The base runs natively on Windows (no WSL, Docker or Linux) for developers
  and for shop installs.
- **Two deployment modes.** It ships as an on-premise install on a shop's Windows PC (offline) and
  as cloud SaaS.
- **Must-haves.** Urdu, free WhatsApp, free FBR integration, and FEFO batch selection at the POS
  bill.

Two consequences follow:
- **ERPNext is out:** it runs only on Linux.
- **On-premise solves offline.** With the server on the shop's own PC, losing the internet does not
  stop the till. The 72 h offline requirement only bites for SaaS shops.

### 8.2 The honest result
**No Windows-native open-source base has all four must-haves out of the box.** Each finalist needs
a defined amount of our own code on top.

| Must-have | Odoo 18 Community | Dolibarr 23 |
|---|---|---|
| Runs natively on Windows | **Y (with limits)**. The official installer bundles Python, PostgreSQL 16 and wkhtmltopdf and registers a Windows service. It runs as a single process with no workers and no memory cap; Odoo's docs call Windows fine for single-user/testing and discourage it for production. Fine for one shop's tills. | **Y**. The DoliWamp installer lags core by a major version (22.0.4 vs 23.0.4), so we would ship our own bundled installer. |
| Urdu | **N**. No `ur` language in core and no `ur.po` in any addon (17/18/19). RTL works in the POS through the RTL asset path, proven by Arabic users. We add the language and translate POS, stock, account and sale ourselves. | **Partial**. `ur_PK` 74.5% of 16,580 keys; TakePOS 68%; RTL set. Quality unchecked. |
| Free WhatsApp | **Y**: [OCA/social `mail_gateway_whatsapp`](https://github.com/OCA/social/tree/18.0/mail_gateway_whatsapp) 18.0, AGPL-3, updated 2026-10-26, Meta Cloud API. Meta still bills per template message. Plus `wa.me` links. | **N**. Only `wa.me` links, which we build. |
| Free FBR (POS fiscalisation) | **N free**. Free modules cover invoices only. POS fiscalisation exists as [`ol_pos_fbr_connector`](https://apps.odoo.com/apps/modules/18.0/ol_pos_fbr_connector), $78, LGPL-3, so we can buy once and fork. Or we write it. | **N**. We build it. |
| FEFO at the POS bill | **N in core**. The POS lists lots unsorted and auto-picks only when there is a single lot. OCA [`pos_product_expiry`](https://github.com/OCA/pos/tree/18.0/pos_product_expiry) blocks expired lots. FEFO suggestion is about 100 lines of our own code. | **Partial**. TakePOS already lists lots expiry-ascending; it needs auto-pick plus the expiry shown on screen (one patch). |
| Khata | **Partial**. POS credit sale and credit limit are in Community. Settling dues in the POS and the aged receivables report are Enterprise-only; OCA `account_financial_report` (free) covers aging. | **Partial**. Unpaid-bill limit and late-payment list; no aging buckets. |
| Loose / decimal UoM | Y | Y |
| Offline POS for SaaS shops | **Y**. Browser IndexedDB order queue. | **N**. Server-rendered POS. |
| Multi-shop SaaS | **Y**. Many databases with a db-filter per host. Must be hosted on a multi-process server (see §8.4). | **Partial**. SellYourSaas is Ubuntu-only; the `multicompany` module's price and licence are unverified. |
| Ecosystem | 55.5k★, LGPL-3 core (our modules can stay closed); OCA has hundreds of free modules | 7.8k★, GPL-3 |

**Others checked and rejected for Round 2:**
- **NexoPOS:** no Urdu, no lots.
- **OSPOS:** about 3% Urdu, no lots.
- **iDempiere:** FEFO in the engine and real multi-tenancy, but no maintained POS and no Urdu.
- **uniCenta and Chromis:** stale Java desktop apps.
- **Frappe Books:** archived.
- **Ever Gauzy:** a TypeScript project, but no retail features.
- **open-mercato:** needs WSL or Docker.
- **Store-POS:** no licence.

**There is no credible TypeScript base.**

### 8.3 Recommendation: Odoo 18 Community
Odoo is the only Windows-native base that already does the two things hardest to build ourselves:
- a POS that queues sales offline in the browser (needed for SaaS shops);
- multi-database SaaS.

It also has free WhatsApp, a free aging report, and a one-click Windows installer that runs as a
service, which is exactly the on-premise shop install.

Version 18 over 19 or 20: the OCA modules we need (`mail_gateway_whatsapp`, `pos_product_expiry`)
exist for 18.0. `mail_gateway_whatsapp` has no 19.0 branch.

**What we build, as our own Odoo modules (core stays unpatched):**

| Module | Covers | Size |
|---|---|---|
| `kitaab_l10n_ur` | `ur_PK` language (RTL); Urdu translations of POS, stock, account and sale | Large (translation), one-off; worth contributing upstream |
| `kitaab_pos_fefo` | Pre-select the earliest-expiry lot with stock, show the expiry on the line, Manager PIN for expired lots (FR-INV-011/012) | Small (about 100–300 lines) |
| `kitaab_khata` | Collect khata in the POS, statements, `wa.me` reminders (FR-CUS-002..006) | Medium |
| `kitaab_fbr_pos` | FBR POS fiscalisation, by forking `ol_pos_fbr_connector` (LGPL) or writing our own. Phase 3, optional (`00` P8). | Medium |
| `kitaab_pet` | Pets, live animals, grooming and boarding, restock reminders | Large (no base has it) |

### 8.4 Risks to accept
1. **Windows production limits.** One process, no workers, no memory cap. Right for one shop's
   tills; wrong for hosting many shops.
   - The SaaS server should run on Linux at a hosting provider. Nobody on the team or at the shops
     ever touches it; it is a cloud box like any website host.
   - If even that is unacceptable, SaaS on Windows Server means one Odoo service per handful of
     tenants behind IIS. It works, but scales worse.
2. **Urdu is entirely our own work** for the four big modules.
3. **Upgrade cadence.**
   - `odoo/odoo` already defaults to 20.0.
   - If Odoo keeps supporting only the three latest versions, 18 falls out of support around late
     2027 (inferred, not checked).
   - Plan one migration.
4. **Licences.**
   - OCA modules are AGPL-3. Shipping them to shops' PCs (on-premise) is distribution, so we offer
     their source.
   - Our own modules built on the LGPL core may stay closed.
5. **FBR** is a $78 purchase or a build. It is not free anywhere for POS.

### 8.5 Not verified
- Real Odoo-on-Windows small-shop deployments.
- Odoo's Weblate Urdu status (the page returned 403).
- Whether the free FBR listings download without a login.
- Paid vendors' FBR claims.
- Meta's current WhatsApp pricing.
- The price and licence of Dolibarr's `multicompany` module.
- TakePOS Urdu translation quality.
