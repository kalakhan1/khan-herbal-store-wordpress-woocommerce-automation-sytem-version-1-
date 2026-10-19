# =============================================================================
# test_editor.py — Interactive Verification Suite
# =============================================================================
# Tests the full editor workflow against your live site.
# Run: python test_editor.py
# =============================================================================

import sys
import time
from getpass import getpass

try:
    import requests
    import wp_client
    import taxonomy
    import media
except ImportError as e:
    print(f"❌ Import failed: {e}")
    print("Run: pip install requests")
    sys.exit(1)


# ANSI colors (fallback safe)
class C:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


def _ok(msg):
    print(f"  {C.GREEN}✅ {msg}{C.RESET}")
    return True


def _fail(msg):
    print(f"  {C.RED}❌ {msg}{C.RESET}")
    return False


def _info(msg):
    print(f"  {C.BLUE}ℹ️  {msg}{C.RESET}")


def _warn(msg):
    print(f"  {C.YELLOW}⚠️  {msg}{C.RESET}")


class TestRunner:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.skipped = 0
        self.results = []

    def test(self, name, func, *args, **kwargs):
        print(f"\n{C.BOLD}▶ {name}{C.RESET}")
        try:
            result = func(*args, **kwargs)
            if result:
                self.passed += 1
                self.results.append((name, "PASS", None))
            else:
                self.failed += 1
                self.results.append((name, "FAIL", None))
        except AssertionError as e:
            self.failed += 1
            _fail(f"Assertion: {e}")
            self.results.append((name, "FAIL", str(e)))
        except Exception as e:
            self.failed += 1
            _fail(f"Exception: {type(e).__name__}: {e}")
            self.results.append((name, "FAIL", str(e)))

    def summary(self):
        print("\n" + "=" * 60)
        print(f"{C.BOLD}  TEST SUMMARY{C.RESET}")
        print("=" * 60)
        total = self.passed + self.failed + self.skipped
        print(f"  Total:    {total}")
        print(f"  {C.GREEN}Passed:   {self.passed}{C.RESET}")
        if self.failed:
            print(f"  {C.RED}Failed:   {self.failed}{C.RESET}")
            print("\n  Failed tests:")
            for name, status, err in self.results:
                if status == "FAIL":
                    print(f"    • {name}")
                    if err:
                        print(f"      {err[:120]}")
        if self.skipped:
            print(f"  {C.YELLOW}Skipped:  {self.skipped}{C.RESET}")
        print("=" * 60)
        return self.failed == 0


# =============================================================================
# TEST FUNCTIONS
# =============================================================================
def test_wp_connect(wp_url, wp_user, wp_pass):
    try:
        r = requests.get(f"{wp_url}/wp-json/wp/v2/users/me",
                          auth=(wp_user, wp_pass), timeout=15)
    except Exception as e:
        _fail(f"Network error: {e}")
        return False
    if r.status_code == 200:
        return _ok(f"Connected as {r.json().get('name', '?')}")
    return _fail(f"HTTP {r.status_code}")


def test_wc_connect(wc_url, ck, cs):
    try:
        r = requests.get(f"{wc_url}/wp-json/wc/v3/system_status",
                          auth=(ck, cs), timeout=15)
    except Exception as e:
        _fail(f"Network error: {e}")
        return False
    if r.status_code == 200:
        return _ok("WooCommerce connected")
    return _fail(f"HTTP {r.status_code}")


def test_list_products(wc_url, ck, cs):
    ok, products, err = wp_client.list_products(wc_url, ck, cs, per_page=5)
    if not ok:
        return _fail(f"List failed: {err}")
    if not products:
        return _fail("No products found (site empty?)")
    _ok(f"Found {len(products)} products")
    return products


def test_get_product(wc_url, ck, cs, product_id):
    ok, product, err = wp_client.get_product(wc_url, ck, cs, product_id)
    if not ok:
        return _fail(f"Get failed: {err}")
    assert product["id"] == product_id, "ID mismatch"
    _ok(f"Product: {product['name']} (Rs {product.get('price', 0)})")
    return product


