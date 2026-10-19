# =============================================================================
# patch_editor_part4.py — Polish + Edit Buttons + Loading
# =============================================================================
# Changes:
#   - Fix Tab 9 Edit button → auto-loads post in Editor
#   - Fix Tab 10 Edit button → auto-loads product in Editor
#   - Add global loading overlay (spinner)
#   - Add loading indicators in load/save operations
#   - Better error messages
#
# Pre-check: Requires Part 3 (post-edit-slug marker)
# =============================================================================

import re
import sys
from pathlib import Path

APP_FILE = Path("app_web.py")


# =============================================================================
# LOADING OVERLAY JS
# =============================================================================
LOADING_JS = '''
// ================================================================
// GLOBAL LOADING OVERLAY
// ================================================================
function showLoading(msg){
    msg = msg || 'Loading...';
    let overlay = document.getElementById('global-loading-overlay');
    if (!overlay){
        overlay = document.createElement('div');
        overlay.id = 'global-loading-overlay';
        overlay.style.cssText = 'position:fixed;inset:0;background:rgba(0,0,0,0.55);z-index:99998;display:flex;align-items:center;justify-content:center;color:#fff;font-size:16px;font-family:Segoe UI,sans-serif;flex-direction:column;gap:16px;backdrop-filter:blur(2px);';
        overlay.innerHTML = '<div style="border:4px solid rgba(255,255,255,0.25);border-top-color:#4ade80;border-radius:50%;width:52px;height:52px;animation:_spinner 0.9s linear infinite"></div><div id="global-loading-msg">Loading...</div><style>@keyframes _spinner{to{transform:rotate(360deg)}}</style>';
        document.body.appendChild(overlay);
    }
    document.getElementById('global-loading-msg').textContent = msg;
    overlay.style.display = 'flex';
}

function hideLoading(){
    const overlay = document.getElementById('global-loading-overlay');
    if (overlay) overlay.style.display = 'none';
}

// Auto-hide loading on any fetch error
window.addEventListener('error', hideLoading);
window.addEventListener('unhandledrejection', hideLoading);
'''

# Insert loading JS right after `async function api(` helper (before its closing brace)
# Actually insert before "// ================================================================\n// TAB 1:"
LOADING_ANCHOR = "// ================================================================\n// TAB 1: CONNECTIONS"


# =============================================================================
# EDIT BUTTON FIXES — Regex based (robust against body changes)
# =============================================================================
EDIT_BLOG_NEW = '''function editBlogPost(id){
    document.querySelectorAll('.tab-btn').forEach(x => x.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(x => x.classList.remove('active'));
    const editorBtn = document.querySelector('[data-tab="editor"]');
    if (editorBtn) editorBtn.classList.add('active');
    document.getElementById('tab-editor').classList.add('active');
    document.getElementById('main').scrollTop = 0;
    document.getElementById('editor-type').value = 'post';
    _editorState.type = 'post';
    loadEditorList().then(() => {
        document.getElementById('editor-item').value = id;
        loadEditorItem();
    });
}'''

EDIT_LIVE_PRODUCT_NEW = '''function editLiveProduct(id){
    document.querySelectorAll('.tab-btn').forEach(x => x.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(x => x.classList.remove('active'));
    const editorBtn = document.querySelector('[data-tab="editor"]');
    if (editorBtn) editorBtn.classList.add('active');
    document.getElementById('tab-editor').classList.add('active');
    document.getElementById('main').scrollTop = 0;
    document.getElementById('editor-type').value = 'product';
    _editorState.type = 'product';
    loadEditorList().then(() => {
        document.getElementById('editor-item').value = id;
        loadEditorItem();
    });
}'''


# =============================================================================
# LOAD EDITOR ITEM — add loading spinner
# =============================================================================
LOAD_EDITOR_FIND = '''    document.getElementById('editor-load-status').textContent = 'Loading...';
    const d = await api('/api/editor/load', {body:{type, id: _editorState.id}});
    if (!d.ok){
        document.getElementById('editor-load-status').textContent = '❌ ' + d.error;
        toast(d.error, 'error');
        return;
    }'''

LOAD_EDITOR_REPLACE = '''    document.getElementById('editor-load-status').textContent = 'Loading...';
    showLoading('Loading ' + type + ' #' + _editorState.id + '...');
    let d;
    try {
        d = await api('/api/editor/load', {body:{type, id: _editorState.id}});
    } finally {
        hideLoading();
    }
    if (!d.ok){
        document.getElementById('editor-load-status').textContent = '❌ ' + d.error;
        toast(d.error, 'error');
        return;
    }'''


# =============================================================================
# SAVE PRODUCT — add loading spinner
# =============================================================================
SAVE_PROD_FIND = '''    toast('Saving...', 'info');
    const d = await api('/api/editor/save-product', {body: payload});
    if (d.ok){
        toast('✅ Product saved');'''

SAVE_PROD_REPLACE = '''    showLoading('Saving product...');
    let d;
    try {
        d = await api('/api/editor/save-product', {body: payload});
    } finally {
        hideLoading();
    }
    if (d.ok){
        toast('✅ Product saved');'''


# =============================================================================
# SAVE POST — add loading spinner
# =============================================================================
SAVE_POST_FIND = '''    toast('Saving...', 'info');
    const d = await api('/api/editor/save-post', {body: payload});
    if (d.ok){
        toast('✅ Post saved');
        if (d.warning) toast(d.warning, 'warning', 6000);'''

