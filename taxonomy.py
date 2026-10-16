# =============================================================================
# KHAN HERBAL STORES — TAXONOMY MANAGER v1.0
# =============================================================================
# File: taxonomy.py
# Purpose: Manage WooCommerce + WordPress taxonomies:
#   - Categories (product_cat, category)
#   - Brands (auto-detect: native WC 9.x / pa_brand attribute / plugin)
#   - Tags (product_tag, post_tag)
#   - Attributes (global WC attributes + terms)
#
# SECTION HIERARCHY:
#   SECTION 1  — Imports & Constants
#   SECTION 2  — Helper Functions
#   SECTION 3  — Categories (CRUD)
#   SECTION 4  — Brands (CRUD + Auto-detect)
#   SECTION 5  — Tags (CRUD for products + posts)
#   SECTION 6  — Attributes (CRUD + Terms)
#   SECTION 7  — Bulk Operations
#   SECTION 8  — Caching Layer
#   SECTION 9  — Standalone Test
# =============================================================================

# =============================================================================
# SECTION 1 — IMPORTS & CONSTANTS
# =============================================================================
import re
import json
import time
from typing import Dict, List, Any, Optional, Tuple

try:
    import requests
except ImportError:
    print("ERROR: requests not installed. Run: pip install requests")
    raise

from slugify import slugify

# --- HTTP constants ---
REQUEST_TIMEOUT = 20
USER_AGENT = "KhanHerbalFactory/3.0 (+taxonomy)"

# --- Endpoints ---
WC_CATEGORIES_ENDPOINT   = "/wp-json/wc/v3/products/categories"
WC_TAGS_ENDPOINT         = "/wp-json/wc/v3/products/tags"
WC_ATTRIBUTES_ENDPOINT   = "/wp-json/wc/v3/products/attributes"
WC_BRANDS_ENDPOINT       = "/wp-json/wc/v3/products/brands"   # WC 9.x native
WP_CATEGORIES_ENDPOINT   = "/wp-json/wp/v2/categories"
WP_TAGS_ENDPOINT         = "/wp-json/wp/v2/tags"

# --- Caching (in-memory per session) ---
_CACHE: Dict[str, Any] = {}
_CACHE_TTL = 300  # 5 minutes


# =============================================================================
# SECTION 2 — HELPER FUNCTIONS
# =============================================================================
def _redact(text):
    """Remove credentials from any log text."""
    if not isinstance(text, str):
        text = str(text)
    for p in [r"ck_[A-Za-z0-9]{20,}", r"cs_[A-Za-z0-9]{20,}",
              r"(?i)(authorization|bearer|password|secret)\s*[:=]\s*\S+"]:
        text = re.sub(p, "***REDACTED***", text)
    return text


def _slugify(name: str) -> str:
    """URL-safe slug from any name."""
    return slugify(name, lowercase=True)[:75].strip("-")


def _auth(ck: str, cs: str) -> Tuple[str, str]:
    return (ck, cs)


def _request(method, url, ck, cs, json_body=None, params=None):
    """
    Safe HTTP wrapper with error handling.
    Returns (ok, data, error_message).
    """
    try:
        r = requests.request(
            method=method.upper(),
            url=url,
            auth=_auth(ck, cs),
            json=json_body,
            params=params,
            headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
            timeout=REQUEST_TIMEOUT,
        )
    except requests.exceptions.SSLError as e:
        return False, None, f"SSL error: {_redact(str(e))}"
    except requests.exceptions.ConnectTimeout:
        return False, None, "Connection timed out"
    except requests.exceptions.ReadTimeout:
        return False, None, "Server took too long to respond"
    except requests.exceptions.ConnectionError as e:
        return False, None, f"Cannot connect: {_redact(str(e))[:150]}"
    except requests.exceptions.RequestException as e:
        return False, None, f"Request failed: {_redact(str(e))[:150]}"

    # Status handling
    if r.status_code in (200, 201, 204):
        try:
            return True, (r.json() if r.text else None), ""
        except ValueError:
            return True, None, ""

    if r.status_code == 401:
        return False, None, "401 Unauthorized — check API keys"
    if r.status_code == 403:
        return False, None, "403 Forbidden — insufficient permissions"
    if r.status_code == 404:
        return False, None, "404 Not Found — endpoint may not exist"
    if r.status_code >= 500:
        return False, None, f"{r.status_code} Server error"

    # 4xx with message
    try:
        msg = r.json().get("message", r.text[:200])
    except Exception:
        msg = r.text[:200]
    return False, None, f"HTTP {r.status_code}: {_redact(msg)}"


