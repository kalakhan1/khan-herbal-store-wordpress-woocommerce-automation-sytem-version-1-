# =============================================================================
# KHAN HERBAL STORES — WORDPRESS CLIENT v1.0
# =============================================================================
# File: wp_client.py
# Purpose: Manage live WordPress blog posts + live WooCommerce products.
#          - List, fetch, update, delete posts
#          - List, fetch, update, delete products
#          - Update images on products
#          - Preview changes (diff)
#
# SECTION HIERARCHY:
#   SECTION 1  — Imports & Constants
#   SECTION 2  — Helper Functions
#   SECTION 3  — Blog Posts (CRUD)
#   SECTION 4  — Live Products (CRUD)
#   SECTION 5  — Product Images Management
#   SECTION 6  — Bulk Operations
#   SECTION 7  — Diff Preview
#   SECTION 8  — Standalone Test
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

REQUEST_TIMEOUT = 25
USER_AGENT = "KhanHerbalFactory/3.0 (+wp_client)"

# Endpoints
WP_POSTS_ENDPOINT       = "/wp-json/wp/v2/posts"
WC_PRODUCTS_ENDPOINT    = "/wp-json/wc/v3/products"
WC_BATCH_ENDPOINT       = "/wp-json/wc/v3/products/batch"

# Caching
_CACHE: Dict[str, Any] = {}
_CACHE_TTL = 120  # 2 minutes


# =============================================================================
# SECTION 2 — HELPER FUNCTIONS
# =============================================================================
def _redact(text):
    if not isinstance(text, str):
        text = str(text)
    for p in [r"ck_[A-Za-z0-9]{20,}", r"cs_[A-Za-z0-9]{20,}",
              r"(?i)(authorization|bearer|password|secret)\s*[:=]\s*\S+"]:
        text = re.sub(p, "***REDACTED***", text)
    return text


def _request(method, url, auth, json_body=None, params=None):
    """Safe HTTP wrapper. auth = (user, pass) or (ck, cs)."""
    try:
        r = requests.request(
            method=method.upper(), url=url, auth=auth,
            json=json_body, params=params,
            headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
            timeout=REQUEST_TIMEOUT,
        )
    except requests.exceptions.SSLError as e:
        return False, None, f"SSL: {_redact(str(e))[:100]}"
    except requests.exceptions.ConnectTimeout:
        return False, None, "Connection timed out"
    except requests.exceptions.ReadTimeout:
        return False, None, "Server slow to respond"
    except requests.exceptions.ConnectionError as e:
        return False, None, f"Cannot connect: {_redact(str(e))[:100]}"
    except requests.exceptions.RequestException as e:
        return False, None, f"Request failed: {_redact(str(e))[:100]}"

    if r.status_code in (200, 201, 204):
        try:
            return True, (r.json() if r.text else None), ""
        except ValueError:
            return True, None, ""

    if r.status_code == 401:
        return False, None, "401 Unauthorized"
    if r.status_code == 403:
        return False, None, "403 Forbidden — insufficient permissions"
    if r.status_code == 404:
        return False, None, "404 Not Found"

    try:
        msg = r.json().get("message", r.text[:150])
    except Exception:
        msg = r.text[:150]
    return False, None, f"HTTP {r.status_code}: {_redact(msg)}"


def _cache_get(key):
    if key in _CACHE:
        val, ts = _CACHE[key]
        if time.time() - ts < _CACHE_TTL:
            return val
    return None


def _cache_set(key, value):
    _CACHE[key] = (value, time.time())


def clear_cache():
    _CACHE.clear()


def _strip_html(html):
    return re.sub(r"<[^>]+>", " ", html or "")


def _count_words(text):
    return len(re.findall(r"\b\w+\b", text or ""))


# =============================================================================
# SECTION 3 — BLOG POSTS (CRUD)
# =============================================================================

