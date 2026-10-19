# =============================================================================
# patch_credential_persistence.py — Save credentials across app restarts
# =============================================================================
# Uses Windows Credential Manager (via keyring library) to securely store
# WP + WC credentials. Auto-reconnects on app reload.
#
# Changes:
#   requirements_web.txt: + keyring>=24.0.0
#   app_web.py:
#     - Optional keyring import
#     - 3 credential helper functions
#     - 3 new Flask routes (/api/credentials/status|restore|clear)
#     - Save on connect (WP + WC)
#     - UI card in Connections tab
#     - Auto-restore on page load
# =============================================================================

import sys
from pathlib import Path

REQ_FILE = Path("requirements_web.txt")
APP_FILE = Path("app_web.py")


# =============================================================================
# REQUIREMENTS — add keyring
# =============================================================================
def patch_requirements():
    print("\n📄 Patching requirements_web.txt...")
    if not REQ_FILE.exists():
        print("   ❌ Not found")
        return False
    content = REQ_FILE.read_text(encoding="utf-8")
    if "keyring" in content:
        print("   ⚠️  Already patched")
        return True
    if not content.endswith("\n"):
        content += "\n"
    content += "keyring>=24.0.0\n"
    REQ_FILE.write_text(content, encoding="utf-8")
    print("   ✅ Added keyring>=24.0.0")
    return True


# =============================================================================
# KEYRING IMPORT
# =============================================================================
IMPORT_FIND = '''try:
    import requests
except ImportError:
    print("ERROR: requests not installed.")
    sys.exit(1)'''

IMPORT_REPLACE = '''try:
    import requests
except ImportError:
    print("ERROR: requests not installed.")
    sys.exit(1)

# Optional keyring for credential persistence (Windows Credential Manager)
try:
    import keyring
    KEYRING_AVAILABLE = True
except ImportError:
    keyring = None
    KEYRING_AVAILABLE = False
    print("WARNING: keyring not installed. Credential persistence disabled.")
    print("         Run: pip install keyring")'''


# =============================================================================
# CREDENTIAL HELPERS
# =============================================================================
HELPERS = '''# =============================================================================
# SECTION 3.5 — CREDENTIAL PERSISTENCE (keyring)
# =============================================================================
KEYRING_SERVICE = "khan-herbal-factory"
KEYRING_WP_KEY = "wp_credentials"
KEYRING_WC_KEY = "wc_credentials"


def save_credentials_to_keyring(wp_data=None, wc_data=None):
    """Save credentials to Windows Credential Manager (encrypted by OS)."""
    if not KEYRING_AVAILABLE:
        return False, "keyring not installed"
    try:
        if wp_data:
            keyring.set_password(KEYRING_SERVICE, KEYRING_WP_KEY, json.dumps(wp_data))
        if wc_data:
            keyring.set_password(KEYRING_SERVICE, KEYRING_WC_KEY, json.dumps(wc_data))
        return True, ""
    except Exception as e:
        return False, str(e)[:150]


def load_credentials_from_keyring():
    """Load saved credentials. Returns (wp_data, wc_data) — either may be None."""
    if not KEYRING_AVAILABLE:
        return None, None
    wp_data = wc_data = None
    try:
        raw = keyring.get_password(KEYRING_SERVICE, KEYRING_WP_KEY)
        if raw:
            wp_data = json.loads(raw)
    except Exception:
        pass
    try:
        raw = keyring.get_password(KEYRING_SERVICE, KEYRING_WC_KEY)
        if raw:
            wc_data = json.loads(raw)
    except Exception:
        pass
    return wp_data, wc_data


def clear_all_keyring():
    """Delete all saved credentials."""
    if not KEYRING_AVAILABLE:
        return
    for key in (KEYRING_WP_KEY, KEYRING_WC_KEY):
        try:
            keyring.delete_password(KEYRING_SERVICE, key)
        except Exception:
            pass


'''


