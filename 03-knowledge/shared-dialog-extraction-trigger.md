# Shared Dialog Extraction Trigger

## Summary
Extract a duplicated inline dialog into a shared component only when a 3rd call site is concrete — not before. Verify the API layer already routes the discriminator so the component passes it through.

## Context
Notify dialogs were ~135 lines duplicated verbatim across command-centre (OTA) + `/bookings/[slug]` (direct). A 3-debater team weighed extract-now vs defer. CLAUDE.md NO OVER-ENGINEERING warns against premature abstraction at 2 sites.

## Decision rule — extract when ALL hold
1. **3rd call site is concrete** (a ticketed feature, not speculative future use).
2. **API layer already routes the discriminator** — e.g. `csApi.js` `booking_type` param on update/delete existed before the UI extraction. Component passes it through; no new branching invented.
3. **Faithful mechanical lift** — same JSX/handlers moved, not rewritten → regression risk = a diff review.
4. **Under complexity caps** (<200 lines, ≤3 conceptual prop groups; the "3 params" rule targets helper fns, not component prop objects).

## When NOT to extract
- Only 2 call sites (YAGNI).
- Discriminator needs a new router/speculative enum.
- Existing dialogs are stable + touching them risks break → defer; build the component for the new site only, retrofit later (the chosen path for `NotifyDialog` — direct-only first, OTA retrofit separate task).

## Tradeoffs
- **Pro:** DRY, single fix point, both pages shed lines.
- **Con:** coupled regression surface (one bug breaks all callers) → smoke test EACH call site after extraction.

## Related
[[command-centre-direct-notify-redesign]] · [[direct-booking-notify-plan]]
