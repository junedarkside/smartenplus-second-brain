---
title: Marketing Tools Debate 2026 — Coupon Admin UI verdict
type: area
status: active
created: 2026-07-29
tags: [marketing, coupon, admin-dashboard, roadmap, business-development]
related:
  - "[[content-marketing-strategy]]"
  - "[[business-development-thesis-2026]]"
  - "[[coupons]]"
---

# Marketing Tools Debate 2026

5-agent debate (UXUI · Marketing · NextJS/FE · Django/BE · Biz-dev), one round + synthesis.
Question: **"What is the better marketing tool to build NEXT?"**
Anchor: backend `Coupon` model fully built, admin-dashboard has zero coupon UI.

## Verdict — UNANIMOUS

**Ship the Coupon Admin UI first.** All 5 agents ranked it #1 independently.
It is not a new feature — it exposes a trapped, production-tested capability. Lowest risk,
highest leverage, ~1 sprint, no new models, no migrations.

## Why (the trapped-capability argument)

- Backend `Coupon` model complete + validated + used in prod (marketers manage via raw Django admin today).
- Frontend customer coupon UI already live (`components/checkout/Coupon.js`).
- Only missing piece = a management CRUD UI in the admin-dashboard app.
- Cost ≈ clone `HeroBannerForm.js` CRUD pattern + one backend ViewSet. Sub-day FE, ~120 lines BE.

## Synthesis table — ranked marketing tools

| Rank | Tool | ROI | Build effort | New BE models? | Reuse |
|---|---|---|---|---|---|
| 1 | **Coupon Admin UI** | Very High | Very Low | None | HeroBannerForm CRUD + existing Coupon model/endpoints |
| 2 | **Campaign / attribution tracking** | High | Low | None (1 aggregation endpoint) | dashboardApi + DataGrid; UTM→order tag |
| 3 | **Cross-sell Bundle MVP** | Very High (strategic) | Medium | Yes (Bundle) | Coupon operator/route M2M targeting; existing cart |
| 4 | **Referral program** | Medium | High | Yes (Referral+ledger) | coupon form clone (FE trivial, BE heavy) |
| 5 | **Loyalty / points** | Low-Med now | Very High | Yes (ledger+rules) | nothing — defer |

## Where agents diverged (resolved)

- **#2 slot:** FE/Marketing/Biz-dev want **campaign/attribution tracking** next (cheap, makes
  everything measurable, satisfies the vault's own Journey-Builder gating condition). UXUI/BE
  leaned to a coupon usage-stats view. → **Resolved: attribution tracking is #2** — it's the
  measurement layer that unblocks validating everything after it. Coupon stats endpoint folds
  into it.
- **Bundles-first?** Biz-dev confirmed bundles = the revenue-per-traveler thesis but must stay
  **gated** until coupon campaigns + attribution prove conversion. No inversion. Bundle MVP
  scoped thin (transport + 1 add-on), not a full itinerary builder.

## Exact BE delta to ship #1 (verified from code, no new models)

1. `CouponAdminSerializer` — full fields incl. `id`, `read_only=['times_used']` (existing
   `CouponSerializer` is read-only order fragment, omits `id`).
2. `CouponViewSet(ModelViewSet)` behind `IsAdminOrIsStaff` (permission class already imported
   `orders/views.py:22`), search on `code`, ordering on dates/active/times_used.
3. One router line: `router.register('admin/coupons', CouponViewSet, ...)`.
   Model's `clean()` already enforces %≤100 and valid_from<valid_to → free validation.

## Exact FE delta (~3 files, ~90% copy-paste)

- `store/api/couponsApi.js` — clone `heroBannersApi.js`, swap endpoint strings.
- `components/coupons/CouponForm.js` — clone `HeroBannerForm.js`, drop image upload,
  add date pickers + discount_type select + max_uses input. Formik+Yup, existing pattern.
- `pages/marketing/coupons/index.js` — clone `hero-banners/index.js` (DataGrid + Drawer + delete Dialog).
- No new deps, no new state lib. Backend calculates discount — FE never re-implements the math.

## Over-engineering guardrails (rejected by the debate)

- ❌ No separate `coupons` Django app — model lives in `orders`, splitting = pure churn.
- ❌ No bulk-generate endpoint day one (needs Celery). Single-create first.
- ❌ No `/api/v2/` versioning for an internal admin surface.
- ❌ No "campaign management" abstraction layer grouping coupons — ops needs a form, not a system.
- ❌ No client-side discount preview math (drifts from backend rules).
- ❌ No WYSIWYG/drag-drop, no new charting lib — reuse existing dashboard chart component.
- ❌ No generic "marketing tool builder" configurable form for both coupons+bundles — two simple forms beat one clever one.
- ❌ Don't wrap `validate_coupon()` in CRUD path — it's an order-context validator, not a definition validator.

## Recommended sequence

1. **Coupon Admin UI** (now) — unblock marketers from Django admin. Gate to exit: ≥1 campaign launched + tracked.
2. **Campaign / attribution tracking** (parallel/next) — UTM→order tag + coupon usage stats. Measurement layer.
3. **Cross-sell Bundle MVP** (gated) — only after coupon+attribution prove conversion. Thin slice.
4. Referral → 5. Loyalty — deferred behind bundle validation + repeat-purchase baseline.

## Do NOT build yet
Referral, loyalty, gift cards — all need new models/migrations/state machines. Higher risk,
no reuse of the Coupon engine. Revisit after bundle validation.
