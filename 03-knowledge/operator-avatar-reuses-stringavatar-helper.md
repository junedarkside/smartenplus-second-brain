---
name: operator-avatar-reuses-stringavatar-helper
description: Broken/missing operator logo images should fall back to a colored letter-avatar (stringAvatar helper, already used for user profile avatars), not the SmartEnPlus brand icon — new shared OperatorAvatar component, reuse-first over inventing a new pattern.
metadata:
  type: decision
---

# Operator Avatar Falls Back to Letter-Avatar, Not SmartEnPlus Icon

## Summary

When an operator's logo image is missing or fails to load, render a colored circle with the operator's initial (deterministic name→color hash) instead of substituting SmartEnPlus's own logo. Reuses `stringAvatar()` (`helpers/avatarHelpers.js`), already shipped for user profile avatars (`components/UI/ProfileHeader.js`) — this session's contribution is a new `components/UI/OperatorAvatar.js` wrapper that reads that helper for its fallback branch instead of an image-based one.

## Why the smartenplus-icon fallback was rejected

First fix attempt (shipped, then superseded same session) used `smartenplus.svg` as the fallback, matching the one place that already had error-handling (`TripDetailsAttribute.js`). User asked directly: "why smartenplus icon, not a colored round icon with the operator's first char?" BD/UXUI review surfaced two real problems with the icon approach:

- **Misattribution** — every operator with a broken logo shows the *same* SmartEnPlus logo, which reads as "these are all SmartEnPlus's own services" on a marketplace-style list where operator identity is part of the trust signal.
- **Indistinguishability** — a user scanning several cards with broken images sees identical icons and may read it as a rendering bug (which, in the reported screenshot, it partly was).

Letter-avatar solves both: still branded to the specific operator (a colored "L" reads as Lomprayah, not us), and visually distinct card-to-card.

## Implementation

`components/UI/OperatorAvatar.js` — `{ src, name, size }` props. Renders `next/image` on the happy path (`onError` state tracked locally), falls back to MUI `Avatar` with `stringAvatar(name)`'s `{ sx: {bgcolor}, children: initial }` spread in, when `src` is falsy OR the image errors. One component, three call sites (`TripItemLayoutV2.js` desktop footer, `TripMobileSummary.js` mobile avatar, `TripDetailsAttribute.js` detail page) — passes the split-test (used in 2+ places, single job, one-sentence description) cleanly, avoided tripling the fallback branch logic across three files.

## Reuse-first lesson

`stringAvatar`/`CustomAvatar` already existed (`helpers/avatarHelpers.js`, `components/UI/CustomAvatar.js`) before this session — found via a `grep -rln "Avatar"` sweep only after the user's question prompted looking, not during the initial bug-fix pass. The initial fix (smartenplus-icon) would have been unnecessary churn if that grep had happened first; worth defaulting to a broader reuse-search sweep before building any new fallback/default-state UI, not just after a design-review nudge.

## Related

[[monolith-audit-500line-rule]]
