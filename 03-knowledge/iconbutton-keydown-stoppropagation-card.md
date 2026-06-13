# IconButton Keydown stopPropagation Card

## Summary
IconButton inside a click+keydown-handled card wrapper needs BOTH `onClick={(e) => e.stopPropagation()}` AND `onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') e.stopPropagation(); }}` — otherwise keyboard users toggle the icon AND navigate to the card.

## Context
The favorite-heart analysis (2026-06-08) Skeptic Finding 3 flagged a keyboard a11y bug: a `Card` component handled both `onClick` (mouse navigation) and `onKeyDown` (Enter/Space to navigate) to make the whole card a clickable surface. An `IconButton` heart inside the card stopped `click` propagation but did NOT stop `keydown`. Result: a keyboard user pressing Enter on a focused card both toggled the heart AND navigated to the detail page — an a11y blocker and a double-action surprise for screen-reader users.

## Problem
React's `onClick` and `onKeyDown` are separate event systems. Devs who remember to stop click propagation habitually forget to stop keyboard propagation, especially when the parent component provides the keyboard handler. The browser still fires the card-level handler because the keyboard event bubbles independently of the click event.

## Details
The correct pattern:

```jsx
function Card({ onSelect, children }) {
  return (
    <div
      role="button"
      tabIndex={0}
      onClick={onSelect}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          onSelect();
        }
      }}
    >
      {children}
    </div>
  );
}

function HeartButton({ active, onToggle }) {
  return (
    <IconButton
      onClick={(e) => { e.stopPropagation(); onToggle(); }}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') e.stopPropagation();
        // let IconButton's own handler run for activation
      }}
      aria-pressed={active}
      aria-label={active ? 'Remove from favorites' : 'Add to favorites'}
    >
      <HeartIcon filled={active} />
    </IconButton>
  );
}
```

Critical points:
- `e.stopPropagation()` in `onKeyDown` is the missing piece. It does not prevent the IconButton from receiving the event; it prevents the bubble to the card wrapper.
- Do NOT `e.preventDefault()` on the IconButton's keydown — that breaks the button's own activation.
- `aria-pressed` is required because the heart is a toggle, not a one-shot action.

## Decision
Every nested button inside a clickable card wrapper MUST stop both click and keydown propagation. The wrapper's keydown handler must check for Enter and Space (both trigger activation in browsers).

## Tradeoffs
- Slight redundancy: the parent handler runs once for the card nav, the child handler runs once for the icon — both see the keydown, both stopPropagation from the icon's perspective only.
- A more architectural fix is to make the card NOT a button (`role="article"`) and put a real `<Link>` around it; but that loses the "click anywhere on card" affordance.
- Screen reader testing (NVDA, VoiceOver) is the only reliable verification — keyboard event simulation in jsdom does not catch this.

## Consequences
Reusable for any nested button inside a clickable card: heart, share, quick-view, add-to-cart, compare. Audit: any `onClick={... stopPropagation ...}` without a matching `onKeyDown` is a bug. The [[wcag-touch-target-enforcement]] rule already requires 44×44px tap targets; this rule completes the keyboard story.

## Related
- [[wcag-touch-target-enforcement]] — sibling a11y rule for clickable surfaces; same review checklist.
