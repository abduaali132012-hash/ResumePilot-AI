# 🚀 ResumePilot AI — Deployment Guide

This guide walks you through deploying ResumePilot AI to **Streamlit Cloud** (the official Streamlit hosting platform).

---

## 📋 Prerequisites

- ✅ GitHub account (your repo is already there: `abduaali132012-hash/ResumePilot-AI`)
- ✅ Gemini API key (from https://aistudio.google.com/apikey)
- ✅ Local code pushed to GitHub (`main` branch)

---

## 🔑 Step 1: Push Your Code to GitHub

Your latest code changes need to be on GitHub for Streamlit Cloud to access them.

### Option A: Using the Push Script (Easiest)

```powershell
.\push-to-github.ps1
```

You'll be prompted for:
- **GitHub username:** Your GitHub account name (e.g., `abduaali132012-hash`)
- **Password:** Your Personal Access Token (not your GitHub password!)

#### Get a Personal Access Token:
1. Go to: https://github.com/settings/tokens/new
2. Click **"Generate new token (classic)"**
3. Configure:
   - **Token name:** `ResumePilot-Deploy`
   - **Expiration:** 90 days or longer
   - **Scopes:** Check ✅ `repo` (full control of private repositories)
4. Click **"Generate token"** and copy it
5. When the push script asks for a password, paste the token

### Option B: Manual Push with Git

```bash
git push origin main
```

If prompted for authentication, use your Personal Access Token as the password.

---

## 🌐 Step 2: Deploy to Streamlit Cloud

### 2.1 Sign In to Streamlit Cloud

1. Visit: https://share.streamlit.io
2. Click **"Sign in"** → **"GitHub"**
3. Authorize Streamlit to access your GitHub account

### 2.2 Create a New App

1. Click **"New app"** (or **"Create app"**)
2. Fill in:
   - **Repository:** `abduaali132012-hash/ResumePilot-AI`
   - **Branch:** `main`
   - **Main file path:** `app.py`
3. Click **"Deploy"**

Streamlit will now:
- Clone your repository
- Install dependencies from `requirements.txt`
- Start the app (URL: `https://resumepilot-ai-XXXXX.streamlit.app` or similar)

### 2.3 Configure Secrets (Gemini API Key)

**Important:** Without this step, your app will show "Gemini API key not found."

1. Your app will appear in Streamlit Cloud (status: "running" or "loading")
2. Click on your app name to open its dashboard
3. Click the **gear icon** (⚙️) in the top-right → **"Settings"**
4. Click **"Secrets"** in the left sidebar
5. Paste this into the text box:
   ```
   GOOGLE_API_KEY = "AIza..."
   ```
   Replace `AIza...` with your actual key from https://aistudio.google.com/apikey
6. Click **"Save"**
7. The app will auto-reboot with your secret loaded

### 2.4 Test Your Deployment

1. Wait for the app to reload (status changes to "running")
2. Click on the app URL or refresh the page
3. You should see ResumePilot AI with the Gemini error **gone**
4. Upload a resume (PDF, DOCX, or TXT) and paste a job description to test

---

## ✅ Verification Checklist

After deployment, verify:

- [ ] App loads without "Gemini API key not found" error
- [ ] Resume upload works (PDF/DOCX/TXT formats)
- [ ] Job description textarea accepts input
- [ ] AI features work (upload resume + JD → click evaluate)
- [ ] Evaluation produces results (no timeout or blank output)

---

## 🔧 Troubleshooting

### ❌ "Gemini API key not found" after deployment

**Cause:** Secret not configured in Streamlit Cloud.

**Fix:**
1. Go to your app dashboard on https://share.streamlit.io
2. Click the gear icon (⚙️) → **"Settings"** → **"Secrets"**
3. Add: `GOOGLE_API_KEY = "AIza..."`
4. Save and wait for auto-reboot

### ❌ App shows "something went wrong"

**Cause:** Dependency installation failed or syntax error in code.

**Fix:**
1. Check Streamlit Cloud logs (click app name → **"Logs"** tab)
2. Look for error messages
3. Common issues:
   - Missing dependency: add to `requirements.txt` and re-deploy
   - Python version incompatibility: check `.streamlit/config.toml`

### ❌ Can't push to GitHub (authentication error)

**Cause:** Invalid credentials or expired token.

**Fix:**
1. Generate a new Personal Access Token: https://github.com/settings/tokens/new
2. Scopes needed: ✅ `repo`
3. Use token as password when prompted by git

### ❌ App is slow or times out

**Cause:** Free tier Streamlit Cloud has resource limits.

**Solutions:**
- Optimize AI queries (use smaller batch sizes)
- Add request caching with `@st.cache_data`
- Upgrade to Streamlit Community Cloud paid tier (if needed)

### ❌ Free Gemini API quota exhausted (HTTP 429)

**Cause:** Hit 20 requests/day free tier limit.

**Fix:**
- Wait until tomorrow (quota resets daily at 12 AM UTC)
- Or upgrade Gemini API to paid: https://cloud.google.com/docs/setup-paid

---

## 📊 Monitoring Your Deployment

Once live, you can:

- **View logs:** App dashboard → **"Logs"** tab
- **Restart the app:** App dashboard → **"Settings"** → **"Reboot app"**
- **Update code:** Push to `main` branch → Streamlit auto-redeploys
- **Check resource usage:** App dashboard → **"Settings"** → view CPU/memory/storage

---

## 🔐 Security Best Practices

1. **Never commit secrets:** API keys, passwords, or tokens should NEVER be in GitHub
   - Use Streamlit Cloud Secrets (not environment variables in code)
   - `.streamlit/secrets.toml` is in `.gitignore` — keep it local-only

2. **Rotate API keys regularly:**
   - Generate new keys every 3-6 months
   - Delete old keys at https://aistudio.google.com/apikey

3. **Use strong GitHub tokens:**
   - Set expiration to 90 days or less
   - Revoke old tokens regularly
   - Use minimal scopes (`repo` only)

---

## 🎯 Next Steps After Deployment

1. ✅ Share the public link: `https://resumepilot-ai-XXXXX.streamlit.app`
2. ✅ Add to your portfolio / resume
3. ✅ Gather user feedback and iterate
4. ✅ Consider upgrading to paid Streamlit tier for better performance

---

## 📚 Additional Resources

- **Streamlit Cloud docs:** https://docs.streamlit.io/streamlit-cloud
- **Gemini API docs:** https://ai.google.dev/
- **GitHub Personal Access Tokens:** https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens

---

## ❓ Need Help?

- **Streamlit Issues:** https://github.com/streamlit/streamlit/issues
- **Gemini API Issues:** https://github.com/google-ai-edge/generative-ai-python/issues
- **ResumePilot Issues:** https://github.com/abduaali132012-hash/ResumePilot-AI/issues

Good luck! 🚀
