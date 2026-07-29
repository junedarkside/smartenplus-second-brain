# CustomSelect reads `key`, not `label` (AD form gotcha)

**Repo:** admin-dashboard · **File:** `components/forms/components/CustomSelect.js`

The shared `CustomSelect` (used via `FormControl control="select"`) renders each
option's display text from **`option.key`** — NOT `label`, NOT `value`.

- `renderValue`: `options.find(o => o.value === selected)?.key`
- MenuItem body: `{option.key}`

**Symptom of the bug:** dropdown opens but every row is blank / no text; selection
still submits the right value. Cause = options passed as `{ value, label }` →
`option.key` is `undefined`.

**Correct shape:**
```js
const OPTIONS = [
  { value: 'percentage', key: 'Percentage (%)' },
  { value: 'fixed', key: 'Fixed Amount' },
]
```

**Convention reference:** `components/contracts/ContractFormFields.js:86` maps
`SERVICE_CATEGORY_OPTIONS.map(o => ({ value: o.value, key: o.label }))`.

**Hit live:** #275 coupon form (Discount Type dropdown blank until `label`→`key`).
