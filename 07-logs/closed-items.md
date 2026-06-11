# Closed Items

Archived from master-state.md Section 2. Audit trail only.

| # | Issue | Resolved |
|---|-------|----------|
| WA-1 | Website audit Sprint 1 (F1-F3) | 2026-06-06 #60. F1 (`40c01e2`) + F2 (`0f9df12`) + F2-followups (`1e4c549` + `fbdca15` + `e782c41`) + F3 (`9472df5`) all shipped. Atom: [[icon-button-size-decision]]. |
| DOMAIN-1 | NEXT_PUBLIC_DOMAIN leading space | 2026-06-05. GitHub Secret + deploy confirmed. |
| TL-1 | Timeline stop deletion bug | 2026-06-04. Migration 0028. 3 atoms. |
| CMA-2 | ServiceDetail.js zero i18n fallback | #42. `09d6f3a`. |
| ACT-DEFAULT-CAT | /activities defaulted to DAY_TOUR | 2026-06-05 #49. `3a4db81`. |
| ACT-PAGINATION-RESET | Pagination chip jumped to page 1 | 2026-06-05 #49. `01b3708`. |
| ACT-7 | Phase 1 QA + merge | Done |
| ACT-8 | Backend merge | `2d5a6ee` → develop |
| ACT-9 | Phase 2 pre-flight (backend) | `508949b` |
| ACT-10 | Phase 2 QA + merge | `b552e55` → develop |
| ACT-11 | Phase 3 mobile layout | `f93df66` → develop |
| ACT-12 | Header search | `5eaf8e2` — ready to merge |
| BW-1 | Blog index hero px-4 padding | Already fixed |
| BW-2 | Blog index featured px-2 md:px-4 | Already fixed |
| BW-3 | BlogCard rounded-lg + no mx- | Already fixed |
| EXP-DETAIL-1 | Experience Detail Page redesign | #33 — shipped |
| HEIC-1 | iPhone HEIC review upload | 2026-06-06 #54. Client-side preview via heic2any. `6c10137`. |
| RR-REVIEW-DETAIL-T1+2 | Review detail page Tier 1+2 | 2026-06-07 #77. `cc3a0dc`. B1 XSS, B2 race, B3 ProfileImage, B4 Sticky, M1 DOMPurify memo, M2 specific errors, M10 back 44px, N1+N2 cleanup. |
| RR-REVIEW-DETAIL-T3 | Review detail page Tier 3 polish | 2026-06-07 #78. `6c09c7d`. M6 sticky@md, M7 skeleton, M8 h1 cap, N3 useMemo normalize. M3 hook deferred. |
| RR-1-FOLLOWUP-1 | Submit-review auth model confirm | 2026-06-07 #79. Finding doc `00-inbox/finding-submit-review-auth-2026-06-07.md`. Auth model confirmed intentional (backend `AllowAny` on create + user/guest_email derivation). UX gap "Submitting as X" shipped `de964e3`. |
| F11-FOLLOWUP-LANDING | /help/faqs landing page | 2026-06-07 #80. `43ed62a`. 2 files 139+ (pages/help/faqs.js NEW + api.js +POSTS_BY_FAQ_CATEGORY). Replaces broken catch-all stub. 4-agent team debate (IA/UX/SEO + code-review) refined plan. Content questions pending. |
| CHECKOUT-BTN-1 | Checkout Next btn enabled on advance-booking/auth-loading | 2026-06-10 #90. `92bf653` dropped `isAdvanceBookingError` from `shouldDisableNext`. Fix `FormCard.js` `f7d2956` + backend `aed70f6` (advance_hr + stop_sale enforced at booking creation). |
| CROSS-SELL-1 | BD inventory gate — cross-sell returns 0 | 2026-06-10 #91. Inline booking modal shipped, ContractRecommendationSerializer fixed. Superseded by CROSS-SELL-MERGE. |
| WP-IMAGE-1 | WP Media Library tab + image URL pipeline | 2026-06-10 #88. `99e45b2` (admin) + `b3b8ee0`/`f7010d2` (backend). Root cause: is_deleted=True row leaking through unfiltered imagegallery_set. |
| IMG-PARITY-1 | ProductImages ↔ OperatorImages parity | #87. `c425ff6` + `e777816`. Migration 0059, shared components in `components/Images/shared/`. 3 atoms. |
| IMG-ALT-1 | Operator image alt_text + caption editing | #86. `71c2352` + `08b6593`. Migration 0058, 3-field dialog + auto-prefill. Atom [[operator-image-alt-caption-fields]]. |
| IMG-META-BUG-1 | ImageGallery metadata dropped on existing-row edit | #87. `operators/views.py:720-722` elif only wrote order. Fix `c185523`. Atom [[django-partial-update-elif-metadata-drop]]. |
| FAV-1 | Favorite heart | 2026-06-08 #83. `951bd9c` FE + `3c0d1b6` BE. RDS migration 0026 DROPPED per user — runbook in `01-projects/favorite-heart-analysis-2026-06-08/migration-0026-runbook.md`. |
| BRANCH-INCIDENT-1 | develop branch accidentally deleted in bulk cleanup | #84. `git branch -d develop` succeeded (merged into itself), main checked out. Self-restored from `origin/develop`. Lesson: `git for-each-ref --format='%(refname:short)' refs/heads/` for scripts. |
| IMG-IND-1 | Operator/contract image independence audit | #85. Intentional separation confirmed (no cascade). Informational Alert in delete dialog. Atom [[django-soft-delete-s3-file-preserve]]. |
| CART-1 | PARSING_ERROR catch | #82. Branch in `DayTripBookingWidget.js` before generic else surfaces RTK PARSING_ERROR (HTML 500). |
| HD-1 | CurrencySelector small tablet | #82. Audit claim stale — `min-h-[40px] min-w-[40px]` already present per WA-6 standard. Actual path `components/UI/CurrencySelector.js:55`. |
| IDX-1..4 | index.md lint (unindexed pages, dup-basename wikilinks) | #82. 3 files renamed `-overview`, 17 wikilinks + 9 YAML parents updated. |
| WA-2 | Website audit Sprint 2 (F4-F8) | `d1fcf47` #62. |
| WA-3 | Website audit Sprint 3 (F9-F11) | `0b30580` #67 + `d9d1425` #68. |
| WA-4 | ProfileMenu UX consolidation | `44e209d` + `40b0a36` + `f4d581f` + `314020c`. |
| WA-5 | Footer secondary nav + SearchDialogTrigger touch targets | `781bf7a` #70. 15 files. |
| WA-6 | F2 refinements — 40px icon button standard | `1e4c549` + `fbdca15` + `e782c41`. |
| WA-7 | ProductSearchForm2 mobile input height | `f1cbb5d` #63. |
| F11 | Homepage visible FAQ section | REWORKED `3534e21` #72. TrustStripSection.js NEW. |
| F11-FIX-1 | item.locationFields undefined in /help/faqs | `e6d1731` #72-followup. |
| TRUST-STRIP-1 | Trust strip white card wrapper | `9505117` #72-followup. |
| GYG-IMPL | GYG 5-pattern | #73. `pages/rate-review/[reviewSlug].js:161,479,414-416`. |
| RR-1 | Rate-review Release 1 | Shipped #74-#79 (`8ac1029`, `cc3a0dc`, `6c09c7d`, `de964e3`). All tiers + UX gap. M3 hook extraction deferred (different endpoints/auth). Auth model confirmed intentional. |
| RR-1-FOLLOWUP | Submit-review no session guard | #79. |
| RR-1-FOLLOWUP | [reviewSlug].js:43 dead commented canonical | #77 N2. |
