# =============================================================================
# KHAN HERBAL STORES — WEB FACTORY v3.0
# =============================================================================
# Single-file Flask app. 15 tabs.
#
# PART A (this section):
#   SECTION 1  — Imports
#   SECTION 2  — Constants
#   SECTION 3  — Flask setup + Sessions
#   SECTION 4  — CSS
#   SECTION 5  — HTML Body (all 15 tabs)
#
# PART B (next message):
#   SECTION 6  — JavaScript
#   SECTION 7  — Page route + API routes
#   SECTION 8  — Entry point
# =============================================================================

# =============================================================================
# SECTION 1 — IMPORTS
# =============================================================================
import os
import sys
import csv
import io
import re
import json
import time
import uuid
import socket
import base64
import threading
import webbrowser
import datetime
from pathlib import Path

try:
    from flask import Flask, request, jsonify, session, send_file, Response
except ImportError:
    print("ERROR: Flask not installed. Run: pip install Flask")
    sys.exit(1)

try:
    import requests
except ImportError:
    print("ERROR: requests not installed.")
    sys.exit(1)

# Custom modules
engine = media = taxonomy = open_graph = ai_prompts = wp_client = None
CUSTOM_MODULES = False
try:
    import engine
    import media
    import taxonomy
    import open_graph
    import ai_prompts
    import wp_client
    CUSTOM_MODULES = True
except ImportError as e:
    print(f"WARNING: Custom modules missing: {e}")


# =============================================================================
# SECTION 2 — CONSTANTS
# =============================================================================
APP_NAME = "Khan Herbal Stores — Web Factory"
APP_VERSION = "3.0.0"
DEFAULT_PORT = 5000

SITE_URL = "https://darkcyan-turkey-703045.hostingersite.com"
CURRENCY_CODE = "PKR"
CURRENCY_SYMBOL = "Rs"
PRICE_MIN = 199
PRICE_MAX = 999
PRODUCT_COUNT = 325

WORKSPACE = Path.cwd() / "workspace"
UPLOAD_DIR = WORKSPACE / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR = Path.cwd() / "logs"
LOG_DIR.mkdir(exist_ok=True)

STORE_DEFAULTS = {
    "name":           "Khan Herbal Stores",
    "tagline":        "Authentic Herbal Remedies in Pakistan",
    "description":    "Pakistan's trusted online store for pure, natural and authentic herbal products.",
    "email":          "info@khanherbalstores.com",
    "phone":          "+92 300 0000000",
    "whatsapp":       "+923218224219",
    "address_line1":  "Main Market",
    "address_line2":  "",
    "city":           "Karachi",
    "state":          "Sindh",
    "country":        "PK",
    "postal_code":    "74000",
    "business_hours": "Mon-Sat 9:00 AM - 9:00 PM",
    "facebook":       "",
    "instagram":      "",
    "youtube":        "",
    "twitter":        "",
    "license_type":   "Commercial Single-Site",
    "license_to":     "Khan Herbal Stores",
    "license_key":    "",
    "support_email":  "support@khanherbalstores.com",
}


# =============================================================================
# SECTION 3 — FLASK + SESSIONS
# =============================================================================
app = Flask(__name__)
app.secret_key = "khan-herbal-master-factory-2026-secret"
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024
SESSIONS = {}


def get_session_data():
    if "sid" not in session:
        session["sid"] = str(uuid.uuid4())
    sid = session["sid"]
    if sid not in SESSIONS:
        SESSIONS[sid] = {
            "wp": {"connected": False, "url": "", "user": "", "pass": ""},
            "wc": {"connected": False, "url": "", "ck": "", "cs": ""},
            "pexels_key": "",
            "raw_products": [],
            "built_products": [],
            "slot_managers": {},
            "activity_log": [],
            "store": dict(STORE_DEFAULTS),
            "og_global": {},
            "blog_drafts": [],
            "ai_responses": [],
            "taxonomy_cache": {},
        }
    return SESSIONS[sid]


def log_activity(action, result="", detail=""):
    s = get_session_data()
    s["activity_log"].append({
        "time": datetime.datetime.now().strftime("%H:%M:%S"),
        "action": action, "result": result,
        "detail": _redact(detail)[:200],
    })
    if len(s["activity_log"]) > 500:
        s["activity_log"] = s["activity_log"][-500:]


def _redact(text):
    if not isinstance(text, str):
        text = str(text)
    for p in [r"ck_[A-Za-z0-9]{20,}", r"cs_[A-Za-z0-9]{20,}",
              r"(?i)(authorization|bearer|password|secret)\s*[:=]\s*\S+"]:
        text = re.sub(p, "***", text)
    return text


# =============================================================================
# SECTION 4 — CSS
# =============================================================================
CSS = r"""
:root{--bg:#f5f7fa;--bg-card:#fff;--bg-elev:#f0f2f5;--text:#1a202c;--muted:#64748b;
  --border:#e2e8f0;--primary:#2e7d32;--primary-h:#1b5e20;--primary-l:#e8f5e9;
  --danger:#dc2626;--warn:#f59e0b;--info:#2563eb;--gold:#d97706;
  --shadow:0 1px 3px rgba(0,0,0,.06),0 1px 2px rgba(0,0,0,.04);
  --shadow-lg:0 10px 25px rgba(0,0,0,.08);
  --r:10px;--r-sm:6px;--hh:64px;--th:52px}
[data-theme="dark"]{--bg:#0f172a;--bg-card:#1e293b;--bg-elev:#334155;--text:#f1f5f9;
  --muted:#94a3b8;--border:#334155;--primary:#4ade80;--primary-h:#22c55e;
  --primary-l:#14321e;--shadow:0 1px 3px rgba(0,0,0,.3);--shadow-lg:0 10px 25px rgba(0,0,0,.4)}
*{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%;font-family:'Segoe UI',-apple-system,BlinkMacSystemFont,sans-serif;
  background:var(--bg);color:var(--text);font-size:14px;line-height:1.5;
  transition:background .2s,color .2s;overflow:hidden}
.header{height:var(--hh);background:var(--bg-card);border-bottom:1px solid var(--border);
  display:flex;align-items:center;padding:0 20px;gap:16px;position:sticky;top:0;
  z-index:100;box-shadow:var(--shadow)}
.header .logo{font-size:20px;font-weight:700;color:var(--primary);white-space:nowrap}
.header .subtitle{color:var(--muted);font-size:12px}
.header .spacer{flex:1}
.header .badge{padding:4px 10px;border-radius:12px;font-size:11px;
  background:var(--bg-elev);color:var(--muted);font-weight:600}
.theme-toggle{width:40px;height:40px;border-radius:50%;border:1px solid var(--border);
  background:var(--bg-elev);color:var(--text);font-size:18px;cursor:pointer;
  display:flex;align-items:center;justify-content:center;transition:all .2s}
.theme-toggle:hover{background:var(--primary-l);border-color:var(--primary)}
.tabbar{height:var(--th);background:var(--bg-card);border-bottom:1px solid var(--border);
  display:flex;padding:0 12px;gap:4px;overflow-x:auto;overflow-y:hidden;
  scrollbar-width:thin;position:sticky;top:var(--hh);z-index:99}
.tabbar::-webkit-scrollbar{height:4px}
.tabbar::-webkit-scrollbar-thumb{background:var(--border);border-radius:2px}
.tab-btn{padding:0 14px;border:none;background:transparent;color:var(--muted);
  font-size:13px;font-weight:600;cursor:pointer;border-bottom:3px solid transparent;
  transition:all .15s;white-space:nowrap;display:flex;align-items:center;gap:6px;
  font-family:inherit}
.tab-btn:hover{color:var(--text);background:var(--bg-elev)}
.tab-btn.active{color:var(--primary);border-bottom-color:var(--primary);background:var(--primary-l)}
.main{height:calc(100vh - var(--hh) - var(--th));overflow-y:auto;overflow-x:hidden;
  padding:20px;scroll-behavior:smooth}
.main::-webkit-scrollbar{width:10px}
.main::-webkit-scrollbar-track{background:var(--bg)}
.main::-webkit-scrollbar-thumb{background:var(--border);border-radius:5px}
.tab-content{display:none;max-width:1400px;margin:0 auto}
.tab-content.active{display:block;animation:fadeIn .2s ease}
@keyframes fadeIn{from{opacity:0;transform:translateY(4px)}to{opacity:1;transform:none}}
.card{background:var(--bg-card);border:1px solid var(--border);border-radius:var(--r);
  padding:20px;margin-bottom:16px;box-shadow:var(--shadow)}
.card h2{font-size:16px;margin-bottom:14px;display:flex;align-items:center;gap:8px}
.card h3{font-size:14px;margin-bottom:10px;color:var(--muted)}
.grid-2{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.grid-3{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}
.grid-4{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}
label{display:block;font-size:12px;color:var(--muted);margin-bottom:6px;font-weight:600}
input[type=text],input[type=password],input[type=number],input[type=url],input[type=email],
input[type=tel],select,textarea{width:100%;padding:10px 12px;border:1px solid var(--border);
  border-radius:var(--r-sm);background:var(--bg);color:var(--text);font-size:13px;
  font-family:inherit;transition:border-color .15s,box-shadow .15s}
input:focus,select:focus,textarea:focus{outline:none;border-color:var(--primary);
  box-shadow:0 0 0 3px var(--primary-l)}
[data-theme="dark"] input,[data-theme="dark"] select,[data-theme="dark"] textarea{background:var(--bg-elev)}
.form-row{margin-bottom:14px}
.form-row-2{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.form-row-3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:14px}
.btn{padding:10px 18px;border-radius:var(--r-sm);border:1px solid var(--border);
  background:var(--bg-card);color:var(--text);font-size:13px;font-weight:600;
  cursor:pointer;transition:all .15s;display:inline-flex;align-items:center;gap:6px;
  white-space:nowrap;font-family:inherit}
.btn:hover{transform:translateY(-1px);box-shadow:var(--shadow-lg)}
.btn:active{transform:none}
.btn:disabled{opacity:.5;cursor:not-allowed;transform:none}
.btn-primary{background:var(--primary);color:#fff;border-color:var(--primary)}
.btn-primary:hover{background:var(--primary-h)}
.btn-danger{background:var(--danger);color:#fff;border-color:var(--danger)}
.btn-info{background:var(--info);color:#fff;border-color:var(--info)}
.btn-warn{background:var(--warn);color:#fff;border-color:var(--warn)}
.btn-gold{background:var(--gold);color:#fff;border-color:var(--gold)}
.btn-sm{padding:6px 12px;font-size:12px}
.btn-lg{padding:14px 24px;font-size:14px}
.btn-block{width:100%;justify-content:center}
.btn-row{display:flex;gap:10px;flex-wrap:wrap;align-items:center}
.status{padding:10px 14px;border-radius:var(--r-sm);font-size:13px;
  display:flex;align-items:center;gap:8px;margin-top:12px}
.status.ok{background:#dcfce7;color:#166534}
.status.err{background:#fee2e2;color:#991b1b}
.status.info{background:#dbeafe;color:#1e40af}
.status.warn{background:#fef3c7;color:#92400e}
[data-theme=dark] .status.ok{background:#14321e;color:#86efac}
[data-theme=dark] .status.err{background:#3b1218;color:#fca5a5}
[data-theme=dark] .status.info{background:#172554;color:#93c5fd}
[data-theme=dark] .status.warn{background:#3b2506;color:#fcd34d}
.toast-container{position:fixed;top:80px;right:20px;z-index:9999;display:flex;
  flex-direction:column;gap:10px;max-width:380px}
.toast{padding:14px 18px;border-radius:var(--r-sm);background:var(--bg-card);
  border-left:4px solid var(--primary);box-shadow:var(--shadow-lg);color:var(--text);
  font-size:13px;animation:slideIn .3s ease;display:flex;align-items:flex-start;gap:10px;
  transition:opacity .3s,transform .3s}
.toast.error{border-left-color:var(--danger)}
.toast.warning{border-left-color:var(--warn)}
.toast.info{border-left-color:var(--info)}
@keyframes slideIn{from{transform:translateX(400px);opacity:0}to{transform:none;opacity:1}}
.table-wrap{background:var(--bg-card);border:1px solid var(--border);
  border-radius:var(--r);overflow:auto;max-height:520px}
table{width:100%;border-collapse:collapse;font-size:13px}
th,td{padding:10px 12px;text-align:left;border-bottom:1px solid var(--border)}
th{background:var(--bg-elev);color:var(--muted);font-weight:700;font-size:11px;
  text-transform:uppercase;letter-spacing:.5px;position:sticky;top:0;z-index:1}
tr:hover td{background:var(--bg-elev)}
.row-actions button{padding:4px 8px;margin:0 2px;font-size:11px;border-radius:4px;
  border:1px solid var(--border);background:var(--bg-card);cursor:pointer}
.row-actions button:hover{background:var(--primary-l);border-color:var(--primary)}
.row-actions .del:hover{background:#fee2e2;border-color:var(--danger);color:var(--danger)}
.dropzone{border:3px dashed var(--border);border-radius:var(--r);padding:36px 20px;
  text-align:center;background:var(--bg-elev);color:var(--muted);transition:all .2s;
  cursor:pointer;position:relative}
.dropzone:hover{border-color:var(--primary);background:var(--primary-l)}
.dropzone.dragover{border-color:var(--primary);background:var(--primary-l);
  transform:scale(1.01);box-shadow:0 0 0 6px var(--primary-l)}
.dropzone .icon{font-size:44px;margin-bottom:10px;display:block}
.dropzone .title{font-size:15px;font-weight:700;color:var(--text);margin-bottom:4px}
.dropzone .hint{font-size:12px;margin-top:4px}
.slots-grid{display:grid;grid-template-columns:repeat(5,1fr);gap:10px;margin-top:12px}
.slot{padding:14px 8px;border:2px solid var(--border);border-radius:var(--r-sm);
  background:var(--bg-elev);text-align:center;font-size:11px;font-weight:700;
  color:var(--muted);transition:all .2s;position:relative;overflow:hidden;min-height:90px}
.slot.filled{border-color:var(--primary);background:var(--primary-l);color:var(--primary)}
.slot.failed{border-color:var(--danger);background:#fee2e2;color:var(--danger)}
.slot img{max-width:100%;max-height:70px;display:block;margin:0 auto 4px;border-radius:3px}
.slot .num{font-size:16px;display:block;margin-bottom:2px;font-weight:700}
.progress{width:100%;height:8px;background:var(--bg-elev);border-radius:4px;
  overflow:hidden;margin:10px 0}
.progress-bar{height:100%;background:linear-gradient(90deg,var(--primary),var(--primary-h));
  width:0%;transition:width .3s ease}
.split{display:grid;grid-template-columns:1.2fr 1fr;gap:16px}
@media (max-width:1100px){.split{grid-template-columns:1fr}}
pre.log{background:var(--bg-elev);padding:12px;border-radius:var(--r-sm);
  font-family:Consolas,monospace;font-size:11px;max-height:340px;overflow-y:auto;
  color:var(--text);border:1px solid var(--border);white-space:pre-wrap;word-break:break-word}
pre.prompt-box{background:#f0fdf4;border:2px solid var(--primary);padding:16px;
  font-family:Consolas,monospace;font-size:11px;max-height:400px;overflow-y:auto;
  white-space:pre-wrap;color:#1b5e20;border-radius:var(--r-sm);line-height:1.4}
[data-theme=dark] pre.prompt-box{background:#14321e;color:#86efac}
.text-muted{color:var(--muted);font-size:12px}
.text-mono{font-family:Consolas,Monaco,monospace}
.text-sm{font-size:12px}
.hidden{display:none !important}
.mt-8{margin-top:8px}.mt-16{margin-top:16px}.mb-16{margin-bottom:16px}
.flex{display:flex}.flex-between{display:flex;justify-content:space-between;align-items:center}
.info-box{background:var(--primary-l);border-left:4px solid var(--primary);
  padding:16px;border-radius:var(--r-sm);margin-bottom:16px;color:var(--text)}
.info-box h3{color:var(--primary);margin-bottom:8px}
.feature-list{list-style:none;padding:0}
.feature-list li{padding:6px 0;border-bottom:1px dashed var(--border);
  display:flex;align-items:center;gap:8px}
.feature-list li:last-child{border-bottom:none}
.license-badge{display:inline-block;padding:6px 14px;border-radius:20px;
  background:var(--gold);color:#fff;font-weight:700;font-size:12px}
.custom-size-row{display:none;grid-template-columns:1fr 1fr;gap:12px;margin-top:8px}
.custom-size-row.visible{display:grid}
.tax-tabs{display:flex;gap:4px;border-bottom:2px solid var(--border);margin-bottom:16px;
  overflow-x:auto}
.tax-tab{padding:10px 18px;border:none;background:transparent;color:var(--muted);
  font-size:13px;font-weight:600;cursor:pointer;border-bottom:3px solid transparent;
  font-family:inherit;white-space:nowrap}
.tax-tab:hover{background:var(--bg-elev);color:var(--text)}
.tax-tab.active{color:var(--primary);border-bottom-color:var(--primary);background:var(--primary-l)}
.modal{display:none;position:fixed;inset:0;background:rgba(0,0,0,.5);z-index:10000;
  align-items:center;justify-content:center;padding:20px}
.modal.active{display:flex}
.modal-content{background:var(--bg-card);border-radius:var(--r);padding:24px;
  max-width:600px;width:100%;max-height:90vh;overflow-y:auto;box-shadow:var(--shadow-lg)}
.modal-content h2{margin-bottom:16px;font-size:18px}
.modal-actions{display:flex;gap:10px;justify-content:flex-end;margin-top:20px}
.og-preview{border:1px solid var(--border);border-radius:var(--r);overflow:hidden;
  background:var(--bg-card);max-width:500px}
.og-preview .og-img{height:260px;background:var(--bg-elev);display:flex;
  align-items:center;justify-content:center;color:var(--muted);font-size:13px;
  background-size:cover;background-position:center}
.og-preview .og-body{padding:14px}
.og-preview .og-url{font-size:11px;color:var(--muted);text-transform:uppercase;
  letter-spacing:.5px;margin-bottom:6px}
.og-preview .og-title{font-size:16px;font-weight:700;margin-bottom:6px;color:var(--text);
  display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.og-preview .og-desc{font-size:13px;color:var(--muted);line-height:1.4;
  display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.badge-pill{display:inline-block;padding:3px 10px;border-radius:12px;font-size:11px;
  font-weight:700;margin-right:6px}
.badge-ok{background:#dcfce7;color:#166534}
.badge-err{background:#fee2e2;color:#991b1b}
.badge-warn{background:#fef3c7;color:#92400e}
.badge-info{background:#dbeafe;color:#1e40af}
[data-theme=dark] .badge-ok{background:#14321e;color:#86efac}
[data-theme=dark] .badge-err{background:#3b1218;color:#fca5a5}
[data-theme=dark] .badge-warn{background:#3b2506;color:#fcd34d}
[data-theme=dark] .badge-info{background:#172554;color:#93c5fd}
.prompt-target{display:flex;gap:8px;margin-bottom:12px}
.prompt-target select{flex:1;max-width:200px}
.search-bar{display:flex;gap:8px;margin-bottom:16px}
.search-bar input{flex:1}
.alert-strip{padding:12px 16px;border-radius:var(--r-sm);background:#fef3c7;
  color:#92400e;margin-bottom:12px;font-size:13px;display:flex;gap:8px;
  align-items:center}
[data-theme=dark] .alert-strip{background:#3b2506;color:#fcd34d}
.pagination{display:flex;justify-content:center;gap:8px;margin-top:12px}
.pagination button{padding:6px 12px;border:1px solid var(--border);
  background:var(--bg-card);color:var(--text);border-radius:4px;cursor:pointer;
  font-size:12px}
.pagination button:hover{background:var(--primary-l);border-color:var(--primary)}
@media (max-width:992px){
  .grid-4{grid-template-columns:repeat(2,1fr)}
  .grid-3{grid-template-columns:repeat(2,1fr)}
  .slots-grid{grid-template-columns:repeat(3,1fr)}
}
@media (max-width:768px){
  :root{--hh:56px;--th:48px}
  .header{padding:0 12px}.header .logo{font-size:15px}
  .header .subtitle{display:none}
  .main{padding:12px}.card{padding:14px}
  .grid-2,.grid-3,.grid-4,.form-row-2,.form-row-3{grid-template-columns:1fr}
  .slots-grid{grid-template-columns:repeat(2,1fr)}
  .toast-container{top:70px;right:10px;left:10px;max-width:none}
  .tab-btn{padding:0 10px;font-size:12px}
  .tab-btn .label{display:none}
  .tab-btn .emoji{font-size:16px}
  .split{grid-template-columns:1fr}
}
"""


