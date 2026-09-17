# Setup Guide - ResumePilot AI

## Prerequisites

- **Python**: 3.8 or higher
- **pip**: Python package manager
- **Git**: For version control
- **Google Account**: To get free Gemini API key

---

## Step-by-Step Installation

### 1. Clone the Repository

```bash
git clone https://github.com/abduaali132012-hash/ResumePilot-AI.git
cd ResumePilot-AI
```

### 2. Create Virtual Environment

**On macOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**On Windows (Command Prompt):**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**On Windows (PowerShell):**
```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Upgrade pip

```bash
pip install --upgrade pip
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Get Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com)
2. Click on "Get API Key"
3. Click "Create API key in new project"
4. Copy your API key

### 6. Configure Environment Variables

```bash
# Copy the example file
cp .env.example .env

# Edit .env and paste your API key
# On macOS/Linux:
nano .env

# On Windows:
notepad .env
```

Add your Gemini API key:
```
GEMINI_API_KEY=your_api_key_here
```

Save and close the file.

### 7. Run the Application

```bash
streamlit run app.py
```

The app will open at: **http://localhost:8501**

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'streamlit'"

**Solution**: Make sure your virtual environment is activated and dependencies are installed.
```bash
source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

### Issue: "API Key Invalid" or "Quota Exceeded"

**Solution**: 
- Verify your API key is correct in `.env` file
- Check that you've copied the entire key
- Ensure your Google account is verified and in good standing
- Free tier allows 20 requests per day; wait until the next day or upgrade

### Issue: "Port 8501 is already in use"

**Solution**: Use a different port
```bash
streamlit run app.py --server.port 8502
```

### Issue: PDF upload not working

**Solution**: Ensure file is a valid PDF with readable text. Try converting to PDF from another format.

### Issue: Application runs but pages are blank

**Solution**: Check your browser console for errors. Try:
```bash
streamlit run app.py --logger.level=debug
```

---

## Configuration

### Streamlit Settings

Edit or create `.streamlit/config.toml`:

```toml
[client]
showErrorDetails = true

[logger]
level = "info"

[server]
port = 8501
headless = false
```

---

## Development

### Running Tests

```bash
python test_app.py
```

### Project Structure

```
ResumePilot-AI/
├── app.py                    # Main application
├── ai.py                     # Core AI module
├── pages/                    # Streamlit pages
│   ├── 4_🌍_Multi_Language_Resume.py
│   ├── 5_📊_Recruiter_Dashboard.py
│   └── 6_🎤_AI_Interview_Coach.py
├── requirements.txt          # Dependencies
├── .env.example              # Environment template
├── .streamlit/config.toml    # Streamlit config
└── README.md                 # Documentation
```

### Code Style

- Follow PEP 8 guidelines
- Use type hints for functions
- Add docstrings to functions and classes
- Keep functions focused and small

---

## Deployment

### Local Testing (Recommended for HackerEarth)

```bash
# Ensure virtual environment is activated
source .venv/bin/activate

# Run the app
streamlit run app.py
```

### Streamlit Cloud Deployment (Optional)

1. Push to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Add secrets in Streamlit Cloud:
   - `GEMINI_API_KEY`: Your API key

### Docker Deployment (Optional)

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["streamlit", "run", "app.py"]
```

Build and run:
```bash
docker build -t resumepilot-ai .
docker run -p 8501:8501 -e GEMINI_API_KEY=your_key resumepilot-ai
```

---

## Testing the Application

### 1. Resume Upload Test

- Go to the main app
- Upload a sample resume (PDF, DOCX, or TXT)
- Paste a job description
- Click "Analyze Resume"
- Verify ATS score appears

### 2. AI Module Test

```python
from ai import calculate_ats_score, find_skill_gaps

resume = "Python, AWS, Docker, Kubernetes"
job = "Python, AWS, Docker, Kubernetes, Jenkins"

score = calculate_ats_score(resume, job)
print(f"ATS Score: {score['score']}%")

gaps = find_skill_gaps(resume, job)
print(f"Missing Skills: {gaps['critical_gaps']}")
```

### 3. Feature Test Checklist

- [ ] Resume upload works (PDF, DOCX, TXT)
- [ ] Job description parsing works
- [ ] ATS score displays
- [ ] Skill gaps are identified
- [ ] AI generation works (requires API key)
- [ ] Cover letter generation works
- [ ] Interview tips display
- [ ] Version history saves
- [ ] Application tracker works
- [ ] All pages load without errors

---

## Performance Optimization

### For Better Performance:
1. Use SSDs for faster file I/O
2. Allocate sufficient RAM (minimum 2GB)
3. Keep browser updated for better rendering
4. Close unnecessary background applications

### Caching:
Streamlit automatically caches:
- `@st.cache_data` for data transformations
- `@st.cache_resource` for global resources

---

## Security Best Practices

1. **Never commit `.env` file** to version control
2. **Rotate API keys** regularly
3. **Use strong credentials** for any accounts
4. **Keep dependencies updated**: `pip install --upgrade -r requirements.txt`
5. **Review third-party packages** before installing

---

## Getting Help

### Documentation
- Streamlit Docs: https://docs.streamlit.io
- Google Gemini API: https://ai.google.dev/docs
- Python Official: https://www.python.org/doc

### GitHub Issues
Open an issue at: https://github.com/abduaali132012-hash/ResumePilot-AI/issues

### Common Questions

**Q: How do I update dependencies?**
```bash
pip install --upgrade -r requirements.txt
```

**Q: Can I use this offline?**
```
No, AI features require internet connection for Gemini API.
Local analysis via ai.py module works offline.
```

**Q: Does this store my resume?**
```
No, data is only kept in your session. 
No data is saved to external servers.
```

---

## Version Information

- **Python**: 3.8+
- **Streamlit**: 1.58.0
- **Google Gemini AI**: Latest
- **Last Updated**: 2026-08-31

---

**Setup is complete! 🎉**

Run `streamlit run app.py` to start the application.
