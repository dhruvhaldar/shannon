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

## 2026-03-17 - [Accessible Landmark Regions for Multi-Form Dashboards]
**Learning:** In dashboards containing multiple distinct tools or calculators on a single page, generic `<form>` elements are not easily distinguishable to screen reader users jumping between landmarks. Adding an `id` to the panel's heading and using `aria-labelledby` on the `<form>` converts it into an accessible landmark region, explicitly associating the form controls with the tool's context. Furthermore, if the application has a feature to sync state to the URL (e.g. `syncFormToUrl`), ensure it is symmetrically applied across *all* forms in the suite to avoid inconsistent user expectations.
**Action:** Always use `aria-labelledby` on `<form>` elements in multi-tool dashboards to create distinct landmark regions, and ensure UX features like URL state syncing are universally applied across similar components.

## 2026-03-22 - [Auto-Submit Shared URL States]
**Learning:** When a dashboard supports sharing state via URLs, loading the form values on initial page load is good, but forcing the user to manually click 'Submit' again creates an unnecessary step and an initially blank/empty state. Automatically submitting the form if it was populated from the URL provides immediate value and a smoother experience for users clicking shared links.
**Action:** Always auto-submit forms on load if their state was successfully populated from URL parameters.

## 2026-03-23 - [Manual prefers-reduced-motion Checks in WebGL/Canvas]
**Learning:** While CSS media queries naturally handle CSS animations and transitions for users with `prefers-reduced-motion: reduce`, JavaScript-driven animations (like `requestAnimationFrame` loops for WebGL backgrounds or Canvas particles) bypass these CSS protections entirely. This can cause severe motion sickness for vulnerable users even when their OS settings request reduced motion.
**Action:** Always instantiate `window.matchMedia('(prefers-reduced-motion: reduce)')` and explicitly check `.matches` inside JavaScript animation loops to selectively pause or disable intensive custom rendering logic.

## 2026-03-25 - [Non-Blocking Error Feedback over Native Alerts]
**Learning:** Using native `alert()` for non-critical UI errors (like failed clipboard operations or missing browser APIs such as Geolocation) creates a disruptive, thread-blocking user experience that breaks immersion and can be visually discordant with custom dark-mode themes.
**Action:** Replace blocking `alert()` calls with temporary, inline visual feedback on the interacting element (e.g., swapping a button's innerHTML to a warning icon) combined with a screen reader announcement via an aria-live region (e.g., `announceA11y`).

## 2026-03-26 - [Visual Keyboard Shortcuts]
**Learning:** Relying solely on `aria-keyshortcuts` or `title` tooltips for keyboard shortcuts leaves the functionality undiscoverable to most users. Explicitly visualizing the shortcut using a `<span>` element bridges the gap between hidden accessibility attributes and actual user discoverability. Since the shortcut text is visually decorative and already announced by screen readers via `aria-keyshortcuts`, it should be marked with `aria-hidden="true"` to prevent redundant reading.
**Action:** Always complement `aria-keyshortcuts` with a visible `<span aria-hidden="true">` hint within the actionable element, dynamically rendering the correct OS shortcut (e.g. ⌘ vs Ctrl).

## 2026-03-28 - Native CSS Variable Inheritance in SVG via D3
**Learning:** When generating interactive SVG graphics dynamically using D3 or vanilla JS, using native CSS variables (e.g., `var(--success)`) within inline `.style()` or `.attr()` declarations perfectly inherits colors and supports native browser accessibility contrast without requiring manual evaluation via `getComputedStyle` or explicit theme-switch listeners.
**Action:** Always prefer setting `var(--theme-token)` instead of hardcoded hex colors for dynamically injected SVG inline styles/attributes to guarantee dark/light mode maintainability.

## 2026-03-30 - [Contextual Descriptions for Form Landmarks]
**Learning:** While `aria-labelledby` on `<form>` elements effectively creates named landmark regions, the contextual descriptions immediately following the headings (e.g., `<p class="panel-subtext">`) are skipped when screen reader users navigate directly by landmarks. This deprives users of critical context about what the tool actually does.
**Action:** Always complement `aria-labelledby` with `aria-describedby` pointing to the subtitle/subtext IDs to ensure screen reader users receive the full context of the tool when landing on the form landmark.

## 2026-04-01 - [Synchronize Native UI Chrome with Custom Dark Theme]
**Learning:** Even when a dark theme is implemented using CSS variables (like `--bg-obsidian`) for background and text colors, the browser's native UI chrome (e.g., scrollbars, default dropdown arrows, input backgrounds on some browsers, form validation popups, and the mobile browser top bar/status bar) remains blissfully unaware of the custom theme unless explicitly told. This can result in glaring white components contrasting jarringly against the dark layout, breaking immersion and sometimes presenting contrast issues.
**Action:** Always set `color-scheme: dark;` on the `:root` pseudo-class in your main stylesheet, and include a `<meta name="theme-color" content="[YOUR_BG_COLOR]">` tag in the `<head>` of your document. This explicitly informs the browser to style its native, unthemed elements and system chrome to match the custom dark theme.

## 2026-04-07 - [CSS Specificity Trap for Interactive Elements]
**Learning:** Hardcoding generic styles inline (`style="background: transparent; border: none;"`) on interactive elements like buttons creates a severe specificity trap (1000 vs 0012) that entirely overrides global interactive CSS pseudo-classes like `:hover`. This results in components feeling dead and unresponsive.
**Action:** Never use inline styles for interactive elements. Abstract common UI patterns into reusable CSS utility classes (e.g., `.text-btn`, `.icon-btn`) and apply those classes in HTML. This ensures pseudo-classes like `:hover` and `:active` can properly cascade and provide visual feedback.
