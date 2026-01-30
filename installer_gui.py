import tkinter as tk
from tkinter import messagebox, ttk
import os
import sys
import threading
import urllib.request
import subprocess
import winshell
from win32com.client import Dispatch
import pythoncom
import psutil

# Config
REPO_URL = "https://raw.githubusercontent.com/Nurali033004/server-manager/main"
FILES_TO_DOWNLOAD = [
    ("SystemBot.exe", f"{REPO_URL}/SystemBot.exe"),
    ("SystemManager.exe", f"{REPO_URL}/SystemManager.exe"),
    ("CloudIDEServer.exe", f"{REPO_URL}/CloudIDEServer.exe"),
    ("assets/ide_index.html", f"{REPO_URL}/assets/ide_index.html"),
    ("start.bat", f"{REPO_URL}/start.bat"),
    ("stop.bat", f"{REPO_URL}/stop.bat"),
    ("uninstall.bat", f"{REPO_URL}/uninstall.bat"),
    ("start.ps1", f"{REPO_URL}/start.ps1"),
    ("stop.ps1", f"{REPO_URL}/stop.ps1"),
    ("uninstall.ps1", f"{REPO_URL}/uninstall.ps1"),
]
CLOUDFLARED_URL = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"

LANGUAGES = {
    "O'zbekcha 🇺🇿": {
        "header": "SystemManager O'rnatish",
        "token": "Bot Token (BotFather):",
        "admin_id": "Admin ID (Telegram):",
        "install": "O'RNATISH",
        "creating_dir": "Tayyorgarlik...",
        "downloading": "Yuklanmoqda: {name}...",
        "settings": "Sozlanmoqda...",
        "shortcuts": "Yuzaga chiqarilmoqda...",
        "starting": "Ishga tushirilmoqda...",
        "success_title": "Tayyor",
        "success_msg": "Ilova muvaffaqiyatli o'rnatildi!",
        "error_title": "Xato",
        "error_msg": "O'rnatishda xatolik: {error}",
        "warning_title": "Diqqat",
        "warning_msg": "Ma'lumotlarni to'liq kiriting!",
        "ready": "Tayyor"
    },
    "Русский 🇷🇺": {
        "header": "Установка SystemManager",
        "token": "Токен бота (BotFather):",
        "admin_id": "Админ ID (Telegram):",
        "install": "УСТАНОВИТЬ",
        "creating_dir": "Подготовка...",
        "downloading": "Загрузка: {name}...",
        "settings": "Настройка...",
        "shortcuts": "Создание ярлыков...",
        "starting": "Запуск...",
        "success_title": "Готово",
        "success_msg": "Приложение успешно установлено!",
        "error_title": "Ошибка",
        "error_msg": "Ошибка при установке: {error}",
        "warning_title": "Внимание",
        "warning_msg": "Пожалуйста, введите Токен и ID!",
        "ready": "Готов"
    },
    "English 🇺🇸": {
        "header": "SystemManager Setup",
        "token": "Bot Token (BotFather):",
        "admin_id": "Admin ID (Telegram):",
        "install": "INSTALL",
        "creating_dir": "Preparing...",
        "downloading": "Downloading: {name}...",
        "settings": "Saving settings...",
        "shortcuts": "Creating shortcuts...",
        "starting": "Launching...",
        "success_title": "Success",
        "success_msg": "Installation complete!",
        "error_title": "Error",
        "error_msg": "An error occurred: {error}",
        "warning_title": "Warning",
        "warning_msg": "Please enter Token and ID!",
        "ready": "Ready"
    }
}

current_lang = "O'zbekcha 🇺🇿"

def get_install_dir():
    return os.path.join(os.path.expanduser("~"), "SystemBot")

def create_shortcut(target, name, icon=None):
    try:
        pythoncom.CoInitialize()
        desktop = winshell.desktop()
        path = os.path.join(desktop, f"{name}.lnk")
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(path)
        shortcut.Targetpath = target
        shortcut.WorkingDirectory = os.path.dirname(target)
        if icon and os.path.exists(icon):
            shortcut.IconLocation = icon
        shortcut.save()
    except Exception as e:
        print(f"Shortcut error: {e}")

