# Hero Banner CMS

## Summary
Backend-controlled hero banner. Staff uploads images + copy via admin dashboard. Frontend auto-rotates as slideshow.

## Context
Homepage had hardcoded static image. Marketing needed to swap without deployment. `HeroBanner` model in `pages_info` app, served via `/front-page/` + `/hero-banners/`, managed via admin CRUD.

## Backend — `pages_info` app

**Model:**
```python
class HeroBanner(models.Model):
    title = CharField(max_length=200)
    subtitle = CharField(max_length=300, blank=True)
    image = FileField(upload_to='hero-banners/', validators=[_validate_banner_image])
    link_url = URLField(blank=True)
    link_text = CharField(max_length=100, blank=True)
    is_active = BooleanField(default=True, db_index=True)
    display_order = PositiveIntegerField(default=0, db_index=True)
    ordering = ['display_order', 'id']
```

`FileField` not `ImageField` — Pillow 9.3.0 has no AVIF decoder. Extension validator enforces `jpg/jpeg/png/webp/gif/avif`.

**Endpoints:** `GET /hero-banners/` (public, ordered), `POST/PATCH/DELETE /hero-banners/{id}/` (staff), `GET /front-page/` (includes `hero_banners` array).
**Permission:** `IsAdminOrWriteOnly` — `pages_info.change_termsandconditions`.
**Migrations:** `0008_herobanner`, `0009_alter_herobanner_image`

## Admin Dashboard

**Files:** `store/api/heroBannersApi.js` (RTK Query, 5 endpoints), `components/heroBanners/HeroBannerForm.js` (Formik+Yup, drag-drop upload), `pages/routemanagement/hero-banners/index.js` (DataGrid CRUD).
**Nav:** Route Management → Hero Banners.
**Gotcha:** `display_order` defaults to `0` when empty. `is_active` as `"true"`/`"false"` string in FormData.

## Frontend — `smartenplus-frontend`

**File:** `pages/homepagev2.js`

```js
const heroBanners = frontPageData?.hero_banners || [];
const [heroBannerIndex, setHeroBannerIndex] = useState(0);
const heroBannerImage = heroBanners.length > 0 ? heroBanners[heroBannerIndex]?.image : null;
useEffect(() => {
  if (heroBanners.length <= 1) return;
  const timer = setInterval(() => setHeroBannerIndex(i => (i + 1) % heroBanners.length), 5000);
  return () => clearInterval(timer);
}, [heroBanners.length]);
```

`imgUrl={heroBannerImage || bgDefault}` — fallback to local image. Slideshow 5s. Client-only, no SEO impact.

## Tradeoffs

| Decision | Why |
|----------|-----|
| `FileField` | Pillow 9.3.0 can't decode AVIF. Extension validator sufficient. |
| `pages_info` app | Already owns CMS content. Same perms. No new app overhead. |
| `/front-page/` injection | Frontend already calls this. Zero new API calls. |
| 5s slideshow, no controls | Banners are background context. Add controls later. |

## Related
- [[backend-architecture]]
- [[admin-dashboard-component-patterns]]
- [[admin-dashboard-image-pipeline]]
- [[nextjs-patterns]]
