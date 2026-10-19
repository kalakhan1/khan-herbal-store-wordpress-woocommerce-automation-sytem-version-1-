# =============================================================================
# KHAN HERBAL STORES — WORDPRESS CLIENT v1.1
# =============================================================================
# File: wp_client.py
# v1.1 CHANGES:
#   - Optional import of taxonomy module
#   - NEW: get_editor_data() — item + options in one call
#   - NEW: get_category_options() — quick categories list
#   - NEW: get_tag_options() — quick tags list
#   - All existing functions unchanged
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

# Optional taxonomy module
try:
    import taxonomy
    TAXONOMY_AVAILABLE = True
except ImportError:
    TAXONOMY_AVAILABLE = False

REQUEST_TIMEOUT = 25
USER_AGENT = "KhanHerbalFactory/3.0 (+wp_client)"

WP_POSTS_ENDPOINT       = "/wp-json/wp/v2/posts"
WC_PRODUCTS_ENDPOINT    = "/wp-json/wc/v3/products"
WC_BATCH_ENDPOINT       = "/wp-json/wc/v3/products/batch"

_CACHE: Dict[str, Any] = {}
_CACHE_TTL = 120


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

def extract_focus_keyword(item_type, item, site_url=None,
                            username=None, app_password=None, item_id=None):
    """
    Extract rank_math_focus_keyword from product meta_data or post meta.
    Products: reads from item['meta_data'] array
    Posts: requires separate meta fetch (get_post_meta)
    """
    if item_type == "product":
        meta = item.get("meta_data", []) or []
        for m in meta:
            if isinstance(m, dict) and m.get("key") == "rank_math_focus_keyword":
                return m.get("value", "") or ""
        return ""
    elif item_type == "post":
        if site_url and item_id:
            ok, meta, _ = get_post_meta(site_url, username, app_password, item_id)
            if ok:
                return meta.get("rank_math_focus_keyword", "") or ""
        return ""
    return ""



# =============================================================================
# SECTION 3 — BLOG POSTS
# =============================================================================
def list_posts(site_url, username, app_password, page=1, per_page=20,
                search="", status="any", use_cache=False):
    url = f"{site_url.rstrip('/')}{WP_POSTS_ENDPOINT}"
    params = {"page": page, "per_page": per_page,
              "status": status, "orderby": "date", "order": "desc"}
    if search:
        params["search"] = search
    ok, data, err = _request("GET", url, (username, app_password), params=params)
    if not ok:
        return False, [], err
    if not isinstance(data, list):
        return False, [], "Unexpected response"
    posts = [_normalize_post(p) for p in data]
    return True, posts, ""


def _normalize_post(raw):
    def _pick(obj, key):
        if not isinstance(obj, dict):
            return str(obj or "")
        return obj.get(key) or obj.get("rendered", "") or obj.get("raw", "")
    return {
        "id": raw.get("id"),
        "title": _pick(raw.get("title"), "raw"),
        "slug": raw.get("slug", ""),
        "status": raw.get("status", "draft"),
        "content": _pick(raw.get("content"), "raw"),
        "excerpt": _pick(raw.get("excerpt"), "raw"),
        "date": raw.get("date", ""),
        "modified": raw.get("modified", ""),
        "link": raw.get("link", ""),
        "author": raw.get("author", 0),
        "categories": raw.get("categories", []),
        "tags": raw.get("tags", []),
        "featured_media": raw.get("featured_media", 0),
    }


def get_post(site_url, username, app_password, post_id):
    url = f"{site_url.rstrip('/')}{WP_POSTS_ENDPOINT}/{post_id}"
    params = {"context": "edit"}
    ok, data, err = _request("GET", url, (username, app_password), params=params)
    if not ok:
        return False, None, err
    return True, _normalize_post(data), ""


def create_post(site_url, username, app_password, title, content,
                 status="draft", slug=None, excerpt="", categories=None,
                 tags=None, featured_media=None, meta=None):
    if not title or not title.strip():
        return False, None, "Title required"
    if not content or not content.strip():
        return False, None, "Content required"
    url = f"{site_url.rstrip('/')}{WP_POSTS_ENDPOINT}"
    payload = {"title": title.strip(), "content": content,
                "status": status, "excerpt": excerpt or ""}
    if slug: payload["slug"] = slug
    if categories: payload["categories"] = categories
    if tags: payload["tags"] = tags
    if featured_media: payload["featured_media"] = featured_media
    if meta: payload["meta"] = meta
    ok, data, err = _request("POST", url, (username, app_password), json_body=payload)
    if not ok:
        return False, None, err
    clear_cache()
    return True, _normalize_post(data), ""


