import telebot
from telebot import types
import os
import psutil
import subprocess
import time
import sys
import re
import platform
import threading
import json
import secrets
import logging
from dotenv import load_dotenv
from flask import Flask, request, jsonify, send_file, make_response

# ==============================================================================
# ⚙️ SOZLAMALAR
# ==============================================================================
if getattr(sys, 'frozen', False):
    BASE_PATH = os.path.dirname(sys.executable)
else:
    BASE_PATH = os.path.dirname(os.path.abspath(__file__))
    
load_dotenv(os.path.join(BASE_PATH, ".env"))

LOG_PATH = os.path.join(BASE_PATH, "logs")
if not os.path.exists(LOG_PATH):
    os.makedirs(LOG_PATH)

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID_STR = os.getenv("ADMIN_ID")

if not TOKEN or not ADMIN_ID_STR:
    print("❌ XATO: .env fayli topilmadi!")
    sys.exit(1)

ADMIN_ID = int(ADMIN_ID_STR)
SECRET_KEY = secrets.token_hex(16)

bot = telebot.TeleBot(TOKEN, parse_mode='HTML')
app = Flask(__name__)

# Flask loglarini o'chirish (Konsolni toza saqlash uchun)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

CLOUDFLARED_PATH = os.path.join(BASE_PATH, "cloudflared.exe")
PUBLIC_URL = None
STATUS_MESSAGE_ID = None

# Keshlar
PROJECTS_CACHE = []
LAST_NET_IO = psutil.net_io_counters()
LAST_NET_TIME = time.time()
RUNNING_PIDS = {} 

SEARCH_PATHS = [
    BASE_PATH,
    os.path.expanduser("~/Desktop"),
    os.path.expanduser("~/Documents"),
    os.path.expanduser("~/PycharmProjects")
]

