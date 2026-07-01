# OTA Resolve Guard Patterns

## Summary
Three bypass paths allow `awaiting_ota_update → resolved` transition in `Ticket.clean()`. Time-based guards were removed in session #203 as unnecessary complexity.

## Context
OTA tickets enter `awaiting_ota_update` when admin is waiting for 12Go/Klook to confirm a change. The resolve-block guard prevents premature resolution before OTA responds. Three legitimate bypass paths exist.

## The Three Bypass Paths

### 1. Supabase Event (automatic)
```python
has_event = OtaBookingEvent.objects.filter(
    ota_booking=self.content_object,
    created_at__gte=old_ticket.status_changed_at
).exists()
if has_event:
    return  # OTA confirmed via Supabase sync
```
Triggered automatically when `sync_ota_bookings` Celery task pulls new events from Supabase. No admin action needed.

### 2. `ota_manually_confirmed` flag (admin button)
```python
if getattr(self, '_ota_manually_confirmed', False) and self.request_status == 'resolved':
    return
```
Admin clicks "Done — OTA Confirmed" in Command Centre. FE sends `ota_manually_confirmed: true` in PATCH body. `RequestStatusViewSet.partial_update` sets `instance._ota_manually_confirmed = True` (transient attribute, not persisted). Use when OTA confirmed via phone/email outside the system.

### 3. Emergency bypass
```python
if self.is_emergency and self.request_status == 'resolved':
    return
```
Admin toggles Emergency ON on ticket detail page. Resolves any ticket regardless of status, skipping all guards. Use for urgent cases.

## Decision: Time-Based Guards Removed (session #203)
Originally had 4h/12h time checks after `admin_contacted_ota_at`. Removed because:
- Adds friction with no real benefit — admin knows when to resolve
- `ota_manually_confirmed` is the right bypass for "OTA confirmed but no Supabase event"
- Time waits don't map to real OTA response patterns

## Final Error Message
When none of the 3 bypasses apply:
> "Cannot resolve awaiting OTA ticket. No Supabase update since awaiting started. Use 'Done — OTA Confirmed' button or toggle Emergency ON to bypass."

## File Locations
- Guard logic: `smartenplus-backend/tickets/models.py` `Ticket.clean()` ~line 119–165
- Transient flag set: `smartenplus-backend/tickets/views.py` `RequestStatusViewSet.partial_update` ~line 272
- Admin button: `admin-dashboard/pages/dashboard/command-centre/index.js` `handleOtaConfirmed`
- API field pass-through: `admin-dashboard/store/api/ordersApi.js` `updateRequestStatus` mutation

## Related
- [[cs-centralization-audit-2026-06-29]]
- [[tickets]]
- [[admin-dashboard-cs-centralization-plan]]