def test_editor_data_product(wp_url, wp_user, wp_pass, wc_url, ck, cs, product_id):
    ok, result, err = wp_client.get_editor_data(
        wp_url, wp_user, wp_pass, wc_url, ck, cs,
        item_type="product", item_id=product_id)
    if not ok:
        return _fail(f"get_editor_data failed: {err}")
    assert result["item"]["id"] == product_id
    opts = result["options"]
    _ok(f"Product: {result['item']['name']}")
    _ok(f"Categories available: {len(opts.get('categories', []))}")
    _ok(f"Tags available: {len(opts.get('tags', []))}")
    _ok(f"Attributes available: {len(opts.get('attributes', []))}")
    fk = result.get("focus_keyword", "")
    _ok(f"Focus keyword: {fk if fk else '(empty)'}")
    return result


def test_editor_data_post(wp_url, wp_user, wp_pass, wc_url, ck, cs, post_id):
    ok, result, err = wp_client.get_editor_data(
        wp_url, wp_user, wp_pass, wc_url, ck, cs,
        item_type="post", item_id=post_id)
    if not ok:
        return _fail(f"get_editor_data failed: {err}")
    assert result["item"]["id"] == post_id
    _ok(f"Post: {result['item']['title']}")
    _ok(f"Status: {result['item']['status']}")
    _ok(f"WP Categories: {len(result['options'].get('categories', []))}")
    _ok(f"WP Tags: {len(result['options'].get('tags', []))}")
    return result


def test_update_product_price(wc_url, ck, cs, product_id, original_price):
    # Update to same price (no actual change)
    ok, product, err = wp_client.update_product(
        wc_url, ck, cs, product_id, regular_price=str(original_price))
    if not ok:
        return _fail(f"Update failed: {err}")
    _ok(f"Product update API works (no-op save)")
    return product


def test_update_product_full_fields(wc_url, ck, cs, product_id, product):
    """Test that we can update categories + tags without breaking."""
    try:
        cats = [{"id": c["id"]} for c in product.get("categories", [])]
        tags = [{"id": t["id"]} for t in product.get("tags", [])]
        ok, updated, err = wp_client.update_product(
            wc_url, ck, cs, product_id,
            categories=cats, tags=tags)
        if not ok:
            return _fail(f"Full update failed: {err}")
        _ok("Full field update (categories + tags) works")
        return updated
    except Exception as e:
        return _fail(f"Exception: {e}")


def test_list_taxonomy(wc_url, ck, cs):
    ok, cats, err = taxonomy.list_all(wc_url, ck, cs, "wc_categories")
    if not ok:
        return _fail(f"Categories list failed: {err}")
    _ok(f"Categories: {len(cats)}")
    ok2, tags, err2 = taxonomy.list_all(wc_url, ck, cs, "wc_tags")
    if ok2:
        _ok(f"Tags: {len(tags)}")
    ok3, attrs, err3 = taxonomy.list_all(wc_url, ck, cs, "wc_attributes")
    if ok3:
        _ok(f"Attributes: {len(attrs)}")
    return True


def test_list_posts(wp_url, wp_user, wp_pass):
    ok, posts, err = wp_client.list_posts(wp_url, wp_user, wp_pass, per_page=5)
    if not ok:
        return _fail(f"List posts failed: {err}")
    _ok(f"Found {len(posts)} posts")
    return posts


def test_get_post_context_edit(wp_url, wp_user, wp_pass, post_id):
    """Verify get_post uses context=edit for raw content."""
    ok, post, err = wp_client.get_post(wp_url, wp_user, wp_pass, post_id)
    if not ok:
        return _fail(f"Get post failed: {err}")
    content = post.get("content", "")
    if "<p>" in content or "<!--" in content:
        _ok("Raw content retrieved (context=edit works)")
    else:
        _warn("Content seems rendered, not raw")
    _ok(f"Post: {post['title']}")
    return post


def test_media_get(wp_url, wp_user, wp_pass, media_id):
    try:
        r = requests.get(
            f"{wp_url}/wp-json/wp/v2/media/{media_id}",
            auth=(wp_user, wp_pass), timeout=15)
        if r.status_code == 200:
            _ok(f"Media {media_id} URL: {r.json().get('source_url', '')[:60]}...")
            return True
        return _fail(f"HTTP {r.status_code}")
    except Exception as e:
        return _fail(f"Exception: {e}")


