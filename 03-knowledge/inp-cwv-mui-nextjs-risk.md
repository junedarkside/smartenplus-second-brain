---
name: inp-cwv-mui-nextjs-risk
description: INP replaced FID as Core Web Vital in Mar 2024; MUI + RTK Query Next.js apps have high INP risk that cannot be measured via curl/markup inspection
metadata:
  type: reference
---

**INP (Interaction to Next Paint)** replaced FID as a Core Web Vital in March 2024. It measures responsiveness: time from user interaction to next paint.

**SmartEnPlus risk profile:**

| Factor | INP Risk |
|--------|----------|
| MUI (Material UI) | High — Emotion CSS-in-JS runtime styling adds JS work on hydration |
| RTK Query | Medium — API fetch + Redux state update on interaction |
| `/activities` card grid | High — full card list hydrates on page load; filter interactions trigger re-renders |
| Next.js Pages Router | Medium — no RSC; full client hydration |

**Why audit missed it:** curl + header inspection cannot measure INP. Only field data (CrUX via PageSpeed Insights) or lab data (WebPageTest with interaction scripts) can assess INP.

**How to measure:**
1. PageSpeed Insights → field data tab → INP score for `/activities`
2. Chrome DevTools → Performance tab → record interaction, look for Long Tasks
3. CrUX dashboard (if GSC connected)

**Threshold:** INP < 200ms = Good, 200-500ms = Needs Improvement, > 500ms = Poor.

**How to apply:** Every CWV audit must explicitly flag INP as assessed or unassessed. Do not claim a CWV score above 8.0 without INP field data. Add INP check to weekly audit checklist. [[howto-schema-booking-flow]]
