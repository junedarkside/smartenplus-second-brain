# E2E Tests Cannot Verify 410-on-POST for CSRF-Protected Legacy Routes

## Summary
Django's `CsrfViewMiddleware` returns 403 before any view runs, so Playwright/E2E tests that POST to a CSRF-protected route will never reach a 410-returning view. Use GET on the same URL to prove the 410 contract; assert 403 on POST to prove CSRF protection is still enforced.

## Context
Adding `HttpResponse(status=410)` to a legacy endpoint (e.g., `payments/webhook-legacy/`, `placeorder/`) to deprecate it. Tests need to verify (a) the 410 fires for honest callers and (b) CSRF protection still works.

## Problem
E2E test sends `POST /legacy-route/` expecting 410. Server returns 403. Test fails. The 410 IS implemented correctly — but the test can never reach it from outside without a valid CSRF token, and forging a CSRF token defeats the protection being verified.

## Pattern: split into 2 tests, one per contract

```ts
// Test 1: GET proves the view returns 410 (CSRF middleware is method-agnostic — only runs on unsafe methods)
test('GET /legacy-route/ returns 410', async ({ request }) => {
  const r = await request.get(`${API_URL}/legacy-route/`);
  expect(r.status()).toBe(410);
});

// Test 2: POST proves CSRF middleware still blocks (positive security test)
test('POST /legacy-route/ is blocked by CSRF (403)', async ({ request }) => {
  const r = await request.post(`${API_URL}/legacy-route/`, { data: {} });
  expect(r.status()).toBe(403);
});
```

**Why this works:**
- GET and POST hit the same view function → if GET returns 410, POST would too if it bypassed CSRF
- CSRF middleware is universal across unsafe methods (POST/PUT/PATCH/DELETE) → if POST returns 403, all unsafe methods are protected
- Tests cover both contracts: deprecation (410) AND CSRF protection (403)

## Decision
Adopt split-test pattern. Never assert `expect(response.status()).toBe(410)` on POST in Playwright E2E without first bypassing CSRF (test client override, manual token fetch) — the bypass itself proves nothing about prod security.

## Tradeoffs
- Pro: pure HTTP test, no fixture setup, no auth
- Pro: 2 fast tests instead of 1 fragile one
- Pro: 410 contract is provable from GET alone (same view, same handler)
- Con: 2 tests instead of 1 (minor noise in test count)
- Con: doesn't cover the case where a view method-overrides CSRF (e.g., `@csrf_exempt` on POST only) — rare, manual code review covers it

## Consequences
- Use this pattern for ALL 410-on-legacy-route tests in E2E suites
- BE unit tests with Django's test client (`self.client.post()`) bypass CSRF by default → can assert 410 there for stronger coverage of the view itself
- E2E tests = security + behavior smoke; unit tests = full logic

## Related
- `smartenplus-frontend/e2e/checkout/payment-deep-review.spec.ts` lines 41-78 — H2 + M10 tests using this pattern (commit `8430805`)
- `smartenplus-backend/payments/tests/test_deep_review_fixes.py` — Django test client tests that DO assert 410 on POST (CSRF bypassed in test client)
- `smartenplus-backend/orders/urls.py:18` — actual 410 stub: `lambda r: HttpResponse("Deprecated", status=410)`
