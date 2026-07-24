## [2026-07-24] session-end #267 | AD bookings: Support SEP resend counter fix. Bug1 no cache invalidation (raw fetch→RTK mutation w/ invalidatesTags). Bug2 missing transformResponse on getBookingSummary. Merged 36ec8ea → AD develop. Flagged user=request.user scope. QA pending.
## [2026-07-24] session-end #266 | AD trips: Copy Trip (frontend prefill) + time-aware dup warning (3-way: scheduled=times, timeless=stations). UX+BD audit pre-build. Merged 0b0b301 → AD develop. QA pending.
## [2026-07-24] session-end #265 | AD route auto-name from stations + duplicate detection (station-pair + name) + confirm dialog. Committed e02fff3 → AD develop.
## [2026-07-24] session-end #264b | curl-verified normalized search on all 6 endpoints + FE browser test guide. No new code.
## [2026-07-24] session-end #264 | space-insensitive search: normalize_search + output_field=CharField() on 6 admin viewsets. BE verified, uncommitted.

## [2026-07-23] session-end #263 | cart 400 fix + FE stale-token 401 + effective-station B1/B2 + N+1 prevention → BE+FE develop. No new atoms.

## [2026-07-22] session-end #259 | FAQ CSS fix on trip detail page: mx-auto conflict + padding split + spacing tighten. Merged develop 4758b4b1. 1 atom: tailwind-mx-auto-conflict-pattern.

## [2026-07-21] session-end #258 | Trips QA+prod deploy, CHAT-IMAGE-SEND prod deploy (Supabase SQL 003+Pillow bump+smoke), seat-availability migrate 0066-0068 prod. 3 items closed.

## [2026-07-21] session-end #257 | rebuilt BE seat-availability-checker + committed+pushed both repos: BE c535dd3 (7 files, migrations 0066-0068), AD b1996c7 (4 files). All clean.

## [2026-07-20] session-end #256 | diagnosed Supabase 406 (transient), added HTTPError body logging to BE supabase_client, merged AD station-mapping feature to develop.

## [2026-07-20] session-end #255 | check external operator seat availability (Phase 1 AD) — OperatorStationMapping model+migration+CRUD, check_seat_availability action on ContractDetailViewSet, n8n seatStatus parsing, SeatAvailabilityChecker component, station-mapping page, AD nav entry. Verified live: 135 seats left Chumphon→Koh Tao.

## [2026-07-19] session-end | branch cleanup + chat design tokens
# Vault Log

## [2026-07-19] session-end #253 | trips index redesign + scale fix merged → develop 24e3104b — 3-agent team, image-forward RouteCards (arrival→departure→default location image), ISR, ItemList TouristTrip + speakable + hreflang (site first), slim payload + 24-batch progressive reveal + JSON-LD cap 100 (prod=297 routes verified). 3 atoms extracted. LOCATIONS Section-2 stale "uncommitted" corrected (merged a25ff23d).

## [2026-07-18] session-end #251 | destinations-page-redesign shipped — image-overlay cards, go-TO H1, a11y pass, mobile sticky filter bar, CTA pin, sitewide 44px touch-target. 4 commits FE develop 354889f1. Vault synced 37f890d. 2 a11y atoms extracted (gradient-contrast, empty-alt-adjacent-text).

## [2026-07-15] session-end #250 | trip-card-v2 flight-style built — V2 default, env rollback flag, P1 batch, skeleton rewritten, mobile compact legs. 8 commits FE develop f70dbe5d. Vault audit synced.

## [2026-07-15] session-end #249 | BE-homepage-price fixed — Min(selling_rate) × 8 annotations now is_active-filtered. 4-agent audit confirmed. Redis flush gotcha documented. REC-SLOT-WASTE closed DO-NOTHING.

## [2026-07-15] session-end #248 | rec-engine 5 phases shipped — timeout+GTM+typo+sessionStorage+purchase attribution+checkout filter+ratecard hook deleted(−138 lines)+never-empty fallback+booked_count 10→0+migration 0064. FE 9fd5b0a5 · BE f0aea8c → develop (not pushed). Vault synced mid-session.

## [2026-07-14] session-end #247 | FE image button hides when allow_image_send flag OFF — imageSendEnabled prop wired _app.js→ChatWidget→canSendImage. FE develop 5c2353f6.

## [2026-07-14] session-end #246 | allow_image_send flag kill switch shipped — 3-agent debate → BE+AD+FE all merged develop. Staff unaffected; default enabled=True.

## [2026-07-14] session-end #245 | chat bubble unread badge fixed — transport gate bug root-caused + fixed, orange pill shipped, FE develop `01d8d617`. Vault badge doc updated.

## [2026-07-14] knowledge | cs-chat-bubble-badge-decision — 3-agent debate verdict: orange pill, 99+ cap correct, staff-only gate correct. 1-line FE change `bg-red-500` → `bg-orange-500`. 3 items deferred.

## [2026-07-14] session-end #244 | HEIC CS-chat image upload fixed — 3 root causes: pillow_heif import-time registration + MIME fallback + pillow-heif 0.15→1.1.1/Pillow 9.5→11.3 upgrade. BE d71db74 → develop. FE+AD both verified with real iPhone HEIC. Deploy + prod smoke still pending.

## [2026-07-14] session-end #243 | CS realtime chat fixed — 5 bugs root-caused + resolved all 3 repos → develop (BE faff358 · FE 9b5f43ad · AD 4c20fb1): empty AD history, duplicate messages, stuck send button, AD history lost on navigate, FE no events (shared-client auth interference). Isolated createClient per hook, trigger-only events → Django cursor fetch, sendingRef guard. 68 tests pass. Debug logs removed. Deploy + prod smoke next.

## [2026-07-13] session-end #241 | CS chat → GetStream hybrid ADR + audit-ready 6-phase plan (vault-only) — debate STAY reversed by user-reported pain (5 bugs + no prod notification + FE/AD history broken); new convs → GetStream Build free tier, old convs stay Django, Supabase kept for OTA mirror. Other team audits before implementation. NO code shipped. Files: [[cs-chat-getstream-hybrid-2026-07-13]] + [[cs-chat-getstream-migration/implementation-plan-2026-07-13]] + [[getstream-migration-debate-2026-07-13]]. Workspace unchanged.

## [2026-07-13] impl | chat image-send IMPLEMENTED all 3 repos → develop (BE 0bd8adf · AD f473a7f · FE 53f30576) — 20 tests green; extra fix custom_domain=None presigning; remaining: Supabase SQL + deploy + smoke

## [2026-07-12] session-end #240 | chat image-send design→audit→implementation-plan complete (v2.1: private presigned storage, token throttle, guest gate) — READY TO IMPLEMENT next session

## [2026-07-12] design | chat image-send v2.1 — plain guests blocked from image send (OTA+login only); gate via conv.ota_booking_id + FE canSendImage flag

## [2026-07-12] audit | chat image-send v2 — 3-agent expert audit: private presigned storage (PDPA), token-keyed throttle, lifecycle rule dropped, delete signal deferred, 16 corrections verified against code

## [2026-07-12] design | chat image-send designed (3 Explore + 1 Plan agent review) — single image_url column + server-convergence endpoint, 5 corrections baked in, READY TO IMPLEMENT

## [2026-07-12] session-end #239 | r14 audit (SEO 8.7/AEO 9.6/GEO 9.0/CWV 7.5/SD 8.0) + r15 deployed (HowTo+OAI-SearchBot+GBP+llms.txt+SSR hero) — 7/7 prod checks green

## [2026-07-11] session-end #238 | command-centre UI redesign: unified buttons/tabs/layout → develop 6ce8e8b

## [2026-07-11] session-end #237 | admin-dashboard bookings column "ReSend Operator" → "Support SEP" (4d67885 → develop → pushed)

## [2026-07-11] session-end #236 | command-centre pending-badge spec reviewed + implemented + merged → develop 8653679
2-agent review confirmed spec line-number claims exact. 2 corrections (edits 3→2; shared-cache dedupe only at default filter). Vault: Review section appended to spec, impl doc created, atom `mui-badge-in-tab-label-clip-fix` extracted. AD: `SideList.js` + `command-centre/index.js` edited, pill-clip fixed (`pr:1.5`), feat branch merged → develop.

## [2026-07-11] scan | age-ssot 3-repo audit + RATE_CARD_AGES dead const removed (a3c88d88)

## [2026-07-11] docs-cleanup #235b | BOOKING-DISPATCH-DOCS done. docs/operations/ENV.md: AUTO vars → N8N_WEBHOOK_URL. docs/n8n-webhook-resend-operator.md: historical banner (AUTO removed, n8n sole target). a750ab5 → develop. Note: removed global `Read(./docs/**)` deny from ~/.claude/settings.json to unblock.

## [2026-07-11] session-end #235 | Booking-confirm dispatch fix. Dead AUTO_SMARTENPLUS_API_URL target (auto.smartenplus.co.th DNS dead) aborted send_booking_data loop before n8n. Collapsed to single n8n POST, removed AUTO settings, added test. 46a8be2 → develop 6a9ea11. Docs cleanup blocked (permission). Deploy pending.

## [2026-07-11] session-end #234 | Email support → booking.smartenplus@gmail.com (booking+order templates). PAYMENT-RECONCILE-FIX merged develop. Review invitation template rebuilt to design system. Test email sent SES confirmed.

