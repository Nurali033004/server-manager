$ErrorActionPreference = "SilentlyContinue"
Write-Host "⚠️ DIQQAT: Bot va uning barcha fayllari o'chirilmoqda..." -ForegroundColor Red

# 1. Jarayonlarni to'xtatish
Write-Host "[1/3] Bot to'xtatilmoqda..." -ForegroundColor Yellow
Stop-Process -Name "SystemBot" -Force
Stop-Process -Name "cloudflared" -Force

# 2. Papkadan chiqish (agar ichida bo'lsa)
$CurrentLocation = Get-Location
if ($CurrentLocation.Path -like "*\SystemBot") {
    Set-Location ..
}

# 3. Papkani o'chirish oldidan so'rash
$BackupPath = "$HOME\Desktop\SystemBot_Backup_$(Get-Date -Format 'yyyyMMdd_HHmm')"

Write-Host "❓ Mijoz fayllarini (yuklangan kodlar, rasmlar) saqlab qolaymi?" -ForegroundColor Cyan
$Response = Read-Host "   (y = Ha, saqlansin / n = Yo'q, hammasi o'chirilsin)"

if ($Response -eq "y" -or $Response -eq "Y") {
    Write-Host "📂 Fayllar nusxalanmoqda..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $BackupPath -Force | Out-Null
    Copy-Item -Path "SystemBot\*" -Destination $BackupPath -Recurse -Force
    Write-Host "✅ Fayllar mana bu yerga saqlandi: $BackupPath" -ForegroundColor Green
    Start-Sleep -Seconds 2
}

Write-Host "[2/3] Asosiy papka o'chirilmoqda..." -ForegroundColor Yellow
Start-Sleep -Seconds 2

if (Test-Path "SystemBot") {
    Remove-Item -Path "SystemBot" -Recurse -Force
    Write-Host "✅ SystemBot papkasi o'chirildi." -ForegroundColor Green
} else {
    Write-Host "ℹ️ SystemBot papkasi topilmadi (ehtimol allaqachon o'chirilgan)." -ForegroundColor Gray
}

Write-Host ""
Write-Host "[3/3] ✅ TOZALASH YAKUNLANDI!" -ForegroundColor Green
Write-Host "Bot va uning ma'lumotlari kompyuterdan butunlay o'chirib tashlandi."
