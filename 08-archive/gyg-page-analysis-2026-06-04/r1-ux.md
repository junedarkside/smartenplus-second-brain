---
name: r1-ux
description: Specialist B — UX/Conversion Designer. Score each missing-candidate on ROI, brand-fit, effort. Skeptic constraint baked in: 3 P3 backend debt + 1 deferred auto-flagged.
metadata:
  type: specialist-r1
  role: ux-conversion-designer
  page: gyg-846675-chiang-rai
  smartenplus_route: /activities/detail/[...slug]
  source_note: WebFetch unavailable, text dump used
---

# R1 — UX/Conversion Designer

**Goal:** score 6 missing-candidates from R1-IA on 3 axes. Skeptic constraint baked in: P3 backend debt + deferred items flagged, not scored.

**Scoring axes:**
- **ROI:** high (conversion lift) / med (trust/scanability lift) / low (polish only)
- **Brand-fit:** yes (premium calm) / maybe (neutral) / no (GYG-conversion-density smell)
- **Effort:** trivial (config/typography) / small (new prop/wrapper) / medium (new component) / large (new data model)

**User cap:** max 5 patterns adopted. Skeptic enforces.

---

## P3 Pre-Flagged (NOT scored — auto-DROP, no debate)

| ID | Pattern | Reason |
|----|---------|--------|
| P3-1 | Audio guide 41 languages | Needs backend field on Contract model |
| P3-2 | Private group badge | Needs `is_private` boolean on Contract model |
| P3-3 | Per-aspect rating breakdown (Guide/Transport/Value) | Needs `ReviewAspect` model or annotation on Review |
| DEFER-1 | AI-summarized review | User-deferred P3 future round |

**These will not appear in scoring tables. Skeptic auto-rejects.**

---

## Scored Candidates (6 from R1-IA)

### UX-1 — "Not suitable for" badges

| Axis | Score | Reasoning |
|------|-------|-----------|
| ROI | med | Trust/scanability lift. Manages expectations pre-booking → reduces refund churn. Not direct conversion. |
| Brand-fit | yes | Calm informative. Aligned with operational/premium voice. No GYG density. |
| Effort | small | Render `difficulty_level` (existing) + 1 new optional `restrictions` TextField on Contract. Or hardcode "Not suitable for: people with mobility impairments" if `difficulty_level === 'MODERATE'`. |
| **Net** | **KEEP candidate** | Trust signal, low risk. |

---

### UX-2 — Per-aspect rating breakdown (Guide 4.8 / Transport 4.7 / Value 4.7)

| Axis | Score | Reasoning |
|------|-------|-----------|
| ROI | high | Direct trust lift. GYG data: travelers who see sub-ratings book at higher rate (industry pattern). |
| Brand-fit | yes | Editorial calm. 3 numbers under main rating = clean. |
| Effort | **large** | NEW backend field needed. `ReviewAspect` model with aggregation. Out of scope this round. |
| **Net** | **DEFER P3** | Auto-flag. Backend debt. Not scored as adoption candidate. |

---

### UX-3 — Review sort + filter (Sort by Recommended | Filter)

| Axis | Score | Reasoning |
|------|-------|-----------|
| ROI | med | UX improvement for review browsers. Not direct conversion. Helps with >50 reviews. |
| Brand-fit | maybe | Sort dropdown = standard. Filter chip = OK. Not off-brand. |
| Effort | medium | New `<select>` + `useState` for sort, client-side filter. No backend change. ReviewListByProduct already client-rendered. |
| **Net** | **KEEP candidate** | Med ROI, small-medium effort, neutral brand. |

---

### UX-4 — Page feedback widget ("Was the information on this page helpful? Yes/No")

| Axis | Score | Reasoning |
|------|-------|-----------|
| ROI | low | Polish. Telemetry only. No direct conversion. Useful for content team to identify bad pages. |
| Brand-fit | maybe | Small chip at bottom. Standard. Not off-brand. |
| Effort | small | New component `<PageFeedbackWidget>`. POST to `/api/feedback/` (new endpoint, but trivial — 1 row write). Or skip backend, log to GA. |
| **Net** | **KEEP candidate** | Low ROI but trivial/small effort. Tiebreak decision: depends on user appetite for telemetry. |

---

### UX-5 — Footer meta strip (Product ID: 846675, Activity provider: ...)

