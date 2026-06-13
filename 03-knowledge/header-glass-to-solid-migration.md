# Header Glass-to-Solid Migration

## Summary
Migrating from glassmorphism header (`backdrop-blur-md` + gradient + dark text) to solid white header (Type A/B split). Required color unblock: `text-white/70` → `text-gray-700` in 5 utility files. MUI AppBar needs `color="inherit"` or `.MuiAppBar-root { background-color: transparent !important }` in globals.css.

## Context
The 2026 header redesign moved from a glassmorphism aesthetic (translucent blur over a colorful background) to a solid white header with clean separation. Glassmorphism worked when the page hero had a strong gradient/photo, but on transactional routes (white background checkout, login) the glass effect was invisible and the dark text on translucent white was unreadable. The new design splits Type A (operational, single row) and Type B (discovery, 2-row with nav) — both solid white.

## Problem
The migration has two non-obvious failure modes:
1. **Color unblock.** Glassmorphism used `text-white/70` for secondary nav text (works on dark/colored backgrounds). On a white header, `text-white/70` is invisible. Five utility files in the header component tree have these classes. None of them fail loudly — they just render unreadable text.
2. **Double-glass bug.** The MUI `AppBar` defaults to a Material-style background. If you apply a `glass-bg` class to the AppBar AND the inner `<div>`, both layers have the glass effect — the inner div blurs the AppBar, which already blurs the page below. Visually noisy. The fix is to set the AppBar's background to `transparent` and put the glass effect only on the inner div. BUT in the new solid-white world, the glass effect is gone entirely — so the AppBar's default background fights the "solid white" intent.

For the solid-white migration, the fix is: `color="inherit"` on MUI AppBar (so it doesn't impose its default theme color) + `.MuiAppBar-root { background-color: transparent !important; }` in globals.css (to override any inline style MUI sets). Then the AppBar's background comes from the parent header div, which is `bg-white`.

## Details
Step 1: replace `text-white/70` with `text-gray-700` (or appropriate gray) in 5 files:
- `components/Header/NavLinks.js`
- `components/Header/UserMenu.js`
- `components/Header/LocaleSwitcher.js`
- `components/Header/CartIndicator.js`
- `components/Header/MobileMenu.js`

Step 2: AppBar background unblock in `styles/globals.css`:

```css
.MuiAppBar-root {
  background-color: transparent !important;
  box-shadow: none !important;
}
```

And in the component:

```jsx
<AppBar position="static" color="inherit">
  {/* children */}
</AppBar>
```

`color="inherit"` makes MUI inherit the parent's color (which is the white div's color). `background-color: transparent` removes the Material default. The `box-shadow: none` removes the elevation shadow that was a glassmorphism-era affordance — solid headers don't need it.

## Decision
- Solid white header is the new default. Glass is removed.
- `text-white/70` → `text-gray-700` in all 5 header utility files
- MUI AppBar uses `color="inherit"` + transparent background override
- The "double glass" pattern (AppBar + inner div both glass-bg) is explicitly forbidden going forward

## Tradeoffs
- Pro: Clean, readable, accessible (WCAG contrast ratios pass on white)
- Pro: Aligns with the broader 2026 brand direction
- Pro: Removes 5 places where dark text on white was invisible
- Con: Loses the "premium glass" look on hero pages. Acceptable trade for accessibility + consistency.
- Con: The MUI `!important` override is a code smell. If MUI updates to remove that override surface, the override stops working and a new solution is needed.
- Con: The 5-file color migration is easy to miss one. Add a CI check that greps for `text-white/` in `components/Header/`.

## Consequences
This is a one-time migration. If brand direction changes again (back to glass, or to a dark theme), the inverse migration will be needed. The pattern — "unblock default background, remove override, fix downstream color classes" — is reusable for any theme shift.

MUI AppBar background override is now a known sharp edge. Document in the MUI + Tailwind integration note. Any new MUI AppBar in the project should start with `color="inherit"` and explicit `background-color: transparent`.

## Related
- [[smartenplus-glassmorphism-header]] — the glassmorphism header atom being replaced
