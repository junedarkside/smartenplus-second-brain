# Manual Confirmation Audit Trail — Transient vs Persisted

## Summary
When staff manually confirm an external action (e.g., "I called Agoda and they confirmed this change"), system needs to record WHO confirmed and WHEN. Common anti-pattern: transient flag that bypasses guard but disappears. Result: zero audit trail for disputes.

## Anti-Pattern

```python
# Model
class Ticket(models.Model):
    # ❌ No confirmation fields
    pass

# Backend guard
def clean(self):
    if self.request_status == 'resolved' and getattr(self, '_ota_manually_confirmed', False):
        return  # Bypass OK (but _ota_manually_confirmed never saved!)

# Frontend
const handleResolve = () => {
    api.patch(`/tickets/${id}`, {
        request_status: 'resolved',
        ota_manually_confirmed: true,  // Always sent, never saved
    })
}
```

**Problem:** Every OTA resolution has hidden `ota_manually_confirmed: true` — whether staff actually confirmed or not. No record of who/when. Dispute with OTA → zero defense.

## Pattern

**Backend:**
```python
class Ticket(models.Model):
    # ✅ Persist audit fields
    ota_manually_confirmed_at = models.DateTimeField(null=True, blank=True)
    ota_manually_confirmed_by = models.ForeignKey(User, null=True, blank=True)

def clean(self):
    if self.request_status == 'resolved' and getattr(self, '_ota_manually_confirmed', False):
        return  # Transient flag still used for guard check

# Persist the audit trail
def partial_update(self, request, *args, **kwargs):
    if request.data.get('ota_manually_confirmed'):
        instance._ota_manually_confirmed = True
        instance.ota_manually_confirmed_at = timezone.now()
        instance.ota_manually_confirmed_by = request.user
```

**Frontend:**
```jsx
// ❌ Hidden always-true flag
...(newStatus === 'resolved' && source === 'ota' ? { ota_manually_confirmed: true } : {})

// ✅ Explicit checkbox with tooltip
<Checkbox
    checked={otaConfirmed}
    onChange={e => setOtaConfirmed(e.target.checked)}
/>
<Tooltip title="Tick only after confirming directly with OTA operator">
    <FormControlLabel label="I have confirmed this change with OTA" />
</Tooltip>

// Only send when explicitly checked
...(otaConfirmed ? { ota_manually_confirmed: true } : {})
```

**Behavior change:** Staff now **must** tick checkbox before OTA resolve unblocks. Guard becomes real, not dead code.

## When This Pattern Applies

- Manual confirmations with external parties (OTAs, operators, suppliers)
- Audit-required actions (refunds, cancellations, overrides)
- Emergency bypasses (staff must justify why normal flow skipped)

## Migration Notes

Adding audit fields to existing table:
- Both fields `null=True, blank=True` — safe for existing rows
- Old resolved tickets show `null` — expected (no audit before this point)
- Add `related_name` to avoid clash with other FKs

## Related
- [[audit-trail-patterns]] — other audit field patterns
- [[manual-workflow-guards]] — when to use transient flags vs persisted

## Context
SmartEnPlus command-centre gap fix C6 — added `ota_manually_confirmed_at/by` fields + explicit checkbox in admin resolve dialog.