# ==============================================================================
# 🎨 WEB APP DIZAYNI
# ==============================================================================
WEBAPP_HTML = """
<!DOCTYPE html>
<html lang="uz" data-bs-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>System Manager Pro</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/ace/1.32.7/ace.js"></script>
    <style>
        body { background-color: #0f0f12; color: #e0e0e0; font-family: 'Segoe UI', sans-serif; padding-bottom: 80px; }
        .navbar-bottom { position: fixed; bottom: 0; width: 100%; background: #18181b; border-top: 1px solid #27272a; z-index: 1000; padding: 10px 0; display: flex; justify-content: space-around; }
        .nav-btn { color: #71717a; text-align: center; font-size: 12px; background: none; border: none; flex: 1; }
        .nav-btn.active { color: #3b82f6; }
        .nav-btn i { font-size: 20px; display: block; margin-bottom: 4px; }
        
        .card { background: #18181b; border: 1px solid #27272a; border-radius: 12px; margin-bottom: 15px; }
        .stat-box { text-align: center; padding: 15px; }
        .stat-val { font-size: 20px; font-weight: bold; color: #fff; }
        .stat-label { font-size: 11px; color: #a1a1aa; }
        
        .net-box { display: flex; justify-content: space-between; padding: 10px 20px; }
        .net-item { text-align: center; }
        .net-icon { font-size: 18px; margin-bottom: 5px; }
        
        .file-item { display: flex; align-items: center; padding: 12px; border-bottom: 1px solid #27272a; cursor: pointer; }
        .file-item:active { background: #27272a; }
        .file-icon { font-size: 24px; margin-right: 15px; }
        .file-info { flex-grow: 1; overflow: hidden; }
        .file-name { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; font-weight: 500; }
        
        .proc-item { padding: 10px; border-bottom: 1px solid #27272a; display: flex; justify-content: space-between; align-items: center; }
        .proc-status { width: 10px; height: 10px; border-radius: 50%; display: inline-block; margin-right: 8px; }
        .status-on { background-color: #22c55e; box-shadow: 0 0 5px #22c55e; }
        .status-off { background-color: #ef4444; }
        
        .terminal-output { background: #000; color: #0f0; font-family: monospace; padding: 10px; border-radius: 8px; height: 300px; overflow-y: auto; font-size: 12px; margin-bottom: 10px; border: 1px solid #333; }
        
        /* Editor Styles */
        #editor-container { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: #1e1e1e; z-index: 2000; display: none; flex-direction: column; }
        #editor { flex-grow: 1; font-size: 14px; }
        .editor-header { padding: 10px; background: #252526; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #333; }
        .editor-console { height: 150px; background: #000; color: #ccc; padding: 10px; font-family: monospace; font-size: 12px; overflow-y: auto; border-top: 1px solid #333; }
        
        .page { display: none; padding: 15px; animation: fadeIn 0.3s; }
        .page.active { display: block; }
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
        
        #install-btn { display: none; margin-top: 5px; }
    </style>
</head>
<body>

    <!-- EDITOR OVERLAY -->
    <div id="editor-container">
        <div class="editor-header">
            <div class="text-truncate me-2" id="editor-filename" style="max-width: 40%;">filename.py</div>
            <div>
                <button class="btn btn-sm btn-success me-1" onclick="saveFile()"><i class="fas fa-save"></i></button>
                <button id="run-btn" class="btn btn-sm btn-primary me-1" onclick="toggleScript()"><i class="fas fa-play"></i> Run</button>
                <button class="btn btn-sm btn-secondary" onclick="closeEditor()"><i class="fas fa-times"></i></button>
            </div>
        </div>
        <div id="editor"></div>
        <div class="editor-console" id="editor-console">
            > Console ready...
        </div>
        <div style="background: #252526; padding: 5px; text-align: center;">
            <button id="install-btn" class="btn btn-sm btn-warning w-100" onclick="installModule()">📦 Install Module</button>
        </div>
    </div>

    <!-- 1. DASHBOARD -->
    <div id="page-home" class="page active">
        <h4 class="mb-3">🖥 Tizim Holati</h4>
        <div class="row g-2 mb-3">
            <div class="col-6">
                <div class="card stat-box">
                    <div class="stat-val" id="cpu-val">...</div>
                    <div class="stat-label">CPU</div>
                </div>
            </div>
            <div class="col-6">
                <div class="card stat-box">
                    <div class="stat-val" id="ram-val">...</div>
                    <div class="stat-label">RAM</div>
                </div>
            </div>
        </div>
        <div class="card mb-3">
            <div class="net-box">
                <div class="net-item text-success">
                    <div class="net-icon"><i class="fas fa-arrow-down"></i></div>
                    <div class="stat-val" id="net-down" style="font-size: 16px;">0 KB/s</div>
                    <div class="stat-label">Download</div>
                </div>
                <div class="net-item text-primary">
                    <div class="net-icon"><i class="fas fa-arrow-up"></i></div>
                    <div class="stat-val" id="net-up" style="font-size: 16px;">0 KB/s</div>
                    <div class="stat-label">Upload</div>
                </div>
            </div>
        </div>
        <div class="card p-3">
            <h6>💾 Disk</h6>
            <div class="progress mb-2" style="height: 10px;">
                <div id="disk-bar" class="progress-bar bg-warning" style="width: 0%"></div>
            </div>
            <div class="d-flex justify-content-between small text-muted">
                <span id="disk-used">...</span>
                <span id="disk-total">...</span>
            </div>
        </div>
    </div>

    <!-- 2. FILES -->
    <div id="page-files" class="page">
        <h4 class="mb-3">📂 Fayl Menejeri</h4>
        <div class="card mb-2 p-2 d-flex flex-row align-items-center">
            <button class="btn btn-sm btn-secondary me-2" onclick="loadFiles('..')">⬆️</button>
            <div id="current-path" class="small text-truncate">...</div>
        </div>
        <div class="card" id="file-list"></div>
    </div>

    <!-- 3. TERMINAL -->
    <div id="page-term" class="page">
        <h4 class="mb-3">💻 Terminal</h4>
        <div class="terminal-output" id="term-out">Microsoft Windows [Version 10.0...]<br>Type command...</div>
        <div class="input-group">
            <input type="text" id="term-in" class="form-control bg-dark text-white border-secondary" placeholder="Buyruq...">
            <button class="btn btn-primary" onclick="runCmd()">Run</button>
        </div>
    </div>

    <!-- 4. PROCESSES (PYTHON SCRIPTS) -->
    <div id="page-proc" class="page">
        <h4 class="mb-3">🐍 Python Skriptlar</h4>
        <button class="btn btn-sm btn-success w-100 mb-2" onclick="loadProcs()">🔄 Yangilash</button>
        <div id="proc-list"></div>
    </div>

    <!-- NAV -->
    <nav class="navbar-bottom">
        <button class="nav-btn active" onclick="switchPage('home', this)"><i class="fas fa-chart-pie"></i>Home</button>
        <button class="nav-btn" onclick="switchPage('files', this)"><i class="fas fa-folder"></i>Fayllar</button>
        <button class="nav-btn" onclick="switchPage('term', this)"><i class="fas fa-terminal"></i>Terminal</button>
        <button class="nav-btn" onclick="switchPage('proc', this)"><i class="fas fa-code"></i>Skriptlar</button>
    </nav>

    <script>
        let tg = null;
        try {
            if (window.Telegram && window.Telegram.WebApp) {
                tg = window.Telegram.WebApp;
                tg.expand();
            }
        } catch (e) {}

        const token = new URLSearchParams(window.location.search).get('token');
        let currentPath = "";
        let editor = null;
        let currentEditingFile = "";
        let logInterval = null;
        let isRunning = false;
        let missingModule = null;

        function initEditor() {
            editor = ace.edit("editor");
            editor.setTheme("ace/theme/monokai");
            editor.session.setMode("ace/mode/python");
            editor.setFontSize(14);
        }

        function openEditor(path) {
            currentEditingFile = path;
            document.getElementById('editor-filename').innerText = path.split(/[\\\\/]/).pop();
            document.getElementById('editor-container').style.display = 'flex';
            document.getElementById('install-btn').style.display = 'none';
            
            if(!editor) initEditor();
            
            fetch(`/api/read_file?path=${encodeURIComponent(path)}&token=${token}`)
                .then(r => r.text())
                .then(code => {
                    editor.setValue(code, -1);
                });
            
            checkStatus();
            startLogTail();
        }

        function closeEditor() {
            document.getElementById('editor-container').style.display = 'none';
            stopLogTail();
        }

        function saveFile() {
            const code = editor.getValue();
            fetch(`/api/save_file?token=${token}`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({path: currentEditingFile, content: code})
            }).then(() => alert("Saqlandi!"));
        }

        function toggleScript() {
            if(isRunning) {
                stopScript();
            } else {
                runScript();
            }
        }

        function runScript() {
            document.getElementById('editor-console').innerHTML += `<div>> Starting...</div>`;
            document.getElementById('install-btn').style.display = 'none';
            
            fetch(`/api/start_script?path=${encodeURIComponent(currentEditingFile)}&token=${token}`)
                .then(r => r.json())
                .then(d => {
                    if(d.status === 'started') {
                        document.getElementById('editor-console').innerHTML += `<div class="text-success">> Started (PID: ${d.pid})</div>`;
                        setRunBtnState(true);
                    } else {
                        document.getElementById('editor-console').innerHTML += `<div class="text-danger">> Error: ${d.msg}</div>`;
                    }
                });
        }

        function stopScript() {
            fetch(`/api/stop_script?path=${encodeURIComponent(currentEditingFile)}&token=${token}`)
                .then(r => r.json())
                .then(d => {
                    document.getElementById('editor-console').innerHTML += `<div class="text-warning">> Stopped</div>`;
                    setRunBtnState(false);
                });
        }

        function setRunBtnState(running) {
            isRunning = running;
            const btn = document.getElementById('run-btn');
            if(running) {
                btn.innerHTML = '<i class="fas fa-stop"></i> Stop';
                btn.className = 'btn btn-sm btn-danger me-1';
            } else {
                btn.innerHTML = '<i class="fas fa-play"></i> Run';
                btn.className = 'btn btn-sm btn-primary me-1';
            }
        }

        function checkStatus() {
            fetch(`/api/check_status?path=${encodeURIComponent(currentEditingFile)}&token=${token}`)
                .then(r => r.json())
                .then(d => {
                    setRunBtnState(d.running);
                });
        }

        function startLogTail() {
            if(logInterval) clearInterval(logInterval);
            const consoleDiv = document.getElementById('editor-console');
            
            // Loglarni har 3 soniyada yangilash (serverni zo'riqtirmaslik uchun)
            logInterval = setInterval(() => {
                fetch(`/api/get_logs?path=${encodeURIComponent(currentEditingFile)}&token=${token}`)
                    .then(r => r.text())
                    .then(logs => {
                        if(logs) {
                            consoleDiv.innerHTML = logs.replace(/\\n/g, '<br>');
                            consoleDiv.scrollTop = consoleDiv.scrollHeight;
                            
                            const match = logs.match(/ModuleNotFoundError: No module named '(.+?)'/);
                            if(match) {
                                missingModule = match[1];
                                const btn = document.getElementById('install-btn');
                                btn.innerText = `📦 Install '${missingModule}'`;
                                btn.style.display = 'block';
                            }
                        }
                    });
            }, 3000);
        }

        function stopLogTail() {
            if(logInterval) clearInterval(logInterval);
        }

        function installModule() {
            if(!missingModule) return;
            const btn = document.getElementById('install-btn');
            btn.disabled = true;
            btn.innerText = "⏳ Installing...";
            
            fetch(`/api/install_module?module=${missingModule}&token=${token}`)
                .then(r => r.json())
                .then(d => {
                    btn.disabled = false;
                    if(d.status === 'ok') {
                        alert(`✅ ${missingModule} o'rnatildi! Qayta ishga tushiring.`);
                        btn.style.display = 'none';
                    } else {
                        alert("❌ Xatolik: " + d.msg);
                        btn.innerText = "❌ Retry";
                    }
                });
        }

        function switchPage(pageId, btn) {
            document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
            document.getElementById('page-' + pageId).classList.add('active');
            document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            if(pageId === 'files' && !currentPath) loadFiles("");
            if(pageId === 'proc') loadProcs();
        }

        function updateStats() {
            fetch(`/api/stats?token=${token}`)
                .then(r => r.json())
                .then(d => {
                    document.getElementById('cpu-val').innerText = d.cpu + '%';
                    document.getElementById('ram-val').innerText = d.ram + '%';
                    document.getElementById('disk-bar').style.width = d.disk + '%';
                    document.getElementById('disk-used').innerText = d.disk_used;
                    document.getElementById('disk-total').innerText = d.disk_total;
                    document.getElementById('net-down').innerText = d.net_down;
                    document.getElementById('net-up').innerText = d.net_up;
                })
                .catch(e => console.error("Stats error:", e));
        }
        // Statistikani har 4 soniyada yangilash
        setInterval(updateStats, 4000);
        updateStats();

        function loadFiles(path) {
            fetch(`/api/files?path=${encodeURIComponent(path)}&token=${token}`)
                .then(r => r.json())
                .then(d => {
                    currentPath = d.current_path;
                    document.getElementById('current-path').innerText = currentPath;
                    let html = '';
                    d.items.forEach(i => {
                        const safePath = i.path.replace(/\\\\/g, '\\\\\\\\');
                        const icon = i.is_dir ? 'fa-folder text-warning' : 'fa-file text-secondary';
                        const click = i.is_dir ? `loadFiles('${safePath}')` : `downloadFile('${safePath}')`;
                        
                        html += `
                        <div class="file-item" onclick="${click}">
                            <i class="fas ${icon} file-icon"></i>
                            <div class="file-info">
                                <div class="file-name">${i.name}</div>
                                <div class="small text-muted">${i.size}</div>
                            </div>
                        </div>`;
                    });
                    document.getElementById('file-list').innerHTML = html;
                });
        }

        function downloadFile(path) {
            window.location.href = `/download?path=${encodeURIComponent(path)}&token=${token}`;
        }

        function runCmd() {
            const cmd = document.getElementById('term-in').value;
            if(!cmd) return;
            const out = document.getElementById('term-out');
            out.innerHTML += `<div>> ${cmd}</div>`;
            document.getElementById('term-in').value = '';
            
            fetch(`/api/cmd?cmd=${encodeURIComponent(cmd)}&token=${token}`)
                .then(r => r.json())
                .then(d => {
                    out.innerHTML += `<div>${d.output}</div><br>`;
                    out.scrollTop = out.scrollHeight;
                });
        }

        function loadProcs() {
            const list = document.getElementById('proc-list');
            list.innerHTML = '<div class="text-center p-3">⏳ Skanerlanmoqda...</div>';
            fetch(`/api/procs?token=${token}`)
                .then(r => r.json())
                .then(d => {
                    let html = '';
                    d.forEach(p => {
                        const statusClass = p.running ? 'status-on' : 'status-off';
                        const statusText = p.running ? `<span class="text-success">Running (PID: ${p.pid})</span>` : '<span class="text-danger">Stopped</span>';
                        const safePath = p.path.replace(/\\\\/g, '\\\\\\\\');
                        
                        html += `
                        <div class="card mb-2" onclick="openEditor('${safePath}')" style="cursor:pointer">
                            <div class="proc-item">
                                <div>
                                    <div class="fw-bold text-white"><span class="proc-status ${statusClass}"></span>${p.name}</div>
                                    <div class="small text-muted" style="font-size: 11px;">${p.path}</div>
                                    <div class="small mt-1">${statusText}</div>
                                </div>
                                <div><i class="fas fa-chevron-right text-muted"></i></div>
                            </div>
                        </div>`;
                    });
                    list.innerHTML = html || '<div class="text-center p-3">Python fayllar topilmadi</div>';
                });
        }
    </script>
</body>
</html>
"""

