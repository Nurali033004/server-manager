import tkinter as tk
from tkinter import ttk, scrolledtext
import subprocess
import os
import psutil
import threading
import time
from datetime import datetime

class SystemManagerControlPanel:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("System Manager - Control Panel")
        self.root.geometry("900x600")
        self.root.resizable(False, False)
        
        # Dark theme colors (inspired by user's designs)
        self.bg_dark = "#1a1a2e"
        self.bg_card = "#252541"
        self.accent_purple = "#7c3aed"
        self.accent_cyan = "#06b6d4"
        self.text_primary = "#ffffff"
        self.text_secondary = "#94a3b8"
        self.success_green = "#10b981"
        self.error_red = "#ef4444"
        
        self.root.configure(bg=self.bg_dark)
        self.setup_ui()
        self.update_status()
        
    def setup_ui(self):
        # Header
        header = tk.Frame(self.root, bg=self.bg_dark, height=80)
        header.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        title = tk.Label(header, text="System Manager", font=("Segoe UI", 24, "bold"), 
                        bg=self.bg_dark, fg=self.text_primary)
        title.pack(side=tk.LEFT)
        
        # Status indicator
        self.status_frame = tk.Frame(header, bg=self.bg_card, padx=15, pady=8)
        self.status_frame.pack(side=tk.RIGHT)
        
        self.status_dot = tk.Canvas(self.status_frame, width=12, height=12, bg=self.bg_card, highlightthickness=0)
        self.status_dot.pack(side=tk.LEFT, padx=(0, 8))
        self.status_circle = self.status_dot.create_oval(0, 0, 12, 12, fill=self.text_secondary, outline="")
        
        self.status_label = tk.Label(self.status_frame, text="Checking...", font=("Segoe UI", 10),
                                     bg=self.bg_card, fg=self.text_secondary)
        self.status_label.pack(side=tk.LEFT)
        
        # Main container
        main_container = tk.Frame(self.root, bg=self.bg_dark)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Left panel - Controls
        left_panel = tk.Frame(main_container, bg=self.bg_card, width=400)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))
        
        controls_label = tk.Label(left_panel, text="Controls", font=("Segoe UI", 14, "bold"),
                                 bg=self.bg_card, fg=self.text_primary, anchor="w", padx=20, pady=15)
        controls_label.pack(fill=tk.X)
        
        # Control buttons
        button_frame = tk.Frame(left_panel, bg=self.bg_card, padx=20, pady=10)
        button_frame.pack(fill=tk.X)
        
        self.start_btn = self.create_gradient_button(button_frame, "▶ Start Bot", self.start_bot, self.success_green)
        self.start_btn.pack(fill=tk.X, pady=5)
        
        self.stop_btn = self.create_gradient_button(button_frame, "⏹ Stop Bot", self.stop_bot, self.error_red)
        self.stop_btn.pack(fill=tk.X, pady=5)
        
        self.restart_btn = self.create_gradient_button(button_frame, "🔄 Restart Bot", self.restart_bot, self.accent_purple)
        self.restart_btn.pack(fill=tk.X, pady=5)
        
        # System info
        info_label = tk.Label(left_panel, text="System Info", font=("Segoe UI", 14, "bold"),
                             bg=self.bg_card, fg=self.text_primary, anchor="w", padx=20, pady=(20, 10))
        info_label.pack(fill=tk.X)
        
        info_frame = tk.Frame(left_panel, bg=self.bg_card, padx=20, pady=10)
        info_frame.pack(fill=tk.BOTH, expand=True)
        
        self.cpu_label = tk.Label(info_frame, text="CPU: ---%", font=("Segoe UI", 11),
                                 bg=self.bg_card, fg=self.text_secondary, anchor="w")
        self.cpu_label.pack(fill=tk.X, pady=3)
        
        self.ram_label = tk.Label(info_frame, text="RAM: ---%", font=("Segoe UI", 11),
                                 bg=self.bg_card, fg=self.text_secondary, anchor="w")
        self.ram_label.pack(fill=tk.X, pady=3)
        
        self.uptime_label = tk.Label(info_frame, text="Uptime: ---", font=("Segoe UI", 11),
                                     bg=self.bg_card, fg=self.text_secondary, anchor="w")
        self.uptime_label.pack(fill=tk.X, pady=3)
        
        # Right panel - Logs
        right_panel = tk.Frame(main_container, bg=self.bg_card)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        logs_label = tk.Label(right_panel, text="Logs", font=("Segoe UI", 14, "bold"),
                             bg=self.bg_card, fg=self.text_primary, anchor="w", padx=20, pady=15)
        logs_label.pack(fill=tk.X)
        
        # Log viewer
        log_container = tk.Frame(right_panel, bg=self.bg_card, padx=20, pady=(0, 20))
        log_container.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_container, wrap=tk.WORD, 
                                                  bg="#16213e", fg=self.text_secondary,
                                                  font=("Consolas", 9), insertbackground=self.text_primary,
                                                  relief=tk.FLAT, padx=10, pady=10)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.insert("1.0", "System Manager Control Panel\n" + "="*50 + "\n\n")
        
    def create_gradient_button(self, parent, text, command, color):
        btn = tk.Button(parent, text=text, command=command, bg=color, fg="white",
                       font=("Segoe UI", 11, "bold"), relief=tk.FLAT, cursor="hand2",
                       padx=20, pady=12, activebackground=color, activeforeground="white")
        return btn
    
    def get_bot_install_dir(self):
        return os.path.join(os.path.expanduser("~"), "SystemBot")
    
    def is_bot_running(self):
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] == 'SystemBot.exe':
                return True
        return False
    
    def start_bot(self):
        install_dir = self.get_bot_install_dir()
        start_script = os.path.join(install_dir, "start.bat")
        
        if os.path.exists(start_script):
            subprocess.Popen([start_script], shell=True, cwd=install_dir)
            self.log("✅ Starting bot...")
            threading.Timer(2.0, self.update_status).start()
        else:
            self.log("❌ Error: Start script not found!")
    
    def stop_bot(self):
        install_dir = self.get_bot_install_dir()
        stop_script = os.path.join(install_dir, "stop.bat")
        
        if os.path.exists(stop_script):
            subprocess.Popen([stop_script], shell=True, cwd=install_dir)
            self.log("⏹ Stopping bot...")
            threading.Timer(2.0, self.update_status).start()
        else:
            self.log("❌ Error: Stop script not found!")
    
    def restart_bot(self):
        self.log("🔄 Restarting bot...")
        self.stop_bot()
        threading.Timer(3.0, self.start_bot).start()
    
    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
    
    def update_status(self):
        running = self.is_bot_running()
        
        if running:
            self.status_dot.itemconfig(self.status_circle, fill=self.success_green)
            self.status_label.config(text="Running", fg=self.success_green)
        else:
            self.status_dot.itemconfig(self.status_circle, fill=self.text_secondary)
            self.status_label.config(text="Stopped", fg=self.text_secondary)
        
        # Update system info
        cpu = psutil.cpu_percent(interval=0.1)
        ram = psutil.virtual_memory().percent
        
        self.cpu_label.config(text=f"CPU: {cpu}%")
        self.ram_label.config(text=f"RAM: {ram}%")
        
        # Schedule next update
        self.root.after(3000, self.update_status)
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = SystemManagerControlPanel()
    app.run()
