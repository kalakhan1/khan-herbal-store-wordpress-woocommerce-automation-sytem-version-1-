# =============================================================================
# KHAN HERBAL STORES — AI PROMPT GENERATOR v1.0
# =============================================================================
# File: ai_prompts.py
# Purpose: Generate ready-to-paste AI prompts for product/blog content.
#          Validates JSON responses and imports into product/post.
#
# SECTION HIERARCHY:
#   SECTION 1  — Imports & Constants
#   SECTION 2  — Product Prompt Template
#   SECTION 3  — Blog Post Prompt Template
#   SECTION 4  — Multi-AI Format Adapters
#   SECTION 5  — Prompt Builder (fills variables)
#   SECTION 6  — Response Parser (JSON)
#   SECTION 7  — Response Validator
#   SECTION 8  — Import to Product/Post
#   SECTION 9  — Batch Operations
#   SECTION 10 — Standalone Test
# =============================================================================

# =============================================================================
# SECTION 1 — IMPORTS & CONSTANTS
# =============================================================================
import os
import re
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List

WORKSPACE = Path.cwd() / "workspace"
PROMPTS_DIR = WORKSPACE / "prompts"
PROMPTS_DIR.mkdir(parents=True, exist_ok=True)

# Target thresholds
TARGET_WORD_MIN = 1000
TARGET_WORD_MAX = 1200
TARGET_DENSITY_MIN = 1.0
TARGET_DENSITY_MAX = 1.5
TARGET_RM_SCORE = 87

# Character limits
SEO_TITLE_MAX = 60
META_DESC_MAX = 160

# Supported AI formats
AI_FORMATS = ["chatgpt", "claude", "gemini", "groq", "ollama", "generic"]


# =============================================================================
# SECTION 2 — PRODUCT PROMPT TEMPLATE
# =============================================================================
PRODUCT_PROMPT_TEMPLATE = """You are an expert SEO content writer for "{store_name}", Pakistan's trusted herbal e-commerce store.

=== TASK ===
Write a comprehensive {word_min}-{word_max} word SEO-optimized product article in HTML format for the following product.

=== PRODUCT DETAILS ===
- Product Name: {product_name}
- Category: {category}
- Brand: {brand}
- Use Case: {use_case}
- Short Description: {user_description}
- Focus Keyword: {focus_keyword}

=== STRICT REQUIREMENTS ===

1. WORD COUNT: {word_min}-{word_max} words (count only visible text, not HTML tags)

2. FOCUS KEYWORD: "{focus_keyword}"
   - Occurrences: 3-4 times ONLY (no more)
   - Keyword density: {density_min}-{density_max}% (safe zone)
   - NO keyword stuffing
   - Place in: H1 title, intro (1x), one benefit paragraph, conclusion (1x)

3. ARTICLE STRUCTURE (exact order):
   - H1: {product_name} for {use_case} — Complete Guide
   - H2 #1: What is {product_name}?
   - H2 #2: Key Benefits (with 6 H3 sub-headings)
   - H2 #3: How to Use {product_name} for Best Results
   - H2 #4: Storage & Safety Guidelines
   - H2 #5: Ingredients & Quality
   - H2 #6: Frequently Asked Questions (3 Q&A with H3)
   - H2 #7: Final Thoughts

4. INTERNAL LINKS (must include at least 4):
   - Home page: <a href="{home_url}">{store_name}</a>
   - Shop: <a href="{shop_url}">shop all products</a>
   - Natural Herbs: <a href="{herbs_url}">explore natural herbs</a>
   - Contact: <a href="{contact_url}">Contact us</a>

5. STORE CTA BLOCK (near end, before Final Thoughts):
   - Include: "Buy {product_name} from {store_name}"
   - WhatsApp button: <a href="https://wa.me/{whatsapp}?text=...">💬 Order on WhatsApp</a>
   - WhatsApp message: "Assalam-o-Alaikum! I am interested in {product_name}. Please share more details and pricing. Product link: {product_url}"

6. TONE: Professional, warm, informative, trust-building

7. CONSTRAINTS:
   - No keyword stuffing
   - No duplicate content
   - No made-up medical claims
   - No prescription-drug comparisons
   - Only HTML tags: h1, h2, h3, p, ul, li, strong, em, a
   - No external CSS, no inline styles

=== STORE INFORMATION ===
- Store: {store_name}
- Tagline: {store_tagline}
- Email: {store_email}
- Phone: {store_phone}
- WhatsApp: {whatsapp}
- Website: {store_url}

=== OUTPUT FORMAT (STRICT — RETURN ONLY JSON) ===
Return ONLY valid JSON, no markdown fences, no explanations:

{{
  "article_html": "<h1>...</h1><p>...</p>...(full HTML)",
  "seo_title": "Under {seo_title_max} characters",
  "meta_description": "Between 150-{meta_desc_max} characters",
  "focus_keyword": "{focus_keyword}",
  "word_count": 1080,
  "keyword_density": 1.25,
  "short_description": "Brief 1-2 line summary",
  "faq": [
    {{"q": "question 1", "a": "answer 1"}},
    {{"q": "question 2", "a": "answer 2"}},
    {{"q": "question 3", "a": "answer 3"}}
  ],
  "benefits": ["benefit 1", "benefit 2", "benefit 3", "benefit 4", "benefit 5", "benefit 6"]
}}

=== PRE-RETURN VALIDATION ===
Before returning, verify:
[✓] Word count between {word_min} and {word_max}
[✓] Focus keyword "{focus_keyword}" appears 3-4 times only
[✓] Focus keyword in H1, intro, and conclusion
[✓] Keyword density between {density_min}% and {density_max}%
[✓] All 7 H2 sections present
[✓] 6 H3 sub-headings under Key Benefits
[✓] 3 H3 questions under FAQs
[✓] At least 4 internal links
[✓] WhatsApp CTA present with correct number
[✓] seo_title <= {seo_title_max} characters
[✓] meta_description between 150-{meta_desc_max} characters
[✓] Valid JSON (no trailing commas, no unescaped quotes)

Return ONLY the JSON object. Nothing else.
"""


