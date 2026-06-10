# Next Priority Debate — 2026-06-09

## Summary

3-agent cross-discipline review (BD Strategist + Engineering Auditor + PM Synthesizer) of SmartEnPlus business strategy vs codebase reality. Output: ranked priority list + single #1 action.

---

## BD Analysis

**Position:** Vertically integrated Thailand transport + tour operator at inflection point. Hard moat: owned minivan network + own-brand tours (Klook-validated). Revenue 90% B2B / 10% B2C. Non-transport (DAY_TOUR/SPA_WELLNESS) just went live on B2C (2026-06-02/03).

**Top Opportunities:**
1. Cross-sell own-brand tours to existing transport buyers — zero new inventory, high-margin SKUs now live
2. Wellness as high-margin add-on — path to 30%+ operating margins, OTAs touch wellness lightly
3. SEO ownership of Hat Yai→Koh Lipe corridor — $54.11 CPC keyword, SmartEnPlus owns live cross-border inventory

**Validated vs Assumed:**

| Claim | Validated? | Evidence or Gap |
|-------|-----------|-----------------|
| US travelers = primary B2C customer | Validated | GA4: US 53.7% engagement, no LINE |
| Own-brand tours have market demand | Validated | Already selling on Klook |
| B2B supply relationships | Validated | 90% revenue, named in business.md |
| B2C customers cross-buy activities after transport | **Assumed** | No conversion data yet |
| Wellness attach rate justifies 30%+ margins | **Assumed** | No commission rate data documented |
| Bundle Score UX lifts AOV | **Assumed** | Not built, not tested |
| Journey builder monetizes planning | **Assumed + risk-flagged** | Multiple docs warn planning ≠ revenue |
| Hat Yai-Lipe has high commercial intent | Validated (proxy) | $54.11 CPC — competitors paying to own it |

**BD Verdict:** Prove cross-sell conversion in 60 days — what % of transport buyers add DAY_TOUR or SPA_WELLNESS — because every downstream investment is gated on that number.

---

## Engineering Audit

**What's Built (ready today):**
- `recommendationsApi.js` — RTK Query, supports `similar/alternatives/packages/hybrid`, hits real backend
- `RelatedTripsSection.js` — "You Might Also Like" on transport trip detail pages
- `PostBookingRecommendations.js` — full card grid on booking confirmation (gated by env flag, GTM wired)
- `CheckoutRelatedTrips.js` — accordion in checkout sidebar, GTM wired, production-ready — **NEVER IMPORTED IN CHECKOUT**
- Multi-category checkout works (DAY_TOUR/SPA_WELLNESS)
- GTM `purchase` event fires

**What's Partial:**
- `CheckoutRelatedTrips` complete but unmounted — needs 1 import + 1 JSX line in `pages/checkout/index.js`
- GTM purchase event missing `item_category` — GA4 cannot break revenue by product type
- `RelatedExperiences.js` uses dumb category filter, not scored `recommendationsApi`
- Post-booking recommendations only use `contracts[0]` in multi-item orders

**What's Missing:**
- Bundle pricing UX — no bundle checkout component, no combined-contract cart shape
- Add-to-cart from recommendations — all surfaces explicitly read-only by design
- Revenue Per Traveler (RPT) tracking — no metric or event exists
- Journey builder / multi-leg itinerary — nothing exists
- Wellness add-on upsell — no cross-category upsell trigger

**Feasibility Matrix:**

| Feature | Status | Effort |
|---------|--------|--------|
| Mount CheckoutRelatedTrips | Partial | 1–2 days |
| Add item_category to GTM | Partial | Same day (3 lines) |
| Wire RelatedExperiences to scored API | Partial | 0–1 days |
| RPT tracking (GA4 calculated metric) | Missing | 2–3 days |
| Bundle UX | Missing | 3–4 weeks |
| Wellness add-on upsell | Missing | 2–3 weeks |
| Journey builder | Missing | 6–10 weeks |

---

## PM Synthesis + Debate

**Key debate findings:**

**1. The "60-day gate" collapses to 2 days.**
BD assumed cross-sell UX needed to be built. Engineering found `CheckoutRelatedTrips` is production-ready and unmounted. 1 import + 1 JSX line. The gate experiment is a 2-day move, not a 60-day project.

**2. Wellness at #2 is premature.**
BD ranked it on margin potential. Engineering confirms add-to-cart is missing by design from all recommendation surfaces — that's 2–3 weeks of frontend work + spa curation, stacked on zero cross-sell data. Cannot justify before cross-sell attach rate is known.

