---
name: hybrid-mui-preserve-tailwind-new-styling-strategy
description: Hybrid strategy: preserve MUI for existing admin-dashboard components, use Tailwind-first for new styling. Semantic tokens only for 5+ reuse. Avoids full rewrite, gradual migration path.
metadata:
  type: knowledge
  status: active
  date: 2026-06-22
  parent: design_system-audit
---

# Hybrid MUI-Preserve + Tailwind-New Styling Strategy

## Summary
Hybrid strategy: preserve MUI for existing admin components, use Tailwind-first for new styling. Semantic tokens only for 5+ reuse. Gradual migration, no big-bang rewrite.

## Why It Matters
Full MUI→Tailwind rewrite expensive (admin-dashboard has 100+ components). Hybrid approach allows incremental adoption, lower risk.

## Detail
**Strategy (debate #2 outcome):**
- **Existing components:** Keep MUI (DataGrid, TextField, Button, etc.). Touch only if broken.
- **New components:** Tailwind-first. Use MUI only if complex component needed (DataGrid, DatePicker).
- **Semantic tokens:** Extract to `designSystem.js` ONLY if reused ≥5 times across app. One-off values stay inline.

**Rules:**
```jsx
// OK — Tailwind new component
<div className="bg-white border rounded-lg shadow p-4">

// OK — MUI existing (unchanged)
<TextField label="Email" variant="outlined" />

// OK — Hybrid (new but needs MUI DatePicker)
<DatePicker />  // Complex, keep MUI

// NO — Don't extract to token if <5 uses
padding="8px"  // Inline, fine
// DON'T: const P_8 = '8px'; export const P_8;
```

**Token extraction criteria:**
- Spacing: margin/padding used ≥5 times → token
- Colors: custom brand colors used ≥5 times → token
- Otherwise inline Tailwind values.

## Constraints / Gotchas
Don't create "utility" tokens for 1-2 uses. Token library bloats fast. Audit before adding: grep usage count first.

## Related
- [[design-system-audit]] — parent audit (debate outcomes, 5-phase roadmap)
- [[mui-tailwind-breakpoint-mismatch-sm-600-vs-640]] — companion breakpoint fix