# =============================================================================
# SECTION 3 — BLOG POST PROMPT TEMPLATE
# =============================================================================
BLOG_PROMPT_TEMPLATE = """You are an expert health & wellness blogger writing for "{store_name}".

=== TASK ===
Write a comprehensive 1500-2000 word blog post in HTML format.

=== BLOG DETAILS ===
- Title: {blog_title}
- Topic: {blog_topic}
- Target Audience: {audience}
- Focus Keyword: {focus_keyword}
- Category: {category}
- Tags: {tags}

=== STRICT REQUIREMENTS ===

1. WORD COUNT: 1500-2000 words

2. FOCUS KEYWORD: "{focus_keyword}"
   - Occurrences: 5-7 times
   - Density: {density_min}-{density_max}%
   - Naturally placed in H2 headings

3. BLOG STRUCTURE:
   - H1: {blog_title}
   - Intro paragraph (150 words, hook + problem)
   - H2: Why This Matters (200 words)
   - H2: Key Information (300 words, with 2-3 H3)
   - H2: How to Apply (250 words, step-by-step)
   - H2: Common Mistakes to Avoid (200 words)
   - H2: Expert Tips (150 words)
   - H2: Frequently Asked Questions (3-5 Q&A)
   - H2: Conclusion + CTA (150 words)

4. INTERNAL LINKS (3-5):
   - Shop: <a href="{shop_url}">shop our herbal products</a>
   - Natural Herbs: <a href="{herbs_url}">browse our collection</a>
   - FAQs: <a href="{faqs_url}">read our FAQs</a>
   - Contact: <a href="{contact_url}">Contact us</a>

5. EXTERNAL LINKS (1-2, authoritative):
   - Link to WHO, NIH, or PubMed for health claims
   - Example: <a href="https://www.who.int/" target="_blank">World Health Organization</a>

6. STORE CTA + WHATSAPP:
   - Bottom CTA: "Visit {store_name} to explore our herbal range"
   - WhatsApp: <a href="https://wa.me/{whatsapp}?text=...">💬 Ask on WhatsApp</a>

7. READABILITY:
   - 8th-grade reading level
   - Short sentences (avg 15 words)
   - Use subheadings generously
   - Bullet points where possible

=== STORE INFORMATION ===
- Store: {store_name}
- Tagline: {store_tagline}
- Email: {store_email}
- Website: {store_url}

=== OUTPUT FORMAT (STRICT JSON ONLY) ===
{{
  "article_html": "<h1>...</h1><p>...</p>...(full HTML)",
  "seo_title": "Under {seo_title_max} chars",
  "meta_description": "150-{meta_desc_max} chars",
  "focus_keyword": "{focus_keyword}",
  "word_count": 1750,
  "keyword_density": 1.3,
  "excerpt": "2-3 line summary",
  "faq": [
    {{"q": "question", "a": "answer"}}
  ],
  "reading_time": "8 min"
}}

=== PRE-RETURN VALIDATION ===
[✓] Word count 1500-2000
[✓] Focus keyword 5-7 times
[✓] Density {density_min}-{density_max}%
[✓] 7 H2 sections
[✓] At least 3 internal links
[✓] At least 1 external link
[✓] WhatsApp CTA
[✓] Valid JSON

Return ONLY the JSON object. Nothing else.
"""


