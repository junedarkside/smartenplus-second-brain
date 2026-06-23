---
name: ota-consent-comms-pii-gate
description: P3c — GATED. Tier-1 service comms (SES email + AWS SNS day-before SMS) to OTA travelers + Supabase consent.records (RLS) + PII gate on CsOtaBooking. Blocked on contract gate + legal sign-off. Awaiting review.
metadata:
  type: project
  status: awaiting-review
  date: 2026-06-23
  parent: ota-portal-overview
---

# P3c — OTA Consent, Comms & PII Gate (GATED)

## Summary
Proactive outbound comms to OTA travelers (Tier-1 service: booking confirm, boarding, day-before SMS reminder, request responses) + consent storage (`consent.records`) + PII gate. **BLOCKED** on the contract gate (12Go/Klook allow operator→traveler contact) + legal sign-off on consent wording.

## Gates (HARD — owner/legal, not engineering)
1. **Contract gate:** confirm 12Go/Klook supplier contracts permit operator→traveler service contact. Contract law > privacy law here ([[booking-command-centre-decision]] recalibration). Blocks ALL proactive OTA outbound.
2. **Legal:** consent string wording (v1) + Privacy Policy URL + Thai PDPA review ([[cs-consent-gdpr-model]] Q1–Q9).
3. **Tier-3 marketing** additionally gated on **P0 rebooking measurement**.

> P2/P3a/P3b are NOT blocked — they are internal staff tooling + customer-initiated read/request. Only this phase proactively contacts OTA travelers.

## Context
OTA travelers are 12Go/Klook's customers, contacted by SmartEnPlus as the **operator running their trip**. Service comms (Tier 1) are defensible + necessary (contract performance + legitimate interest) — NOT the high-risk poaching prior CS docs framed. Marketing (Tier 3) remains the real risk, kept separate + gated.

## Approach
### 3-tier consent model ([[cs-consent-gdpr-model]])
| Tier | Comms | Opt-in | Channel |
|---|---|---|---|
| 1 Service | confirm, boarding, how-to-travel, trip changes, request responses, **day-before reminder** | No | SES email (live) + **AWS SNS SMS** day-before (`boto3`, zero new dep) |
| 2 Enhanced | faster updates + ongoing support | Yes | WhatsApp/Line (BSP, deferred) |
| 3 Marketing | rebooking / book-direct | Yes (gated P0) | — |

### Consent storage (split identity)
- OTA guests (no Account): **Supabase `consent.records`** — keyed on email, separate from booking row. RLS: anon **INSERT-only** (no SELECT → prevents enumeration), service_role read/write from Django.
- Bridge: on Account creation → migrate Supabase consent → Django `ConsentRecord` (`migrated_from_supabase=True`); Supabase row marked `migrated=true`, retained for audit.
- Consent strings = source-controlled versions (`accounts/consent_versions.py`); FE reads `CURRENT_CONSENT_VERSION` from API, never hardcodes.

### PII gate
Hide `CsOtaBooking` details until OTA user proves ownership via magic-link token (P3a) or completes OTP. Closes loose-end **CS-GUEST-EMAIL-GATE**.

### Enforcement
`MarketingConsentManager` = only marketing-audience API. Model-level block on `comms_type=marketing` for `source=ota` without active consent (after P1 `source` migration — `Order.source` exists; `BookingItem` TBD).

## Files
- **Supabase:** create `consent.records` table + RLS policies (anon INSERT-only).
- **BE new:** `accounts/consent_versions.py`, `MarketingConsentManager`, consent migration bridge, SNS day-before reminder task (Celery beat), `consent/current-version/` endpoint.
- **FE:** consent capture UI (Tier-2), My-Trip consent toggle.

## Risks / tradeoffs
- **Contract gate = real blocker** — building P3c code before the gate clears risks unusable outbound. Recommend: build consent infra + PII gate now (ungated); defer SNS/email send activation until gate clears.
- **Erasure (GDPR Art 17)** — Supabase PII anonymization is the hard part; `DataErasureRequest` model + 2 Celery tasks (Django + Supabase service_role), 30-day window. Scope separately.
- **Probabilistic email merge** — consent keyed on email inherits 20–40% merge noise.

## Review focus
- Is the gate boundary right (build consent infra + PII gate now, defer send activation)?
- RLS anon INSERT-only on `consent.records` — sufficient, or needs CAPTCHA/rate-limit on the insert?
- Day-before SMS via SNS — confirm AWS account has SNS SMS enabled (SES confirmed; SNS unverified).
- Erasure scope — include in P3c or split to its own gated note?

## Verification
- Tier-1 sends without opt-in; Tier-2/3 blocked without active consent.
- Anon key can INSERT but not SELECT `consent.records` (enumeration test fails).
- PII gate: `CsOtaBooking` details hidden until valid magic-link token.
- Migration bridge preserves timestamps + versions (`migrated_from_supabase=True`).

## Related
[[ota-portal-overview]] · [[cs-consent-gdpr-model]] · [[booking-command-centre-decision]] · [[cs-api-contract]] · [[supabase-ota-booking-store]]
