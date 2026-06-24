# rtk-query-dedicated-basequery-per-credential

## Summary
When a new endpoint uses a different auth credential than the app default (e.g. an OTA Bearer token vs the session `accessToken`), it needs a dedicated RTK Query API slice or a custom `baseQuery` variant. One `apiSlice.prepareHeaders` can only inject one credential scheme.

## Why It Matters
Trying to overload the existing session-credentialed `prepareHeaders` for a magic-link/OTA endpoint either attaches the wrong token or needs fragile conditional logic keyed on URL. A separate slice keeps credential boundaries explicit and avoids cross-contaminating the session auth path.

## Detail
```js
// Existing — session auth only
const apiSlice = createApi({
  baseQuery: fetchBaseQuery({
    baseUrl: '/api',
    prepareHeaders: (headers, { getState }) => {
      const token = getState().session.accessToken;
      if (token) headers.set('authorization', `Bearer ${token}`);
      return headers;
    },
  }),
});

// New OTA/magic-link endpoint — dedicated slice, different credential
const otaApi = createApi({
  baseQuery: fetchBaseQuery({
    baseUrl: '/api/cs/ota',
    prepareHeaders: (headers) => {
      headers.set('authorization', `Bearer ${otaTokenFromUrl()}`);
      return headers;
    },
  }),
});
```

## Constraints / Gotchas
- The new credential source may be ephemeral (URL token, not Redux state) — `prepareHeaders` must read it from its actual location.
- Don't add `Authorization` conditionally based on URL inside one `prepareHeaders` — splits auth logic invisibly. Two slices = two clear credential paths.

## Related
- [[ota-portal-review]] — P3a risk source
- [[ota-magic-link-trip-view]]
