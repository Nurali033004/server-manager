$ErrorActionPreference = "SilentlyContinue"

Stop-Process -Name "SystemBot" -Force
Stop-Process -Name "cloudflared" -Force

Write-Host "🛑 Bot muvaffaqiyatli to'xtatildi!" -ForegroundColor Red
