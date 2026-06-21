# ISR Revalidate — Which Fields Need It (CSR vs ISR vs On-Demand)

## Summary

Not every field on the detail pages needs ISR revalidation. Match the refresh mechanism to the field's volatility + consumer. This matrix settles what the on-demand revalidate signal is actually for, and what it deliberately does NOT touch.

> **Note:** "ISR" here = Next.js **page-level** revalidation (`revalidate: 300` in `getStaticProps`) applied to the whole page — Next.js has no field-level ISR. "ISR only" means a field is sourced from the ISR HTML (no CSR overlay), not that the field is revalidated independently.

## Matrix (verified against source)

| Field | trips/detail | activities/detail | Right mechanism | Why |
|---|---|---|---|---|
| **rate / ratecard** | CSR overlay (`useCheckContractQuery`, mount, uncached `/contract/{id}`) | ISR on first paint; CSR only after date pick | CSR for buyer **+** ISR/on-demand for SEO | money must be live for the human; the JSON-LD `Offer.price` (server-rendered) must be fresh for crawlers |
| **content** (description, tour_highlights, inclusions, route_info, timeline, images, policies) | **ISR only** (not in CSR merge `[...slug].js:105-110`) | **ISR only** (CSR mount fetches reviews only) | no CSR safety net → on-demand revalidate is the ONLY guaranteed fresh path |
| **SEO / JSON-LD / meta** | ISR (`getStaticProps`) | ISR | on-demand revalidate | Googlebot reads ISR HTML, not the CSR overlay |
| **daily_counter** | not rendered | not rendered | n/a | — |
| **booked_count** | ISR prop | not rendered | ISR timer (stale-OK) | social proof; deliberately NOT on-demand (counter writes use `.update()` → no post_save → no storm; see [[django-update-bypasses-post-save-signal]]) |

## Key conclusions

- **On-demand revalidate exists for CONTENT + SEO**, not for the human-visible rate (CSR covers that) and not for the counter (timer is fine, and wiring it would storm).
- Why not just the native ISR timer for content? Next 14.2.5 standalone time-based revalidation is **request-triggered** (lazy), not a background cron → a quiet/zero-traffic page never regenerates, and the visitor who triggers regen still sees stale (stale-while-revalidate, next visit sees fresh). On-demand `res.revalidate()` is the only thing that guarantees fresh-on-edit for any page.
- `/contract/{id}` (trips CSR endpoint) is `products.ContractViewSet` (`views.py:359`) which only overrides `list`; `retrieve` is plain DRF → **uncached**, live DB every call → trips rate always fresh for humans.

## Related
- [[docker-standalone-isr-revalidate-gap]]
- [[isr-csr-overlay-stale-fields]]
- [[django-update-bypasses-post-save-signal]]
- [[frontend-url-canonical-www-not-apex]]