# ==============================================================================
# 🔄 FONDA ISHLAYDIGAN JARAYONLAR
# ==============================================================================

def scanner_thread():
    """Barcha .py fayllarni topish"""
    global PROJECTS_CACHE
    while True:
        temp = []
        for path in SEARCH_PATHS:
            if not os.path.exists(path): continue
            try:
                for root, dirs, files in os.walk(path):
                    dirs[:] = [d for d in dirs if d not in ['.venv', 'venv', '.git', '__pycache__', 'node_modules']]
                    for f in files:
                        if f.endswith('.py'):
                            full = os.path.join(root, f).replace("\\", "/")
                            if full not in temp: temp.append(full)
            except: pass
        PROJECTS_CACHE = sorted(list(set(temp)))
        time.sleep(300)

# ==============================================================================
# 🌐 FLASK ROUTES
# ==============================================================================

def check_auth():
    token = request.args.get('token')
    if token != SECRET_KEY: return False
    return True

@app.route('/')
def home():
    if not check_auth(): return "⛔ Ruxsat yo'q!"
    response = make_response(WEBAPP_HTML)
    response.headers['Content-Type'] = 'text/html; charset=utf-8'
    return response

@app.route('/api/stats')
def api_stats():
    if not check_auth(): return jsonify({})
    global LAST_NET_IO, LAST_NET_TIME
    
    try:
        cpu = psutil.cpu_percent(interval=0.1)
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/')
        
        curr_net = psutil.net_io_counters()
        curr_time = time.time()
        
        time_diff = curr_time - LAST_NET_TIME
        if time_diff == 0: time_diff = 1
        
        bytes_sent = curr_net.bytes_sent - LAST_NET_IO.bytes_sent
        bytes_recv = curr_net.bytes_recv - LAST_NET_IO.bytes_recv
        
        up_speed = bytes_sent / time_diff
        down_speed = bytes_recv / time_diff
        
        def fmt_speed(bytes_sec):
            if bytes_sec < 1024: return f"{bytes_sec:.0f} B/s"
            elif bytes_sec < 1024**2: return f"{bytes_sec/1024:.1f} KB/s"
            else: return f"{bytes_sec/(1024**2):.1f} MB/s"

        LAST_NET_IO = curr_net
        LAST_NET_TIME = curr_time

        return jsonify({
            'cpu': cpu,
            'ram': ram,
            'disk': disk.percent,
            'disk_used': f"{disk.used // (1024**3)} GB",
            'disk_total': f"{disk.total // (1024**3)} GB",
            'net_up': fmt_speed(up_speed),
            'net_down': fmt_speed(down_speed)
        })
    except: return jsonify({})