def update_post(site_url, username, app_password, post_id, **fields):
    if not post_id:
        return False, None, "Post ID required"
    url = f"{site_url.rstrip('/')}{WP_POSTS_ENDPOINT}/{post_id}"
    allowed = {"title", "content", "status", "slug", "excerpt",
               "categories", "tags", "featured_media", "meta"}
    payload = {k: v for k, v in fields.items() if k in allowed and v is not None}
    if not payload:
        return False, None, "No fields to update"
    ok, data, err = _request("POST", url, (username, app_password), json_body=payload)
    if not ok:
        return False, None, err
    clear_cache()
    return True, _normalize_post(data), ""


def delete_post(site_url, username, app_password, post_id, force=True):
    if not post_id:
        return False, "Post ID required"
    url = f"{site_url.rstrip('/')}{WP_POSTS_ENDPOINT}/{post_id}"
    ok, _, err = _request("DELETE", url, (username, app_password),
                           params={"force": str(force).lower()})
    if not ok:
        return False, err
    clear_cache()
    return True, ""


def get_post_meta(site_url, username, app_password, post_id):
    url = f"{site_url.rstrip('/')}{WP_POSTS_ENDPOINT}/{post_id}"
    params = {"context": "edit"}
    ok, data, err = _request("GET", url, (username, app_password), params=params)
    if not ok:
        return False, {}, err
    meta = data.get("meta", {}) if isinstance(data, dict) else {}
    return True, meta, ""


# =============================================================================
# SECTION 4 — LIVE PRODUCTS
# =============================================================================
def list_products(site_url, ck, cs, page=1, per_page=20, search="",
                   status="any", category=None, tag=None, use_cache=False):
    url = f"{site_url.rstrip('/')}{WC_PRODUCTS_ENDPOINT}"
    params = {"page": page, "per_page": per_page,
              "status": status, "orderby": "date", "order": "desc"}
    if search: params["search"] = search
    if category: params["category"] = category
    if tag: params["tag"] = tag
    ok, data, err = _request("GET", url, (ck, cs), params=params)
    if not ok:
        return False, [], err
    if not isinstance(data, list):
        return False, [], "Unexpected response"
    products = [_normalize_product(p) for p in data]
    return True, products, ""


def _normalize_product(raw):
    images = []
    for img in raw.get("images", []) or []:
        images.append({
            "id": img.get("id"), "src": img.get("src", ""),
            "alt": img.get("alt", ""), "position": img.get("position", 0),
        })
    categories = [{"id": c.get("id"), "name": c.get("name", ""), "slug": c.get("slug", "")}
                   for c in (raw.get("categories", []) or [])]
    tags = [{"id": t.get("id"), "name": t.get("name", ""), "slug": t.get("slug", "")}
            for t in (raw.get("tags", []) or [])]
    attributes = []
    for attr in raw.get("attributes", []) or []:
        attributes.append({
            "id": attr.get("id"),
            "name": attr.get("name", ""),
            "position": attr.get("position", 0),
            "visible": attr.get("visible", True),
            "variation": attr.get("variation", False),
            "options": attr.get("options", []),
        })
    return {
        "id": raw.get("id"),
        "name": raw.get("name", ""),
        "slug": raw.get("slug", ""),
        "sku": raw.get("sku", ""),
        "type": raw.get("type", "simple"),
        "status": raw.get("status", "draft"),
        "price": raw.get("price", "0"),
        "regular_price": raw.get("regular_price", ""),
        "sale_price": raw.get("sale_price", ""),
        "stock": raw.get("stock_quantity", 0),
        "stock_status": raw.get("stock_status", "instock"),
        "manage_stock": raw.get("manage_stock", False),
        "description": raw.get("description", ""),
        "short_description": raw.get("short_description", ""),
        "categories": categories,
        "category_names": [c["name"] for c in categories],
        "category_ids": [c["id"] for c in categories],
        "tags": tags,
        "tag_names": [t["name"] for t in tags],
        "tag_ids": [t["id"] for t in tags],
        "attributes": attributes,
        "images": images,
        "featured_image_id": images[0]["id"] if images else None,
        "featured_image_url": images[0]["src"] if images else "",
        "gallery_image_ids": [img["id"] for img in images[1:]] if len(images) > 1 else [],
        "permalink": raw.get("permalink", ""),
        "date_created": raw.get("date_created", ""),
        "meta_data": raw.get("meta_data", []),
    }


