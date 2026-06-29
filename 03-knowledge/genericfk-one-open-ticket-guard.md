# GenericFK — One-Open-Ticket Guard Pattern

**Type:** PATTERN · **Found:** CS-Centralization audit 2026-06-29

## Problem

Multiple booking channels (direct + OTA) can create tickets against the same booking. Without a guard, a customer can open duplicate tickets, corrupting the state machine and creating ambiguous resolution paths.

## Where to put the guard

In `Ticket.clean()` — the existing validation hub, called on model save and via `full_clean()`. Do NOT put it in individual views (it would need to be duplicated).

## Pattern

```python
# tickets/models.py — in Ticket.clean()
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError

def clean(self):
    # existing validations ...

    # One-open-ticket guard — reuses GenericFK already on the model
    open_statuses = ['pending', 'in_review', 'awaiting_ota_update']
    if self.content_type_id and self.object_id:
        qs = Ticket.objects.filter(
            content_type_id=self.content_type_id,
            object_id=self.object_id,
            request_status__in=open_statuses,
        )
        if self.pk:
            qs = qs.exclude(pk=self.pk)
        if qs.exists():
            raise ValidationError(
                {'booking': 'An open ticket already exists for this booking.'}
            )
```

## Wire it in create views

```python
# tickets/views.py CustomerTicketViewSet.create (line ~203)
# cs/views.py OtaChangeRequestView.post (line ~527)
ticket = serializer.save()
ticket.full_clean()  # triggers clean() including the guard
```

## Key points

- Must query BOTH `content_type_id` + `object_id` — the GenericFK pair is the booking identity.
- Exclude `self.pk` so updates don't block themselves.
- `full_clean()` must be called explicitly in views — Django's `Model.save()` does NOT call it automatically.
- Guard is additive — rejects duplicates only, no existing valid flow broken.

## Case

`tickets/views.py:203-230` + `cs/views.py:527-567` — both create unconditionally. A customer can submit via the customer portal AND the OTA portal, creating two open tickets on the same booking.

**Related:** [[cs-centralization-audit-2026-06-29]] Tier-1 #2