def _cache_get(key):
    """Get cached value if not expired."""
    if key in _CACHE:
        val, ts = _CACHE[key]
        if time.time() - ts < _CACHE_TTL:
            return val
    return None


def _cache_set(key, value):
    """Set cache with timestamp."""
    _CACHE[key] = (value, time.time())


def clear_cache():
    """Clear all cached taxonomy data."""
    _CACHE.clear()


# =============================================================================
# SECTION 3 — CATEGORIES (WooCommerce Products + WP Posts)
# =============================================================================

# -----------------------------------------------------------------------------
# 3.1 — List Categories
# -----------------------------------------------------------------------------
def list_wc_categories(site_url, ck, cs, search="", per_page=100,
                        use_cache=True) -> Tuple[bool, List[Dict], str]:
    """
    List all WooCommerce product categories.
    Returns list of {id, name, slug, parent, count, description, image}
    """
    cache_key = f"wc_cats_{site_url}_{search}"
    if use_cache and not search:
        cached = _cache_get(cache_key)
        if cached is not None:
            return True, cached, ""

    url = f"{site_url.rstrip('/')}{WC_CATEGORIES_ENDPOINT}"
    params = {"per_page": per_page, "orderby": "name", "order": "asc"}
    if search:
        params["search"] = search

    ok, data, err = _request("GET", url, ck, cs, params=params)
    if not ok:
        return False, [], err
    if not isinstance(data, list):
        return False, [], "Unexpected response format"

    if use_cache and not search:
        _cache_set(cache_key, data)
    return True, data, ""


def list_wp_categories(site_url, ck, cs, search="", per_page=100,
                        use_cache=True) -> Tuple[bool, List[Dict], str]:
    """List all WordPress blog post categories."""
    cache_key = f"wp_cats_{site_url}_{search}"
    if use_cache and not search:
        cached = _cache_get(cache_key)
        if cached is not None:
            return True, cached, ""

    url = f"{site_url.rstrip('/')}{WP_CATEGORIES_ENDPOINT}"
    params = {"per_page": per_page, "orderby": "name", "order": "asc"}
    if search:
        params["search"] = search

    ok, data, err = _request("GET", url, ck, cs, params=params)
    if not ok:
        return False, [], err
    if not isinstance(data, list):
        return False, [], "Unexpected response format"

    if use_cache and not search:
        _cache_set(cache_key, data)
    return True, data, ""


# -----------------------------------------------------------------------------
# 3.2 — Create Category
# -----------------------------------------------------------------------------
def create_wc_category(site_url, ck, cs, name,
                        slug=None, parent_id=0, description="",
                        image_url="") -> Tuple[bool, Optional[Dict], str]:
    """
    Create a new WooCommerce product category.
    Returns (ok, category_dict_or_none, error).
    """
    if not name or not name.strip():
        return False, None, "Category name is required"

    url = f"{site_url.rstrip('/')}{WC_CATEGORIES_ENDPOINT}"
    payload = {
        "name": name.strip(),
        "slug": slug or _slugify(name),
        "parent": parent_id or 0,
        "description": description or "",
    }
    if image_url:
        payload["image"] = {"src": image_url}

    ok, data, err = _request("POST", url, ck, cs, json_body=payload)
    if not ok:
        return False, None, err
    _CACHE.clear()  # Invalidate cache
    return True, data, ""


def create_wp_category(site_url, ck, cs, name,
                        slug=None, parent_id=0,
                        description="") -> Tuple[bool, Optional[Dict], str]:
    """Create a new WordPress blog category."""
    if not name or not name.strip():
        return False, None, "Category name is required"

    url = f"{site_url.rstrip('/')}{WP_CATEGORIES_ENDPOINT}"
    payload = {
        "name": name.strip(),
        "slug": slug or _slugify(name),
        "parent": parent_id or 0,
        "description": description or "",
    }

    ok, data, err = _request("POST", url, ck, cs, json_body=payload)
    if not ok:
        return False, None, err
    _CACHE.clear()
    return True, data, ""


# -----------------------------------------------------------------------------
# 3.3 — Update Category
# -----------------------------------------------------------------------------
def update_wc_category(site_url, ck, cs, category_id, **fields):
    """Update an existing WooCommerce category."""
    if not category_id:
        return False, None, "Category ID required"

    url = f"{site_url.rstrip('/')}{WC_CATEGORIES_ENDPOINT}/{category_id}"
    allowed = {"name", "slug", "parent", "description", "image", "menu_order"}
    payload = {k: v for k, v in fields.items() if k in allowed and v is not None}

    if not payload:
        return False, None, "No fields to update"

    ok, data, err = _request("PUT", url, ck, cs, json_body=payload)
    if not ok:
        return False, None, err
    _CACHE.clear()
    return True, data, ""


