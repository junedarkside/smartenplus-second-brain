---
name: llmstxt-spec-linked-entries
description: llmstxt.org spec requires markdown hyperlinks in section bodies, not prose bullets — current SmartEnPlus llms.txt uses prose only
metadata:
  type: reference
---

The llmstxt.org specification (2025) requires section bodies to contain **markdown hyperlinks** in the form:

```markdown
## Section Title

- [Page Name](https://www.example.com/page): Short description of what this page covers
- [Another Page](https://www.example.com/other): Description
```

**Current SmartEnPlus state (r14):** `public/llms.txt` uses well-structured prose bullets but **no URLs**. Content and entity disambiguation are strong; format non-compliant.

**Fix:** Add linked entries to key sections:
- Activities section → `[Activities & Tours](https://www.smartenplus.co.th/activities)`
- Destinations section → `[Destinations](https://www.smartenplus.co.th/destinations)`
- Reference section → `[Transport Reference](https://www.smartenplus.co.th/ref)`
- Route booking section → `[Book Trips](https://www.smartenplus.co.th/trips)`

**Priority:** P3 — prose content is still consumed by LLMs; linked format is an enhancement. [[oai-searchbot-robots-pattern]]
