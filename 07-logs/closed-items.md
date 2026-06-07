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
