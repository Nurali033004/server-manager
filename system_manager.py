import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import subprocess
import os
import psutil
import threading
import time
from datetime import datetime
from dotenv import load_dotenv
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
import winreg
import sys

# --- CONFIGURATION ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class SystemManagerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("System Manager - Pro Edition")
        self.geometry("1100x700")
        self.resizable(False, False)

        # State Variables
        self.install_dir = os.path.join(os.path.expanduser("~"), "SystemBot")
        self.auto_start_var = ctk.BooleanVar(value=self.check_autostart())
        self.alert_var = ctk.BooleanVar(value=False)
        self.cpu_history = [0] * 60
        self.ram_history = [0] * 60
        self.time_history = list(range(60))

        # Layout Logic
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(5, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar, text="System\nManager", font=ctk.CTkFont(size=24, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.sidebar_btn_1 = ctk.CTkButton(self.sidebar, text="Dashboard", command=lambda: self.show_frame("dashboard"))
        self.sidebar_btn_1.grid(row=1, column=0, padx=20, pady=10)
        
        self.sidebar_btn_2 = ctk.CTkButton(self.sidebar, text="Web IDE", command=lambda: self.show_frame("webide"))
        self.sidebar_btn_2.grid(row=2, column=0, padx=20, pady=10)

        self.sidebar_btn_3 = ctk.CTkButton(self.sidebar, text="Console Logs", command=lambda: self.show_frame("logs"))
        self.sidebar_btn_3.grid(row=3, column=0, padx=20, pady=10)

        self.sidebar_btn_4 = ctk.CTkButton(self.sidebar, text="Settings", command=lambda: self.show_frame("settings"))
        self.sidebar_btn_4.grid(row=4, column=0, padx=20, pady=10)

        # Status Indicator in Sidebar (Bottom)
        self.status_label = ctk.CTkLabel(self.sidebar, text="STATUS: CHECKING", font=("Consolas", 12, "bold"))
        self.status_label.grid(row=6, column=0, padx=20, pady=(10, 20))

        # Main Content Area
        self.frames = {}
        for F in (DashboardPage, LogsPage, SettingsPage, WebIDEPage):
            page_name = F.__name__
            frame = F(parent=self, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=1, sticky="nsew")

        self.show_frame("dashboard")

        # Start Background Threads
        self.running = True
        self.web_process = None
        self.tunnel_process = None
        self.monitoring_thread = threading.Thread(target=self.monitor_system, daemon=True)
        self.monitoring_thread.start()

    def show_frame(self, name):
        mapping = {"dashboard": "DashboardPage", "logs": "LogsPage", "settings": "SettingsPage", "webide": "WebIDEPage"}
        frame = self.frames[mapping[name]]
        frame.tkraise()

    def check_autostart(self):
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_READ)
            winreg.QueryValueEx(key, "SystemManagerBot")
            key.Close()
            return True
        except WindowsError:
            return False

    def toggle_autostart(self):
        exe_path = sys.executable  # In a real frozen app, this is the exe path
        # If running as script, use python path + script path (Simplified for this context)
        # Assuming this file is run directly or compiled
        script_path = os.path.abspath(__file__)
        cmd = f'"{sys.executable}" "{script_path}"' if not getattr(sys, 'frozen', False) else f'"{sys.executable}"'

        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_ALL_ACCESS)
        if self.auto_start_var.get():
            winreg.SetValueEx(key, "SystemManagerBot", 0, winreg.REG_SZ, cmd)
            self.log_msg("Settings: Auto-start ENABLED")
        else:
            try:
                winreg.DeleteValue(key, "SystemManagerBot")
                self.log_msg("Settings: Auto-start DISABLED")
            except WindowsError: pass
        key.Close()

    def monitor_system(self):
        while self.running:
            # CPU & RAM
            cpu = psutil.cpu_percent(interval=1)
            ram = psutil.virtual_memory().percent
            
            # Update History
            self.cpu_history.append(cpu)
            self.cpu_history.pop(0)
            self.ram_history.append(ram)
            self.ram_history.pop(0)

            # Update GUI
            self.frames["DashboardPage"].update_stats(cpu, ram)
            self.frames["DashboardPage"].update_graph(self.cpu_history, self.ram_history)

            # Bot Status
            bot_running = False
            for proc in psutil.process_iter(['name']):
                if proc.info['name'] == 'SystemBot.exe':
                    bot_running = True
                    break
            
            status_text = "BOT ACTIVE" if bot_running else "BOT STOPPED"
            status_color = "green" if bot_running else "red"
            try:
                self.status_label.configure(text=f"STATUS: {status_text}", text_color=status_color)
            except: pass

            # Alerts
            if self.alert_var.get() and (cpu > 90 or ram > 90):
                 # Simple beep or toast would be here, limiting frequency
                 pass

            time.sleep(0.5)

    def log_msg(self, msg):
        self.frames["LogsPage"].add_log(msg)

    def on_closing(self):
        self.running = False
        self.destroy()

