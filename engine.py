# =============================================================================
# KHAN HERBAL STORES — ENGINE v5.0
# =============================================================================
# File: engine.py
# Purpose: Content + SEO + RankMath engine for products AND blog posts.
#
# v5.0 CHANGES (vs v4.4):
#   - NEW: generate_blog_article() for blog posts
#   - NEW: build_blog_rankmath_meta() for RankMath on posts
#   - NEW: build_blog_og_meta() integration with open_graph
#   - NEW: store info available to blog content
#   - KEPT: All product functions (100% same as v4.4)
# =============================================================================

# =============================================================================
# SECTION 1 — IMPORTS
# =============================================================================
import os
import re
import json
import random
import hashlib
from typing import Dict, List, Any, Tuple

from slugify import slugify
from urllib.parse import quote_plus

try:
    from jinja2 import Template
    JINJA = True
except ImportError:
    Template = None
    JINJA = False

random.seed(42)


# =============================================================================
# SECTION 2 — CONSTANTS
# =============================================================================
SITE_URL = "https://darkcyan-turkey-703045.hostingersite.com"
PRODUCT_BASE = "/product/"
CURRENCY_CODE = "PKR"
CURRENCY_SYMBOL = "Rs"
PRICE_MIN = 199
PRICE_MAX = 999
PRODUCT_COUNT = 325

DENSITY_MIN = 1.0
DENSITY_MAX = 1.5
DENSITY_HARD_MAX = 2.5

# Blog-specific targets
BLOG_WORD_MIN = 1500
BLOG_WORD_MAX = 2000
BLOG_DENSITY_MIN = 1.0
BLOG_DENSITY_MAX = 1.5


# =============================================================================
# SECTION 3 — STORE
# =============================================================================
STORE_DEFAULTS = {
    "name":           "Khan Herbal Stores",
    "tagline":        "Authentic Herbal Remedies in Pakistan",
    "description":    "Pakistan's trusted online store for pure, natural and authentic herbal products.",
    "email":          "info@khanherbalstores.com",
    "phone":          "+92 300 0000000",
    "whatsapp":       "+923218224219",
    "address_line1":  "Main Market",
    "address_line2":  "",
    "city":           "Karachi",
    "state":          "Sindh",
    "country":        "PK",
    "postal_code":    "74000",
    "business_hours": "Mon-Sat 9:00 AM - 9:00 PM",
    "facebook":       "",
    "instagram":      "",
    "youtube":        "",
    "twitter":        "",
}

_ACTIVE_STORE = dict(STORE_DEFAULTS)


def set_store(store: Dict[str, Any]) -> None:
    global _ACTIVE_STORE
    merged = dict(STORE_DEFAULTS)
    merged.update({k: v for k, v in (store or {}).items() if v is not None})
    _ACTIVE_STORE = merged


def get_store() -> Dict[str, Any]:
    return dict(_ACTIVE_STORE)


# =============================================================================
# SECTION 4 — SITE PAGES
# =============================================================================
SITE_PAGES = {
    "home":         {"name": "Home",            "url": f"{SITE_URL}/",                          "anchors": ["Khan Herbal Stores", "our home page", "main store"]},
    "shop":         {"name": "Shop",            "url": f"{SITE_URL}/shop/",                     "anchors": ["shop all products", "browse our collection", "view product range", "explore the full catalog"]},
    "herbs":        {"name": "Natural Herbs",   "url": f"{SITE_URL}/natural-herbs/",            "anchors": ["explore natural herbs", "browse herbal collection", "discover natural remedies", "shop herbal products"]},
    "how_to_shop":  {"name": "How To Shop",     "url": f"{SITE_URL}/how-to-shop/",              "anchors": ["learn how to shop", "read shopping guide", "see ordering steps"]},
    "faqs":         {"name": "FAQs",            "url": f"{SITE_URL}/faqs/",                     "anchors": ["read our FAQs", "find common answers", "view frequently asked questions"]},
    "cart":         {"name": "Cart",            "url": f"{SITE_URL}/cart/",                     "anchors": ["add to your cart", "proceed to checkout", "complete your order"]},
    "shipping":     {"name": "Shipping Policy", "url": f"{SITE_URL}/shipping-delivery-policy/", "anchors": ["check shipping policy", "see delivery options", "view shipping info"]},
    "refund":       {"name": "Refund Policy",   "url": f"{SITE_URL}/refund-returns-policy/",    "anchors": ["read refund policy", "view return policy", "check refund terms"]},
    "about":        {"name": "About Us",        "url": f"{SITE_URL}/about-us/",                 "anchors": ["about Khan Herbal Stores", "learn our story", "know us better"]},
    "contact":      {"name": "Contact Us",      "url": f"{SITE_URL}/contact-us/",               "anchors": ["contact us", "reach out to us", "get in touch"]},
    "account":      {"name": "My Account",      "url": f"{SITE_URL}/my-account/",               "anchors": ["your account", "manage account", "view dashboard"]},
    "tracking":     {"name": "Order Tracking",  "url": f"{SITE_URL}/order-tracking/",           "anchors": ["track your order", "check order status", "order tracking"]},
    "checkout":     {"name": "Checkout",        "url": f"{SITE_URL}/checkout/",                 "anchors": ["secure checkout", "complete payment"]},
    "privacy":      {"name": "Privacy Policy",  "url": f"{SITE_URL}/privacy-policy/",           "anchors": ["privacy policy"]},
    "terms":        {"name": "Terms",           "url": f"{SITE_URL}/terms-conditions/",         "anchors": ["terms & conditions"]},
    "disclaimer":   {"name": "Disclaimer",      "url": f"{SITE_URL}/disclaimer/",               "anchors": ["disclaimer"]},
    "cookie":       {"name": "Cookie Policy",   "url": f"{SITE_URL}/cookie-policy/",            "anchors": ["cookie policy"]},
}

CATEGORIES = {
    "oils":     {"name": "Herbal Oils",         "slug": "herbal-oils"},
    "unani":    {"name": "Unani Medicines",     "slug": "unani-medicines"},
    "syrups":   {"name": "Syrups & Sharbat",    "slug": "syrups-sharbat"},
    "vinegars": {"name": "Vinegars & Sirka",    "slug": "vinegars-sirka"},
    "herbs":    {"name": "Herbs & Botanicals",  "slug": "herbs-botanicals"},
    "powders":  {"name": "Powders & Tablets",   "slug": "powders-tablets"},
}

TAG_RULES = [
    ("oil", "herbal-oil"), ("vinegar", "herbal-vinegar"), ("syrup", "herbal-syrup"),
    ("majun", "unani-majun"), ("khamira", "khamira"), ("itrifal", "itrifal"),
    ("jawarish", "jawarish"), ("laboob", "laboob"), ("seed", "herbal-seeds"),
    ("leaves", "herbal-leaves"), ("flower", "herbal-flowers"), ("bark", "herbal-bark"),
    ("root", "herbal-root"), ("safoof", "safoof"), ("kushta", "kushta"),
]

ATTRIBUTE_PRESETS = {
    "oils":     {"name": "Volume",    "options": ["100ml", "200ml", "500ml"]},
    "syrups":   {"name": "Volume",    "options": ["200ml", "500ml", "1000ml"]},
    "vinegars": {"name": "Volume",    "options": ["250ml", "500ml", "1000ml"]},
    "herbs":    {"name": "Weight",    "options": ["100g", "250g", "500g", "1kg"]},
    "unani":    {"name": "Pack Size", "options": ["125g", "250g", "500g"]},
    "powders":  {"name": "Weight",    "options": ["50g", "100g", "250g"]},
}

USE_CASE_KEYWORDS = {
    "hair":        ["hair", "bhringraj", "amla", "castor", "almond", "coconut", "hibiscus", "malkangni"],
    "skin":        ["skin", "neem", "aloe", "sandalwood", "turmeric", "multani", "babchi", "chamomile"],
    "digestive":   ["digest", "jawarish", "itrifal", "hing", "sonth", "ajwain", "kamooni", "halila"],
    "immunity":    ["immunity", "shilajit", "ashwagandha", "giloy", "tulsi", "mulethi"],
    "respiratory": ["throat", "cough", "mulethi", "banafsha", "tulsi", "sual", "sandal"],
    "wellness":    ["wellness", "health", "vitality", "strength", "energy", "tonic"],
}

KEYWORD_MODIFIERS = {
    "long_tail":     ["best", "pure", "organic", "natural", "premium", "cold-pressed", "authentic"],
    "short_tail":    ["buy", "shop", "online", "price"],
    "navigational":  ["near me", "online store", "official site", "in pakistan"],
    "informational": ["benefits", "uses", "how to use", "for hair", "for skin", "side effects"],
    "transactional": ["buy online", "order now", "free delivery", "cash on delivery", "cod"],
    "commercial":    ["best brand", "top quality", "review", "price in pakistan", "wholesale"],
}


