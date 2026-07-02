# Django Serializer N+1 Pattern — List vs Detail Separation

## Summary
When DRF serializers include computed fields that trigger database queries (e.g., `SerializerMethodField` calling related models), list views become N+1 time bombs. Solution: separate list/detail serializers.

## Pattern

**Problem:**
```python
class TicketSerializer(serializers.ModelSerializer):
    latest_event = serializers.SerializerMethodField()  # N+1!

    def get_latest_event(self, obj):
        return OtaBookingEvent.objects.filter(
            ota_booking=obj.content_object
        ).order_by('-created_at').first()  # Query per ticket
```

List endpoint with `Ticket.objects.all()` → 50 tickets = 50 extra queries.

**Solution:**
```python
# Minimal list serializer — no computed relations
class TicketListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ['id', 'ticket_number', 'title', ...]

# Detail serializer extends list, adds computed fields
class TicketDetailSerializer(TicketListSerializer):
    latest_event = serializers.SerializerMethodField()

    def get_latest_event(self, obj):
        # Single-ticket detail view → one extra query OK
        return OtaBookingEvent.objects.filter(
            ota_booking=obj.content_object
        ).order_by('-created_at').first()

# Views use appropriate serializer
class TicketViewSet(ModelViewSet):
    serializer_class = TicketListSerializer  # List view → no N+1

class RequestStatusViewSet(GenericViewSet, UpdateModelMixin):
    serializer_class = TicketDetailSerializer  # Single-ticket detail → safe
```

## When to Split

- **List view** + `SerializerMethodField` hitting relations → always split
- **Admin-only endpoints** + low volume → can defer (add TODO comment)
- **Detail views only** → single serializer fine (one query = one query)

## Better Alternative

For truly large lists, annotate at queryset level instead:
```python
Ticket.objects.annotate(
    latest_event_at=Max('ota_booking__events__created_at')
)
```

But separate serializers is cheaper upfront — defer annotation until proven bottleneck.

## Related
- [[django-orm-performance]] — queryset optimization patterns
- [[drf-viewset-patterns]] — viewset conventions

## Context
SmartEnPlus command-centre gap fix H9 — `TicketDetailSerializer` adds `latest_ota_event_at` without breaking list endpoint performance.