# =============================================================================
# SECTION 4 — MULTI-AI FORMAT ADAPTERS
# =============================================================================
def wrap_for_chatgpt(prompt: str) -> str:
    """ChatGPT / GPT-4 format — plain text."""
    return prompt


def wrap_for_claude(prompt: str) -> str:
    """Claude prefers XML-tagged structure."""
    return f"""<task>
{prompt}
</task>

<reminder>
Return ONLY valid JSON. No markdown code fences. No explanatory text.
</reminder>"""


def wrap_for_gemini(prompt: str) -> str:
    """Gemini works best with clear delimiters."""
    return f"""### INSTRUCTIONS ###
{prompt}

### REMINDER ###
Return ONLY valid JSON. Nothing else. No markdown fences."""


def wrap_for_groq(prompt: str) -> str:
    """Groq — concise prompt for fast inference."""
    return prompt + "\n\n[OUTPUT: JSON only. No prose. No fences.]"


def wrap_for_ollama(prompt: str) -> str:
    """Ollama — local models prefer explicit stop sequence."""
    return f"""{prompt}

STOP SEQUENCE: Return only the JSON object. Do not add any text before or after."""


def wrap_for_generic(prompt: str) -> str:
    """Generic wrapper — works for any AI."""
    return prompt


def adapt_prompt_for(prompt: str, ai_format: str) -> str:
    """Adapt prompt for target AI."""
    adapters = {
        "chatgpt": wrap_for_chatgpt,
        "claude":  wrap_for_claude,
        "gemini":  wrap_for_gemini,
        "groq":    wrap_for_groq,
        "ollama":  wrap_for_ollama,
        "generic": wrap_for_generic,
    }
    return adapters.get(ai_format.lower(), wrap_for_generic)(prompt)


# =============================================================================
# SECTION 5 — PROMPT BUILDER
# =============================================================================
def _slug_base(name: str) -> str:
    """Simple slugify (avoid circular import with engine)."""
    s = name.lower().strip()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s_]+", "-", s)
    return re.sub(r"-+", "-", s).strip("-")


def _auto_focus_keyword(product_name: str, use_case: str) -> str:
    return f"{product_name.lower()} for {use_case.lower()}"