**3. RPT measurement must precede cross-sell mount.**
BD's gate logic is unmeasurable without `item_category` in the GTM purchase event. GA4 currently cannot break revenue by product type. Shipping cross-sell without measurement = 60 days of blind data. Sequence: measurement fix Day 1 → cross-sell mount Day 2.

**4. SEO runs in parallel, no debate needed.**
Zero engineering dependency. 3–6 month lag means starting late is permanent lost ground. Start this week, run forever.

**5. Journey builder lite is a false economy.**
Even a 1–2 week prototype needs multi-leg cart state + itinerary display + cross-category pricing. No booking = no conversion path = demo with no value. Gate is correctly set.

---

## Final Priority List (Ranked 1–5)

**#1 — Add `item_category` to GTM purchase event**
- What: Add `item_category: contract.service_category` to `tripItems` map in `useOmisePayment.js:55`
- Why: BD's entire gate metric is unmeasurable without it. Every experiment is blind.
- Effort: 3 lines, same day
- Impact: Unlocks GA4 revenue breakdown by product type — prerequisite for all measurement
- Risk if skipped: 60 days of cross-sell data is uninterpretable

**#2 — Mount `CheckoutRelatedTrips` in checkout**
- What: 1 import + 1 JSX line in `pages/checkout/index.js`, pass `cartItems`
- Why: Production-ready surface. GTM wired. Zero new inventory. This IS the 60-day gate experiment.
- Effort: 1–2 days
- Impact: First B2C cross-sell signal. RPT measurement begins.
- Risk if skipped: Entire strategic roadmap stays hypothetical indefinitely

**#3 — Wire `RelatedExperiences` to scored `recommendationsApi`**
- What: Replace dumb category filter with `useGetRecommendationsQuery({ type: 'similar' })` in `RelatedExperiences.js`
- Why: Activity detail pages show unranked results. Scored recommendations push highest-margin SKUs (DAY_TOUR/SPA_WELLNESS) to the top.
- Effort: 0–1 days
- Impact: Improves recommendation quality, supports cross-sell evidence gathering
- Risk if skipped: Activity page cross-sell signal is noise

**#4 — SEO: Hat Yai → Koh Lipe corridor**
- What: Publish landing pages targeting Hat Yai→Koh Lipe transport + tour combinations
- Why: SmartEnPlus owns live cross-border inventory. $54.11 CPC proxy. 3–6 month SEO lag.
- Effort: Zero engineering, 2–4 weeks content
- Impact: Owned traffic economics. Only B2C channel that doesn't depend on OTA commission.
- Risk if skipped: Competitor fills SERP gap while SmartEnPlus pays OTA commissions forever

**#5 — Post-booking recommendations multi-item fix**
- What: Extend `PostBookingRecommendations.js` to use all contracts, not just `contracts[0]`
- Why: Multi-category checkout works. Post-booking upsell is systematically wrong for multi-item orders.
- Effort: 1–2 days
- Impact: Improves recommendation relevance for the users most likely to cross-buy again
- Risk if skipped: Post-booking upsell degraded for exactly the buyers you want most

---

## #1 Recommendation

Add `item_category` to the GTM purchase event (`useOmisePayment.js:55`) this week — before mounting `CheckoutRelatedTrips`. The 3-line change costs nothing and ensures every purchase event from Day 1 is attributable by product type. Then mount `CheckoutRelatedTrips` on Day 2. **Success in 30 days:** GA4 shows at least one purchase with a DAY_TOUR or SPA_WELLNESS line item, and you have a cross-category conversion rate from checkout impressions. That number — even if 0.5% — is the only real data point in this entire strategic debate.

---

## What NOT to Build Yet

**Bundle pricing UX** — 3–4 weeks, requires add-to-cart from recommendations (excluded by design), and zero evidence customers want bundles. Build after cross-sell attach rate data exists.

**Wellness add-on upsell** — Margin case is real but path requires add-to-cart capability + spa curation + cross-category pricing. Zero cross-sell data = speculation on speculation. Revisit at 60-day data read.

**Journey builder / multi-leg itinerary** — 6–10 weeks, no validated demand, no monetization path confirmed. Gate is correctly set. Q4 conversation at earliest.

---

## Related

- [[business]] — roadmap sequence, moat table
- [[business-development-thesis-2026]] — four-phase growth model, cross-sell gate
- [[business-development-thailand-bundle-architecture]] — bundle UX spec (gated)
- [[business-development-zeitrip-mvp]] — journey builder spec (gated)
- [[content-marketing-strategy-2026-06-03]] — Hat Yai-Lipe SEO strategy
