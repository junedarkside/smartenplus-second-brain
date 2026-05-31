# Second Brain — Operational Log

Chronological record of vault operations. Parseable: `grep "^## \[" log.md | tail -5`

## [2026-05-31] session-end | carousel 4-card desktop fix: xl:w-[284px] on PopularRouteImageCard + ExperienceCard. 4×284+4×16=1200px. b104962 pushed. PR-2 closed.
## [2026-05-30] debug | hero back/share buttons: 3 root causes found (wrong prop name, wrong containing block, dynamic loader chain breaks showActions). Buttons moved to TripDetailHero/DayTripHero outer wrapper. Glassmorphism pill style. UNVERIFIED — server in production mode. Resume: npm run dev first.
## [2026-05-30] post-mortem | FeaturedImageHeader width bug: w-[1200px] hardcoded in 0ebd755 broke mobile. Fix: w-full + max-w-[1200px]. Vault note created.
## [2026-05-30] session-end | EXP-1 implemented: PopularExperienceSerializer + ExploreExperiencesSection + ExperienceCard. 27 contracts. Backend 4ab5771, frontend f27f077. Master-state Section 1-3 updated, EXP-1 moved to closed.

## [2026-05-30] session-end | vault-only session. Experiences section feasibility: 3-agent research + scrutinize (3 wrong claims fixed) + grill (all decisions locked). EXP-1 added to loose ends. No code changes.

## [2026-05-30] grill | homepage-experiences-section-audit — all design decisions locked: skip rating (N+1), hide booked_count (default=10 misleading), card=title+category+price, image=imagegallery_set S3, serializer=standalone ModelSerializer, prefetch_related imagegallery_set.

## [2026-05-30] scrutinize | homepage-experiences-section-audit — 3 critical wrong claims fixed: featured_image missing on Contract (use ImageGallery), service_category list incomplete (TRANSPORTATION/ACCOMMODATION missed), HomeSerializer wrong copy template (use ContractSerializer). Vault doc updated.

## [2026-05-30] audit | homepage-experiences-section — 3-agent feasibility team (frontend+backend+vault). Verdict: VIABLE after AT-1. Backend ready, no new models. 5 files ~160 lines. Inventory gate required. Vault doc created.

## [2026-05-30] session-end | Airport Transfers section redesigned — Omio-style route cards with real pricing from backend. Backend airport_routes API added. Data shape bug fixed (StationSerializer shadow). Style audit 8 fixes. 1eec0aa + 3759dc2 pushed. Atom extracted: django-serializer-shadowing-pattern.

## [2026-05-30] session-end | Width consistency audit + sort dropdown fix.3-agent team (header/sections/live-verifier). Root cause: w-full + max-w-[1200px] = full viewport. Fix: explicit w-[1200px] on hero absolute div. Sort dropdown inline with title row. AirportTransferSection commented out pending AT-1. 0ebd755 committed.

## [2026-05-29] session-end | added Ask Away + Explore More to ProfileMenu (auth+guest), removed CustomerServiceSection from homepage. 7650f3c pushed.

## [2026-05-29] session-end | ProfileButton redesign complete (dac7e66) + next/image hostname fixes (help/blog). Pill trigger single-line, guest path fixed, MUI-preserve, bottom sheet mobile.

## [2026-05-29] decision | profile-dropdown-redesign — 3-specialist team (UX+UI+Frontend). 11→6 items, 296px, pill trigger, bottom sheet mobile, 3-file split, MUI-preserve. Vault doc created.

## [2026-05-29] session-end | homepage visual consistency audit + Check Your Booking UX redesign (trust badges, header position, copy)

## [2026-05-29] decision | check-your-booking v2 — reference image 2-column layout adopted. Judge: fb-blue not indigo, Order ID text link not tab, "Check" not "Manage", gap-4 not gap-6. v1 centered card rejected by user.

## [2026-05-29] decision | check-your-booking v1 — OTA utility card adopted (superseded by v2). 3-agent debate (FOR/AGAINST/JUDGE). Illustration removed, 840px card, warm-surface bg, inputs upgraded, eyebrow removed per judge, trust row copy fixed.

## [2026-05-29] session-end | homepage visual refinement: Popular Routes cards stronger, guides section renamed, reviews CTA removed, destinations grid fix reverted to 5 cards, sitewide width deferred

## [2026-05-29] create | travel-thailand-better-section-redesign — 3 editorial sections → 1 unified section. 1 featured + 2 secondary card layout. Spec ready, implementation pending.

## [2026-05-28] ingest | carousel design standard + popular routes fix: vw-based card widths, embla DOM structure, focus ring handling, items-per-screen table across 5 breakpoints

## [2026-05-28] vault-lint | 16 orphan docs analyzed. 9 hero files merged → 1 comprehensive audit. nav-header-redesign merged into existing (richer content). isr-stale-data merged into isr-429 fix doc. 5 files indexed + cross-linked (mobile-header, wireframe-architecture, uxui-research, trip-detail-deep-review, trip-detail-page-review). 11 files deleted. Index: 57→61 pages.

## [2026-05-28] vault-atomize | 5 atoms extracted from 3 source docs: hero-88px-gap-root-cause ← hero-audit, featured-image-header-usage-matrix ← hero-audit, smartenplus-product-positioning ← wireframe-architecture, smartenplus-2026-ux-direction ← uxui-research, mobile-header-scroll-behavior-change ← hero-audit. Index: 62→67 pages.

