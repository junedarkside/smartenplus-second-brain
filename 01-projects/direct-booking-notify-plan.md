# Direct Booking Notify — Admin Dashboard + Backend

**Date:** 2026-07-01  
**Branch strategy:** `feat/be-booking-item-notify` + `feat/admin-direct-booking-notify`  
**Status:** APPROVED — ready to implement

---

## Context

OTA notify (Phase 3) ships for `CsOtaBooking`. `TripNotification` model supports both `ota_booking FK` and `booking_item FK`. Direct SmartEnPlus bookings at admin `/bookings/[slug]` have no notify UI. Customer-facing `InfoUpdateNotice` already renders `notifications[]` from `BookingItemDetailSerializer` — so FE is zero-change once BE endpoints exist.

---

## Grill Audit Results

| # | Question | Answer |
|---|---------|--------|
| G1 | `booking.id` DB PK available in admin? | YES — `BookingItemDetailSerializer` `fields='__all__'`, `data[0].id` = DB PK |
| G2 | Slug vs DB id confusion? | Page URL uses slug (query param), notify endpoints use DB id — both in same response. No ambiguity |
| G3 | RTK vs axios mixing? | Core fetch stays axios. Notify-specific hooks use RTK csApi (already in store). Clean separation |
| G4 | `NOTIFY_CATEGORIES` DRY? | Inline in `[slug].js` — no shared import (isolated page, no FE component shares this) |
| G5 | `ActionDialog` reuse? | YES — `components/utils/ActionDialog.jsx` imported, same pattern as command-centre |
| G6 | Edit/delete shared endpoint? | `PATCH/DELETE /api/cs/notifications/<pk>/` already works for both OTA and direct. Reuse. Add `booking_type` param to invalidation |
| G7 | Circular import W8? | Still deferred — `bookings/serializers.py` → `cs/serializers.py` safe at runtime |
| G8 | Over-engineering risk? | No new component files. Dialog inline. State local. No new RTK slice. 4 files only |

---

## 4 Files Changed

### 1. `smartenplus-backend/cs/views.py`

Add 2 new view classes (mirror of OtaNotifyView / OtaBookingNotificationsView):

**`BookingItemNotifyView`** — `POST /api/cs/bookings/<pk>/notify/`
- Looks up `BookingItem` by `pk`
- Validates `body` non-empty, `category` in `CATEGORY_CHOICES`
- Creates `TripNotification(booking_item=booking, category=..., body=..., sent_by=request.user)`
- Returns `{'status': 'sent'}` 201

**`BookingItemNotificationsView`** — `GET /api/cs/bookings/<pk>/notifications/`
- Looks up `BookingItem` by `pk`
- Returns `TripNotificationAdminSerializer` (includes `sent_by_name`) with `select_related('sent_by')`

Import: add `BookingItem` to imports from `bookings.models`.

### 2. `smartenplus-backend/cs/urls.py`

```python
path('bookings/<int:pk>/notify/', BookingItemNotifyView.as_view(), name='booking-item-notify'),
path('bookings/<int:pk>/notifications/', BookingItemNotificationsView.as_view(), name='booking-item-notifications'),
```

### 3. `admin-dashboard/store/api/csApi.js`

- Add `'BookingItemNotifications'` to `tagTypes`
- Add `sendBookingItemNotification` mutation → `POST /api/cs/bookings/${booking_pk}/notify/`
- Add `getBookingItemNotifications` query → `GET /api/cs/bookings/${booking_pk}/notifications/`
- Update `updateTripNotification` + `deleteTripNotification` `invalidatesTags` to support `booking_type` param:
  ```javascript
  invalidatesTags: (_, __, { booking_pk, booking_type = 'ota' }) => [
    { type: booking_type === 'direct' ? 'BookingItemNotifications' : 'OtaBookingNotifications', id: booking_pk }
  ]
  ```
- Export `useSendBookingItemNotificationMutation`, `useGetBookingItemNotificationsQuery`

**Backward compat:** OTA callers pass no `booking_type` → defaults to `'ota'` → existing behavior unchanged.

### 4. `admin-dashboard/pages/bookings/[slug].js`

