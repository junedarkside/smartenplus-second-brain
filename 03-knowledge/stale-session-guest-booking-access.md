# Failed Token Refresh Must Clear the Token, Not Just Flag It

## Summary

next-auth's `jwt`/`session` callbacks marked a session with `error: "RefreshAccessTokenError"` on failed
refresh but kept spreading the **old, dead `accessToken` forward unchanged**. Every consumer checks
`session?.accessToken` truthiness, not `session.error` — so a stale browser session kept sending a
known-dead `Authorization: Bearer <token>` header on every request. Django's global `JWTAuthentication`
rejects that before any view's own `permission_classes` logic runs, including `AllowAny` views with a
public fallback path. **Rule: on refresh failure, null the token fields, not just flag an error.**

## Symptom Signature

- Feature works in incognito / a browser with zero session, fails in a normal browser with an old login.
- Backend logs show `POST /api/token/refresh/ 401` immediately followed by 401s on unrelated endpoints —
  the refresh failure and the subsequent bad requests are two different log lines, easy to read as
  unrelated.
- Any `AllowAny`/public DRF view that's supposed to have a guest fallback (e.g. `?email=` param) instead
  returns "Access denied" / 401 for a real guest.

## Why It Happens

DRF's `DEFAULT_AUTHENTICATION_CLASSES` (`JWTAuthentication` here) runs **before** any view's
`permission_classes` check. `AllowAny` means "no auth required" — it does NOT mean "ignore a bad
`Authorization` header if one is present." A present-but-invalid token is rejected at the authentication
stage; the view's own guest-fallback logic never gets a chance to run.

On the frontend side, next-auth's `refreshAccessToken()` catch block and the `jwt` callback's
refresh-failure branch both did `return { ...token, error: "RefreshAccessTokenError" }` — spreading the
stale `accessToken`/`accessTokenExpiry` forward instead of clearing them. Every RTK Query `prepareHeaders`
and every component-level `if (session?.accessToken)` guard across the app (~50 call sites, grepped) reads
presence of the token as "logged in," not the error flag.

## This Incident (2026-08-20, #333)

Booking-confirmation emails' "VIEW MY BOOKING" deep-link (`/bookings/{id}?email=...`) is designed to work
for guests via an email-param fallback on the backend (`bookings/views.py` `BookingDetailsViewSet`). A
user with an expired session cookie clicked the link, got "Access denied" — the backend's guest branch was
never actually reached, because the frontend still attached the dead token from a failed refresh.

Fix (`pages/api/auth/[...nextauth].js`): null `accessToken`/`accessTokenExpiry` at all 3 places refresh
failure is recorded — the `refreshAccessToken()` early-return, its catch block, and the `jwt` callback's
failure branch — plus a required guard in the `session` callback (`session.accessToken = token.error ?
undefined : token.accessToken`) to heal browsers that already hold a poisoned cookie from before the fix
shipped. `refreshToken` is deliberately kept intact so a later refresh can still recover.

## Rejected Approach: Proactive `signOut()` on Error

A dead file (`hooks/useAuth.js`, zero importers) already implemented "call `signOut()` when
`session.error === 'RefreshAccessTokenError'`." Rejected and deleted: the failing route is a
booking-confirmation deep-link meant to work for **guests** — redirecting to `/account/login` on token
error would break the exact use case the guest fallback exists for. Clearing the token at the source lets
the request correctly fall through to guest access instead of forcing a login redirect.

## Blast Radius Check

Before shipping, grepped every `session?.accessToken` / `session.accessToken` usage app-wide (~50 sites:
chat widget, checkout, payment, forum, blog reactions, passenger management, orders). None of them checked
`session.error` either — meaning all of them already silently sent dead tokens under the same stale-session
condition, just with less visible symptoms (silent 401 on a background poll vs. a customer-facing "Access
denied" page). The source-level fix makes all of them correct for free; no site required an individual
patch.

## Related
- [[booking-item-serializer-name-collision]] — unrelated but same investigation area (bookings app)
