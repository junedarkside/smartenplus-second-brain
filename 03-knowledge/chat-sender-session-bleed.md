# Chat sender session bleed

## Summary
When a customer-facing widget and a staff/admin tool share one backend "send message" endpoint, deriving `sender` from the HTTP session misattributes messages whenever a staff session reaches the customer surface.

## Context
SmartEnPlus CS chat: customer widget (`smartenplus-frontend`) + admin inbox (`admin-dashboard`) both `POST /api/cs/messages/send/`. BE `MessageCreateView` derived `sender = 'cs' if is_staff else 'customer'` from `request.user`.

## Problem
A staff/admin account logged into the customer site (`:3000`) and using the widget sends its staff Bearer token → BE marks `sender='cs'` → customer's own messages render as "Support" on the wrong side. Prod customers (guest or non-staff) unaffected; break = staff-on-customer-site (real edge case — staff who book trips). FE NextAuth session exposed no role, so the widget couldn't self-detect staff.

## Decision
**Ownership-gated client hint.** Widget sends `sender:'customer'` (it is unambiguously the customer channel). BE honors the hint ONLY when the caller proves customer ownership of the conversation:
- authenticated user is the conv owner (`conv.user_id == request.user.id`), OR
- valid guest token (`X-CS-Guest-Token` resolves to the conv).

Otherwise → 403. Admin inbox sends no hint → unchanged session-derived `'cs'` path.

## Tradeoffs
- **Secure:** staff can't spoof a customer voice (no guest token, don't own customer convs → 403). "Never trust client" preserved via ownership proof.
- **Contained:** BE view + widget one field; no auth/role-token change (rejected alternative: expose role in NextAuth session — bigger, touches token claims + callbacks).
- **Edge:** a staff user who owns a conv (their own customer booking) sending `sender:'customer'` is honored — harmless (their own conv, acting as customer).

## Consequences
- Pattern reusable for any dual-surface (customer + staff) shared endpoint where role must be asserted client-side: **client hints role, server re-proves ownership before honoring.**
- Only affects NEW sends; old mis-attributed rows stay (unreliable to reclassify retroactively).

## Related
- BE `cs/views.py` `MessageCreateView` · FE `components/chat/ChatPanel.js`
- [[cs-centralization-audit-2026-06-29]] · master-state Section 2 (#193 update)