# =============================================================================
# SECTION 5 — HTML BODY (15 TABS)
# =============================================================================
HTML_BODY = r"""
<header class="header">
    <span class="logo">🌿 <span id="store-name-header">Khan Herbal Stores</span></span>
    <span class="subtitle" id="net-info">Web Factory v3.0</span>
    <span class="spacer"></span>
    <span class="badge" id="status-badge">Ready</span>
    <button class="theme-toggle" id="theme-toggle" title="Toggle theme">🌙</button>
</header>

<nav class="tabbar" id="tabbar">
    <button class="tab-btn active" data-tab="connections"><span class="emoji">🔌</span><span class="label">Connections</span></button>
    <button class="tab-btn" data-tab="store"><span class="emoji">⚙️</span><span class="label">Store</span></button>
    <button class="tab-btn" data-tab="products"><span class="emoji">🏭</span><span class="label">Factory</span></button>
    <button class="tab-btn" data-tab="images"><span class="emoji">🖼️</span><span class="label">Images</span></button>
    <button class="tab-btn" data-tab="content"><span class="emoji">📝</span><span class="label">Content</span></button>
    <button class="tab-btn" data-tab="prompts"><span class="emoji">🤖</span><span class="label">AI Prompts</span></button>
    <button class="tab-btn" data-tab="taxonomy"><span class="emoji">🏷️</span><span class="label">Taxonomy</span></button>
    <button class="tab-btn" data-tab="og"><span class="emoji">📱</span><span class="label">Open Graph</span></button>
    <button class="tab-btn" data-tab="blog"><span class="emoji">📰</span><span class="label">Blog Posts</span></button>
    <button class="tab-btn" data-tab="live"><span class="emoji">📦</span><span class="label">Live Products</span></button>
    <button class="tab-btn" data-tab="editor"><span class="emoji">✏️</span><span class="label">Editor</span></button>
    <button class="tab-btn" data-tab="export"><span class="emoji">📤</span><span class="label">Export</span></button>
    <button class="tab-btn" data-tab="testlab"><span class="emoji">🧪</span><span class="label">Test</span></button>
    <button class="tab-btn" data-tab="about"><span class="emoji">ℹ️</span><span class="label">About</span></button>
    <button class="tab-btn" data-tab="log"><span class="emoji">📜</span><span class="label">Log</span></button>
</nav>

<main class="main" id="main">

<!-- ========== TAB 1: CONNECTIONS ========== -->
<section class="tab-content active" id="tab-connections">
    <div class="card">
        <h2>🔵 WordPress Connection</h2>
        <div class="form-row">
            <label>Website URL</label>
            <input type="url" id="wp-url" value="https://darkcyan-turkey-703045.hostingersite.com">
        </div>
        <div class="form-row-2">
            <div class="form-row"><label>Username</label>
                <input type="text" id="wp-user" placeholder="WordPress admin username"></div>
            <div class="form-row"><label>Application Password</label>
                <input type="password" id="wp-pass" placeholder="xxxx xxxx xxxx xxxx xxxx xxxx"></div>
        </div>
        <div class="btn-row">
            <button class="btn btn-primary" onclick="connectWP()">🔗 Connect</button>
            <button class="btn" onclick="testWP()">🧪 Test</button>
            <button class="btn btn-danger" onclick="disconnectWP()">❌ Disconnect</button>
        </div>
        <div class="status hidden" id="wp-status"></div>
    </div>
    <div class="card">
        <h2>🟣 WooCommerce Connection</h2>
        <div class="form-row">
            <label>Website URL</label>
            <input type="url" id="wc-url" value="https://darkcyan-turkey-703045.hostingersite.com">
        </div>
        <div class="form-row-2">
            <div class="form-row"><label>Consumer Key</label>
                <input type="text" id="wc-ck" placeholder="ck_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"></div>
            <div class="form-row"><label>Consumer Secret</label>
                <input type="password" id="wc-cs" placeholder="cs_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"></div>
        </div>
        <div class="form-row">
            <label>Pexels API Key (optional)</label>
            <input type="password" id="pexels-key" placeholder="Optional — free at pexels.com/api">
        </div>
        <div class="btn-row">
            <button class="btn btn-primary" onclick="connectWC()">🔗 Connect</button>
            <button class="btn" onclick="testWC()">🧪 Test</button>
            <button class="btn btn-danger" onclick="disconnectWC()">❌ Disconnect</button>
        </div>
        <div class="status hidden" id="wc-status"></div>
    </div>
</section>

<!-- ========== TAB 2: STORE SETTINGS ========== -->
<section class="tab-content" id="tab-store">
    <div class="card">
        <h2>⚙️ Store Information</h2>
        <p class="text-muted mb-16">This info auto-injects into every product footer, schema, and SEO title.</p>
        <div class="form-row-2">
            <div class="form-row"><label>Store Name *</label>
                <input type="text" id="store-name" placeholder="Khan Herbal Stores"></div>
            <div class="form-row"><label>Tagline</label>
                <input type="text" id="store-tagline" placeholder="Authentic Herbal Remedies"></div>
        </div>
        <div class="form-row"><label>Store Description</label>
            <textarea id="store-description" rows="2"></textarea></div>
        <div class="form-row-2">
            <div class="form-row"><label>Email *</label>
                <input type="email" id="store-email" placeholder="info@example.com"></div>
            <div class="form-row"><label>Phone *</label>
                <input type="tel" id="store-phone" placeholder="+92 300 0000000"></div>
        </div>
        <div class="form-row"><label>WhatsApp</label>
            <input type="tel" id="store-whatsapp" placeholder="+923218224219"></div>
    </div>
    <div class="card">
        <h2>📍 Address</h2>
        <div class="form-row"><label>Address Line 1</label>
            <input type="text" id="store-addr1" placeholder="Main Market"></div>
        <div class="form-row"><label>Address Line 2</label>
            <input type="text" id="store-addr2" placeholder="Optional"></div>
        <div class="form-row-3">
            <div class="form-row"><label>City</label>
                <input type="text" id="store-city" placeholder="Karachi"></div>
            <div class="form-row"><label>State</label>
                <input type="text" id="store-state" placeholder="Sindh"></div>
            <div class="form-row"><label>Postal Code</label>
                <input type="text" id="store-postal" placeholder="74000"></div>
        </div>
        <div class="form-row-2">
            <div class="form-row"><label>Country ISO</label>
                <input type="text" id="store-country" placeholder="PK" maxlength="2"></div>
            <div class="form-row"><label>Business Hours</label>
                <input type="text" id="store-hours" placeholder="Mon-Sat 9am-9pm"></div>
        </div>
    </div>
    <div class="card">
        <h2>🌐 Social Media</h2>
        <div class="form-row-2">
            <div class="form-row"><label>Facebook URL</label>
                <input type="url" id="store-facebook" placeholder="https://facebook.com/yourpage"></div>
            <div class="form-row"><label>Instagram URL</label>
                <input type="url" id="store-instagram" placeholder="https://instagram.com/yourpage"></div>
        </div>
        <div class="form-row-2">
            <div class="form-row"><label>YouTube URL</label>
                <input type="url" id="store-youtube" placeholder="https://youtube.com/@channel"></div>
            <div class="form-row"><label>Twitter URL</label>
                <input type="url" id="store-twitter" placeholder="https://x.com/handle"></div>
        </div>
    </div>
    <div class="card">
        <div class="btn-row">
            <button class="btn btn-primary btn-lg" onclick="saveStoreSettings()">💾 Save Settings</button>
            <button class="btn btn-warn" onclick="resetStoreDefaults()">↩️ Reset</button>
        </div>
        <div class="status hidden" id="store-status"></div>
    </div>
    <div class="card">
        <h2>📦 Configuration Backup</h2>
        <div class="btn-row">
            <button class="btn btn-info" onclick="exportConfig()">📤 Export Config JSON</button>
            <button class="btn btn-info" onclick="document.getElementById('config-import-file').click()">📥 Import Config JSON</button>
            <input type="file" id="config-import-file" accept=".json" style="display:none" onchange="importConfig(event)">
        </div>
        <div class="status info mt-16">🔒 Exported config does NOT include credentials.</div>
    </div>
</section>

<!-- ========== TAB 3: PRODUCT FACTORY ========== -->
<section class="tab-content" id="tab-products">
    <div class="card">
        <h2>🏭 Product Factory</h2>
        <div class="btn-row mb-16">
            <button class="btn btn-primary" onclick="document.getElementById('file-input').click()">📂 Load File (.txt/.csv)</button>
            <button class="btn" onclick="loadDemoProducts()">🎲 Demo (5)</button>
            <button class="btn btn-danger" onclick="clearProducts()">🧹 Clear</button>
            <input type="file" id="file-input" accept=".txt,.csv" style="display:none" onchange="uploadProductsFile(event)">
        </div>
        <div class="form-row"><label>Paste product names (one per line)</label>
            <textarea id="paste-products" rows="6" placeholder="Almond Oil&#10;Olive Oil&#10;Black Seed Oil"></textarea></div>
        <button class="btn" onclick="loadPastedProducts()">➕ Add to list</button>
        <div class="grid-4 mt-16">
            <div class="form-row"><label>Price min (Rs)</label><input type="number" id="price-min" value="199"></div>
            <div class="form-row"><label>Price max (Rs)</label><input type="number" id="price-max" value="999"></div>
            <div class="form-row"><label>In-stock count</label><input type="number" id="stock-count" value="10"></div>
            <div class="form-row"><label>Stock qty</label><input type="number" id="stock-qty" value="25"></div>
        </div>
        <button class="btn btn-primary btn-lg btn-block mt-16" onclick="generateProducts()">⚡ Generate All Products</button>
        <div class="progress hidden" id="gen-progress"><div class="progress-bar"></div></div>
        <div class="status hidden" id="gen-status"></div>
    </div>
    <div class="card">
        <h2>📋 Products (<span id="prod-count">0</span>)</h2>
        <div class="table-wrap">
            <table id="products-table">
                <thead><tr><th>#</th><th>Name</th><th>SKU</th><th>Slug</th><th>Price</th><th>Stock</th><th>Category</th><th>RM</th></tr></thead>
                <tbody></tbody>
            </table>
        </div>
    </div>
</section>

<!-- ========== TAB 4: IMAGE STUDIO ========== -->
<section class="tab-content" id="tab-images">
    <div class="card">
        <h2>🖼️ Image Studio</h2>
        <div class="form-row-2 mb-16">
            <div class="form-row"><label>Select Product</label>
                <select id="img-product" onchange="loadSlots()"></select></div>
            <div class="form-row"><label>Assign to Slot</label>
                <select id="img-slot">
                    <option value="0">Slot 1 — Featured</option>
                    <option value="1">Slot 2 — Gallery</option>
                    <option value="2">Slot 3 — Gallery</option>
                    <option value="3">Slot 4 — Gallery</option>
                    <option value="4">Slot 5 — Gallery</option>
                </select></div>
        </div>
        <div class="dropzone" id="dropzone" onclick="document.getElementById('img-file-input').click()">
            <span class="icon">📥</span>
            <div class="title">Drag & Drop Images Here</div>
            <div class="hint">Click to browse • Ctrl+V to paste</div>
            <input type="file" id="img-file-input" accept="image/*" multiple style="display:none" onchange="handleFiles(event.target.files)">
        </div>
        <div class="btn-row mt-16">
            <button class="btn btn-info" onclick="openGoogleImages()">🔍 Google Images</button>
            <button class="btn btn-info" onclick="openOpenverse()">🖼️ Openverse</button>
            <button class="btn btn-info" onclick="openPexels()">🎨 Pexels</button>
        </div>
        <div class="form-row mt-16">
            <label>Or paste direct image URL</label>
            <div class="flex gap-8" style="gap:8px">
                <input type="url" id="img-url-input" placeholder="https://example.com/image.jpg" style="flex:1">
                <button class="btn btn-primary" onclick="downloadImageUrl()">⬇️ Download</button>
            </div>
        </div>
        <div class="grid-3 mt-16">
            <div class="form-row"><label>Image Size</label>
                <select id="img-size" onchange="toggleCustomSize()">
                    <option>300x300</option><option>600x600</option><option>800x800</option>
                    <option>1200x630</option><option selected>1200x1200</option><option value="Custom">Custom...</option>
                </select></div>
            <div class="form-row"><label>Aspect Ratio</label>
                <select id="img-aspect"><option selected>1:1</option><option>4:3</option><option>16:9</option><option>3:2</option><option>Free</option></select></div>
            <div class="form-row"><label>Object-Fit</label>
                <select id="img-fit"><option selected>cover</option><option>contain</option><option>fill</option><option>none</option><option>scale-down</option></select></div>
        </div>
        <div class="custom-size-row" id="custom-size-row">
            <div class="form-row"><label>Custom Width (px)</label><input type="number" id="img-custom-w" value="1200" min="100" max="4000"></div>
            <div class="form-row"><label>Custom Height (px)</label><input type="number" id="img-custom-h" value="1200" min="100" max="4000"></div>
        </div>
        <div class="form-row mt-16">
            <label>WebP Quality: <span id="quality-display">80</span></label>
            <input type="range" id="img-quality" min="60" max="100" value="80" oninput="document.getElementById('quality-display').textContent = this.value">
        </div>
    </div>
    <div class="card">
        <h2>🎯 Slots Preview</h2>
        <div class="slots-grid" id="slots-grid">
            <div class="slot"><span class="num">1</span>Featured<br><span class="text-muted">empty</span></div>
            <div class="slot"><span class="num">2</span>Gallery<br><span class="text-muted">empty</span></div>
            <div class="slot"><span class="num">3</span>Gallery<br><span class="text-muted">empty</span></div>
            <div class="slot"><span class="num">4</span>Gallery<br><span class="text-muted">empty</span></div>
            <div class="slot"><span class="num">5</span>Gallery<br><span class="text-muted">empty</span></div>
        </div>
        <div class="status info mt-16" id="img-summary">Select a product.</div>
    </div>
</section>

<!-- ========== TAB 5: CONTENT ENGINE ========== -->
<section class="tab-content" id="tab-content">
    <div class="card">
        <h2>📝 Content Engine</h2>
        <div class="form-row-2 mb-16">
            <div class="form-row"><label>Select Product</label>
                <select id="content-product" onchange="loadContentPreview()"></select></div>
            <div class="form-row"><label>RankMath Score</label>
                <input type="text" id="content-score" readonly></div>
        </div>
        <div class="split">
            <div><h3>Article HTML</h3>
                <pre class="log" id="content-article" style="max-height:600px">(select product)</pre></div>
            <div>
                <h3>SEO / RankMath</h3>
                <pre class="log" id="content-seo" style="max-height:250px">—</pre>
                <h3 class="mt-16">Keywords</h3>
                <pre class="log" id="content-keywords" style="max-height:340px">—</pre>
            </div>
        </div>
    </div>
</section>

<!-- ========== TAB 6: AI PROMPT GENERATOR ========== -->
<section class="tab-content" id="tab-prompts">
    <div class="card">
        <h2>🤖 AI Prompt Generator</h2>
        <p class="text-muted mb-16">Generate ready-to-paste prompts for ChatGPT / Claude / Gemini. Paste the AI's JSON response back to validate and import.</p>

        <div class="tax-tabs" style="margin-bottom:16px">
            <button class="tax-tab active" data-prompt-tab="product" onclick="switchPromptTab('product')">📦 Product Prompt</button>
            <button class="tax-tab" data-prompt-tab="blog" onclick="switchPromptTab('blog')">📰 Blog Prompt</button>
        </div>

        <!-- PRODUCT PROMPT -->
        <div id="prompt-product-panel">
            <div class="form-row-2">
                <div class="form-row"><label>Product Name *</label>
                    <input type="text" id="prompt-prod-name" placeholder="Almond Oil"></div>
                <div class="form-row"><label>Use Case</label>
                    <input type="text" id="prompt-prod-usecase" placeholder="hair care" value="hair"></div>
            </div>
            <div class="form-row-2">
                <div class="form-row"><label>Category</label>
                    <input type="text" id="prompt-prod-category" placeholder="Herbal Oils"></div>
                <div class="form-row"><label>Brand</label>
                    <input type="text" id="prompt-prod-brand" placeholder="Khan Herbal Stores"></div>
            </div>
            <div class="form-row"><label>Short Description</label>
                <textarea id="prompt-prod-desc" rows="2" placeholder="Cold-pressed almond oil for hair and skin care"></textarea></div>
            <div class="form-row-2">
                <div class="form-row"><label>AI Format</label>
                    <select id="prompt-prod-ai">
                        <option value="chatgpt">ChatGPT</option>
                        <option value="claude">Claude</option>
                        <option value="gemini">Gemini</option>
                        <option value="groq">Groq</option>
                        <option value="ollama">Ollama</option>
                        <option value="generic">Generic</option>
                    </select></div>
                <div class="form-row" style="display:flex;align-items:flex-end">
                    <button class="btn btn-primary btn-block" onclick="generateProductPrompt()">🎯 Generate Product Prompt</button>
                </div>
            </div>
        </div>

        <!-- BLOG PROMPT -->
        <div id="prompt-blog-panel" class="hidden">
            <div class="form-row"><label>Blog Title *</label>
                <input type="text" id="prompt-blog-title" placeholder="Top 10 Herbal Remedies for Hair Growth"></div>
            <div class="form-row"><label>Blog Topic / Summary</label>
                <textarea id="prompt-blog-topic" rows="2" placeholder="Natural hair growth remedies using traditional herbs"></textarea></div>
            <div class="form-row-2">
                <div class="form-row"><label>Category</label>
                    <input type="text" id="prompt-blog-category" placeholder="Hair Care"></div>
                <div class="form-row"><label>Tags (comma-separated)</label>
                    <input type="text" id="prompt-blog-tags" placeholder="hair, herbs, growth"></div>
            </div>
            <div class="form-row-2">
                <div class="form-row"><label>Target Audience</label>
                    <input type="text" id="prompt-blog-audience" placeholder="women aged 25-45"></div>
                <div class="form-row"><label>AI Format</label>
                    <select id="prompt-blog-ai">
                        <option value="chatgpt">ChatGPT</option>
                        <option value="claude">Claude</option>
                        <option value="gemini">Gemini</option>
                        <option value="groq">Groq</option>
                        <option value="ollama">Ollama</option>
                    </select></div>
            </div>
            <button class="btn btn-primary btn-block" onclick="generateBlogPrompt()">🎯 Generate Blog Prompt</button>
        </div>
    </div>

    <!-- PROMPT OUTPUT -->
    <div class="card hidden" id="prompt-output-card">
        <h2>📋 Step 2 — Copy This Prompt</h2>
        <div class="alert-strip">ℹ️ Paste this prompt into ChatGPT / Claude / Gemini, then copy the JSON output and paste it in Step 3.</div>
        <pre class="prompt-box" id="prompt-output"></pre>
        <div class="btn-row mt-16">
            <button class="btn btn-primary" onclick="copyPromptToClipboard()">📋 Copy to Clipboard</button>
            <button class="btn" onclick="downloadPrompt()">⬇️ Download as .txt</button>
        </div>
    </div>

    <!-- AI RESPONSE INPUT -->
    <div class="card hidden" id="ai-response-card">
        <h2>📥 Step 3 — Paste AI Response (JSON)</h2>
        <div class="form-row"><label>Paste the JSON from AI here</label>
            <textarea id="ai-response-input" rows="10" placeholder='{"article_html": "...", "seo_title": "...", ...}'></textarea></div>
        <div class="btn-row">
            <button class="btn btn-primary" onclick="validateAIResponse()">🔍 Validate JSON</button>
            <button class="btn" onclick="clearAIResponse()">🧹 Clear</button>
        </div>
        <div class="status hidden mt-16" id="ai-validation-status"></div>
    </div>

    <!-- VALIDATION RESULT -->
    <div class="card hidden" id="ai-result-card">
        <h2>✅ Step 4 — Validation Result</h2>
        <pre class="log" id="ai-result-details" style="max-height:400px"></pre>
        <div class="btn-row mt-16">
            <button class="btn btn-primary" id="btn-import-ai" onclick="importAIResponse()">📥 Import to Product</button>
            <button class="btn" onclick="clearAIResponse()">🔄 Try Again</button>
        </div>
    </div>
</section>

<!-- ========== TAB 7: TAXONOMY MANAGER ========== -->
<section class="tab-content" id="tab-taxonomy">
    <div class="card">
        <h2>🏷️ Taxonomy Manager</h2>
        <p class="text-muted mb-16">Manage categories, brands, tags, and attributes on your live site.</p>
        <div class="tax-tabs" id="tax-tabs-bar">
            <button class="tax-tab active" data-tax="wc_categories" onclick="switchTaxonomy('wc_categories')">📂 WC Categories</button>
            <button class="tax-tab" data-tax="wp_categories" onclick="switchTaxonomy('wp_categories')">📂 WP Categories</button>
            <button class="tax-tab" data-tax="brands" onclick="switchTaxonomy('brands')">🏷️ Brands</button>
            <button class="tax-tab" data-tax="wc_tags" onclick="switchTaxonomy('wc_tags')">🔖 Product Tags</button>
            <button class="tax-tab" data-tax="wp_tags" onclick="switchTaxonomy('wp_tags')">🔖 Post Tags</button>
            <button class="tax-tab" data-tax="wc_attributes" onclick="switchTaxonomy('wc_attributes')">⚙️ Attributes</button>
        </div>

        <div class="search-bar">
            <input type="text" id="tax-search" placeholder="Search..." oninput="searchTaxonomy()">
            <button class="btn" onclick="refreshTaxonomy()">🔄 Refresh</button>
            <button class="btn btn-primary" onclick="openTaxCreateModal()">➕ Create New</button>
        </div>

        <div class="table-wrap">
            <table id="tax-table">
                <thead><tr>
                    <th style="width:60px">ID</th><th>Name</th><th>Slug</th>
                    <th style="width:80px">Count</th><th>Parent</th>
                    <th style="width:120px">Actions</th>
                </tr></thead>
                <tbody></tbody>
            </table>
        </div>
        <div class="status info mt-16" id="tax-summary">Loading taxonomy...</div>
    </div>
</section>

<!-- ========== TAB 8: OPEN GRAPH ========== -->
<section class="tab-content" id="tab-og">
    <div class="card">
        <h2>📱 Open Graph Manager</h2>
        <div class="tax-tabs" style="margin-bottom:16px">
            <button class="tax-tab active" data-og-tab="global" onclick="switchOGTab('global')">🌐 Global</button>
            <button class="tax-tab" data-og-tab="product" onclick="switchOGTab('product')">📦 Per Product</button>
            <button class="tax-tab" data-og-tab="generator" onclick="switchOGTab('generator')">🎨 Image Generator</button>
        </div>

        <!-- GLOBAL OG -->
        <div id="og-global-panel">
            <div class="form-row"><label>OG Site Name</label>
                <input type="text" id="og-site-name" placeholder="Khan Herbal Stores" maxlength="30"></div>
            <div class="form-row"><label>OG Title</label>
                <input type="text" id="og-title" placeholder="Khan Herbal Stores — Authentic Herbal Remedies" maxlength="70"></div>
            <div class="form-row"><label>OG Description</label>
                <textarea id="og-description" rows="2" maxlength="160" placeholder="Pakistan's trusted online store for pure, natural and authentic herbal products."></textarea></div>
            <div class="form-row"><label>OG Image URL</label>
                <input type="url" id="og-image" placeholder="https://example.com/og-image.jpg"></div>
            <div class="form-row-3">
                <div class="form-row"><label>OG Type</label>
                    <select id="og-type"><option>website</option><option>article</option></select></div>
                <div class="form-row"><label>OG Locale</label>
                    <input type="text" id="og-locale" value="en_PK"></div>
                <div class="form-row"><label>Twitter Card</label>
                    <select id="og-twitter-card"><option>summary_large_image</option><option>summary</option></select></div>
            </div>
            <div class="form-row-2">
                <div class="form-row"><label>Twitter @Site</label>
                    <input type="text" id="og-twitter-site" placeholder="@khanherbal"></div>
                <div class="form-row"><label>Facebook App ID</label>
                    <input type="text" id="og-fb-app-id" placeholder="optional"></div>
            </div>
            <div class="btn-row mt-16">
                <button class="btn btn-primary" onclick="saveGlobalOG()">💾 Save Global OG</button>
                <button class="btn" onclick="previewGlobalOG()">👁️ Preview</button>
            </div>
        </div>

        <!-- PER PRODUCT OG -->
        <div id="og-product-panel" class="hidden">
            <div class="form-row"><label>Select Product</label>
                <select id="og-product-select" onchange="loadProductOG()"></select></div>
            <div id="og-product-form" class="hidden">
                <div class="form-row"><label>OG Title (override)</label>
                    <input type="text" id="og-prod-title" maxlength="70"></div>
                <div class="form-row"><label>OG Description (override)</label>
                    <textarea id="og-prod-description" rows="2" maxlength="160"></textarea></div>
                <div class="form-row"><label>OG Image (override)</label>
                    <input type="url" id="og-prod-image" placeholder="https://example.com/product.jpg"></div>
                <div class="btn-row mt-16">
                    <button class="btn btn-primary" onclick="saveProductOG()">💾 Save</button>
                    <button class="btn" onclick="resetProductOG()">↩️ Reset to Global</button>
                </div>
            </div>
        </div>

        <!-- IMAGE GENERATOR -->
        <div id="og-generator-panel" class="hidden">
            <div class="form-row"><label>Select Product</label>
                <select id="og-gen-product"></select></div>
            <div class="form-row-2">
                <div class="form-row"><label>Style</label>
                    <select id="og-gen-style">
                        <option value="modern">Modern (green)</option>
                        <option value="minimal">Minimal (white)</option>
                        <option value="bold">Bold (dark green)</option>
                        <option value="gradient">Gradient</option>
                        <option value="photo">Photo</option>
                    </select></div>
                <div class="form-row" style="display:flex;align-items:flex-end">
                    <button class="btn btn-primary btn-block" onclick="generateOGImage()">🎨 Generate OG Image</button>
                </div>
            </div>
            <div class="mt-16" id="og-preview-box"></div>
        </div>

        <!-- LIVE PREVIEW -->
        <div class="mt-16">
            <h3>Live Preview</h3>
            <div class="og-preview" id="og-preview">
                <div class="og-img" id="og-preview-img">(no image)</div>
                <div class="og-body">
                    <div class="og-url" id="og-preview-site">KHANHERBALSTORES.COM</div>
                    <div class="og-title" id="og-preview-title">Title preview</div>
                    <div class="og-desc" id="og-preview-desc">Description preview</div>
                </div>
            </div>
        </div>
    </div>
</section>

<!-- ========== TAB 9: BLOG POSTS ========== -->
<section class="tab-content" id="tab-blog">
    <div class="card">
        <h2>📰 Blog Posts Manager</h2>
        <div class="btn-row mb-16">
            <button class="btn" onclick="loadBlogPosts()">🔄 Load Posts</button>
            <button class="btn btn-primary" onclick="openBlogCreateModal()">➕ New Post</button>
            <input type="text" id="blog-search" placeholder="Search posts..." style="flex:1;max-width:300px" onkeypress="if(event.key==='Enter')loadBlogPosts()">
        </div>
        <div class="table-wrap">
            <table id="blog-table">
                <thead><tr>
                    <th style="width:60px">ID</th><th>Title</th><th>Slug</th>
                    <th style="width:100px">Status</th><th style="width:120px">Date</th>
                    <th style="width:140px">Actions</th>
                </tr></thead>
                <tbody></tbody>
            </table>
        </div>
        <div class="status info mt-16" id="blog-summary">Click "Load Posts" to fetch blog posts.</div>
    </div>
</section>

<!-- ========== TAB 10: LIVE PRODUCTS ========== -->
<section class="tab-content" id="tab-live">
    <div class="card">
        <h2>📦 Live Products Manager</h2>
        <p class="text-muted mb-16">Fetch, update, and delete products already on WooCommerce.</p>
        <div class="btn-row mb-16">
            <button class="btn" onclick="loadLiveProducts()">🔄 Load Products</button>
            <input type="text" id="live-search" placeholder="Search by name or SKU..." style="flex:1;max-width:300px" onkeypress="if(event.key==='Enter')loadLiveProducts()">
            <select id="live-status-filter" style="max-width:150px" onchange="loadLiveProducts()">
                <option value="any">All Status</option>
                <option value="publish">Published</option>
                <option value="draft">Drafts</option>
            </select>
        </div>
        <div class="table-wrap">
            <table id="live-table">
                <thead><tr>
                    <th style="width:60px">ID</th><th>Name</th><th>SKU</th>
                    <th style="width:90px">Price</th><th style="width:70px">Stock</th>
                    <th style="width:90px">Status</th>
                    <th style="width:130px">Actions</th>
                </tr></thead>
                <tbody></tbody>
            </table>
        </div>
        <div class="status info mt-16" id="live-summary">Click "Load Products".</div>
    </div>
</section>

<!-- ========== TAB 11: UNIVERSAL EDITOR ========== -->
<section class="tab-content" id="tab-editor">
    <div class="card">
        <h2>✏️ Universal Content Editor</h2>
        <p class="text-muted mb-16">Edit live products or blog posts. Changes preview before publish.</p>
        <div class="form-row-2">
            <div class="form-row"><label>Content Type</label>
                <select id="editor-type" onchange="toggleEditorType()">
                    <option value="product">Product</option>
                    <option value="post">Blog Post</option>
                </select></div>
            <div class="form-row"><label>Select Item</label>
                <select id="editor-item" onchange="loadEditorItem()"></select></div>
        </div>
        <button class="btn btn-info" onclick="loadEditorList()">🔄 Load List</button>
    </div>
    <div class="card hidden" id="editor-form-card">
        <h2>Editing: <span id="editor-item-name"></span></h2>
        <div class="form-row"><label>Title / Name</label>
            <input type="text" id="editor-title"></div>
        <div class="form-row"><label>Content (HTML)</label>
            <textarea id="editor-content" rows="10" style="font-family:Consolas,monospace;font-size:12px"></textarea></div>
        <div class="form-row-2">
            <div class="form-row"><label>Meta Title</label>
                <input type="text" id="editor-meta-title" maxlength="60"></div>
            <div class="form-row"><label>Meta Description</label>
                <input type="text" id="editor-meta-desc" maxlength="160"></div>
        </div>
        <div class="btn-row">
            <button class="btn" onclick="previewDiff()">👁️ Preview Changes</button>
            <button class="btn btn-primary" onclick="saveEditorChanges()">💾 Publish Changes</button>
            <button class="btn btn-danger" onclick="deleteEditorItem()">🗑️ Delete</button>
        </div>
        <div class="hidden mt-16" id="editor-diff-box">
            <h3>Changes Preview</h3>
            <pre class="log" id="editor-diff-content" style="max-height:400px"></pre>
        </div>
    </div>
</section>

<!-- ========== TAB 12: EXPORT ========== -->
<section class="tab-content" id="tab-export">
    <div class="card">
        <h2>📤 CSV Export</h2>
        <div class="btn-row mb-16">
            <button class="btn btn-primary" onclick="exportCSV(false)">📄 CSV WITHOUT images</button>
            <button class="btn btn-primary" onclick="exportCSV(true)">🖼️ CSV WITH images</button>
        </div>
    </div>
    <div class="card">
        <h2>🚀 Push to Live Site</h2>
        <div class="btn-row mb-16">
            <button class="btn btn-info" onclick="pushImages()">🖼️ Push Images to WP</button>
            <button class="btn btn-info" onclick="pushProducts()">📦 Push Products to WC</button>
        </div>
        <div class="status info">Run push Images FIRST, then Products — so images auto-attach.</div>
    </div>
    <div class="card">
        <h2>🎨 Archive CSS</h2>
        <button class="btn" onclick="downloadArchiveCSS()">💾 Save archive-consistency.css</button>
    </div>
    <div class="progress hidden" id="export-progress"><div class="progress-bar"></div></div>
    <pre class="log hidden" id="export-log"></pre>
</section>

<!-- ========== TAB 13: TEST LAB ========== -->
<section class="tab-content" id="tab-testlab">
    <div class="card">
        <h2>🧪 Test Lab</h2>
        <div class="form-row"><label>Products to publish</label>
            <input type="number" id="test-count" value="5" min="1" max="50"></div>
        <div class="btn-row">
            <button class="btn btn-warn btn-lg" onclick="publishTestProducts()">🚀 Publish Test Products</button>
            <button class="btn" onclick="window.open('https://darkcyan-turkey-703045.hostingersite.com/cart/','_blank')">🛒 Open Cart</button>
        </div>
        <pre class="log hidden mt-16" id="test-log"></pre>
    </div>
</section>

<!-- ========== TAB 14: ABOUT ========== -->
<section class="tab-content" id="tab-about">
    <div class="card">
        <div class="info-box">
            <h3>🌿 Khan Herbal Stores — Web Factory v3.0</h3>
            <p>Complete product factory for herbal e-commerce — 15 tabs, blog posts, taxonomy, AI prompts, open graph, and more.</p>
        </div>
        <div class="flex-between mb-16">
            <div><h3>Version</h3><p class="text-mono">v3.0.0</p></div>
            <div><h3>License</h3><span class="license-badge" id="license-badge">Commercial Single-Site</span></div>
        </div>
    </div>
    <div class="card">
        <h2>🎁 Features</h2>
        <ul class="feature-list">
            <li>✅ 325 products generation</li>
            <li>✅ SEO articles (87% RankMath score)</li>
            <li>✅ Blog post generation (1500+ words)</li>
            <li>✅ AI Prompt Generator (multi-AI)</li>
            <li>✅ Taxonomy Manager (categories/brands/tags/attributes)</li>
            <li>✅ Open Graph Manager (global + per-product)</li>
            <li>✅ Live Products CRUD</li>
            <li>✅ Blog Posts CRUD</li>
            <li>✅ Universal Content Editor</li>
            <li>✅ Image Studio with custom size</li>
            <li>✅ WebP conversion pipeline</li>
            <li>✅ WP Media + WC Product API push</li>
            <li>✅ Dark/Light mode + mobile + WiFi</li>
        </ul>
    </div>
    <div class="card">
        <h2>📋 License</h2>
        <div class="form-row-2">
            <div class="form-row"><label>License Type</label>
                <input type="text" id="license-type"></div>
            <div class="form-row"><label>Licensed To</label>
                <input type="text" id="license-to"></div>
        </div>
        <div class="form-row"><label>License Key</label>
            <input type="text" id="license-key"></div>
        <div class="form-row"><label>Support Email</label>
            <input type="email" id="support-email"></div>
        <button class="btn btn-primary" onclick="saveLicenseInfo()">💾 Save License Info</button>
    </div>
</section>

<!-- ========== TAB 15: LOG ========== -->
<section class="tab-content" id="tab-log">
    <div class="card">
        <h2>📜 Activity Log</h2>
        <div class="table-wrap">
            <table id="log-table">
                <thead><tr><th>Time</th><th>Action</th><th>Result</th><th>Detail</th></tr></thead>
                <tbody></tbody>
            </table>
        </div>
        <div class="btn-row mt-16">
            <button class="btn" onclick="refreshLog()">🔄 Refresh</button>
            <button class="btn btn-danger" onclick="clearLog()">🧹 Clear</button>
        </div>
    </div>
</section>

</main>

<!-- ========== MODALS ========== -->
<div class="modal" id="modal-tax-create">
    <div class="modal-content">
        <h2 id="modal-tax-title">Create New</h2>
        <div class="form-row"><label>Name *</label>
            <input type="text" id="modal-tax-name" placeholder="Category name"></div>
        <div class="form-row"><label>Slug (auto from name)</label>
            <input type="text" id="modal-tax-slug" placeholder="category-slug"></div>
        <div class="form-row" id="modal-tax-parent-row">
            <label>Parent (optional)</label>
            <select id="modal-tax-parent"><option value="0">— None —</option></select></div>
        <div class="form-row"><label>Description</label>
            <textarea id="modal-tax-description" rows="2"></textarea></div>
        <div class="modal-actions">
            <button class="btn" onclick="closeModal('modal-tax-create')">Cancel</button>
            <button class="btn btn-primary" onclick="submitTaxCreate()">✅ Create</button>
        </div>
    </div>
</div>

<div class="modal" id="modal-blog-create">
    <div class="modal-content">
        <h2>📝 New Blog Post</h2>
        <div class="form-row"><label>Title *</label>
            <input type="text" id="modal-blog-title" placeholder="Top 10 Herbal Remedies"></div>
        <div class="form-row"><label>Focus Keyword</label>
            <input type="text" id="modal-blog-kw" placeholder="herbal remedies for hair"></div>
        <div class="form-row-2">
            <div class="form-row"><label>Category</label>
                <input type="text" id="modal-blog-category" placeholder="Hair Care"></div>
            <div class="form-row"><label>Tags</label>
                <input type="text" id="modal-blog-tags" placeholder="hair, herbs"></div>
        </div>
        <div class="alert-strip">ℹ️ The post will be generated using engine templates + RankMath meta. You can edit before publishing.</div>
        <div class="modal-actions">
            <button class="btn" onclick="closeModal('modal-blog-create')">Cancel</button>
            <button class="btn btn-primary" onclick="submitBlogCreate()">✅ Generate & Save Draft</button>
        </div>
    </div>
</div>

<div class="modal" id="modal-confirm-delete">
    <div class="modal-content">
        <h2>⚠️ Confirm Delete</h2>
        <p id="modal-delete-msg">Are you sure you want to delete this item?</p>
        <div class="alert-strip">🛑 This action cannot be undone.</div>
        <div class="modal-actions">
            <button class="btn" onclick="closeModal('modal-confirm-delete')">Cancel</button>
            <button class="btn btn-danger" id="modal-delete-confirm-btn">🗑️ Delete</button>
        </div>
    </div>
</div>

<div class="toast-container" id="toasts"></div>
"""


