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
        self.root.title("System Manager")
        self.root.geometry("1000x650")
        self.root.resizable(False, False)
        
        # Dark theme colors
        self.bg_dark = "#1a1a2e"
        self.bg_card = "#252541"
        self.accent_purple = "#7c3aed"
        self.accent_cyan = "#06b6d4"
        self.text_primary = "#ffffff"
        self.text_secondary = "#94a3b8"
        self.success_green = "#10b981"
        self.error_red = "#ef4444"
        
        self.root.configure(bg=self.bg_dark)
        
        # Get install directory
        self.install_dir = os.path.join(os.path.expanduser("~"), "SystemBot")
        
        # Load environment
        env_path = os.path.join(self.install_dir, ".env")
        if os.path.exists(env_path):
            load_dotenv(env_path)
        
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
        self.status_frame = tk.Frame(header, bg=self.bg_card, padx=15, pady=8, relief=tk.FLAT)
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
        left_panel = tk.Frame(main_container, bg=self.bg_card, width=450)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))
        
        # Bot Controls Section
        controls_label = tk.Label(left_panel, text="Bot Controls", font=("Segoe UI", 14, "bold"),
                                 bg=self.bg_card, fg=self.text_primary, anchor="w")
        controls_label.pack(fill=tk.X, padx=20, pady=15)
        
        button_frame = tk.Frame(left_panel, bg=self.bg_card)
        button_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.start_btn = self.create_button(button_frame, "▶ Start Bot", self.start_bot, self.success_green)
        self.start_btn.pack(fill=tk.X, pady=5)
        
        self.stop_btn = self.create_button(button_frame, "⏹ Stop Bot", self.stop_bot, self.error_red)
        self.stop_btn.pack(fill=tk.X, pady=5)
        
        self.restart_btn = self.create_button(button_frame, "🔄 Restart Bot", self.restart_bot, self.accent_purple)
        self.restart_btn.pack(fill=tk.X, pady=5)
        
        # System Info Section
        info_label = tk.Label(left_panel, text="System Info", font=("Segoe UI", 14, "bold"),
                             bg=self.bg_card, fg=self.text_primary, anchor="w")
        info_label.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        info_frame = tk.Frame(left_panel, bg=self.bg_card)
        info_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.cpu_label = tk.Label(info_frame, text="CPU: ---%", font=("Segoe UI", 11),
                                 bg=self.bg_card, fg=self.text_secondary, anchor="w")
        self.cpu_label.pack(fill=tk.X, pady=3)
        
        self.ram_label = tk.Label(info_frame, text="RAM: ---%", font=("Segoe UI", 11),
                                 bg=self.bg_card, fg=self.text_secondary, anchor="w")
        self.ram_label.pack(fill=tk.X, pady=3)
        
        self.uptime_label = tk.Label(info_frame, text="Uptime: ---", font=("Segoe UI", 11),
                                     bg=self.bg_card, fg=self.text_secondary, anchor="w")
        self.uptime_label.pack(fill=tk.X, pady=3)
        
        # Quick Actions Section
        actions_label = tk.Label(left_panel, text="Quick Actions", font=("Segoe UI", 14, "bold"),
                                bg=self.bg_card, fg=self.text_primary, anchor="w")
        actions_label.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        actions_frame = tk.Frame(left_panel, bg=self.bg_card)
        actions_frame.pack(fill=tk.X, padx=20, pady=10)
        
        open_logs_btn = self.create_button(actions_frame, "📂 Open Logs Folder", self.open_logs, self.accent_cyan)
        open_logs_btn.pack(fill=tk.X, pady=5)
        
        open_folder_btn = self.create_button(actions_frame, "📁 Open Install Folder", self.open_folder, self.accent_cyan)
        open_folder_btn.pack(fill=tk.X, pady=5)
        
        # Right panel - Logs
        right_panel = tk.Frame(main_container, bg=self.bg_card)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        logs_label = tk.Label(right_panel, text="Activity Logs", font=("Segoe UI", 14, "bold"),
                             bg=self.bg_card, fg=self.text_primary, anchor="w")
        logs_label.pack(fill=tk.X, padx=20, pady=15)
        
        # Log viewer
        log_container = tk.Frame(right_panel, bg=self.bg_card)
        log_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        self.log_text = scrolledtext.ScrolledText(log_container, wrap=tk.WORD, 
                                                  bg="#16213e", fg=self.text_secondary,
                                                  font=("Consolas", 9), insertbackground=self.text_primary,
                                                  relief=tk.FLAT, padx=10, pady=10)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.insert("1.0", "System Manager - Activity Monitor\n" + "="*60 + "\n\n")
        
    def create_button(self, parent, text, command, color):
        btn = tk.Button(parent, text=text, command=command, bg=color, fg="white",
                       font=("Segoe UI", 11, "bold"), relief=tk.FLAT, cursor="hand2",
                       padx=20, pady=12, activebackground=color, activeforeground="white")
        return btn
    
    def is_bot_running(self):
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'] == 'SystemBot.exe':
                    return True
            except:
                pass
        return False
    
    def start_bot(self):
        start_script = os.path.join(self.install_dir, "start.bat")
        
        if os.path.exists(start_script):
            subprocess.Popen([start_script], shell=True, cwd=self.install_dir)
            self.log("✅ Starting bot...")
            threading.Timer(2.0, self.update_status).start()
        else:
            self.log("❌ Error: Start script not found!")
            messagebox.showerror("Error", "Installation files not found!")
    
    def stop_bot(self):
        stop_script = os.path.join(self.install_dir, "stop.bat")
        
        if os.path.exists(stop_script):
            subprocess.Popen([stop_script], shell=True, cwd=self.install_dir)
            self.log("⏹ Stopping bot...")
            threading.Timer(2.0, self.update_status).start()
        else:
            self.log("❌ Error: Stop script not found!")
    
    def restart_bot(self):
        self.log("🔄 Restarting bot...")
        self.stop_bot()
        threading.Timer(3.0, self.start_bot).start()
    
    def open_logs(self):
        log_dir = os.path.join(self.install_dir, "logs")
        if os.path.exists(log_dir):
            os.startfile(log_dir)
            self.log("📂 Opened logs folder")
        else:
            self.log("❌ Logs folder not found!")
    
    def open_folder(self):
        if os.path.exists(self.install_dir):
            os.startfile(self.install_dir)
            self.log("📁 Opened installation folder")
        else:
            self.log("❌ Installation folder not found!")
    
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
        try:
            cpu = psutil.cpu_percent(interval=0.1)
            ram = psutil.virtual_memory().percent
            
            self.cpu_label.config(text=f"CPU: {cpu}%")
            self.ram_label.config(text=f"RAM: {ram}%")
        except:
            pass
        
        # Schedule next update
        self.root.after(3000, self.update_status)
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = SystemManager()
    app.run()