def get_product(site_url, ck, cs, product_id):
    url = f"{site_url.rstrip('/')}{WC_PRODUCTS_ENDPOINT}/{product_id}"
    ok, data, err = _request("GET", url, (ck, cs))
    if not ok:
        return False, None, err
    return True, _normalize_product(data), ""


def get_product_by_sku(site_url, ck, cs, sku):
    ok, items, err = list_products(site_url, ck, cs, search=sku, per_page=5)
    if not ok:
        return False, None, err
    for p in items:
        if p.get("sku") == sku:
            return True, p, ""
    return False, None, f"No product with SKU '{sku}'"


def update_product(site_url, ck, cs, product_id, **fields):
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


def delete_product(site_url, ck, cs, product_id, force=True):
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
# SECTION 4.5 — EDITOR DATA HELPERS (NEW in v1.1)
# =============================================================================
def get_editor_data(site_url_wp, wp_user, wp_pass,
                     site_url_wc, ck, cs,
                     item_type="product", item_id=None,
                     include_options=True):
    """
    Fetch item + all taxonomy options in one call for editor.
    Returns dict: {item, focus_keyword, options, errors}
    """
    result = {
        "item": None,
        "focus_keyword": "",
        "options": {"categories": [], "tags": [], "attributes": [], "brands": []},
        "errors": [],
    }

    if not item_id:
        return False, result, "item_id required"

    if item_type == "product":
        ok, product, err = get_product(site_url_wc, ck, cs, item_id)
        if not ok:
            return False, result, err
        result["item"] = product
        result["focus_keyword"] = extract_focus_keyword("product", product)
    elif item_type == "post":
        ok, post, err = get_post(site_url_wp, wp_user, wp_pass, item_id)
        if not ok:
            return False, result, err
        result["item"] = post
        result["focus_keyword"] = extract_focus_keyword(
            "post", post, site_url_wp, wp_user, wp_pass, item_id)
    else:
        return False, result, f"Unknown item_type: {item_type}"

    if include_options and TAXONOMY_AVAILABLE:
        try:
            options = taxonomy.get_all_options_for_autocomplete(
                site_url_wc, ck, cs,
                include_wp_categories=(item_type == "post"),
                include_attributes=(item_type == "product"),
            )
            if item_type == "product":
                result["options"]["categories"] = options.get("categories", [])
                result["options"]["tags"] = options.get("tags", [])
                result["options"]["attributes"] = options.get("attributes", [])
                result["options"]["brands"] = options.get("brands", [])
            else:
                result["options"]["categories"] = options.get("wp_categories", [])
                result["options"]["tags"] = options.get("wp_tags", [])
            result["errors"] = options.get("errors", [])
        except Exception as e:
            result["errors"].append(f"Taxonomy fetch failed: {str(e)[:100]}")
    elif include_options and not TAXONOMY_AVAILABLE:
        result["errors"].append("taxonomy.py not available")

    return True, result, ""


def get_category_options(site_url, ck, cs, for_post=False):
    """Quick categories list for select dropdowns."""
    if not TAXONOMY_AVAILABLE:
        return []
    if for_post:
        ok, cats, _ = taxonomy.list_wp_categories(site_url, ck, cs)
    else:
        ok, cats, _ = taxonomy.list_wc_categories(site_url, ck, cs)
    if ok and cats:
        return [{"id": c.get("id"), "name": c.get("name"), "slug": c.get("slug")}
                for c in cats]
    return []


def get_tag_options(site_url, ck, cs, for_post=False):
    """Quick tags list for select dropdowns."""
    if not TAXONOMY_AVAILABLE:
        return []
    if for_post:
        ok, tags, _ = taxonomy.list_wp_tags(site_url, ck, cs)
    else:
        ok, tags, _ = taxonomy.list_wc_tags(site_url, ck, cs)
    if ok and tags:
        return [{"id": t.get("id"), "name": t.get("name"), "slug": t.get("slug")}
                for t in tags]
    return []


