# =============================================================================
# KHAN HERBAL STORES — OPEN GRAPH MANAGER v1.0
# =============================================================================
# File: open_graph.py
# Purpose: Manage Open Graph + Twitter Card metadata:
#   - Global OG settings (site-wide fallback)
#   - Per-product / per-post OG overrides
#   - OG image auto-generator (Pillow, 5 styles)
#   - RankMath meta integration
#   - Live preview + validation
#
# SECTION HIERARCHY:
#   SECTION 1  — Imports & Constants
#   SECTION 2  — Global OG Settings
#   SECTION 3  — Per-Item OG (product/post)
#   SECTION 4  — OG Meta Tag Builder
#   SECTION 5  — RankMath Integration
#   SECTION 6  — OG Image Generator (5 styles)
#   SECTION 7  — Validation & Preview
#   SECTION 8  — Standalone Test
# =============================================================================

# =============================================================================
# SECTION 1 — IMPORTS & CONSTANTS
# =============================================================================
import os
import re
import time
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# --- Constants ---
OG_IMAGE_WIDTH = 1200
OG_IMAGE_HEIGHT = 630
OG_IMAGE_MAX_BYTES = 5 * 1024 * 1024   # 5 MB
OG_TITLE_MAX = 70
OG_DESC_MAX = 160
OG_SITE_NAME_MAX = 30

OG_DEFAULT_LOCALE = "en_PK"
OG_DEFAULT_TYPE = "website"
OG_DEFAULT_TWITTER_CARD = "summary_large_image"

# Output directory for generated OG images
WORKSPACE = Path.cwd() / "workspace"
OG_IMAGES_DIR = WORKSPACE / "og_images"
OG_IMAGES_DIR.mkdir(parents=True, exist_ok=True)


# =============================================================================
# SECTION 2 — GLOBAL OG SETTINGS
# =============================================================================
GLOBAL_OG_DEFAULTS = {
    "site_name":         "Khan Herbal Stores",
    "og_title":          "Khan Herbal Stores — Authentic Herbal Remedies",
    "og_description":    "Pakistan's trusted online store for pure, natural and authentic herbal products.",
    "og_image":          "",       # URL to default OG image
    "og_type":           "website",
    "og_locale":         "en_PK",
    "twitter_card":      "summary_large_image",
    "twitter_site":      "",       # @handle
    "twitter_creator":   "",       # @handle
    "fb_app_id":         "",       # optional
    "pinterest_verify":  "",       # optional
}


def get_global_defaults() -> Dict[str, str]:
    """Return default global OG settings."""
    return dict(GLOBAL_OG_DEFAULTS)


def merge_global_settings(custom: Dict[str, Any]) -> Dict[str, str]:
    """Merge custom settings with defaults."""
    merged = dict(GLOBAL_OG_DEFAULTS)
    if custom:
        for k, v in custom.items():
            if v is not None and k in merged:
                merged[k] = v
    return merged


