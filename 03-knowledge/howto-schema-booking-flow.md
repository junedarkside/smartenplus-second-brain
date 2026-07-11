---
name: howto-schema-booking-flow
description: HowTo JSON-LD pattern for transport booking steps — highest-leverage new AEO signal for SmartEnPlus homepage; feeds AI "how do I book..." answers
metadata:
  type: reference
---

`HowTo` schema is the highest-leverage new AEO signal available for a booking site. It directly feeds AI answer engine responses to "how do I book a ferry/bus/van in Thailand?" queries.

**Pattern for SmartEnPlus homepage:**

```json
{
  "@context": "https://schema.org",
  "@type": "HowTo",
  "name": "How to Book Thailand Transport Tickets on SmartEnPlus",
  "description": "Book bus, ferry, van and train tickets in Thailand in 4 steps.",
  "totalTime": "PT5M",
  "step": [
    {
      "@type": "HowToStep",
      "position": 1,
      "name": "Search your route",
      "text": "Enter your departure and destination locations and travel date.",
      "url": "https://www.smartenplus.co.th"
    },
    {
      "@type": "HowToStep",
      "position": 2,
      "name": "Compare options",
      "text": "Browse available buses, ferries, vans, and taxis. Compare prices, schedules, and operators.",
      "url": "https://www.smartenplus.co.th"
    },
    {
      "@type": "HowToStep",
      "position": 3,
      "name": "Book and pay securely",
      "text": "Select your ticket and pay online with credit card or bank transfer. Instant confirmation.",
      "url": "https://www.smartenplus.co.th/checkout"
    },
    {
      "@type": "HowToStep",
      "position": 4,
      "name": "Receive your e-ticket",
      "text": "Your e-ticket is emailed instantly. Show it on your phone at departure.",
      "url": "https://www.smartenplus.co.th"
    }
  ]
}
```

**Add to:** `pages/homepagev2.js` as a 7th JSON-LD block alongside the existing 6.

**Priority:** P2 AEO-1. Aligns with llms.txt "How it works" section. [[llmstxt-spec-linked-entries]]
