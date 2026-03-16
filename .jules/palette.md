## 2024-03-24 - [Emoji Accessibility via innerHTML]
**Learning:** When adding `aria-hidden="true"` spans around decorative emojis in dynamic JavaScript states (like loading buttons or copy success states), it's crucial to switch from using `.innerText` to `.innerHTML` for state management. Using `.innerText` will render the literal HTML string instead of parsing the accessibility tags, whereas `.innerHTML` correctly preserves the DOM nodes and prevents screen readers from redundantly reading out the emojis.
**Action:** Always check the method used for DOM updates when adding accessibility tags to dynamic text. Ensure state capture (e.g., `const original = btn.innerHTML`) and restoration also use `.innerHTML`.
## 2026-03-09 - [Input Form Readability and Highlight Contrast]
**Learning:** Dark mode interfaces with light text `var(--text-main)` demand special care regarding contrast. Form inputs need distinct boundaries (e.g. `var(--text-dim)`) to satisfy WCAG 1.4.11 Non-text Contrast, as muted borders often blend with the background. Furthermore, hardcoded light-themed highlight colors (like `#dcfce7`) for temporary active states cause severe readability issues by creating a 1:1 text-to-background contrast with light text.
**Action:** Use distinct contrast values like `var(--text-dim)` for input borders, and always rely on alpha-blended accent colors (e.g. `rgba(255, 176, 0, 0.2)`) for temporary state highlights rather than hardcoded light/dark colors that conflict with the theme's text.

## 2026-03-11 - [Dynamic JS Colors & Contrast]
**Learning:** Hardcoded hex colors injected by JS for dynamic states (like success/error margins) can cause severe contrast issues in dark themes.
**Action:** Always prefer applying CSS classes or using existing CSS custom properties (variables like `var(--success)`) for dynamic inline styling to ensure consistent, accessible contrast across themes.

## 2026-03-14 - [Auto-Select Text on Focus for Engineering Forms]
**Learning:** In technical data-entry applications (like Link Budget calculators or TLE form fields) where `<input>` fields are pre-filled with dense default values (e.g., `2400000000` or `1 25544U...`), forcing users to manually highlight or backspace the existing text before typing a new value introduces significant friction. Adding a simple vanilla JS listener (`input.addEventListener('focus', function() { this.select(); })`) is a massive micro-UX win that drastically speeds up data entry and reduces frustration for power users, mirroring standard spreadsheet behavior.
**Action:** For dense forms with default values, always implement `this.select()` on focus to allow users to immediately overwrite the data without explicit text highlighting.

## 2026-03-15 - [Monospace Fonts for Fixed-Format Technical Strings]
**Learning:** For inputs containing highly-structured, fixed-format technical strings where column alignment and character positioning convey important information (such as Two-Line Element sets / TLEs), using standard variable-width fonts makes the data unreadable and hard to verify. Applying a monospace font significantly improves readability and usability by maintaining vertical alignment of the fixed-width data fields.
**Action:** Always apply `font-family: monospace;` to input fields that accept fixed-format, column-aligned technical data.

## 2026-03-16 - [Prevent Accidental Data Corruption on Number Inputs via Wheel Scrolling]
**Learning:** In technical forms with many `input[type="number"]` fields, users frequently scroll the page using the mouse wheel or trackpad. If a number input is focused and the cursor happens to be hovering over it during a scroll, the browser natively intercepts the `wheel` event to increment or decrement the input's value. This leads to silent data corruption, as users often do not realize the value has changed while they were simply trying to navigate the page.
**Action:** Always add a global `wheel` event listener to pages with number inputs that calls `document.activeElement.blur()` if the active element is of type `number`, ensuring the page scrolls gracefully and preventing unintentional data modification.
