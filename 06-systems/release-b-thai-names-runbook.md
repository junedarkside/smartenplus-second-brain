# Release B runbook — Thai names for Locations/Stations (ship + rollback)

> Written session #444 (2026-10-01). Code is on `develop` in both repos (BE `07ad9dc`, FE `4fb62b9c`), **not on `main`**. The owner ships production; Claude never touches production. Release A (Thai chrome, `lang_th` flag ON) is already live.

## Two switches (do not confuse)
| | Flag `lang_th` | Approval (`is_reviewed`) |
|---|---|---|
| Controls | the whole Thai site (kill switch) | one Thai NAME at a time |
| Who | owner/admin with `change_featureflag` (NOT "Thai editors") | "Thai editors" group |
| Where | Django admin `/securelogin/` → CS → Feature flags → `lang_th` → Enabled | Location/Station list → tick rows → Actions → "Approve selected translations"; or tick "is reviewed" in the item; filter "translation review" finds drafts |
| Effect delay | ≤60 s (BE cache) | API immediate; FE ISR pages ≤1 min–1 h (results page ≤300 s, `/locations` ≤60 s, homepage/`/trips`/airport ≤3600 s → run `pages/api/revalidate.js`) |
Thai names appear only after approval. The flag is already ON; there is **no "turn the flag on" step** for names.

## Decision: deploy code first, content later
Ship code with empty translation tables; import machine draft as **unreviewed drafts only**; reviewer's sheet gates only the APPROVAL. Never `--auto-approve` machine text.

## Pre-ship (owner, read-only)
1. **`Account.has_perm` change** (`accounts/models.py`: `is_admin or super().has_perm()`): `super()` grants everything to active `is_superuser=True`; non-admin staff with hand-assigned groups/user perms gain them. Check: `Account.objects.filter(is_superuser=True, is_admin=False)` and `filter(is_staff=True, is_admin=False)` + groups/user_permissions. Decide keep/restrict (e.g. only honour group "Thai editors").
2. `pg_stat_activity` for long transactions; **RDS snapshot**; optional: run migrations on a restored snapshot (else record "untested on RDS" — SQL reviewed: new empty tables + 4 nullable columns).
3. Read-only diff of the 32 `POPULAR_DESTINATIONS.name` (FE `utils/destinations.js`, `nameTh` interim) vs real `Location.location_name`.
4. Re-run English golden diff (below) on the exact `main` merge commit.

## Ship (owner, quiet window)
1. **BE**: `docker-compose -f docker-compose-rds.yml build --no-cache web` then `up --no-deps web -d`. `migrate` runs at container start (only `stations/0042`, `0043`); expect **10–30 s of 502** (1 gunicorn worker). Leave `lang_th` as is.
2. Once: `docker-compose -f docker-compose-rds.yml exec web python manage.py ensure_thai_editors_group`; add editors in admin (`is_staff` + group "Thai editors", **not** `is_admin`).
3. **FE**: push `main` (GitHub Actions → `scripts/deploy-ghcr.sh`); confirm log line "Cleared" for volume `smartenplus_next_cache` (script warns and continues if removal fails).
4. Verify English unchanged (golden curls).

## Content
- Reviewer fills `export_station_names` CSV (columns `*_th`). **Pitfalls:** stations description column is the real typo `desciption_th_html`; keep `english_name_at_export` byte-identical (Excel trim/re-case → `skipped_english_name_changed`); names >100 chars → silent `skipped_invalid` (dry-run counts are the only signal); HTML allowlist `p,br,b,i,em,strong,u,ul,ol,li,a(href),h2-4`; "any hotel" (44 stations) = one agreed naming pattern; 15 operator-owned stations: put on a separate tab, verify with dry-run (code does not confirm owner handling). Expect 95 locations / 210 stations.
- Deliver CSV (container `mem_limit` is **256 m**; run when idle; use `exec`, not `run`):
  `CID=$(docker-compose -f docker-compose-rds.yml ps -q web); docker cp sheet.csv $CID:/tmp/names.csv`
  `docker-compose -f docker-compose-rds.yml exec web python manage.py import_station_names --kind locations --file /tmp/names.csv --dry-run` (then without `--dry-run` + `--batch-id prod-th-1`; same for `--kind stations`).
- Approve: admin bulk action (flushes caches automatically). After any `--auto-approve --reviewed-by "<name>"` import run once: `manage.py shell -c "from stations.translation_signals import flush_translation_caches as f; f()"` (the deferred flush runs before the transaction commits).
- Rollback of an import: `--rollback --kind K --batch-id prod-th-1` (deletes drafts + auto-approved rows; keeps rows a person approved).

## Smoke tests (public API; paths have no `/api/` prefix; fields are `translated_*`)
`curl -s "https://api.smartenplus.co.th/stations/?search=phuket&lang=en"` — must be identical to the pre-ship capture, no `translated_*`. With `&lang=th`: `translated_*` present (approved = Thai, others = English fallback). Same pairs for `/locations/?summary=true&limit=5000`, `/front-page/`, `/stationsinfo/<slug>/`. Also `-H 'Accept-Language: th'` without `lang`.

## Monitoring / rollback
Watch 30–60 min + 24 h: Sentry on stations/locations/front-page, 5xx rate, queries per request, cache hit ratio, p95 `/locations`, FE hydration warnings under `/th`. **Rollback triggers:** English 5xx rise, English payload diff, queries/p95 > ~+30 %, Thai text in a cart/order value, hydration errors. **Ladder:** unapprove names (names only) or flag `lang_th` OFF (whole Thai site) → `import_station_names --rollback --batch-id` → previous FE image. **Never reverse migrations 0042/0043** (drops the translation tables and loses all translations). Old code on the new DB is safe; new code on an old DB errors (migrate-at-start prevents it).

## Verified before this runbook (#443–#444)
BE 1209 tests 6F/87E = baseline; FE jest 225F/38 (224 once) = baseline; isolated `next build` ok; English parity vs Release A: 17/17 APIs + 6 pages (real-volume 95/210 run), 22/23 endpoints with real trips (tripfilter list order only); only new migrations 0042/0043; no FE package/config/Docker changes; admin-dashboard: sends no `lang`; renaming a station/location via its API keeps Thai text but un-reviews it and clears the approver, slug regenerates (existing), other-field PATCH leaves translations; `/th` funnel (picker → results → cart → checkout, headless): values/URLs/cart payloads English, no Thai in any API URL/body except the typed picker search, persisted state/sessionStorage Thai-free; English pages in a Thai-language browser: zero Thai names.

## Still English at go-live (put in launch notes)
Cart/checkout UI (by design), emails/PDF (`BE-EMAILS-EN-ONLY`), filter chips, `EnhancedTripCard`, "recent searches", station-slug routes, station descriptions (fallback), lowercase `koh-lipe` in English boxes, `AddTripModal` placeholders. SEO: `/th` stays blocked by robots + out of sitemap; canonicals are per page type (homepage `/th` self-canonical + hreflang th → blocked URL; other pages English path) → make robots/sitemap/canonical/hreflang consistent TOGETHER before any indexing.

## Owner decisions (defaults)
Reviewer name + date (`--reviewed-by`); approve names after verification in a quiet window; `/th` noindex 1–2 weeks after launch; accept `nameTh` interim + 32-name diff; migration test on snapshot (recommended); keep/restrict `Account.has_perm`.
