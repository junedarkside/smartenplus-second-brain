# Atomic Notes

## Summary
Rules for extracting single-concept notes from fat topic pages. Used automatically during session wrap-up and on-demand via `/lint-vault`.

## What Counts as an Atom

**Extract if:**
- Standalone — understood without reading parent note
- Name doubles as a search query
- Would be linked from ≥2 other notes if extracted

**Keep in parent if:**
- Enum/constant value lists
- Step-by-step procedures belonging to a workflow
- Context-only paragraphs that scaffold surrounding content

## Naming Convention
`{domain}-{specific-concept}.md`

Good: `promptpay-no-webhook-on-expiry.md`, `locked-amount-reset-rules.md`, `nextjs-ssr-disabled-checkout.md`
Bad: `payment-notes.md`, `misc-fixes.md`, `important.md`

## Extraction Process
1. Identify candidate concept in source note
2. Check it passes the 3 criteria above
3. Create `03-knowledge/{domain}-{concept}.md` using `[[atomic-note]]` template
4. In source note: replace extracted content with 2-line summary + `[[wikilink]]`
5. Add atom to `index.md`

## Quality Check
Before extracting, ask:
- Will this be searched directly by name?
- Would I link this from a different domain page?
- Is this one concept or two?

If two → split further. If one but too small → skip, leave in parent.

## Related
- [[ingestion-workflow]]
- [[ai-workflows]]