def install_logic(token, admin_id, progress_var, status_label, root):
    pythoncom.CoInitialize()
    global current_lang
    txt = LANGUAGES[current_lang]
    install_dir = get_install_dir()
    
    try:
        if not os.path.exists(install_dir):
            os.makedirs(install_dir)
        
        # Kill running processes to allow overwriting
        status_label.config(text="Eski jarayonlar to'xtatilmoqda...")
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] in ['SystemManager.exe', 'SystemTray.exe', 'SystemBot.exe', 'CloudIDEServer.exe']:
                try: proc.kill()
                except: pass
        import time
        time.sleep(1) # Wait for release
            
        # Download files
        for i, (name, url) in enumerate(FILES_TO_DOWNLOAD):
            status_label.config(text=txt["downloading"].format(name=name))
            dest_path = os.path.join(install_dir, name)
            dest_dir = os.path.dirname(dest_path)
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)
            urllib.request.urlretrieve(url, dest_path)
            progress_var.set(10 + (i * 10))
            root.update_idletasks()

        # Cloudflared
        status_label.config(text=txt["downloading"].format(name="cloudflared"))
        urllib.request.urlretrieve(CLOUDFLARED_URL, os.path.join(install_dir, "cloudflared.exe"))
        progress_var.set(70)

        # .env
        status_label.config(text=txt["settings"])
        with open(os.path.join(install_dir, ".env"), "w") as f:
            f.write(f"BOT_TOKEN={token}\nADMIN_ID={admin_id}\n")
        progress_var.set(80)

        # Shortcut
        status_label.config(text=txt["shortcuts"])
        create_shortcut(os.path.join(install_dir, "SystemManager.exe"), "System Manager")
        progress_var.set(90)

        # Start
        status_label.config(text=txt["starting"])
        subprocess.Popen([os.path.join(install_dir, "SystemManager.exe")], shell=True, cwd=install_dir)
        progress_var.set(100)

        messagebox.showinfo(txt["success_title"], txt["success_msg"])
        root.quit()
        
    except Exception as e:
        messagebox.showerror(txt["error_title"], txt["error_msg"].format(error=str(e)))
        status_label.config(text="Error")

def start_install():
    token = token_entry.get().strip()
    admin_id = id_entry.get().strip()
    
    if not token or not admin_id:
        messagebox.showwarning(LANGUAGES[current_lang]["warning_title"], LANGUAGES[current_lang]["warning_msg"])
        return
    
    install_btn.config(state=tk.DISABLED)
    threading.Thread(target=install_logic, args=(token, admin_id, progress_var, status_label, root)).start()

def change_language(event):
    global current_lang
    current_lang = lang_combo.get()
    txt = LANGUAGES[current_lang]
    header_label.config(text=txt["header"])
    token_label.config(text=txt["token"])
    id_label.config(text=txt["admin_id"])
    install_btn.config(text=txt["install"])
    status_label.config(text=txt["ready"])

# --- UI SETUP ---
root = tk.Tk()
root.title("SystemManager Setup")
root.geometry("450x550")
root.resizable(False, False)

# RADIANT DARK THEME for Setup
bg_color = "#050505"
card_color = "#141416"
purple_color = "#8b5cf6"
text_color = "#ffffff"

root.configure(bg=bg_color)

main_frame = tk.Frame(root, bg=bg_color, padx=30, pady=30)
main_frame.pack(fill=tk.BOTH, expand=True)

# Lang selection (Top right)
lang_frame = tk.Frame(main_frame, bg=bg_color)
lang_frame.pack(fill=tk.X)
lang_combo = ttk.Combobox(lang_frame, values=list(LANGUAGES.keys()), state="readonly", width=12)
lang_combo.set(current_lang)
lang_combo.pack(side=tk.RIGHT)
lang_combo.bind("<<ComboboxSelected>>", change_language)

# Header
header_label = tk.Label(main_frame, text=LANGUAGES[current_lang]["header"], font=("Segoe UI", 20, "bold"), 
                        bg=bg_color, fg=purple_color)
header_label.pack(pady=(20, 30))

# Inputs
input_frame = tk.Frame(main_frame, bg=bg_color)
input_frame.pack(fill=tk.X)

token_label = tk.Label(input_frame, text=LANGUAGES[current_lang]["token"], bg=bg_color, fg="#71717a", font=("Segoe UI", 9))
token_label.pack(anchor="w")
token_entry = tk.Entry(input_frame, bg=card_color, fg=text_color, insertbackground=text_color, relief=tk.FLAT, 
                       font=("Segoe UI", 11), borderwidth=8)
token_entry.pack(fill=tk.X, pady=(5, 15))

id_label = tk.Label(input_frame, text=LANGUAGES[current_lang]["admin_id"], bg=bg_color, fg="#71717a", font=("Segoe UI", 9))
id_label.pack(anchor="w")
id_entry = tk.Entry(input_frame, bg=card_color, fg=text_color, insertbackground=text_color, relief=tk.FLAT, 
                    font=("Segoe UI", 11), borderwidth=8)
id_entry.pack(fill=tk.X, pady=(5, 15))

# Progress
progress_var = tk.DoubleVar()
style = ttk.Style()
style.theme_use('default')
style.configure("Radiant.Horizontal.TProgressbar", thickness=6, background=purple_color, troughcolor=card_color, borderwidth=0)
progress_bar = ttk.Progressbar(main_frame, variable=progress_var, maximum=100, style="Radiant.Horizontal.TProgressbar")
progress_bar.pack(fill=tk.X, pady=(20, 10))

status_label = tk.Label(main_frame, text=LANGUAGES[current_lang]["ready"], bg=bg_color, fg="#71717a", font=("Segoe UI", 9))
status_label.pack()

# Install Button
install_btn = tk.Button(main_frame, text=LANGUAGES[current_lang]["install"], command=start_install, 
                        bg=purple_color, fg=text_color, font=("Segoe UI", 12, "bold"), relief=tk.FLAT, 
                        cursor="hand2", pady=12)
install_btn.pack(fill=tk.X, side=tk.BOTTOM, pady=20)

root.mainloop()
