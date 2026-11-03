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

## Verification
Not scaffolded yet. Once the apps exist, list the typecheck, lint and test commands here and run them
after every approved fix.
