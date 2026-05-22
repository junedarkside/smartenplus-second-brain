# Admin Dashboard

Admin dashboard for SmartEnPlus — Thailand transport booking platform. Frontend admin interface for bookings, orders, routes, operators, vehicles, contracts.

## Stack

Next.js 14 (Pages Router) · React 18.2 · MUI 5.14 · RTK Query 1.9 · redux-persist 6.0 · NextAuth 4.22 · Formik + Yup · TipTap 2.3 · date-fns · Tailwind CSS · Recharts · react-dnd

## Repos

| Repo | Path | Role |
|------|------|------|
| `smartenplus-backend` | `~/Desktop/SmartEnPlus/smartenplus-backend` | Django REST API |
| `smartenplus-frontend` | `~/Desktop/SmartEnPlus/smartenplus-frontend` | Customer app |
| `admin-dashboard` | `~/Desktop/AdminDashBoard/admin-dashboard` | This repo — admin interface |

## Structure

```
pages/routemanagement/
  contracts/[slug].js          # Contract detail — main logic
  operators/images/
    index.js                   # Operator image gallery
    ImageEditDialog.js         # Image edit dialog
  hero-banners/
    index.js                   # Hero Banner CRUD (DataGrid + HeroBannerForm)
components/
  contracts/                   # Contract category registry, form fields, policy section
  forms/contract/              # BookingConfig, DayTripDetails, TransportComposit, etc.
  Images/                      # ImageSelection, ProductImages, OperatorImages, DropFilesInput
  heroBanners/
    HeroBannerForm.js          # Formik form with drag-and-drop image upload
  location/                    # LocationCreateDialog (inline location creation)
  orders/                      # Order management, filters, status constants
  utils/                       # AlertProvider, contractUtils, imageHelpers
store/api/                     # RTK Query slices (ordersApi, operatorsApi, heroBannersApi, etc.)
```

## Auth Flow

NextAuth CredentialsProvider → JWT (30d session, 24h refresh) → `AuthSync` `_app.js` → Redux `auth.accessToken` → RTK Query `Bearer` header.

## Related

- [[operators]] — Operator management, contract forms, image gallery
- [[orders]] — Order lifecycle, statuses, refunds
- [[bookings]] — BookingItem, extras, confirmation
- [[backend-architecture]] — Django apps, models
- [[admin-dashboard-contracts]] — Category registry, form flow, payload rules
- [[admin-dashboard-component-patterns]] — Formik+Yup, RTK Query, MUI patterns
- [[hero-banner-cms]] — Hero banner CRUD, FileField vs ImageField, AVIF gotcha, slideshow pattern