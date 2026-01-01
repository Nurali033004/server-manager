import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import subprocess
import os
import psutil
import threading
import time
from datetime import datetime
from dotenv import load_dotenv

class SystemManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("System Manager - Radiant Edition")
        self.root.geometry("1000x700")
        self.root.resizable(False, False)
        
        # Radiant Purple Theme (Inspired by Image 4)
        self.bg_black = "#050505"    # Pure deep black
        self.bg_card = "#141416"     # Card background
        self.accent_purple = "#8b5cf6" # Radiant purple
        self.accent_cyan = "#06b6d4"   # Secondary cyan
        self.text_primary = "#ffffff"  # White
        self.text_dim = "#71717a"      # Muted text
        self.btn_green = "#10b981"
        self.btn_red = "#f43f5e"
        
        self.root.configure(bg=self.bg_black)
        
        # Get install directory
        self.install_dir = os.path.join(os.path.expanduser("~"), "SystemBot")
        
        # Load environment
        env_path = os.path.join(self.install_dir, ".env")
        if os.path.exists(env_path):
            load_dotenv(env_path)
        
        self.setup_ui()
        self.update_status()
        
    def setup_ui(self):
        # --- HEADER ---
        header = tk.Frame(self.root, bg=self.bg_black, height=100)
        header.pack(fill=tk.X, padx=30, pady=(30, 20))
        
        title_frame = tk.Frame(header, bg=self.bg_black)
        title_frame.pack(side=tk.LEFT)
        
        tk.Label(title_frame, text="System", font=("Segoe UI", 28, "bold"), 
                 bg=self.bg_black, fg=self.text_primary).pack(side=tk.LEFT)
        tk.Label(title_frame, text="Manager", font=("Segoe UI", 28, "bold"), 
                 bg=self.bg_black, fg=self.accent_purple).pack(side=tk.LEFT, padx=(5, 0))
        
        # Top-right Status
        self.status_card = tk.Frame(header, bg=self.bg_card, padx=20, pady=10)
        self.status_card.pack(side=tk.RIGHT)
        
        self.status_indicator = tk.Canvas(self.status_card, width=10, height=10, bg=self.bg_card, highlightthickness=0)
        self.status_indicator.pack(side=tk.LEFT, padx=(0, 10))
        self.status_dot = self.status_indicator.create_oval(0, 0, 10, 10, fill=self.text_dim, outline="")
        
        self.status_label = tk.Label(self.status_card, text="INIT", font=("Segoe UI", 10, "bold"),
                                     bg=self.bg_card, fg=self.text_dim)
        self.status_label.pack(side=tk.LEFT)

        # --- MAIN LAYOUT ---
        content = tk.Frame(self.root, bg=self.bg_black)
        content.pack(fill=tk.BOTH, expand=True, padx=30)

        # 1. STATISTICS CARDS (Inspired by Image 3)
        stats_frame = tk.Frame(content, bg=self.bg_black)
        stats_frame.pack(fill=tk.X, pady=(0, 20))

        # CPU Card
        self.cpu_card = self.create_stat_card(stats_frame, "CPU USAGE", "0.0%", self.accent_purple)
        self.cpu_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        self.cpu_val = self.cpu_card.winfo_children()[1]

        # RAM Card
        self.ram_card = self.create_stat_card(stats_frame, "MEMORY (RAM)", "0.0%", self.accent_cyan)
        self.ram_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))
        self.ram_val = self.ram_card.winfo_children()[1]

        # 2. CONTROLS & LOGS
        main_body = tk.Frame(content, bg=self.bg_black)
        main_body.pack(fill=tk.BOTH, expand=True)

        # Left: Controls
        left_body = tk.Frame(main_body, bg=self.bg_black, width=350)
        left_body.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))

        control_card = tk.Frame(left_body, bg=self.bg_card, padx=20, pady=20)
        control_card.pack(fill=tk.X)

        tk.Label(control_card, text="CORE CONTROLS", font=("Segoe UI", 9, "bold"), 
                 bg=self.bg_card, fg=self.text_dim).pack(anchor="w", pady=(0, 15))
        
        self.start_btn = self.create_neon_button(control_card, "START BOT", self.start_bot, self.btn_green)
        self.start_btn.pack(fill=tk.X, pady=5)
        
        self.stop_btn = self.create_neon_button(control_card, "STOP BOT", self.stop_bot, self.btn_red)
        self.stop_btn.pack(fill=tk.X, pady=5)
        
        self.restart_btn = self.create_neon_button(control_card, "RESTART", self.restart_bot, self.accent_cyan)
        self.restart_btn.pack(fill=tk.X, pady=5)

        # Folder Actions
        folder_card = tk.Frame(left_body, bg=self.bg_card, padx=20, pady=20)
        folder_card.pack(fill=tk.X, pady=(20, 0))

        tk.Label(folder_card, text="QUICK ACCESS", font=("Segoe UI", 9, "bold"), 
                 bg=self.bg_card, fg=self.text_dim).pack(anchor="w", pady=(0, 15))

        self.create_neon_button(folder_card, "OPEN LOGS", self.open_logs, self.accent_purple).pack(fill=tk.X, pady=5)
        self.create_neon_button(folder_card, "INSTALL DIR", self.open_folder, self.text_dim).pack(fill=tk.X, pady=5)

        # Right: Logs (Modern ScrolledText)
        right_body = tk.Frame(main_body, bg=self.bg_card, padx=2)
        right_body.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.log_text = scrolledtext.ScrolledText(right_body, wrap=tk.WORD, 
                                                 bg="#0c0c0e", fg="#a1a1aa",
                                                 font=("Consolas", 10), relief=tk.FLAT,
                                                 padx=15, pady=15, borderwidth=0)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.insert("1.0", ">>> INITIALIZING SYSTEM MANAGER...\n" + "-"*40 + "\n")

    def create_stat_card(self, parent, title, val, color):
        card = tk.Frame(parent, bg=self.bg_card, padx=25, pady=25)
        tk.Label(card, text=title, font=("Segoe UI", 9, "bold"), bg=self.bg_card, fg=self.text_dim).pack(anchor="w")
        tk.Label(card, text=val, font=("Segoe UI", 24, "bold"), bg=self.bg_card, fg=color).pack(anchor="w", pady=(5, 0))
        return card

    def create_neon_button(self, parent, text, cmd, color):
        # Simulated rounded-ish button using padding and relief
        btn = tk.Button(parent, text=text, command=cmd, bg=color, fg="white" if color != self.text_dim else "black",
                       font=("Segoe UI", 10, "bold"), relief=tk.FLAT, borderwidth=0,
                       cursor="hand2", padx=10, pady=10, activebackground=self.text_primary)
        return btn

    def is_bot_running(self):
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'] == 'SystemBot.exe':
                    return True
            except: pass
        return False
    
    def start_bot(self):
        script = os.path.join(self.install_dir, "start.bat")
        if os.path.exists(script):
            subprocess.Popen([script], shell=True, cwd=self.install_dir)
            self.log("EVENT: Starting Bot Services...")
            threading.Timer(2.0, self.update_status).start()
        else: self.log("ERROR: Installation directory unavailable.")

    def stop_bot(self):
        script = os.path.join(self.install_dir, "stop.bat")
        if os.path.exists(script):
            subprocess.Popen([script], shell=True, cwd=self.install_dir)
            self.log("EVENT: Stopping Bot Services...")
            threading.Timer(2.0, self.update_status).start()

    def restart_bot(self):
        self.log("ACTION: Restart Sequence Triggered.")
        self.stop_bot()
        threading.Timer(3.0, self.start_bot).start()

    def open_logs(self):
        path = os.path.join(self.install_dir, "logs")
        if os.path.exists(path): os.startfile(path)

    def open_folder(self):
        if os.path.exists(self.install_dir): os.startfile(self.install_dir)

    def log(self, message):
        t = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{t}] {message}\n")
        self.log_text.see(tk.END)

    def update_status(self):
        active = self.is_bot_running()
        if active:
            self.status_indicator.itemconfig(self.status_dot, fill=self.btn_green)
            self.status_label.config(text="SYSTEM ACTIVE", fg=self.btn_green)
        else:
            self.status_indicator.itemconfig(self.status_dot, fill=self.text_dim)
            self.status_label.config(text="SYSTEM IDLE", fg=self.text_dim)

        try:
            c = psutil.cpu_percent()
            r = psutil.virtual_memory().percent
            self.cpu_val.config(text=f"{c}%")
            self.ram_val.config(text=f"{r}%")
        except: pass
        
        self.root.after(3000, self.update_status)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = SystemManager()
    app.run()
