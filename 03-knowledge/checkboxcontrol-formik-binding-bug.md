# CheckBoxControl never bound to Formik `checked` (AD shared bug)

**Repo:** admin-dashboard · **File:** `components/forms/components/CheckBoxControl.js`

**Bug (original):**
```jsx
<Field as={FormControlLabel} control={<Checkbox name={name}/>} label={label} />
```
The inner `<Checkbox>` is a static child. `Field as={FormControlLabel}` passes
`value/onChange` to the LABEL, never to the box → the checkbox's `checked` is
never driven by `values[name]`. Result: every checkbox using this control is
**cosmetic-only on edit** — loads unchecked regardless of saved state, and toggles
may not persist. Create-mode defaults hid it for a long time.

**Fix (render-prop + `type="checkbox"`):**
```jsx
<Field name={name} type="checkbox">
  {({ field }) => (
    <FormControlLabel
      control={<Checkbox {...field} checked={!!field.value} color="primary" />}
      label={label}
    />
  )}
</Field>
```
`type="checkbox"` makes Formik manage `checked`/`onChange`; `field.value` drives the box.

**Blast radius:** shared control — affected coupon form, hero-banner `is_active`
(`HeroBannerForm.js:188`), ModalPopUp `agreeTerms`. All boolean; fix makes every
caller correct, no API change (props `label`,`name` unchanged).

**Hit live:** #275 — coupon edit checkboxes (Active / one-per-customer / new-users) blank.

**Lesson:** MUI `FormControlLabel + Checkbox` under Formik needs the box bound
directly (`{...field} checked`), not the label. `<Field as>` on a wrapper does not
propagate to a fixed `control` child.