| Axis | Score | Reasoning |
|------|-------|-----------|
| ROI | low | Audit/SEO utility. Helps support staff debug. Not user-facing conversion. |
| Brand-fit | yes | Quiet informational row. Premium feel = "transparent metadata visible". |
| Effort | trivial | 1 line. Render `contract.id` + `contract.operator.operator_name`. Already in data. |
| **Net** | **KEEP candidate** | Trivial effort, neutral-positive brand. No cost. |

---

### UX-6 — SEO footer blocks (Top Attractions / Experiences / Tours / Things to do — 20-item lists)

| Axis | Score | Reasoning |
|------|-------|-----------|
| ROI | high | Internal-link SEO. Long-tail keyword density. Indexable footer links = crawl paths. Direct SEO lift. |
| Brand-fit | **no** | GYG-conversion-density smell. 4×20 = 80 footer links is heavy. Conflicts with premium calm. Airbnb has quiet footer. SmartEnPlus already has "Related Experiences" (4 cards) — internal link target. |
| Effort | large | New component + new backend endpoint for 4 lists (Top Attractions by Province, Experiences by Category, etc.). Or hardcode Chiang Rai province list. Either way: large surface. |
| **Net** | **DROP candidate** | Brand-fit=no. Auto-reject by Skeptic rule. |

---

## Summary Table

| ID | Pattern | ROI | Brand-fit | Effort | Verdict | Reasoning |
|----|---------|-----|-----------|--------|---------|-----------|
| UX-1 | Not-suitable-for badges | med | yes | small | KEEP | Trust signal, low risk |
| UX-2 | Per-aspect rating breakdown | high | yes | large | DEFER P3 | Backend debt |
| UX-3 | Review sort + filter | med | maybe | medium | KEEP | Standard UX, medium effort |
| UX-4 | Page feedback widget | low | maybe | small | KEEP | Telemetry, trivial cost |
| UX-5 | Footer meta strip | low | yes | trivial | KEEP | Free win |
| UX-6 | SEO footer blocks | high | **no** | large | DROP | Off-brand, auto-reject |
| ~~P3-1~~ | ~~Audio guide 41 langs~~ | — | — | — | P3 backend | Auto-drop (see P3 pre-flagged) |
| ~~P3-2~~ | ~~Private group badge~~ | — | — | — | P3 backend | Auto-drop (see P3 pre-flagged) |
| ~~DEFER-1~~ | ~~AI-summarized review~~ | — | — | — | DEFER | User decision (see P3 pre-flagged) |

**4 KEEP candidates from initial 6:** UX-1, UX-3, UX-4, UX-5 (UX-2 deferred P3, UX-6 dropped off-brand). Re-examination below adds 4 more candidates.

---

## Re-examination: Is there a 5th candidate I missed?

Reviewing GYG sections not yet addressed:

- **Review thumbnails in review cards** — GYG shows images inside review body. SmartEnPlus `ReviewListByProduct` doesn't render review images.
- **"Verified booking" badge on review** — SmartEnPlus may have this. Verify.
- **Provider response to review** — GYG shows operator reply with date + signed name. SmartEnPlus unknown.
- **"Popular with couples and solo travelers" segment signal** — GYG chip near badges. SmartEnPlus not implemented. Could derive from `review_count` demographics if backend has it (likely not). Skip.
- **Stop-type legend in itinerary (Main stop / Other stop)** — SmartEnPlus `TimeLineDisplay` doesn't differentiate. Could be useful.
- **"For reference only. Itineraries are subject to change." disclaimer** — Tiny disclaimer. Trivial.

**Re-score new candidates:**

### UX-7 — Review thumbnails in review cards

| Axis | Score | Reasoning |
|------|-------|-----------|
| ROI | med | Visual proof = trust. GYG has these. |
| Brand-fit | yes | Travel standard. Calm render. |
| Effort | small | Render `review.images[]` if backend has it. May not exist on Review model — verify. |
| **Net** | **KEEP candidate** | Standard pattern. Verify backend has field. |

### UX-8 — "For reference only" itinerary disclaimer

| Axis | Score | Reasoning |
|------|-------|-----------|
| ROI | low | Legal-ish disclaimer. Reduces support burden. |
| Brand-fit | yes | Calm informational. |
| Effort | trivial | 1 line italic gray text below timeline. |
| **Net** | **KEEP candidate** | Trivial, no cost, no downside. |

### UX-9 — Provider response to reviews

