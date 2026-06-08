# Master State — SmartEnPlus

---

## Section 1 — Session Handoff

**Updated:** 2026-06-08 (session #87)

**Achieved this session (#87):**
- **ProductImages ↔ OperatorImages parity SHIPPED** — 2 repos on `develop`:
  - `admin-dashboard` `c425ff6` — feat(operator-images): bring ProductImages to parity (search/filter, metadata dialog, caption bar)
  - `smartenplus-backend` `e777816` — feat(operators): add alt_text/description/caption to ImageGallery + persist on update
- **Backend schema** — 3 nullable `CharField(250)` on `ImageGallery` (alt_text, description, caption). Migration `0059` applied. Serializer exposes all 3 as writable.
- **Shared module** — `components/Images/shared/` with `ImageMetadataDialog`, `ImageSearchBar`, `useImageSearch`, `DraggableImageCard` (caption bar). OperatorImages + ProductImages both consume it. No duplication.
- **Add-flow carries metadata** — `addImageIfUnique` copies alt_text/description/caption from `OperatorImageGallery` to `ImageGallery` via `imageSelection` payload. No FK, only string refs.
- **Edit-flow reuses contract Save** — click tile → `ImageMetadataDialog` in edit mode → writes to Formik `imageSelection` + provider `useAlert` snackbar → contract Save persists. No separate mutation endpoint. No new save button.
- **Bug fix (debug-mantra)** — symptom "editing alt/description/caption can't be saved" survived 4 hypotheses. Root cause: `operators/views.py:720-722` `elif` branch only wrote `order` on existing `ImageGallery` rows, dropped metadata. CREATE branch (line 711-719) wrote metadata → first save after add worked; every subsequent metadata edit silently lost. Fix: `else` branch with unconditional metadata sync + operator_image fallback chain. `c185523`.
- **3 atoms extracted** — [[django-partial-update-elif-metadata-drop]], [[image-metadata-formik-state-only-save]], [[add-flow-metadata-helper-pattern]]. `index.md` + `log.md` updated.

**Resume point (EXACT):**
1. **Open: IMG-ALT-DEBUG-1** — confirm HMR staleness recurs on future dialogs. Optional refactor: move mutation into `ImageEditDialog`. Atom: [[nextjs-hmr-cross-module-callback-staleness]]. Low priority.
2. **F11-FOLLOWUP content answers** — apply 1-line patches if BD/content team answers differ from defaults. Doc: `00-inbox/2026-06-07-content-questions-help-faqs.md`. Deadline 2026-06-09.
3. **BRANCH-CLEANUP-REMOTE** — 81 merged remote `origin/2606*` branches pending deletion. Use `git for-each-ref` (per BRANCH-INCIDENT-1 lesson) → `xargs git push origin --delete {}`.

**Plan doc:** `/Users/charuwatnaranong/.claude/plans/create-team-to-review-tranquil-pebble.md`

Full plan: [[product-images-operator-images-parity-2026-06-08]]

**Achieved this session (#86):**
- **Operator image alt_text + caption SHIPPED** — 2 repos on `develop`:
  - `admin-dashboard` `71c2352` — feat(operator-images): edit alt_text + caption alongside description
  - `smartenplus-backend` `08b6593` — feat(operators): add alt_text + caption to OperatorImageGallery
- **Schema** — 2 nullable `CharField(250)` on `OperatorImageGallery` (alt_text, caption). Migration `0058`. Serializer exposes both as writable.
- **Dialog UX** — `pages/routemanagement/operators/images/ImageEditDialog.js` now has 3 `TextField`s (alt/description/caption), each `maxLength=250`. Alt text auto-prefills from `<operatorName> - <filename-slug>` when empty. Grid `alt` chain: `alt_text || description || operator_name || ''`.
- **Debug saga** — symptom "only description persists" survived hard refresh. Five `[DBG-IMG-EDIT]` probes (dialog → page → RTK → network → backend) proved code was correct end-to-end. Root cause: Next.js Pages Router Fast Refresh replaced `ImageEditDialog` module (3 fields visible) but left the parent `index.js` module's `handleDialogSubmit` callback stale → it destructured only OLD keys and dropped alt/caption. Hard refresh after the second `.next` recompile finally replaced the parent module. Probes removed, code clean.
- **IMG-ALT-1 CLOSED.** Atom: [[operator-image-alt-caption-fields]]. Debuggable artifact: [[nextjs-hmr-cross-module-callback-staleness]].

---

## Section 2 — Loose Ends (Open)

| # | Issue | Status | Where |
|---|-------|--------|-------|
| **IMG-PARITY-1** | ProductImages ↔ OperatorImages parity | **CLOSED** (#87). 3 backend fields (alt_text/description/caption) on `ImageGallery` (migration 0059), 4 shared components in `components/Images/shared/`, add-flow carries metadata, edit-flow reuses contract Save. Both repos on `develop` (`admin-dashboard` `c425ff6` + `smartenplus-backend` `e777816`). 3 atoms extracted. | `components/Images/{ProductImages,OperatorImages,shared/*}.js`, `operators/models.py:520-522`, `serializers.py:151,303`, `views.py:711-728` |
| **IMG-ALT-1** | Operator image alt_text + caption editing | **CLOSED** (#86). 2 nullable CharField(250) on `OperatorImageGallery`, serializer writable, migration `0058`, dialog 3-field + auto-prefill, grid alt chain updated. Both repos on `develop` (`admin-dashboard` `71c2352` + `smartenplus-backend` `08b6593`). Atom: [[operator-image-alt-caption-fields]]. | `pages/routemanagement/operators/images/ImageEditDialog.js`, `index.js:143,263`; `operators/models.py:559-561`, `serializers.py:33` |
| **IMG-ALT-DEBUG-1** | Next.js HMR cross-module callback staleness | OPEN. Fast Refresh can replace a child module (dialog) but leave the parent module's callback stale → new fields silently dropped, hard refresh may or may not fix. Confirmed in #86 via 5-probe instrumentation. Prevention: move mutation call INTO the dialog component, drop parent `onSubmit` indirection. Atom: [[nextjs-hmr-cross-module-callback-staleness]]. Optional refactor. | `pages/routemanagement/operators/images/ImageEditDialog.js`, `index.js:140-178` |
| **IMG-META-BUG-1** | Editing ImageGallery metadata on existing rows dropped | **CLOSED** (#87). `operators/views.py:720-722` `elif` only wrote `order` on existing rows. CREATE branch wrote metadata → first save worked; every subsequent edit lost. Fix: `else` branch with unconditional metadata sync + operator_image fallback chain (`c185523`). Atom: [[django-partial-update-elif-metadata-drop]]. | `operators/views.py:720-733` |
| **BRANCH-CLEANUP-REMOTE** | 81 merged remote `origin/2606*` branches pending deletion | OPEN. Local cleanup (94) done in #84. Need: `git for-each-ref refs/remotes/origin/260 --format='%(refname:short)' | sed 's|^origin/||' | xargs -I {} git push origin --delete {}`. Verify `git branch -r | wc -l` → 2. Run `git fetch --prune`. | `origin/2606*` (81 branches) |
| F11-FOLLOWUP | `/help/faqs` landing page (25-30 Q&As) | **CLOSED** (`43ed62a` #80). New `pages/help/faqs.js` (123 lines) replaces broken catch-all stub. Static segment wins Pages Router over catch-all. Individual Q&As at `/help/faqs/{postSlug}` still route to catch-all (unchanged). Footer link from #72 now serves real Q&A content. 4-agent team debate refined spec. Content questions sent to BD/content team: `00-inbox/2026-06-07-content-questions-help-faqs.md`. If answers differ from defaults, 1-line patches needed. | `pages/help/faqs.js` (NEW), `helpers/wordpress/api.js` (+`POSTS_BY_FAQ_CATEGORY`) |
| F11-FOLLOWUP | B2B corporate CTA strip | DEFERRED. BD recommended. Awaits product decision on 280px slot. | TBD |
| F11-FOLLOWUP | Shared `<Accordion>` / `<FAQAccordion>` atom | DEFERRED. UX flagged. | `components/UI/` (new file) |
| RR-1 | Rate-review Release 1 shipped | P0+P1-1→P1-9 + FE-22 RESOLVED 2026-06-07. **Sprint 1 SHIPPED** (`8ac1029` #74) — P1-3,4,5,6,8,9. P1-7 already done. **Tier 1+2 SHIPPED** (`cc3a0dc` #77) — B1 XSS, B2 race, B3 ProfileImage, B4 Sticky, M1 DOMPurify memo, M2 specific errors, M10 back 44px, N1+N2 cleanup. **Tier 3 SHIPPED** (`6c09c7d` #78) — M6 sticky@md, M7 skeleton, M8 h1 cap, N3 useMemo normalize. **UX gap SHIPPED** (`de964e3` #79) — "Submitting as X" Alert in form. M3 hook extraction deferred — different endpoints/auth. Grill audit verified. Auth model confirmed intentional via `00-inbox/finding-submit-review-auth-2026-06-07.md`. | `RateAndReviewForm.js`, `pages/rate-review/index.js`, `ReviewFirstPage.js`, `ReviewListByProduct.js`, `ReviewImageThumbnails.js`, `pages/rate-review/[reviewSlug].js`, `pages/rate-review/submit-review/[...slug].js` |
| RR-1-FOLLOWUP | `submit-review/[...slug].js:77` brittle slug fallback | API returns `booking_item_slug` only. Confirm contract. Low priority. | `pages/rate-review/submit-review/[...slug].js:77` |
| GSC-1 | GSC Crawled-Not-Indexed | Phase 1+2 shipped, monitoring. Phase 3 needs backend `route_exists`. | `seoConfig.js:41`, `server-sitemap.xml` |
| CMA-1 | Contract Model Ambiguity | P1/P2 partial. Remaining: data inventory. | `operators/models.py` |
| FAV-1 | Favorite heart | **CLOSED** (`951bd9c` FE + `3c0d1b6` BE #83). Both repos merged to develop + pushed to origin. 5 BLOCKERs + 3 NITs closed via 6-agent team workflow. Manual smoke on detail page PASSED. RDS 0026 migration DROPPED per user "doint touch rds" — runbook in vault `01-projects/favorite-heart-analysis-2026-06-08/migration-0026-runbook.md` for whoever runs prod migrations. Vault docs: `audit.md` + `r1-{backend,frontend,ux}.md` + `r2-skeptic.md` + `r3-leader-synthesis.md`. | `dialogue/views.py`, `BookmarkButton.js`, `LikeButton.js`, `DayTripCard.js`, `AirbnbPhotoGrid.js`, `store/api/api-slice.js` |
| AT-1 | Airport Transfer redesign | P0. Spec: `03-knowledge/transportation-category-audit`. | `AirportTransferRouteCard.js` |
| AT-2 | Airport-transfer width mismatch | Inner margins. | `StationInformation.js` etc. |
| 15 | refetchOnMountOrArgChange | Needs justification. | `useTripData.js:16,24` |
| 1 | AdminBookingSummaryViewSet auth | Needs frontend sign-off. | `orders/views.py` |
| 2 | Delete RefundViewSet | Waiting on zero DEPRECATED_ENDPOINT_USED. | `cards/views.py` |
| 3 | Remove Stripe 410 stub | Waiting on zero prod traffic. | `payments/urls.py` |
| 8 | Forex endpoint naming | Naming debt. | `cards/urls.py` |
| Nav | NavigationSection empty | Restart backend + populate. | `pages_info` |
| Explore | location_type CharField | Needs `Location` model change. | `stations/models.py` |
| HD-2 | CartButton dim (70%) | Low — acceptable. | `CartButton.js:116` |
| HD-3 | xl padding gap | Low. | `main-header.js:90` |
| HD-6 | Logo size jump | P2. | `main-header.js:66,95` |
| GAP-3 | Mobile position flip | P2. | `main-header.js:45-77` |
| GAP-5 | Nav hidden while searching | P2 — accepted. | `main-header.js:112` |
| GAP-6 | threshold=0 abrupt snap | P3. | `useStickyVisibility.js:12` |
| GAP-7 | Wordmark hidden md-xl | P3. | `main-header.js:95` |
| **BRANCH-INCIDENT-1** | `develop` branch accidentally deleted in #84 during bulk cleanup | **CLOSED** (#84). Cause: `sed 's/^ //'` only strips 1 leading space. `git branch -d develop` succeeded because develop IS merged (into itself). `-d` only refuses unmerged, not "currently checked out sibling" branches. `main` was checked out, error hidden in 94-successes output. `origin/develop` intact at `f15d7cf`. User self-restored via `git branch develop origin/develop`. **Lesson:** use `git for-each-ref --format='%(refname:short)' refs/heads/` for clean branch names in scripts. Avoid `sed 's/^ //'` + anchored regex on `git branch` output. | N/A |
| **IMG-IND-1** | Operator/contract image independence audit + dialog copy | **CLOSED** (#85). Confirmed intentional separation (no cascade). 1 admin-dashboard file change (informational Alert in delete dialog). Atom: [[django-soft-delete-s3-file-preserve]]. Optional follow-ups (`safe_to_delete` split, `is_deleted` in `_ImageGallerySerializer`) deferred. | `pages/routemanagement/operators/images/index.js:365-376` |
| CART-1 | PARSING_ERROR catch | **CLOSED** (#82). Branch added at `DayTripBookingWidget.js` before generic `else` — surfaces `error.status === 'PARSING_ERROR'` (RTK Query string from HTML 500 page) with clear user-facing message. Per `01-projects/cartitems-500-error-analysis-2026-06-02` Bug 3 + `03-knowledge/view-utility-call-exception-wrapper.md` caveat. No backend change. | `smartenplus-frontend/components/activities/detail/DayTripBookingWidget.js` |
| HD-1 | CurrencySelector small tablet | **CLOSED** (#82). Audit claim 40×24 stale — codebase already has `min-h-[40px] min-w-[40px]` per WA-6 user feedback 40px standard. Actual path `components/UI/CurrencySelector.js:55` (audit said `search/`). | `components/UI/CurrencySelector.js:55` |
| FAQ-1 | ExperienceFAQ | P0-P2 done. Admin `ageRestriction` deferred. | `admin-dashboard/DayTripDetails.js` |
| IDX-1 | Unindexed experience-detail | **CLOSED** (#82). | `index.md:25` |
| IDX-2 | Unindexed experience-faq | **CLOSED** (#82). | `index.md` (under Active Projects) |
| IDX-3 | Missing content-marketing-strategy | **CLOSED** (#82). | `index.md:191` |
| IDX-4 | Duplicate-basename wikilinks | **CLOSED** (#82). 3 files renamed with `-overview` suffix, 17 wikilink references + 9 YAML `parent:` fields updated. | `01-projects/*-overview.md` (3 files) |
| WA-1 | Website audit Sprint 1 (F1-F3) | **CLOSED** (2026-06-06 #60). | various |
| WA-2 | Website audit Sprint 2 (F4-F8) | **CLOSED** (`d1fcf47` #62). | `ProductSearchForm2.js` |
| WA-3 | Website audit Sprint 3 (F9-F11) | **CLOSED** (`0b30580` #67 + `d9d1425` #68). | `pages/homepagev2.js` |
| WA-4 | ProfileMenu UX consolidation | DONE (`44e209d` + `40b0a36` + `f4d581f` + `314020c`). | `ProfileButton.js`, `ProfileMenu.js` |
| WA-5 | Footer secondary nav + SearchDialogTrigger touch targets | **CLOSED** (`781bf7a` #70). | 15 files |
| WA-6 | F2 refinements — 40px icon button standard | DONE (`1e4c549` + `fbdca15` + `e782c41`). | `ProductSearchForm2.js`, `CurrencySelector.js`, `ProfileImage.js` |
| WA-7 | ProductSearchForm2 mobile input height inconsistency | **CLOSED** (`f1cbb5d` #63). | `components/search/ProductSearchForm2.js:228,257` |
| F11 | Homepage visible FAQ section | **REWORKED** (`3534e21` #72). | `pages/homepagev2.js`, `lib/homepage/components/TrustStripSection.js` (NEW), `components/layout/footer.js` |
| F11-FIX-1 | Pre-existing `item.locationFields` undefined in /help/faqs | **CLOSED** (`e6d1731` #72-followup). | `pages/help/[...slug].js:39,45,51` |
| TRUST-STRIP-1 | Trust strip white card wrapper | **CLOSED** (`9505117` #72-followup). | `lib/homepage/components/TrustStripSection.js` |
| GYG-IMPL | GYG 5-pattern | **CLOSED** (#73). | `pages/rate-review/[reviewSlug].js:161,479,414-416` |
| RR-1-FOLLOWUP | Submit-review no session guard | **CLOSED** (#79). | `pages/rate-review/submit-review/[...slug].js` |
| RR-1-FOLLOWUP | `[reviewSlug].js:43` dead commented canonical | **CLOSED** (#77 N2). | `pages/rate-review/[reviewSlug].js:43` |

---

**See also:** [[vault-protocol]] (API contract) · [[vault-guardrails]] (architecture) · [[session-history]] (#38-#49) · [[closed-items]] (resolved)
