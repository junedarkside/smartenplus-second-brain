# CS Chat — Same-Email OTA vs Guest Conv Debate

**Date:** 2026-07-08  
**Status:** IMPLEMENTED ✅ 2026-07-08 — P1+P2 merged to develop (BE `8df33ab` migration 0012 · AD `1bd7a48`). Soft-link set at OTA create; "Related #id" chip + Merge dialog in AD; merge closes source with system-message audit in both threads.

**Comeback extension ✅ 2026-07-08 (BE `943cabe` · AD `7776fe2`) — Hybrid design:**
- **OTA comeback reopens** the closed conv for (email, booking) — token-proven identity, one thread per booking, duplicate convs stop at source. System message `'Conversation reopened.'` (wording must never contain the substring "closed" — FE widget close-listener).
- **Guest comeback = new conv + link** — reopen rejected: closed history would be accessible to anyone typing the email (OTP gate only guards open/pending convs).
- **Auth comeback = new conv + link** — Zendesk thread-per-issue; no mega-thread resurrection.
- **Uniform chain rule:** `related_conversation` = latest other thread of same identity, any status. Staff walks history via Related chip; chip click seeds the AD search box (search overrides the Active status filter so closed convs surface).
- Note: `MessageCreateView` auto-reopen is dead code in realtime mode (customer sends bypass Django via Supabase insert).  
**Trigger:** Scenario 2 manual test revealed same-email collision: `june_pinkfloyd@hotmail.com` had open Conv-G (guest, homepage) + Conv-OTA (OTA magic link, `/my-trip`).  
**Linked notes:** [[cs-guest-identity-best-practices]] · [[ota-chat-auth-switch-analysis-2026-07-08]] · [[cs-realtime-be-traffic-design-verdict-2026-07-08]]

---

## The Scenario

1. Customer types `june_pinkfloyd@hotmail.com` into chat widget on homepage → Conv-G created (`ota_booking_id=NULL`)
2. Same customer visits `/my-trip?token=<OTA_JWT>` (same email in token, `booking_id=12GO00000000`)
3. OTA `get-or-create` filters on `(guest_email + ota_booking_id)` → no match with Conv-G → Conv-OTA created
4. Customer now has 2 open conversations for same email. Staff sees both in inbox. Customer only sees whichever is active in browser session.

---

## 3-Agent Debate Summary

### Security Agent — ISOLATE (Approach A)

**Verdict:** Current behavior correct. Never merge OTA into generic guest conv.

**Reasoning:**
- OTA token = cryptographically signed (Django signing), bound to `booking_id + email`, validates booking status = **strong identity proof**
- Guest conv = email only, no proof of ownership, anyone who knows email can create = **weak identity proof**
- Merging weak-proof conv into strong-proof context violates access control hierarchy
- OTP bypass risk: guest path enforces OTP on re-access (line 137); merging lets OTA path skip that gate
- Booking context leakage: Conv-G has zero booking data; merging would expose `CsOtaBooking` details to unverified guest session
- Staff triage broken: OTA convs signal "booking verified, operational triage"; guest convs signal "unverified inquiry" — mixing defeats inbox prioritization

**Risk table:**

| Scenario | Merge risk | Isolate benefit |
|---------|-----------|----------------|
| Attacker knows email, OTA conv exists | Can access booking details without OTA token | OTA token requirement enforced |
| OTP bypass | Guest conv → OTA link → merged conv = no 2nd auth | Separate gates maintained |
| Family/shared email | Wrong person's booking context merged | Both convs stay scoped to original identity signal |

---

### Product Agent — ISOLATE + SOFT-LINK (Approach D from prior research)

**Verdict:** Isolation correct, but soft-link badge needed for staff UX.

**Customer expectation:** On `/my-trip`, customer expects booking-specific chat — not their generic homepage question. OTA magic link = booking-context signal. Showing Conv-OTA (not Conv-G) on `/my-trip` is correct intent.

**Industry pattern:**
- Booking.com / Airbnb: separate channel per booking, not merged. Staff sees booking ref + email + source — sufficient.
- Zendesk / Intercom: auto-merge only on **token-based identity** (JWT/OAuth), never email alone.
- Crisp: opt-in merge, privacy-first, GDPR-aligned.

**Staff UX gap:** Today, staff sees 2 unlinked convs, must manually correlate. Fix = soft-link badge (already recommended in `[[cs-guest-identity-best-practices]]` Option D):
- `related_conversation_id` nullable FK on `Conversation`
- AD inbox: "Related conversation" badge → click → see Conv-G history
- Agent-initiated merge: confirm dialog + system message log
- Customer never sees linked history (PDPA — no data repurposing without re-consent)

**Journey map (correct end-state):**

| Touchpoint | What customer sees | What staff sees |
|-----------|-------------------|-----------------|
| Homepage widget | Conv-G (generic Q) | Conv-G in inbox, no booking chip |
| `/my-trip` widget | Conv-OTA (booking-scoped) | Conv-OTA in inbox, booking chip, "Related: Conv-G" badge |
| Staff merge (optional) | Unchanged (customer sees Conv-OTA) | Merged thread with separator + audit log |