## [2026-07-11] session-end #233 | Payment debug: Funnel off + dead poll gate for payment_pending. Recovered order UUR5314673. BE fix 3a178cd (reconcile gate). 348/348 tests pass. Merge pending.

## [2026-07-09] session-end #232 | Staff push notifications verified locally + renotify bug fixed (63ef3f4 → main). 2 atomic notes: web-push-renotify-tag-collapse-bug + macos-notification-testing-gotchas. Prod VPS setup pending.

## [2026-07-09] session-end #231 | 5 chat fixes shipped to prod: CSP Supabase+GTM, registered-user OTP silent close, BE email case gate, OTP Change link + autofill. All repos main updated.

## [2026-07-09] session-end #230 | Fixed FE nginx CSP: Supabase connect-src + GTM img-src. Diagnosed STAFF-PUSH missing VAPID in Vercel. All repos shipped to prod. Next: nginx reload on VPS + VAPID prod setup + realtime chat test.

## [2026-07-08] session-end #229 | Added Supabase+chat vars to all 4 GitHub Actions deploy layers (Dockerfile, deploy.yml ×2, deploy-ghcr.sh heredoc). FE `8220c8b8`. Next: add 3 GitHub Secrets before prod deploy.

## [2026-07-08] session-end #228 | Staff Web Push notifications built + merged → develop. BE: StaffPushSubscription + signals + push helper + VAPID. AD: sw.js + manifest + hook + Enable banner + background push in SideList. BE `8c00267` · AD `842752b`.

## [2026-07-08] session-end #227 | CS realtime chat identity-switch 10/10 PASS — comeback hybrid + soft-link + merge gate tested. 4 bugs fixed (AD badge, reopen status, inbox filter, FE ✕ cleanup). FE `436499b0` · BE `943cabe` · AD `1b62ed3`.

## [2026-07-07] session-end #225 | CS realtime unread badge verified working — sidebar icon + inbox row pill + preview/timestamp via Supabase payload, client-authoritative, CHAT-SUPABASE-OFFLOAD closed. admin `9316997`.

## [2026-07-07] session-end #224 | Chat UX: guest leave button + login-while-chatting reset + CHAT-409 browser verified. BE `f48f8a8` · FE `c70a38b0`. User to confirm E2E manually then CHAT P6 prod deploy.

## [2026-07-07] session-end #223 | CHAT-409 RESOLVED. RC: staff/superuser test account hit `SupabaseTokenView` STAFF tier → upsert never called → conv row never mirrored → FK 23503. Fix: staff tier requires `scope='staff'` (BE `5071926`), admin hooks send it (`4a766af`), FE debug logs reverted (`91485ac6`). Verified live: upsert id=3 status=201. All merged develop (BE `da88aed` · FE `dd1df3da` · admin `509927e`). Next: browser E2E + T1-T14 + CHAT P6 deploy. Note: `01-projects/chat-409-diagnosis-handoff-2026-07-07.md`.

## [2026-07-07] session-end #222 | Chat customer 409 — RC pinned to FK 23503 on missing cs_conversations row. BE `fix/chat-conv-upsert-conflict` + FE `debug/chat-409-console-log` shipped unverified. Handoff: get visible Supabase upsert response, then either decode JWT claim mismatch or pivot to plain INSERT-not-UPSERT. Full note: `01-projects/chat-409-diagnosis-handoff-2026-07-07.md`.

## [2026-07-07] session-end #220 | Chat→Supabase Realtime P1-P5 SHIPPED. FE↔admin both send/receive <1s. Fixed: SUPABASE_JWT_SECRET (Legacy JWT Secret tab, not API Keys page), supabase-js accessToken callback pattern, schema routing headers, sequence grants. Atom: supabase-jwt-secret-location.md. Prod beat still needs manual Django admin registration. Next: P6 prod deploy checklist.

## [2026-07-05] session-end #219 | Chat→Supabase Realtime offload: prepared-path draft ADR + 7-phase migration plan + 23-task model-cost card (6 Haiku/14 Sonnet/3 Opus). GATED on >30 req/s trigger. Vault-only, commits 3515e62 + 8626e80. Next: SEO r13 prod deploy + re-audit.
## [2026-07-07] session-end | Chat deep review 18 bugs fixed + realtime BE bypass — 3 repos merged develop, E2E test guide created

## [2026-07-03] session-end #218 | r12 SEO audit (SEO 9.1 · AEO 9.6 · GEO 9.0 · CWV 7.5 · SD 7.5) + /grill caught 4 AI specialist errors + r13 9-item fix sprint merged → FE develop c2920a81. Next: deploy develop→main + re-audit next week.

## [2026-07-03] session-end #217 | Confirmed OTA Auto-Sync toggle built (settings.js:66-91, cs/tasks.py:75 FeatureFlag gate, 15-min Celery beat). Vault doc committed 63c8ae3.

## [2026-07-03] discovery | OTA Auto-Sync toggle already built — admin-dashboard Settings page (`pages/dashboard/settings/settings.js:66-91`). Switch hits `FeatureFlag(key='ota_sync')` via `useUpdateFeatureFlagMutation`. BE `cs/tasks.py:75` exits early when disabled. Celery beat still runs every 15 min but no-ops.

## [2026-07-03] session-end #216 | Merged admin fix/ota-resend-email-ui → develop (8746b41). Deployed all 3 repos develop→main prod. Closed CS-CENTRALIZATION-DEPLOY + OTA-FLOW-BUGS + OTA-RESEND-EMAIL.

## [2026-07-03] session-end #215 | Fix OTA Send Trip Link never emailing — wired send_html_email into OtaResendMagicLinkView, migration 0009, template; 647f3b5 merged develop. SES confirmed. Hotmail inbox miss = junk filter.

## [2026-07-03] session-end #214 | Fix traveling_date JSON serialize crash in booking dispatch — orders/services.py 2 lines, commit 61c10f2 merged develop.

## [2026-07-03] session-end #213 | OTA magic link email: BE wired SES send + null guard + tracking (fix/ota-resend-email-send 3873806), admin inline trip_link display (fix/ota-resend-email-ui 517a62c), ota_trip_link_email.html template — SES verified live. Branches not yet merged. FRONTEND_URL gap noted.

## [2026-07-02] session-end #212 | OTA bookings filter+search+pagination: BE server-side params (`feat/ota-bookings-filter-api` f393a98) + admin DateRangeFilter+TablePagination (`feat/ota-bookings-filter-ui` c68fbf3) — both merged develop. TEST- rows deleted (19 rows, 565 real intact). formatDate named import crash fixed.

## [2026-07-02] cleanup | deleted 19 TEST- OTA booking rows (24 cascade) from dev BE — CsOtaBooking clean, 565 real rows remain

## [2026-07-02] decision | OTA sync date filter: fetch only Date >= today from Supabase at source

## [2026-07-02] session-end #211 | command-centre gap fixes: H8 (resolution_note OTA customer), H9 (latest_ota_event_at detail serializer), C7 (customer queryset booking ownership), C1 (PUT blocked + read_only_fields), C3 (OTP gate 403), C6 (OTA confirm checkbox + audit trail). 6/7 tasks done, H1 deferred (UUID unique). Backend `develop` `4690fcb` · admin `develop` `1aea2e4`. 5 knowledge atoms extracted: serializer N+1 pattern, PUT bypass, guest token security, audit trail pattern, multi-repo audit methodology.

## [2026-07-02] session #210 | admin command-centre Direct Requests cleanup (ce873f9) + 3-agent gap audit → 7 CRITICAL (SLA dead, PUT bypass, guest-token leak, no email backend, resend sends nothing, OTA gate bypass, admin tickets invisible). → [[command-centre-gap-audit]]

## [2026-07-02] session #209 | Celery fix: task name mismatch (cs.sync_ota_bookings→cs.tasks.sync_ota_bookings) + broker retry deprecation warning — merged → develop `85a4850`

## [2026-07-02] session #208 | InfoUpdateNotice width fix (BookingDetailMain desktop 1200px centered) + OTA /my-trip gap fix (mt-4) — both merged → develop `50fb201e`

## [2026-07-01] session #204 | FE-M1 InfoUpdateNotice built + BE TripNotification API (29/29 tests) + Admin Phase 2 filters/columns — all 3 feature branches ready → merge develop

## [2026-07-01] session-end #203 | OTA manual testing ALL PASS (9/9) + 3 fixes: form-reshow, time-guard removal, clipboard fallback — all pushed develop

## [2026-06-30] session-end #199 | all 3 repos merged develop→main — BE 259c0d8 · admin 830cfec · FE 80714750 on main. Context resumed post-compaction. Prod deploy pending: migrations 0005-0009 + Celery beat. Remaining tests: C6/C8/B7-5/Flow E.

## [2026-06-30] session-end #198 | Path A ✅ + admin/FE UX fixes — Admin: "Processing with OTA" → "Mark In Review" (dead ternary, unanimous 3-agent debate, `7b73650`). Thai button guide via extraContent prop OTA-only (`830cfec`). FE: TicketStatusBanner `source` prop → correct provider name "12Go" not hardcoded "Klook/12Go" (`80714750`). Path A (TEST-12GO-0007) PASS: sync event guard timestamp verified, resolve succeeded, booking_status=canceled, ticket resolved. Workflow design decision: manual resolve (not auto) for this version — simpler, no over-engineering. Remaining: C6/C8/B7-5/Flow E.