## [2026-05-28] session-end | homepage redesign 2026 implemented — commit 96bc6f9. Color tokens #1E40AF, Inter font, hero removed, DiscoverySection live, PopularRoutes polished. TrustRow + RouteChips removed per user. QA + merge next session.
## [2026-05-28] session-end | header redesign Days 1–3 complete. Branch 260528-feat/header-redesign-2026 a4158b0. Day 4 QA + merge next session. Context 48% at wrap-up.
## [2026-05-28] session-end | header redesign Days 1–3 implemented — branch 260528-feat/header-redesign-2026 commit a4158b0. Glassmorphism removed. Solid white header. 10 files. HeaderRowsContext live. Day 4 QA + merge pending.
## [2026-05-28] create | header-redesign-2026-implementation — handoff doc with full change log, architecture notes, QA checklist, remaining work
## [2026-05-28] update | header-redesign-2026 FINAL — Type A/B adaptive split locked. /blog → Type B. Keep all 5 nav items (Explore Thailand stays). Dynamic layout offset 80/96px. HeaderRowsContext for StickySearchBar. 12 files, 4-day impl + 2 separate PRs. Spec + team-review both updated.
## [2026-05-28] review | header-redesign-2026-team-review — 3-specialist audit (Design+UX+Frontend). 10 files not 5. 4 missing components (SearchDialogTrigger, CartButton, ProfileButton, NavDropdown). 2 open decisions (rows prop, mobile scroll hide). Full color map + regression matrix written.
## [2026-05-28] session-end | 2026 header redesign spec — revert merge c6d7248 (header-search-bugs), full solid-white header design brief written (HEADER_REDESIGN_2026.md + vault doc header-redesign-2026-spec.md). 5-file impl plan ready. Not yet implemented.
## [2026-05-27] create | mobile-header-redesign-glassmorphism — design spec for premium glass mobile header (solid blue → cinematic glassmorphism, always-fixed, scroll-reactive opacity, currency pill mobile variant, hero bleed pattern)
## [2026-05-27] session-end | header scroll opacity fix — root cause: CSS transition asymmetry (.glass-bg had 300ms, .glass-bg-scrolled had none) → asymmetric smooth/jarring on scroll direction change. Fix: added 200ms transition to .glass-bg-scrolled + reduced 300ms→200ms. Also removed scroll-based class toggle — desktop header always dark glass-bg-scrolled. Investigation: 1 agent (debug-specialist), 3-layer deep trace. No code pushed.
## [2026-05-25] session-end | passenger CSV export — added 6 columns (Passenger Names, Passport IDs, DOBs, Adults/Children/Infants Count). Hotfix: datifbirth→datofbirth, rate_type→attribute. Committed to feat/passenger-csv-export→develop (pushed), merged to main (user pushes manually).
## [2026-05-25] plan | premium-glassmorphism-header — team analysis (glass-auditor + hero-reviewer + scroll-specialist). Decision: Option A unified glass (both rows identical dark gradient, no divider). Remove Slide, use sticky + threshold scroll + CSS transitions. FeaturedImageHeader overlay reduction needed. Report: 01-projects/smartenplus-glassmorphism-header.md. index.md updated.
## [2026-05-25] session-end | nav redesign Phases 0-2 done + Phase 3 backend+frontend code complete. Label renames (5), Experiences dropdown, Explore Thailand dropdown + URL param, NavigationSection+NavigationItem models (0010 migrated), NavigationViewSet with cache, Django admin inline, RTK Query nav endpoint with fallback. Blocked: /pages-info/navigation/ 404 (server restart needed), NavigationSection data not populated. 3 bug fixes: api-slice path, /api/v1 prefix, React key in PopularRoutesCarousel+CardCarouselContainer. Branches: frontend 260524-feat/nav-label-changes, backend 260525-feat/nav-api-endpoint.
## [2026-05-24] plan | nav-header-redesign — 3-phase dropdown plan (UI scaffold → URL param enhancement → backend data). 3-agent audit (UX, SEO, Mobile) found: URL param links broken on /destinations, /locations, /trips (no router.query reading); mobile drawer flat list, no accordion; navLinks/menuLinks separate arrays; CategoryMenu.js wrong pattern for mobile accordion. Revised plan ready. Vault doc: nav-header-redesign-2026-05-24.md
## [2026-05-24] validate | nav-header-redesign — 6-agent validation (component-audit, pattern-specialist, implementation-critic) converged: Phase 1 dropdown over-engineered, label changes only is better Phase 0. All submenu links go to same base page (URL params don't work). Only Experiences dropdown works immediately (via /activities?category=). Mobile accordion deferred (stopPropagation a11y trap, focus management complexity, 7 extra mobile items product decision needed). Phase 0 label changes: 15 min, zero risk. Plan finalized. Vault doc updated.
## [2026-05-24] session-end | content marketing playbook rewritten — 5-agent review, 6 contradictions fixed, keyword CSV analysis, tech stack + real URLs integrated. No code changes to dev repos.
## [2026-05-24] session-end | auth pages noindex fixed — NextSeo moved outside ProtectedComponent on /bookings + /orders. 4209def pushed to main → production. All SEO wave-2 issues resolved.
## [2026-05-24] session-end | strategic direction grill complete — no code changes. Vault updated + pushed 6ba72e8. Next: auth pages noindex fix.
## [2026-05-24] ingest | strategic direction validated via grill — B2B/B2C split confirmed (90/10), EN customer confirmed (GA4+support), Malaysia Phase 2, vertical integration moat (minivan network+own tours), Stippl product vision, revenue model = markup not commission
## [2026-05-24] cleanup | deleted master-state.original.md (stale 2026-05-22 backup) + breadcrumb-dedup-plan-2026-05-20.md (work done, plan doc misleading): docker-standalone-isr-revalidate-gap, on-demand-revalidation-api-route, celery-task-over-bare-thread-django-signals, isr-csr-overlay-stale-fields, persistgate-ssr-suppresses-head-component, webpack-image-src-og-absolute-url-rule. isr-stale-data-audit (344→36L) + seo-wave2-audit (282→32L) trimmed. index.md updated. log.md appended.
## [2026-05-23] deploy | PersistGate SSR fix merged → develop df81b19 → main → production live 2026-05-23
## [2026-05-23] session-end | seo-wave2 — all 11 bugs fixed, merged to main. Auth pages noindex blocked by ProtectedComponent returning null SSR (fix deferred). Vault updated. Main merged, not pushed (user held).
## [2026-05-23] session-end | PersistGate SSR blocker fixed — all OG meta tags restored site-wide; OG image relative paths fixed in seoHelper.js + trips/index.js; NEXT_PUBLIC_SITE_URL tech debt reverted; branch 260523-fix/trips-og-image-and-site-url-env (4 commits: 61134c9, f8d9907, 4644fac, ac6f8aa) — merged → main → production
## [2026-05-23] session-end | og:image:secure_url site-wide — 24 files, homepage domain fallback, generateBlogSEO() updated, merged → main 190e2a2; verified live
## [2026-05-23] scrutinize | og-image-inferred — fix plan corrected: homepage use inline 3-tier fallback (not getSiteUrl() cross-module import); blog use generateBlogSEO() helper (not N inline copies); search page has seo object already (not blank slate); vault doc updated
## [2026-05-23] audit | og-image-inferred — site-wide Facebook og:image warning; RC1: NEXT_PUBLIC_DOMAIN undefined in prod → homepage Seo crash; RC2: missing secureUrl on blog pages; vault doc written; fix pending
## [2026-05-23] session-end | og:image Facebook "inferred" warning fixed — hardcoded 1200×630 + missing secure_url in BlogPostHeader.js; 1dd9d01 pushed to main
## [2026-05-23] audit | isr-stale-data — ISR revalidate:300 broken in Docker standalone; Django signals clear Redis but never notify Next.js; on-demand revalidation API route proposed (Option A over B/C/D); **2 blockers + 3 major findings from team scrutinize — reword before implementing: (1) revalidate.js doesn't exist, (2) network path unverified, (3) daemon thread → use Celery instead, (4) consider revalidateTag, (5) root cause conflates 2 different issues**
## [2026-05-23] audit | fast-refresh-infinite-loop — 7 fix attempts failed; RefreshTokenHandler diagnosis OVERTURNED by scrutiny (lastExpiryRef guard blocks loop); actual cause likely Next.js 14.2.x HMR + on-demand compilation cascade (self-terminating); git bisect + debug instrumentation recommended; CurrencyContext fix applied
## [2026-05-23] audit-draft | fast-refresh-infinite-loop — 7 fix attempts, RefreshTokenHandler Date.now() + state loop identified by 3 agents; CurrencyContext fix applied; vault audit doc written
## [2026-05-23] session-end | infinite fetch investigation — circular-dep theory overturned; Fast Refresh reload loop (hot-update 404) + CurrencyContext race condition identified; vault doc written; no code changes; items #16+#17 added to loose ends
## [2026-05-23] scrutinize | currency-context-infinite-fetch — initial circular-dep claim overturned; actual cause: Fast Refresh full-reload loop (hot-update 404) + CurrencyContext race condition; doc updated with correct trace + 2-step fix order
## [2026-05-23] deploy | frontend + backend pushed to main — 429 fix (67cdf66) + auth dep fix (da3c2b1) now in production
## [2026-05-23] session-end | migration audit — locked_amount chain 0038→0042 verified intact on develop; no changes made
## [2026-05-23] session-end | 429 fix + auth dep fix — 3-agent team review caught flat cache key bug; parameterized key + no DEBUG guard; Fix A merged backend 67cdf66, Fix D merged frontend da3c2b1, both pushed origin/develop
## [2026-05-23] rework | isr-429-cold-start-fix — scrutiny overturned 2 false claims: REVALIDATE_SECONDS irrelevant in dev, getStaticPaths build-time only; actual cause: DRF anon 500/hour window persists across runserver restarts; fix = backend response cache on FrontPageViewSet.list; nextjs-patterns.md corrected
## [2026-05-23] ingest | isr-429-cold-start-fix — cold start 429 on /front-page/ diagnosed: REVALIDATE_SECONDS=60 + refetchOnMountOrArgChange:300 + props-in-deps; 3 fixes identified; nextjs-patterns.md ISR+RTK rules updated
## [2026-05-23] feat | rename /daytrips → /activities complete — 7 phases, 5 scrutiny fixes (v4/v5 migration gap, duplicate [slug].js route, git rename detection, SEO title, test pathname), merged → develop d424d4e; post-deploy: clear smartenplus_next_cache + resubmit GSC sitemap
## [2026-05-23] ingest | daytrips-to-activities-rename — 3-specialist team review, unanimous `activities`, 51 files mapped, 9 critical risks documented, cart/payment flows confirmed safe; branch 260523-feat/rename-daytrips-to-activities created
## [2026-05-23] session-end | vault optimization — synopsis atom note created, 26 files caveman compressed (139KB→128KB, 7% reduction), 12 old backups + 3 empty stubs cleaned; all 3 repos unchanged
## [2026-05-23] optimize | caveman:compress — 26 files compressed (139KB→128KB, 7% byte reduction); 3 empty stubs deleted; 37 .original.md backups retained for rollback
## [2026-05-22] ingest | smartenplus-synopsis — project-wide synopsis atom note created; 12 .original.md backups cleaned
## [2026-05-22] session-end | trip detail width/gap/rounded consistency — RelatedTripsSection my-0→my-2 + rounded-md, breadcrumb padding confirmed px-2 md:px-3; merged → develop → main → production
## [2026-05-22] session-end | trips filter page gap+rounded consistency — gap-3 sidebar↔results + cards, rounded-lg unified across filter bar/sort/table; 4da9175 pushed to main
## [2026-05-22] session-end | section width unification on /trips filter+detail pages — mx-2 md:mx-3 xl:mx-0 pattern applied to calendar, filter bar, sidebar, cards, overview, summary, blog post; SlideCalendar2 className prop added; e7345ea on main (not pushed)
## [2026-05-22] session-end | blog hero-breadcrumb gap unified via BlogPageWrapper flex restructure; CategoryMenu moved to hero actionButton + styled to match back/share buttons (bg-black/25 white); all pages gap-2; 260522-fix/trip-detail-ux merged → develop
## [2026-05-22] session-end | site-wide style consistency + breadcrumb gap standardization — 8px rhythm across all pages; removed mb-6/py-2 from 35 files; ContentCard rounded-md, typography gray-900, gap-1→gap-2 filters; branch 260522-fix/trip-detail-ux uncommitted
## [2026-05-22] session-end | trip detail UX/UI audit + all P1 fixes done; branch 260522-fix/trip-detail-ux ready for PR to develop
## [2026-05-22] fix | trip-detail-uxui — 32 issues found+implemented: ContentCard wrappers, h1 text-sm, z-5→z-10, text-md phantom, pb-16, CLS fallbacks, booking bar a11y; branch 260522-fix/trip-detail-ux (3 commits)
## [2026-05-22] session-end | created trip-detail-uxui-auditor agent — 3-specialist team, 32-item checklist; deep width/margin audit confirmed Section/ContentCard absent from entire trip detail tree; calendar fix = wrap at page level; fixes pending
## [2026-05-22] session-end | homepage SEO audit all 30 findings done + AI misclassification 6 fixes; both merged to develop; next: backend #4 locked_amount + useTripSEO TouristTrip audit
## [2026-05-22] fix | ai-classification — /bookings unblocked robots.txt, BusTrip @type, Service schema, llms.txt, hasOfferCatalog on TravelAgency
## [2026-05-22] fix | homepage-seo-p1 — aggregateRating live, sameAs, lastReviewed, WebSite schema, DefaultSeo, og/twitter, logo, geo fix, preconnect, CLS, hero crossfade
## [2026-05-22] session-end | P0 SEO fixes done on branch 260522-fix/homepage-seo-p0; next: P1 fixes (aggregateRating, sameAs, DefaultSeo, Seo.js og) then merge + backend #4
## [2026-05-22] fix | homepage-seo-p0 — fake phone replaced, fake address removed (taxID added), server-sitemap.xml 404 hotfix, robots.txt policy merged
## [2026-05-22] ingest | homepage-seo-performance-deep-review — 3-specialist audit, 30 issues (3 critical, 11 major), P0: server-sitemap.xml 404 + fake phone/address in TravelAgency schema
## [2026-05-21] session-end | SEO specialist team built — agent + vault doc created; team NOT yet run; next: run review then P0 fixes + backend #4 locked_amount
## [2026-05-21] ingest | seo-homepage-specialist-team — agent created (seo-homepage-auditor.md), vault knowledge doc added, 10 pre-identified SEO gaps documented
## [2026-05-21] session-end | homepage UX/UI review doc fully cleared P0-P3; #1 trip-seo→main user handling; next: backend #4 locked_amount constraint
## [2026-05-21] session-end | homepage P1+P2+P3 fixes complete — 3 branches merged to develop, booking ID format corrected (ABC1234567 not BK prefix), P4 deferred
## [2026-05-21] session-end | homepage UX/UI review (3-agent, 11 sections) + scrutinize corrections applied — vault 52 pages, frontend on 260521-fix/trip-seo-usd-hardcode PR open
## [2026-05-21] scrutinize | homepage-ux-review — 3 corrections: IATA claim wrong (capitalizeWords preserves uppercase), DOMPurify SSR risk (use isomorphic-dompurify), help links also missing leading slash (line 46, not just forum line 83)
## [2026-05-21] ingest | homepage-ux-review — 3-agent UX/UI review, 11 sections, 4 critical (XSS, hero VP, search validation, location title) + 34 major + 15 minor; section reorder recommended
## [2026-05-21] session-end | useTripSEO USD /30 hardcode fixed (49e6f17) — PR open on 260521-fix/trip-seo-usd-hardcode
## [2026-05-21] session-end | /lint-vault first run — 6 atoms extracted; vault 51 pages, all 3 repos clean on main
## [2026-05-21] lint | /lint-vault run — 6 atoms extracted: payment-sentinel-idempotency, nextauth-session-shape, cart-reprovision-after-reset, promptpay-no-webhook-on-expiry, nextjs-isr-ratecard-empty-array-guard, nextjs-307-vs-301-product-reclassify
## [2026-05-21] session-end | atomic notes system shipped — auto-atomize in wrap-up + /lint-vault command; vault bd2fc03 pushed
## [2026-05-21] ingest | atomic-notes system — auto-atomize on wrap-up (Step 5) + /lint-vault command; atomic-note template + atomic-notes rules doc created
## [2026-05-21] session-end | Popular Routes image carousel (edccb75) — CardCarouselContainer extracted, BlogCardContainer refactored, 4-card responsive layout pushed to PR
## [2026-05-21] session-end | header/footer alignment + icon normalization merged to develop→main (e67379f). All 3 repos clean on main.
## [2026-05-21] session-end | trip detail H3 fix — fetchData 8s timeout for blocking fallback SSR (c39f83c) + H1/H2 verified already fixed — merged to develop + main
## [2026-05-21] session-end | trip detail quick-wins — 9/10 already done, 2 applied (console.log→warn, dead __dataSource branch) — b866f6c merged to develop + main
## [2026-05-21] session-end | homepage full consistency audit + design system sync — 6 fixes (footer typo, booking section brand colors, Guides double-nav, Reviews error color, hero stray class, design system hex/config) — 260520-update/frontpage merged to develop + main
## [2026-05-21] session-end | frontpage style consistency — section card rounded+margin+overflow-hidden, footer bg-fb-blue full-width, 2 commits pushed on 260520-update/frontpage
## [2026-05-20] session-end | help icon mobile fix round 2 (revert MUI sx → Tailwind div), vault updated with Emotion cache provider lesson
## [2026-05-20] fix | Help icon mobile — reverted MUI Box sx responsive breakpoints (need Emotion cache), use Tailwind div wrapper per existing pattern
## [2026-05-20] session-end | all repos merged to develop, breadcrumb dedup merged, forum table width fixed, MUI+Tailwind knowledge doc — 12 commits on frontend, vault updated

