# Second Brain — Vault Schema

AI operating instructions for Obsidian vault. Read first every session.

LLM Wiki — persistent, compounding knowledge artifact. LLM writes+maintains. Human curates+directs. Knowledge compiled once, kept current, not re-derived per query.

---

## Core Principles

1. **Simplicity First** — no over-engineering, no premature abstractions, no deep nesting, no complex tagging
2. **Everything Is a Knowledge Asset** — conversations, bugs, architecture, research, lessons → structured reusable notes
3. **AI-Optimized** — explain WHY not WHAT, preserve tradeoffs+decisions, include operational context, reduce ambiguity, stay readable months later
4. **Obsidian Is Source of Truth** — wiki, project OS, architecture handbook, decision database, operational memory, learning graph
5. **Anti-Duplication** — search before creating. If existing page covers 80%: extend, don't fork
6. **Anti-Overengineering** — 3 similar lines > premature helper. No config options "just in case"

## Folder Structure

| Folder | Purpose | Permanence |
|--------|---------|------------|
| `00-inbox/` | Unprocessed captures, raw dumps | Temporary |
| `01-projects/` | Active outcome-based work. Each has README.md | Time-bound |
| `02-areas/` | Long-term responsibilities | Evergreen |
| `03-knowledge/` | Reusable cross-project knowledge | Evergreen |
| `04-decisions/` | ADRs, architecture decisions, tradeoffs | Historical |
| `05-templates/` | Reusable note templates (copy, don't link) | Permanent |
| `06-systems/` | Operational systems, workflows, AI pipelines | Semi-permanent |
| `07-logs/` | Changelogs, retrospectives | Historical |
| `08-archive/` | Deprecated/completed. Never delete — archive | Historical |

Flat structure within folders. No sub-folders until scale demands it.

## Naming Conventions

- lowercase kebab-case: `payment-webhook-race-condition.md`
- Descriptive. No dates in filenames. No vague titles, random numbering, unclear abbreviations.
- Bad: `notes.md`, `2024-01-15-meeting.md` | Good: `promptpay-qr-polling.md`

## Note Structure

Not every section required. Use what fits.

```markdown
# Title
## Summary      — one-line explanation
## Context      — why this exists
## Problem      — what issue this addresses
## Details      — main information
## Decision     — what was decided and why
## Tradeoffs    — pros/cons
## Consequences — long-term impact
## Related      — [[linked-note]]
```

## Ingestion Workflow

1. **Understand** — identify project, domain, permanence, note type
2. **Search** — check `index.md`. If 80% covered: UPDATE, don't create
3. **Classify** — pick folder: inbox / project / knowledge / decision / system / archive
4. **Write** — clean structured markdown per note structure above
5. **Cross-link** — `[[wikilinks]]` to related pages. Link liberally — orphan pages degrade vault
6. **Update `index.md`** — one-line entry with wikilink
7. **Update `log.md`** — `## [YYYY-MM-DD] type | title`
8. **Extract** — flag architecture decisions, tradeoffs, reusable knowledge

## Operations

**Ingest:** User drops source → LLM reads → writes summary page → updates index+entity pages → appends log. Single source may touch 10–15 pages.

**Query:** User asks → LLM searches `index.md` → drills into pages → synthesizes with citations. Good answers filed back as new pages.

**Lint:** Periodic health-check — contradictions, stale claims, orphan pages, missing cross-references. LLM flags and suggests fixes.

## Quality Rules

Every note must answer: What is this? Why does it matter? What problem does it solve? What are tradeoffs? What should future AI understand?

Prefer: clarity, operational usefulness, explicit context, reusable knowledge.
Avoid: filler, vague summaries, generic AI writing, unnecessary metadata, duplicate concepts.

## Lifecycle & Cross-Referencing

- **Create** — new knowledge not captured anywhere
- **Update** — existing page incomplete or stale
- **Merge** — two pages same topic → combine, update all links
- **Archive** — completed/superseded → move to `08-archive/`. Never delete.
- `[[page-name]]` wikilinks. No aliases in content notes. Display aliases (`[[name|Title]]`) allowed in `index.md` only. `[[name]]` with no matching page = "worth writing later", not error.
- When updating: check if linked pages need updates too.

## Behavior Rules

**Must:** flag tech debt | challenge bad architecture | prevent duplication | optimize for AI retrieval | preserve decision context | keep notes under 200 lines (split if longer) | suggest vault improvements

**Must NOT:** create unnecessary folders | over-tag (folder structure IS tag) | duplicate concepts | generate boilerplate | store temporary noise | create notes that should be sections | add abstraction "just in case" | encourage overengineering

## Special Files

| File | Role | Updated |
|------|------|---------|
| `CLAUDE.md` | This file. Vault schema + AI operating instructions. | When conventions evolve |
| `index.md` | Global navigation catalog. One line per page with wikilink. | Every ingest |
| `log.md` (root) | Main operational journal. `grep "^## \[" log.md \| tail -5` | Every ingest |
| `07-logs/log.md` | Session-end log. Wrap-up protocol appends here. | Session wrap-up |
| `master-state.md` | Live session state: branches, loose ends, API contract, guardrails. | S1: every session. S2: weekly. S3–4: monthly or less. |
| `vault-protocol.md` | API contract details. Read only when working on API changes. | On API contract change |
| `vault-guardrails.md` | Architecture guardrails. Read only when working on payment/infra. | On guardrail change |

## Session Initialization Protocol

At start of every session working on SmartEnPlus vault:

1. **Read** `master-state.md` at vault root
2. **Run live git commands** on all 4 repos:
   - `git -C /Users/charuwatnaranong/Desktop/SmartEnPlus/smartenplus-backend branch --show-current`
   - `git -C /Users/charuwatnaranong/Desktop/SmartEnPlus/smartenplus-backend log --oneline -3`
   - `git -C /Users/charuwatnaranong/Desktop/SmartEnPlus/smartenplus-backend status --short`
   - `git -C /Users/charuwatnaranong/Desktop/SmartEnPlus/smartenplus-frontend branch --show-current`
   - `git -C /Users/charuwatnaranong/Desktop/SmartEnPlus/smartenplus-frontend log --oneline -3`
   - `git -C /Users/charuwatnaranong/Desktop/AdminDashBoard/admin-dashboard branch --show-current`
   - `git -C /Users/charuwatnaranong/Desktop/AdminDashBoard/admin-dashboard log --oneline -3`
   - `git -C /Users/charuwatnaranong/Desktop/SmartEnPlus/smartenplus-content branch --show-current`
   - `git -C /Users/charuwatnaranong/Desktop/SmartEnPlus/smartenplus-content log --oneline -3`
   - `git -C /Users/charuwatnaranong/Desktop/SmartEnPlus/smartenplus-content status --short`
3. **Update `master-state.md` Section 1** with live branch+commit data
4. **Respond with 3-part brief** before writing code or making changes:

> **Current State Summary** — last worked on + next step + live uncommitted changes
> **Immediate Focus** — top open item from master-state.md Section 2
> **Workspace Map** — live branch per repo + key external paths

5. **Acknowledge and wait** — do not proceed until user gives instructions

## /lint-vault Command

**Trigger:** user types `/lint-vault`

**Steps:**
1. Read all notes in `01-projects/` and `03-knowledge/` over 150 lines
2. Identify extractable atomic concepts per [[atomic-notes]] rules
3. **Propose list to user BEFORE writing any files:**
   ```
   payment-system.md → locked-amount-reset-rules.md, payment-finalized-at-guard.md
   nextjs-patterns.md → nextjs-ssr-disabled-checkout.md
   ```
4. User confirms or excludes items
5. Extract confirmed atoms, update source notes, update `index.md`
6. Append to `log.md`: `## [YYYY-MM-DD] lint | atomized N concepts from M notes`
7. Commit+push vault

---

## Session Wrap-Up Protocol

**Auto-triggers** (execute immediately, no confirmation needed):
- Explicit: "wrap up", "wrap-up", "wrapup", "session end", "end session"
- Natural: "done for today", "that's it", "good night", "see you tomorrow", "see you", "ok stop", "let's stop here", "stopping here", "bye", "cya"
- Thai: "พอแล้ว", "เลิกแล้ว", "พักก่อน", "โอเคพอ"

**Steps:**
1. **Run `bash vault-wrapup.sh`** — collects git state for all 4 repos. Use output for Section 1.
2. **Edit `master-state.md` Section 1** — overwrite latest session block with achievements + exact resume point. Move previous session to `07-logs/session-history.md`.
3. **Edit `master-state.md` Section 2** — close resolved items (move to `07-logs/closed-items.md`), add new bugs/edge cases.
4. **Atomize** (max 5 per session) — extract to `03-knowledge/`, update `index.md`.
5. **Append to `07-logs/log.md`** — `## [YYYY-MM-DD] session-end | <one-line summary>`
6. **Commit+push vault and content repo:**
   ```bash
   git -C vault add -A && git -C vault commit -m "session-end: <summary>" && git -C vault push
   git -C content add -A && git -C content commit -m "session-end: <summary>" && git -C content push
   ```

**File structure (optimized):**
- `master-state.md` — Section 1 (latest session + resume point) + Section 2 (open items only). ~60 lines.
- `vault-protocol.md` — API contract. Read only when working on API changes.
- `vault-guardrails.md` — Architecture guardrails. Read only when working on payment/infra.
- `07-logs/session-history.md` — Historical sessions (#38+).
- `07-logs/closed-items.md` — Resolved items for audit trail.
- `vault-wrapup.sh` — Git state collection script.

## Projects in This Vault

- **SmartEnPlus** — Thailand transport booking platform. 4-repo ecosystem.
  - `smartenplus-backend` | `smartenplus-frontend` | `admin-dashboard` | `smartenplus-content`
  - See [[README]], [[admin-dashboard]]
- **SmartEnPlus Content** — Content marketing strategy, keyword research, blog drafts.
  - `smartenplus-content` at `/Users/charuwatnaranong/Desktop/SmartEnPlus/smartenplus-content/`
  - See [[content-marketing-strategy-review]]

## Active Knowledge Domains

- AI workflows & LLM Wiki pattern
- Next.js patterns (ISR, RTK Query, SSR)
- Payment integration (Thai methods, Omise)
- Design systems (token-based approach)
- Admin dashboard contracts, image pipeline, component patterns

---

Vault: `/Users/charuwatnaranong/Desktop/SmartEnPlus/smartenplus project/` | Created: 2026-05-16