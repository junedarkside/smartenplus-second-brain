---
name: customer-os-thesis-review
description: 5-agent strategic review of the Smarten Customer OS thesis (3 specialists + leader + grill)
metadata:
  type: thesis-review
  status: under-review
  source: Smarten Customer OS Thesis (2026 phase roadmap)
  date: 2026-06-20
  scope: all 5 phases, strategic
---

# Smarten Customer OS Thesis — Review

## Summary

Strategic review of the **Smarten Customer OS Thesis**: a 5-phase roadmap to centralize the customer relationship that OTAs (Klook/12Go/Bookaway) currently own — via Customer DB, Account/My-Trip, omnichannel messaging, smart CS, and an AI Copilot. Demand-side complement to the existing supply-side [[business-development-unified-travel-wellness-thesis]].

## Context — why this review

Customers arrive from OTAs and remember the OTA brand, not Smarten. Conversations fragment across systems; CS hunts across tools; repeat-business is hard. Thesis proposes a centralized Customer OS to convert OTA travelers into direct brand users. This review validates strategic fit, technical feasibility, sequencing, and surfaces adversarial risk before any build commitment.

## Process

| Round | Agent | Output |
|-------|-------|--------|
| 1 | r1-strategy | [[r1-strategy]] — validity, OTA-data-ownership, moat |
| 1 | r1-tech-feasibility | [[r1-tech-feasibility]] — greenfield reality, build cost, realism |
| 1 | r1-product | [[r1-product]] — sequencing, ROI, dependencies, MVP |
| 2 | r3-leader | [[r3-leader-synthesis]] — skeptic pass + ranking + verdict |
| 3 | grill | [[grill-audit]] — contradictions, fuzzy terms, edge cases |

Verdict + re-evaluation triggers → [[smarten-customer-os-thesis]] (decision doc).

## Backend reality (pre-scanned)

- Customer / Conversation / Message / ChatSession / SupportTicket models: **absent → greenfield**
- Channels / Celery / Redis / Daphne in `Smartenplus/settings.py`: **absent → net-new realtime infra**
- Telegram / WhatsApp / LINE integration: **absent → all greenfield**
- Existing apps to check for reuse: `accounts/`, `bookings/`, `orders/`, `tickets/`, `dialogue/`, `operators/`, `journeys/`

## Status

**Under review** — pending Phase 1 build decision. Re-evaluation triggers documented in the decision doc.

## Related

- [[smarten-customer-os-thesis]] — decision doc
- [[business-development-unified-travel-wellness-thesis]] — supply-side thesis (wellness + transport)
- [[business-development-thesis-2026-2029]] — overall strategic position
- [[business]] — B2B(90%)+B2C(10%) strategy, "Stippl for SEA" vision
- [[accounts]] · [[tickets]]
