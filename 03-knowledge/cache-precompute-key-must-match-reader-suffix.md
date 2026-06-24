# cache-precompute-key-must-match-reader-suffix

## Summary
A precompute writer and a runtime reader of the same cache must build IDENTICAL keys — including optional-component suffixes. A reader appending `:none` for the no-date case while the writer omits it → zero cache hits system-wide.

## Why It Matters
This single mismatch made every recommendation call hit the DB from launch, draining CPU credits on a 1-vCPU instance (prod incident). Cache "worked" (keys written, reads coded) but never matched. Hardest class of bug: writer and reader each look correct in isolation.

## Detail
```
WRITER (products/tasks.py):   recommendations:{contract}:{rec_type}:{limit}
READER (products/services.py): recommendations:{contract}:{rec_type}:{limit}:{rate_date or 'none'}
```
For the common no-date path the reader appends `:none`; the writer never does → keys never equal.

**Rule:** centralize key construction in ONE function used by both writer and reader. Never build cache keys inline in two places. Any optional component (`rate_date`, currency, version) must be applied identically on both sides, including the "absent" representation (`:none`).

## Constraints / Gotchas
- Date-specific requests (`rate_date='2026-06-20'`) still miss if the precompute only writes the `:none` key — acceptable if date-specific is an edge case, but document it.
- Verifying: `redis-cli --scan --pattern "recommendations:*:hybrid:8:none" | wc -l` should be >0 after a manual trigger.

## Related
- [[precompute-popular-contracts-fix-plan]] — BUG 3 source
- [[precompute-popular-contracts-audit]] — original audit
- [[recommendation-engine-completion-roadmap]] — broader engine
