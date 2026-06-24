# MUI: Button vs IconButton — Mobile UX Rule

`IconButton + Tooltip` = invisible on touch devices. Tooltip requires hover — doesn't fire on tap. No label = user can't discover the action.

**Rule:** any action a mobile user needs to discover → use `Button` with `startIcon` + text label.

```jsx
// Bad — mobile user sees icon, no idea what it does
<Tooltip title="View PDF">
  <span><IconButton onClick={handlePdf}><PictureAsPdfIcon /></IconButton></span>
</Tooltip>

// Good — label is always visible, icon reinforces meaning
<Button
  size="small"
  variant="contained"
  startIcon={<PictureAsPdfIcon sx={{ fontSize: 18 }} />}
  onClick={handlePdf}
  sx={{
    textTransform: 'none',
    fontSize: '0.75rem',
    boxShadow: 'none',
    '&.Mui-disabled': { opacity: 0.5 },  // MUI default disabled opacity too low
  }}
>
  Get Ticket
</Button>
```

Implemented in `BookingDetailMain.js` header (session #159). Replaced "print booking" + "request booking" icon buttons that users reported not understanding.