@app.route('/api/files')
def api_files():
    if not check_auth(): return jsonify({})
    path = request.args.get('path', BASE_PATH)
    if not path or not os.path.exists(path): path = BASE_PATH
    
    items = []
    try:
        for name in os.listdir(path):
            full = os.path.join(path, name)
            size = "-"
            if os.path.isfile(full):
                size = f"{os.path.getsize(full) // 1024} KB"
            items.append({
                'name': name,
                'path': full,
                'is_dir': os.path.isdir(full),
                'size': size
            })
        items.sort(key=lambda x: (not x['is_dir'], x['name'].lower()))
    except: pass
    return jsonify({'current_path': path, 'items': items})

@app.route('/download')
def download():
    if not check_auth(): return "Error"
    path = request.args.get('path')
    return send_file(path, as_attachment=True)

@app.route('/api/cmd')
def api_cmd():
    if not check_auth(): return jsonify({})
    cmd = request.args.get('cmd')
    try:
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        out = res.stdout if res.stdout else res.stderr
        if not out: out = "Done."
    except Exception as e:
        out = str(e)
    return jsonify({'output': out.replace('\n', '<br>')})

@app.route('/api/procs')
def api_procs():
    if not check_auth(): return jsonify({})
    running_pids = {}
    for p in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if 'python' in p.info['name'].lower():
                cmd = p.info['cmdline']
                if cmd and len(cmd) > 1:
                    for arg in cmd[1:]:
                        if arg.endswith('.py'):
                            abs_path = os.path.abspath(arg).replace("\\", "/")
                            running_pids[abs_path] = p.info['pid']
        except: pass

    results = []
    scan_list = PROJECTS_CACHE if PROJECTS_CACHE else []
    if not scan_list:
        for f in os.listdir(BASE_PATH):
            if f.endswith('.py'):
                scan_list.append(os.path.join(BASE_PATH, f).replace("\\", "/"))

    for script_path in scan_list:
        is_running = script_path in running_pids
        results.append({
            'name': os.path.basename(script_path),
            'path': script_path,
            'running': is_running,
            'pid': running_pids.get(script_path, None)
        })
    return jsonify(results)