# --- PAGES ---

class DashboardPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Header
        self.label = ctk.CTkLabel(self, text="Dashboard", font=ctk.CTkFont(size=24, weight="bold"))
        self.label.grid(row=0, column=0, columnspan=2, padx=20, pady=20, sticky="w")

        # Stat Cards
        self.cpu_card = self.create_stat_card("CPU Usage", "0%", 1, 0)
        self.ram_card = self.create_stat_card("RAM Usage", "0%", 1, 1)

        # Controls
        self.controls_frame = ctk.CTkFrame(self)
        self.controls_frame.grid(row=2, column=0, columnspan=2, padx=20, pady=20, sticky="ew")

        self.start_btn = ctk.CTkButton(self.controls_frame, text="▶ START BOT", fg_color="#10b981", hover_color="#059669",
                                       command=lambda: self.run_script("start.bat"))
        self.start_btn.pack(side="left", padx=10, pady=10, expand=True, fill="x")

        self.stop_btn = ctk.CTkButton(self.controls_frame, text="⏹ STOP BOT", fg_color="#ef4444", hover_color="#dc2626",
                                      command=lambda: self.run_script("stop.bat"))
        self.stop_btn.pack(side="left", padx=10, pady=10, expand=True, fill="x")

        self.restart_btn = ctk.CTkButton(self.controls_frame, text="🔄 RESTART", fg_color="#3b82f6", hover_color="#2563eb",
                                         command=self.restart_bot)
        self.restart_btn.pack(side="left", padx=10, pady=10, expand=True, fill="x")

        # Graph
        self.graph_frame = ctk.CTkFrame(self)
        self.graph_frame.grid(row=3, column=0, columnspan=2, padx=20, pady=(0, 20), sticky="nsew")
        self.grid_rowconfigure(3, weight=1)

        # Matplotlib Setup
        self.fig, self.ax = plt.subplots(facecolor='#2b2b2b', figsize=(6, 3))
        self.ax.set_facecolor('#2b2b2b')
        self.line_cpu, = self.ax.plot([], [], label='CPU', color='#8b5cf6', linewidth=2)
        self.line_ram, = self.ax.plot([], [], label='RAM', color='#06b6d4', linewidth=2)
        
        self.ax.set_ylim(0, 100)
        self.ax.set_xlim(0, 60)
        self.ax.grid(True, color='#404040')
        self.ax.tick_params(axis='x', colors='white')
        self.ax.tick_params(axis='y', colors='white')
        self.ax.legend(facecolor='#2b2b2b', edgecolor='white', labelcolor='white')

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def create_stat_card(self, title, pct, r, c):
        frame = ctk.CTkFrame(self)
        frame.grid(row=r, column=c, padx=20, pady=10, sticky="ew")
        
        lbl_title = ctk.CTkLabel(frame, text=title, text_color="gray")
        lbl_title.pack(padx=20, pady=(15, 0), anchor="w")
        
        lbl_val = ctk.CTkLabel(frame, text=pct, font=ctk.CTkFont(size=40, weight="bold"))
        lbl_val.pack(padx=20, pady=(0, 15), anchor="w")
        
        return lbl_val

    def update_stats(self, cpu, ram):
        self.cpu_card.configure(text=f"{cpu}%")
        self.ram_card.configure(text=f"{ram}%")

    def update_graph(self, cpu_hist, ram_hist):
        x_data = range(len(cpu_hist))
        self.line_cpu.set_data(x_data, cpu_hist)
        self.line_ram.set_data(x_data, ram_hist)
        self.canvas.draw_idle()

    def run_script(self, script_name):
        path = os.path.join(self.controller.install_dir, script_name)
        if os.path.exists(path):
            subprocess.Popen([path], shell=True, cwd=self.controller.install_dir)
            self.controller.log_msg(f"CMD: Executed {script_name}")
        else:
            self.controller.log_msg(f"ERROR: {script_name} not found")

    def restart_bot(self):
        self.run_script("stop.bat")
        threading.Timer(3.0, lambda: self.run_script("start.bat")).start()

class LogsPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.label = ctk.CTkLabel(self, text="Console Logs", font=ctk.CTkFont(size=24, weight="bold"))
        self.label.pack(padx=20, pady=20, anchor="w")
        
        self.textbox = ctk.CTkTextbox(self, font=("Consolas", 12))
        self.textbox.pack(padx=20, pady=(0, 20), fill="both", expand=True)
        
        self.add_log("System Manager Initialized...")

    def add_log(self, message):
        t = datetime.now().strftime("%H:%M:%S")
        try:
            self.textbox.insert("end", f"[{t}] {message}\n")
            self.textbox.see("end")
        except: pass

class SettingsPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        self.label = ctk.CTkLabel(self, text="Settings", font=ctk.CTkFont(size=24, weight="bold"))
        self.label.pack(padx=20, pady=20, anchor="w")

        # Appearance
        self.frame_1 = ctk.CTkFrame(self)
        self.frame_1.pack(padx=20, pady=10, fill="x")
        
        ctk.CTkLabel(self.frame_1, text="Appearance Mode:", font=("Arial", 14, "bold")).pack(padx=20, pady=(20, 5), anchor="w")
        self.appear_opt = ctk.CTkOptionMenu(self.frame_1, values=["Dark", "Light", "System"], command=self.change_appearance_mode)
        self.appear_opt.pack(padx=20, pady=(0, 20), anchor="w")

        # Auto Start
        self.frame_2 = ctk.CTkFrame(self)
        self.frame_2.pack(padx=20, pady=10, fill="x")
        
        self.sw_autostart = ctk.CTkSwitch(self.frame_2, text="Auto-start on Login", 
                                          variable=self.controller.auto_start_var, 
                                          command=self.controller.toggle_autostart)
        self.sw_autostart.pack(padx=20, pady=20, anchor="w")

        # Alerts
        self.frame_3 = ctk.CTkFrame(self)
        self.frame_3.pack(padx=20, pady=10, fill="x")
        
        self.sw_alert = ctk.CTkSwitch(self.frame_3, text="High Usage Alerts (>90%)", 
                                      variable=self.controller.alert_var)
        self.sw_alert.pack(padx=20, pady=20, anchor="w")

    def change_appearance_mode(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)

class WebIDEPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.label = ctk.CTkLabel(self, text="Web IDE Control", font=ctk.CTkFont(size=24, weight="bold"))
        self.label.pack(padx=20, pady=20, anchor="w")

        # Status Info
        self.info_frame = ctk.CTkFrame(self)
        self.info_frame.pack(padx=20, pady=10, fill="x")
        
        self.url_label = ctk.CTkLabel(self.info_frame, text="URL: Server Stopped", font=("Consolas", 14), text_color="gray")
        self.url_label.pack(padx=20, pady=20)

        # Controls
        self.btn_frame = ctk.CTkFrame(self)
        self.btn_frame.pack(padx=20, pady=10, fill="x")

        self.start_web_btn = ctk.CTkButton(self.btn_frame, text="Start Cloud IDE", fg_color="#10b981", command=self.start_server)
        self.start_web_btn.pack(side="left", padx=20, pady=20, expand=True, fill="x")

        self.stop_web_btn = ctk.CTkButton(self.btn_frame, text="Stop Cloud IDE", fg_color="#ef4444", command=self.stop_server, state="disabled")
        self.stop_web_btn.pack(side="left", padx=20, pady=20, expand=True, fill="x")

        # Instructions
        self.instr = ctk.CTkLabel(self, text="Tutorial:\n1. 'Start Cloud IDE' ni bosing.\n2. Tunnel URL paydo bo'lguncha kuting.\n3. Shu URL orqali botingizga kiring.", 
                                  justify="left", text_color="gray")
        self.instr.pack(padx=20, pady=20, anchor="w")

    def start_server(self):
        # Start Backend (Look for EXE first, then script)
        exe_path = os.path.join(os.path.dirname(__file__), "CloudIDEServer.exe")
        server_path = os.path.join(os.path.dirname(__file__), "web_server.py")
        
        if os.path.exists(exe_path):
            self.controller.web_process = subprocess.Popen([exe_path], cwd=os.path.dirname(__file__))
        else:
            self.controller.web_process = subprocess.Popen([sys.executable, server_path], cwd=os.path.dirname(__file__))
        
        self.controller.log_msg("WEB: Backend started")
        
        # Start Cloudflare Tunnel (Assuming installed in SystemBot dir)
        cf_path = os.path.join(self.controller.install_dir, "cloudflared.exe")
        if os.path.exists(cf_path):
            self.controller.tunnel_process = subprocess.Popen([cf_path, "tunnel", "--url", "http://localhost:8000"],
                                                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            threading.Thread(target=self.watch_tunnel, daemon=True).start()
        else:
            self.url_label.configure(text="URL: http://localhost:8000 (Local Only)", text_color="orange")
            self.controller.log_msg("WEB: cloudflared.exe not found. Local link only.")

        self.start_web_btn.configure(state="disabled")
        self.stop_web_btn.configure(state="normal")

    def watch_tunnel(self):
        for line in self.controller.tunnel_process.stdout:
            if "trycloudflare.com" in line:
                url = "https://" + line.split("https://")[1].strip()
                self.url_label.configure(text=f"URL: {url}", text_color="#10b981")
                self.controller.log_msg(f"WEB: IDE is live at {url}")
                break

    def stop_server(self):
        if self.controller.web_process:
            self.controller.web_process.terminate()
        if self.controller.tunnel_process:
            self.controller.tunnel_process.terminate()
        
        self.url_label.configure(text="URL: Server Stopped", text_color="gray")
        self.start_web_btn.configure(state="normal")
        self.stop_web_btn.configure(state="disabled")
        self.controller.log_msg("WEB: Cloud IDE Stopped.")

if __name__ == "__main__":
    app = SystemManagerApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