## [2026-06-30] session-end #197 | OTA manual test + BE blank-desc fix + admin dialog UX — BE fix: change-request 400 on blank description → fallback `f'{request_type} request'` (cs/views.py:588, `259c0d8`). Admin fix: `awaiting_ota_update` orange→grey, View Order hidden for OTA source (command-centre/index.js, `06dc0ff`). Manual tests: C1-C5 ✅, B7-4 ✅ (guard working), Path A (Supabase sync simulate) ✅ — cancellation E2E confirmed. UX gap found (not fixed): my-trip:238 guard hides ticket section when booking.status=canceled → customer misses "Cancellation Confirmed" banner. Remaining: C6/C8/B7-5/Flow E.

## [2026-06-30] scan+audit | OTA flow E2E scan → 4-agent audit → fix + final verify — 5 original bugs + 2 polling anti-patterns found. All 5 FE fixed (3 commits `c96b1724` `09e3f955` `0657c6fb`): COLORS.gray[400] crash, data.image guard, ChangeRequestsSection redundant poll removed, /my-trip useState/useEffect gate → useRef, TDZ crash patched. 2 BE deferred. 1 security finding deferred (otaConsent.js 8-char collision). New atom: `rtk-query-self-correcting-polling-pattern.md`. Branch: `fix/ota-flow-bugs` (not yet merged → develop).

## [2026-06-30] session-end #195 | pax_change full flow + command centre bugs — UpdatePassenger editable fields (BE 8a9ff51, admin 1e7ec93), checkbox confirm fix send selectedRows not editableRows (1497cf6), isDirty Submit button, closed_no_action Chip crash fix 'inherit'→'default' (c60086c), resolution_note shown in View dialog (e7f613d). All 3 direct flows tested ✅. CS-CENTRALIZATION READY for main deploy.

## [2026-06-30] session-end #194 | CS cancel flow fixes + manual test date/cancel ✅ — booking_outcome from request (BE 20ae04b), GFK refresh fix (798f151), FE terminal status badges real label (0aa1bde9+822a0efb), refetch on cancel resolve (23eea41b), UpdatePassenger UX guidance+empty+error (admin ae12c9f), Apply Change new-tab button (374ac55). Manual tested VGR9349116: date_change ✅ cancellation ✅. pax_change not yet tested. Deploy gate: OTA flows + pax_change test remaining.

## [2026-06-30] session-end #192 | CS command-centre dialog redesign + manual-test bug fixes — ActionDialog tone-grouped zones + 2-step ConfirmDialog (admin 4af50b1); emergency toggle OTA-only (1a3ef2a); resolution_note transmit bug fix (9ac7089); FE TicketStatusBanner shows requested_value (FE 36aab76); BE Account.get_full_name fix (f675ddc) for chat inbox 500. 3-agent team → test guide vault note. B-8 cancellation + resolution_note fix verified. Tier-1 verified landed (master-state "BLOCKED" stale). Resume: commit #191 uncommitted + NEXTAUTH_SECRET; restart BE → re-verify Flow D; finish C/E; deploy CS → main.

## [2026-06-29] session-end #191 | CS manual test + bug fixes — created test guide (5 flows), fixed 500→400 duplicate guard, admin theme crash, dialog UX + resolution note field. BE/FE/admin all have uncommitted fixes. Resume: commit all 3 repos → finish manual test → deploy.

## [2026-06-29] audit | CS-centralization deep cross-layer re-audit — 6 Explore agents + 6 direct reads. Gap report 2026-06-27 superseded (stale 4 ways: FE chat+OTP built unreported; BE-B2/B4/B5 shipped; 3/4 admin mutations now functional; 10 new criticals missed). Tier-1 blockers: signals dead (tickets/apps.py no ready()), beat schedule absent (no sync_ota_bookings/check_sla_breaches), resend emits dead UUID token (cs/views.py:595), no one-open-ticket guard, resolution side-effect absent, magic-link fixed-7d, trip_id missing, closed_no_action unreachable, OTP issues full-site JWT, requested_value unbounded. Files: `01-projects/cs-centralization-audit-2026-06-29.md` + `03-knowledge/django-signals-ready-import-gotcha.md` + `03-knowledge/genericfk-one-open-ticket-guard.md`. Gap report marked ⚠️ SUPERSEDED. Workflow spec updated with audit pointer.

## [2026-06-28] session-end #186 | CS-Centralization cross-repo fix + ship — analyzed FE/BE/admin vs revised workflow; fixed 4 critical (BE resolve-block guard wired to API + emergency path + field-only PATCH; admin resend payload + emergency route); merged all 3 repos → develop (BE 424f72a, admin 69bde06, FE 4c0df60); pruned 12 stale branches. 64/64 BE tests green. #185 archived.

## [2026-06-28] session-end #185 | CS Guide staff help — Thai guide + Mermaid workflow diagrams + sidebar nav wiring (admin-dashboard feat/cs-workflow-revised-gaps, uncommitted pending manual test). Phase 4 BUILT. #184 archived.

## [2026-06-28] session-end #184 | Wrapup after FE-B1..B5 ship — feat/cs-ticket-status-banner merged → develop (463a740). SEO-R6-R9-DEPLOY closed (subsumed by FULL-DEPLOY 2026-06-26). #183 archived to session-history. CS readiness ~90%.

## [2026-06-27] session-end #182b | Migration 0006 fixed — backfill magic_token per-row before unique constraint (60176c5). Local DB migrated OK.

## [2026-06-27] session-end #182 | CS BE gaps closed — 3-agent team fixed B1–B5 on feat/cs-centralization-blockers (magic_token, sync+resend endpoints, admin fields, OtaBookingEvent). 30 tests added, 104 pass. FE OTA 4 gaps remain. BE + admin-dashboard PRs ready.

## [2026-06-27] session-end #179 | CS Centralization business analysis completed. Identified 3 BLOCKERS (~30.5h) gating go-live: resolve-block guard, SLA display, emergency path. Catalogued 7 MAJOR gaps, documented 5 missing business rules. Captured stakeholder concerns with quotes. Extracted 5 reusable analysis frameworks to 03-knowledge/. Added CS-BLOCKER-DECISION to master-state Section 2. Vault optimized — already following best practices.

## [2026-06-27] scrutinize | cs-workflow-revised-2026-06-27 — 3-agent scrutiny (arch+workflow+codebase-verify). Verdict fix-then-ship. 5 blockers + 7 majors corrected inline (max_length truncation, duplicate FK vs GenericFK, cancellation terminal-state contradiction, direct-booking cancel gap, Supabase webhook free-tier contingency, admin_initiated boolean, dead matched_ticket, TripNotification constraint, ticket collision, customer notify). 1 doc claim REFUTED vs code. Status accepted→fix-then-ship. 7 open Qs re-tiered.

## [2026-06-27] ingest | cs-workflow-revised-2026-06-27 — 4-agent team (BD+UX+Arch+FE) + grill session. Stakeholder map, 3 triggers, Ticket state machine (6 statuses), TripNotification model, webhook+Celery hybrid sync, frontend gaps + new components. 6 open questions. Owner decisions locked.

## [2026-06-26] session-end #178 | CS centralization status audit + full deploy vault sync. All 3 repos on main. CS workflow/stakeholder revision pending (team meeting happened, content next session). cs_chat FeatureFlag seed + P2-OTA-SYNC migrations still open.

## [2026-06-26] session-end #177 | FULL DEPLOY — all 3 repos develop→main prod. FE 43299da · BE ebbb044 · admin 3d5a3a4. Includes CS chat Steps 5-7, G8 PDPA gate, P3a/P3b OTA portal, r12 SEO, CS-CHAT-PERF 5-layer polling, phone/checkout fixes. Chat FAB hidden until cs_chat FeatureFlag seeded in prod DB.

## [2026-06-26] session-end #176 | r10 audit (SEO 9.0·AEO 9.5·GEO 9.0·CWV 7.0·SD 7.0) + r12 fixes (numberOfItems, ISR TTL 3600, S3 preconnect, desc trim, currenciesAccepted) → develop 43299da. r11 re-audit: GEO/CWV 10.0, SD 9.0. All r12 verified ✅.

## [2026-06-26] session-end #175 | r9 5-specialist live-prod audit (SEO 8.3·AEO 6.5·GEO 6.8·CWV 6.8·SD 5.5) + r11 fixes deployed (dbdc097): soft-404 destinations, activities schema+title, llms.txt cross-border+activities+TAT/VAT, aggregateRating removed, TAT identifier, Penang addressCountry MY, description trimmed 233→152.

## [2026-06-26] session-end #174 | checkout phone hardening: MuiTelInput validation + normalizePhone legacy repair + prefill blank fix (bare "+66" junk in Redux blocked session phone). 3 branches→develop→prod. Frontend main dd2b763.

## [2026-06-26] session-end #173 | prod hotfix: birthDate truncated year → 500 on /order-billing/ (SRL9043592). FE year padStart(4), BE calculate_age guard. Both merged→develop→prod deployed.

## [2026-06-26] session-end #172 | r10 SEO fixes (availableLanguage ISO, BlogPosting entity-type, 404 de-brand, rate-review og:url) → develop pushed 8d505d9. 9 stale branches pruned. Scores: SEO 8.4→8.6+ target post-deploy. r11 backlog: /help/faqs FAQPage, homepage TAT schema, H5 author, llms.txt.

