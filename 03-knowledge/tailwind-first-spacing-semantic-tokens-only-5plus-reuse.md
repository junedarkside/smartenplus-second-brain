---
name: tailwind-first-spacing-semantic-tokens-only-5plus-reuse
description: Tailwind-first for spacing, semantic tokens only for 5+ reuse. Rule prevents token bloat. One-off spacing values stay inline in Tailwind classes; only repeated patterns become tokens.
metadata:
  type: knowledge
  status: active
  date: 2026-06-22
  parent: design_system-audit
---

# Tailwind-First Spacing + Semantic Tokens (5+ Reuse)

## Summary
Tailwind-first for spacing. Semantic tokens ONLY if reused ≥5 times. Prevents token bloat. One-off spacing values stay inline Tailwind.

## Why It Matters
Token libraries explode if every value extracted. Maintenance nightmare. Tailwind's strength = utility classes, not pre-abstraction.

## Detail
**Debate #1 outcome:**

**Tailwind-first:**
```jsx
// PREFERRED — Tailwind utility
<div className="p-4 m-2">  // padding: 1rem, margin: 0.5rem

// OK for 5+ reuse — extract to semantic token
<div className="p-4"> → const spacing = { card: 'p-4 m-2', section: 'p-6' }
```

**Semantic token criteria:**
- Spacing pattern appears ≥5 times across app → token
- Naming by purpose: `spacing.card`, `spacing.section`, NOT `P_16`, `M_8`
- Document in `helpers/designSystem.js`

**Inline allowed:**
```jsx
// FINE — one-off layout
<div className="p-3 lg:p-5">

// DON'T EXTRACT
const P_3 = '0.75rem'; const P_5_LG = '1.25rem';  // Bloat
```

**Enforcement:** Before adding token, `grep -r "p-4"` codebase → if <5 matches, keep inline.

## Constraints / Gotchas
Exceptions: spacing tied to DESIGN SYSTEM (8px grid, 4px baseline) → token even if <5 uses (e.g., icon spacing, touch targets 44px).

## Related
- [[design_system-audit]] — parent audit (debate #1)
- [[hybrid-mui-preserve-tailwind-new-styling-strategy]] — companion strategy
