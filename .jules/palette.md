## 2026-02-28 - [Visual Cues for Initial State]
**Learning:** Result panels appeared completely blank or as empty bordered containers on initial load, leaving users without guidance on what those areas are for. Furthermore, disabled buttons lacked visual styling, leading to confusion during loading states.
**Action:** Add helpful empty states with icons and descriptive text to result containers before data is fetched. Ensure `button:disabled` states are explicitly styled in CSS with appropriate opacity and cursor changes.

## 2026-03-01 - [Screen Reader Support for Visualizations]
**Learning:** `canvas` elements and D3-generated SVGs in this app were not properly announced by screen readers without explicit ARIA roles. For SVGs, screen readers attempted to parse the internal `<line>` and `<text>` nodes sequentially, which creates a noisy and confusing experience out of context.
**Action:** Add `role="img"` to `<canvas>` elements and D3-generated SVGs. Provide an appropriate `aria-label` or fallback text to ensure the visualization's purpose is communicated correctly to screen reader users.

## 2026-03-02 - [Screen Reader Announcements for Visual Cues]
**Learning:** Visual feedback mechanisms (like highlighting background colors, changing button text briefly, or auto-filling form inputs) are completely missed by screen reader users, leaving them unaware of dynamic state changes that occur silently in the DOM.
**Action:** Implement an explicit `aria-live="polite"` announcer region (`#a11y-announcer`) and wire it up to announce text for purely visual state changes, such as successfully copying to clipboard, loading presets, or auto-populating inputs via geolocation/paste.