def build_product_prompt(
    product_name: str,
    store: Dict[str, Any],
    pages: Dict[str, Dict],
    category: str = "",
    brand: str = "",
    use_case: str = "wellness",
    user_description: str = "",
    ai_format: str = "chatgpt",
) -> Tuple[bool, str, str]:
    """
    Build a ready-to-paste AI prompt for a product.

    Returns (ok, prompt_or_error, focus_keyword)
    """
    if not product_name or not product_name.strip():
        return False, "Product name is required", ""

    product_name = product_name.strip()
    focus_kw = _auto_focus_keyword(product_name, use_case)
    product_slug = _slug_base(product_name)

    # Get URLs from pages
    def _page_url(key: str) -> str:
        return pages.get(key, {}).get("url", "")

    # Store info
    store_name = store.get("name", "Khan Herbal Stores")
    store_tagline = store.get("tagline", "")
    store_email = store.get("email", "")
    store_phone = store.get("phone", "")
    whatsapp_raw = store.get("whatsapp", "") or "923218224219"
    whatsapp = re.sub(r"[^\d]", "", whatsapp_raw) or "923218224219"
    store_url = _page_url("home") or "https://example.com"

    product_url = f"{_page_url('home').rstrip('/')}/product/{product_slug}/" \
        if _page_url('home') else f"/product/{product_slug}/"

    # Fill template
    try:
        filled = PRODUCT_PROMPT_TEMPLATE.format(
            store_name=store_name,
            store_tagline=store_tagline,
            store_email=store_email,
            store_phone=store_phone,
            store_url=store_url,
            whatsapp=whatsapp,
            product_name=product_name,
            category=category or "Herbal Products",
            brand=brand or store_name,
            use_case=use_case,
            user_description=user_description or f"Premium herbal {product_name}",
            focus_keyword=focus_kw,
            word_min=TARGET_WORD_MIN,
            word_max=TARGET_WORD_MAX,
            density_min=TARGET_DENSITY_MIN,
            density_max=TARGET_DENSITY_MAX,
            seo_title_max=SEO_TITLE_MAX,
            meta_desc_max=META_DESC_MAX,
            home_url=_page_url("home"),
            shop_url=_page_url("shop"),
            herbs_url=_page_url("herbs"),
            contact_url=_page_url("contact"),
            faqs_url=_page_url("faqs"),
            product_url=product_url,
        )
    except KeyError as e:
        return False, f"Template variable missing: {e}", ""

    adapted = adapt_prompt_for(filled, ai_format)
    return True, adapted, focus_kw


def build_blog_prompt(
    blog_title: str,
    blog_topic: str,
    store: Dict[str, Any],
    pages: Dict[str, Dict],
    category: str = "",
    tags: str = "",
    audience: str = "general wellness seekers",
    ai_format: str = "chatgpt",
) -> Tuple[bool, str, str]:
    """
    Build a ready-to-paste AI prompt for a blog post.
    Returns (ok, prompt, focus_keyword)
    """
    if not blog_title or not blog_title.strip():
        return False, "Blog title is required", ""

    blog_title = blog_title.strip()
    focus_kw = _slug_base(blog_title)  # Simplified — user can edit

    # Extract focus keyword suggestions
    focus_kw = _auto_focus_keyword(blog_title, "health")
    # Better: use first 4-5 meaningful words
    words = [w for w in blog_title.split() if len(w) > 3][:4]
    focus_kw = " ".join(words).lower() if words else blog_title.lower()

    def _page_url(key: str) -> str:
        return pages.get(key, {}).get("url", "")

    store_name = store.get("name", "Khan Herbal Stores")
    store_tagline = store.get("tagline", "")
    store_email = store.get("email", "")
    store_url = _page_url("home") or "https://example.com"
    whatsapp_raw = store.get("whatsapp", "") or "923218224219"
    whatsapp = re.sub(r"[^\d]", "", whatsapp_raw) or "923218224219"

    try:
        filled = BLOG_PROMPT_TEMPLATE.format(
            store_name=store_name,
            store_tagline=store_tagline,
            store_email=store_email,
            store_url=store_url,
            whatsapp=whatsapp,
            blog_title=blog_title,
            blog_topic=blog_topic or blog_title,
            audience=audience,
            focus_keyword=focus_kw,
            category=category or "Health Tips",
            tags=tags or "",
            density_min=TARGET_DENSITY_MIN,
            density_max=TARGET_DENSITY_MAX,
            seo_title_max=SEO_TITLE_MAX,
            meta_desc_max=META_DESC_MAX,
            shop_url=_page_url("shop"),
            herbs_url=_page_url("herbs"),
            faqs_url=_page_url("faqs"),
            contact_url=_page_url("contact"),
        )
    except KeyError as e:
        return False, f"Template variable missing: {e}", ""

    adapted = adapt_prompt_for(filled, ai_format)
    return True, adapted, focus_kw


