# LESSONS.md — what agents have learned on this repo

Read at the start of every session; written at the end of every task. Protocol: `AGENTS.md` §4.

**Entry format**
```
### L-NNN · YYYY-MM-DD · <area> · confidence: high|medium|low
**Trigger:** what happened (the correction, failure or surprise).
**Lesson:** the general truth behind it.
**Do:** the concrete behaviour to apply next time.
**Evidence:** command, file:line, PR or quote that backs it.
```
Areas: `domain` · `db` · `sync` · `api` · `frontend` · `design` · `i18n` · `testing` · `tooling` · `process`.
Numbers are never reused. Superseded lessons stay in the Archive with a pointer to their replacement.

---

## Active

### L-001 · 2026-11-03 · process · confidence: high
**Trigger:** The founder's 15-document spec arrived as one paste that was cut at the 50,000-character
message limit. `docs/04-architecture.md` stops mid-§6.7 and docs 05–12 never arrived.
**Lesson:** A missing spec is a question for the founder, not a gap to fill by inference. Invented
data models or API shapes become "the spec" the moment code is built on them.
**Do:** Treat 05–12 and the rest of 04 as unavailable until the founder supplies them. Ask for them
in multiple parts or as files. Remove this lesson once they are in place.
**Evidence:** `docs/04-architecture.md` truncation marker; stub banners in `docs/05`–`12`.

### L-002 · 2026-11-03 · tooling · confidence: high
**Trigger:** Development is on Windows with Git Bash. The `design-fix` skill documents that
Git Bash rewrites any argument starting with `/` into a filesystem path.
**Lesson:** MSYS path conversion silently mangles URL paths and routes passed as CLI arguments
(`/admin` arrives as `C:/Program Files/Git/admin`).
**Do:** Pass routes without the leading slash (`--routes admin,pos`), or prefix the command with
`MSYS_NO_PATHCONV=1` when a tool needs the slash.
**Evidence:** `~/.claude/skills/design-fix/SKILL.md`, "Windows Git Bash" paragraph.

---

## Archive
_(Promoted or superseded lessons move here with `promoted → <where>` or `superseded by L-NNN`.)_