---

### Backend Agent — MERGE/UPGRADE (Approach B)

**Verdict:** Upgrade Conv-G in-place when OTA path finds it (set `ota_booking_id` on Conv-G).

**Rationale:**
- `guest_token` encodes `(email, conversation_id)` — if you upgrade Conv-G by setting `ota_booking_id`, the token tuple is unchanged. No token re-mint. RLS scope unchanged.
- Single conv = no fragmentation, customer sees continuity.
- Smallest blast radius: 1 view change, no schema migration.

**Proposed query:**
```python
conv = Conversation.objects.filter(
    guest_email=email,
    ota_booking_id__isnull=True,
    status__in=[STATUS_OPEN, STATUS_PENDING],
).order_by('-updated_at').first()
if conv:
    conv.ota_booking_id = ota_booking_id
    conv.ota_source = ota_source
    conv.save(update_fields=['ota_booking_id', 'ota_source', 'updated_at'])
else:
    # fall through to OTA-keyed get-or-create
```

**Risks:**
- Race condition: two concurrent OTA requests both find Conv-G → double-upgrade. Needs `@transaction.atomic` + partial unique constraint.
- Semantic corruption: Conv-G may have messages unrelated to the booking. Now those messages appear in a booking-scoped conv. Staff sees context bleed.
- Irreversible: once upgraded, Conv-G IS Conv-OTA. No rollback without migration.
- PDPA exposure: guest data repurposed into OTA booking context without re-consent (same concern as auto-merge rejected in prior research).

---

## Leader Synthesis — FINAL VERDICT

### Approach A wins. Approach B rejected. Approach D (soft-link) added as roadmap item.

**Decision matrix:**

| Criterion | A: Isolate (current) | B: Merge/Upgrade | C: Link FK |
|-----------|---------------------|-----------------|-----------|
| Security | ✅ Strong | ❌ Identity downgrade | ✅ Safe |
| PDPA | ✅ Clean | ❌ Purpose violation | ✅ Clean |
| UX (customer) | ⚠️ 2 convs | ✅ 1 conv | ⚠️ 2 convs |
| UX (staff) | ⚠️ Fragmented | ⚠️ Context bleed | ✅ Linked |
| Race condition | ✅ None | ❌ High risk | ✅ None |
| Blast radius | ✅ Zero (no change) | ❌ Medium | ⚠️ FK migration |
| Reversibility | ✅ N/A | ❌ Irreversible | ✅ Nullable FK |

**Why B loses despite smallest code change:**  
Backend Agent's proposal has a fatal semantic flaw: Conv-G may contain messages about unrelated topics ("what's the cancellation policy?") that now appear under a booking chip in staff inbox. Staff assumes all messages in Conv-OTA relate to that booking. Context bleed = wrong triage = CS quality failure. Also PDPA: guest didn't consent to their generic chat being repurposed into booking-linked record.

**Why A + D is correct:**

1. **Keep current isolation** — OTA always gets its own conv scoped to `(email, ota_booking_id)`. No change to `ConversationCreateView`.

2. **Fix Scenario 2 widget bug (already tracked as Audit A)** — `/my-trip` must always show Conv-OTA, not stale Conv-G. This is the real UX fix. `handleOpen` Audit A guard does this.

3. **Add soft-link as next roadmap item** — `related_conversation_id` nullable FK. On OTA conv creation, query for existing guest conv with same `guest_email` + `ota_booking_id=NULL` → if found, set `conv.related_conversation_id = existing_guest_conv.id`. AD inbox badge: "Related: #{id}". Agent merge gate: optional, logged. Cost: ~80 LOC total.

---

## What This Means for Scenario 2 Test

**Current behavior is architecturally correct.** Two convs = expected. Test passes if:
- Conv-OTA ≠ Conv-G ✅ (correct isolation)
- `/my-trip` widget shows Conv-OTA (empty), NOT Conv-G ✅ (Audit A fix)
- Staff sees booking chip on Conv-OTA ✅
- Staff does NOT see Conv-G context without manual lookup ⚠️ (accepted gap — soft-link roadmap)

**Test was failing to distinguish "wrong conv shown" from "correct isolation with missing UX bridge."** The isolation is right. The soft-link is missing.

---

## Action Items

| Priority | Item | Owner | Branch |
|---------|------|-------|--------|
| P0 (done) | Audit A fix: widget shows Conv-OTA on /my-trip | FE | `fix/ota-chat-auth-switch` ✅ merged |
| P1 (roadmap) | `related_conversation_id` FK on `Conversation` | BE | `feat/cs-conv-soft-link` |
| P1 (roadmap) | AD inbox "Related" badge | AD | same branch |
| P2 (roadmap) | Agent merge gate (confirm dialog + system message) | AD+BE | `feat/cs-conv-agent-merge` |
| P3 (ops) | Schedule `sync_chat_messages` Celery beat | DevOps | config only |
