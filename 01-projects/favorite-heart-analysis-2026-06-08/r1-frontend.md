## Frontend Status

### ADR Compliance
- BookmarkButton icon+variant: SHIPPED `components/blog/BookmarkButton.js:31-32` (props), `:105-129` (overlay JSX). Heart icons imported `:4-5`. `IconButton` imported `:6`. Matches ADR spec.
- DayTripCard wired: SHIPPED `components/activities/browse/DayTripCard.js:16,20` (dynamic+ssr:false), `:123-133` (mount). Local state heart fully removed.
- axiosInstance fix: MISSING. `BookmarkButton.js:41-45` still inline; `:65` dep array still has `axiosInstance` → fires fetch every render until state stabilizes.
- LikeButton axiosInstance: MISSING `components/UI/LikeButton.js:18-22` (inline), `:41` (dep). Same bug. Pre-existing per ADR.

### N+1 Hydration Risk
`FilterDayTripsPage.js:53` hardcodes `pageSize: 12` → 12 `DayTripCard` per page → 12 `BookmarkButton` → 12 `axios.create()` + 12 `/check/` calls per render cycle. With `axiosInstance` inline bug, the setBookmarked bail-out masks the storm (1-2 cycles), but parent re-render (filter change, currency swap, sort) re-triggers full flood. Q2 fix (defer hydration via `useEffect` on intersection/visibility) reduces this to 0 on initial load + N only on user-visible cards. Confirmed: Q2 → 0 baseline + lazy on scroll.

### Hook Pattern Recommendation
Match `useAuthRedirect.js:3-17` (factory function, returns object, consumer destructures). Signature:

```js
export const useAuthAxios = () => {
  const { data: session } = useSession();
  const token = session?.accessToken;
  const instance = useMemo(() => axios.create({
    baseURL, headers: { Authorization: `Bearer ${token}` }
  }), [token]);
  return { instance, token, isAuthenticated: !!token };
};
```

Return `instance` (not wrapper) — minimal API change, callers keep `.get/.post/.delete`. Drop `useMemo` dep on token only; effect deps become `[contentType, objectId, token]`. Place at `components/utils/useAuthAxios.js` to match neighbour hooks (`useAuthRedirect`, `useCommentSubmit`, `useDebounce`).

### Accessibility Check
- 44×44 touch target: NO. `BookmarkButton.js:108` `size="medium"` → MUI default 40×40. Below WCAG 2.5.5 recommended 44. Bump to `size="large"` (48) or wrap in 44px box.
- aria-label dynamic: YES `:117` toggles `'Save to wishlist'` / `'Remove from wishlist'`. Good.
- Focus ring visible: NO. Default MUI `IconButton` focus ring is faint. Add `&:focus-visible` outline in `sx` like DayTripCard `:107-110`.
- Contrast #E11D48 on rgba(255,255,255,0.8): PASS (ratio ~5.0:1, exceeds 3:1 graphical). `text.secondary` on same bg: PASS.

### Frontend Tasks (in priority order)
1. `[BookmarkButton.js:41-45,65] [wrap axiosInstance in useMemo([token]); switch dep to [contentType,objectId,token]] [S] [low — guarded by state bail-out]`
2. `[LikeButton.js:18-22,41] [same useMemo fix; share via new useAuthAxios hook] [S] [low]`
3. `[components/utils/useAuthAxios.js] [new file — match useAuthRedirect pattern; return {instance,token,isAuthenticated}] [S] [none — additive]`
4. `[BookmarkButton.js:108] [size="medium" → "large" for 48px (or add sx minWidth/minHeight 44) to meet WCAG 2.5.5] [XS] [low]`
5. `[BookmarkButton.js:107-118] [add '&:focus-visible': { outline: '2px solid #1E40AF', outlineOffset: 2 } to overlay sx] [XS] [low]`
6. `[DayTripCard.js:127-132] [defer hydration: BookmarkButton stays dynamic(ssr:false); consider gating fetch on IntersectionObserver or mouseenter to cut N+1 to 0] [M] [med — adds complexity but fixes real perf issue]`
7. `[DayTripCard.js:20] [move dynamic import above first use — code review order nit, no behavior change] [XS] [none]`