def update_wp_category(site_url, ck, cs, category_id, **fields):
    """Update an existing WordPress category."""
    if not category_id:
        return False, None, "Category ID required"

    url = f"{site_url.rstrip('/')}{WP_CATEGORIES_ENDPOINT}/{category_id}"
    allowed = {"name", "slug", "parent", "description"}
    payload = {k: v for k, v in fields.items() if k in allowed and v is not None}

    if not payload:
        return False, None, "No fields to update"

    ok, data, err = _request("POST", url, ck, cs, json_body=payload)
    if not ok:
        return False, None, err
    _CACHE.clear()
    return True, data, ""


# -----------------------------------------------------------------------------
# 3.4 — Delete Category
# -----------------------------------------------------------------------------
def delete_wc_category(site_url, ck, cs, category_id, force=True):
    """
    Delete WooCommerce category. force=True permanent.
    WC always uses force=true for hard delete.
    """
    if not category_id:
        return False, "Category ID required"

    url = f"{site_url.rstrip('/')}{WC_CATEGORIES_ENDPOINT}/{category_id}"
    ok, _, err = _request("DELETE", url, ck, cs, params={"force": str(force).lower()})
    if not ok:
        return False, err
    _CACHE.clear()
    return True, ""


def delete_wp_category(site_url, ck, cs, category_id, force=True):
    """Delete WordPress category."""
    if not category_id:
        return False, "Category ID required"

    url = f"{site_url.rstrip('/')}{WP_CATEGORIES_ENDPOINT}/{category_id}"
    ok, _, err = _request("DELETE", url, ck, cs, params={"force": str(force).lower()})
    if not ok:
        return False, err
    _CACHE.clear()
    return True, ""


# -----------------------------------------------------------------------------
# 3.5 — Get Category by ID
# -----------------------------------------------------------------------------
def get_wc_category(site_url, ck, cs, category_id):
    url = f"{site_url.rstrip('/')}{WC_CATEGORIES_ENDPOINT}/{category_id}"
    ok, data, err = _request("GET", url, ck, cs)
    if not ok:
        return False, None, err
    return True, data, ""


def get_wp_category(site_url, ck, cs, category_id):
    url = f"{site_url.rstrip('/')}{WP_CATEGORIES_ENDPOINT}/{category_id}"
    ok, data, err = _request("GET", url, ck, cs)
    if not ok:
        return False, None, err
    return True, data, ""


# =============================================================================
# SECTION 4 — BRANDS (Auto-detect: native WC / custom attribute / plugin)
# =============================================================================
# WooCommerce brands can exist in 3 places:
#   A) WC 9.x native "product_brand" taxonomy → /wp-json/wc/v3/products/brands
#   B) Custom attribute "pa_brand"           → /wp-json/wc/v3/products/attributes
#   C) 3rd-party plugin (Perfect Brands etc.) → varies
#
# This module auto-detects which is available and uses it.

_BRAND_METHOD_CACHE: Dict[str, str] = {}


def detect_brand_method(site_url, ck, cs) -> Tuple[str, str]:
    """
    Detect which brand method the site uses.
    Returns (method_name, details).
      method_name: "native" | "attribute" | "plugin" | "none"
    """
    key = site_url.rstrip("/")
    if key in _BRAND_METHOD_CACHE:
        method = _BRAND_METHOD_CACHE[key]
        return method, "cached"

    # Try 1: Native WC 9.x brands endpoint
    url = f"{key}{WC_BRANDS_ENDPOINT}"
    ok, data, err = _request("GET", url, ck, cs, params={"per_page": 1})
    if ok:
        _BRAND_METHOD_CACHE[key] = "native"
        return "native", "Native WC brands"

    # Try 2: Custom attribute "pa_brand"
    url = f"{key}{WC_ATTRIBUTES_ENDPOINT}"
    ok, data, err = _request("GET", url, ck, cs)
    if ok and isinstance(data, list):
        for attr in data:
            slug = (attr.get("slug") or "").lower()
            if slug in ("pa_brand", "brand", "pa_brands", "brands"):
                _BRAND_METHOD_CACHE[key] = f"attribute:{attr['id']}"
                return f"attribute:{attr['id']}", f"Attribute: {attr.get('name')}"

    _BRAND_METHOD_CACHE[key] = "none"
    return "none", "No brand system found"


