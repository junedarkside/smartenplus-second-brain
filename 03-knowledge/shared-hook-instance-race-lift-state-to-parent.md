# Shared URL-Syncing Hook — Two Instances Race, Lift State to Common Parent

**Problem:** A hook that syncs local state to the URL (`router.push` on every change) is safe with exactly one live instance. The moment a second component tree needs the same state and calls the hook itself instead of receiving it as props, you get two independent state machines both writing to the same URL — race on write order, duplicate/conflicting state, possible flicker as each corrects toward what it thinks the URL should be.

**Example:** `hooks/useDayTripFilters.js` syncs `filters` to the URL via `router.push` (own code comment already warns: sync is "gated on hydration and enabled to prevent secondary instances racing"). `ActivitySearch.js` supports both controlled (`filters`/`updateFilter` props) and uncontrolled (calls its own `useDayTripFilters()`) modes. `FilterDayTripsPage.js` already called the hook and rendered one `ActivitySearch` in controlled mode. Adding a second `ActivitySearch` instance elsewhere on the page (e.g. inside a hero overlay) in uncontrolled mode would spin up a second `useDayTripFilters()` — exactly the race the hook's own comment warns about.

**Fix:** Single owner, lifted to the nearest common ancestor. `pages/activities/index.js` (the page component, common parent of both consumers) becomes the sole caller of `useDayTripFilters()`, passes `filters`/`updateFilter` down as props to both the hero's `ActivitySearch` (controlled mode, already supported, zero changes to the component itself) and `FilterDayTripsPage` (which had to switch from calling its own hook to receiving props instead — same controlled-prop pattern `ActivitySearch` itself already used, so the target shape already existed in the codebase, just needed to be applied one level up).

Related concrete fallout when lifting: any other hook tied to a specific rendered element (e.g. `useStickyVisibility`'s `IntersectionObserver` ref) has to move with whichever component now owns the DOM node it targets — a ref can't be created in a child and attached to a parent-rendered element, so once the search bar moved into the hero (in the parent), `useStickyVisibility` had to move up too, not stay behind in the child that no longer renders that DOM node.

**Detection heuristic:** before adding a second render site for any component that internally calls a stateful hook, check if that hook syncs to a shared store (URL, localStorage, a singleton). If yes, the new render site needs controlled/prop-driven mode, not another independent hook call — check whether the component already supports both modes (many do, via a `propsGiven !== undefined ? controlled : ownHook()` branch) before building anything new.

**Severity:** would have been a live bug (URL flicker/inconsistent filter state) if shipped uncontrolled — caught in planning via a specialist review reading the hook's own warning comment, not discovered live.

Part of hero-banner Activities page work, #335. See [[use-day-trip-filters-hydration-spurious-push]] for a different bug on the same hook (hydration-timing URL overwrite, not multi-instance racing).

## Related
- [[use-day-trip-filters-hydration-spurious-push]] — different bug, same hook, cross-link
- `hooks/useDayTripFilters.js`
- `components/activities/shared/ActivitySearch.js` (controlled/uncontrolled dual-mode precedent)
- `hooks/useStickyVisibility.js` (ref-follows-DOM-node fallout)
- CLAUDE.md: "useEffect chains forbidden" (related simplicity principle — don't add a second effect chain to work around a lifted-state gap)
