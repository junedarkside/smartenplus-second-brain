# Payment Deep Review — KB Verification (2026-06-12)

## Summary

3 verifier agents cross-checked all 5 HIGHs + 18 MEDIUMs from [[payment-deep-review]] against ~1700 lines of vault payment/omise KB (`03-knowledge/`) + read-only code spot-checks. **Result: 20 CONFIRMED · 2 REFINED (H1, M17) · 1 REFUTED (M4) · 1 KB inaccuracy (M8) · 12 KB gaps surfaced.**

One material correction: **M4 is REFUTED** — the deep-review claim that BE emits `{error:'payment_pending'}` and FE doesn't map it is wrong. KB + code show the canonical code is `pending_charge_exists` and FE maps it at `useOmisePayment.js:170`. M4's "no cancel affordance" UX concern may still be valid but needs a different framing — likely a M1-style missing-branch, not a missing 409 mapping.

**Process:** 3 Explore agents in parallel (no writes outside this doc), each owning a non-overlapping domain. All agents used strict verdict format: `CONFIRMED` / `REFINED` / `REFUTED` / `MISSING` per finding with KB citation + code line ref.

---

## Per-Finding Verdicts

| # | Finding | Agent | Verdict | KB ref | Notes |
|---|---------|-------|---------|--------|-------|
| H1 | Charge amount client-controlled, never validated against order total | 1 (API) | **REFINED** | `[[payment-backend-charge-flow]]` §6 silent on validation | Finding stands; grill-correction (subtract `fee`) correct; KB silent on this gap |
| H2 | Legacy webhook live, unverified, bypasses `finalize_payment` | 1 (API) | CONFIRMED | `[[payment-gateway-charge-architecture]]` SSOT, `[[omise-webhook-security]]` | KB doesn't enumerate legacy route; finding correct |
| H3 | Idempotent order-reuse returns wrong response shape | 2 (Webhook) | **REFINED** | (KB silent on order-create envelope) | Finding stands; no KB coverage of `{"message","order"}` wrapper contract |
| H4 | Explicit QR cancel never expires: `charge_id` dropped from `orderDetails` | 3 (FE) | CONFIRMED | `[[payment-qr-polling-mechanics]]` Cleanup section | KB explicit: explicit cancel = sole expire trigger; FE destructure breaks it |
| H5 | Paid-but-unfinalized order invisible + unrecoverable in UI | 2 (Webhook) | CONFIRMED | `[[payment-finalize-deep-dive]]` "Critical Behaviors" + `[[payment-exception-catalog]]` | KB explicitly supports fix safety (`payment_finalized_at` guard) |
| M1 | PromptPay lacks `pendingCharge` branch | 3 (FE) | CONFIRMED | `[[payment-frontend-flow-mechanics]]` 409 Mapping | KB lists 3 branches; QR path missing one |
| M2 | `alreadyPaid`/`amountLocked` unconsumed in card/redirect flows | 3 (FE) | CONFIRMED | `[[payment-frontend-flow-mechanics]]` 409 Mapping | Card/redirect path handles 1/3 of 409s |
| M3 | `cancelState.success` cleared instantly by method-change effect | 3 (FE) | CONFIRMED | `[[payment-checkout-architecture-audit]]` Fix 5 | KB describes the fix; finding flags residual UX gap |
| M4 | Cross-order 409 body `{error:'payment_pending'}` not in FE mapping | 2 (Webhook) | **REFUTED** | `[[payment-exception-catalog]]` Frontend 409 Mapping | Canonical code is `pending_charge_exists`, FE maps it. **Finding's error code is wrong.** |
| M5 | `payment_pending`+`locked_amount` set before `create_charge`; `BaseError` not caught | 2 (Webhook) | CONFIRMED | (KB silent) | KB has no `omise.errors.BaseError` rollback pattern; finding correct |
| M6 | Lock contention: ApplyCouponView Coupon lock vs finalize_payment implicit Coupon lock | 2 (Webhook) | CONFIRMED | `[[payment-finalize-deep-dive]]` "Lock contention (M6):" | KB explicitly documents M6; same root cause + fix |
| M7 | Refunds: no over-refund guard in either recorder | 3 (FE) | CONFIRMED | `[[refund-flow]]` Full vs Partial | KB documents cumulative semantics; guard location unspecified |
| M8 | Guest charge initiation requires no email match | 1 (API) | CONFIRMED | `[[payment-backend-charge-flow]]` §5 — **KB OUT OF DATE** | Code at `views.py:109` doesn't read `email`; KB §5 claims it does |
| M9 | Concurrent `create_charge` IntegrityError: orphaned Omise charge possible | 1 (API) | CONFIRMED | (KB silent on orphaned-charge cleanup) | `omise_charge.expire()` not called in `except IntegrityError` handler |
| M10 | `PlaceOrderViewSet` still routed | 1 (API) | CONFIRMED | (KB silent on legacy route inventory) | Live `apis/urls.py:37` + `carts/views.py:281-411` second finalization path |
| M11 | `OrderViewSet.create` guest `get_or_create` with no cart filter | 1 (API) | CONFIRMED | (KB silent) | Cross-guest order collision in `orders/views.py:120-129` |
| M12 | Card 3DS charges excluded from all self-heal sweeps | 1 (API) | CONFIRMED | `[[payment-status-enums]]` METHOD_EXPIRY | KB documents exclusion; lost-webhook recovery gap unspecified |
| M13 | Charge response `status`/`failure_message` never read (silent decline) | 3 (FE) | CONFIRMED | `[[payment-exception-catalog]]` "Silent Declined Card (M13)" | KB is the source — finding fully catalogued |
| M14 | Coupon `isProcessing` stuck `true` if refetch throws | 3 (FE) | CONFIRMED | (KB silent — MISSING) | `usePaymentCouponManager` lifecycle undocumented |
| M15 | Polling silently stops on any 4xx | 3 (FE) | CONFIRMED | (KB silent on 4xx branch — MISSING) | `useQRPolling` lifecycle diagram lacks API_ERROR |
| M16 | `usePaymentInitialization` cleanup closes over registering-run's `formStep` | 3 (FE) | CONFIRMED | (KB silent — MISSING) | Init hook lifecycle undocumented |
| M17 | KakaoPay / Alipay dead end-to-end | 1 (API) | **REFINED** | `[[payment-status-enums]]` PAYMENT_METHOD_MAP | KakaoPay stands; Alipay half may be overstated (`AP`/`APC` routes exist) |
| M18 | `Payment.amount_paid = amount_thb + fee` double-counts fee | 1 (API) | CONFIRMED | (KB silent on `Payment.amount_paid`) | Reporting-only; `finalize_payment` doesn't update Payment |

