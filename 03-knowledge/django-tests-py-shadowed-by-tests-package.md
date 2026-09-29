---
name: django-tests-py-shadowed-by-tests-package
description: An app with both tests.py and a tests/ package crashes unittest discovery ("'tests' module incorrectly imported") and the tests.py never runs. Found in operators/ and orders/ 2026-09-29.
type: knowledge-atom
date: 2026-09-29
parent: backend-architecture
---

# `tests.py` Shadowed by a `tests/` Package

## Summary
When a Django app contains both `tests.py` and a `tests/` directory with `__init__.py`, Python imports the package as `app.tests`. Test discovery then raises:
```
ImportError: 'tests' module incorrectly imported from '<app>/tests'. Expected '<app>'.
```
`manage.py test` (no label) and `manage.py test <app>` both abort; the `tests.py` file has never actually run.

## Why It Matters
In SmartEnPlus this hid the whole backend suite: nobody could run a full test pass, and `orders/tests.py` (Omise `verify_omise_event` webhook tests) had silently not run at all. After the fix the suite discovered 1098 tests and exposed 6 failures + 87 errors that had been invisible.

## Fix
`git mv app/tests.py app/tests/test_<topic>.py` — no code change. Scan for others:
```bash
find . -path ./venv -prune -o -name tests.py -print | while read f; do [ -d "$(dirname $f)/tests" ] && echo "$f"; done
```
Rule: never add `tests.py` to an app that has a `tests/` package.

## Related
- [[django-tests-share-live-redis-cache]]
