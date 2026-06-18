---
name: not-suitable-for-section-2026-06-18
description: 5-agent team debate (business/UX/design/backend/frontend+admin) on adding GetYourGuide-style operator-authored "Not suitable for" section to activity detail page across all 3 repos. User decided FULL build. Converged: JSONField enum array on Contract, frontend-mapped labels, replace "Good to know" badges with icon+text list, admin multi-select on BookingConfig.js. Plan file ready.
metadata:
  type: project
  reviewed_by: not-suitable-for-5-agent-team
  date: 2026-06-18
  repos: [smartenplus-frontend, smartenplus-backend, admin-dashboard]
  status: SPEC — plan ready, no code shipped
---

# Not Suitable For Section — 5-Agent Team Debate 2026-06-18

## Summary

GetYourGuide shows a dedicated operator-authored **"Not suitable for"** list on every activity (wheelchair users, pregnant women, heart conditions, age limits). SmartEnPlus only has a derived **"Good to know"** BadgeChip strip from `age_restriction` + `difficulty_level` (`IncludedExcluded.js`). User decided to **build the full feature** across all 3 repos. 5-agent team (business / UX / design / backend / frontend+admin) converged on a clean MVP. This note = the debate + decisions. Execution plan lives in plan file `not-suitable-for-full-build.md`.

## Context

**Why now:** GYG = activity-page benchmark. Prior vault analysis [[gyg-page-analysis-2026-06-04-overview]] adopted a "not-suitable-for badges" P1 — but that shipped only as derived badges (`age_restriction` + `difficulty_level`), NOT an explicit operator-authored list. [[experience-faq-architecture-review-2026-06-02]] separately flagged `age_restriction` is booking-blocking and must not be buried. This round = build the real thing: operator-authored predefined exclusion list, new backend field, admin UI, dedicated FE section.

**Current code reality (verified):**
- `components/activities/detail/IncludedExcluded.js:12-20,48-61` — "Good to know" badges derived from 2 fields.
- Backend `operators/models.py:369-381` — only `difficulty_level` + `age_restriction`. No `not_suitable_for`.
- `0746b2c` "Merge 260605-feat/not-suitable-badges into develop" = the derived-badge version (live).

## Team Convergence

### Business (build case + data model)
- GYG/Klook surface this for **3 commercial jobs**: pre-qualification (ineligible user exits before booking, not after = margin saved), **dispute deflection** ("you were warned at purchase" converts goodwill refund → policy-governed denial), liability positioning (mixed-nationality routes, foreign-jurisdiction customers).
- SmartEnPlus highest-dispute segments (wheelchair/pregnant/elderly/children) = exactly who benefits. Refund/dispute is a known pain area ([[payment-deep-review-2026-06-12]]).
- **Data model = HYBRID** (predefined enum + optional free-text note). **MVP = predefined enum array only**, no free-text v1.
- **Risk:** empty section worse than none → display nothing when blank (NOT "suitable for all" — false claim = liability). Copy = "Operator-provided restrictions — consult your doctor," platform is messenger not medical authority.
- Follow-up metric: add `cancellation_reason_category` enum to GatewayCharge for dispute attribution (separate ticket).

### UX/IA
- **Placement:** standalone section directly **after `IncludedExcluded`**, before MeetingPoint/FAQ. It's the 3rd factual pillar (got/not-got/not-suitable), booking-blocking → must appear before user is deep down page. Mobile scroll order is the binding constraint.
- **Pattern:** icon+text vertical list, NOT chips (chips imply 2-axis scan; an exclusion list of 4-6 items reads faster as rows; matches existing CheckCircle/Cancel list pattern).
- **Empty state:** render nothing.
- **vs "Good to know":** REPLACE — migrate `age_restriction` + `difficulty_level` out of badges into new section, eliminate duplicate-render. Optional 2px left-border warning accent.

### Design (tokens)
- Token = `COLORS.status.warning` (`#F59E0B` amber), NOT error red (soft filter, not broken state).
- Icon = `WarningAmberOutlined` @18px (NOT `CancelIcon` — already = "Not Included" in same file, false equivalence).
- **Extend `IncludedExcluded.js`** (no new file; ~64→~90 lines, under 200 max, contract prop already there).
- Differentiation from "Good to know": chips stay filled/pill; this block = bare icon+text, white ground, no tint. Same hue family, different shape carries semantic weight ([[unified-badge-system-pattern]]).

