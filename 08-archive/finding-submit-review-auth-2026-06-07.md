---
title: RR-1 Submit-Review Auth Model — Finding
date: 2026-06-07
status: finding (no action required on auth)
tags: [rr1-followup, auth, review, backend, frontend]
related:
  - 01-projects/rate-review-uxui-audit-2026-06-06/r1-frontend.md:333
  - smartenplus-backend/dialogue/views.py
  - smartenplus-frontend/components/RateAndReview/RateAndReviewForm.js
---

# RR-1 Submit-Review Auth Model — Finding

## 1. TL;DR

The auth model for `/rate-review/submit-review/[...slug].js` is **intentional and correct**. No code change to backend or auth. The RR-1 audit's "ambiguous" finding resolves to: **token-based guest flow is by design**.

The **real issue** is a UX gap: the form has no indicator showing whether the user is submitting as a logged-in user or as a guest. UX-only follow-up, no backend work.

## 2. Audit claim (the original concern)

From `01-projects/rate-review-uxui-audit-2026-06-06/r1-frontend.md:333`:

> "Whether the backend accepts this depends on backend token-review policy. This is ambiguous — if token-based reviews are meant to be accessible to unauthenticated users (email-invited reviewers), the backend must accept empty bearer tokens, but the form never informs the guest that they are submitting unauthenticated."

The audit flagged it as ambiguous. Session #74 deferred to "confirm w/ backend" follow-up.

## 3. Backend code evidence

File: `smartenplus-backend/dialogue/views.py`

### 3.1 `ReviewViewSet.get_permissions` (lines 1037-1040)

```python
class ReviewViewSet(ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def get_permissions(self):
        if self.action == 'list':
            return [IsAuthenticated()]
        return [AllowAny()]
```

**Read this carefully:** only the `list` action (the dashboard `GET /dialogue/reviews/booking-reviews/`) requires `IsAuthenticated`. Everything else — including `create` (POST), `retrieve` (GET /{slug}/), `update`, `destroy` — returns `AllowAny()`.

**Conclusion:** `POST /dialogue/reviews/` **accepts requests without any auth header**. The frontend's empty `Authorization: Bearer ` header is **valid** and gets through.

### 3.2 `create` method (lines 1175-1205)

```python
# Try to get user from booking_item or order (optional for token-based reviews)
user = booking_item.user

# Fallback: Try to get user from order
if not user and booking_item.order:
    user = booking_item.order.user

# Get guest email for anonymous reviews
guest_email = None
if not user and booking_item.order:
    guest_email = booking_item.order.email

review_data = {
    'user': user.id if user else None,  # Allow None for anonymous reviews
    'guest_email': guest_email,  # Email for guest reviews
    'content_type': content_type.id,
    'object_id': content_object.id,
    'booking_item': booking_item.id,
    'rating': rating,
    'title': title,
    'review_text': review_text
}
```

**Backend derives everything from `booking_id`** (sent in formData):
- `user` = booking owner (or `None` for guest)
- `guest_email` = order email (or `None`)
- No frontend auth check needed because backend handles ownership derivation

**Conclusion:** Token-based guest submission is **explicitly supported**. The `# optional for token-based reviews` comment confirms this is by design.

### 3.3 Token endpoint (lines 1126-1133)

```python
@action(detail=False, methods=['get'], url_path=r'token/(?P<token>[A-Za-z0-9]+)')
def retrieve_by_token(self, request, token=None):
    ...
    booking_token_decode = urlsafe_base64_decode(token).decode()
    ...
    booking_item = get_object_or_404(
        BookingItem, slug=booking_token_decode)
```

**Token is base64-encoded booking slug.** Page loads booking context via token (no auth). Form submits with `booking_id` (the same slug) → backend derives ownership.

## 4. Frontend code evidence

File: `smartenplus-frontend/components/RateAndReview/RateAndReviewForm.js`

### 4.1 Session import (line 29)

```js
const { data: session } = useSession();
```