def get_attribute_options(site_url, ck, cs):
    """Quick attributes with terms list for editor."""
    if not TAXONOMY_AVAILABLE:
        return []
    ok, attrs, _ = taxonomy.list_wc_attributes(site_url, ck, cs)
    if not ok:
        return []
    result = []
    for a in attrs:
        attr_data = {"id": a.get("id"), "name": a.get("name"),
                     "slug": a.get("slug"), "type": a.get("type", "select"),
                     "terms": []}
        ok_t, terms, _ = taxonomy.list_attribute_terms(site_url, ck, cs, a.get("id"))
        if ok_t:
            attr_data["terms"] = [{"id": t.get("id"), "name": t.get("name"), "slug": t.get("slug")}
                                   for t in terms]
        result.append(attr_data)
    return result


def get_brand_options(site_url, ck, cs):
    """Quick brands list for editor."""
    if not TAXONOMY_AVAILABLE:
        return []
    ok, brands, _ = taxonomy.list_brands(site_url, ck, cs)
    if ok:
        return [{"id": b.get("id"), "name": b.get("name"), "slug": b.get("slug")}
                for b in brands]
    return []


# =============================================================================
# SECTION 5 — PRODUCT IMAGES MANAGEMENT
# =============================================================================
def update_product_images(site_url, ck, cs, product_id,
                           featured_media_id=None, gallery_media_ids=None):
    images = []
    if featured_media_id:
        images.append({"id": featured_media_id, "position": 0})
    if gallery_media_ids:
        for i, mid in enumerate(gallery_media_ids, start=1):
            images.append({"id": mid, "position": i})
    if not images:
        return False, None, "At least one image ID required"
    return update_product(site_url, ck, cs, product_id, images=images)


def append_gallery_images(site_url, ck, cs, product_id, new_media_ids):
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
def batch_update_products(site_url, ck, cs, updates):
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
    updated_ids = {u.get("id") for u in data.get("update", []) or []}
    for u in updates:
        if u.get("id") not in updated_ids:
            failed += 1
            errors.append(f"ID {u.get('id')}")
    clear_cache()
    return True, {"updated": updated, "failed": failed, "errors": errors}, ""


def bulk_delete_products(site_url, ck, cs, product_ids, force=True):
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


def bulk_update_prices(site_url, ck, cs, updates):
    return batch_update_products(site_url, ck, cs, updates)


def bulk_update_stock(site_url, ck, cs, updates):
    return batch_update_products(site_url, ck, cs, updates)


# =============================================================================
# SECTION 7 — DIFF PREVIEW
# =============================================================================
def compute_diff(old_data, new_data):
    diffs = []
    all_keys = set(old_data.keys()) | set(new_data.keys())
    for k in sorted(all_keys):
        old_v = old_data.get(k)
        new_v = new_data.get(k)
        if isinstance(old_v, (dict, list)):
            old_v = json.dumps(old_v, sort_keys=True, default=str)
        if isinstance(new_v, (dict, list)):
            new_v = json.dumps(new_v, sort_keys=True, default=str)
        old_s = str(old_v or "")
        new_s = str(new_v or "")
        diffs.append({
            "field": k, "old": old_s[:120], "new": new_s[:120],
            "changed": old_s != new_s,
        })
    return diffs


def summarize_diff(diffs):
    changed = [d for d in diffs if d["changed"]]
    return {"total_fields": len(diffs), "changed_fields": len(changed),
            "changed_list": changed}


# =============================================================================
# SECTION 8 — STANDALONE TEST
# =============================================================================
if __name__ == "__main__":
    print("wp_client.py v1.1 loaded")
    print()
    print("Functions available:")
    print("  Posts: list/get/create/update/delete")
    print("  Products: list/get/update/delete + get_by_sku")
    print("  Images: update_product_images, append_gallery_images")
    print("  Bulk: batch_update, bulk_delete, bulk_update_prices/stock")
    print("  Diff: compute_diff, summarize_diff")
    print("  NEW: get_editor_data, get_category_options, get_tag_options")
    print("  NEW: get_attribute_options, get_brand_options")
    print()

    old_p = {"name": "Almond Oil", "price": "450.00", "stock": 25, "status": "draft"}
    new_p = {"name": "Almond Oil Premium", "price": "550.00", "stock": 25, "status": "publish"}
    diffs = compute_diff(old_p, new_p)
    summary = summarize_diff(diffs)
    print("=== Diff Test ===")
    print(f"  Total: {summary['total_fields']}  Changed: {summary['changed_fields']}")
    for d in summary["changed_list"]:
        print(f"  • {d['field']}: '{d['old']}' → '{d['new']}'")

    print(f"\nTaxonomy module available: {TAXONOMY_AVAILABLE}")
    print("\n✅ All tests complete")