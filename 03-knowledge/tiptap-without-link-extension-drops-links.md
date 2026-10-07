# Tiptap Without the Link Extension Drops Links

## Summary
Tiptap's StarterKit has no Link mark. Loading HTML with `<a href>` and saving it again silently removes the anchors. Also: the editor rewrites stored HTML on load, so "send only if changed" must compare against the normalized original.

## Context
AD editor config (`components/editor/editorConfig.js`) was StarterKit + Color + TextStyle. A toolbar `setLink` helper existed but nothing registered the mark, and the toolbar had no link button. 3 of 6 existing station descriptions contained links.

## Details
- Fix: `@tiptap/extension-link` pinned to the same version as `@tiptap/core` (2.3.2, exact), `Link.configure({ openOnClick: false, autolink: false, validate: safe-protocol })`, plus a toolbar button calling the existing `setLink` helper. Adding it to the shared config also stops silent link loss in Location, FAQ and contract editors.
- Change detection: `new Editor({ extensions, content }).getHTML()` gives the normalized form (`<br />` → `<br>`, entities). Initialize the form with that, compare against it, and send the field only when different; an emptied editor (`<p></p>`) is sent as `''`. Otherwise a name-only edit rewrites the description.
- Toolbar/visitor mismatch: editor offers h1, h5, h6, blockquote, code, strike; the visitor sanitizer keeps only `p br b i em strong u ul ol li a h2 h3 h4` (tag dropped, text kept).

## Related
[[bot-draft-then-human-approve-design]] · [[react-api-field-access-null-guard-pattern]]