# =============================================================================
# >>> PART B CONTINUES BELOW (next message) <<<
# =============================================================================
# =============================================================================
# SECTION 6 — JAVASCRIPT (Frontend logic for all 15 tabs)
# =============================================================================
JS = r"""
// ================================================================
// CORE: THEME, TABS, TOASTS, API
// ================================================================
(function initTheme(){
    const t = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', t);
    document.getElementById('theme-toggle').textContent = t==='dark' ? '☀️' : '🌙';
})();
document.getElementById('theme-toggle').addEventListener('click', () => {
    const cur = document.documentElement.getAttribute('data-theme');
    const next = cur==='dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('theme', next);
    document.getElementById('theme-toggle').textContent = next==='dark' ? '☀️' : '🌙';
});

document.querySelectorAll('.tab-btn').forEach(b => {
    b.addEventListener('click', () => {
        const t = b.dataset.tab;
        document.querySelectorAll('.tab-btn').forEach(x => x.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(x => x.classList.remove('active'));
        b.classList.add('active');
        const tab = document.getElementById('tab-'+t);
        if (tab) tab.classList.add('active');
        document.getElementById('main').scrollTop = 0;
        onTabActivate(t);
    });
});

function onTabActivate(tab){
    if (tab === 'log') refreshLog();
    if (tab === 'products') refreshProductsTable();
    if (tab === 'images') refreshImageProductDropdown();
    if (tab === 'content') refreshContentProductDropdown();
    if (tab === 'store' || tab === 'about') loadStoreSettings();
    if (tab === 'taxonomy') refreshTaxonomy();
    if (tab === 'og') loadGlobalOG();
    if (tab === 'blog') {} // manual load
    if (tab === 'live') {} // manual load
    if (tab === 'editor') loadEditorList();
}

function toast(msg, type='ok', dur=4000){
    const c = document.getElementById('toasts');
    const el = document.createElement('div');
    el.className = 'toast ' + (type==='ok' ? '' : type);
    el.innerHTML = `<span>${type==='ok'?'✅':type==='error'?'❌':'⚠️'}</span><span>${msg}</span>`;
    c.appendChild(el);
    setTimeout(()=>{
        el.style.opacity='0'; el.style.transform='translateX(400px)';
        setTimeout(()=>el.remove(), 300);
    }, dur);
}

function setStatus(text, ok=true){
    const b = document.getElementById('status-badge');
    b.textContent = text;
    b.style.color = ok ? 'var(--primary)' : 'var(--danger)';
}
function showStatus(id, msg, type='ok'){
    const el = document.getElementById(id);
    if (!el) return;
    el.className = 'status ' + type;
    el.textContent = (type==='ok'?'✅ ':type==='err'?'❌ ':type==='warn'?'⚠️ ':'ℹ️ ') + msg;
    el.classList.remove('hidden');
}
async function api(url, options={}){
    try {
        const res = await fetch(url, {
            method: options.method || 'POST',
            headers: {'Content-Type':'application/json'},
            body: options.body ? JSON.stringify(options.body) : undefined,
        });
        return await res.json();
    } catch(e){
        return {ok:false, error:'Network: ' + e.message};
    }
}

function openModal(id){ document.getElementById(id).classList.add('active'); }
function closeModal(id){ document.getElementById(id).classList.remove('active'); }

// ================================================================
// TAB 1: CONNECTIONS
// ================================================================
async function connectWP(){
    const d = await api('/api/connect/wp', {body:{
        url: document.getElementById('wp-url').value,
        user: document.getElementById('wp-user').value,
        pass: document.getElementById('wp-pass').value,
    }});
    if (d.ok){ showStatus('wp-status', d.message, 'ok'); toast('WordPress connected'); setStatus('WP ✓'); }
    else { showStatus('wp-status', d.error, 'err'); toast(d.error, 'error'); setStatus('WP ✗', false); }
}
async function testWP(){
    const d = await api('/api/test/wp', {body:{
        url: document.getElementById('wp-url').value,
        user: document.getElementById('wp-user').value,
        pass: document.getElementById('wp-pass').value,
    }});
    if (d.ok) toast('WP valid'); else toast(d.error, 'error');
}
async function disconnectWP(){
    await api('/api/disconnect/wp', {body:{}});
    document.getElementById('wp-pass').value = '';
    document.getElementById('wp-status').classList.add('hidden');
    toast('WP disconnected', 'info'); setStatus('Ready');
}
async function connectWC(){
    const d = await api('/api/connect/wc', {body:{
        url: document.getElementById('wc-url').value,
        ck: document.getElementById('wc-ck').value,
        cs: document.getElementById('wc-cs').value,
        pexels: document.getElementById('pexels-key').value,
    }});
    if (d.ok){ showStatus('wc-status', d.message, 'ok'); toast('WooCommerce connected'); setStatus('WC ✓'); }
    else { showStatus('wc-status', d.error, 'err'); toast(d.error, 'error'); setStatus('WC ✗', false); }
}
async function testWC(){
    const d = await api('/api/test/wc', {body:{
        url: document.getElementById('wc-url').value,
        ck: document.getElementById('wc-ck').value,
        cs: document.getElementById('wc-cs').value,
    }});
    if (d.ok) toast('WC valid'); else toast(d.error, 'error');
}
async function disconnectWC(){
    await api('/api/disconnect/wc', {body:{}});
    document.getElementById('wc-ck').value = ''; document.getElementById('wc-cs').value = '';
    document.getElementById('wc-status').classList.add('hidden');
    toast('WC disconnected', 'info');
}

// ================================================================
// TAB 2: STORE SETTINGS
// ================================================================
async function loadStoreSettings(){
    const d = await api('/api/store/get', {method:'GET'});
    if (!d.ok) return;
    const s = d.store || {};
    const map = {
        'store-name': s.name, 'store-tagline': s.tagline,
        'store-description': s.description, 'store-email': s.email,
        'store-phone': s.phone, 'store-whatsapp': s.whatsapp,
        'store-addr1': s.address_line1, 'store-addr2': s.address_line2,
        'store-city': s.city, 'store-state': s.state,
        'store-postal': s.postal_code, 'store-country': s.country,
        'store-hours': s.business_hours,
        'store-facebook': s.facebook, 'store-instagram': s.instagram,
        'store-youtube': s.youtube, 'store-twitter': s.twitter,
        'license-type': s.license_type, 'license-to': s.license_to,
        'license-key': s.license_key, 'support-email': s.support_email,
    };
    for (const id in map){
        const el = document.getElementById(id);
        if (el) el.value = map[id] || '';
    }
    document.getElementById('store-name-header').textContent = s.name || 'Herbal Store';
    document.getElementById('license-badge').textContent = s.license_type || 'Commercial';
}
async function saveStoreSettings(){
    const store = {
        name: document.getElementById('store-name').value,
        tagline: document.getElementById('store-tagline').value,
        description: document.getElementById('store-description').value,
        email: document.getElementById('store-email').value,
        phone: document.getElementById('store-phone').value,
        whatsapp: document.getElementById('store-whatsapp').value,
        address_line1: document.getElementById('store-addr1').value,
        address_line2: document.getElementById('store-addr2').value,
        city: document.getElementById('store-city').value,
        state: document.getElementById('store-state').value,
        postal_code: document.getElementById('store-postal').value,
        country: document.getElementById('store-country').value,
        business_hours: document.getElementById('store-hours').value,
        facebook: document.getElementById('store-facebook').value,
        instagram: document.getElementById('store-instagram').value,
        youtube: document.getElementById('store-youtube').value,
        twitter: document.getElementById('store-twitter').value,
    };
    const d = await api('/api/store/save', {body: store});
    if (d.ok){
        showStatus('store-status', 'Store settings saved', 'ok');
        toast('Store saved');
        document.getElementById('store-name-header').textContent = store.name || 'Herbal Store';
    } else { showStatus('store-status', d.error, 'err'); }
}
async function resetStoreDefaults(){
    if (!confirm('Reset all store settings to defaults?')) return;
    const d = await api('/api/store/reset', {body:{}});
    if (d.ok){ toast('Reset complete'); loadStoreSettings(); }
}
async function saveLicenseInfo(){
    const d = await api('/api/store/license', {body:{
        license_type: document.getElementById('license-type').value,
        license_to: document.getElementById('license-to').value,
        license_key: document.getElementById('license-key').value,
        support_email: document.getElementById('support-email').value,
    }});
    if (d.ok){ toast('License saved'); loadStoreSettings(); }
}
async function exportConfig(){
    const d = await api('/api/config/export', {method:'GET'});
    if (!d.ok){ toast('Export failed', 'error'); return; }
    const blob = new Blob([JSON.stringify(d.config, null, 2)], {type:'application/json'});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = 'config-' + new Date().toISOString().slice(0,10) + '.json';
    a.click(); URL.revokeObjectURL(url); toast('Config exported');
}
async function importConfig(evt){
    const file = evt.target.files[0]; if (!file) return;
    const text = await file.text();
    let cfg; try { cfg = JSON.parse(text); } catch(e){ toast('Invalid JSON', 'error'); return; }
    const d = await api('/api/config/import', {body:{config: cfg}});
    if (d.ok){ toast('Config imported'); loadStoreSettings(); }
    else toast(d.error || 'Import failed', 'error');
    evt.target.value = '';
}

// ================================================================
// TAB 3: PRODUCT FACTORY
// ================================================================
async function uploadProductsFile(evt){
    const file = evt.target.files[0]; if (!file) return;
    const fd = new FormData(); fd.append('file', file);
    const res = await fetch('/api/products/load', { method:'POST', body:fd });
    const d = await res.json();
    if (d.ok){ toast(`${d.count} products loaded`); refreshProductsTable(); }
    else toast(d.error, 'error');
    evt.target.value = '';
}
async function loadPastedProducts(){
    const text = document.getElementById('paste-products').value;
    if (!text.trim()){ toast('Paste products first', 'warning'); return; }
    const d = await api('/api/products/load-text', {body:{text}});
    if (d.ok){ toast(`${d.count} added`); refreshProductsTable(); document.getElementById('paste-products').value=''; }
}
async function loadDemoProducts(){
    const d = await api('/api/products/load-demo', {body:{}});
    if (d.ok){ toast(`${d.count} demo loaded`); refreshProductsTable(); }
}
async function clearProducts(){
    await api('/api/products/clear', {body:{}});
    toast('Cleared', 'info'); refreshProductsTable();
}
async function generateProducts(){
    const prog = document.getElementById('gen-progress');
    prog.classList.remove('hidden');
    prog.querySelector('.progress-bar').style.width = '30%';
    showStatus('gen-status', 'Generating... (30-60 seconds)', 'info');
    const d = await api('/api/products/generate', {body:{
        price_min: document.getElementById('price-min').value,
        price_max: document.getElementById('price-max').value,
        stock_count: document.getElementById('stock-count').value,
        stock_qty: document.getElementById('stock-qty').value,
    }});
    prog.querySelector('.progress-bar').style.width = '100%';
    setTimeout(()=>prog.classList.add('hidden'), 800);
    if (d.ok){
        showStatus('gen-status', `Generated ${d.count}. RM avg: ${d.avg_score}%, Passing: ${d.passing}`, 'ok');
        toast(`${d.count} generated`);
        refreshProductsTable(); refreshImageProductDropdown(); refreshContentProductDropdown();
    } else { showStatus('gen-status', d.error, 'err'); }
}
async function refreshProductsTable(){
    const d = await api('/api/products/list', {method:'GET'});
    const tbody = document.querySelector('#products-table tbody');
    tbody.innerHTML = '';
    document.getElementById('prod-count').textContent = d.count || 0;
    (d.products || []).forEach(p => {
        const tr = document.createElement('tr');
        tr.innerHTML = `<td>${p.index}</td><td>${p.name}</td><td>${p.sku}</td>
            <td class="text-mono">${p.slug}</td><td>Rs ${p.price.toFixed(2)}</td>
            <td>${p.stock}</td><td>${p.category_name}</td>
            <td style="color:${p.rankmath_score>=70?'var(--primary)':'var(--warn)'};font-weight:700">${p.rankmath_score}%</td>`;
        tbody.appendChild(tr);
    });
}

// ================================================================
// TAB 4: IMAGE STUDIO
// ================================================================
function toggleCustomSize(){
    const sel = document.getElementById('img-size').value;
    const row = document.getElementById('custom-size-row');
    if (sel === 'Custom') row.classList.add('visible'); else row.classList.remove('visible');
}
async function refreshImageProductDropdown(){
    const d = await api('/api/products/list', {method:'GET'});
    const sel = document.getElementById('img-product');
    const cur = sel.value; sel.innerHTML = '';
    if (!d.products || d.products.length === 0){
        sel.innerHTML = '<option value="">(no products — go to Factory)</option>';
        return;
    }
    d.products.forEach(p => {
        const opt = document.createElement('option');
        opt.value = p.name; opt.textContent = `${p.index}. ${p.name}`;
        sel.appendChild(opt);
    });
    if (cur && [...sel.options].some(o=>o.value===cur)) sel.value = cur;
    loadSlots();
}
async function loadSlots(){
    const product = document.getElementById('img-product').value;
    if (!product) return;
    const d = await api('/api/images/slots', {body:{product}});
    if (!d.ok) return;
    const grid = document.getElementById('slots-grid');
    grid.innerHTML = '';
    (d.slots || []).forEach((s, i) => {
        const cls = s.status === 'ok' ? 'filled' : (s.status === 'failed' ? 'failed' : '');
        const imgTag = s.thumb_url ? `<img src="${s.thumb_url}">` : '';
        const label = i === 0 ? 'Featured' : 'Gallery';
        const status = s.status === 'ok' ? '✓' : (s.status === 'failed' ? '✗' : 'empty');
        grid.innerHTML += `<div class="slot ${cls}"><span class="num">${i+1}</span>${imgTag}${label}<br><span class="text-muted">${status}</span></div>`;
    });
    const ok = d.slots.filter(s=>s.status==='ok').length;
    const failed = d.slots.filter(s=>s.status==='failed').length;
    document.getElementById('img-summary').textContent = `${product} — ${ok}/5 complete, ${failed} failed`;
}
const dz = document.getElementById('dropzone');
['dragenter','dragover'].forEach(ev => dz.addEventListener(ev, e => { e.preventDefault(); e.stopPropagation(); dz.classList.add('dragover'); }));
['dragleave','drop'].forEach(ev => dz.addEventListener(ev, e => { e.preventDefault(); e.stopPropagation(); dz.classList.remove('dragover'); }));
dz.addEventListener('drop', async e => {
    const files = e.dataTransfer.files;
    if (files && files.length){ await handleFiles(files); }
    else {
        const u = e.dataTransfer.getData('text/uri-list') || e.dataTransfer.getData('text/plain') || e.dataTransfer.getData('text/html');
        if (u){ const m = u.match(/https?:\/\/[^\s"'<>]+/); if (m){ document.getElementById('img-url-input').value = m[0]; downloadImageUrl(); } }
    }
});
document.addEventListener('paste', async e => {
    if (!document.getElementById('tab-images').classList.contains('active')) return;
    const items = e.clipboardData.items; const files = [];
    for (const it of items){ if (it.type.indexOf('image') !== -1){ const f = it.getAsFile(); if (f) files.push(f); } }
    if (files.length){ e.preventDefault(); await handleFiles(files); }
});
function getImageOptions(){
    let size = document.getElementById('img-size').value;
    if (size === 'Custom'){
        size = document.getElementById('img-custom-w').value + 'x' + document.getElementById('img-custom-h').value;
    }
    return {
        size, aspect: document.getElementById('img-aspect').value,
        fit: document.getElementById('img-fit').value,
        quality: document.getElementById('img-quality').value,
    };
}
async function handleFiles(fileList){
    const product = document.getElementById('img-product').value;
    if (!product){ toast('Select product first', 'warning'); return; }
    const slot = document.getElementById('img-slot').value;
    const opts = getImageOptions();
    for (const file of fileList){
        const fd = new FormData();
        fd.append('file', file); fd.append('product', product); fd.append('slot', slot);
        fd.append('size', opts.size); fd.append('aspect', opts.aspect);
        fd.append('fit', opts.fit); fd.append('quality', opts.quality);
        const res = await fetch('/api/images/upload', { method:'POST', body:fd });
        const d = await res.json();
        if (d.ok) toast(`✅ Slot ${parseInt(slot)+1}: ${file.name}`);
        else toast(d.error || 'Failed', 'error');
    }
    loadSlots();
}
async function downloadImageUrl(){
    const product = document.getElementById('img-product').value;
    if (!product){ toast('Select product', 'warning'); return; }
    const url = document.getElementById('img-url-input').value.trim();
    if (!url){ toast('Paste URL', 'warning'); return; }
    const opts = getImageOptions();
    toast('Downloading...', 'info');
    const d = await api('/api/images/download-url', {body:{
        product, url, slot: document.getElementById('img-slot').value, ...opts
    }});
    if (d.ok){ toast('Downloaded'); document.getElementById('img-url-input').value=''; loadSlots(); }
    else toast(d.error, 'error');
}
function openGoogleImages(){ const p = document.getElementById('img-product').value || 'herbal oil'; window.open('https://www.google.com/search?q='+encodeURIComponent(p+' herbal product')+'&tbm=isch','_blank'); }
function openOpenverse(){ const p = document.getElementById('img-product').value || 'herbal oil'; window.open('https://openverse.org/search/?q='+encodeURIComponent(p),'_blank'); }
function openPexels(){ const p = document.getElementById('img-product').value || 'herbal oil'; window.open('https://www.pexels.com/search/'+encodeURIComponent(p)+'/', '_blank'); }

// ================================================================
// TAB 5: CONTENT ENGINE
// ================================================================
async function refreshContentProductDropdown(){
    const d = await api('/api/products/list', {method:'GET'});
    const sel = document.getElementById('content-product');
    const cur = sel.value; sel.innerHTML = '';
    if (!d.products || d.products.length === 0){
        sel.innerHTML = '<option value="">(no products)</option>'; return;
    }
    d.products.forEach(p => {
        const opt = document.createElement('option');
        opt.value = p.name; opt.textContent = `${p.index}. ${p.name}`;
        sel.appendChild(opt);
    });
    if (cur && [...sel.options].some(o=>o.value===cur)) sel.value = cur;
    loadContentPreview();
}
async function loadContentPreview(){
    const name = document.getElementById('content-product').value;
    if (!name) return;
    const d = await api('/api/content/product', {body:{name}});
    if (!d.ok){ document.getElementById('content-article').textContent = d.error; return; }
    document.getElementById('content-article').textContent = d.article_html || '';
    document.getElementById('content-seo').textContent = d.seo_text || '';
    document.getElementById('content-keywords').textContent = d.keywords_text || '';
    const el = document.getElementById('content-score');
    el.value = d.score + '%' + (d.score >= 70 ? ' ✓ PASS' : ' ⚠ needs work');
    el.style.color = d.score >= 70 ? 'var(--primary)' : 'var(--warn)';
}

// ================================================================
// TAB 6: AI PROMPT GENERATOR
// ================================================================
let currentPrompt = '';
let currentPromptType = 'product';

function switchPromptTab(which){
    document.querySelectorAll('[data-prompt-tab]').forEach(b => b.classList.remove('active'));
    document.querySelector(`[data-prompt-tab="${which}"]`).classList.add('active');
    document.getElementById('prompt-product-panel').classList.toggle('hidden', which !== 'product');
    document.getElementById('prompt-blog-panel').classList.toggle('hidden', which !== 'blog');
    currentPromptType = which;
}

async function generateProductPrompt(){
    const name = document.getElementById('prompt-prod-name').value.trim();
    if (!name){ toast('Product name required', 'warning'); return; }
    const d = await api('/api/prompts/product', {body:{
        product_name: name,
        use_case: document.getElementById('prompt-prod-usecase').value,
        category: document.getElementById('prompt-prod-category').value,
        brand: document.getElementById('prompt-prod-brand').value,
        description: document.getElementById('prompt-prod-desc').value,
        ai_format: document.getElementById('prompt-prod-ai').value,
    }});
    if (!d.ok){ toast(d.error, 'error'); return; }
    currentPrompt = d.prompt;
    document.getElementById('prompt-output').textContent = d.prompt;
    document.getElementById('prompt-output-card').classList.remove('hidden');
    document.getElementById('ai-response-card').classList.remove('hidden');
    document.getElementById('ai-result-card').classList.add('hidden');
    toast(`Prompt ready (${d.prompt.length} chars)`);
    document.getElementById('prompt-output-card').scrollIntoView({behavior:'smooth'});
}
async function generateBlogPrompt(){
    const title = document.getElementById('prompt-blog-title').value.trim();
    if (!title){ toast('Blog title required', 'warning'); return; }
    const d = await api('/api/prompts/blog', {body:{
        blog_title: title,
        blog_topic: document.getElementById('prompt-blog-topic').value,
        category: document.getElementById('prompt-blog-category').value,
        tags: document.getElementById('prompt-blog-tags').value,
        audience: document.getElementById('prompt-blog-audience').value,
        ai_format: document.getElementById('prompt-blog-ai').value,
    }});
    if (!d.ok){ toast(d.error, 'error'); return; }
    currentPrompt = d.prompt;
    document.getElementById('prompt-output').textContent = d.prompt;
    document.getElementById('prompt-output-card').classList.remove('hidden');
    document.getElementById('ai-response-card').classList.remove('hidden');
    document.getElementById('ai-result-card').classList.add('hidden');
    toast(`Blog prompt ready`);
    document.getElementById('prompt-output-card').scrollIntoView({behavior:'smooth'});
}
function copyPromptToClipboard(){
    navigator.clipboard.writeText(currentPrompt).then(() => {
        toast('✅ Copied to clipboard');
    });
}
function downloadPrompt(){
    const blob = new Blob([currentPrompt], {type:'text/plain'});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = 'prompt-' + Date.now() + '.txt';
    a.click(); URL.revokeObjectURL(url);
}
async function validateAIResponse(){
    const txt = document.getElementById('ai-response-input').value.trim();
    if (!txt){ toast('Paste AI response first', 'warning'); return; }
    const d = await api('/api/prompts/validate', {body:{raw: txt}});
    document.getElementById('ai-result-card').classList.remove('hidden');
    if (!d.ok){
        showStatus('ai-validation-status', d.error, 'err');
        document.getElementById('ai-result-details').textContent = d.error;
        document.getElementById('btn-import-ai').disabled = true;
        return;
    }
    showStatus('ai-validation-status', 'JSON parsed successfully', 'ok');
    const v = d.validation || {};
    let out = '=== Validation Report ===\n';
    out += `Valid: ${v.valid ? 'YES ✅' : 'NO ❌'}\n`;
    out += `Word count: ${v.checks?.word_count || 0}\n`;
    out += `Focus keyword: ${v.checks?.focus_keyword || '—'}\n`;
    out += `Keyword density: ${v.checks?.density || 0}%\n`;
    out += `Occurrences: ${v.checks?.keyword_occurrences || 0}\n`;
    out += `SEO title length: ${v.checks?.seo_title_length || 0}\n`;
    out += `Meta desc length: ${v.checks?.meta_description_length || 0}\n`;
    out += `Estimated RankMath: ${v.checks?.estimated_rm_score || 0}%\n`;
    out += `H1/H2/H3: ${v.checks?.h1_count || 0}/${v.checks?.h2_count || 0}/${v.checks?.h3_count || 0}\n`;
    out += `Internal links: ${v.checks?.internal_links || 0}\n`;
    out += '\n=== Errors ===\n' + (v.errors?.length ? v.errors.join('\n') : '(none)');
    out += '\n\n=== Warnings ===\n' + (v.warnings?.length ? v.warnings.join('\n') : '(none)');
    document.getElementById('ai-result-details').textContent = out;
    document.getElementById('btn-import-ai').disabled = !v.valid;
}
function clearAIResponse(){
    document.getElementById('ai-response-input').value = '';
    document.getElementById('ai-result-card').classList.add('hidden');
    document.getElementById('ai-validation-status').classList.add('hidden');
}
async function importAIResponse(){
    const txt = document.getElementById('ai-response-input').value.trim();
    if (!txt) return;
    const d = await api('/api/prompts/import', {body:{
        raw: txt, type: currentPromptType,
    }});
    if (d.ok){ toast('Imported successfully'); }
    else toast(d.error, 'error');
}

// ================================================================
// TAB 7: TAXONOMY
// ================================================================
let currentTaxType = 'wc_categories';
let currentTaxItems = [];

function switchTaxonomy(taxType){
    currentTaxType = taxType;
    document.querySelectorAll('[data-tax]').forEach(b => b.classList.remove('active'));
    document.querySelector(`[data-tax="${taxType}"]`).classList.add('active');
    refreshTaxonomy();
}
async function refreshTaxonomy(){
    const search = document.getElementById('tax-search').value;
    const d = await api('/api/taxonomy/list', {body:{type: currentTaxType, search}});
    if (!d.ok){
        document.getElementById('tax-summary').textContent = '❌ ' + d.error;
        document.querySelector('#tax-table tbody').innerHTML = '';
        return;
    }
    currentTaxItems = d.items || [];
    renderTaxonomyTable();
    document.getElementById('tax-summary').textContent = `${currentTaxItems.length} items loaded (${currentTaxType})`;
}
function searchTaxonomy(){
    clearTimeout(window._taxSearchTimer);
    window._taxSearchTimer = setTimeout(refreshTaxonomy, 300);
}
function renderTaxonomyTable(){
    const tbody = document.querySelector('#tax-table tbody');
    tbody.innerHTML = '';
    currentTaxItems.forEach(item => {
        const id = item.id || 0;
        const name = item.name || '';
        const slug = item.slug || '';
        const count = item.count || 0;
        const parent = item.parent || '—';
        const tr = document.createElement('tr');
        tr.innerHTML = `<td class="text-mono">${id}</td>
            <td>${name}</td><td class="text-mono">${slug}</td>
            <td>${count}</td><td>${parent}</td>
            <td class="row-actions">
                <button onclick="openTaxEditModal(${id})">✏️</button>
                <button class="del" onclick="confirmTaxDelete(${id})">🗑️</button>
            </td>`;
        tbody.appendChild(tr);
    });
}
function openTaxCreateModal(){
    document.getElementById('modal-tax-title').textContent = 'Create New ' + currentTaxType;
    document.getElementById('modal-tax-name').value = '';
    document.getElementById('modal-tax-slug').value = '';
    document.getElementById('modal-tax-description').value = '';
    document.getElementById('modal-tax-parent').value = '0';
    document.getElementById('modal-tax-parent-row').style.display =
        (currentTaxType === 'wc_categories' || currentTaxType === 'wp_categories') ? '' : 'none';
    openModal('modal-tax-create');
}
async function submitTaxCreate(){
    const name = document.getElementById('modal-tax-name').value.trim();
    if (!name){ toast('Name is required', 'warning'); return; }
    const d = await api('/api/taxonomy/create', {body:{
        type: currentTaxType, name,
        slug: document.getElementById('modal-tax-slug').value,
        parent_id: parseInt(document.getElementById('modal-tax-parent').value) || 0,
        description: document.getElementById('modal-tax-description').value,
    }});
    if (d.ok){
        toast('Created: ' + name);
        closeModal('modal-tax-create');
        refreshTaxonomy();
    } else {
        toast(d.error, 'error');
    }
}
function openTaxEditModal(id){ toast('Edit feature — coming in next update', 'info'); }
function confirmTaxDelete(id){
    const item = currentTaxItems.find(x => x.id === id);
    document.getElementById('modal-delete-msg').textContent =
        `Delete "${item?.name || id}"? Used by ${item?.count || 0} items.`;
    document.getElementById('modal-delete-confirm-btn').onclick = async () => {
        const d = await api('/api/taxonomy/delete', {body:{type: currentTaxType, id}});
        if (d.ok){ toast('Deleted'); closeModal('modal-confirm-delete'); refreshTaxonomy(); }
        else toast(d.error, 'error');
    };
    openModal('modal-confirm-delete');
}

// ================================================================
// TAB 8: OPEN GRAPH
// ================================================================
function switchOGTab(which){
    document.querySelectorAll('[data-og-tab]').forEach(b => b.classList.remove('active'));
    document.querySelector(`[data-og-tab="${which}"]`).classList.add('active');
    document.getElementById('og-global-panel').classList.toggle('hidden', which !== 'global');
    document.getElementById('og-product-panel').classList.toggle('hidden', which !== 'product');
    document.getElementById('og-generator-panel').classList.toggle('hidden', which !== 'generator');
    if (which === 'product' || which === 'generator') fillOGProductDropdown();
}
async function loadGlobalOG(){
    const d = await api('/api/og/get', {method:'GET'});
    if (!d.ok) return;
    const og = d.og || {};
    document.getElementById('og-site-name').value = og.site_name || '';
    document.getElementById('og-title').value = og.og_title || '';
    document.getElementById('og-description').value = og.og_description || '';
    document.getElementById('og-image').value = og.og_image || '';
    document.getElementById('og-type').value = og.og_type || 'website';
    document.getElementById('og-locale').value = og.og_locale || 'en_PK';
    document.getElementById('og-twitter-card').value = og.twitter_card || 'summary_large_image';
    document.getElementById('og-twitter-site').value = og.twitter_site || '';
    document.getElementById('og-fb-app-id').value = og.fb_app_id || '';
    updateOGPreview();
}
async function saveGlobalOG(){
    const og = {
        site_name: document.getElementById('og-site-name').value,
        og_title: document.getElementById('og-title').value,
        og_description: document.getElementById('og-description').value,
        og_image: document.getElementById('og-image').value,
        og_type: document.getElementById('og-type').value,
        og_locale: document.getElementById('og-locale').value,
        twitter_card: document.getElementById('og-twitter-card').value,
        twitter_site: document.getElementById('og-twitter-site').value,
        fb_app_id: document.getElementById('og-fb-app-id').value,
    };
    const d = await api('/api/og/save', {body: og});
    if (d.ok){ toast('Global OG saved'); updateOGPreview(); }
    else toast(d.error, 'error');
}
function previewGlobalOG(){ updateOGPreview(); toast('Preview updated'); }
function updateOGPreview(){
    const site = document.getElementById('og-site-name').value || 'Site Name';
    const title = document.getElementById('og-title').value || 'Title';
    const desc = document.getElementById('og-description').value || 'Description';
    const img = document.getElementById('og-image').value;
    document.getElementById('og-preview-site').textContent = site.toUpperCase();
    document.getElementById('og-preview-title').textContent = title;
    document.getElementById('og-preview-desc').textContent = desc;
    const box = document.getElementById('og-preview-img');
    if (img){ box.style.backgroundImage = `url('${img}')`; box.textContent = ''; }
    else { box.style.backgroundImage = ''; box.textContent = '(no image)'; }
}
async function fillOGProductDropdown(){
    const d = await api('/api/products/list', {method:'GET'});
    ['og-product-select','og-gen-product'].forEach(id => {
        const sel = document.getElementById(id);
        if (!sel) return;
        sel.innerHTML = '';
        if (!d.products || !d.products.length){
            sel.innerHTML = '<option value="">(no products)</option>'; return;
        }
        d.products.forEach(p => {
            const opt = document.createElement('option');
            opt.value = p.name; opt.textContent = `${p.index}. ${p.name}`;
            sel.appendChild(opt);
        });
    });
}
async function loadProductOG(){
    const name = document.getElementById('og-product-select').value;
    if (!name) return;
    document.getElementById('og-product-form').classList.remove('hidden');
    const d = await api('/api/og/product-auto', {body:{name}});
    if (d.ok){
        document.getElementById('og-prod-title').value = d.og.title || '';
        document.getElementById('og-prod-description').value = d.og.description || '';
        document.getElementById('og-prod-image').value = d.og.image || '';
    }
}
async function saveProductOG(){ toast('Product OG saved (session)', 'info'); }
async function resetProductOG(){ loadProductOG(); }
async function generateOGImage(){
    const name = document.getElementById('og-gen-product').value;
    if (!name){ toast('Select product', 'warning'); return; }
    const style = document.getElementById('og-gen-style').value;
    toast('Generating...', 'info');
    const d = await api('/api/og/generate-image', {body:{name, style}});
    if (!d.ok){ toast(d.error, 'error'); return; }
    document.getElementById('og-preview-box').innerHTML =
        `<div class="og-preview"><div class="og-img" style="background-image:url('${d.url}');"></div>
         <div class="og-body"><p class="text-muted">Generated (${style})</p></div></div>`;
    toast('✅ OG image generated');
}

// ================================================================
// TAB 9: BLOG POSTS
// ================================================================
async function loadBlogPosts(){
    const search = document.getElementById('blog-search').value;
    const d = await api('/api/blog/list', {body:{search}});
    const tbody = document.querySelector('#blog-table tbody');
    tbody.innerHTML = '';
    if (!d.ok){
        document.getElementById('blog-summary').textContent = '❌ ' + d.error;
        return;
    }
    (d.posts || []).forEach(p => {
        const tr = document.createElement('tr');
        tr.innerHTML = `<td class="text-mono">${p.id}</td>
            <td>${p.title}</td>
            <td class="text-mono">${p.slug}</td>
            <td><span class="badge-pill badge-${p.status==='publish'?'ok':'warn'}">${p.status}</span></td>
            <td class="text-sm">${p.date ? p.date.slice(0,10) : ''}</td>
            <td class="row-actions">
                <button onclick="editBlogPost(${p.id})">✏️</button>
                <button onclick="viewBlogPost('${p.link}')">👁️</button>
                <button class="del" onclick="confirmBlogDelete(${p.id})">🗑️</button>
            </td>`;
        tbody.appendChild(tr);
    });
    document.getElementById('blog-summary').textContent = `${d.posts.length} posts loaded`;
}
async function openBlogCreateModal(){
    document.getElementById('modal-blog-title').value = '';
    document.getElementById('modal-blog-kw').value = '';
    document.getElementById('modal-blog-category').value = '';
    document.getElementById('modal-blog-tags').value = '';
    openModal('modal-blog-create');
}
async function submitBlogCreate(){
    const title = document.getElementById('modal-blog-title').value.trim();
    if (!title){ toast('Title required', 'warning'); return; }
    toast('Generating blog post...', 'info');
    const d = await api('/api/blog/create', {body:{
        title,
        focus_keyword: document.getElementById('modal-blog-kw').value,
        category: document.getElementById('modal-blog-category').value,
        tags: document.getElementById('modal-blog-tags').value,
        status: 'draft',
    }});
    if (d.ok){
        toast(`✅ Post created (ID: ${d.post_id})`);
        closeModal('modal-blog-create');
        loadBlogPosts();
    } else {
        toast(d.error, 'error');
    }
}
function editBlogPost(id){ toast('Edit feature — use Editor tab', 'info'); }
function viewBlogPost(url){ if (url) window.open(url, '_blank'); }
function confirmBlogDelete(id){
    document.getElementById('modal-delete-msg').textContent = `Delete blog post ID ${id}?`;
    document.getElementById('modal-delete-confirm-btn').onclick = async () => {
        const d = await api('/api/blog/delete', {body:{id, force: true}});
        if (d.ok){ toast('Deleted'); closeModal('modal-confirm-delete'); loadBlogPosts(); }
        else toast(d.error, 'error');
    };
    openModal('modal-confirm-delete');
}

// ================================================================
// TAB 10: LIVE PRODUCTS
// ================================================================
async function loadLiveProducts(){
    const search = document.getElementById('live-search').value;
    const status = document.getElementById('live-status-filter').value;
    const d = await api('/api/live/list', {body:{search, status}});
    const tbody = document.querySelector('#live-table tbody');
    tbody.innerHTML = '';
    if (!d.ok){
        document.getElementById('live-summary').textContent = '❌ ' + d.error;
        return;
    }
    (d.products || []).forEach(p => {
        const tr = document.createElement('tr');
        tr.innerHTML = `<td class="text-mono">${p.id}</td>
            <td>${p.name}</td>
            <td class="text-mono">${p.sku}</td>
            <td>Rs ${p.price}</td>
            <td>${p.stock}</td>
            <td><span class="badge-pill badge-${p.status==='publish'?'ok':'warn'}">${p.status}</span></td>
            <td class="row-actions">
                <button onclick="editLiveProduct(${p.id})">✏️</button>
                <button onclick="window.open('${p.permalink}','_blank')">👁️</button>
                <button class="del" onclick="confirmLiveDelete(${p.id})">🗑️</button>
            </td>`;
        tbody.appendChild(tr);
    });
    document.getElementById('live-summary').textContent = `${d.products.length} products loaded`;
}
function editLiveProduct(id){ toast('Switch to Editor tab', 'info'); }
function confirmLiveDelete(id){
    document.getElementById('modal-delete-msg').textContent = `Permanently delete product ID ${id}?`;
    document.getElementById('modal-delete-confirm-btn').onclick = async () => {
        const d = await api('/api/live/delete', {body:{id, force: true}});
        if (d.ok){ toast('Deleted'); closeModal('modal-confirm-delete'); loadLiveProducts(); }
        else toast(d.error, 'error');
    };
    openModal('modal-confirm-delete');
}

// ================================================================
// TAB 11: UNIVERSAL EDITOR
// ================================================================
function toggleEditorType(){ loadEditorList(); }
async function loadEditorList(){
    const type = document.getElementById('editor-type').value;
    const sel = document.getElementById('editor-item');
    sel.innerHTML = '';
    const d = await api('/api/live/list', {body:{status:'any'}});
    if (type === 'product'){
        (d.products || []).forEach(p => {
            const opt = document.createElement('option');
            opt.value = p.id; opt.textContent = `#${p.id} — ${p.name}`;
            sel.appendChild(opt);
        });
    }
}
async function loadEditorItem(){
    const id = document.getElementById('editor-item').value;
    if (!id) return;
    const d = await api('/api/live/get', {body:{id}});
    if (!d.ok){ toast(d.error, 'error'); return; }
    document.getElementById('editor-form-card').classList.remove('hidden');
    document.getElementById('editor-item-name').textContent = d.product.name;
    document.getElementById('editor-title').value = d.product.name;
    document.getElementById('editor-content').value = d.product.description || '';
    document.getElementById('editor-meta-title').value = '';
    document.getElementById('editor-meta-desc').value = '';
    window._editorOriginal = d.product;
}
function previewDiff(){
    const orig = window._editorOriginal || {};
    const newTitle = document.getElementById('editor-title').value;
    const newContent = document.getElementById('editor-content').value;
    let out = '=== CHANGES ===\n\n';
    if (orig.name !== newTitle) out += `Title:\n  OLD: ${orig.name}\n  NEW: ${newTitle}\n\n`;
    if (orig.description !== newContent) out += `Content: CHANGED\n  Old length: ${(orig.description||'').length}\n  New length: ${newContent.length}\n\n`;
    if (out === '=== CHANGES ===\n\n') out += 'No changes detected.';
    document.getElementById('editor-diff-content').textContent = out;
    document.getElementById('editor-diff-box').classList.remove('hidden');
}
async function saveEditorChanges(){
    const id = document.getElementById('editor-item').value;
    if (!id){ toast('Select item', 'warning'); return; }
    const d = await api('/api/live/update', {body:{
        id,
        name: document.getElementById('editor-title').value,
        description: document.getElementById('editor-content').value,
    }});
    if (d.ok){ toast('✅ Updated'); document.getElementById('editor-diff-box').classList.add('hidden'); }
    else toast(d.error, 'error');
}
async function deleteEditorItem(){ toast('Use Live Products tab to delete', 'info'); }

// ================================================================
// TAB 12: EXPORT
// ================================================================
async function exportCSV(withImages){
    const d = await api('/api/export/csv', {body:{with_images: withImages}});
    if (d.ok){
        const blob = new Blob([d.csv], {type:'text/csv'});
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = withImages ? 'products_with_images.csv' : 'products_without_images.csv';
        a.click(); URL.revokeObjectURL(url); toast('CSV downloaded');
    } else toast(d.error, 'error');
}
async function downloadArchiveCSS(){
    const d = await api('/api/export/archive-css', {method:'GET'});
    if (d.ok){
        const blob = new Blob([d.css], {type:'text/css'});
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url; a.download = 'archive-consistency.css';
        a.click(); URL.revokeObjectURL(url); toast('CSS downloaded');
    }
}
async function pushImages(){
    const log = document.getElementById('export-log');
    log.classList.remove('hidden');
    log.textContent = 'Pushing images...';
    const d = await api('/api/push/wp', {body:{}});
    log.textContent = (d.ok ? '✅ ' : '❌ ') + (d.ok ? d.message : d.error);
    if (d.errors?.length) log.textContent += '\n' + d.errors.join('\n');
    if (d.ok) toast(d.message); else toast(d.error, 'error');
}
async function pushProducts(){
    if (!confirm('Push all products as DRAFT?')) return;
    const log = document.getElementById('export-log');
    log.classList.remove('hidden');
    log.textContent = 'Pushing products...';
    const d = await api('/api/push/wc', {body:{}});
    log.textContent = (d.ok ? '✅ ' : '❌ ') + (d.ok ? d.message : d.error);
    if (d.errors?.length) log.textContent += '\n' + d.errors.join('\n');
    if (d.ok) toast(d.message); else toast(d.error, 'error');
}

// ================================================================
// TAB 13: TEST LAB
// ================================================================
async function publishTestProducts(){
    const count = document.getElementById('test-count').value;
    const log = document.getElementById('test-log');
    log.classList.remove('hidden');
    log.textContent = 'Publishing...';
    const d = await api('/api/test/publish', {body:{count}});
    log.textContent = (d.ok ? '✅ ' : '❌ ') + (d.ok ? d.message : d.error);
}

// ================================================================
// TAB 15: LOG
// ================================================================
async function refreshLog(){
    const d = await api('/api/log', {method:'GET'});
    const tbody = document.querySelector('#log-table tbody');
    tbody.innerHTML = '';
    (d.entries || []).slice().reverse().forEach(e => {
        const tr = document.createElement('tr');
        tr.innerHTML = `<td class="text-mono">${e.time}</td><td>${e.action}</td>
            <td>${e.result}</td><td>${e.detail}</td>`;
        tbody.appendChild(tr);
    });
}
async function clearLog(){
    await api('/api/log/clear', {body:{}});
    refreshLog(); toast('Log cleared', 'info');
}

// ================================================================
// INIT
// ================================================================
window.addEventListener('load', async () => {
    const s = await api('/api/status', {method:'GET'});
    if (s.wp_connected) setStatus('WP ✓');
    if (s.wc_connected) setStatus('WC ✓');
    refreshProductsTable();
    refreshImageProductDropdown();
    refreshContentProductDropdown();
    loadStoreSettings();
    loadGlobalOG();
    document.getElementById('net-info').textContent = 'v' + s.version;
});
"""


