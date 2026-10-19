# =============================================================================
# patch_og_complete_fix.py — Combined Part 5 + CSS fix (absolute positioning)
# =============================================================================

import sys
from pathlib import Path

APP_FILE = Path("app_web.py")

# Session og_products
SESS_FIND = '''            "og_global": {},
            "blog_drafts": [],'''
SESS_REPLACE = '''            "og_global": {},
            "og_products": {},
            "blog_drafts": [],'''

# New preview JS with absolute positioning (fixes invisible image bug)
NEW_PREVIEW_JS = r'''function getOGPreviewData(){
    const activeTabEl = document.querySelector('[data-og-tab].active');
    const activeTab = activeTabEl ? activeTabEl.dataset.ogTab : 'global';
    const site = (document.getElementById('og-site-name')?.value || 'Khan Herbal Stores');
    const globalTitle = document.getElementById('og-title')?.value || '';
    const globalDesc = document.getElementById('og-description')?.value || '';
    const globalImg = document.getElementById('og-image')?.value || '';
    if (activeTab === 'product'){
        return {
            site,
            title: document.getElementById('og-prod-title')?.value || globalTitle || '(product title)',
            desc: document.getElementById('og-prod-description')?.value || globalDesc || '(product description)',
            img: document.getElementById('og-prod-image')?.value || globalImg,
        };
    }
    if (activeTab === 'generator'){
        return {
            site,
            title: globalTitle || '(title)',
            desc: globalDesc || '(description)',
            img: window._lastGeneratedOG || globalImg,
        };
    }
    return { site, title: globalTitle || '(title)', desc: globalDesc || '(description)', img: globalImg };
}

function refreshOGPreview(){
    const data = getOGPreviewData();
    const siteEl = document.getElementById('og-preview-site');
    const titleEl = document.getElementById('og-preview-title');
    const descEl = document.getElementById('og-preview-desc');
    const box = document.getElementById('og-preview-img');
    if (siteEl) siteEl.textContent = (data.site || 'SITE').toUpperCase();
    if (titleEl) titleEl.textContent = data.title;
    if (descEl) descEl.textContent = data.desc;
    if (!box) return;
    box.style.position = 'relative';
    box.style.overflow = 'hidden';
    box.style.background = '';
    box.style.backgroundImage = '';
    box.style.color = '';
    box.style.fontSize = '';
    box.style.display = 'block';
    box.innerHTML = '';
    console.log('[OG Preview] data.img =', data.img);
    if (data.img){
        const img = document.createElement('img');
        img.alt = 'OG preview';
        img.style.cssText = 'position:absolute;top:0;left:0;width:100%;height:100%;object-fit:cover;display:block;';
        img.onload = function(){ console.log('[OG Preview] Loaded:', data.img, img.naturalWidth + 'x' + img.naturalHeight); };
        img.onerror = function(){
            console.warn('[OG Preview] Failed:', data.img);
            if (img.parentNode) img.parentNode.removeChild(img);
            box.style.display = 'flex';
            box.style.alignItems = 'center';
            box.style.justifyContent = 'center';
            box.style.background = '#fee2e2';
            box.style.color = '#dc2626';
            box.style.fontSize = '12px';
            box.textContent = 'Image failed: ' + String(data.img).substring(0, 60);
        };
        box.appendChild(img);
        img.src = data.img;
    } else {
        box.style.display = 'flex';
        box.style.alignItems = 'center';
        box.style.justifyContent = 'center';
        box.style.color = 'var(--muted)';
        box.style.fontSize = '13px';
        box.textContent = '(no image URL)';
    }
}

function updateOGPreview(){ refreshOGPreview(); }
'''

SWITCH_OG_FIND = '''    if (which === 'product' || which === 'generator') fillOGProductDropdown();
}'''
SWITCH_OG_REPLACE = '''    if (which === 'product' || which === 'generator') fillOGProductDropdown();
    refreshOGPreview();
}'''

LOAD_PROD_OG_NEW = r'''async function loadProductOG(){
    const name = document.getElementById('og-product-select').value;
    if (!name) return;
    document.getElementById('og-product-form').classList.remove('hidden');
    ['og-prod-title', 'og-prod-description', 'og-prod-image'].forEach(id => {
        const el = document.getElementById(id);
        if (el && !el._ogWired){
            el.addEventListener('input', refreshOGPreview);
            el._ogWired = true;
        }
    });
    const d = await api('/api/og/product-get', {body:{name}});
    if (d.ok){
        document.getElementById('og-prod-title').value = d.og.title || '';
        document.getElementById('og-prod-description').value = d.og.description || '';
        document.getElementById('og-prod-image').value = d.og.image || '';
    }
    refreshOGPreview();
}'''

