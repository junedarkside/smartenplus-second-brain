---
name: cs-centralization-review-2026-06-22
description: Knowledge-integrity review of the 9-note CS-Centralization cluster (3-agent read-only audit). 1 HIGH supersession drift, 5 index orphans, 1 over-cap note, 6 hard build blockers. Vault edits RESOLVED 2026-06-22; bucket-C decision gaps remain open.
metadata:
  type: review
  status: resolved
  date: 2026-06-22
  parent: smarten-customer-os-thesis
---

# CS Centralization — Integrity Review 2026-06-22

> ✅ **Closure 2026-06-22** — the 5 recommended vault edits are **APPLIED**: (1) thesis:42 P1b row + lines 70/72
> rewritten to both-sides-poll (Supabase struck from message path, banner → [[cs-architecture-decision]]);
> (2) `cs-centralization-design-concept` split (211→~155 lines), token audit extracted →
> [[cs-design-tokens-audit]]; (3) D1-D6 triaged into [[cs-centralization-stack]] (D1/D3/D5 applied, D2 already
> present, D4/D6 marked MOOT post-reversal); (4) thesis back-links added (consent-model, p0-protocol, stack,
> arch-decision); (5) this status flipped `active → resolved`. **Still OPEN (bucket-C, not editable —
> owner/legal/eng sign-off):** the 6 hard build blockers + 6 GAP-A→F spec holes in the ledger below.

> **3-agent read-only audit** (consistency / link-graph / open-questions). Reviewed the 9-note CS cluster
> in-place. **No source note was edited** — this note only *recommends* fixes; a user-approved follow-up
> applies them. Scope: vault knowledge only, no code repos read.

## Summary Verdict

Cluster is **~98% internally consistent and structurally sound**. The 2026-06-21 transport reversal
(Supabase Realtime → both-sides-poll-Django, Supabase OUT of message path) propagated correctly across
8 of 9 notes. **One HIGH drift remains:** the root thesis still asserts the reversed Supabase design as
current. Vault-hygiene is good except **5 of 9 notes are missing from `index.md`** and one note is over the
200-line cap. The real bottleneck to build-start is not the docs — it's **~20 unresolved owner/legal/eng
decisions**, 6 of them hard blockers.

## Contradictions / Supersession Drift

| # | Where | Problem | Sev |
|---|---|---|---|
| C1 | `smarten-customer-os-thesis:42` (P1b row) ↔ `cs-architecture-decision` | Thesis P1b row still reads "CS Dashboard subscribes to **Supabase Realtime** `cs.messages`… `sync_status`… Django→Celery writes to Supabase `cs` schema." This is the **reversed Option B**, removed 2026-06-21. No SUPERSEDED banner. Single point-of-confusion for any reader starting at the thesis. | **HIGH** |

Everything else agrees. Anchor cross-checks **all PASS**: OTP store = PostgreSQL not Redis
(`cs-api-contract:21,61` ↔ `cs-gap-debate-verdicts:68` S2); OTP type = HOTP not TOTP (`:61` ↔ `:23-24` B3);
app = new `cs/` (`:18` B1 both); DB index = composite `(conversation_id, created_at)` (`cs-gap-debate-verdicts:20-21`
B2; `cs-api-contract` states only `created_at db_index`, MINOR — let B2 be canonical). Design-concept's
"architecture-agnostic" claim still valid post-reversal (optimistic echo hides poll-vs-push).

## Vault Hygiene

**Index orphans (HIGH) — 5 of 9 notes absent from `index.md`:**
`cs-api-contract`, `cs-consent-gdpr-model`, `cs-centralization-design-concept`, `cs-p0-measurement-protocol`,
`cs-centralization-doc-review`. (`cs-architecture-decision` appears only as a passing ref inside the
prod-capacity line, not as its own entry — also needs a real entry.) Present: thesis, stack, gap-verdicts.

**Over-cap (MED) — 1 note:** `cs-centralization-design-concept.md` = **211 lines** (vault cap 200).
Split candidate: extract the token-gaps + design-system reuse map → `cs-design-tokens-audit.md`; keep the
3-surface flows in the design-concept.

