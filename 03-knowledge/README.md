# 03-knowledge — MOC

## Summary
Atomic concepts extracted from projects, audits, and bugs. Each note = one idea, reusable across projects. ~222 notes grouped by topic below.

## Contents

### Frontend — Next.js
- [[nextjs-patterns]] — master index of Next.js patterns
- [[nextjs-hydration-rules]] — hydration pitfalls
- [[nextjs-fixed-header-per-route]] — per-route header height
- [[nextjs-307-vs-301-product-reclassify]] — redirect semantics
- [[nextjs-isr-ratecard-empty-array-guard]] — ISR empty array guard
- [[nextjs-static-path-prop-divergence]] — static vs dynamic prop drift
- [[nextjs-fast-refresh-stale-hash-loop]] — HMR loop fix
- [[nextjs-hmr-cross-module-callback-staleness]] — HMR staleness
- [[nextjs-shallow-router-push-scroll-false]] — router scroll restore
- [[next-seo-v6-robots-prop-broken]] — next-seo v6 robots prop
- [[next-font-self-host-perf-pattern]] — font self-hosting
- [[getstaticprops-fetch-timeout-isr-blocking]] — ISR blocking fetch
- [[docker-standalone-isr-revalidate-gap]] — standalone ISR gap
- [[isr-csr-overlay-stale-fields]] — CSR overlay staleness
- [[isr-client-rtk-stats-seo-pattern]] — RTK stats in ISR
- [[on-demand-revalidation-api-route]] — revalidation API
- [[persistgate-ssr-suppresses-head-component]] — PersistGate SSR
- [[tiered-empty-page-noindex-strategy]] — empty page noindex
- [[static-route-beats-catchall-priority]] — route priority
- [[defaultseo-fallback-pattern]] — default SEO fallback
- [[og-image-1200x630-webp]] — og image spec (see [[og-image-1200x630-webp]])
- [[og-image-1200x630-webp]] — og image spec
- [[production-url-rename-cost-framework]] — URL rename framework
- [[sentinel-content-type-bookmark-blog]] — sentinel pattern

### Frontend — React
- [[react-hooks-rules-lowercase-component]] — hook rules
- [[react-strictmode-useref-persistence]] — useRef + StrictMode
- [[react-state-no-op-guard-side-effect-prevention]] — no-op guard
- [[react-dual-hook-url-race]] — dual hook URL race
- [[react-client-key-null-id-pattern]] — null-id key pattern
- [[useeffect-cancellation-guard-pattern]] — cleanup guard
- [[useauth-axios-hook-factory]] — axios hook factory
- [[checkout-hoc-architecture]] — HOC pattern
- [[checkout-state-persistence]] — checkout state
- [[checkout-formdata-persist-guard-pattern]] — formdata guard
- [[checkout-formdata-time-fields]] — time fields
- [[checkout-step-flow]] — step flow
- [[checkout-next-btn-disable-conditions]] — disable logic
- [[refund-flow]] — refund flow

### Frontend — Redux / RTK
- [[redux-store-architecture]] — store arch
- [[redux-persist-gate-scope-gap]] — PersistGate scope
- [[rtk-query-advanced-patterns]] — RTK Query patterns
- [[rtk-lazy-query-tuple-misuse]] — tuple misuse
- [[rtk-cart-tag-invalidation-auto-refetch]] — tag invalidation

