# Design System Audit — 2026-06-13

## Summary

SmartEnPlus frontend has 288-line design token system at `helpers/designSystem.js` and 59 shared UI components, but suffers from inconsistent adoption: 290 hardcoded hex colors in components/pages (745 project-wide), 252 inline `style={{}}` attributes in components/pages, and mixed styling approaches (Tailwind + MUI + CSS Modules + inline). Design tokens exist for colors, typography scale, spacing, border radius, and elevation, but lack opacity scale, z-index system, and transition tokens. No component documentation or Storybook exists. Typography tokens lack line-height and letter-spacing. Globals.css has 22 hardcoded colors not using design tokens. 47 CSS module files in components/ (56 project-wide, up to 410 lines) coexist with Tailwind.

## Current State

### Infrastructure
- **designSystem.js**: 288 lines, centralized design tokens
- **tailwind.config.js**: 87 lines, extended with brand colors, spacing, border radius
- **theme.js**: 24 lines, MUI theme (palette + breakpoints)
- **globals.css**: 773 lines, contains hardcoded colors and utility classes
- **UI Components**: 59 shared components in `components/UI/`
- **CSS Modules**: 47 files in components/ (56 project-wide, 0-410 lines range)

### Existing Token Categories
- **COLORS**: Brand (primary, secondary), Status (success, warning, error, info), Badge (neutral, difficulty levels), Neutral (gray50-900)
- **TYPOGRAPHY_SCALE**: h1-h6, body, small, caption (responsive classes)
- **FONT_WEIGHTS**: normal, medium, semibold, bold
- **SPACING**: Base 4px, scale (xs-2xl), responsive patterns
- **BORDER_RADIUS**: container (6px), badge (4px), input (8px), button (6px), imageCard (12px)
- **ELEVATION_TOKENS**: none, sm, md, lg, xl (box-shadow scale)
- **BREAKPOINTS**: xs, sm, md, lg, xl, 2xl (Tailwind defaults)
- **COMPONENT_CONFIGS**: BREADCRUMB, CARD_CONFIG, BUTTON_CONFIG, INPUT_CONFIG, HOMEPAGE_SECTION

## Token Coverage Matrix

| Dimension | Status | Tokens Exist | Violations Found | Gap Severity |
|-----------|--------|--------------|-----------------|--------------|
| **Colors** | ✅ Partial | Yes (brand, status, neutral, badge) | 290 in components/pages (745 project-wide) | Medium |
| **Typography Scale** | ✅ Partial | Yes (h1-h6, body, small) | 30+ inline fontSize declarations | Low |
| **Typography Details** | ❌ Missing | No (line-height, letter-spacing) | Scattered in components | Medium |
| **Spacing (gap)** | ✅ Yes | Yes (xs-2xl scale) | Minimal violations | Low |
| **Padding/Margin** | ❌ Missing | No scale defined | 20+ inline padding/margin in style props | Medium |
| **Sizing (width/height)** | ❌ Missing | No scale | Hardcoded values in components | Medium |
| **Border Radius** | ✅ Yes | Yes (5 variants) | Consistent usage | Low |
| **Elevation/Shadows** | ✅ Yes | Yes (none/sm/md/lg/xl) | Some hardcoded rgba() shadows | Low |
| **Opacity** | ❌ Missing | No scale | ~20 opacity values hardcoded (estimated) | Medium |
| **Z-index** | ❌ Missing | No scale | ~20 z-index values (z-10 to z-50, estimated) | Medium |
| **Transitions/Animation** | ❌ Missing | No scale | ~15 inline transition declarations (estimated) | Medium |
| **Breakpoints** | ✅ Yes | Yes (Tailwind defaults) | MUI sm=600 vs Tailwind sm=640 mismatch | Low |

## Component Violation Report

