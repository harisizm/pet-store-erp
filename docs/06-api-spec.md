# API Specification (Odoo 18)

> **Re-authored 2026-11-03** for Odoo 18 (ADR-0003). The original was written for a NestJS REST API
> and was lost in transit. Odoo supplies most of the transport. This file defines conventions for
> everything Hisabkar adds, and lists every Hisabkar route. A route not listed here does not exist.

## 1. Surfaces Odoo already provides
| Surface | Used for | Notes |
|---|---|---|
| Web client RPC (`/web/dataset/call_kw`, JSON-RPC) | Back office and POS calls to model methods | Session cookie auth. Access rights and record rules apply. |
| POS order sync (`pos.order.sync_from_ui`) | Pushing POS orders, including ones queued offline | Dedupes on `pos.order.uuid`, so a replayed order is not created twice. This is the idempotency mechanism for sales (`docs/AGENTS.md` §1.6). |
| POS data loading (`pos.session.load_data` / data service) | Pulling products, partners, prices, lots and settings into the till | Hisabkar extends the loaded fields through `_load_pos_data_fields` overrides. |
| External API (`/json/2` … or `/xmlrpc/2`, `/jsonrpc`) with user API keys (`res.users.apikeys`) | Integrations and scripts | Off by default for shop users. Integration users get keys scoped to a dedicated user with minimal groups. |

## 2. Conventions for Hisabkar routes
- **Prefix:** `/hisabkar/v1/...` for JSON and `/hisabkar/r/...` for public pages. Version bumps only on
  breaking changes.
- **Controllers:**
  - `type='jsonrpc'` for calls from our OWL code;
  - `type='http'` for public pages and webhooks;
  - `auth='user'` unless the route is public (e-receipt) or a webhook (signature-checked);
  - `csrf=False` only for signed webhooks.
- **Idempotency:** every write route requires an `Idempotency-Key` header or a client `uuid`.
  - The first result is stored in `hisabkar.idempotency` (key, route, user, response hash, created) and
    returned unchanged on replay.
  - Rows expire after 30 days.
- **Payloads:** decimal strings for money and quantity in JSON (`"1250.00"`, `"2.500"`); ISO-8601
  UTC timestamps; ids as integers; client-generated records carry `uuid`.
- **Errors:** JSON-RPC error with `data.code` from a fixed list:
  - `HISABKAR_FORBIDDEN`
  - `HISABKAR_NOT_FOUND`
  - `HISABKAR_VALIDATION`
  - `HISABKAR_CONFLICT`
  - `HISABKAR_EGRESS_BLOCKED`
  - `HISABKAR_RATE_LIMITED`

  Each error has a human message that is translatable (en/ur).
- **Webhooks (inbound):** verify the provider's HMAC signature before parsing; reject on mismatch
  (`401`); store the raw event in `hisabkar.webhook.event` before processing so it can be replayed;
  process asynchronously (cron / queue).
- **Egress:** a route that calls outward must use a host on the allowlist (ADR-0005). Otherwise it
  fails with `HISABKAR_EGRESS_BLOCKED`.

## 3. Hisabkar routes (planned)
| Route | Type / auth | Purpose | Idempotency | Requirement | Phase |
|---|---|---|---|---|---|
| `POST /hisabkar/csp-report` | http / none, no CSRF (browsers send it) | Receives Content-Security-Policy violation reports; logs them as a warning; returns 204. Body capped at 16 KB. **Built** (`hisabkar_privacy`). | n/a (log only) | NFR-SEC-007 | P0 |
| `GET /hisabkar/r/<token>` | http / public | E-receipt page (unguessable token) | n/a (read) | FR-POS-009 | P1 |
| `GET /hisabkar/s/<token>` | http / public | Customer statement page | n/a | FR-CUS-004 | P1 |
| `POST /hisabkar/v1/khata/collect` | jsonrpc / user | Record a khata payment from the POS (creates `account.payment`) | client `uuid` | FR-CUS-003, FR-POS-002 | P1 |
| `POST /hisabkar/v1/pos/override` | jsonrpc / user | Validate a Manager PIN for discount, expired-lot or no-receipt-return overrides; writes an audit row | client `uuid` | FR-POS-004, FR-INV-012, FR-POS-010 | P1 |
| `POST /hisabkar/v1/device/register` | jsonrpc / manager | Register a till device, issue a `device_code` | client `uuid` | FR-ADM-006 | P1 |
| `POST /hisabkar/v1/device/heartbeat` | jsonrpc / user | Report last sync time and offline queue length | key = device + minute | NFR-OBS-003 | P1 |
| `POST /hisabkar/webhook/whatsapp` | http / public, Meta signature | Incoming WhatsApp messages and status (through the OCA gateway) | Meta message id | FR-CUS-006 | P2 |
| `POST /hisabkar/webhook/woocommerce/<conn>` | http / public, HMAC | Order and product events | WooCommerce delivery id | FR-ORD-001, FR-ORD-006 | P2 |
| `POST /hisabkar/webhook/shopify/<conn>` | http / public, HMAC | Order and inventory events | `X-Shopify-Webhook-Id` | FR-ORD-001, FR-ORD-006 | P2 |

## 4. Offline behaviour (summary)
- **Sales and refunds:** queued by the POS and synced through `sync_from_ui`, deduped by uuid. The
  server never rejects an offline sale for stock reasons. Anomalies (negative stock, expired lot,
  unauthorised price) become review-list entries (architecture §6.1.4).
- **Khata payments and overrides made offline:** queued by our POS code under a client `uuid` and
  replayed to the routes above. Replay is safe because of idempotency.
- **Reference data:** catalog, prices, lots and partners are pull-only through the POS data loader.
