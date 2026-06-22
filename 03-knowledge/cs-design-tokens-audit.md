---
name: cs-design-tokens-audit
description: Design-token + WCAG audit extracted from the CS design concept — 4 status/gray tokens FAIL AA as text (platform-wide, not CS-only), 15 token gaps (G-01..15) to add to designSystem.js, full design-system reuse map for the 3 CS surfaces.
metadata:
  type: knowledge
  status: active
  date: 2026-06-21
  parent: cs-centralization-design-concept
---

# CS Design Tokens + WCAG Audit

> Extracted 2026-06-22 from [[cs-centralization-design-concept]] (was over the 200-line vault cap). The
> token gaps + reuse map + WCAG findings live here so the design concept stays focused on flows/states.
> **G-05/06/07 are NOT CS-only** — they fix a platform-wide WCAG failure in `helpers/designSystem.js`.

## ⚠️ Blocking Finding — Design-System Token WCAG Failures

A11y audit measured 3 status tokens + gray400 FAIL WCAG AA as text on white. **Affects the whole feature**
and any other feature using these for text.

| Token | Ratio on white | Verdict | Rule applied here |
|---|---|---|---|
| `status.success` #10B981 | 2.54:1 | FAIL | icon/dot only, never text |
| `status.warning` #F59E0B | 2.15:1 | FAIL | icon only |
| `status.error` #EF4444 | 3.76:1 | FAIL (normal weight) | icon + badge-dot only; never error text |
| `neutral.gray400` #9CA3AF | 2.54:1 | FAIL | replaced by gray500 (4.83:1 floor) everywhere |

**Safe pairs used throughout:** white-on-`brand.primary` (6.84:1) · `gray900`-on-`gray100` (16.12:1) ·
`primaryDark`-on-`primaryLight` (8.93:1) · `brand.secondary` #2563eb on white (5.17:1) · `gray700` on white
(8.59:1, used for ALL error/success TEXT).

→ Proposed companion text-tokens `status.successText`/`errorText`/`warningText` (G-05..07 below). **File a
design-token audit issue against `helpers/designSystem.js` regardless of CS feature** — these failures pre-exist.

## Design-System Reuse Map

| Element | Token/preset | Source |
|---|---|---|
| FAB / header / outgoing-tint bg | `COLORS.brand.primary` / `primaryDark` / `primaryLight` | designSystem.js |
| Incoming bubble | `COLORS.neutral.gray100` + `gray900` | designSystem.js |
| Timestamps / secondary text | `COLORS.neutral.gray500` (4.83:1 floor) | designSystem.js |
| Error/success TEXT | `COLORS.neutral.gray700` (8.59:1) | designSystem.js |
| Inputs | `INPUT_CONFIG.base/focus/error/borderRadius` | designSystem.js |
| Buttons | `BUTTON_CONFIG.primary/secondary` | designSystem.js |
| Badges/chips | `COLORS.badge.primary/neutral` + `BORDER_RADIUS.badge` | designSystem.js |
| Tap targets | `TOUCH_TARGET.minHeight` 44px | designSystem.js |
| Mobile drawer | `ProfileBottomSheet.js` shell | frontend |
| Desktop dialog | `Modal.js` shell | frontend |
| OTP/auth screens | `login.js` layout + `SuccessState` | frontend |
| CS Dashboard | admin `lightTheme.js` palette + MUI Chip/Avatar/TextField | admin |
| Toast | `react-toastify` ^9.1.1 | frontend package.json |
| Lazy mount | `dynamic(ssr:false)` `_app.js:22` | frontend |

## Token Gaps (15 — propose adding to designSystem.js)

| ID | Token | Value | Why |
|---|---|---|---|
| G-01/02 | `BORDER_RADIUS.chatBubbleOutgoing/Incoming` | `12 12 2 12` / `12 12 12 2` | asymmetric tail not coverable |
| G-03 | `BORDER_RADIUS.chatFab` | `50%` | no circle token |
| G-04 | `BORDER_RADIUS.chatDrawerTop` | `16 16 0 0` | codify ProfileBottomSheet value |
| **G-05** | `COLORS.status.successText` | `#065F46` (9.73:1) | success TEXT (status.success fails) |
| **G-06** | `COLORS.status.errorText` | `#991B1B` (6.30:1) | error TEXT (status.error fails) |
| **G-07** | `COLORS.status.warningText` | `#92400E` (9.73:1) | warning TEXT (status.warning fails) |
| G-08/09 | `COLORS.cs.pendingChipBg/Text` | `#FEF3C7`/`#92400E` | pending chip (no amber chip token) |
| G-10 | `Z_INDEX.chatWidget` | `75` | above `notification`(70)/snackbar conflict |
| G-11..14 | `DIMENSIONS.chatFabSize/PanelWidth/PanelHeight/AgentAvatarSize` | 56/380/560/28px | no chat geometry tokens |
| G-15 | `COLORS.cs.listPaneSelectedBg` | `#E3E8F0` | admin-only, document for CS list |

**G-05/06/07 are not just chat gaps — they fix a platform-wide WCAG failure.** This is bucket-C open
work in [[cs-centralization-review-2026-06-22]] (Design owner sign-off).

## Related
- [[cs-centralization-design-concept]] — parent (surface flows, states, microcopy)
- [[design-systems]] — token source (`helpers/designSystem.js`)
- [[cs-centralization-review-2026-06-22]] — integrity review (lists this as the over-cap split)