# =============================================================================
# SECTION 5 — SYNONYMS
# =============================================================================
SYNONYMS = {
    "herbal": ["botanical", "plant-based", "natural", "organic", "herb-based"],
    "natural": ["pure", "authentic", "traditional", "genuine", "unadulterated"],
    "beneficial": ["helpful", "useful", "advantageous", "valuable", "rewarding"],
    "excellent": ["outstanding", "superb", "remarkable", "exceptional", "top-tier"],
    "use": ["apply", "utilize", "employ", "incorporate", "leverage"],
    "product": ["item", "offering", "solution", "remedy", "preparation"],
    "quality": ["grade", "standard", "caliber", "excellence", "craftsmanship"],
    "traditional": ["time-honored", "age-old", "classical", "heritage", "ancestral"],
    "effective": ["potent", "powerful", "efficient", "reliable", "proven"],
    "pure": ["unadulterated", "clean", "authentic", "refined", "unmixed"],
    "trusted": ["reliable", "dependable", "proven", "established", "reputed"],
    "carefully": ["meticulously", "precisely", "attentively", "thoughtfully", "expertly"],
    "sourced": ["obtained", "procured", "selected", "acquired", "harvested"],
    "processed": ["prepared", "manufactured", "formulated", "crafted", "developed"],
    "preserve": ["retain", "maintain", "keep", "safeguard", "protect"],
    "potency": ["strength", "efficacy", "power", "vigor", "intensity"],
    "support": ["assist", "aid", "enhance", "promote", "facilitate"],
    "wellness": ["health", "wellbeing", "vitality", "fitness", "balance"],
    "journey": ["path", "route", "process", "experience", "transition"],
    "solutions": ["options", "remedies", "alternatives", "approaches", "methods"],
    "customers": ["buyers", "clients", "users", "patrons", "shoppers"],
    "rely": ["depend", "trust", "count on", "lean on", "bank on"],
    "deliver": ["provide", "supply", "offer", "give", "present"],
    "premium": ["high-end", "top-grade", "superior", "exclusive", "elite"],
    "consistent": ["steady", "stable", "uniform", "reliable", "dependable"],
    "ingredients": ["components", "elements", "substances", "materials", "contents"],
    "growers": ["farmers", "cultivators", "producers", "harvesters", "suppliers"],
    "strict": ["rigorous", "stringent", "tight", "careful", "disciplined"],
    "control": ["management", "oversight", "supervision", "regulation", "monitoring"],
    "measures": ["steps", "methods", "actions", "procedures", "practices"],
    "variety": ["range", "selection", "assortment", "collection", "diversity"],
    "formula": ["recipe", "composition", "blend", "mixture", "preparation"],
    "remedy": ["treatment", "cure", "solution", "medicine", "therapy"],
    "centuries": ["generations", "decades", "ages", "eras", "long periods"],
    "authentic": ["genuine", "real", "true", "verified", "legitimate"],
    "routine": ["regimen", "habit", "practice", "schedule", "pattern"],
    "results": ["outcomes", "effects", "benefits", "consequences", "returns"],
    "experience": ["undergo", "feel", "enjoy", "encounter", "realize"],
    "explore": ["discover", "examine", "investigate", "consider", "survey"],
    "health": ["wellbeing", "vitality", "fitness", "condition", "state"],
    "regular": ["consistent", "routine", "steady", "ongoing", "continuous"],
    "usage": ["application", "consumption", "intake", "utilization", "administration"],
    "directions": ["instructions", "guidelines", "recommendations", "protocols", "steps"],
    "container": ["bottle", "jar", "pack", "package", "vessel"],
    "freshness": ["quality", "newness", "vitality", "potency", "integrity"],
    "convenience": ["ease", "simplicity", "accessibility", "comfort", "usability"],
    "versatile": ["adaptable", "flexible", "multipurpose", "all-purpose", "multi-use"],
    "genuine": ["authentic", "real", "true", "legitimate", "certified"],
    "crafted": ["made", "created", "produced", "developed", "formed"],
    "extracted": ["obtained", "derived", "collected", "harvested", "procured"],
    "blend": ["mixture", "combination", "fusion", "mix", "amalgam"],
    "fresh": ["new", "recent", "unused", "vibrant", "vivid"],
    "nourish": ["feed", "strengthen", "fortify", "sustain", "nurture"],
    "restore": ["renew", "revitalize", "revive", "replenish", "refresh"],
    "enhance": ["improve", "boost", "increase", "elevate", "strengthen"],
    "protect": ["shield", "guard", "defend", "safeguard", "preserve"],
    "balance": ["harmonize", "stabilize", "regulate", "align", "equilibrate"],
    "rejuvenate": ["refresh", "revitalize", "restore", "renew", "reinvigorate"],
    # Blog-specific
    "learn": ["discover", "understand", "explore", "study", "examine"],
    "tips": ["guidelines", "recommendations", "pointers", "advice", "insights"],
    "guide": ["handbook", "manual", "roadmap", "walkthrough", "tutorial"],
    "improve": ["enhance", "boost", "upgrade", "advance", "strengthen"],
    "people": ["individuals", "users", "customers", "readers", "audience"],
    "important": ["crucial", "essential", "vital", "critical", "significant"],
    "many": ["numerous", "several", "countless", "various", "multiple"],
    "start": ["begin", "commence", "initiate", "kick off", "launch"],
    "avoid": ["prevent", "skip", "sidestep", "evade", "stay away from"],
}


# =============================================================================
# SECTION 6 — TEMPLATES
# =============================================================================
INTRO_OPENERS = [
    "Discover the timeless benefits of", "Experience the remarkable power of",
    "Unlock the natural potential of", "Trust the tradition behind",
    "Choose the purity of", "Embrace the goodness of",
]
INTRO_CONNECTORS = [
    "one of the most trusted herbal preparations in traditional Unani and Ayurvedic medicine.",
    "a premium herbal remedy carefully sourced from trusted cultivators.",
    "an authentic wellness solution refined through time-honored methods.",
    "a highly regarded botanical formula used for generations across South Asia.",
    "a natural herbal product valued for its consistent and reliable results.",
]
INTRO_CLOSERS = [
    "Thousands of customers trust it for its beneficial properties and dependable performance.",
    "Our store delivers authentic herbal products right to your doorstep with fast shipping.",
    "Every batch is quality-checked to ensure maximum potency and freshness.",
    "Whether you are new to herbal wellness or a long-time user, it delivers consistent results.",
    "It is the ideal choice for anyone seeking authentic herbal solutions for daily wellbeing.",
]


# =============================================================================
# SECTION 7 — KEYWORD ENGINE
# =============================================================================
def slugify_product(name: str) -> str:
    return slugify(name, lowercase=True)[:75].strip("-")


def base_keyword(product_name: str) -> str:
    return re.sub(r"\([^)]*\)", "", product_name.lower()).strip()


def get_use_case(product_name: str) -> str:
    base = base_keyword(product_name)
    for uc, words in USE_CASE_KEYWORDS.items():
        if any(w in base for w in words):
            return uc
    return "wellness"


def generate_focus_keyword(product_name: str) -> str:
    return f"{base_keyword(product_name)} for {get_use_case(product_name)}"


def generate_long_tail_keywords(p, count=5):
    return [f"{m} {base_keyword(p)}" for m in KEYWORD_MODIFIERS["long_tail"][:count]]


def generate_short_tail_keywords(p, count=4):
    return [f"{m} {base_keyword(p)}" for m in KEYWORD_MODIFIERS["short_tail"][:count]]


def generate_navigational_keywords(p, count=3):
    return [f"{base_keyword(p)} {m}" for m in KEYWORD_MODIFIERS["navigational"][:count]]


def generate_informational_keywords(p, count=4):
    return [f"{base_keyword(p)} {m}" for m in KEYWORD_MODIFIERS["informational"][:count]]


def generate_transactional_keywords(p, count=4):
    return [f"{base_keyword(p)} {m}" for m in KEYWORD_MODIFIERS["transactional"][:count]]


def generate_commercial_keywords(p, count=4):
    return [f"{m} {base_keyword(p)}" for m in KEYWORD_MODIFIERS["commercial"][:count]]


def generate_semantic_keywords(product_name: str, count=8) -> List[str]:
    cat = guess_category(product_name)
    pool = [
        "herbal remedies", "natural wellness", "ayurvedic medicine",
        "unani treatment", "traditional healing", "organic skincare",
        "hair care", "skin care", "digestive health", "immunity booster",
        "natural oils", "pure herbs", "cold pressed", "no preservatives",
    ]
    if cat == "oils":
        pool += ["cold pressed oil", "carrier oil", "massage oil", "hair oil"]
    elif cat == "syrups":
        pool += ["herbal syrup", "natural tonic", "sharbat", "immunity syrup"]
    elif cat == "vinegars":
        pool += ["apple cider vinegar", "herbal vinegar", "natural vinegar"]
    elif cat == "herbs":
        pool += ["dried herbs", "herbal powder", "botanical ingredients"]
    r = random.Random(hash(product_name) % 10000)
    r.shuffle(pool)
    return pool[:count]


def generate_all_keywords(product_name: str) -> Dict[str, Any]:
    return {
        "focus":         generate_focus_keyword(product_name),
        "long_tail":     generate_long_tail_keywords(product_name),
        "short_tail":    generate_short_tail_keywords(product_name),
        "navigational":  generate_navigational_keywords(product_name),
        "informational": generate_informational_keywords(product_name),
        "transactional": generate_transactional_keywords(product_name),
        "commercial":    generate_commercial_keywords(product_name),
        "semantic":      generate_semantic_keywords(product_name),
    }


def calculate_keyword_density(text: str, keyword: str) -> float:
    if not text or not keyword:
        return 0.0
    text_lower = text.lower()
    total_words = len(re.findall(r"\b\w+\b", text_lower))
    if total_words == 0:
        return 0.0
    kw_count = text_lower.count(keyword.lower())
    kw_words = len(keyword.split())
    return round((kw_count * kw_words / total_words) * 100, 2)


def count_keyword(text: str, keyword: str) -> int:
    return text.lower().count(keyword.lower())


def guess_category(product_name: str) -> str:
    n = product_name.lower()
    if "oil" in n: return "oils"
    if "vinegar" in n: return "vinegars"
    if "syrup" in n or "sharbat" in n: return "syrups"
    if any(k in n for k in ["majun", "khamira", "itrifal", "jawarish", "laboob"]): return "unani"
    if any(k in n for k in ["safoof", "kushta"]) or n.endswith(" hab"): return "powders"
    return "herbs"


def _syn(word: str, variant: int = 0) -> str:
    if word.lower() in SYNONYMS:
        pool = SYNONYMS[word.lower()]
        return pool[variant % len(pool)]
    return word


# =============================================================================
# SECTION 8 — STORE HELPERS
# =============================================================================
def build_brand_link() -> str:
    s = get_store()
    return f'<a href="{SITE_PAGES["home"]["url"]}">{s["name"]}</a>'