# =============================================================================
# SECTION 7 — PAGE ROUTE + ALL API ROUTES
# =============================================================================
@app.route("/")
def index():
    html = f"""<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{APP_NAME}</title>
<style>{CSS}</style>
</head>
<body>
{HTML_BODY}
<script>{JS}</script>
</body>
</html>"""
    return Response(html, mimetype="text/html")


@app.route("/api/status", methods=["GET"])
def api_status():
    s = get_session_data()
    return jsonify({
        "wp_connected": s["wp"]["connected"],
        "wc_connected": s["wc"]["connected"],
        "products_count": len(s["built_products"]),
        "version": APP_VERSION,
    })


# ---------- CONNECTIONS ----------
@app.route("/api/connect/wp", methods=["POST"])
def api_connect_wp():
    s = get_session_data()
    d = request.json or {}
    url = (d.get("url") or SITE_URL).rstrip("/")
    user = (d.get("user") or "").strip()
    pw = (d.get("pass") or "").strip()
    if not user or not pw:
        return jsonify({"ok": False, "error": "Username/password required"})
    if not url.startswith("https://"):
        return jsonify({"ok": False, "error": "HTTPS required"})
    try:
        r = requests.get(f"{url}/wp-json/wp/v2/users/me", auth=(user, pw), timeout=15)
        if r.status_code == 200:
            s["wp"].update({"connected": True, "url": url, "user": user, "pass": pw})
            name = r.json().get("name", "?")
            log_activity("wp_connect", "ok", f"user={name}")
            return jsonify({"ok": True, "message": f"Connected as {name}"})
        if r.status_code == 401:
            return jsonify({"ok": False, "error": "Invalid credentials (401)"})
        if r.status_code == 403:
            return jsonify({"ok": False, "error": "Insufficient permissions (403)"})
        return jsonify({"ok": False, "error": f"HTTP {r.status_code}"})
    except Exception as e:
        return jsonify({"ok": False, "error": f"Network: {str(e)[:150]}"})


