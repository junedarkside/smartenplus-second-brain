# Accounts — User Management

## Summary
Custom user model (`AbstractBaseUser`). `USERNAME_FIELD='email'`. `Account` is central. `LoggedInUser` tracks device logins. `FamilyAndFriend` stores passenger profiles for booking. Guest checkout via `BillingProfile.get_or_new()` — no Account required.

---

## Models

### Account
Custom user model (`AbstractBaseUser` + `PermissionsMixin`). Django auth compatible.

**Key fields:**
- `email` — `USERNAME_FIELD`. Unique. Used for login.
- `username` — required (not `USERNAME_FIELD`)
- `first_name`, `last_name`
- `phone_number`
- `id_or_passport`
- `datofbirth`
- `profile_image`

**Flags:** `is_admin`, `is_staff`, `is_active`, `is_superadmin`. `date_joined`, `last_login`.

**Auth:** standard Django auth — session-based for admin, token-based for API (DRF).

### LoggedInUser
Device-based login tracking. Links `device_id` to `Account`. `last_login` auto-updated.

Unique constraint: `(device_id,)` — one user per device.

Used for: analytics, device management, session tracking.

### FamilyAndFriend
Passenger profiles linked to Account. Stored per user for reuse in bookings.

Fields: `first_name`, `last_name`, `id_or_passport`, `datofbirth`.

---

## Auth Flows

**Admin:** session-based. Django admin login at `/admin/`. Staff/admin superusers.

**API:** token-based. DRF token authentication. `Authorization: Token <token>` header.

**Self-profile endpoints:**
- `GET/PUT /api/user/` — own profile (token auth, no ID). Backend: `UserAPIView` (`RetrieveUpdateAPIView`).
- `GET/PUT /api/users/{id}/` — admin-only since 2026-05-07 (`IsAdminOrIsStaff` on `UserViewSet`).
- Frontend profile page (`pages/account/profile.js`) uses `PUT /api/user/` for updates.

**Guest checkout:** no Account required. `BillingProfile.get_or_new()` creates anonymous profile linked to email. On order completion, guest can optionally create account.

---

## Related
- [[backend-architecture]]
- [[billings]] (BillingProfile for guest checkout)
- [[bookings]] (BookingPassengerDetail)