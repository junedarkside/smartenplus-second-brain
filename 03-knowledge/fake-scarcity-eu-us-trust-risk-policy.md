---
name: fake-scarcity-eu-us-trust-risk-policy
description: EU/US trust risk: fabricated scarcity ("Only 2 left!", "Booked 5 times today") violates consumer protection laws. Fake urgency claims without data backing = legal liability.
metadata:
  type: knowledge
  status: active
  date: 2026-06-22
  parent: recommendation-engine-completion-roadmap
---

# Fake Scarcity — EU/US Trust Risk Policy

## Summary
EU/US trust risk: fabricated scarcity ("Only 2 left!", "Booked 5 times today") violates consumer protection laws. Fake urgency without data = legal liability.

## Why It Matters
EU Unfair Commercial Practices Directive + US FTC ban deceptive scarcity claims. Showing fake urgency = fines, reputational damage.

## Detail
**Prohibited (without evidence):**
- "Only 2 seats left!" (no inventory count backing)
- "Booked 5 times today" (fabricated number)
- "Selling fast" (no rate-of-sale data)
- Countdown timers without expiry basis

**Allowed WITH data:**
- "3 seats left" (live inventory count >0)
- "20 people viewed today" (real view count from analytics)
- "High demand for this route" (backed by booking trend data)

**Policy:**
1. All scarcity claims must be data-backed
2. Inventory counts real-time (not cached stale)
3. "Viewed by X users" from analytics, not hardcoded
4. No "booked X times" unless from actual order count

**Regions:** EU strictest (UCPD), US (FTC deception guidelines), UK (CAP Code). Thailand: TBD (PDPA guidance).

## Constraints / Gotchas
Hardcode "Only X left" in components — VIOLATION. Use live API: `GET /inventory/{contract_id}/remaining` → render count OR hide if <3.

## Related
- [[recommendation-engine-completion-roadmap]] — parent (EU/US compliance gap)
