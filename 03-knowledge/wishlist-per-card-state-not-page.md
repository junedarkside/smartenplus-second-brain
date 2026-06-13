# Wishlist Per-Card State Not Page

## Summary
Per-card `useState` for the heart icon in `DayTripCard.js`; never lift wishlist state to the page level (causes 80 re-renders per click). Backend wishlist endpoint does not exist yet — stub is correct.

## Context
The favorite/wishlist heart icon appears on every card in marketplace grids (experiences, activities, search results). When the toggle was first implemented it lifted the `isFavorited` boolean and the optimistic-update function to the page component. A single click on a heart re-rendered every visible card. With 20 cards on screen and 4 grid positions, that was 80 React re-renders per click — visible jank on lower-end devices.

## Problem
Two issues:
1. **Re-render storm:** lifting toggle state forces all sibling cards to reconcile even though their props haven't changed.
2. **Premature coupling:** the page component now owns wishlist state for every card, creating prop drilling and a single source of truth that scales poorly.

## Details
The right shape — each card owns its optimistic state:

```jsx
function DayTripCard({ dayTrip }) {
  const [isFavorited, setIsFavorited] = useState(dayTrip.is_favorited);

  const toggleFavorite = async (e) => {
    e.stopPropagation();
    const next = !isFavorited;
    setIsFavorited(next);            // optimistic
    try {
      await api.post(`/day-trips/${dayTrip.id}/favorite/`, { active: next });
    } catch {
      setIsFavorited(!next);         // rollback
    }
  };

  return (
    <button onClick={toggleFavorite} aria-pressed={isFavorited}>
      <HeartIcon filled={isFavorited} />
    </button>
  );
}
```

Because the endpoint is not yet built, the `await` rejects immediately and the rollback fires — but the UI still feels responsive. The stub is the correct intermediate state; do NOT build a global Redux slice yet.

## Decision
Per-card local state until a real backend endpoint and a cross-page wishlist page (where global state is actually needed) both exist. At that point, introduce RTK Query with `providesTags: ['Wishlist']` and a single `getWishlist` query.

## Tradeoffs
- Per-card state means the heart doesn't sync if a card appears twice on the page (rare but possible in recommendation rails). Acceptable for now.
- Stub rollback is misleading: the user sees the heart fill then unfill on a no-op endpoint. Add a console.warn so devs know it's stubbed.
- Lifting to Redux now would be premature — there's no cross-card consistency requirement yet.

## Consequences
Reusable for any optimistic-UI toggle (bookmark, follow, "in cart" pill) across a card grid. The rule: **card-local UI state stays card-local** until a sibling component needs to read it. Audit pattern: any `useState` that lives in a parent of a card grid and only one card consumes it is a refactor candidate.

## Related
- [[react-state-no-op-guard-side-effect-prevention]] — same family: don't trigger effects when state didn't change.
- [[gtm-impression-dedup-sessionstorage]] — impression tracking also needs per-card dedup, not page-level.
- [[rtk-cart-tag-invalidation-auto-refetch]] — when global wishlist state IS justified, this is the eventual shape.
