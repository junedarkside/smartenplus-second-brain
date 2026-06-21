# r1 Specialist — Audit Template

## When to use
You're a Round-1 specialist (UX, Visual, SEO, Performance, Mobile, etc.) auditing a feature/page. Output goes in `<subfolder>/r1-<role>.md`. Skeptic (r2) will challenge your findings.

---

## Frontmatter (required)
```yaml
---
name: r1-<role>
description: <one-line role + scope of this audit>
metadata:
  type: specialist-r1
  role: <ux-conversion-designer | visual-designer | seo | perf | mobile | ...>
  page: <feature/page audited>
  smartenplus_route: <path>
  date: YYYY-MM-DD
  parent: <subfolder-slug>
---
```

## Structure

```markdown
# R1-<ROLE> — <Short Scope>

**Goal:** <one-line: what are you scoring?>

**Scoring axes:**
- **ROI:** high (conversion lift) / med (trust/scanability) / low (polish)
- **Brand-fit:** yes (premium calm) / maybe (neutral) / no (conversion-density smell)
- **Effort:** trivial (config) / small (new prop) / medium (new component) / large (new data model)

---

## Patterns / Findings

### <ID>-1 — <Pattern Name>

| Axis | Score | Reasoning |
|------|-------|-----------|
| ROI | high/med/low | <why> |
| Brand-fit | yes/maybe/no | <why> |
| Effort | trivial/small/medium/large | <evidence: file:line> |
| **Net** | **KEEP / DOWNGRADE / DROP** | <one-line summary> |

---

## Reuse Notes
- <existing util/component to reuse, with file path>

## Critical Bug Found (if any)
- **P0:** <description + evidence file:line>

## Related
- [[r2-skeptic]]
- [[r3-leader-synthesis]]
- [[<feature-specific notes>]]
```

## Rules

1. **Score all 3 axes** for every pattern. No "effort TBD" — cite file:line.
2. **Cite evidence**: file path + line range. "Inline code span" for paths, not wikilinks.
3. **Code symbols are inline code**: `\`useAuthRedirect\`` not ``useAuthRedirect``.
4. **One verdict per pattern**: KEEP / DOWNGRADE / DROP / DEFER P3.
5. **Pre-flag backend debt** in a separate table — don't score it.
6. **Length target**: 50-150 lines. If > 200, split out atoms to `03-knowledge/`.
7. **End with `## Related`** linking siblings (`r2-skeptic`, `r3-leader-synthesis`).

## Anti-patterns

- "Dark pattern" / "critical" / "blocker" without evidence
- P0 labels for hygiene issues
- Duplicate findings across specialists
- Code symbol wikilinks (``theme.js`` is wrong)
- No frontmatter
- No evidence file:line