| Category | Count | Severity | Top 5 Files (violations) |
|----------|-------|----------|---------------------------|
| **Hardcoded Colors** | 290 (745 project-wide) | High | pdfStyles.js (33), ProfileMenu.js (23), ServiceCategoryBadge.js (17), SUV icon (15), ProfessionalOrderHeader.js (12) |
| **Inline Styles** | 252 | High | ProfileMenu.js (26), OrderDetail.js (18), rate-review page (15), layout.js (14), ProductSearchForm2.js (9) |
| **Inline fontSize** | 30+ | Medium | ProfessionalOrderHeader.js (7), ProfileHeader.js (9), ServiceCategoryBadge.js (4), CarouselArrowButtons.js (4) |
| **Inline Padding/Margin** | 20+ | Medium | ProfileMenu.js (4) - all in style props |
| **Z-index Usage** | 20+ | Medium | ScrollTop.js (zIndex: 500), BackDrop.js (theme.zIndex.drawer + 1), various z-10 to z-50 classes |
| **Opacity Values** | 20+ | Medium | LocationGridComponent (bg-opacity-40), NavBar (opacity-0 hover:opacity-100), OrderDetail.js (opacity: 0.4) |
| **!important Usage** | 20+ | Low | globals.css (10), print.css (6), loading-animations.css (1) |
| **CSS Module Files** | 47 (56 project-wide) | Low | NetworkStatus.module.css (410 lines), trips/trip-item.module.css (362 lines), OfflineTripDetailWrapper.module.css (410 lines) |
| **Transition Inline** | 15+ | Low | CarouselArrowButtons.js (2), DynamicCheckboxItem.js (1), ProfileImage.js (2) |
| **Background Hardcode** | 15+ | Medium | backgroundColor with rgba() in 10+ files, linear-gradient in FeaturedImageHeader |
| **Box Shadow Inline** | 10+ | Low | ProfessionalOrderHeader.js (boxShadow: '0 4px 12px rgba(0,0,0,0.12)'), ProfileHeader.js (2 instances) |

## Page Layout Patterns

| Page | Container Width | Padding | Grid System | Responsive |
|------|-----------------|---------|-------------|------------|
| **Homepage** | max-w-[1200px] | mx-2 md:mx-3 xl:mx-0 | Various (depends on section) | Yes |
| **Locations [slug]** | No explicit max-width | Uses FeaturedImageHeader | GridComponent3 | Yes |
| **Checkout** | No max-width on main | FormCard containers | 1-column mobile, 2-column desktop | Yes (sidebar sticky) |
| **Trip Detail** | max-w-[1200px] | px-4 xl:px-0 | Multiple sections | Yes |
| **Blog** | lg:w-full variant | Blog-specific padding | Grid for cards | Yes |
| **Rate/Review** | No explicit max-width | Standard page padding | Grid layout | Yes |

## UX Pattern Inventory

| Pattern | Implementation | Consistent? | Issues |
|---------|----------------|-------------|--------|
| **Card Containers** | ContentCard (missing from many pages) | No | Many pages lack Section/ContentCard wrapper pattern |
| **Buttons** | Mixed MUI Button + custom | No | Primary/Secondary tokens defined but not consistently used |
| **Form Inputs** | INPUT_CONFIG defined | Partial | Some components use MUI TextField instead of tokens |
| **Badges/Chips** | BadgeChip with config | Partial | Multiple badge implementations (BadgeChip, ServiceCategoryBadge) |
| **Carousels** | Embla-based | Yes | Consistent carousel-standard applied |
| **Modals** | MUI Dialog + custom Modal | No | Two different modal patterns coexist |
| **Sidebars** | Sticky sidebar pattern | Partial | Width varies (240px vs responsive) |
| **Breadcrumbs** | StandardBreadcrumb | Yes | Consistent breadcrumb implementation |
| **Loading States** | Skeleton screens | Partial | Not all pages have loading states |
| **Empty States** | EmptyState component | Partial | Inconsistent error state handling |

## Accessibility Assessment