# =============================================================================
# SECTION 3 — PER-ITEM OG (Product / Post)
# =============================================================================
def auto_fill_og(
    item_type: str,
    product_or_post: Dict[str, Any],
    global_og: Dict[str, str],
) -> Dict[str, Any]:
    """
    Auto-fill OG fields for a product or post based on existing data.

    item_type: "product" | "post"

    Returns dict with keys:
      enabled (bool), title, description, image, url, type, locale,
      site_name, twitter_card, price (product), currency, availability
    """
    if item_type == "product":
        name = product_or_post.get("name", "")
        rankmath = product_or_post.get("rankmath", {})
        title = rankmath.get("meta:rank_math_title") or f"{name} — Buy Online"
        desc = rankmath.get("meta:rank_math_description") or \
               f"Shop {name} at {global_og.get('site_name', 'our store')}. " \
               f"100% pure, natural & authentic. Fast delivery across Pakistan."
        image = product_or_post.get("featured_image", "") or global_og.get("og_image", "")
        url = product_or_post.get("product_url", "")
        og_type = "product"
        price = product_or_post.get("price", 0)
        currency = "PKR"
        availability = "instock" if product_or_post.get("stock", 0) > 0 else "outofstock"
    else:  # post
        name = product_or_post.get("title", "")
        rankmath = product_or_post.get("rankmath", {})
        title = rankmath.get("meta:rank_math_title") or name
        desc = rankmath.get("meta:rank_math_description") or \
               product_or_post.get("excerpt", "")[:160]
        image = product_or_post.get("featured_image", "") or global_og.get("og_image", "")
        url = product_or_post.get("url", "")
        og_type = "article"
        price = None
        currency = None
        availability = None

    result = {
        "enabled":        False,
        "title":          title[:OG_TITLE_MAX],
        "description":    desc[:OG_DESC_MAX],
        "image":          image,
        "url":            url,
        "type":           og_type,
        "locale":         global_og.get("og_locale", OG_DEFAULT_LOCALE),
        "site_name":      global_og.get("site_name", ""),
        "twitter_card":   global_og.get("twitter_card", OG_DEFAULT_TWITTER_CARD),
        "twitter_site":   global_og.get("twitter_site", ""),
    }
    if price is not None:
        result["price"] = f"{price:.2f}"
        result["currency"] = currency
        result["availability"] = availability
    return result


# =============================================================================
# SECTION 4 — OG META TAG BUILDER
# =============================================================================
def build_og_meta_html(og: Dict[str, Any]) -> str:
    """
    Build <meta property="og:*"> + Twitter tags as HTML string.
    For embedding in <head> or previewing.
    """
    tags = []
    site = og.get("site_name", "")
    if site:
        tags.append(f'<meta property="og:site_name" content="{_esc(site)}">')
    if og.get("title"):
        tags.append(f'<meta property="og:title" content="{_esc(og["title"])}">')
    if og.get("description"):
        tags.append(f'<meta property="og:description" content="{_esc(og["description"])}">')
    if og.get("image"):
        tags.append(f'<meta property="og:image" content="{_esc(og["image"])}">')
    if og.get("url"):
        tags.append(f'<meta property="og:url" content="{_esc(og["url"])}">')
    if og.get("type"):
        tags.append(f'<meta property="og:type" content="{_esc(og["type"])}">')
    if og.get("locale"):
        tags.append(f'<meta property="og:locale" content="{_esc(og["locale"])}">')

    # Product-specific
    if og.get("price"):
        tags.append(f'<meta property="product:price:amount" content="{_esc(og["price"])}">')
    if og.get("currency"):
        tags.append(f'<meta property="product:price:currency" content="{_esc(og["currency"])}">')
    if og.get("availability"):
        tags.append(f'<meta property="product:availability" content="{_esc(og["availability"])}">')

    # Twitter
    tags.append(f'<meta name="twitter:card" content="{_esc(og.get("twitter_card", "summary_large_image"))}">')
    if og.get("twitter_site"):
        tags.append(f'<meta name="twitter:site" content="{_esc(og["twitter_site"])}">')
    if og.get("title"):
        tags.append(f'<meta name="twitter:title" content="{_esc(og["title"])}">')
    if og.get("description"):
        tags.append(f'<meta name="twitter:description" content="{_esc(og["description"])}">')
    if og.get("image"):
        tags.append(f'<meta name="twitter:image" content="{_esc(og["image"])}">')

    return "\n".join(tags)


def _esc(text: str) -> str:
    """Escape HTML attribute."""
    if text is None:
        return ""
    return (str(text)
            .replace('"', "&quot;")
            .replace("<", "&lt;")
            .replace(">", "&gt;"))


