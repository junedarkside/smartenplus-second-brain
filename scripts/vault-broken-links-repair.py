#!/usr/bin/env python3
"""Repair broken wikilinks in vault via explicit rule map. Idempotent."""
import re
import sys
from pathlib import Path

VAULT = Path("/Users/charuwatnaranong/Desktop/SmartEnPlus/smartenplus project")
WIKILINK_RE = re.compile(r"\[\[([^\]\n]+?)\]\]")

# explicit repair rules: source fragment -> replacement
# Each rule runs in order. Use raw substring match within file text.
RULES = [
    # 4a: cross-vault / path-based
    ("[[features/payment/PAYMENT_CHECKOUT_ARCHITECTURE_REVIEW.md]]", "[[payment-checkout-architecture-audit]]"),
    ("[[testing/PAYMENT_CANCEL_FLOW_TESTS.md]]", "[[payment-cancel-state-prevmethod-guard]]"),
    ("[[testing/PAYMENT_CHECKOUT_AUDIT.md]]", "[[payment-checkout-architecture-audit]]"),
    ("[[testing/PAYMENT_CHECKOUT_MANUAL_TEST_GUIDE.md]]", "[[payment-checkout-e2e-testing]]"),
    # 4b: code symbols -> inline code
    ("[[ProfileButton.js]]", "`ProfileButton.js`"),
    ("[[theme.js]]", "`theme.js`"),
    ("[[designSystem.js]]", "`designSystem.js`"),
    ("[[useAuthRedirect patterns elsewhere]]", "`useAuthRedirect` patterns elsewhere"),
    # 4f: relative paths in 01-projects/<sub>/
    ("[[../help-faqs-landing-2026-06-07/audit]]", "[[help-faqs-landing-2026-06-07-audit]]"),
    # 4x: .md suffix in wikilinks
    ("[[master-state.original.md]]", "[[08-archive/.originals/master-state.original]]"),
    ("[[payment-exception-catalog.md]]", "[[payment-exception-catalog]]"),
    ("[[payment-frontend-flow-mechanics.md]]", "[[payment-frontend-flow-mechanics]]"),
    ("[[payment-idempotency-key-cart-total.md]]", "[[payment-idempotency-key-cart-total]]"),
    # 4d: PascalCase ADR check — keep, flag for human
    # 4c: ALL_CAPS
    ("[[CODE_PATTERNS]]", "[[nextjs-patterns]]"),  # alias to nextjs-patterns (best fit)
    ("[[DESIGN_SYSTEM]]", "[[design-systems]]"),
    # 4b2: extension tail
    ("[[payment-promptpay-no-webhook-on-expiry]]", "[[promptpay-no-webhook-on-expiry]]"),
    ("[[webp-og-image-1200x630]]", "[[og-image-1200x630-webp]]"),
    # orphan redirects to real notes
    ("[[r2-skeptic-review]]", "[[customer-os-thesis-r2-skeptic-review]]"),  # alias -> full filename (8 linkers, false orphan)
    ("[[thailand-platform-analysis]]", "[[business-development-thailand-platform-analysis]]"),
    ("[[thailand-bundle-architecture]]", "[[business-development-thailand-bundle-architecture]]"),
    ("[[zeitrip-mvp-product-spec]]", "[[business-development-zeitrip-mvp]]"),
    ("[[thailand-bundling-margin-strategy]]", "[[business-development-thailand-bundling-margin]]"),
    ("[[website-audit-full-2026-06-06]]", "[[website-audit-full-2026-06-06-overview]]"),
    ("[[rate-review-uxui-audit-2026-06-06]]", "[[rate-review-uxui-audit-2026-06-06-overview]]"),
    ("[[homepage-seo-performance-deep-review]]", "[[homepage-seo-performance-deep-review-2026-05-21]]"),
    ("[[unified-travel-wellness-thesis]]", "[[business-development-unified-travel-wellness-thesis]]"),
    ("[[experiences-section-canonical-categories]]", "[[experiences-2026-marketplace-redesign]]"),
    ("[[southeast_asia_transport_platform_direction]]", "[[southeast-asia-transport-platform-direction]]"),
    ("[[activities-browse-architecture]]", "[[activities-browse-filter-inactive-contracts]]"),
    ("[[design-system-tokens-expansion-2026-05-31]]", "[[design-system-tokens-expansion]]"),
    ("[[payment-frontend-checkout-flow]]", "[[payment-frontend-flow-mechanics]]"),
    ("[[order-creation-filter-rule]]", "[[django-booking-creation-validation-gate]]"),
    ("[[send_booking_data]]", "[[payment-checkout-architecture-audit]]"),
    ("[[payment-model-fields]]", "[[payment-charge-service-layer]]"),
    ("[[decouple-env-pattern]]", "[[site-url-config-pattern]]"),
    ("[[card-carousel-container-pattern]]", "[[carousel-design-standard]]"),
    ("[[popular-routes-carousel-fix-2026-05-28]]", "[[carousel-design-standard]]"),
    ("[[sticky-sidebar-debugger]]", "[[sidebar-sticky-2col-responsive-grid]]"),
    ("[[nav-config-research]]", "[[adaptive-header-route-type-pattern]]"),
    ("[[nav-header-redesign-2026-05-24]]", "[[nav-header-redesign]]"),
    ("[[seo-homepage-auditor]]", "[[seo-homepage-specialist-team]]"),
    ("[[security-best-practices]]", "[[dompurify-xss-prevention-pattern]]"),
    ("[[form-layout]]", "[[checkout-formdata-persist-guard-pattern]]"),
    ("[[in-article-cta-pattern]]", "[[section-contentcard-wrapper-pattern]]"),
    ("[[navigation-api]]", "[[adaptive-header-route-type-pattern]]"),
    ("[[nextjs-image-component-cls-prevention]]", "[[next-image-component-cls-prevention|hero-cls-precise-sizes-attribute]]"),  # alt target
    ("[[omise-api-docs]]", "[[omise-api-reference-2026-06-12]]"),
    ("[[order-create-response-shape]]", "[[django-400-vs-409-duplicate-cart-item]]"),
    ("[[payment-method-name-contract]]", "[[payment-checkout-architecture-audit]]"),
    ("[[products-routes]]", "[[api-endpoints]]"),
    ("[[quick-filter-pills-direct-refundable]]", "[[activities-sort-filter-ux]]"),
    ("[[search-cover-ssr-data-fallback]]", "[[nextjs-patterns]]"),
    ("[[session-structure]]", "[[nextauth-session-shape]]"),
    ("[[tailwind-arbitrary-values-inline-style-bloat]]", "[[mui-emotion-tailwind-injectfirst]]"),
    ("[[use-payment-coupon-manager-state]]", "[[payment-frontend-flow-mechanics]]"),
    ("[[use-payment-initialization-lifecycle]]", "[[payment-frontend-flow-mechanics]]"),
    ("[[useAuthRedirect]]", "`useAuthRedirect`"),
    # 5: template placeholders -> mask in HTML comments (handled in step 5 instead; skip here)
    # folder-as-link
    ("[[01-projects]]", "[[01-projects/README]]"),
    ("[[03-knowledge]]", "[[03-knowledge/README]]"),
    ("[[05-templates]]", "[[05-templates/README]]"),
    ("[[08-archive]]", "[[08-archive/README]]"),
    ("[[04-decisions]]", "[[04-decisions/README]]"),
    ("[[02-areas]]", "[[02-areas/README]]"),
    ("[[06-systems]]", "[[06-systems/README]]"),
    ("[[07-logs]]", "[[07-logs/README]]"),
    # already-handled
    ("[[next-image-component-cls-prevention|hero-cls-precise-sizes-attribute]]", "[[hero-cls-precise-sizes-attribute]]"),
]

def main():
    md_files = [p for p in VAULT.rglob("*.md") if ".git" not in p.parts and ".obsidian" not in p.parts]
    total_changes = 0
    files_changed = 0
    for p in md_files:
        text = p.read_text(encoding="utf-8", errors="ignore")
        original = text
        local = 0
        for old, new in RULES:
            if old in text:
                count = text.count(old)
                text = text.replace(old, new)
                local += count
        if text != original:
            p.write_text(text, encoding="utf-8")
            total_changes += local
            files_changed += 1
            print(f"  {p.relative_to(VAULT)}: {local} changes")
    print(f"\nfiles_changed: {files_changed}")
    print(f"total_replacements: {total_changes}")

if __name__ == "__main__":
    main()
