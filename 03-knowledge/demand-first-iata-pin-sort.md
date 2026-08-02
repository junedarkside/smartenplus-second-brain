# Demand-first IATA pin sort (zero-BE, degrades safe)

**What:** Order an airport/station list so high-demand entries lead, with no backend column, no analytics feed, no A-Z machinery. Pin a fixed IATA priority list; everything else keeps natural order. Source: `pages/airport-transfer/index.js` `sortedStations` useMemo (#282).

```js
const sortedStations = useMemo(() => {
  const priority = ['BKK', 'DMK', 'HKT', 'CNX', 'USM']; // ~85-90% of TH transfer demand
  const rank = (s) => {
    const i = priority.indexOf((s.iata_code || '').toUpperCase());
    return i === -1 ? priority.length : i;   // unranked → bucket after all pinned
  };
  return [...currentItems].sort((a, b) => rank(a) - rank(b));
}, [currentItems]);
```

**Why pin by IATA, not by DB order or a `sort_weight` column:**
- **Degrades safe:** an airport not in the DB is simply *absent* from the list — never a dead/empty pinned slot. A `sort_weight` FK would need backfill + admin UI + can point at a deleted row.
- **Zero BE:** no migration, no annotation, no analytics dependency. Demand share is a stable domestic fact (BKK/DMK/HKT/CNX/USM carry the vast majority) — hardcoding it is correct, not a hack, for a <12-item catalog.
- **Stable, not clever:** `indexOf → rank` is a 3-line pure function. No chained ternaries, no `Intl.Collator`, no A-Z toggle UI (that machinery was dropped — over-engineering for 4 airports).

**When this stops scaling:** catalog >12 airports, or measured picker drop-off → then earn a real popularity signal (booking-count annotation) + search field. Until then, the pin is the simplest thing that works.

**Pairs with:** the "Popular" badge on the same IATA set (`POPULAR_IATA = ['BKK','DMK','HKT']`) so the visual cue matches the sort. Keep the two lists intentionally — badge is a tighter subset (top-3) than the sort pin (top-5).

Related: [[station-type-airport-first-class-iata-restriction]] · [[airport-transfer-at1-redesign-spec]]
