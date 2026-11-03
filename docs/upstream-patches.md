# Upstream Patches

Every change Hisabkar makes to upstream behaviour **other than** through normal module inheritance
is listed here. Upstream means Odoo and OCA code in `vendor/`, pinned in `repos.json`.

What counts as a change: a monkey-patch, an override of a private method that upstream may rename,
or a workaround for an upstream bug. Re-check each row on every upstream upgrade.

`vendor/` itself is never edited.

| # | What | Where (our code) | Why | Upstream issue | Re-check on upgrade |
|---|---|---|---|---|---|
| 1 | Process-wide egress guard: wraps `socket.getaddrinfo`, `socket.socket.connect` and `connect_ex` | `addons/hisabkar_privacy/egress.py` | ADR-0005 / NFR-SEC-005..006: no outbound connection except to allowlisted hosts; the vendor's domains are always denied | n/a (policy, not a bug) | Python version bump; any new outbound library that bypasses `socket` (C extensions); `gethostbyname` and UDP `sendto` are not covered (the network firewall is); the gevent worker, where the framework patches `socket` before us (expected to work, unverified until the SaaS spike P0-8); `tests/test_zero_egress.py` must stay green |
| 2 | Overrides of private methods and routes: `ir.model.data._process_end` (purge timing), `ir.module.module._state_update` / `update_list`, `publisher_warranty.contract._get_message` / `_get_sys_logs`, `mail.link.preview._is_link_preview_enabled` / `_create_from_message_and_notify` / `_search_or_create_from_url`, `res.partner._get_gravatar_image`, `ir.http._post_dispatch` / `_handle_error`, and the html editor's `link_preview_metadata*` routes | `addons/hisabkar_privacy/models/`, `controllers/main.py` | Same as row 1: block the paid-service modules and neutralise every audited data flow | n/a | If upstream renames any of these, the override silently stops applying. `test_overridden_upstream_methods_still_exist` fails when a name disappears upstream; the other tests drive upstream's own callers (the email onchange, the cron, `button_install`). |
| 3 | `db_template = hisabkar_template` (C/C locale) instead of `template0` | `scripts/setup-dev.ps1`, the on-premise installer | PostgreSQL on Windows refuses databases whose collate (`C`, forced by upstream for `template0`) differs from ctype (a Windows locale): "collations with different collate and ctype values are not supported on this platform" | Upstream forces `LC_COLLATE 'C'` only for `template0` (`odoo/service/db.py` `_create_empty_database`) | Whether upstream's database-creation SQL changes |
