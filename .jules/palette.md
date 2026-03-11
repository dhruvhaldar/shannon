## 2024-03-24 - [Emoji Accessibility via innerHTML]
**Learning:** When adding `aria-hidden="true"` spans around decorative emojis in dynamic JavaScript states (like loading buttons or copy success states), it's crucial to switch from using `.innerText` to `.innerHTML` for state management. Using `.innerText` will render the literal HTML string instead of parsing the accessibility tags, whereas `.innerHTML` correctly preserves the DOM nodes and prevents screen readers from redundantly reading out the emojis.
**Action:** Always check the method used for DOM updates when adding accessibility tags to dynamic text. Ensure state capture (e.g., `const original = btn.innerHTML`) and restoration also use `.innerHTML`.
## 2026-03-09 - [Input Form Readability and Highlight Contrast]
**Learning:** Dark mode interfaces with light text `var(--text-main)` demand special care regarding contrast. Form inputs need distinct boundaries (e.g. `var(--text-dim)`) to satisfy WCAG 1.4.11 Non-text Contrast, as muted borders often blend with the background. Furthermore, hardcoded light-themed highlight colors (like `#dcfce7`) for temporary active states cause severe readability issues by creating a 1:1 text-to-background contrast with light text.
**Action:** Use distinct contrast values like `var(--text-dim)` for input borders, and always rely on alpha-blended accent colors (e.g. `rgba(255, 176, 0, 0.2)`) for temporary state highlights rather than hardcoded light/dark colors that conflict with the theme's text.

## 2026-03-11 - [Dynamic JS Colors & Contrast]
**Learning:** Hardcoded hex colors injected by JS for dynamic states (like success/error margins) can cause severe contrast issues in dark themes.
**Action:** Always prefer applying CSS classes or using existing CSS custom properties (variables like `var(--success)`) for dynamic inline styling to ensure consistent, accessible contrast across themes.
