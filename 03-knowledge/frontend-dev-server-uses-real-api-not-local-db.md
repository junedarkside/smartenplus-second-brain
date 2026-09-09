# Frontend dev server/build hits real backend API, not local DB

## Summary
`npm run dev` and `npm run build` in `smartenplus-frontend` fetch product data from the live backend API, not a local Django DB. A prior "local dev DB has no seed data, activity/trip detail pages 404" claim (master-state #393) was stale — likely caused by a dead/stuck dev server process from an earlier session, not an actual data gap.

## Context
Session #393 recorded activity detail and trip detail pages 404ing locally ("tour not found") and flagged it as a blocking local-env data gap for any future visual QA. Session #395 (activity detail cleanup work) needed to verify fixes in a real browser and hit the same claim — but before accepting it, ran `npm run build` and found real product slugs (`smart-en-plus-co-ltdeddd-day-tour-121`, etc.) prerendering successfully with real data ("Pre-building 12 day trip pages for static generation" in build log). Restarted `npm run dev` clean (killed a stray process on port 3000 first) and the same slugs returned 200 with full page render, zero console errors.

## Details
- `NEXT_PUBLIC_API_URL` (or equivalent env var) points at a real backend, not `localhost` Django — confirmed by build output showing real contract data, not synthetic/seed data.
- The 404s in #393 were reproducible at the time but the root cause was never confirmed as "no seed data" — that was an assumption, not a verified diagnosis. A stray/stale dev server process (multiple `npm run dev` instances left running across a session, common when background-launching for repeated checks) is a more likely explanation, and matches what session #395 found: killing port 3000 and restarting cleanly fixed it immediately.
- Practical implication: before citing "local DB has no seed data" as a blocker again, first try `lsof -ti:3000 | xargs kill -9` and a clean `npm run dev` restart, and/or check `npm run build` output for real prerendered slugs to test against.

## Consequences
Don't propagate "local dev DB has no seed data" as an accepted blocker without re-verifying — it blocked live browser QA across at least 2 sessions unnecessarily. Live verification is available and should be the default expectation for FE work on this repo, not an exception.

## Related
- [[activities-day-tour-page-review]] — original context where this blocker was first hit and cited as unverified
