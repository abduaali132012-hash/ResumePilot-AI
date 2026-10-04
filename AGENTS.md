# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Project Structure

Dual-stack project: a **React/TypeScript SPA** (Vite, Tailwind v4) and a **Python/Streamlit** multi-page app. Both target the same product but are independent entry points.

- `app.py` + `pages/` — Streamlit app (main entry is `app.py`, `st.set_page_config` must be the FIRST Streamlit call)
- `src/` — React SPA entry point (`src/main.tsx`), pages in `src/pages/`, shared UI in `src/components/ui.tsx`
- `ai.py` — standalone Python AI helpers (no Streamlit dependency)
- `resumepilot-extension/` — Chrome extension (vanilla JS, no build step)

## Commands

### React/TypeScript (Vite)
```
npm run dev       # runs scripts/decode-files.mjs first, then vite optimize && vite
npm run build     # also runs decode-files.mjs first
```
> `predev`/`prebuild` hooks decode `*.b64` files in the repo root into `public/`. This step is **required** — skipping it means `public/` assets will be missing.

No lint or typecheck script in `package.json`. Run TypeScript checks manually:
```
npx tsc --noEmit
```

### Python / Streamlit
```
streamlit run app.py          # main app
pytest test_app.py -v         # all tests
pytest test_app.py::test_score_partial_match -v   # single test
```
Tests in `test_app.py` import directly from `app.py` — they require no API keys and no Streamlit runtime.

## Critical Gotchas

- **Supabase credentials are hardcoded** in [`src/lib/supabase.ts`](src/lib/supabase.ts) (anon key + project URL). Do not rotate without updating that file.
- **Gemini API key** is read from `st.secrets["GEMINI_API_KEY"]` (Streamlit Cloud) or `.streamlit/secrets.toml` locally. The secrets file is `.gitignored` — never commit it.
- **`generate_with_retry()`** in `app.py` deliberately does NOT retry HTTP 429 daily-quota errors — only transient failures. This distinction is intentional.
- **Auto-analyze** in `app.py` uses a SHA-256 hash of `resume+job1` to debounce API calls across Streamlit reruns, preventing redundant quota usage.
- **Vite HMR is disabled** (`hmr: false` in `vite.config.ts`) — changes require a manual browser refresh in dev.
- **SVG imports** must use the `?react` suffix (e.g. `import { ReactComponent } from './icon.svg?react'`). The `?import&react` alias in `vite.config.ts` is a custom shim.

## TypeScript Style (React SPA)

- Strict mode enabled: `noUnusedLocals`, `noUnusedParameters`, `erasableSyntaxOnly`
- All type-only imports use `import type { … }` syntax
- All shared UI primitives live in **`src/components/ui.tsx`** — extend that file rather than creating new component files for Button, Card, Input, TextArea, Badge, Tabs, Spinner, EmptyState
- Design tokens (colors, fonts) are defined in **`src/index.css`** under `@theme { }` using `oklch()` — do not hardcode hex/rgb colors; use CSS custom properties (`var(--color-primary)` etc.)
- Tailwind v4 is used via `@import "tailwindcss"` — no `tailwind.config.js` exists; config is in CSS
- Custom utility classes defined in `src/index.css`: `.glass`, `.glass-strong`, `.gradient-text`, `.focus-ring`, `.scrollbar-thin`, `.animate-scoreFill`, `.animate-fadeSlideUp`

## Python Style

- All shared types use `Dict`, `List`, `Any` from `typing` (Python 3.9 compatible)
- Section parsing from Gemini responses uses `extract_section(text, header, next_header)` from `app.py` — use this helper rather than inline string splits
- Gemini model is pinned to `"gemini-2.5-flash"` in `app.py`

## SpecCheck (IBM Bob 2.0 Hackathon)
SpecCheck is a set of IBM Bob custom modes that answer one question:
"Does the code actually do what the requirements say?"
It reads a requirements document, finds the code that implements each
requirement, verifies each one strictly, writes the missing tests, and produces
a traceability report with a coverage score. ResumePilot is the demo target;
the requirements document is `speccheck/PRD.md`.

Workflow (one mode per step):
1. Spec Reader       -> speccheck/reports/01_requirements.md
2. Evidence Finder   -> speccheck/reports/02_evidence.md
3. Strict Verifier   -> speccheck/reports/03_verdicts.md
4. Test Writer       -> tests/speccheck/ + speccheck/reports/04_tests.md
5. Trace Reporter    -> speccheck/reports/05_TRACE_REPORT.md

Rules for all SpecCheck work:
- Work only on branch `speccheck`. Never modify `main`.
- Never mark a requirement as met without file:line evidence.
- Never invent numbers. Every metric must come from a real command run.
- Tests must run offline. Do not set or require GOOGLE_API_KEY; use the
  deterministic fallback.
- Do not change application code unless explicitly asked. SpecCheck reports
  gaps; it does not silently "fix" the product.
- Keep the existing app runnable (`streamlit run app.py`).
- Never modify or commit `.venv/`.
- Coverage score = (requirements that are Implemented AND Tested) / (total
  requirements) x 100, rounded to one decimal.