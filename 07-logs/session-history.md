# Session History

Archived from master-state.md. Latest session stays in master-state.md Section 1.

---

## Session #357 (2026-08-25)

**Achieved (#357) — AD location image system built out (preview, WP media reuse, compression) + 5th occurrence of a double-prefix image URL bug hunted down and fixed across 2 sessions.**

1. Tiptap editor reused for AD Location description (was plain textarea — first REUSE FIRST search missed it, `Tiptap` isn't FormControl-wrapped). AD `e4671f4`.
2. `LocationImagePicker.js` — image preview + WP media picker, single-select, reusing shared building blocks (`ImageCard`, `ImagePreviewModal`, `ImageGrid`, `ImageSearchBar`). BE `2d58d5a` + AD `afef6fc`. `Location.image` now accepts uploaded file OR verbatim WP URL.
3. Image compression wired via `process_operator_image()` (WebP, 300KB/1920px budget, same as operator hero).
4. 5th double-prefix occurrence fixed: `SummaryLocationSerializer` (`/locations` index, 4th occurrence) + `LocationPageSerializer` (`/destinations`, 5th) via `location_image_url()` guard. BE `4fc945e` + `1186b2a`. Hatyai card live-verified 403→200.
5. AD Locations list image thumbnail column (`LocationThumbnail.js`, mirrors `PlaceThumbnail.js`). AD `a665a95`.

**Threshold flagged:** a 6th double-prefix occurrence = build the shared fix (model property/mixin), not a 6th inline guard.

---

## Session #356 (2026-08-25)

**Achieved (#356) — Full SEO/AEO/GEO audit of `/locations/[slug]` + all 12 fix items shipped across 3 batches, backend migration included.**

`seo-specialist` agent audit found title/meta templated, zero LLM-extractable claim, FAQ not in DOM, no rel=nofollow, lastReviewed always "now", broken hero alt, no hreflang. 3-agent review (Next.js/Django/SWE) corrected 5 of the audit's suggested approaches before implementing. Batch 1 (`1ffa572f`, 9 items), Batch 2 (`85170fd2`, FAQ details + hero priority), Batch 3 (BE `96c2556` + FE `d9f17c7c`, real updated_at field). All verified live.

---

## Session #355 (2026-08-25)

**Achieved (#355) — Airport transfer link-out (UXUI+BD debated) + header spacing token, both shipped.**

Parallel UXUI + BD review rejected a full airport-transfer section on `/locations/[slug]`; shipped a text link instead. Caught 2 real bugs during implementation: non-deterministic airport pick (Phuket has a demo + real airport station), link hidden when location has zero configured routes. Added `LAYOUT.sectionHeaderClasses` token, applied to 4 location page headers. BE `develop @ a4b782c`, FE `develop @ 6b5e7995`.

---

## Session #354 (2026-08-25)

**Achieved (#354) — Hero image audit (data-gap, logged) + LocationFAQ real-data fix (BE+FE), verified across 7 locations.**

Hero image traced end-to-end as content data-gap not a bug (logged `LOCATIONS-MISSING-HERO-IMAGE`). `LocationFAQ.js` Q2 transport-type claim was a hardcoded string, false for 100% of 7 locations tested (one had zero real data, would've claimed 4 fake modes). BE `transport_types` aggregation + FE conditional answer. Pushed BE `develop @ 71037bd`, FE `develop @ 57e29705`.

---

## Session #353 (2026-08-25)

**Achieved (#353) — `/locations/hatyai` UX/design audit + 5 fixes shipped to develop.**

Vault check (no prior notes) + browser audit of `/locations/hatyai` → found 5 issues, all fixed and pushed: section order fix (About before Guides), Read more button placement + collapse, blog card tokens + Guides white wrapper, unified carousel token across BlogCard/PopularRouteImageCard/ExperienceCard, 4.2 cards-per-row token (276px). All on `develop @ ef99742b`.

---

## Session #352 (2026-08-25)

**Achieved (#352) — `/locations/[slug]` hub tech-debt shipped: 5 atomic commits, 3 page bugs fixed end-to-end, 1 SSR interop bug, 1 TDZ bug.**

Full audit of `/locations/hatyai` per session #351 resume point → vault + FE scan → 9-section priority ranking. Branch `fix/locations-hub-tech-debt`, 5 atomic commits merged `--no-ff` into `develop @ 28aed83e`. Hydration fix, self-dest filter, fallback image, ESM/CJS interop fix, TDZ fix. Verified live: 200, 141 KB, all 5 JSON-LD blocks, 0 hydration warnings, 0 self-chips.

---

## Session #351 (2026-08-25)

**Achieved (#351) — Popular Routes card: design review + responsive audit + mobile scroll-snap shipped to develop.**

Full multi-dimension review (UX/UI, designer, BD, Next.js, Django) of "Popular routes from Hatyai" section. Decisions: NO price (vault [[locations-destinations-product-split]] — price stays on /destinations), NO image card (2 real S3 images exist for hatyai destinations, 21/54 locations lack images; would need BE summary-endpoint image join), NO carousel (data too small: hatyai 4, bangkok 1, phuket 1 dests; section is zero-typing shortcut, not browse). Responsive audit via Playwright: PASS all widths 320–1920, no overflow, 76px touch targets, contrast AA. User saw mobile stack (~700px worst case) = "sucked" → chose horizontal scroll-snap. Shipped FE `develop @ 4c4b06c4` (merge of `28db07bd` on branch `feat/locations-popular-routes-mobile-scroll`, pushed): CSS-only mobile swipe row (`overflow-x-auto sm:overflow-x-visible sm:flex-wrap no-scrollbar scroll-snap-x-mandatory`, card `w-[160px] shrink-0 sm:w-auto sm:min-w-[180px]` + `scroll-snap-align-start` + `truncate`), all utilities pre-existing in globals.css, same idiom as ReviewFirstPage. design-review agent verified 9/9 live (snap boundaries, all viewports, long-name truncate, tap nav, bangkok 1-chip). Caught pre-live: missing `shrink-0` would compress cards not scroll. Desktop unchanged. **Deploy note: clear `smartenplus_next_cache` ISR volume or /locations/* serves stale.**

**Side-findings logged (Section 2):** LocationOverview hydration warning (About section, `18ae253f`), self-destination chip (hatyai→hatyai), BE uncommitted test file reminder (#304 decision).


Archived from master-state.md. Latest session stays in master-state.md Section 1.

---

## Session #350 (2026-08-25)

**Achieved (#350) — DECISION: "Where are you starting from?" section NOT re-added to /locations/[slug] (analysis-only, zero code).**

User asked whether requirement's post-hero "Where are you starting from?" section should return on `/locations/hatyai`. Evidence: vault #344 (section existed) + #347 (commit `028cf304` removed it same-day — old chain linked dead station-slug URLs; 4 files deleted: RouteGridSection, TransportPointFilter, useLocationRouteFiltering, GridComponent3), live-page curl (no section/h2), BE `_summary_response` (destinations field incl. intra-location airport transfers). 3-role analysis (UX/UI + designer + BD) all concluded: don't re-add — hero `DestinationSearch` asks destination (origin known from slug), station granularity deferred to `/trips/{origin}/{dest}` list showing real departure station per trip. Re-adding = double location question back-to-back, no crawlable URL target, rebuilds removed-for-cause pattern with width-bug history (#342–#344). User confirmed: keep current, zero work. Revisit trigger: analytics show station-first demand ("hat yai airport taxi" intent) → then as DestinationSearch "From station" field (needs BE station→destination matrix), not separate section.

---

## Session #349 (2026-08-25)

**Achieved (#349) — Completed /locations/[slug] page: merged all pending BE+FE branches, fixed XSS in About section.**

BE: merged `feat/locations-summary-destinations` → develop (`ca2a35b`) — includes both `feat/locations-detail-transport-hub` (`31e2f43`, Location.description field + summary endpoint) and `feat/locations-summary-destinations` (`4bae803`, destinations field). Both pushed to origin. FE: applied `fix/locations-overview-sanitize` directly to develop (`18ae253f`) — new `LocationOverview.js` DOMPurify-sanitizes `Location.description` before rendering (XSS fix), adds length-gated Read more toggle (>320 chars), TouristDestination JSON-LD schema block. Pushed. All location page work now on develop both repos, pending prod deploy + `python manage.py migrate stations` (migration `0038_location_description`).

---

## Session #347 (2026-08-25)

**Achieved (#347) — DestinationSearch on `/locations/[slug]`: replace hero grid-filter with destination picker, fix dead route links, remove grid section. Fixed 3 bugs in DestinationSearch (input not displaying, button layout, freeSolo interaction). Merged → develop.**

BE `feat/locations-summary-destinations` (`4bae803`): added `destinations` field to `_summary_response()` — arrival-location names+counts for routes departing this location. 60/60 tests green. FE `feat/locations-destination-search` (`028cf304` + `9e2d05f5`): new `DestinationSearch.js` — origin known from slug, user picks destination, navigates to `/trips/{origin}/{dest-slug}`. Deleted 4 dead files (RouteGridSection, TransportPointFilter, useLocationRouteFiltering, GridComponent3). PopularRoutesSection + ItemList JSON-LD rebuilt on real outbound destinations. Merged to develop `0e9ec095`. Post-merge bug fixes: (1) input not showing typed text — CSS `paddingLeft:3rem` needed to push text past search icon; (2) input blank after selection — `reason!=='reset'` guard blocked MUI's label sync; (3) button floating below input — fused into single `flex-row` with inline arrow button. Removed `freeSolo` (closed set). FE develop pushed.

---

## Session #345 (2026-08-24)

**Achieved (#345) — Committed, pushed, and merged #344's width fix (+ #343's dead-param fix) into `smartenplus-frontend` develop.**

Continuation of #344 same day. 2 commits on `feat/locations-detail-transport-hub`: `f425f64e` (#343's `?from=bangkok` removal, 2 files) + `9128764b` (#344's `RouteGridSection.js` width-token fix). Pushed branch to origin, fast-forward-clean merge (`--no-ff`) into `develop` (no conflicts — develop hadn't moved), pushed. `smartenplus-frontend` `develop @ a312ea50`. `smartenplus-backend`'s copy of the same branch (`feat/locations-detail-transport-hub`, latest `31e2f43`) was NOT touched/merged this session — only frontend was asked for; BE still sits on its feature branch with 1 unrelated untracked test file, needs its own merge decision later.

---

## Session #344 (2026-08-24)

**Achieved (#344) — Root-caused + fixed "Find Perfect Routes" section width mismatch on `/locations/[slug]` (the #342/#343 unresolved width bug, resume point #1).**

User pointed at exactly which section this time: "Find Perfect Routes in Hatyai" (`RouteGridSection.js`) vs the rest of `/locations/hatyai`. Direct source read (no screenshot/Playwright needed — diff was visible in code) found the actual bug: every other section on the page (`Where are you starting from?`, `Popular routes from X`, `About X`, FAQ — all in `pages/locations/[slug].js`) uses the shared `LAYOUT.pageContentClasses` token (`max-w-[1200px] mx-auto px-4 xl:px-0`), but `RouteGridSection.js` had its own bespoke recipe: `<section>` had `max-w-[1200px] mx-auto` with no horizontal padding, while horizontal inset instead came from an inner div's `sm:mx-3` (12px, zero on mobile) + card `p-4`. Different mechanism (padding-on-section vs margin-on-inner-div) and different breakpoints (`px-4 xl:px-0` vs `sm:mx-3`) meant the card never aligned with sibling sections at any breakpoint — worst at `xl+`, where siblings go flush to the 1200px bound but this section kept a permanent 12px inset. Same bug class as the 2 prior Popular Routes fixes (`a58570eb`, `3a3226f7`) — a section not wired to the shared token drifts. Fix: `RouteGridSection.js` now imports `LAYOUT`, outer `<section>` uses `` `${LAYOUT.pageContentClasses} w-full ...` `` matching siblings exactly, inner div's competing `sm:mx-3` removed. Went into #345 same day for commit/push/merge.

---

## Session #343 (2026-08-24)

**Achieved (#343) — Removed dead `?from=bangkok` query param from homepage "Thailand's Top Destinations" links.**

User asked why `/locations/hatyai?from=bangkok`-style links carry a `from` param and whether it's removable. Explore-agent investigation confirmed it's dead: `pages/locations/[slug].js` `getServerSideProps` only reads `query.page`, never `query.from`; no component under `components/locations/` reads it; repo-wide `query.from` grep only hits an unrelated page (login-redirect callback on `PassengersList.js`). The value was also a hardcoded literal (`bangkok`), never derived from real user origin. Canonical/OG/breadcrumb URL generation (`domainURL` in `pages/locations/[slug].js:28-31`) already does `router.asPath.split('?')[0]`, stripping all query params before building canonical — so removal has zero SEO impact. Git blame traced it to commit `ade94ee0`, added alongside a "Search buses to {location}" CTA that's since been removed from the codebase — orphaned leftover. Removed from the 2 link-building sites: `lib/homepage/components/DestinationsEditorialGrid.js:20`, `lib/homepage/components/DestinationsCarousel.js:20`. Side benefit: link URL now matches the existing hover-prefetch URL in `lib/homepage/components/LocationsSection.js` (previously mismatched, wasting the prefetch). Uncommitted, same branch (`feat/locations-detail-transport-hub`) as #342's unresolved width bug — not pushed. (Width bug went on to be root-caused + fixed in #344 — see master-state.md Section 1.)

---

## Session #342 (2026-08-24)

**Achieved (#342) — `/locations/[slug]` transportation-hub redesign built, reverted once, rebuilt, then 4 rounds of width-inconsistency chasing — real root cause found+fixed on round 4, but user says it's STILL not visually right. Unresolved, needs fresh eyes next session.**

Multi-session arc on one branch (`feat/locations-detail-transport-hub`, both FE+BE, not pushed): user supplied an external pSEO report proposing a "location page = transportation hub" redesign for `/locations/{location}`. Checked against vault (`03-knowledge/locations-destinations-product-split.md` — `/locations` = route-list only, `/destinations` = booking/pricing, never consolidate) and found the report's price/duration destination cards would violate that split. Scoped down via user Q&A: Transportation Points = data-derived departure-station filter cards (not fake sub-pages), Popular Routes = name+count only (no price), About = new `Location.description` field (in scope, conditional render), FAQ = templated + inline guide links (reuses existing `RouteByLocationInfo.blog_slug`, no new backend). Travel Guides section explicitly rejected as a dedicated block after BD+UX agent review (sparse content, duplicates FAQ) — inline links only.

3-agent review (Next.js/Django/SWE) before first implementation caught: original dual-fetch plan would've doubled a confirmed N+1 query (25 queries for 13 routes) — replaced with a new DB-aggregated `?summary=true` action on `LocationV2ViewSet` (5 queries, zero N+1, verified); `PageSeo.js` doesn't support `WebPageJsonLd` (would've shipped wrong schema); branch/vault-naming/reuse gaps. Built, verified via SSR (JSON-LD present, zero price leakage, 0/1-departure edge cases correct), shipped.

**Then it started cycling.** User screenshot showed Popular Routes cards broken (reused `LocationCard`, image-forward, against `image:null` data — tiny broken photo tiles). Reverted the whole page to pre-redesign `develop` state, kept the backend endpoint. Rebuilt with a dedicated `PopularRouteCard.js` (text-only, no image ever). Then **3 more rounds of width-inconsistency chasing on the same file**, each one guessing wrong and getting corrected by the next screenshot: round 3 matched section padding to the breadcrumb's `px-2 md:px-3` (wrong — never checked what the homepage actually does); round 4 found homepage's real `Section` component pattern is `px-4 xl:px-0` uniformly and switched back (right token, but round 5 flip-flopped back to `px-2 md:px-3` again mid-edit before being called out for cycling); round 6 finally **measured real rendered box widths via Playwright** (not grep/inference) and found the actual bug — `LAYOUT.pageContentClasses` sets `max-width` but never `width:100%`, so the 4 content sections were rendering at 843px/564px/378px (shrunk to content) instead of 1200px. Added `w-full`, re-measured — every container now reports `left=120, w=1200` uniformly, confirmed via screenshot.

**User says width/design is STILL not right after the `w-full` fix** (this session's very last message, before `/wrapup` was invoked) — not yet investigated further. This is a genuine unresolved bug, not just a "needs browser-verify" item — 4 rounds of fixing attempts have not satisfied the user, and the actual visual problem still open as of end of session.

---

## Session #341 (2026-08-22)

**Achieved (#341) — "Plan Your Next Adventure" recommendation section audited (vault + live FE/BE), 2 real bugs found + fixed + merged to develop.**

User asked to check the vault, then deep-audit the post-booking recommendations section ("Plan Your Next Adventure" on `/bookings/[id]` for confirmed bookings) against a live booking — price, availability, product image+logo. Vault check found no prior note on this section specifically; closest match (`03-knowledge/ratecard-category-mixing-price-bug.md`, a bug already fixed on the FE trip-sort page in #317) turned out directly relevant — same bug class, unfixed, on a different code path.

Live-tested against local BE using real booking `FOM9228841`. Found: **(1) Price bug** — all 8 finder functions in `products/services.py` computed `lowest_price` via a flat `Min()` across every ratecard category (ADULT/CHILD/INFANT/VEHICLE) with no filter, so the card showed whichever category was cheapest (often INFANT) instead of the category the contract bills (JOIN→ADULT, PRIVATE/CHARTER→VEHICLE — the exact rule already correct elsewhere in the same file via `route_lowest_price_annotation()`, just never reused here). Live proof: contract 7 showed "from ฿400" (INFANT) for a ฿900 adult fare. User pushed on scope twice — confirmed live the bug also hits activity products (DAY_TOUR/ATTRACTION_TICKET, not transport-only) via a second real repro (contract 166's recommendations: contracts 136/137 showing CHILD rate instead of ADULT). **(2) Expired-contract leak** — none of the 8 finders filtered `end_date`, only `is_actived` (a separate flag that doesn't track date-range expiry) — 2 of 7 recommendations for booking `FOM9228841` were contracts already past their own `end_date`, still rendered as bookable cards.

Built a visual artifact (recreated recommendation card wrong-vs-correct, real ratecard breakdown, pipeline trace to the bug) before the fix. User then asked for backend-architect + code-reviewer agent review of the plan before implementing — architect recommended a direct filtered `Min()`+two-branch `Q` over porting the more complex Subquery pattern (simpler for this queryset shape, no N+1 risk, cache key needs a version bump); SWE reviewer caught 10 concrete risks including that literal fixture tests would break (existing `Contract_RateCard` fixtures omit `ratecard=`), 3 disagreeing reference implementations for the "no billing-category row" fallback semantic (resolved: fall back to any rate, never silently hide a price), hybrid-limit starvation as an expected side effect (not a bug), a pre-existing `0.0`/`None` inconsistency sitting in the fix's blast radius, and a 9th related-but-out-of-scope bug in the serializer's fallback path. Also audited the plan itself against project CLAUDE.md rules before implementing — found and fixed one gap (git branch step wasn't explicit) and one process gap (deferred items needed a real tracked issue, not just plan-file prose).

Implemented on `fix/recommendation-price-category-expiry` (off develop): 2 new shared helpers (`contract_lowest_price_annotation()`, `contract_lowest_price_fallback_annotation()`, `contract_not_expired_q()`) applied at all 8 call sites in `products/services.py`, cache key bumped to `v2`, the `0.0`/`None` inconsistency fixed in the same pass. 9 new tests added (`products/tests.py`) — direct repros of both bugs (JOIN/PRIVATE/CHARTER category picks, expiry exclusion, no-category fallback, direct-annotation construction test so a filter bug raises loud instead of the finder silently degrading to `[]`) plus an end-to-end regression test through the real `find_alternative_contracts()`. Full `products.tests` suite: 1 pre-existing unrelated failure, confirmed identical on the `develop` baseline before this session's changes (not a regression). **Live-verified against both original repro cases post-fix**: contract 7 now `฿900` (was `฿400`), contracts 26/29 (expired) no longer appear, contracts 136/137 now `฿800`/`฿400` (were `฿600`/`฿300`) — exact match to predicted values. Committed, merged → develop (`ee7f481`). Not yet pushed to remote.

3 items explicitly deferred (out of scope for this fix) filed as a tracked vault open item, not left as silent prose → RECOMMENDATION-ENGINE-DEFERRED-ITEMS (Section 2). Availability filter audit (client-side `filterValidRecommendations.js`) found 1 of 4 filters is dead code (seat-availability check references a field shape that doesn't exist in the real API response) — flagged, not fixed (FE-side, separate from this BE fix). Product image/operator-logo behavior confirmed by-design, not a bug — flagged as a product-quality gap only.

---

## Session #340 (2026-08-22)

**Achieved (#340) — CS staff chat notification gap fixed + shipped to develop; 13 stale merged branches pruned (BE repo).**

User reported staff don't get notified properly when customers use the chat widget. Scanned all 3 repos (3 parallel Explore agents — FE chat widget, BE `cs` app, AD staff inbox) + vault (no prior decision doc on this). Root cause: BE `cs/signals.py` only fired staff Web Push on `Conversation` creation (message #1 of a new chat) — no signal existed for `Message` creation, so every follow-up message in an existing conversation got zero server push. Staff fell back entirely to client-side Supabase Realtime + an open AD browser tab, which silently fails when the tab/browser closes or the realtime token (14min TTL) drops. AD's notification UI itself (badges, tab title, service worker, permission prompt) was already fully correct — it just never received a push past message #1.

Built a visual before/after artifact (flow diagrams: working new-conv path vs broken follow-up path vs fix) before writing code, per user request. Then Django-architect + SWE-reviewer agents audited the fix design against actual code before implementing — caught and corrected: original guard (`instance.conversation.message_set.count()==1`) had a wrong reverse-accessor name (real: `.messages`, would've crashed) and was racy/wasteful; confirmed a separate `bulk_create` sync path (`sync_chat_messages`) would've silently skipped signals if it were the real write path, but verified the actual customer-send flow uses `Message.objects.create()` so signals do fire correctly; caught that `send_push_to_subscriptions()` runs synchronous blocking `webpush()` calls and should dispatch via Celery (already established in this app) rather than inline in the signal.

Implemented on `fix/staff-chat-notify-followup-messages` (off develop): `cs/signals.py` now fires on `Message` post_save (`sender=customer` only), dispatched via new `cs/tasks.py::notify_staff_new_message` Celery task; `Conversation`-creation signal no longer pushes on its own (the paired first message covers it — no double-fire guard needed since conv-create and first-message-create are separate requests). 5 new unit tests added (`cs/tests/test_staff_notify_signal.py`), all pass; full `cs` suite 179/180 (1 pre-existing unrelated failure, confirmed on clean develop baseline too). **Real E2E run** (not just mocked): local Postgres+Redis+Celery worker, fired real signals via Django shell — confirmed exactly-once task dispatch per customer message (first + follow-up), zero dispatch on staff reply. Committed, pushed, merged → develop (`2c0b2df`). No FE/AD changes needed.

Separately: pruned 13 stale branches (12 requested + this session's own `fix/staff-chat-notify-followup-messages`) from `smartenplus-backend`, local + remote — all confirmed merged into develop via `git branch -r --merged`, verified none was the checked-out branch, used `git branch -d` (safe-delete, git double-checks merge status) not `-D`. Clean, `git branch -a` confirms zero trace.

Visual demo artifact: https://claude.ai/code/artifact/dd43d4ba-a5f8-406f-a219-08bb20f31c14

## Session #339 (2026-08-22)

**Achieved (#339) — BE bot-scan log noise investigated, root-caused to local Tailscale Funnel (not prod). No code changed.**

User saw BE log WARNINGs (404s for `/keyfile.json`, `/firebase-adminsdk.json`, `/wp-login.php`, `/api/v1/auto_login`) and asked for a Django security audit. Confirmed via `urls.py` all paths genuinely 404 — no route match, no exploit, no data touch. Explore-agent audit of `smartenplus-backend` settings.py found real prod gaps (missing `SECURE_*` headers, no `django.request` 404 filtering, `docker-compose-rds.yml` publishes port 8000 alongside nginx) and a Plan-agent second pass caught a correction (a `LOGGING` filter can't distinguish urlconf-miss 404s from real DRF 404s — `handler404` override is the precise fix) — full plan drafted and ship-risk-checked.

Mid-approval, user revealed the log was from **local dev**, not prod. Root cause: `tailscale funnel status` confirmed Funnel active, publicly proxying `macbook-air-2.tailc1dfbd.ts.net` → local `127.0.0.1:8000` Django — turned on intentionally for payment-webhook testing (Omise/Stripe need a public callback URL), left on. Public Funnel URL gets a real TLS cert → cert-transparency-log bots scan it within hours, same as any public HTTPS endpoint. Nothing wrong with Django; noise is the accepted cost of an open Funnel tunnel.

User declined the prod hardening changes this session (out of scope — trigger wasn't actually a prod issue) and is keeping Funnel on (still testing). **No code changed, no commits.**

**NOT done this session:**
- Prod hardening (`SECURE_*` headers, `handler404` 404-log fix, port-8000 compose exposure) — real gaps found, documented, but explicitly deferred. Worth revisiting on its own if prod security posture becomes the actual focus later.
- Funnel not turned off — user still mid webhook-testing, reminder only (their own follow-up, not actioned).

## Session #338 (2026-08-22)

**Achieved (#338) — tawk.to migration debate (vault-only report) + 2 chat-widget fixes, both merged → develop.**

3-role debate (BD + Backend Django + Frontend Next.js) on replacing the customer-support chat system with tawk.to, after full vault+code audit of the existing CS platform (SLA/OTA-sync/ticket-linked chat, prod since 2026-07-03). All 3 roles converge AGAINST full replacement — no tawk.to equivalent for the business logic already built; only carve-out is an additive pre-sales widget on marketing pages, gated on BD pre-committing a pilot metric. No code changed. Report → `01-projects/tawkto-migration-debate-2026-08-22.md`, 2 artifacts published (debate memo + later a before/after visual demo for the chat-widget fixes below).

Separately, user reported 3 chat-widget bugs (z-index, icon size, position) + a 4th (color mismatch). Root-caused against actual source, SWE-audited against CLAUDE.md before implementing (audit corrected 2 of 3 original fixes — see below), visually demoed before/after via published artifact, then implemented across 2 branches:

1. **`fix/chat-widget-zindex-icons-positioning`** (`develop @ 5eed40ea`) — `ChatBubble.js`/`ChatPanel.js` built z-index via Tailwind template-literal (`` z-[${var}] ``), which the JIT scanner never picks up as a real class — dead z-index, fixed via inline style (matches existing `ScrollTop.js` precedent). Added app-wide `ICON` scale token (none existed before) — grepped real usage app-wide (`w-6 h-6` dominant, 33 uses) and snapped the chat launcher from an untracked 28px outlier (`w-7 h-7`, only 2 uses app-wide) to the real 24px rung, rather than just preserving the outlier as first proposed. Made `CHAT.position` responsive (viewport-relative insets, matching the #337 mobile-overflow fix pattern) instead of a fixed `w-80`. Also fixed 2 hardcoded fallback banners in `ChatWidget.js` sharing the same bug, caught during implementation.
2. **`fix/chat-widget-brand-color-tokens`** (`develop @ c903ce3f`) — separate follow-up bug: panel header/launcher correctly used `COLORS.brand.primary` (`#3b5998`), but every other chat surface (message bubbles, send button, focus rings, guest-form links, read-receipt ticks) was hardcoded to Tailwind's default `blue-600` (`#2563EB`) — a visibly different blue. Swapped 12+ occurrences across 4 files to the already-registered `bg-brand-primary`/`text-brand-primary` Tailwind classes (no new tokens needed — they already existed in `tailwind.config.js`, just weren't used). Full-sweep grep confirmed zero `blue-N` left in `components/chat/`.

**NOT done this session:**
- No browser verification of either chat fix — no browser tool available this session (same limitation noted in prior sessions). Both fixes shipped on code-level lint/grep verification + a visual mockup artifact, not a live click-through.
- No develop→main deploy — both chat fixes are develop-only, joining the existing deploy queue.
- Tawk.to debate stayed vault-only — no pilot built, pending BD's metric pre-commitment.

---

## Session #337 (2026-08-21)

**Achieved (#337) — 2 mobile-only bugs in #336's airport-transfer search tab found+fixed, merged → develop.**

Follow-up to #336, same session's feature. User screenshot showed the address dropdown clipped off the right edge on mobile — root cause: `PlacePicker.js`'s suggestion dropdown was `absolute`-positioned relative to `PlacePicker`'s own inner wrapper, which sits ~70-90px inset inside `AddressField.js`'s field (after the leading icon + role label), not at the field's true edge. Fixed by moving the positioning anchor up to `AddressField.js`'s outer `label` — `PlacePicker`'s bare-mode wrapper drops `relative`, confirmed via code check that `ZonePriceBox.js`'s non-bare pill usage (its own `relative` context) is unaffected, byte-for-byte unchanged there.

That fix then exposed a **worse** regression, caught by the user immediately: the page itself gained a horizontal scrollbar on mobile (real layout overflow, not just visual clipping) — root cause traced to the dropdown's `w-[max(100%,320px)] max-w-[90vw]` width formula, which can still compute wider than the viewport under certain anchor/viewport combinations, and with no ancestor setting `overflow-x:hidden`, that excess became real scrollable page width. Fixed by replacing the width formula entirely with `left-0 right-0` (no explicit width) on both the address AND airport dropdowns — makes each dropdown's box mathematically identical to its already-safe parent field's box, structurally incapable of exceeding the page regardless of viewport quirks. Visual root-cause diagrams (box-model diagrams, before/after) built for both bugs before shipping either fix.

Branch `fix/airport-transfer-mobile-dropdown-overflow`, frontend `develop @ 0a9e7bd4`. 3 files changed (`PlacePicker.js`, `AddressField.js`, `AirportSuggestionList.js`).

**NOT done this session:**
- No browser click-through by Claude — no browser automation tool available; both fixes shipped on user-provided screenshot diagnosis + lint/build verification only, confirmed live by the user.
- No develop→main deploy — develop-only.
- #336's still-open items (ranking/location-bias decision, full click-through pass) remain open.

---

## Session #336 (2026-08-21)

**Achieved (#336) — airport-transfer search-tab address autocomplete + swap, frontend-only, merged → develop.**

Search section's Airport Transfer tab gained a Google Places address field alongside the existing airport picker, reusing 100% existing pieces (`PlacePicker.js`, `resolveZone` API) — no new backend work. Address+coords+direction now carry through the URL (`?addr=&lat=&lng=&atdir=`) to `/airport-transfer/[slug]`, which pre-fills `ZonePriceBox` and auto-resolves a price without the user re-typing. Multi-round design work: 4-specialist review (UX/design-system/Next.js/Django) up front, then a 2nd higher-rigor audit pass (Next.js/Django/SWE) caught 3 real seeding bugs before ship (direction-param vocabulary collision, `selectedRef` not seeded alongside `selected`, stale state on same-slug SPA re-navigation — fixed via a `key` prop forcing `ZonePriceBox` remount).

Also added, per follow-up requests: a clear (×) button on the airport field (parity with the address field), and a From⇄To swap toggle reusing `ZonePriceBox`'s existing swap pattern (new files `SwapButton.js`, `AirportField.js`, `AddressField.js`, `AirportSuggestionList.js` — extracted to keep `AirportTransferSearch.js` under the 200-line component budget after the swap logic pushed it to 251).

**7 live bugs found via user screenshots/testing and fixed same session**, each independently root-caused (several backed by opus-tier SWE/Next.js/Django audit passes, not guesswork): (1) address dropdown capped to its own narrow field instead of a sensible width + no text truncation; (2) `×` clear button anchored to an unstretched wrapper div, floating mid-field; (3) airport dropdown sized off the whole 3-field row instead of just its own field; (4) 4 real style diffs between the two dropdowns (width formula, position anchor, row height, missing empty-state) — unified; (5) swap wiped the typed address instead of preserving it — required reverting an earlier "clear on swap" design decision plus fixing a `Fragment`-branch reordering pattern that risked positional remount despite keys (switched to a flat keyed array, the React-correct fix); (6) mobile clear-button positions inconsistent — the two buttons used entirely different layout mechanisms (inline-flex vs absolute), unified by branching `PlacePicker`'s `bare` mode to flow inline; (7) refocusing an already-selected airport field showed false "No airports match" — filter compared the formatted display label against raw unformatted station fields, fixed by adding the formatted-label as a 3rd match check. Deferred, not fixed: cross-border/irrelevant Google Places ranking noise (needs airport lat/lng, which exists in neither backend nor frontend today — hardcode-vs-backend-field decision raised, not made).

Frontend only, `develop @ 29769a2d`. Backend/admin-dashboard untouched this session.

**NOT done this session:**
- No browser click-through by Claude — no browser automation tool available; all fixes verified via lint+build only, confirmed live by the user via screenshots at each step.
- No develop→main deploy — develop-only.
- Ranking/location-bias fix for the address autocomplete — deferred, needs a product decision (frontend-hardcoded airport coords vs. new backend `Station.latitude/longitude` field).

(#335's detail archived → below.)

---

## Session #335 (2026-08-21)

**Achieved (#335) — hero banner end-to-end, 3 repos, all merged → develop.**

Built the first real frontend consumer of the previously-unused `HeroBanner` Django model. **BE**: `placement` field (`home`/`activities` TextChoices, `default='home'`), migration, fixed a pre-existing bug (4 serializer classes byte-for-byte duplicated in the same file — dead code, silently shadowed, landmine for future edits), `HeroBannerViewSet` gains `?placement=` filter, `FrontPageViewSet._fetch_hero_banners_data()` gains a required home-scoping fix (without it, any future `activities` row would silently leak into the homepage payload), 1 regression test. `develop @ 6945754`. **FE Activities page**: hero wired to the BE image via `getStaticProps` (LCP-safe, not client-fetched), then — on explicit user request reversing the original "no overlay text" recommendation — the H1 + subtitle + `ActivitySearch` were moved from below the hero into a centered overlay on top of it (`.hero-top-gradient` scrim + layered text-shadow + upward-biased placement, all visually mocked and signed off before building). The search-bar move required lifting `useDayTripFilters()` to the page level to avoid two competing hook instances racing on URL writes — the real architectural work of that phase. 2 live bugs found via user screenshot/testing and fixed same session: search input had no background fill (transparent MUI default, invisible on white pages, broken against a photo) and the hero fetch hit a wrong URL (`/api/v1/hero-banners/` — `pages_info.urls` is actually mounted at the site root, not under `/api/v1/`; confirmed via curl, silently swallowed by the `Promise.allSettled` fallback so it just looked like "the image won't change"). `develop @ 152b9d1b`. **AD**: `HeroBannerForm.js` gains a required Placement dropdown (starts empty on create so staff can't accidentally leave a banner defaulted to Home), list page gains a placement column + filter, plus a `resetPage()` fix applied to both the new filter and the pre-existing search box (neither called the pagination-reset helper that already existed for this). `develop @ dc94e09`. Every phase reviewed by 2-4 domain specialists (Next.js/Django/UX-UI/general-SWE) before implementation, with real findings each round (not rubber-stamps) — caught the serializer duplication bug, the home-scoping leak risk, the `useDayTripFilters` race, and 4-5 admin-dashboard should-fix items (pagination reset, responsive grid, constants shape/location, `queryParams` stale-closure risk).

**Also this session, unrelated:** BE contract search (`/api/v1/contract/?search=`) now normalizes spaces/hyphens before comparing — "day trip"/"daytrip"/"day-trip" all resolve to the same contracts (reused the exact `normalize_search()`+`Replace()` pattern `RouteViewSet` already uses for `hatyai`/`Hat Yai`). First attempt (word-splitting) only solved half the reported bug; caught via user re-testing and replaced with the correct fix same session. `develop @ a6dd5bc`.

**Explicitly NOT done, by decision not oversight:** homepage has zero `HeroBanner` consumer — `placement='home'` is fully wired backend-side and selectable in the admin dropdown, but picking it does nothing visible today. User confirmed this is fine to leave as-is; not scoped this session.

**NOT done this session:**
- No browser click-through beyond the 2 bugs the user caught live — no formal mobile/desktop/long-location-string pass beyond what was mocked.
- No develop→main deploy on any of the 3 repos — all develop-only.
- Admin-dashboard `is_staff` provisioning check (flagged by backend review as unverified, not a code gap) never done.
- Optional backend write-path test for `HeroBannerViewSet` POST/PATCH (recommended by review, not required) not added.

(#334's detail archived → below.)

---

## Session #334 (2026-08-20)

**Achieved (#334) — loader spinner off-center bug found+fixed, merged → develop.**

User reported `<Loader />` (PuffLoader spinner shown during initial fetch) not vertically centered on `/guest-order/[orderId]`. Root cause: `Loader.module.css`'s `.loader` used `height:50vh`, which centers the spinner within its own 50vh box — but that box sits inside `<main>` (`components/layout/layout.js` `PageMain`), which carries `md:pt-[96px]`/`md:pt-[48px]` top padding for the fixed header plus a footer below. `50vh` is blind to both, so the spinner's visual center sat below true viewport center. Confirmed via grep this is the sole `Loader` implementation, used identically on `pages/guest-order/[orderId].js` and `pages/orders/[orderid].js` — no other "correct" pattern existed elsewhere to copy. Fix: `.loader` switched from a flat `height:50vh` to `flex:1` (fills whatever space its flex-column parent — `#outer-container` in `layout.js`, already `flex flex-col min-h-screen justify-between` — actually gives it, between header and footer) with `min-height:50vh` kept as a floor for any non-flex parent. Single-file CSS change, `Loader.js` itself untouched. Branch `fix/loader-centering`, frontend `develop @ 96ebd191`.

**NOT done this session:**
- Not browser-click-verified — fix applied and Fast-Refresh-confirmed to compile, but the loading state is transient on localhost (fetch resolves too fast to screenshot without network throttling).
- No develop→main deploy — develop-only.

(#333's detail archived → this file, below.)

---

## Session #333 — 2026-08-20

**Achieved:** 2 booking-access bugs found+fixed, both merged → develop.

User reported a real customer confirmation email (`XUW6154469`) rendering "departing ." with a blank Date of Travel section. Traced via Explore agent to `orders/services.py` `dispatch_booking_notifications`: `traveling_date` was stringified (`.strftime`) at line 67 for an unrelated operator-API payload, then that same string got reused at line 180 for the customer-email context instead of the raw `date` object. Django's `|date:"j F Y"` template filter silently renders empty on a string input (no exception, and the paired `{% if %}` guard still passes since the string is truthy) — hit all 5 places `booking.traveling_date` appears in `booking_confirmation_template.html`. Fix: `orders/services.py:180` now passes `booking.traveling_date` (the raw `date` object) instead of the pre-stringified `context['traveling_date']`, matching the pattern already used for `contract_departure_time`/`contract_arrival_time` nearby. Verified `order_email_template_pro.html` (separate order-confirmation email) unaffected — its context builder already passed the raw field. Self-reviewed against the report before committing (re-verified `render_to_string` is stock Django with no custom filter overrides, confirmed no `{% load %}` tricks in the template, confirmed `booking` loop-var scope). Backend `develop @ 1496573`.

**Second bug, same investigation thread, different mechanism:** user separately reported "VIEW MY BOOKING" links in emails returning "Access denied" for guest customers — but only in a normal browser, not incognito. Traced through the full auth chain (BE `bookings/views.py` `BookingDetailsViewSet.get_queryset()`, FE `pages/bookings/[bookingId].js`, `store/api/bookingsApi.js`, next-auth config) and confirmed with the user's own backend logs (`POST /api/token/refresh/ 401` immediately followed by a second 401 on an unrelated endpoint) that the guest-access code path itself was never broken. Root cause: when next-auth's token refresh fails, `refreshAccessToken()`/the `jwt` callback in `pages/api/auth/[...nextauth].js` marked the session with `error: "RefreshAccessTokenError"` but kept spreading the dead `accessToken` forward unchanged. Every downstream consumer (~50 call sites app-wide, not just the booking page) checks truthiness of `accessToken`, not the `error` flag, so a stale/expired browser session kept attaching `Authorization: Bearer <dead token>` — Django's global `JWTAuthentication` rejects that before the view's `AllowAny` + guest-email fallback ever runs. Incognito has no stale cookie, so no bad header gets sent, which is why it "just worked" there. Fix (3 files, trimmed from an initial 6-file draft after a CLAUDE.md-compliance self-review cut 2 speculative defensive guards that would only re-check a state the source fix already eliminates): null `accessToken`/`accessTokenExpiry` at all 3 places refresh failure gets recorded in `[...nextauth].js`, including a required (not optional) guard in the `session` callback to heal browsers that already hold a poisoned cookie today; simplified `[bookingId].js`'s skip/error logic around a single `isAuthed` flag; deleted dead file `hooks/useAuth.js` (zero importers, confirmed via grep, implemented a rejected signOut-redirect approach that would have bounced guests off their own emailed link). Confirmed via grep audit that this fix makes every one of the ~50 other `session?.accessToken` call sites strictly more correct, not just the booking page — none of them currently check `session.error` either, so they all silently attach dead tokens today too. Branch `fix/stale-session-blocks-guest-booking-access`, frontend `develop @ 7b06b435`.

Both bugs investigated with 2 visual Artifact demos built along the way (broken-vs-fixed email mockup; 3-lane auth-flow diagram showing guest/login/stale-session through the same backend gate) — user explicitly asked for visual explanations before approving each fix.

**NOT done this session:**
- Neither fix has been browser/live-verified in a real environment — both verified via code trace, self-review, and (for the email fix) a direct Django template-engine test of the `|date` filter behavior on string vs. date input. No `next build` or live click-through done for the auth fix.
- No develop→main deploy for either fix — both are develop-only.
- The stale-session bug's fix is source-level only; the ~50 other call sites that share the same `session?.accessToken`-without-`error`-check pattern were confirmed safe by the source fix but not individually touched or tested.

---

## Session #332 — 2026-08-20

**Achieved:** Transport composit reorder (BE+AD+FE, all 3 repos merged → develop) + staff contract-ID debug badge extended to trips/activities lists (FE, merged → develop).

Started as an AD-side question ("can we reorder van/speedboat/bus in a contract?") — scanned all 3 repos, found zero order field anywhere (implicit DB/array order only), planned + reviewed the plan through 4 rounds (Django/Next.js/SWE specialist agents, then a CLAUDE.md-compliance pass) before writing code. Shipped in 5 phases per the reviewed plan: **Phase 1-2 (BE, `develop @ f69271f`)** — `Contract_TranspotComposit.order` IntegerField + `Meta.ordering`, migration + PK-order backfill (preserves existing visual order), write path assigns `order` from array position, capacity-calc `.first()` made explicit `order_by` (was implicitly relying on default ordering for PRIVATE/CHARTER vehicle-quantity math — real risk caught by review, not hypothetical), contract clone now copies `order`. 9 new tests, full `operators`+`carts` suites 79/80 (1 pre-existing unrelated failure). **Phase 3 (AD, `develop @ b2f1e42`)** — up/down `IconButton`s on both desktop table and mobile card layouts in `TransportComposit.js`, disabled at list boundaries, stamps `order: idx` via `setFieldValue`. Reviewed pattern choice (buttons, not drag-and-drop) against `react-dnd`'s existing image-reorder precedent — table-row refs + dual desktop/mobile layout made DnD a worse fit here. **Phase 4-5 (FE, `develop @ dd316f76`, 2 separate commits)** — fixed `[...slug].js`'s CSR merge whitelist (was fetching fresh `transport_composit` live but silently discarding it, reorders invisible for up to 5min) + a GTM tracking bug reading the same stale copy; fixed `DayTripDetailPage.js`'s live-refetch gate (`useGetContractBySlugQuery` was skipped until the user manually picked a date, so first paint always showed stale order) — dropped Phase 5's original 2-page scope to 1 after re-verifying source: `ZoneOptionCard.js` (airport-transfer) turned out to already be live via `useLazyResolveZoneQuery`, no fix needed there at all.

**Then, same session, separate feature:** extended the existing airport-transfer staff QA badge (Shift+D → visible `#contractId` label) to the trips list (`/trips/[origin]/[destination]`) and activities list (`/activities`) pages, per explicit user request. Copied the toggle listener a 3rd time rather than extracting a shared hook — an SWE review against `smartenplus-frontend/CLAUDE.md` explicitly flagged hook-extraction-across-an-unrelated-working-file as scope creep contradicting "NO OVER-ENGINEERING," reversing the initial plan. Live testing (with the user, iteratively, via console logs) surfaced 2 real bugs neither static review caught: (1) `TripItem.js`'s `React.memo` custom comparator didn't check the new `showDebugId` prop, so toggling the shortcut updated parent state but silently never re-rendered the card — classic stale-memo bug, only visible by watching `setShowDebugIds` fire while the child's render log stayed frozen; (2) the "Top Pick" recommended card (`RecommendedTripCard.js`) never received `showDebugId` at all — a second, separate call site to the same underlying `TripItem` that the original wiring pass missed. Both fixed. Also fixed a real visual collision on the activities card (badge and the wishlist-heart icon sharing the same top-right corner) by adding an optional `position` prop to the shared `DebugIdBadge.js` (default unchanged, so `ZoneOptionCard.js` and the new trips-list usage are unaffected) and scoping the activities badge to the card's image area specifically.

**NOT done this session:**
- No manual browser click-through of the transport-composit reorder feature end-to-end (backend `migrate` run by the user directly, mid-session, after a sandbox permission block — confirmed applied cleanly; AD/FE verified via `next build` + lint only, not live UI).
- Staff badge feature WAS live-tested interactively this session (the two memo/wiring bugs above were found this way) but not on a true production-like build — dev server only.
- No develop→main deploy for either piece of work — both are develop-only, on top of an already-large `feat/transport-composit-order` branch that also carried #330/#331's unrelated commits before this session started (that branch has since been merged and is done).
- Migration must still be run wherever `develop` gets deployed next (`python manage.py migrate operators`) — not a deploy-automation step, flagging explicitly.

---

## Session #331 — 2026-08-20

**Achieved:** Admin-dashboard zone-pricing: 2 bugs found+fixed+pushed to develop (AD + BE), independent of the checkout-side #330 work. User-reported staff bug: on AD `/routemanagement/transfer-zones`, saving an existing general-transfer contract's zone removed its zone-pricing links. Root-caused via Explore agent + manual trace, then a Plan-agent review pass against project CLAUDE.md rules before implementing (same second-pass-review pattern noted valuable in #330). **Bug 1 — general-transfer zone save wiped contract links.** `components/transfer-zones/ZoneForm.js` `onSubmit` (introduced in `90e9129`, the #330-adjacent "general-transfer zone extension" commit) force-cleared `contract_ids`/`contract_airport_pins`/`airport_ids` for every save where `zoneType === 'general'` — not just an actual airport→general transition. Any save of an already-general zone, even a no-op, sent `contract_ids: []`, which the BE's full-replace row-diff sync (`stations/services.py` `_apply_diff`) applied literally — deactivating all `ZoneContract` links, including ones set via the separate contract-page `TransferZonesSection.js` entry point. Fix: reuse the existing `showTypeTransitionWarning` flag (already the single source of truth for "this save destructively reclassifies") to gate the clear — zones that loaded as general now omit those keys from the payload instead of zeroing them; BE confirmed (`stations/serializers.py` `TransferZoneSerializer`, `required=False` + `.pop(field, None)` + `if is not None` guard) that an omitted key is its own designed "leave untouched" contract, so no BE change was needed for this bug. AD `develop @ 36d4702`. **Bug 2 — zone list row order changed after any save (found immediately after Bug 1 fix, same page).** `stations/models.py` `TransferZone.Meta.ordering = ['-priority']` had no tiebreaker; zones sharing a priority (common by design — the fallback zone sits at 0) had undefined relative SQL order, and any UPDATE touching the table could shift the query plan and reshuffle tied rows on the next list fetch. Fix: `ordering = ['-priority', 'id']`, matching the only existing multi-field-ordering convention in this codebase (`operators/models.py`, `pages_info/models.py`, `dialogue/models.py` all append `id`, never a name field — confirmed via grep before choosing). Migration `0037_alter_transferzone_options.py` (AlterModelOptions only, no schema change). 2 new regression tests added to `stations/tests.py` (`TransferZoneOrderingTests`); full `stations` suite (60/60) green after the change. BE `develop @ cc7840e`. Both fixes frontend/backend-boundary-correct: Bug 1 stayed 100% FE (BE already designed for the omit case), Bug 2 stayed 100% BE (no FE change needed once list order is deterministic). No new abstractions added — both fixes reused existing flags/conventions rather than inventing new ones, per CLAUDE.md. **NOT done:** no manual browser verification of either fix in the live admin-dashboard UI — reasoning verified via code trace + Plan-agent review + BE test suite, not click-tested; no develop→main deploy — both fixes are develop-only; the untracked pre-existing file `smartenplus-backend/operators/tests/test_transport_composit_pagination.py` (from #304, tracked as a loose end in Section 2) was correctly left alone again, still awaiting its own commit-or-discard decision; this session's AD work is unrelated to #330's checkout-side zone-pricing bugs (different layer: admin zone-management page vs customer checkout).

---

## Session #330 — 2026-08-20

**Achieved:** Zone-pricing general-transfer: 2 more checkout display bugs found+fixed via live E2E-adjacent debugging, frontend merged to develop. Direct continuation of #329's top resume item (manual E2E of the zone-pricing feature) — bugs surfaced from user-provided screenshots of the real checkout flow, not a from-scratch audit. Both bugs traced to the same root pattern: checkout components independently reimplementing a decision that should be shared, and a fix landing in one copy but not propagating to siblings. **Bug 1 — pickup box showing when contract has no `pickup_point` enabled** (contract `o7lfBSOenh`, dropoff-only). Root cause: 4 spots in `components/forms/checkout/Passengers.js` read `contract.pickup_requires_zone`/`dropoff_requires_zone` as the sole trigger, without checking `pickup_point`/`dropoff_point` in `contract.info_fields` — two independently-settable admin controls that can drift (backend `operators/views.py:498` writes the zone flag with zero cross-check, flagged as separate BE follow-up). Fixed via shared `isInfoFieldEnabled(contract, fieldType)` helper used at all 4 sites incl. the blocking Yup `pickupZoneMatched`/`dropoffZoneMatched` validation (an Opus-model deep-review caught this before ship — fixing only seed+render would've left checkout step 1 permanently stuck). Merged `develop @ fcee73ad` → `d9a85f93`. **Bug 2 — Cart Summary sidebar + step-3 Confirmation showing wrong/unrelated route** for general-transfer trips. Root cause: identical to a bug already fixed in `EnhancedTripCard.js` the day before — `isZoneBooking` in `CartDetailDisplay.js:79` and `TripsConfirmation.js:29` checked only "does this trip have a saved zone address," true for both airport-transfer AND general-transfer trips. `TripsConfirmation.js:29` was the 3rd occurrence and weakest (no guard at all), found only via a dedicated Opus SWE-review pass against CLAUDE.md's REUSE FIRST rule. Fixed both by reusing the pre-existing `isAirportTransfer(contract)` helper from `helpers/airportTransfer.js` instead of a 4th divergent check. Merged `develop @ 709f4ba9` → `ba51c72b`. **Process note:** both bugs were plan-mode reviewed by a second model pass (Opus subagent) before implementation — worth keeping for checkout-critical fixes. **NOT done:** full #329 E2E checklist still not walked systematically; `CONTRACTDETAILVIEWSET-SILENT-FIELD-DROP` BE follow-up not actioned; no develop→main deploy; 3-way `isZoneBooking` duplication not unified (deliberately, to keep fixes scoped).

---

## Session #329 — 2026-08-19

**Achieved:** Zone-pricing general-transfer: FE checkout wired, 3 real bugs found+fixed via live debugging, ALL 3 REPOS MERGED TO DEVELOP. Picked up #328's handoff exactly where left off. Built FE checkout wiring per a 4-agent review (Next.js/Django/UXUI/SWE) against the real codebase: `ZoneGatedField.js` (new, wraps `PlacePicker.js`), mutual-exclusion guard against the old `info_fields` textarea (the exact #327 collision), `resolveGeneralZone` RTK Query endpoint, Yup `trips` array schema validating `{field}ZoneMatched` per-item via `this.parent` (not global context, since each trip carries its own contract). BE gap closed: `carts/serializers.py` `ContractSerializer` now exposes `pickup_requires_zone`/`dropoff_requires_zone` to checkout's cart fetch. **3 real bugs found and fixed via live user-reported evidence:** (1) boolean-restore data loss — `Passengers.js`'s `savedData` merge guard treated `false` as falsy, any boolean trip field silently failed to restore from Redux on Formik reinit; (2) pre-existing address not displayed — `ZoneGatedField` never received `formik.values`, `PlacePicker.js` had no prop to accept an initial address; (3) airport-styled card on general-transfer trips — `EnhancedTripCard.js`'s `isZoneBooking` gate checked only for a saved pickup/dropoff point, true for both airport-transfer AND general-transfer trips; added a `transfer_airport` truthy check. Debated and rejected disable-while-invalid Next button (both SWE+UXUI against it — async zone-match field would flicker). Merged all 3 repos to develop this session (explicit user override of #328's "browser-verify before commit" caution): backend `develop @ abd60c2` (128/128 tests), admin-dashboard `develop @ 90e9129`, frontend `develop @ 5e21bffc`. **NOT done: no manual E2E browser test of the full merged feature** — all 3 fixes diagnosed from screenshots + code tracing, not a live click-through post-merge. No develop→main deploy. `CONTRACTDETAILVIEWSET-SILENT-FIELD-DROP` (`meeting_point_place`/`checkin_info`) still untouched. SWE-found `enableReinitialize` race condition reviewed, never live-reproduced, not hardened.

---

## Session #328 — 2026-08-19

**Achieved:** Zone-pricing general-transfer restarted from scratch per user's explicit correction ("that plan is incorrect, review my requirement from that plan again") rather than resuming #327's reverted branches. Redesigned across 3 separate agent-review rounds (Next.js/Django/SWE), landed on: per-field opt-in (`Contract.pickup_requires_zone`/`dropoff_requires_zone`, migration `0071`), general-transfer zones drop the anchor-station concept entirely (unlike airport-transfer), draw-only zone creation (no Airports/Contracts picker on the zone form — linking happens contract-side only), new `ResolveGeneralZoneView`/`resolve_zone_for_contract` (separate from airport-transfer's resolve path). AD: `ZoneForm.js` (453 lines, 2.25× the limit) split into `AirportTransferFields.js`/`ZoneContractPicker.js`/`ZoneTypeToggle.js`; zone list Type column added; `TransferZoneFieldToggles.js` relabeled to plain language + repositioned after user flagged confusion. Found+fixed a silent-save bug in `ContractDetailViewSet.update()` (hand-copies fields off `request.data`, new booleans weren't in the manual list) — also found 2 more pre-existing fields with the same bug (`meeting_point_place`, `checkin_info`), left untouched, tracked separately. BE 128/128 tests pass. FE checkout deliberately not started — scope held to AD+BE only. Nothing committed on either feature branch this session, not yet browser-verified. (FE checkout wiring + the merge to develop happened next session, #329.)

---

## Session #327 — 2026-08-19

**Achieved:** Zone-pricing (general-transfer) plan paused after full revert; shipped a small staff QA tool instead. Planned+built the `zone-pricing-general-transfer-extension` feature across all 3 repos (backend model/serializer/view, frontend checkout required-fields, admin contract checkbox) — 4-agent review (UXUI/Next.js/Django/SWE) done, manual browser testing began, then hit a real UX collision: `Passengers.js` already has a DIFFERENT older pickup/dropoff mechanism (`info_fields`-driven plain textarea) that would visually collide with the new zone-resolved fields if moved to that step. User decided to pause the whole plan and **fully revert all 3 repos** rather than resolve the collision now. Reverted cleanly: all 3 feature branches deleted (`feat/zone-pricing-general-transfer` backend, `feat/zone-pricing-checkout-fields` frontend, `feat/zone-pricing-contract-checkbox` admin), backend DB migrations (`carts.0018`, `operators.0071`, `stations.0037`) unmigrated back to pre-session schema, all repos confirmed back on clean `develop`/`main`. Nothing was ever pushed to any remote during the zone-pricing work, so revert was purely local.

Separately, shipped a small staff-only QA tool on `/airport-transfer/hatyai-airport`: `data-contract-id` attribute (devtools-inspectable) + Shift+D keyboard shortcut toggling a visible contract-ID badge on each `ZoneOptionCard`. Originated from "staff want to check contract/product listing correctness by ID" — 4-agent review unanimously recommended against any customer-visible ID and converged on the devtools-attribute pattern; user then asked for a faster on-screen toggle too. `ZoneOptionCard.js` badge extracted to new `DebugIdBadge.js` to stay under the 200-line component limit. 3 commits on `fix/zone-option-card-contract-id-attr`, merged → `develop`, pushed (`452c1ca3..b4b484c0`).

---

## Session #326 — 2026-08-18

**Achieved:** Fixed production ISR cache bug blocking `/airport-transfer/chiang-rai-international-airport` — `getStaticProps` returned bare `{notFound:true}` on transient errors, permanently ISR-cached. Discriminated real 404 (revalidate 3600) vs transient 5xx/network (revalidate 60, auto-recovers). Fixed `AirportTransferSEO.js` unguarded null → "undefined Transfer!" in meta. Also fixed `keywords` array pushing raw `departureStation` instead of `stationLabel`. 2 commits: `82da53a6` + `452c1ca3`. Pushed → develop.

---

## Session #325 — 2026-08-18

**Achieved:** Fixed mobile overflow on `/airport-transfer/hatyai-airport` Private Transfer section. Two bugs: `AirportEndPill` had no `min-w-0`, PlacePicker wrappers had no `min-w-0 w-full` on mobile. Fixes applied across `AirportEndPill`, `PlacePicker`, section margin, page wrapper. Also bumped `ZoneOptionCard` thumbnail to responsive 96×68px mobile / 120×80px sm+. 2 commits: `819aec2e` + `ba82e757`.

---

## Session #324 — 2026-08-18

**Achieved:** Fixed mobile overflow on `/airport-transfer/hatyai-airport` Private Transfer section. Two bugs: `AirportEndPill` had no `min-w-0`, PlacePicker wrappers had no `min-w-0 w-full` on mobile. Fixes applied across `AirportEndPill`, `PlacePicker`, section margin, page wrapper. Also bumped `ZoneOptionCard` thumbnail to responsive 96×68px mobile / 120×80px sm+. 2 commits: `819aec2e` + `ba82e757`.

**Workspace:** frontend `develop ba82e757` · backend `main 5632db2` · admin `main 5bd6a36` · content `master 3756e5b`

---

**Updated:** 2026-08-17 (session #323)

**Achieved (#323) — Fixed BE 400 on airport transfer booking: expired contract surfacing + resolve-zone date filter + BookButton error toast.**

Investigated 400 Bad Request on `POST /carts/{cartId}/cartitems/` from `/airport-transfer/hatyai-airport`. Root cause: Contract 11 (`hatyai airport to george town (Sedan)`) had `end_date=2025-12-31` (expired) but `is_actived=True` — `resolve-zone` surfaced it because it only validated ratecard existence, not contract `start_date`/`end_date` range. Booking hit `is_valid_travel_date()` → 400 `"traveling date not within valid range"`. Two fixes: (1) BE `stations/views.py` `ResolveZoneView` now filters by `contract__start_date__lte=date` / `contract__end_date__gte=date` — expired/future contracts never surface on the page. (2) FE `BookButton.js` catch block now extracts `error.data.non_field_errors[0]` / `detail` / `message` / array[0] to show the actual backend message instead of generic "Could not add item to cart". Also extended Contract 11 `end_date` to 2027-12-31 (test data fix). Both merged → develop: BE `5632db2` / FE `0d716961`.

**Workspace (#323):**
- frontend: `develop` → `0d716961`. Clean.
- backend: `develop` → `5632db2`. One pre-existing untracked (`operators/tests/test_transport_composit_pagination.py`, from #304).
- admin-dashboard: `main` → `5bd6a36`. Clean.
- content: `master` → `3756e5b`. Clean.

---

**Updated:** 2026-08-17 (session #322)

**Achieved (#322) — Airport transfer direction filter (BE+FE), Hatyai test contracts, ZoneOptionCard 120×80 vehicle thumbnail.**

Deep-analysed `/airport-transfer/hatyai-airport` page + vault: `resolve-zone` returned ALL contracts regardless of direction tab. Built direction filter using existing `Contract.trip.effective_departure_station / effective_arrival_station` vs `airport_id` — zero new models/migrations. BE `stations/views.py`: derives `FROM_AIRPORT`/`TO_AIRPORT`/`BOTH` per link, filters by optional `direction` param. FE `ZonePriceBox.js`: passes `FROM_AIRPORT`/`TO_AIRPORT` based on `tabValue`; `toggleDirection` now calls `handleClearAddress()` first (no stale ref re-resolve on tab swap). `tripsApi.js`: `direction` param forwarded. 3-agent review (NextJS/Django/SWE) before build — caught: use `effective_*` not `trip.route.*` directly, no `tabValue` in useEffect deps (chain violation). Created Hatyai test data via Django shell: Route 31, Trip 39, Contract 202 (`hatyai any hotel to airport (Sedan)`, TRANSPORTATION, PRIVATE), RateCard 1935 (4000 default) + 1936 (4500 on 2026-08-22), ZoneContract 6 (zone1 pinned to Hatyai Airport). Verified filter: `direction=FROM_AIRPORT` → Contract 11 only; `direction=TO_AIRPORT` → Contract 202 only; no param → both. Also upgraded `ZoneOptionCard` vehicle image: `24×24` icon → `120×80px` 3:2 thumbnail (Kiwitaxi/Booking.com pattern) with "Fixed price" overlay badge (GYG pattern); icon fallback at 48px. All merged → develop: FE `ee74c6f2`, BE `6c65cd7`.

**Workspace (#322):**
- frontend: `develop` → `ee74c6f2`. Clean.
- backend: `develop` → `6c65cd7`. One pre-existing untracked (`operators/tests/test_transport_composit_pagination.py`, from #304).
- admin-dashboard: `main` → `5bd6a36`. Clean.
- content: `master` → `3756e5b`. Clean.

---

## Session #321 — 2026-08-16

**Achieved:** Checkout "Add another trip" CTA: AddTripModal 3-tab redirect picker + Itineraries CTA button, merged → develop `14f438a9`. Built `components/forms/checkout/AddTripModal.js` (~255 lines): Transportation tab (AutoCompleteSearch + CalendarDatePickerv2 reused from homepage via nested Dialog at z-index 1400), Activities tab, Airport Transfer tab. Wired dashed CTA button into `Itineraries.js`. Key decisions: same-tab `router.push`; Redux location+calendar cleared on modal open; mobile tabs responsive via `isSmDown`. 7 commits on `feat/checkout-add-trip-cta`, merged `--no-ff` → develop `14f438a9`, pushed.

**Workspace:** frontend `develop 14f438a9` · backend `develop a7eb4f1` · admin `main 5bd6a36` · content `master 3756e5b`

---

## Session #321 (2026-08-16)

**Achieved (#321) — Checkout "Add another trip" CTA: AddTripModal (3-tab redirect picker) + Itineraries CTA button, merged → develop `14f438a9`.**

Full UX/UI/BD 3-agent audit of `/checkout` page first. Then built `components/forms/checkout/AddTripModal.js` (new, ~255 lines) with 3 tabs: Transportation (AutoCompleteSearch + CalendarDatePickerv2 reused from homepage, nested Dialog z-index 1400 pattern to prevent autocomplete expanding parent modal height, redirects to `/trips/[from]/[to]`), Activities (text search → `/activities`), Airport Transfer (redirect → `/airport-transfer`). CTA dashed button wired into `Itineraries.js` after items list (`formStep === 0` only), plus empty-state prominent CTA. Key decisions: SearchDialog reuse rejected (2 independent agents confirmed `onSearch` fires zero-arg then closes — navigation only); same-tab `router.push` not `window.open`; Redux state cleared on modal open; mobile tabs responsive via `isSmDown` (`iconPosition="top"`, short labels, `fontSize: 0.65rem`). 7 commits on `feat/checkout-add-trip-cta`, merged `--no-ff` → develop, pushed. Vault audit doc at `01-projects/checkout-add-items-cta-audit.md`.

---

## Session #320 (2026-08-16)

**Achieved (#320) — r16 weekly SEO audit run + 2 SEO quick wins shipped to develop.**

(Archived from master-state.md #320 block — see log.md for full detail.)

---

## Session #319 (2026-08-15)

**Achieved (#319) — RouteFAQ real-data fix at `/trips/hatyai/koh-lipe`: full cross-discipline report, 3-specialist debate, shipped → develop on both repos.**

User reported the FAQ section ("Frequently Asked Questions — Hatyai to Koh Lipe") showed generic filler instead of real data. Live-verified via curl against prod: 5/6 answers were the generic fallback branch, baked into SSR/ISR HTML. Root-caused two independent bugs: (1) `RouteFAQ.js`'s `tripsFilterSet` prop is client-only (`useGetTripFilterSetQuery`, RTK Query, date-scoped), always `undefined` at SSR time; (2) the `contracts` prop it also reads never actually carried `ratecard` data — `ExteaContractSerializer` has no such field, so the component's own price-derivation logic silently produced `null`. Cross-referenced 3 prior vault findings that predicted this exact failure mode ([[filter-trips-seo-faq-prop-dropped]], [[help-faqs-wp-graphql-broken-prod]], [[build-experience-faq-items-pure-function]]) — this is the third occurrence of the SSR-empty/client-fill bug class.

Ran a full cross-discipline report (SWE/Next.js/Django/SEO/UX/BD) in plan mode before any code, then a pre-merge 3-specialist adversarial debate (Next.js, Django, SEO agents, explicitly told to find holes not confirm) against the resulting implementation plan. Debate caught a real correctness bug before ship: the draft's cancellation-summary logic picked "first contract with any structured policy," unrelated to which contract produced the displayed cheapest price — could have shown one operator's cancellation terms while the price pointed at a cheaper, different operator. Fixed to source cancellation terms from the same contract as the cheapest price first, only falling back if that one has none. Debate also caught: reuse this file's existing `cache.get`/`cache.set` idiom instead of proposing new infra, add `select_related`/`prefetch_related` to avoid a real N+1, drop a planned "how far in advance do I need to book?" question as booking-funnel content with no search intent, and make the FAQPage JSON-LD dedup between `FilterTripsSEO` and `RouteFAQ` (previously coincidental, both gated on the same `contracts.length > 0` condition) explicit via a comment. One SEO-agent claim (a `useCurrency()` loading-gate blocking SSR) was checked directly against `CurrencyContext.js` and found unfounded — corrected before it reached the plan.

**Shipped, both repos, branch `fix/route-faq-real-data` → merged `--no-ff` → `develop`:**
- Backend `develop` `a7eb4f1` (feature `a912cf3`): `products/views.py` `HomeViewSet.custom_route` — new `route_faq` aggregate (cheapest price+operator, operator roster, direct-route flag, cancellation summary from structured `cancellation_policies`, attribution-safe), cached with existing idiom (TTL matched to FE's `revalidate: 300`), `select_related`/`prefetch_related` guarded.
- Frontend `develop` `bd651b33` (feature `e2400fe4`): `pages/trips/[...slug].js` (`route_faq` threaded through all 3 `getStaticProps` return paths), `components/trips/FilterTripsPage.js` (prop pass-through + explicit schema-dedup comment), `components/trips/RouteFAQ.js` (merged `effectiveFilterSet` fallback, new 7th "Can I cancel my booking?" question, hedged price wording for the ISR/live-results date mismatch).

**Verified:** `next build` prerenders real price/operator/cancellation text into static HTML for `/trips/hatyai/koh-lipe` (real numbers: ฿990 Smart EN Plus Co., LTD, 6 operators, direct-route true, tiered cancellation 72h/48h) and `/trips/hatyai/penang` — confirmed via direct inspection of `.next/server` output (equivalent to curl/Googlebot, no JS). Zero-contract routes (`phuket/phuket`, `bangkok/bangkok`) correctly skip FAQ rendering, no crash, no "undefined". Exactly one FAQPage schema per page confirmed (dedup works). BE `products` test suite run — 1 pre-existing unrelated failure (`RecommendationTestCase.test_find_similar_contracts`), confirmed present on clean `develop` too before this session's changes.

**Not browser-click-tested. No BE unit test written for the new `_build_route_faq_aggregate`/`_best_cancellation_summary` helpers** (flagged, non-blocking).

**Workspace (#319):**
- frontend: `develop` → `bd651b33`. Clean.
- backend: `develop` → `a7eb4f1`. One pre-existing untracked file (`operators/tests/test_transport_composit_pagination.py`, from #304, correctly left alone).
- admin-dashboard, content: untouched this session.

---

## Session #318 (2026-08-15)

**Achieved (#318) — Available Transport filter/chip bug at `/trips/hatyai/koh-lipe`: full audit (FE+BE), 4-agent review, chip redesign, shipped → develop on both repos.**

Prod report: Available Transport filter chips sometimes mixed vehicle types (speedboat+van) and sometimes looked duplicated. Deep-dived FE+BE in parallel (2 Explore agents), found the real root cause was subtler than the report implied: on clean data the two compared strings (`contract.transport_composit` vs the filter-facet's `trasportation_com`) are byte-identical — no format mismatch. The actual fragility was missing whitespace/case normalization, plus a genuine `"van undefined"` bug where `vehicle_class` being absent got string-concatenated raw. Separately found the backend's per-operator-cheapest dedup on the facet endpoint (`unique_transport_composit_list`) silently hides composit variety the results endpoint still returns — flagged as a known gap, not fixed (would need product sign-off, changes visible inventory).

Spawned 4 parallel review agents (nextjs-fullstack-architect, backend-architect) against the initial fix plan — caught: BE `type_class`/`vehicle_class` fields needed adding to the serializer (additive, N+1-guarded via `prefetch_related`); FE needed to normalize composit strings before comparing, guard the undefined-concat bug, and dedupe the flattened contract list by id. A second round of 4 reviews (ux-research-specialist, senior-frontend-developer ×2, backend-architect) on the resulting chip UI **independently and unanimously rejected** the first display fix (parenthetical "(Standard)" suffix in the chip label) — chip is only 120-140px wide, the suffix doesn't fit and fails WCAG contrast at 10px gray-400.

User then manually tested against seeded contracts with real 1/2/3-composit and mixed-class (`van standard` + `speedboat vip`) combos — caught 3 more real bugs through iterative screenshot review that no static review surfaced: (1) `parseOption` only read leg-0's class, so a mixed-class contract silently showed the wrong single class; (2) mixing a tagged-chip shape with a plain-label chip shape in the same row produced inconsistent heights (`min-h` vs `h`); (3) 3 tagged legs measured ~165-170px of content in a 140px chip — would have silently clipped via `overflow-hidden` rather than visibly breaking. Iterated the design in Artifact demos (not code) until the user approved: per-leg icon+class-tag columns, no shared text label, fixed `h-[72px]` everywhere, `w-[170px]` only for 3+-leg chips.

**Shipped, both repos, branch `fix/available-transport-filter-mismatch` → merged `--no-ff` → `develop`:**
- Frontend `develop` `7507e3e4`: `FilteredTripList.js` (normalize+dedupe match logic, dedupe flattened list by contract id), `TransportationOptionsFilter.js` (full chip rework — per-leg class tags, fixed height, conditional width), 3 new `helpers/` files (`normalizeTransportComposit.js`, `matchesTransportOption.js`, `transportOptionDisplay.js` — extracted to keep both touched components under the 200-line cap).
- Backend `develop` `e5d5037`: `products/serializers.py` — additive `type_class`/`vehicle_class` fields on `ContractTranspotCompositSerializer` + `prefetch_related` guard on the FK chain (avoids N+1 on the trips-list endpoint). New dev-only management command `operators/management/commands/seed_transport_composit_variety.py` (idempotent, `--cleanup` flag) — seeds 4 test contracts with varied vehicle-type/class combos for exercising this exact bug class in local dev.

**Not browser-click-tested** — Chrome tool declined again this session (asked twice, declined both times). All verification was: ESLint clean, `next build` succeeds and prerenders `/trips/hatyai/koh-lipe`, curl against live Django dev server confirms new API fields present with correct per-contract values, and iterative real screenshots from the user against seeded data (not a live click-through of filter selection). Backend regression test coverage for the new serializer fields not written (flagged by review, non-blocking).

**Workspace (#318):**
- frontend: `develop` → `7507e3e4`. Clean.
- backend: `develop` → `e5d5037`. One pre-existing untracked file (`operators/tests/test_transport_composit_pagination.py`, from #304, correctly left alone).
- admin-dashboard, content: untouched this session.

---

## Session #317 (2026-08-15)

**Achieved (#317) — Trip sort-tab audit at `/trips/hatyai/koh-lipe` (Recommended/Cheapest/Fastest/Early Departure/Top Rated). Found + fixed 2 real bugs, shipped → develop.**

User reported sort-tab results "don't seem correct" after testing. Investigation ran in two passes: an Explore agent traced the full pipeline (route → hooks → sort helpers → API → backend), then an Opus Plan agent did a deep business-model audit of price specifically (user asked how sort-by-price should behave given ADULT/CHILD/INFANT/VEHICLE ratecard rows and per-date overrides). Self-scrutinized the first draft against actual code before reporting — caught and retracted a wrong claim (suspected date-override leakage; backend already resolves ratecard rows to the searched date server-side, `products/serializers.py:332-369`, confirmed reached via `context={'request': request}`). Demoed both bugs to the user as a before/after Artifact with real numbers before implementing.

**Bug 1 (structural):** "Our Pick for This Route" card (`components/trips/FilteredTripList.js:113-129`) extracted the highest-`computeConfidenceScore` contract out of the list **on every sort tab**, not just Recommended — so clicking Cheapest/Fastest/Early Departure/Top Rated could silently bump the wrong contract to an unlabeled card above the correctly-sorted list, hiding the actual #1 result. Fix: gated the extraction behind `sort === 'Recommended'`.

**Bug 2 (business-model, price):** price used for filter/sort/display was `Math.max(...contract.ratecard.map(i => i.selling_rate))` — taking the max across ALL passenger categories (ADULT/CHILD/INFANT/VEHICLE) instead of the one category the contract actually bills (ADULT for JOIN, VEHICLE for PRIVATE/CHARTER). New knowledge atom written: [[ratecard-category-mixing-price-bug]]. Fix reused an existing correct helper (`helpers/utils.js` `findMinSellingRate`) instead of writing new code — wired into `FilteredTripList.js:97` (filter+sort) and `TripItem.js` (display, replacing `getMaxRate` + the old 5-arg `getMainPrice`). Also fixed a related ordering bug: unpriced contracts now sort last, not first (`sortContractsByRate`), and the price-range filter gained a `!= null` guard (JS coerces `null >= 0` to `true`, would've silently let unpriced contracts through).

**Shipped:** branch `fix/trip-sort-price-model`, commit `52657377`, merged `--no-ff` → `develop` `9a0317d6`. Deleted `helpers/getMaxRate.js` (duplicate of the bug) and unreferenced dead hook `hooks/useFilteredAndSortedContracts.js` (same bug, zero consumers, confirmed via grep before deletion). ESLint clean on all 4 changed files. Verified page renders (curl, all 5 pills present in SSR HTML, no crash) but **client-side click-through NOT browser-verified** — no Playwright/browser-automation tool available this session; user declined to test before merge, chose to ship + verify later.

**Explicitly NOT done this session (needs BD decision before building):** party-total pricing (sum adult/child/infant counts × their rates, matching what checkout actually charges via `components/search/Passenger.js:112-139`) vs. keeping a single per-unit rate — changes what "Cheapest" ordering means whenever child/adult price ratios differ across operators, and the price label needs to state which. Slider bounds (`hooks/useTripFilters.js:33-36`) still seeded from category-unaware backend `min_rate`/`max_rate` — the correct, category-aware `min_display_rate` field already exists server-side (`products/views.py:1913`) and is used elsewhere but not yet wired into this slider. Full spec → plan file `~/.claude/plans/check-vault-and-fe-hazy-hopcroft.md`.

**Workspace (#317):**
- frontend: `develop` → `9a0317d6`. Clean.
- backend, admin-dashboard, content: untouched this session.

---

## Session #316 (2026-08-15)

**Achieved (#316) — Overnight-arrival "+1 day" badge fix for trip search cards. Reviewed by 3-specialist agent pass, shipped, merged → develop on both repos.**

Prod bug report (Thai, BD-sourced): trip search-result cards showed overnight routes like "9:30 PM - 11:30 AM" with no indicator arrival is next calendar day — foreign travelers risk double-booking accommodation. Plan-mode investigation traced root cause: `TripCardV2.js` renders bare `HH:MM` substrings with zero day-boundary logic; backend `Trip.departure_time`/`arrival_time` are date-blind `TimeField`s, no `is_overnight` signal anywhere. User asked for 3 specialist review agents (Next.js, Django backend, general SWE) before finalizing the plan — ran in parallel, synthesized findings. Key resolution: `Contract.duration` can't be trusted as the overnight signal (lives on a different model than the trip times, zero `clean()`/`save()` cross-validation in Django admin — confirmed by grep) — raw `departure_time`/`arrival_time` comparison is the reliable source. `tour_duration_days` guards multi-day tour products from a naive "+1" mislabel.

Built a before/after Artifact mockup (dark/light theme, mirrors the real `TripCardV2` grid) to confirm the visual with the user before implementing — user flagged bare "+1" as unclear to first-time foreign travelers; changed to spelled-out "+1 day" (self-evident, no tooltip/hover dependency, matters since nothing hovers on mobile).

**Shipped:** Backend `ContractSerializer.is_overnight` computed `SerializerMethodField` (`products/serializers.py`, zero migration, short-circuits for multi-day tours) — commit `292fe39`. Frontend: `isOvernightArrival()` fallback helper in `helpers/formatTime.js` + inline "+1 day" badge (not full `BadgeChip`, arrival column too narrow) wired through `TripCardV2.js`/`TripItemLayoutV2.js` and the legacy `TripCard.js`/`TripItemHeader.js`/`TripItem.js` path for parity — commit `87f2b1c2`. Both on branch `fix/overnight-arrival-badge`, pushed, merged `--no-ff` → `develop` on both repos (backend `99616f1`, frontend `65d25a8a`). `TripMobileSummary.js` confirmed out of scope — it doesn't render times at all today (separate pre-existing gap, noted not fixed).

Verified without a browser tool (user declined Claude-in-Chrome install): backend logic confirmed via Django shell (`venv/bin/python manage.py shell`) — overnight trip → `is_overnight: True`, same-day → `False`, multi-day-tour guard → `False`; frontend fallback helper confirmed matching via Node. Then user asked to make real contract `pkXYnPg0He` (id 6, hatyai railway station → koh-lipe, single-contract trip, safe to edit) overnight for a live click-through test — set `arrival_time` 13:30→06:30 + `duration` 4:30:00→22:00:00, confirmed `is_overnight: True` live via curl, then reverted both fields back to original values once the user confirmed the badge looked right in-browser.

**Workspace (#316):**
- backend: `develop` → `99616f1`. Untracked `operators/tests/test_transport_composit_pagination.py` still present (pre-existing from #304, correctly left uncommitted — untouched this session).
- frontend: `develop` → `65d25a8a`. Clean.
- admin-dashboard, content: untouched this session.

---

## Session #315 (2026-08-15)

**Achieved (#315) — Admin-dashboard transfer-zone contract/operator UX fix + Thai help-page update. Both shipped, merged → develop.**

Staff couldn't tell which company owned which contract when mapping zone↔airport↔contract on `/routemanagement/transfer-zones` — contract chips/rows showed contract name only, no operator. UXUI-vs-BD debate report first (operator inline text vs badge/groupBy), then implemented via nextjs-developer + backend-architect agent pair. Iterated 4x against user screenshots: v1 (em-dash suffix) truncated the wrong end (operator clipped, not contract name); v2 (composed `<Stack>` label) still clipped — root cause found by reading MUI source directly (`Chip.js` hard-codes `overflow:hidden` on the label slot regardless of content); v3 fixed via `sx` override on `.MuiChip-label`, worked for chips but pin-rows still truncated (genuine space-budget issue, 3 elements in ~520px); v4 restructured pin-rows to 2-line stacked layout — confirmed working via user screenshot. Added one BE field (`ZoneContractSerializer.operator_name`, admin-only endpoint, zero customer-frontend impact) with user approval per backend-safety rule. Shipped: AD `41be857` (FE) + backend `3e292f6` (BE serializer field), both merged `feat/zone-airport-contract-scoping` → `develop` (this also carried forward #313/#314's unmerged multi-airport zone picker + per-contract airport pin work — user explicitly confirmed shipping the whole branch, not just today's fix).

Second half of session: help.js (Thai ops tutorial page, written at `a8d93bf`) was stale against 3 commits that shipped after it. Spawned nextjs-developer to diff `c4daaf6`/`70ffa57`/`41be857` against current `ZoneForm.js`+`index.js` and list every undocumented user-facing change. Added 5 new Thai sections/callouts: multi-airport zone selection, per-contract "restrict to one airport" pin feature (biggest gap — full workflow + when-to-use-it explanation), operator badge/grouping in picker, cross-border test-address search, "Test from {airport}" selector, plus a troubleshooting callout for stale pins after removing an airport from a zone. Committed directly on `develop` (docs-only, zero behavior risk) — `5bd6a36`, pushed.

**Workspace (#315):**
- admin-dashboard: `develop` → `5bd6a36`.
- backend: `develop` → `3e292f6`. Untracked `operators/tests/test_transport_composit_pagination.py` still present (pre-existing from #304, correctly left uncommitted).
- frontend, content: untouched this session.

---

## Session #314 (2026-08-14)

**Achieved (#314) — FE customer-facing airport-transfer PlacePicker: cross-border address search + clear-text button. Shipped, merged → develop.**

User asked to check the vault + `/airport-transfer/phuket-airport` for the same neighboring-country fix just shipped in admin-dashboard's transfer-zone tester (commit `c4daaf6`, TH-only → TH+MY/LA/MM/KH). Traced the FE render path: `pages/airport-transfer/[slug].js` → `ZonePriceBox.js` → `PlacePicker.js` — found the identical hardcoded `componentRestrictions: { country: ['th'] }` blocking real cross-border pickup/dropoff search (e.g. Hatyai airport transfer into Penang, Malaysia). Widened to the same 5-country list AD used (Google Places caps at 5 country codes/request), sourced from vault note `thailand-location-coverage-framework.md` Category 9. Single caller (`ZonePriceBox.js`), no shared-API break — confirmed via grep before editing.

Follow-up ask: add a clear (✕) button to the address input. Found existing project pattern first (`components/autocompletesearch/SearchInputField.js` — `HighlightOffOutlinedIcon` from `@mui/icons-material`, right-aligned, shown only when input has text, `aria-label` clear text) and reused it rather than inventing new UI. Added `onClear` prop to `PlacePicker.js` (optional, mirrors the `onSelect` shape) and wired it in `ZonePriceBox.js` to reset `selected` state — without this, clearing the text would've left a stale price/zone card on screen since `ZonePriceBox` owns that state independently of the input's own text.

**Ship path.** Branch `fix/airport-transfer-cross-border-search` off `develop`, one commit `6c1f8307`, pushed, merged `--no-ff` → `develop` `fa5476eb`, pushed. Lint clean both files, verified via running dev server (page 200, HMR live).

**Workspace (#314):**
- frontend: `develop` → `fa5476eb`. Feature branch `fix/airport-transfer-cross-border-search` left on remote (merged, cleanup candidate).
- backend, admin-dashboard, content: untouched this session.

---

## Session #313 (2026-08-14)

**Achieved (#313) — Airport-transfer zone↔airport reuse (Slice 7) + per-airport contract scoping fix (§9), both shipped on feature branches, PRs opened against develop (not yet merged).**

User asked to make transfer zones reusable across multiple airports (e.g. one "Chiang Mai Zone A" offered from both CNX and CEI). Built `ZoneAirport` M:N link table mirroring the existing `ZoneContract` idiom (migrations 0034/0035, `resolve_zone()` query change, AD `ZoneForm.js` single→multi airport picker). 36 stations tests passing at that point.

Mid-review, user personally traced a real gap this reuse introduced: `ZoneAirport` (zone↔airport) and `ZoneContract` (zone↔contract) are independent — once a zone resolves from any linked airport, every linked contract is offered, with no way to restrict an operator to the specific airport it actually serves. Walked through a concrete numeric example (Contract-001 CNX-only, Contract-002/003 CEI-only, all sharing one zone) that made the risk undeniable. Two review rounds followed a same-day reversal (first "wait," then "build now" once the example landed): a first 4-agent pass (BD/Django/Next.js/SWE) on whether to fix, a second 3-agent pass (Django/Next.js/SWE) validating the actual design against project rules. Shipped: nullable `ZoneContract.airport` FK (migration 0036, no backfill needed), one-line filter in `ResolveZoneView`, `clean()` guard against pinning to an airport the zone isn't linked to, new `set_zone_contract_airport()` service fn, AD pin-control UI. 42/42 stations tests pass, including the exact bug repro.

AD pin-control UI needed 3 iterations to land: attempt 1 (Select nested inside Autocomplete's `renderTags`) was structurally broken — MUI Autocomplete's click-away detection is DOM-ancestry-based and Select's Portal-rendered menu sits outside that subtree, so no `stopPropagation` fix was possible. Attempt 2 moved the pin control to a separate list block below the Autocomplete — fixed the real bug but user found a second issue live-testing: MUI's `Select` hides its label text on an empty (`''`) value unless `displayEmpty` is set, so "Any airport" looked blank/broken even though clicking real airports worked correctly the whole time. One-line fix (`displayEmpty` prop) closed it.

A third 3-agent review (same trio) assessed the user's follow-up question — should this pivot to contract-first editing (zone creation stays simple, contracts map to zones from the Contract page instead)? All 3 converged: no, don't pivot — the backend is already direction-agnostic (`_apply_diff` is the same sync engine either way), the two UI failures were a MUI bug true on any page not evidence zone-first is wrong, and removing contract-management from the zone page would lose a real bulk-view capability. User confirmed: keep current design, defer contract-side pin support as a future non-blocking addition.

**Ship path.** Both repos branched `feat/zone-airport-contract-scoping` off `main` (not `develop` — both were on `main` going in), committed, pushed. `gh` CLI unavailable — PRs not yet opened via API; GitHub provided direct compare-PR links in push output for both repos, need to be opened manually with base=`develop`.

**Workspace (#313):**
- backend: `feat/zone-airport-contract-scoping` → `bcf2326`, pushed. PR not yet opened.
- admin-dashboard: `feat/zone-airport-contract-scoping` → `70ffa57`, pushed. PR not yet opened.
- frontend, content: untouched this session — confirmed zero FE changes needed for this fix (server-side filtering only, `resolveZone` contract unchanged).
- Full design history: ADR §7 (zone-airport M:N), §8 (documented-then-superseded "wait" decision), §9 (shipped fix + UI iteration + pivot-rejection) in `04-decisions/adr-airport-transfer-zone-pricing.md`.

---

## Session #312 (2026-08-14)

**Achieved (#312) — Trip search-results skeleton rebuilt to match #311's redesigned card, all breakpoints. Merged → develop.**

`components/itinerary/SkeletonSection.js` still drew the old pre-#311 card anatomy (single non-responsive template, plain rounded icon boxes, price/CTA in old desktop position, no Top Pick/favorite row, no divider/CTA column) — every loading→loaded swap visibly jumped/reflowed on every viewport. Explore agent traced the live render path (`pages/trips/[...slug].js` → `TripSearchResults.js` dynamic-import fallback + `TripsPageLayout.js` `isFetching` state → `<SkeletonSection />` ×3) and confirmed a second file, `components/trips/TripResultsSkeleton.js`, was dead code (zero imports, only a stale comment reference).

Rewrote `SkeletonSection.js` as one card template with explicit `sm:hidden`/`hidden sm:flex` blocks mirroring the real component tree: mobile block matches `TripMobileSummary.js` (Top Pick+favorite row, indigo-tinted journey box, `BadgeChip`-shaped pill row instead of plain icon boxes, operator row above price, merged price+CTA row with 132px book-button placeholder) and `sm:`-only block matches `TripCardV2.js`+`TripCtaColumn.js`+footer (grid `auto_1fr_auto` time/station skeleton, contract-badge placeholder, divider, CTA column stack, bottom operator footer). Deleted `TripResultsSkeleton.js`; removed its stale reference from a comment in `CheckoutStepSkeleton.js:14`. 111 lines, `eslint` clean on both touched files; user's own `next dev` was live so build was verified via lint + grep for dangling references rather than a competing `npm run build`.

**Ship path.** Branch `fix/trip-card-skeleton-parity`, one commit `96ecff50`, pushed, merged `--no-ff` → `develop` `44756128`, pushed. Clean merge, no conflicts. Feature branch left on remote (cleanup candidate, same as #311's).

**Workspace (#312):**
- frontend: `develop` → `44756128` (merge of `fix/trip-card-skeleton-parity`, commit `96ecff50`).
- admin-dashboard, backend, content: untouched this session (backend has an unrelated pre-existing untracked file, `operators/tests/test_transport_composit_pagination.py`, carried from #304, not touched).

---

## Session #311 (2026-08-14)

**Achieved (#311) — Mobile trip card UX audit + fixes shipped, `/trips/hatyai/koh-lipe` 375px. Merged → develop.**

**Review process — 3-agent debate + iterative demo, then real implementation team.** Started from a mobile screenshot review: UX/UI + Designer + BD debate on the trip card vs world OTA platforms (Trip.com/Booking/12Go/GYG — general-knowledge comparison, live scrape blocked by DataDome-class WAFs on all 3, confirmed this session not just carried from prior vault findings). Built and iterated an HTML Artifact demo (before/after mobile mockup) across many rounds as the decision-making surface before touching real code — user caught real issues each pass (density mismatch vs actual screenshot, missing operator-row alignment, Skyscanner-referenced price+CTA pattern, redundant chip, journey/perks consolidation). Once the direction was validated in the demo, spawned a 2-agent review team (`nextjs-fullstack-architect` → `senior-frontend-developer`) to turn the accumulated chat findings into a real implementation plan — the architect verified all 14 proposed findings against actual current source (not the demo), catching that 3 didn't reproduce in real V2 code (duplicate ids were V1-only, station `<h3>` never existed, booked-badge was already inline) and that 2 needed descoping entirely (THB decimals = payment-adjacent shared helper w/ 24+ consumers, needs its own PR; seat-count anomaly = backend data question, not a frontend clamp).

**Implementation, iterative — shipped, then corrected against live user feedback across several follow-up rounds.** `TripCtaColumn.js`/`TripItemLayoutV2.js`: strikethrough price contrast `gray-400`→`gray-600` (WCAG AA). `TripItem.js`/`TripItemHeader.js`: duplicate `accordion-collapse*` DOM ids fixed on the still-live V1 legacy path (confirmed reachable via `FilteredTripList.js`/`RecommendedTripCard.js` on destinations/airport-transfer listings — not dead code). `TripItemLayoutV2.js`/`TripItem.js`: `rounded-lg`→`rounded-md`, Top Pick border → `border-emerald-500` (matches `COLORS.status.success` #10B981 exactly). `TripCardV2.js`: duration label `text-[10px]`→`text-xs`; from→to grid rebuilt `flex-1 basis-0` (equal-thirds, squeezed long station names) → `grid-cols-[auto_1fr_auto]` (content-sized time/station columns, duration gets the flexible middle) — this was the real fix for a user-reported "doesn't match demo" alignment complaint, root-caused by comparing the demo's CSS grid against the real component's flex approach. `ExtraItemsList.js`: added `aria-label` to icon-only badges (shared, 6 consumers, additive-only). New `TripMobileSummary.js` (~130 lines) — consolidates what was 4 stacked mobile groups (Shared Ride pill, journey stepper, icon-only badges, value pills) into 2 (bordered journey block with ride-type as lead tag; one flat labeled "perks" row), merges price+CTA into one Skyscanner-referenced bottom row (price left, Book Now right), moves operator identity (logo/name/rating/booked-count) above that row as its own line (user-confirmed: close but not merged into the CTA row itself), relocates the favorite heart to share a row with the "⭐ Top Pick" badge instead of sitting alone (fixed a dead-whitespace bug from an earlier iteration of this same session), and switches the heart's `BookmarkButton` variant `overlay`→`ghost` to match desktop's already-compact size (fixed a real MUI `sizeLarge` padding-waste bug user caught from live-rendered HTML). Dropped the "🎫 Refund" chip per user's confirmed choice — turned out to not exist in real code at all (backend-driven `extraItems`, no hardcoded "Refund" string anywhere), so this was corrected to "don't build a filter for a chip that isn't real" rather than removing anything. One real JSX bug (orphaned `</Box></div>)}` fragment from an incomplete earlier edit) caught by the user's dev-server error and fixed same-session.

**Verification.** `npm run build` clean throughout (some flaky intermittent failures mid-session traced to the user's own concurrent `next dev` server racing the build's `.next` cache — not real errors, resolved by not fighting it). No browser/screenshot tool available this session (Claude-in-Chrome declined) — all visual confirmation came from the user pasting live rendered output/screenshots and flagging specific mismatches, which is how the from→to alignment bug and heart-padding bug were actually found. Real-device/browser visual confirm still outstanding — every fix this session was verified by build-clean + code-level reasoning + user's pasted screenshots, not a direct browser check by the agent.

**Ship path.** Single branch `fix/trip-card-mobile-a11y-conversion`, one commit `bc0bc79e` (all rounds squashed into one commit since nothing was pushed until the user's explicit "commit and push then merge" at session end), pushed, merged `--no-ff` → `develop` `d9bf10ad`, pushed. Clean merge, no conflicts.

**Workspace (#311):**
- frontend: `develop` → `d9bf10ad` (merge of `fix/trip-card-mobile-a11y-conversion`, commit `bc0bc79e`). Feature branch fully merged, left on remote (cleanup candidate).
- admin-dashboard, backend, content: untouched this session.

---

## Session #310 (2026-08-14)

**Achieved (#310) — Trip card "View Detail" disclosure redesign, continuing #309's CTA column work. Two rounds, both shipped and merged → develop.**

**Round 1: merge two disclosure controls into one.** Card had an icon-only chevron (opens gallery+price accordion) AND a separate "View details" text button (opens `ServiceGuidelines` drawer with transport/vehicle info) — two triggers, two surfaces. Merged into one inline accordion behind a single "View Detail" button: `TripItemAccordionContent` (`TripItem.js`) now renders gallery + price table + transport/vehicle/seat list (reusing `ServiceGuidelines`'s child components — `TransportDescription`, `TravelTimeItem`, `ConditionalIconListItem`, `MaxSeatListItem`, `TransportExtraList`) in one panel. `ServiceGuidelines.js` itself kept (4 other call sites confirmed live, incl. legacy V1 path) — only its call site inside V2's `TripItemLayoutV2.js` footer removed. Also fixed pre-existing P2 debt from #309's audit: duplicate DOM ids (`accordion-collapse*` was hardcoded, shared across every card in the list) — suffixed with `productSlug` throughout. Verified via `design-review` agent, live at 1440px/375px: exactly one button per card, `aria-expanded` toggles correctly, merged panel renders gallery+price+transport together, no console errors (one unrelated pre-existing S3 403 on vehicle images, not caused by this change).

**Placement debate → technical review → visual-only fix (round 2).** User asked for a UX/Design/BD debate on where the button should sit. Debate leaned toward moving it from the CTA column into the footer (proximity-to-Book-Now / mislabeled-as-price-detail concerns). Followed with a NextJS + SWE technical review of that specific move, which surfaced real costs neither the design debate nor product-perspective could see: **(a)** the accordion (`{accordion}`) renders *between* header and footer in `TripItemLayoutV2.js` DOM — moving the trigger into the footer puts it *after* the content it controls, inverting expected screen-reader/keyboard tab order; **(b)** footer's desktop right-cluster is currently empty (both children `sm:hidden`) — not a clean append, needs a visibility-logic rework; **(c)** CTA column was purpose-built *this same session's predecessor* (#309) specifically to hold price/favorite/Book Now/View Detail together, already verified — footer move would be a same-session revert-and-redo, not a discovered oversight; **(d)** zero test coverage exists for any of this interaction, so a 3rd structural change with no automated regression net is real risk. User picked: **keep position, fix the actual complaint (visual competition with Book Now) by demoting weight instead of moving.**

**Implementation.** New `components/trips/TripDetailToggleButton.js` (~20 lines) — extracts the button JSX that was duplicated between `TripCtaColumn.js` (desktop) and `TripItemLayoutV2.js` (mobile inline), both technical reviews had independently flagged this as pre-existing REUSE-FIRST debt. Style demoted from `font-semibold text-gray-700 hover:text-gray-900` to `font-medium text-gray-500 hover:text-gray-700` — reads secondary next to Book Now's filled MUI button, no fill/border added, 44px touch target preserved. Both call sites now differ only by a `className` prop (spacing). Lint clean on all 3 touched files.

**Ship path.** All work stayed on `feat/trip-card-merge-view-detail` (single branch, both rounds, no separate branch per round — reasonable since round 2 directly modifies round 1's files before anything was pushed). One commit `101c5b68` (amended once to cover full scope — initial message only described round 1, amended before push since nothing was public yet), pushed, merged `--no-ff` → `develop` `53967dcd`, pushed. Clean merge, no conflicts.

**Workspace (#310):**
- frontend: `develop` → `53967dcd` (merge of `feat/trip-card-merge-view-detail`, commit `101c5b68`). Feature branch fully merged, left on remote (cleanup candidate).
- admin-dashboard, backend, content: untouched this session.

---

## Session #309 (2026-08-14)

**Achieved (#309) — Trip card redesign shipped on top of #308's rename work: deduped "Shared Ride" pill, added a journey stepper, restored trust chips, and gave price/Book Now a dedicated CTA column. Committed, pushed, merged → develop.** Continuation of the same `feat/shared-ride-label-rename` branch — user reviewed #308's shipped rename and flagged the card still looked cluttered/duplicated, kicking off a design-iteration session.

**Design process — demo-first, two rejected rounds before landing.** First implementation attempt (journey stepper + CTA moved into a stacked header corner) was rejected outright ("look really bad design now, revert") — fully reverted. User then shared a reference design (3-zone horizontal card, dedicated CTA column) and asked for a formal debate: spawned `ux-research-specialist` + `nextjs-fullstack-architect` + `senior-frontend-developer` (2 rounds each, independent-then-rebuttal) comparing the reference against the shipped card. Converged on **cherry-pick, not full-adopt**: take the dedicated price/CTA column + a "View details" text-link relabel; defer the reference's dotted-circle journey diagram and 4-chip trust row (no N-leg fallback spec, no confirmed chip count, doesn't fit real mobile card width per feasibility agent's numbers). Built and iterated an HTML artifact demo through several rounds before any code — user caught real gaps in the demo itself (missing review count, missing ride-type pill, missing trust chips after a stepper rebuild) each time, all fixed in the mockup first.

**Pre-implementation review round 2.** Same `nextjs-fullstack-architect` + `senior-frontend-developer` pairing reviewed the concrete implementation plan (not just the design) against CLAUDE.md constraints. Caught two real blockers: BookButton's DOM-order-vs-visual-position risk (screen-reader reading order) needed an explicit strategy, not just "verify later"; and no stated mobile breakpoint-collapse behavior for the new CTA column (real-width math: fixed vertical column doesn't fit desktop/mobile at 316-359px alongside stepper+chips). Both resolved in the plan before coding: CTA column DOM stays after left-zone content (CSS Grid handles visual position independent of source order), and the column collapses to the existing horizontal mobile layout below `sm`.

**Implementation.** New `TripJourneyStepper.js` (one shared component at every breakpoint — icon+vehicle+seat-count per leg, connector glyph carries "guaranteed connection" via `Tooltip` with `enterTouchDelay={0}` for mobile tap support, no more standalone jargon text). New `TripValueSignals.js` (Free Cancellation/Instant Confirm via existing `BadgeChip type="status"`, no new chip component needed). New `TripCtaColumn.js` (price/bar-rate/favorite/Book Now, extracted as its own file specifically to keep `TripItemLayoutV2.js` under the 200-line ceiling — first draft blew past it twice, 238 then 221 lines, from an early mistake duplicating `TripCardV2`+stepper across separate mobile/desktop JSX blocks, exactly the anti-pattern the plan had explicitly banned; fixed by collapsing to one shared tree). `ServiceGuidelines.js` "•••" icon-only drawer button relabeled to visible "View details" text + chevron, `aria-label` updated to match (WCAG 2.5.3). `TripItem.js` memo comparator gained `average_rating`/`booked_count` diffing (rating now has more visual weight, staleness risk was previously silent). Re-wired the already-present-but-unwired `contractType` prop from `TripItemLayoutV2` → `TripCardV2` so `ContractTypeBadge` (top-left pill) actually renders — this was the fix for the original duplicate-label complaint from `#308`/earlier this thread.

**Post-implementation bug — caught by user screenshot, not by me.** First live render was broken: everything (times, stepper, chips, price, button) smeared into one horizontal row instead of a proper left-zone/divider/CTA-column split. Root cause: used Tailwind `sm:contents` (`display:contents`) on the left-zone wrapper trying to make its children act as direct grid items while still "belonging" to column 1 — `display:contents` doesn't work that way, it dissolves the wrapper's box entirely, so children got auto-placed across all 3 grid columns/rows by the browser instead of stacking in column 1. Fixed by replacing with a real `flex flex-col` box as one genuine grid item; `items-stretch` on the parent grid lets the CTA column match the left zone's height and vertically center its own content, matching the approved demo.

**Testing gap found, not fixed (flagged as new follow-up).** Plan required an RTL test asserting BookButton's click doesn't bubble to `onTripClick`. Writing it surfaced a **pre-existing, unrelated bug**: every `@mui/material` component (`Chip`, `IconButton`, `Button`, `Drawer`) fails to render in this project's current jest environment — confirmed via isolated `<IconButton>`/`<Chip>` render tests, nothing to do with this session's changes. User approved skipping the test rather than scope-creeping into unrelated jest/MUI config. New Section 2 item opened (`FE-JEST-MUI-BROKEN`).

**Ship path:** same branch `feat/shared-ride-label-rename` off `develop b0809821`, one commit `13be60ba` (21 files: 18 modified continuing #308's rename + 3 new components from this session), pushed, merged `--no-ff` → `develop c336b248`, pushed. Lint clean. User visually confirmed the fixed render before merge approval ("look ok, commit and push then merge to develop").

**Workspace (#309):**
- frontend: `develop` → `c336b248` (merge of `feat/shared-ride-label-rename`, commit `13be60ba`). Feature branch fully merged, left on remote (cleanup candidate, same as #307's pattern).
- admin-dashboard, backend, content: untouched this session.

---

## Session #308 (2026-08-14)

**Achieved (#308) — "Join" contract-type label renamed to "Shared Ride"/"Private Ride" across the whole customer-facing surface, plus the pre-existing missing-indicator gap on trip search cards and detail page closed. NOT YET COMMITTED (branch ready, awaiting explicit commit approval).** User reported "Join" as bad UX wording for transportation on `/trips/hatyai/koh-lipe`.

**Phase 1 — 3-agent debate.** Ground-truth first: "Join" is not a booking CTA (`BookButton` always says "Book Now") — it's `CONTRACT_TYPE.JOIN`, a shared-vs-private vehicle indicator, displayed as `CONTRACT_TYPE_NAMES.JOIN = "Join Tour"`, and was **completely missing** from `TripCardV2`/detail page (pre-existing V1→V2 regression, previously flagged in [[trip-card-v2-flight-style-audit]] P1#1). Ran 3 parallel specialist agents (`ux-research-specialist`, `react-ui-engineer`, `business-analyst-expert`) debating independently. Unanimous: reappear on both search card + detail page, consolidate to one central label map. Split 3 ways on copy: UX→"Shared Ride"/"Private Ride", UI-eng→keep "Join Tour" (status quo), BD→"Shared & Save"/"Private Vehicle" (benefit-framed). Synthesized to vault → [[join-label-transport-ux-debate]].

**Phase 2 — competitor research.** Live-checked Bookaway (2 routes: Bangkok-Koh Chang, Rio-Ilha Grande) — found their actual pattern badges ONLY the private option, leaves shared unmarked by omission. Didn't resolve JOIN wording directly but de-risked PRIVATE naming (all 3 agents + Bookaway converge near "Private Ride"). 12Go/Omio blocked (JS-rendered / 403), flagged as gap not finding.

**Phase 3 — user decision.** User picked UX's "Shared Ride" for JOIN over the other two. Confirmed "Private Ride" (not bare "Share") for parallel construction, reasoning: bare "Share"/"Join" both fail the same object-less-verb UX problem.

**Phase 4 — implementation, wider than the debate assumed.** Explore agent found the blast radius wasn't just the central `CONTRACT_TYPE_NAMES` constant — **4 separate hardcoded label sources** existed (`OperatorFilterBar.js` own `FILTER_LABELS`, `EnhancedTripCard.js`/`ServiceCategoryDetail.js` inline ternaries defaulting to raw uppercase for PRIVATE — a pre-existing display bug, fixed as a side-effect —, a second `TOUR_TYPES`/`TOUR_TYPE_LABELS` map in `dayTripConstants.js`, and `vehicleDescriptions.js` feeding `VehicleTypeTooltip` which was rendering the **raw enum value** `{vehicleType}` directly, not the mapped label — the actual worst offender, silently showing bare "JOIN" on every trip card via tooltip even before this session). Live browser sweep (Playwright, since `chromium-cli` unavailable on this machine — used repo's own `node_modules/playwright` directly) caught 6 MORE unmapped raw-`.type` render sites the static grep/Explore pass missed: `RouteSummary.js`, `RouteFAQ.js` (SEO-facing FAQ answer text + schema), `TripSummary.js` (2 sites, one feeding `ItemList` JSON-LD `Product.name`), `TripDetailHeader.js`, `TripDetailHero.js`, `TripDetailsImageAndMap.js` (page heading). Total 16 files touched. New UI: `ContractTypeBadge.js` (pre-existing, previously only used on `pages/operators/[slug].js`) wired into `TripCardV2.js` (new `contractType` prop, threaded from `TripItemLayoutV2.js`'s existing `vehicleType`) and `TripDetailsAttribute.js`.

**Verification — live browser, not just lint/build.** `npm run build` compiled clean (pre-existing unrelated `/account` page error confirmed present on `develop` too, not caused by this work). Full eslint clean on all 16 files. Playwright-driven: `/trips/hatyai/koh-lipe` search cards (desktop 1440px + mobile 375px), trip detail page (`/trips/detail/GV6BatJ8ld`), operator listing (`/operators/smartenplus`) all screenshot-confirmed — "Shared Ride"/"Private Ride" render correctly everywhere, zero visible "JOIN" text-node hits (DOM tree-walker sweep, script/style tags excluded), zero console errors, operator filter tabs read "All (15) / Private Ride (4) / Shared Ride (10) / Charter (1)" with counts intact.

**Ship path:** branch `feat/shared-ride-label-rename` off clean `develop` (per policy). **NOT committed yet** — user ran `/wrapup` before the commit step; FE code changes are verified-working but sitting as uncommitted working-tree diff. Dev server + scratch Playwright scripts cleaned up (ports 3000/3001 killed, scratch `.js` files removed).

**Workspace (#308):**
- frontend: branch `feat/shared-ride-label-rename` (off `develop b0809821`), 16 files modified, **uncommitted**.
- admin-dashboard, backend, content: untouched this session. (Backend has an unrelated pre-existing untracked test file, not from this session — see Section 2 item carried from #304.)

## Session #307 (2026-08-13)

**Achieved (#307) — Fav/heart button repositioned on TripItemLayoutV2 trip-result cards (tablet/desktop only), plus a follow-up spacing fix. Shipped to develop.** User asked to move the fav/save heart button from the card footer (buried next to operator info + Book Now) up to the price row, on `/trips/hatyai/koh-lipe`.

**Placement debate.** Before coding, ran a genuine 2-agent debate (`ux-research-specialist` vs `senior-frontend-developer`, backgrounded in parallel) on exact heart position within the price row. UX argued left-of-price (proximity to the decision anchor, price). Design argued right-of-price (the price column is `flex-col items-end` — everything right-anchors; a left-side icon breaks that alignment contract; also flagged the reused `variant="overlay"` skin — translucent circle built for photo backgrounds — as wrong on a plain white card regardless of side). Design's structural argument won: right-of-price still satisfies UX's core ask (heart beside price, out of the footer's Book-now mistap zone) without inventing a layout exception. Built a static HTML mockup artifact (before/after, both proposed placements) to walk the user through the result before coding.

**Shipped scope correction.** Initial implementation applied the change to all viewports (no breakpoint split existed on that row). User clarified the request was tablet/desktop-only — added `hidden sm:block` / `sm:hidden` split so mobile (<640px) keeps the original footer placement untouched, while `sm:`+ gets the new price-row placement. Verified via Playwright CLI screenshots at 390px/768px/1024px/1440px.

**Follow-up bug — heart/arrow crowding.** User reported price and heart "collapse sometimes" on iPad/desktop, then supplied the actual rendered DOM. Real cause (not a timing bug, contrary to first hypothesis): the arrow `IconButton`'s existing `sx={{p:1.25, m:-1.25}}` applies a **-10px margin on all sides**, including its own left edge — originally tuned to sit flush against the price text. With the heart now sitting between price and arrow, the arrow's -10px pull ate into the heart's `mr-2` (8px), netting a slight overlap/crowd instead of a gap. Fixed by bumping the heart wrapper's `mr-2` → `mr-3`; confirmed visually via screenshot at 1024px (clear gap now present on all cards). Also added a new `variant="ghost"` to `BookmarkButton.js` (bare icon-button skin matching the arrow's style, `size="small"`, no bg-fill) to replace the ill-fitting `overlay` skin in this context — isolated to this one caller, all other `icon="heart"` callers (`DayTripCard`, `DayTripHero`, `AirbnbPhotoGrid`, `SavedItemRow`, `TripDetailHero`) untouched.

**Ship path:** branch `fix/trip-card-favbtn-price-row` off clean `develop`, 2 commits (reposition + gap fix folded into working tree before single commit `ec65c0a0`), pushed, merged `--no-ff` → `develop b0809821`, pushed. Lint clean both commits. Not yet screenshot-verified on a real mobile device (only viewport-emulated via Playwright).

**Workspace (#307):**
- frontend: `develop` → `b0809821` (merge of `fix/trip-card-favbtn-price-row`, commit `ec65c0a0`). Feature branch left on remote (merged, cleanup candidate).
- admin-dashboard, backend, content: untouched this session.

## Session #306 (2026-08-13)

**Achieved (#306) — Two-part fix to the TripCardV2 station-block layout, both shipped to develop.** User re-reported the from→to block on `/trips/hatyai/koh-lipe` as visually broken, this time with live rendered HTML pasted in-chat (turned out decisive both rounds — literal DOM state caught a wrong diagnosis and later confirmed the right one).

**Part 1 — stuck-left / dead-space-before-price.** First move was reusing #305's verified-but-unshipped fix: uniform `line-clamp-2` (dropped `sm:line-clamp-1`) + `min-h-[2.5rem]` on both station spans in `components/trips/TripCardV2.js`. Applied it — user reported **zero visible change**, pasting HTML that still showed old classes. Investigated: source file had the fix correctly (confirmed via `git diff`), Tailwind v3.4.4 has line-clamp built in (no plugin needed, class is valid) — not a stale-cache issue at the code level, the fix was real but **irrelevant to what the user was seeing**, since clamp/tilt only changes wrapping *inside* a fixed `min-w-[64px]` column, invisible unless a name sits near the 2-line boundary. Re-traced the actual width/flex chain via Explore agent: `FilterTripsPage.js` (`max-w-[1200px]`) → `TripsPageLayout.js` (`w-full flex-grow`) → `FilteredTripList.js` `<li>` full-width → `TripItemLayoutV2.js:50` header row (real `flex`+`justify-between` context) → `TripCardV2.js:16` wrapper (`flex-1 min-w-0 max-w-[560px]`). Confirmed with user (desktop wide, >1024px): `max-w-[560px]` itself was the bug — on wide viewports the card stretches far past 560px, so time/station content boxes into a 560px column on the left while the price block (`flex-shrink-0`) pins to the true far-right edge of the full card. User independently suggested removing the cap; confirmed via the trace and shipped: removed `max-w-[560px]`, kept the line-clamp/min-h change alongside (harmless, closes a real minor edge case). Branch `fix/trip-card-station-clamp-tilt` (reused from #305, not deleted) → `b767f11f` → merged `develop fe1f8594`.

**Part 2 — departure/arrival column width imbalance.** Same session, next message: user flagged the two station columns (e.g. "Hatyai Airport" vs "Koh Lipe Pattaya Beach") rendering at visibly different widths, asked for FE+Next.js agent analysis. Spawned `react-specialist` (read-only): confirmed `min-w-[64px]` on both columns (`TripCardV2.js:21,49`) is a floor not a fixed/equal width — with no `flex-1`/equal-basis, each column shrink-to-fits its own content in the parent flex row (only the middle arrow column had `flex-1`), so a short name renders a narrower column than a long one by construction. No existing "equal column" pattern found elsewhere in `components/trips/` to copy. Agent also clarified `line-clamp-2` was never the truncation risk feared — it only clamps past 2 lines, behaves as plain wrap for 1-2 line content, so kept as-is. Asked user to pick between two equal-width mechanisms (flexbox `basis-0 grow` vs CSS Grid `grid-cols-[1fr_auto_1fr]`) and clamp policy (keep vs remove) — user took both recommended defaults. Fix: `min-w-[64px]` → `flex-1 basis-0 min-w-0` on both station columns, three-way even split with the arrow column, `line-clamp-2` untouched. New branch `fix/trip-card-station-column-width` (properly branched off `develop` per policy, unlike part 1's branch reuse) → `4b7b2236` → merged `develop 8f09d413`.

**Both parts NOT yet visually confirmed in-browser** — no Chrome extension tool available either round this session (declined again). Both merges are code-verified (diff review, CSS mechanism traced) but not screenshot-verified.

**Workspace (#306):**
- frontend: `develop` → `8f09d413` (two merges this session: `fix/trip-card-station-clamp-tilt` → `b767f11f` → `fe1f8594`, then `fix/trip-card-station-column-width` → `4b7b2236` → `8f09d413`). Both branches left on remote, unmerged-cleanup candidates once visually confirmed.
- admin-dashboard, backend, content: untouched this session — unchanged from #305 end-state (identical to #304 state).

---

## Session #305 (2026-08-13)

**Achieved (#305) — Attempted a UI fix on smartenplus-frontend trip-result cards, fully reverted; documented as a post-mortem, no code shipped.** User flagged the from→to time-block section of `TripCardV2.js` (trip search results, e.g. `/trips/hatyai/koh-lipe`) as visually unorganized from a prod screenshot. Root cause independently confirmed by 3 specialist agent reviews (UX, visual design, code-quality): `line-clamp-2 sm:line-clamp-1` clamped departure/arrival station labels to a different line count depending on breakpoint and independently per column, so a long name wraps 2 lines while a short one wraps 1, tilting the row — a genuine, verified defect. Everything after that first fix was chasing knock-on whitespace complaints (gap after the dashed line, gap before the price block, price block position) through **five different fix locations** across two files (`TripCardV2.js` root, duration column, `TripItemLayoutV2.js` card root, header row wrapper, inner flex row) — most were reverted by the next user message because they moved something the user hadn't asked to move (price position, whole-card width) or reintroduced a defect a prior fix had just closed (removing the duration-column's own `max-w` cap, which had been added earlier in the same session specifically to stop the dashed line over-stretching). No browser tool was available all session (user had declined the Chrome extension install early on); compensated with self-authored static HTML mock artifacts that only ever validated my own assumptions, never the real render — every mock "looked right" and every one was later contradicted by the user's actual screenshot. Session ended with the user asking for a full revert + explicit accounting of what went wrong; `git restore` on the one modified file (`TripCardV2.js`) returned both files to clean `develop` state — nothing was ever committed, so the revert was trivial. Wrote a 6-point post-mortem directly to the user (available in conversation transcript, not duplicated to a vault doc since nothing shipped): (1) never verified visually before claiming success, (2) chased the symptom up the DOM tree instead of reading the full container chain first, (3) repeatedly proposed edits outside a scope the user had explicitly fenced off, (4) undid a guardrail added earlier in the same session without weighing the consequence, (5) got a repo-specific warning from a review agent (`SkeletonSection.js` hardcoded widths would desync if card dimensions changed) and then stopped tracking it, (6) told the user a broken screenshot "looks correct" — the most damaging error, since it asked them to trust an assessment made without the ability to see the actual result.

**Workspace (#305):**
- frontend: `fix/trip-card-station-clamp-tilt` branch exists (created off clean `develop`, still equal to it — zero commits, working tree clean after final revert). Real fix (the `line-clamp` uniformity bug) was never re-applied after the revert — branch is a no-op, safe to delete or reuse.
- admin-dashboard, backend, content: untouched this session — all unchanged from #304 end-state (see below).

---

## Session #304 (2026-08-10)

**Achieved (#304) — Root-caused + fixed the "Transport Composit dropdown only shows 10 items" bug reported by staff (admin-dashboard only; backend untouched).** User asked to check vault + review the live contract page (`/routemanagement/contracts/silaphat-hatyai-airport-to-koh-lipe-94`) where ops staff found the Transport Composit selector in the contract form capped at 10 options. Root cause (both sides confirmed): `TransportCompositViewSet` (`smartenplus-backend/operators/views.py:2835-2843`) uses `CustomPagination` (`page_size=10`, `max_page_size=100`) — correct, intentional DRF behavior, not a bug. The actual bug was in `admin-dashboard/components/forms/contract/TransportComposit.js:106` — its `fetchData` called `clientFetchDataFromApi(endpoint, 'GET', null, config)` with no `page_size` param and read only `responseData.results`, silently accepting page 1 of 10 and never asking for more. Considered disabling BE pagination entirely (`pagination_class = None`, precedent exists for pure lookup tables like VehicleType/VehicleClass/Country/Province/City) but ruled it out — discovered via Explore agent that `admin-dashboard/store/api/vehiclesApi.js` (`getVehicles`, powering the real paginated Vehicles management table at `pages/routemanagement/vehicles/index.js`) hits the same endpoint and depends on the `{results,count,next}` shape + working `page`/`page_size` params. Killing BE pagination would've silently broken that page. Fix: one-line, FE-only — pass `{ page_size: 100 }` to match BE's own `max_page_size` ceiling. Also wrote a BE regression test (`smartenplus-backend/operators/tests/test_transport_composit_pagination.py`, 3 tests, not committed — stays local) proving the pagination behavior the fix depends on (default caps at 10, `page_size=100` returns all rows, over-max clamps safely). **Process learning, not code:** committed the FE fix straight to `main` then fast-forward merged into `develop` without checking out a feature branch first — violated the vault's own **Git Branch Policy** (`vault-guardrails.md:24-29`, "MANDATORY (all repos), NEVER commit directly to main or develop"), which already existed but wasn't read this session because the session opened directly in the admin-dashboard project, not the vault, so the vault's session-init protocol never fired. User caught it, corrected an initial wrong instinct to duplicate the rule into AD's cross-session memory system (removed after user redirected — git policy belongs in the vault only, project-level memory is the wrong home for it). Left the already-pushed AD commit as-is; no rollback attempted, damage was cosmetic (clean ff-merge, no branch mess).

**Workspace (#304):**
- admin-dashboard: `main` **and** `develop` both → `cbb6199` (fix committed direct to `main`, ff-merged into `develop`, both pushed — see process-learning note above re: should have branched first).
- backend: unchanged, `main` `489c5c4`. New untracked/uncommitted file: `operators/tests/test_transport_composit_pagination.py` (regression test, deliberately not committed this session).
- frontend: unchanged, `main` `10e7d72d`.
- content: unchanged, `master` `3756e5b` (clean).

---

## Session #303 (2026-08-09)

**Achieved (#303) — Passenger update feature: admin-dashboard + backend + smartenplus-frontend, all merged to develop.** Booking-page passenger edit/add/remove — previously only reachable by opening a support ticket first. Backend (`smartenplus-backend`): extracted passenger mutation logic into shared `apply_passenger_edits()` used by both the ticket endpoint (`TicketViewSet.partial_update`) and a new booking-scoped path (`BookingItemUpdateViewSet`), so edits don't require a ticket. Fixed a crash where an empty `datofbirth` on an existing passenger attempted to write NULL into a NOT NULL column. Added `HistoricalRecords` to `BookingPassengerDetail` (no prior audit trail on passport/DOB/name edits) + migration `0049`. Added `passenger_count_changed` flag in the response so the frontend can warn when confirmed headcount drifts from paid headcount (no auto price/refund logic — deliberately manual). 11 new tests in `tickets/test_passenger_update.py`. Admin-dashboard: wired `UpdatePassenger.js` into the booking detail page (`disableStatusGate` prop, `bookingItemId` routing to the new endpoint), added Add-passenger button, per-row Remove action with `ConfirmDialog`, DataGrid column UX fixes (hid raw `id` column, native date picker for DOB, passport placeholder), Thai-language help page (`pages/bookings/passenger-update-help.js`), and fixed the bookings-list passenger-count badge (`BookingPassengerDetail.js` — was counting unconfirmed/cancelled passengers via `.length`, now filters by `.confirm`). smartenplus-frontend (customer-facing): fixed a real rendering bug where the "Canceled" badge on a cancelled passenger row was absolutely-positioned and overlapped the DOB text; converted the row to a fixed CSS Grid template (Name/DOB/Passport/Status) so columns stay aligned across rows regardless of passenger status; replaced `border-left` status indicator with `box-shadow` (border was shifting row content); fixed React key using array index instead of real passenger id; fixed DOB fallback silently rendering a fabricated "Jan 01, 2000" for passengers with no birthdate on file. Extensive live-tested iteration across ~15 turns (screenshots caught 3 real bugs the initial fixes missed). Live-caught bug: `HistoricalRecords` migration existed but was never applied to dev DB (test suite uses disposable SQLite, masked the gap) — migrated. All 3 repos: feature branch → commit → push → `--no-ff` merge into `develop` → push. Backend tested (11 passing tests + full suite run, 3 pre-existing unrelated failures confirmed on clean stash). Frontend verified live in-browser by user across multiple rounds, not just build/lint.

**Workspace (#303):**
- admin-dashboard: `develop` → `99c311b` (merge of `feat/booking-page-passenger-update`). `main` unchanged `9f131d6`.
- backend: `develop` → `489c5c4` (merge of `feat/booking-page-passenger-update`). `main` unchanged `0996a66`.
- frontend: `develop` → `10e7d72d` (merge of `fix/passenger-details-canceled-badge-layout`). `main` unchanged `bb06d910`.
- content: unchanged, `master` `3756e5b` (clean)

---

## Session #302 (2026-08-06)

**Achieved — Admin-dashboard: git-branch housekeeping only, no product code changed. PARTIAL — remote delete blocked.** User pasted 14 named branches + `chore/drop-contract-seat-api-url` from `admin-dashboard` (repo `smartenplus-dashboard`), asked to check + purge. Confirmed trunk: `main` and `develop` sit at the same commit `9f131d6` here (unlike backend's dead `master`), so checked merge against `origin/main`. All 15 merged. Noted repo has a duplicate remote setup — `main` and `origin` git remotes both point to the same GitHub URL. Sync check vs `origin`: 11 in sync, 4 remote-already-gone (`feat/mapping-dialog-supabase`, `feat/seat-check-operator`, `feat/transfer-zone-admin`, `fix/transfer-zones-gate-transport-private-charter`). Deleted all 15 local (`git branch -d`, clean — all merged). **`git push origin --delete` for the 11 remote branches was blocked by the auto-mode permission classifier** (cwd was `admin-dashboard`, not pre-authorized like the backend repo in the prior session) — reported the blocker + exact command to the user, did not retry or attempt a workaround. User ended session before re-running or approving it. **Remote-side, all 11 branches are still live on GitHub** — only local cleanup landed.

**Workspace (#302):**
- admin-dashboard: local branch list pruned (15 → 0), but `origin` still has the 11 that were meant to go — **not actually clean yet**. `main`/`develop` unchanged at `9f131d6`.
- backend: unchanged, `main`/`develop` `0996a66` per #301
- frontend: unchanged, still `develop`/`main` `bb06d910` per #300
- content: unchanged, `master` `3756e5b` (clean)

---

## Session #301 (2026-08-06)

**Achieved — Backend: git-branch housekeeping only, no product code changed.** User pasted a list of 19 named branches + `chore/drop-contract-seat-api-url` from `smartenplus-backend` and asked to check + report purge candidates. Confirmed `master` is a dead ref (frozen since Dec 2022, 959 commits behind `develop`) — real trunk is `develop`. Ran `git branch --merged origin/develop` — all 20 branches merged. Checked each against `origin/*` for sync/divergence: 16 in sync (local==remote SHA), 4 remote-already-gone (`feat/airport-transfer-zone-pricing`, `feat/mapping-dialog-supabase`, `feat/seat-check-operator`, `fix/airport-transfer-from-price-flag`). Reported findings, user said "go." Deleted all 20 local (`git branch -d`, safe — refuses on unmerged, none hit that) + 16 remote (`git push origin --delete`). Verified final `git branch -a`: only `main`/`develop`/`master` + unrelated in-flight branches (`chore/remove-cs-debug-logs`, `feat/admin-ota-ticket-create`, various `feat/chat-*`/`feat/cs-*`/`feat/ota-*`/`fix/*` not in the purge list) remain. Repo now clean of the 20 stale branches.

**Workspace (#301):**
- backend: `main`/`develop` unchanged at `0996a66` (branch list pruned only — 20 stale branches → 0)
- frontend: unchanged, still `develop`/`main` `bb06d910` per #300
- admin-dashboard: unchanged, still `main` `9f131d6` per #297
- content: unchanged, `master` `3756e5b` (clean)

---

## Session #300 (2026-08-06)

**Achieved — Frontend: git-branch housekeeping only, no product code changed.** User pasted a list of 30 stray local branches from `smartenplus-frontend` (feature/fix branches from the airport-transfer work + misc fixes) and asked to check + purge. Ran `git branch --merged develop` — 29 of 30 already merged, safe delete; kept 1 (`fix/remove-trip-listing-airport-transfer`) since it showed unmerged. Deleted the 29: local `git branch -d` for all, plus `git push origin --delete` for the 25 that had a remote (4 were local-only: `feat/airport-transfer-zone-picker`, `feat/dashboard-redesign`, `fix/booking-notifications-direction`, `fix/style-consistency-airport-transfer`). Verified `develop`/`main` untouched at `bb06d910` throughout. User then asked to double-check the held-back branch rather than assume it was junk — inspected its single commit `46a713b1` (removes `TripListingSection`/`MobileFilterDialog` from `pages/airport-transfer/[slug].js` + `AirportTransferHeader.js`, 157 lines, real diff, not empty). Found it was **not novel work**: a sibling commit `df6b6e93` (from the already-merged-and-purged `fix/style-consistency-airport-transfer`) does the identical removal plus additional token/style cleanup — confirmed `46a713b1` is NOT an ancestor of `df6b6e93` via `git merge-base --is-ancestor` (independent duplicate, not a predecessor), and confirmed current `develop` already has zero references to either removed component via grep. Force-deleted (`git branch -D`, local-only, no remote) since content was fully superseded. Also: user asked to stop a stray `npm run dev` — killed both PIDs on port 3000. All work was read-only git inspection + branch deletion; no plan-mode code edits were needed or made.

**Workspace (#300):**
- frontend: `develop`/`main` unchanged at `bb06d910` (branch list pruned only — 30 stray branches → 0; repo now clean: just `main`+`develop` locally)
- backend: unchanged, still `main` `0996a66` per #297
- admin-dashboard: unchanged, still `main` `9f131d6` per #297
- content: unchanged, `master` `3756e5b` (clean)

---

## Session #299 (2026-08-06)

**Achieved — Frontend: shipped Airport Transfer as a 3rd homepage/dialog search tab, end-to-end, through 2 build passes + a 3-agent UX debate, all merged → develop.** Pass 1: built the tab from scratch (`feat/airport-transfer-search-tab`) — new `getAirportStations` RTK query (`tripsApi.js`, path/filter copied from 3 existing precedents), new `AirportTransferSearch.js` component, wired into `SearchModeTabs.js`/`TabbedSearchPanel.js`. Reviewed by a 3-agent team (ui-component-engineer, nextjs-fullstack-architect, code-reviewer) which caught 2 real bugs before merge: RTK query used `limit` instead of the backend's actual `page_size` pagination param (DRF silently drops unknown params, was truncating to 10 airports), and missing `isError` handling — both fixed. Merged → develop `334d1f2e`. User then screenshotted the live picker and questioned the native `<select>` UI + spotted demo/test stations (`[DEMO] Phuket Hotel Zone`, `Demo Phuket Airport`) leaking into the customer-facing list alongside real ones. Backend read-only research confirmed the leak as real: `Station` model has no `is_demo`/`is_active` flag, `seed_demo_destination.py` (the `[DEMO]`-prefix seeder) has zero environment guard, nothing stops it hitting a shared/prod DB. Spawned a 3-agent debate (ux-research-specialist, ui-component-engineer, design-review) on picker pattern + the leak — unanimous verdict: replace `<select>` with a chip row (small closed set favors tap-to-select over typeahead; reject reusing `AutoCompleteSearch.js`, wrong tool — Redux-coupled, built for live search over thousands of open-ended stations) + client-side regex filter as a stop-gap for the demo rows. Verdict + full reasoning written to vault (`03-knowledge/airport-picker-ux-pattern-and-demo-data-leak.md`). Implemented and merged (`83200ba7`). User then pushed back again: chip row breaks past ~8 airports (horizontal scroll hunt) and asked specifically for typing — clarified this wasn't a contradiction of the debate (which rejected the *heavy* `AutoCompleteSearch.js` modal, not typing itself); built a **client-side type-to-filter combobox** instead — plain controlled `<input>` + local suggestion dropdown filtering the already-loaded `airportOptions` array in memory, no RTK-per-keystroke, no Redux (`be65255d`). Same pass fixed a real mobile bug user screenshotted: 3 tab labels at `gap-6` overflowed narrow viewports, clipping "Airport Transfer" off-screen — made `SearchModeTabs.js` horizontally scrollable, same `overflow-x-auto scrollbar-hide` idiom `ExperiencesSearch.js` already used (`8496bc91`). Merged → develop `334d1f2e`→`bb06d910` chain. One more user-reported bug (screenshot: typed text but no dropdown appeared) fixed by force-reopening the suggestion list on every keystroke, not just on focus (`c373f29c`) — note: this fix was first committed directly to `develop` by mistake (violates repo's mandatory branch policy), caught before push, corrected via `git reset --soft` + redone on `fix/airport-search-dropdown-reopen` → merged `bb06d910`. Fix is a plausible-not-confirmed diagnosis (no browser tool access this session to verify live) — flagged to user as such, they accepted shipping it for their own retest. Diagram artifact published mid-session comparing chip-vs-combobox mechanics and the combobox-vs-AutoCompleteSearch distinction (not persisted here, ephemeral aid for the plan-approval step).

**Workspace (#299):**
- frontend: `develop` `bb06d910` (pushed origin, clean) — 6 commits this session across 2 feature/fix branches, all merged
- backend: unchanged this session, still `main` `0996a66` per #297
- admin-dashboard: unchanged this session, still `main` `9f131d6` per #297
- content: unchanged, `master` `3756e5b` (clean)

---

## Session #298 (2026-08-06)

**Achieved — Frontend-only, no code repo change beyond docs: reviewed a user-pasted "AI Cost-Optimized Development Workflow" policy doc via a 2-agent debate (cost-advocate vs quality-advocate), synthesized a verdict, applied the one real change to `smartenplus-frontend/CLAUDE.md`.** Vault check first (per `CLAUDE.md` protocol) — no existing vault note on model-tiering/cost policy, so no duplication risk. Spawned 2 general-purpose agents in parallel, each reading the full policy doc + the repo's `CLAUDE.md`: cost-advocate argued for adopting the doc's model-tiering/plan-first/parallel/context rules; quality-advocate argued most of it either duplicates existing AGENT POLICY rules (Explore-agent 739k-token cost gate, Context Discipline no-paste-echo, Team Spawn 4-axes gate, Core Constraints) or doesn't map onto Claude Code's actual controls — the main session model is user-set via `/model`, not chosen per-subtask by the assistant, so "always use lowest-capability model" is false as a literal rule. Both sides converged: the only real, unused lever is the `Agent` tool's `model` param. Verdict — reject the doc's model-tiering table as written; do not touch CRITICAL GOTCHAS-covered areas (payment state machine, SEO canonical, checkout SSR, cart/auth) with any capability-downgrade logic, since those already carry a quality floor the doc doesn't account for; adopt one narrow addition. Applied: 2-line addition to `CLAUDE.md`'s "Subagent Routing" section — "Model routing: when Explore is justified and the task is pure lookup (find/read/summarize, no judgment), pass `model: \"haiku\"` to the Agent call. Keep default model for anything requiring judgment (review, design, payment/security-sensitive code)." Committed on new branch `docs/agent-model-routing-tier` (commit `020ef740`) per repo's mandatory branch policy, pushed to origin, merged → develop `bfad79ff` (confirmed merged by session #299, was miscarried as still-open in this block originally).

---

## Session #297 (2026-08-06)

**Achieved — Frontend-only session: traced "update GMAP key for GH Actions scan" to two separate real bugs, fixed both, merged to develop.** (1) Investigated why GitHub was flagging `NEXT_PUBLIC_APP_GMAP_API_KEY` — `deploy.yml` itself was clean (correctly sourced from `secrets.NEXT_PUBLIC_APP_GMAP_API_KEY`), but `.env.local.docker` was **tracked in git HEAD** since commit `817f03fd` (2025-12-05, 8 months exposed), holding 5 real secrets in plaintext: `NEXT_PUBLIC_APP_GMAP_API_KEY`, `NEXTAUTH_SECRET`, `GOOGLE_CLIENT_SECRET`, `FACEBOOK_CLIENT_SECRET`, `LINE_CHANNEL_SECRET`. `.gitignore`'s `.env*.local` pattern didn't match `.env.local.docker` (doesn't end in `.local`) — the gap that let it get committed. Vault (`adr-airport-transfer-zone-pricing.md`) confirmed the GMAP key was always meant to be client-side/domain-restricted by design, so browser exposure wasn't the bug — the bug was the key (and 3 unrelated OAuth secrets) sitting in a publicly-readable tracked file. Fixed: `git rm --cached .env.local.docker` + added explicit `.env.local.docker` line to `.gitignore` (branch `fix/untrack-env-local-docker-secrets` → develop `adfa81ca`). User confirmed local dev uses `npm run dev` (reads plain `.env.local`, unaffected) not `docker-compose` — so the untracked file, already deleted off disk too, has zero impact on local workflow; the file only ever mattered for a now-unused local Docker Compose path (prod uses a separate `docker-compose.prod.yml` + `.env.deploy` generated server-side from GH Secrets at deploy time, untouched by this fix). History purge (git filter-repo/BFG) explicitly declined by user — rotation neutralizes risk without rewriting history; old commits keep dead values. (2) User later pasted a prod console log showing Google Maps JS blocked by CSP (`script-src` directive) on `/airport-transfer` — unrelated to the secret work, a pure allowlist gap: `nginx/sites-available/smartenplus.conf:158`'s live CSP `script-src` never listed `maps.googleapis.com` (img/connect/font directives already covered `*.googleapis.com` broadly, only script-src was missing it). One-line fix, branch `fix/csp-allow-google-maps` → develop `29ece50a`. Both fixes on `develop`; confirmed `main`==`develop` HEAD in this repo (not the 3-branch model docs describe, but consistent with observed state). **Still open:** actual secret rotation (Google Cloud Console, Facebook Dev, LINE Developers, GitHub repo Secrets) is console-side, cannot be scripted — user has not yet rotated, confirmed by the CSP console log still showing the old key `AIzaSyCN-ezFHp4Of7l...` live in prod. Also open: whether nginx config changes reach the VPS automatically (deploy script only handles the frontend Docker image per current understanding) — user hasn't confirmed the nginx-reload mechanism, so the CSP fix may not be live on the actual server yet despite being merged to develop.

---

## Session #296 (2026-08-05)

**Achieved — Trip-level station override (per-trip `departure_station`/`arrival_station` FK, falling back to route's default via `effective_*_station`) wasn't reaching several surfaces — traced and fixed across all 3 repos.** Started from a simple AD question: editing a trip at `/routemanagement/trips` showed the Route input blank in prod (worked in dev). Root cause: the Route/Station Autocomplete's displayed `value` was looked up via `.find()` inside a **paginated 50-row options list** — if the trip's actual route/station fell outside that page (prod-only, since dev's smaller table always fit page 1), the field silently rendered blank even though the underlying Formik value was correct. Fixed by fetching the selected route/station by id and merging it into the options list via one small reusable `withSelected()` helper (admin-dashboard `components/trips/tripEdit.js`). Follow-up: departure/arrival station Autocompletes appeared "locked together" — both shared one `stationSearch` state, so typing in one refetched the shared options list backing both; split into independent `depStationSearch`/`arrStationSearch`. Follow-up: trips table's Departure/Arrival Station columns always showed the **route's default** station, never the trip-level override (`store/api/tripsApi.js` transform hardcoded `trip.route.departure_station` instead of reading the backend's already-correct `departure_station_name`/`arrival_station_name` fields) — fixed to prefer those, added a 📍 tooltip marking overridden rows for staff. From there, user asked the deeper question — how far does an override actually propagate? Audited every booking notification/display surface and found the override was **silently dropped** almost everywhere except the live checkout/cart serializers: (1) `carts/utils.py` — the permanent `BookingItem.departure_station`/`arrival_station` CharField snapshot (write-once at checkout) read `route.departure_station` directly, skipping `trip.effective_departure_station` — this one write path feeds every booking-confirmation email, order-confirmation email, review-invitation email, the ops n8n webhook, and admin resend actions, so fixing it fixed all of them at once; (2) `bookings/serializers.py` admin dashboard booking summary — same bug, separate live-query code path; (3) `orders/serializers.py` `get_trip()` on both `BookingItemSerializer` and `BookingItemSendingSerializer` — customer-facing order-detail API (`OrderDetailsViewSet`, `AllowAny`), built route data via a plain `RouteSerializer` every request, confirmed live-consumed by frontend `OrderDetail.js`; (4) `products/views.py` `HomeViewSet.custom_route` (the `/trips/[dep]/[arr]` SEO landing page's backend) only matched the **route's** station, never the trip-level override FK, so an operator's override station was unfindable by its own slug — extended to also match `Contract.trip__departure_station`/`arrival_station`, plus the Station's own `normalized_station_name` field directly (not only through the nullable `Station.location_name` FK) for resilience, mirroring the already-correct pattern in the separate `FindTripViewSet.fetch_trips` (the actual endpoint backing live search, registered at `/api/v1/trips/{from}/{to}/` — took real debugging to find this was a *third*, distinct endpoint from the two already checked). Hit two non-code blockers while live-testing the SEO page fix: a test station named `"[DEMO] Phuket Airport"` had brackets that survived normalization (`normalize_location` only strips hyphens/spaces) and broke every `icontains` substring match against the bracket-free URL slug — renamed via Django shell (`Station.save()`, not a raw DB write) to `"Demo Phuket Airport"`; and `FindTripViewSet.list()`'s 15-minute Redis cache had memoized the pre-rename **empty** result under the exact query key, so even after the code fix + rename, retests kept serving stale `[]` until the specific cache key was manually cleared. Frontend: `pages/trips/[...slug].js` was discarding `contracts` entirely whenever the Route-based SEO/blog content (`routes[]`) was empty (correct for an override station, since no `RouteByLocationInfo` row exists for it) — decoupled so only the blog/FAQ fetch is skipped, contracts render independently. Also found `OrderBookingCard`/`OrderDetail.js` never actually displayed station data at all for regular (non-zone-transfer) transport bookings — only ever showed `route_name` — added a station-pair fallback (`departure_station to arrival_station`) ahead of the route-name fallback, reusing data already made correct by the `orders/serializers.py` fix. Last: added a `📍 Station:` line to the Telegram "New Booking Notification" (`bookings/tasks.py`), which had never printed station text at all — the data existed in `orders/services.py`'s `context` dict but was never copied into the smaller `context_message` dict actually sent to the Telegram task; added the two missing keys and the message line. **Tested live end-to-end** for booking `OSG6305868`: built the real `context_message` from the DB and called `send_booking_data_by_telegram` synchronously (not `.delay()`, so failures surface immediately) against a Telegram test group (`sep-test-group`, not prod ops) — confirmed message text `📍 Station: phuket bus station → Demo Phuket Airport`. Plan mode used throughout (re-entered ~8 times as new findings emerged mid-session); user pushed back once on an early plan for being over-engineered (3 near-duplicate merge blocks) — collapsed to one reusable `withSelected()` helper, confirmed as the right call. All 3 repos: admin-dashboard committed+pushed directly to `develop` (`9f131d6`); frontend committed+pushed directly to `develop` (`f3af2f81`); backend — new branch `fix/trip-station-override-notifications` off `main` (repo was checked out on `main`, not `develop`, at session start) → committed (`834b848`) → pushed → merged into `develop` (`0996a66`) → pushed. Backend feature branch kept (not deleted) per user request.

---

## Session #295 (2026-08-05)

**Achieved — Backend: root-caused + fixed the airport-transfer booking-confirmation email (zone-transfer bookings showed time as "—", From/To mismatched the hero line, passenger count was an unlabeled "1A"), resent the dev-test booking, merged to develop.** User forwarded a broken confirmation email for dev-test booking `WET4806711` (deliberately messy test input on a Hatyai↔George Town zone-price contract) and asked why — first suspected a regression of the prior session's `has_range` From/To fix, but `git show` on both commits (`a5c2ce3f`, `cefa9cdd`) confirmed those touched only the pre-checkout search-results price widget, never the email path; unrelated. Traced the real cause via direct file reads (backend `orders/services.py`, `carts/utils.py`, `bookings/emails/booking_confirmation_template.html`) cross-checked against an Explore-agent pass that landed on the same files independently. Root cause: zone/airport-transfer bookings have no `Contract.trip` (pickup time is customer-chosen at checkout, not a fixed schedule), so the email's time slot — which only ever read `booking.contract_departure_time`/`departure_time` from `Contract.trip` — was structurally always `None`, always rendering "—". A *prior* fix session (commit `d32bd18`, the day before) had already patched the **station** half of this same From/To block to fall back to `pickup_info`/`dropoff_info` when direction-branched, but never touched the **time** span — same fix pattern, half-applied, which is why the user's "we tried to fix this before" was right but the fix didn't fully land. Also found the hero line ("You're all set for X to Y") was built from the direction-agnostic `route_name` (fixed `Route` model field), so it could disagree with the direction-aware From/To timeline below it. User clarified mid-investigation that the visible garbled text ("eewew", "eee", pickup-time-after-dropoff-time) was intentional messy test input for this dev contract, not a real bug — descoped a planned checkout-validation fix accordingly, keeping only the two real template/backend defects. Fix: (1) `booking_confirmation_template.html` — time spans now fall back to `pickup_info.pickup_time`/`dropoff_info.dropoff_time` mirroring the station fallback already there; hero line rebuilt from resolved pickup/dropoff per direction instead of `route_name` for zone bookings. (2) `bookings/admin.py` `build_booking_context()` (the function backing the admin "resend confirmation email" action) was found to never set `booking.direction` at all — meaning even with the template fixed, admin-triggered resends would always hit the blank-direction fallback branch and still look broken; added the missing field from `InfoFields.direction`. Verified by rendering the real template against `WET4806711`'s live context (not a mock) — confirmed hero and timeline now agree, To time went from "—" to "09:00". Verified non-zone (fixed-route, `direction=''`) bookings are unaffected via a second real booking render. Resent the email live via SES through the admin action's underlying task (had to clear 3 stale `UserJourneyEvent` idempotency-guard rows for this one test booking — dev data only, no other booking touched). User then separately flagged the passenger count "1A" as cryptic; fixed same session to spell out "1 Adult" / "2 Adults, 1 Child" etc. via Django's `pluralize` filter, verified against 5 count combinations, resent again. Committed (`e606724`), pushed `fix/airport-transfer-email-time-direction`, merged → backend develop `6f9bfaa`, pushed. Plan mode used throughout investigation (Explore agent + direct file reads before any edit); an HTML before/after mockup artifact was also produced mid-investigation (before the real direction value was confirmed, so its Pickup/Dropoff assignment was illustrative, not DB-verified — superseded by the actual fix): https://claude.ai/code/artifact/591bd25f-1a1d-4db3-b4b5-25d0b37eed43

**Workspace (#295):**
- frontend: `develop` `a5c2ce3f` (clean)
- backend: `develop` `6f9bfaa` (pushed origin)
- admin-dashboard: `develop` `45cbb85` (clean)
- content: `master` `3756e5b` (clean)

---

## Session #294 (2026-08-05)

**Achieved — Backend: fixed date-specific ratecard priority bug across 4 sites + honest "from" price label on airport-transfer cards, merged to develop (both repos).** User asked why airport-transfer vehicle cards always show "from THB X" even for contracts with only one price ever — traced to `has_range` (added this session) being computed against a per-date `Contract_RateCard` queryset built with `Q(rate_date=date) | Q(rate_date__isnull=True)` (OR). User caught the deeper issue: submitting a specific date should resolve to exactly ONE applicable rate, but the OR-filter fetches both the date-specific override row AND the NULL base-rate row when both exist, then takes `Min()`/`min()` across them — silently picking whichever is *cheaper*, not the correct date-specific one (e.g. a NULL base rate at 5,000 wrongly wins over an intended holiday-surge override at 8,000). Confirmed via `Contract_RateCard.Meta.unique_together = ['contract','ratecard','rate_date']` that at most one NULL row and one date-specific row can exist per (contract, ratecard) — "prefer date-specific, else NULL" is deterministic, no ambiguity. Same bug pattern found in 4 places total via repo-wide grep (`stations/views.py` resolve-zone + `products/views.py` ×3: `_get_display_rate` helper, trip-search loop, fare-calendar loop) — pre-existing, not introduced this session. Fix: new shared `operators/rate_resolution.py` with `resolve_ratecards_for_date()` (date-specific wins outright, NULL fallback only when no override exists for that date — returns a queryset so each site keeps its own aggregation style/type-filtering/positivity-check quirks intact) and `contract_has_date_range()` (redefines `has_range` as "does this contract have 2+ date-specific override rows *anywhere on the calendar*", independent of the single date being queried — since post-fix the resolved-for-date queryset always collapses to 1 row, the old `count()>1` logic would've always been `False`). All 4 call sites updated to use the shared resolver, preserving every existing per-site inconsistency (site 1 has no type filtering, sites 2-4 do; positivity-check style differs slightly; `_is_contract_bookable` gate at site 4 untouched). Added 5 new resolver unit tests + 2 regression tests (date-specific price wins over cheaper NULL) + 1 new `has_range` semantics test proving the calendar-wide-variance definition (1 override → False; 2nd override on a different date → True, even though the resolved price for the queried date is still exactly 1 row). Built as two branches (`fix/airport-transfer-from-price-flag` for `has_range`, `fix/ratecard-date-priority` for the resolver) then merged together by hand-resolving the expected `stations/views.py` conflict to the combined form. `python manage.py check` clean; 121/122 backend tests pass (1 pre-existing unrelated failure, confirmed via `git stash` on develop before this session's changes). Frontend consumer (`ZoneOptionCard.js`/`ZonePriceBox.js`) renders `hasRange===false ? price : "from "+price`, missing/undefined field falls back to "from" for old cached responses. Both branches pushed + fast-forward merged → develop in backend (`38c0470→53506e9`) and frontend (`a1fd3cca→a5c2ce3f`), both pushed to origin. Also produced a diagram artifact tracing the full options-list render mechanism (address pick → resolve-zone API → per-card contract fetch → BookButton) for reference: https://claude.ai/code/artifact/47ba1a2d-6215-4196-bfdb-ee70db9d2762

**Workspace (#294):**
- frontend: `develop` `a5c2ce3f` (pushed origin)
- backend: `develop` `53506e9` (pushed origin)
- admin-dashboard: `develop` `45cbb85` (clean)
- content: `master` `3756e5b` (clean)

---

## Session #293 (2026-08-04)

**Achieved — Frontend: redesigned Booking Items card layout for airport transfer (guest-order + booking detail), plus fixed an unrelated CartButton crash it uncovered.** User flagged `/guest-order/[orderId]` "Booking Items" card as ugly for airport-transfer bookings — route text (e.g. "Hatyai Airport (HDY) to Lee Gardens Plaza Hotel Hat Yai, ถนน ประชาธิปัตย์…") collided with the "Airport Transfer" badge on desktop, and wrapped character-by-character on mobile with the badge clipped off-edge. Explored+confirmed root cause directly in `OrderBookingCard.js` (`components/order/`) and the near-duplicate `BookingItemCard.js` (`components/bookings/`) — both had the route row as a single `flex justify-between items-center` div with an unbounded text `<div>` (no `min-w-0`/wrap control) sitting directly beside the badge, so flexbox couldn't shrink the text and the badge got squeezed/pushed. Fixed both: row → `flex flex-wrap`, route text → `min-w-0 flex-1 basis-full sm:basis-0 break-words` (full-width on mobile so badge always drops to its own line; inlines on ≥sm when it fits), badge+direction-label → separate `flex-shrink-0 ml-auto` group. Also fixed `duration (0 hr)` noise — `duration` is a truthy `"00:00:00"` time string, not a number, so the old `duration && …` guard never caught the zero case; added a `hasDuration` check that parses hours/minutes. First fix pass (min-w-0/break-words alone) fixed desktop but NOT mobile — root cause was `flex-1`'s default `flex-basis:0%` letting the badge share the first line before wrap kicked in; `basis-full sm:basis-0` was the actual fix, confirmed via a Playwright DOM-width probe (text div went from a squeezed width to full 275px row width, badge cleanly dropped below). While live-verifying via Playwright screenshots at 375/768/1200px, hit an unrelated pre-existing crash blocking the whole guest-order page in dev: `CartButton.js:41` called `refetch()` on a RTK Query query that `useCheckCartIdQuery` skips when `cartId` is null (guest sessions on `/guest-order/*` have none) → "Cannot refetch a query that has not been started yet." Confirmed present on unmodified `develop` too (not caused by this session's edit) — got user go-ahead before touching it, fixed with a one-line `cartId` guard on the `refetch()` call. All three files lint-clean; verified live via Playwright screenshots + user's own phone screenshot confirming the fix. Committed + pushed `fix/airport-transfer-card-layout`, merged → frontend `develop` `a1fd3cca`, pushed.

**Workspace (#293):**
- frontend: `develop` `a1fd3cca` (pushed origin)
- backend: `develop` `38c0470` (clean)
- admin-dashboard: `develop` `45cbb85` (clean)
- content: `master` `3756e5b` (clean)

---

## Session #292 (2026-08-04)

**Achieved — Frontend: airport-transfer From/To widget rebalance + tablet layout + row-height match.** User flagged `/airport-transfer/hatyai-airport` "Private transfer — fixed price" From/To widget (`ZonePriceBox.js`) as visually imbalanced — screenshot showed a compact static airport pill vs. a longer focus-highlighted address autocomplete input, plus a swap button stretched full-height via `items-stretch`/`w-11` into a tall thin sliver, and icon asymmetry (plane icon only on the airport row). Root cause confirmed by reading `ZonePriceBox.js`/`PlacePicker.js` directly; fix reused the exact sitewide swap-control pattern already proven in `components/search/TransportationSearch.js` (circular 40×40 `IconButton` badge on the row seam, `SwapVertOutlinedIcon`/`SwapHorizOutlinedIcon`, `FmdGoodOutlinedIcon` for the destination-icon convention) rather than inventing new treatment. Three incremental passes, each verified live via the `design-review` agent (Playwright) before moving on: **(1)** rebalanced rows — added an optional `icon` prop to `PlacePicker` (backward-compatible, single caller confirmed via grep), matched `AirportEndPill`'s icon chrome to it, replaced the stretched rectangle swap button with a 40×40 circular badge on the seam; **(2)** added `md:`+ (tablet/desktop) horizontal side-by-side layout matching the homepage search form's `flex-col md:flex-row` responsive pattern (`TransportationSearch.js:138`) — kept mobile stacked, added a second breakpoint-scoped swap button (`SwapHorizOutlinedIcon`, centered in the gap between `md:w-1/2` rows) since icon+position differ between stacked/horizontal; extracted a small `SwapButton` sub-component to de-duplicate the two `IconButton` instances; **(3)** user reported row height still didn't match the homepage search form despite the redesign — root cause was `py-2`/no `min-h` vs. the reference's `min-h-[44px] py-3` — one-line fix per spot (`AirportEndPill`, both `PlacePicker` input variants). All three passes lint-clean, verified live at 375/768/1024/1280px (stacked↔horizontal swap, autocomplete dropdown unclipped, icons vertically centered, no console errors, no layout jump on swap-click). Committed + pushed `fix/airport-transfer-fromto-balance`, merged → frontend `develop` `cfb3872d`, pushed.

**Workspace (#292):**
- frontend: `develop` `cfb3872d` (pushed origin)
- backend: `develop` `38c0470` (clean)
- admin-dashboard: `develop` `45cbb85` (clean)
- content: `master` `3756e5b` (clean)

---

## Session #291 (2026-08-04)

**Achieved — Frontend: airport-transfer fare-card vehicle icon + operator identity.** User flagged `/airport-transfer/hatyai-airport` "Private transfer — fixed price" fare list: every option (van/suv/sedan/demo) rendered the same generic MUI `AirportShuttleOutlinedIcon`, no visual distinction between vehicle types, and no operator info surfaced pre-booking. Explored `ZoneOptionCard.js` (the actual fare-card component under `ZonePriceBox.js`) + its data source (`useCheckContractQuery` → `Contract`/`ContractSerializer`, which already includes `operator.operator_name`/`operator.image` — unread by the component). Researched real-world consolidator platforms (Klook, Kiwitaxi, Suntransfers, Booking.com Airport Taxis — same fixed-price model as SmartEnPlus): they use one generic icon per vehicle *class*, not real photos, and initially hide operator identity pre-booking (bidding marketplaces like GetTransfer are the exception). First pass (per that norm) added only vehicle-class icons — reused existing `helpers/transportMode.js` → `TransportMode(vehicleName)`, which already string-matches `"van standard"/"suv standard"/"sedan standard"` (from `contract.transport_composit[0].transport_composit`) to existing SVG icon components (`VanIcon`/`SuvIcon`/`CarIcon`), with graceful fallback to the original MUI icon on no match (e.g. the seeded `[DEMO] Airport Private Transfer` contract). User then reconsidered — no real vehicle/operator photos exist in the app at all, and wanted the customer to know who services the transfer before booking — so added operator name + logo too, reusing the same field pattern already proven in `TripItemOperatorInfo.js` (`contract?.operator?.operator_name || 'smartenplus'`, `contract?.operator?.image || smartenplusIcon`), rendered as a small 16px logo + gray text line directly under the vehicle name, no new API call (data was already in the existing `checkContract` fetch). Domains for `next/image` already whitelisted in `next.config.js` (same ones `TripItem.js` uses). Lint clean. Committed + pushed `fix/airport-transfer-vehicle-icons`, merged → frontend `develop` `4bd5f1ef`, pushed.

**Workspace (#291):**
- frontend: `develop` `4bd5f1ef` (pushed origin)
- backend: `develop` `38c0470` (clean)
- admin-dashboard: `develop` `45cbb85` (clean)
- content: `master` `3756e5b` (clean)

---

## Session #290 (2026-08-04)

**Achieved — Admin-dashboard: transfer-zone workflow audit + gate/nudge fix.** Ran a 3-agent read-only audit (UXUI + BD + SWE) of the full airport-transfer zone-price→contract→booking admin workflow, sourced from existing vault research (`adr-airport-transfer-zone-pricing.md`, `airport-transfer-rate-dynamic-pricing.md`, `checkout-zone-transfer-card-spec.md`) plus live reads of `components/transfer-zones/*` and `components/contracts/TransferZonesSection.js`. All three agents independently converged on the same top risk: the PRIVATE/CHARTER-only zone-linking gate (JOIN contracts must never link — they price per-seat with no pax selector in the traveler widget, so linking one would silently under-charge groups) was enforced by two different mechanisms depending on screen — a hard server-side query filter on the zone form, but on the contract form (`TransferZonesSection.js`) protection came *only* from the caller's render-gate condition in `ContractFormFields.js`, with zero internal awareness in the component itself. Also flagged: `TestLocationPanel` (address→price verification tool) is fully optional — a zone can Save and go live (`is_active:true` default) without ever being tested against a real address. Implemented both fixes, scoped deliberately small per explicit "no tech debt / no over-engineering / reuse / no side effects" instruction: (1) `TransferZonesSection` now accepts a `contractType` prop and self-guards (`if (contractType && !['PRIVATE','CHARTER'].includes(contractType)) return null`) — mirrors the file's existing `if (!contractId) return null` idiom, omitted prop = old behavior, zero side effect on the one existing caller; `ContractFormFields.js` now threads `contractType={formik.values.type?.value}` the same way it already threads a `contractType` prop to a sibling component one line below (established pattern, not new). (2) `ZoneForm.js` shows a passive warning caption ("Not yet tested against a real address…") when a polygon is drawn but `testMarker` (existing state, already set by `TestLocationPanel`'s `onResolved`) is still null — informational only, no Yup/Formik error key, never blocks Save (rejected a hard block deliberately — punishes legitimate no-test edits like a priority bump on an already-verified zone). Explicitly rejected as out-of-scope for this pass: overlap/priority-tie detection UI, delete-impact preview, unified save button across zone+contract forms, repo-wide `transformResponse` convention retrofit — all real findings, each a separate larger-scope change. Lint clean on all 3 touched files. Committed + pushed directly to admin-dashboard `develop` (`45cbb85`) — already on develop, no separate branch/merge needed.

**Workspace (#290):**
- frontend: `develop` `8c2b5c33` (clean)
- backend: `develop` `38c0470` (clean)
- admin-dashboard: `develop` `45cbb85` (pushed origin)
- content: `master` `3756e5b` (clean)

---

## Session #289 (2026-08-04)

**Achieved — Admin-dashboard: booking detail table text-overflow fix.** User flagged screenshot of `/bookings/PPF3522223` — Pickup/Dropoff Point and other long values were cut off at the viewport edge instead of wrapping. Root cause: `components/booking/BookingDetails.js:29` wrapped the whole two-column layout in a div with Tailwind `whitespace-nowrap`, which cascaded (CSS `white-space` is inherited) into every `TableCell` in the desktop `BookingInfoDetails.js` table; combined with `TableContainer`'s `overflow: 'hidden'`, long text simply clipped. Only the Remark row had a local `whitespace-normal break-words` override, proving the intended pattern was never applied elsewhere. Fix: removed the stray `whitespace-nowrap` from the ancestor div, and added `sx={{ whiteSpace: 'normal', wordBreak: 'break-word' }}` to all desktop-table value cells (Operator, Contract Id, Type, Travel Mode, dates, Route, stations, flight info, Pickup/Dropoff Point/Time) for belt-and-suspenders wrapping on unbroken long strings. Mobile card layout was already unaffected (had its own `wordBreak: 'break-word'`). Committed + pushed directly to admin-dashboard `develop` (`cb9df45`) — no PR/merge needed since branch was already develop.

**Workspace (#289):**
- frontend: `develop` `8c2b5c33` (clean)
- backend: `develop` `38c0470` (clean)
- admin-dashboard: `develop` `cb9df45` (pushed origin)
- content: `master` `3756e5b` (clean)

---

## Session #288 (2026-08-04)

**Achieved — Admin-dashboard: airport-transfer coords + booking type badge on booking detail page.** Investigated why `/bookings/PPF3522223` looked like it had no airport-transfer info — confirmed data was present (`InfoFields.direction='address_to_airport'`, `pickuplat/pickuplng`), the FE just never rendered it. Built `MapLinkIcon.js` (pickup/dropoff lat/lng → Google Maps link, inline next to existing Pickup/Dropoff rows in `BookingInfoDetails.js`). Ran a UXUI+BD agent debate on "how should staff tell Airport Transfer / Tour / Transfer apart at a glance" → consensus: explicit badge, `direction`-based, plus a 4th "Needs Review" state for ambiguous data (TRANSFER category + no direction) instead of silently guessing. Ran nextjs+django agent pair to verify the data path — found category lives at `Contract.service_category` on the detail endpoint (confirmed via `operators/models.py:330`, `bookings/serializers.py:79-113`), and that the *list-grid* endpoint exposes the same value under a differently-named key (`contract.type`, `bookings/serializers.py:265`) — scope trimmed to detail-page-only to avoid a two-shape helper (grid deferred). Built `bookingTypeUtils.js` (`getBookingType()`) + `BookingTypeBadge.js`, wired into `pages/bookings/[slug].js` header. Zero backend changes — all fields already serialized. Admin-dashboard `develop` `f65a805` (committed, not pushed).

**Workspace (#288):**
- frontend: `develop` `8c2b5c33` (clean)
- backend: `develop` `38c0470` (clean)
- admin-dashboard: `develop` `f65a805` (pushed origin)
- content: `master` `3756e5b` (clean)

---

## Session #287 (2026-08-04)

**Achieved:** Airport transfer date-aware dynamic pricing. Diagnosed: `resolveZone` returned date-agnostic base price → displayed price ≠ cart price when date-specific ratecards exist. Fixed: BE `ResolveZoneView` now accepts optional `?date=YYYY-MM-DD`, applies `Q(rate_date=date)|Q(rate_date__isnull=True)` (mirrors `_get_display_rate()`). FE `resolveZone` RTK query passes `date` param; `ZonePriceBox` sends `bookingDate` on address select + `useEffect` re-triggers on date change. Vault note created: `03-knowledge/airport-transfer-rate-dynamic-pricing.md`. Both branches merged → develop. BE `38c0470` · FE `8c2b5c33`.

**Workspace:** frontend `develop` `8c2b5c33` · backend `develop` `38c0470` · admin-dashboard `develop` `c003314` (clean) · content `master` `3756e5b` (all clean)

---

## Session #286 (2026-08-04)

**Achieved:** Airport transfer `/airport-transfer/[slug]` full style+UX overhaul. Removed wrong-product elements (TripListingSection, hero search, price subtext). Fixed style tokens (5 components). Calendar date centering fixed via `showFares={false}`. Back button removed, breadcrumb promoted. Breadcrumb invisible bug fixed (double ssr:false → direct NextBreadcrumbs import). Moved breadcrumb above trust strip. Merged to develop `944b2b1f`.

**Workspace:** frontend `develop` `944b2b1f` · backend `develop` `aa56361` · admin `develop` `c003314` · content `master` `3756e5b` (all clean)

---

## #285 (2026-08-04) — Airport transfer detail page UX/style overhaul shipped to develop

**Achieved:** Full style + UX audit of `/airport-transfer/[slug]` page. Removed wrong-product elements: `TripListingSection` (intercity trips, not zone transfers), hero search input (opened intercity trip modal), price subtext (`fromPrice` chain — backend `contracts` field = intercity trip contracts, not zone prices). Fixed style tokens across 5 components: `ZonePriceBox` (`rounded-2xl→rounded-xl`, `rounded-lg→rounded-input`, `bg-gray-50→bg-white`), `ZoneOptionCard` (`rounded-lg→rounded-container`, `bg-gray-50→bg-warm-surface`, `text-green-700→text-status-success`), `PlacePicker` (`focus:border-primary→focus:border-fb-blue` [was broken], `z-50→z-popover`, `rounded-lg→rounded-input/container`), `AirportTransferTrustStrip` (`max-w-[1200px]→max-w-container`), `StationInformation` (`color="primary"→className="text-fb-blue"`, `sm:rounded-lg→sm:rounded-container`, description typo fallback). Calendar date text centering fixed via additive `showFares={false}` prop on `SlideCalendar2` — skips invisible placeholder row that was pushing date text top-aligned. Removed back arrow button from `AirportTransferHeader` (props 8→1, `departureStation` only) — breadcrumb handles navigation. Breadcrumb invisible bug fixed: double `ssr:false` wrapping (`StandardBreadcrumb` → `NextBreadcrumbs`) caused silent render failure — import `NextBreadcrumbs` directly, one dynamic layer. Moved breadcrumb above trust strip (immediately below hero). All changes on `fix/style-consistency-airport-transfer` → merged to develop `944b2b1f`.

## #284 (2026-08-03) — Airport-transfer checkout zone card + notification fixes: validated + shipped to develop

**Achieved:** Validated merged airport-transfer stack on real BE data (user junedarkside@gmail.com, order VAR1397366, items Aug 6–8). Found + fixed 3 bugs post-merge: (1) `ZoneTransferRoute.js` — `address` var always picked `dropoffPoint` first regardless of direction (now branches on `isAirportFirst`); (2) `TripsConfirmation.js` — same address-pick bug + `airportName` resolved to route placeholder "Hatyai Any Hotel" instead of real airport (fixed: `zoneAirportFirst` computed before `zoneAddress`, `airportName` from `contract.transfer_airport.station_name`); (3) BE carts `ContractSerializer` missing `transfer_airport` field — added `get_transfer_airport()` (same ZoneContract query as products serializer). `EnhancedTripCard` updated to pass `airportStation` + `airportIata` from `transfer_airport`. `ZoneTransferRoute` now accepts `airportIata` prop + renders `Hatyai Airport (HDY)`. Notification gaps fixed: `orders/services.py` — added `direction` to `context` from `InfoFields.direction` + added `direction/pickuppoint/dropoffpoint/pickuptime/dropofftime` to `context_message` (Telegram payload) + added `booking.direction` to `customer_context` (email). `bookings/tasks.py` — zone-transfer block in Telegram message (direction label + pickup + dropoff, guarded by empty-check, zero side-effect on non-zone). Email template `booking_confirmation_template.html` — timeline FROM/TO station now branches on `booking.direction` (airport_to_address → typed address as arrival; address_to_airport → typed address as departure; blank → unchanged for route-list + activity). Tested synchronously: all 3 bookings SAW4621917/AJW0055474/PPF3522223 Telegram + email sent OK.

**Git:** FE uncommitted (3 files: `ZoneTransferRoute.js`, `TripsConfirmation.js`, `EnhancedTripCard.js`). BE uncommitted (4 files: `booking_confirmation_template.html`, `bookings/tasks.py`, `carts/serializers.py`, `orders/services.py`).

---

## #283 (2026-08-03) — Airport-transfer checkout + booking display: 6 branches shipped (FE 5 + BE 1), MERGED to develop + pushed

**Achieved:** FE + BE checkout-zone-card direction-storage pipeline, booking-display direction gate (no guessing), merged 6-branch stack to develop and pushed to origin. System check + migration validation passed. Git: FE `b9c14639`, BE `f6a9146`.

**Sequence:** (1) UXUI+BD agent research → 3-reviewer impl plan for detail-page conversion spec (8 ROI-ranked FE changes, DO-NOT-BUILD patterns). (2) FE airport-detail-cosmetics: R1 "from THB 400" hero price, R5 hero copy fix, R6 "All Destinations" label fix, R3 static trust strip, R7/R8 deferred, Bug B AirportTransferJsonLd empty-crash guard, dead `pickupMode` cut, **PlacePicker transparency fix** (inline-style override, not z-index). (3) FE airport-zone-card-rich: ZoneOptionCard extracted + vehicle/seats + Instant/Free-cancel row + direction chip. (4) FE airport-zone-direction-switch: deleted clear-on-tab useEffect, added `From ⇄ To` swap, removed route tabs. (5) 3-agent checkout-zone-card debate: direction inversion + address on card. FE fix/checkout-zone-card: EnhancedTripCard reads `selectTripInfo` → address+direction+vehicle, React.memo, ZonePriceBox stash explicit direction. Senior FE flagged guest→auth merge ID-change (deferred). (6) BE+FE cross-repo direction+framing: BE `feat/checkout-direction-and-station-type` added `CartItemCheckoutInfo.direction` + `InfoFields.direction` columns, persisted both write paths, TripSerializer +station_type/iata (migrations carts 0017 + bookings 0048, system-check clean, 28 tests pass). FE `feat/checkout-airport-framed-card`: getAirportEnd() → "Hatyai Airport (HDY)→…" for route-list, priority: zone-address > airport-framed > station-route > name, degrades safe.

**Booking display:** Gate on `hasStoredDirection()` only (no guessing). Stored direction → full airport treatment (badge, route frame, label). No stored direction → plain station route (general booking). New zone-swap bookings store direction end-to-end via stash→checkout→booking.

**Git state:** All 6 branches **MERGED to develop** and **PUSHED to origin**. FE `develop` tip `b9c14639`, BE `develop` tip `f6a9146`. Main untouched. No stashed work.

---

## #282 (2026-08-02) — /airport-transfer INDEX card redesign: image-led picker cards SHIPPED to develop (FE only, 0 BE)
UXUI+BD agent team → bare text StationCard → image card (`next/image` fill + object-cover group-hover:scale-105 + blur + onError→bgDefault, idiom copied from PopularRouteImageCard NOT forked). IATA chip, Popular badge (BKK/DMK/HKT), city·province subtitle, focus-ring a11y fix. Data caveat verified: `location_name.image` null for ALL 4 airports → branded fallback today. Width matched homepage "Explore Popular Routes" via shared Section+SectionHeader (py-6 px-4 xl:px-0). Fixed crash: capitalizeWords got nested location_name OBJECT. Demand-first IATA pin sort (zero-BE, degrades safe). 2 branches → develop: `0b24cc82`, `7d9d9dd3` (final). main untouched. Atoms: [[nextimage-card-fallback-idiom]], [[demand-first-iata-pin-sort]].

---

## #281 (2026-08-01) — Airport-transfer multi-contract-per-zone + JOIN-restriction: committed+merged+pushed (3 repos) + AD UX fixes

**Merged + pushed all 3 develops** (the #280 feature was uncommitted; now shipped to `origin/develop`): backend `8fb94ea` (multi-contract M:N + JOIN-block + migrations 0030–0033; 28 tests) `126f213..8fb94ea`; admin-dashboard `c003314` (Slice 2 + both pages + 3 UX fixes) `3ea1fa5..c003314`; frontend `3c3e590c` (tier cards) `b959f1ea..3c3e590c`. **AD UX fixes** (branch `fix/transfer-zones-gate-transport-private-charter` `29f0925`): (1) contract-page zones gate widened — was `service_category==='TRANSFER'` (hid transport contracts like 183=TRANSPORTATION+PRIVATE), now `isTransportationCategory(cat) && type∈{PRIVATE,CHARTER}` + added missing import (else ReferenceError); (2) transfer-zones list page client-side search+status filter (mirrors vehicle-types, 0 BE); (3) ZoneForm contract picker operator+station dropdowns + `isOptionEqualToValue` (no MUI chip crash). JOIN-trap root cause: contract 184=type JOIN → guard 400s correctly; fix = widened gate hides section for JOIN. All lint clean; BE 28 tests green; `migrate --check` clean.

## #280 (2026-08-01) — Airport-transfer zone: multi-contract-per-zone + JOIN-restriction (built, uncommitted at session end)

**Multi contracts per zone (M:N):** `TransferZone.contract` single FK → `ZoneContract` link table (zone·contract·is_active·unique), M2M-through idiom. Migrations 0031 (schema) + 0032 (backfill). SSOT `_apply_diff` sync (both admin sides, race-safe). `resolve-zone` → `options:[{contract_id,contract_name,price}]` (per-contract MIN, skip null). FE `ZonePriceBox` tier cards (`ZoneOptionCard`). AD `ZoneForm` multi-select + contract-page `TransferZonesSection` + `contract-zones/` endpoints + `TestLocationPanel` options. **3-agent scrutiny → fix-then-ship** (sync single-source, null-price skip, FE tab-reset, dead-code cut). **JOIN-restriction** (BD+UXUI debate → nextjs/django/senior review): `assert_zone_eligible` SSOT (serializer + APIView + model.clean) + migration 0033 (deactivate legacy JOIN links, live-caught 184/zone2) + AD picker `?contract_type=PRIVATE,CHARTER`. 28 tests. CHARTER kept, JOIN deferred (unblock w/ pax selector). ADR §6+§6b. All 3 branches uncommitted at #280 close (committed+merged+pushed in #281).

## #277-279 (2026-07-30 → -31) — Airport-transfer zone pricing: Slices 1–4b built + live-verified

5-agent review + 4-agent polygon-shape debate → POLYGON only (JSONField + ray-casting, NO PostGIS); Google DrawingManager removed v3.65 → click-to-draw. **Slice 1** BE zone core (`TransferZone` + `stations/geo.py` + `resolve-zone` + admin + migration 0030, 13 tests). **Slice 2** AD polygon-draw page (`transfer-zones/` DataGrid+drawer, `ZoneMap` click-to-draw+undo/delete/finish, `ZoneForm`, `TestLocationPanel`, sidebar+icon, `@react-google-maps/api`). **Slice 3** FE traveler picker (`ZonePriceBox`+`PlacePicker`, `tripsApi.resolveZone`, mounted on `[slug].js`, show-price-only). **Slice 4a** BE booking persistence (+4 coord FloatField + `resolved_contract` FK on InfoFields+CartItemCheckoutInfo, migrations 0047/0016, 17 tests, SPLIT verdict). **Slice 4b** FE Book wiring (withCartValidation, bookingDate+tabValue, full-contract fetch, BookButton+saveTripInfo stash). 2 bugs fixed: `session.id` gotcha; RTK Immer-frozen clone. Branches: BE `feat/airport-transfer-zone-pricing` `0da5a1c`, AD `feat/transfer-zone-admin` `6f36624`, FE `feat/airport-transfer-zone-picker` `00000a80`. Google billing was the live-map blocker (later resolved). All unmerged.

---

## Session #275 — 2026-07-29 — coupon admin management shipped to PROD (BE CRUD + AD UI)

- **5-agent marketing debate** (UXUI/marketing/nextjs/django/biz-dev) → verdict: ship coupon admin UI first (trapped capability — BE `Coupon` model built, zero admin UI). Report → `02-areas/marketing-tools-debate-2026.md`.
- **BE**: `CouponAdminSerializer` (write-capable, reuses model `clean()`) + `CouponViewSet` (`IsAdminOrIsStaff`) at `/admin-dashboard-orders/admin/coupons/`. No new model/migration. Develop `13ce885`.
- **AD**: coupon CRUD page + `CouponForm.js` (Formik+Yup) + `couponsApi.js` + `CouponRestrictionSelect.js` (operator/route M2M autocomplete). Develop `3ea1fa5`.
- **2 shared-form bugfixes**: `CustomSelect` key-gotcha (`option.key` not `label`); `CheckBoxControl` Formik-binding (render-prop + `type="checkbox"`). Affected coupon + hero-banner + ModalPopUp.
- Both repos DEPLOYED TO PROD 2026-07-29.

**Session #274 (2026-07-29) — personalized homepage band for logged-in users + card token fixes (FE):**
- New `components/FrontPage/PersonalizedHomeBand.js` — client-only `dynamic(ssr:false)` band below hero. Logged-in: "Welcome back, {name}" + upcoming confirmed trips (`BookingItemCard`, dynamic 1-col/2-col grid) + "Book again" rebook chips from completed history (deduped by route). Guest: `null` → byte-identical static/ISR homepage (no cross-user leak).
- `homepagev2.js` — band after `<DiscoverySection>` + `useSession` gate hiding guest booking-lookup strip + `MyBookingsSection` for logged-in. No `getStaticProps` change.
- Card token fixes: `PopularRouteImageCard` `rounded-lg`→`rounded-xl` + dropped inline `boxShadow:'none'`; `GuideCard` → standard `border-gray-200 shadow-sm hover:shadow-lg`. `ReviewCard` left `rounded-md`.
- Gotcha: `/bookingsummary/` reads `tab` numeric (`'1'`=upcoming); string `'upcoming'` silently returns ALL rows. Guarded w/ `getBookingStatus==='confirmed'`.
- Shipped `86912129` → merged develop `a505cfcb`. Deployed prod 2026-07-29.

**Session #273 (2026-07-26) — login page input focus ring removed:**
- Removed focus ring flash from email + password inputs on `/account/login`.
- `AuthInput` + `AuthPassword` in `FormControl.js`: replaced `focus:ring-2 focus:ring-blue-500 focus:border-transparent` → `outline-none focus:border-blue-500`. Base `outline-none` (not focus variant) prevents browser default outline flash before React render.
- Committed `9b37ef92` on `fix/login-input-focus-ring`, merged → develop, pushed.

---

**Session #272 (2026-07-26) — Dashboard redesign merge + profile menu link:**
- Added Dashboard link to profile menu Account section (`components/auth/ProfileMenu.js`).
- Merged `feat/dashboard-redesign` → develop `8401d3fd`, pushed.

---

**Session #271 (2026-07-26) — Account dashboard redesign + profile menu dashboard link:**
- Audited `/account/dashboard` with 3-specialist agent team (UX/UI + React architecture + Next.js perf) + design token audit.
- `ProfileHeader.js`: 358→90 lines — collapsed mobile/desktop JSX duplication, removed `showStats`/`stats` props, extracted `stringToColor`/`stringAvatar` to `helpers/avatarHelpers.js`, applied COLORS tokens.
- `AccountCard.js`: removed `hover:scale-105` (touch persist bug), `transition-all` → `transition-shadow`, `rounded-xl` → `rounded-container`, white-card variant added.
- `StatCard.js` (new): uniform neutral stat tile — gray icon column + hairline divider + dark number + muted label. No per-card color variation.
- `ActivityFeed.js` (new, `components/account/`): extracted activity list, `onNavigate` prop (no internal router side-effect).
- `helpers/avatarHelpers.js` (new): reusable avatar utils extracted from ProfileHeader.
- `store/api/accountApi.js`: fixed circular `providesTags`, added `keepUnusedDataFor: 60` on stats+activity.
- `pages/account/dashboard.js`: `getServerSideProps` server-side auth redirect, per-section loading, primary action strip, `max-w-container`, 0 gradient surfaces.
- `helpers/designSystem.js` + `tailwind.config.js`: added `brand.indigo`/`brand.indigo-light` tokens.
- `components/auth/ProfileMenu.js`: added Dashboard link (first item in Account section) → `/account/dashboard`.
- Merged `feat/dashboard-redesign` → develop `8401d3fd`. Build: ✓

---

**Session #270 (2026-07-25) — All 3 repos shipped to production:**
- Fixed git checkout error (`migration.js` uncommitted WIP blocked branch switch).
- AD `migration.js`: added `HelpIcon` tooltip to Trip Migration page. Committed `1b079b2` → main.
- BE + FE + AD all on `main` — shipped to production.
- Workspace: frontend `main` (`b3ee0fdf`) clean; backend `main` (`ae68e51`) `resources.txt` uncommitted; admin `main` (`1b079b2`) clean; content `master` (`3756e5b`) clean.

---

**Session #269 (2026-07-24) — AD contracts: Trip/Route column + grouped trip picker:**
- `ContractSerializer` exposes nested `trip` via `TripWithRouteSerializer`. `select_related` extended to cover `trip__route__departure_station/arrival_station`. BE `ae68e51` → develop.
- `ContractsDataGrid.jsx`: new "Trip / Route" col (`flex:1, minWidth:220`) — `departure_station → arrival_station`; non-transport = `-`; Tooltip clips. AD `0484eac` → develop.
- ⚠️ Manual QA NOT run.

---

**Session #268 (2026-07-24) — AD locations: soft duplicate warning (FE-only):**
- `/routemanagement/locations` create+edit warns on duplicate name (normalized). Save Anyway override. No BE change.
- Shared utils: `locationDuplicateUtils.js` + `useLocationDuplicateCheck.js`. Pattern from route duplicate check.
- Modified: `locationsApi.js`, `locationEdit.js`, `LocationCreateDialog.js`.
- Shipped: `f5ec0a6` → merged `--no-ff` → AD develop `1923124`. ⏳ Manual QA not run.

---

**Session #267 (2026-07-24) — AD bookings: Support SEP resend counter live update:**
- **Root cause traced end-to-end.** "Support SEP" col (`DataGridComp.js:230`) → `renderResendOp` → `ResendOp` `Resend (N)` button (`number=row.added`). N stuck at (0) despite backend working.
- **Backend CORRECT (untouched):** POST `/admin-dashboard/booking-send/` → `SendBookingViewSet.create` → `booking.added += 1; booking.save()` (`bookings/views.py:406`). `added` in `BookingSummarySerializer` (`serializers.py:191`). DB increment persists.
- **Bug 1 (primary):** `ResendOp` POSTed via raw `clientFetchDataFromApi` — no cache invalidation → RTK held stale `added:0` for the session. **Fix:** new `resendBookingToOperator` mutation in `ordersApi.js` (`invalidatesTags:['Booking','BookingSummary']`); `ResendOp` rewritten to `useResendBookingToOperatorMutation` — same props (no ripple to `DataGridComp`), added error branch + `disabled` while sending. Grid auto-refetches → N updates live.
- **Bug 2 (latent):** `getBookingSummary` missing `transformResponse` that every sibling query has (BE paginated `{results}`). Added `(r) => r?.results ?? r` — one-liner, so `added`/all fields reach rows.
- **Files:** `store/api/ordersApi.js`, `components/booking/ResendOp.js`. Committed `7aea52c` → merged `--no-ff` → AD develop (`36ec8ea`), pushed. No lint/build run this session.
- ⏳ Manual QA NOT run — click Resend, expect (N+1) live + persist on reload.
- **⚠️ Flagged (out of scope):** `BookingSummaryViewSet.get_queryset` filters `user=request.user` + `order__status='paid'` (`bookings/views.py:48-52`) — admin page scoped to logged-in admin's own paid bookings. If admin should see ALL users' bookings, that endpoint is wrong. User's call.
- ✅ Backend #264 search fix COMMITTED this session — `d39ca6d` → develop, pushed. All 4 repos now clean.

---

**Session #266 (2026-07-24) — AD trips: Copy Trip + time-aware duplicate warning:**
- **Copy Trip** — `ContentCopyOutlined` row action opens dialog in create-mode prefilled from source row. Frontend-only (no backend endpoint — trip has no deep children). "Copy Trip — {route}" title.
- **Time-aware duplicate warning** (frontend-only, non-blocking). 3-way rule: scheduled = route+operator+dep_time+arr_time; timeless charter/transfer = route+operator+override stations. Operator NULL (shared) normalized both sides (`?? ''`). Confirm dialog names matched trip(s) + 100-row-cap disclosure. Ports the `routeEdit.js` lazy-query pattern from #265.
- **`tripsApi.js`** — transform preserves raw override station ids + null-guard; exports `useLazyGetTripsQuery`. `contract_trip_count` in list operator column.
- Fixed pre-existing edit-prefill bug (override stations blank on edit). Copy-of-shared blast-radius guardrail Alert.
- UX + BD experts audited plan pre-build. Committed `78c7fa2` → merged `--no-ff` → AD develop (`0b0b301`). Lint clean, `next build` passes. Manual QA (10-item) NOT run.

**Session #265 (2026-07-24) — AD route management: auto-name + duplicate detection:**
- Auto-default route name from dep → arr station names on create; stops on manual edit (`nameEditedByUser` ref); resets on close
- Station-pair dup check on select (lazy `useLazyGetRoutesQuery`) + route-name dup check at submit (case-insensitive), merged
- Confirm dialog to override any dup; edit mode excludes self
- `FormControl` → `Field`+`TextField` for route_name (Formik onChange override bug)
- Committed `e02fff3` → AD develop, pushed

---

**Session #264 (2026-07-24) — space-insensitive search on 6 admin viewsets:**
- Normalized search added to `RouteViewSet`, `TripDashBoardViewSet`, `migration_audit`, `PlaceViewset`, `DashBoardStationViewSet`, `DashBoardLocationViewSet`
- Pattern: `normalize_search(s)` strips spaces/hyphens + lowercases → annotate FK fields with `Replace(Lower(F(...)), output_field=CharField())` → filter annotated fields
- `output_field=CharField()` fix for Django 3.2 nullable FK expression inference
- Backend curl-verified (trips 19, routes 11, stations 4, locations 1, places 1, migration audit 19)
- Backend only — no frontend changes, no migrations
- Uncommitted at session end (`products/views.py` + `stations/views.py`)

---

## Session #263 — 2026-07-23

**Achieved:**
- **Cart 400 fixed.** `carts/serializers.py` `get_departure_station`/`get_arrival_station` returned `ReturnDict(<string>)` → `ValueError` → 400 on every transport cart. Fixed: return `station.station_name` directly.
- **FE stale-token 401 storm fixed.** Extended `publicEndpoints` skip-list in `store/api/tripsApi.js` + `store/api/api-slice.js`.
- **B1 effective-station in recommendations + detail** — `ContractRecommendationSerializer.get_route` + `ProductDetailSerializer.to_representation` patched.
- **B2 admin trip search fixed** — `route__departure_station__icontains` (FK int) → `route__departure_station__station_name__icontains` + OR-branch for override stations.
- **N+1 prevented** via `select_related` in 5 service chains.
- **All merged → develop** (BE `8d03b30`, FE `b3ee0fdf`).

---

## Session #263 — 2026-07-23
CART + FE FIXES. Fixed universal cart 400 (`GET /carts/{uuid}/` broken for all transport trips since `c00c87a` merge): `carts/serializers.py` `get_departure_station`/`get_arrival_station` called `StationSerializer(station).data` → `ReturnDict(<string>)` → `ValueError 400`; fixed by returning `station.station_name` directly. Fixed FE 401 storm on public endpoints (tripfilter, carts): extended existing `publicEndpoints` skip-list in `store/api/tripsApi.js` + `store/api/api-slice.js` so stale Bearer never attached to AllowAny endpoints. Also fixed B1/B2 effective-station: `ContractRecommendationSerializer.get_route` + `ProductDetailSerializer.to_representation` now use `effective_*_station` override; admin trip search fixed (`route__departure_station__icontains` FK-int bug → `__station_name__icontains`); N+1 prevented via `select_related` in services.py + views.py. All merged → develop (BE `8d03b30`, FE `b3ee0fdf`). → [[operator-scoped-trip-station]] · [[guest-cart-401-refresh-storm]]

---

## Session #262 — 2026-07-22
PROD SEAT-CHECK DEBUGGING (real Lomprayah live). Diagnosed prod MAPPING_NOT_FOUND = station-record mismatch: contract `bangkok-khao-san-to-koh-tao-1220` route dep station = `"boonsiri counter khaosan bangkok"` but mapping row targets a different record `"Lomprayah Bangkok khao san"` (backend matches by station FK) — data-entry issue. Built BE debug block on `check-seat-availability` (operator, dep/arr station id+name, from/to/date/time, n8n URL, all operator mappings; always-on for MAPPING_NOT_FOUND, `?debug=1` elsewhere) + AD panel to render it. Timeout 15→25s (n8n `/webhook/search` latency 10-19s variable; "browser-first then works" = timing luck). Fixed HTTP 500: n8n returns `{"data":"no trip"}` STRING when no service → parser did `data_list[0]`.get on a char → `AttributeError`; now guards `data` type. 4 branches merged develop → deployed main (BE `073623b`, AD `ef41c7b`). Atom [[n8n-seat-search-response-contract]]. Resume: fix prod mapping data (delete+recreate against correct dep station → id 43/44), then E2E. → [[seat-availability-reseller-operator-gap]] · [[station-mapping-multi-operator-design]] · [[n8n-seat-search-response-contract]]

---

## Session #261 — 2026-07-22
SEAT-CHECK Part B SHIPPED → main — `operator_station_id` in Station Mapping dialog is now a Supabase `RouteID` autocomplete (unblocks #260's deferred item; **no BE proxy needed**). PostgREST leaks the exposed-schema list in the error `hint` on any invalid `Accept-Profile` → hook probes `schema('__probe__')`, parses hint, matches operator schema by name-prefix (longest, denylisted non-operator schemas), confirms via `Operator` col. `Lomprayah`→`lompraya` (lowercased 8-char truncation, not derivable); `RouteID` cols `Route`/`ID`/`Operator`, 39 rows. Label `"Route (ID)"`, saves `ID`; `freeSolo` preserves stale ids; no schema → free-text fallback. New `helpers/operatorRouteIds.js` (pure) + `hooks/useOperatorRouteIds.js` (module-cached discovery). Grid sorts by id asc. AD+BE deployed → main (AD `8780af4`, BE `5baebe8`). Prod remaining: `migrate operators` 0069+0070; recreate "lomprayah" op+mappings as real data. 2 atoms extracted. → [[postgrest-exposed-schema-hint-discovery]] · [[supabase-per-operator-schema-routeid]] · [[station-mapping-multi-operator-design]]

---

## Session #260 — 2026-07-22
SEAT-CHECK-RESELLER — `Contract.seat_check_operator` FK lets a reseller contract check seat availability against a source operator (Silaphat resells "lomprayah"). Resolution `operator = contract.seat_check_operator or contract.operator` covers mapping lookups + api_url. BE migration `0069`, AD form Autocomplete + transform. STATION-MAPPING-SEAT-API-VISIBILITY: page shows operator/API per mapping (chip + `Seat API` grid col via `operator_has_api` serializer field + `?our_station=` filter). DROP-CONTRACT-SEAT-API-URL: removed redundant `Contract.seat_availability_api_url` (1/81 usage, migration `0070`) + URL `.strip()` fix. All merged → develop + pushed (BE `5baebe8`, AD `3fc14e0`). Part B (Supabase id autocomplete) deferred — assumed `RouteID` anon-unreadable, needs BE proxy. → [[seat-availability-reseller-operator-gap]] [[station-mapping-multi-operator-design]]

---

## Session #259 — 2026-07-22
FAQ CSS FIX — Trip detail page FAQ section alignment + spacing fixed. Removed conflicting `mx-auto mx-2` → `mx-auto px-2 md:px-3 xl:px-0`. Fixed padding conflict (`p-4` outer → inner `<div className="p-4 md:p-5">`). Tightened heading `mb-3→mb-2`, item padding `py-2→py-3`, `rounded-md md:rounded-lg` → `rounded-md`. Committed `1e6eaec0` on `fix/faq-spacing-alignment` → merged develop → pushed `4758b4b1`.

## Session #258 — 2026-07-21
TRIPS QA + PROD DEPLOY + CHAT-IMAGE-SEND + SEAT-AVAILABILITY MIGRATE — Trips redesign QA passed, prod deployed (ISR cache flushed). CHAT-IMAGE-SEND prod deploy: Supabase SQL 003, Pillow bump, BE→AD→FE deployed, smoke passed. manage.py migrate 0066/0067/0068 on prod.

---

## Session #257 — 2026-07-21
SEAT-AVAILABILITY commit+push — Committed BE (`c535dd3`: 4 files + migrations 0066-0068) + AD (`b1996c7`: 4 files) to develop. Then completed: Trips Redesign QA, CHAT-IMAGE-SEND prod deploy, `manage.py migrate` 0066-0068 on prod.

---

## Session #256 — 2026-07-21
SEAT-AVAILABILITY-CHECKER-REBUILD — BE station-mapping feature was never committed (migration existed, model/views/serializer lost). Rebuilt from scratch: `OperatorStationMapping` model + CRUD viewset + `check-seat-availability` @action on `ContractDetailViewSet`. Wired n8n webhook (`https://n8n.smartenplus.co.th/webhook/search`). Added `seat_availability_api_url` field to Operator + Contract models (migrations 0067+0068) with priority chain: contract > operator. Fixed `seatStatus` parsing bug (`== 'Available'` exact match → `!= 'Sold Out'` logic). Added API URL fields in AD: OperatorForm + ContractFormFields + useContractFormData + contractUtils. All uncommitted (BE 4 files + 3 migrations; AD 4 files).

---

## Session #255 — 2026-07-20
STATION-MAPPING + SUPABASE-ERROR-LOGGING — Diagnosed Supabase 406 (transient outage, not code bug). Added HTTPError body logging to `_fetch_schema`. Committed + merged BE fix (`fix/cs-supabase-error-logging` → develop). Committed + merged AD station-mapping feature (`feat/station-mapping` → develop): SeatAvailabilityChecker, station-mapping page, nav entry, CRUD API endpoints.

---

## Session #254 — 2026-07-20
BRANCH-CLEANUP + CHAT-DESIGN-TOKENS — Pruned 45 merged branches across all 3 repos. Fixed ScrollTop overlap. Added CHAT design tokens. Refactored ChatBubble + ChatPanel to use tokens. Commit `4957f22b` → develop.

---

## Session #253 — 2026-07-19
TRIPS-PAGE-REDESIGN — `/trips` index redesigned via 3-agent team (UX auditor → designer → frontend implementer). `pages/trips/index.js` rewritten 733→162 lines: `getStaticProps` + ISR revalidate:3600, `PageSeo`, reuses `components/locations/{SearchBar,FilterControls,StatsDisplay,EmptyState}` unchanged. New: `components/trips/RouteCard.js` (image-forward, `TouristTrip` schema, gradient overlay, `departure → arrival` text), `hooks/useTripsFiltering.js` (memoised search+sort on joined route string), `hooks/useTripsStructuredData.js` (`ItemList` of `TouristTrip` + `BreadcrumbList` + `CollectionPage` with `speakable`). First page in codebase with `hreflang="en"` + `hreflang="x-default"`. Projected SEO 8.5 / AEO 8.5 / GEO 7.0. **Status: COMMITTED `db5982be`, not yet pushed.** Branch `feat/trips-page-redesign`.

---

## Session #252 — 2026-07-18
LOCATIONS-PAGE-REDESIGN — visual redesign of `/locations` index page on branch `feat/locations-page-redesign`. Mirror of destinations redesign: image-forward `LocationCard`, hero with H1 "Where in Thailand Do You Want to Travel?", back+share overlay (`top-2 z-40 pointer-events-none/auto`), `SearchBar` + `FilterControls` + `StatsDisplay` extracted into `components/locations/`. Two new hooks: `useLocationsFiltering(allLocations, searchTerm, sortOption)` (memoised filter+sort) and `useLocationsStructuredData(allLocations, domainURL, lastReviewedTimestamp)` (returns `seo`, `itemListElements` for `ItemList` JSON-LD `TouristDestination`, `breadcrumbItems`, `organizationSchema`, `CollectionPage` schema with `lastReviewed`). `pages/locations/index.js` reduced to composition. Status at session end: UNCOMMITTED on `feat/locations-page-redesign` (`354889f1`); later merged → develop `a25ff23d`. Workspace: backend `main` `06423c5` · admin `main` `21d03eb` · content `master` `3756e5b` — clean. Resume was: commit + push + verify locations JSON-LD/OG + mobile QA 375/768/1280 + parity vs destinations redesign.

---

## Session #251 — 2026-07-18
DESTINATIONS-PAGE-REDESIGN — full visual redesign of `/destinations` index shipped → develop. 3-agent team (design-review auditor → designer w/ 12Go/Booking/GYG/Klook research → react-specialist impl). Image-forward overlay cards (`location.image || DEFAULT_ROUTE_IMAGE`), go-TO intent H1 "Where in Thailand Do You Want to Go?", full a11y pass. 2-agent mobile debate (verdict YES-WITH-FIXES) → sticky FilterControls (`top-0 md:top-20`), mobile SearchBar moved hero→sticky bar, responsive MUI select widths, Book CTA pinned card-bottom (`mt-auto`). 4 commits → merge `354889f1` → develop (pushed): `943deb7d` redesign · `6d89c875` CTA pin · `24c92257` mobile sticky · `1e4f2f46` hero pill buttons 36→44px sitewide (16 non-destinations files). 22 files total. Lint clean. Build skipped (trivial touch-target change). Full design+debate record: `01-projects/destinations-page-redesign.md`. Workspace: frontend `develop` `354889f1` clean; `feat/destinations-page-redesign` kept on remote. Resume: (1) destinations live test (grid/card interactions, search/filter/expand/CTA) — local dev backend returned 0 locations; (2) carry-forward prod-deploy queue: TRIP-CARD-V2 (ISR cache flush + ENV.md row), REC-PRICE-FIX (Redis `recommendations:*` flush + `manage.py migrate` operators/0064), CHAT-IMAGE-SEND (Supabase SQL 003 + Pillow bump + deploy BE→AD→FE + smoke).

---

## Session #250 — 2026-07-15
TRIP-CARD-V2 — built flight-OTA style card from scratch (`TripCardV2.js` + `TripItemLayoutV2.js`). Env flag `NEXT_PUBLIC_TRIP_CARD_V2` (unset=V2, `false`=V1 rollback). 2-agent UX/Design audit → scorecard V2 7/7 vs V1 4.5/5. P1 batch: stops text under arrow, JOIN chip, amenity icons, station `line-clamp-2`, `max-w-[560px]`, 44px chevron. `SkeletonSection` rewritten to V2 anatomy; `TripSearchResults` inline skeleton replaced. Mobile compact legs breakpoint-split (`hidden sm:flex` full / `flex sm:hidden` compact). 8 commits → develop, pushed `f70dbe5d`. `NEXT_PUBLIC_TRIP_CARD_V2` row still needs adding to ENV.md (docs/ permission denied this session). VAULT AUDIT — `01-projects/trip-card-v2-flight-style-audit.md` created; `index.md` + `log.md` updated. Workspace: frontend `main` `f70dbe5d` · backend `main` `06423c5` · admin `main` `21d03eb` · content `master` `3756e5b` — all clean. Resume: (1) TRIP-CARD-V2 prod deploy — ISR cache clear (`smartenplus_next_cache` Docker volume) + add `NEXT_PUBLIC_TRIP_CARD_V2` to ENV.md; (2) REC-PRICE-FIX prod — BE main has `06423c5`, deploy + MANDATORY Redis flush `redis-cli --scan --pattern "recommendations:*" | xargs redis-cli del` + `manage.py migrate` (operators/0064); (3) CHAT-IMAGE-SEND prod — Supabase SQL 003 + `pip install -r requirements.txt` (Pillow bump) + deploy BE→AD→FE + smoke.

---

## Session #249 — 2026-07-15
BE-HOMEPAGE-PRICE FIXED — all 8 `Min(selling_rate)` finder annotations in `products/services.py` now filter `contract_ratecard__is_active=True` (inactive ratecards could win Min → unbookable "From" prices on rec cards). Branch `fix/rec-price-active-filter` → develop `06423c5`, pushed to origin. 4-agent audit (BD/UX/BE/FE) confirmed fix complete; other price paths already `is_active`-filtered. DEPLOY GOTCHA: Redis `recommendations:*` flush mandatory post-deploy (skip-if-fresh guard `tasks.py:66-75` serves stale prices up to 24h). REC-SLOT-WASTE closed DO-NOTHING per 4-agent audit — near-zero incidence, `checkout_recommendation_empty` GTM monitors it. Vault: `01-projects/rec-engine-report-audit.md` created, atom extracted `[[precompute-cache-stale-after-logic-fix]]`. Vault commit `eea2c7f` pushed.

---

## Session #248 — 2026-07-15
REC ENGINE — 5 phases shipped across FE + BE, all → develop. Phase 1 (`fix/rec-quick-wins`): 2s timeout on recommendationsApi · `recommendation_modal_open` GTM · `chidren` typo fix · sessionStorage Safari guard. Phase 2 (`feat/rec-purchase-event`): purchase attribution — `markRecSourcedContract` + `fireRecommendationPurchaseEvents` in `helpers/gtmUtils.js`; wired in `RecommendationBookingModal.js` + `hooks/useOmisePayment.js`. Funnel complete: view→click→modal→add_cart→purchase. Phase 3 (`fix/rec-checkout-filter`): `filterValidRecommendations` applied at checkout rec list. Phase 4 (`chore/rec-remove-ratecard-hook`): deleted `hooks/useRecommendationRatecards.js` (−138 lines). Phase 5 (`feat/rec-never-empty-fallback`): `find_global_fallback()` in `products/services.py`; hybrid dedupe; `booked_count` default 10→0; migration `operators/0064` applied locally. 28/29 BE tests pass (1 pre-existing failure `test_find_similar_contracts`). FE develop: `9fd5b0a5` · BE develop: `f0aea8c`.

---