# =============================================================================
# SECTION 6 — RESPONSE PARSER (JSON)
# =============================================================================
def parse_ai_response(raw_text: str) -> Tuple[bool, Optional[Dict], str]:
    """
    Parse AI response into a dict.
    Handles: pure JSON, markdown-fenced JSON, prose-wrapped JSON.
    Returns (ok, dict, error).
    """
    if not raw_text or not raw_text.strip():
        return False, None, "Empty response"

    text = raw_text.strip()

    # Strip markdown code fences
    fence_patterns = [
        r"```json\s*(.+?)\s*```",
        r"```\s*(.+?)\s*```",
    ]
    for pat in fence_patterns:
        m = re.search(pat, text, re.DOTALL | re.IGNORECASE)
        if m:
            text = m.group(1).strip()
            break

    # Find first `{` and last `}`
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return False, None, "No JSON object found in response"

    json_str = text[start:end + 1]

    # Try parsing
    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        # Try to fix common issues
        fixed = _fix_common_json_issues(json_str)
        try:
            data = json.loads(fixed)
        except json.JSONDecodeError as e2:
            return False, None, f"Invalid JSON: {e2}"

    if not isinstance(data, dict):
        return False, None, "JSON root must be an object"

    # Normalize keys (lowercase, strip)
    normalized = {}
    for k, v in data.items():
        key = str(k).lower().strip().replace(" ", "_")
        normalized[key] = v

    return True, normalized, ""


def _fix_common_json_issues(text: str) -> str:
    """Fix common AI-generated JSON mistakes."""
    # Remove trailing commas before } or ]
    text = re.sub(r",\s*}", "}", text)
    text = re.sub(r",\s*]", "]", text)
    # Replace smart quotes
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    text = text.replace("\u2018", "'").replace("\u2019", "'")
    return text


# =============================================================================
# SECTION 7 — RESPONSE VALIDATOR
# =============================================================================
def _strip_html(html: str) -> str:
    return re.sub(r"<[^>]+>", " ", html or "")


def _count_words(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text or ""))


def _count_keyword_occurrences(text: str, keyword: str) -> int:
    if not keyword or not text:
        return 0
    return text.lower().count(keyword.lower())


def _calculate_density(text: str, keyword: str) -> float:
    if not keyword or not text:
        return 0.0
    plain = _strip_html(text)
    total = _count_words(plain)
    if total == 0:
        return 0.0
    count = _count_keyword_occurrences(plain, keyword)
    kw_words = len(keyword.split())
    return round((count * kw_words / total) * 100, 2)


