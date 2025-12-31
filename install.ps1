# =================================================================
#  System Manager Bot - Avtomatik O'rnatuvchi (EXE Versiya)
# =================================================================

$ErrorActionPreference = "Stop"

Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "     SYSTEM MANAGER BOT - O'RNATISH (SETUP) " -ForegroundColor Yellow
Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host ""

# 1. SystemBot.exe yuklab olish
$BotExeUrl = "https://github.com/Nurali033004/server-manager/raw/main/SystemBot.exe"
$BotExePath = "$PSScriptRoot\SystemBot.exe"

Write-Host "[1/4] Bot fayli yuklanmoqda..." -ForegroundColor Green
if (-not (Test-Path $BotExePath)) {
    try {
        Invoke-WebRequest -Uri $BotExeUrl -OutFile $BotExePath
        Write-Host "✅ Bot yuklandi!" -ForegroundColor Green
    } catch {
        Write-Host "❌ Xatolik: Bot faylini yuklab bo'lmadi. Internetni tekshiring yoki GitHubga EXE yuklanganligiga ishonch hosil qiling." -ForegroundColor Red
        exit
    }
} else {
    Write-Host "✅ Bot fayli mavjud." -ForegroundColor Green
}

# 2. Boshqaruv fayllarini yuklab olish (Start/Stop/Uninstall)
$BaseUrl = "https://raw.githubusercontent.com/Nurali033004/server-manager/main"
$Scripts = @("start.ps1", "stop.ps1", "uninstall.ps1", "start.bat", "stop.bat", "uninstall.bat")

Write-Host "[2/4] Yordamchi fayllar yuklanmoqda..." -ForegroundColor Green
foreach ($Script in $Scripts) {
    $ScriptPath = "$PSScriptRoot\$Script"
    if (-not (Test-Path $ScriptPath)) {
        try {
            Invoke-WebRequest -Uri "$BaseUrl/$Script" -OutFile $ScriptPath
            Write-Host "   + $Script yuklandi" -ForegroundColor Gray
        } catch {
            Write-Host "   - $Script yuklab bo'lmadi (muhim emas)" -ForegroundColor DarkGray
        }
    }
}

# 3. Cloudflared yuklab olish
$CloudflaredUrl = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
$CloudflaredPath = "$PSScriptRoot\cloudflared.exe"

Write-Host "[3/4] Cloudflared.exe tekshirilmoqda..." -ForegroundColor Green
if (-not (Test-Path $CloudflaredPath)) {
    Write-Host "⏳ Cloudflared yuklanmoqda... (Biroz kuting)" -ForegroundColor Yellow
    try {
        Invoke-WebRequest -Uri $CloudflaredUrl -OutFile $CloudflaredPath
        Write-Host "✅ Cloudflared yuklandi!" -ForegroundColor Green
    } catch {
        Write-Host "❌ Xatolik: Cloudflared yuklab bo'lmadi." -ForegroundColor Red
    }
} else {
    Write-Host "✅ Cloudflared mavjud." -ForegroundColor Green
}

# 4. Sozlamalar (.env)
Write-Host "[4/4] Sozlamalar (.env fayl)" -ForegroundColor Green
$EnvPath = "$PSScriptRoot\.env"

if (-not (Test-Path $EnvPath)) {
    Write-Host "Bot ma'lumotlarini kiriting:" -ForegroundColor Cyan
    
    $BotToken = Read-Host "🤖 Bot Tokenini kiriting (BotFather)"
    while (-not $BotToken) {
        $BotToken = Read-Host "❌ Token kiritilmadi. Qayta urinib ko'ring"
    }

    $AdminId = Read-Host "👤 Admin ID raqamini kiriting (Telegram ID)"
    while (-not $AdminId) {
        $AdminId = Read-Host "❌ ID kiritilmadi. Qayta urinib ko'ring"
    }

    $EnvContent = "BOT_TOKEN=$BotToken`nADMIN_ID=$AdminId"
    Set-Content -Path $EnvPath -Value $EnvContent
    Write-Host "✅ .env fayl yaratildi!" -ForegroundColor Green
} else {
    Write-Host "✅ .env fayl mavjud." -ForegroundColor Yellow
}

# Botni ishga tushirish
Write-Host ""
Write-Host "🎉 O'rnatish tugadi! Bot ishga tushirilmoqda..." -ForegroundColor Green
Start-Process -FilePath "$BotExePath" -WindowStyle Hidden
Write-Host "Bot orqa fonda ishga tushdi."