# =============================================================================
# SECTION 5 — RANKMATH INTEGRATION
# =============================================================================
def build_rankmath_og_meta(og: Dict[str, Any]) -> Dict[str, str]:
    """
    Convert OG dict into RankMath meta fields for REST API / CSV push.
    These keys use the `meta:` prefix used by WooCommerce CSV importer.
    """
    return {
        "meta:rank_math_facebook_title":        og.get("title", ""),
        "meta:rank_math_facebook_description":  og.get("description", ""),
        "meta:rank_math_facebook_image":        og.get("image", ""),
        "meta:rank_math_twitter_title":         og.get("title", ""),
        "meta:rank_math_twitter_description":   og.get("description", ""),
        "meta:rank_math_twitter_image":         og.get("image", ""),
    }


def merge_og_into_rankmath(existing_rm: Dict[str, str],
                            og: Dict[str, Any]) -> Dict[str, str]:
    """
    Merge OG meta into an existing rankmath dict, overriding the
    facebook/twitter keys only.
    """
    if existing_rm is None:
        existing_rm = {}
    merged = dict(existing_rm)
    merged.update(build_rankmath_og_meta(og))
    return merged


# =============================================================================
# SECTION 6 — OG IMAGE GENERATOR (5 styles)
# =============================================================================
def _load_font(size: int, bold: bool = False):
    """Try to load a system font, fallback to default."""
    if not PIL_AVAILABLE:
        return None
    candidates = [
        "arialbd.ttf" if bold else "arial.ttf",
        "segoeuib.ttf" if bold else "segoeui.ttf",
        "calibrib.ttf" if bold else "calibri.ttf",
        "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf",
    ]
    for name in candidates:
        try:
            return ImageFont.truetype(name, size)
        except (OSError, IOError):
            continue
    try:
        return ImageFont.load_default()
    except Exception:
        return None


def _hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    hex_color = hex_color.lstrip("#")
    if len(hex_color) == 3:
        hex_color = "".join(c * 2 for c in hex_color)
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def _draw_centered_text(draw, text, font, box, fill, max_lines=3):
    """Wrap and center text inside box=(x1,y1,x2,y2)."""
    if not font:
        return
    x1, y1, x2, y2 = box
    max_width = x2 - x1
    words = text.split()
    lines = []
    current = ""
    for w in words:
        test = (current + " " + w).strip()
        try:
            bbox = draw.textbbox((0, 0), test, font=font)
            w_px = bbox[2] - bbox[0]
        except Exception:
            w_px = len(test) * 10
        if w_px <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = w
            if len(lines) >= max_lines - 1:
                break
    if current:
        lines.append(current)

    line_height = 0
    try:
        bbox = draw.textbbox((0, 0), "Hg", font=font)
        line_height = bbox[3] - bbox[1] + 12
    except Exception:
        line_height = 30

    total_height = line_height * len(lines)
    cy = y1 + (y2 - y1 - total_height) // 2
    for line in lines:
        try:
            bbox = draw.textbbox((0, 0), line, font=font)
            w_px = bbox[2] - bbox[0]
        except Exception:
            w_px = len(line) * 10
        cx = x1 + (max_width - w_px) // 2
        draw.text((cx, cy), line, font=font, fill=fill)
        cy += line_height