# -----------------------------------------------------------------------------
# 4.1 — List Brands
# -----------------------------------------------------------------------------
def list_brands(site_url, ck, cs, search="") -> Tuple[bool, List[Dict], str]:
    """
    List brands using auto-detected method.
    Returns list of {id, name, slug, count, description}
    """
    method, _ = detect_brand_method(site_url, ck, cs)

    if method == "native":
        url = f"{site_url.rstrip('/')}{WC_BRANDS_ENDPOINT}"
        params = {"per_page": 100, "orderby": "name", "order": "asc"}
        if search:
            params["search"] = search
        ok, data, err = _request("GET", url, ck, cs, params=params)
        if ok and isinstance(data, list):
            return True, data, ""
        return False, [], err or "Failed to list native brands"

    elif method.startswith("attribute:"):
        attr_id = int(method.split(":")[1])
        return list_attribute_terms(site_url, ck, cs, attr_id, search)

    else:
        return False, [], "No brand system detected on this site"


# -----------------------------------------------------------------------------
# 4.2 — Create Brand
# -----------------------------------------------------------------------------
def create_brand(site_url, ck, cs, name, slug=None,
                  description="", image_url="") -> Tuple[bool, Optional[Dict], str]:
    """Create brand via detected method."""
    if not name or not name.strip():
        return False, None, "Brand name is required"

    method, _ = detect_brand_method(site_url, ck, cs)

    if method == "native":
        url = f"{site_url.rstrip('/')}{WC_BRANDS_ENDPOINT}"
        payload = {
            "name": name.strip(),
            "slug": slug or _slugify(name),
            "description": description or "",
        }
        if image_url:
            payload["image"] = {"src": image_url}
        ok, data, err = _request("POST", url, ck, cs, json_body=payload)
        if not ok:
            return False, None, err
        _CACHE.clear()
        return True, data, ""

    elif method.startswith("attribute:"):
        attr_id = int(method.split(":")[1])
        ok, data, err = create_attribute_term(
            site_url, ck, cs, attr_id, name,
            slug=slug, description=description
        )
        if not ok:
            return False, None, err
        return True, data, ""

    else:
        return False, None, (
            "No brand system detected. Create a global attribute named "
            "'brand' (or 'pa_brand') in WooCommerce → Products → Attributes."
        )


# -----------------------------------------------------------------------------
# 4.3 — Update Brand
# -----------------------------------------------------------------------------
def update_brand(site_url, ck, cs, brand_id, **fields):
    method, _ = detect_brand_method(site_url, ck, cs)

    if method == "native":
        url = f"{site_url.rstrip('/')}{WC_BRANDS_ENDPOINT}/{brand_id}"
        allowed = {"name", "slug", "description", "image"}
        payload = {k: v for k, v in fields.items() if k in allowed and v is not None}
        if not payload:
            return False, None, "No fields to update"
        ok, data, err = _request("PUT", url, ck, cs, json_body=payload)
        if not ok:
            return False, None, err
        _CACHE.clear()
        return True, data, ""

    elif method.startswith("attribute:"):
        attr_id = int(method.split(":")[1])
        return update_attribute_term(
            site_url, ck, cs, attr_id, brand_id, **fields
        )

    else:
        return False, None, "No brand system detected"


# -----------------------------------------------------------------------------
# 4.4 — Delete Brand
# -----------------------------------------------------------------------------
def delete_brand(site_url, ck, cs, brand_id, force=True):
    method, _ = detect_brand_method(site_url, ck, cs)

    if method == "native":
        url = f"{site_url.rstrip('/')}{WC_BRANDS_ENDPOINT}/{brand_id}"
        ok, _, err = _request("DELETE", url, ck, cs,
                              params={"force": str(force).lower()})
        if not ok:
            return False, err
        _CACHE.clear()
        return True, ""

    elif method.startswith("attribute:"):
        attr_id = int(method.split(":")[1])
        return delete_attribute_term(site_url, ck, cs, attr_id, brand_id, force=force)

    else:
        return False, "No brand system detected"


# =============================================================================
# SECTION 5 — TAGS (Products + Blog Posts)
# =============================================================================

# -----------------------------------------------------------------------------
# 5.1 — List Tags
# -----------------------------------------------------------------------------
def list_wc_tags(site_url, ck, cs, search="", per_page=100,
                  use_cache=True) -> Tuple[bool, List[Dict], str]:
    """List WooCommerce product tags."""
    cache_key = f"wc_tags_{site_url}_{search}"
    if use_cache and not search:
        cached = _cache_get(cache_key)
        if cached is not None:
            return True, cached, ""

    url = f"{site_url.rstrip('/')}{WC_TAGS_ENDPOINT}"
    params = {"per_page": per_page, "orderby": "name", "order": "asc"}
    if search:
        params["search"] = search

    ok, data, err = _request("GET", url, ck, cs, params=params)
    if not ok:
        return False, [], err
    if not isinstance(data, list):
        return False, [], "Unexpected response"

    if use_cache and not search:
        _cache_set(cache_key, data)
    return True, data, ""


