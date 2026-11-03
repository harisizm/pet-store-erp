# Architecture

> **PARTLY SUPERSEDED (2026-11-03).** Kitaab is built on Odoo 18 Community (ADR-0003).
> - §2–3 (the NestJS stack and monorepo layout) no longer apply.
> - §4–6 remain the reference for module boundaries, tenancy intent and offline-sync behaviour, but
>   they are realised through Odoo mechanisms. The mapping is in `05-data-model.md` and `06-api-spec.md`.
>
> **INCOMPLETE — truncated in transit (2026-11-03).** The source paste was cut at the 50,000-character
> message limit partway through §6.7. Everything below up to the marker is verbatim. The rest of §6.7
> and any later sections were not received. Do not reconstruct them from memory; ask the founder for
> the remainder. See `LESSONS.md` L-001.

## 1. Overview
```
┌───────────────┐   ┌──────────────────┐   ┌─────────────────────┐
│ POS PWA       │   │ Admin Web        │   │ Public e-receipts / │
│ (React+Vite)  │   │ (Next.js)        │   │ statements (Next.js)│
│ IndexedDB     │   │ Owner/Manager    │   │                     │
│ Sync engine   │   │ dashboard        │   │                     │
└──────┬────────┘   └────────┬─────────┘   └──────────┬──────────┘
       │ HTTPS (REST + sync)  │                        │
       └──────────────┬───────┴────────────────────────┘
                      ▼
            ┌───────────────────────┐        ┌──────────────────┐
            │ API (NestJS)          │◄──────►│ Redis            │
            │ Modular monolith      │        │ cache, BullMQ    │
            │ REST /v1, /sync       │        └──────────────────┘
            │ Webhook receivers     │        ┌──────────────────┐
            │ Workers (BullMQ)      │───────►│ Object storage   │
            └─────────┬─────────────┘        │ (S3-compatible)  │
                      ▼                      └──────────────────┘
            ┌───────────────────────┐        ┌──────────────────┐
            │ PostgreSQL 16 (RLS)   │        │ External:        │
            │ single DB, schemas    │        │ WhatsApp Cloud,  │
            │ per module            │        │ WooCommerce,     │
            └───────────────────────┘        │ Shopify, SMS,    │
                                             │ couriers, FBR    │
                                             └──────────────────┘
```

## 2. ADR-0001: Technology choices (DECIDED)
| Concern | Choice | Why |
|---|---|---|
| Language | TypeScript end-to-end | One language for agents; shared contracts |
| API | NestJS (Fastify adapter) | Modules, DI, guards map cleanly to module boundaries |
| DB | PostgreSQL 16 | Transactions, RLS, numeric types, JSONB |
| ORM / migrations | Drizzle ORM + Drizzle Kit | SQL-first, typed, transparent migrations |
| Validation / contracts | Zod (shared package) → OpenAPI via `zod-to-openapi` | Single source for types |
| Jobs / queues | BullMQ on Redis | Webhooks, sync to channels, messaging, reports |
| Admin web | Next.js (App Router), TanStack Query, Tailwind, shadcn/ui | Fast to build, SSR for public pages |
| POS | React + Vite PWA, Workbox, Dexie (IndexedDB) | Offline-first, installable |
| Auth | Own implementation: OTP + JWT access (15 min) + rotating refresh tokens; device registration | Phone-first market |
| Files | S3-compatible (Cloudflare R2 / AWS S3) | Images, attachments, exports |
| PDF | Server-side HTML → PDF (Playwright/Chromium) worker | Receipts, statements, certificates |
| Search (POS) | Local in-memory index (MiniSearch) built from IndexedDB | Instant offline search |
| Search (admin) | Postgres `pg_trgm` + full text | No extra infra |
| Infra | Docker; single region; managed Postgres; 2 API instances behind LB | Simple, cheap |
| Observability | OpenTelemetry → Grafana/Loki or vendor; Sentry | |
| CI/CD | GitHub Actions; preview envs for PRs | |

Rejected: microservices (too much overhead for team size), Firebase (relational ledgers + RLS needed), native POS app in P1 (PWA sufficient).

## 3. Repository layout
```
kitaab/
├── apps/
│   ├── api/            # NestJS: modules, workers, webhook receivers
│   ├── web/            # Next.js: admin + public e-receipts
│   └── pos/            # React+Vite PWA
├── packages/
│   ├── shared/         # zod contracts, money, quantity, enums, i18n keys, feature flags
│   ├── db/             # drizzle schema, migrations, RLS policies, seeds
│   ├── domain/         # pure domain logic (pricing, tax, WAC, FEFO, khata) — no IO
│   ├── ui/             # shared React components (both web and pos)
│   └── config/         # eslint, tsconfig, tailwind presets
├── docs/               # these documents + adr/
└── infra/              # docker-compose (dev), IaC
```
`packages/domain` is pure TypeScript with no IO, so the **same pricing/tax/FEFO logic runs in the POS offline and on the server**. The server is authoritative.

