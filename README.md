# 🌿 Khan Herbal Stores — Web Factory v3.0

> **Complete product factory for herbal e-commerce.**
> Generate 325 products + blog posts with SEO articles, RankMath metadata,
> internal linking, WebP images, taxonomy management, AI prompts, and Open Graph —
> all from one local web app.

[![Version](https://img.shields.io/badge/version-3.0.0-green.svg)](#)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/flask-3.0+-red.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/license-Commercial-orange.svg)](#-license)

---

## 📖 Table of Contents

1. [Overview](#-overview)
2. [Key Features](#-key-features)
3. [Project Structure](#-project-structure)
4. [Requirements](#-requirements)
5. [Installation](#-installation)
   - [From Local Folder](#option-1-from-local-folder)
   - [From GitHub Clone](#option-2-from-github-clone)
6. [Configuration](#-configuration)
   - [WordPress Application Password](#-wordpress-application-password)
   - [WooCommerce API Keys](#-woocommerce-api-keys)
   - [RankMath Setup](#-rankmath-setup)
7. [Running the App](#-running-the-app)
8. [Tabs Guide](#-tabs-guide)
9. [Workflows](#-workflows)
   - [Workflow 1: Generate Products](#workflow-1-generate-products)
   - [Workflow 2: Create Blog Post](#workflow-2-create-blog-post)
   - [Workflow 3: Update Live Content](#workflow-3-update-live-content)
   - [Workflow 4: AI Prompt Generation](#workflow-4-ai-prompt-generation)
10. [Store Settings](#-store-settings)
11. [Taxonomy Manager](#-taxonomy-manager)
12. [Open Graph Manager](#-open-graph-manager)
13. [AI Prompt Generator](#-ai-prompt-generator)
14. [API Reference](#-api-reference)
15. [Troubleshooting](#-troubleshooting)
16. [FAQ](#-faq)
17. [License](#-license)
18. [Support](#-support)

---

## 🎯 Overview

**Khan Herbal Stores — Web Factory v3.0** is a **single-machine web application**
that automates the complete content workflow for WooCommerce + WordPress herbal
stores. Built with **Flask + Vanilla JS + Pillow** — no Node.js, no React, no
build process.

Runs locally on Windows 10/11, accessible from any device on the same WiFi
network. Everything runs offline — no external AI API required (optional).

### What It Does

- **Generates 325 products** with SEO articles, RankMath metadata, and internal links
- **Creates blog posts** (1500+ words) with proper structure and CTAs
- **Manages taxonomy** — categories, brands, tags, attributes on live site
- **Generates AI prompts** for ChatGPT / Claude / Gemini
- **Builds Open Graph images** automatically with 5 styles
- **Pushes products & images** to live WordPress/WooCommerce via REST API
- **Updates existing content** — posts and products

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🏭 **325 Products Bulk** | Generate from a text list — SKU, slug, price, stock |
| 📝 **1000+ Word Articles** | SEO-optimized, 87% RankMath score |
| 📰 **Blog Post Generator** | 1500+ words, proper structure |
| 🤖 **AI Prompt Generator** | Multi-AI support (ChatGPT, Claude, Gemini, Groq, Ollama) |
| 🏷️ **Taxonomy Manager** | Categories, brands, tags, attributes CRUD |
| 📱 **Open Graph Manager** | Global + per-product OG, image generator |
| 📦 **Live Products CRUD** | Fetch, update, delete existing products |
| 📰 **Blog Posts CRUD** | List, create, update, delete posts |
| ✏️ **Universal Editor** | Edit live content with diff preview |
| 🖼️ **Image Studio** | Drag-drop, URL paste, WebP conversion |
| 🎨 **Custom Image Sizes** | Any width × height, aspect ratio, object-fit |
| 🔒 **Duplicate Prevention** | N-gram Jaccard similarity check |
| 🔗 **Internal Linking** | 17 pages + 4 related products per article |
| 🏢 **Store Brand CTA** | Home page link + WhatsApp button |
| 📊 **RankMath 87%** | Automated metadata generation |
| 🎯 **Keyword Density** | 1.0–1.5% safe zone |
| 🌙 **Dark / Light Mode** | Toggle with persistence |
| 📱 **Mobile Responsive** | Full UI on phone, tablet, desktop |
| 💾 **Config Export/Import** | Sale-ready deployment |
| 🔐 **Server-Side Sessions** | Credentials in RAM only |
| 🚀 **REST API Push** | WP Media + WC Product endpoints |

---

## 📁 Project Structure

```
herbal-master-factory/
│
├── app_web.py                 # Main Flask app (single-file, ~4000 lines)
├── engine.py                  # Content + SEO + RankMath engine
├── media.py                   # Image processing + WP media push
├── wp_client.py               # Live WP posts + WC products API
├── taxonomy.py                # Categories, brands, tags, attributes
├── open_graph.py              # OG manager + image generator
├── ai_prompts.py              # AI prompt templates + validators
│
├── requirements_web.txt       # Python dependencies
├── update.ps1                 # Auto-update script (Windows)
├── README.md                  # This file
│
├── workspace/                 # Auto-created at runtime
│   ├── uploads/               # Raw uploaded images
│   ├── images/                # Processed WebP images
│   ├── og_images/             # Generated OG images
│   └── prompts/               # Saved AI prompts
│
└── logs/                      # Activity logs
    └── activity.log
```

**Total: 7 core files + 3 auxiliary** — kept minimal for easy deployment.

---

## 🖥️ Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **OS** | Windows 10 / 11 | Windows 11 |
| **Python** | 3.10+ | 3.11 / 3.13 |
| **RAM** | 4 GB | 8 GB |
| **Disk** | 500 MB | 2 GB |
| **Browser** | Chrome / Edge / Firefox | Chrome |
| **WordPress** | 5.6+ with REST API | 6.4+ |
| **WooCommerce** | 4.0+ | 8.0+ |
| **RankMath** | Free or Pro | Pro |

---

## 🛠️ Installation

### Option 1: From Local Folder

**Step 1 — Prerequisites**

- Install [Python 3.10+](https://www.python.org/downloads/)  
  ✅ **Important:** During install, tick **"Add Python to PATH"**

**Step 2 — Navigate to Folder**

```powershell
cd "C:\Users\YOUR_USERNAME\OneDrive\Desktop\herbal-master-factory"
```

**Step 3 — Create Virtual Environment** *(first time only)*

```powershell
python -m venv .venv
```

**Step 4 — Activate Virtual Environment**

```powershell
.\.venv\Scripts\Activate.ps1
```

**If you see execution policy error:**

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force
.\.venv\Scripts\Activate.ps1
```

**You should see** `(.venv)` prefix in PowerShell prompt.

**Step 5 — Install Dependencies** *(first time only)*

```powershell
pip install -r requirements_web.txt
```

**Step 6 — Run Application**

```powershell
python app_web.py
```

---

### Option 2: From GitHub Clone

**Step 1 — Prerequisites**

- Install [Python 3.10+](https://www.python.org/downloads/) ✅ Add to PATH
- Install [Git for Windows](https://git-scm.com/download/win)

**Step 2 — Clone Repository**

```powershell
cd "C:\Users\YOUR_USERNAME\OneDrive\Desktop"
git clone https://github.com/YOUR_USERNAME/herbal-master-factory.git
cd herbal-master-factory
```

**Step 3 — Create Virtual Environment**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Step 4 — Install Dependencies**

```powershell
pip install -r requirements_web.txt
```

**Step 5 — Run Application**

```powershell
python app_web.py
```

---

## ⚙️ Configuration

### 🔵 WordPress Application Password

**Where to find:**

1. Log in to WordPress Admin → `/wp-admin/`
2. Go to **Users → Profile** (or edit specific user)
3. Scroll to **Application Passwords** section
4. Enter name: `Khan Herbal Factory`
5. Click **Add New Application Password**
6. **Copy the 24-character password** (with spaces) — you won't see it again!

**Requirements:**
- User must have **Administrator** role
- **HTTPS is mandatory** — Application Passwords only work over HTTPS

**Where to paste in app:**
- Tab: **🔌 Connections → WordPress Connection → Application Password**

---

### 🟣 WooCommerce API Keys

**Where to find:**

1. WordPress Admin → **WooCommerce → Settings**
2. Click **Advanced** tab → **REST API**
3. Click **Add key**
4. Fill in:
   - **Description:** `Khan Herbal Factory`
   - **User:** Select an Administrator
   - **Permissions:** **Read/Write**
5. Click **Generate API key**
6. **Copy both:**
   - **Consumer Key** — starts with `ck_...`
   - **Consumer Secret** — starts with `cs_...`

**Where to paste in app:**
- Tab: **🔌 Connections → WooCommerce Connection**

---

### 📊 RankMath Setup

- RankMath **must be installed** on your WordPress site
- No API keys required — metadata is injected via:
  - **CSV import** → `meta:rank_math_*` columns
  - **REST API push** → `meta_data` array

**Verify after import:**
1. WP Admin → **Products → All Products**
2. Click any product → **Edit**
3. Scroll to **RankMath** panel
4. Check **score badge** — should be **85%+**

---

## 🚀 Running the App

### Standard Run

```powershell
cd "C:\Users\YOUR_USERNAME\OneDrive\Desktop\herbal-master-factory"
.\.venv\Scripts\Activate.ps1
python app_web.py
```

### Expected Output

```
======================================================================
  🌿 Khan Herbal Stores — Web Factory  v3.0.0
======================================================================
  Local:    http://127.0.0.1:5000
  Network:  http://192.168.1.5:5000    ← same WiFi
======================================================================
  Store:    Khan Herbal Stores
  Tabs:     15
  Ctrl+C to stop
======================================================================
```

Browser opens automatically. If not, open manually: **http://127.0.0.1:5000**

### Access from Phone

1. Ensure phone is on **same WiFi** as PC
2. Open `http://192.168.1.5:5000` (use your PC's network IP)
3. Full responsive UI will load

### Stop Server

Press **`Ctrl+C`** in the PowerShell window.

### Change Port

```powershell
$env:PORT=8080
python app_web.py
```

---

## 📑 Tabs Guide

The app has **15 tabs**, each focused on a specific task.

| # | Tab | Purpose |
|---|-----|---------|
| 1 | 🔌 **Connections** | WP + WC API credentials & connection status |
| 2 | ⚙️ **Store Settings** | Store name, contact, address, social media |
| 3 | 🏭 **Product Factory** | Load/generate products bulk |
| 4 | 🖼️ **Image Studio** | Drag-drop images, WebP conversion, slots |
| 5 | 📝 **Content Engine** | Article + SEO + keyword preview |
| 6 | 🤖 **AI Prompts** | Generate prompts for ChatGPT/Claude/Gemini |
| 7 | 🏷️ **Taxonomy Manager** | Manage categories, brands, tags, attributes |
| 8 | 📱 **Open Graph** | OG meta settings + image generator |
| 9 | 📰 **Blog Posts** | CRUD blog posts on live WP |
| 10 | 📦 **Live Products** | CRUD products on live WC |
| 11 | ✏️ **Universal Editor** | Edit live content with diff preview |
| 12 | 📤 **Export** | CSV download, WP/WC API push |
| 13 | 🧪 **Test Lab** | Publish drafts for cart testing |
| 14 | ℹ️ **About** | Version, features, license |
| 15 | 📜 **Log** | Activity log with timestamps |

---

## 🔄 Workflows

### Workflow 1: Generate Products

**Step 1 — Connect APIs**

1. Go to **🔌 Connections** tab
2. Enter WP credentials → **🔗 Connect** → Wait for green status
3. Enter WC credentials → **🔗 Connect** → Wait for green status

**Step 2 — Configure Store**

1. Go to **⚙️ Store Settings** tab
2. Update: Store Name, Email, Phone, WhatsApp, Address
3. Click **💾 Save Settings**

**Step 3 — Generate Products**

1. Go to **🏭 Product Factory** tab
2. Load products:
   - **📂 Load File** → Upload `.txt` or `.csv`
   - **Paste** names → **➕ Add to list**
   - **🎲 Demo** → 5 sample products
3. Set price range and stock count
4. Click **⚡ Generate All Products**
5. Verify **RankMath avg: 87%**, **Passing: 100%**

**Step 4 — Assign Images**

1. Go to **🖼️ Image Studio** tab
2. Select product from dropdown
3. Choose slot (1 = Featured, 2-5 = Gallery)
4. Add image via:
   - **Drag-drop** into drop zone
   - **Click** drop zone to browse
   - **Ctrl+V** to paste from clipboard
   - **Paste URL** → click Download
5. Repeat for all 5 slots

**Step 5 — Push to Live Site**

⚠️ **Order matters!**

1. Go to **📤 Export** tab
2. **Step 5A:** Click **🖼️ Push Images to WP**
   - Wait for: `Pushed X products' images (Y files). Failed: 0`
3. **Step 5B:** Click **📦 Push Products to WC**
   - Wait for: `Pushed X products. Failed: 0`
   - Images will **auto-attach**

**Step 6 — Verify**

1. WP Admin → **Products → All Products**
2. Filter by **Drafts**
3. Open product → check:
   - ✅ Featured image + 4 gallery images
   - ✅ RankMath score 85%+
   - ✅ Article body present

**Step 7 — Publish Test Products**

1. Go to **🧪 Test Lab** tab
2. Enter count (default: 5)
3. Click **🚀 Publish Test Products**
4. Visit `https://yoursite.com/shop/` and test add-to-cart

---

### Workflow 2: Create Blog Post

**Step 1 — Open Blog Posts Tab**

1. Click **📰 Blog Posts** tab
2. Click **🔄 Load Posts** → fetch existing posts

**Step 2 — Create New Post**

1. Click **➕ New Post**
2. Fill in:
   - **Title:** `Top 10 Herbal Remedies for Hair Growth`
   - **Focus Keyword:** `herbal remedies for hair`
   - **Category:** `Hair Care`
   - **Tags:** `hair, herbs, growth`
3. Click **✅ Generate & Save Draft**

**Step 3 — What Happens**

- Engine generates 1500+ word article with:
  - Proper H1 + 7 H2 sections
  - Internal links to shop, herbs, contact
  - WhatsApp CTA
  - RankMath metadata
- Post saved as **draft** on live WP
- Check WP Admin → **Posts → Drafts**

**Step 4 — Edit Before Publishing**

1. Option A: WP Admin → **Posts → Edit** manually
2. Option B: **✏️ Universal Editor** tab → Select post → Edit → Preview changes → Publish

---

### Workflow 3: Update Live Content

**Step 1 — Load Live Products**

1. Go to **📦 Live Products** tab
2. Click **🔄 Load Products** → shows all WC products
3. Filter by status (All / Published / Drafts)
4. Search by name or SKU

**Step 2 — Edit Product**

1. Click **✏️** on any product
2. Goes to **✏️ Universal Editor** tab automatically
3. Edit:
   - Title / Name
   - Content (HTML)
   - Meta title / description
4. Click **👁️ Preview Changes** → see diff
5. Click **💾 Publish Changes** → live update

**Step 3 — Delete Product**

1. In Live Products tab, click **🗑️** on product
2. Confirmation modal appears
3. Click **🗑️ Delete** → permanently removed

---

### Workflow 4: AI Prompt Generation

**Step 1 — Fill Product Info**

1. Go to **🤖 AI Prompts** tab
2. Click **📦 Product Prompt**
3. Fill in:
   - **Product Name:** `Almond Oil`
   - **Use Case:** `hair care`
   - **Category:** `Herbal Oils`
   - **Brand:** `Khan Herbal Stores`
   - **Short Description:** `Cold-pressed almond oil for hair`
   - **AI Format:** ChatGPT / Claude / Gemini / Groq / Ollama
4. Click **🎯 Generate Product Prompt**

**Step 2 — Copy Prompt to AI**

1. Prompt appears in Step 2 box (green background)
2. Click **📋 Copy to Clipboard**
3. Or **⬇️ Download as .txt**

**Step 3 — Paste in AI Tool**

1. Open ChatGPT / Claude / Gemini
2. Paste the prompt
3. Wait for JSON response

**Step 4 — Paste Response Back**

1. Copy the JSON from AI
2. Return to app → Step 3 box → paste JSON
3. Click **🔍 Validate JSON**

**Step 5 — Review Validation**

- Word count
- Density
- RankMath estimate
- Structure (H1/H2/H3)
- Internal links

If valid → Click **📥 Import to Product** → data imported.

---

## ⚙️ Store Settings

Every product article automatically includes:

1. **Store footer** — Address, phone, email, hours
2. **Brand CTA block** — "Buy X from Khan Herbal Stores" + WhatsApp button
3. **Home page link** — Anchor text = store name
4. **Contact page link** — "Contact us anytime"

### Configurable Fields

| Field | Default | Used In |
|-------|---------|---------|
| Store Name | Khan Herbal Stores | CTA, footer, schema |
| Tagline | Authentic Herbal Remedies in Pakistan | Meta, footer |
| Email | info@khanherbalstores.com | Footer, schema |
| Phone | +92 300 0000000 | Footer, schema |
| WhatsApp | **+923218224219** | WhatsApp CTA button |
| Address | Main Market, Karachi, Sindh, PK 74000 | Footer, schema |
| Business Hours | Mon-Sat 9:00 AM - 9:00 PM | Footer, schema |

### WhatsApp CTA Behavior

When a customer clicks **💬 Order on WhatsApp**:

```
Opens WhatsApp with pre-filled message:
"Assalam-o-Alaikum! I am interested in Almond Oil.
 Please share more details and pricing.
 Product link: https://yoursite.com/product/almond-oil/"
```

- **Default number:** +923218224219
- **Override:** Update in Store Settings → WhatsApp field → Save

---

## 🏷️ Taxonomy Manager

### Overview

Manage all taxonomies directly from the app. 6 sub-tabs:

| Sub-Tab | What It Manages |
|---------|-----------------|
| 📂 WC Categories | Product categories (product_cat) |
| 📂 WP Categories | Blog post categories |
| 🏷️ Brands | Product brands (auto-detects method) |
| 🔖 Product Tags | WC product tags |
| 🔖 Post Tags | WP blog post tags |
| ⚙️ Attributes | Global WC attributes + terms |

### Operations

**Create:**
1. Click **➕ Create New**
2. Enter Name (slug auto-generated)
3. Optionally set Parent
4. Click **✅ Create**

**Delete:**
1. Click **🗑️** on any row
2. Confirmation modal → shows usage count
3. Click **🗑️ Delete**

**Search:**
- Type in search box → live filter

### Brand Auto-Detection

The app automatically detects which brand system your site uses:

- **Native WC 9.x** → `/wp-json/wc/v3/products/brands`
- **Custom Attribute** → `pa_brand` in attributes
- **3rd-party Plugin** → via Perfect Brands etc.

---

## 📱 Open Graph Manager

### Global Settings

| Field | Purpose |
|-------|---------|
| OG Site Name | Facebook card top |
| OG Title | Fallback title (60 chars max) |
| OG Description | Fallback description (160 chars max) |
| OG Image | Default 1200×630 image |
| OG Type | website / article / product |
| OG Locale | en_PK |
| Twitter Card | summary_large_image |
| Twitter @Site | Your handle |
| Facebook App ID | For FB Insights |

### Image Generator

5 styles available:

- **Modern** — Green background, professional
- **Minimal** — White background, clean
- **Bold** — Dark green, big typography
- **Gradient** — Color gradient
- **Photo** — Blends with product image

Generated at **1200×630**, WebP format, ~20 KB.

### Per-Product OG

Override global OG for specific products:
- Custom OG title
- Custom OG description
- Custom OG image
- Auto-fills from product data

---

## 🤖 AI Prompt Generator

### Supported AI Formats

| Format | Best For |
|--------|----------|
| **ChatGPT** | GPT-3.5 / GPT-4 / GPT-4o |
| **Claude** | Claude Sonnet / Opus |
| **Gemini** | Google Gemini Pro |
| **Groq** | Fast inference models |
| **Ollama** | Local models (Llama, Mistral) |
| **Generic** | Any other AI |

### Prompt Structure

Each prompt includes:
- ✅ Role assignment
- ✅ Product/blog details
- ✅ Strict word count target
- ✅ Focus keyword requirements
- ✅ Heading structure
- ✅ Internal link list
- ✅ CTA + WhatsApp instructions
- ✅ JSON output format
- ✅ Pre-return validation checklist

### Response Validation

The app checks:
- JSON validity
- Word count (1000-1200 for products, 1500-2000 for blogs)
- Keyword density (1.0-1.5%)
- Focus keyword occurrences
- Structure (H1/H2/H3)
- Internal links count
- WhatsApp CTA presence
- Estimated RankMath score

---

## 🔌 API Reference

All routes are **same-origin** — no CORS issues.

### Connection Endpoints

| Method | Route | Purpose |
|--------|-------|---------|
| POST | `/api/connect/wp` | Save WP credentials |
| POST | `/api/test/wp` | Test without saving |
| POST | `/api/disconnect/wp` | Clear WP session |
| POST | `/api/connect/wc` | Save WC credentials |
| POST | `/api/test/wc` | Test without saving |
| POST | `/api/disconnect/wc` | Clear WC session |

### Store Endpoints

| Method | Route | Purpose |
|--------|-------|---------|
| GET | `/api/store/get` | Fetch store settings |
| POST | `/api/store/save` | Save store settings |
| POST | `/api/store/reset` | Reset to defaults |
| GET | `/api/config/export` | Export config JSON |
| POST | `/api/config/import` | Import config |

### Product Endpoints

| Method | Route | Purpose |
|--------|-------|---------|
| POST | `/api/products/load` | Upload file |
| POST | `/api/products/load-text` | Paste text |
| POST | `/api/products/load-demo` | Load demo |
| POST | `/api/products/clear` | Clear session |
| GET | `/api/products/list` | List products |
| POST | `/api/products/generate` | Generate all |

### Image Endpoints

| Method | Route | Purpose |
|--------|-------|---------|
| POST | `/api/images/slots` | Get slot status |
| POST | `/api/images/upload` | Upload image |
| POST | `/api/images/download-url` | Download from URL |
| GET | `/api/images/thumb` | Serve thumbnail |

### AI Prompts Endpoints

| Method | Route | Purpose |
|--------|-------|---------|
| POST | `/api/prompts/product` | Build product prompt |
| POST | `/api/prompts/blog` | Build blog prompt |
| POST | `/api/prompts/validate` | Validate JSON response |
| POST | `/api/prompts/import` | Import AI response |

### Taxonomy Endpoints

| Method | Route | Purpose |
|--------|-------|---------|
| POST | `/api/taxonomy/list` | List taxonomy |
| POST | `/api/taxonomy/create` | Create new |
| POST | `/api/taxonomy/delete` | Delete item |

### Open Graph Endpoints

| Method | Route | Purpose |
|--------|-------|---------|
| GET | `/api/og/get` | Get global OG |
| POST | `/api/og/save` | Save global OG |
| POST | `/api/og/product-auto` | Auto-fill product OG |
| POST | `/api/og/generate-image` | Generate OG image |

### Blog Posts Endpoints

| Method | Route | Purpose |
|--------|-------|---------|
| POST | `/api/blog/list` | List posts |
| POST | `/api/blog/create` | Create new post |
| POST | `/api/blog/delete` | Delete post |

### Live Products Endpoints

| Method | Route | Purpose |
|--------|-------|---------|
| POST | `/api/live/list` | List live products |
| POST | `/api/live/get` | Get single |
| POST | `/api/live/update` | Update |
| POST | `/api/live/delete` | Delete |

### Export & Push

| Method | Route | Purpose |
|--------|-------|---------|
| POST | `/api/export/csv` | Generate CSV |
| GET | `/api/export/archive-css` | Get archive CSS |
| POST | `/api/push/wp` | Push images |
| POST | `/api/push/wc` | Push products |

### Log

| Method | Route | Purpose |
|--------|-------|---------|
| GET | `/api/log` | Get activity log |
| POST | `/api/log/clear` | Clear log |

---

## 🐛 Troubleshooting

### App Won't Start

**Error:** `ModuleNotFoundError: No module named 'flask'`  
**Fix:**
```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements_web.txt
```

**Error:** `.\.venv\Scripts\Activate.ps1 not recognized`  
**Fix:** Venv not created. Run:
```powershell
python -m venv .venv
```

**Error:** `Execution Policy`  
**Fix:**
```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force
```

---

### Pylance "Import could not be resolved" Warnings

**Cause:** VS Code not using venv interpreter.

**Fix:**
1. `Ctrl+Shift+P` → `Python: Select Interpreter`
2. Select `.venv` one
3. `Ctrl+Shift+P` → `Developer: Reload Window`

---

### Connection Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| **401 Unauthorized** | Wrong password | Regenerate WP Application Password |
| **403 Forbidden** | User lacks permission | Ensure Administrator role |
| **404 Not Found** | REST API disabled | Enable in WP → Settings → Permalinks |
| **SSL Error** | Cert issue | Verify HTTPS in browser |
| **Timeout** | Slow host | Check network |

---

### Image Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| **Drag-drop fails** | Browser CORS | Use **Ctrl+V** paste method |
| **Upload fails** | File too large | Max 50 MB per file |
| **WebP not saving** | Pillow missing | `pip install Pillow` |
| **Images not attaching** | Wrong push order | Push images **before** products |

---

### Content Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| **Blog density high** | Old version | Ensure v5.0+ engine.py |
| **Word count low** | Wrong template | Regenerate |

---

## ❓ FAQ

**Q: Do I need AI (OpenAI, Claude) for content generation?**  
A: No. The engine uses formula-based templates. AI prompts are optional
(you can paste them into ChatGPT manually).

**Q: How many products can I generate?**  
A: Tested up to 325. Larger lists work but may take longer.

**Q: Does RankMath score really reach 87%?**  
A: Yes — verified on demo products. Score may vary ±5%.

**Q: Are my credentials stored on disk?**  
A: No. They stay in **server memory only**. Closing the app wipes them.

**Q: Can I run this on Mac or Linux?**  
A: Yes — same Python commands. Only `update.ps1` is Windows-only.

**Q: Why does drag-drop fail sometimes?**  
A: Browser CORS blocks direct image drag. Use **Ctrl+V** paste or **URL paste**.

**Q: Can I use this for non-herbal products?**  
A: Yes — edit `CATEGORIES` and `TAG_RULES` in `engine.py`.

**Q: How do I add more product categories?**  
A: Use the **Taxonomy Manager** tab → WC Categories → Create New.

**Q: What if images don't auto-attach?**  
A: Ensure **Push Images** first, then **Push Products**. Check logs.

**Q: Can I sell this project to clients?**  
A: Yes — Commercial Single-Site license. See License section.

**Q: Does it work without internet?**  
A: Content generation works offline. API push and image download need internet.

**Q: Is my site data sent to any AI?**  
A: No. Everything runs locally. No external API calls for content.

**Q: Can I generate OG images without a product image?**  
A: Yes — the Open Graph tab has a built-in image generator (5 styles).

**Q: How do I create custom brand taxonomies?**  
A: Use the Taxonomy Manager → Brands tab. Auto-detects native/custom method.

---

## 📜 License

**Commercial Single-Site License**

- ✅ Use on **one** production WooCommerce store
- ✅ Modify source code for personal use
- ❌ Redistribute or resell as-is
- ❌ Use on multiple stores without separate license
- ❌ Remove license/copyright notices

For multi-site or white-label licensing, contact **support@khanherbalstores.com**.

---

## 💬 Support

**Documentation:** This README  
**Version:** 3.0.0  
**Last Updated:** 2026-10-16

### Reporting Bugs

Include:
1. **Tab name** where error occurred
2. **Full traceback** from terminal
3. **Steps to reproduce**
4. **Python version** (`python --version`)

### Contact

- **Email:** support@khanherbalstores.com
- **WhatsApp:** +923218224219

---

## 🎯 Quick Reference Card

```
┌───────────────────────────────────────────────────────────────┐
│  INSTALL (first time only)                                    │
│    cd "path/to/herbal-master-factory"                         │
│    python -m venv .venv                                       │
│    .\.venv\Scripts\Activate.ps1                               │
│    pip install -r requirements_web.txt                        │
│                                                               │
│  RUN                                                          │
│    python app_web.py                                          │
│                                                               │
│  TEST MODULES                                                 │
│    python engine.py                                           │
│    python media.py                                            │
│    python taxonomy.py                                         │
│    python open_graph.py                                       │
│    python ai_prompts.py                                       │
│    python wp_client.py                                        │
│                                                               │
│  AUTO-UPDATE                                                  │
│    .\update.ps1                                               │
│                                                               │
│  ROLLBACK                                                     │
│    Copy-Item "engine.py.bak" "engine.py" -Force               │
│    Copy-Item "app_web.py.bak" "app_web.py" -Force             │
└───────────────────────────────────────────────────────────────┘
```

---

## 🌟 Credits

- **Framework:** Flask + Jinja2
- **Image processing:** Pillow
- **HTTP client:** Requests
- **Slug generation:** python-slugify
- **UI:** Vanilla JS + Modern CSS

---

**Built with ❤️ for Pakistani herbal store owners.**

*Khan Herbal Stores — Authentic Herbal Remedies in Pakistan*