SAVE_PROD_OG_NEW = r'''async function saveProductOG(){
    const name = document.getElementById('og-product-select').value;
    if (!name){ toast('Select a product first', 'warning'); return; }
    const d = await api('/api/og/product-save', {body:{
        name,
        title: document.getElementById('og-prod-title').value,
        description: document.getElementById('og-prod-description').value,
        image: document.getElementById('og-prod-image').value,
    }});
    if (d.ok){ toast('Product OG saved'); }
    else { toast(d.error || 'Save failed', 'error'); }
}'''

RESET_PROD_OG_NEW = r'''async function resetProductOG(){
    const name = document.getElementById('og-product-select').value;
    if (!name){ toast('Select a product', 'warning'); return; }
    await api('/api/og/product-reset', {body:{name}});
    const d = await api('/api/og/product-get', {body:{name}});
    if (d.ok){
        document.getElementById('og-prod-title').value = d.og.title || '';
        document.getElementById('og-prod-description').value = d.og.description || '';
        document.getElementById('og-prod-image').value = d.og.image || '';
    }
    refreshOGPreview();
    toast('Reset to auto-filled values', 'info');
}'''

GEN_OG_NEW = r'''async function generateOGImage(){
    const name = document.getElementById('og-gen-product').value;
    if (!name){ toast('Select product', 'warning'); return; }
    const style = document.getElementById('og-gen-style').value;
    toast('Generating...', 'info');
    const d = await api('/api/og/generate-image', {body:{name, style}});
    if (!d.ok){ toast(d.error, 'error'); return; }
    window._lastGeneratedOG = d.url;
    document.getElementById('og-preview-box').innerHTML =
        '<div class="og-preview"><div class="og-img" style="background-image:url(\'' + d.url + '\');background-size:cover;background-position:center;"></div>' +
        '<div class="og-body"><p class="text-muted">Generated (' + style + ')</p></div></div>';
    refreshOGPreview();
    toast('OG image generated');
}'''

NEW_FLASK_ROUTES = '''@app.route("/api/og/product-get", methods=["POST"])
def api_og_product_get():
    s = get_session_data()
    name = (request.json or {}).get("name", "")
    if not name:
        return jsonify({"ok": False, "error": "Name required"})
    saved = (s.get("og_products") or {}).get(name)
    if saved:
        return jsonify({"ok": True, "og": saved, "source": "saved"})
    p = next((x for x in s["built_products"] if x["name"] == name), None)
    if not p:
        return jsonify({"ok": True, "og": {}, "source": "auto"})
    if CUSTOM_MODULES and open_graph:
        og = open_graph.auto_fill_og("product", p, s.get("og_global") or {})
    else:
        og = {}
    return jsonify({"ok": True, "og": og, "source": "auto"})


@app.route("/api/og/product-save", methods=["POST"])
def api_og_product_save():
    s = get_session_data()
    d = request.json or {}
    name = d.get("name", "")
    if not name:
        return jsonify({"ok": False, "error": "Name required"})
    s.setdefault("og_products", {})
    s["og_products"][name] = {
        "title": d.get("title", ""),
        "description": d.get("description", ""),
        "image": d.get("image", ""),
    }
    log_activity("og_product_save", "ok", f"name={name}")
    return jsonify({"ok": True})


@app.route("/api/og/product-reset", methods=["POST"])
def api_og_product_reset():
    s = get_session_data()
    name = (request.json or {}).get("name", "")
    if not name:
        return jsonify({"ok": False, "error": "Name required"})
    if "og_products" in s and name in s["og_products"]:
        del s["og_products"][name]
    return jsonify({"ok": True})


'''

FLASK_ANCHOR = '@app.route("/api/og/generate-image", methods=["POST"])'