def validate_ai_response(parsed: Dict[str, Any],
                          expected_keyword: str = "") -> Dict[str, Any]:
    """
    Validate the parsed AI response.
    Returns {valid, errors, warnings, checks}
    """
    errors = []
    warnings = []
    checks = {}

    # Check required fields
    required = ["article_html", "seo_title", "meta_description"]
    for field in required:
        if not parsed.get(field):
            errors.append(f"Missing required field: {field}")

    if errors:
        return {"valid": False, "errors": errors,
                "warnings": warnings, "checks": checks}

    # Analyze article
    article = parsed.get("article_html", "")
    plain = _strip_html(article)
    wc = _count_words(plain)
    checks["word_count"] = wc
    if wc < TARGET_WORD_MIN:
        warnings.append(f"Word count {wc} below target {TARGET_WORD_MIN}")
    elif wc > TARGET_WORD_MAX + 300:
        warnings.append(f"Word count {wc} much higher than target {TARGET_WORD_MAX}")
    else:
        checks["word_count_ok"] = True

    # Keyword density
    kw = expected_keyword or parsed.get("focus_keyword", "")
    checks["focus_keyword"] = kw
    if kw:
        density = _calculate_density(plain, kw)
        checks["density"] = density
        if density < TARGET_DENSITY_MIN - 0.3:
            warnings.append(f"Density {density}% below {TARGET_DENSITY_MIN}%")
        elif density > TARGET_DENSITY_MAX + 0.5:
            errors.append(f"Density {density}% exceeds safe zone")
        else:
            checks["density_ok"] = True

        occ = _count_keyword_occurrences(plain, kw)
        checks["keyword_occurrences"] = occ
        if occ > 8:
            warnings.append(f"Keyword {occ} times — may look stuffed")

    # SEO title length
    title = parsed.get("seo_title", "")
    checks["seo_title_length"] = len(title)
    if len(title) > SEO_TITLE_MAX:
        warnings.append(f"SEO title too long ({len(title)} > {SEO_TITLE_MAX})")
    else:
        checks["seo_title_ok"] = True

    # Meta description length
    desc = parsed.get("meta_description", "")
    checks["meta_description_length"] = len(desc)
    if len(desc) < 100:
        warnings.append(f"Meta description short ({len(desc)})")
    elif len(desc) > META_DESC_MAX:
        warnings.append(f"Meta description too long ({len(desc)} > {META_DESC_MAX})")
    else:
        checks["meta_description_ok"] = True

    # Structure checks
    h1_count = len(re.findall(r"<h1[^>]*>", article, re.IGNORECASE))
    h2_count = len(re.findall(r"<h2[^>]*>", article, re.IGNORECASE))
    h3_count = len(re.findall(r"<h3[^>]*>", article, re.IGNORECASE))
    checks["h1_count"] = h1_count
    checks["h2_count"] = h2_count
    checks["h3_count"] = h3_count

    if h1_count != 1:
        warnings.append(f"Expected 1 H1, found {h1_count}")
    if h2_count < 5:
        warnings.append(f"Expected 5+ H2 sections, found {h2_count}")

    # Links check
    link_count = len(re.findall(r"<a\s+[^>]*href=", article, re.IGNORECASE))
    checks["internal_links"] = link_count
    if link_count < 4:
        warnings.append(f"Only {link_count} links — target 4+")

    # WhatsApp check
    if "wa.me" not in article.lower() and "whatsapp" not in article.lower():
        warnings.append("WhatsApp CTA not found in article")

    # Estimate RankMath score
    score = _estimate_rankmath_score(parsed, wc, checks)
    checks["estimated_rm_score"] = score
    if score < 70:
        warnings.append(f"Estimated RankMath score {score}% — improve focus")
    elif score >= TARGET_RM_SCORE:
        checks["score_target_met"] = True

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "checks": checks,
    }


def _estimate_rankmath_score(parsed: Dict[str, Any],
                              word_count: int,
                              checks: Dict[str, Any]) -> int:
    """Estimate RankMath score based on parsed data."""
    score = 0
    kw = (parsed.get("focus_keyword") or "").lower()
    title = (parsed.get("seo_title") or "").lower()
    desc = (parsed.get("meta_description") or "").lower()
    article = parsed.get("article_html", "")
    plain_lower = _strip_html(article).lower()

    if kw and kw in title: score += 10
    if kw and kw in desc: score += 10
    if kw and kw in plain_lower[:600]: score += 10
    if 1.0 <= checks.get("density", 0) <= 1.5: score += 10
    if word_count >= 1000: score += 10
    elif word_count >= 800: score += 6
    if len(title) <= 60: score += 5
    if 140 <= len(desc) <= 160: score += 5
    if kw and kw in plain_lower: score += 5
    if article.count("<a ") >= 5: score += 10
    elif article.count("<a ") >= 1: score += 5
    if 'alt="' in article: score += 3
    if checks.get("h2_count", 0) >= 5: score += 5
    if checks.get("h3_count", 0) >= 3: score += 4
    if "wa.me" in article.lower(): score += 2

    return min(score, 100)


