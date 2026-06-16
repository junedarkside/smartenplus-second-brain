# Project: Trip Detail SEO/AEO/GEO Audit

## Summary
6-round trip-detail SEO audit spanning AEO (answer engine), GEO (generative engine), classic SEO, leader synthesis, implementation, and re-audit.

## Status
completed

## Context
Bring trip-detail pages up to AEO/GEO-readiness for LLM-based answer engines plus classic SEO.

## Stack
- Next.js Pages Router
- ISR (`revalidate: 300`)

## Key Files
- `r1-aeo.md` — AEO findings
- `r1-geo.md` — GEO findings
- `r1-seo.md` — classic SEO findings
- `r2-leader-synthesis.md` — leader synthesis
- `r3-implementation-plan.md` — implementation plan
- `r4-re-audit-post-impl.md` — post-implementation re-audit

## Architecture
Trip-detail = ISR static page with structured data + OpenGraph. See [[trip-detail-server-side-seo-pattern]] and [[structured-data-schema-patterns]].

## Active Tasks
- [x] r1 AEO + GEO + SEO
- [x] r2 leader synthesis
- [x] r3 implementation plan
- [x] r4 post-impl re-audit

## Related
- [[trip-page-full-audit-2026-06-15]]
- [[trip-route-page-seo-aeo-geo-audit-2026-06-15]]
- [[trip-detail-server-side-seo-pattern]]
- [[seo-canonical-getsiteurl-pattern]]