## [2026-05-20] session-end | MUI+Tailwind CSS fixes, trip detail 4 fixes, breadcrumb dedup branch — hero button sx color, help icon MUI Box breakpoint, breadcrumb SSR, redirect 308, scroll rAF, reviews fetch removed; pushed to origin

## [2026-05-20] ingest | mui-tailwind-css-specificity.md — MUI Emotion CSS overrides Tailwind className on MUI components; root cause + fix patterns (sx prop, div wrapper) + property-by-property guide; affects IconButton, Button, SvgIcon

## [2026-05-20] ingest | breadcrumb-dedup-plan-2026-05-20.md — 16 files across 3 groups; GROUP B (10 section/div), GROUP C (4 padding-only), GROUP D (2 section/py-0); 8 already correct; 5 skipped (context-dependent)

## [2026-05-20] session-end | blog index 2 fixes (1e34601) + HMR hot-update 404 fix (b56d62a) — H1 visible on mobile, Load More filled button, next.config.js Cache-Control narrowed to chunks/css only; PRs still pending

## [2026-05-20] session-end | build errors fixed + ssr:false removed + reviewer artifact deleted — calculateAge exported (96c9c10), dead getStaticProps re-export removed, DynamicReviewListByProduct ssr:false dropped (3f948bf), build clean; PRs still pending

