# Engineering

## Summary
Software engineering practices, standards, and principles. Long-term area covering all projects.

## Core Principles
- Simplicity over cleverness
- Reuse before create
- Max 200 lines per component/file
- Max 30 lines per function, max 3 params
- Guard clauses at top of functions
- Named exports, no circular imports
- Comment WHY, never WHAT

## State Management
- Props down, events up
- Max 3 prop levels → move to global state
- `useState` for UI-only
- Global state for cross-component
- Derive inline or `useMemo` — never in `useEffect`

## API Patterns
- RTK Query for all API calls
- Transform in RTK, not components
- `skip` for conditional queries
- Never create endpoint without checking existing

## Error Handling
- Return `null` + log from utilities
- Formik + Yup at system boundaries
- Never throw from helpers
- Validate at boundaries, trust internal code

## Security
- No secrets in commits
- `NEXT_PUBLIC_` only for truly public values
- Formik + Yup validation at boundaries
- OWASP top 10 awareness

## Related
- [[nextjs-patterns]]
- [[payment-integration]]
- [[design-systems]]
