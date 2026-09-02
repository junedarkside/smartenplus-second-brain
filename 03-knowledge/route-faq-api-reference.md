# Route FAQ API Reference

## Overview
Feature lets each departure→arrival route carry an editable FAQ list, shown on the public trip page (`/trips/{from}/{to}`). No model literally named `RouteInfo` — real model is `RouteByLocationInfo` (app `stations`), 1→N `RouteFAQ`. Serializers/views live in `products` app, not `stations`.

Two write paths exist for `RouteFAQ`:
- **Agent path** (`RouteFAQViewSet`) — single service account (`is_route_faq_agent=True`), no admin UI, likely automation/bulk-load.
- **Staff admin path** (`RouteFAQAdminViewSet`) — human staff via admin dashboard, has optimistic-concurrency guard.

Both write paths trigger Next.js ISR revalidation of the trip page on save/delete.

---

## Models

### `RouteByLocationInfo` (`stations/models.py:249`)
| Field | Type | Notes |
|---|---|---|
| `departure_location` | FK → `Location` | `related_name='departure_routes'` |
| `arrival_location` | FK → `Location` | `related_name='arrival_routes'` |
| `overview` | `TextField` | route description |
| `blog_slug` | `SlugField` | unique, nullable, max 200 |

### `RouteFAQ` (`stations/models.py:262`)
| Field | Type | Notes |
|---|---|---|
| `route` | FK → `RouteByLocationInfo` | `related_name='faqs'` |
| `faq_slug` | `SlugField` | nullable, max 200 |
| `question` | `CharField` | max 255 |
| `answer` | `RichTextField` | HTML, sanitized on write (see below) |
| `order` | `PositiveIntegerField` | default 0, `Meta.ordering = ['order']` |
| `is_active` | `BooleanField` | default `True` |
| `created_at` / `updated_at` | `DateTimeField` | auto |
| `updated_by` | FK → `AUTH_USER_MODEL` | nullable, `SET_NULL` |

Related flag: `accounts.Account.is_route_faq_agent` (`BooleanField`, default `False`) — gates the agent write endpoint.

---

## Endpoints

Base prefix for all routes below: `admin-dashboard-routes/` (mounted in `Smartenplus/urls.py`). **Prefix is legacy naming — `home/` action is public, unauthenticated.** Not an auth boundary.

### 1. Public — Route + FAQ read
`GET admin-dashboard-routes/home/<departure>/<arrival>/`
View: `HomeViewSet.custom_route` (`products/views.py:1648`)
Auth: **none** (public)
Path params: `departure`, `arrival` — free text, normalized (lowercased, `-`/spaces stripped) then matched `icontains` against `Location.normalized_location_name` / `location_name`.

Response:
```json
{
  "routes": [
    {
      "...RouteByLocationInfo fields...": "...",
      "departure_location": { "...LocationSerializer...": "..." },
      "arrival_location": { "...LocationSerializer...": "..." },
      "route_by_from": "...",
      "route_by_to": "...",
      "avaliable_routes": "...",
      "faqs": [
        { "id": 1, "question": "...", "answer": "<p>...</p>", "order": 0 }
      ]
    }
  ],
  "contracts": [ "...ExteaContractSerializer output..." ],
  "route_faq": {
    "min_display_rate": 350.0,
    "cheapest_operator": "string|null",
    "operator_count": 3,
    "operator_names": ["..."],
    "has_direct_route": true,
    "cancellation_summary": {
      "operator": "string|null",
      "is_cheapest_operator": true,
      "tiers": [{ "hours": 24, "refund_pct": 100 }]
    }
  }
}
```
Notes:
- `faqs` filtered `is_active=True`, ordered by `order`, served from a prefetch (`to_attr='active_faqs'`) — no N+1.
- `route_faq` aggregate cached 5 min TTL, computed from active contracts (`is_actived=True`, `end_date__gte=today`).

---

### 2. Agent write — `RouteFAQViewSet`
Router basename `route-faqs` → prefix `admin-dashboard-routes/route-faqs/`
Auth: `IsRouteFAQAgent` (only account with `is_route_faq_agent=True`)
Throttle: `route_faq_agent` scope, **100/hour**
Methods: **`POST` only** — no GET/list/PUT/PATCH/DELETE (`http_method_names = ['post', 'head', 'options']`). Restricted after a 3-lens (BD/backend/security) review concluded an unreviewed automation account editing/deleting existing rows (no per-row ownership check — could touch any FAQ, not just its own) was a bigger blast radius than it adding junk rows; staff already owns full CRUD via `route-faqs-admin/`.
Serializer: `RouteFAQWriteSerializer`

| Method | Path | Body | Response |
|---|---|---|---|
| `POST` | `route-faqs/` | `{route, question, answer, order, is_active}` | created `RouteFAQ` (write shape) |