# =============================================================================
# NEW FLASK ROUTES
# =============================================================================
NEW_ROUTES = '''# ---------- CREDENTIAL PERSISTENCE ----------
@app.route("/api/credentials/status", methods=["GET"])
def api_credentials_status():
    if not KEYRING_AVAILABLE:
        return jsonify({
            "ok": True,
            "keyring_available": False,
            "wp_saved": False, "wp_url": "",
            "wc_saved": False, "wc_url": "",
        })
    wp_data, wc_data = load_credentials_from_keyring()
    return jsonify({
        "ok": True,
        "keyring_available": True,
        "wp_saved": bool(wp_data),
        "wp_url": (wp_data or {}).get("url", ""),
        "wp_user": (wp_data or {}).get("user", ""),
        "wc_saved": bool(wc_data),
        "wc_url": (wc_data or {}).get("url", ""),
    })


@app.route("/api/credentials/restore", methods=["POST"])
def api_credentials_restore():
    if not KEYRING_AVAILABLE:
        return jsonify({"ok": False, "error": "keyring not installed"})
    wp_data, wc_data = load_credentials_from_keyring()
    if not wp_data and not wc_data:
        return jsonify({"ok": False, "error": "No saved credentials"})
    s = get_session_data()
    results = {"wp": False, "wc": False, "wp_error": "", "wc_error": "", "wp_name": ""}

    if wp_data:
        try:
            url = (wp_data.get("url") or "").rstrip("/")
            user = wp_data.get("user") or ""
            pw = wp_data.get("pass") or ""
            if url and user and pw:
                r = requests.get(f"{url}/wp-json/wp/v2/users/me",
                                  auth=(user, pw), timeout=15)
                if r.status_code == 200:
                    s["wp"].update({"connected": True, "url": url,
                                     "user": user, "pass": pw})
                    results["wp"] = True
                    results["wp_name"] = r.json().get("name", "?")
                    log_activity("wp_auto_restore", "ok", f"user={results['wp_name']}")
                else:
                    results["wp_error"] = f"HTTP {r.status_code}"
            else:
                results["wp_error"] = "Incomplete saved data"
        except Exception as e:
            results["wp_error"] = str(e)[:100]

    if wc_data:
        try:
            url = (wc_data.get("url") or "").rstrip("/")
            ck = wc_data.get("ck") or ""
            cs = wc_data.get("cs") or ""
            if url and ck and cs:
                r = requests.get(f"{url}/wp-json/wc/v3/system_status",
                                  auth=(ck, cs), timeout=15)
                if r.status_code == 200:
                    s["wc"].update({"connected": True, "url": url,
                                     "ck": ck, "cs": cs})
                    results["wc"] = True
                    log_activity("wc_auto_restore", "ok")
                else:
                    results["wc_error"] = f"HTTP {r.status_code}"
            else:
                results["wc_error"] = "Incomplete saved data"
        except Exception as e:
            results["wc_error"] = str(e)[:100]

    return jsonify({"ok": True, **results})


@app.route("/api/credentials/clear", methods=["POST"])
def api_credentials_clear():
    if not KEYRING_AVAILABLE:
        return jsonify({"ok": False, "error": "keyring not installed"})
    clear_all_keyring()
    log_activity("credentials_clear", "ok")
    return jsonify({"ok": True})


# ---------- CONNECTIONS ----------'''


# =============================================================================
# WP CONNECT — add save
# =============================================================================
WP_SAVE_FIND = 'log_activity("wp_connect", "ok", f"user={name}")'
WP_SAVE_REPLACE = '''# Auto-save credentials (if remember enabled)
            try:
                if KEYRING_AVAILABLE:
                    save_credentials_to_keyring(
                        wp_data={"url": url, "user": user, "pass": pw})
            except Exception:
                pass
            log_activity("wp_connect", "ok", f"user={name}")'''


# =============================================================================
# WC CONNECT — add save
# =============================================================================
WC_SAVE_FIND = 'log_activity("wc_connect", "ok")'
WC_SAVE_REPLACE = '''# Auto-save credentials (if remember enabled)
            try:
                if KEYRING_AVAILABLE:
                    save_credentials_to_keyring(
                        wc_data={"url": url, "ck": ck, "cs": cs})
            except Exception:
                pass
            log_activity("wc_connect", "ok")'''


# =============================================================================
# UI CARD
# =============================================================================
UI_CARD = '''<section class="tab-content active" id="tab-connections">
    <div class="card" style="border-left:4px solid #f59e0b;">
        <h2>🔑 Credential Persistence</h2>
        <p class="text-muted mb-16">Save credentials securely using Windows Credential Manager. Auto-reconnects on app restart.</p>
        <label style="display:flex;align-items:center;gap:10px;cursor:pointer;margin-bottom:12px;">
            <input type="checkbox" id="remember-creds" checked onchange="toggleRememberCreds()" style="width:auto;margin:0;">
            <span><strong>Remember credentials</strong> &mdash; auto-connect on reload</span>
        </label>
        <div id="creds-status-banner" class="status info">
            &trade; Checking saved credentials...
        </div>
        <div class="btn-row mt-16">
            <button class="btn btn-sm btn-warn" onclick="forgetSavedCreds()">🗑️ Forget Saved Credentials</button>
            <button class="btn btn-sm" onclick="checkSavedCreds()">🔄 Refresh Status</button>
        </div>
    </div>
'''