## [2026-05-20] session-end | trip detail 16 fixes + recommend-route all committed; PRs pending — 3-agent review (24 issues) + 4-agent adversarial deep review (8 hidden); 10 quick-wins (3f35d8c) + 6 deferred fixes (0bf038d); recommend-route frontend (2434124) + backend (3e49644) committed; PRs not opened yet

## [2026-05-20] ingest | trip-detail-deep-review-2026-05-20.md — 4-agent adversarial pass; 3 original findings overturned (P2 isClient, S1 307→301, C4 typo); 8 hidden issues; top 3 risks: ratecard wipe crash, fetch timeout 500 loop, invalid ISO8601 TouristTrip schema

## [2026-05-20] ingest | trip-detail-page-review-2026-05-20.md — 3-agent review of pages/trips/detail/[...slug].js; 24 issues (8 perf, 8 SEO, 8 code quality); verified against actual code, false positives removed

## [2026-05-20] session-end | dashboard Main.js RTK Query migration (c06af90) — 3-agent review team, 12 useState→0, raw axios→RTK Query, shadowed import+memory leak+mock trends fixed, new dashboardApi.js slice, 334→170 lines; updated admin-dashboard-component-patterns.md, master-state.md

## [2026-05-20] session-end | Popular Routes admin page committed (beaf1a7) — read-only DataGrid consuming GET /admin-dashboard-routes/home/; backend+frontend recommend-route changes still uncommitted; updated recommendation-system.md, master-state.md, index.md