def build_product_cta_block(product_name: str, product_url: str) -> str:
    """CTA block with WhatsApp button + store brand."""
    s = get_store()
    wa_number = re.sub(r"[^\d]", "", s.get("whatsapp", "") or "")
    if not wa_number:
        wa_number = "923218224219"
    message = (
        f"Assalam-o-Alaikum! I am interested in {product_name}. "
        f"Please share more details and pricing. "
        f"Product link: {product_url}"
    )
    wa_link = f"https://wa.me/{wa_number}?text={quote_plus(message)}"
    brand = s["name"]
    home_url = SITE_PAGES["home"]["url"]
    return (
        '<div class="product-cta" style="margin:24px 0;padding:20px;'
        'background:linear-gradient(135deg,#f1f8e9,#e8f5e9);border-radius:10px;'
        'border-left:4px solid #2e7d32;">'
        f'<p style="margin:0 0 12px 0;font-size:15px;color:#1b5e20;">'
        f'<strong>Buy {product_name} from '
        f'<a href="{home_url}" style="color:#2e7d32;text-decoration:none;'
        f'font-weight:700;">{brand}</a></strong>'
        f' — Pakistan&#39;s trusted online store for authentic herbal products.'
        f'</p>'
        f'<a href="{wa_link}" target="_blank" rel="noopener" '
        f'style="display:inline-block;background:#25D366;color:#fff;'
        f'padding:12px 24px;border-radius:8px;text-decoration:none;'
        f'font-weight:700;font-size:15px;'
        f'box-shadow:0 2px 6px rgba(37,211,102,0.4);">'
        f'&#128172; Order on WhatsApp</a>'
        f'<span style="margin-left:12px;font-size:12px;color:#666;">'
        f'Ask about <strong>{product_name}</strong> — fast reply</span>'
        '</div>'
    )


def build_blog_cta_block(blog_title: str) -> str:
    """CTA block for blog posts."""
    s = get_store()
    wa_number = re.sub(r"[^\d]", "", s.get("whatsapp", "") or "")
    if not wa_number:
        wa_number = "923218224219"
    message = (
        f"Assalam-o-Alaikum! I just read your article '{blog_title}' "
        f"and I am interested in learning more about your herbal products."
    )
    wa_link = f"https://wa.me/{wa_number}?text={quote_plus(message)}"
    brand = s["name"]
    home_url = SITE_PAGES["home"]["url"]
    shop_url = SITE_PAGES["shop"]["url"]
    return (
        '<div class="blog-cta" style="margin:24px 0;padding:20px;'
        'background:linear-gradient(135deg,#e3f2fd,#e1f5fe);border-radius:10px;'
        'border-left:4px solid #2563eb;">'
        f'<p style="margin:0 0 12px 0;font-size:15px;color:#0d47a1;">'
        f'<strong>Trusted by thousands across Pakistan — '
        f'<a href="{home_url}" style="color:#1565c0;text-decoration:none;'
        f'font-weight:700;">{brand}</a></strong>'
        f'</p>'
        f'<p style="margin:0 0 14px 0;font-size:14px;color:#333;">'
        f'Explore our full range of authentic herbal products: '
        f'<a href="{shop_url}" style="color:#1565c0;">shop here</a>.</p>'
        f'<a href="{wa_link}" target="_blank" rel="noopener" '
        f'style="display:inline-block;background:#25D366;color:#fff;'
        f'padding:12px 24px;border-radius:8px;text-decoration:none;'
        f'font-weight:700;font-size:15px;">'
        f'&#128172; Chat with us on WhatsApp</a>'
        '</div>'
    )


# =============================================================================
# SECTION 9 — PRODUCT CONTENT BUILDERS (unchanged from v4.4)
# =============================================================================
def _build_intro(product_name, kw, cat, rng):
    opener = rng.choice(INTRO_OPENERS)
    connector = rng.choice(INTRO_CONNECTORS)
    closer = rng.choice(INTRO_CLOSERS)
    v = rng.randint(0, 4)
    s = get_store()
    cat_text = {
        "oils": "herbal oil", "syrups": "herbal syrup", "vinegars": "herbal vinegar",
        "herbs": "herbal botanical", "unani": "Unani preparation", "powders": "herbal formulation",
    }.get(cat, "herbal product")
    return (
        f"<strong>{product_name}</strong> is {connector} "
        f"If you have been searching for the best <strong>{kw}</strong> in Pakistan, "
        f"you are in the right place. {opener} {product_name} — a "
        f"{_syn('natural', v)} {cat_text} that supports your {_syn('wellness', v)} "
        f"journey with {_syn('consistent', v)} results. Whether you want authentic "
        f"{_syn('herbal', v)} remedies or are simply exploring options, this product "
        f"delivers {_syn('premium', v)} {_syn('quality', v)} in every use. Available "
        f"exclusively at {s['name']}. {closer}"
    )


def _build_what_is(product_name, kw, cat, rng):
    v = rng.randint(0, 4)
    cat_text = {
        "oils": f"{product_name} is a cold-pressed or traditionally extracted herbal oil used for hair care, skin care, and therapeutic massage.",
        "syrups": f"{product_name} is a herbal syrup (sharbat) prepared from natural ingredients, commonly used for cooling, digestion, and general wellness.",
        "vinegars": f"{product_name} is a naturally fermented vinegar infused with herbal goodness, traditionally used for digestive and metabolic support.",
        "herbs": f"{product_name} is a dried botanical product sourced from premium herbs, used in teas, poultices, and traditional remedies.",
        "unani": f"{product_name} is a classical Unani preparation made from a blend of herbs, spices, and natural ingredients following traditional formulas.",
        "powders": f"{product_name} is a finely processed powder formulation used in traditional medicine for specific wellness needs.",
    }.get(cat, f"{product_name} is a premium herbal product.")
    return (
        f"{cat_text} It has been used for {_syn('centuries', v)} across South Asia "
        f"and the Middle East as part of traditional healing systems. The product "
        f"retains its {_syn('natural', v)} properties through {_syn('carefully', v)} "
        f"{_syn('sourced', v)} ingredients and traditional {_syn('processed', v)} "
        f"methods, ensuring maximum {_syn('potency', v)} with every use. Unlike "
        f"synthetic alternatives, it works gently with your body's natural systems. "
        f"Whether you are a long-time user of {_syn('herbal', v)} remedies or just "
        f"beginning your {_syn('wellness', v)} journey, this product offers a "
        f"{_syn('reliable', v)}, {_syn('traditional', v)} solution. Each package is "
        f"designed to {_syn('preserve', v)} freshness and {_syn('potency', v)}, so "
        f"what reaches you is exactly what nature intended. It is an ideal choice "
        f"for anyone seeking a {_syn('genuine', v)} botanical solution."
    )


def _build_benefits(product_name, kw, cat, rng):
    v = rng.randint(0, 4)
    intro = (
        f"{product_name} offers a wide range of advantages that make it a staple "
        f"in many homes across Pakistan. When used consistently, it supports "
        f"multiple aspects of health and {_syn('wellness', v)}. Below are the key "
        f"benefits of choosing this {_syn('traditional', v)} {_syn('remedy', v)} "
        f"for your daily {_syn('routine', v)}."
    )
    benefit_pairs = [
        ("Hair Care Support",
         "Rich in nutrients that strengthen hair roots, promote natural growth, "
         "and reduce hair fall. Regular use nourishes the scalp and adds visible shine to dull hair."),
        ("Skin Wellness",
         "Helps improve skin texture, reduce dryness, and maintain a healthy glow. "
         "The natural compounds support hydration and elasticity without harsh chemicals."),
        ("Digestive Balance",
         "Supports healthy digestion, soothes the stomach, and helps maintain gut "
         "balance when used as directed. A trusted choice for daily wellness."),
        ("Immunity Support",
         "Contains natural antioxidants that help strengthen the body's defenses "
         "and promote overall vitality. Ideal for seasonal wellness routines."),
        ("Quality Assurance",
         "Free from artificial colors, synthetic fragrances, and harmful "
         "preservatives. Every batch is tested for purity, potency, and freshness."),
        ("Value & Convenience",
         "Offered at a fair price with cash on delivery available across Pakistan. "
         "Fast shipping ensures you receive your order quickly and in perfect condition."),
    ]
    rng.shuffle(benefit_pairs)
    parts = []
    for title, text in benefit_pairs[:6]:
        parts.append(f"<h3>{product_name} for {title}</h3>\n<p>{text}</p>")
    return intro, "\n".join(parts)


def _build_how_to_use(product_name, cat, rng):
    v = rng.randint(0, 4)
    usage = {
        "oils": "Apply a small quantity to the desired area and massage gently in circular motions. For hair, use 2–3 times a week before washing. For skin, apply daily after bathing.",
        "syrups": "Take 1–2 teaspoons (5–10ml) twice daily after meals, or as directed by a healthcare practitioner. Shake well before use. Mix with water or milk for taste.",
        "vinegars": "Mix 1–2 teaspoons in a glass of warm water and consume once or twice daily, preferably before meals. Can also be used in salads and cooking. Not for children under 12.",
        "herbs": "Use 1–2 teaspoons in hot water to make a herbal tea. Alternatively, add to warm milk with honey. For topical use, mix with a little water to form a paste.",
        "unani": "Take the recommended dosage (usually 5–10g) once or twice daily with water or milk, or as prescribed by a Unani practitioner. Best consumed after meals.",
        "powders": "Take 1–2 teaspoons (or as directed) with water, honey, or milk. For best results, consume consistently for 4–6 weeks without skipping days.",
    }.get(cat, "Use as directed by a qualified practitioner.")
    return (
        f"{usage} For best results, maintain a consistent schedule and follow the "
        f"recommended {_syn('directions', v)}. Many customers notice visible "
        f"improvements within 4–6 weeks of regular use. {product_name} is gentle "
        f"enough for daily application yet {_syn('effective', v)} enough to deliver "
        f"noticeable changes. Always store the product in a cool, dry place away "
        f"from direct sunlight. Keep the {_syn('container', v)} tightly closed after "
        f"each use to {_syn('preserve', v)} {_syn('freshness', v)}. Consult a "
        f"healthcare professional before use if you are pregnant, nursing, or taking "
        f"medication. Keep out of reach of children. For any questions about usage "
        f"or dosage, please reach out through our website — our team is happy to "
        f"guide you on the best way to use this product."
    )


