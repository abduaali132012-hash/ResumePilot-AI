# Configure git credentials and push changes
Write-Host "Configuring git credentials for push..." -ForegroundColor Cyan
git config --global credential.helper manager-core

Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. When prompted for credentials:" -ForegroundColor White
Write-Host "   - Username: Your GitHub username" -ForegroundColor White
Write-Host "   - Password: Your Personal Access Token" -ForegroundColor White
Write-Host ""
Write-Host "2. Get a token at: https://github.com/settings/tokens/new" -ForegroundColor White
Write-Host "   Scope needed: 'repo'" -ForegroundColor White
Write-Host ""
Write-Host "3. Run: git push origin main" -ForegroundColor Cyan
Write-Host ""
Write-Host "Ready to push!" -ForegroundColor Green
