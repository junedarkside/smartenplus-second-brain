# design-system-missing-tokens-gaps

## Summary
Four system-level gaps in `helpers/designSystem.js` that force components to invent values: no circular radius, OPACITY scale unmapped to Tailwind, no sub-caption font sizes, no error-tinted background.

## Why It Matters
These gaps are the root cause of repeated token violations — components hardcode `rounded-full`, `bg-white/20`, `0.7rem`, `bg-red-50` because no token exists. Audits keep flagging the same families until the tokens are added. Track them as a system todo, not per-component bugs.

## Detail
| Gap | Symptom | Fix |
|-----|---------|-----|
| No circular radius token | `rounded-full` hardcoded in 4 components | Add `BORDER_RADIUS.circle: '50%'` or `'9999px'` |
| `OPACITY` scale not mapped to Tailwind | 6 components use `bg-white/20` etc. | Add Tailwind `backgroundOpacity` mapping in config |
| No `0.7rem`/`0.85rem`/`0.9rem` in `TYPOGRAPHY_SCALE` | Components invent sizes | Enforce `caption` (12px) as minimum; ban sub-caption |
| No error-state tinted background | `bg-red-50` used for error UI | Add `COLORS.status.errorLight` or `COLORS.badge.error.bg` |

## Constraints / Gotchas
- These are SYSTEM gaps, distinct from component bugs (wrong token where a correct one exists). Fix the token layer once vs. patching every component.
- Sub-caption font sizes (`0.7rem`) below accessibility floor — ban, don't tokenize.

## Related
- [[design-system-audit-activity-detail]] — audit that surfaced these gaps
- [[design-system-audit]] — project-wide audit + migration roadmap
- [[design-systems]] — token inventory