# -----------------------------------------------------------------------------
# 3.1 — List Posts
# -----------------------------------------------------------------------------
def list_posts(site_url, username, app_password,
                page=1, per_page=20,
                search="", status="any",
                use_cache=False) -> Tuple[bool, List[Dict], str]:
    """
    List WordPress blog posts.
    status: any | publish | draft | pending | private
    Returns list of normalized post dicts.
    """
    url = f"{site_url.rstrip('/')}{WP_POSTS_ENDPOINT}"
    params = {"page": page, "per_page": per_page,
              "status": status, "orderby": "date", "order": "desc"}
    if search:
        params["search"] = search

    ok, data, err = _request("GET", url, (username, app_password),
                              params=params)
    if not ok:
        return False, [], err
    if not isinstance(data, list):
        return False, [], "Unexpected response"

    posts = [_normalize_post(p) for p in data]
    return True, posts, ""


def _normalize_post(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize WP post response."""
    return {
        "id":            raw.get("id"),
        "title":         raw.get("title", {}).get("rendered", "") if isinstance(raw.get("title"), dict) else raw.get("title", ""),
        "slug":          raw.get("slug", ""),
        "status":        raw.get("status", "draft"),
        "content":       raw.get("content", {}).get("rendered", "") if isinstance(raw.get("content"), dict) else raw.get("content", ""),
        "excerpt":       raw.get("excerpt", {}).get("rendered", "") if isinstance(raw.get("excerpt"), dict) else raw.get("excerpt", ""),
        "date":          raw.get("date", ""),
        "modified":      raw.get("modified", ""),
        "link":          raw.get("link", ""),
        "author":        raw.get("author", 0),
        "categories":    raw.get("categories", []),
        "tags":          raw.get("tags", []),
        "featured_media": raw.get("featured_media", 0),
    }


# -----------------------------------------------------------------------------
# 3.2 — Get Single Post
# -----------------------------------------------------------------------------
def get_post(site_url, username, app_password, post_id) -> Tuple[bool, Optional[Dict], str]:
    url = f"{site_url.rstrip('/')}{WP_POSTS_ENDPOINT}/{post_id}"
    ok, data, err = _request("GET", url, (username, app_password))
    if not ok:
        return False, None, err
    return True, _normalize_post(data), ""


# -----------------------------------------------------------------------------
# 3.3 — Create Post
# -----------------------------------------------------------------------------
def create_post(site_url, username, app_password,
                 title, content,
                 status="draft", slug=None,
                 excerpt="", categories=None, tags=None,
                 featured_media=None, meta=None) -> Tuple[bool, Optional[Dict], str]:
    """
    Create a new WordPress post.
    categories/tags: list of IDs
    meta: dict of meta_key -> value (RankMath etc.)
    """
    if not title or not title.strip():
        return False, None, "Title required"
    if not content or not content.strip():
        return False, None, "Content required"

    url = f"{site_url.rstrip('/')}{WP_POSTS_ENDPOINT}"
    payload = {
        "title":   title.strip(),
        "content": content,
        "status":  status,
        "excerpt": excerpt or "",
    }
    if slug:
        payload["slug"] = slug
    if categories:
        payload["categories"] = categories
    if tags:
        payload["tags"] = tags
    if featured_media:
        payload["featured_media"] = featured_media
    if meta:
        payload["meta"] = meta

    ok, data, err = _request("POST", url, (username, app_password),
                              json_body=payload)
    if not ok:
        return False, None, err
    clear_cache()
    return True, _normalize_post(data), ""


# -----------------------------------------------------------------------------
# 3.4 — Update Post
# -----------------------------------------------------------------------------
def update_post(site_url, username, app_password, post_id,
                 **fields) -> Tuple[bool, Optional[Dict], str]:
    """
    Update an existing WordPress post.
    Accepts: title, content, status, slug, excerpt, categories, tags, meta
    """
    if not post_id:
        return False, None, "Post ID required"

    url = f"{site_url.rstrip('/')}{WP_POSTS_ENDPOINT}/{post_id}"
    allowed = {"title", "content", "status", "slug", "excerpt",
               "categories", "tags", "featured_media", "meta"}
    payload = {k: v for k, v in fields.items() if k in allowed and v is not None}

    if not payload:
        return False, None, "No fields to update"

    ok, data, err = _request("POST", url, (username, app_password),
                              json_body=payload)
    if not ok:
        return False, None, err
    clear_cache()
    return True, _normalize_post(data), ""


# -----------------------------------------------------------------------------
# 3.5 — Delete Post
# -----------------------------------------------------------------------------
def delete_post(site_url, username, app_password,
                 post_id, force=True) -> Tuple[bool, str]:
    """
    Delete WordPress post.
    force=True → permanent, force=False → trash
    """
    if not post_id:
        return False, "Post ID required"

    url = f"{site_url.rstrip('/')}{WP_POSTS_ENDPOINT}/{post_id}"
    ok, _, err = _request("DELETE", url, (username, app_password),
                           params={"force": str(force).lower()})
    if not ok:
        return False, err
    clear_cache()
    return True, ""


# -----------------------------------------------------------------------------
# 3.6 — Get Post Meta
# -----------------------------------------------------------------------------
def get_post_meta(site_url, username, app_password, post_id) -> Tuple[bool, Dict, str]:
    """
    Fetch post meta (RankMath fields).
    Requires post to be fetched with context=edit — may need auth plugin.
    """
    url = f"{site_url.rstrip('/')}{WP_POSTS_ENDPOINT}/{post_id}"
    params = {"context": "edit"}
    ok, data, err = _request("GET", url, (username, app_password), params=params)
    if not ok:
        return False, {}, err
    meta = data.get("meta", {}) if isinstance(data, dict) else {}
    return True, meta, ""


# =============================================================================
# SECTION 4 — LIVE PRODUCTS (CRUD)
# =============================================================================

# -----------------------------------------------------------------------------
# 4.1 — List Products
# -----------------------------------------------------------------------------
def list_products(site_url, ck, cs,
                   page=1, per_page=20,
                   search="", status="any",
                   category=None, tag=None,
                   use_cache=False) -> Tuple[bool, List[Dict], str]:
    """
    List WooCommerce products.
    status: any | publish | draft | pending | private
    """
    url = f"{site_url.rstrip('/')}{WC_PRODUCTS_ENDPOINT}"
    params = {"page": page, "per_page": per_page,
              "status": status, "orderby": "date", "order": "desc"}
    if search:
        params["search"] = search
    if category:
        params["category"] = category
    if tag:
        params["tag"] = tag

    ok, data, err = _request("GET", url, (ck, cs), params=params)
    if not ok:
        return False, [], err
    if not isinstance(data, list):
        return False, [], "Unexpected response"

    products = [_normalize_product(p) for p in data]
    return True, products, ""


def _normalize_product(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize WC product response to a manageable dict."""
    images = []
    for img in raw.get("images", []) or []:
        images.append({
            "id": img.get("id"),
            "src": img.get("src", ""),
            "alt": img.get("alt", ""),
            "position": img.get("position", 0),
        })

    categories = [c.get("name", "") for c in raw.get("categories", []) or []]
    tags = [t.get("name", "") for t in raw.get("tags", []) or []]

    return {
        "id":            raw.get("id"),
        "name":          raw.get("name", ""),
        "slug":          raw.get("slug", ""),
        "sku":           raw.get("sku", ""),
        "type":          raw.get("type", "simple"),
        "status":        raw.get("status", "draft"),
        "price":         raw.get("price", "0"),
        "regular_price": raw.get("regular_price", ""),
        "sale_price":    raw.get("sale_price", ""),
        "stock":         raw.get("stock_quantity", 0),
        "stock_status":  raw.get("stock_status", "instock"),
        "manage_stock":  raw.get("manage_stock", False),
        "description":   raw.get("description", ""),
        "short_description": raw.get("short_description", ""),
        "categories":    categories,
        "tags":          tags,
        "images":        images,
        "featured_image_id": images[0]["id"] if images else None,
        "featured_image_url": images[0]["src"] if images else "",
        "permalink":     raw.get("permalink", ""),
        "date_created":  raw.get("date_created", ""),
        "meta_data":     raw.get("meta_data", []),
    }


# -----------------------------------------------------------------------------
# 4.2 — Get Single Product
# -----------------------------------------------------------------------------
def get_product(site_url, ck, cs, product_id) -> Tuple[bool, Optional[Dict], str]:
    url = f"{site_url.rstrip('/')}{WC_PRODUCTS_ENDPOINT}/{product_id}"
    ok, data, err = _request("GET", url, (ck, cs))
    if not ok:
        return False, None, err
    return True, _normalize_product(data), ""


def get_product_by_sku(site_url, ck, cs, sku) -> Tuple[bool, Optional[Dict], str]:
    ok, items, err = list_products(site_url, ck, cs, search=sku, per_page=5)
    if not ok:
        return False, None, err
    for p in items:
        if p.get("sku") == sku:
            return True, p, ""
    return False, None, f"No product with SKU '{sku}'"


# -----------------------------------------------------------------------------
# 4.3 — Update Product
# -----------------------------------------------------------------------------
def update_product(site_url, ck, cs, product_id,
                    **fields) -> Tuple[bool, Optional[Dict], str]:
    """
    Update an existing WooCommerce product.
    Accepts: name, slug, description, short_description, regular_price,
             sale_price, stock_quantity, stock_status, manage_stock,
             categories, tags, images, status, meta_data
    """
    if not product_id:
        return False, None, "Product ID required"

    url = f"{site_url.rstrip('/')}{WC_PRODUCTS_ENDPOINT}/{product_id}"
    allowed = {
        "name", "slug", "description", "short_description",
        "regular_price", "sale_price", "price",
        "stock_quantity", "stock_status", "manage_stock",
        "categories", "tags", "images", "status",
        "meta_data", "attributes",
    }
    payload = {k: v for k, v in fields.items() if k in allowed and v is not None}

    if not payload:
        return False, None, "No fields to update"

    ok, data, err = _request("PUT", url, (ck, cs), json_body=payload)
    if not ok:
        return False, None, err
    clear_cache()
    return True, _normalize_product(data), ""


# -----------------------------------------------------------------------------
# 4.4 — Delete Product
# -----------------------------------------------------------------------------
def delete_product(site_url, ck, cs, product_id, force=True) -> Tuple[bool, str]:
    """
    Delete WooCommerce product.
    force=True → permanent, force=False → trash
    """
    if not product_id:
        return False, "Product ID required"

    url = f"{site_url.rstrip('/')}{WC_PRODUCTS_ENDPOINT}/{product_id}"
    ok, _, err = _request("DELETE", url, (ck, cs),
                           params={"force": str(force).lower()})
    if not ok:
        return False, err
    clear_cache()
    return True, ""


# =============================================================================
# SECTION 5 — PRODUCT IMAGES MANAGEMENT
# =============================================================================
def update_product_images(site_url, ck, cs, product_id,
                           featured_media_id=None,
                           gallery_media_ids=None) -> Tuple[bool, Optional[Dict], str]:
    """
    Update product images.
    featured_media_id: WP media ID for featured image
    gallery_media_ids: list of WP media IDs for gallery
    If you only want to keep gallery, pass featured_media_id=None.
    """
    images = []
    if featured_media_id:
        images.append({"id": featured_media_id, "position": 0})
    if gallery_media_ids:
        for i, mid in enumerate(gallery_media_ids, start=1):
            images.append({"id": mid, "position": i})

    if not images:
        return False, None, "At least one image ID required"

    return update_product(site_url, ck, cs, product_id, images=images)


def append_gallery_images(site_url, ck, cs, product_id,
                            new_media_ids) -> Tuple[bool, Optional[Dict], str]:
    """Append new images to existing gallery (keep featured)."""
    ok, product, err = get_product(site_url, ck, cs, product_id)
    if not ok:
        return False, None, err

    existing = product.get("images", [])
    new_images = list(existing)
    start_pos = len(existing)

    for i, mid in enumerate(new_media_ids):
        new_images.append({"id": mid, "position": start_pos + i})

    return update_product(site_url, ck, cs, product_id, images=new_images)


# =============================================================================
# SECTION 6 — BULK OPERATIONS
# =============================================================================
def batch_update_products(site_url, ck, cs, updates) -> Tuple[bool, Dict, str]:
    """
    Batch update products.
    updates: list of {id, ...fields}
    Returns {updated, failed, errors}
    """
    if not updates:
        return False, {}, "No updates"
    if len(updates) > 100:
        return False, {}, "Max 100 updates per batch"

    url = f"{site_url.rstrip('/')}{WC_BATCH_ENDPOINT}"
    payload = {"update": updates}

    ok, data, err = _request("POST", url, (ck, cs), json_body=payload)
    if not ok:
        return False, {}, err

    updated = len(data.get("update", []) or [])
    failed = 0
    errors = []
    for u in updates:
        if not any(x.get("id") == u.get("id") for x in data.get("update", []) or []):
            failed += 1
            errors.append(f"ID {u.get('id')}")

    clear_cache()
    return True, {"updated": updated, "failed": failed, "errors": errors}, ""


def bulk_delete_products(site_url, ck, cs, product_ids,
                          force=True) -> Dict[str, Any]:
    """Delete multiple products."""
    deleted = failed = 0
    errors = []
    for pid in product_ids:
        ok, err = delete_product(site_url, ck, cs, pid, force=force)
        if ok:
            deleted += 1
        else:
            failed += 1
            errors.append(f"ID {pid}: {err}")
    return {"deleted": deleted, "failed": failed, "errors": errors[:10]}


def bulk_update_prices(site_url, ck, cs, updates) -> Tuple[bool, Dict, str]:
    """
    Bulk update prices.
    updates: list of {id, regular_price}
    """
    return batch_update_products(site_url, ck, cs, updates)


def bulk_update_stock(site_url, ck, cs, updates) -> Tuple[bool, Dict, str]:
    """
    Bulk update stock.
    updates: list of {id, stock_quantity}
    """
    return batch_update_products(site_url, ck, cs, updates)


# =============================================================================
# SECTION 7 — DIFF PREVIEW
# =============================================================================
def compute_diff(old_data: Dict[str, Any],
                  new_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Compute field-level diff between old and new.
    Returns list of {field, old, new, changed}
    """
    diffs = []
    all_keys = set(old_data.keys()) | set(new_data.keys())

    for k in sorted(all_keys):
        old_v = old_data.get(k)
        new_v = new_data.get(k)

        # Normalize for comparison
        if isinstance(old_v, (dict, list)):
            old_v = json.dumps(old_v, sort_keys=True, default=str)
        if isinstance(new_v, (dict, list)):
            new_v = json.dumps(new_v, sort_keys=True, default=str)

        old_s = str(old_v or "")
        new_s = str(new_v or "")

        changed = (old_s != new_s)
        diffs.append({
            "field":   k,
            "old":     old_s[:120],
            "new":     new_s[:120],
            "changed": changed,
        })

    return diffs


def summarize_diff(diffs: List[Dict]) -> Dict[str, Any]:
    """Summarize diff report."""
    changed = [d for d in diffs if d["changed"]]
    return {
        "total_fields": len(diffs),
        "changed_fields": len(changed),
        "changed_list": changed,
    }


# =============================================================================
# SECTION 8 — STANDALONE TEST
# =============================================================================
if __name__ == "__main__":
    print("wp_client.py v1.0 loaded")
    print()
    print("Functions available:")
    print("  Posts:")
    print("    list_posts, get_post, create_post, update_post, delete_post")
    print("  Products:")
    print("    list_products, get_product, get_product_by_sku,")
    print("    update_product, delete_product")
    print("  Images:")
    print("    update_product_images, append_gallery_images")
    print("  Bulk:")
    print("    batch_update_products, bulk_delete_products,")
    print("    bulk_update_prices, bulk_update_stock")
    print("  Diff:")
    print("    compute_diff, summarize_diff")
    print()

    # Test diff
    old_p = {
        "name": "Almond Oil",
        "price": "450.00",
        "stock": 25,
        "status": "draft",
    }
    new_p = {
        "name": "Almond Oil Premium",
        "price": "550.00",
        "stock": 25,
        "status": "publish",
    }
    diffs = compute_diff(old_p, new_p)
    summary = summarize_diff(diffs)

    print("=== Diff Test ===")
    print(f"  Total fields: {summary['total_fields']}")
    print(f"  Changed:      {summary['changed_fields']}")
    for d in summary["changed_list"]:
        print(f"  • {d['field']}: '{d['old']}' → '{d['new']}'")

    print("\n✅ All tests complete")