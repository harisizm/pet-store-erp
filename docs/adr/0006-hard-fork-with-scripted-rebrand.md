# ADR-0006: Hard fork of the core with a scripted, repeatable rebrand

- **Status:** accepted (founder, 2026-11-03). Execution waits for the product name (`00` B5).
- **Date:** 2026-11-03
- **Amends:** ADR-0003. The "upstream referenced, never edited" rule becomes "upstream is only ever
  changed by the rebrand tool".
- **Requirements:** founder: "delete every trace of the word odoo … that should never come up in
  the future"

## Context
The founder wants no trace of Odoo anywhere, including the code, not just what users see. Options
put to the founder, with consequences stated:
1. erase it from everything anyone sees;
2. that, plus our docs;
3. hard fork and rename all code.

The founder chose **3**.

**Hard limits that cannot be waived:**
- **Legal (GPL-3 §4–5, which LGPL-3 builds on, and LGPL-3 §4).** We must keep intact:
  - copyright notices;
  - licence notices (including each file's header line, "Part of Odoo. See LICENSE file for full
    copyright and licensing details.");
  - the `LICENSE` and `COPYRIGHT` files.

  We must also add a prominent notice that we modified the work, with a date. On-premise
  distributions must state that the LGPL library is used and include its licence. Removing these is
  copyright infringement. They are the only Odoo text that remains, and they appear only in source
  files and the legal-notices document, never on screen.
- **Technical.** Odoo's Python package is named `odoo` and every core and OCA module imports it. The
  OWL front-end library is `@odoo/owl`. Renaming them breaks compatibility with every unmodified
  upstream or OCA module. So the OCA modules we use must go through the same rename.

## Decision
Build a **rebrand tool** (`tools/rebrand/`, our code). It is deterministic and re-runnable.

**Input:** a pinned upstream commit (from `repos.json`) for Odoo and each OCA repo.

**Output:** a renamed tree published to our own fork repos (`<brand>-core`, `<brand>-oca-*`).

**What the tool renames:**
- the Python package (`odoo` → `<brand>core` or similar);
- `odoo-bin`;
- `@odoo/owl` and `odoo.define`/`@odoo-module` markers;
- the URL prefix `/odoo` → `/<brand>`;
- config file and key names, and `ODOO_*` environment variables;
- user-facing strings, including all `.po` translations;
- logos, favicons and assets;
- module names and paths containing "odoo";
- HTTP headers and log names;
- the Windows service and process names.

**What it never touches:** the licence and copyright notices listed above.

**What it adds:**
- a `NOTICE` file and per-file "Modified by <brand>, <date>" notices (GPL-3 §5a);
- a CHANGES log.

**Gate:** a release test fails on any case-insensitive "odoo" outside an explicit allowlist of the
legal lines. It runs over:
- the fork's source;
- the rendered UI;
- PDFs and emails;
- HTTP responses;
- installer artefacts.

**Upgrades** (including security fixes):
1. bump the commit in `repos.json`;
2. rerun the tool;
3. diff;
4. run all tests;
5. publish.

This is how we stay able to take upstream fixes. It is semi-manual, never automatic.

**Licences of the forks:**
- The core fork stays LGPL-3. Its source is provided to on-premise customers on request (LGPL
  duty).
- OCA forks stay AGPL-3 and are published publicly.

Our `<brand>_*` business modules stay proprietary (ADR-0004). They import the renamed package.

## Consequences
- We own a fork. Every upstream release needs a rebrand run, test pass and review.
- Community answers, tutorials and Odoo documentation no longer match our names one-to-one. The
  tool's mapping table (`tools/rebrand/mapping.*`) is the translation key for developers and agents.
- Free OCA modules beyond the ones we pinned need a rebrand run before use.
- The work is sized by the occurrence count recorded in `tools/rebrand/README.md` when the tool is
  built.
- **Before the tool exists:** we develop against plain upstream in `vendor/`, so feature work
  isn't blocked. Our own module code avoids the word except in imports, so switching to the renamed
  package is a mechanical import rewrite, which the tool also applies to our modules.
- **Legal review (`00` L2)** must include the notice-retention and modification-notice approach.
