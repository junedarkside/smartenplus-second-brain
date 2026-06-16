# r2 Skeptic — Challenge Template

## When to use
You're the Round-2 Skeptic. Your job: challenge every R1 finding, enforce caps, drop low-ROI/off-brand items, surface backend debt, identify duplicate findings. Output goes in `<subfolder>/r2-skeptic.md`.

---

## Frontmatter (required)
```yaml
---
name: r2-skeptic
description: <one-line: rounds challenged + cap enforced + auto-DROP rules>
metadata:
  type: specialist-r2
  role: skeptic
  page: <feature/page audited>
  smartenplus_route: <path>
  date: YYYY-MM-DD
  parent: <subfolder-slug>
---
```

## Structure

```markdown
# R2 — Skeptic (<Scope>)

**Role:** challenge every R1 finding. Enforce max-K cap. Reject off-brand.

**Skeptic rules (auto-applied):**
- `ROI=low AND brand-fit=maybe` → AUTO-DROP
- `brand-fit=no` → AUTO-DROP
- `effort > small AND ROI not high` → DOWNGRADE P2
- Backend debt (no data field) → DEFER P3
- User-deferred → DROP

**Tiebreak order (when ranking):** ROI high→low, brand-fit yes→maybe→no, effort trivial→large.

---

## Auto-DROP (no debate)

| ID | Pattern | Reason |
|----|---------|--------|
| <ID> | <pattern> | <one-line> |

---

## Verdict (per R1 finding)

### <ID>-1 — <Pattern Name>

- **R1-<ROLE> claim:** ROI=<>, brand-fit=<>, effort=<>
- **Skeptic counter:** <challenge with evidence file:line>
- **Verdict:** KEEP / DOWNGRADE / DROP / DEFER P<n> / MERGE
- **Reasoning:** <one-line>

---

## Conflicts Between Specialists

### Conflict N: <ID> vs <ID>
- <R1-X says>...
- <R1-Y says>...
- **Winner:** <X or Y> — <reason>

---

## Final K (cap-enforced)

| Rank | ID | Pattern | ROI | Brand-fit | Effort | Notes |
|------|----|---------|-----|-----------|--------|-------|
| 1 | <ID> | <pattern> | <r> | <b> | <e> | <notes> |

---

## Open Questions for Leader

1. <question that leader must answer before commit>
2. <question>

---

## Related Atoms (Extracted YYYY-MM-DD)
- [[<atom-note>]] — <Skeptic Finding N reference>

## Related
- [[r1-ux]] | [[r1-visual]] | [[r1-<other-specialist>]]
- [[r3-leader-synthesis]]
```

## Rules

1. **Challenge every R1 finding** — don't rubber-stamp. Cite evidence.
2. **Auto-DROP table first** — items rejected without debate go here.
3. **Use same ID scheme as R1** — `UX-1` in r1-ux → `UX-1` in r2-skeptic.
4. **Cite file:line** for every counter-claim.
5. **Merge duplicates** — if FE-14 and UX-15 are the same, drop UX-15, note "DUPLICATE of FE-14".
6. **Enforce cap** — final K must be a fixed number (5, 12, etc.) per scope.
7. **End with `## Open Questions for Leader`** — questions only Leader can answer.
8. **Extract atoms** — list `## Related Atoms (Extracted YYYY-MM-DD)` at bottom.
9. **Length target**: 100-200 lines. Verdict table 30-50 rows max.

## Severity guide

| Severity | Trigger |
|---|---|
| **P0** | crash / data loss / security / XSS / WCAG critical |
| **P1** | conversion blocker / SEO critical / serious a11y |
| **P2** | UX friction / polish / minor a11y |
| **P3** | hygiene / dead code / dev quality |

Skeptic downgrades 30-50% of R1's flags. That's normal.

## Anti-patterns

- Rubber-stamping all R1 findings
- No evidence in counter-claims
- P0 for hygiene issues
- Missing cap enforcement
- No conflict resolution between specialists
- No Open Questions
