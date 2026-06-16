# Project: GYG Card Rate Analysis

## Summary
3-round analysis of GetYourGuide card rate display: UX, skeptical review, leader synthesis.

## Status
completed

## Context
Determine why GYG-sourced cards show inconsistent rates vs. native operator cards.

## Stack
- Next.js Pages Router
- GYG partner API integration

## Key Files
- `r1-ux.md` — UX findings
- `r2-skeptic.md` — skeptical review
- `r3-leader-synthesis.md` — leader synthesis

## Architecture
Card render pipeline normalizes GYG rates through `currency-context`. See [[currency-context-price-rendering-rule]].

## Active Tasks
- [x] r1 UX round
- [x] r2 skeptical review
- [x] r3 leader synthesis

## Sibling Sub-Files
- [[gyg-card-rate-analysis-2026-06-05]] — top-level overview note

## Related
- [[gyg-page-analysis-2026-06-04-overview]]
- [[currency-context-price-rendering-rule]]