@app.route('/api/kill')
def api_kill():
    if not check_auth(): return jsonify({})
    pid = int(request.args.get('pid'))
    try:
        psutil.Process(pid).kill()
    except: pass
    return jsonify({'status': 'ok'})

# --- EDITOR API ---

@app.route('/api/read_file')
def api_read_file():
    if not check_auth(): return ""
    path = request.args.get('path')
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except: return "# Error reading file"

@app.route('/api/save_file', methods=['POST'])
def api_save_file():
    token = request.args.get('token')
    if token != SECRET_KEY: return jsonify({'status': 'error'})
    data = request.json
    try:
        with open(data['path'], 'w', encoding='utf-8') as f:
            f.write(data['content'])
        return jsonify({'status': 'ok'})
    except Exception as e:
        return jsonify({'status': 'error', 'msg': str(e)})

@app.route('/api/start_script')
def api_start_script():
    if not check_auth(): return jsonify({})
    path = request.args.get('path')
    log_file = os.path.join(LOG_PATH, os.path.basename(path) + ".log")
    
    try:
        for p in psutil.process_iter(['pid', 'cmdline']):
            if p.info['cmdline'] and path in p.info['cmdline']:
                p.kill()
        
        with open(log_file, "w") as f:
            proc = subprocess.Popen([sys.executable, "-u", path], cwd=os.path.dirname(path), stdout=f, stderr=f)
            
        return jsonify({'status': 'started', 'pid': proc.pid})
    except Exception as e:
        return jsonify({'status': 'error', 'msg': str(e)})

