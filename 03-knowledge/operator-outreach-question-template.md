# Operator Outreach — Question Template (grill skill input)

## Summary
Reusable template for `grill` skill invocation. Generates BD-ready question docs that staff forward to operators to close catalog coverage gaps.

## Context
Live-catalog gap audit ([[products-live-catalog-audit]]) identifies coverage gaps. Each gap needs a structured question doc that staff can hand to BD contacts. Template ensures consistent quality + operator profile criteria across rounds.

## Details

### Template structure (per gap)

```markdown
# Operator Outreach — {GAP_TYPE}: {GAP_TITLE}

## Gap
What SmartEnPlus is missing in the live catalog. Cite discovery evidence (sitemap URL, admin query, reference set entry).

## Demand signal
Why we believe demand exists: query_count from admin DB, competitor coverage (12Go/Klook/GetYourGuide), BD intel, social listening. Distinguish hard data vs hypothesis.

## What we need from operator
Plain language: "We are looking for an operator who runs X from Y to Z. Specifically, a {service_category} contract at {station}, with coverage for {date_range or year-round}."

## Operator profile criteria
- Fleet size / vehicle type / language coverage
- License + insurance (per BE `operators` model)
- Cancellation policy + deposit terms + payout cadence
- Existing digital channel maturity (Booking.com / Klook / 12Go partner?)

## Commercial ask
- Commission rate (SmartEnPlus standard)
- Net rates vs retail rates
- Min guaranteed volume / seasonal terms

## Compliance + onboarding checklist
- [ ] Operator agreement signed
- [ ] Insurance cert valid
- [ ] Vehicle docs
- [ ] Pricing sheet provided
- [ ] Sample inventory load via admin

## Next step
Ask staff to return:
1. Operator name + contact
2. Summary of fit
3. Expected timeline to first inventory
4. Any blockers
```

### Coverage lens tagging

Each gap tagged with 5-lens status from [[three-layer-gap-coverage-matrix]]:

| Lens | What to ask |
|---|---|
| Join | "Can you run shared scheduled service on this route?" |
| Private | "Can you offer private vehicle per booking?" |
| Charter | "Do you provide hourly or point-to-point charter?" |
| Experiences | "Do you offer multi-day packages from this hub?" |
| Activities | "Any day tours, attractions, spa, events, dining from this location?" |

### grill skill invocation pattern

```
/grill Use the operator-outreach-question-template to produce a question set for this gap: [paste gap entry]
```

Skill fills template fields + surfaces missing context for staff to gather. Save output to `business-development/products-live-catalog/grill-questions/{YYYY-MM-DD}-{slug}.md`.

### File naming

`grill-questions/{YYYY-MM-DD}-{slug}.md` — one per gap, link back to parent gap entry in `gap-inventory.md`. Resolved gaps → `resolved/{slug}-resolved-{date}.md`.

## Decision
Single template, reused every gap-fill round. Avoids drift in question quality. Resolves per-round questions land in dedicated `resolved/` archive so master gap inventory stays clean.

## Tradeoffs

- **Pro:** Consistent BD quality + faster staff turnaround.
- **Pro:** Atomic template — easy to update when BD learns new criteria.
- **Con:** Template may not fit all gap types (cross-border vs domestic differ in compliance).
- **Con:** Grill skill output quality depends on input detail — vague gap entries produce vague questions.

## Related
- [[live-catalog-discovery-protocol]]
- [[three-layer-gap-coverage-matrix]]
- [[thailand-location-coverage-framework]]
- [[products-live-catalog-audit]]