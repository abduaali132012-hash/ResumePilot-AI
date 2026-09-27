# Project Coding Rules (Non-Obvious Only)

- **One UI file rule**: All React UI primitives (Button, Card, Input, TextArea, Badge, Tabs, Spinner, EmptyState) live exclusively in `src/components/ui.tsx`. Add new primitives there, not in new files.
- **Design tokens are CSS-only**: Colors and fonts are declared in `src/index.css` under `@theme {}` using `oklch()`. Never use hex/rgb in component JSX or new CSS. Always use `var(--color-*)` or Tailwind's semantic classes (`text-primary`, `bg-background`, etc.).
- **Tailwind v4 — no config file**: Configuration is entirely inside `src/index.css`. There is no `tailwind.config.js` or `tailwind.config.ts`.
- **SVG import pattern**: Use `import { ReactComponent as Icon } from './file.svg?react'` — the `?import&react` alias in `vite.config.ts` is just a shim for that.
- **`predev`/`prebuild` hooks are mandatory**: `scripts/decode-files.mjs` decodes `*.b64` files into `public/`. If you bypass npm scripts (e.g. running `vite` directly), `public/` assets will be absent.
- **No test runner for the React app**: There are no Vitest/Jest configs. The only test suite is `test_app.py` (pytest) for the Python side.
- **Gemini retry logic boundary**: `generate_with_retry()` in `app.py` skips retries for daily quota 429s — do not change this behavior when modifying error handling.
- **Session state debouncing**: The auto-analyze feature compares `hashlib.sha256(resume+job1)` against `last_analyzed_hash` to avoid burning API quota on every Streamlit rerun. Preserve this pattern when adding new analysis triggers.
- **`st.set_page_config` must stay as the absolute first Streamlit call in `app.py`** — moving it below any other `st.*` call crashes the app.
- **Supabase auth uses implicit flow** (`flowType: "implicit"` in `src/lib/supabase.ts`) — session is stored in URL hash on redirect, not PKCE.
