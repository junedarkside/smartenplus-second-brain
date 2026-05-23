# On-Demand Revalidation API Route

## Summary

`pages/api/revalidate.js` — Next.js API route that triggers ISR revalidation on-demand. Called by backend Celery task after admin saves.

## Implementation

```javascript
import { NextResponse } from 'next/server';

const REVALIDATION_SECRET = process.env.REVALIDATION_SECRET;

export async function POST(request) {
  const authHeader = request.headers.get('authorization');
  const secret = authHeader?.replace('Bearer ', '') || request.nextUrl.searchParams.get('secret');

  if (secret !== REVALIDATION_SECRET) {
    return NextResponse.json({ error: 'Invalid token' }, { status: 401 });
  }

  let paths = [];
  try {
    const body = await request.json();
    paths = Array.isArray(body.paths) ? body.paths : [body.path];
    paths = paths.map(p => '/' + p.replace(/\/+$/, '').replace(/^\/+/, ''));
  } catch {
    const pathParam = request.nextUrl.searchParams.get('path');
    if (pathParam) paths = [pathParam];
  }

  if (paths.length === 0) {
    return NextResponse.json({ error: 'No paths provided' }, { status: 400 });
  }

  const results = [];
  for (const path of paths) {
    try {
      await request.revalidatePath(path);
      results.push({ path, status: 'revalidated' });
    } catch (err) {
      results.push({ path, status: 'error', message: err.message });
    }
  }

  const hasErrors = results.some(r => r.status === 'error');
  return NextResponse.json(
    { revalidated: !hasErrors, paths: results },
    { status: hasErrors ? 207 : 200 }
  );
}
```

## Auth

- Bearer token via `Authorization` header
- `?secret=` query param fallback (for management commands)
- `REVALIDATION_SECRET` — server-only env var, never `NEXT_PUBLIC_`

## Returns

- `200` — all success
- `207` — partial failure
- `400` — no paths provided
- `401` — invalid token

## Deployment

1. Frontend first — endpoint sits idle until backend wires in, zero risk
2. Backend second — Celery task calls route after signal fires
3. Verify: admin edit → page updates on next visit (seconds, not hours)

## ISR Pages — 19 Total

| Page | revalidate |
|------|-----------|
| `trips/detail/[...slug].js` | 300s |
| `activities/detail/[...slug].js` | 3600s |
| `airport-transfer/[slug].js` | 3600s |
| `trips/[...slug].js` | 300s |

## Related
- [[docker-standalone-isr-revalidate-gap]]
- [[celery-task-over-bare-thread-django-signals]]
- [[docker-production]]