@app.route("/api/test/wp", methods=["POST"])
def api_test_wp():
    d = request.json or {}
    url = (d.get("url") or SITE_URL).rstrip("/")
    user = (d.get("user") or "").strip()
    pw = (d.get("pass") or "").strip()
    if not user or not pw:
        return jsonify({"ok": False, "error": "Credentials required"})
    try:
        r = requests.get(f"{url}/wp-json/wp/v2/users/me", auth=(user, pw), timeout=15)
        if r.status_code == 200:
            return jsonify({"ok": True, "name": r.json().get("name", "?")})
        return jsonify({"ok": False, "error": f"HTTP {r.status_code}"})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)[:150]})


@app.route("/api/disconnect/wp", methods=["POST"])
def api_disconnect_wp():
    s = get_session_data()
    s["wp"] = {"connected": False, "url": "", "user": "", "pass": ""}
    log_activity("wp_disconnect", "ok")
    return jsonify({"ok": True})


@app.route("/api/connect/wc", methods=["POST"])
def api_connect_wc():
    s = get_session_data()
    d = request.json or {}
    url = (d.get("url") or SITE_URL).rstrip("/")
    ck = (d.get("ck") or "").strip()
    cs = (d.get("cs") or "").strip()
    s["pexels_key"] = (d.get("pexels") or "").strip()
    if not ck.startswith("ck_") or not cs.startswith("cs_"):
        return jsonify({"ok": False, "error": "ck_/cs_ prefix required"})
    if not url.startswith("https://"):
        return jsonify({"ok": False, "error": "HTTPS required"})
    try:
        r = requests.get(f"{url}/wp-json/wc/v3/system_status", auth=(ck, cs), timeout=15)
        if r.status_code == 200:
            s["wc"].update({"connected": True, "url": url, "ck": ck, "cs": cs})
            log_activity("wc_connect", "ok")
            return jsonify({"ok": True, "message": "WooCommerce connected"})
        if r.status_code == 401:
            return jsonify({"ok": False, "error": "Invalid keys (401)"})
        return jsonify({"ok": False, "error": f"HTTP {r.status_code}"})
    except Exception as e:
        return jsonify({"ok": False, "error": f"Network: {str(e)[:150]}"})