---

## KB Inaccuracy (must fix)

### `payment-backend-charge-flow.md` §5 — guest email validation claim

**Current (wrong):** `payment-backend-charge-flow.md:60-70` states `ChargeOrderView` validates `email` for guest requests.

**Actual:** `payments/views.py:106-109` auth path uses `user=request.user`; guest path uses `user__isnull=True` only — `email` never read. Email validation **only** exists in `ExpirePendingChargeView` (`payments/views.py:375-376`).

**Fix:** Edit §5 to clarify guest email validation is **only** in `ExpirePendingChargeView`; **missing** in `ChargeOrderView` (which is M8).

---

## KB Gaps Surfaced (12 candidates for atomization)

| # | KB gap | Source finding | Suggested note |
|---|--------|----------------|----------------|
| 1 | Server-side amount validation rule | H1 | `[[payment-amount-validation-rule]]` — client `amount_thb` must equal `(order_total + fee - discount)` within 1.00 THB tolerance |
| 2 | Legacy webhook/route inventory | H2, M10 | `[[payment-legacy-deprecation-map]]` — `webhook-legacy/`, `placeorder/`, deprecation status |
| 3 | IntegrityError → orphaned Omise charge cleanup | M9 | Add to `[[payment-charge-service-layer]]` `create_charge` step 6: `omise_charge.expire()` in `except IntegrityError` |
| 4 | Order creation filter rule | M11 | `[[django-booking-creation-validation-gate]]` — guest orders must be cart-scoped, not global `user=None, status='ordering'` |
| 5 | Self-heal coverage matrix | M12 | Add to `[[payment-status-enums]]` — per-method sweep coverage (PP/MB yes, Card 3DS no) |
| 6 | `Payment` model field semantics | M18 | `[[payment-charge-service-layer]]` — `amount_paid` lifecycle, `amount_precise`, ownership of updates |
| 7 | FE→BE payment-method name contract | M17 | `[[payment-checkout-architecture-audit]]` — short codes (`'PP'`/`'KP'`) vs full names (`'kakao_pay'`) vs OmiseMethod values |
| 8 | `useQRPolling` 4xx API_ERROR branch | M15 | Add to `[[payment-qr-polling-mechanics]]` lifecycle diagram — API_ERROR silent stop is a bug |
| 9 | `usePaymentInitialization` init lifecycle | M16 | `[[payment-frontend-flow-mechanics]]` — `initialized.current` reset semantics, cleanup closure |
| 10 | `usePaymentCouponManager` state machine | M14 | `[[payment-frontend-flow-mechanics]]` — `isProcessing` reset paths, error handling |
| 11 | Refund validation rule | M7 | Add "Validation" subsection to `[[refund-flow]]` — cumulative sum guard, multi-booking dimension |
| 12 | Order-create response envelope contract | H3 | `[[django-400-vs-409-duplicate-cart-item]]` — `{"message": "...", "order": serializer.data}` consistency between create + reuse paths |

