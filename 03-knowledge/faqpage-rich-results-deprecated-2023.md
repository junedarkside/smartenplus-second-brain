---
name: faqpage-rich-results-deprecated-2023
description: FAQPage rich results were deprecated by Google in Aug 2023 — use FAQ prose for AEO text signal only, not structured data rich result
metadata:
  type: reference
---

Google deprecated FAQPage rich results in August 2023. Pages with `FAQPage` JSON-LD no longer get the expandable Q&A accordion in SERP.

**What this means for SmartEnPlus:**
- `/help/faqs` FAQPage ops-blocked (WP GraphQL returns `[]`) — **not a priority fix**. Even if fixed, zero SERP rich result benefit.
- FAQ prose content still has AEO value for AI answer engines (Perplexity, ChatGPT cite prose Q&A). Keep FAQ text visible.
- `FAQPage` schema on trip route pages (`pages/trips/detail/[...slug].js:464`) — harmless to keep (no penalty), but don't treat as an SEO win.

**How to apply:** Do not open tickets for FAQPage schema fixes unless specifically for AEO prose visibility, not rich results. Remove from open finding lists.

**Source:** r14 specialist review 2026-07-11. [[oai-searchbot-robots-pattern]]