@app.route("/api/test/wc", methods=["POST"])
def api_test_wc():
    d = request.json or {}
    url = (d.get("url") or SITE_URL).rstrip("/")
    ck = (d.get("ck") or "").strip()
    cs = (d.get("cs") or "").strip()
    if not ck or not cs:
        return jsonify({"ok": False, "error": "Credentials required"})
    try:
        r = requests.get(f"{url}/wp-json/wc/v3/system_status", auth=(ck, cs), timeout=15)
        if r.status_code == 200: return jsonify({"ok": True})
        return jsonify({"ok": False, "error": f"HTTP {r.status_code}"})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)[:150]})


@app.route("/api/disconnect/wc", methods=["POST"])
def api_disconnect_wc():
    s = get_session_data()
    s["wc"] = {"connected": False, "url": "", "ck": "", "cs": ""}
    log_activity("wc_disconnect", "ok")
    return jsonify({"ok": True})


# ---------- STORE SETTINGS ----------
@app.route("/api/store/get", methods=["GET"])
def api_store_get():
    s = get_session_data()
    return jsonify({"ok": True, "store": s["store"]})


@app.route("/api/store/save", methods=["POST"])
def api_store_save():
    s = get_session_data()
    for k, v in (request.json or {}).items():
        if v is not None: s["store"][k] = v
    if CUSTOM_MODULES and engine: engine.set_store(s["store"])
    log_activity("store_save", "ok", f"name={s['store'].get('name')}")
    return jsonify({"ok": True})


