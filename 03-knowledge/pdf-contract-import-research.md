# PDF Contract Import — Research Summary

## Summary

Operators submit non-standard PDFs (Thai/English) to update existing contracts. Architecture agreed 2026-06-01. Status: **PARKED** — not yet scheduled for implementation.

**Agreed flow:** Admin pastes NotebookLM output → Django bulk extract endpoint → `ContractImportDraft` DB staging → admin review/confirm → PATCH contract.

## Decision: NotebookLM as extraction layer

Direct LLM API (Django + Claude) rejected — overkill for current volume. NotebookLM chosen: free, Thai support, no infra, admin controls quality. When volume grows → revisit Django + Claude Haiku `tool_use`.

## Status of Open Questions

- Local agent: **RESOLVED** — no local agent. Django calls GLM/MiniMax server-side.
- Rate card merge: **RESOLVED** — merge by `ratecard` type key (untouched types survive).
- Place resolution: **RESOLVED** — manual admin selection via `LocationSelector`. Fuzzy match rejected.
- Draft payload: **RESOLVED** — delta only stored.
- Auth: **RESOLVED** — admin NextAuth session. No service token.
- Remaining open: prompt template design, confidence threshold validation, trip delta field scope.

## Related

[[pdf-parsing-pipeline-pattern]] — full pipeline architecture, flow diagram, backend components, rate card rules
[[pdf-import-pre-validation-rules]] — 6 red flags + 3-screen UX, all must resolve before first commit
[[pdf-contract-import-adversarial-review]] — adversarial critique, revised model schema, missing safeguards table
[[django-async-ai-call-pattern]] — Celery async pattern for LLM calls
[[admin-dashboard-contracts]] — category registry, form flow, payload rules
[[celery-tasks]] — Celery beat TTL pattern
