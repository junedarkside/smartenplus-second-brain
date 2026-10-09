---
name: cpu-credit-exhaustion-burstable-ec2
description: Why a burstable EC2 box (t2/t3 micro) looks fine for ~1.5 days after a load increase, then turns slow all at once when CPU credits hit 0 - drain math and what to alarm on.
metadata:
  type: knowledge
  status: active
  date: 2026-10-09
  source: user's CloudWatch screenshot (2026-10-09 17:25) + AWS burstable-instance model; instance type not confirmed
---

# CPU Credit Exhaustion on a Burstable EC2 Box

## Summary
Burstable instances (t2/t3/t4g) run on a credit balance. Use less CPU than the earn rate and credits pile up to a cap; use more and the balance drains. At balance 0 (Standard mode) the CPU is held to the baseline (~10% of a vCPU on a micro), so every container on the box slows at once. A load increase can hide for a day or more because the balance absorbs it.

## Numbers (SmartEnPlus prod, 2026-10-07 release)
- Cap 144 credits, earn about 6 credits/hour (about 0.5 per 5 min): matches t2.micro or t3.nano class.
- Before release: CPU ~5%, balance full. After: CPU ~12%, usage ~0.8 credits per 5 min (~9.6/h).
- Net loss ~3.6/h, so 144 / 3.6 = ~40 h. Graph: balance starts falling 10-07 night, hits 0 on 10-09.
- 1 credit = 1 vCPU-minute. Load of x% of one vCPU costs 0.6 * x credits/hour.

## Recovery
Only load below the earn rate rebuilds the balance. At ~5% load: +3/h, so ~7 h to 20 credits and ~2 days to full. At ~10% or more it never recovers.

## Rules
- Alarm on `CPUCreditBalance` (< 30), not on CPU %. CPU % stays flat at the baseline once throttled.
- Fast relief is a user/ops call: Unlimited credits (surplus billed), upsize, or cut load. Standard-vs-Unlimited mode and the exact type must be checked in the console.
- After a release, compare the credit balance slope for 2 days, not only CPU in the first hour.

## Related
[[prod-capacity-celery-audit]] · [[ad-first-page-timeout-investigation]] · [[destination-trips-slow-root-cause]]
