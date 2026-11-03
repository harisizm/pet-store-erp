# design-fix overlay — Kitaab ERP

## Design authority (in order)
1. `DESIGN.md` at the repo root: tokens, type scale, spacing, radii, motion.
2. `docs/08-ux-and-screens.md`: screen inventory and flows (stub until the founder supplies it).
3. `docs/03-srs.md`: NFR-USE-001..004 (Urdu/RTL, PKR formatting, WCAG AA, 44 px POS targets),
   NFR-PERF-004 (dashboard < 2 s on 3G).
4. `AGENTS.md` §3: the AI-slop blacklist and product needs.

## Project rules
- Audit every POS route at `tablet` and `mobile` as well as `desktop`. The POS runs on 10" Android
  tablets and phones.
- Audit each route in both `en` (LTR) and `ur` (RTL). A layout that only breaks in RTL is a FIX,
  not noise.
- Any touch target under 44 px on a POS route is high severity (NFR-USE-004).
- `color-off-token` findings are always real here: the project rule is tokens only.

## Known intentional exceptions
None yet. Add each one with the `DESIGN.md` section that allows it.

## App under test
- Odoo 18 at `http://localhost:8069`: back office at `/odoo`, POS at `/pos/ui`. The founder starts
  it with `.venv\Scripts\python vendor\odoo\odoo-bin -c odoo.conf`. Never start it yourself.
- Styling lives in `addons/kitaab_theme`. Upstream templates are in `vendor/` and are never edited.
  Fixes go in `kitaab_*` overrides.
- Any user-visible "Odoo" text, logo or favicon is a FIX (ADR-0004).
- So is any request to an external host (ADR-0005).

## Verification
After every approved fix, run the touched module's tests (`AGENTS.md` §6), then re-audit.