def list_wp_tags(site_url, ck, cs, search="", per_page=100,
                  use_cache=True) -> Tuple[bool, List[Dict], str]:
    """List WordPress blog post tags."""
    cache_key = f"wp_tags_{site_url}_{search}"
    if use_cache and not search:
        cached = _cache_get(cache_key)
        if cached is not None:
            return True, cached, ""

    url = f"{site_url.rstrip('/')}{WP_TAGS_ENDPOINT}"
    params = {"per_page": per_page, "orderby": "name", "order": "asc"}
    if search:
        params["search"] = search

    ok, data, err = _request("GET", url, ck, cs, params=params)
    if not ok:
        return False, [], err
    if not isinstance(data, list):
        return False, [], "Unexpected response"

    if use_cache and not search:
        _cache_set(cache_key, data)
    return True, data, ""


# -----------------------------------------------------------------------------
# 5.2 — Create Tag
# -----------------------------------------------------------------------------
def create_wc_tag(site_url, ck, cs, name, slug=None,
                    description="") -> Tuple[bool, Optional[Dict], str]:
    """Create WooCommerce product tag."""
    if not name or not name.strip():
        return False, None, "Tag name required"

    url = f"{site_url.rstrip('/')}{WC_TAGS_ENDPOINT}"
    payload = {
        "name": name.strip(),
        "slug": slug or _slugify(name),
        "description": description or "",
    }
    ok, data, err = _request("POST", url, ck, cs, json_body=payload)
    if not ok:
        return False, None, err
    _CACHE.clear()
    return True, data, ""


def create_wp_tag(site_url, ck, cs, name, slug=None,
                    description="") -> Tuple[bool, Optional[Dict], str]:
    """Create WordPress blog post tag."""
    if not name or not name.strip():
        return False, None, "Tag name required"

    url = f"{site_url.rstrip('/')}{WP_TAGS_ENDPOINT}"
    payload = {
        "name": name.strip(),
        "slug": slug or _slugify(name),
        "description": description or "",
    }
    ok, data, err = _request("POST", url, ck, cs, json_body=payload)
    if not ok:
        return False, None, err
    _CACHE.clear()
    return True, data, ""


# -----------------------------------------------------------------------------
# 5.3 — Update Tag
# -----------------------------------------------------------------------------
def update_wc_tag(site_url, ck, cs, tag_id, **fields):
    url = f"{site_url.rstrip('/')}{WC_TAGS_ENDPOINT}/{tag_id}"
    allowed = {"name", "slug", "description"}
    payload = {k: v for k, v in fields.items() if k in allowed and v is not None}
    if not payload:
        return False, None, "No fields to update"
    ok, data, err = _request("PUT", url, ck, cs, json_body=payload)
    if not ok:
        return False, None, err
    _CACHE.clear()
    return True, data, ""


def update_wp_tag(site_url, ck, cs, tag_id, **fields):
    url = f"{site_url.rstrip('/')}{WP_TAGS_ENDPOINT}/{tag_id}"
    allowed = {"name", "slug", "description"}
    payload = {k: v for k, v in fields.items() if k in allowed and v is not None}
    if not payload:
        return False, None, "No fields to update"
    ok, data, err = _request("POST", url, ck, cs, json_body=payload)
    if not ok:
        return False, None, err
    _CACHE.clear()
    return True, data, ""


# -----------------------------------------------------------------------------
# 5.4 — Delete Tag
# -----------------------------------------------------------------------------
def delete_wc_tag(site_url, ck, cs, tag_id, force=True):
    url = f"{site_url.rstrip('/')}{WC_TAGS_ENDPOINT}/{tag_id}"
    ok, _, err = _request("DELETE", url, ck, cs,
                          params={"force": str(force).lower()})
    if not ok:
        return False, err
    _CACHE.clear()
    return True, ""


def delete_wp_tag(site_url, ck, cs, tag_id, force=True):
    url = f"{site_url.rstrip('/')}{WP_TAGS_ENDPOINT}/{tag_id}"
    ok, _, err = _request("DELETE", url, ck, cs,
                          params={"force": str(force).lower()})
    if not ok:
        return False, err
    _CACHE.clear()
    return True, ""