**Imports to add:**
- `NotificationsIcon` from `@mui/icons-material`
- `Select`, `MenuItem`, `TextField`, `FormControl`, `InputLabel`, `IconButton` from `@mui/material`
- `EditIcon`, `DeleteIcon`, `SaveIcon`, `CancelIcon as CancelEditIcon` from `@mui/icons-material`
- `ActionDialog` from `@/components/utils/ActionDialog`
- `useSendBookingItemNotificationMutation`, `useGetBookingItemNotificationsQuery`, `useUpdateTripNotificationMutation`, `useDeleteTripNotificationMutation` from `@/store/api/csApi`

**State (7 vars, all local):**
```javascript
const [notifyOpen, setNotifyOpen] = useState(false)
const [notifyCategory, setNotifyCategory] = useState('other')
const [notifyBody, setNotifyBody] = useState('')
const [notifyError, setNotifyError] = useState('')
const [isNotifying, setIsNotifying] = useState(false)
const [editingId, setEditingId] = useState(null)
const [editBody, setEditBody] = useState('')
const [deletingId, setDeletingId] = useState(null)
```

**NOTIFY_CATEGORIES constant** (above component):
```javascript
const NOTIFY_CATEGORIES = [
  { value: 'boarding', label: 'Boarding Update' },
  { value: 'pickup',   label: 'Pickup Update' },
  { value: 'weather',  label: 'Weather Notice' },
  { value: 'delay',    label: 'Delay Notice' },
  { value: 'other',    label: 'Other' },
]
```

**RTK hooks** (inside component, after `booking = data[0]`):
```javascript
const [sendBookingItemNotification] = useSendBookingItemNotificationMutation()
const [updateTripNotification] = useUpdateTripNotificationMutation()
const [deleteTripNotification] = useDeleteTripNotificationMutation()
const { data: existingNotifications = [] } = useGetBookingItemNotificationsQuery(
  booking?.id,
  { skip: !booking?.id || !notifyOpen }
)
```

**Button** — in action bar alongside `CreateTicket`:
```jsx
<Button variant="outlined" size="small" color="info"
  startIcon={<NotificationsIcon />} onClick={() => setNotifyOpen(true)}
  sx={{ width: { xs: '100%', sm: 'auto' } }}>
  Send Trip Update
</Button>
```

**ActionDialog** — same `extraContent` structure as command-centre OTA notify dialog:
- Category `Select` + body `TextField` multiline
- Error alert if `notifyError`
- "Send" action button (primary tone, loading=isNotifying)
- Existing notifications list with edit/delete per row (same icon pattern as command-centre)

**onClose resets all 8 state vars.**

---

## Impact Analysis

| Component | Changed | Risk |
|-----------|--------|------|
| FE customer `InfoUpdateNotice` | NO | Already renders `notifications[]` |
| `BookingItemDetailSerializer` | NO | Already returns `notifications[]` |
| `BookingItemDetailViewset` | NO | Already `prefetch_related('notifications')` |
| `[slug].js` core axios fetch | NO | Only new state + RTK hooks added |
| `CreateTicket.js` | NO | |
| OTA notify (command-centre) | Minor | `invalidatesTags` adds `booking_type` default='ota' → same behavior |
| `TripNotificationDetailView` | NO | Shared PATCH/DELETE endpoint |

---

## Verification Steps

1. BE: `python manage.py shell` → `POST /api/cs/bookings/<id>/notify/` with staff token → 201
2. Admin: `/bookings/<slug>` → "Send Trip Update" button visible
3. Open dialog → select category, enter body → Send → list updates
4. Customer: `/bookings/<slug>` (FE) → `InfoUpdateNotice` banner visible
5. Edit body in dialog → PATCH → list refreshes
6. Delete → DELETE → list refreshes
7. Empty body → validation error shown, no API call
8. Close + reopen dialog → state reset, fresh list
9. OTA notify (command-centre) → regression — still works

---

## No-Change Files

- `smartenplus-frontend` — zero changes needed
- `smartenplus-backend/bookings/` — zero changes needed
- `admin-dashboard/components/` — zero new components
