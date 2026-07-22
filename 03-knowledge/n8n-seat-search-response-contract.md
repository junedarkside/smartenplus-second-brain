---
name: n8n-seat-search-response-contract
description: n8n /webhook/search (Lomprayah seat availability) response shapes — data is a list of dicts for a real trip but a bare string "no trip" when none; parser must guard or it 500s. Latency 10-19s variable.
metadata:
  type: reference
---

# n8n Seat-Search Response Contract

Operator seat availability proxies through n8n: `https://n8n.smartenplus.co.th/webhook/search`
Called by BE `operators/views.py check_seat_availability` as
`GET ...?from=<opStationId>&to=<opStationId>&date=YYYY-MM-DD&time=HHMM`
(the `operator.seat_availability_api_url`; `from`/`to` come from `OperatorStationMapping.operator_station_id`).

## Response shapes (verified live 2026-07-22)

**Real trip** (e.g. `from=43&to=9`, `from=44&to=9`):
```json
{"status":"success","count":1,"data":[
  {"sourceStation":"Bangkok (Khaosan)","sourceStationId":"43",
   "destinationStation":"Koh Tao","destinationStationId":"9",
   "adultOnewayPrice":1250,"vehicleNameEn":"NORMAL BUS",
   "seatStatus":"33 seat(s) left","departureTime":"22:00","ArrivalTime":"08:45"}]}
```
`data` = **list of dicts**. `43`=normal bus (฿1250), `44`=VIP bus (฿1550).

**No trip** (reversed / invalid / no-service pair, e.g. `9→43`, `43→43`):
```json
{"status":"success","count":0,"data":"no trip"}
```
`data` = **bare string** (NOT a list). ⚠️ Note `status:"success"` even here.

**Some invalid pairs / cold** → empty body (non-JSON) → BE try/except → `OPERATOR_API_ERROR` 502.

## Gotcha — parser must guard `data` type (caused a prod 500)

Original parser assumed a list:
```python
data_list = payload.get('data', [])
item = data_list[0] if data_list else {}   # "no trip"[0] == "n"  (indexes the STRING)
seat_status = item.get('seatStatus', '')   # "n".get(...) → AttributeError → HTTP 500
```
Fix: only use `data[0]` when `data` is a **non-empty list of dicts**; surface a string `data` as a note.
```python
if isinstance(data_list, list) and data_list and isinstance(data_list[0], dict):
    item = data_list[0]
else:
    item = {}
note = data_list if isinstance(data_list, str) else None
# seat_status = item.get('seatStatus','') or (note or '')  → available:null, "no trip"
```

## Latency — 10-19s, variable

Measured warm: 9.9 / 11.4 / 15.7 / 19.1 / 12.2 s. Cold: hangs 25s+. BE timeout was 15s → caught the slow
tail → intermittent 502. Raised to **25s** (`fix/seat-check-timeout-25s`). Real cure is n8n-side workflow
speed (out of BE scope). A "hit it in browser first, then it works" symptom = timing luck, not a fix.

## Related

[[station-mapping-multi-operator-design]] · [[seat-availability-reseller-operator-gap]] · [[supabase-per-operator-schema-routeid]]
