---
name: frontend-jest-mui-components-fail-to-render
description: Every `@mui/material` component (Chip, IconButton, Button, Drawer) throws "Element type is invalid... got object" when rendered via RTL in the frontend repo's current jest setup — pre-existing, not scoped to one component.
metadata:
  type: knowledge
  status: active
  date: 2026-08-14
  parent: trip-card-cta-column-redesign
---

# Frontend Jest: MUI Components Fail to Render

## Summary
Any `@mui/material` import rendered through `@testing-library/react` in the `smartenplus-frontend` repo throws `Element type is invalid: expected a string... but got: object`. Confirmed project-wide, not scoped to `Chip` or any single component — a bare `<IconButton>x</IconButton>` fails identically to `<Chip label="x" />`.

## Why It Matters
Blocks writing any RTL test that touches a component using MUI internally, directly or via a child. Discovered while trying to add a required click-isolation test (`BookButton` click shouldn't bubble to `onTripClick`) for the trip-card CTA redesign — the test target itself doesn't need MUI, but its sibling tree (`IconButton` for the accordion chevron, `ContractTypeBadge`'s `Chip`) does, so the whole render tree fails.

## Detail
**Isolation method used** (repeat this to confirm the bug still exists before assuming a fix landed):
```jsx
import { render } from '@testing-library/react';
import { IconButton } from '@mui/material';

test('IconButton', () => { render(<IconButton>x</IconButton>); });
```
This fails on its own, proving the break is in jest's MUI module resolution, not in any project component.

**Likely cause (not yet confirmed/fixed):** `jest.config.js` uses `next/jest`'s default `transformIgnorePatterns`, which typically excludes `node_modules` from transformation — but MUI ships some packages as ESM, which Next's SWC/babel transform needs to explicitly include via a pattern like `transformIgnorePatterns: ['node_modules/(?!(@mui)/)']`. The repo's current `transformIgnorePatterns` only has `'node_modules/(?!(.*\\.mjs$))'` — may not cover all of MUI's ESM entry points.

## Constraints / Gotchas
- Don't add ad-hoc `jest.mock('@mui/material', ...)` per-test as a workaround — that masks real component behavior and doesn't fix the underlying config gap for the next person.
- Fix belongs in `jest.config.js` (`transformIgnorePatterns` or `moduleNameMapper`), not in individual test files.

## Related
- [[trip-card-cta-column-redesign]] — where this was found (#309)
- Vault Section 2 open item: `FE-JEST-MUI-BROKEN`