`perform_create` sets `updated_by = request.user` **and force-overrides `is_active=False`**, regardless of what the request body sends. Agent-created FAQs never go live automatically — public read (`home/<from>/<to>/`) filters `is_active=True`, so a new row is invisible on the trip page until a staff member reviews it and flips `is_active=True` via `route-faqs-admin/` (PATCH). This is the review gate: staff, not the agent, decides what publishes.

**No server-side `order` auto-assignment.** `perform_create` only sets `updated_by` — `order` defaults to `0` in the model if omitted from the body, and there is no unique constraint on `(route, order)`. Caller must compute the next `order` itself (read `faqs[]` from `home/<from>/<to>/`, take `max(order) + 1`) or new FAQs will collide at `0`/whatever value was sent and sort arbitrarily among ties.

**No dedup / no unique constraint on `(route, question)`** — nothing stops creating the same FAQ twice. Caller must check `faqs[]` from the public read before POSTing to avoid duplicates; retrying a script without this check will pile up copies.

**Validation error shape** — no custom `EXCEPTION_HANDLER` configured, so 400s are plain DRF field-error dicts, e.g. `{"question": ["This field may not be blank."], "route": ["Invalid pk \"999\" - object does not exist."]}`. `answer` never rejects on unsafe HTML — see `validate_answer` below, it silently strips instead of raising.

---

### 3. Staff admin CRUD — `RouteFAQAdminViewSet`
Router basename `route-faqs-admin` → prefix `admin-dashboard-routes/route-faqs-admin/`
Auth: `IsAdminOrIsStaff`
Throttle: none
Methods: full CRUD (`ModelViewSet`)
Read serializer: `RouteFAQAdminReadSerializer` — write serializer: `RouteFAQWriteSerializer`

| Method | Path | Query/body | Response |
|---|---|---|---|
| `GET` | `route-faqs-admin/` | `?route=<id>&is_active=false&page=&page_size=&all=true&ordering=order` | paginated `{count, total, page_size, results: [...]}` |
| `GET` | `route-faqs-admin/{id}/` | — | single `RouteFAQAdminReadSerializer` |
| `POST` | `route-faqs-admin/` | `{route, question, answer, order, is_active}` | created |
| `PUT`/`PATCH` | `route-faqs-admin/{id}/` | body + optional `updated_at` | updated, or `409` |
| `DELETE` | `route-faqs-admin/{id}/` | — | 204 |

**Optimistic concurrency**: if request body includes `updated_at`, view does `select_for_update()` in a transaction and compares to DB row's `updated_at`. Mismatch → custom `Conflict` exception, `status_code=409`, message: `"This FAQ was changed by someone else. Reload and try again."` Omit `updated_at` to skip the check.

**`?is_active=false` filter** (`get_queryset`) — lists all pending-review rows across every route in one call, not scoped to a single `route_id`. This is the review queue: agent-created FAQs land `is_active=False` (see `RouteFAQViewSet` above), so `GET route-faqs-admin/?is_active=false` is how staff find what needs review without knowing which route it landed on. Accepts `true`/`1` (case-insensitive) for active, anything else for false.

Admin read shape adds fields not public: `route, created_at, updated_at, updated_by`.

---

### 4. Route picker (autocomplete) — `RouteByLocationInfoPickerViewSet`
Router basename `route-picker` → prefix `admin-dashboard-routes/route-picker/`
Auth: `IsAdminOrIsStaff`
Methods: `GET` only (read-only)

| Method | Path | Query | Response |
|---|---|---|---|
| `GET` | `route-picker/` | `?search=<text>` (icontains on departure/arrival location name) + pagination | paginated `{id, departure_location_name, arrival_location_name}[]` |
| `GET` | `route-picker/{id}/` | — | single object, same shape |

Purpose: populates admin dashboard's route Autocomplete when attaching a FAQ to a route. `RouteByLocationInfo` itself has no full CRUD endpoint anywhere.

---

## Route discovery

No endpoint lists all `RouteByLocationInfo`/FAQ routes directly. Three list-ish endpoints exist on `HomeViewSet` + the picker — don't conflate them:

| Endpoint | Model | Auth | Gives you |
|---|---|---|---|
| `GET home/?no_pagination=true` | `Route` (via `HomeSerializer`) | none | every bookable route + stations — this is what the frontend sitemap generator uses |
| `GET home/locations-and-slugs/` | `Route` (via `RouteLocationAndSlugSerializer`) | none | flat departure/arrival name + slug pairs |
| `GET route-picker/?search=` | `RouteByLocationInfo` | `IsAdminOrIsStaff` | FAQ-content routes, requires a search term — not a full list |