## [2026-05-20] session-end | hydration infinite refresh fixed — 4 files (_app.js dual-tree, PopularRoutesStructuredData Date.now, GridComponent useCallback, CurrencyContext useMemo); agent ~55% accuracy; backend+frontend still uncommitted on 260520-update/recommend-route

## [2026-05-20] session-end | forex 429 fix (backend c859f3b + frontend ff1f378) + admin HeroBanner UI committed (d3194d8); all 4 repos clean + pushed

## [2026-05-20] session-end | blog perf/SEO round 2 (6b655d6) — parallel fetches, image fixes, HMR infinite loop fixed; admin HeroBanner UI still uncommitted

## [2026-05-19] session-end | blog SEO fixes + perf optimizations committed (0f38cf8); admin HeroBanner UI still uncommitted

## [2026-05-19] ingest | DAYTRIP_DOCUMENTATION_SUMMARY.md — deleted from vault root, replaced with tour-system-status.md

- Source was a 2026-03-03 meta-index pointing to 36 repo docs. Low vault value — repo already has `docs/tour-system/INDEX.md`.
- Deleted: `DAYTRIP_DOCUMENTATION_SUMMARY.md` from vault root (wrong location, stale counts, just a directory map)
- Created: `01-projects/tour-system-status.md` — Phase 2 open gaps, trust signal fields, pointer to authoritative repo docs
- Core facts still valid: Contract/TimeSlot/ContractAddon/ContractTranslation models intact. 46+ commits since doc date — test/contract counts stale.
- See [[tour-system-status]], [[operators]]

## [2026-05-19] session-end | built vault session system — init/wrap-up protocols, master-state.md, optimized CLAUDE.md + master-state.md

## [2026-05-19] system | master-state.md created — mission control / session handoff

- New file at vault root alongside `index.md` and `log.md`. Partitioned by change frequency.
- Section 1 (every session): active branches, uncommitted changes, next step, last worked on.
- Section 2 (weekly): open loose ends, in-flight features, recently closed bugs.
- Section 3 (monthly): cross-repo API contract, auth rules, data shape gotchas, payment constants.
- Section 4 (rarely): architecture guardrails — lock order, payment rules, Celery patterns, heal commands.
- Updated `index.md` (41 pages) and vault `CLAUDE.md` Special Files table.

## [2026-05-19] session-end | blog/index.js style fixes (5 gaps) + design audit (9 gaps identified, not yet fixed)
- Solves baton-pass problem: AI reads this at session start instead of re-deriving state from git log.

## [2026-05-19] feature | Hero Banner CMS — backend-controlled homepage hero

- New `HeroBanner` model in `pages_info` app. `FileField` (not `ImageField`) — Pillow 9.3.0 has no AVIF decoder, `ImageField` rejected AVIF uploads.
- Backend: `/hero-banners/` CRUD endpoint + injected into `/front-page/` response. Migrations `0008`, `0009`.
- Admin dashboard: `heroBannersApi` RTK Query slice, `HeroBannerForm` with drag-and-drop, DataGrid CRUD page at `/routemanagement/hero-banners`.
- Frontend: `homepagev2.js` — 5s auto-slideshow via `setInterval`, fallback to `bgDefault` if no banners. SSG unaffected, no SEO impact.
- Key gotcha: `display_order` empty string → DRF rejects as non-integer. Fixed in FormData submit handler.
- See [[hero-banner-cms]]

## [2026-05-19] session-end | blog detail sidebar padding — iPad mini + iPad Pro flush-right fixed

## [2026-05-19] fix | Contract_TranspotComposit admin crash — frontend sentinel id=-1

- Root cause: frontend sends `id: -1` for new unsaved rows. Backend passed it as PK into `get_or_create(id=-1)` → UniqueViolation on every save attempt.
- Fix: `operators/views.py:739-774` — branch on `id <= 0` (new) → `create()` vs positive id → `get_or_create()`. Sentinel never enters keep-list.
- Pattern captured: sentinel ids must never be PK lookup keys. See [[operators]] Contract_TranspotComposit section + [[admin-dashboard-contracts]] Payload Rules.

## [2026-05-19] refactor | Nav/Header Redesign — Minimal White Style + A11y Baseline

