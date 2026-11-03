# ADR-0004: Licensing — proprietary Kitaab modules, published AGPL glue

- **Status:** accepted (founder, 2026-11-03). **Needs legal review before first paid customer.**
- **Date:** 2026-11-03
- **Requirements:** `00` B6 (on-prem + SaaS)

## Context
Kitaab will modify the base heavily, host it as paid SaaS, and install it on shop PCs. The founder
asked to confirm this is legally safe.

**What was verified on 2026-11-03:**
- **Odoo 18 Community is LGPL-3.** `LICENSE` at the pinned commit says so, and so does
  [odoo.com/documentation/18.0/legal/licenses](https://www.odoo.com/documentation/18.0/legal/licenses.html).
  - We may modify it, host it as SaaS and sell installs, with no fee to Odoo S.A.
  - The licence for released 18.0 code cannot be revoked.
- **Odoo Enterprise is a separate product.** It uses OEEL-1: usable only with a subscription, and
  publishing or selling copies is forbidden. We use none of it.
- **The OCA modules we picked are AGPL-3.** This covers `mail_gateway_whatsapp`,
  `pos_product_expiry`, `account_financial_report`, `report_xlsx` and `auditlog`.
  `date_range` is LGPL-3.
- **The 2015 Odoo S.A. + OCA licence agreement**
  ([source](https://odoo-community.org/blog/news-1/post/oca-odoo-meeting-on-licenses-21)):
  - "any module must be compatible and respect the license of its dependencies".
  - A proprietary module cannot depend on an AGPLv3 module.
  - Proprietary and AGPLv3 modules may run together if neither depends on the other.
  - Odoo S.A. and the OCA will not pursue end users who follow these rules.

## Decision
- **Proprietary core.** Kitaab business modules are `'license': 'Other proprietary'` under our own
  EULA:
  - khata, FEFO, pet, Urdu, FBR, theme, privacy, and others like them;
  - they depend only on Odoo core (LGPL-3) and LGPL-compatible modules.
- **AGPL glue.** When a feature needs an OCA AGPL module, the code touching it goes in a separate
  thin module:
  - named `kitaab_<x>_oca`;
  - licensed `'license': 'AGPL-3'`, which pulls in the AGPL obligations below;
  - published in a public repo;
  - containing no business logic of ours beyond the wiring.
  - Proprietary modules never depend on glue modules.
- **No Enterprise code, ever.** That includes reading Enterprise source to reimplement it.

**Obligations we accept:**
- **LGPL (Odoo core), on-premise.** Shipping to shops is distribution.
  - Include the LGPL notice.
  - Offer the Odoo source we ship. It is unmodified, because we never patch `vendor/`.
  - Do not forbid the user from modifying or relinking the LGPL part.
- **AGPL (OCA and glue modules), on-premise and SaaS.** Offer their source, including our
  modifications, to every user. A public repo link in the about dialog and the EULA satisfies this.
- **Third-party components in the on-premise installer.** PostgreSQL (PostgreSQL licence), Python
  (PSF), wkhtmltopdf (LGPL-3) and nssm (public domain): ship their licence notices.

## Consequences
- Business logic stays closed, and competitors cannot legally reuse it.
- Some features need two modules: a proprietary one, plus an AGPL glue module.
- `dod-reviewer` checks that no proprietary module depends on AGPL.
- **On-premise exposes our Python source on shop PCs.** Odoo modules ship as source, and obfuscation
  is weak. Protection is contractual (EULA: no copying, no redistribution), not technical.
- **Open: trademark.** Odoo's trademark page returned 404 at two URLs on 2026-11-03, so we could not
  read its exact terms. We comply by never using the Odoo name or logo user-facing (`docs/AGENTS.md`
  §1.14). A lawyer confirms before launch (`00` L1).
- **Open: legal review.** A licence lawyer reviews this ADR, the EULA and the glue-module pattern
  before the first paid customer (`00` L2). This ADR is engineering diligence, not legal advice.