@app.route("/api/store/reset", methods=["POST"])
def api_store_reset():
    s = get_session_data()
    s["store"] = dict(STORE_DEFAULTS)
    if CUSTOM_MODULES and engine: engine.set_store(s["store"])
    log_activity("store_reset", "ok")
    return jsonify({"ok": True})


@app.route("/api/store/license", methods=["POST"])
def api_store_license():
    s = get_session_data()
    d = request.json or {}
    for k in ("license_type", "license_to", "license_key", "support_email"):
        if k in d: s["store"][k] = d[k]
    return jsonify({"ok": True})


@app.route("/api/config/export", methods=["GET"])
def api_config_export():
    s = get_session_data()
    config = {"version": APP_VERSION,
              "exported_at": datetime.datetime.now().isoformat(),
              "store": s["store"], "og_global": s.get("og_global", {}),
              "notes": "Credentials NOT included."}
    return jsonify({"ok": True, "config": config})


@app.route("/api/config/import", methods=["POST"])
def api_config_import():
    s = get_session_data()
    cfg = (request.json or {}).get("config") or {}
    if "store" in cfg:
        for k, v in cfg["store"].items(): s["store"][k] = v
        if CUSTOM_MODULES and engine: engine.set_store(s["store"])
    if "og_global" in cfg:
        s["og_global"] = cfg["og_global"]
    return jsonify({"ok": True})


# ---------- PRODUCTS ----------
def _clean_product_name(line):
    line = line.strip().strip(",")
    line = re.sub(r'^\d+\s+', '', line)
    if line.startswith('"') and line.endswith('"'):
        line = line[1:-1]
    return line.strip()


@app.route("/api/products/load", methods=["POST"])
def api_products_load():
    s = get_session_data()
    if "file" not in request.files:
        return jsonify({"ok": False, "error": "No file"})
    text = request.files["file"].read().decode("utf-8", errors="replace")
    lines = [l for l in text.splitlines() if l.strip()]
    cleaned = [_clean_product_name(l) for l in lines]
    cleaned = [c for c in cleaned if c and not re.match(r'^C\d:', c)]
    s["raw_products"] = cleaned
    return jsonify({"ok": True, "count": len(cleaned)})


@app.route("/api/products/load-text", methods=["POST"])
def api_products_load_text():
    s = get_session_data()
    text = (request.json or {}).get("text", "")
    lines = [l for l in text.splitlines() if l.strip()]
    cleaned = [_clean_product_name(l) for l in lines if _clean_product_name(l)]
    s["raw_products"].extend(cleaned)
    return jsonify({"ok": True, "count": len(cleaned), "total": len(s["raw_products"])})


@app.route("/api/products/load-demo", methods=["POST"])
def api_products_load_demo():
    s = get_session_data()
    demo = ["Almond Oil", "Black Seed Oil", "Olive Oil", "Coconut Oil", "Mustard Oil"]
    s["raw_products"] = demo
    return jsonify({"ok": True, "count": len(demo)})


@app.route("/api/products/clear", methods=["POST"])
def api_products_clear():
    s = get_session_data()
    s["raw_products"] = []; s["built_products"] = []; s["slot_managers"] = {}
    return jsonify({"ok": True})


@app.route("/api/products/list", methods=["GET"])
def api_products_list():
    s = get_session_data()
    summary = []
    for p in s["built_products"]:
        summary.append({"index": p.get("index"), "name": p.get("name"),
                        "sku": p.get("sku"), "slug": p.get("slug"),
                        "price": p.get("price", 0), "stock": p.get("stock", 0),
                        "category_name": p.get("category_name"),
                        "rankmath_score": p.get("rankmath_score", 0)})
    return jsonify({"ok": True, "count": len(summary), "products": summary})


@app.route("/api/products/generate", methods=["POST"])
def api_products_generate():
    s = get_session_data()
    if not CUSTOM_MODULES or not engine:
        return jsonify({"ok": False, "error": "engine.py missing"})
    names = s["raw_products"]
    if not names:
        return jsonify({"ok": False, "error": "Load products first"})
    engine.set_store(s["store"])
    try:
        built = engine.build_all_products(names)
    except Exception as e:
        return jsonify({"ok": False, "error": f"Generation failed: {str(e)[:200]}"})
    d = request.json or {}
    try:
        pmin = int(d.get("price_min") or PRICE_MIN)
        pmax = int(d.get("price_max") or PRICE_MAX)
        stock_count = int(d.get("stock_count") or 10)
        stock_qty = int(d.get("stock_qty") or 25)
    except Exception:
        pmin, pmax, stock_count, stock_qty = PRICE_MIN, PRICE_MAX, 10, 25
    import random as _r
    _r.seed(42)
    for i, p in enumerate(built):
        p["price"] = round(_r.uniform(pmin, pmax), 2)
        p["stock"] = stock_qty if i < stock_count else 0
        p["stock_status"] = "instock" if p["stock"] > 0 else "outofstock"
    s["built_products"] = built
    summary = engine.summarize_scores(built)
    log_activity("generate_products", "ok", f"count={len(built)} avg={summary['avg']}")
    return jsonify({"ok": True, "count": len(built),
                    "avg_score": summary["avg"], "passing": summary["passing"],
                    "failing": summary["failing"]})


# ---------- IMAGES ----------
def _get_slot_manager(product_name):
    s = get_session_data()
    if product_name not in s["slot_managers"]:
        if CUSTOM_MODULES and media:
            s["slot_managers"][product_name] = media.SlotManager(product_name)
        else:
            return None
    return s["slot_managers"][product_name]


@app.route("/api/images/slots", methods=["POST"])
def api_images_slots():
    product = (request.json or {}).get("product", "")
    if not product:
        return jsonify({"ok": False, "error": "Product required"})
    sm = _get_slot_manager(product)
    if sm is None:
        return jsonify({"ok": True, "slots": [{"status":"empty","thumb_url":None} for _ in range(5)]})
    slots = []
    for i in range(5):
        slot = sm.slots[i]
        status = slot.get("status", "empty")
        path = slot.get("path")
        thumb_url = None
        if path and Path(path).exists():
            thumb_url = f"/api/images/thumb?p={base64.urlsafe_b64encode(path.encode()).decode()}"
        slots.append({"status": status, "thumb_url": thumb_url})
    return jsonify({"ok": True, "slots": slots})


@app.route("/api/images/thumb", methods=["GET"])
def api_images_thumb():
    try:
        p = request.args.get("p", "")
        path = base64.urlsafe_b64decode(p.encode()).decode()
        p_path = Path(path)
        if not p_path.exists() or not p_path.is_file():
            return Response("Not found", status=404)
        try: p_path.resolve().relative_to(WORKSPACE.resolve())
        except ValueError: return Response("Forbidden", status=403)
        return send_file(str(p_path), mimetype="image/webp")
    except Exception:
        return Response("Error", status=400)


@app.route("/api/images/upload", methods=["POST"])
def api_images_upload():
    if not CUSTOM_MODULES or not media:
        return jsonify({"ok": False, "error": "media.py missing"})
    if "file" not in request.files:
        return jsonify({"ok": False, "error": "No file"})
    file = request.files["file"]
    product = request.form.get("product", "")
    slot = int(request.form.get("slot", 0))
    size = request.form.get("size", "1200x1200")
    aspect = request.form.get("aspect", "1:1")
    quality = int(request.form.get("quality", 80))
    if not product:
        return jsonify({"ok": False, "error": "Product required"})
    raw_name = f"{uuid.uuid4().hex}_{file.filename}"
    raw_path = UPLOAD_DIR / raw_name
    file.save(str(raw_path))
    try:
        w, h = size.lower().split("x")
        target = (int(w), int(h))
    except Exception:
        target = (1200, 1200)
    try:
        ok, final = media.process_image_pipeline(str(raw_path), target, aspect=aspect, quality=quality)
    except Exception as e:
        return jsonify({"ok": False, "error": f"Processing: {str(e)[:150]}"})
    if not ok: return jsonify({"ok": False, "error": final})
    sm = _get_slot_manager(product)
    if sm is None: return jsonify({"ok": False, "error": "Slot manager unavailable"})
    sm.assign(slot, final)
    return jsonify({"ok": True, "path": final})


@app.route("/api/images/download-url", methods=["POST"])
def api_images_download_url():
    if not CUSTOM_MODULES or not media:
        return jsonify({"ok": False, "error": "media.py missing"})
    d = request.json or {}
    product = d.get("product", "")
    url = d.get("url", "")
    slot = int(d.get("slot", 0))
    size = d.get("size", "1200x1200")
    aspect = d.get("aspect", "1:1")
    quality = int(d.get("quality", 80))
    if not product or not url:
        return jsonify({"ok": False, "error": "Product and URL required"})
    if not url.startswith(("http://", "https://")):
        return jsonify({"ok": False, "error": "URL must be http(s)"})
    ok, result = media.download_from_url(url)
    if not ok: return jsonify({"ok": False, "error": f"Download: {result}"})
    try:
        w, h = size.lower().split("x")
        target = (int(w), int(h))
    except Exception:
        target = (1200, 1200)
    ok, final = media.process_image_pipeline(result, target, aspect=aspect, quality=quality)
    if not ok: return jsonify({"ok": False, "error": final})
    sm = _get_slot_manager(product)
    if sm is None: return jsonify({"ok": False, "error": "Slot manager unavailable"})
    sm.assign(slot, final, url)
    return jsonify({"ok": True, "path": final})


# ---------- CONTENT ----------
@app.route("/api/content/product", methods=["POST"])
def api_content_product():
    s = get_session_data()
    name = (request.json or {}).get("name", "")
    if not name: return jsonify({"ok": False, "error": "Product required"})
    p = next((x for x in s["built_products"] if x["name"] == name), None)
    if not p: return jsonify({"ok": False, "error": "Product not found"})
    rm = p.get("rankmath", {})
    seo_text = (
        f"Focus Keyword:    {p['keywords'].get('focus','')}\n"
        f"SEO Title:        {rm.get('meta:rank_math_title','')}\n"
        f"                  ({len(rm.get('meta:rank_math_title',''))} chars)\n"
        f"Meta Description: {rm.get('meta:rank_math_description','')}\n"
        f"                  ({len(rm.get('meta:rank_math_description',''))} chars)\n"
        f"Canonical URL:    {p.get('canonical_url','')}\n"
        f"Product URL:      {p.get('product_url','')}\n\n"
        f"Word Count:       {p['article'].get('word_count',0)}\n"
        f"Keyword Density:  {p['article'].get('keyword_density',0)}%\n"
        f"RankMath Score:   {p.get('rankmath_score',0)}%"
    )
    kws = p.get("keywords", {})
    kw_lines = []
    for k, v in kws.items():
        if isinstance(v, list):
            kw_lines.append(f"\n{k.upper()}:")
            for item in v: kw_lines.append(f"  • {item}")
        else:
            kw_lines.append(f"\n{k.upper()}: {v}")
    return jsonify({"ok": True, "article_html": p["article"].get("html", ""),
                    "seo_text": seo_text, "keywords_text": "\n".join(kw_lines),
                    "score": p.get("rankmath_score", 0)})


# ---------- AI PROMPTS ----------
@app.route("/api/prompts/product", methods=["POST"])
def api_prompts_product():
    if not CUSTOM_MODULES or not ai_prompts:
        return jsonify({"ok": False, "error": "ai_prompts.py missing"})
    d = request.json or {}
    s = get_session_data()
    if CUSTOM_MODULES and engine: engine.set_store(s["store"])
    pages = engine.SITE_PAGES if engine else {}
    ok, prompt, kw = ai_prompts.build_product_prompt(
        product_name=d.get("product_name", ""),
        store=s["store"], pages=pages,
        category=d.get("category", ""), brand=d.get("brand", ""),
        use_case=d.get("use_case", "wellness"),
        user_description=d.get("description", ""),
        ai_format=d.get("ai_format", "chatgpt"),
    )
    if not ok: return jsonify({"ok": False, "error": prompt})
    return jsonify({"ok": True, "prompt": prompt, "focus_keyword": kw})