def _find_function_end(content, start_pos):
    i = start_pos
    depth = 0
    in_string = False
    sc = None
    in_lc = False
    in_bc = False
    while i < len(content):
        c = content[i]
        n = content[i+1] if i+1 < len(content) else ''
        if not in_string and not in_bc and c == '/' and n == '/':
            in_lc = True; i += 2; continue
        if in_lc:
            if c == '\n': in_lc = False
            i += 1; continue
        if not in_string and not in_lc and c == '/' and n == '*':
            in_bc = True; i += 2; continue
        if in_bc:
            if c == '*' and n == '/': in_bc = False; i += 2; continue
            i += 1; continue
        if not in_string and c in ('"', "'", '`'):
            in_string = True; sc = c; i += 1; continue
        if in_string:
            if c == '\\': i += 2; continue
            if c == sc: in_string = False
            i += 1; continue
        if c == '{': depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0: return i
        i += 1
    return -1


def _replace_fn(content, name, new_body, is_async=False):
    pat = f'async function {name}(' if is_async else f'function {name}('
    s = content.find(pat)
    if s == -1: return content, False
    e = _find_function_end(content, s)
    if e == -1: return content, False
    return content[:s] + new_body + content[e+1:], True


def main():
    print("=" * 60)
    print("  OG Complete Fix - Part 5 + CSS Combined")
    print("=" * 60)

    if not APP_FILE.exists():
        print("ERROR: app_web.py not found")
        return 1

    content = APP_FILE.read_text(encoding="utf-8")

    if "function refreshOGPreview" in content and "/api/og/product-save" in content:
        print("Already patched. Skipping.")
        return 0

    print("Pre-checking markers...")
    markers = {
        "session": SESS_FIND,
        "updateOGPreview": "function updateOGPreview(){",
        "switchOGTab": "function switchOGTab(which){",
        "loadProductOG": "async function loadProductOG(){",
        "saveProductOG": "async function saveProductOG(){",
        "resetProductOG": "async function resetProductOG(){",
        "generateOGImage": "async function generateOGImage(){",
        "Flask anchor": FLASK_ANCHOR,
    }
    missing = []
    for k, m in markers.items():
        if m in content: print(f"  OK  {k}")
        else: print(f"  MISS {k}"); missing.append(k)

    if missing:
        print(f"\n{len(missing)} missing - ABORTING")
        return 1

    backup = APP_FILE.with_suffix(".py.bak")
    backup.write_text(content, encoding="utf-8")
    print(f"\nBackup: {backup}\n")

    content = content.replace(SESS_FIND, SESS_REPLACE, 1)
    print("[1/8] Session og_products")

    content, ok = _replace_fn(content, "updateOGPreview", NEW_PREVIEW_JS)
    if not ok: print("FAIL updateOGPreview"); return 1
    print("[2/8] Preview system (absolute positioning)")

    if SWITCH_OG_FIND in content:
        content = content.replace(SWITCH_OG_FIND, SWITCH_OG_REPLACE, 1)
        print("[3/8] switchOGTab refresh")
    else:
        print("[3/8] WARN switchOGTab marker gone")

    content, ok = _replace_fn(content, "loadProductOG", LOAD_PROD_OG_NEW, is_async=True)
    if not ok: print("FAIL loadProductOG"); return 1
    print("[4/8] loadProductOG")

    content, ok = _replace_fn(content, "saveProductOG", SAVE_PROD_OG_NEW, is_async=True)
    if not ok: print("FAIL saveProductOG"); return 1
    print("[5/8] saveProductOG")

    content, ok = _replace_fn(content, "resetProductOG", RESET_PROD_OG_NEW, is_async=True)
    if not ok: print("FAIL resetProductOG"); return 1
    print("[6/8] resetProductOG")

    content, ok = _replace_fn(content, "generateOGImage", GEN_OG_NEW, is_async=True)
    if not ok: print("FAIL generateOGImage"); return 1
    print("[7/8] generateOGImage")

    content = content.replace(FLASK_ANCHOR, NEW_FLASK_ROUTES + FLASK_ANCHOR, 1)
    print("[8/8] Flask product-og routes")

    APP_FILE.write_text(content, encoding="utf-8")
    print(f"\napp_web.py saved ({len(content.splitlines())} lines)")
    print("\n" + "=" * 60)
    print("  FIX APPLIED")
    print("=" * 60)
    print("\nNext:")
    print("  1. python -c \"import ast; ast.parse(open('app_web.py', encoding='utf-8').read()); print('OK')\"")
    print("  2. python app_web.py")
    print("  3. F12 Console + Open Graph tab test")
    return 0


if __name__ == "__main__":
    sys.exit(main())