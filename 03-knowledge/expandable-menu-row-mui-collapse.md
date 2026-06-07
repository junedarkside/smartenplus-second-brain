---
name: expandable-menu-row-mui-collapse
description: MUI Menu + Collapse pattern for parent rows that toggle 2-3 child rows. Per-row useState, aria-expanded, chevron rotation animation. Saves 60-120px per collapsed group in tall menus.
type: knowledge-atom
date: 2026-06-06
parent: website-audit-full-2026-06-06-overview
---

# Expandable Menu Row (MUI Collapse)

## Summary
2-component pattern for tall menus: `ExpandableMenuRow` (parent, chevron, `aria-expanded`, per-row `useState`, `<Collapse>`) + `SubMenuRow` (indented child). Each parent maintains independent open/closed state. Saves 60-120px per collapsed group. Reusable for any nested menu UX where 4+ related actions share a theme.

## Context
`website-audit-full-2026-06-06` r3-leader-synthesis. ProfileMenu flat layout was 11 items + 4 dividers ≈ 820px tall, exceeded viewport after F2 anchor shift. Solution: group related rows under 3 expandable parents. Closed parents hide 2-3 sub-rows each. Cumulative savings: 3 expandables × ~80px = **−240px** default height.

## Problem
- 8+ menu items force scroll OR viewport overflow
- 4+ dividers create visual noise ("SaaS admin panel" aesthetic)
- Flat layout treats "My Bookings" and "Help Center" as equal-weight — but users perceive them as grouped (activity vs account vs support)
- Mobile Bottom Sheet (80dvh) makes tall content worse

## Pattern

### ExpandableMenuRow
```jsx
function ExpandableMenuRow({ icon, label, subtitle, children, disabled }) {
  const [open, setOpen] = useState(false);
  return (
    <>
      <MenuItem
        onClick={() => setOpen((o) => !o)}
        disabled={disabled}
        sx={ROW_SX}
        aria-expanded={open}
      >
        <span style={{ color: '#9CA3AF', flexShrink: 0, marginTop: 2 }}>{icon}</span>
        <span style={{ display: 'flex', flexDirection: 'column', gap: 1, flex: 1 }}>
          <span style={{ fontSize: 14, fontWeight: 500, color: '#374151', lineHeight: '20px' }}>{label}</span>
          {subtitle && <span style={{ fontSize: 12, color: '#9CA3AF', lineHeight: '16px' }}>{subtitle}</span>}
        </span>
        <ExpandMoreOutlinedIcon
          sx={{
            color: '#9CA3AF', flexShrink: 0, marginTop: 2,
            transform: open ? 'rotate(180deg)' : 'rotate(0deg)',
            transition: 'transform 200ms',
          }}
        />
      </MenuItem>
      <Collapse in={open} timeout={200}>
        {children}
      </Collapse>
    </>
  );
}
```

### SubMenuRow
```jsx
function SubMenuRow({ icon, label, onClick, disabled }) {
  return (
    <MenuItem onClick={onClick} disabled={disabled} sx={{ ...ROW_SX, pl: '32px', py: '8px', minHeight: 0 }}>
      <span style={{ color: '#9CA3AF', flexShrink: 0, marginTop: 2 }}>{icon}</span>
      <span style={{ fontSize: 13, fontWeight: 400, color: '#374151', lineHeight: '18px' }}>{label}</span>
    </MenuItem>
  );
}
```

### Usage
```jsx
<ExpandableMenuRow
  icon={<HistoryOutlinedIcon sx={SZ} />}
  label="My Activity"
  subtitle="Bookings, orders, reviews"
>
  <SubMenuRow icon={<ConfirmationNumberOutlinedIcon sx={...} />} label="My Bookings" onClick={() => navigateTo('/bookings')} />
  <SubMenuRow icon={<ReceiptLongOutlinedIcon sx={...} />} label="My Orders" onClick={() => navigateTo('/orders')} />
  <SubMenuRow icon={<RateReviewOutlinedIcon sx={...} />} label="Rate & Reviews" onClick={() => navigateTo('/rate-review')} />
</ExpandableMenuRow>
```

## Details

### Per-Row useState
- Each `ExpandableMenuRow` has independent open state
- Multiple rows can be open simultaneously (users can compare across groups)
- Alternative: single shared state with `openId` — more complex, lower UX value

### aria-expanded
- Set on parent MenuItem: `aria-expanded={open}`
- Required for screen readers (announces "collapsed"/"expanded")
- Also helps ARIA-based test queries (`page.getByRole('button', { expanded: true })`)

### Collapse timeout
- `timeout={200}` matches chevron rotation duration
- Faster than MUI default (300ms) — feels snappier for menu UX
- Children stay mounted but hidden — preserves child state if reopened

### SubMenuRow Styling
- `pl: '32px'` — 16px row padding + 16px indent for hierarchy
- `fontSize: 13, fontWeight: 400` — smaller than parent (14/500) signals child
- `minHeight: 0` — overrides MUI default 48px row height; sub-rows can be ~36px
- `py: '8px'` — tighter than parent's 10px

### Visual Spec
- Closed parent: 1 row (40-48px) + 1 chevron icon
- Open parent: 1 row + collapse animation + 2-3 sub-rows (~36px each)
- 3 closed groups save ~240px vs 3 flat rows
- Sub-rows render even when closed (no extra render cost)

## Real-World Triggers
Use this pattern when:
- 4+ related actions share a theme (Activity, Account, Support)
- Tall menus overflow viewport on small screens
- Users benefit from collapsed default (less visual noise)
- Mobile bottom sheet has hard height cap (80dvh)

## Grouping Heuristic
- **Activity group:** Bookings, Orders, Reviews (user's own data)
- **Account group:** Profile, Family/Friends, Password (settings)
- **Support group:** FAQ, Forum, Help Center (help-seeking)
- 2-3 sub-rows per parent feels balanced; 1 = don't group, 4+ = split

## Tradeoffs
- **Pro:** 60-120px height savings per collapsed group
- **Pro:** Visual hierarchy without losing discoverability
- **Pro:** `aria-expanded` is screen-reader accessible
- **Pro:** Sub-rows preserve state when parent reopens
- **Con:** 1 extra click to access sub-rows (acceptable — discoverable via subtitle)
- **Con:** Chevron + collapse adds ~30 lines per parent (3 parents = 90 lines)

## When NOT to Use
- 1-2 sub-items — just nest directly or keep flat
- Actions with wildly different labels (e.g., "Log Out" + "Settings") — keep flat
- Menus with 3-4 items total — collapse overhead exceeds savings

## Related
- [[mui-menu-paper-overflow-guard]] — companion for viewport-edge menus
- [[mui-dropdown-preserve-strategy]] — MUI Menu core + 3-file split
- [[profile-dropdown-redesign-2026-05-29]] — original 11→6 item reduction