# =============================================================================
# JS FUNCTIONS
# =============================================================================
JS_HELPERS = '''// ================================================================
// CREDENTIAL PERSISTENCE
// ================================================================
async function checkSavedCreds(){
    const banner = document.getElementById('creds-status-banner');
    if (!banner) return;
    try {
        const d = await api('/api/credentials/status', {method:'GET'});
        if (!d.ok){
            banner.className = 'status err';
            banner.textContent = '❌ Status check failed: ' + (d.error || 'unknown');
            return;
        }
        if (!d.keyring_available){
            banner.className = 'status warn';
            banner.textContent = '⚠️ keyring not installed. Run: pip install keyring';
            return;
        }
        const parts = [];
        if (d.wp_saved) parts.push('WP: ' + (d.wp_url || '') + (d.wp_user ? ' (' + d.wp_user + ')' : ''));
        if (d.wc_saved) parts.push('WC: ' + (d.wc_url || ''));
        if (parts.length === 0){
            banner.className = 'status info';
            banner.textContent = 'ℹ️ No saved credentials';
        } else {
            banner.className = 'status ok';
            banner.innerHTML = '✅ Saved credentials found<br><span class="text-sm" style="font-weight:400">' + parts.join(' • ') + '</span>';
        }
        if (d.wp_saved && d.wp_url) document.getElementById('wp-url').value = d.wp_url;
        if (d.wc_saved && d.wc_url) document.getElementById('wc-url').value = d.wc_url;
    } catch (e) {
        banner.className = 'status err';
        banner.textContent = '❌ Error: ' + e.message;
    }
}

async function autoRestoreCreds(){
    try {
        const status = await api('/api/credentials/status', {method:'GET'});
        if (!status.ok || !status.keyring_available) return;
        if (!status.wp_saved && !status.wc_saved) return;
        showLoading('Restoring saved connections...');
        try {
            const d = await api('/api/credentials/restore', {body:{}});
            if (d.ok){
                const restored = [];
                if (d.wp) { setStatus('WP ✓'); restored.push('WP (' + (d.wp_name || '?') + ')'); }
                if (d.wc) { setStatus('WC ✓'); restored.push('WC'); }
                if (restored.length){
                    toast('✅ Auto-restored: ' + restored.join(' • '), 'ok', 5000);
                }
                if (d.wp_error) toast('WP: ' + d.wp_error, 'warning', 6000);
                if (d.wc_error) toast('WC: ' + d.wc_error, 'warning', 6000);
            }
        } finally {
            hideLoading();
        }
    } catch (e) {
        console.warn('Auto-restore failed', e);
    }
}

async function toggleRememberCreds(){
    const cb = document.getElementById('remember-creds');
    const checked = cb.checked;
    localStorage.setItem('remember_creds', checked ? 'true' : 'false');
    if (!checked){
        if (!confirm('Unchecking will clear all saved credentials. Continue?')){
            cb.checked = true;
            localStorage.setItem('remember_creds', 'true');
            return;
        }
        await forgetSavedCreds(true);
    }
}

async function forgetSavedCreds(silent){
    if (!silent && !confirm('Remove saved credentials from Windows Credential Manager?')) return;
    try {
        const d = await api('/api/credentials/clear', {body:{}});
        if (d.ok){
            if (!silent) toast('✅ Saved credentials cleared');
            const banner = document.getElementById('creds-status-banner');
            if (banner){
                banner.className = 'status info';
                banner.textContent = 'ℹ️ No saved credentials';
            }
        } else {
            toast(d.error || 'Failed to clear', 'error');
        }
    } catch (e) {
        toast('Error: ' + e.message, 'error');
    }
}

'''


# JS INIT ANCHOR
JS_INIT_FIND = '''window.addEventListener('load', async () => {
    const s = await api('/api/status', {method:'GET'});'''

JS_INIT_REPLACE = '''window.addEventListener('load', async () => {
    // Credential persistence — auto-restore first
    try {
        const remember = localStorage.getItem('remember_creds') !== 'false';
        const cb = document.getElementById('remember-creds');
        if (cb) cb.checked = remember;
        if (remember) await autoRestoreCreds();
        await checkSavedCreds();
    } catch (e) {
        console.warn('Credential persistence init failed', e);
    }
    
    const s = await api('/api/status', {method:'GET'});'''