The two `home/` list actions are `Route`-based (bookable/priced routes — what *should* have FAQ content), not `RouteByLocationInfo`-based (what *already has* FAQ content). `route-picker/` is the only lister on the FAQ model itself, and it's staff/admin only — an `IsRouteFAQAgent` account (not staff/admin) cannot call it and has **zero route-discovery capability of its own**.

**`home/?no_pagination=true`** — confirmed live consumer: `smartenplus-frontend/pages/server-sitemap.xml/index.js:320` (`generateRoutesSitemap()`), which filters the response to `operator_count > 0` and builds every `/trips/{from}/{to}` sitemap URL from `route.departure_station.location.location_name` / `route.arrival_station.location.location_name`.
```
GET https://api.smartenplus.co.th/admin-dashboard-routes/home/?no_pagination=true

# response — array, one entry per bookable route
[{
  "departure_station": { "location": { "location_name": "Bangkok" } },
  "arrival_station": { "location": { "location_name": "Phuket" } },
  "operator_count": 3,
  "updated_at": "2026-08-01T00:00:00Z"
}]
```

**Discovery flow for an agent account** (no staff/admin role): pull all pairs from `home/?no_pagination=true` → for each pair, call `home/<from>/<to>/` (endpoint 1 above) to check whether `routes[0].faqs` is already populated and grab `routes[0].id` → decide continue/append vs skip → write via `route-faqs/` (endpoint 2) using that `id`.

---

## Sanitization
`RouteFAQWriteSerializer.validate_answer` (`products/serializers.py:961`) runs `bleach.clean(value, strip=True)` on write — a DRF `validate_<field>` hook, auto-invoked when `answer` is deserialized.
- Allowed tags: `p, br, b, i, em, strong, u, ul, ol, li, a`
- Allowed attrs: `{'a': ['href']}`
- Allowed protocols: `http, https, mailto`

**`strip=True` — never raises.** Disallowed tags/attrs/protocols are silently removed, not rejected. No 400 for "unsafe" HTML; the saved/returned `answer` may differ from what was sent. Caller should not assume its markup was preserved as-is. `question`/`answer` do still 400 on blank (`allow_blank=False`).

Mirrors frontend `sanitizeHtml.js` ALLOWED_TAGS — keep both in sync if either changes.

---

## Side effects — ISR revalidation
`post_save` / `post_delete` signals on `RouteFAQ` (`stations/signals.py::revalidate_route_faq`) enqueue Celery task `products.tasks.revalidate_route_faq_isr`:
```
POST {FRONTEND_URL}/api/revalidate
Authorization: Bearer {REVALIDATION_SECRET}
Body: {"from": <departure_slug>, "to": <arrival_slug>}
```
Triggers Next.js on-demand ISR for `/trips/{from}/{to}`. Fires on both agent and staff-admin write paths (same model, same signal).

---

## Auth summary
| Endpoint | Auth | Notes |
|---|---|---|
| `GET home/<departure>/<arrival>/` | none | public trip page data |
| `route-faqs/` (POST only) | `IsRouteFAQAgent` | single service account, 100/hr throttle, force `is_active=False` |
| `route-faqs-admin/` (full CRUD) | `IsAdminOrIsStaff` | staff/admin dashboard, 409 optimistic-lock |
| `route-picker/` (GET) | `IsAdminOrIsStaff` | autocomplete source |

---

## AI agent access

Same JWT flow as any client — no agent-specific auth mechanism exists beyond the calling account's role flag (`is_route_faq_agent`, `is_admin`, `is_staff`).

**Obtain credentials** — `POST /api/token/` → `MyTokenObtainPairView` (`apis/urls.py:138`). Access token 24h lifetime, refresh 7d, rotates on use (`Smartenplus/settings.py:432` `SIMPLE_JWT`). Send `Authorization: Bearer <access>` on every authenticated call; refresh via `POST /api/token/refresh/`.
```
POST https://api.smartenplus.co.th/api/token/
{ "email": "agent@smartenplus.com", "password": "..." }

# 200
{ "access": "eyJhbGciOi...", "refresh": "eyJhbGciOi..." }
```

Per-endpoint credential requirement:
- `home/` (read, discovery) — no token needed
- `route-faqs/` (agent write) — token must belong to the one account with `is_route_faq_agent=true`
- `route-faqs-admin/`, `route-picker/` — token must belong to an `is_admin` or `is_staff` account

An `is_route_faq_agent` account cannot also assume staff/admin scope through the same token — the two write paths are deliberately kept separate (`products/views.py:1718` docstring: "keeping them physically separate means IsRouteFAQAgent has exactly one call site, always").

---

## Related
- [[api-endpoints]] (index entry)
- `08-archive/help-faqs-landing-2026-06-07/` — unrelated, older WordPress-sourced general Help/FAQs page. Do not conflate.
