# ResumePilot AI — Feature Upgrades (Streamlit)

This folder contains ready-to-paste code for four new features:

| # | Feature | File to create |
|---|---------|---------------|
| 1 | 🌍 Multi-language resume support | `pages/4_🌍_Multi_Language_Resume.py` |
| 2 | 📊 Recruiter dashboard | `pages/5_📊_Recruiter_Dashboard.py` |
| 3 | 🎤 AI interview coach | `pages/6_🎤_AI_Interview_Coach.py` |
| 4 | 🧩 Chrome extension | folder `resumepilot-extension/` |

## How to integrate

1. **Multipage apps (recommended):** create a `pages/` folder next to `app.py` and drop files 1–3 in there. Streamlit adds them to the sidebar automatically.
2. **Single-file app:** open the code from each file and merge it into `app.py` (wrap each feature in a function or add tabs).
3. **Chrome extension:** create a folder `resumepilot-extension/`, add the 5 files from `04-chrome-extension.md`, load in Chrome via `chrome://extensions` → Developer mode → *Load unpacked*.
4. **Accept jobs from the extension:** add the query-param snippet from doc 04 to your Analyze page.

## Dependencies

Everything uses libraries you already have (`google-genai`, `pandas`, `plotly`, `python-docx`, `reportlab`). The Chrome extension needs no pip packages.

## Fix the existing deploy crash

Add to `requirements.txt`:
```txt
starlette==0.36.3
```

## Secrets

All Gemini features read `GOOGLE_API_KEY` from `.streamlit/secrets.toml`:
```toml
GOOGLE_API_KEY = "your-key-here"
```