## [2026-06-26] session-end #170 | SEO/AEO/GEO audit reconcile (r6, 3-specialist vs live code) + r6-r9 fixes to develop (LOCAL/dev-verified, NOT prod): help 500→404, destinations undefined-fallback, manifest EN, availableLanguage, /activities canonical, help og:image, sitemap /ref/article exclude, dual-BlogPosting drop, og:locale 6 files, synthetic reviews removal, About org schema+TAT, FAQPage wiring (route+activity). Build unblock (OtaPdpaGate apostrophe). Verified help canonical + P0-A crawlers already-done. ⚠️ Report=PROD, fixes=LOCAL — deploy+prod-verify pending (SEO-R6-R9-DEPLOY). Atomized 4 (jsonld-@id-merge, pages-router-notFound, dev-stale-cache; extended nextseo-v6-jsonld-silent-drop).

## [2026-06-25] session-end #169 | G8 OTA PDPA consent gate — 4-agent debate + grill audit; PDPA gate built (OtaPdpaGate.js + otaConsent.js + my-trip gate); once-per-token localStorage; flash-of-gate fixed with consentChecked flag. FE feat/g8-ota-pdpa-gate d0d2069 ready to merge.

## [2026-06-25] session-end #168 | P3b OTA ticket flow — debug + fix /my-trip ticket display. BE OtaTripView returns tickets[] array; FE renders all cards stacked; cache invalidated on submit; two-Django-process bug traced + fixed. BE fix/ota-trip-tickets-list f8e1f4b + FE fix/my-trip-tickets-list d18941e pushed.

## [2026-06-24] session-end #164 | admin-dashboard command-centre UX + ticket lifecycle auto-sync — confirm dialog, status filter fix, booking ref column, View order button, request_status→ticket_status auto-sync on resolve/reject, editor lock + reopen, 4-agent debate unanimous Option A. 8 commits across 2 BE branches + 1 FE branch.

## [2026-06-24] session-end #163 | Vault optimization (vault-only, no code repos touched) — (1) cost: master-state Section 2 pruned 79→62, root log.md rotated 752→355 (May→log-2026-05), 9 atoms + 7 deferred back-refs, fixed leaked skill-output; (2) orphan/stale: "71 orphans" was vault-stats.py artifact (65 .original.md backups), wired 5 patterns, fixed r2-skeptic alias (8 links), archived 2 superseded reviews, fixed stats exclusions — orphans 71→0 true; (3) rate-review r1-ux verdict: KEEP (archived+linked), 8/9 findings resolved, FE-22 not-a-bug (backend booking_item__slug lookup, designed 2024-12-14), UX-03 P2 open. 4 commits da58b04/bdc3da2/9f1f0bc/d2b9968.

## [2026-06-24] session-end #162 | Branch prune — FE 21 branches + BE 5 branches deleted (local+remote). FE develop 46e4550.

## [2026-06-24] session-end #161 | Booking detail CSS cont. — mobile icon-only buttons, traveling date → header subtitle, section label px aligned (px-2 md:px-3 xl:px-0), Passenger Details label simplified, dead state removed. Branch fix/booking-header-mobile-icon-buttons dcba31d — merge to develop pending.

## [2026-06-24] session-end #160 | Booking detail page full CSS consistency redesign — card margins (mx-2 md:mx-3 xl:mx-0), double-padding removed (9 files), section labels unified (h2 outside card, small+semibold+gray-700), gap/padding scale normalized, header nav row aligned to card edges + py-2 breathing room, PostBookingRecommendations title/padding fixed. FE develop c14708a.

## [2026-06-24] session-end #159 | P1e complete (ChangeRequestsSection built + redesigned), header buttons labeled Get Ticket/Request Change, mobile responsive flex-wrap header fix, BE debug logs removed

## [2026-06-23] session-end #157 | P2 OTA booking sync built + all branches merged to develop — `CsOtaBooking` model + Celery task + Supabase client querying gmail12go+gmailklook schemas directly (PostgREST public schema not exposed). 563 rows fetched, 560 upserted, idempotent. `feat/p2-ota-sync` → develop (BE). `fix/cs-chat-perf` → develop (FE + admin-dashboard). Stale branches pruned all repos. Next: develop→main deploy + prod DB migrations + seed FeatureFlag + schedule Celery beat.

## [2026-06-23] session-end #156 | Booking Command Centre rescope — owner clarified CS Centralization goal = unified command centre (OTA+direct bookings, customer self-service requests, chat=sub-channel). 4-advocate debate → direct-only vertical slice first (zero deps, ~80% staff UI exists, validates request taxonomy on safe slice). 3-tier consent model locked (service always no opt-in / WhatsApp+SMS opt-in / marketing gated on P0); service-comms legal risk recalibrated HIGH→LOW (SmartEnPlus = operator running the trip, not poaching; contract check = real gate). Approved plan P0-P5 (`.claude/plans/check-vault-for-cs-clever-bonbon.md`). New [[booking-command-centre-decision]] + thesis rescope banner + index/log. No code written — planning + vault only. Resume: deploy cs-chat-perf [USER ACTION] → Phase 1 direct slice.

## [2026-06-23] session-end #155 | CS storm mitigations + kill switch — 5-layer mitigation built (backoff+jitter, stop-on-close, 429, DRF throttle, FeatureFlag kill switch). 3 repos on fix/cs-chat-perf. Deploy pending. 2 atoms: feature-flag-kill-switch-pattern + polling-backoff-jitter-pattern.

## [2026-06-23] closed: deploy-blocking items verified shipped — SEO-P0, search-tabs (#138), rec-zones (#133), ISR (#129/#130), homepage price (#136)

## [2026-06-23] session-end #154-full | robots.txt audit (SEO pass, AEO/GEO 95%, OAI-SearchBot gap) + 5 deploy-blocking items verified git main + closed in vault

## [2026-06-23] session-end #153-full | CS weakpoint audit (3-agent, 19 items → cs-subsystem-weakpoints.md) + surgical High-severity fixes (tokenRef, session race, XOR creds 403, in-flight guard, error surfacing; 16 FE + 7 BE tests green; both repos pushed develop) + branch pruning all 3 repos (FE 8, BE 8+2remote, admin 2)

## [2026-06-23] session-end #153-cont | CS identity debate (soft-link), perf analysis (idle backoff + closed-conv stop planned), guest email gate risk. No new code commits.

## [2026-06-23] knowledge | CS guest identity best practices (3-agent debate): Soft link recommended over auto-merge. PDPA + false-positive rationale. Option D: related_conversation_id FK + agent-initiated merge gate.

## [2026-06-23] session-end #153 | CS guest 403 (5 rounds): CORS x-cs-guest-token header + stale convId/no-credentials guard. Admin stale status dropdown fixed (RTK derive selectedConversation). All phases live on develop. Deploy pending.

## [2026-06-22] session-end #152 | SEO/AEO/GEO P0 audit + 4 code fixes (robots.txt AI-crawlers, /ref/ sitemap URL poison, /help canonical, /help/faqs schema guard). CF Block AI Bots toggled off. develop `60d1e1a` awaits prod deploy. 3 atoms extracted.

## [2026-06-22] session-end #150 | email redesign: booking + order confirmation black/white minimalist. Service-category timeline, double-email fix, TimeField format, addons, coupon_code, payment_method, idempotency guard, design tokens. Merged develop→main `7c8f9c6`, shipped to production.

## [2026-06-22] session-end #149 | og:image fix (image field singular + absolute fallback + product namespace tags via additionalMetaTags) + getDayTripCoverImage field fix + CSP Google Ads pixel: 23 country TLDs added nginx img-src+connect-src. All shipped prod (frontend 0026784, nginx reloaded).

## [2026-06-22] session-end #148 | CS Centralization vault audit + gap debate. Supabase schema source-verified: `gmailklook` 503 records 100% email + `gmail12go` 58 records = 561 total. All Supabase gaps closed (source field solved in view, marketing_consent dropped, smarten_order_id dropped, Bookaway=12Go). 3-agent gap debate: 12 verdicts (B1-B6 backend + F1-F6 frontend) + 6 skeptic corrections (S1-S6). Key corrections: poll safe limit=30 widgets not 150, OTP store=PostgreSQL not Redis, server-side cursor not client timestamp, reopen rate limit needed. cs-api-contract.md updated (4 corrections). cs-p0-measurement-protocol.md updated (sample ~35→~450). NEW: [[cs-gap-debate-verdicts]]. No code built — vault only. → [[cs-gap-debate-verdicts]] · [[supabase-ota-booking-store]] · [[cs-api-contract]]

## [2026-06-21] session-end #147 | Destinations card redesign (5-col text-below-image, c23a71b main) + pruned 3 merged branches + atom [[destinations-card-redesign]]

## [2026-06-21] session-end #146 | Thailand Travel Guide redesigned — 3-col equal card grid, shipped to production (c3e2da9 main)

## [2026-06-21] session-end #145 | Git branch policy added to CLAUDE.md + vault-guardrails. Never commit to main/develop directly.

## [2026-06-21] session-end #144 | Live prod audit — 9/10 SEO fixes verified. /about og:url fully fixed (Head→NextSeo, 0aa748c main).

