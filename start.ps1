$ErrorActionPreference = "SilentlyContinue"
$BotPath = "$PSScriptRoot\SystemBot.exe"

if (Test-Path $BotPath) {
    Start-Process -FilePath $BotPath -WindowStyle Hidden
    Write-Host "✅ Bot orqa fonda ishga tushirildi!" -ForegroundColor Green
} else {
    Write-Host "❌ SystemBot.exe topilmadi." -ForegroundColor Red
}