## 4. Modules (bounded contexts)
| Module | Owns tables (prefix) | Depends on (via interfaces/events) |
|---|---|---|
| `platform` | tenants, plans, subscriptions, feature flags | — |
| `identity` | users, roles, permissions, devices, sessions, otp | platform |
| `org` | branches, settings, sequences | platform |
| `catalog` | items, sellable_units, units, barcodes, prices, categories, brands | org |
| `inventory` | stock_movements, stock_balances, batches, serials, counts, transfers | catalog, org |
| `sales` | sales, sale_lines, payments, returns, shifts, cash_movements, day_closes | catalog, inventory, customers, ledger |
| `customers` | customers, khata entries | ledger |
| `purchasing` | suppliers, purchase_orders, receipts, bills, supplier_payments, purchase_returns | catalog, inventory, ledger |
| `expenses` | expenses, money_accounts, transfers | ledger |
| `ledger` | accounts, journal_entries, journal_lines, posting rules | — |
| `orders` (P2) | orders, order_lines, deliveries, cod_settlements | catalog, inventory, customers, channels |
| `channels` (P2) | channel_connections, product_links, sync_jobs, webhook_events | catalog, inventory, orders |
| `messaging` | message_templates, outbound_messages, opt_ins | customers |
| `pet` (P2, pack) | pets, animal_records, health_events, appointments, boarding_stays, reminders | catalog, inventory, customers, sales |
| `reports` | read models / materialized views | reads all (read-only) |
| `audit` | audit_log | all (write via event) |
| `sync` | device_sync_state, sync_inbox | all writable offline modules |

Rules:
- Each module exposes a `*.service.ts` public API and emits domain events (`sale.completed`, `stock.changed`, `purchase.received`, `khata.entry_posted`, …) via an in-process event bus with a **transactional outbox** table for anything that triggers external side-effects.
- Lint rule (`eslint-plugin-boundaries`) enforces imports.
- Cross-module writes in one business transaction (e.g., sale → stock movement → khata → journal) happen inside a single DB transaction orchestrated by the owning module's service (sales), calling other modules' **transaction-aware** service methods.

## 5. Multi-tenancy
- Single database, shared schema, `tenant_id uuid not null` on every tenant table.
- Postgres RLS: `USING (tenant_id = current_setting('app.tenant_id')::uuid)`. API sets `SET LOCAL app.tenant_id` per transaction from the authenticated principal.
- Branch-level access enforced in the application layer (guards) plus `branch_id` filters; optionally RLS on branch for Cashier roles (P2).
- Platform admin uses a separate DB role with `BYPASSRLS`, only in the `platform` admin endpoints, fully audited.

## 6. Offline-first POS & sync (core design)

### 6.1 Principles
1. POS writes are **commands recorded locally** (outbox) and also applied to local state for immediate UX.
2. Server is the source of truth. On sync, the server **re-validates and applies** each command; the result is returned.
3. All offline-creatable records use client-generated **UUIDv7** IDs; each command carries an `idempotency_key` (= command id).
4. Business documents created offline are **never rejected for stock reasons** (sale happened in the real world). Server applies them and flags anomalies (negative stock, expired batch sold, price mismatch) into review queues.
5. Pull is **incremental by change cursor** per entity type.

### 6.2 Local stores (Dexie/IndexedDB)
- Reference data (pull-only): sellable units, barcodes, prices, categories, customers (branch-scoped subset + recent), customer balances, batches with available qty (branch), settings, users/PIN hashes for the branch, tax classes, payment methods.
- Transactional data (push): `outbox` of commands: `sale.create`, `sale_return.create`, `khata_payment.create`, `cash_movement.create`, `shift.open`, `shift.close`, `customer.create`, `customer.update`.
- Local projections: today's sales, held bills, local stock deltas (for display only).

### 6.3 Push protocol
`POST /v1/sync/push` with batch of ≤ 100 commands, ordered by local sequence.
Server processing per command (own transaction):
- If `idempotency_key` already processed → return stored result (`duplicate: true`).
- Validate schema → apply domain logic → write documents, movements, ledger → store result → commit.
- Per-command result: `applied` | `applied_with_warnings` (e.g., `NEGATIVE_STOCK`, `EXPIRED_BATCH`, `PRICE_OVERRIDE_UNAUTHORIZED`) | `rejected` (only for malformed/forbidden commands, e.g., revoked device; rejected commands go to a device "failed" list visible to managers, never silently dropped).

### 6.4 Pull protocol
`GET /v1/sync/pull?cursors=<json>`: server returns changes since each entity cursor (based on a monotonically increasing `change_seq bigint` from a per-tenant sequence, written on every insert/update of synced tables), plus tombstones for deletions/deactivations. Page size 500; client loops until `has_more=false`.

### 6.5 Conflict rules
| Data | Rule |
|---|---|
| Sales, returns, payments, cash movements | Append-only; no conflicts (each is a new fact) |
| Stock | Derived server-side from facts; POS stock is advisory |
| Customer profile edits | Last-writer-wins per field with `updated_at`; khata balance is derived (never written by client) |
| Prices | Server authoritative; offline sale records the price actually charged; if differs from server price at sale time and user lacked override permission, warning flag |
| Catalog | Pull-only to POS |

### 6.6 Receipt numbering offline
Per device daily sequence: `{branchCode}-{deviceCode}-{yyyymmdd}-{seq4}`. Device code assigned at registration. Guarantees uniqueness without the server.

### 6.7 Batch allocation offline
POS runs FEFO from loc

<!-- ===== TRUNCATED IN SOURCE: content below this line was not received ===== -->