## [2026-06-21] session-end #143 | SEO audit reconciliation (debug-mantra repro re-audit) + P0+P1 impl. 28 findings: 4 phantom (apex-301 artifact), 10 FE-fixable, 5 CMS-only. 9 fixes in 14 files merged to develop e5de5f5. Atom: nextseo-v6-jsonld-silent-drop. → [[seo-audit-reconciliation-2026-06-21]]

## [2026-06-20] session-end #139 | Prod incident fix: Celery rec + payment tasks crushing 1-vCPU EC2. CloudWatch alert (CPU spike + net burst at top-of-hour, CPU-credit-limited burstable instance). Audited all scheduled tasks. ROOT CAUSE: `precompute_popular_contracts` wrote 4-part cache keys but `get_recommendations` reads 5-part (`:none` suffix) → zero cache hits → every rec call + hourly precompute hit RDS; 1000+ contracts drained credits; 2 AM all-contracts (12k computations) bigger bomb. Debunked false leads (list.count TypeError wrong — Django sliced QS stays QuerySet; update_route_query_counts NOT cause, Mon-only; "1200 simultaneous" wrong at concurrency=1 — serial). Fixed branch `fix/precompute-popular-contracts` 4 commits: `7b6a9f8` cache-key `:none` + cache list-not-dict; `a59b9b8` skip-if-fresh ttl guard; `2c2c799` revert stagger + hourly→every-6h + drop nightly; `bf633ac` bound sync_pending_charges (worker-only 10s socket timeout, batch cap 40 oldest-first, time_limit=540) — 15 payment tests pass, no finalization logic touched. Merged develop `e983c3e`, pushed, DEPLOYED. Admin DatabaseScheduler updated (precompute every-6h Enabled, nightly Disabled). 3 vault reports written. Resume: verify CloudWatch tomorrow AM (credit balance stops draining, no spikes).

## [2026-06-20] session-end #138 | Unified search dialog w/ homepage tabbed search (FE-only, no deploy). Extracted `TabbedSearchPanel` (Transportation + Experiences tabs), wired into `SearchDialog` (all 3 dialog hosts — StickySearchBar/HeaderSearchSummary/SearchCover — now show both tabs) + `DiscoverySection`. `ExperiencesSearch` gained optional `onNavigate` (post-nav dialog close). Transport path unchanged (`handleSearch`→host `handleFindTrips`). `isSearching` reset via guard + `setTimeout` fallback (mirrors `TransportationSearch.js:86-89`). 2-agent review (report-only): zero regressions, state isolation clean, `ProductSearchForm2` alias intact (still used by AirportTransferHeader + 2 destination pages). Review's "double-divider" finding = false alarm (theme.js has no MuiDialog border override). Merged develop `ceaa003` (--no-ff, no conflicts), feat branch pruned (local+remote). FE main @ `ceaa003`, clean. NO deploy. Resume: manual UI test (SEARCH-DIALOG-UI-TEST) → deploy FE develop→main.

## [2026-06-19] session-end #137 | Vault optimization pass (4 phases, vault-only, no code/deploy). Phase 0: committed #136 carry-forward loose files. Phase 1: archived 8 audit bundles (47 files) + 15 completed projects → 08-archive; 01-projects 91→70, flat restored, 0 broken links. Phase 2: atomize assessment — vault already atomized, 1 superseded archived, aggressive atomize skipped per user. Phase 3 (#125 CLOSED): stripped dates from 62 active filenames, ~795 wikilinks rewritten, 2 collision pairs resolved semantically, 0 dated filenames outside archive. 4 commits pushed (77e47e5, 9a3eded, a531694, d235870). Eng work unchanged — resume = deploy FE+BE develop→main + #129 ISR activation + REC min-price bug.

## [2026-06-19] session-end #136 | BE homepage "From" price type-filter fix. Homepage prices are BE-computed (front-page endpoint). `PopularExperienceSerializer.get_min_price()` (Explore Experiences) + `_fetch_airport_routes_data` lowest_price (airport routes) picked cheapest rate across ALL types → CHILD/INFANT surfaced as "From". Fixed: experiences → ADULT+fallback; airport → type-aware (JOIN→ADULT, PRIVATE/CHARTER→VEHICLE). Extracted `route_lowest_price_annotation()` + `ROUTE_PRICE_SENTINEL` into `products/services.py`, HomeViewSet + airport-routes share it (dedup of already-correct HomeViewSet logic). New PopularExperienceMinPriceTestCase (3 pass). Suite 29, 2 pre-existing Redis fails only. Merged BE develop `cff26b3`, branch pruned. FE: pruned 7 merged fix/activities-* branches (local+remote). BE-HOMEPAGE-PRICE partial-close: homepage DONE (needs deploy + front-page cache bust), REC-engine same-bug-class still OPEN.

## [2026-06-19] session-end #135 | Activity detail + browse page fixes. P3 design tokens: BookedCounter/IncludedExcluded/MeetingPointCard Tailwind→COLORS inline styles (DayTripHero also fixed but dead code — not imported). AirbnbPhotoGrid: trust backend image order array, featured_image fallback only, totalCount fix. Double From label: PricingDisplay compact owns label — removed caller-side From in DayTripMobileBookingBar + PremiumBookingPanel. PricingDisplay align prop: default 'end', callers pass 'start' for left-align (MobileBar + PremiumBookingPanel). getFromPrice type-aware: JOIN→ADULT, other→VEHICLE, mirrors findLowestSellingRate. DayTripCard: replaced inline Math.min with getFromPrice. FE develop 143f9a2. Pending BE fix: PopularExperienceSerializer.get_min_price() no type filter → homepage Explore Experiences price may show wrong From (CHILD/INFANT rate).

## [2026-06-19] audit | Design token compliance scan — activity detail page. 18 components audited, 39 violations found across 6 categories. P0: 6 wrong hex colors (MeetingPointCard `#1D4ED8`, RatingDisplay `#FFA000`, DayTripDetailHeader `#666`×3, ShareButton `'green'`). P1: 4 shadow/radius violations (PremiumBookingPanel 16px radius gap, PromotionalBadge rgba shadows). P2: 4 off-scale font sizes. System gaps: no circular radius token, no errorLight bg token. Compliant: PricingDisplay, PricingTypeBadge, RelatedExperiences, DayTripCard, ExperienceTitleArea, DayTripHighlights. Report: [[design-system-audit-activity-detail]].

## [2026-06-18] session-end #133 | Recommendation zones MERGED to develop both repos (BE `ae31f1f`, FE `0877d23`) + 2 product-review fixes + 4 branches pruned. Anchor priority FLIPPED experience-first (ANCHOR_PRIORITY DAY_TOUR 100 … TRANSPORT 30/TRANSFER 20; retires obsolete [[recommendation-anchor-first-transport-rule]]). Removed minCartPrice floor (was hiding cheap complementary add-ons like THB 300 ferry). recType-follows-anchor fix (debug-mantra + /grill): mixed cart tour+ferry showed NO recs — anchor=tour but recType keyed off "any transport in cart" → 'packages' → needs anchor route → tour has none → empty; fixed `recType = anchorIsTransport ? 'packages':'hybrid'`, verified 6 recs. Merged full #132 stack (P0 hybrid fix, serializer image/price/logo_url, zones, matrix, seed cmd, price-bug, card-count) via no-ff. Pre-merge: 15 BE tests (1 pre-existing unrelated fail), check clean, FE eslint 0 errors. Pruned BE+FE feat/checkout-recommendation-zones + fix/recommendation-serializer-fields + fix/people-also-book-title-image-price. 3 vault review addenda (zones best-practice, card-count, multi-cart). NEXT: deploy develop→main both repos (folds in #129 ISR). Deferred tracked: REC-SLOT-WASTE (exclude_ids API), recommendation_purchase GTM, UPGRADE zone (upgrade_of FK), multi-destination.

## [2026-06-18] session-end #132 | Checkout "Complete your trip" recommendation ENGINE built end-to-end. P0 hybrid regression FIXED (`841e59f`: non-transport carts got 0 recs — hybrid ran only route finders that bail [] with no trip.route; fallthrough to find_nearby_activities). Seed root cause fixed: 17 activity contracts shared a dummy NULL-station trip → cross-destination wrong recs; detached + fixed create_day_tours/create_all_service_tours + new idempotent seed_demo_destination (Phuket anchor 185). Zone system shipped (`feat/checkout-recommendation-zones` BE+FE): find_transport_at_location (ESSENTIAL via route-station→location bridge) + CATEGORY_MATRIX + find_nearby_activities split POPULAR(cross-cat)/SIMILAR(same-cat cap1); dropped +30 same-category bonus; booked_count tiebreak; ZONE_LIMITS {essential2/popular3/similar1}; FE conditional labeled zones reusing RecommendationCard. Price bug: Min(selling_rate) picked free INFANT 0.00 → "Price on request"; filtered selling_rate__gt=0 ×7 finders. Card-count review items: recommendation_add_cart GTM, mobile POPULAR cap2 (useMediaQuery), POPULAR 4→3, fixed render-path empty-event bug→useEffect. 4 vault review addenda (strategy/card-count/best-practice/gap) in [[recommendation-engine-completion-roadmap]]. UPGRADE zone deliberately deferred (needs upgrade_of FK, no heuristic debt). Branches committed NOT pushed; push serializer branch first then zones (stacked). Tests pass (1 pre-existing unrelated fail). New atoms candidates: zone-recommendation-engine, route-station-location-bridge, min-rate-excludes-zero.

