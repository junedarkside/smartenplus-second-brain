# Stations — Spatial Data Layer

## Summary
Stations app manages locations, stations, places, and route timelines. Provides spatial data for search, booking, and route visualization. Key: `Station` (physical stops), `Location` (city/province/country), `Place` (hotels/ports/pickup points), `Timeline` (route itinerary with icons).

---

## Models

### Location
City/province/country hierarchy. Used for route departure/arrival.

Fields: `location_name`, `city`, `province`, `country` (FK to `Country`), `normalized_location_name` (indexed, auto-lowercased via signal), `image`.

### Station
Physical transport stop. Linked from `Route.departure_station` / `arrival_station`.

**Key fields:**
- `station_name`, `slug` (auto-slugified)
- `iata_code` — 3-letter IATA code, unique. **Validation:** only `station_type='airport'` can have IATA code.
- `station_type` — 33 choices (airport, train_station, metro, bus_station, bus_stop, port, pier, ferry_terminal, hotel, hostel, resort, motel, guesthouse, bnb, beach, park, campground, helipad, parking_lot, rest_area, service_station, other)
- `location_name` FK to `Location`
- `required_extra_info` — bool
- `desciption` (RichText), `google_maps_link`
- `normalized_station_name` (indexed, auto-lowercased)

**`clean()` validation:** IATA code only allowed for airport type. `save()` calls `full_clean()`.

### Image
Generic image model. Used by `PlaceImage` M2M through table.

### Place
Pickup/dropoff/meeting points. `Contract.meeting_point_place` FK.

**Fields:**
- `place_type` — airport/hotel/port/pier/train_station/bus_station/beach/other
- `owner` — FK to `Operator` (nullable — general vs operator-specific)
- `name`, `location` FK
- `image_gallery` — M2M to `Image` via `PlaceImage` (caption per entry)
- `google_url`

### Timeline
Route itinerary. `Contract.timeline` FK.

`place` M2M to `Place` via `TimeLinePlace`.

### TimeLinePlace
Through table: Timeline ↔ Place.

Fields: `title`, `place` FK, `timeline` FK, `description` (RichText), `time`, `order`, `icon` (FontAwesome choices: bus/van/car/hotel/ferry/departure/arrival/home/star/rocket/globe/beach/pier).

### RouteByLocationInfo
Blog-style route pages. `departure_location` + `arrival_location` FK to `Location`. `overview` text, `blog_slug` (unique).

---

## Relationships

- `Route.departure_station` / `arrival_station` → `Station`
- `Route` → `Trip` → `Route` (route has many trips)
- `Contract.timeline` → `Timeline` → `TimeLinePlace` → `Place`
- `Contract.meeting_point_place` → `Place`

---

## Related
- [[operators]] (Contract uses Place, Timeline, Station)
- [[products-routes]] (Route/Trip relationship)