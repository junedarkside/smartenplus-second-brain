# Hero Banner CMS

## Summary

Backend-controlled hero banner for the SmartEnPlus homepage. Staff uploads images + sets copy via admin dashboard. Frontend auto-rotates banners as a slideshow.

## Context

Homepage previously had a hardcoded static image (`bgDefault` local webp). Marketing needed to swap hero images without a deployment. Solution: `HeroBanner` model in `pages_info` app, served via `/front-page/` and `/hero-banners/` endpoints, managed via admin dashboard CRUD page.

## Details

### Backend — `pages_info` app

**Model** (`pages_info/models.py`):
```python
class HeroBanner(models.Model):
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=300, blank=True)
    image = models.FileField(upload_to='hero-banners/', validators=[_validate_banner_image])
    link_url = models.URLField(blank=True)
    link_text = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    display_order = models.PositiveIntegerField(default=0, db_index=True)
    ordering = ['display_order', 'id']
```

`FileField` not `ImageField` — Pillow 9.3.0 has no AVIF decoder so `ImageField` rejects AVIF files. Extension validator (`_validate_banner_image`) enforces `jpg/jpeg/png/webp/gif/avif`.

**Migrations:** `0008_herobanner`, `0009_alter_herobanner_image` (ImageField→FileField)

**Endpoints:**
- `GET /hero-banners/` — public, returns active banners ordered by `display_order`
- `POST/PATCH/DELETE /hero-banners/{id}/` — staff only (`IsAdminOrWriteOnly` perm: `pages_info.change_termsandconditions`)
- `GET /front-page/` — now includes `hero_banners` array (injected in `FrontPageViewSet.list()`)

**Permission:** `IsAdminOrWriteOnly` — same as all other `pages_info` endpoints. GET public, writes require `pages_info.change_termsandconditions`.

**Django Admin:** `HeroBannerAdmin` — `list_editable` for `is_active` and `display_order` for quick toggling.

### Admin Dashboard — `admin-dashboard`

**Files created:**
- `store/api/heroBannersApi.js` — RTK Query slice (5 endpoints: list, detail, create, update, delete)
- `components/heroBanners/HeroBannerForm.js` — Formik+Yup form with drag-and-drop image upload
- `pages/routemanagement/hero-banners/index.js` — DataGrid CRUD page

**Files modified:**
- `store/index.js` — registered reducer, middleware, blacklist; bumped `currentVersion` 1.7→1.8
- `components/sidemenu/menuData.js` — "Hero Banners" nav item (`FeaturedPlayListOutlined` icon, already imported)

**Nav path:** Route Management → Hero Banners

**Image upload:** drag-and-drop + click. Accepts JPG/PNG/WebP/GIF/AVIF, max 10MB. `FormData` POST.

**Key gotcha:** `display_order` and `is_active` need explicit handling in FormData submit — `display_order` defaults to `0` when empty, `is_active` serialized as `"true"`/`"false"` string. DRF `BooleanField` accepts string booleans in multipart.

### Frontend — `smartenplus-frontend`

**File modified:** `pages/homepagev2.js`

```js
const heroBanners = frontPageData?.hero_banners || [];
const [heroBannerIndex, setHeroBannerIndex] = useState(0);
const heroBannerImage = heroBanners.length > 0 ? (heroBanners[heroBannerIndex]?.image || null) : null;

useEffect(() => {
  if (heroBanners.length <= 1) return;
  const timer = setInterval(() => {
    setHeroBannerIndex((i) => (i + 1) % heroBanners.length);
  }, 5000);
  return () => clearInterval(timer);
}, [heroBanners.length]);
```

`imgUrl={heroBannerImage || bgDefault}` — fallback to local image if no banners.

**SEO:** No impact. `<h1>` and meta tags come from `getStaticProps` (SSG). Slideshow timer is client-only. Googlebot sees first banner image as static HTML.

**Slideshow interval:** 5000ms. Change in `homepagev2.js`.

## Tradeoffs

| Decision | Why |
|----------|-----|
| `FileField` over `ImageField` | Pillow 9.3.0 can't decode AVIF. Extension validator is sufficient for hero banners. |
| `pages_info` app (not new app) | Already owns CMS content. Same permission pattern. Avoids new app overhead. |
| `/front-page/` injection | Frontend already calls this endpoint. Zero new API calls. |
| 5s slideshow, no controls | Simple. Banners are background context, not interactive content. Add controls later if needed. |
| `display_order` not unique | No `unique_together` constraint — admin can have gaps/ties. Simple enough for now. |

## Related

- [[backend-architecture]] — pages_info app context
- [[admin-dashboard-component-patterns]] — Formik+FormData+RTK Query patterns
- [[admin-dashboard-image-pipeline]] — image upload patterns
- [[nextjs-patterns]] — SSG/ISR, `getStaticProps`