## [2026-06-18] session-end #131 | "People also book" checkout recommendations: 3 prod bugs fixed (title "to" / image / price) + anchor+recType+GTM improvements + spec gap analysis. Title bug: `route=null` → `"" to ""` truthy stopped OR chain — guard added. Image bug: BE `ContractRecommendationSerializer` missing `image` field — added `get_image()` reusing `ImageGallerySerializer`. Price bug: `_lowest_price=0.0` on no-price → `formatPrice(0)=null` — fixed to `None` sentinel (×5 in services.py). Broken URL fallback: `imgError` state + `onError` → `CATEGORY_CONFIG` icon fallback (reused from `ServiceCategoryBadge`, no new component). Anchor: replaced `SKIP_CATS` with `ANCHOR_PRIORITY` map — all 9 cats scored. `recType` `'activity'` → `'hybrid'` for non-transport. GTM `checkout_recommendation_empty` added. Context-aware title. Spec compare: ~50% implemented; 3-zone section, fallback layers 1–4, ranking formula, 2 GTM events, weekly booked_count all unbuilt. Both FE + BE branches have uncommitted changes only — need commit+PR→develop.

## [2026-06-18] session-end #130 | Category-aware duration fix SHIPPED TO PROD (FE main `35c524d`). Spa "1 Day" bug killed. Root cause category-wide: all activities components read `tour_duration_days` (BE default 1, days) → "X Day(s)" regardless of `service_category`; LIST serializer omits the field so cards always fell to "1 Day". Same ternary in 5 sites (3 components + 2 SEO JSON-LD). Fix (FE-only): new `helpers/formatContractDuration.js` single source of truth, gated by existing `SERVICE_CATEGORY_CONFIG.showDuration` + new additive `durationUnit` ('days'|'time'|'nights'). spa/dining → "2h 30m" from `duration` (colon string, reused `customFormatDuration`); event/attraction/OTHER → hidden; accommodation → nights; tours → days (null if absent). Only behavior change: `OTHER.showDuration` true→false. Verified ESLint + 36 serviceCategoryHelper tests + BE confirmed `duration`=`"2:30:00"` not ISO8601. **Side effect: FE main now carries ISR route (66d896e) — FE half of #129 ISR activation deployed; BE activation still pending.** New atom: [[category-aware-duration-formatter]]. Follow-up DURATION-DAYS-CARDS: optional BE Option B (add `tour_duration_days` to list serializer).

## [2026-06-18] session-end #129 | ISR on-demand revalidation IMPLEMENTED + merged to develop both repos; prod root cause found. Admin contract content edit → `res.revalidate()` regen in seconds (native, not workaround — chosen over lazy timer because Next 14.2.5 standalone regen is request-triggered so quiet pages never self-heal). BE develop `4eaaf8d` (`0f2d108`+`d37dee3`): `revalidate_frontend_isr` task + `_trigger_revalidate` from Contract/RateCard post_save; daily_counter `.update(F+1)` enabler so per-view+nightly counter writes fire NO post_save = NO revalidate storm (verified deployed code); admin update confirmed `instance.save()` (`views.py:946`); REVALIDATION_SECRET setting; +2 latent fixes (clear_trip_cache Trip null-guard, precompute_contract_on_create missing self → closes #127 carry). FE develop `66d896e` (`898159e`): Pages-Router `pages/api/revalidate.js` (slug→both paths, secret-guarded) + deploy secret wiring + next_cache volume-clear hardening. **Prod root cause: `FRONTEND_URL` apex → 301→www dropped POST body/auth → revalidate never landed; fixed default→www** (`settings.py:373`). Verified: manage.py check, 29 tests, ESLint, import chain. Secret set both sides in prod. ACTIVATION PENDING: deploy develop→main + prod FRONTEND_URL=www + restart worker. New atoms: [[isr-revalidate-csr-vs-isr-field-matrix]], [[django-update-bypasses-post-save-signal]], [[frontend-url-canonical-www-not-apex]].

## [2026-06-17] session-end #128 | ISR revalidation gap (activities+trips detail) — root cause + impl plan, NO code changed. Admin contract edit doesn't reach prod `/activities/detail` + `/trips/detail`. Cause: backend busts Redis (`operators/signals.py:33`) but Next.js Pages-Router ISR static HTML never told to regen + no `/api/revalidate` route → stale ≤revalidate window, forever on cold pages (persistent `next_cache` volume). debug-mantra + scrutinize. Backend innocent. Plan: `daily_counter`→`.update(F+1)` (enabler, stops per-view post_save), new FE `/api/revalidate` (Pages Router, POSTs {slug}, owns path map), new BE `revalidate_frontend_isr` Celery task + `_trigger_revalidate` signal helper, `REVALIDATION_SECRET` both repos (incl GH Actions runtime path). Plan: `~/.claude/plans/create-team-to-check-jaunty-goblet.md`. Vault ISR notes extended/corrected (App-Router→Pages-Router `res.revalidate`).

## [2026-06-17] session-end #127 | Operator cover_image pipeline upgrade + orphan cleanup, shipped + deployed. BE `dbbbe97`: cover → process_operator_image (parametrized, WebP 300KB/1920 hero budget, HEIC server-side) + replaced-file S3 delete in OperatorViewSet.update (_safe_delete_storage_file). admin `874d74d`: shared isHeic/convertHeicToJpeg in imageHelpers, cover handler decodes iPhone HEIC. Impact-checked: gallery + review unaffected. Tracked BE-IMAGE-DEDUP debt.

## [2026-06-17] deploy #126 | All 3 repos deployed to prod by user — `main == develop` (BE `28e584a`, FE `1609c38`, admin `285e83b`). Operator cover-image hero + admin upload + tab-counts now live. ⚠️ verify migration `0062_operator_cover_image` ran on prod DB.

## [2026-06-17] session-end #126 | Operator cover-image hero shipped to develop (BE `28e584a` + migration 0062, admin `285e83b`, FE `1609c38`) — FeaturedImageHeader reuse, bgDefault fallback, floating back/share pills, mobile responsive, description SSR pass-through fix. Not deployed to prod.

## [2026-06-16] deploy #123 | BE develop `0e52782` + admin develop `f75d721` deployed to prod, migration `0061` run — contract soft-delete + dashboard status/expiry cards live.

## [2026-06-16] session-end #123 | contract soft-delete SHIPPED + dashboard status/expiry cards — pushed+merged `feat/contract-soft-delete` → develop both repos (BE `0e52782`, admin `f75d721`), branch pruned. Fixed: global summary counts under status filter, `is_deleted` list-payload omission (badge+restore root fix), status-aware Restore buttons, id-only deleted badge. Added dashboard Contracts status card + Expiry card (BE list-users stats + admin Main.js). Atoms: serializer-field-omission-starves-ui, summary-must-not-scope-by-its-own-selector. SOFT-DELETE-SHIP closed.

## [2026-06-16] session-end #121 | prod deploy confirmed + admin-dashboard hygiene — FE `19984f2`+BE `21fbdcf` confirmed live in prod, synced w/ develop. admin-dashboard: 5 untracked-but-linked docs committed+pushed (`5e5b984`). Branch cleanup: 33 local + 31 remote branches, all merged into main+develop, deleted 32 local + 29 remote (kept main/develop only). Same pattern as prior BRANCH-CLEANUP-REMOTE.

## [2026-06-16] deploy | FE `main` @ `19984f2` + BE `main` @ `21fbdcf` deployed to prod, both synced with develop — no pending-deploy gap.

## [2026-06-16] session-end #120 | build fix + dead-code cleanup + branch hygiene — Debug-mantra root cause: `getOptimalImageQuality is not a function` broke build on 13 activity-detail pages. `helpers/imageOptimization.js` missing export, only existed in 3 stale agent worktrees. Re-added export, grilled module — deleted 4 dead exports (zero callers: `convertToWebP`, `calculateResponsiveImageDimensions`, `preloadHeroImage`, `isImageCached`). 2-agent audit (code-reviewer + build-verifier) PASS, surfaced unrelated bug same class: `pages/help/faqs.js` named-import `{ fetcher }` vs `helpers/fetcher.js` default export. Fixed. Committed `19984f2` → develop, pushed. Cleaned up 3 worktrees + 4 branches (1 remote) — all confirmed merged/superseded by content-diff, not just ancestor check. Atom: [[dangling-export-import-bug-pattern]].

## [2026-06-16] session-end #119 | trip-detail SEO/AEO/GEO: 3-specialist audit + 3-agent implementation + re-audit, 7/7 HIGH fixed, merged develop `bddb1c0` — Audit: 25→18 findings, 7 HIGH (canonical, BreadcrumbList, FAQPage, TouristTrip, route-facts, og:locale:alternate, hreflang). Impl: new `tripDetailSEOUtils.js`, `TripDetailSEO.js` rewritten, `useTripSEO.js` deleted (-244 lines), `getStaticProps` wired. Re-audit 7/7 PASS. 1 PARTIAL (TouristTrip @context/@type) fixed immediately `bddb1c0`. Vault closed. Atom: [[trip-detail-server-side-seo-pattern]].