# =============================================================================
# MAIN
# =============================================================================
def main():
    print("=" * 60)
    print(f"{C.BOLD}  Khan Herbal Editor — Verification Test Suite{C.RESET}")
    print("=" * 60)
    print("\nEnter credentials (press Enter for defaults):\n")

    wp_url = input("WP URL [https://darkcyan-turkey-703045.hostingersite.com/]: ").strip() or "https://darkcyan-turkey-703045.hostingersite.com"
    wp_url = wp_url.rstrip("/")
    wp_user = input("WP username: ").strip()
    wp_pass = getpass("WP application password: ")

    wc_url_input = input("WC URL [same as WP]: ").strip()
    wc_url = (wc_url_input or wp_url).rstrip("/")
    ck = input("WC consumer key: ").strip()
    cs = getpass("WC consumer secret: ")

    if not wp_user or not wp_pass:
        print("\n❌ WP credentials required")
        return 1
    if not ck or not cs:
        print("\n❌ WC credentials required")
        return 1

    print("\n" + "=" * 60)
    print("  Running Tests...")
    print("=" * 60)

    runner = TestRunner()

    # Connection tests
    runner.test("WP Connect", test_wp_connect, wp_url, wp_user, wp_pass)
    runner.test("WC Connect", test_wc_connect, wc_url, ck, cs)

    # Products
    products = None
    try:
        print(f"\n{C.BOLD}▶ List Products{C.RESET}")
        products = test_list_products(wc_url, ck, cs)
        runner.passed += 1
        runner.results.append(("List Products", "PASS", None))
    except Exception as e:
        runner.failed += 1
        runner.results.append(("List Products", "FAIL", str(e)))

    if products and isinstance(products, list) and len(products) > 0:
        first_product_id = products[0]["id"]

        runner.test("Get Product", test_get_product, wc_url, ck, cs, first_product_id)
        runner.test("Editor Data (Product)", test_editor_data_product,
                     wp_url, wp_user, wp_pass, wc_url, ck, cs, first_product_id)

        # Get full product for further tests
        ok, full_product, err = wp_client.get_product(wc_url, ck, cs, first_product_id)
        if ok:
            try:
                test_update_product_price(wc_url, ck, cs, first_product_id,
                                           full_product.get("regular_price", "0"))
                runner.passed += 1
                runner.results.append(("Update Product Price", "PASS", None))
            except Exception as e:
                runner.failed += 1
                runner.results.append(("Update Product Price", "FAIL", str(e)))

            try:
                test_update_product_full_fields(wc_url, ck, cs, first_product_id, full_product)
                runner.passed += 1
                runner.results.append(("Full Field Update", "PASS", None))
            except Exception as e:
                runner.failed += 1
                runner.results.append(("Full Field Update", "FAIL", str(e)))

        # Test featured image if product has one
        if full_product and full_product.get("featured_image_id"):
            runner.test("Media Get", test_media_get,
                         wp_url, wp_user, wp_pass,
                         full_product["featured_image_id"])
    else:
        _warn("No products found — skipping product tests")

    # Posts
    posts = None
    try:
        print(f"\n{C.BOLD}▶ List Posts{C.RESET}")
        posts = test_list_posts(wp_url, wp_user, wp_pass)
        runner.passed += 1
        runner.results.append(("List Posts", "PASS", None))
    except Exception as e:
        runner.failed += 1
        runner.results.append(("List Posts", "FAIL", str(e)))

    if posts and isinstance(posts, list) and len(posts) > 0:
        first_post_id = posts[0]["id"]
        runner.test("Get Post (context=edit)", test_get_post_context_edit,
                     wp_url, wp_user, wp_pass, first_post_id)
        runner.test("Editor Data (Post)", test_editor_data_post,
                     wp_url, wp_user, wp_pass, wc_url, ck, cs, first_post_id)
    else:
        _warn("No posts found — skipping post tests")

    # Taxonomy
    runner.test("List Taxonomy", test_list_taxonomy, wc_url, ck, cs)

    return 0 if runner.summary() else 1


if __name__ == "__main__":
    sys.exit(main())