- Desktop: white bg (`bg-white`), `border-b border-gray-200`, tab-style active link (`border-b-2 border-brand-primary`)
- Mobile: brand blue preserved. All icons/text: `text-white md:text-gray-600` pattern (hamburger, logo, cart, profile consistent)
- Replaced pipe separators with `<nav aria-label>` + flex gap-1
- A11y: `aria-current="page"`, `focus-visible:ring`, skip-to-content link, `<IconButton>` close on drawer
- Fixed profile icon clipping: ProfileImage Box 40→44px (chevron badge `-2px` overflow clipped by AppBar `overflow:hidden`)
- Fixed huge gaps: right cluster `justify-between` → `justify-end` (was spreading items across ~900px)
- Key gotcha: MUI AppBar needs `color="inherit"` for Tailwind bg classes to take effect
- Commit `082a154` on branch `260513-refactor/payment`
- Created: `nav-header-redesign.md`. Updated: `design-systems.md`, `index.md`, `log.md`

---

## [2026-05-18] fix | StickySearchBar empty route name on fresh page load

- Root cause: `StickySearchBar` reads only Redux `state.location.from_location/to_location`. Fresh load = empty Redux = blank route name.
- Fix: `FilterTripsPage` passes `fromSearch`/`toSearch` (URL slug-derived) as props. `StickySearchBar` uses `reduxValue || propValue` fallback.
- Same pattern already existed in `SearchCover` (`fromLocationRedux || initialFromLocation`).
- 2 files changed, ~6 lines. No new abstractions, no Redux dispatch.
- Updated: CLAUDE.md (Search/UI section), vault nextjs-patterns.md (Redux Fallback Props Pattern)

---

## [2026-05-18] fix | Profile 403 Forbidden — PUT endpoint migration + UX