SAVE_POST_REPLACE = '''    showLoading('Saving post...');
    let d;
    try {
        d = await api('/api/editor/save-post', {body: payload});
    } finally {
        hideLoading();
    }
    if (d.ok){
        toast('✅ Post saved');
        if (d.warning) toast(d.warning, 'warning', 6000);'''


# =============================================================================
# PATCHER
# =============================================================================
def _find_function_end(content, func_start_pos):
    """Find the closing brace of a JS function starting at func_start_pos."""
    i = func_start_pos
    depth = 0
    in_string = False
    string_char = None
    in_line_comment = False
    in_block_comment = False
    while i < len(content):
        c = content[i]
        n = content[i+1] if i+1 < len(content) else ''
        # Handle comments
        if not in_string and not in_block_comment and c == '/' and n == '/':
            in_line_comment = True
            i += 2
            continue
        if in_line_comment:
            if c == '\n':
                in_line_comment = False
            i += 1
            continue
        if not in_string and not in_line_comment and c == '/' and n == '*':
            in_block_comment = True
            i += 2
            continue
        if in_block_comment:
            if c == '*' and n == '/':
                in_block_comment = False
                i += 2
                continue
            i += 1
            continue
        # Handle strings
        if not in_string and c in ('"', "'", '`'):
            in_string = True
            string_char = c
            i += 1
            continue
        if in_string:
            if c == '\\':
                i += 2
                continue
            if c == string_char:
                in_string = False
            i += 1
            continue
        # Handle braces
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return -1


def _replace_function(content, func_name, new_body):
    """Replace a JS function by finding its start and matching closing brace."""
    pattern = f'function {func_name}('
    start = content.find(pattern)
    if start == -1:
        return content, False
    end = _find_function_end(content, start)
    if end == -1:
        return content, False
    return content[:start] + new_body + content[end+1:], True


def patch_app():
    print("\n📄 Patching app_web.py...")

    if not APP_FILE.exists():
        print("   ❌ app_web.py not found")
        return False

    content = APP_FILE.read_text(encoding="utf-8")

    # Pre-check Part 3 applied
    if 'id="post-edit-slug"' not in content:
        print("   ❌ Part 3 not applied (post-edit-slug not found)")
        print("   ⚠️  Please run patch_editor_part3_v2.py first")
        return False
    print("   ✅ Part 3 detected")

    # Check if already patched
    if 'global-loading-overlay' in content and 'loadEditorList().then(() => {' in content:
        print("   ⚠️  Already patched. Skipping.")
        return True

    # Pre-check all markers
    print("   🔍 Pre-checking markers...")
    markers = {
        "function editBlogPost": "function editBlogPost(id)",
        "function editLiveProduct": "function editLiveProduct(id)",
        "loadEditorItem loading": LOAD_EDITOR_FIND,
        "saveProduct loading": SAVE_PROD_FIND,
        "savePost loading": SAVE_POST_FIND,
        "TAB 1 marker": LOADING_ANCHOR,
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

    # 1. Insert loading JS
    if LOADING_JS not in content:
        content = content.replace(LOADING_ANCHOR, LOADING_JS + "\n\n" + LOADING_ANCHOR, 1)
        print("   ✅ [1/6] Loading overlay JS added")

    # 2. Fix editBlogPost
    content, ok = _replace_function(content, "editBlogPost", EDIT_BLOG_NEW)
    if ok:
        print("   ✅ [2/6] editBlogPost() fixed")
    else:
        print("   ❌ [2/6] editBlogPost() replace failed")
        return False

    # 3. Fix editLiveProduct
    content, ok = _replace_function(content, "editLiveProduct", EDIT_LIVE_PRODUCT_NEW)
    if ok:
        print("   ✅ [3/6] editLiveProduct() fixed")
    else:
        print("   ❌ [3/6] editLiveProduct() replace failed")
        return False

    # 4. loadEditorItem — loading spinner
    if LOAD_EDITOR_FIND in content:
        content = content.replace(LOAD_EDITOR_FIND, LOAD_EDITOR_REPLACE, 1)
        print("   ✅ [4/6] loadEditorItem loading added")
    else:
        print("   ⚠️  [4/6] loadEditorItem already updated")

    # 5. saveProductChanges — loading spinner
    if SAVE_PROD_FIND in content:
        content = content.replace(SAVE_PROD_FIND, SAVE_PROD_REPLACE, 1)
        print("   ✅ [5/6] saveProductChanges loading added")
    else:
        print("   ⚠️  [5/6] saveProductChanges already updated")

    # 6. savePostChanges — loading spinner
    if SAVE_POST_FIND in content:
        content = content.replace(SAVE_POST_FIND, SAVE_POST_REPLACE, 1)
        print("   ✅ [6/6] savePostChanges loading added")
    else:
        print("   ⚠️  [6/6] savePostChanges already updated")

    APP_FILE.write_text(content, encoding="utf-8")
    print(f"\n   ✅ app_web.py saved ({len(content.splitlines())} lines)")
    return True


def main():
    print("=" * 60)
    print("  Part 4 — Polish + Edit Buttons + Loading")
    print("=" * 60)
    ok = patch_app()
    print("\n" + "=" * 60)
    if ok:
        print("  ✅ PATCH COMPLETE")
        print("=" * 60)
        print("\nNext:")
        print("  1. python -c \"import ast; ast.parse(open('app_web.py', encoding='utf-8').read()); print('Syntax OK')\"")
        print("  2. python app_web.py")
        print("  3. Run tests: python test_editor.py")
        return 0
    print("  ❌ PATCH FAILED")
    print("=" * 60)
    return 1


if __name__ == "__main__":
    sys.exit(main())