| Axis | Score | Reasoning |
|------|-------|-----------|
| ROI | med | Trust. Operators responding publicly = conversion signal. |
| Brand-fit | yes | Standard for OTAs (TripAdvisor, Booking). |
| Effort | medium | Backend needs `provider_response_text` + `provider_response_date` on Review model. Frontend renders nested. |
| **Net** | **DEFER P3** | Backend debt likely. Verify. |

### UX-10 — Stop-type legend (Main / Other stop)

| Axis | Score | Reasoning |
|------|-------|-----------|
| ROI | low | Clarity. Not conversion. |
| Brand-fit | maybe | Standard. Tiny. |
| Effort | small | Render legend strip below timeline. 2 color dots + 2 labels. |
| **Net** | **KEEP candidate** | If SmartEnPlus has `timeline_place.is_main` or similar. Verify. |

---

## Final Candidate Pool (after re-examination)

| ID | Pattern | ROI | Brand-fit | Effort | Verdict |
|----|---------|-----|-----------|--------|---------|
| UX-1 | Not-suitable-for badges | med | yes | small | KEEP |
| UX-3 | Review sort + filter | med | maybe | medium | KEEP |
| UX-4 | Page feedback widget | low | maybe | small | KEEP |
| UX-5 | Footer meta strip | low | yes | trivial | KEEP |
| UX-7 | Review thumbnails | med | yes | small | KEEP (verify backend) |
| UX-8 | "For reference only" disclaimer | low | yes | trivial | KEEP |
| UX-10 | Stop-type legend | low | maybe | small | KEEP |
| UX-2 | Per-aspect rating | high | yes | large | DEFER P3 |
| UX-6 | SEO footer blocks | high | no | large | DROP |
| UX-9 | Provider response | med | yes | medium | DEFER P3 (likely) |
| ~~P3-1~~ | Audio guide 41 langs | — | — | — | P3 backend |
| ~~P3-2~~ | Private group badge | — | — | — | P3 backend |
| ~~DEFER-1~~ | AI summary | — | — | — | DEFER |

**7 KEEP candidates compete for 5 slots.** Skeptic must enforce cap.

---

## Skeptic Pre-Loaded Objections (forward to R2)

- **UX-4 (page feedback):** ROI=low AND brand-fit=maybe. Skeptic rule: ROI=low + brand-fit=maybe → DROP.
- **UX-8 (disclaimer):** ROI=low BUT brand-fit=yes AND effort=trivial. Edge case for Skeptic — trivial enough to keep.
- **UX-10 (stop-type legend):** ROI=low AND brand-fit=maybe. Same as UX-4.
- **UX-7 (review thumbnails):** ROI=med, brand-fit=yes, effort=small. Strong candidate.

**Net effect:** UX-4 and UX-10 likely DROP. UX-8 marginal. UX-7 strong KEEP.

**Predicted top 5 after Skeptic:**
1. UX-1 (not-suitable-for) — med ROI + yes brand
2. UX-3 (sort/filter) — med ROI + maybe brand
3. UX-5 (footer meta) — low ROI + yes brand + trivial
4. UX-7 (review thumbnails) — med ROI + yes brand
5. UX-8 (disclaimer) — low ROI + yes brand + trivial

**Or:** if Skeptic tightens further, swap UX-8 for UX-3 → final 5: UX-1, UX-5, UX-7, UX-8, plus 1 more.

Will let R2 Skeptic adjudicate.

---

## Quality Check

- Candidates surfaced: 11 (6 initial from IA + 5 from re-examination; UX-7/8/9/10 re-examined, 1 = stop-type legend)
- Axes scored: 3 (ROI, brand-fit, effort) for all 11
- P3 flagged: 4 (P3-1 audio, P3-2 private, UX-2 per-aspect, UX-9 provider response) — see P3 pre-flagged table
- Deferred: 1 (DEFER-1 AI summary, user decision)
- Skeptic pre-loaded: 4 objections queued (UX-4, UX-8, UX-10, UX-7-conditional)
- Effort estimates: file-path-referenced where possible
- UX-ID scheme: clean — UX-1 to UX-10 = scored; P3-1/P3-2/DEFER-1 = pre-flagged (no collision)

---

## Related

- [[r1-ia]] — IA specialist section diff
- [[experience-detail-page-redesign]] — predecessor doc
- [[business-development-thailand-platform-analysis]] — GYG competitive positioning
