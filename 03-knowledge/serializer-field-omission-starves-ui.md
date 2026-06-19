# Serializer field omission silently starves the UI

## Summary
A field missing from a DRF serializer's `Meta.fields` ships as `undefined` to the
client — the UI degrades silently (no error), often falling back to a wrong default.

## Context
Contract soft-delete (admin dashboard, 2026-06-16). A deleted contract showed a red
**Inactive** badge instead of grey **Deleted**, and the **Restore** bulk action never
appeared outside the Deleted filter. The model had `is_deleted`, the client already read
`params.row.is_deleted` (grid) and `c.is_deleted` (action-bar split), and the backend
soft-delete logic was correct.

## Problem
The **list** serializer `ContractSerializer.Meta.fields` (`operators/serializers.py`)
did not list `is_deleted`. The *detail* serializer did — so it looked correct in spot
checks. Every list row therefore had `is_deleted === undefined`:
- Badge: `undefined` falsy → `isActive ? Active : Inactive` → wrong red badge.
- Restore: `selectedDeletedCount` (derived from `is_deleted`) always 0 → button hidden.

One missing field broke two unrelated features, with no console error to point at it.

## Decision
Add `is_deleted`, `deleted_at` to the list serializer fields. No frontend change — the
consumers already expected the field; they were starved, not wrong.

## Lesson
- When a client reads a field that "should be there" but behaves as falsy/empty, check
  the **serializer used by that exact endpoint** (list vs detail often differ) before
  suspecting the client.
- A field present on the model + read on the client is NOT proof it's serialized.
- Status/flag fields driving UI branches are high-leverage: their absence picks a
  default silently. Verify they're in `Meta.fields` for every serializer that feeds a UI
  that branches on them.

## Related
- [[adr-contract-soft-delete]]
- [[summary-must-not-scope-by-its-own-selector]]
