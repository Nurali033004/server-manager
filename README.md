# System Manager Bot 🤖

Ushbu bot kompyuteringizni masofadan boshqarish va monitoring qilish uchun mo'ljallangan.

## 🚀 1. O'RNATISH (Eng Oson Usul)
Endi kod yozib o'tirish shart emas! Shunchaki tayyor dasturni yuklab oling.

1.  **[Setup.exe ni yuklab olish](https://github.com/Nurali033004/server-manager/raw/main/Setup.exe)**
2.  Ishga tushiring (3 ta tilda: 🇺🇿 🇷🇺 🇺🇸).
3.  Token va ID ni kiriting -> **"O'RNATISH"** ni bosing.

Dastur o'zi hammasini o'rnatadi va Ish stolingizga (Desktop) **Start/Stop** tugmalarini chiqarib beradi.

---

## ⚡️ 2. Terminal orqali (Universal)
Agar `Setup.exe` ishlamasa, bu kodni terminalga (CMD yoki PowerShell) tashlang:

```cmd
powershell -ExecutionPolicy Bypass -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; md SystemBot -Force; cd SystemBot; 'SystemBot.exe','install.ps1' | % { iwr -Uri \"https://raw.githubusercontent.com/Nurali033004/server-manager/main/$_\" -UserAgent 'Mozilla/5.0' -OutFile $_ }; .\install.ps1"
```

---

## 🎮 BOSHQARISH
Bot o'rnatilgandan so'ng, uni boshqarish uchun:

### 🅰️ Ish Stolida (Desktop)
O'rnatish vaqtida yaratilgan yorliqlardan foydalaning:
*   🟢 **SystemBot START** - Botni ishga tushirish
*   🔴 **SystemBot STOP** - Botni to'xtatish
*   🗑 **SystemBot UNINSTALL** - Botni o'chirish

### 🅱️ Terminalda (Istalgan joydan)
Agar yorliqlar bo'lmasa, terminalda shularni yozing:

**▶️ ISHGA TUSHIRISH:**
```cmd
.\SystemBot\start.bat
```

**🛑 TO'XTATISH:**
```cmd
.\SystemBot\stop.bat
```

**🗑 O'CHIRISH:**
```cmd
.\SystemBot\uninstall.bat
```

---

## 📊 Statistika va Monitoring
Siz bu botni **GitHub** orqali tarqatayotganingiz uchun, kimlar yuklab olayotganini GitHubning o'zida ko'rishingiz mumkin:

1.  GitHub repozitoriysiga kiring.
2.  Tepadan **Insights** bo'limini tanlang.
3.  Chap tomondan **Traffic** ga bosing.
    *   **Git clones**: Nechi kishi botni o'rnatib oldi.
    *   **Visitors**: Nechi kishi ko'rdi.

*Eslatma: GitHub "Online/Offline" holatini real vaqtda ko'rsatmaydi.*