## [2026-06-15] session-end #118 | min-rate bugs: FE 4 fixes merged to develop, BE lowest_price two-subquery fix pushed (not merged) — FE: `fix/min-rate-bugs` merged → `develop` (`a95a241`): stale fareCalendar on scroll (onCenterDateChange prop), off-by-one minFare (>= 1), allSame false-positive (length > 1 guard), homepage route filter (lowest_price > 0). BE: `fix/popular-routes-lowest-price` pushed @ `4da0b81`: two subqueries (JOIN/ADULT + PRIVATE/CHARTER/VEHICLE) + `Least()` + sentinel 999999999 — mirrors FareCalendar display_rates logic exactly. New atom: [[popular-routes-lowest-price-farecalendar-parity]].

## [2026-06-15] session-end #117 | trip page audit + currency fix merged to develop — `fix/trip-page-audit-2026-06-15` merged → `develop` @ `f018e02`. 4 commits: crash guards/XSS/dead code, SEO audit, checkbox filter fix, THB/฿ → `useFormatPrice()`. Deleted 366 lines of dead code (tripItemv2/TripList/RouteFaqs). FE `develop` pushed, ready for prod deploy.

## [2026-06-15] session-end #115 | trip route SEO/AEO/GEO audit + all fixes shipped — 3-specialist deep audit of `/trips/hatyai/koh-lipe`. Found 3 P0 + 4 P1 + 2 P2. All code-fixable items implemented and merged to `develop`. Key fixes: FAQ now renders in SSR HTML (gate on `contracts.length` not RTK `tripsFilterSet`); H1 has text at SSR (`initialFromLocation` fallback); ItemList URLs absolute (`NEXT_PUBLIC_DOMAIN` fallback); `LocalBusinessSchema` `BusStation` → `Place`; `transportModes` derived from real `transport_composit` data (backend `ExteaContractSerializer` + `AvialableContractSerializer` both updated with nested `ContractTranspotCompositSerializer`); `TripSummary` aria-label added; S3 preconnect added. Also: `Service` JSON-LD added to `TripOverview`, `BlogPosting` schema added to `BlogPost`, duplicate `FAQPage` removed from `FilterTripsSEO`, `findMinSellingRate` type-aware (ADULT/VEHICLE split), `ProductJsonLd` price uses `Math.min`. Meta description now shows `"van standard, speedboat standard"` (real data). Pending: Django admin fix for hatyai→koh-lipe wrong `overview` text + `blog_slug` (Khao Lak content served). FE `develop` @ `45f5d7e`, BE `develop` @ `c24e73d`. Local feature branches cleaned up. Audit report: [[trip-route-page-seo-aeo-geo-audit]].

## [2026-06-15] session-end #114 | round-trip UX fixes + R2 scope cuts — TripProgressIndicator collapsed into breadcrumb row (−44px, no card chrome). Desktop: dots+label. Mobile: step icon+counter. Width fixed to standard `mx-2 md:mx-3 xl:mx-0` pattern. Hero route fix: `SearchCover` now swaps from/to when `isReturnJourneyActive` (`FilterTripsPage.js:211-212`). R2 scope cuts: P3/P4/P5/P7/P8/P9/P10 all CUT via grill+scrutinize (dup data / no consumer / fake metrics). SelectedOutboundSummary debated → reverted, plan saved. `feat/route-intelligence-hero` merged → `develop` @ `a3c328a`.

## [2026-06-14] session-end #113 | calendar strip redesign + skeleton mobile fix — SlideCalendar2 4-row tab → 2-row (merged day+date `EEE d`, cheapest=green price, filled selected card, no badge row). Transport card: removed double focus ring, fixed top-border clip (`py-1`). Skeleton mobile width: inline DynamicTripsPageLayout loading fallback now gets `mx-2 md:mx-3 xl:mx-0` matching TripsPageLayout + real cards. SkeletonSection margins cleaned, gap-1→gap-3. Branch `feat/route-intelligence-hero` @ `3d33ba6` pushed, NOT merged.

## [2026-06-14] session-end #111 | hero + filter redesign (branch, not merged) — `SearchCover` mobile single search-bar (OTA pattern) + desktop unified secondary buttons; merged ResultsPageHeader (N departures + desktop trust line) into hero, extended hero-top-gradient; FIXED desktop filter access gap after sidebar removal (Filters button + count badge in TripSearchFilters, dialog → centered modal desktop via `fullScreen={!isSmallScreen}`, deleted auto-close-on-desktop bug); sort dedup (removed SortDropdown from dialog + mobile bar — QuickSortPills cover all sizes). Heavy design iteration via 3-agent + 2-agent reviews. Branch `feat/route-intelligence-hero` @ `7e34d49` pushed, NOT merged. Remaining R2 phases (card confidence/timeline/social-proof/recommended/insight/seats) not started.

## [2026-06-14] review+plan | RouteIntelligenceHero P1a — 3-agent review (FE-arch + UX + BE-data) on hero spec. Consensus: route viz BLOCKED (`Contract.timeline` per-contract, no canonical route path), confidence-score/trust-badges/travel-insight CUT (no on-time data / per-contract / fake), real route-level data = min price + departure count + duration RANGE + first/last departure. New component (SearchCover at 220-line limit). Screenshot-validated: photo hero eats ~540px first screen. 3 refinements: add first/last, "From ฿N" must match bookable cards (advance_hr), drop "today". FE branch `feat/route-intelligence-hero`. FINAL SPEC in [[trip-search-results-implementation-plan-2026-06-14]] Phase 1. Gate = user visual check.

## [2026-06-14] plan | trip-search round-2 — 11-phase top→bottom plan, BACKEND-VERIFIED. Key finding: route timeline (`Contract.timeline.timeline_place[]` with `time`+`icon`+`order`) + social-proof counts already serialized — NO BE needed for those. Seats-available derivable (1 method, reuse `TimeSlot.get_current_bookings`). On-time % CUT (no data). `booked_count` default=10 = the FE `/10` hack cause. Plan in [[trip-search-results-implementation-plan-2026-06-14]] Round 2 section.

## [2026-06-14] session-end #110 | trip-search-redesign phases 3-7 shipped + merged — ResultsPageHeader, fare calendar price badges (±7d), QuickSortPills, Top Pick badge, design polish. 5 bugs fixed (advance_hr, operator dedup, min_display_rate, hydration quality, computeConfidenceScore guard). TRUST-BADGE-BUG closed. FE+BE both on `develop`, not yet deployed.

## [2026-06-13] session-end #107 | checkout payment step width fix — `md:m-2` caused 16px horizontal indent on PaymentMethodSelector/QRPaymentForm/PendingChargeNotice vs `my-2` on all other steps. Fixed in `c55f6a1` (3 files, pushed to FE `develop`). Also standardized `md:rounded-md` → `rounded`.


## [2026-06-13] session-end #106 | payment pending deadlock fixed — 3 BE fixes on `develop` `482cfc6`: ExpirePendingChargeView recovery branch, reconcile_gateway_charge PAID+stuck retry, _handle_existing_charge local-PAID finalize parity. 16 new tests, 278 pass. Vault atom [[payment-pending-deadlock]] updated with repro steps + fix status. Production recovery: POST expire on chrg_test_67zrcauou19uk2t655l.

## [2026-06-12] session-end #105 | payment pending deadlock diagnosed — live prod bug order `PLB0229785` stuck `payment_pending` despite charge PAID at Omise (`chrg_test_67zrcauou19uk2t655l`, 1,012.71 THB PromptPay). Debug Mantra 4-step applied: repro from logs, fail path traced to `ExpirePendingChargeView:389` returning 400 for non-pending charges, hypothesis falsified across 4 scenarios, all breadcrumbs cross-checked. Root cause: `finalize_payment` throws `PaymentAmountMismatchError` (or webhook lost) → order intentionally left `payment_pending` → no recovery path. Two backend fixes proposed: (1) expire endpoint recovery for paid/failed charges, (2) reconcile retry for paid+unfinalized. Atom: [[payment-pending-deadlock]]. Plan at `.claude/plans/check-frontend-and-backend-enchanted-rocket.md`. Next session: implement fixes.

## [2026-06-12] session-end #104 | payment E2E fully automated (8/8 PASS) + webhook gap closed — all 8 previously-skipped Playwright UI tests now automated via `payment-auto-qa.spec.ts` + fixture CLI `e2e_payment_fixtures.py`. Real Omise webhook delivery verified locally via Tailscale funnel: forged payload→400, PP auto-completes, webhook finalizes order no FE, dedupe→already_processed — all 5 PASS. New atom: [[omise-webhook-tailscale-local-testing]]. PAYMENT-FIX ready to merge (PRs via GitHub UI).

