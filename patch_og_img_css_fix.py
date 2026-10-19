# =============================================================================
# patch_og_img_css_fix.py — Fix invisible OG preview image
# =============================================================================
# Root cause: .og-img uses display:flex which prevents img from stretching
# Fix: absolute positioning + object-fit + debug logging
# =============================================================================

import sys
from pathlib import Path

APP_FILE = Path("app_web.py")


# Robust preview function with absolute-positioned image + debug logs
NEW_FUNC = r'''function refreshOGPreview(){
    const data = getOGPreviewData();
    const siteEl = document.getElementById('og-preview-site');
    const titleEl = document.getElementById('og-preview-title');
    const descEl = document.getElementById('og-preview-desc');
    const box = document.getElementById('og-preview-img');
    if (siteEl) siteEl.textContent = (data.site || 'SITE').toUpperCase();
    if (titleEl) titleEl.textContent = data.title;
    if (descEl) descEl.textContent = data.desc;
    if (!box) return;

    // Reset box
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
        img.onload = function(){
            console.log('[OG Preview] Image loaded OK:', data.img, img.naturalWidth + 'x' + img.naturalHeight);
        };
        img.onerror = function(){
            console.warn('[OG Preview] Image load failed:', data.img);
            if (img.parentNode) img.parentNode.removeChild(img);
            box.style.display = 'flex';
            box.style.alignItems = 'center';
            box.style.justifyContent = 'center';
            box.style.background = '#fee2e2';
            box.style.color = '#dc2626';
            box.style.fontSize = '12px';
            box.textContent = 'Image failed: ' + String(data.img).substring(0, 70);
        };
        box.appendChild(img);
        img.src = data.img;
        // Catch silent failure after short delay
        setTimeout(function(){
            if (img.parentNode && img.naturalWidth === 0 && img.complete){
                console.warn('[OG Preview] Silent fail - naturalWidth=0 for:', data.img);
            }
        }, 2000);
    } else {
        box.style.display = 'flex';
        box.style.alignItems = 'center';
        box.style.justifyContent = 'center';
        box.style.color = 'var(--muted)';
        box.style.fontSize = '13px';
        box.textContent = '(no image URL)';
    }
}
'''


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


def main():
    print("=" * 60)
    print("  OG Preview Image CSS Fix")
    print("=" * 60)

    if not APP_FILE.exists():
        print("ERROR: app_web.py not found")
        return 1

    content = APP_FILE.read_text(encoding="utf-8")

    if "position:absolute;top:0;left:0;width:100%;height:100%;object-fit:cover" in content:
        print("Already patched. Skipping.")
        return 0

    marker = "function refreshOGPreview(){"
    start = content.find(marker)
    if start == -1:
        print("ERROR: refreshOGPreview not found")
        print("(Part 5 patch not applied? Run patch_og_preview_fix.py first)")
        return 1

    end = _find_function_end(content, start)
    if end == -1:
        print("ERROR: function end not found")
        return 1

    backup = APP_FILE.with_suffix(".py.bak")
    backup.write_text(content, encoding="utf-8")
    print(f"Backup: {backup}")

    content = content[:start] + NEW_FUNC + content[end+1:]
    APP_FILE.write_text(content, encoding="utf-8")

    print("refreshOGPreview replaced with absolute-position version")
    print(f"app_web.py saved ({len(content.splitlines())} lines)")
    print("\n" + "=" * 60)
    print("  FIX APPLIED")
    print("=" * 60)
    print("\nNext:")
    print("  1. python -c \"import ast; ast.parse(open('app_web.py', encoding='utf-8').read()); print('Syntax OK')\"")
    print("  2. python app_web.py")
    print("  3. Open Graph tab -> Per Product -> select product")
    print("  4. Open F12 Console - look for [OG Preview] logs")
    return 0


if __name__ == "__main__":
    sys.exit(main())