---
name: cs-p0-measurement-protocol
description: P0 rebooking-rate test that gates the CS Centralization conversion thesis — email ~35 Confirmed Supabase OTA travelers a tracked direct-booking offer, measure 30-day direct rebooking. Directional pilot (small N), not significance test. 5 owner decisions block start.
metadata:
  type: project
  status: ready-to-run
  date: 2026-06-21
  parent: smarten-customer-os-thesis
---

# P0 Measurement Protocol — OTA→Direct Rebooking

> **Gap-5 closure 2026-06-21** (business-analyst). The single test that decides whether the OTA→direct conversion objective is built or killed. If P0 fails → collapse to CS-tooling-only ([[smarten-customer-os-thesis]] consequence). Runnable by business owner, near-zero cost, ~5 weeks to verdict.

## Hypothesis + metric
- **H0:** OTA travelers who get a Smarten service touchpoint do NOT rebook direct above ~zero.
- **Metric:** direct rebooking rate = (tracked attributable direct bookings) / (travelers messaged), measured at **day 30 per individual** (not batch date).
- Revised P0 (post-Supabase): not "can we capture contacts" (yes, 80%+) — measure "do captured travelers **rebook direct**."

## Sample (~25-45 usable)
Filter `gmail12go.Information`: **Status=Confirmed** · travel date 2026-01-01→2027-01-01 (exclude `5000-08-02` outlier) · Gmail non-null · **Langkawi/Koh Lipe routes only** (no route-mixing confound). 58 total → ~25-45 after filter (run live query, ~5min).

**Honest power statement:** 58 records is NOT significance-adequate (5% rate needs ~700 contacts @ 80% power). This is a **directional pilot** — "is this plausible?" not "is this proven?" 0-1 rebooking = negative; 3+ = positive enough to justify building a bigger contact base. Value = speed + near-zero cost. Don't skip it; building on an unvalidated assumption is worse.

## Method
- **No control group** (sub-groups too small). Single cohort, baseline = current ~10% B2C direct.
- **Service-framed message** (channel-conflict mitigation): thank-you for traveling via 12Go + direct-booking link w/ convenience benefit + opt-in line ("Reply YES for trip updates + offers" = `marketing_consent` capture) + opt-out notice. NOT a marketing campaign — service follow-up.
- **Channel:** AWS SES (live, ~$0, Smarten domain SPF/DKIM).
- **Timing:** future-dated records → pre-trip T-7 (active planning, return-leg intent); past-dated → immediate. One touch per traveler.

## Attribution (the hard part — concrete)
- **Unique tracked link/recipient:** `smartenplus.com/[booking]?ref=p0-[BOOKING_ID]` (Booking_ID from Supabase, e.g. `12GO29980150`). Ties click→record, no new infra.
- **Attributed iff:** (1) clicks link AND (2) completes Smarten booking within 30d AND (3) order email matches Supabase `Gmail` (probabilistic merge — OK for manual small-N review).
- **Discount code (optional, owner Q3):** unique `DIRECT-12GO-xxxx` = robust 2nd signal (survives cross-device click→book). Recommended if offer includes discount.
- **Does NOT count:** order email no Supabase match · rebooks via 12Go again (OTA not direct) · already-direct-before-email.
- **Logging:** pre-send CSV (Booking_ID, Gmail, Name, Date, Destination, send_date, ref_code); day-30 cross-ref Django orders. Manual spreadsheet, no eng.

## Window: 30 days from send
Langkawi-Koh Lipe booked 1-4wk ahead; 30d captures next-trip intent, excludes implausibly-distant. Beyond 30d attribution weakens. **Seasonality:** monsoon ~May-Oct closes Koh Lipe immigration — June/July launch may suppress signal; pre-trip future-dated sends partially mitigate (those travelers committed). If borderline → re-run Oct-Nov high season.

## Threshold + decision rule (set BEFORE send, don't move after)
| Result (~35 contacts) | Decision |
|---|---|
| 0 (0%) | Collapse to CS-tooling. Kill conversion + P5. P1a/P1b efficiency-only. Defer P2/P3. |
| 1 (~3%) | Marginal — single booking unreliable. Extend pilot (+more contacts: Klook/Bookaway if schemas found) or treat negative. |
| 2-3 (~5-9%) | Positive. Proceed full roadmap incl P3/P5. Expect OTA friction <12mo — contractual cover ready. |
| 4+ (10%+) | Strong. Accelerate. Understand discount-driver before scaling (economics shift). |

Below 3% (= 0-1 in 35) collapses demand-side. **CS-tooling spine continues regardless** (independent ROI).

## Confounds / validity threats
- **Small N** — wide CIs. Check SES open/click: open <20% = "didn't see email" ≠ "won't rebook" (different fix).
- **Channel-conflict** — Gmail from 12Go confirmation emails; messaging = contacting their customers; poaching/delisting risk. Service framing minimizes, not eliminates. **Owner decision Q2.**
- **Seasonality** — June/July monsoon suppresses; 0 result then ≠ definitive fail.
- **Self-selection** — agency emails in Gmail field (check `Name` vs `PassengerNames` divergence = group/agency, lower attribution confidence).
- **Single-channel** — email only; 0 doesn't rule out SMS/WhatsApp/on-site.
- **Offer confound** — discount result ≠ service-quality result; document offer size (10% discount + 5% rebook ≠ 5% rebook no-discount).

## Who / when / cost
Owner: approve contact list + offer + copy + send + day-30 go/no-go. Tech (~5-6h total): query Supabase (30m) · ref-code URLs (30m) · copy (2h) · SES config (1h) · day-30 cross-ref (1h). SES ~$0. **Decision→verdict ~5 weeks** (3d prep + 30d window + 2d analysis).

## OWNER DECISIONS (block start — only owner)
1. **Threshold confirm** — use thesis 3%/5-10%? Lock before send.
2. **Willingness to message OTA contacts** — poaching risk acceptable? If no → wait for inbound (website chat P1b) + capture consent there, measure from consent-clean pool.
3. **Offer/discount** — A: none (service-only, clean test, lower conversion) · B: small fixed discount (unique code attribution) · C: free service upgrade (relational, on-brand).
4. **Supabase service_role access** — check Klook/Bookaway schemas to grow sample?
5. **Send timing** — T-7 future-dated / immediate past-dated (recommended) — confirm.

## Related
- [[smarten-customer-os-thesis]] — the P0 gate + thresholds + consequences
- [[supabase-ota-booking-store]] — the data source (58 records, gmail12go)
- [[cs-consent-gdpr-model]] — consent capture in the message (opt-in line)