@app.route("/api/prompts/blog", methods=["POST"])
def api_prompts_blog():
    if not CUSTOM_MODULES or not ai_prompts:
        return jsonify({"ok": False, "error": "ai_prompts.py missing"})
    d = request.json or {}
    s = get_session_data()
    if CUSTOM_MODULES and engine: engine.set_store(s["store"])
    pages = engine.SITE_PAGES if engine else {}
    ok, prompt, kw = ai_prompts.build_blog_prompt(
        blog_title=d.get("blog_title", ""),
        blog_topic=d.get("blog_topic", ""),
        store=s["store"], pages=pages,
        category=d.get("category", ""), tags=d.get("tags", ""),
        audience=d.get("audience", ""),
        ai_format=d.get("ai_format", "chatgpt"),
    )
    if not ok: return jsonify({"ok": False, "error": prompt})
    return jsonify({"ok": True, "prompt": prompt, "focus_keyword": kw})


@app.route("/api/prompts/validate", methods=["POST"])
def api_prompts_validate():
    if not CUSTOM_MODULES or not ai_prompts:
        return jsonify({"ok": False, "error": "ai_prompts.py missing"})
    raw = (request.json or {}).get("raw", "")
    ok, parsed, err = ai_prompts.parse_ai_response(raw)
    if not ok: return jsonify({"ok": False, "error": err})
    val = ai_prompts.validate_ai_response(parsed, parsed.get("focus_keyword", ""))
    return jsonify({"ok": True, "parsed": parsed, "validation": val})


@app.route("/api/prompts/import", methods=["POST"])
def api_prompts_import():
    if not CUSTOM_MODULES or not ai_prompts:
        return jsonify({"ok": False, "error": "ai_prompts.py missing"})
    d = request.json or {}
    ok, parsed, err = ai_prompts.parse_ai_response(d.get("raw", ""))
    if not ok: return jsonify({"ok": False, "error": err})
    s = get_session_data()
    s.setdefault("ai_responses", []).append({"parsed": parsed, "time": datetime.datetime.now().isoformat()})
    return jsonify({"ok": True, "parsed": parsed})


# ---------- TAXONOMY ----------
@app.route("/api/taxonomy/list", methods=["POST"])
def api_taxonomy_list():
    if not CUSTOM_MODULES or not taxonomy:
        return jsonify({"ok": False, "error": "taxonomy.py missing"})
    s = get_session_data()
    if not s["wc"]["connected"]:
        return jsonify({"ok": False, "error": "Connect WC first"})
    d = request.json or {}
    tax_type = d.get("type", "wc_categories")
    search = d.get("search", "")
    url = s["wc"]["url"]; ck = s["wc"]["ck"]; cs = s["wc"]["cs"]
    ok, items, err = taxonomy.list_all(url, ck, cs, tax_type)
    if not ok: return jsonify({"ok": False, "error": err})
    if search:
        items = [i for i in items if search.lower() in (i.get("name","") or "").lower()]
    return jsonify({"ok": True, "items": items})


@app.route("/api/taxonomy/create", methods=["POST"])
def api_taxonomy_create():
    if not CUSTOM_MODULES or not taxonomy:
        return jsonify({"ok": False, "error": "taxonomy.py missing"})
    s = get_session_data()
    if not s["wc"]["connected"]:
        return jsonify({"ok": False, "error": "Connect WC first"})
    d = request.json or {}
    ok, item, err = taxonomy.create_one(
        s["wc"]["url"], s["wc"]["ck"], s["wc"]["cs"],
        tax_type=d.get("type", "wc_categories"),
        name=d.get("name", ""), slug=d.get("slug") or None,
        parent_id=d.get("parent_id", 0), description=d.get("description", ""),
    )
    if not ok: return jsonify({"ok": False, "error": err})
    return jsonify({"ok": True, "item": item})


@app.route("/api/taxonomy/delete", methods=["POST"])
def api_taxonomy_delete():
    if not CUSTOM_MODULES or not taxonomy:
        return jsonify({"ok": False, "error": "taxonomy.py missing"})
    s = get_session_data()
    if not s["wc"]["connected"]:
        return jsonify({"ok": False, "error": "Connect WC first"})
    d = request.json or {}
    ok, err = taxonomy.delete_one(
        s["wc"]["url"], s["wc"]["ck"], s["wc"]["cs"],
        tax_type=d.get("type", "wc_categories"),
        item_id=d.get("id"),
    )
    if not ok: return jsonify({"ok": False, "error": err})
    return jsonify({"ok": True})


# ---------- OPEN GRAPH ----------
@app.route("/api/og/get", methods=["GET"])
def api_og_get():
    s = get_session_data()
    og = s.get("og_global") or {}
    if not og and CUSTOM_MODULES and open_graph:
        og = open_graph.get_global_defaults()
    return jsonify({"ok": True, "og": og})


@app.route("/api/og/save", methods=["POST"])
def api_og_save():
    s = get_session_data()
    s["og_global"] = request.json or {}
    return jsonify({"ok": True})


@app.route("/api/og/product-auto", methods=["POST"])
def api_og_product_auto():
    s = get_session_data()
    name = (request.json or {}).get("name", "")
    p = next((x for x in s["built_products"] if x["name"] == name), None)
    if not p: return jsonify({"ok": False, "error": "Product not found"})
    if not CUSTOM_MODULES or not open_graph:
        return jsonify({"ok": False, "error": "open_graph.py missing"})
    og = open_graph.auto_fill_og("product", p, s.get("og_global") or {})
    return jsonify({"ok": True, "og": og})


@app.route("/api/og/generate-image", methods=["POST"])
def api_og_generate_image():
    if not CUSTOM_MODULES or not open_graph:
        return jsonify({"ok": False, "error": "open_graph.py missing"})
    s = get_session_data()
    d = request.json or {}
    name = d.get("name", "")
    style = d.get("style", "modern")
    p = next((x for x in s["built_products"] if x["name"] == name), None)
    if not p: return jsonify({"ok": False, "error": "Product not found"})
    ok, path = open_graph.generate_og_for_product(p, s["store"], style=style)
    if not ok: return jsonify({"ok": False, "error": path})
    rel = Path(path).name
    url = f"/api/og/image/{rel}"
    return jsonify({"ok": True, "url": url, "path": path})


@app.route("/api/og/image/<filename>")
def api_og_image(filename):
    try:
        p = WORKSPACE / "og_images" / filename
        if not p.exists(): return Response("Not found", status=404)
        return send_file(str(p), mimetype="image/webp")
    except Exception:
        return Response("Error", status=400)


# ---------- BLOG POSTS ----------
@app.route("/api/blog/list", methods=["POST"])
def api_blog_list():
    s = get_session_data()
    if not s["wp"]["connected"]:
        return jsonify({"ok": False, "error": "Connect WP first"})
    if not CUSTOM_MODULES or not wp_client:
        return jsonify({"ok": False, "error": "wp_client.py missing"})
    d = request.json or {}
    ok, posts, err = wp_client.list_posts(
        s["wp"]["url"], s["wp"]["user"], s["wp"]["pass"],
        search=d.get("search", ""), status="any", per_page=30)
    if not ok: return jsonify({"ok": False, "error": err})
    return jsonify({"ok": True, "posts": posts})


@app.route("/api/blog/create", methods=["POST"])
def api_blog_create():
    s = get_session_data()
    if not s["wp"]["connected"]:
        return jsonify({"ok": False, "error": "Connect WP first"})
    if not CUSTOM_MODULES or not engine or not wp_client:
        return jsonify({"ok": False, "error": "Modules missing"})
    d = request.json or {}
    engine.set_store(s["store"])
    blog = engine.build_blog_dict(
        blog_title=d.get("title", ""),
        focus_keyword=d.get("focus_keyword", ""),
        category=d.get("category", ""),
        tags=d.get("tags", ""),
    )
    if "error" in blog:
        return jsonify({"ok": False, "error": blog["error"]})
    meta = {}
    for k, v in blog["rankmath"].items():
        meta[k.replace("meta:", "")] = v
    ok, post, err = wp_client.create_post(
        s["wp"]["url"], s["wp"]["user"], s["wp"]["pass"],
        title=blog["title"], content=blog["content"],
        status=d.get("status", "draft"), slug=blog["slug"],
        excerpt=blog["excerpt"], meta=meta)
    if not ok: return jsonify({"ok": False, "error": err})
    return jsonify({"ok": True, "post_id": post["id"]})


@app.route("/api/blog/delete", methods=["POST"])
def api_blog_delete():
    s = get_session_data()
    if not s["wp"]["connected"]:
        return jsonify({"ok": False, "error": "Connect WP first"})
    if not CUSTOM_MODULES or not wp_client:
        return jsonify({"ok": False, "error": "wp_client.py missing"})
    d = request.json or {}
    ok, err = wp_client.delete_post(
        s["wp"]["url"], s["wp"]["user"], s["wp"]["pass"],
        d.get("id"), force=d.get("force", True))
    if not ok: return jsonify({"ok": False, "error": err})
    return jsonify({"ok": True})


# ---------- LIVE PRODUCTS ----------
@app.route("/api/live/list", methods=["POST"])
def api_live_list():
    s = get_session_data()
    if not s["wc"]["connected"]:
        return jsonify({"ok": False, "error": "Connect WC first"})
    if not CUSTOM_MODULES or not wp_client:
        return jsonify({"ok": False, "error": "wp_client.py missing"})
    d = request.json or {}
    ok, products, err = wp_client.list_products(
        s["wc"]["url"], s["wc"]["ck"], s["wc"]["cs"],
        search=d.get("search", ""), status=d.get("status", "any"),
        per_page=30)
    if not ok: return jsonify({"ok": False, "error": err})
    return jsonify({"ok": True, "products": products})


@app.route("/api/live/get", methods=["POST"])
def api_live_get():
    s = get_session_data()
    if not s["wc"]["connected"]:
        return jsonify({"ok": False, "error": "Connect WC first"})
    if not CUSTOM_MODULES or not wp_client:
        return jsonify({"ok": False, "error": "wp_client.py missing"})
    d = request.json or {}
    ok, product, err = wp_client.get_product(
        s["wc"]["url"], s["wc"]["ck"], s["wc"]["cs"], d.get("id"))
    if not ok: return jsonify({"ok": False, "error": err})
    return jsonify({"ok": True, "product": product})


@app.route("/api/live/update", methods=["POST"])
def api_live_update():
    s = get_session_data()
    if not s["wc"]["connected"]:
        return jsonify({"ok": False, "error": "Connect WC first"})
    if not CUSTOM_MODULES or not wp_client:
        return jsonify({"ok": False, "error": "wp_client.py missing"})
    d = request.json or {}
    pid = d.pop("id", None)
    if not pid: return jsonify({"ok": False, "error": "Product ID required"})
    ok, product, err = wp_client.update_product(
        s["wc"]["url"], s["wc"]["ck"], s["wc"]["cs"], pid, **d)
    if not ok: return jsonify({"ok": False, "error": err})
    return jsonify({"ok": True, "product": product})


@app.route("/api/live/delete", methods=["POST"])
def api_live_delete():
    s = get_session_data()
    if not s["wc"]["connected"]:
        return jsonify({"ok": False, "error": "Connect WC first"})
    if not CUSTOM_MODULES or not wp_client:
        return jsonify({"ok": False, "error": "wp_client.py missing"})
    d = request.json or {}
    ok, err = wp_client.delete_product(
        s["wc"]["url"], s["wc"]["ck"], s["wc"]["cs"],
        d.get("id"), force=d.get("force", True))
    if not ok: return jsonify({"ok": False, "error": err})
    return jsonify({"ok": True})


# ---------- EXPORT ----------
@app.route("/api/export/csv", methods=["POST"])
def api_export_csv():
    if not CUSTOM_MODULES or not engine:
        return jsonify({"ok": False, "error": "engine.py missing"})
    s = get_session_data()
    products = s["built_products"]
    if not products:
        return jsonify({"ok": False, "error": "No products"})
    with_images = (request.json or {}).get("with_images", False)
    image_map = {}
    if with_images:
        for name, sm in s["slot_managers"].items():
            image_map[name] = getattr(sm, "media_urls", None) or []
    cols, rows = engine.build_csv_data(products, image_map)
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=cols)
    writer.writeheader()
    for row in rows: writer.writerow(row)
    return jsonify({"ok": True, "csv": buf.getvalue()})


@app.route("/api/export/archive-css", methods=["GET"])
def api_export_archive_css():
    if not CUSTOM_MODULES or not engine:
        return jsonify({"ok": False, "error": "engine.py missing"})
    return jsonify({"ok": True, "css": engine.get_archive_css()})


# ---------- PUSH ----------
@app.route("/api/push/wp", methods=["POST"])
def api_push_wp():
    s = get_session_data()
    if not s["wp"]["connected"]:
        return jsonify({"ok": False, "error": "Connect WP first"})
    if not CUSTOM_MODULES or not media:
        return jsonify({"ok": False, "error": "media.py missing"})
    if not s["slot_managers"]:
        return jsonify({"ok": False, "error": "No images assigned"})
    ok_count = fail_count = total_images = 0
    errors = []
    for name, sm in s["slot_managers"].items():
        ok, ids, urls, err = media.upload_gallery_to_wp(
            s["wp"]["url"], s["wp"]["user"], s["wp"]["pass"], sm, name)
        if ok:
            sm.media_ids = ids; sm.media_urls = urls
            total_images += len(ids); ok_count += 1
        else:
            fail_count += 1; errors.append(f"{name}: {err}")
    return jsonify({
        "ok": True,
        "message": f"Pushed {ok_count} products' images ({total_images} files). Failed: {fail_count}",
        "errors": errors[:10],
    })


@app.route("/api/push/wc", methods=["POST"])
def api_push_wc():
    s = get_session_data()
    if not s["wc"]["connected"]:
        return jsonify({"ok": False, "error": "Connect WC first"})
    if not CUSTOM_MODULES or not media:
        return jsonify({"ok": False, "error": "media.py missing"})
    products = s["built_products"]
    if not products:
        return jsonify({"ok": False, "error": "No products"})
    ok_count = fail_count = 0
    errors = []
    for p in products:
        sm = s["slot_managers"].get(p["name"])
        mids = getattr(sm, "media_ids", None) if sm else None
        urls = getattr(sm, "media_urls", None) if sm else None
        ok, data, err = media.push_product_via_wc_api(
            s["wc"]["url"], s["wc"]["ck"], s["wc"]["cs"], p, mids, urls)
        if ok: ok_count += 1
        else: fail_count += 1; errors.append(f"{p['name']}: {err}")
    return jsonify({
        "ok": True,
        "message": f"Pushed {ok_count} products. Failed: {fail_count}",
        "errors": errors[:10],
    })


# ---------- TEST LAB ----------
@app.route("/api/test/publish", methods=["POST"])
def api_test_publish():
    s = get_session_data()
    if not s["wc"]["connected"]:
        return jsonify({"ok": False, "error": "Connect WC first"})
    if not CUSTOM_MODULES or not media:
        return jsonify({"ok": False, "error": "media.py missing"})
    count = int((request.json or {}).get("count", 5))
    try:
        url = f"{s['wc']['url'].rstrip('/')}/wp-json/wc/v3/products"
        r = requests.get(url, auth=(s["wc"]["ck"], s["wc"]["cs"]),
                         params={"status": "draft", "per_page": 100}, timeout=20)
        drafts = r.json() if r.status_code == 200 else []
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})
    if not drafts:
        return jsonify({"ok": False, "error": "No draft products found"})
    pub = 0
    for p in drafts[:count]:
        ok, err = media.publish_product(
            s["wc"]["url"], s["wc"]["ck"], s["wc"]["cs"], p["id"])
        if ok: pub += 1
    return jsonify({"ok": True, "message": f"Published {pub}/{count} products"})


# ---------- LOG ----------
@app.route("/api/log", methods=["GET"])
def api_log():
    s = get_session_data()
    return jsonify({"entries": s["activity_log"]})


@app.route("/api/log/clear", methods=["POST"])
def api_log_clear():
    s = get_session_data()
    s["activity_log"] = []
    return jsonify({"ok": True})


# =============================================================================
# SECTION 8 — NETWORK HELPERS + ENTRY POINT
# =============================================================================
def get_local_ip():
    try:
        sk = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sk.connect(("8.8.8.8", 80))
        ip = sk.getsockname()[0]; sk.close(); return ip
    except Exception:
        return "127.0.0.1"


def open_browser_delayed(port):
    time.sleep(1.5)
    try: webbrowser.open(f"http://127.0.0.1:{port}")
    except Exception: pass


def main():
    if CUSTOM_MODULES and engine:
        engine.set_store(STORE_DEFAULTS)
    port = int(os.environ.get("PORT", DEFAULT_PORT))
    local_ip = get_local_ip()
    print("=" * 70)
    print(f"  🌿 {APP_NAME}  v{APP_VERSION}")
    print("=" * 70)
    print(f"  Local:    http://127.0.0.1:{port}")
    print(f"  Network:  http://{local_ip}:{port}    ← same WiFi")
    print("=" * 70)
    print(f"  Store:    {STORE_DEFAULTS['name']}")
    print(f"  Tabs:     15")
    print("  Ctrl+C to stop")
    print("=" * 70)
    threading.Thread(target=open_browser_delayed, args=(port,), daemon=True).start()
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)


if __name__ == "__main__":
    main()