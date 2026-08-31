# Tailwind classes silently no-op inside MUI Dialog (admin-dashboard)

## Summary
Any Tailwind utility class used inside a component that renders inside a MUI `Dialog` will silently fail to apply — no error, no warning, just dead CSS. Affects the shared Tiptap toolbar (`components/editor/MenuBar.js`) and will affect any future component with the same shape.

## Context
`admin-dashboard/tailwind.config.js` sets `important: '#__next'` — every compiled Tailwind utility's CSS selector is scoped to `#__next .classname { ... !important }`. `#__next` is Next.js's default page-root div. MUI's `Dialog` component portals its content to `document.body` by default, **outside** `#__next` in the DOM tree. A Tailwind class applied to an element inside a Dialog therefore never matches its own compiled selector — it's present in the `class` attribute but has zero effect.

## Problem
This surfaced twice in the same component during the same session (#370), as two different symptoms:
1. `hidden md:flex` / `flex md:hidden` (responsive show/hide) — both the "desktop" and "mobile" toolbar rows rendered simultaneously inside a dialog, since neither `hidden` nor its `md:` override ever applied. Outside a dialog, this pattern works fine.
2. `flex flex-wrap items-center gap-0.5` (layout) — after fixing (1) with a JS-based `useMediaQuery` check instead of Tailwind breakpoints, the container still fell back to block-stacking (one button-group per row) because `flex`/`flex-wrap` themselves never applied either.

Neither failure throws, lints, or shows up in a build — it's a pure visual/layout bug only caught by looking at the rendered page.

## Detection
- Bug only reproduces **inside a MUI Dialog** (or any other component that portals outside `#__next` — `Popper`, `Menu`, `Tooltip` with default `disablePortal={false}`, etc.). The exact same component renders correctly when NOT inside a portal.
- Check `tailwind.config.js` for an `important: '#selector'` scope config before assuming Tailwind classes "should just work" anywhere in this codebase.
- A working component in the same file/codebase that uses MUI `Box`+`sx` for the identical layout (not Tailwind classes) and has never shown the bug is a strong tell — compare against it.

## Decision
Fix: don't use Tailwind utility classes in any component that might render inside a MUI Dialog/Popper/Menu. Use MUI's `sx` prop (real inline styles, immune to selector-scoping) instead — exactly like `components/editor/MenuBar.js`'s `compact` branch already did, which is why that branch never showed either bug.

## Consequences
- Any OTHER component that both (a) uses Tailwind classes for layout/responsive behavior and (b) can render inside a Dialog/Popper/Menu/Popover in this admin-dashboard has the same latent risk, unconfirmed until someone opens it inside a portal. `MenuBar.js` is also used by `components/location/locationEdit.js` and `components/forms/contract/DayTripDetails.js` — both dialogs, both share this exact fix now.
- Don't blanket-remove `important: '#__next'` from `tailwind.config.js` to "fix this at the root" — that changes specificity/behavior for the entire app, far wider blast radius than the actual bug.

## Related
- `components/editor/MenuBar.js`
- [[mui-autocomplete-oninputchange-reset-clobbers-selection]]
