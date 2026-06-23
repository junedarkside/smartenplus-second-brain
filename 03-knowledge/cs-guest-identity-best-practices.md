# CS Guest Identity Best Practices

## Summary
World-class CS + booking platforms use soft-link (not auto-merge) for guest→auth identity. Recommendation for SmartEnPlus: `related_conversation_id` FK + agent-initiated merge gate. Auto-merge rejected (PDPA + false-positive risk).

## Context
Research commissioned 2026-06-23 via 3-agent debate team covering:
- CS platforms: Zendesk, Intercom, Freshdesk, HubSpot, Crisp, Drift
- Booking platforms: Booking.com, Airbnb, GetYourGuide, Klook, Viator, 12Go
- Skeptic lens: PDPA compliance, failure modes, SmartEnPlus constraints

Current SmartEnPlus state: guest conv (`user=None`, `guest_email`) + auth conv (`user=Account`) — fully separate, no link. Agents blind to prior guest context.

## Problem
When a customer chats as guest, then later logs in or already has an account, CS agents have zero visibility into prior guest conversations. Two options considered — auto-merge or stay separate. Both are wrong alone.

## Details

### CS Platform Patterns

**Zendesk/Intercom (auto-merge):**
- Guest → login → conversations merged into single thread
- "Authenticated at X" separator shown in timeline
- Token-based ID (JWT/OAuth), never email alone (email is spoofable)

**Crisp (opt-in merge, privacy-first):**
- Default = separate sessions; merge requires `session_merge: true` + secure token
- User controls when history links — GDPR-aligned
- Tradeoff: higher UX complexity; user must opt-in

**Identity signal hierarchy (industry consensus):**
1. Secure auth token (JWT/OAuth) → automatic identity
2. Email match → account lookup trigger (NOT auto-merge)
3. Browser cookie → same-device session resume only

**OTP in CS context:**
- Magic link > OTP > password (least friction in support)
- Chat persists during OTP entry — no reload
- Allow guest escalation WITHOUT forcing auth (agent discretion)

### Booking Platform Patterns

**Booking.com / Airbnb:**
- Guest booking links to account only on user-initiated registration — NOT on email match alone
- OTA channel bookings shown as separate "channel" view, not merged into account history
- CS agents see: booking ref + passenger email + channel source — sufficient without merge

**Identity resolution in booking context:**
- Email = best-effort signal only; NOT definitive identity
- Family sharing, corporate travel, group bookings produce email collisions
- Booking reference (PNR/order ID) more reliable than email for identity
- CS principle: "same email ≠ same person"

### Why NOT Auto-Merge

**PDPA (Thailand, effective 2022):**
- Article 18 (Purpose limitation): guest chat re-purposed as customer history without re-consent = breach
- Article 22 (Access rights): customer can't distinguish guest vs authenticated origin — loss of transparency

**False positive risk:**
- Family Gmail (parent + child), shared inboxes, corporate delegation → wrong person's bookings merged
- Wrong merge is near-irreversible; manual untangle = error-prone + agent time

## Decision

**Option D — Soft Link with Agent-Initiated Merge Gate**

| Option | Risk | Verdict |
|--------|------|---------|
| A — Silent separate (current) | Agents blind to prior context | Worst UX |
| B — Auto-merge on email match | PDPA breach + family-email false positive | Reject |
| C — Agent confirm before any link | Auth friction kills conversion momentum | Too heavy |
| **D — Soft link + agent merge gate** | No privacy risk, reversible, audit trail | **Recommended** |

**Mechanics:**
- Add `related_conversation_id` nullable FK on `Conversation` model
- On `OtpVerifyView` success: query `Conversation.objects.filter(guest_email=user.email)` → set link if found
- Admin dashboard: "Related conversation" badge + view link in sidebar
- Agent-initiated merge: staff clicks Merge → confirm dialog → system message logged with agent + timestamp
- Guest and auth threads stay separate (no data repurposing)

## Tradeoffs

| Tradeoff | Detail |
|----------|--------|
| Agent must manually check for related convs | Mitigated by dashboard badge |
| Merge is optional → some agents skip it | Acceptable — soft link still visible |
| FK migration adds ~50 LOC backend | Trivial cost |
| No automatic UX continuity for customer | Customer doesn't see linked guest history (by design — PDPA) |

## Consequences

**Positive:**
- PDPA-safe: no unauthorized data repurposing
- Reversible: soft link can be cleared; merge can be journaled and reversed
- Phase 4 OTA-ready: when `CsOtaBooking` sync builds, `passenger_email` lookup extends naturally to sidebar
- Low cost: ~50 lines backend + ~30 lines admin UI badge

**Watch for:**
- Agents ignoring the "Related" badge — UX training needed
- Multiple guest convs for same email (repeat visitors) → show all, not just most recent

## Related
- [[cs-centralization-review-2026-06-22]]
- [[supabase-ota-booking-store]]
- [[cs-architecture-decision]]
