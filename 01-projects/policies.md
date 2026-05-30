No file path — text provided directly. Compressing inline.

# Policies — Contract Policy System

## Summary
Two cancellation systems: legacy single-tier (`CancellationPolicy`) + new multi-tier (`CancellationPolicies` + `CancellationDetail`). Contract FKs to both; new tier wins when both set.

---

## Models

### CancellationPolicy (old single-tier)
Per-operator cancellation policy.

**Fields:**
- `operator` FK
- `free_refund` — yes/no
- `refund_hours` — Duration. Free refund window (hours before departure).
- `charge_type` — `100%` (full), `50%` (half), `fixed_amount` (specific amount)
- `charge_amount` — required if `charge_type=fixed_amount`
- `is_actived`

**`clean()` validation:** `free_refund=yes` → `refund_hours` required. `charge_type=fixed_amount` → `charge_amount` required.

**String repr:** dynamic refund policy description.

---

### CancellationPolicies (new multi-tier)
Named policy with multiple `CancellationDetail` rows.

**Fields:** `name`, `description`.

### CancellationDetail
Per-tier cancellation condition.

**Fields:**
- `policy` FK → `CancellationPolicies`
- `condition_hours` — hours before departure
- `refund_percentage` — nullable (100 = full, 50 = half)
- `fixed_amount` — nullable (specific amount)
- `priority` — ordering

**Helper:** `get_refund_description()` — "Refund: $X" | "Refund: X%" | "No Refund".

**Example:** 74h+ → 100%, 48h+ → 50%, 24h+ → 0%.

---

### BaggagePolicy
Baggage allowances + fees.

**Fields:**
- `carry_on_limit`, `carry_on_overweight_size_limit`, `carry_on_oversized_size_limit`
- `checked_bag_limit`, `checked_bag_overweight_size_limit`, `checked_bag_oversized_size_limit`
- `oversized_fee`, `overweight_fee` (Decimal)

---

### GeneralInformation
General info text for contracts.

**Fields:** `name`, `description` (RichText), `is_default`, `operator` FK.

`is_default=True` → applies all operators unless overridden.

---

## Dual Cancellation System

`Contract` FKs:
- `Contract.cancellation_policy` → `CancellationPolicy` (old)
- `Contract.cancellation_policies` → `CancellationPolicies` (new)

Both coexist. Prefer new multi-tier when both set.

---

## Related
- [[operators]] (Contract FKs to all policy models)