### Backend
- **Field = `JSONField(default=list, blank=True)`** on Contract — NOT M2M (needless join, values never aggregated), NOT ArrayField (unused in codebase, `contrib.postgres` dependency). JSON list path-upgrades to `{key,note}` dicts for v2 free-text with no schema migration.
- Canonical serializer `operators/serializers.py:557` `ContractDetailSerializer` uses `fields='__all__'` (line 634) → **field auto-exposed, zero serializer edit** on the FE detail endpoint. Add explicitly to `ContractSerializer` (operators:183) + `ProductsContract` (products:374) only if list/card needs it.
- **Migration = additive, zero-downtime safe** (Postgres `ADD COLUMN DEFAULT '[]'::jsonb NOT NULL`, no rewrite). No backfill from `age_restriction` (free text unparseable; keep as legacy fallback).
- **Labels frontend-mapped**, NOT in ContractTranslation (enum keys carry no language; same approach as `difficulty_level` FE mapping). Keeps translation table prose-only.

### Frontend + Admin
- FE prop chain needs **zero wiring** — `contract` object already flows `[...slug].js:121 getStaticProps` → `DayTripDetailPage.js:205` → `IncludedExcluded contract={contract}`. Only edit inside `IncludedExcluded.js`.
- Label map → `constants/dayTripConstants.js` (`NOT_SUITABLE_FOR_LABELS`), correct home (already holds category constants).
- **Remove duplicate `age_restriction` render in `DayTripContent.js:98-115`** in same PR (ghost component, flagged in [[experience-faq-architecture-review-2026-06-02]]).
- SEO/JSON-LD = **NO** (no Schema.org property rewards it; speculative bloat).
- **Admin vault paths were STALE** — corrected by verification:
  - `components/contract/DayTripDetails.js` → actual `components/forms/contract/DayTripDetails.js`; difficulty field actually in `components/forms/contract/BookingConfig.js:54-69`
  - `utils/contractUtils.js` → `components/utils/contractUtils.js`
  - options → `components/contracts/constants.js`; schema → `components/schemas/index.js`; help → `components/contracts/contractFieldHelp.js`
- Admin pattern: MUI `Select multiple` on `BookingConfig.js`, bound via `setFieldValue('notSuitableFor', e.target.value)` (returns array natively). Mirror `difficultyLevel` wiring across the 5 admin files.

## Conflict Resolved — Enum Key Set

Backend proposed health-style keys (`BACK_NECK_INJURY`, `PREGNANCY`…); FE proposed mixed (`wheelchair`, `age_min_5`…). **Canonical set (10 keys, UPPER_SNAKE, FE-mapped labels):**

| Key | Label |
|---|---|
| `WHEELCHAIR_USERS` | Not wheelchair accessible |
| `PREGNANCY` | Not recommended if pregnant |
| `HEART_CONDITION` | Not suitable for heart conditions |
| `BACK_NECK_INJURY` | Not suitable for back/neck conditions |
| `MOBILITY_IMPAIRED` | Requires moderate physical fitness |
| `VERTIGO_MOTION_SICKNESS` | Not suitable for vertigo/motion sickness |
| `FEAR_OF_HEIGHTS` | Not suitable for fear of heights |
| `FEAR_OF_WATER` | Not suitable for fear of water |
| `MIN_AGE_5` | Minimum age 5 years |
| `MIN_AGE_12` | Minimum age 12 years |

Same key set lives 3 places: backend `choices` validation hint, FE `NOT_SUITABLE_FOR_LABELS`, admin `NOT_SUITABLE_FOR_OPTIONS`. Single source of truth = these keys; only labels live FE.

## Decisions Locked

1. MVP = predefined enum array only, no free-text (v2 path preserved via JSON).
2. `JSONField(default=list)` on Contract, auto-exposed via `__all__` serializer.
3. Labels frontend-mapped, never translated backend.
4. Section = icon+text list, amber warning token, after `IncludedExcluded`, extend that file.
5. REPLACE "Good to know" badges; remove duplicate `age_restriction` in `DayTripContent.js`.
6. Empty = render nothing.
7. No JSON-LD.
8. `cancellation_reason_category` on GatewayCharge = deferred follow-up.

## Out of Scope
- Free-text per-item note (v2).
- Search/filter by suitability tag (next sprint — enum keys are the foundation).
- Dispute-attribution enum on GatewayCharge (separate ticket).
- Code shipping (plan file only).

## Related
- [[gyg-page-analysis-2026-06-04-overview]] — predecessor; shipped derived badges only (this supersedes the "not-suitable" line item)
- [[experience-faq-architecture-review-2026-06-02]] — flagged age_restriction booking-blocking + DayTripContent ghost + stale admin paths
- [[experience-detail-page-redesign-2026-06-02]] — parent redesign
- [[payment-deep-review-2026-06-12]] — refund/dispute pain area (business case)
- [[unified-badge-system-pattern]] — fill-vs-no-fill differentiation rule