### Frontend — UI / Design System
- [[design-systems]] — DS hub
- [[design-system-phase1-migration]] — phase 1 migration
- [[design-system-tokens-expansion]] — token expansion
- [[design-token-caption-tailwind-gotcha]] — token gotcha
- [[designsystem-shadow-border-tokens]] — shadow/border tokens
- [[migrate-bootstrap-palette-to-ds-tokens]] — palette migration
- [[unified-badge-system-pattern]] — badge system
- [[touch-target-44px-enforcement]] — 44px rule
- [[wcag-touch-target-enforcement]] — WCAG touch target
- [[ios-zoom-input-16px-rule]] — iOS 16px rule
- [[carousel-design-standard]] — carousel standard
- [[carousel-embla-align-start-mobile-snap]] — embla mobile snap
- [[sidebar-sticky-2col-responsive-grid]] — sticky 2-col
- [[section-render-order-principles]] — render order
- [[section-contentcard-wrapper-pattern]] — contentcard wrapper
- [[header-rows-context-dynamic-offset]] — header offset
- [[header-glass-to-solid-migration]] — header glass→solid
- [[mobile-header-scroll-behavior-change]] — mobile scroll
- [[adaptive-header-route-type-pattern]] — adaptive header
- [[icon-button-size-decision]] — icon button size
- [[iconbutton-keydown-stoppropagation-card]] — keydown stopprop
- [[star-aria-radiogroup-pattern]] — star a11y
- [[expandable-menu-row-mui-collapse]] — menu collapse
- [[mui-autocomplete-inputvalue-sync]] — autocomplete sync
- [[mui-autocomplete-handlInputchange-parent-emit]] — autocomplete parent emit
- [[mui-dropdown-preserve-strategy]] — dropdown preserve
- [[mui-menu-paper-overflow-guard]] — menu overflow
- [[mui-emotion-tailwind-injectfirst]] — emotion injectFirst
- [[mui-tailwind-css-specificity]] — MUI+Tailwind specificity
- [[usedayTripFilters-hydration-spurious-push]] — filter hydration
- [[hero-cls-precise-sizes-attribute]] — hero CLS
- [[hero-88px-gap-root-cause]] — hero gap
- [[hero-back-share-buttons-2row-header-fix]] — hero back/share
- [[editorial-grid-layout-pattern]] — editorial grid
- [[featured-image-header-usage-matrix]] — featured image matrix
- [[featured-image-header-width-bug]] — width bug
- [[transport-combo-card-pattern]] — combo card
- [[section-contentcard-wrapper-pattern]] — in-article CTA
- [[currency-context-price-rendering-rule]] — price render
- [[site-url-config-pattern]] — site URL config
- [[site-url-config-pattern]] — env decoupling (see site-url)
- [[brand-name-constant-extraction]] — brand constant
- [[wishlist-per-card-state-not-page]] — wishlist state
- [[add-flow-metadata-helper-pattern]] — metadata helper
- [[core-web-vitals-budget]] — CWV budget
- [[layout-spacing-consistency-audit]] — spacing audit
- [[homepage-section-render-order-conversion]] — homepage order
- [[homepage-experiences-section-audit]] — homepage audit
- [[transportation-category-audit]] — transport category
- [[mobile-search-bar-ux-competitor-research-2026]] — search bar
- [[admin-dashboard-component-patterns]] — admin components
- [[admin-dashboard-contracts]] — admin contracts
- [[admin-dashboard-image-pipeline]] — image pipeline
- [[frontend-debug-utilities]] — debug utils

### Frontend — SEO
- [[structured-data-schema-patterns]] — schema patterns
- [[seo-canonical-getsiteurl-pattern]] — canonical pattern
- [[seo-homepage-specialist-team]] — homepage SEO team
- [[sitemap-filter-by-inventory-or-recency]] — sitemap filter
- [[keyword-research-routes]] — keyword research
- [[trip-detail-server-side-seo-pattern]] — trip SEO
- [[tiered-empty-page-noindex-strategy]] — empty noindex
- [[wordpress-faqpage-deprecation-note]] — WP FAQ deprecate
- [[og-image-1200x630-webp]] — og image