| WCAG Criterion | Status | Violations | Files |
|----------------|--------|-------------|-------|
| **Touch Targets (2.5.5)** | Partial | 44px min not enforced | Icon buttons vary in size |
| **Color Contrast** | Partial | Some low-contrast text | Gray text on light backgrounds |
| **Focus Indicators** | Partial | Inconsistent focus rings | MUI components have focus, custom don't |
| **ARIA Labels** | Partial | Missing on some interactive elements | Icon buttons, carousels |
| **Keyboard Navigation** | Partial | Tab order issues | Some custom components not keyboard-accessible |
| **Form Labels** | Good | Labels present | Form fields generally labeled |
| **Error Messages** | Good | Visible error messages | Form validation errors displayed |

## Dark Mode Readiness

### Architecture Assessment
- **Current State**: No dark mode support
- **Globals.css**: Has commented-out dark mode media query (lines 81-89), but not implemented
- **Design Tokens**: No color palette for dark mode
- **Component Support**: Components not designed for dark mode
- **Images**: No dark mode image variants

### What Needs to Change
1. Add dark mode color tokens to `designSystem.js` (COLORS.darkMode)
2. Implement dark mode toggle in context/provider
3. Update all color-consuming components to use theme-aware colors
4. Test all components in both modes
5. Add dark mode to globals.css with proper CSS variables

## Debate Outcomes

### 1. Padding/Margin/Width/Height tokens vs Tailwind utilities

**Position**: Use Tailwind utilities as primary, add tokens only for semantic spacing patterns.

**Reasoning**:
- Tailwind's spacing scale (4px base) is comprehensive and well-tested
- Adding parallel token layer for every padding/margin value increases maintenance burden without benefit
- Industry standard: Tailwind-first with semantic tokens for repeated patterns only (like `spacing.responsive` already in designSystem.js)
- Exception: Add semantic tokens for component-level patterns (e.g., `CARD_CONFIG.padding`, `SECTION_GAP`) where the same spacing is reused across 5+ components — not for one-off values
- Width/height: only add tokens for repeated layout constants (container widths, sidebar widths), not arbitrary sizes

### 2. Styling approach: MUI components vs Custom + Tailwind vs Hybrid

**Position**: Hybrid approach with MUI-preserve strategy for existing MUI, Tailwind for new.

**Reasoning**:
- 62 components already use mixed approach; full rewrite too expensive
- MUI components (Dialog, Autocomplete, TextField) provide complex interactions reliably
- New components should use Tailwind-first approach
- Pattern: MUI component → div wrapper with Tailwind for layout/spacing
- Migration path: Gradual, component-by-component as touched

### 3. Dark mode: invest now or later?

**Position**: Architectural prep now, full implementation later.

**Reasoning**:
- Token structure can be prepared without affecting light mode
- Dark mode is not current user requirement
- Prep work: organize tokens to support theme switching, add CSS variables
- Full implementation: gated by user demand/competitive analysis
- Risk: Unprepared architecture makes dark mode expensive later

### 4. CSS Modules vs Tailwind-only vs Hybrid

**Position**: Hybrid - CSS Modules for component-scoped complex styles, Tailwind for utilities.

**Reasoning**:
- 47 CSS module files in components/ (56 project-wide, some up to 410 lines) - eliminating is impractical
- CSS Modules useful for: animations, complex pseudo-elements, component-specific overrides
- Tailwind for: layout, spacing, colors, responsive utilities
- Pattern: Tailwind base classes + CSS Modules for component-specific needs
- No migration plan needed - current hybrid is sustainable

### 5. Documentation: Storybook vs simpler approach?

**Position**: Component docstrings in code + vault documentation, not Storybook.

**Reasoning**:
- Team size doesn't justify Storybook maintenance overhead
- Vault already documents patterns (design-systems.md, CODE_PATTERNS.md)
- Component-level JSDoc comments sufficient for current team
- Storybook value: visual testing, but not critical for current workflow
- Alternative: screenshots in vault docs for key components

## Migration Roadmap

### Phase 1: Token Completion (1-2 days)
**Objective**: Fill missing token categories