# =============================================================================
# SECTION 6 — ATTRIBUTES (Global WC + Terms)
# =============================================================================

# -----------------------------------------------------------------------------
# 6.1 — List Attributes
# -----------------------------------------------------------------------------
def list_wc_attributes(site_url, ck, cs) -> Tuple[bool, List[Dict], str]:
    """List global WooCommerce product attributes."""
    cached = _cache_get(f"wc_attrs_{site_url}")
    if cached is not None:
        return True, cached, ""

    url = f"{site_url.rstrip('/')}{WC_ATTRIBUTES_ENDPOINT}"
    ok, data, err = _request("GET", url, ck, cs)
    if not ok:
        return False, [], err
    if not isinstance(data, list):
        return False, [], "Unexpected response"

    _cache_set(f"wc_attrs_{site_url}", data)
    return True, data, ""


# -----------------------------------------------------------------------------
# 6.2 — Create Attribute
# -----------------------------------------------------------------------------
def create_wc_attribute(site_url, ck, cs, name, slug=None,
                         attr_type="select", order_by="menu_order",
                         has_archives=False) -> Tuple[bool, Optional[Dict], str]:
    """
    Create global WooCommerce attribute.
    attr_type: select | text
    order_by: menu_order | name | name_num | id
    """
    if not name or not name.strip():
        return False, None, "Attribute name required"

    url = f"{site_url.rstrip('/')}{WC_ATTRIBUTES_ENDPOINT}"
    payload = {
        "name": name.strip(),
        "slug": slug or f"pa_{_slugify(name)}",
        "type": attr_type,
        "order_by": order_by,
        "has_archives": bool(has_archives),
    }
    ok, data, err = _request("POST", url, ck, cs, json_body=payload)
    if not ok:
        return False, None, err
    _CACHE.clear()
    return True, data, ""


# -----------------------------------------------------------------------------
# 6.3 — Update Attribute
# -----------------------------------------------------------------------------
def update_wc_attribute(site_url, ck, cs, attr_id, **fields):
    url = f"{site_url.rstrip('/')}{WC_ATTRIBUTES_ENDPOINT}/{attr_id}"
    allowed = {"name", "slug", "type", "order_by", "has_archives"}
    payload = {k: v for k, v in fields.items() if k in allowed and v is not None}
    if not payload:
        return False, None, "No fields to update"
    ok, data, err = _request("PUT", url, ck, cs, json_body=payload)
    if not ok:
        return False, None, err
    _CACHE.clear()
    return True, data, ""


# -----------------------------------------------------------------------------
# 6.4 — Delete Attribute
# -----------------------------------------------------------------------------
def delete_wc_attribute(site_url, ck, cs, attr_id, force=True):
    url = f"{site_url.rstrip('/')}{WC_ATTRIBUTES_ENDPOINT}/{attr_id}"
    ok, _, err = _request("DELETE", url, ck, cs,
                          params={"force": str(force).lower()})
    if not ok:
        return False, err
    _CACHE.clear()
    return True, ""


# -----------------------------------------------------------------------------
# 6.5 — Attribute Terms
# -----------------------------------------------------------------------------
def list_attribute_terms(site_url, ck, cs, attr_id,
                          search="", per_page=100) -> Tuple[bool, List[Dict], str]:
    """List terms for a WC attribute."""
    url = f"{site_url.rstrip('/')}{WC_ATTRIBUTES_ENDPOINT}/{attr_id}/terms"
    params = {"per_page": per_page, "orderby": "name", "order": "asc"}
    if search:
        params["search"] = search

    ok, data, err = _request("GET", url, ck, cs, params=params)
    if not ok:
        return False, [], err
    if not isinstance(data, list):
        return False, [], "Unexpected response"
    return True, data, ""


def create_attribute_term(site_url, ck, cs, attr_id, name,
                           slug=None, description="",
                           menu_order=0) -> Tuple[bool, Optional[Dict], str]:
    """Add a term to a WC attribute."""
    if not name or not name.strip():
        return False, None, "Term name required"

    url = f"{site_url.rstrip('/')}{WC_ATTRIBUTES_ENDPOINT}/{attr_id}/terms"
    payload = {
        "name": name.strip(),
        "slug": slug or _slugify(name),
        "description": description or "",
        "menu_order": menu_order,
    }
    ok, data, err = _request("POST", url, ck, cs, json_body=payload)
    if not ok:
        return False, None, err
    _CACHE.clear()
    return True, data, ""


