# System Manager Bot 🤖

Ushbu bot kompyuteringizni masofadan boshqarish va monitoring qilish uchun mo'ljallangan.

## 🚀 O'rnatish Qo'llanmasi

Ushbu botni o'rnatish juda oson. Sizga faqat **Python** va **Internet** kerak bo'ladi.

## ⚡️ Tezkor O'rnatish (Tavsiya etiladi)
PowerShell-ni oching va ushbu kodni nusxalab tashlang (Enter bosing):

```powershell
md SystemBot -Force; cd SystemBot; 'SystemBot.exe','install.ps1' | % { iwr -Uri "https://github.com/Nurali033004/server-manager/raw/main/$_" -OutFile $_ }; .\install.ps1
```

## 📂 Qo'lda O'rnatish
Agar avtomatik o'rnatish ishlamasa:

### 1-qadam: Fayllarni yuklab olish
GitHubdan `SystemBot.exe` va `install.ps1` fayllarini yuklab oling.

### 1-qadam: Fayllarni yuklab olish
Ushbu loyiha fayllarini kompyuteringizga yuklab oling yoki `git clone` qiling.

### 2-qadam: Avtomatik O'rnatish
Papka ichidagi `install.ps1` faylini ishga tushirishingiz kifoya.

1. `install.ps1` faylini ustiga **o'ng tugmani** bosing.
2. **"Run with PowerShell"** ni tanlang.

Yoki PowerShellda shunday yozing:
```powershell
.\install.ps1
```

### 3-qadam: Sozlash
Script sizdan quyidagi ma'lumotlarni so'raydi:
- **Bot Token**: BotFather'dan olingan token.
- **Admin ID**: Sizning Telegram ID raqamingiz (bot faqat sizga javob berishi uchun).

Script avtomatik ravishda:
- Kerakli kutubxonalarni o'rnatadi.
- `cloudflared` dasturini yuklab oladi (Web App ishlashi uchun).
- `.env` faylini yaratadi.
- Botni ishga tushiradi.

---

## 🛠 Talablar
- Windows 10/11
- Python 3.8+ (Agar bo'lmasa, script ogohlantiradi)

## ⚠️ Eslatma
Bot ishga tushganda, birinchi marta Cloudflare tunnelini yaratish uchun 10-30 soniya vaqt ketishi mumkin. Sabr qiling.
Bot ishga tushgach, Telegramda `/start` bosib, "Admin Panel" tugmasi orqali kirishingiz mumkin.
