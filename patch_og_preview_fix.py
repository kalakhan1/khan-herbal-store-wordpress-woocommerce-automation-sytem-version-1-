# =============================================================================
# patch_og_preview_fix.py — Part 5
# =============================================================================
# Fixes:
#   - Live Preview now reads from active OG tab (global/product/generator)
#   - Generated image shows in Live Preview (not just separate box)
#   - Per-product OG save actually persists (new Flask routes)
#   - External image load errors handled gracefully
#   - Product OG inputs wired to live preview on change
# =============================================================================

import sys
from pathlib import Path

APP_FILE = Path("app_web.py")


# =============================================================================
# SESSION INIT — add og_products
# =============================================================================
SESS_FIND = '''            "og_global": {},
            "blog_drafts": [],'''

SESS_REPLACE = '''            "og_global": {},
            "og_products": {},
            "blog_drafts": [],'''


# =============================================================================
# NEW PREVIEW JS — getOGPreviewData + refreshOGPreview + updateOGPreview alias
# =============================================================================
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
    box.style.backgroundImage = '';
    box.style.background = '';
    box.style.color = '';
    box.style.fontSize = '';
    box.innerHTML = '';
    if (data.img){
        const img = document.createElement('img');
        img.src = data.img;
        img.style.cssText = 'width:100%;height:100%;object-fit:cover;display:block;';
        img.onerror = function(){
            box.style.background = '#fee2e2';
            box.style.color = '#dc2626';
            box.style.fontSize = '12px';
            box.textContent = 'Image failed to load (hotlink/CORS protection?)';
        };
        box.appendChild(img);
    } else {
        box.textContent = '(no image)';
    }
}

function updateOGPreview(){ refreshOGPreview(); }
'''


# =============================================================================
# SWITCH OG TAB — add refresh call
# =============================================================================
SWITCH_OG_FIND = '''    if (which === 'product' || which === 'generator') fillOGProductDropdown();
}'''

SWITCH_OG_REPLACE = '''    if (which === 'product' || which === 'generator') fillOGProductDropdown();
    refreshOGPreview();
}'''


# =============================================================================
# LOAD PRODUCT OG — full replacement
# =============================================================================
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
        if (d.source === 'saved') toast('Loaded saved OG for this product', 'info', 3000);
    }
    refreshOGPreview();
}'''


# =============================================================================
# SAVE / RESET / GENERATE — full replacements
# =============================================================================
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


# =============================================================================
# NEW FLASK ROUTES
# =============================================================================
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


# =============================================================================
# HELPERS
# =============================================================================
def _find_function_end(content, start_pos):
    i = start_pos
    depth = 0
    in_string = False
    string_char = None
    in_line_comment = False
    in_block_comment = False
    while i < len(content):
        c = content[i]
        n = content[i+1] if i+1 < len(content) else ''
        if not in_string and not in_block_comment and c == '/' and n == '/':
            in_line_comment = True; i += 2; continue
        if in_line_comment:
            if c == '\n': in_line_comment = False
            i += 1; continue
        if not in_string and not in_line_comment and c == '/' and n == '*':
            in_block_comment = True; i += 2; continue
        if in_block_comment:
            if c == '*' and n == '/':
                in_block_comment = False; i += 2; continue
            i += 1; continue
        if not in_string and c in ('"', "'", '`'):
            in_string = True; string_char = c; i += 1; continue
        if in_string:
            if c == '\\': i += 2; continue
            if c == string_char: in_string = False
            i += 1; continue
        if c == '{': depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0: return i
        i += 1
    return -1


def _replace_function(content, func_name, new_body, is_async=False):
    pattern = f'async function {func_name}(' if is_async else f'function {func_name}('
    start = content.find(pattern)
    if start == -1:
        return content, False
    end = _find_function_end(content, start)
    if end == -1:
        return content, False
    return content[:start] + new_body + content[end+1:], True