def update_attribute_term(site_url, ck, cs, attr_id, term_id, **fields):
    url = f"{site_url.rstrip('/')}{WC_ATTRIBUTES_ENDPOINT}/{attr_id}/terms/{term_id}"
    allowed = {"name", "slug", "description", "menu_order"}
    payload = {k: v for k, v in fields.items() if k in allowed and v is not None}
    if not payload:
        return False, None, "No fields to update"
    ok, data, err = _request("PUT", url, ck, cs, json_body=payload)
    if not ok:
        return False, None, err
    _CACHE.clear()
    return True, data, ""


def delete_attribute_term(site_url, ck, cs, attr_id, term_id, force=True):
    url = f"{site_url.rstrip('/')}{WC_ATTRIBUTES_ENDPOINT}/{attr_id}/terms/{term_id}"
    ok, _, err = _request("DELETE", url, ck, cs,
                          params={"force": str(force).lower()})
    if not ok:
        return False, err
    _CACHE.clear()
    return True, ""


# =============================================================================
# SECTION 7 — BULK OPERATIONS
# =============================================================================
def bulk_create_wc_categories(site_url, ck, cs, items) -> Dict[str, Any]:
    """
    Bulk create WC categories.
    items: list of {name, parent_id, description}
    Returns {created, failed, errors}
    """
    created, failed, errors = [], [], []
    for item in items:
        ok, data, err = create_wc_category(
            site_url, ck, cs,
            name=item.get("name", ""),
            parent_id=item.get("parent_id", 0),
            description=item.get("description", ""),
        )
        if ok:
            created.append(data)
        else:
            failed.append(item.get("name", ""))
            errors.append(f"{item.get('name')}: {err}")
    return {"created": len(created), "failed": len(failed), "errors": errors}


def bulk_create_wc_tags(site_url, ck, cs, names) -> Dict[str, Any]:
    """Bulk create WC tags from list of names."""
    created, failed, errors = [], [], []
    for name in names:
        ok, data, err = create_wc_tag(site_url, ck, cs, name)
        if ok:
            created.append(data)
        else:
            failed.append(name)
            errors.append(f"{name}: {err}")
    return {"created": len(created), "failed": len(failed), "errors": errors}


def bulk_create_attribute_terms(site_url, ck, cs, attr_id, names) -> Dict[str, Any]:
    """Bulk create terms under an attribute."""
    created, failed, errors = [], [], []
    for name in names:
        ok, data, err = create_attribute_term(site_url, ck, cs, attr_id, name)
        if ok:
            created.append(data)
        else:
            failed.append(name)
            errors.append(f"{name}: {err}")
    return {"created": len(created), "failed": len(failed), "errors": errors}


def import_taxonomy_csv(site_url, ck, cs, csv_text, taxonomy_type) -> Dict[str, Any]:
    """
    Import taxonomy from CSV text.
    CSV format: name,slug,parent,description
    taxonomy_type: 'category' | 'tag' | 'brand' | 'attribute'
    """
    import csv as _csv
    import io

    created = failed = 0
    errors = []
    reader = _csv.DictReader(io.StringIO(csv_text))

    for row in reader:
        name = (row.get("name") or "").strip()
        if not name:
            continue

        slug = (row.get("slug") or "").strip() or None
        desc = (row.get("description") or "").strip()

        try:
            if taxonomy_type == "category":
                parent = int(row.get("parent") or 0)
                ok, _, err = create_wc_category(site_url, ck, cs, name,
                                                 slug=slug, parent_id=parent,
                                                 description=desc)
            elif taxonomy_type == "tag":
                ok, _, err = create_wc_tag(site_url, ck, cs, name,
                                            slug=slug, description=desc)
            elif taxonomy_type == "brand":
                ok, _, err = create_brand(site_url, ck, cs, name,
                                           slug=slug, description=desc)
            elif taxonomy_type == "attribute":
                ok, _, err = create_wc_attribute(site_url, ck, cs, name, slug=slug)
            else:
                ok, err = False, f"Unknown type: {taxonomy_type}"

            if ok:
                created += 1
            else:
                failed += 1
                errors.append(f"{name}: {err}")
        except Exception as e:
            failed += 1
            errors.append(f"{name}: {_redact(str(e))[:100]}")

    return {"created": created, "failed": failed, "errors": errors[:20]}


