# Project Documentation Rules (Non-Obvious Only)

- **Two separate apps share a repo**: `app.py`/`pages/` is the Streamlit app; `src/` is the React SPA. They are independent — the Streamlit app does NOT serve the React build.
- **`pages/` numbering is load order**: Streamlit loads `pages/` files in alphabetical/numeric order. Page numbers in filenames (e.g. `4_🌍_Multi_Language_Resume.py`) control sidebar order — gaps in numbering are intentional.
- **`ai.py` is NOT imported by `app.py`**: It's a standalone utility module. The Streamlit app has its own inline implementations of similar logic.
- **`src/lib/types.ts` is the canonical type reference**: All domain types (ATSResult, JobApplication, AnalysisMode, etc.) are defined there. Check it before adding new types.
- **Chrome extension is in `resumepilot-extension/`**: Plain JS, no build step. It injects job description text into a `?jd=` query param that `app.py` reads at startup via `st.query_params.get("jd")`.
- **`.b64` files in the root are binary assets encoded for git**: `ResumePilot_AI_Presentation.pptx.b64`, `README.pdf.b64`, etc. The decode script in `scripts/decode-files.mjs` outputs them to `public/` at dev/build time.
- **Streamlit theme** is dark by default (`base="dark"`) with custom primary color `#00C2FF`, configured in `.streamlit/config.toml`.