- Root cause: `PUT /users/${userId}/` admin-only since 2026-05-07. Frontend never migrated PUT from old endpoint.
- Backend: `UserAPIView` changed `RetrieveAPIView` → `RetrieveUpdateAPIView` (adds PUT support)
- Frontend: `pages/account/profile.js` endpoint migrated `/users/${userId}/` → `/api/user/`
- UX: `id_or_passport` + `datofbirth` made optional (OAuth providers don't supply these)
- UX: Debug error summary replaced with MUI Alert + friendly field labels (touched-only)
- Commit `a1944df` on branch `260513-refactor/payment`
- Updated: CLAUDE.md, vault accounts.md, vault api-endpoints.md

---

## [2026-05-18] fix | multi-tab payment gaps — all 7 resolved (GAP-1→7), PAY NOW lock, daytrip build fix

---

## [2026-05-18] fix | Checkout Access Broken for Auth Users — session?.email Regression

- Root cause: commit `8b3151f` changed `session?.user?.email` → `session?.email` based on wrong CLAUDE.md doc
- NextAuth does NOT set `session.email` at root level — email lives ONLY at `session.user.email`
- Effect: `email = undefined` for all auth users → `useCheckCartIdQuery` got null email → cart query returned stale/empty data → checkout redirect fired → users bounced to home
- Blast radius: 3 code files + 2 CLAUDE.md doc lines
- Investigation method: 3-agent parallel team (vault reader, checkout investigator, cart-login investigator) + independent plan reviewer (PASS) + code reviewer (PASS) + debug specialist (0 lint errors, 0 remaining hits)
- Fix: `session?.email` → `session?.user?.email` in `pages/checkout/index.js:47`, `pages/checkout/PaymentComponent.js:150`, `pages/orders/[orderid].js:113`
- Doc fix: CLAUDE.md session structure bullet + cart reprovisioning bullet corrected
- Verified: guest path (`formData?.email`, `router.query.email`) untouched. All prior payment fixes unaffected.
- Commit `5b7fa3c` on branch `260513-refactor/payment`

## [2026-05-18] fix | GAP-1 Payment Processing Banner — Dead Code Activated

- Multi-tab payment research GAP-1: `isPaymentProcessing` never dispatched, `GlobalPaymentWarning` dead code
- Worse than documented: `setPaymentProcessing` imported in `PaymentComponent.js` but never called. Component had broken `isMounted` guard — timer never started
- Fix: full lifecycle — set on charge creation, clear on paid/timeout/rehydration/error
- Backend-sourced timing: `expires_at` from charge response drives countdown. Removed hardcoded `qr_expiry_minutes: 5`. Backend `METHOD_EXPIRY` is source of truth
- Files: `useOmisePayment.js`, `GlobalPaymentWarning.js`, `paymentStatusSlice.js`, `_app.js`, `PaymentComponent.js`, order detail pages
- `GlobalPaymentWarning` moved from `_app.js` to `checkout/index.js` — under step nav, same position as guest banner
- Uses `AlertMessage` component with `warning` type (added to AlertMessage alertStyles)
- `reconcileStaleProcessing` reducer: auto-clears if `paymentInitiatedAt` >30 min on rehydration
- Branch `260513-refactor/payment`

## [2026-05-18] refactor | GAP-3 Cart Mutation Error Handling — isPaymentPendingError Utility

- Multi-tab payment research identified 6 gaps (2 HIGH, 2 MEDIUM, 2 LOW)
- Picked GAP-3: cart item DELETE silent fail on 409 — best impact-to-effort ratio
- Key discovery: research doc referenced dead code (`Itinerary.js`, zero imports). Active component: `EnhancedTripCard.js`
- Extracted `helpers/handleCartMutationError.js` — shared `isPaymentPendingError()` used by 4 components
- Fixed `EnhancedTripCard.js`: non-409 delete errors now show Alert instead of silent close
- Fixed latent bug in `BookButton.js`: bare `error?.status === 409` matched ALL 409s, not just payment_pending
- Deleted dead `components/itinerary/Itinerary.js`
- Commit `2116530` on branch `260513-refactor/payment`
- Docs: `docs/features/payment/GAP3_CART_DELETE_ERROR_FIX.md`, `docs/features/payment/MULTITAB_PAYMENT_RESEARCH.md`
- Updated `payment-integration.md` in vault: "Centralized Payment Error Detection" pattern

## [2026-05-18] fix | cartId Null After Payment Redirect — Cart Reprovisioning

- Root cause: `resetCart()` nulls `cartId` in Redux on order detail pages (correct behavior — paid cart abandoned)
- No mechanism existed to provision new cart before user navigated to booking page
- `withCartValidation` HOC creates cart on demand but trip/search pages are NOT wrapped with it
- Fix: `pages/orders/[orderid].js` + `pages/guest-order/[orderId].js` — call `createCart()` fire-and-forget after `resetCart()`
- Auth flow: `session?.email` (not `session?.user?.email`). Guest flow: `decodeURIComponent(router.query.email)`
- Commit `3c89bff` on branch `260513-refactor/payment`
- Pattern added to `payment-integration.md`: "Cart Reprovisioning After Payment Reset"

## [2026-05-17] fix | PAYMENT_PENDING 409 on Step Navigation — 5 Bugs Fixed

- Root cause: `formStep === 2` guard fired `savePassengerAssignmentsToCart` in non-mixed flow (step 2 = Confirmation, not Assignment) → 409 with pending charge
- Fix 1: `index.js:805` — added `&& hasMixedPassengerCounts` guard → non-mixed flow never PATCHes cart items on step 2→3
- Fix 2: `index.js:256-261` — removed premature `isPaymentLocked` reset effect (fired on same render cycle as lock was set, nullified it)
- Fix 3: `FormCard.js:41` — added `|| isPaymentLocked` to `shouldDisableNext` → Next button disabled when payment locked
- Fix 4: `index.js:767` — added `if (isPaymentLocked) return` at top of forward nav → navbar step-click also blocked
- Fix 5: `index.js:983` — `onUnlockPayment` now calls `refetch()` to invalidate stale cart cache after cancel
- Bonus: `FormCard.js:46` — `getValidationErrorMessage` now returns correct message when `isPaymentLocked`
- 3-agent team: debug-specialist + code-reviewer for diagnosis, 3 fix agents in parallel, reviewer verified all pass

## [2026-05-17] fix | session.user.email Root Bug — 3 Files Fixed

- Root bug: `pages/checkout/index.js:46` — `session?.user?.email` always `undefined` (session has no `.user` wrapper)
- `email` variable was always `null` for all authenticated users, propagated to cart query + cancel handlers
- Fix 1: `session?.user?.email` → `session?.email` in checkout/index.js
- Fix 2: `Itineraries.js` cancel handler rewritten with auth-aware Bearer token + proper guest email fallback
- Fix 3: `savePassengerAssignmentsToCart.js` dead `session?.user?.email` URL branch removed
- Updated `payment-checkout-e2e-testing-2026-05-17.md` Bug 4 resolved + Bug 5 documented

## [2026-05-17] test | Payment Checkout E2E Attempt — Failed, Manual Guide Created

- Wrote 4 Playwright specs (3873 lines total) via 6-agent team for payment checkout E2E
- E2E failed: MSW intercepts `api.smartenplus.co.th` but Playwright `baseURL` is `localhost:3000` — MSW never intercepts
- Only 1 test passed (code inspection, no API calls needed)
- E2E specs deleted (cart-lock, cancel-state-machine, qr-polling, payment-recovery)
- Manual test guide created: `docs/testing/PAYMENT_CHECKOUT_MANUAL_TEST_GUIDE.md`
- Bug fix still valid: `savePassengerAssignmentsToCart.js` chargeId extraction (commit `38c7320`)
- data-testid attrs added to Input, Textarea, Passengers, PaymentMethodSelector (still present)
- Updated `payment-checkout-e2e-testing-2026-05-17.md` in vault

## [2026-05-17] test | Payment Checkout E2E Testing — 6-Agent Team

- Spawned 6 agents to test payment checkout flows end-to-end
- 4 E2E specs written: cart-lock (11 tests), cancel-state-machine (23 tests), qr-polling (24 scenarios), payment-recovery (16 tests)
- Audit results: Frontend 10/10, Backend 10/10, QR polling pass, Cancel spec valid
- Bug found: `savePassengerAssignmentsToCart.js` missing `chargeId` in cart 409 — 1-line fix (commit `38c7320`)
- Infrastructure issue: missing `data-testid` attrs — added to Textarea, Input, Passengers.js, PaymentMethodSelector.js
- Created `payment-checkout-e2e-testing-2026-05-17.md` in vault
- Updated index.md

## [2026-05-17] audit | Payment Checkout Architecture Audit — 20/20 Pass

- Audited smartenplus-frontend + smartenplus-backend against `PAYMENT_CHECKOUT_ARCHITECTURE_REVIEW.md`
- 20/20 items validated pass (10 frontend, 10 backend)
- One medium gap fixed: `getPrimaryCharge()` sort order corrected (oldest-first → latest-first)
- PromptPay intentional exclusion from one-active-lock per architecture doc
- Created `payment-checkout-architecture-audit-2026-05-17.md` in vault
- Updated MEMORY.md (SB), `project_payments_app.md` (SB)

## [2026-05-17] retro | Payment Refactor — Session Retrospective + Vault Update

- Branch `260513-refactor/payment`: 12 frontend files (+465 lines), 7 backend files (+233 lines)
- Fixed 7 frontend gaps (F1–F6 + QR expiry) and 4 backend gaps (B1–B4) vs architecture doc
- 25/28 use cases covered, 3 partial (Phase 2: WebSocket, admin reconcile UI, webhook replay)
- 5 mistakes documented: over-broad FormCard guard, positional alert text, settings.json schema, auth email param, dual cancel surface
- Key lessons: child terminal state → parent callback, sessionStorage init after persist rehydration, auth-conditional params key off token not email, dual UI surfaces sharing chargeId must be mutually exclusive
- Updated `payment-integration.md` with 8 new patterns
- Vault: log.md updated, index.md updated

## [2026-05-16] update | Repay Failure RCA — Phase 1 + Phase 2 Complete

- User couldn't repay after refresh or cart update
- Identified 8 frontend root causes → all fixed
- Phase 2 backend: idempotency key, reconciliation endpoint, CheckoutSnapshot model, expire protection
- Frontend integration: X-Idempotency-Key header, ORDER_ALREADY_PAID handling, cross-tab cart sync
- Updated: CLAUDE.md (frontend patterns), REPAY_FAILURE_RCA.md, PHASE2_BACKEND_IMPLEMENTATION.md
- Updated: payment-system.md (vault), index.md

## [2026-05-16] bootstrap | Vault Initialized

- Created vault at `~/second-brain`
- Bootstrapped full structure: 9 folders, 3 root files, 4 templates, 4 project seeds, 4 knowledge seeds
- Seeded SmartEnPlus project knowledge from existing 550 docs (synthesized, not copied)
- Git initialized with `.obsidian/` in gitignore
- Key decisions: flat folder structure, no frontmatter, wikilinks only, no raw sources folder yet

## [2026-05-16] seed | SmartEnPlus Project

- Created `01-projects/smartenplus/` with 4 pages
- README: project overview, stack, 3-repo ecosystem
- Architecture: Pages Router, Redux slices, RTK Query APIs, component tree
- Payment System: Omise, GatewayCharge, QR polling, canonical charge rule
- Checkout Flow: SSR-disabled, cart item keys, passenger assignment, guest mode

## [2026-05-16] seed | Knowledge Base

- Created 4 knowledge pages in `03-knowledge/`
- AI Workflows: LLM Wiki pattern (ingest/query/lint), three-layer architecture
- Next.js Patterns: ISR cache, dynamic imports, RTK Query, DatePicker handling
- Payment Integration: Thai methods, Omise source types, webhook reconciliation
- Design Systems: Token approach, COLORS/SPACING/BORDER_RADIUS/TYPOGRAPHY_SCALE

## [2026-05-16] update | Backend Documentation Ingest

- Created [[backend-architecture]]: Django app structure, key models, API endpoints, Celery tasks, dev commands
- Updated [[payment-system]]: added 11 backend sections (finalize_payment, locked_amount, ExpirePendingChargeView, IdempotencyKey, WebhookEvent audit, JPY handling, polling fallback, notification dedup, status machines, charge creation order, ManualAdjustment)
- Updated [[payment-integration]]: added idempotency sentinel pattern, amount locking pattern, webhook audit pattern
## [2026-05-19] fix | Breadcrumb + CategoryMenu Tech Debt + Blog Spacing Consistency
## [2026-05-20] session-end | Recommend-route review + partial implementation — hydration issue blocking

## [2026-05-22] session-end | locked_amount db_index fix (backend #4 closed) + master-state stale item corrected

## [2026-05-22] session-end | trip SEO schema fake data fixed + dynamic sitemap phantom closed

## [2026-05-25] feat | Experiences nav category filtering — ADR written, 7 distinct categories fixed, nav 404 + empty-array fallback bug resolved
## [2026-05-25] audit | n8n webhook resend operator doc v1.1 — scrutinize audit. Findings: duplicate send on retry (major), N8N_WEBHOOK_URL required in all envs (major), payload omitted InfoFields (nit). Doc updated, implementation ready on feat/n8n-resend-webhook.
## [2026-05-25] session-end | n8n webhook deployed to production. send_booking_data moved to bookings/tasks.py, n8n webhook forwarding added, 4 commits (fa687cb+4285e70+8d88ba3+2bdf31b), 3 bugs caught pre-merge (import crash x2, orphaned try block, N8N_WEBHOOK_URL missing default). Branch→develop→main→production. Knowledge entry 04-knowledge/backend-n8n-resend-webhook.md created.
## [2026-05-27] session-end | Header search pattern review + 4 bug fixes. 3-agent team (UX/Design/Engineer) audited header. Fixed: NavDropdown WCAG contrast, HeaderSearchContext useMemo, injection effect over-firing, deleted dead StickySearchBar.js. Merged + pushed to develop (0ccf03c). Wireframe doc moved to vault.

## [2026-05-28] session-end | Header search input redesign — variant=input, white bg, fb-blue button, h-10, Plan your Thailand journey placeholder. Team debate h-9/h-11 → h-10 compromise. Search bar left-aligned in header. Header height research documented (no changes). master-state updated.

## [2026-05-28] session-end | Popular Routes no-white-bg + section/card gap fixes

## [2026-05-28] session-end | GYG split-card + all committed — 7 commits on header-redesign branch
## [2026-05-30] audit | transportation-category-audit — 3-level category system documented, Airport Transfer architecture justified, Django shell queries for inventory/booking split
## [2026-05-30] scrutinize | transportation-category-audit — 8 corrections applied: 26 not 25 station_types, TRANSFER/filter decoupled, lowest_price nullable, arrival-only gap, ZeroDivisionError guard, is_actived typo table, query_count Celery mechanism, 10% threshold is heuristic
## [2026-05-30] design | airport-transfer-redesign-spec — professional redesign spec added to audit doc: image card with IATA badge + gradient fallback, carousel mobile, serializer expansion plan, null safety requirements
## [2026-05-30] session-end | vault-only session — transport audit + scrutinize + redesign spec. master-state updated. AT-1 added as P0 next-session task. No code committed.
## [2026-05-30] optimize | vault structure fix — rogue 04-knowledge/ deleted (file moved to 03-knowledge/), homepage/ folder deleted (2 files → 01-projects/), southeast_asia doc → 02-areas/, glassmorphism → 08-archive/, 3 stale DECIDED → COMPLETED, index updated + Archive section added. Known debt: 01-projects/smartenplus/ subfolder (50+ files) violates flat schema — defer, wikilinks resolve correctly.
## [2026-05-30] session-end | #8 wrap-up — vault optimize complete. master-state updated. No code committed. Next: AT-1 airport transfer redesign (spec in 03-knowledge/transportation-category-audit-2026-05-30.md).
## [2026-05-30] audit | airport-transfer-width — 3-agent parallel audit. Root cause: inner px/mx margins (px-2 md:px-3, mx-2, mx-3) eating into max-w-[1200px] container. Fix attempt (removing all margins) broke layout — reverted. Issue unresolved. Report: [[airport-transfer-width-audit-2026-05-30]]. Next team: redesign sections as full-width with centered inner content, or accept current padding.
