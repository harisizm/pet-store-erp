# ADR-0005: Zero egress — no data to Odoo S.A. or any unlisted third party

- **Status:** accepted (founder, 2026-11-03: "I don't want any data to be sent to them; our software
  will be used by high-value businesses")
- **Date:** 2026-11-03
- **Requirements:** NFR-SEC-005, NFR-SEC-006, NFR-SEC-007 (`03-srs.md`)

## Context
An audit of the pinned Odoo 18.0 code (`vendor/odoo`, 2026-11-03) found these outbound data flows.

**To Odoo S.A.**

| Flow | Where | What leaves | Default |
|---|---|---|---|
| Publisher-warranty "update notification" | `mail/models/update.py:72-74`; cron in `mail/data/ir_cron_data.xml`; URL `http://services.odoo.com/publisher-warranty/` (`odoo/tools/config.py:78`) | Database UUID, `web.base.url`, user counts, installed apps and more | **On, daily** |
| IAP (in-app purchase services) | `iap/tools/iap_tools.py:16,97,129` → `https://iap.odoo.com` | Varies by service | `iap` **auto-installs** |
| SMS, snail mail, partner autocomplete | `sms`, `snailmail`, `snailmail_account`, `partner_autocomplete`, `pos_sms`, `stock_sms`, `sale_sms` | Phone numbers, message bodies, documents, company names | All **auto-install** with what we use |
| Media library | `html_editor/controllers/main.py:469-476` → `media-api.odoo.com`; `web_unsplash` | Search terms, database identifiers | `web_unsplash` **auto-installs** |

**To other third parties**

| Destination | Where | Trigger |
|---|---|---|
| Gravatar | `base/models/res_partner.py:982-984` | Partner email avatar lookup |
| Link previews | `mail/tools/link_preview.py:33` | Any URL pasted in chatter |
| GIF search (`api.klipy.com`) | `mail/controllers/discuss/gif.py` | Only if configured |
| Google Translate, Twilio, SFU | `mail/controllers/google_translate.py`, `mail/models/mail_ice_server.py`, `mail/models/discuss/*` | Only if configured |
| Webhooks, URL imports, remote images | `base/models/ir_actions.py:875`, `base_import`, `web_editor/models/ir_qweb_fields.py:528` | Only if a user sets them up |

Everything else that matched `odoo.com` in the audit (about 230 hits) is a help or upgrade
hyperlink. A link sends nothing unless someone clicks it, and we remove the user-facing ones anyway
(debranding).

None of the modules Hisabkar needs hard-depends on the IAP family. That was checked by computing the
dependency closure of `point_of_sale`, `stock`, `account`, `sale`, `purchase`, `product_expiry`,
`mail`, `contacts`, `l10n_pk` and `phone_validation`. So the whole family can be removed.

## Decision
The default is **zero egress**. Data leaves only through integrations the shop has explicitly
enabled, each one on an allowlist. Five layers enforce it, so that no single mistake leaks.

1. **Module layer (`hisabkar_privacy`).**
   - At the end of every install or update pass, uninstall the blocked modules:
     - `iap`, `iap_mail`, `sms`, `snailmail`, `snailmail_account`, `partner_autocomplete`,
       `web_unsplash`, `pos_sms`, `stock_sms`, `sale_sms`;
     - `account_edi_proxy_client`, `account_peppol` and `iap_crm`, which talk to vendor proxies;
     - any module whose name matches `*_iap*`.
   - Set `auto_install = False` on them, re-applied after every module-list refresh, so upstream's
     auto-install loop never selects them.
   - Refuse explicit installs of them (`ir.module.module` overrides).
2. **Code layer (`hisabkar_privacy`).**
   - Neutralise `publisher_warranty.contract`: no-op methods, cron deactivated.
   - Disable Gravatar lookups.
   - Disable link previews everywhere: chatter, the `/mail/link_preview` route, the html editor's
     `/html_editor/link_preview_*` routes, and the client flag.
   - Install a process-wide **egress guard**, the only sanctioned monkey-patch. It is installed when
     the module's Python package is imported, which happens at server start because the module is
     in `server_wide_modules`.
     - It wraps outbound connections at the socket level.
     - It turns HTTP proxies off (`NO_PROXY=*`), so a proxy cannot hide the real destination.
     - Allowed: loopback, the `smtp_server` from the config file, and hosts listed in
       `hisabkar_egress_allowlist`. A mail relay configured only in the UI (`ir.mail_server`) must
       also be allowlisted.
     - `*.odoo.com` is **always** denied, even if allowlisted.
     - Every blocked attempt is logged with its caller and raises a clear error.
     - Limits: lookups through `gethostbyname`, UDP `sendto`, and code outside Python sockets are not
       covered. Layer 5 covers them.
3. **Config layer.** `scripts/setup-dev.ps1` and the production and on-premise configs set
   `publisher_warranty_url` to an unroutable local address. SaaS also sets `list_db = False`.
4. **Browser layer.**
   - `hisabkar_privacy` sends a Content-Security-Policy on every page and error page:
     - `default-src 'self'`;
     - `img-src` and `connect-src` limited to `'self'`, `data:`, `blob:` and our own websocket.
   - A stricter upstream policy, such as `default-src 'none'` on file downloads, is never loosened.
   - Violations are reported to our own server (`/hisabkar/csp-report`) and logged; nothing goes to
     a third party.
   - The web client and POS therefore cannot fetch from Odoo, Gravatar, Unsplash, YouTube or CDNs.
   - Fonts and assets are self-hosted.
   - Routes served without a database (the database manager) carry no policy; production sets
     `list_db = False`, which closes them.
5. **Network layer.**
   - **SaaS (Linux cloud host):** a default-deny egress firewall with an explicit allowlist (Meta
     WhatsApp API, FBR, the shop's WooCommerce/Shopify hosts, SMTP relay), plus a DNS sinkhole for
     `odoo.com`.
   - **On-premise (Windows):** the installer adds hosts-file sinkhole entries for every Odoo
     hostname found in the audit, and an outbound Windows Firewall block for the Odoo service
     except the allowlist.

**Proof:**
- An automated test (`hisabkar_privacy/tests/test_zero_egress.py`) installs every `hisabkar_*` module,
  triggers every `ir.cron` job and the known flows above, and asserts the guard saw zero
  non-allowlisted connection attempts. It runs in CI and is part of the DoD (`docs/AGENTS.md` §3).
- Release check: run the on-premise build for 24 h under network capture (Windows Resource Monitor
  or `pktmon`) and record zero connections outside the allowlist.

## Consequences
- Odoo's SMS, snail mail, partner autocomplete and stock-photo features are unavailable. WhatsApp
  comes through the OCA Meta Cloud API module instead, allowlisted per shop.
- **Collateral blocking.** These modules depend on a blocked one, so they cannot be installed:
  - `base_automation` (automation rules; depends on `sms`);
  - `hr_presence`;
  - `l10n_in*` and `l10n_it_edi*`;
  - OCA `report_label`.

  None is in our Phase 1 set. If one becomes necessary, it needs an ADR, either a glue module
  that drops the dependency or a reviewed exception.
- **Module-store downloads.** `base_import_module` (auto-installed) can fetch apps from
  `apps.odoo.com`; the guard's deny-list blocks it. Our modules are deployed from our own repos.
- **Recorded exception: `auto_install: True` on `hisabkar_privacy`.** It must be on every database.
  Auto-install does not fire on a database whose dependencies were installed earlier, so
  installers and setup scripts install it explicitly as well. Because it is server-wide, it
  cannot be uninstalled from the UI.
- **POS hardware.** `connect-src` stops the browser from calling LAN hardware directly (Epson ePOS
  printers, the IoT hardware proxy). Printing goes through the OS print dialog (NFR-CMP-002). A
  network printer integration would need that printer's address added to the policy.
- Every new integration costs an allowlist entry, a test and a line in `docs/09` describing what
  leaves.
- Upstream upgrades must rerun the egress audit (grep plus test), because new Odoo versions may add
  new calls.
- The guard is a monkey-patch, which is a maintenance point on each Python/Odoo upgrade. It is
  covered by its own tests.
