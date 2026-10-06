# Claude Agent Roster — SmartEnPlus

Last audited: 2026-10-06

## Global Agents (`~/.claude/agents/`)

All `model: sonnet`. Apply to all 3 repos.

| Agent | Domain |
|-------|--------|
| `django-python-expert` | Django 4.2 + DRF + Celery + Django Channels — SmartEnPlus payment rules |
| `payment-security-specialist` | Omise/GatewayCharge lifecycle, idempotency, QR/redirect, 409 mapping |
| `smartenplus-swe` | Cross-repo SWE generalist — 3-repo routing guide, payment gotchas, branch policy |
| `nextjs-fullstack-architect` | Next.js — Pages Router default (caveat added; no App Router suggestions) |
| `backend-architect` | Generic Node.js/Python/Go APIs |
| `react-ui-engineer` | React components |
| `senior-frontend-developer` | React/Vue/Angular |
| `ui-component-engineer` | React UI |
| `api-architect` / `api-designer` / `api-documenter` | REST/GraphQL |
| `code-reviewer` | Code quality |
| `code-refactoring-specialist` | Refactoring |
| `debug-specialist` | Debugging |
| `ux-research-specialist` | UX research |
| `design-review` | Visual/a11y (uses Playwright MCP) |
| `postgres-pro` / `postgresql-expert` | PostgreSQL |
| `websocket-architect` | WS/Django Channels |
| `multi-agent-orchestrator` | Team coordination |
| `business-analyst-expert` | BA/requirements |
| `context-manager` | State/memory (tools: Read, Write only — redis/ES not available) |

## FE Project Agents (`smartenplus-frontend/.claude/agents/`)

| Agent | Domain |
|-------|--------|
| `nextjs-fullstack-architect` | Pages Router + SmartEnPlus ISR/Redux/MUI patterns |
| `react-specialist` | React/SmartEnPlus specific |
| `devops-engineer` | CI/CD + Docker |
| `seo-specialist` | SEO |
| `seo-homepage-auditor` | SEO orchestrator (3-phase audit + /compact hint at Phase 2→3) |
| `trip-detail-uxui-auditor` | UX/UI orchestrator (3-phase audit + /compact hint at Phase 2→3) |

## BE Project Agents (`smartenplus-backend/.claude/agents/`)

| Agent | Domain |
|-------|--------|
| `django-backend` | Project-scoped: app structure, payment rules, Celery, cross-repo awareness |
| `django-expert-developer` | Generic Django (existed pre-audit) |

## Admin Dashboard Project Agents (`admin-dashboard/.claude/agents/`)

| Agent | Domain |
|-------|--------|
| `debugger` | Django/Next.js debugging |
| `frontend-developer` | React/MUI components |
| `nextjs-developer` | Next.js Pages Router (already correct) |

## Skills

| Skill | Model | Why |
|-------|-------|-----|
| `/wrapup` | `haiku` | Mechanical: git state + file writes, no judgment |
| `herdr` | `sonnet` | Terminal coordination, JSON parsing, agent state machines |