# =============================================================================
# SECTION 8 — UNIFIED API (for UI)
# =============================================================================
def list_all(site_url, ck, cs, taxonomy_type) -> Tuple[bool, List[Dict], str]:
    """Unified list dispatcher."""
    if taxonomy_type == "wc_categories":
        return list_wc_categories(site_url, ck, cs)
    elif taxonomy_type == "wp_categories":
        return list_wp_categories(site_url, ck, cs)
    elif taxonomy_type == "brands":
        return list_brands(site_url, ck, cs)
    elif taxonomy_type == "wc_tags":
        return list_wc_tags(site_url, ck, cs)
    elif taxonomy_type == "wp_tags":
        return list_wp_tags(site_url, ck, cs)
    elif taxonomy_type == "wc_attributes":
        return list_wc_attributes(site_url, ck, cs)
    else:
        return False, [], f"Unknown taxonomy: {taxonomy_type}"


def create_one(site_url, ck, cs, taxonomy_type, name,
                slug=None, parent_id=0, description="",
                attr_id=None) -> Tuple[bool, Optional[Dict], str]:
    """Unified create dispatcher."""
    if taxonomy_type == "wc_categories":
        return create_wc_category(site_url, ck, cs, name,
                                    slug=slug, parent_id=parent_id,
                                    description=description)
    elif taxonomy_type == "wp_categories":
        return create_wp_category(site_url, ck, cs, name,
                                    slug=slug, parent_id=parent_id,
                                    description=description)
    elif taxonomy_type == "brands":
        return create_brand(site_url, ck, cs, name,
                             slug=slug, description=description)
    elif taxonomy_type == "wc_tags":
        return create_wc_tag(site_url, ck, cs, name,
                              slug=slug, description=description)
    elif taxonomy_type == "wp_tags":
        return create_wp_tag(site_url, ck, cs, name,
                              slug=slug, description=description)
    elif taxonomy_type == "wc_attributes":
        return create_wc_attribute(site_url, ck, cs, name, slug=slug)
    elif taxonomy_type == "attribute_terms":
        if not attr_id:
            return False, None, "attr_id required for terms"
        return create_attribute_term(site_url, ck, cs, attr_id, name,
                                       slug=slug, description=description)
    else:
        return False, None, f"Unknown taxonomy: {taxonomy_type}"


def update_one(site_url, ck, cs, taxonomy_type, item_id, **fields):
    """Unified update dispatcher."""
    if taxonomy_type == "wc_categories":
        return update_wc_category(site_url, ck, cs, item_id, **fields)
    elif taxonomy_type == "wp_categories":
        return update_wp_category(site_url, ck, cs, item_id, **fields)
    elif taxonomy_type == "brands":
        return update_brand(site_url, ck, cs, item_id, **fields)
    elif taxonomy_type == "wc_tags":
        return update_wc_tag(site_url, ck, cs, item_id, **fields)
    elif taxonomy_type == "wp_tags":
        return update_wp_tag(site_url, ck, cs, item_id, **fields)
    elif taxonomy_type == "wc_attributes":
        return update_wc_attribute(site_url, ck, cs, item_id, **fields)
    else:
        return False, None, f"Unknown taxonomy: {taxonomy_type}"


def delete_one(site_url, ck, cs, taxonomy_type, item_id,
                force=True, attr_id=None) -> Tuple[bool, str]:
    """Unified delete dispatcher."""
    if taxonomy_type == "wc_categories":
        return delete_wc_category(site_url, ck, cs, item_id, force=force)
    elif taxonomy_type == "wp_categories":
        return delete_wp_category(site_url, ck, cs, item_id, force=force)
    elif taxonomy_type == "brands":
        return delete_brand(site_url, ck, cs, item_id, force=force)
    elif taxonomy_type == "wc_tags":
        return delete_wc_tag(site_url, ck, cs, item_id, force=force)
    elif taxonomy_type == "wp_tags":
        return delete_wp_tag(site_url, ck, cs, item_id, force=force)
    elif taxonomy_type == "wc_attributes":
        return delete_wc_attribute(site_url, ck, cs, item_id, force=force)
    elif taxonomy_type == "attribute_terms":
        if not attr_id:
            return False, "attr_id required"
        return delete_attribute_term(site_url, ck, cs, attr_id, item_id, force=force)
    else:
        return False, f"Unknown taxonomy: {taxonomy_type}"


# =============================================================================
# SECTION 9 — STANDALONE TEST
# =============================================================================
if __name__ == "__main__":
    print("taxonomy.py v1.0 loaded")
    print("Functions available:")
    print("  - Categories: list/create/update/delete (WC + WP)")
    print("  - Brands: auto-detect + list/create/update/delete")
    print("  - Tags: list/create/update/delete (WC + WP)")
    print("  - Attributes: list/create/update/delete + terms")
    print("  - Bulk: bulk_create_*, import_taxonomy_csv")
    print("  - Unified: list_all, create_one, update_one, delete_one")
    print()
    print("This module requires site_url + ck + cs to function.")