**Tasks**:
1. Add opacity scale (OPACITY: { disabled: 0.5, hover: 0.8, etc. })
2. Add z-index system (Z_INDEX: { dropdown: 50, modal: 100, tooltip: 200 })
3. Add transition tokens (TRANSITION: { fast: '150ms', normal: '200ms', slow: '300ms' })
4. Add line-height and letter-spacing to TYPOGRAPHY_SCALE
5. Add semantic layout tokens for repeated patterns only (CONTAINER_WIDTH: '1200px', SIDEBAR_WIDTH: '240px')
6. Replace hardcoded colors in `globals.css` with CSS variables from tokens

**Files to Change**:
- `helpers/designSystem.js` (+80 lines)
- `tailwind.config.js` (add new token mappings)
- `styles/globals.css` (replace 22 hardcoded colors)

### Phase 2: Component Cleanup (1-2 weeks)
**Objective**: Remove inline styles and hardcoded values from top 10 violation files

> **Counts as of 2026-06-13 audit.** Re-run `grep` before cleanup — violation counts drift with code changes; relative priority (most-first) is more stable than absolute counts.

**Priority Order** (by violation count):
1. `pdfStyles.js` (33 hardcoded colors) - PDF export styling, consider separate token system
2. `components/auth/ProfileMenu.js` (23 colors, 26 inline styles) - Convert to design tokens
3. `components/UI/ServiceCategoryBadge.js` (17 colors) - Use COLORS.badge tokens
4. `components/icons/transportations/suv-icon.js` (15 colors) - SVG fill colors
5. `components/order/ProfessionalOrderHeader.js` (12 colors, 7 fontSize) - Use typography tokens
6. `components/order/OrderDetail.js` (18 inline styles) - Convert to Tailwind
7. `pages/rate-review/[reviewSlug].js` (15 inline styles) - Use design tokens
8. `components/layout/layout.js` (14 inline styles) - Convert to Tailwind
9. `components/search/ProductSearchForm2.js` (9 inline styles) - Convert to Tailwind
10. `components/search/ProductSearchForm.js` (8 inline styles) - Convert to Tailwind

**Pattern**: One file per commit, incremental verification

### Phase 3: Pattern Standardization (2-3 weeks)
**Objective**: Standardize component patterns

**Tasks**:
1. **Button Pattern**: Audit all button implementations, standardize on BUTTON_CONFIG or MUI Button
2. **Card Pattern**: Ensure all pages use Section/ContentCard wrapper pattern
3. **Modal Pattern**: Choose one modal approach (MUI Dialog or custom), migrate all uses
4. **Badge Pattern**: Consolidate BadgeChip and ServiceCategoryBadge
5. **Form Pattern**: Standardize on INPUT_CONFIG or MUI TextField consistently

### Phase 4: Documentation + Governance (1 week)
**Objective**: Document design system usage

**Tasks**:
1. Add JSDoc comments to all design system exports
2. Create vault doc: `design-system-usage-guide.md` with examples
3. Add design system lint rules (no hardcoded colors, no inline fontSize)
4. Document component props and usage patterns
5. Create visual examples in vault for key components

### Phase 5: Advanced (2-4 weeks)
**Objective**: Dark mode and animation system

**Tasks**:
1. Implement dark mode architecture (CSS variables, theme context)
2. Add animation tokens (timing, easing)
3. Add responsive spacing patterns
4. Performance audit (CSS bundle size, unused Tailwind)
5. Accessibility audit and fixes

## Priority Matrix

| Priority | Issue | Impact | Effort | Phase |
|----------|-------|--------|--------|-------|
| **P0** | Replace globals.css hardcoded colors | High | Low | Phase 1 |
| **P0** | Add opacity/z-index/transition tokens | High | Low | Phase 1 |
| **P1** | ProfileMenu.js inline styles | High | Medium | Phase 2 |
| **P1** | OrderDetail.js inline styles | High | Medium | Phase 2 |
| **P1** | ProfessionalOrderHeader.js fontSize inline | Medium | Medium | Phase 2 |
| **P2** | PDF styles color standardization | Medium | High | Phase 2 |
| **P2** | Button pattern consolidation | Medium | High | Phase 3 |
| **P2** | Modal pattern consolidation | Medium | High | Phase 3 |
| **P3** | Badge pattern consolidation | Low | Medium | Phase 3 |
| **P3** | Dark mode prep | Medium | Low | Phase 5 |