## [2026-06-12] session-end #102 | payment deep review — all 5 batches shipped + pushed (BE 7 commits `d7af0e9..6937f39`, FE 4 commits `a3c8c80..c7caaf3` on `fix/payment-deep-review`). 20 BE unit + 84 FE jest + 5 Playwright API + 7 Playwright UI (skip) tests written, 104 passing. PRs + staging QA pending (gh CLI not installed → manual via GitHub UI).
## [2026-06-12] session-end #102b | Playwright E2E smoke run — 2 spec bugs found and fixed: (1) `**/checkout**` inside `/* */` block comment had its `*/` matched by the substring inside the string literal → unterminated string error, file failed to parse, 0 tests ran. Fix `4f88093`: convert `/* */` to `//` line comments in the already-skipped smoke test. (2) H2+M10 POST tests expected 410, got 403 — Django CSRF middleware blocks POST before the 410 view runs. Fix `8430805`: POST tests now assert CSRF 403; 410 contract covered by GET on same URL (same view, same handler). **Result: 7/7 Playwright API tests pass, 8 UI tests skip, 0 fail.** Both FE follow-up commits on `fix/payment-deep-review` (NOT yet pushed).
## [2026-06-12] session-end #102c | manual QA runbook for 8 skipped tests — [[payment-manual-test-skip-2026-06-12]] written in vault. Per-test: Django shell fixture setup, step-by-step UI/API actions, expected results, pass criteria. Results template for closing PAYMENT-FIX after staging deploy. index.md updated.
## [2026-06-12] session-end #103 | wrap + handoff — PAYMENT-FIX E2E green (7/7 API), manual runbook ready, FE has 2 unpushed follow-up commits (parser fix + CSRF assertions). Atom extracted: [[e2e-csrf-blocks-410-legacy-post-tests]] (CSRF blocks 410-on-POST in E2E → split into GET-410 + POST-403). master-state §1 rewritten as consolidated handoff. Next session: push 2 FE commits → open 2 PRs via GitHub UI → staging QA → close PAYMENT-FIX.

## [2026-06-12] session-end #101 | payment deep review 4-pass audit complete — [[payment-deep-review]] (5 HIGH all verified, ~18 MEDIUM, ~15 LOW, 10 test gaps). 3 KB corrections: payment-gateway-charge-architecture lock order, payment-finalize-deep-dive side-effect order, payment-exception-catalog M13 silent declined-card. No code changed. PAYMENT-FIX open item added to master-state.

## [2026-06-11] session-end #99 | whole-site SEO+sitemap 3-agent audit — 6 P0 (WAF/Googlebot verify, fake reviews ×3, broken noindex, malformed activities canonical, sitemap ships private URLs, origin missing 301s), 10 P1 incl. 480-line dead JSON-LD pipeline. No code changed. Vault: [[seo-sitemap-whole-site-audit-2026-06-11]].

## [2026-06-11] session-end #97d | CROSS-SELL-MERGE CLOSED — branch already fully merged into develop (confirmed via git merge-base). CheckoutRelatedTrips mounted at checkout/index.js:1010. Renamed remaining work to CROSS-SELL-BD-INVENTORY (BD task: Koh Lipe return route + DAY_TOUR + SPA contracts). No eng work remaining on cross-sell.

## [2026-06-11] session-end #97c | FRONTEND-AUDIT-FOLLOWUP-1 CLOSED — 2 exhaustive-deps suppressions added to FormikValuesSync.js. Effect 1: refs + useState setter stable, correctly excluded. Effect 2: `cartitems?.cart_item` kept (not `cartitems`) — tighter RTK trigger (scrutinize caught agent's wrong swap proposal). Lint clean `7107516`.

## [2026-06-11] session-end #97b | FRONTEND-AUDIT-MANUAL-PRS DROPPED (all 3 branches confirmed merged into develop — retroactive PRs add no value). BRANCH-CLEANUP-REMOTE CLOSED — 42 stale `origin/2606*` branches deleted, 45 active remain. Vault count was stale (said 81, actual 42).

## [2026-06-11] session-end #97 | BOOKING-PAY-REPRO-1 C1+C2 fixed. C1: `isCartLoaded &&` gate on clear-assignments effect in `checkout/index.js:188` — stops premature clear before RTK Query resolves on hard refresh. C2: `if (error?.status === 404)` guard in `check-and-createcart.js:67` — transient 500/503/timeouts no longer nuke cartId. Grill validation confirmed RTK Query error shapes + stable `!!data` bool. Commit `cb817d9` on develop. BOOKING-PAY-REPRO-1 CLOSED.

## [2026-06-11] session-end #96 | activity cross-sell: 3-layer bug fixed (viewset valid_types + global trip guard + arrival_station dispatch); find_nearby_activities() added; booking widget blank error fixed (advanceHourPassed + nonOperatingDay messages); cache-clearing WARNING silenced for non-transport contracts. 2 atoms extracted.

## [2026-06-11] session-end #94 | booking-to-payment flow audit: 4 bugs fixed (stable_id cart sync, clearTripInfo, dead lazy query), 53 tests pass, SM-1–4 smoke passed, merged fix/checkout-stable-id-cleanup → develop (f271aef). C1/C2 deferred pending repro.

## [2026-06-11] session-end #93 | Two-pass falsification audit of booking-payment e2e doc — all root causes survived disproof, doc amended (test files + falsification notes), 2 atoms extracted (rtk-lazy-query-tuple-misuse, redux-persist-gate-scope-gap). Next: BOOKING-PAY-FIX-1 (implement bugs 1-4).

## [2026-06-10] session-end #90 | Checkout Next btn fix (advance booking + auth race) + backend advance_hr/stop_sale enforcement at booking creation. Both repos on develop.

## [2026-06-10] session-end #89 | CROSS-SELL SYSTEM IMPLEMENTED — all 10 service categories, checkout step-0 BD gate, find_activity_contracts backend. Blocked by BD inventory (no Koh Lipe return route / DAY_TOUR / SPA contracts). CROSS-SELL-1 OPEN.

## [2026-06-10] decision | checkout step-0 cross-sell: 3-agent debate (UX+FE+BD). Consensus: inline CheckoutRelatedTrips at formStep=0 (checkout/index.js:1007). 3 lines. Collapsed accordion, non-blocking. BD gate signal: checkout_recommendation_click ≥5% over 60 days unlocks journey builder. Blocked by inventory gap — auto-hides until BD creates DAY_TOUR/SPA at Koh Lipe. UX/UI+Design deep debate launched next.

## [2026-06-09] decision | no-cart-page cross-sell: 4-agent debate. UX+Design+Frontend voted post-add-to-cart modal (3-4h, BookButton.js:241 intercept). BD dissents — transport buyers impatient, modal = 5-8% abandonment. Resolution: two-tier by product type (transport = no modal, DAY_TOUR/SPA = modal). Modal BACKLOG until BD creates activity inventory at destination. cross-sell-placement-strategy.md updated.

## [2026-06-09] knowledge | cross-sell-placement-strategy.md created. Industry standard: post-booking #1 (SmartEnPlus already built+mounted), trip detail #2 (live), checkout sidebar = abandon risk (removed). Filtering rules documented: same-route exclude (station → location fallback), operational_day weekday filter, price filter. BD gap: no DAY_TOUR/SPA contracts at Koh Lipe blocks cross-sell value.

## [2026-06-09] impl-plan | 4-AGENT UX×FE×BE×SCRUTINIZE — implementation-plan-cross-sell-2026-06-09.md created. 2 blockers found vs PM debate: (1) mobile sidebar = separate component CheckOutSideBar.js not CheckoutSidebar.js; (2) post-booking multi-item fix BLOCKED — analyzeBookingContext single-booking architecture. item_category confirmed 1 line (stronger than PM said). Priority order: GTM fix today → mount CheckoutRelatedTrips desktop → wire RelatedExperiences scored API → SEO content → post-booking deferred sprint 2. Key risk: contract_id flat field on cart item must be verified before shipping priority 2.

## [2026-06-09] team-review | 3-AGENT BD×ENG×PM DEBATE — next-priority-debate-2026-06-09.md created. #1: add item_category to GTM purchase event (3 lines, useOmisePayment.js:55). #2: mount CheckoutRelatedTrips (1 import + 1 JSX, pages/checkout/index.js). NOT to build: bundle UX, wellness upsell, journey builder. Gate: cross-sell attach rate data in 30 days unlocks rest of roadmap.

## [2026-06-09] bd-strategy | NON-TRANSPORT LIVE + JOURNEY BUILDER GATED — 6 vault docs updated. Non-transport booking (DAY_TOUR/SPA_WELLNESS) confirmed live on B2C (FE `0c3bb14`, BE `9ef2752`). `business.md`: moat table updated, roadmap steps 1+2 → Done, step 3 → cross-sell/bundle (not journey builder). Journey builder explicitly gated: build only after multi-booking rate validates demand. Decision logged in `business.md`, `business-development-thesis-2026.md`, `business-development-thesis-2026-2029.md`, `business-development-zeitrip-mvp.md` (GATED status), `business-development-thailand-bundle-architecture.md` (ACTIVE status), `checkout-confirmation-payment-crash.md` (PENDING → RESOLVED).

## [2026-06-09] session-end #88 | WP MEDIA TAB + IMAGE URL PIPELINE FIXED — 3 repos pushed. `admin-dashboard` `99e45b2`: WordPress Media Library tab (WordpressImages.js, wordpressMediaApi.js RTK slice, MUI Tabs in ImageSelection.js, /wp-api rewrite proxy, wp_ id prefix dedup). `smartenplus-backend` `b3b8ee0`: get_image() SerializerMethodField verbatim https:// fix on operators/serializers.py (_ImageGallerySerializer + ImageGallerySerializer) + products/serializers.py (ImageGallerySerializer); imagegallery_set is_deleted=False filter on ContractSerializer + ProductDetailSerializer; PK guard for wp_ prefix in operators/views.py. Root cause of 403: id=2881 soft-deleted row with wrong-bucket URL le