def _build_storage_safety(product_name, rng):
    v = rng.randint(0, 4)
    return (
        f"To ensure {product_name} retains its {_syn('potency', v)} and "
        f"{_syn('freshness', v)} for as long as possible, store it in a cool, dry "
        f"place away from direct sunlight and heat sources. Keep the container "
        f"tightly sealed after each use to prevent contamination and oxidation. "
        f"Avoid contact with water inside the container. Do not refrigerate unless "
        f"specifically instructed on the label. Keep away from children and pets. "
        f"If you have sensitive skin, perform a patch test before first use. "
        f"Consult a qualified healthcare practitioner before using this product if "
        f"you are pregnant, nursing, taking prescription medication, or have any "
        f"pre-existing medical condition. This product is not intended to diagnose, "
        f"treat, cure, or prevent any disease. Individual results may vary based on "
        f"body type, lifestyle, and consistency of use."
    )


def _build_ingredients(product_name, cat, rng):
    v = rng.randint(0, 4)
    return (
        f"At our store, {product_name} is prepared using the finest "
        f"{_syn('natural', v)} {_syn('ingredients', v)} sourced from trusted "
        f"{_syn('growers', v)}. We follow {_syn('strict', v)} {_syn('quality', v)} "
        f"{_syn('control', v)} {_syn('measures', v)} at every stage — from harvest "
        f"to packaging. No artificial colors, synthetic fragrances, or harmful "
        f"preservatives are added. Every batch is tested for purity and "
        f"{_syn('potency', v)}, ensuring that what you receive is exactly what "
        f"nature intended. Our commitment to authenticity means you can trust "
        f"every drop that reaches your doorstep. This {_syn('traditional', v)} "
        f"{_syn('product', v)} reflects our dedication to providing genuine "
        f"{_syn('herbal', v)} {_syn('solutions', v)} to {_syn('customers', v)} "
        f"across Pakistan. We believe in transparency, which is why all our "
        f"products come with a clear ingredient list and usage instructions."
    )


def _build_faq(product_name, kw, cat):
    faqs = [
        (f"What is {product_name} used for?",
         f"{product_name} is traditionally used for overall wellness, hair care, "
         f"skin health, digestion, and immunity support. Always follow the "
         f"recommended dosage or usage instructions for best results."),
        (f"Is {product_name} safe for daily use?",
         f"Yes, when taken or applied as directed. If you are pregnant, nursing, "
         f"or on medication, consult a doctor before use. Our quality-tested "
         f"formula ensures consistent safety across batches."),
        (f"How long until I see results?",
         f"Most users notice visible improvements within 4–6 weeks of consistent "
         f"use. Results vary by individual, so we recommend completing at least "
         f"one full cycle for best assessment."),
        (f"Where can I buy {product_name} online in Pakistan?",
         f"You can order directly from our online store with fast delivery and "
         f"cash on delivery available across Pakistan."),
    ]
    html = ""
    for q, a in faqs:
        html += f"<h3>{q}</h3>\n<p>{a}</p>\n"
    return html


def _build_conclusion(product_name, rng, kw):
    v = rng.randint(0, 4)
    s = get_store()
    brand_link = build_brand_link()
    return (
        f"<strong>{product_name}</strong> is more than just a {_syn('product', v)} — "
        f"it is a {_syn('traditional', v)} {_syn('remedy', v)} that connects you to "
        f"generations of {_syn('herbal', v)} wisdom. If you have been searching for "
        f"<strong>{kw}</strong>, we deliver {_syn('quality', v)} you can trust. "
        f"{s['name']} offers authentic {product_name} with fast shipping across "
        f"Pakistan. Visit {brand_link} to explore our full range of herbal products. "
        f"Order today and experience the difference. Our team is always available to "
        f"answer your questions and help you choose the right herbal solution for "
        f"your needs."
    )


PRODUCT_ARTICLE_TEMPLATE = """<h1>{title}</h1>

<p>{intro}</p>

<h2>What is {product_name}?</h2>
<p>{what_is}</p>

<h2>Key Benefits</h2>
<p>{benefits_intro}</p>
{benefits_list}

<h2>How to Use {product_name}</h2>
<p>{how_to_use}</p>

<h2>Storage &amp; Safety Guidelines</h2>
<p>{storage_safety}</p>

<h2>Ingredients &amp; Quality</h2>
<p>{ingredients}</p>

<h2>Frequently Asked Questions</h2>
{faq_html}

<h2>Final Thoughts</h2>
<p>{conclusion}</p>

{product_cta}

{related_products_html}
"""


# =============================================================================
# SECTION 10 — DENSITY / DUPLICATE
# =============================================================================
def _strip_html(html: str) -> str:
    return re.sub(r"<[^>]+>", " ", html or "")


def enforce_density(html: str, product_name: str, kw: str) -> Tuple[str, Dict[str, Any]]:
    plain = _strip_html(html)
    density = calculate_keyword_density(plain, kw)
    count = count_keyword(plain, kw)
    return html, {
        "density": density,
        "occurrences": count,
        "in_range": DENSITY_MIN <= density <= DENSITY_MAX,
        "safe": density <= DENSITY_HARD_MAX,
    }


def _ngrams(text: str, n: int = 5) -> set:
    words = re.findall(r"\b\w+\b", text.lower())
    if len(words) < n:
        return set()
    return {tuple(words[i:i+n]) for i in range(len(words) - n + 1)}


def _jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def _article_plain(product: Dict[str, Any], max_words: int = 200) -> str:
    html = product.get("article", {}).get("html", "")
    words = _strip_html(html).split()[:max_words]
    return " ".join(words)