# =============================================================================
# PATCHER
# =============================================================================
def patch_app():
    print("\nPatching app_web.py...")
    if not APP_FILE.exists():
        print("  ERROR: app_web.py not found")
        return False

    content = APP_FILE.read_text(encoding="utf-8")

    if "getOGPreviewData" in content and "/api/og/product-save" in content:
        print("  Already patched. Skipping.")
        return True

    print("  Pre-checking markers...")
    markers = {
        "session og_global": SESS_FIND,
        "function updateOGPreview": "function updateOGPreview(){",
        "function switchOGTab": "function switchOGTab(which){",
        "async function loadProductOG": "async function loadProductOG(){",
        "async function saveProductOG": "async function saveProductOG(){",
        "async function resetProductOG": "async function resetProductOG(){",
        "async function generateOGImage": "async function generateOGImage(){",
        "Flask og/generate-image": FLASK_ANCHOR,
    }
    missing = []
    for name, m in markers.items():
        if m in content:
            print(f"    OK  {name}")
        else:
            print(f"    MISS {name}")
            missing.append(name)

    if missing:
        print(f"\n  {len(missing)} missing - ABORTING (file not modified)")
        return False

    backup = APP_FILE.with_suffix(".py.bak")
    backup.write_text(content, encoding="utf-8")
    print(f"\n  Backup: {backup}\n")

    # 1. Session og_products
    content = content.replace(SESS_FIND, SESS_REPLACE, 1)
    print("  [1/8] Session og_products added")

    # 2. Replace updateOGPreview with new preview system
    content, ok = _replace_function(content, "updateOGPreview", NEW_PREVIEW_JS, is_async=False)
    if not ok:
        print("  ERROR: updateOGPreview replace failed"); return False
    print("  [2/8] Preview system replaced (getOGPreviewData + refreshOGPreview)")

    # 3. switchOGTab
    if SWITCH_OG_FIND in content:
        content = content.replace(SWITCH_OG_FIND, SWITCH_OG_REPLACE, 1)
        print("  [3/8] switchOGTab refresh added")
    else:
        print("  WARN: switchOGTab marker gone, skipping")

    # 4. loadProductOG
    content, ok = _replace_function(content, "loadProductOG", LOAD_PROD_OG_NEW, is_async=True)
    if not ok:
        print("  ERROR: loadProductOG replace failed"); return False
    print("  [4/8] loadProductOG replaced")

    # 5. saveProductOG
    content, ok = _replace_function(content, "saveProductOG", SAVE_PROD_OG_NEW, is_async=True)
    if not ok:
        print("  ERROR: saveProductOG replace failed"); return False
    print("  [5/8] saveProductOG implemented")

    # 6. resetProductOG
    content, ok = _replace_function(content, "resetProductOG", RESET_PROD_OG_NEW, is_async=True)
    if not ok:
        print("  ERROR: resetProductOG replace failed"); return False
    print("  [6/8] resetProductOG implemented")

    # 7. generateOGImage
    content, ok = _replace_function(content, "generateOGImage", GEN_OG_NEW, is_async=True)
    if not ok:
        print("  ERROR: generateOGImage replace failed"); return False
    print("  [7/8] generateOGImage wired to live preview")

    # 8. Flask routes
    content = content.replace(FLASK_ANCHOR, NEW_FLASK_ROUTES + FLASK_ANCHOR, 1)
    print("  [8/8] Flask product-og routes added")

    APP_FILE.write_text(content, encoding="utf-8")
    print(f"\n  app_web.py saved ({len(content.splitlines())} lines)")
    return True


def main():
    print("=" * 60)
    print("  Part 5 - Open Graph Preview + Per-Product OG Fix")
    print("=" * 60)
    ok = patch_app()
    print("\n" + "=" * 60)
    if ok:
        print("  PATCH COMPLETE")
        print("=" * 60)
        print("\nNext:")
        print("  1. python -c \"import ast; ast.parse(open('app_web.py', encoding='utf-8').read()); print('Syntax OK')\"")
        print("  2. python app_web.py")
        print("  3. Test Open Graph tab (all 3 sub-tabs)")
        return 0
    print("  PATCH FAILED")
    print("=" * 60)
    return 1


if __name__ == "__main__":
    sys.exit(main())