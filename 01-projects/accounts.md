# Accounts — User Management

## Summary
Custom user model (`AbstractBaseUser`). `USERNAME_FIELD='email'`. `Account` = central. `LoggedInUser` = device logins. `FamilyAndFriend` = passenger profiles for booking. Guest checkout via `BillingProfile.get_or_new()` — no Account needed.

---

## Models

### Account
Custom user model (`AbstractBaseUser` + `PermissionsMixin`). Django auth compatible.

**Key fields:**
- `email` — `USERNAME_FIELD`. Unique. Login identifier.
- `username` — required (not `USERNAME_FIELD`)
- `first_name`, `last_name`
- `phone_number`
- `id_or_passport`
- `datofbirth`
- `profile_image`

**Flags:** `is_admin`, `is_staff`, `is_active`, `is_superadmin`. `date_joined`, `last_login`.

**Auth:** Django standard — session for admin, token for API (DRF).

### LoggedInUser
Device-based login tracking. Links `device_id` to `Account`. `last_login` auto-updated.

Unique constraint: `(device_id,)` — one user per device.

Used for: analytics, device management, session tracking.

### FamilyAndFriend
Passenger profiles linked to Account. Reused across bookings.

Fields: `first_name`, `last_name`, `id_or_passport`, `datofbirth`.

---

## Auth Flows

**Admin:** session-based. Django admin login at `/admin/`. Staff/admin superusers.

**API:** token-based. DRF token auth. `Authorization: Token <token>` header.

**Self-profile endpoints:**
- `GET/PUT /api/user/` — own profile (token auth, no ID). Backend: `UserAPIView` (`RetrieveUpdateAPIView`).
- `GET/PUT /api/users/{id}/` — admin-only since 2026-05-07 (`IsAdminOrIsStaff` on `UserViewSet`).
- Frontend profile page (`pages/account/profile.js`) uses `PUT /api/user/` for updates.

**Guest checkout:** no Account required. `BillingProfile.get_or_new()` creates anonymous profile linked to email. Guest can optionally create account post-order.

**Planned (CS Centralization P1a — [[cs-centralization-stack]]):** `Account` is the Customer-identity base (r2 rejected `BillingProfile` — its manager churns identity per checkout). Account-lite adds **Email-OTP** via `pyotp` + the live AWS SES path; reuse-first, net-new dep `pyotp` only. Existing token/DRF + NextAuth (Google ✓ wired, Apple new) flows extend, not replace.

---

## Related
- [[backend-architecture]]
- [[billings]] (BillingProfile for guest checkout)
- [[bookings]] (BookingPassengerDetail)
- [[smarten-customer-os-thesis]] · [[cs-centralization-stack]] · [[r2-skeptic-review]] (Account = planned Customer identity)