### Backend — Django
- [[django-booking-creation-validation-gate]] — booking gate
- [[django-400-vs-409-duplicate-cart-item]] — 400 vs 409
- [[django-async-ai-call-pattern]] — async AI
- [[django-m2m-location-join-recommendations]] — m2m join
- [[django-nested-delete-sweep-pattern]] — nested delete
- [[django-nullable-fk-migration-pattern]] — nullable FK
- [[django-parse-int-list-text-fallback]] — int list fallback
- [[django-partial-update-elif-metadata-drop]] — partial update
- [[django-serializer-shadowing-pattern]] — serializer shadow
- [[django-soft-delete-s3-file-preserve]] — S3 preserve
- [[contract-soft-delete-is-actived-invariant]] — soft delete
- [[contract-confidence-score-algorithm]] — confidence score
- [[contract-fk-icontains-or-fallback]] — FK icontains
- [[contract-trip-null-non-transport-pattern]] — trip null
- [[contract-serializer-non-transport-fields]] — serializer fields
- [[extea-contract-serializer-no-ratecard]] — EXTEA serializer
- [[manual-adjustment-model]] — adjustment model
- [[copy-cartitem-trip-none-guard]] — cartitem guard
- [[cart-reprovision-after-reset]] — cart reprovision
- [[stations-arrival-viewset-public-leak]] — viewset leak
- [[serializer-field-omission-starves-ui]] — field omission
- [[toctou-select-for-update-before-api-call]] — TOCTOU guard
- [[summary-must-not-scope-by-its-own-selector]] — selector scope
- [[lru-cache-content-type-lookup]] — LRU cache
- [[orm-annotation-aggregate-min-rate]] — aggregate min
- [[never-notfound-in-catch-block]] — exception handling
- [[view-utility-call-exception-wrapper]] — exception wrapper
- [[parseiso-null-guard-date-sort-pattern]] — date sort
- [[dangling-export-import-bug-pattern]] — import bug
- [[pdf-parsing-pipeline-pattern]] — PDF pipeline
- [[pdf-contract-import-research]] — PDF research
- [[pdf-contract-import-adversarial-review]] — PDF review
- [[pdf-import-pre-validation-rules]] — PDF validation

### Backend — Celery / Async
- [[celery-tasks]] — master hub
- [[celery-task-over-bare-thread-django-signals]] — task over thread
- [[celery-beat-payment-scheduling]] — beat scheduling
- [[django-celery-beat-database-scheduler]] — DB scheduler
- [[backend-n8n-resend-webhook]] — n8n webhook

### Backend — Data Model
- [[django-booking-creation-validation-gate]] — order filter (see [[django-booking-creation-validation-gate]])
- [[payment-checkout-architecture-audit]] — booking data contract
- [[payment-charge-service-layer]] — payment model

