---
name: cs-consent-gdpr-model
description: CS Centralization consent/GDPR data model — two-store (Django ConsentRecord + Supabase consent.records), append-only, versioned consent strings, service-vs-marketing enforcement via MarketingConsentManager. 9 owner/legal questions open.
metadata:
  type: decision
  status: draft
  date: 2026-06-21
  parent: smarten-customer-os-thesis
---

# CS Consent / GDPR Data Model

> **Gap-3 closure 2026-06-21** (business-analyst). Posture (from [[smarten-customer-os-thesis]]): **service-only-by-default** — OTA-sourced contact is service-comms only until explicit opt-in; never auto-sync to marketing. Audience: EU (GDPR) + US + Thai (PDPA).

## 1. Storage — TWO-STORE (split identity)

Two traveler types, must not conflate:
- **Registered** — Django `Account` exists.
- **OTA guest** — exists only in Supabase `gmail12go.Information`, no Account, email-only merge key (20-40% noise).

**Do NOT** add `marketing_consent` as flat columns on `gmail12go.Information` (one-per-booking not one-per-person, no version, no surface, no withdrawal, no proof — fails GDPR).

| Store | Population | Shape |
|---|---|---|
| **Django `ConsentRecord` table** | registered | append-only log, FK→Account |
| **Supabase `consent.records` table** | OTA guests | keyed on email, separate from Information booking row |

**Bridge rule:** OTA guest later creates Account → P1a identity-merge migrates Supabase consent → Django `ConsentRecord` (`migrated_from_supabase=True`, preserve timestamps+versions); Supabase row marked `migrated=true`, retained (never deleted) for audit.

## 2. Record schema (what each captures)

**Django `ConsentRecord`** (accounts/models.py — append-only, never UPDATE):
`account` FK(PROTECT, null during migration) · `action` (granted/withdrawn) · `timestamp_utc` (explicit, NOT auto_now_add — allows historical migration) · `consent_string_version` (e.g. `marketing-v1`) · `consent_string_text` (verbatim text shown — preserved even after v2) · `surface` (chat_widget/otp_flow/checkout/migration) · `legal_basis` (default consent) · `ip_address` (GDPR proof) · `user_agent` · `migrated_from_supabase` · `supabase_consent_uuid`.

Live state = property (not stored field): `marketing_consent_active` = latest row by `timestamp_utc` has `action=granted`. Withdrawal = new `withdrawn` row, never delete.

**Supabase `consent.records`:** uuid PK · `email` · `booking_id` (null) · `action` · `timestamp_utc` · `consent_string_version` · `consent_string_text` · `surface` · `legal_basis` · `ip_address` · `user_agent` · `migrated` bool. RLS: service_role full; anon INSERT-only (no SELECT — prevents enumeration). Django reads via service_role.

## 3. Consent-string versioning

Consent string = legal instrument, not microcopy. Change one word → new version → v1 consenter has NOT consented to v2.

`marketing-v1` (design-concept draft): "Keep me updated on travel deals and SmartEnPlus news. I can unsubscribe any time. This is optional and separate from messages about your booking."

Version registry = **source-controlled constant** (`accounts/consent_versions.py`), NOT a DB table (git = auditable). FE reads `CURRENT_CONSENT_VERSION` from API (`GET /api/consent/current-version/` → `{version, text}`), never hardcodes. Server serves text + records version → stored `consent_string_text` always matches what was served.

v2 eligibility check: `is_eligible_for_marketing(account, required_version)` — v1 consenter NOT auto-eligible for v2 campaigns unless campaign explicitly accepts v1 (owner decision Q5).

## 4. Service vs Marketing enforcement (structural, not documentary)

| Service (no consent — contract/legitimate-interest) | Marketing (needs consent) |
|---|---|
| booking confirm, trip reminder SMS, chat reply, status change, OTP | deals, newsletter, upsell, re-engagement, any bulk not tied to current booking |

**3 enforcement mechanisms:**
1. **`MarketingConsentManager.eligible_for_marketing(version)`** — the ONLY API returning a marketing audience (filters to active GRANTED). Bulk-send Celery tasks accept only this queryset. Dev must actively work around it to violate.
2. **`comms_type` field** on Message (service/marketing) — CS Dashboard exposes only `service` send; marketing UI (if built) gated `is_superadmin`. Self-documenting audit log.
3. **OTA source guard** — after P1a `source` migration on Order/BookingItem, block `comms_type=marketing` on `source=ota` order without active consent (model-level).

> Note grill finding: Order/BookingItem have NO `source` field today → service-only-by-default is currently unenforceable. `source` migration is required P1a deliverable before any comms.

## 5. GDPR essentials

| Comms | Lawful basis | Art |
|---|---|---|
| booking confirm | contract | 6(1)(b) |
| trip reminder | legitimate interest | 6(1)(f) |
| chat reply | contract/LI | 6(1)(b)/(f) |
| marketing | **consent** | 6(1)(a) |

- **Consent quality** (Art 7/Recital 32): freely-given (unchecked, not a gate) ✅ · specific ✅ · informed (needs Privacy Policy link — GAP Q2) · unambiguous (active opt-in) ✅ · granular (one checkbox email+SMS — Q3).
- **Withdrawal** (Art 7(3)): email unsubscribe link (signed token, 30day, no login) + SMS `STOP` (SNS native) + My-Trip toggle (P2). New `withdrawn` row, re-evaluate per-send.
- **Erasure** (Art 17): Django = anonymise/cascade. **Supabase = hard part** — null/hash PII in `gmail12go.Information` + `consent.records` (keep event, anonymise identity). Not instant — `DataErasureRequest` model + 2 Celery tasks (Django + Supabase service_role), 30-day window (Art 12).
- **ROPA** (Art 30): `ConsentRecord` = technical record; separate ROPA doc lists purpose/basis/categories/retention/processors (SES, SNS, Supabase)/EU-transfer (confirm AWS region).
- ePrivacy (EU) + CAN-SPAM/TCPA (US) satisfied by opt-in + opt-out.

## 6. OWNER / LEGAL QUESTIONS (batched — only owner can answer)

1. **Consent string wording** — legal sign-off (GDPR + Thai PDPA). Locks as v1.
2. **Privacy Policy link** — exists? URL? inline or adjacent? (Art needs informed consent.)
3. **Channel granularity** — one checkbox (email+SMS) or two?
4. **Consent retention period** — after delete/withdrawal (3-5yr legal-claims window?).
5. **v1→v2 upgrade policy** — v1 valid for all future / re-consent / segment?
6. **DPO / data-controller** — named GDPR contact for Privacy Policy.
7. **Thai PDPA review** — done/planned?
8. **IP pseudonymisation** — raw IP retention (90d→hash?) + full IP or prefix-only?
9. **OTA data processing** — confirmed 12Go ToS permits processing PII from confirmation emails? (channel-conflict/data-origin — consent doesn't cure upstream.)

## Concrete engineering artifacts
`ConsentRecord` model (§2) · version registry (§3) · `MarketingConsentManager` (§4). §5-6 = legal/ops obligations before any consent surface goes live.

## Related
- [[smarten-customer-os-thesis]] — service-only posture
- [[supabase-ota-booking-store]] — gmail12go store, OTA identity
- [[cs-centralization-design-concept]] — consent microcopy + versioning
- [[cs-api-contract]] — `/api/consent/current-version/`
