# Project Architecture Rules (Non-Obvious Only)

- **Dual-stack, not monorepo**: The React SPA (`src/`) and Streamlit app (`app.py`) are completely independent — no shared build output, no shared runtime. Changes to one do not affect the other.
- **Streamlit app is stateless across browser sessions**: All analysis data lives in `st.session_state` (in-memory, per-tab). Export/Import JSON is the only persistence mechanism for version history and applications — no database on the Python side.
- **React app uses Supabase for all persistence**: Auth (`src/lib/store.tsx`), saved analyses, and job applications route through Supabase. The anon key in `src/lib/supabase.ts` is the only credential needed for the client.
- **React routing is client-side only**: `BrowserRouter` with all routes defined in `src/App.tsx`. All pages are lazy-loaded (`React.lazy`). The catch-all `path="*"` redirects to `LandingPage` — no 404 page.
- **`AuthProvider` wraps the entire React tree**: `useAuth()` throws if called outside `AuthProvider`. The provider is in `src/lib/store.tsx` and is the single source of auth truth.
- **Gemini is the only LLM used in production**: `gemini-2.5-flash` via `google-genai` SDK. There is no abstraction layer — all prompts are inline strings in `app.py`.
- **ATS score has a hidden +40 boost for display**: `calculate_score(resume, job1, boost=40)` is used for the displayed score; raw `calculate_score(resume, job1)` (no boost) is used for multi-job comparisons. This asymmetry is intentional.
- **Streamlit Multipage App page files must use `st.set_page_config` only in `app.py`** — calling it in a `pages/` file would break navigation.