### Payment
- [[payment-system]] — system hub
- [[payment-integration]] — integration hub
- [[payment-checkout-5-principles]] — 5 principles
- [[payment-checkout-architecture-audit]] — architecture audit
- [[payment-checkout-e2e-testing]] — e2e testing
- [[payment-e2e-rerun-guide]] — rerun guide
- [[payment-frontend-flow-mechanics]] — frontend flow
- [[payment-backend-charge-flow]] — backend charge
- [[payment-gateway-charge-architecture]] — gateway arch
- [[payment-charge-service-layer]] — charge service
- [[payment-status-enums]] — status enums
- [[payment-cancel-state-prevmethod-guard]] — cancel guard
- [[payment-cancel-vs-expire-error-mapping]] — error mapping
- [[payment-celery-expiry-strategy]] — expiry strategy
- [[payment-orphan-charge-expire-pattern]] — orphan expire
- [[payment-pending-deadlock]] — pending deadlock
- [[payment-reconcile-gate-extension]] — reconcile gate
- [[payment-sentinel-idempotency]] — sentinel idempotency
- [[payment-idempotency-key-cart-total]] — idempotency key
- [[payment-qr-polling-mechanics]] — QR polling
- [[promptpay-no-webhook-on-expiry]] — promptpay expiry
- [[payment-guest-email-guard-mirror]] — guest email guard
- [[payment-amount-validation-rule]] — amount validation
- [[payment-audit-bugs]] — audit bugs
- [[payment-exception-catalog]] — exception catalog
- [[payment-finalize-deep-dive]] — finalize deep dive
- [[payment-legacy-deprecation-map]] — legacy deprecation
- [[payment-self-heal-coverage-matrix]] — self-heal matrix
- [[multitab-payment-race-condition-fixes]] — race fixes
- [[refund-flow]] — refund flow
- [[omise-client-integration]] — Omise client
- [[omise-api-reference]] — Omise API ref
- [[omise-attributes-dict-extraction]] — Omise attributes
- [[omise-webhook-security]] — webhook security
- [[omise-webhook-tailscale-local-testing]] — tailscale testing
- [[locations-destinations-product-split]] — location split
- [[operator-image-alt-caption-fields]] — operator alt/caption
- [[operator-image-soft-delete-cascade-gap]] — image cascade
- [[people-also-book-checkout-audit]] — PAB audit
- [[cross-sell-placement-strategy]] — cross-sell placement
- [[cross-sell-suppress-during-payment]] — cross-sell suppress
- [[activity-to-activity-cross-sell]] — A2A cross-sell
- [[recommendation-anchor-first-transport-rule]] — anchor rule
- [[recommendation-type-selection-by-service-category]] — rec selection
- [[multi-item-cart-anchor-last-transport]] — cart anchor
- [[popular-routes-lowest-price-farecalendar-parity]] — parity
- [[slidecalendar2-farecalendar-prop-pattern]] — farecalendar

### API
- [[api-mirroring-pattern-new-features]] — API mirror
- [[two-surface-parity-shared-module]] — two-surface parity

### Security
- [[dompurify-xss-prevention-pattern]] — DOMPurify XSS
- [[e2e-csrf-blocks-410-legacy-post-tests]] — CSRF + 410
- [[dompurify-xss-prevention-pattern]] — security index (see [[admin-dashboard-contracts]])
- [[omise-webhook-security]] — Omise security

### Audit / Research
- [[contract-model-ambiguity-audit]] — contract audit
- [[design-system-audit-2026-05-31]] — DS audit
- [[design-system-audit]] — DS audit 06-13
- [[rate-review-css-audit]] — rate review CSS
- [[rate-review-page-shell-pattern]] — rate review shell
- [[trip-detail-deep-review]] — trip deep
- [[trip-detail-page-review]] — trip page
- [[trip-page-full-audit]] — trip full
- [[trip-filter-modal-audit]] — trip filter
- [[airport-transfer-width-audit]] — width audit
- [[airport-transfer-at1-redesign-spec]] — AT1 spec
- [[booking-widget-availability-error-display]] — widget error
- [[gtm-impression-dedup-sessionstorage]] — GTM dedup
- [[gtm-purchase-item-category-attribute]] — GTM purchase
- [[blog-canonical-url-wp-subdomain-bug]] — blog canonical
- [[canonicalization-audit-checklist]] — canonical checklist
- [[smartenplus-2026-ux-direction]] — 2026 UX
- [[smartenplus-product-positioning]] — positioning
- [[smartenplus-synopsis]] — synopsis
- [[content-marketing-strategy-review]] — content strategy
- [[experiences-2026-marketplace-redesign]] — canonical categories (see [[experiences-2026-marketplace-redesign]])
- [[activities-browse-filter-inactive-contracts]] — filter inactive
- [[activities-sort-filter-ux]] — sort filter
- [[activities-location-search-backend-text-fallback]] — location search
- [[journeys]] — journeys hub
- [[nextauth-session-shape]] — NextAuth shape
- [[nav-label-url-slug-two-layer-strategy]] — nav label strategy

## Conventions for this folder
- One idea per note; if note grows past 200 lines, extract sub-concepts
- Source projects: see [[01-projects/README]] and [[08-archive/README]]
- Frontmatter optional; many notes use `metadata.type` when present
- Link liberally — orphan pages degrade vault
