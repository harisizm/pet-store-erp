# Security and Compliance

> **Re-authored 2026-11-03** for Odoo 18 (ADR-0003, ADR-0004, ADR-0005). The original was lost in
> transit.

## 1. Deployment profiles
| | On-premise (shop's Windows PC) | SaaS (Linux cloud host) |
|---|---|---|
| Odoo process | Windows service (nssm) under a dedicated low-privilege account; threaded server | Multi-worker (`workers > 0`) behind a reverse proxy (`proxy_mode = True`) |
| Databases | One, for the shop | One per tenant; `dbfilter = ^%d$` (subdomain); `list_db = False` |
| TLS | Local CA + certificate per install, trusted on each till (needed for POS offline reload, `00` C4) | Public certificate; TLS 1.2+, HSTS (NFR-SEC-001) |
| Network exposure | Bound to the shop LAN only; no inbound from the internet | Only 443 inbound; DB not publicly reachable |
| Master password (`admin_passwd`) | Random per install, stored by the founder's team | Random, in the secret store |
| Egress | Hosts-file sinkhole for Odoo hosts + Windows Firewall outbound block except allowlist (ADR-0005) | Default-deny egress firewall + allowlist; DNS sinkhole for `odoo.com` |
| Backups | Nightly `pg_dump` + filestore copy to an external drive; optional encrypted upload to our backup bucket (allowlisted) | WAL archiving / PITR 7 days, daily snapshots 30 days, monthly restore test (NFR-DAT-001/002) |

## 2. Identity and access
- **Back-office login:** Odoo users with `auth_totp` 2FA required for Owner/Manager/Accountant.
  Phone + OTP is OPEN (`00` T5) and must not use Odoo's IAP SMS.
- **Cashiers:** `pos_hr` employee PIN on a registered device (`kitaab.pos.device`). Five failures
  lock that employee on that device for 5 minutes (FR-ADM-006). A device can be revoked remotely
  (NFR-SEC-004).
- **Permissions:** the SRS §12 matrix is implemented as `kitaab_*` groups. Branch isolation uses
  record rules on warehouse, POS config, session, order and picking, each with a test.
- **Integration users:** a dedicated user per integration with minimal groups and an API key. No
  shared admin credentials.

## 3. Zero egress: no data to Odoo S.A. (NFR-SEC-005..007)
Full design and audit evidence: ADR-0005. Summary:
1. **Module layer.** `kitaab_privacy` removes `iap`, `iap_mail`, `sms`, `snailmail*`,
   `partner_autocomplete`, `web_unsplash` and `*_sms`, and blocks their reinstall.
2. **Code layer.** The publisher-warranty call is neutralised. Gravatar and link previews are off.
   A socket-level egress guard denies all non-allowlisted hosts and always denies `*.odoo.com`.
3. **Config layer.** `publisher_warranty_url = http://127.0.0.1:9/` in every config.
4. **Browser layer.** A strict Content-Security-Policy; all fonts and assets are self-hosted.
5. **Network layer.** Firewall and DNS, per profile (§1).
6. **Proof.** The `test_zero_egress` test in CI; a 24 h capture on each release candidate.

## 4. Data inventory: what may leave, and to whom
| Data | Leaves to | When | Basis |
|---|---|---|---|
| Nothing | Odoo S.A. | Never | NFR-SEC-005 |
| Customer phone + message parameters | Meta (WhatsApp Cloud API) | P2, only for opted-in customers (`kitaab_wa_opt_in`) | FR-CUS-001/006 |
| Email address + PDF | Deployment SMTP relay | Statements and digests | FR-CUS-004, FR-RPT-013 |
| SKU + stock qty; orders in | The shop's own WooCommerce/Shopify | P2, when a channel is connected | FR-ORD-006 |
| Consignee details, COD | Courier | P3, per shipment | FR-ORD-004 |
| Invoice data, NTN | FBR | P3, only if the tenant opts in | `00` P8 |
| Encrypted backup | Our backup bucket | On-premise, optional, opt-in | NFR-DAT-001 |

Tenant data export (CSV/JSON zip) is available on request within 24 h (NFR-DAT-003). Logs carry
`db`, `uid` and request ids, and no customer PII beyond ids (NFR-OBS-001).

## 5. Licensing compliance (ADR-0004)
- **Our modules:** business modules are `Other proprietary` and depend only on LGPL core. AGPL glue
  modules (`kitaab_*_oca`) are published.
- **On-premise installers ship:**
  - the LGPL notice and an offer of the (unmodified) Odoo source;
  - the AGPL source offer for OCA and glue modules;
  - licence notices for PostgreSQL, Python, wkhtmltopdf and nssm;
  - our EULA.
- **Branding:** nothing user-facing says "Odoo" (`docs/AGENTS.md` §1.14).
- **Open items:** trademark terms unread (`00` L1); legal review before the first paid customer
  (`00` L2).

## 6. Secure development
- **Secrets:** in `odoo.conf` (gitignored) or the deployment secret store; never in XML/CSV or
  commits.
- **Dependencies:** pinned by commit (`repos.json`) and by Odoo's `requirements.txt`. Upgrades go
  through the full test suite plus the egress audit.
- **OWASP ASVS:** Level 1 for P1, Level 2 targets for P2 (NFR-SEC-003). Odoo's CSRF protection
  stays on for all non-webhook routes.
