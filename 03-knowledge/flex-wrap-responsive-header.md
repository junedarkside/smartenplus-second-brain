# Tailwind: Responsive Header — flex-wrap Row Pattern

Single `flex-row` header with many items (back button + ID + badge + action buttons) clips action buttons on mobile 375px.

**Pattern:** `flex-wrap` on outer row + `shrink-0` on button group + `min-w-0` on info div.

`ml-auto` on button group = right-aligned on desktop (single row) AND right-aligned on mobile (wrapped second row).

```jsx
<div className="flex flex-row flex-wrap gap-x-2 gap-y-2 items-center">
  <IconButton>←</IconButton>

  {/* Info — can shrink, text truncates */}
  <div className="flex items-center gap-2 min-w-0">
    <span className="truncate">Booking ID: PSF9498724</span>
    <Badge>Confirmed</Badge>
  </div>

  {/* Buttons — don't shrink, wrap to row 2 on mobile, stay right */}
  <div className="flex gap-2 ml-auto items-center shrink-0">
    <Button>Get Ticket</Button>
    <Button>Request Change</Button>
  </div>
</div>
```

- Desktop wide: all fit row 1, buttons pushed right by `ml-auto`
- Mobile 375px: info + badge fill row 1, buttons wrap to row 2 right-aligned

Implemented in `BookingDetailMain.js` (session #159, `fix/header-responsive`).
