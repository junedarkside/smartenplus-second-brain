# Supabase JWT Secret — Location + Auth Pattern for Third-Party JWTs

## Summary
PostgREST uses the **Legacy JWT Secret** (HS256) to verify all JWTs. The new Supabase API Keys page (`sb_secret_...`) is NOT this secret. Wrong secret = PGRST301 401 on every request.

## Problem
Supabase redesigned their dashboard in 2025/2026. Two common wrong locations:
- **API Keys page** → shows `sb_publishable_...` and `sb_secret_...` — these are new-style API keys, NOT JWT signing secrets
- **JWT Keys → JWT Signing Keys tab** → shows the current key (now ECC P-256 asymmetric) — Django can't sign asymmetric JWTs

## Correct Location
**Dashboard → Settings → JWT Keys → Legacy JWT Secret tab → Reveal**

The value is a long base64 string (64+ chars). Set in backend `.env`:
```
SUPABASE_JWT_SECRET=<revealed-value>
```

## Verify Signature (Python)
```python
import hmac, hashlib, base64

secret = '<your-legacy-jwt-secret>'
anon_key = 'eyJ...'  # from dashboard

parts = anon_key.split('.')
hp = '.'.join(parts[:2]).encode()
sig = base64.urlsafe_b64decode(parts[2] + '==')
actual = hmac.new(secret.encode(), hp, hashlib.sha256).digest()
print('match:', hmac.compare_digest(sig, actual))  # must be True
```

## supabase-js v2 Auth Pattern for Django JWTs

**Wrong (breaks with 401 — GoTrue validates against auth.users, Django users not there):**
```js
supabase.auth.setSession({ access_token: djangoJwt, refresh_token: '' })
```

**Correct:**
```js
// helpers/supabaseClient.js
let accessToken = null;
export const supabase = createClient(url, anonKey, {
  accessToken: async () => accessToken,
});
export function setSupabaseToken(token) {
  accessToken = token;
  supabase.realtime.setAuth(token);  // required for Realtime subscriptions
}
```

Call `setSupabaseToken(djangoJwt)` after minting. Call `setSupabaseToken(null)` on cleanup.

## PostgREST Schema Routing
If project exposes multiple schemas (`gmail12go`, `gmailklook`, `public`), PostgREST defaults to first configured schema — NOT `public`. Server-side `requests.post()` must include:
```python
'Accept-Profile': 'public',
'Content-Profile': 'public',
```
`supabase-js` client sends these automatically for the public schema.

## Sequence Permission for INSERT
After creating table, grant to `authenticated` role:
```sql
GRANT USAGE, SELECT ON SEQUENCE public.cs_messages_id_seq TO authenticated;
GRANT INSERT ON TABLE public.cs_messages TO authenticated;
```

## Related
[[chat-supabase-impl-tasks]] · [[cs-chat-supabase-offload]] · [[supabase-ota-booking-store]]
