# nextjs-double-sticky-sidebar-silent-break

## Summary
Nesting a `<StickySidebar>` inside another `<StickySidebar>` breaks sticky positioning silently — no runtime error, no console warning. The inner element just doesn't stick (or jitters). Detection is visual only.

## Why It Matters
A common refactor — wrapping a booking widget that already self-wraps in StickySidebar — produces a "working build, broken UX" with zero error signal. Easy to ship. The fix is structural: only ONE StickySidebar in the ancestor chain.

## Detail
Anti-pattern (silent break):
```jsx
// DayTripBookingWidget.js internally returns:
<StickySidebar><Card>...</Card></StickySidebar>

// Page wraps it again:
<StickySidebar><PremiumBookingPanel><DayTripBookingWidget/></PremiumBookingPanel></StickySidebar>
// → double sticky, broken
```
Fix: remove StickySidebar from the child component; place it once at the page level. When building a wrapper around a self-stickying component, the wrapper must NOT re-sticky.

## Constraints / Gotchas
- No error/warning — smoke-test stickiness visually after any StickySidebar refactor.
- A new wrapper component around an existing sticky component is the trigger. Check the wrapped component's return statement before adding an outer StickySidebar.

## Related
- [[experience-detail-page-redesign]] — PremiumBookingPanel + DayTripBookingWidget source
