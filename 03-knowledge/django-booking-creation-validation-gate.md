# Django Booking Creation Validation Gate

**Pattern:** Validate business rules at EVERY enforcement point in the booking funnel, not just the earliest one.

## SmartEnPlus Example

| Validation | Availability endpoint | CartItem creation | BookingItem creation |
|---|---|---|---|
| advance_hr | — | ✅ `check_advance_hour()` in `CartItemViewSet.get_serializer_class()` | ✅ added #90 |
| stop_sale_dates | ✅ `ContractViewSet.availability()` | ✅ added #90 | ✅ added #90 |
| is_actived | — | ✅ `AddCartSerializer` | ✅ `copy_cartitem_to_bookingitem` |
| confirm | — | — | ✅ `copy_cartitem_to_bookingitem` |

## Key Files

- `carts/utils.py` → `copy_cartitem_to_bookingitem()` — validates before BookingItem.objects.create()
- `carts/serializers.py` → `AddCartSerializer.validate()` — validates at CartItem creation
- `carts/utils.py` → `check_advance_hour(contract_id, traveling_date)` — reusable util, returns bool

## Why Redundancy Matters

User can add item at T=0 (passes advance check with 48hr margin), complete checkout slowly, and attempt booking at T=47hr. Without validation at booking creation, order is accepted after deadline. "Defense in depth" across all funnel layers = no silent bypass.

## Pattern

```python
def copy_cartitem_to_bookingitem(cartitem, order, assignment=None):
    # Validate ALL business rules before any DB writes
    if not cartitem.contract.is_actived:
        raise ValidationError('Cannot book inactive contract')
    if not check_advance_hour(cartitem.contract.id, str(cartitem.traveling_date)):
        raise ValidationError('Cannot book: advance booking deadline has passed')
    if cartitem.contract.stop_sale_dates.filter(date=cartitem.traveling_date).exists():
        raise ValidationError('Cannot book: traveling date is a stop-sale date')
    # ... proceed with BookingItem.objects.create()
```
