# =============================================================================
# patch_taxonomy_kw_fix.py — Fix tax_type → taxonomy_type keyword bug
# =============================================================================

import sys
from pathlib import Path

APP_FILE = Path("app_web.py")

OLD = 'tax_type=d.get("type", "wc_categories"),'
NEW = 'taxonomy_type=d.get("type", "wc_categories"),'


def main():
    print("=" * 60)
    print("  Taxonomy Keyword Fix")
    print("=" * 60)

    if not APP_FILE.exists():
        print("❌ app_web.py not found")
        return 1

    content = APP_FILE.read_text(encoding="utf-8")

    count = content.count(OLD)
    print(f"Found {count} occurrence(s) of old pattern")

    if count == 0:
        print("⚠️  Pattern not found — already fixed or file changed")
        return 0

    # Backup
    backup = APP_FILE.with_suffix(".py.bak")
    backup.write_text(content, encoding="utf-8")
    print(f"✅ Backup: {backup}")

    # Replace all
    content = content.replace(OLD, NEW)
    APP_FILE.write_text(content, encoding="utf-8")

    print(f"✅ Fixed {count} route(s)")
    print(f"✅ app_web.py saved ({len(content.splitlines())} lines)")
    print("\n" + "=" * 60)
    print("  ✅ FIX COMPLETE")
    print("=" * 60)
    print("\nNext:")
    print("  1. python -c \"import ast; ast.parse(open('app_web.py', encoding='utf-8').read()); print('Syntax OK')\"")
    print("  2. Restart: python app_web.py")
    print("  3. Test Taxonomy → Create")
    return 0


if __name__ == "__main__":
    sys.exit(main())