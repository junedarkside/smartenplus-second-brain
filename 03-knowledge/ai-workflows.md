# AI Workflows — LLM Wiki Pattern

## Summary
LLM-maintained knowledge base. LLM writes + maintains wiki; human curates + directs. Knowledge compiled once, kept current, not re-derived per query.

## Context
Traditional RAG: retrieves chunks at query time, no accumulation. LLM Wiki: incrementally builds structured wiki — updates pages, flags contradictions, maintains cross-refs. Knowledge compounds.

## Three Layers

1. **Raw sources** — immutable source documents. LLM reads, never modifies.
2. **The wiki** — LLM-generated markdown. Summaries, entity pages, concepts. LLM owns.
3. **The schema** — `CLAUDE.md` tells LLM how wiki structured, conventions, workflows.

## Operations

### Ingest
Drop source → LLM reads → discusses → writes summary → updates index → updates entity pages → appends log. Single source may touch 10-15 pages.

### Query
Ask against wiki → LLM searches pages → synthesizes with citations. Good answers filed as new pages.

### Lint
Periodic health-check: contradictions, stale claims, orphan pages, missing pages, broken cross-refs.

## Why It Works
Humans abandon wikis due to maintenance burden. LLMs don't get bored, don't forget cross-refs, can touch 15 files per pass. Maintenance cost ≈ zero.

Human: curate sources, direct analysis, ask questions, interpret.
LLM: summarize, cross-reference, file, bookkeep.

## Navigation
- **index.md** — content catalog, one line per page with wikilink. Works at ~100 sources, hundreds of pages without RAG.
- **log.md** — chronological journal. `## [YYYY-MM-DD] type | title`. Grep-parseable.

## Related
- [[ingestion-workflow]]
- [[engineering]]