# =============================================================================
# SECTION 8 — IMPORT INTO PRODUCT / POST
# =============================================================================
def inject_into_product(product: Dict[str, Any],
                         parsed: Dict[str, Any]) -> Dict[str, Any]:
    """Merge parsed AI response into a product dict."""
    updated = dict(product)

    # Update article
    if parsed.get("article_html"):
        updated.setdefault("article", {})
        updated["article"]["html"] = parsed["article_html"]
        plain = _strip_html(parsed["article_html"])
        updated["article"]["word_count"] = _count_words(plain)
        kw = parsed.get("focus_keyword") or product.get("keywords", {}).get("focus", "")
        updated["article"]["keyword_density"] = _calculate_density(plain, kw)

    # Update rankmath meta
    updated.setdefault("rankmath", {})
    if parsed.get("seo_title"):
        updated["rankmath"]["meta:rank_math_title"] = parsed["seo_title"]
    if parsed.get("meta_description"):
        updated["rankmath"]["meta:rank_math_description"] = parsed["meta_description"]
    if parsed.get("focus_keyword"):
        updated["rankmath"]["meta:rank_math_focus_keyword"] = parsed["focus_keyword"]
        updated.setdefault("keywords", {})
        updated["keywords"]["focus"] = parsed["focus_keyword"]

    # Update short description
    if parsed.get("short_description"):
        updated["short_description"] = parsed["short_description"]

    return updated


def inject_into_post(post: Dict[str, Any],
                      parsed: Dict[str, Any]) -> Dict[str, Any]:
    """Merge parsed AI response into a blog post dict."""
    updated = dict(post)

    if parsed.get("article_html"):
        updated["content"] = parsed["article_html"]
        plain = _strip_html(parsed["article_html"])
        updated["word_count"] = _count_words(plain)
    if parsed.get("seo_title"):
        updated["seo_title"] = parsed["seo_title"]
    if parsed.get("meta_description"):
        updated["meta_description"] = parsed["meta_description"]
    if parsed.get("focus_keyword"):
        updated["focus_keyword"] = parsed["focus_keyword"]
    if parsed.get("excerpt"):
        updated["excerpt"] = parsed["excerpt"]
    if parsed.get("faq"):
        updated["faq"] = parsed["faq"]

    return updated


# =============================================================================
# SECTION 9 — BATCH OPERATIONS
# =============================================================================
def build_batch_prompts(products: List[str],
                         store: Dict[str, Any],
                         pages: Dict[str, Dict],
                         ai_format: str = "chatgpt") -> Tuple[bool, str]:
    """
    Build a CSV of prompts for many products.
    Columns: index, product_name, focus_keyword, prompt
    Returns (ok, csv_text_or_error).
    """
    import csv as _csv
    import io

    buf = io.StringIO()
    writer = _csv.writer(buf, quoting=_csv.QUOTE_ALL)
    writer.writerow(["index", "product_name", "focus_keyword", "prompt"])

    for i, name in enumerate(products, start=1):
        ok, prompt, focus_kw = build_product_prompt(
            product_name=name, store=store, pages=pages,
            ai_format=ai_format,
        )
        if ok:
            writer.writerow([i, name, focus_kw, prompt])
        else:
            writer.writerow([i, name, "", f"ERROR: {prompt}"])

    return True, buf.getvalue()


def save_prompt_to_file(prompt: str, filename: str) -> Tuple[bool, str]:
    """Save a prompt to workspace/prompts/."""
    safe = re.sub(r"[^\w\-.]", "_", filename)
    if not safe.endswith(".txt"):
        safe += ".txt"
    path = PROMPTS_DIR / safe
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(prompt)
        return True, str(path)
    except Exception as e:
        return False, f"Save failed: {e}"


def list_saved_prompts() -> List[Dict[str, Any]]:
    """List all saved prompts in workspace/prompts/."""
    files = []
    if not PROMPTS_DIR.exists():
        return files
    for p in PROMPTS_DIR.glob("*.txt"):
        try:
            files.append({
                "filename": p.name,
                "size": p.stat().st_size,
                "modified": time.strftime(
                    "%Y-%m-%d %H:%M", time.localtime(p.stat().st_mtime)),
            })
        except Exception:
            continue
    return sorted(files, key=lambda x: x["modified"], reverse=True)


