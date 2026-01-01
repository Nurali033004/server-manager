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

# Config
REPO_URL = "https://raw.githubusercontent.com/Nurali033004/server-manager/main"
FILES_TO_DOWNLOAD = [
    ("SystemBot.exe", f"{REPO_URL}/SystemBot.exe"),
    ("SystemManager.exe", f"{REPO_URL}/SystemManager.exe"),
    ("start.bat", f"{REPO_URL}/start.bat"),
    ("stop.bat", f"{REPO_URL}/stop.bat"),
    ("uninstall.bat", f"{REPO_URL}/uninstall.bat"),
    ("start.ps1", f"{REPO_URL}/start.ps1"),
    ("stop.ps1", f"{REPO_URL}/stop.ps1"),
    ("uninstall.ps1", f"{REPO_URL}/uninstall.ps1"),
]
CLOUDFLARED_URL = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"

# Translations
LANGUAGES = {
    "O'zbekcha 🇺🇿": {
        "header": "SystemBot O'rnatish",
        "token": "Bot Token (BotFather):",
        "admin_id": "Admin ID (Telegram):",
        "install": "O'RNATISH",
        "creating_dir": "Papka yaratilmoqda...",
        "downloading": "Yuklanmoqda: {name}...",
        "settings": "Sozlamalar saqlanmoqda...",
        "shortcuts": "Yorliqlar yaratilmoqda...",
        "starting": "Bot ishga tushirilmoqda...",
        "success_title": "Muvaffaqiyat",
        "success_msg": "O'rnatish tugadi! Bot ishga tushdi.\nIsh stolidagi yorliqlarni tekshiring.",
        "error_title": "Xatolik",
        "error_msg": "O'rnatishda xatolik yuz berdi:\n{error}",
        "warning_title": "Diqqat",
        "warning_msg": "Iltimos, Token va ID ni kiriting!",
        "ready": "Tayyor"
    },
    "Русский 🇷🇺": {
        "header": "Установка SystemBot",
        "token": "Бот Токен (BotFather):",
        "admin_id": "Админ ID (Telegram):",
        "install": "УСТАНОВИТЬ",
        "creating_dir": "Создание папки...",
        "downloading": "Загрузка: {name}...",
        "settings": "Сохранение настроек...",
        "shortcuts": "Создание ярлыков...",
        "starting": "Запуск бота...",
        "success_title": "Успешно",
        "success_msg": "Установка завершена! Бот запущен.\nПроверьте ярлыки на рабочем столе.",
        "error_title": "Ошибка",
        "error_msg": "Произошла ошибка при установке:\n{error}",
        "warning_title": "Внимание",
        "warning_msg": "Пожалуйста, введите Токен и ID!",
        "ready": "Готово"
    },
    "English 🇺🇸": {
        "header": "SystemBot Setup",
        "token": "Bot Token (BotFather):",
        "admin_id": "Admin ID (Telegram):",
        "install": "INSTALL",
        "creating_dir": "Creating directory...",
        "downloading": "Downloading: {name}...",
        "settings": "Saving settings...",
        "shortcuts": "Creating shortcuts...",
        "starting": "Starting bot...",
        "success_title": "Success",
        "success_msg": "Installation complete! Bot started.\nCheck Desktop for shortcuts.",
        "error_title": "Error",
        "error_msg": "Installation failed:\n{error}",
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
        if icon:
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
        # 1. Create Directory
        status_label.config(text=txt["creating_dir"])
        if not os.path.exists(install_dir):
            os.makedirs(install_dir)
        progress_var.set(10)

        # 2. Download Files
        total_files = len(FILES_TO_DOWNLOAD) + 1 
        current = 0
        
        for name, url in FILES_TO_DOWNLOAD:
            status_label.config(text=txt["downloading"].format(name=name))
            dest = os.path.join(install_dir, name)
            urllib.request.urlretrieve(url, dest)
            current += 1
            progress_var.set(10 + (current / total_files * 60))
        
        # Cloudflared
        status_label.config(text=txt["downloading"].format(name="cloudflared"))
        cf_path = os.path.join(install_dir, "cloudflared.exe")
        if not os.path.exists(cf_path):
            urllib.request.urlretrieve(CLOUDFLARED_URL, cf_path)
        progress_var.set(70)

        # 3. Create .env
        status_label.config(text=txt["settings"])
        env_path = os.path.join(install_dir, ".env")
        with open(env_path, "w") as f:
            f.write(f"BOT_TOKEN={token}\nADMIN_ID={admin_id}")
        progress_var.set(80)

        # 4. Create Shortcuts
        status_label.config(text=txt["shortcuts"])
        create_shortcut(os.path.join(install_dir, "SystemManager.exe"), "System Manager")
        progress_var.set(90)

        # 5. Start Bot
        status_label.config(text=txt["starting"])
        subprocess.Popen([os.path.join(install_dir, "start.bat")], shell=True, cwd=install_dir)
        progress_var.set(100)
        
        messagebox.showinfo(txt["success_title"], txt["success_msg"])
        root.quit()

    except Exception as e:
        messagebox.showerror(txt["error_title"], txt["error_msg"].format(error=str(e)))
        status_label.config(text=txt["error_title"])
        install_btn.config(state=tk.NORMAL)

def start_install():
    global current_lang
    txt = LANGUAGES[current_lang]
    token = token_entry.get()
    admin_id = admin_id_entry.get()

    if not token or not admin_id:
        messagebox.showwarning(txt["warning_title"], txt["warning_msg"])
        return

    install_btn.config(state=tk.DISABLED)
    threading.Thread(target=install_logic, args=(token, admin_id, progress_var, status_label, root)).start()

def change_language(event):
    global current_lang
    current_lang = lang_combo.get()
    txt = LANGUAGES[current_lang]
    
    header_label.config(text=txt["header"])
    token_label.config(text=txt["token"])
    admin_id_label.config(text=txt["admin_id"])
    install_btn.config(text=txt["install"])
    status_label.config(text=txt["ready"])

# GUI Setup
root = tk.Tk()
root.title("SystemBot Setup")
root.geometry("400x420")
root.resizable(False, False)

style = ttk.Style()
style.theme_use('clam')

# Main Frame
main_frame = tk.Frame(root, padx=20, pady=10)
main_frame.pack(fill=tk.BOTH, expand=True)

# Language Selector
lang_frame = tk.Frame(main_frame)
lang_frame.pack(fill=tk.X, pady=(0, 10))
tk.Label(lang_frame, text="Language / Til / Язык:", font=("Arial", 8)).pack(side=tk.LEFT)
lang_combo = ttk.Combobox(lang_frame, values=list(LANGUAGES.keys()), state="readonly")
lang_combo.current(0)
lang_combo.bind("<<ComboboxSelected>>", change_language)
lang_combo.pack(side=tk.RIGHT)

# Header
header_label = tk.Label(main_frame, text=LANGUAGES[current_lang]["header"], font=("Arial", 16, "bold"), pady=10)
header_label.pack()

# Inputs
token_label = tk.Label(main_frame, text=LANGUAGES[current_lang]["token"], font=("Arial", 10))
token_label.pack(anchor=tk.W)
token_entry = tk.Entry(main_frame, width=40)
token_entry.pack(fill=tk.X, pady=(0, 10))

admin_id_label = tk.Label(main_frame, text=LANGUAGES[current_lang]["admin_id"], font=("Arial", 10))
admin_id_label.pack(anchor=tk.W)
admin_id_entry = tk.Entry(main_frame, width=40)
admin_id_entry.pack(fill=tk.X, pady=(0, 20))

# Progress
progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(main_frame, variable=progress_var, maximum=100)
progress_bar.pack(fill=tk.X, pady=10)

status_label = tk.Label(main_frame, text=LANGUAGES[current_lang]["ready"], font=("Arial", 9), fg="gray")
status_label.pack()

# Button
install_btn = tk.Button(main_frame, text=LANGUAGES[current_lang]["install"], font=("Arial", 12, "bold"), bg="#4CAF50", fg="white", height=2, command=start_install)
install_btn.pack(fill=tk.X, pady=20)

root.mainloop()
