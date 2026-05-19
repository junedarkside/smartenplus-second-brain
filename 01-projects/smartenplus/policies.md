# Policies — Contract Policy System

## Summary
Contract policy models. Two cancellation systems coexist: legacy single-tier (`CancellationPolicy`) and new multi-tier (`CancellationPolicies` + `CancellationDetail`). Contract has FKs to both; new tier takes precedence when both set.

---

## Models

### CancellationPolicy (old single-tier)
Per-operator cancellation policy.

**Fields:**
- `operator` FK
- `free_refund` — yes/no
- `refund_hours` — Duration. Free refund valid until this many hours before departure.
- `charge_type` — `100%` (full charge), `50%` (half), `fixed_amount` (specific amount)
- `charge_amount` — required if `charge_type=fixed_amount`
- `is_actived`

**`clean()` validation:** `free_refund=yes` requires `refund_hours` set. `charge_type=fixed_amount` requires `charge_amount`.

**String repr:** dynamically describes refund policy.

---

### CancellationPolicies (new multi-tier)
Named policy containing multiple `CancellationDetail` rows.

**Fields:** `name`, `description`.

### CancellationDetail
Per-tier cancellation condition.

**Fields:**
- `policy` FK → `CancellationPolicies`
- `condition_hours` — hours before departure
- `refund_percentage` — nullable (e.g., 100 = full refund, 50 = half)
- `fixed_amount` — nullable (specific amount)
- `priority` — ordering

**Helper:** `get_refund_description()` — returns "Refund: $X" or "Refund: X%" or "No Refund".

**Example:** 74h+ → 100%, 48h+ → 50%, 24h+ → 0%.

---

### BaggagePolicy
Baggage allowances and fees.

**Fields:**
- `carry_on_limit`, `carry_on_overweight_size_limit`, `carry_on_oversized_size_limit`
- `checked_bag_limit`, `checked_bag_overweight_size_limit`, `checked_bag_oversized_size_limit`
- `oversized_fee`, `overweight_fee` (Decimal)

---

### GeneralInformation
General info text for contracts.

**Fields:** `name`, `description` (RichText), `is_default`, `operator` FK.

`is_default=True` → applies to all operators unless overridden.

---

## Dual Cancellation System

`Contract` has FKs to both:
- `Contract.cancellation_policy` → `CancellationPolicy` (old)
- `Contract.cancellation_policies` → `CancellationPolicies` (new)

Both can coexist. Frontend/display logic should prefer the new multi-tier when both are set.

---

## Related
- [[operators]] (Contract FKs to all policy models)