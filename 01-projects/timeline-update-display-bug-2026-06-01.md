# Timeline Update Display Bug Audit 2026-06-01

## Summary
Timeline page `/routemanagement/timelines/[slug]` — frontend doesn't display correctly after update.

## Context
User reported that after editing and saving a timeline, the frontend display breaks. Page URL: `http://localhost:3000/routemanagement/timelines/smart-en-plus-co-ltdeddd-copy-2d1n-chiang-mai-boutique-hotel-182`. Need multi-agent investigation to identify root cause, debate, and fix.

## Data Flow Trace

### Frontend
```
Contract GET → data.timeline → initialValues.dndCharacterData → Formik → TimeLine/Draggable
Save: Formik.values { dndCharacterData: {...} } → PATCH update-timeline → setData(response)
```

### Key Files
| File | Role |
|------|------|
| `pages/routemanagement/timelines/[slug].js` | Page: fetch, handleSubmit, initialValues |
| `components/draganddrop/TimeLine.js` | Editor: CRUD, DnD, create/copy/delete |
| `components/draganddrop/dragable.js` | Stop card: display + edit dialog |
| `components/draganddrop/DragAndDrop.js` | Formik bridge: `dndCharacterData` field |

### Backend
| File | Role |
|------|------|
| `operators/views.py` | `update_timeline` action, returns `ContractDetailSerializer` |
| `operators/serializers.py` | `TimelineSerializer` with `get_place()` method → full place objects |
| `stations/models.py` | `Timeline`, `TimeLinePlace` models |

## Suspected Root Causes

### 1. Payload Key Mismatch (HIGH)
- Frontend sends: `{ dndCharacterData: { id, title, route, place: [...] } }`
- Backend likely reads: `request.data.get('timeline')` or similar
- `dndCharacterData` ≠ `timeline` → backend ignores update → returns stale data
- **Evidence needed**: read backend `update_timeline` method, check which key it reads

### 2. Place Data Shape Mismatch (HIGH)
- Frontend Autocomplete sets: `place: { id, name, image_gallery: [...] }` (full object)
- Backend expects: `place: <integer_id>` (FK)
- DRF may ignore nested object or error silently
- **Evidence needed**: check backend how it processes `place` field in timeline items

### 3. Response → initialValues Race (MEDIUM)
- After save: `setData(responseData)` → `useMemo([data])` recalcs `initialValues`
- Formik `enableReinitialize={true}` reinitializes
- If response structure differs from initial GET, display breaks
- Both endpoints use `ContractDetailSerializer` so this should be consistent

### 4. `handleAddStop` Default Place Shape (LOW)
- New stop: `place: { id: '', name: '', image_gallery: [] }` — empty string id
- If backend receives this and tries to deserialize, may error
- **Evidence needed**: test adding new stop then saving

## Architecture Observations

### No RTK Query
Timeline uses raw `clientFetchDataFromApi` calls instead of RTK Query. No caching, no automatic invalidation, no loading states from RTK. Manual loading/error management.

### Split API Domains
- Read/write timeline: `/admin-dashboard-operators/contract-details/`
- Delete timeline: `/admin-dashboard-stations/timelines/`
- Two different API prefixes for same feature

### Formik Pattern
- `initialValues = useMemo(() => ({ dndCharacterData: data?.timeline }), [data])`
- Maps backend `timeline` field to Formik `dndCharacterData` field
- On submit, sends back `dndCharacterData` — backend needs to map back to `timeline`

## Investigation Plan

### Phase 1: Backend Confirmation
- Read `update_timeline` method in `operators/views.py`
- Confirm expected request payload shape
- Confirm how `place` field is processed (ID vs object)

### Phase 2: Live Testing
- Start dev server
- Open timeline page, edit stop, save
- Inspect network request/response
- Compare payload shapes

### Phase 3: Fix
- Add transform in `handleSubmit`: `dndCharacterData` → expected backend format
- Extract `place.id` from place objects
- Ensure response maps correctly back to `dndCharacterData`

## Status
**AUDIT IN PROGRESS** — awaiting team investigation

## Related
- [[admin-dashboard]] — Admin interface overview
- [[admin-dashboard-contracts]] — Contract category registry
- [[operators]] — Contract model, timeline FK
- [[stations]] — Timeline, TimeLinePlace models
