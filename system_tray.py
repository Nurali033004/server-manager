import pystray
from pystray import MenuItem as item
from PIL import Image
import subprocess
import os
import psutil
import threading
import time

class SystemManagerTray:
    def __init__(self):
        self.icon_path = r'C:/Users/User/.gemini/antigravity/brain/25ea2a1e-2140-461b-83dd-c20126ec5b45/system_manager_icon_1767257421817.png'
        self.icon_image = Image.open(self.icon_path)
        self.install_dir = os.path.join(os.path.expanduser("~"), "SystemBot")
        
    def is_bot_running(self):
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] == 'SystemBot.exe':
                return True
        return False
    
    def start_bot(self, icon, item):
        start_script = os.path.join(self.install_dir, "start.bat")
        if os.path.exists(start_script):
            subprocess.Popen([start_script], shell=True, cwd=self.install_dir)
    
    def stop_bot(self, icon, item):
        stop_script = os.path.join(self.install_dir, "stop.bat")
        if os.path.exists(stop_script):
            subprocess.Popen([stop_script], shell=True, cwd=self.install_dir)
    
    def open_control_panel(self, icon, item):
        control_panel = os.path.join(os.path.dirname(__file__), "control_panel.py")
        if os.path.exists(control_panel):
            subprocess.Popen(['py', control_panel])
    
    def open_logs(self, icon, item):
        log_dir = os.path.join(self.install_dir, "logs")
        if os.path.exists(log_dir):
            os.startfile(log_dir)
    
    def exit_app(self, icon, item):
        icon.stop()
    
    def create_menu(self):
        return pystray.Menu(
            item('System Manager', lambda: None, enabled=False),
            pystray.Menu.SEPARATOR,
            item('Control Panel', self.open_control_panel),
            pystray.Menu.SEPARATOR,
            item('Start Bot', self.start_bot),
            item('Stop Bot', self.stop_bot),
            pystray.Menu.SEPARATOR,
            item('Open Logs', self.open_logs),
            pystray.Menu.SEPARATOR,
            item('Exit', self.exit_app)
        )
    
    def run(self):
        icon = pystray.Icon("SystemManager", self.icon_image, "System Manager", self.create_menu())
        icon.run()

if __name__ == "__main__":
    app = SystemManagerTray()
    app.run()