# =============================================================================
# SECTION 10 — STANDALONE TEST
# =============================================================================
if __name__ == "__main__":
    print("ai_prompts.py v1.0 loaded")
    print()

    # Dummy store + pages
    test_store = {
        "name": "Khan Herbal Stores",
        "tagline": "Authentic Herbal Remedies in Pakistan",
        "email": "info@khanherbalstores.com",
        "phone": "+92 300 0000000",
        "whatsapp": "+923218224219",
    }
    test_pages = {
        "home":    {"url": "https://example.com/"},
        "shop":    {"url": "https://example.com/shop/"},
        "herbs":   {"url": "https://example.com/natural-herbs/"},
        "faqs":    {"url": "https://example.com/faqs/"},
        "contact": {"url": "https://example.com/contact-us/"},
    }

    # Test product prompt
    print("=== Product Prompt Test ===")
    ok, prompt, focus_kw = build_product_prompt(
        product_name="Almond Oil",
        store=test_store,
        pages=test_pages,
        category="Herbal Oils",
        brand="Khan Herbal Stores",
        use_case="hair",
        user_description="Cold-pressed almond oil for hair and skin care",
        ai_format="chatgpt",
    )
    if ok:
        print(f"  ✅ Prompt built ({len(prompt)} chars)")
        print(f"  Focus keyword: {focus_kw}")
        print(f"  First 200 chars:\n{prompt[:200]}...")
    else:
        print(f"  ❌ {prompt}")

    # Test blog prompt
    print("\n=== Blog Prompt Test ===")
    ok2, blog_prompt, blog_kw = build_blog_prompt(
        blog_title="Top 10 Herbal Remedies for Hair Growth",
        blog_topic="Natural hair growth remedies using traditional herbs",
        store=test_store,
        pages=test_pages,
        category="Hair Care",
        tags="hair, herbs, growth",
        audience="women aged 25-45",
        ai_format="claude",
    )
    if ok2:
        print(f"  ✅ Blog prompt built ({len(blog_prompt)} chars)")
        print(f"  Focus keyword: {blog_kw}")
    else:
        print(f"  ❌ {blog_prompt}")

    # Test parser with sample JSON
    print("\n=== Parser Test ===")
    sample_json = '''```json
{
  "article_html": "<h1>Almond Oil for Hair</h1><p>Test content...</p>",
  "seo_title": "Almond Oil for Hair — Best Herbal Remedy",
  "meta_description": "Buy Almond Oil for hair care at Khan Herbal Stores. Pure, cold-pressed, fast delivery across Pakistan. Order now with cash on delivery.",
  "focus_keyword": "almond oil for hair",
  "word_count": 1080,
  "keyword_density": 1.25
}
```'''
    pok, parsed, perr = parse_ai_response(sample_json)
    if pok:
        print(f"  ✅ Parsed {len(parsed)} fields")
        print(f"  Title: {parsed.get('seo_title', '')[:50]}")
    else:
        print(f"  ❌ {perr}")

    # Test validator
    if pok:
        print("\n=== Validator Test ===")
        val = validate_ai_response(parsed, "almond oil for hair")
        print(f"  Valid:    {val['valid']}")
        print(f"  Errors:   {val['errors']}")
        print(f"  Warnings: {val['warnings'][:3]}")
        print(f"  Estimated RM: {val['checks'].get('estimated_rm_score', 0)}%")

    # Test batch
    print("\n=== Batch Prompt Test (3 products) ===")
    okb, batch_csv = build_batch_prompts(
        products=["Almond Oil", "Black Seed Oil", "Olive Oil"],
        store=test_store, pages=test_pages, ai_format="chatgpt",
    )
    if okb:
        print(f"  ✅ Batch CSV generated ({len(batch_csv)} chars)")
        print(f"  Lines: {len(batch_csv.splitlines())}")

    print("\n✅ All tests complete")