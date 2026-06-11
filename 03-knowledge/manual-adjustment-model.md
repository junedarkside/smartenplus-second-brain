# ManualAdjustment Model

## Summary
Admin-recorded manual charge entries. Replaces legacy `ExtraItemAction → cards.Charge` flow. No Omise integration — purely internal record. `PROTECT` FK prevents order deletion if adjustments exist.

## Context
`orders/models.py:459-473`. Used by admin dashboard to record manual charges (e.g., baggage add-on, operator payout correction, upgrade fee) outside the normal Omise payment flow.

## Model Definition
```python
class ManualAdjustment(models.Model):
    """Admin-recorded manual charge entries. Replaces ExtraItemAction → cards.Charge."""
    order = models.ForeignKey(
        Order,
        on_delete=models.PROTECT,  # can't delete order with adjustments
        related_name='manual_adjustments'
    )
    amount = models.DecimalField(
        max_digits=12, decimal_places=2,
        validators=[MinValueValidator(0)]  # never negative
    )
    reason = models.TextField()      # required: why this adjustment was made
    note   = models.TextField(blank=True)  # optional: internal notes
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='manual_adjustments')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
```

## Key Constraints
- `amount ≥ 0` — adjustments are always additive charges, never credits (refunds go through `payments.Refund`)
- `PROTECT` on `order` FK — attempting `order.delete()` raises `ProtectedError` if any adjustments exist
- `PROTECT` on `created_by` FK — admin user deletion blocked if they have recorded adjustments
- No status field — these are permanent records (cannot be voided via model; must be a separate negative adjustment if needed)

## Legacy Replacement
Before `ManualAdjustment`:
- `ExtraItemAction` model triggered charge via `cards.Charge` (Omise API)
- Now: admin records adjustment manually in dashboard; no Omise API call
- `cards.Charge` deprecated — see `[[refund-flow]]` for deprecation status

## Use Cases
- Excess baggage fees collected offline (cash)
- Price correction after booking (operator error)
- Currency conversion adjustment
- Manual payout recording for reconciliation

## No Omise Integration
`ManualAdjustment` has no `gateway_charge_id` or payment method fields. It's a ledger entry only. Revenue reconciliation must sum: `order.total_paid` (from `GatewayCharge`) + `order.manual_adjustments.aggregate(Sum('amount'))`.

## Related
- [[payment-gateway-charge-architecture]] — GatewayCharge model (canonical payment record)
- [[refund-flow]] — Refund model (for credits back to customer)
- [[orders]] — Order model, related fields
