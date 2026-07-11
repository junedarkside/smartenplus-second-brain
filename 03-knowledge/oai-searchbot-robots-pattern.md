---
name: oai-searchbot-robots-pattern
description: OAI-SearchBot is the SearchGPT citation crawler (distinct from GPTBot training); must be explicitly allowed in robots.txt for ChatGPT Search citation eligibility
metadata:
  type: reference
---

Two distinct OpenAI crawlers exist with different purposes:

| Bot | Purpose | robots.txt needed? |
|-----|---------|-------------------|
| `GPTBot` | Training data collection | ✅ Already in robots.txt |
| `ChatGPT-User` | Browsing plugin | ✅ Already in robots.txt |
| `OAI-SearchBot` | **SearchGPT / ChatGPT Search citations** | ❌ **Missing as of r14** |

`OAI-SearchBot` is the crawler behind ChatGPT Search (SearchGPT). If absent from robots.txt, SmartEnPlus is not eligible to be cited in ChatGPT Search answers even with correct `llms.txt` and entity schema.

**Fix:**
```
# OAI-SearchBot
User-agent: OAI-SearchBot
Allow: /
```

Add to `public/robots.txt` adjacent to other OpenAI bot entries.

**Status:** Missing as of r14 (2026-07-11). In r13 plan but not deployed. GEO-2 P2. [[faqpage-rich-results-deprecated-2023]]
