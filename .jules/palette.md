## 2024-05-23 - [Dashboard Skip Link Pattern]
**Learning:** The main dashboard container was a generic `div`, preventing semantic navigation and skip link targeting. Using `<main id="main-content" tabindex="-1">` provided a robust target for keyboard users without disrupting the visual layout.
**Action:** Always check semantic landmarks when implementing skip links in existing layouts.

## 2024-05-23 - [Global Focus Visibility]
**Learning:** The application relied entirely on browser default focus rings, which were often invisible against the white background. Implementing a high-contrast `*:focus-visible` style with `outline-offset` ensured visibility without cluttering the UI for mouse users.
**Action:** Verify focus visibility on all interactive elements, especially custom inputs and buttons.

## 2024-06-13 - [HTML5 Validation Baseline]
**Learning:** The application relied solely on backend validation, resulting in generic error messages for simple issues like missing fields. Adding HTML5 validation attributes (`required`, `min`, `step`) provided immediate, accessible feedback without custom JS logic.
**Action:** Always baseline forms with HTML5 validation attributes before relying on backend validation feedback.

## 2026-02-20 - [Smart TLE Paste]
**Learning:** Users frequently work with structured multi-line text (TLEs) that map to multiple inputs. Forcing manual copy-paste per field breaks flow. Intercepting the `paste` event to intelligently parse and distribute content provides a "delightful" efficiency boost without cluttering the UI with extra buttons.
**Action:** For multi-part data often copied as a block, consider "smart paste" logic on individual inputs to auto-fill related fields.

## 2026-02-21 - [Hidden Affordances]
**Learning:** Smart interaction patterns like paste-handling are invisible without cues. Adding a simple helper text ("Paste a full TLE set...") immediately bridges the gap between feature existence and user discovery, while `aria-describedby` ensures screen reader users also benefit from the context.
**Action:** Always pair hidden "power user" interactions with visible, accessible hints.

## 2026-02-21 - [Visual Feedback for Auto-fill Actions]
**Learning:** When actions like "Smart Paste" or "Use My Location" auto-fill multiple fields, users may miss the change. Adding a simple transient visual cue (e.g., green flash) to the affected inputs provides immediate confirmation and builds trust in the automation.
**Action:** Extract and reuse the `highlightInputs` pattern for any multi-field auto-fill interaction.

## 2026-02-23 - [Auto-Fill State Management]
**Learning:** The `highlightInputs` function failed when triggered rapidly because it captured the *current* state (which was already modified) instead of the true original state, leading to a "stuck" highlight color. This is a common pitfall in transient UI feedback.
**Action:** When implementing temporary state changes (like success flashes), always check for existing state metadata (e.g., `dataset`) before capturing, or store the original state permanently on initialization.

## 2026-02-23 - [Complex Form Presets]
**Learning:** Forms with >5 engineering inputs (like Link Budgets) create significant friction for exploratory testing. Users often need "standard scenarios" to start from. Adding a simple `<select>` preset loader transformed a data-entry task into a rapid exploration tool without cluttering the UI.
**Action:** Identify forms with high input density and implement "Load Scenario" presets for common use cases.

## 2026-03-01 - [Data Portability]
**Learning:** For calculation tools where the output is critical for further reporting, users often struggle to extract formatted data. Adding a simple "Copy Result" button next to the output block bridges the gap between the tool and the user's workflow without cluttering the UI with export features.
**Action:** Identify read-only output blocks and implement clipboard copy functionality for user convenience.