# =============================================================================
# PATCHER
# =============================================================================
def patch_app():
    print("\n📄 Patching app_web.py...")
    if not APP_FILE.exists():
        print("   ❌ app_web.py not found")
        return False

    content = APP_FILE.read_text(encoding="utf-8")

    # Check already patched
    if "KEYRING_AVAILABLE" in content and "/api/credentials/restore" in content:
        print("   ⚠️  Already patched. Skipping.")
        return True

    # Pre-check markers
    print("   🔍 Pre-checking markers...")
    markers = {
        "import block": IMPORT_FIND,
        "before index route": '@app.route("/")\ndef index():',
        "CONNECTIONS comment": "# ---------- CONNECTIONS ----------",
        "WP connect save": WP_SAVE_FIND,
        "WC connect save": WC_SAVE_FIND,
        "UI anchor": '<section class="tab-content active" id="tab-connections">',
        "JS init anchor": JS_INIT_FIND,
        "TOAST marker": "function toast(msg, type='ok', dur=4000){",
    }
    missing = []
    for name, m in markers.items():
        if m in content:
            print(f"   ✅ {name}")
        else:
            print(f"   ❌ {name}")
            missing.append(name)

    if missing:
        print(f"\n   ❌ {len(missing)} missing — ABORTING")
        return False

    # Backup
    backup = APP_FILE.with_suffix(".py.bak")
    backup.write_text(content, encoding="utf-8")
    print(f"\n   ✅ Backup: {backup}\n")

    # 1. Import
    content = content.replace(IMPORT_FIND, IMPORT_REPLACE, 1)
    print("   ✅ [1/7] keyring import added")

    # 2. Helpers before index route
    content = content.replace('@app.route("/")\ndef index():',
        HELPERS + '@app.route("/")\ndef index():', 1)
    print("   ✅ [2/7] Credential helpers added")

    # 3. Routes
    content = content.replace("# ---------- CONNECTIONS ----------",
        NEW_ROUTES, 1)
    print("   ✅ [3/7] Credential routes added")

    # 4. WP connect save
    if WP_SAVE_FIND in content:
        content = content.replace(WP_SAVE_FIND, WP_SAVE_REPLACE, 1)
        print("   ✅ [4/7] WP connect auto-save")
    else:
        print("   ⚠️  [4/7] WP save marker gone (skipping)")

    # 5. WC connect save
    if WC_SAVE_FIND in content:
        content = content.replace(WC_SAVE_FIND, WC_SAVE_REPLACE, 1)
        print("   ✅ [5/7] WC connect auto-save")
    else:
        print("   ⚠️  [5/7] WC save marker gone (skipping)")

    # 6. UI card
    content = content.replace(
        '<section class="tab-content active" id="tab-connections">',
        UI_CARD, 1)
    print("   ✅ [6/7] UI card added")

    # 7. JS helpers + init modification
    toast_pos = content.find("function toast(msg, type='ok', dur=4000){")
    if toast_pos != -1:
        content = content[:toast_pos] + JS_HELPERS + content[toast_pos:]
        print("   ✅ [7a/7] JS functions added")

    content = content.replace(JS_INIT_FIND, JS_INIT_REPLACE, 1)
    print("   ✅ [7b/7] Init auto-restore added")

    APP_FILE.write_text(content, encoding="utf-8")
    print(f"\n   ✅ app_web.py saved ({len(content.splitlines())} lines)")
    return True


def main():
    print("=" * 60)
    print("  Credential Persistence Patch")
    print("=" * 60)

    ok_req = patch_requirements()
    ok_app = patch_app()

    print("\n" + "=" * 60)
    if ok_req and ok_app:
        print("  ✅ PATCH COMPLETE")
        print("=" * 60)
        print("\nNext:")
        print("  1. pip install keyring")
        print("  2. python -c \"import ast; ast.parse(open('app_web.py', encoding='utf-8').read()); print('Syntax OK')\"")
        print("  3. python app_web.py")
        print("  4. Connect WP + WC → credentials saved")
        print("  5. Reload page → auto-reconnect ✅")
        return 0
    print("  ❌ PATCH FAILED")
    print("=" * 60)
    return 1


if __name__ == "__main__":
    sys.exit(main())