## Quick Wins — Do This Week

1. **Replace globals.css hardcoded colors** (1 hour)
   - 22 hardcoded colors → CSS variables from designSystem.js
   - File: `styles/globals.css:12,69,71,98-99,109,126,134-165,399`

2. **Add missing tokens to designSystem.js** (1 hour)
   - Add OPACITY scale (5 values)
   - Add Z_INDEX system (5 levels)
   - Add TRANSITION tokens (3 speeds)
   - Add line-height to TYPOGRAPHY_SCALE
   - Add CONTAINER_WIDTH / SIDEBAR_WIDTH for repeated layout constants

3. **ProfileMenu.js color cleanup** (1 hour)
   - Replace 22 hardcoded colors with COLORS tokens
   - File: `components/auth/ProfileMenu.js`

4. **ServiceCategoryBadge.js use existing badge tokens** (30 min)
   - Replace 17 hardcoded colors with COLORS.badge
   - File: `components/UI/ServiceCategoryBadge.js`

5. **Add CSS variables for brand colors** (30 min)
   - Define CSS variables in globals.css from designSystem.js COLORS
   - Enables theme switching later

6. **Standardize ProfessionalOrderHeader.js fontSize** (30 min)
   - Replace 7 inline fontSize with TYPOGRAPHY_SCALE
   - File: `components/order/ProfessionalOrderHeader.js`

7. **Create design-system-usage-guide.md** (1 hour)
   - Document how to use design tokens
   - Add examples for each token category
   - Store in vault

8. **Add JSDoc to designSystem.js exports** (30 min)
   - Document each token category
   - Add usage examples

9. **Fix globals.css !important usage** (30 min)
   - Reduce 10 !important declarations
   - Most unnecessary specificity

10. **Create component prop documentation** (2 hours)
    - Add JSDoc to top 10 most-used UI components
    - Document props, usage patterns, examples

## Delta from 2026-05-31 Audit

Previous audit (`[[design-system-audit-2026-05-31]]`) covered brand color (#3b5998) and initial token gaps. This audit is deeper:
- **Expanded scope**: 10 token dimensions (vs ~5), 13 violation categories, 12 UX dimensions
- **Verified counts**: grep-confirmed violation numbers (previous used estimates)
- **New findings**: CSS module surface larger than expected (47 vs presumed ~33), globals.css specificity issues, MUI/Tailwind breakpoint mismatch
- **Resolved**: Debate outcomes for padding/margin tokens (Tailwind-first, not new token layer), documentation approach (vault docs, not Storybook)

## Related

- `designSystem.js` — Token definitions (helpers/designSystem.js:1)
- `tailwind.config.js` — Tailwind configuration (tailwind.config.js:1)
- `theme.js` — MUI theme configuration (theme.js:1)
- [[nextjs-patterns]] — Component patterns (docs/development/CODE_PATTERNS.md)
- [[design-systems]] — Design system documentation (docs/design/DESIGN_SYSTEM.md)
- [[design-systems]] — Vault design system knowledge (03-knowledge/design-systems.md)

## Atomized Notes (Extracted 2026-06-22)

- [[mui-tailwind-breakpoint-mismatch-sm-600-vs-640]] — MUI `sm=600` vs Tailwind `sm=640` mismatch. Standardize on Tailwind.
- [[hybrid-mui-preserve-tailwind-new-styling-strategy]] — hybrid: preserve MUI existing, Tailwind-first new. Semantic tokens ≥5 reuse.
- [[tailwind-first-spacing-semantic-tokens-only-5plus-reuse]] — Tailwind-first spacing. Tokens only if reused ≥5×.
