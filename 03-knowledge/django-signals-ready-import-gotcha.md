# Django Signals — `AppConfig.ready()` Import Gotcha

**Type:** BUG PATTERN · **Found:** CS-Centralization audit 2026-06-29

## Problem

`signals.py` exists but handlers **never fire** — silent dead code.

Root cause: Django only imports signal handlers when `AppConfig.ready()` imports them. If `ready()` is absent, the module is never loaded and `@receiver` decorators never execute.

## Pattern (broken)

```python
# tickets/apps.py — BROKEN
class TicketsConfig(AppConfig):
    name = 'tickets'
    # NO ready() → signals.py never imported → all handlers dead
```

## Pattern (correct)

```python
# tickets/apps.py — CORRECT (mirrors products/operators/bookings/dialogue/orders)
class TicketsConfig(AppConfig):
    name = 'tickets'

    def ready(self):
        from . import signals  # noqa: F401
```

## Detection

```bash
# Find apps that have signals.py but no ready():
for app in tickets payments orders; do
    echo "=== $app ===" && grep -n "ready" $app/apps.py || echo "NO ready()"
done
```

## Why it's hard to catch

- No error raised — signals module exists, it just isn't imported.
- Tests that call handlers directly (bypassing the signal system) pass green.
- Only fails silently in a running server.

## Case

`tickets/apps.py:1-7` — missing `ready()`. All `tickets/signals.py` handlers (email on resolve/reject/closed_no_action, manifest push) are dead in production. Fix = 2 lines.

**Related:** [[cs-centralization-audit-2026-06-29]] Tier-1 #3
