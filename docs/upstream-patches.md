# Upstream Patches

Every change Hisabkar makes to upstream behaviour **other than** through normal module inheritance is
listed here. Upstream means Odoo and OCA code in `vendor/`, pinned in `repos.json`.

What counts as a change: a monkey-patch, an override of a private method that upstream may rename,
or a workaround for an upstream bug. Re-check each row on every upstream upgrade.

`vendor/` itself is never edited.

| # | What | Where (our code) | Why | Upstream issue | Re-check on upgrade |
|---|---|---|---|---|---|
| — | None yet. `hisabkar_privacy`'s socket-level egress guard (ADR-0005) will be row 1 when task P0-2 lands. | | | | |