**Back-links (LOW):** all declared `parent:` fields resolve; all wikilinks resolve (no broken links).
2 children (`cs-consent-gdpr-model`, `cs-p0-measurement-protocol`) are named in the thesis prose but lack a
Related-section back-link. No duplicate concepts — clean separation across all 9.

## Consolidated Open-Questions Ledger (the real blockers)

### HARD BLOCKERS — build cannot start

| Owner | Source | Question | Blocks |
|---|---|---|---|
| Business | `cs-p0-measurement-protocol:65` | 5 P0 decisions: threshold, willingness-to-message OTA, offer strategy, Supabase service_role access, send timing | P0 pilot launch |
| Business | `smarten-customer-os-thesis:94` | Lock the proceed-vs-collapse conversion threshold BEFORE P0 send (not after) | Whole roadmap commitment |
| Legal | `cs-consent-gdpr-model:78-87` | 9 GDPR/PDPA questions: consent wording, Privacy Policy URL, channel granularity, retention, v1→v2, DPO, PDPA review, IP pseudonymisation, **OTA ToS authorization to process PII** | Consent model + service-only enforcement |
| Eng | `smarten-customer-os-thesis:110` + `cs-gap-debate-verdicts:36` (B6) | Supabase↔Django sync spec: which fields, merge key, refresh cadence | B6 Celery sync task |
| Eng | `cs-centralization-design-concept:199-205` | 5 API-contract Qs: OTP expiry, response-time category (FAST/NORMAL/SLOW), consent versioning, after-hours source, dashboard online/away toggle | P1a/P1b frontend |
| Design | `cs-centralization-design-concept:22-35` | WCAG token fix (3 status tokens + gray400 fail AA as text) — add G-05/06/07 or fix hex in `designSystem.js` | Token use in P1b (platform-wide, not CS-only) |

### SOFT BLOCKERS — can defer

- **D1-D6 doc corrections** (`cs-centralization-doc-review:80-89`): factual hygiene before P1b build — incl.
  D4 "anon key = Realtime-only, no row reads" is FALSE (RLS exposes REST reads of CS PII). Apply before code.
- Branding reopened (`thesis:105`); channel-conflict appetite (`:106`); WhatsApp 24h-window scope (`:103`);
  P0 sample underpowered for 2% booking metric (`cs-p0-measurement-protocol:27`).

### GAPS — referenced but never recorded

`Conversation.status` enum + transition rules (what triggers `pending`?); `reopen_count` reset edge cases
(`cs-api-contract:47-50` ↔ `cs-gap-debate-verdicts:70` S3); `Message.sender` per-agent vs unified `cs`;
service-vs-marketing ORM guard (concept only, no query); Supabase merge-key algorithm (conceptual only).
These need pinning before the Step-1 Django migration in the gap-verdicts build order.

## Recommended Edits (UPDATE, do not fork — anti-dup rule)

1. **`smarten-customer-os-thesis.md:42`** — add SUPERSEDED banner on P1b row pointing to
   `[[cs-architecture-decision]]`, OR rewrite row to both-sides-poll (drop Supabase Realtime / `sync_status` /
   Celery→Supabase write). Fixes the only HIGH contradiction.
2. **`index.md`** — add the 5 missing CS notes (+ a real entry for `cs-architecture-decision`) under a
   "Knowledge — CS Centralization" sub-heading.
3. **`cs-centralization-design-concept.md`** — split token-gaps out → new `cs-design-tokens-audit.md` to get
   under the 200-line cap.
4. **`cs-centralization-doc-review.md` D1-D6** — apply factual corrections before any P1b code.
5. Add Related back-links: thesis → consent-model + p0-protocol.

## Related

[[smarten-customer-os-thesis]] · [[cs-centralization-stack]] · [[cs-architecture-decision]] ·
[[cs-api-contract]] · [[cs-consent-gdpr-model]] · [[cs-centralization-design-concept]] ·
[[cs-p0-measurement-protocol]] · [[cs-centralization-doc-review]] · [[cs-gap-debate-verdicts]]
