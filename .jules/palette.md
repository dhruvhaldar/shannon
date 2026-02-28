## 2026-02-28 - [Visual Cues for Initial State]
**Learning:** Result panels appeared completely blank or as empty bordered containers on initial load, leaving users without guidance on what those areas are for. Furthermore, disabled buttons lacked visual styling, leading to confusion during loading states.
**Action:** Add helpful empty states with icons and descriptive text to result containers before data is fetched. Ensure `button:disabled` states are explicitly styled in CSS with appropriate opacity and cursor changes.
