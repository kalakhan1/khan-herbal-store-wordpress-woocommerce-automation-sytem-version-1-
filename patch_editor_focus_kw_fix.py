# =============================================================================
# patch_editor_focus_kw_fix.py — Fixed HTML marker
# =============================================================================
# Only patches app_web.py (wp_client.py already patched successfully)
# Uses flexible markers with fallbacks
# =============================================================================

import sys
from pathlib import Path

APP_FILE = Path("app_web.py")


# HTML insertion — 3 fallback markers (first match wins)
POST_HTML_CANDIDATES = [
    # Most likely (single line)
    (
        'id="post-edit-title"></div>',
        'id="post-edit-title"></div>\n            <div class="form-row"><label>Focus Keyword</label>\n                <input type="text" id="post-edit-focus-kw" placeholder="e.g. herbal remedies for hair"></div>',
    ),
    # Fallback: multi-line Content (HTML) variant
    (
        '<div class="form-row"><label>Content (HTML)</label>\n                <textarea id="post-edit-content"',
        '<div class="form-row"><label>Focus Keyword</label>\n                <input type="text" id="post-edit-focus-kw" placeholder="e.g. herbal remedies for hair"></div>\n            <div class="form-row"><label>Content (HTML)</label>\n                <textarea id="post-edit-content"',
    ),
    # Fallback: single-line Content (HTML)
    (
        '<div class="form-row"><label>Content (HTML)</label><textarea id="post-edit-content"',
        '<div class="form-row"><label>Focus Keyword</label><input type="text" id="post-edit-focus-kw" placeholder="e.g. herbal remedies for hair"></div>\n            <div class="form-row"><label>Content (HTML)</label><textarea id="post-edit-content"',
    ),
]


# Rest of markers (verified working in previous run)
JS_PROD_RENDER_FIND = "document.getElementById('prod-edit-short-desc').value = p.short_description || '';"
JS_PROD_RENDER_REPLACE = "document.getElementById('prod-edit-focus-kw').value = _editorState.focus_keyword || '';\n    document.getElementById('prod-edit-short-desc').value = p.short_description || '';"

JS_PROD_SAVE_FIND = "        categories: _editorState.categories.map(c => ({id: c.id})),"
JS_PROD_SAVE_REPLACE = "        focus_keyword: document.getElementById('prod-edit-focus-kw').value,\n        categories: _editorState.categories.map(c => ({id: c.id})),"

JS_POST_RENDER_FIND = "document.getElementById('post-edit-title').value = p.title || '';"
JS_POST_RENDER_REPLACE = "document.getElementById('post-edit-title').value = p.title || '';\n    document.getElementById('post-edit-focus-kw').value = _editorState.focus_keyword || '';"

JS_POST_SAVE_FIND = "        content: document.getElementById('post-edit-content').value,\n    };"
JS_POST_SAVE_REPLACE = "        content: document.getElementById('post-edit-content').value,\n        focus_keyword: document.getElementById('post-edit-focus-kw').value,\n    };"

JS_LOAD_FIND = "    _editorState.original = JSON.parse(JSON.stringify(d.item));"
JS_LOAD_REPLACE = "    _editorState.focus_keyword = d.focus_keyword || '';\n    _editorState.original = JSON.parse(JSON.stringify(d.item));"

JS_STATE_FIND = "    original: null,\n};"
JS_STATE_REPLACE = "    focus_keyword: '',\n    original: null,\n};"

FLASK_PROD_FIND = '''    if "images" in d:
        fields["images"] = d["images"]
    ok, product, err = wp_client.update_product(
        s["wc"]["url"], s["wc"]["ck"], s["wc"]["cs"], pid, **fields)'''

FLASK_PROD_REPLACE = '''    if "images" in d:
        fields["images"] = d["images"]
    if d.get("focus_keyword") is not None:
        try:
            ok_get, existing, _ = wp_client.get_product(
                s["wc"]["url"], s["wc"]["ck"], s["wc"]["cs"], pid)
            meta_data = list(existing.get("meta_data", []) or []) if ok_get else []
            found = False
            for m in meta_data:
                if m.get("key") == "rank_math_focus_keyword":
                    m["value"] = d["focus_keyword"]
                    found = True
                    break
            if not found:
                meta_data.append({"key": "rank_math_focus_keyword",
                                   "value": d["focus_keyword"]})
            fields["meta_data"] = meta_data
        except Exception:
            pass
    ok, product, err = wp_client.update_product(
        s["wc"]["url"], s["wc"]["ck"], s["wc"]["cs"], pid, **fields)'''

FLASK_POST_FIND = '''    for k in ["title", "content", "status", "excerpt"]:
        if k in d and d[k] is not None:
            fields[k] = d[k]
    if not fields:
        return jsonify({"ok": False, "error": "No fields to update"})
    ok, post, err = wp_client.update_post(
        s["wp"]["url"], s["wp"]["user"], s["wp"]["pass"], pid, **fields)'''