@app.route('/api/stop_script')
def api_stop_script():
    if not check_auth(): return jsonify({})
    path = request.args.get('path')
    try:
        for p in psutil.process_iter(['pid', 'cmdline']):
            if p.info['cmdline'] and path in p.info['cmdline']:
                p.kill()
        return jsonify({'status': 'stopped'})
    except: return jsonify({'status': 'error'})

@app.route('/api/check_status')
def api_check_status():
    if not check_auth(): return jsonify({})
    path = request.args.get('path')
    is_running = False
    for p in psutil.process_iter(['pid', 'cmdline']):
        try:
            if p.info['cmdline'] and path in p.info['cmdline']:
                is_running = True
                break
        except: pass
    return jsonify({'running': is_running})

@app.route('/api/get_logs')
def api_get_logs():
    if not check_auth(): return ""
    path = request.args.get('path')
    log_file = os.path.join(LOG_PATH, os.path.basename(path) + ".log")
    if os.path.exists(log_file):
        try:
            with open(log_file, "r") as f:
                return f.read()
        except: pass
    return ""

@app.route('/api/install_module')
def api_install_module():
    if not check_auth(): return jsonify({})
    module = request.args.get('module')
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", module], check=True)
        return jsonify({'status': 'ok'})
    except Exception as e:
        return jsonify({'status': 'error', 'msg': str(e)})

