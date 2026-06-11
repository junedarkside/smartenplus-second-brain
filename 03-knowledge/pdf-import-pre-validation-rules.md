# PDF Import Pre-Validation Rules

## Summary

6 mandatory safeguards for the PDF contract import pipeline. All must be resolved before first commit. From adversarial review 2026-06-01.

## Context

Full critique in [[pdf-contract-import-adversarial-review]]. These are the non-negotiable rules extracted as an independent checklist for future implementation.

## 6 Red Flags (All Must Be Fixed)

| # | Red Flag | Risk | Required Fix |
|---|----------|------|-------------|
| 1 | Sync AI call in Django view | Blocks WSGI worker for 5–30s | Return `task_id` immediately, Celery handles AI call, frontend polls status endpoint. See [[django-async-ai-call-pattern]] |
| 2 | Hard-delete draft on reject | No audit trail | Soft-delete: `status = "rejected"`, keep row. Hard-delete only after 7-day TTL |
| 3 | LLM matching contracts by route name | Hallucinated slug → wrong contract gets draft | Pass full contract list as context. Admin confirms match in review step — never auto-apply without confirmation |
| 4 | No pre-validation before draft write | Invalid data (date format, enum, min>max) silently written | Validate all fields before writing draft. Store errors in `validation_errors` JSONField, surface per-field in review UI |
| 5 | Confidence auto-accept | 0.85 threshold pre-checks without admin verification | Pre-check is UI hint only — admin must still click Confirm. No auto-PATCH on confidence alone |
| 6 | No large-delta warning | Operator mistake silently accepted (e.g., rate 1200 → 12000) | Show ⚠️ warning in diff table when delta > 50% of current value for numeric fields |

## 3-Screen UX (Revised)

**Screen 1 — Import trigger**
- "Import from PDF" button in `ContractDetailHeader`
- Paste JSON textarea (NotebookLM output)
- "Extract & Propose" → POST bulk endpoint → shows task progress (async)

**Screen 2 — Match review**
- Table: Route | Matched Contract | Confidence | ✓ Accept
- High confidence (>0.85): pre-checked as hint (not auto-applied)
- Low confidence: unchecked, admin must manually check
- "Create Drafts" button — only checked rows get drafts

**Screen 3 — Draft review (per contract)**
- Field diff table: Current | Proposed | ⚠️ Warning | ✓ Accept field
- Large-delta (>50% change): ⚠️ shown inline
- Place name fields: extracted name hint + `LocationSelector` dropdown
- `validation_errors` shown per field
- Confirm → PATCH | Reject → soft-delete draft

## Related

[[pdf-parsing-pipeline-pattern]] — full pipeline architecture
[[pdf-contract-import-adversarial-review]] — full adversarial critique with model schema
[[django-async-ai-call-pattern]] — async Celery task pattern for LLM calls