def compute_uniqueness_report(products: List[Dict[str, Any]],
                               sample_size: int = 30) -> Dict[str, Any]:
    total = len(products)
    if total < 2:
        return {"products_checked": total, "pairs_checked": 0,
                "avg_similarity": 0.0, "max_similarity": 0.0,
                "high_similarity_pairs": []}
    rng = random.Random(12345)
    pairs_to_check = min(sample_size, total * (total - 1) // 2)
    fps = {i: _ngrams(_article_plain(products[i]), n=5) for i in range(total)}
    sims, high = [], []
    seen = set()
    for _ in range(pairs_to_check):
        i, j = rng.sample(range(total), 2)
        key = tuple(sorted([i, j]))
        if key in seen:
            continue
        seen.add(key)
        s = _jaccard(fps[i], fps[j])
        sims.append(s)
        if s > 0.35:
            high.append({"p1": products[i]["name"], "p2": products[j]["name"],
                         "similarity": round(s * 100, 1)})
    if not sims:
        return {"products_checked": total, "pairs_checked": 0,
                "avg_similarity": 0.0, "max_similarity": 0.0,
                "high_similarity_pairs": []}
    return {"products_checked": total, "pairs_checked": len(sims),
            "avg_similarity": round(sum(sims) / len(sims) * 100, 1),
            "max_similarity": round(max(sims) * 100, 1),
            "high_similarity_pairs": high[:10]}


# =============================================================================
# SECTION 11 — SEO ENGINE (products)
# =============================================================================
def generate_seo_title(product_name: str, focus_kw: str) -> str:
    s = get_store()
    brand = s["name"]
    candidates = [
        f"{focus_kw.title()} | Buy Online in Pakistan",
        f"{product_name} — {focus_kw.title()}",
        f"{product_name} | {brand}",
        f"Buy {product_name} Online | {brand}",
    ]
    for c in candidates:
        if len(c) <= 60:
            return c
    return f"{product_name[:35]} | {brand}"[:60]


def generate_meta_description(product_name: str, focus_kw: str) -> str:
    s = get_store()
    brand = s["name"]
    templates = [
        f"Shop {product_name} at {brand} — {focus_kw}. 100% pure, natural & authentic. Fast delivery across Pakistan. Order now with COD.",
        f"Buy {product_name} online at {brand}. {focus_kw.capitalize()}. Premium quality, free delivery on bulk orders across Pakistan.",
        f"{product_name} for {focus_kw} — available at {brand}. Natural, authentic, quality-tested. Order today with fast & reliable delivery.",
    ]
    for t in templates:
        if 140 <= len(t) <= 160:
            return t
    best = min(templates, key=lambda x: abs(len(x) - 155))
    return best[:160]


def generate_canonical_url(product_name: str) -> str:
    return f"{SITE_URL}{PRODUCT_BASE}{slugify_product(product_name)}/"


def calculate_rankmath_score(meta: Dict[str, Any], article: Dict[str, Any]) -> int:
    """RankMath score estimate."""
    score = 0
    kw = meta.get("focus_keyword", "").lower()
    product_name = meta.get("product_name", "")
    title = meta.get("meta:rank_math_title", "").lower()
    desc = meta.get("meta:rank_math_description", "").lower()
    url = meta.get("meta:rank_math_canonical_url", "")
    html = article.get("html", "")
    html_lower = html.lower()
    plain = _strip_html(html).lower()

    if kw and kw in title: score += 10
    if kw and kw in desc: score += 10
    if product_name and slugify_product(product_name) in url: score += 5
    if kw and kw in plain[:600]: score += 10

    d = article.get("keyword_density", 0)
    if 1.0 <= d <= 1.5: score += 10
    elif 0.5 <= d <= 2.0: score += 6

    wc = article.get("word_count", 0)
    if wc >= 800: score += 10
    elif wc >= 600: score += 5

    if 40 <= len(title) <= 60: score += 5
    if 140 <= len(desc) <= 160: score += 5
    if kw and kw in html_lower: score += 5

    if html.count("<a href=") >= 5: score += 10
    elif html.count("<a href=") >= 1: score += 5

    if 'alt="' in html: score += 3
    if url and len(url) < 75: score += 5

    h_all = re.findall(r"<h[12][^>]*>(.*?)</h[12]>", html_lower, re.S)
    if any(kw in h for h in h_all): score += 2

    return min(score, 100)


# =============================================================================
# SECTION 12 — RANKMATH META (products)
# =============================================================================
def build_rankmath_meta(product_name: str, focus_kw: str = None) -> Dict[str, str]:
    if focus_kw is None:
        focus_kw = generate_focus_keyword(product_name)
    seo_title = generate_seo_title(product_name, focus_kw)
    meta_desc = generate_meta_description(product_name, focus_kw)
    canonical = generate_canonical_url(product_name)
    robots = 'a:2:{i:0;s:5:"index";i:1;s:6:"follow";}'
    return {
        "meta:rank_math_focus_keyword":         focus_kw,
        "meta:rank_math_title":                 seo_title,
        "meta:rank_math_description":           meta_desc,
        "meta:rank_math_robots":                robots,
        "meta:rank_math_canonical_url":         canonical,
        "meta:rank_math_facebook_title":        seo_title,
        "meta:rank_math_facebook_description":  meta_desc,
        "meta:rank_math_twitter_title":         seo_title,
        "meta:rank_math_twitter_description":   meta_desc,
        "meta:rank_math_advanced_robots":       "",
    }


# =============================================================================
# SECTION 13 — INTERNAL LINKS
# =============================================================================
_RELATED_CACHE: Dict[str, List[str]] = {}
_ALL_PRODUCTS: List[str] = []


def set_product_universe(products: List[str]) -> None:
    global _ALL_PRODUCTS, _RELATED_CACHE
    _ALL_PRODUCTS = list(products)
    _RELATED_CACHE = {}


def _same_category_score(p1, p2):
    return 3 if guess_category(p1) == guess_category(p2) else 0


def _word_overlap_score(p1, p2):
    w1 = set(re.findall(r"\b\w+\b", p1.lower()))
    w2 = set(re.findall(r"\b\w+\b", p2.lower()))
    w1.discard("oil"); w2.discard("oil")
    return len(w1 & w2)


def _use_case_score(p1, p2):
    s = 0
    for uc, words in USE_CASE_KEYWORDS.items():
        if any(w in p1.lower() for w in words) and any(w in p2.lower() for w in words):
            s += 2
    return s


def find_related_products(product_name: str, top_n: int = 4) -> List[str]:
    if not _ALL_PRODUCTS:
        return []
    if product_name in _RELATED_CACHE:
        return _RELATED_CACHE[product_name]
    scores = []
    for other in _ALL_PRODUCTS:
        if other == product_name:
            continue
        s = (_same_category_score(product_name, other) * 2
             + _word_overlap_score(product_name, other) * 3
             + _use_case_score(product_name, other) * 2)
        scores.append((other, s))
    scores.sort(key=lambda x: -x[1])
    related = [n for n, _ in scores[:top_n]]
    _RELATED_CACHE[product_name] = related
    return related


def product_url(product_name: str) -> str:
    return f"{SITE_URL}{PRODUCT_BASE}{slugify_product(product_name)}/"


def build_product_link(product_name: str, anchor: str = None) -> str:
    return f'<a href="{product_url(product_name)}">{anchor or product_name}</a>'


def build_page_link(page_key: str, anchor: str = None) -> str:
    if page_key not in SITE_PAGES:
        return ""
    page = SITE_PAGES[page_key]
    if anchor is None:
        anchor = random.choice(page["anchors"])
    return f'<a href="{page["url"]}">{anchor}</a>'


def build_internal_links_html(product_name: str) -> Dict[str, str]:
    seed = int(hashlib.md5(product_name.encode()).hexdigest(), 16)
    rng = random.Random(seed)
    s = get_store()
    pages = ["shop", "herbs", "how_to_shop", "faqs", "cart", "shipping", "refund"]
    rng.shuffle(pages)

    home_link = f'<p>Browse the complete collection at {build_brand_link()}.</p>'
    intro_link = f'<p>Explore our full {build_page_link(pages[0])} collection today.</p>'
    benefits_link = f'<p>You can browse more options in our {build_page_link(pages[1])} category.</p>'
    how_to_use_link = f'<p>New to herbal products? Read our {build_page_link("how_to_shop", "shopping guide")}.</p>'
    conclusion_link = (f'<p><a href="{SITE_PAGES["shop"]["url"]}">'
                       f'<strong>Order {product_name} now</strong></a> '
                       f'from {s["name"]} with fast delivery across Pakistan.</p>')
    contact_link = f'<p>Questions? <a href="{SITE_PAGES["contact"]["url"]}">Contact us</a> anytime.</p>'

    related = find_related_products(product_name, top_n=4)
    related_items = [f"<li>{build_product_link(rp)}</li>" for rp in related]
    related_html = ""
    if related_items:
        related_html = "<h2>Related Herbal Products</h2>\n<ul>\n" + "\n".join(related_items) + "\n</ul>"

    return {
        "home_link": home_link, "intro_link": intro_link,
        "benefits_link": benefits_link, "how_to_use_link": how_to_use_link,
        "conclusion_link": conclusion_link, "contact_link": contact_link,
        "related_products_html": related_html,
    }


# =============================================================================
# SECTION 14 — PRODUCT ARTICLE ASSEMBLY
# =============================================================================
def generate_article(product_name: str, keywords: Dict[str, Any] = None) -> Dict[str, Any]:
    if keywords is None:
        keywords = generate_all_keywords(product_name)

    kw = keywords["focus"]
    cat = guess_category(product_name)
    use_case = get_use_case(product_name)
    seed = int(hashlib.md5(product_name.encode()).hexdigest(), 16) % 2**31
    rng = random.Random(seed)

    title = f"{product_name} for {use_case.title()} — Complete Guide"

    intro = _build_intro(product_name, kw, cat, rng)
    what_is = _build_what_is(product_name, kw, cat, rng)
    benefits_intro, benefits_list = _build_benefits(product_name, kw, cat, rng)
    how_to_use = _build_how_to_use(product_name, cat, rng)
    storage_safety = _build_storage_safety(product_name, rng)
    ingredients = _build_ingredients(product_name, cat, rng)
    faq_html = _build_faq(product_name, kw, cat)
    conclusion = _build_conclusion(product_name, rng, kw)
    product_cta = build_product_cta_block(product_name, product_url(product_name))

    links = build_internal_links_html(product_name)
    intro = intro + " " + links["intro_link"]
    benefits_intro = benefits_intro + " " + links["benefits_link"]
    how_to_use = how_to_use + " " + links["how_to_use_link"] + " " + links["contact_link"]

    html = PRODUCT_ARTICLE_TEMPLATE.format(
        title=title, product_name=product_name, intro=intro,
        what_is=what_is, benefits_intro=benefits_intro,
        benefits_list=benefits_list, how_to_use=how_to_use,
        storage_safety=storage_safety, ingredients=ingredients,
        faq_html=faq_html, conclusion=conclusion,
        product_cta=product_cta,
        related_products_html=links["related_products_html"],
    )

    html, density_report = enforce_density(html, product_name, kw)

    plain = _strip_html(html)
    word_count = len(re.findall(r"\b\w+\b", plain))
    density = calculate_keyword_density(plain, kw)
    occurrences = count_keyword(plain, kw)

    return {
        "html": html, "word_count": word_count,
        "keyword_density": density, "keyword_occurrences": occurrences,
        "density_in_range": density_report["in_range"],
        "focus_keyword": kw, "variant_used": seed % 10,
    }


# =============================================================================
# SECTION 15 — PRODUCT BUILDER
# =============================================================================
def assign_category(product_name: str) -> Dict[str, str]:
    key = guess_category(product_name)
    return {"key": key, "name": CATEGORIES[key]["name"], "slug": CATEGORIES[key]["slug"]}


def assign_tag(product_name: str) -> str:
    n = product_name.lower()
    for keyword, tag in TAG_RULES:
        if keyword in n:
            return tag
    return "herbal-products"


def assign_attribute(product_name: str) -> Dict[str, Any]:
    cat = guess_category(product_name)
    preset = ATTRIBUTE_PRESETS.get(cat, {"name": "Size", "options": ["Standard"]})
    return {"name": preset["name"], "value": preset["options"][0],
            "visible": True, "variation": False}


def generate_sku(index: int) -> str:
    return f"HERB-{index + 1:03d}"


def generate_price(product_name: str) -> float:
    seed = int(hashlib.md5(product_name.encode()).hexdigest(), 16)
    rng = random.Random(seed)
    return round(rng.uniform(PRICE_MIN, PRICE_MAX), 2)


def assign_stock(index: int, total: int, in_stock_count: int = 10) -> int:
    return random.choice([5, 10, 15, 20, 25]) if index < in_stock_count else 0


def build_product_dict(product_name: str, index: int, total: int) -> Dict[str, Any]:
    keywords = generate_all_keywords(product_name)
    article = generate_article(product_name, keywords)
    rankmath = build_rankmath_meta(product_name, keywords["focus"])
    category = assign_category(product_name)
    tag = assign_tag(product_name)
    attribute = assign_attribute(product_name)
    sku = generate_sku(index)
    slug = slugify_product(product_name)
    price = generate_price(product_name)
    stock = assign_stock(index, total)

    score = calculate_rankmath_score(
        {**rankmath, "focus_keyword": keywords["focus"],
         "product_name": product_name}, article)

    return {
        "index": index + 1, "name": product_name, "slug": slug, "sku": sku,
        "price": price, "stock": stock,
        "stock_status": "instock" if stock > 0 else "outofstock",
        "category_key": category["key"], "category_name": category["name"],
        "category_slug": category["slug"], "tag": tag, "attribute": attribute,
        "keywords": keywords, "article": article,
        "rankmath": rankmath, "rankmath_score": score,
        "canonical_url": generate_canonical_url(product_name),
        "product_url": product_url(product_name),
    }


def build_all_products(products: List[str]) -> List[Dict[str, Any]]:
    set_product_universe(products)
    return [build_product_dict(name, i, len(products)) for i, name in enumerate(products)]


# =============================================================================
# SECTION 16 — CSV BUILDER
# =============================================================================
WOO_COLUMNS_BASE = [
    "ID", "Type", "SKU", "Name", "Published", "Is featured?", "Visibility in catalog",
    "Short description", "Description", "Date sale price starts", "Date sale price ends",
    "Tax status", "Tax class", "In stock?", "Stock", "Low stock amount",
    "Backorders allowed?", "Sold individually?", "Weight (kg)", "Length (cm)",
    "Width (cm)", "Height (cm)", "Allow customer reviews?", "Purchase note",
    "Sale price", "Regular price", "Categories", "Tags", "Shipping class",
    "Images", "Download limit", "Download expiry days", "Parent",
    "Grouped products", "Upsells", "Cross-sells", "External URL", "Button text",
    "Position", "Attribute 1 name", "Attribute 1 value(s)", "Attribute 1 visible",
    "Attribute 1 global",
]


def build_csv_row(product: Dict[str, Any], image_urls: List[str] = None) -> Dict[str, str]:
    s = get_store()
    short_desc = (f"{product['name']} from {s['name']} — a premium herbal product "
                  f"sourced from trusted growers, processed to preserve natural "
                  f"potency. Order online in Pakistan with fast delivery.")
    return {
        "ID": "", "Type": "simple", "SKU": product["sku"], "Name": product["name"],
        "Published": "1", "Is featured?": "0", "Visibility in catalog": "visible",
        "Short description": short_desc, "Description": product["article"]["html"],
        "Date sale price starts": "", "Date sale price ends": "",
        "Tax status": "taxable", "Tax class": "",
        "In stock?": "1" if product["stock"] > 0 else "0",
        "Stock": str(product["stock"]), "Low stock amount": "5",
        "Backorders allowed?": "0", "Sold individually?": "0",
        "Weight (kg)": "0.5", "Length (cm)": "", "Width (cm)": "", "Height (cm)": "",
        "Allow customer reviews?": "1", "Purchase note": "",
        "Sale price": "", "Regular price": f"{product['price']:.2f}",
        "Categories": product["category_name"], "Tags": product["tag"],
        "Shipping class": "",
        "Images": ",".join(image_urls) if image_urls else "",
        "Download limit": "", "Download expiry days": "", "Parent": "",
        "Grouped products": "", "Upsells": "", "Cross-sells": "",
        "External URL": "", "Button text": "", "Position": str(product["index"]),
        "Attribute 1 name": product["attribute"]["name"],
        "Attribute 1 value(s)": product["attribute"]["value"],
        "Attribute 1 visible": "1", "Attribute 1 global": "0",
        **product["rankmath"],
    }


def build_csv_data(products, image_map=None):
    if image_map is None:
        image_map = {}
    all_cols = list(WOO_COLUMNS_BASE)
    if products:
        for k in products[0]["rankmath"].keys():
            if k not in all_cols:
                all_cols.append(k)
    rows = []
    for p in products:
        row = build_csv_row(p, image_map.get(p["name"], []))
        for c in all_cols:
            row.setdefault(c, "")
        rows.append(row)
    return all_cols, rows


# =============================================================================
# SECTION 17 — BLOG POST CONTENT GENERATION (v5.1 — density fixed)
# =============================================================================
# Strategy: focus keyword only 5 times in ~1800 words (density ~1.1%)
# Uses synonyms, pronouns, and topic variants elsewhere.

BLOG_OPENERS = [
    "If you have been searching for reliable information about",
    "Many people across Pakistan are talking about",
    "The wellness community in Pakistan is increasingly focused on",
    "Understanding the truth about",
    "Recent interest in traditional herbal medicine has brought attention to",
]

BLOG_CTA_INTROS = [
    "The team at {store} is committed to helping you make informed choices about natural wellness.",
    "At {store}, we believe in empowering our readers with honest, research-backed information.",
    "Our experts at {store} have spent years helping customers find the right herbal solutions.",
    "{store} has become Pakistan's trusted destination for authentic herbal remedies.",
]


def _blog_slug(title: str) -> str:
    return slugify(title, lowercase=True)[:75].strip("-")


def _blog_focus_keyword(title: str) -> str:
    """Extract focus keyword from blog title — 4 words."""
    stop_words = {"a", "an", "the", "and", "or", "for", "of", "to", "in",
                  "on", "with", "how", "what", "why", "when", "best", "top"}
    words = [w for w in re.findall(r"\b\w+\b", title.lower())
             if w not in stop_words and len(w) > 2]
    if len(words) >= 4:
        return " ".join(words[:4])
    if len(words) >= 3:
        return " ".join(words[:3])
    return " ".join(words) if words else title.lower()


def _blog_build_intro(title: str, kw: str, rng: random.Random) -> str:
    """~260 words. Focus keyword appears ONCE."""
    s = get_store()
    opener = rng.choice(BLOG_OPENERS)
    v = rng.randint(0, 4)
    return (
        f"<p>{opener} <strong>{kw}</strong>, you are not alone. "
        f"This comprehensive guide walks you through everything you need to know "
        f"about natural approaches to hair and wellness — from the science behind "
        f"them to practical tips you can apply today.</p>"
        f"<p>Whether you are new to {_syn('herbal', v)} wellness or a long-time "
        f"user of {_syn('traditional', v)} remedies, this article will give you "
        f"clear, actionable insights that actually work. The {_syn('natural', v)} "
        f"health market in Pakistan has grown significantly in recent years. With "
        f"that growth comes both opportunity and responsibility. Our goal at "
        f"{s['name']} is to help you navigate this space with {_syn('trusted', v)} "
        f"information you can rely on.</p>"
        f"<p>Over the next few minutes, we will explore the fundamentals, the "
        f"practical application, the common mistakes to avoid, and the expert "
        f"tips that separate {_syn('average', 0)} results from {_syn('excellent', v)} "
        f"ones. By the end, you will have a solid framework for making "
        f"{_syn('better', 0)} choices for yourself and your family.</p>"
        f"<p>Let's begin with why this topic matters more than ever in today's "
        f"world.</p>"
    )


def _blog_build_why_matters(title: str, kw: str, rng: random.Random) -> str:
    """~320 words. Focus keyword appears ZERO times — uses synonyms."""
    v = rng.randint(0, 4)
    return (
        f"<h2>Why This Matters More Than Ever</h2>"
        f"<p>The shift toward {_syn('natural', v)}, {_syn('holistic', 0)} "
        f"approaches to wellness is not a passing trend. It reflects a growing "
        f"global movement toward {_syn('authentic', v)} care that aligns with "
        f"{_syn('traditional', v)} practices and is backed by {_syn('careful', v)} "
        f"evidence. Millions of people worldwide are seeking "
        f"{_syn('alternatives', 0)} that respect both ancient wisdom and modern "
        f"standards of safety.</p>"
        f"<p>In Pakistan specifically, {_syn('herbal', v)} traditions have been "
        f"part of the cultural fabric for {_syn('centuries', v)}. From Unani "
        f"medicine to Ayurvedic practices, our ancestors understood the value of "
        f"{_syn('plant-based', 0)} healing long before modern science caught up. "
        f"Today, we have the unique opportunity to combine that wisdom with "
        f"contemporary standards of {_syn('quality', v)} and consistency.</p>"
        f"<p>When it comes to natural hair and wellness care, the difference "
        f"between success and frustration often comes down to understanding three "
        f"things: the fundamentals, the right way to apply them, and the common "
        f"mistakes to avoid. This article covers all three so you can move "
        f"forward with {_syn('confidence', 0)}.</p>"
        f"<p>Beyond the practical benefits, there is also a deeper reason this "
        f"matters. When you choose {_syn('natural', v)} approaches over synthetic "
        f"alternatives, you are making a {_syn('conscious', 0)} decision about "
        f"what you put into and onto your body. You are choosing products that "
        f"work with your body's natural systems rather than against them.</p>"
        f"<p>Whether you are looking to {_syn('improve', 0)} your daily routine, "
        f"support a specific wellness goal, or simply learn more about "
        f"{_syn('herbal', v)} practices, the information below will serve as a "
        f"{_syn('practical', 0)} foundation.</p>"
    )


def _blog_build_main_content(title: str, kw: str, rng: random.Random) -> str:
    """~550 words. Focus keyword appears TWICE (in H2 + one para)."""
    v = rng.randint(0, 4)
    return (
        f"<h2>Understanding {kw.title()} — The Basics</h2>"
        f"<p>Before diving into advanced applications, let us establish a solid "
        f"foundation. This topic involves several key components that work "
        f"together to deliver {_syn('beneficial', v)} results. Understanding "
        f"these components helps you make {_syn('better', 0)} decisions and get "
        f"the most from your {_syn('wellness', v)} routine.</p>"

        f"<h3>The Science Behind It</h3>"
        f"<p>Modern research has begun to validate what {_syn('traditional', v)} "
        f"practitioners have known for {_syn('centuries', v)}. The active "
        f"compounds in many herbs have been studied for their "
        f"{_syn('potential', 0)} benefits, and the evidence continues to grow. "
        f"Scientific studies have identified specific phytonutrients that play a "
        f"role in supporting health at a cellular level. That said, it is "
        f"important to set {_syn('realistic', 0)} expectations — "
        f"{_syn('herbal', v)} remedies work gradually and supportively, not as "
        f"instant fixes.</p>"
        f"<p>What makes them {_syn('effective', v)} is their ability to work in "
        f"harmony with your body's natural systems. Rather than forcing a rapid "
        f"change, they support gradual improvement that is more likely to last.</p>"

        f"<h3>The Quality Factor</h3>"
        f"<p>One of the most overlooked aspects is the quality of what you use. "
        f"The {_syn('difference', 0)} between average and {_syn('excellent', v)} "
        f"results often comes down to sourcing. Choose products from "
        f"{_syn('trusted', v)} suppliers who follow strict {_syn('quality', v)} "
        f"{_syn('control', v)} {_syn('measures', v)}.</p>"
        f"<p>Look for clear ingredient lists, transparent sourcing information, "
        f"and certificates of analysis when available. A little extra care in "
        f"this step pays off significantly in results.</p>"

        f"<h3>Common Misconceptions</h3>"
        f"<p>One of the biggest misconceptions is that more is always better. "
        f"In reality, {_syn('consistent', v)} moderate use delivers "
        f"{_syn('superior', 0)} results compared to occasional heavy use. Another "
        f"misconception is that all natural products are the same — the reality "
        f"is that {_syn('quality', v)} varies widely and sourcing matters "
        f"immensely.</p>"
        f"<p>Some people also expect overnight results. Natural approaches work "
        f"on your body's timeline, which is {_syn('gradual', 0)} and "
        f"{_syn('sustainable', 0)}. Give the process {_syn('patience', 0)} and "
        f"consistency.</p>"

        f"<h2>How to Apply These Principles in Practice</h2>"
        f"<p>Putting knowledge into practice is where real {_syn('results', v)} "
        f"come from. Here is a step-by-step approach that works for most people:</p>"
        f"<ul>"
        f"<li><strong>Start small:</strong> Introduce one change at a time and "
        f"observe how your body responds over one to two weeks.</li>"
        f"<li><strong>Stay consistent:</strong> The topic works best when applied "
        f"regularly rather than sporadically. Consistency is the foundation of "
        f"all progress.</li>"
        f"<li><strong>Track your progress:</strong> Keep simple notes on what "
        f"works and what does not — this helps you refine over time.</li>"
        f"<li><strong>Adjust gradually:</strong> Based on results, fine-tune your "
        f"routine. Small tweaks compound into big improvements.</li>"
        f"<li><strong>Be patient:</strong> Meaningful change takes weeks, not "
        f"days. Give your body time to respond naturally.</li>"
        f"</ul>"
    )


def _blog_build_mistakes(title: str, kw: str, rng: random.Random) -> str:
    """~270 words. Focus keyword appears ZERO times."""
    v = rng.randint(0, 4)
    return (
        f"<h2>Common Mistakes to Avoid</h2>"
        f"<p>Even {_syn('well-intentioned', 0)} people make mistakes when they "
        f"first start with {_syn('natural', v)} wellness. Avoiding these common "
        f"pitfalls can save you time, money, and frustration:</p>"
        f"<ul>"
        f"<li><strong>Expecting instant results:</strong> "
        f"{_syn('Herbal', v)} remedies work with your body, not against it. "
        f"Give them time to take effect.</li>"
        f"<li><strong>Ignoring quality:</strong> Cheap, low-{_syn('quality', v)} "
        f"products often deliver poor results. Invest in {_syn('authentic', v)} "
        f"sources.</li>"
        f"<li><strong>Mixing too many things:</strong> Adding five new products "
        f"at once makes it impossible to know what is working.</li>"
        f"<li><strong>Skipping professional advice:</strong> If you have a "
        f"medical condition or take prescription medication, always consult a "
        f"healthcare provider first.</li>"
        f"<li><strong>Giving up too early:</strong> Many people stop just before "
        f"results would begin to show. Consistency is the {_syn('key', 0)}.</li>"
        f"</ul>"
        f"<p>By avoiding these pitfalls, you dramatically increase your chances "
        f"of {_syn('long-term', 0)} success. The best approach is one that fits "
        f"your lifestyle and can be sustained comfortably.</p>"
    )


def _blog_build_expert_tips(title: str, kw: str, rng: random.Random) -> str:
    """~230 words. Focus keyword appears ZERO times."""
    v = rng.randint(0, 4)
    s = get_store()
    return (
        f"<h2>Expert Tips for Better Results</h2>"
        f"<p>After working with thousands of customers across Pakistan, the team "
        f"at {s['name']} has identified a few {_syn('practical', v)} tips that "
        f"consistently make a difference:</p>"
        f"<ol>"
        f"<li><strong>Invest in quality sources:</strong> The difference between "
        f"average and {_syn('excellent', v)} results often comes down to "
        f"sourcing. Choose {_syn('trusted', v)} suppliers with transparent "
        f"practices.</li>"
        f"<li><strong>Follow dosage guidelines:</strong> More is not better. "
        f"Follow the recommended usage for {_syn('optimal', 0)} results.</li>"
        f"<li><strong>Combine with lifestyle habits:</strong> Natural approaches "
        f"work best alongside a balanced diet, adequate sleep, and regular "
        f"activity. They are supporting players, not replacements.</li>"
        f"<li><strong>Document your journey:</strong> A simple journal helps you "
        f"identify patterns and adjust effectively over time.</li>"
        f"<li><strong>Seek guidance when needed:</strong> Do not hesitate to ask "
        f"questions — our team is here to help you succeed.</li>"
        f"</ol>"
    )


def _blog_build_faq(title: str, kw: str, rng: random.Random) -> str:
    """~280 words. Focus keyword appears ONCE."""
    faqs = [
        (f"What makes this topic so important for wellness?",
         f"Natural approaches have gained significant attention in recent years "
         f"because they offer a {_syn('practical', 0)}, {_syn('accessible', 0)} "
         f"path to {_syn('better', 0)} health outcomes. They align with "
         f"{_syn('traditional', 0)} practices that have been refined over "
         f"{_syn('centuries', 0)}."),
        (f"How long until I see results?",
         f"Most people notice gradual improvements within four to six weeks of "
         f"consistent practice. Individual results vary based on "
         f"{_syn('lifestyle', 0)}, diet, and how regularly you apply the "
         f"principles. Patience and consistency are the {_syn('key', 0)} to "
         f"success."),
        (f"Is it safe for everyone to use?",
         f"Generally yes, but individual circumstances matter. If you are "
         f"pregnant, nursing, taking prescription medication, or managing a "
         f"chronic condition, consult a qualified healthcare provider before "
         f"making changes to your routine."),
        (f"Where can I buy authentic herbal products in Pakistan?",
         f"Reputable stores like Khan Herbal Stores offer "
         f"{_syn('quality-tested', 0)} herbal products with fast delivery "
         f"across Pakistan. For specific {kw}, we recommend exploring our full "
         f"collection online or contacting our team directly."),
    ]
    html = ""
    for q, a in faqs:
        html += f"<h3>{q}</h3>\n<p>{a}</p>\n"
    return html


def _blog_build_conclusion(title: str, kw: str, rng: random.Random) -> str:
    """~200 words. Focus keyword appears ONCE."""
    v = rng.randint(0, 4)
    s = get_store()
    cta = rng.choice(BLOG_CTA_INTROS).format(store=s["name"])
    return (
        f"<p>Throughout this guide, we have covered the fundamentals, the "
        f"practical application, the common mistakes, and the expert tips that "
        f"separate {_syn('average', 0)} from {_syn('excellent', v)} results. "
        f"The <strong>{kw}</strong> approach is a journey, not a destination. "
        f"The principles we have discussed form a solid foundation for anyone "
        f"looking to improve their wellness naturally.</p>"
        f"<p>{cta} We offer a wide range of {_syn('authentic', v)}, "
        f"{_syn('quality-tested', 0)} herbal products delivered across Pakistan. "
        f"Whether you are starting fresh or refining an existing routine, we are "
        f"here to help.</p>"
        f"<p>Take the first step today. Explore our collection, ask us any "
        f"questions, and begin your journey toward better health through "
        f"{_syn('natural', v)} choices that honor both tradition and modern "
        f"standards.</p>"
    )


BLOG_ARTICLE_TEMPLATE = """<h1>{title}</h1>

{intro}

{why_matters}

{main_content}

{mistakes}

{expert_tips}

<h2>Frequently Asked Questions</h2>
{faq_html}

<h2>Conclusion</h2>
{conclusion}

{blog_cta}
"""


def generate_blog_article(
    blog_title: str,
    focus_keyword: str = "",
    category: str = "",
    tags: str = "",
    audience: str = "",
) -> Dict[str, Any]:
    """Generate a comprehensive 1500-2000 word blog post."""
    if not blog_title or not blog_title.strip():
        return {"error": "Blog title is required"}

    blog_title = blog_title.strip()
    if not focus_keyword:
        focus_keyword = _blog_focus_keyword(blog_title)
    focus_keyword = focus_keyword.strip()

    seed = int(hashlib.md5(blog_title.encode()).hexdigest(), 16) % 2**31
    rng = random.Random(seed)

    intro = _blog_build_intro(blog_title, focus_keyword, rng)
    why_matters = _blog_build_why_matters(blog_title, focus_keyword, rng)
    main_content = _blog_build_main_content(blog_title, focus_keyword, rng)
    mistakes = _blog_build_mistakes(blog_title, focus_keyword, rng)
    expert_tips = _blog_build_expert_tips(blog_title, focus_keyword, rng)
    faq_html = _blog_build_faq(blog_title, focus_keyword, rng)
    conclusion = _blog_build_conclusion(blog_title, focus_keyword, rng)
    blog_cta = build_blog_cta_block(blog_title)

    s = get_store()
    internal_links = (
        f'<p>Explore our full '
        f'<a href="{SITE_PAGES["shop"]["url"]}">herbal collection</a> '
        f'and <a href="{SITE_PAGES["herbs"]["url"]}">natural herbs</a> '
        f'at {s["name"]}. Have questions? '
        f'<a href="{SITE_PAGES["contact"]["url"]}">Contact us</a> or read our '
        f'<a href="{SITE_PAGES["faqs"]["url"]}">FAQs</a>.</p>'
    )
    main_content = main_content + internal_links

    html = BLOG_ARTICLE_TEMPLATE.format(
        title=blog_title,
        intro=intro, why_matters=why_matters, main_content=main_content,
        mistakes=mistakes, expert_tips=expert_tips,
        faq_html=faq_html, conclusion=conclusion, blog_cta=blog_cta,
    )

    plain = _strip_html(html)
    word_count = len(re.findall(r"\b\w+\b", plain))
    density = calculate_keyword_density(plain, focus_keyword)
    occurrences = count_keyword(plain, focus_keyword)

    seo_title = _blog_seo_title(blog_title, focus_keyword)
    meta_desc = _blog_meta_description(blog_title, focus_keyword)
    slug = _blog_slug(blog_title)

    return {
        "html": html,
        "word_count": word_count,
        "keyword_density": density,
        "keyword_occurrences": occurrences,
        "focus_keyword": focus_keyword,
        "seo_title": seo_title,
        "meta_description": meta_desc,
        "slug": slug,
        "category": category,
        "tags": tags,
        "audience": audience,
        "in_target_range": (BLOG_DENSITY_MIN <= density <= BLOG_DENSITY_MAX),
    }


def _blog_seo_title(blog_title: str, focus_kw: str) -> str:
    s = get_store()
    brand = s["name"]
    candidates = [
        f"{blog_title[:50]} | {brand}",
        f"{focus_kw.title()} — Complete Guide",
        f"{blog_title[:55]}",
    ]
    for c in candidates:
        if len(c) <= 60:
            return c
    return blog_title[:60]


def _blog_meta_description(blog_title: str, focus_kw: str) -> str:
    s = get_store()
    brand = s["name"]
    templates = [
        f"Learn everything about {focus_kw}. Expert tips, common mistakes, and practical guidance from {brand}, Pakistan's trusted herbal store.",
        f"{blog_title[:100]}. Read the complete guide at {brand} — authentic herbal products and expert advice.",
        f"Discover {focus_kw} in this comprehensive guide from {brand}. Clear, practical, and backed by traditional wisdom.",
    ]
    for t in templates:
        if 140 <= len(t) <= 160:
            return t
    best = min(templates, key=lambda x: abs(len(x) - 155))
    return best[:160]


def build_blog_rankmath_meta(blog_title: str, focus_kw: str = "") -> Dict[str, str]:
    if not focus_kw:
        focus_kw = _blog_focus_keyword(blog_title)
    seo_title = _blog_seo_title(blog_title, focus_kw)
    meta_desc = _blog_meta_description(blog_title, focus_kw)
    slug = _blog_slug(blog_title)
    canonical = f"{SITE_URL}/{slug}/"
    robots = 'a:2:{i:0;s:5:"index";i:1;s:6:"follow";}'
    return {
        "meta:rank_math_focus_keyword":         focus_kw,
        "meta:rank_math_title":                 seo_title,
        "meta:rank_math_description":           meta_desc,
        "meta:rank_math_robots":                robots,
        "meta:rank_math_canonical_url":         canonical,
        "meta:rank_math_facebook_title":        seo_title,
        "meta:rank_math_facebook_description":  meta_desc,
        "meta:rank_math_twitter_title":         seo_title,
        "meta:rank_math_twitter_description":   meta_desc,
        "meta:rank_math_advanced_robots":       "",
    }


def build_blog_dict(blog_title: str, focus_keyword: str = "",
                     category: str = "", tags: str = "") -> Dict[str, Any]:
    article = generate_blog_article(
        blog_title=blog_title, focus_keyword=focus_keyword,
        category=category, tags=tags,
    )
    if "error" in article:
        return article
    rankmath = build_blog_rankmath_meta(blog_title, article.get("focus_keyword", ""))
    return {
        "title": blog_title, "slug": article["slug"],
        "content": article["html"],
        "excerpt": _strip_html(article["html"])[:200].strip(),
        "word_count": article["word_count"],
        "keyword_density": article["keyword_density"],
        "focus_keyword": article["focus_keyword"],
        "seo_title": article["seo_title"],
        "meta_description": article["meta_description"],
        "category": category, "tags": tags,
        "rankmath": rankmath,
        "rankmath_score": _calculate_blog_rm_score(article, rankmath),
    }


def _calculate_blog_rm_score(article: Dict[str, Any],
                               rankmath: Dict[str, str]) -> int:
    score = 0
    kw = article.get("focus_keyword", "").lower()
    title = rankmath.get("meta:rank_math_title", "").lower()
    desc = rankmath.get("meta:rank_math_description", "").lower()
    html = article.get("html", "")
    html_lower = html.lower()
    plain = _strip_html(html).lower()

    if kw and kw in title: score += 10
    if kw and kw in desc: score += 10
    if kw and kw in plain[:600]: score += 10

    d = article.get("keyword_density", 0)
    if 1.0 <= d <= 1.5: score += 10
    elif 0.5 <= d <= 2.0: score += 6

    wc = article.get("word_count", 0)
    if wc >= 1500: score += 10
    elif wc >= 1000: score += 7
    elif wc >= 800: score += 5

    if 40 <= len(title) <= 60: score += 5
    if 140 <= len(desc) <= 160: score += 5
    if kw and kw in html_lower: score += 5

    if html.count("<a href=") >= 5: score += 10
    elif html.count("<a href=") >= 1: score += 5

    h_count = len(re.findall(r"<h[23][^>]*>", html, re.IGNORECASE))
    if h_count >= 8: score += 5
    elif h_count >= 5: score += 3

    if "wa.me" in html_lower: score += 5

    return min(score, 100)



# =============================================================================
# SECTION 18 — ARCHIVE CSS
# =============================================================================
ARCHIVE_CSS = """/* Khan Herbal Stores — Archive Cards */
:root{--hcw:280px;--hch:440px;--hih:280px;--hth:48px;--hph:40px;--hbh:44px;--hg:20px;--hr:8px}
ul.products{display:grid!important;grid-template-columns:repeat(4,1fr);gap:var(--hg);list-style:none;padding:0;margin:0}
ul.products li.product{width:100%!important;height:var(--hch);margin:0!important;border-radius:var(--hr);
  box-shadow:0 2px 8px rgba(0,0,0,.08);background:#fff;overflow:hidden;display:flex;flex-direction:column;
  transition:transform .2s}
ul.products li.product:hover{transform:translateY(-4px)}
ul.products li.product img{width:100%;height:var(--hih);object-fit:cover;object-position:center}
ul.products li.product .woocommerce-loop-product__title{height:var(--hth);font-size:15px;
  padding:8px 12px;overflow:hidden;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;
  line-height:1.4}
ul.products li.product .price{height:var(--hph);line-height:var(--hph);font-size:17px;
  font-weight:700;color:#2e7d32;padding:0 12px}
ul.products li.product .button{height:var(--hbh);line-height:var(--hbh);margin:auto 12px 12px;
  background:#2e7d32;color:#fff;border-radius:6px;text-align:center;font-weight:600;text-decoration:none}
@media(max-width:1200px){ul.products{grid-template-columns:repeat(3,1fr)}}
@media(max-width:992px){ul.products{grid-template-columns:repeat(2,1fr)}}
@media(max-width:576px){ul.products{grid-template-columns:1fr}}
"""


def get_archive_css() -> str:
    return ARCHIVE_CSS


def save_archive_css(path="archive-consistency.css") -> str:
    with open(path, "w", encoding="utf-8") as f:
        f.write(ARCHIVE_CSS)
    return path


# =============================================================================
# SECTION 19 — REPORTS
# =============================================================================
def summarize_scores(products):
    if not products:
        return {"count": 0, "avg": 0, "min": 0, "max": 0, "passing": 0, "failing": 0}
    scores = [p.get("rankmath_score", 0) for p in products]
    return {"count": len(scores), "avg": round(sum(scores) / len(scores), 2),
            "min": min(scores), "max": max(scores),
            "passing": sum(1 for s in scores if s >= 70),
            "failing": sum(1 for s in scores if s < 70)}


def summarize_density(products):
    if not products:
        return {"avg_density": 0, "in_range": 0, "too_high": 0, "too_low": 0}
    d = [p["article"].get("keyword_density", 0) for p in products]
    return {"avg_density": round(sum(d) / len(d), 2),
            "in_range": sum(1 for x in d if DENSITY_MIN <= x <= DENSITY_MAX),
            "too_high": sum(1 for x in d if x > DENSITY_MAX),
            "too_low": sum(1 for x in d if x < DENSITY_MIN)}


def summarize_wordcount(products):
    if not products:
        return {"avg_words": 0, "min_words": 0, "max_words": 0, "under_800": 0}
    c = [p["article"].get("word_count", 0) for p in products]
    return {"avg_words": round(sum(c) / len(c)), "min_words": min(c),
            "max_words": max(c), "under_800": sum(1 for x in c if x < 800)}


def full_report(products):
    return {"scores": summarize_scores(products),
            "density": summarize_density(products),
            "wordcount": summarize_wordcount(products),
            "uniqueness": compute_uniqueness_report(products)}


def preview_product(product):
    a = product["article"]
    return (f"[{product['index']:03d}] {product['name']}\n"
            f"  SKU: {product['sku']}  Slug: {product['slug']}\n"
            f"  Price: Rs {product['price']:.2f}  Category: {product['category_name']}\n"
            f"  Focus KW: {product['keywords']['focus']}\n"
            f"  Words: {a['word_count']}  Density: {a['keyword_density']}%  "
            f"Occurrences: {a.get('keyword_occurrences', 0)}\n"
            f"  RM Score: {product['rankmath_score']}%\n")


def preview_blog(blog: Dict[str, Any]) -> str:
    return (f"[BLOG] {blog.get('title')}\n"
            f"  Slug: {blog.get('slug')}\n"
            f"  Focus KW: {blog.get('focus_keyword')}\n"
            f"  Words: {blog.get('word_count')}  Density: {blog.get('keyword_density')}%\n"
            f"  RM Score: {blog.get('rankmath_score')}%\n")


# =============================================================================
# SECTION 20 — STANDALONE TEST
# =============================================================================
if __name__ == "__main__":
    set_store({
        "name": "Khan Herbal Stores",
        "email": "info@khanherbalstores.com",
        "phone": "+92 300 1234567",
        "whatsapp": "+923218224219",
        "address_line1": "Shop 12, Main Market",
        "city": "Karachi", "state": "Sindh", "postal_code": "74000",
        "business_hours": "Mon-Sat 9am-9pm",
    })

    print("=== Product Test ===")
    demo = ["Almond Oil", "Black Seed Oil", "Olive Oil",
            "Coconut Oil", "Mustard Oil", "Neem Oil",
            "Amla Oil", "Castor Oil", "Sesame Oil", "Bhringraj Oil"]
    products = build_all_products(demo)
    for p in products[:3]:
        print(preview_product(p))
        print("-" * 60)
    rep = full_report(products)
    print("Scores:     ", rep["scores"])
    print("Density:    ", rep["density"])
    print("Word count: ", rep["wordcount"])
    print("Uniqueness: ", rep["uniqueness"])

    print("\n=== Blog Post Test ===")
    blog = build_blog_dict(
        blog_title="Top 10 Herbal Remedies for Hair Growth in Pakistan",
        focus_keyword="herbal remedies for hair",
        category="Hair Care",
        tags="hair, herbal, remedies",
    )
    print(preview_blog(blog))
    print(f"  SEO Title: {blog['seo_title']}")
    print(f"  Meta: {blog['meta_description'][:100]}...")

    print("\n✅ All tests complete")