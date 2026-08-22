---
name: tailscale-funnel-local-dev-public-exposure
description: Local Django dev server logs showing prod-looking bot-scan 404 noise (keyfile.json, wp-login.php etc) can mean Tailscale Funnel is publicly exposing localhost, not a prod issue. Check `tailscale funnel status` before assuming prod misconfiguration.
metadata:
  type: knowledge
  status: active
  date: 2026-08-22
  parent: bot-scan-noise-investigation-2026-08-22
---

# Tailscale Funnel — Local Dev Public Exposure Gotcha

## Summary
Bot-scan 404 noise (`/keyfile.json`, `/firebase-adminsdk.json`, `/wp-login.php`, `/api/v1/auto_login`) in Django logs looks like prod attack surface, but on a local dev box it can mean Tailscale Funnel is publicly proxying `localhost` — not a Django/prod config gap.

## Why It Matters
Tailscale has two modes that look similar but aren't:
- `tailscale serve` — shares a local port within your own tailnet only. Private, not internet-reachable.
- `tailscale funnel` — shares a local port on the public internet via a real `*.ts.net` TLS cert. Internet-reachable, indexed by certificate-transparency logs, scanned by bots within hours of cert issuance — same as any public domain.

Easy to enable Funnel for one-off use (e.g. payment-webhook testing — Omise/Stripe need a public callback URL) and forget it's on. Every subsequent bot 404 in local logs then looks like a prod security incident when it's actually expected noise from an intentionally-public tunnel.

## Detail
**Diagnostic:**
```bash
tailscale funnel status
tailscale serve status
```
If `Funnel on` shows a `*.ts.net` URL proxying to a local port (e.g. `127.0.0.1:8000`), that's the exposure source — not the app.

**Effect on the app itself:** none. Django/any backend still correctly 404s unmatched routes — no route match, no view executes, no data touch. The "vulnerability" is the tunnel being public, not the app being insecure.

**Resolution:** `tailscale funnel off` when done with whatever needed the public URL (webhook testing, demo, etc). Don't leave it running as a background default — it's easy to forget and it silently becomes a persistent public attack surface for the machine.

## Related
[[django-config-validate-at-call-time-not-startup]]
