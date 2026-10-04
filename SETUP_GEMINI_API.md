# 🔑 Gemini API Key Setup Guide

## Problem

Your ResumePilot AI app requires a **Gemini API key** to enable AI-powered resume evaluation features. Without it, the app shows an error and degrades to deterministic (non-AI) evaluation mode.

## Solution: 3 Setup Options

### Option 1: Local Development (Easiest)

For running the app locally on your machine:

1. **Get a free Gemini API key:**
   - Visit https://aistudio.google.com/apikey
   - Click "Create API key"
   - Copy the generated key (starts with `AIza...`)

2. **Add it to your local secrets file:**
   - Open `.streamlit/secrets.toml` in the repo root
   - Replace the placeholder with your actual key:
     ```toml
     GOOGLE_API_KEY = "AIza..."
     ```
   - **This file is already in `.gitignore` — it will NOT be committed to GitHub**

3. **Run the app:**
   ```bash
   streamlit run app.py
   ```

**Free tier limits:** 20 requests/day. [Enable billing](https://cloud.google.com/docs/setup-paid) for higher limits.

---

### Option 2: Streamlit Cloud Deployment

For deploying to https://streamlit.io (public or private app):

1. **Get a Gemini API key** (same as Option 1)

2. **Add it to Streamlit Cloud Secrets:**
   - Go to your app on Streamlit Cloud
   - Click **"Settings"** (gear icon, top right)
   - Click **"Secrets"**
   - Paste the key as:
     ```
     GOOGLE_API_KEY = "AIza..."
     ```
   - Click **"Save"**
   - The app will auto-reboot with your secret loaded

3. **Verify it works:**
   - Refresh your app
   - The error should disappear
   - You can now upload a resume and paste a job description

**Security note:** Streamlit Cloud encrypts and isolates secrets per app instance. Your key is never logged or exposed.

---

### Option 3: Environment Variable (CLI / Evaluation Suite)

For running the evaluation script or CLI tools:

```bash
# Set the environment variable (Linux/Mac)
export GOOGLE_API_KEY="AIza..."
python evaluation/run_evaluation.py

# Or (Windows PowerShell)
$env:GOOGLE_API_KEY = "AIza..."
python evaluation/run_evaluation.py

# Or inline (any OS)
GOOGLE_API_KEY="AIza..." python evaluation/run_evaluation.py
```

---

## What to Do If...

### ❌ "API key not found"
→ Follow **Option 1** or **Option 2** above.

### ❌ "Your Gemini API key was rejected"
→ Your key may have been revoked (e.g. after GitHub's secret scanning detected it).
- Generate a **new** key at https://aistudio.google.com/apikey
- Update it in Streamlit Cloud → Settings → Secrets (or `.streamlit/secrets.toml` locally)
- Reboot the app

### ❌ "HTTP 429" or "Quota exceeded"
→ You've hit the free tier limit (20 requests/day). Either:
- Wait until tomorrow
- [Enable billing](https://cloud.google.com/docs/setup-paid) for higher limits

### ✅ Key accepted, but deterministic mode is running
→ The key is valid, but the AI features are optional. You can still use ResumePilot with the built-in deterministic evaluator.

---

## Key Resolution Order (How ResumePilot Finds Your Key)

ResumePilot checks for your key in this order:

1. **Streamlit Cloud Secrets** (`st.secrets["GOOGLE_API_KEY"]` or `st.secrets["GEMINI_API_KEY"]`)
2. **Environment variables** (`GOOGLE_API_KEY` or `GEMINI_API_KEY`)
3. **Local secrets file** (`.streamlit/secrets.toml`)

This means you can:
- Use different keys for different environments (local dev ≠ production)
- Keep your key out of source control (✅ `.streamlit/secrets.toml` is in `.gitignore`)
- Share the app code publicly without exposing your key

---

## FAQ

**Q: Is it safe to commit my API key?**  
A: **Never.** Always keep it in secrets management (Streamlit Cloud, `.streamlit/secrets.toml`, or env vars). GitHub's secret scanning will detect committed keys and revoke them automatically.

**Q: Can I use a different API than Gemini?**  
A: Currently, ResumePilot uses Google's Gemini. You could extend it to support other models by modifying `ai/inference/gemini_client.py`.

**Q: What's the free tier limit?**  
A: **20 requests per day.** This is enough for a few evaluations per day. [Upgrade to paid](https://cloud.google.com/docs/setup-paid) for unlimited (pay-as-you-go).

**Q: Can I use one key for multiple environments?**  
A: Yes. A single Gemini API key works everywhere. But you can also generate separate keys for different projects if you prefer isolation.

**Q: Where do I find my key after generating it?**  
A: Go to https://aistudio.google.com/apikey and it will show all your keys. You can regenerate or delete old ones there.

---

## Next Steps

1. ✅ Generate your key: https://aistudio.google.com/apikey
2. ✅ Add it locally or to Streamlit Cloud (choose Option 1 or 2 above)
3. ✅ Restart the app
4. ✅ Upload a resume and paste a job description to test it

Happy optimizing! 🚀