def generate_og_image(
    product_name: str,
    price: Optional[float] = None,
    store_name: str = "Khan Herbal Stores",
    tagline: str = "",
    category: str = "",
    style: str = "modern",
    output_filename: Optional[str] = None,
) -> Tuple[bool, str]:
    """
    Generate a 1200×630 OG image with Pillow.

    Styles: modern, minimal, bold, gradient, photo
    Returns (ok, path_or_error).
    """
    if not PIL_AVAILABLE:
        return False, "Pillow not installed"

    if style not in ("modern", "minimal", "bold", "gradient", "photo"):
        style = "modern"

    # --- Style colors ---
    style_palette = {
        "modern":   {"bg": "#f1f8e9", "title": "#1b5e20", "accent": "#2e7d32",
                     "subtitle": "#4caf50", "price": "#2e7d32"},
        "minimal":  {"bg": "#ffffff", "title": "#111111", "accent": "#2e7d32",
                     "subtitle": "#555555", "price": "#2e7d32"},
        "bold":     {"bg": "#2e7d32", "title": "#ffffff", "accent": "#ffffff",
                     "subtitle": "#c8e6c9", "price": "#ffffff"},
        "gradient": {"bg1": "#2e7d32", "bg2": "#66bb6a", "title": "#ffffff",
                     "accent": "#ffffff", "subtitle": "#e8f5e9", "price": "#ffffff"},
        "photo":    {"bg": "#1b5e20", "title": "#ffffff", "accent": "#ffffff",
                     "subtitle": "#c8e6c9", "price": "#ffffff"},
    }
    pal = style_palette[style]

    W, H = OG_IMAGE_WIDTH, OG_IMAGE_HEIGHT
    img = Image.new("RGB", (W, H), _hex_to_rgb(pal.get("bg", "#ffffff")))

    # Gradient fill for "gradient" style
    if style == "gradient":
        c1 = _hex_to_rgb(pal["bg1"])
        c2 = _hex_to_rgb(pal["bg2"])
        px = img.load()
        for y in range(H):
            t = y / H
            r = int(c1[0] + (c2[0] - c1[0]) * t)
            g = int(c1[1] + (c2[1] - c1[1]) * t)
            b = int(c1[2] + (c2[2] - c1[2]) * t)
            for x in range(W):
                px[x, y] = (r, g, b)

    draw = ImageDraw.Draw(img)

    # --- Fonts ---
    font_brand = _load_font(32, bold=True)
    font_name = _load_font(72, bold=True)
    font_sub = _load_font(28, bold=False)
    font_price = _load_font(48, bold=True)
    font_foot = _load_font(22, bold=False)

    # --- Top bar with brand ---
    if style == "minimal":
        draw.text((60, 50), store_name, font=font_brand, fill=_hex_to_rgb(pal["title"]))
        draw.line([(60, 100), (W - 60, 100)], fill=_hex_to_rgb(pal["accent"]), width=2)
    else:
        draw.text((60, 50), f"🌿  {store_name}", font=font_brand, fill=_hex_to_rgb(pal["title"]))

    # --- Tagline (top right) ---
    if tagline:
        tl = tagline[:60]
        try:
            bbox = draw.textbbox((0, 0), tl, font=font_sub)
            tw = bbox[2] - bbox[0]
        except Exception:
            tw = len(tl) * 12
        draw.text((W - 60 - tw, 55), tl, font=font_sub, fill=_hex_to_rgb(pal["subtitle"]))

    # --- Product name ---
    _draw_centered_text(
        draw, product_name, font_name,
        (80, 180, W - 80, 320),
        _hex_to_rgb(pal["title"]),
        max_lines=2,
    )

    # --- Category ---
    if category:
        cat_text = category.upper()
        try:
            bbox = draw.textbbox((0, 0), cat_text, font=font_sub)
            cw = bbox[2] - bbox[0]
        except Exception:
            cw = len(cat_text) * 12
        draw.text(((W - cw) // 2, 340), cat_text,
                  font=font_sub, fill=_hex_to_rgb(pal["subtitle"]))

    # --- Price badge ---
    if price is not None and price > 0:
        price_text = f"Rs {price:.0f}"
        try:
            bbox = draw.textbbox((0, 0), price_text, font=font_price)
            pw = bbox[2] - bbox[0]
            ph = bbox[3] - bbox[1]
        except Exception:
            pw, ph = 200, 40

        badge_pad_x = 30
        badge_pad_y = 15
        bx1 = (W - pw) // 2 - badge_pad_x
        bx2 = (W + pw) // 2 + badge_pad_x
        by1 = 430
        by2 = by1 + ph + badge_pad_y * 2

        # Rounded rect background
        if style == "minimal":
            draw.rounded_rectangle([bx1, by1, bx2, by2], radius=15,
                                    outline=_hex_to_rgb(pal["accent"]), width=3)
        else:
            draw.rounded_rectangle([bx1, by1, bx2, by2], radius=15,
                                    fill=_hex_to_rgb(pal["accent"]))
            draw.text(((W - pw) // 2, by1 + badge_pad_y), price_text,
                      font=font_price,
                      fill=(255, 255, 255) if style != "minimal" else _hex_to_rgb(pal["title"]))

        if style == "minimal":
            draw.text(((W - pw) // 2, by1 + badge_pad_y), price_text,
                      font=font_price, fill=_hex_to_rgb(pal["price"]))

    # --- Bottom footer ---
    footer = "Pakistan's trusted herbal store  •  Fast delivery  •  COD available"
    try:
        bbox = draw.textbbox((0, 0), footer, font=font_foot)
        fw = bbox[2] - bbox[0]
    except Exception:
        fw = len(footer) * 10
    draw.text(((W - fw) // 2, H - 60), footer, font=font_foot,
              fill=_hex_to_rgb(pal["subtitle"]))

    # --- Save ---
    if not output_filename:
        safe = re.sub(r"[^\w]", "-", product_name.lower())[:40].strip("-")
        output_filename = f"og_{safe}_{style}_{int(time.time())}.webp"

    out_path = OG_IMAGES_DIR / output_filename
    try:
        img.save(str(out_path), "WEBP", quality=88, method=6)
        return True, str(out_path)
    except Exception as e:
        return False, f"Save failed: {e}"


def generate_og_for_product(product: Dict[str, Any],
                             store: Dict[str, Any],
                             style: str = "modern") -> Tuple[bool, str]:
    """Convenience: generate OG image for a built product dict."""
    name = product.get("name", "")
    price = product.get("price")
    store_name = store.get("name", "Khan Herbal Stores")
    tagline = store.get("tagline", "")
    category = product.get("category_name", "")
    return generate_og_image(
        product_name=name, price=price,
        store_name=store_name, tagline=tagline,
        category=category, style=style,
    )


# =============================================================================
# SECTION 7 — VALIDATION & PREVIEW
# =============================================================================
def validate_og(og: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate an OG dict.
    Returns {valid, warnings, errors, checks}
    """
    errors = []
    warnings = []
    checks = {}

    title = og.get("title", "") or ""
    desc = og.get("description", "") or ""
    image = og.get("image", "") or ""
    url = og.get("url", "") or ""

    # Title
    if not title:
        errors.append("Title is required")
    elif len(title) > OG_TITLE_MAX:
        warnings.append(f"Title too long ({len(title)} > {OG_TITLE_MAX})")
    checks["title_length"] = len(title)

    # Description
    if not desc:
        errors.append("Description is required")
    elif len(desc) < 100:
        warnings.append(f"Description short ({len(desc)} chars)")
    elif len(desc) > OG_DESC_MAX:
        warnings.append(f"Description too long ({len(desc)} > {OG_DESC_MAX})")
    checks["description_length"] = len(desc)

    # Image
    if not image:
        warnings.append("No image set — preview will be grey box")
    elif not image.startswith(("http://", "https://")):
        warnings.append("Image URL should start with http(s)://")
    else:
        ext = image.rsplit(".", 1)[-1].lower() if "." in image else ""
        if ext not in ("jpg", "jpeg", "png", "webp", "gif"):
            warnings.append(f"Uncommon image extension: .{ext}")
    checks["image"] = image

    # URL
    if not url:
        warnings.append("URL is empty")
    elif not url.startswith("https://"):
        warnings.append("OG URL should be HTTPS for best compatibility")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "checks": checks,
    }


def preview_og_ascii(og: Dict[str, Any]) -> str:
    """
    Return an ASCII representation of the OG card preview.
    Useful for CLI test.
    """
    site = og.get("site_name", "Store")
    title = og.get("title", "(no title)")[:70]
    desc = og.get("description", "(no description)")[:100]
    img = og.get("image", "")
    url = og.get("url", "")

    lines = [
        "┌" + "─" * 62 + "┐",
        "│  FACEBOOK / WHATSAPP PREVIEW" + " " * 30 + "│",
        "├" + "─" * 62 + "┤",
        "│  " + (("🖼  IMAGE: " + img[:50]) if img else "(no image)").ljust(58) + "  │",
        "├" + "─" * 62 + "┤",
        "│  " + site.upper()[:58].ljust(58) + "  │",
        "│  " + title.ljust(58) + "  │",
        "│  " + desc[:58].ljust(58) + "  │",
        "│  " + url[:58].ljust(58) + "  │",
        "└" + "─" * 62 + "┘",
    ]
    return "\n".join(lines)


def check_og_image_size(image_path: str) -> Tuple[bool, str]:
    """Validate an OG image file size + dimensions."""
    if not PIL_AVAILABLE:
        return False, "Pillow not installed"
    p = Path(image_path)
    if not p.exists():
        return False, "File not found"
    size = p.stat().st_size
    if size > OG_IMAGE_MAX_BYTES:
        return False, f"Too large: {size/1024/1024:.1f} MB > 5 MB limit"
    try:
        img = Image.open(p)
        w, h = img.size
        ratio = round(w / h, 2)
        if ratio < 1.7 or ratio > 2.1:
            return True, f"OK size ({size/1024:.0f} KB), but ratio {ratio} — 1.91:1 ideal"
        return True, f"OK: {w}×{h}, {size/1024:.0f} KB"
    except Exception as e:
        return False, f"Cannot read image: {e}"


# =============================================================================
# SECTION 8 — STANDALONE TEST
# =============================================================================
if __name__ == "__main__":
    print("open_graph.py v1.0 loaded")
    print()
    print("=== Global defaults ===")
    for k, v in get_global_defaults().items():
        print(f"  {k}: {v}")

    # Simulate product auto-fill
    demo_product = {
        "name": "Almond Oil",
        "price": 450.0,
        "stock": 25,
        "category_name": "Herbal Oils",
        "product_url": "https://example.com/product/almond-oil/",
        "featured_image": "https://example.com/almond.webp",
        "rankmath": {
            "meta:rank_math_title": "Almond Oil — Best for Hair & Skin",
            "meta:rank_math_description":
                "Buy Almond Oil at Khan Herbal Stores. Pure, cold-pressed, "
                "cold-pressed, fast delivery across Pakistan. Order now with COD.",
        },
    }
    global_og = get_global_defaults()
    og = auto_fill_og("product", demo_product, global_og)
    print("\n=== Auto-filled OG for 'Almond Oil' ===")
    for k, v in og.items():
        print(f"  {k}: {str(v)[:80]}")

    print("\n=== Validation ===")
    v = validate_og(og)
    print(f"  valid:    {v['valid']}")
    print(f"  errors:   {v['errors']}")
    print(f"  warnings: {v['warnings']}")

    print("\n=== ASCII Preview ===")
    print(preview_og_ascii(og))

    print("\n=== Meta HTML (first 5 lines) ===")
    html = build_og_meta_html(og)
    for line in html.split("\n")[:5]:
        print("  " + line)

    print("\n=== RankMath meta ===")
    for k, v in build_rankmath_og_meta(og).items():
        print(f"  {k}: {v[:70]}")

    # Image generator test
    if PIL_AVAILABLE:
        print("\n=== Generating OG image (modern style) ===")
        ok, path = generate_og_image(
            product_name="Almond Oil",
            price=450.0,
            store_name="Khan Herbal Stores",
            tagline="Authentic Herbal Remedies",
            category="Herbal Oils",
            style="modern",
        )
        if ok:
            print(f"  ✅ Generated: {path}")
            check_ok, msg = check_og_image_size(path)
            print(f"  Size check: {msg}")
        else:
            print(f"  ❌ {path}")
    else:
        print("\n(Pillow not installed — skipping image generation)")