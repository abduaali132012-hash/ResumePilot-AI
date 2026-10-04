# ResumePilot AI — Push to GitHub Script
# ======================================
# This script pushes your local changes to GitHub for deployment to Streamlit Cloud.
#
# Usage: .\push-to-github.ps1
# You will be prompted for your GitHub credentials.

Write-Host "🚀 ResumePilot AI — Pushing to GitHub" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Check if there are commits to push
$unpushedCommits = git log origin/main..main --oneline 2>$null
if (-not $unpushedCommits) {
    Write-Host "✅ No new commits to push (already in sync with GitHub)" -ForegroundColor Green
    exit 0
}

Write-Host "📋 Commits to push:" -ForegroundColor Yellow
$unpushedCommits | ForEach-Object { Write-Host "   $_" }
Write-Host ""

# Attempt to push
Write-Host "🔄 Pushing to origin/main..." -ForegroundColor Cyan
git push origin main

# Check if push succeeded
if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Push successful!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📌 Next steps for Streamlit Cloud deployment:" -ForegroundColor Green
    Write-Host "   1. Visit: https://share.streamlit.io" -ForegroundColor White
    Write-Host "   2. Sign in with your GitHub account" -ForegroundColor White
    Write-Host "   3. Click 'New app' → Select this repo → Select 'app.py'" -ForegroundColor White
    Write-Host "   4. Configure Secrets:" -ForegroundColor White
    Write-Host "      - In the app settings, go to 'Secrets'" -ForegroundColor White
    Write-Host "      - Add: GOOGLE_API_KEY = 'AIza...'" -ForegroundColor White
    Write-Host "   5. Click 'Deploy'" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "❌ Push failed. Check your credentials and try again." -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 Troubleshooting:" -ForegroundColor Yellow
    Write-Host "   • Did you paste your Personal Access Token as the password?" -ForegroundColor White
    Write-Host "   • Generate a new token at: https://github.com/settings/tokens/new" -ForegroundColor White
    Write-Host "   • Scope required: 'repo' (full control of private repositories)" -ForegroundColor White
    Write-Host ""
    exit 1
}
