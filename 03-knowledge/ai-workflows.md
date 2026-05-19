# AI Workflows — LLM Wiki Pattern

## Summary
Pattern for building persistent, compounding knowledge bases using LLMs. LLM writes and maintains wiki; human curates and directs. Knowledge compiled once, kept current — not re-derived on every query.

## Context
Traditional RAG: LLM retrieves chunks at query time, no accumulation. Each query re-discovers from scratch. LLM Wiki: LLM incrementally builds structured wiki — updates pages, flags contradictions, maintains cross-references. Knowledge compounds.

## Three Layers

1. **Raw sources** — immutable source documents. LLM reads, never modifies. Source of truth.
2. **The wiki** — LLM-generated markdown. Summaries, entity pages, concepts, comparisons. LLM owns this layer.
3. **The schema** — `CLAUDE.md` tells LLM how wiki is structured, conventions, workflows. Key config file.

## Operations

### Ingest
Drop source → LLM reads → discusses takeaways → writes summary page → updates index → updates entity/concept pages → appends to log. Single source may touch 10-15 pages.

### Query
Ask against wiki → LLM searches pages → synthesizes answer with citations. Good answers filed back as new pages. Explorations compound.

### Lint
Periodic health-check: contradictions, stale claims, orphan pages, missing pages, broken cross-references. LLM suggests new questions and sources.

## Why It Works
Maintenance burden is why humans abandon wikis. LLMs don't get bored, don't forget cross-references, can touch 15 files per pass. Cost of maintenance ≈ zero.

Human: curate sources, direct analysis, ask questions, interpret meaning.
LLM: summarizing, cross-referencing, filing, bookkeeping.

## Navigation
- **index.md** — content catalog, one line per page with wikilink. Works at moderate scale (~100 sources, hundreds of pages) without RAG infrastructure.
- **log.md** — chronological journal. Format: `## [YYYY-MM-DD] type | title`. Parseable with grep.

## Related
- [[ingestion-workflow]]
- [[engineering]]
