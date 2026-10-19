# =============================================================================
# patch_og_preview_css.py — Responsive CSS for Live Preview (CSS-ONLY)
# =============================================================================
# Zero logic change. Only .og-preview CSS block replaced.
# All JS, Flask routes, PIL generation untouched.
# =============================================================================

import sys
from pathlib import Path

APP_FILE = Path("app_web.py")


NEW_CSS = r""".og-preview{border:1px solid var(--border);border-radius:var(--r);overflow:hidden;
  background:var(--bg-card);width:100%;max-width:500px;box-sizing:border-box;margin:0 auto}
.og-preview .og-img{width:100%;aspect-ratio:1.91/1;background-color:var(--bg-elev);
  background-size:cover;background-position:center;background-repeat:no-repeat;
  display:flex;align-items:center;justify-content:center;color:var(--muted);
  font-size:clamp(11px,2.5vw,13px);text-align:center;padding:8px;
  box-sizing:border-box;overflow:hidden;position:relative;line-height:1.3}
.og-preview .og-img img{position:absolute;inset:0;width:100%;height:100%;
  object-fit:cover;display:block}
.og-preview .og-body{padding:clamp(10px,2vw,14px);box-sizing:border-box}
.og-preview .og-url{font-size:clamp(9px,1.5vw,11px);color:var(--muted);
  text-transform:uppercase;letter-spacing:.5px;margin-bottom:6px;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:100%}
.og-preview .og-title{font-size:clamp(13px,3vw,16px);font-weight:700;
  margin-bottom:6px;color:var(--text);line-height:1.25;
  display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;
  overflow:hidden;overflow-wrap:anywhere;word-break:break-word}
.og-preview .og-desc{font-size:clamp(11px,2.2vw,13px);color:var(--muted);
  line-height:1.4;display:-webkit-box;-webkit-line-clamp:2;
  -webkit-box-orient:vertical;overflow:hidden;
  overflow-wrap:anywhere;word-break:break-word}
@media (max-width:480px){
  .og-preview .og-title{-webkit-line-clamp:3;font-size:14px}
  .og-preview .og-desc{-webkit-line-clamp:3}
}"""


def main():
    print("=" * 60)
    print("  OG Preview CSS Responsive Fix (CSS-only)")
    print("=" * 60)

    if not APP_FILE.exists():
        print("ERROR: app_web.py not found")
        return 1

    content = APP_FILE.read_text(encoding="utf-8")

    # Already patched?
    if "aspect-ratio:1.91/1" in content and "clamp(13px,3vw,16px)" in content:
        print("Already patched. Skipping.")
        return 0

    # Locate the CSS block: from ".og-preview{" to the closing "}" of .og-preview .og-desc
    start_marker = ".og-preview{border:1px solid var(--border)"
    start_idx = content.find(start_marker)
    if start_idx == -1:
        print("ERROR: .og-preview CSS block start not found")
        return 1

    desc_marker = ".og-preview .og-desc{"
    desc_idx = content.find(desc_marker, start_idx)
    if desc_idx == -1:
        print("ERROR: .og-preview .og-desc block not found")
        return 1

    # Find the closing brace of .og-preview .og-desc
    end_idx = content.find("}", desc_idx)
    if end_idx == -1:
        print("ERROR: closing brace not found")
        return 1
    end_idx += 1  # include the closing brace

    old_block = content[start_idx:end_idx]
    print(f"Found CSS block: {len(old_block)} chars")
    print(f"Preview of old block: {repr(old_block[:100])}...")

    # Backup
    backup = APP_FILE.with_suffix(".py.bak")
    backup.write_text(content, encoding="utf-8")
    print(f"Backup: {backup}")

    # Replace
    content = content[:start_idx] + NEW_CSS + content[end_idx:]
    APP_FILE.write_text(content, encoding="utf-8")

    print(f"\nReplaced with responsive CSS: {len(NEW_CSS)} chars")
    print(f"app_web.py saved ({len(content.splitlines())} lines)")

    print("\n" + "=" * 60)
    print("  CSS PATCH APPLIED - NO LOGIC CHANGED")
    print("=" * 60)
    print("\nVerification:")
    print("  1. python -c \"import ast; ast.parse(open('app_web.py', encoding='utf-8').read()); print('OK')\"")
    print("  2. python app_web.py")
    print("  3. F12 responsive mode test")
    print("\nWhat changed in CSS:")
    print("  - .og-img: fixed height 260px -> aspect-ratio 1.91/1 (fluid)")
    print("  - Font sizes: fixed px -> clamp(min, vw, max) (fluid)")
    print("  - Added: overflow-wrap + word-break for long text")
    print("  - Added: mobile @media for 3-line clamp on small screens")
    print("  - Added: text-overflow ellipsis on URL")
    print("\nWhat did NOT change:")
    print("  - All JS functions (refreshOGPreview, generateOGImage, etc.)")
    print("  - All Flask routes")
    print("  - PIL image generation logic")
    print("  - Any HTML structure")
    return 0


if __name__ == "__main__":
    sys.exit(main())