FLASK_POST_REPLACE = '''    for k in ["title", "content", "status", "excerpt"]:
        if k in d and d[k] is not None:
            fields[k] = d[k]
    warning = ""
    if "focus_keyword" in d and d["focus_keyword"] is not None:
        fields["meta"] = {"rank_math_focus_keyword": d["focus_keyword"]}
        warning = "Focus keyword sent via meta. If not saved, verify in WP Admin."
    if not fields:
        return jsonify({"ok": False, "error": "No fields to update"})
    ok, post, err = wp_client.update_post(
        s["wp"]["url"], s["wp"]["user"], s["wp"]["pass"], pid, **fields)'''

FLASK_POST_RETURN_FIND = '''    log_activity("editor_save_post", "ok", f"id={pid}")
    return jsonify({"ok": True, "post": post})'''

FLASK_POST_RETURN_REPLACE = '''    log_activity("editor_save_post", "ok", f"id={pid}")
    return jsonify({"ok": True, "post": post, "warning": warning})'''


def main():
    print("=" * 60)
    print("  Focus Keyword Patch — HTML Marker Fix")
    print("=" * 60)

    if not APP_FILE.exists():
        print("❌ app_web.py not found")
        return 1

    content = APP_FILE.read_text(encoding="utf-8")

    if "prod-edit-focus-kw" in content and "post-edit-focus-kw" in content:
        print("⚠️  Already patched. Skipping.")
        return 0

    # Find a working post HTML marker
    post_find = None
    post_replace = None
    for find, replace in POST_HTML_CANDIDATES:
        if find in content:
            post_find = find
            post_replace = replace
            print(f"✅ Post HTML marker found (variant: {find[:50]}...)")
            break

    if not post_find:
        print("❌ Post HTML marker not found in any variant")
        print("   This should not happen. Please report the HTML post editor section.")
        return 1

    # Pre-check all other markers
    markers = {
        "Prod HTML heading": '<h2>🔍 SEO / Meta</h2>',
        "JS prod render": JS_PROD_RENDER_FIND,
        "JS prod save": JS_PROD_SAVE_FIND,
        "JS post render": JS_POST_RENDER_FIND,
        "JS post save": JS_POST_SAVE_FIND,
        "JS load": JS_LOAD_FIND,
        "JS state": JS_STATE_FIND,
        "Flask prod": FLASK_PROD_FIND,
        "Flask post": FLASK_POST_FIND,
        "Flask post return": FLASK_POST_RETURN_FIND,
    }
    missing = []
    for name, m in markers.items():
        if m in content:
            print(f"✅ {name}")
        else:
            print(f"❌ {name} MISSING")
            missing.append(name)

    if missing:
        print(f"\n❌ {len(missing)} markers missing — ABORTING (file not modified)")
        return 1

    # Backup
    backup = APP_FILE.with_suffix(".py.bak")
    backup.write_text(content, encoding="utf-8")
    print(f"\n✅ Backup: {backup}\n")

    # Apply all replacements
    content = content.replace('<h2>🔍 SEO / Meta</h2>',
        '<h2>🔍 SEO / Meta</h2>\n            <div class="form-row"><label>Focus Keyword</label>\n                <input type="text" id="prod-edit-focus-kw" placeholder="e.g. almond oil for hair"></div>', 1)
    print("✅ Prod HTML focus kw")

    content = content.replace(post_find, post_replace, 1)
    print("✅ Post HTML focus kw")

    content = content.replace(JS_PROD_RENDER_FIND, JS_PROD_RENDER_REPLACE, 1)
    print("✅ JS prod render")

    content = content.replace(JS_PROD_SAVE_FIND, JS_PROD_SAVE_REPLACE, 1)
    print("✅ JS prod save")

    content = content.replace(JS_POST_RENDER_FIND, JS_POST_RENDER_REPLACE, 1)
    print("✅ JS post render")

    content = content.replace(JS_POST_SAVE_FIND, JS_POST_SAVE_REPLACE, 1)
    print("✅ JS post save")

    content = content.replace(JS_LOAD_FIND, JS_LOAD_REPLACE, 1)
    print("✅ JS load focus_kw")

    content = content.replace(JS_STATE_FIND, JS_STATE_REPLACE, 1)
    print("✅ JS state focus_kw")

    content = content.replace(FLASK_PROD_FIND, FLASK_PROD_REPLACE, 1)
    print("✅ Flask prod meta save")

    content = content.replace(FLASK_POST_FIND, FLASK_POST_REPLACE, 1)
    print("✅ Flask post meta save")

    content = content.replace(FLASK_POST_RETURN_FIND, FLASK_POST_RETURN_REPLACE, 1)
    print("✅ Flask post warning")

    APP_FILE.write_text(content, encoding="utf-8")
    print(f"\n✅ app_web.py saved ({len(content.splitlines())} lines)")
    print("\n" + "=" * 60)
    print("  ✅ PATCH COMPLETE")
    print("=" * 60)
    print("\nNext:")
    print("  1. python -c \"import ast; ast.parse(open('app_web.py', encoding='utf-8').read()); print('Syntax OK')\"")
    print("  2. python app_web.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())