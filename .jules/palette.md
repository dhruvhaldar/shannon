## 2024-05-23 - [Dashboard Skip Link Pattern]
**Learning:** The main dashboard container was a generic `div`, preventing semantic navigation and skip link targeting. Using `<main id="main-content" tabindex="-1">` provided a robust target for keyboard users without disrupting the visual layout.
**Action:** Always check semantic landmarks when implementing skip links in existing layouts.

## 2024-05-23 - [Global Focus Visibility]
**Learning:** The application relied entirely on browser default focus rings, which were often invisible against the white background. Implementing a high-contrast `*:focus-visible` style with `outline-offset` ensured visibility without cluttering the UI for mouse users.
**Action:** Verify focus visibility on all interactive elements, especially custom inputs and buttons.
