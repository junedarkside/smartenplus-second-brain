# Tour System — Phase 2 Status & Open Gaps

## Summary
Day trip / tour booking feature. Core system production-ready since 2026-01. Phase 2 UI features (time slot selection, add-ons) remain incomplete on frontend. Trust signal fields empty.

## Context
Backend tour system lives in `operators` app (Contract, TimeSlot, ContractAddon, ContractTranslation). Full model docs in [[operators]]. 46+ commits to operators/ and products/ since the original doc was written (2026-03-03) — test/contract counts below may be stale.

## Authoritative Docs
All detail docs live in the repo, not the vault:
- `smartenplus-backend/docs/tour-system/INDEX.md` — backend doc hub (14 files)
- `smartenplus-backend/docs/tour-system/api/backend-api.md` — 30+ endpoints
- `smartenplus-backend/docs/tour-system/pricing/guide.md` — JOIN/PRIVATE/CHARTER pricing logic
- `smartenplus-backend/docs/tour-system/creating-new-contracts.md` — operator guide

## Open Gaps (as of 2026-03-03 — verify current state)

### Trust Signal Data — fields exist, not populated
- `Contract.rating` — empty
- `Contract.review_count` — 0
- `Contract.booking_count_30_days` — 0
- `Contract.badges` — empty array

### Phase 2 Frontend UI — backend ready, UI not built
- Time slot selection UI (`TimeSlot` model + API exist)
- Add-ons booking UI (`ContractAddon` model + `calculate_price()` exist)
- Real-time availability display (API endpoint exists, UI pending)

## Stale Metrics (from 2026-03-03 snapshot)
- 57 active contracts (may have changed)
- 85 backend tests (may have changed — run `python manage.py test operators --keepdb`)

## Related
- [[operators]] — full model reference (Contract, TimeSlot, ContractAddon, ContractTranslation)
- [[backend-architecture]]
- [[bookings]]