def run_flask():
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

def start_cloudflared():
    global PUBLIC_URL, STATUS_MESSAGE_ID
    if not os.path.exists(CLOUDFLARED_PATH):
        print("⚠️ Cloudflared.exe topilmadi!")
        return

    try:
        subprocess.run("taskkill /F /IM cloudflared.exe", shell=True, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    except: pass
    time.sleep(2)

    while True:
        print("🔄 Cloudflare Tunnel ishga tushmoqda...")
        try:
            if STATUS_MESSAGE_ID:
                bot.edit_message_text("⏳ Web server qayta ishga tushmoqda...", ADMIN_ID, STATUS_MESSAGE_ID)
            else:
                msg = bot.send_message(ADMIN_ID, "⏳ Web server ishga tushmoqda...")
                STATUS_MESSAGE_ID = msg.message_id
        except: pass

        cmd = [CLOUDFLARED_PATH, 'tunnel', '--url', 'http://localhost:5000']
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        start_time = time.time()
        found_url = False
        
        while time.time() - start_time < 30:
            line = process.stderr.readline()
            if not line: break
            
            if 'trycloudflare.com' in line:
                match = re.search(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com', line)
                if match:
                    PUBLIC_URL = match.group(0)
                    print(f"✅ WEB LINK: {PUBLIC_URL}")
                    time.sleep(5)
                    try:
                        full_url = f"{PUBLIC_URL}?token={SECRET_KEY}"
                        markup = types.InlineKeyboardMarkup()
                        markup.add(types.InlineKeyboardButton("🚀 Web Appni Ochish", web_app=types.WebAppInfo(url=full_url)))
                        bot.edit_message_text("✅ <b>Web App Tayyor!</b>\n\nIltimos, faqat shu yangi tugmani bosing:", ADMIN_ID, STATUS_MESSAGE_ID, reply_markup=markup)
                    except: pass
                    found_url = True
                    break
        
        if found_url:
            process.wait()
            print("⚠️ Tunnel uzildi! Qayta ulanmoqda...")
            PUBLIC_URL = None
        else:
            print("❌ URL olinmadi. 5 soniyadan keyin qayta urinib ko'ramiz...")
            try: 
                subprocess.run("taskkill /F /IM cloudflared.exe", shell=True, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
            except: pass
            time.sleep(5)

# ==============================================================================
# 🤖 TELEGRAM BOT
# ==============================================================================
@bot.message_handler(commands=['start', 'webapp', 'link'])
def start(message):
    global STATUS_MESSAGE_ID
    if message.from_user.id != ADMIN_ID: return
    
    if PUBLIC_URL:
        full_url = f"{PUBLIC_URL}?token={SECRET_KEY}"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🚀 Web Appni Ochish", web_app=types.WebAppInfo(url=full_url)))
        bot.send_message(message.chat.id, "📱 <b>Telegram Mini App</b>\n\nBoshqaruv paneliga kirish uchun bosing:", reply_markup=markup)
    else:
        msg = bot.send_message(message.chat.id, "⏳ Web server ishga tushmoqda... Biroz kuting.")
        STATUS_MESSAGE_ID = msg.message_id

if __name__ == "__main__":
    threading.Thread(target=scanner_thread, daemon=True).start()
    threading.Thread(target=run_flask, daemon=True).start()
    threading.Thread(target=start_cloudflared, daemon=True).start()
    
    print("✅ BOT ISHGA TUSHDI!")
    
    # 🛠 TUZATILDI: Polling barqarorligi oshirildi
    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
        except Exception as e:
            print(f"⚠️ Bot polling xatosi: {e}")
            time.sleep(5)