**Atomization note:** Per vault CLAUDE.md, 12 is high — recommend batching with next `/lint-vault` or splitting into 2 sessions (gap #1–6 first, #7–12 in following).

---

## M4 Refutation Detail

**Deep-review M4 claim:** "GAP-2 cross-order 409 body `{error:'payment_pending'}` (`services.py:660-664`) not in FE's 409-mapping table (`useOmisePayment.js:169-178` checks `pending_charge_exists` only) → generic toast, no cancel affordance despite `charge_id` supplied."

**Verification finding:**
- `[[payment-exception-catalog]]` "Exception Reference" table row 1: `PendingChargeError` → 409 → `{error: 'pending_charge_exists', charge: {...}}`.
- `[[payment-frontend-flow-mechanics]]` 409 Mapping: `pending_charge_exists` (mapped), `amount_locked` (mapped), `Order already paid` (mapped).
- `useOmisePayment.js:169-178` code reads `error === 'pending_charge_exists'` — this is the first branch.

**What is actually true:** The 409 IS mapped. The "no cancel affordance" concern may still be valid — it could be that the `pendingCharge` branch is missing in the QR path (M1) or the cancel UX surface needs work. **M4 as written misidentifies the error code.**

**Recommended action:** Either (a) retract M4, or (b) rewrite M4 to address the real concern: e.g., "QR `handleQRPayment` missing `pendingCharge` UI affordance — when 409 returns `pending_charge_exists`, the `PendingChargeNotice` doesn't surface" (which is what M1 already covers). Net: M4 is subsumed by M1; M4 should be retracted.

---

## Refinement Deltas

### H1 — amount validation (no spec change)
KB did not surface this gap; finding stands. **No code-path delta** — grill-correction already applied to fix spec.

### M17 — Alipay half may be overstated
- **KakaoPay (stands):** `PAYMENT_METHOD_MAP` has `'KP' → OmiseMethod.KAKAO_PAY='kakao_pay'`; FE sends `'kakaopay'`. The mismatch at the FE→BE boundary is real.
- **Alipay (overstated):** `payments/views.py:38-39` shows `'AP' → OmiseMethod.ALIPAY` AND `'APC' → OmiseMethod.ALIPAY_CN` are both present. KB confirms Alipay routing exists. The FE `OMISE_SOURCE_TYPES` gap is a separate, smaller issue.

**Recommended fix scope (revised):**
- KakaoPay: add `'kakaopay': OmiseMethod.KAKAO_PAY` to `PAYMENT_METHOD_MAP` (per finding).
- Alipay: verify FE `OMISE_SOURCE_TYPES` has `ALIPAY: 'alipay'` key; if missing, add it. (May be a non-issue — needs spot-check in implementation phase.)

---

## KB Cross-References Confirmed (no KB write needed)

These findings are fully covered by existing KB and require no atomization:
- **H5** — `payment-finalize-deep-dive.md` "Critical Behaviors" + `payment-exception-catalog.md` "PaymentAmountMismatchError Contract" explicitly supports fix safety
- **H6/M13** — `payment-exception-catalog.md` "Silent Declined Card" is the originating source
- **M6** — `payment-finalize-deep-dive.md` "Lock contention (M6):" section explicitly references this finding
- **M1, M2** — `payment-frontend-flow-mechanics.md` 409 Mapping defines the full set; findings are gaps in implementation
- **M3** — `payment-checkout-architecture-audit.md` Fix 5 documents the fix; finding identifies post-fix UX gap

---

## Verdict Tally

| Verdict | Count | Findings |
|---------|-------|----------|
| CONFIRMED | 20 | H2, H4, H5, M1, M2, M3, M5, M6, M7, M8, M9, M10, M11, M12, M13, M14, M15, M16, M18 |
| REFINED | 2 | H1, M17 |
| REFUTED | 1 | M4 |
| MISSING-aspect (KB silent, finding stands) | 1 | H3 (no KB coverage of order-create envelope contract — but counted as REFINED per delta) |

**Net correction to deep-review:** M4 should be retracted (subsumed by M1). All other findings stand. Fix order in deep-review's "Suggested fix order" remains correct.

---

## Related

[[payment-deep-review]] · [[omise-api-reference]] · [[payment-finalize-deep-dive]] · [[payment-charge-service-layer]] · [[payment-frontend-flow-mechanics]] · [[payment-exception-catalog]] · [[payment-qr-polling-mechanics]] · [[refund-flow]] · [[payment-backend-charge-flow]] · [[payment-status-enums]] · [[payment-gateway-charge-architecture]] · [[omise-webhook-security]] · [[payment-checkout-architecture-audit]] · [[payment-sentinel-idempotency]] · [[multitab-payment-race-condition-fixes]]
