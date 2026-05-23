# PersistGate SSR Suppresses Head Component

## Summary

`PersistGate loading={null}` renders null on server. Everything inside — DefaultSeo, Head, Layout — suppressed during SSR. Result: empty og tags in view-source, crawlers see blank shell.

## Symptom

```
curl http://localhost:3000/ | grep 'next-head-count'
→ content="2" (should be 14+)
opengraph.dev → empty meta tags
view-source → no og:image, og:title, og:description
```

## Root Cause

```jsx
// BAD — everything suppressed SSR
<PersistGate persistor={persistor} loading={null}>
  <DefaultSeo ... />
  <Layout>
    <Component {...pageProps} />
  </Layout>
</PersistGate>
```

## Fix

Hoist meta components above PersistGate. Only wrap client-only utilities inside.

```jsx
// GOOD — meta + page render SSR; persist wraps only client utilities
<DefaultSeo ... />
<Head>...</Head>
<Layout>
  <PersistGate persistor={persistor} loading={null}>
    <RefreshTokenHandler ... />
    <DevToolsProvider />
  </PersistGate>
  <Component {...pageProps} />
</Layout>
```

Fixed in `_app.js` commit `ac6f8aa`. Verified `next-head-count="14"` after fix.

## Related
- [[webpack-image-src-og-absolute-url-rule]]
- [[nextjs-patterns]]
- [[og-image-ssr-fix-2026-05-23]]