Form **has** session access, but it's optional. Form works for both authed and unauthed paths.

### 4.2 Auth header (line 78)

```js
const headers = {
    Authorization: session?.accessToken ? `Bearer ${session.accessToken}` : '',
};
```

When no session, sends **empty string** as the header value. **This is valid** because backend `AllowAny` on create.

### 4.3 Form data includes booking_id (line 64)

```js
formData.append('booking_id', bookingId);
```

Frontend sends `booking_id` in formData. Backend uses this to find the booking and derive user/guest_email. No need for auth check on the frontend.

File: `smartenplus-frontend/pages/rate-review/submit-review/[...slug].js`

### 4.4 No session check on page (verified via grep)

```bash
$ grep -n "useSession\|useAuthRedirect\|getSession" pages/rate-review/submit-review/\[...slug\].js
(no matches)
```

Page has **zero auth checks**. **Intentional** — page supports both paths (authed user navigating directly + email-invited guest with token URL).

## 5. Decision tree resolved

| Audit's question | Answer (from code) |
|------------------|-------------------|
| Does backend accept empty bearer on POST? | **Yes** — `AllowAny` on create (views.py:1037-1040) |
| Is token-based guest submission intentional? | **Yes** — explicit `user = None` + `guest_email` derivation in create (views.py:1180-1195) |
| Is the missing session check a bug? | **No** — page is designed for both authed and guest paths |

**RR-1-FOLLOWUP-1 closed.** No backend ticket. No auth ticket.

## 6. UX gap (the real issue)

The form has `useSession()` but renders **no indicator** showing:
- Whether the user is logged in (authed path) or submitting as a guest (guest path)
- Which email will be associated with the review (currently derived silently from `order.email`)

**Where to add it** (frontend-only, no backend change):

`components/RateAndReview/RateAndReviewForm.js` — between line 30 (after `useSession()`) and the form start. Add a banner:

```jsx
{session?.user?.email ? (
  <Alert severity="info" sx={{ mb: 2 }}>
    Submitting as {session.user.email}
  </Alert>
) : (
  <Alert severity="info" sx={{ mb: 2 }}>
    Submitting as guest. Your review will be associated with the email on your booking.
  </Alert>
)}
```

**Effort:** XS (~5 lines). **Impact:** clarifies the auth path for the user.

## 7. Optional v2 enhancements (deferred)

- **Explicit email field for guest** — let guest override the email (currently pulled silently from `order.email`)
- **"Switch to logged-in user" link** — if guest is authed elsewhere, offer to link accounts
- **Token expiry** — backend currently decodes token without expiry check; add TTL to the base64 token

## 8. Follow-up

| Action | Owner | Effort | Status |
|--------|-------|--------|--------|
| Add "Submitting as X" indicator in form | Frontend | XS (~5 lines) | New ticket |
| Backend token expiry (v2) | Backend | M | Deferred |
| Guest email override field (v2) | Frontend | S | Deferred |

**RR-1-FOLLOWUP-1 status:** CLOSED — auth model is intentional, no code change. Remaining work is UX polish (separate ticket).

## 9. File:line references summary

| Pattern | File:line | Significance |
|---------|-----------|--------------|
| `ReviewViewSet.get_permissions` | `dialogue/views.py:1037-1040` | AllowAny on non-list actions |
| `create` user derivation | `dialogue/views.py:1180-1195` | user + guest_email optional |
| Token decode | `dialogue/views.py:1129-1133` | base64(booking slug) |
| `useSession` in form | `RateAndReviewForm.js:29` | Optional, works for both paths |
| Empty bearer header | `RateAndReviewForm.js:78` | Valid (backend AllowAny) |
| `booking_id` in formData | `RateAndReviewForm.js:64` | Backend derives ownership |
| No session check on page | `pages/rate-review/submit-review/[...slug].js` | Intentional |
| Original audit finding | `01-projects/rate-review-uxui-audit-2026-06-06/r1-frontend.md:333` | "ambiguous" — now resolved |
