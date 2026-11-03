# AGENTS.md — Rules for Coding Agents

## 0. Before writing code
- Read `README.md`, this file, and the SRS sections for your task.
- Find the requirement IDs you are implementing. If none exist, stop and add them to `03-srs.md` first (mark `status: proposed`).
- Check `00-assumptions-and-open-questions.md`. Do not build on an "OPEN" item without noting it in your PR.

## 1. Non-negotiable engineering rules
1. **Money is never a float.** Store and compute money as integer **paisa** (`bigint`). 1 PKR = 100 paisa. Use the shared `Money` helpers in `packages/shared/money`. Rounding: half-up, at line level, then sum.
2. **Quantities** are `numeric(14,3)` in DB and decimal strings in JSON (e.g., `"2.500"`), handled with a decimal library (`decimal.js`). Never JS `number` for quantities in business logic.
3. **Every tenant-owned table has `tenant_id`** and is protected by Postgres Row-Level Security. No query may bypass RLS except in the `platform-admin` module.
4. **Stock is a ledger.** On-hand quantity is derived from `stock_movements`. Never "update quantity = x" directly. Cached balances (`stock_balances`) are updated only inside the same transaction as the movement.
5. **Financial documents are immutable once posted.** Corrections are made by reversal/credit-note documents, never by editing or deleting.
6. **IDs are UUIDv7**, generated client-side for anything that can be created offline.
7. **Every write endpoint accepts `Idempotency-Key`.** Offline sync depends on it.
8. **Times** are stored in UTC (`timestamptz`). Display in the branch timezone (default `Asia/Karachi`). Business day boundaries use the branch timezone.
9. **Module boundaries:** a module may only touch its own tables. Cross-module access goes through the other module's service interface or domain events. See `04-architecture.md §4`.
10. **Contracts first:** request/response schemas live in `packages/shared/contracts` as Zod schemas. API and clients both import them.
11. **i18n from day one:** no hard-coded user-facing strings. Keys in `en` and `ur`. UI must survive RTL.
12. **No secrets in code.** Use env vars; document them in `.env.example`.

## 2. Repository conventions
- Monorepo: pnpm workspaces + Turborepo.
- TypeScript `strict: true` everywhere. No `any` without an explaining comment.
- Lint: ESLint + Prettier. Commits: Conventional Commits, e.g. `feat(inventory): FEFO batch picking [FR-INV-021]`.
- DB migrations: Drizzle Kit, forward-only, one migration per PR, reviewed SQL committed.
- Feature flags: `tenant_features` table + `packages/shared/features.ts`. Vertical-pack features must be behind flags.

## 3. Definition of Done (every task)
- [ ] Requirement IDs referenced in code comments at entry points and in tests.
- [ ] Unit tests for domain logic; integration test for each new endpoint (real Postgres via Testcontainers).
- [ ] RLS test proving tenant A cannot read/write tenant B data for every new table.
- [ ] Money/quantity edge cases tested (zero, negative returns, rounding).
- [ ] If offline-capable: sync replay test (same payload twice → one effect).
- [ ] i18n keys added for `en` and `ur`.
- [ ] Audit log entries for create/update/void on business documents.
- [ ] API docs (OpenAPI) regenerated; `06-api-spec.md` updated if conventions changed.
- [ ] No TODOs without a linked issue.

## 4. When unsure
Choose the simplest design that satisfies the SRS, write the decision as an ADR in `docs/adr/NNNN-title.md`
(context, decision, consequences), and continue.
