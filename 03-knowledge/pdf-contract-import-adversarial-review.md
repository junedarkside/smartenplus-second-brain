# PDF Contract Import — Adversarial Architecture Review

## Summary

Full critique of the original PDF import design. 6 red flags identified — all must be resolved before first commit. Core problem: extraction + matching + confirmation coupled into one pipeline. Clean design separates them. See [[pdf-contract-import-research]] for the full agreed architecture.

---

## 6 Red Flags — Stop Before Development

### Red Flag 1: One draft per contract with hard delete
Silent data loss via TTL. Audit impossible. Race condition in concurrent use.

**Fix:** Append-with-batch-ID + soft-delete (`status=expired`, never `DELETE`). Confirmed drafts retained forever.

### Red Flag 2: Synchronous AI call in Django request
WSGI worker blocked 5–20s per import. 5 concurrent admins = all workers stalled = dashboard degrades.

**Fix:** View returns `task_id` immediately. Celery handles AI call. Frontend polls `GET /tasks/{id}/`. See [[django-async-ai-call-pattern]].

### Red Flag 3: LLM doing contract matching
Passing all operator contracts to LLM = expensive, slow, non-deterministic. Wrong direction matches are real (e.g. southbound vs northbound, same route, high confidence).

**Fix:** LLM does extraction only. Python fuzzy matching handles contract matching against pre-fetched queryset. Show top 2–3 candidates — admin selects.

### Red Flag 4: No pre-validation before draft creation
Rate type mismatch (JOIN contract + VEHICLE rate) surfaces as 400 at confirmation — after admin reviewed and approved. Trust destroyed.

**Fix:** All validation runs at draft creation time. Errors in `validation_errors` JSONField, shown per-field in review UI.

### Red Flag 5: Confidence score as auto-accept gate
0.85 threshold that auto-checks rows is a live-pricing risk.

**Fix:** Confidence = display emphasis only (color banding). All rows require explicit human checkbox. Never pre-check.

### Red Flag 6: No large-delta warning
LLM decimal errors (13500 vs 1350) are common.

**Fix:** Flag rate change >30% as hard warning regardless of confidence. Two lines of Python. Non-negotiable in MVP.

---

## Revised Draft Model (required fields before first commit)

```
batch_id          UUID, indexed — one per import session
created_by        FK to Account
source_text_hash  SHA-256 of pasted input (dedup detection)
confirmed_at      timestamp
confirmed_by      FK to Account
superseded_by     FK self-referential, nullable
match_candidates  JSON — top 3 matches per row, not just best
status            pending / confirmed / rejected / expired  ← never DELETE
```

---

## 3-Screen UX (reduced from 5)

**Screen 1: Import Setup**
Operator (pre-populated from context) + paste area + Submit → returns `task_id` immediately.

**Screen 2: Unified Review Table**
One row per extracted update. Columns: route from PDF | matched contract + slug | confidence color band | field deltas inline ("ADULT: 1200→1350") | warnings | accept checkbox. Expandable row = field-level sub-table. Keyboard nav (Tab/Space/Enter).

**Screen 3: Confirmation Summary**
"X contracts updated. Y have active bookings. Confirm?" One click.

---

## Missing Safeguards (must add)

| Missing | Risk | Fix |
|---------|------|-----|
| Re-import guard | Overwrites first import silently | Warn if `source_text_hash` exists within TTL |
| Active booking warning | Rate change on contract with future bookings | Query orders, surface count as hard warning |
| Concurrent race condition | Two admins same contract = last write wins | `select_for_update()` on draft record |
| `transaction.atomic()` on confirm | Contract PATCH succeeds, Trip PATCH fails = partial state | Wrap both PATCHes in single atomic block |
| Audit log | No record of who/what/when | Store import session (text, AI response, batch_id, user) |
| Delta vs current-at-confirmation | Base state changes between draft + confirm | Show delta vs live values at confirm time |

---

## Revised API Endpoints

```
POST /admin-dashboard-operators/contract-import/            → returns task_id immediately (async)
GET  /admin-dashboard-operators/import-tasks/{task_id}/     → status + result
POST /admin-dashboard-operators/contract-import/{batch_id}/confirm/  → list of draft IDs, atomic
```

---

## Architecture Component Verdicts

| Component | Verdict |
|-----------|---------|
| NotebookLM extraction | Keep — add structured prompt template |
| Django AI call (sync) | Redesign → async Celery |
| LLM for matching | Remove → Python fuzzy |
| `ContractImportDraft` model | Redesign with batch_id + soft-delete |
| Match Review (separate screen) | Remove → merge into unified table |
| Draft Review per contract (separate page) | Simplify → expandable row |
| Rate card delta merge | Keep — merge-by-type-key correct |
| Celery TTL hard delete | Redesign → status=expired only |

---

## Related

- [[pdf-contract-import-research]] — full agreed architecture, field extraction map, prompt template
- [[django-async-ai-call-pattern]] — async LLM call pattern (Celery + task polling)
- [[celery-tasks]] — existing Celery beat patterns
