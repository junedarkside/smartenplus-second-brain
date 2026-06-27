---
name: new-2-partner-case-id-closed
description: NEW-2 closure — partner_case_id field not needed, existing (source, booking_id) provides OTA case tracking
metadata:
  type: decision
  status: closed
  date: 2026-06-27
  parent: cs-workflow-revised-2026-06-27
---

# NEW-2 — `partner_case_id` Field CLOSED

**Status:** NOT NEEDED — Existing mechanism covers this use case  
**Date:** 2026-06-27  
**Decision:** Closed. No implementation needed.

---

## What Was Proposed

Add `partner_case_id` field to Ticket model for OTA case deduplication:

```python
# PROPOSED (NOT IMPLEMENTED)

class Ticket(models.Model):
    partner_case_id = CharField(max_length=100, null=True, blank=True)
    # Examples: "KH-12345", "12GO-67890"
```

**Intended purpose:** When OTA forwards customer request to SmartEnPlus, admin records OTA case ID to prevent duplicate tickets.

---

## Why Not Needed

**Existing `(source, booking_id)` composite key on `CsOtaBooking` already provides OTA case tracking.**

```python
# EXISTING (already in codebase)

# cs/models.py
class CsOtaBooking(models.Model):
    source = CharField(max_length=20)      # '12go', 'klook'
    booking_id = CharField(max_length=100) # OTA case reference
    
    class Meta:
        unique_together = [['source', 'booking_id']]

# tickets/models.py
class Ticket(models.Model):
    content_type = FK(ContentType)
    object_id = PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    # Phase 2: content_object → CsOtaBooking (OTA bookings)
```

**Linking path:**
```
CsOtaBooking(source='klook', booking_id='KH-12345')
    ↑
Ticket.content_object (via GenericFK)
```

**To access OTA case ID from ticket:**
```python
ticket.content_object.booking_id  # Returns 'KH-12345'
ticket.content_object.source       # Returns 'klook'
```

---

## Deduplication Already Works

**Scenario: Klook forwards customer change request**

```
Day 1: Customer calls Klook → Klook opens case KH-12345
       → Klook emails SmartEnPlus: "Process change for booking KH-12345"

Day 1: Admin creates Ticket:
       → Links to CsOtaBooking(source='klook', booking_id='KH-12345')
       → Ticket.content_object = CsOtaBooking instance

Day 2: If duplicate request arrives:
       → Admin queries: CsOtaBooking.objects.filter(
           source='klook', 
           booking_id='KH-12345'
         ).exists()
       → Finds existing CsOtaBooking → sees linked Ticket
       → Rejects duplicate
```

**No separate field needed.** `(source, booking_id)` composite key IS the deduplication mechanism.

---

## Verified Against Codebase

**Existing GenericFK on Ticket (tickets/models.py:48-52):**
```python
content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
object_id = models.PositiveIntegerField()
content_object = GenericForeignKey('content_type', 'object_id')
# Phase 2: content_object → CsOtaBooking (OTA, source='12go'/'klook')
```

**CsOtaBooking unique constraint (cs/models.py):**
```python
class Meta:
    unique_together = [['source', 'booking_id']]
```

**Both already exist.** No migration needed.

---

## Data Flow

```
Supabase OTA booking (Klook/12Go source)
    ↓ (sync_ota_bookings Celery task)
CsOtaBooking(source='klook', booking_id='KH-12345')
    ↓ (Ticket.content_object GenericFK)
Ticket (request_type='date_change', source='ota')
    ↓ (admin UI)
Admin sees: "Linked to Klook booking KH-12345"
```

Every OTA booking tracked by `(source, booking_id)`. Every OTA ticket links to CsOtaBooking.

---

## Cost Avoided

| Item | Proposed Effort | Actual Effort |
|---|---|---|
| Add `partner_case_id` field | 5min BE + migration | **0** |
| Admin UI for field | 30min FE | **0** |
| API endpoint update | 30min BE | **0** |
| **Total** | **1 hour BE + 30min FE** | **0** |

---

## Decision

**CLOSED.** `partner_case_id` field NOT needed.

Existing mechanism:
- `CsOtaBooking` has `(source, booking_id)` composite unique key
- `Ticket.content_object` GenericFK links to `CsOtaBooking`
- OTA case ID accessible via `ticket.content_object.booking_id`

**Confidence:** HIGH — verified against existing code (tickets/models.py:48-52, cs/models.py).

---

## Related

[[cs-workflow-revised-2026-06-27]] — Main workflow decision document  
[[booking-command-centre-decision]] — Parent decision  
[[cs-architecture-decision]] — CS system architecture
