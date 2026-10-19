# 🌿 Khan Herbal Stores — Web Factory v3.1

> **Complete product factory for herbal e-commerce.**
> Generate 325 products + blog posts with SEO articles, RankMath metadata,
> internal linking, WebP images, taxonomy management, AI prompts, and Open Graph —
> all from one local web app.

[![Version](https://img.shields.io/badge/version-3.1.0-green.svg)](#)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/flask-3.0+-red.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/license-Commercial-orange.svg)](#-license)

---

## 📖 Table of Contents

1. [Overview](#-overview)
2. [Key Features](#-key-features)
3. [What's New in v3.1](#-whats-new-in-v31)
4. [Project Structure](#-project-structure)
5. [Requirements](#-requirements)
6. [Installation](#-installation)
   - [Windows 10/11](#option-1-windows-1011)
   - [macOS](#option-2-macos)
   - [Linux (Ubuntu/Debian)](#option-3-linux-ubuntudebian)
   - [From GitHub Clone](#option-4-from-github-clone)
7. [Configuration](#-configuration)
   - [WordPress Application Password](#-wordpress-application-password)
   - [WooCommerce API Keys](#-woocommerce-api-keys)
   - [RankMath Setup](#-rankmath-setup)
8. [Running the App](#-running-the-app)
9. [Tabs Guide](#-tabs-guide)
10. [Workflows](#-workflows)
11. [Store Settings](#-store-settings)
12. [Product Editor](#-product-editor)
13. [Blog Post Editor](#-blog-post-editor)
14. [Taxonomy Manager](#-taxonomy-manager)
15. [Open Graph Manager](#-open-graph-manager)
16. [AI Prompt Generator](#-ai-prompt-generator)
17. [Credential Persistence](#-credential-persistence)
18. [Image Pipeline](#-image-pipeline)
19. [API Reference](#-api-reference)
20. [Troubleshooting](#-troubleshooting)
21. [FAQ](#-faq)
22. [License](#-license)
23. [Support](#-support)

---

## 🎯 Overview

**Khan Herbal Stores — Web Factory** is a **single-machine web application** that
automates the complete content workflow for WooCommerce + WordPress herbal
stores. Built with **Flask + Vanilla JS + Pillow + keyring** — no Node.js,
no React, no build process.

Runs locally on **Windows, macOS, and Linux**, accessible from any device on the
same WiFi network. Everything runs offline — no external AI API required (optional).

### What It Does

- **Generates 325 products** with SEO articles, RankMath metadata, and internal links
- **Creates blog posts** (1500+ words) with proper structure and CTAs
- **Edits live products/posts** — full field control (price, stock, categories, tags, attributes, images)
- **Manages taxonomy** — categories, brands, tags, attributes on live site
- **Generates AI prompts** for ChatGPT / Claude / Gemini / Groq / Ollama
- **Builds Open Graph images** automatically with 5 styles + responsive preview
- **Pushes products & images** to live WordPress/WooCommerce via REST API
- **Saves credentials securely** with Windows Credential Manager (auto-reconnect on reload)

---

## ✨ Key Features

### Content Generation
| Feature | Description |
|---------|-------------|
| 🏭 **325 Products Bulk** | Generate from a text list — SKU, slug, price, stock |
| 📝 **1000+ Word Articles** | SEO-optimized, 87% RankMath score |
| 📰 **Blog Post Generator** | 1500+ words, proper structure, 82% RankMath |
| 🎯 **Focus Keyword** | Auto-generated per product/post, editable |
| 🔒 **Duplicate Prevention** | N-gram Jaccard similarity check |
| 🔗 **Internal Linking** | 17 pages + 4 related products per article |

### Content Management
| Feature | Description |
|---------|-------------|
| ✏️ **Product Editor** | Full field control (price, stock, categories, tags, attributes, images) |
| 📰 **Post Editor** | Full field control (title, content, categories, tags, featured image, status) |
| 🏷️ **Taxonomy Manager** | Categories, brands, tags, attributes CRUD |
| 🔄 **Live Updates** | Edit existing products/posts without leaving the app |
| 👁️ **Diff Preview** | See changes before saving |

### Media & SEO
| Feature | Description |
|---------|-------------|
| 🖼️ **Image Studio** | Drag-drop, URL paste, WebP conversion |
| 🎨 **Custom Image Sizes** | Any width × height, aspect ratio, object-fit |
| 📱 **Open Graph Manager** | Global + per-product OG, 5 image styles, responsive preview |
| 📊 **RankMath 87%** | Automated metadata generation |
| 🎯 **Keyword Density** | 1.0–1.5% safe zone |

### AI & Automation
| Feature | Description |
|---------|-------------|
| 🤖 **AI Prompt Generator** | Multi-AI support (ChatGPT, Claude, Gemini, Groq, Ollama) |
| 📋 **Batch Prompts** | Generate prompts for 325 products at once |
| ✅ **Response Validator** | Check AI-generated JSON before import |

### Infrastructure
| Feature | Description |
|---------|-------------|
| 🔑 **Credential Persistence** | Windows Credential Manager (auto-reconnect) |
| 🌙 **Dark / Light Mode** | Toggle with persistence |
| 📱 **Mobile Responsive** | Full UI on phone, tablet, desktop |
| 💾 **Config Export/Import** | Sale-ready deployment |
| 🔐 **Server-Side Sessions** | Credentials in RAM only |
| 🚀 **REST API Push** | WP Media + WC Product endpoints |

---

## 🆕 What's New in v3.1

### Product Editor (Full Form)
- **All fields editable**: price, sale price, stock, manage stock, status
- **Categories chips** with autocomplete (type + Enter to add)
- **Tags chips** with autocomplete
- **Brand chips** with autocomplete
- **Attributes** — comma-separated values
- **Featured image** upload + remove
- **Gallery images** upload + remove
- **Focus keyword** field

### Post Editor (Full Form)
- **Title, slug, status, excerpt** editable
- **Categories chips** (WP categories)
- **Tags chips** (WP tags)
- **Featured image** upload + remove
- **Focus keyword** field
- **Content HTML** editor

### Taxonomy Manager Fixes
- **Edit modal** — now opens with current values (was a stub)
- **Create/Update** — both work via the same modal
- **Keyword bug fixed** — `tax_type` → `taxonomy_type`

### UX Improvements
- **Loading overlay** — dark spinner for all save/load operations
- **Edit buttons** — Tab 9 (Blog Posts) and Tab 10 (Live Products) auto-switch to Editor tab
- **Responsive OG preview** — fluid layout for all screen sizes

### Security
- **Credential Persistence** — Windows Credential Manager (encrypted at OS level)
- **Auto-reconnect** — credentials restore on page reload (opt-out available)
- **Forget button** — clear saved credentials anytime

---

## 📁 Project Structure

```
herbal-master-factory/
│
├── app_web.py                 # Main Flask app (~4000 lines)
├── engine.py                  # Content + SEO + RankMath engine (~1400 lines)
├── media.py                   # Image processing + WP media push (~700 lines)
├── wp_client.py               # Live WP posts + WC products API (~620 lines)
├── taxonomy.py                # Categories, brands, tags, attributes (~800 lines)
├── open_graph.py              # OG manager + image generator (~500 lines)
├── ai_prompts.py              # AI prompt templates + validators (~700 lines)
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

**Total: 7 core files + 3 auxiliary files** — kept minimal for easy deployment.

---

## 🖥️ Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **OS** | Windows 10 / macOS 11 / Ubuntu 20.04 | Windows 11 / macOS 14 / Ubuntu 22.04 |
| **Python** | 3.10+ | 3.11 / 3.12 / 3.13 |
| **RAM** | 4 GB | 8 GB |
| **Disk** | 500 MB | 2 GB |
| **Browser** | Chrome / Edge / Firefox / Safari | Chrome |
| **WordPress** | 5.6+ with REST API | 6.4+ |
| **WooCommerce** | 4.0+ | 8.0+ |
| **RankMath** | Free or Pro | Pro |

### Dependencies

```
Flask>=3.0.0
requests>=2.31.0
Pillow>=10.0.0
Jinja2>=3.1.2
pandas>=2.0.0
python-slugify>=8.0.0
beautifulsoup4>=4.12.0
lxml>=5.0.0
keyring>=24.0.0
```

---

## 🛠️ Installation

### Option 1: Windows 10/11

**Step 1 — Prerequisites**

- Install [Python 3.10+](https://www.python.org/downloads/)
  - ✅ **Important:** During install, tick **"Add Python to PATH"**

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

If you see execution policy error:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force
.\.venv\Scripts\Activate.ps1
```

**You should see** `(.venv)` prefix in PowerShell prompt.

**Step 5 — Install Dependencies**

```powershell
pip install -r requirements_web.txt
```

**Step 6 — Run Application**

```powershell
python app_web.py
```

**Step 7 — Open Browser**

Go to: **http://127.0.0.1:5000**

---

### Option 2: macOS

**Step 1 — Prerequisites**

Install Homebrew (if not installed):

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Install Python:

```bash
brew install python@3.11
```

**Step 2 — Navigate to Folder**

```bash
cd ~/Desktop/herbal-master-factory
```

**Step 3 — Create Virtual Environment** *(first time only)*

```bash
python3 -m venv .venv
```

**Step 4 — Activate Virtual Environment**

```bash
source .venv/bin/activate
```

**You should see** `(.venv)` prefix in terminal prompt.

**Step 5 — Install Dependencies**

```bash
pip install -r requirements_web.txt
```

**Step 6 — Run Application**

```bash
python app_web.py
```

**Step 7 — Open Browser**

Go to: **http://127.0.0.1:5000**

> **Note:** Keyring backend on macOS uses macOS Keychain (encrypted).

---

### Option 3: Linux (Ubuntu/Debian)

**Step 1 — Prerequisites**

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv libsecret-1-dev
```

**Step 2 — Navigate to Folder**

```bash
cd ~/Desktop/herbal-master-factory
```

**Step 3 — Create Virtual Environment** *(first time only)*

```bash
python3 -m venv .venv
```

**Step 4 — Activate Virtual Environment**

```bash
source .venv/bin/activate
```

**Step 5 — Install Dependencies**

```bash
pip install -r requirements_web.txt
```

**Step 6 — Run Application**

```bash
python app_web.py
```

**Step 7 — Open Browser**

Go to: **http://127.0.0.1:5000**

> **Note:** Keyring on Linux uses Secret Service (GNOME Keyring / KWallet).
> If unavailable, credentials will stay in-memory only (feature gracefully degrades).

---

### Option 4: From GitHub Clone

**Step 1 — Prerequisites**

- Install [Git](https://git-scm.com/downloads)
- Install Python 3.10+ (per OS above)

**Step 2 — Clone Repository**

```bash
cd ~/Desktop     # or "cd %USERPROFILE%\Desktop" on Windows
git clone https://github.com/YOUR_USERNAME/herbal-master-factory.git
cd herbal-master-factory
```

**Step 3 — Create Virtual Environment**

**Windows:**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Step 4 — Install Dependencies**

```bash
pip install -r requirements_web.txt
```

**Step 5 — Run Application**

```bash
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

**Windows:**
```powershell
cd "C:\Users\YOUR_USERNAME\OneDrive\Desktop\herbal-master-factory"
.\.venv\Scripts\Activate.ps1
python app_web.py
```

**macOS/Linux:**
```bash
cd ~/Desktop/herbal-master-factory
source .venv/bin/activate
python app_web.py
```

### Expected Output

```
======================================================================
  🌿 Khan Herbal Stores — Web Factory  v3.1.0
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

Press **`Ctrl+C`** in the terminal.

### Change Port

**Windows:**
```powershell
$env:PORT=8080
python app_web.py
```

**macOS/Linux:**
```bash
PORT=8080 python app_web.py
```

---

## 📑 Tabs Guide

The app has **15 tabs**, each focused on a specific task.

| # | Tab | Purpose |
|---|-----|---------|
| 1 | 🔌 **Connections** | WP + WC API credentials & persistence |
| 2 | ⚙️ **Store Settings** | Store name, contact, address, social media |
| 3 | 🏭 **Product Factory** | Load/generate products bulk |
| 4 | 🖼️ **Image Studio** | Drag-drop images, WebP conversion, slots |
| 5 | 📝 **Content Engine** | Article + SEO + keyword preview |
| 6 | 🤖 **AI Prompts** | Generate prompts for ChatGPT/Claude/Gemini |
| 7 | 🏷️ **Taxonomy Manager** | Categories, brands, tags, attributes CRUD |
| 8 | 📱 **Open Graph** | OG meta settings + image generator |
| 9 | 📰 **Blog Posts** | CRUD blog posts on live WP |
| 10 | 📦 **Live Products** | CRUD products on live WC |
| 11 | ✏️ **Universal Editor** | Full product/post editing with all fields |
| 12 | 📤 **Export** | CSV download, WP/WC API push |
| 13 | 🧪 **Test Lab** | Publish drafts for cart testing |
| 14 | ℹ️ **About** | Version, features, license |
| 15 | 📜 **Log** | Activity log with timestamps |

---

## 🔄 Workflows

### Workflow 1: Generate New Products

1. **🔌 Connections** → Connect WP + WC
2. **🏭 Product Factory** → Load list → **⚡ Generate All**
3. **🖼️ Image Studio** → Assign 5 images per product
4. **📤 Export** → Push Images → Push Products
5. **🧪 Test Lab** → Publish for testing

### Workflow 2: Edit Existing Product

1. **📦 Live Products** → **🔄 Load Products**
2. Click **✏️ Edit** on any product
3. Auto-switches to **✏️ Universal Editor**
4. Edit fields:
   - Name, SKU, Status
   - Regular Price, Sale Price, Stock
   - Stock Status, Manage Stock
   - Short + Full Description
   - **Focus Keyword**
   - **Categories** (chips + autocomplete)
   - **Tags** (chips + autocomplete)
   - **Brand** (chips + autocomplete)
   - **Attributes** (comma-separated)
   - **Featured Image** (upload/change/remove)
   - **Gallery Images**
5. Click **👁️ Preview** to see diff
6. Click **💾 Save Changes**

### Workflow 3: Edit Existing Post

1. **📰 Blog Posts** → **🔄 Load Posts**
2. Click **✏️ Edit** on any post
3. Auto-switches to **✏️ Universal Editor**
4. Edit fields:
   - Title, Slug, Status
   - Excerpt
   - **Focus Keyword**
   - Content (HTML)
   - **Categories** (chips + autocomplete)
   - **Tags** (chips + autocomplete)
   - **Featured Image**
5. Click **💾 Save Changes**

### Workflow 4: Create New Blog Post

1. **📰 Blog Posts** → **➕ New Post**
2. Fill in:
   - Title
   - Focus Keyword
   - Category
   - Tags
3. Click **✅ Generate & Save Draft**
4. Engine generates 1500+ word article with RankMath metadata
5. Post saved as **draft** on live WP

### Workflow 5: AI Prompt Generation

1. **🤖 AI Prompts** tab
2. Select **📦 Product Prompt** or **📰 Blog Prompt**
3. Fill in product/blog details
4. Select **AI Format** (ChatGPT/Claude/Gemini/Groq/Ollama)
5. Click **🎯 Generate Prompt**
6. **📋 Copy to Clipboard**
7. Paste into AI tool
8. Copy JSON response
9. Paste into **Step 3** box
10. Click **🔍 Validate JSON**
11. If valid → **📥 Import to Product**

### Workflow 6: Taxonomy Management

1. **🏷️ Taxonomy Manager** tab
2. Select sub-tab (WC Categories / WP Categories / Brands / Tags / Attributes)
3. **🔍 Search** or scroll through list
4. **➕ Create New** → fill name/slug → Create
5. **✏️ Edit** → modal opens with current values → change → Save
6. **🗑️ Delete** → confirmation → Delete

---

## ⚙️ Store Settings

Every product/article includes:

1. **Store footer** — Address, phone, email, hours
2. **Brand CTA block** — "Buy X from Khan Herbal Stores" + WhatsApp button
3. **Home page link** — Anchor text = store name
4. **Contact page link**

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

---

## ✏️ Product Editor

### Access
- **Tab 11** → Content Type: **Product** → Load List → Select Product

### Fields

| Field | Type | Notes |
|-------|------|-------|
| Name | Text | Product title |
| SKU | Text | Unique identifier |
| Status | Select | Draft / Publish / Pending / Private |
| Regular Price | Number | In Rs |
| Sale Price | Number | Optional |
| Stock Quantity | Number | Numeric |
| Stock Status | Select | In Stock / Out of Stock / On Backorder |
| Manage Stock | Checkbox | Enable stock tracking |
| Short Description | Textarea | For catalog listing |
| Full Description | Textarea | HTML supported |
| **Focus Keyword** | Text | For RankMath |
| **Categories** | Chips | Type + Enter to add, × to remove |
| **Tags** | Chips | Type + Enter to add |
| **Brand** | Chips | Type + Enter to add |
| **Attributes** | Dynamic | Comma-separated values |
| Featured Image | Image picker | Upload/change/remove |
| Gallery Images | Multi-image | Add/remove |
| Meta Title | Text | Max 60 chars |
| Meta Description | Textarea | Max 160 chars |

### Actions
- **👁️ Preview** — See changes before saving
- **💾 Save Changes** — Apply updates
- **🗑️ Delete** — Permanently remove

---

## 📰 Blog Post Editor

### Access
- **Tab 11** → Content Type: **Blog Post** → Load List → Select Post

### Fields

| Field | Type | Notes |
|-------|------|-------|
| Title | Text | Post title |
| Status | Select | Draft / Publish / Pending / Private |
| Slug | Text | URL slug |
| Excerpt | Textarea | Short summary |
| **Focus Keyword** | Text | For RankMath |
| Content | Textarea | HTML |
| **Categories** | Chips | WP categories |
| **Tags** | Chips | WP tags |
| Featured Image | Image picker | Upload/change/remove |
| Meta Title | Text | (Auto-generated) |
| Meta Description | Textarea | (Auto-generated) |

### Actions
- **👁️ Preview** — See changes
- **💾 Save Changes** — Apply
- **🗑️ Delete** — Remove permanently

---

## 🏷️ Taxonomy Manager

### Access
- **Tab 7** → Select sub-tab

### Sub-Tabs

| Sub-Tab | Manages |
|---------|---------|
| 📂 WC Categories | Product categories (product_cat) |
| 📂 WP Categories | Blog post categories |
| 🏷️ Brands | Product brands (auto-detects method) |
| 🔖 Product Tags | WC product tags |
| 🔖 Post Tags | WP blog post tags |
| ⚙️ Attributes | Global WC attributes + terms |

### Actions

| Action | How |
|--------|-----|
| **Create** | ➕ Create New → fill fields → Create |
| **Edit** | ✏️ Edit → modal opens with current values → change → Save |
| **Delete** | 🗑️ Delete → confirmation → Delete |
| **Search** | Type in search box → live filter |
| **Refresh** | 🔄 Refresh → re-fetch from live site |

---

## 📱 Open Graph Manager

### Access
- **Tab 8** → 3 sub-tabs

### Global Settings
- Site Name, OG Title, OG Description, OG Image URL
- OG Type, OG Locale
- Twitter Card Type, Twitter @Site, Facebook App ID

### Per-Product OG
- Select product from dropdown
- Override global OG for that product
- **Live preview** updates as you type
- **Save** persists to session
- **Reset** returns to auto-filled values

### Image Generator
- Select product
- Choose style: **Modern / Minimal / Bold / Gradient / Photo**
- Click **🎨 Generate**
- Image shows in:
  - Panel box
  - **Live Preview** (bottom of page)
- Image is **1200×630**, WebP format, ~20-30 KB

### Live Preview (Responsive)
- **Aspect ratio 1.91:1** (matches Facebook/WhatsApp)
- **Fluid fonts** (`clamp()`) for all screen sizes
- **Text never cut** on mobile/tablet/desktop
- **Ellipsis** for long URLs
- **Auto error handling** — red box if image fails to load

### Test Responsive
- **F12** → **`Ctrl+Shift+M`** → test at 375px, 768px, 1440px, 2560px

---

## 🤖 AI Prompt Generator

### Access
- **Tab 6**

### Supported AI Formats

| Format | Best For |
|--------|----------|
| **ChatGPT** | GPT-3.5 / GPT-4 / GPT-4o |
| **Claude** | Claude Sonnet / Opus |
| **Gemini** | Google Gemini Pro |
| **Groq** | Fast inference models |
| **Ollama** | Local models (Llama, Mistral) |

### Workflow

1. Fill in product/blog details
2. Select AI format
3. Click **🎯 Generate Prompt**
4. **📋 Copy to Clipboard** or **⬇️ Download as .txt**
5. Paste into AI tool
6. Copy JSON response
7. Paste into **Step 3** box
8. Click **🔍 Validate JSON**
9. If valid → **📥 Import to Product**

### Validation Checks
- JSON validity
- Word count (1000-1200 products, 1500-2000 blogs)
- Keyword density (1.0-1.5%)
- Focus keyword occurrences
- Structure (H1/H2/H3)
- Internal links count
- WhatsApp CTA presence
- Estimated RankMath score

---

## 🔑 Credential Persistence

### Access
- **Tab 1 (Connections)** → top **🔑 Credential Persistence** card

### How It Works

When you connect WP + WC:
1. Credentials saved to **OS-native encrypted vault**:
   - **Windows** → Windows Credential Manager
   - **macOS** → macOS Keychain
   - **Linux** → Secret Service (GNOME Keyring / KWallet)
2. On app reload (`F5`), credentials auto-restore
3. Auto-connect happens in background

### UI Controls

| Control | Action |
|---------|--------|
| ☑️ **Remember credentials** | Enable/disable auto-save |
| **🔄 Refresh Status** | Check if saved credentials exist |
| **🗑️ Forget Saved Credentials** | Clear from OS vault |

### Banner Status

- ℹ️ **"No saved credentials"** — nothing saved yet
- ✅ **"Saved credentials found"** — auto-restore will run
- ⚠️ **"keyring not installed"** — install `keyring` package

### Verify OS Storage

**Windows:**
```powershell
cmdkey /list | findstr "khan-herbal-factory"
```

**macOS:**
```bash
security find-generic-password -s "khan-herbal-factory"
```

**Linux:**
```bash
secret-tool search service "khan-herbal-factory"
```

### Opt-Out

- Uncheck **Remember credentials** → clears saved credentials on next reload
- Or click **🗑️ Forget Saved Credentials** anytime

### Security

| Concern | How Handled |
|---------|-------------|
| **Encryption** | OS-level (Windows DPAPI, macOS Keychain, Linux Secret Service) |
| **Access** | Only your user account can decrypt |
| **Network** | Credentials never leave your PC |
| **Session** | Browser JS never sees password (server-side session) |
| **Clear** | Forget button wipes from OS vault |

---

## 🖼️ Image Pipeline

### Image Studio (Tab 4)

| Method | How |
|--------|-----|
| **Drag-drop** | Drag from browser or desktop |
| **File browse** | Click drop zone |
| **Ctrl+V paste** | Copy image from browser |
| **URL paste** | Direct image URL |

### Processing
1. Aspect ratio crop (center)
2. Resize with LANCZOS (high quality)
3. WebP conversion (quality 82, method 6)

### Custom Sizes
- 300×300, 600×600, 800×800, 1200×630, 1200×1200
- **Custom** → any width × height

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

### Credential Persistence

| Method | Route | Purpose |
|--------|-------|---------|
| GET | `/api/credentials/status` | Check saved credentials |
| POST | `/api/credentials/restore` | Restore + auto-connect |
| POST | `/api/credentials/clear` | Wipe from OS vault |

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
| GET | `/api/products/list` | List products |
| POST | `/api/products/generate` | Generate all |

### Editor Endpoints

| Method | Route | Purpose |
|--------|-------|---------|
| POST | `/api/editor/load` | Fetch item + taxonomy |
| POST | `/api/editor/save-product` | Save product (all fields) |
| POST | `/api/editor/save-post` | Save post (all fields) |
| POST | `/api/media/upload` | Upload image to WP |
| GET | `/api/media/<id>` | Get media URL |

### Taxonomy Endpoints

| Method | Route | Purpose |
|--------|-------|---------|
| POST | `/api/taxonomy/list` | List taxonomy |
| POST | `/api/taxonomy/create` | Create new |
| POST | `/api/taxonomy/update` | Update existing |
| POST | `/api/taxonomy/delete` | Delete |

### Open Graph Endpoints

| Method | Route | Purpose |
|--------|-------|---------|
| GET | `/api/og/get` | Get global OG |
| POST | `/api/og/save` | Save global OG |
| POST | `/api/og/product-get` | Load product OG |
| POST | `/api/og/product-save` | Save product OG |
| POST | `/api/og/product-reset` | Reset product OG |
| POST | `/api/og/generate-image` | Generate OG image |

### Blog Endpoints

| Method | Route | Purpose |
|--------|-------|---------|
| POST | `/api/blog/list` | List posts |
| POST | `/api/blog/create` | Create post |
| POST | `/api/blog/delete` | Delete post |

### Live Product Endpoints

| Method | Route | Purpose |
|--------|-------|---------|
| POST | `/api/live/list` | List live products |
| POST | `/api/live/get` | Get single product |
| POST | `/api/live/update` | Update product |
| POST | `/api/live/delete` | Delete product |

### AI Prompt Endpoints

| Method | Route | Purpose |
|--------|-------|---------|
| POST | `/api/prompts/product` | Generate product prompt |
| POST | `/api/prompts/blog` | Generate blog prompt |
| POST | `/api/prompts/validate` | Validate JSON |
| POST | `/api/prompts/import` | Import response |

### Export & Push

| Method | Route | Purpose |
|--------|-------|---------|
| POST | `/api/export/csv` | Generate CSV |
| GET | `/api/export/archive-css` | Get archive CSS |
| POST | `/api/push/wp` | Push images to WP |
| POST | `/api/push/wc` | Push products to WC |

### Log

| Method | Route | Purpose |
|--------|-------|---------|
| GET | `/api/log` | Get activity log |
| POST | `/api/log/clear` | Clear log |

---

## 🐛 Troubleshooting

### App Won't Start

| Error | Cause | Fix |
|-------|-------|-----|
| `ModuleNotFoundError: flask` | Flask not installed | `pip install -r requirements_web.txt` |
| `.\.venv\Scripts\Activate.ps1 not recognized` | Venv missing | `python -m venv .venv` |
| `Execution Policy` (Windows) | PowerShell restriction | `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force` |
| `permission denied` (macOS/Linux) | Script not executable | `chmod +x` or use `python3` |
| `port already in use` | Port 5000 busy | `$env:PORT=8080; python app_web.py` (Windows) or `PORT=8080 python app_web.py` (macOS/Linux) |

### Pylance "Import could not be resolved"

**Cause:** VS Code not using venv interpreter.

**Fix:**
1. `Ctrl+Shift+P` → `Python: Select Interpreter`
2. Select `.venv` one
3. `Ctrl+Shift+P` → `Developer: Reload Window`

### Connection Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| **401 Unauthorized** | Wrong password | Regenerate WP Application Password |
| **403 Forbidden** | User lacks permission | Ensure Administrator role |
| **404 Not Found** | REST API disabled | Enable in WP → Settings → Permalinks |
| **SSL Error** | Cert issue | Verify HTTPS in browser |
| **Timeout** | Slow host | Check network |

### Taxonomy Create Fails

| Error | Cause | Fix |
|-------|-------|-----|
| `unexpected keyword argument 'tax_type'` | Old bug | Fixed in v3.1 — verify patch applied |
| `403 Forbidden` | User not admin | Ensure WC user is Administrator |

### Editor Load Fails

| Error | Cause | Fix |
|---------|-------|-----|
| `Connect WC first` | Not connected | Tab 1 → Connect |
| `Product not found` | Invalid ID | Reload Live Products list |
| `keyring not installed` | Missing package | `pip install keyring` |

### Credential Persistence

| Symptom | Cause | Fix |
|---------|-------|-----|
| **"keyring not installed"** | Package missing | `pip install keyring` |
| **Auto-restore doesn't work** | Remember unchecked | Check "Remember credentials" |
| **Credentials not saved** | Keyring backend unavailable | `python -c "import keyring; print(keyring.get_keyring())"` |
| **Windows: no cmdkey entry** | Save failed | Reconnect WP+WC |

### Image Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| **Drag-drop fails** | Browser CORS | Use **Ctrl+V** paste method |
| **Upload fails** | File too large | Max 50 MB per file |
| **WebP not saving** | Pillow missing | `pip install Pillow` |
| **Images not attaching** | Wrong push order | Push images **before** products |

### OG Preview Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| **Preview blank** | JS error | F12 Console → share error |
| **Image not visible** | CSS issue | Run CSS patch |
| **Text cut off** | Fixed dimensions | Run responsive CSS patch |

---

## ❓ FAQ

**Q: Do I need AI (OpenAI, Claude) for content generation?**
A: No. The engine uses formula-based templates. AI prompts are optional.

**Q: How many products can I generate?**
A: Tested up to 325. Larger lists work but may take longer.

**Q: Does RankMath score really reach 87%?**
A: Yes — verified on demo products. Score may vary ±5%.

**Q: Are my credentials stored on disk?**
A: Only if you enable **Remember credentials**. Stored in **OS-encrypted vault** (Windows Credential Manager / macOS Keychain / Linux Secret Service). Default: **session memory only**.

**Q: Can I run this on Mac or Linux?**
A: Yes — same Python commands (see [Installation](#-installation)).

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

**Q: Where are credentials stored?**
A: Windows Credential Manager (Windows), macOS Keychain (macOS), Secret Service (Linux). All encrypted by OS.

**Q: What if I forget my password?**
A: Regenerate WP Application Password in WP Admin → Users → Profile.

**Q: Can I disable credential persistence?**
A: Yes — uncheck "Remember credentials" in Connections tab.

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
**Version:** 3.1.0
**Last Updated:** 2026-10-19

### Reporting Bugs

Include:
1. **Tab name** where error occurred
2. **Full traceback** from terminal
3. **Steps to reproduce**
4. **OS + Python version** (`python --version`)

### Contact

- **Email:** support@khanherbalstores.com
- **WhatsApp:** +923218224219

---

## 🎯 Quick Reference Card

```
┌────────────────────────────────────────────────────────────────┐
│  WINDOWS                                                        │
│    cd "C:\Users\YOUR_USERNAME\OneDrive\Desktop\herbal-master-factory" │
│    python -m venv .venv                                         │
│    .\.venv\Scripts\Activate.ps1                                 │
│    pip install -r requirements_web.txt                          │
│    python app_web.py                                            │
│                                                                 │
│  macOS                                                          │
│    cd ~/Desktop/herbal-master-factory                           │
│    python3 -m venv .venv                                        │
│    source .venv/bin/activate                                    │
│    pip install -r requirements_web.txt                          │
│    python app_web.py                                            │
│                                                                 │
│  LINUX (Ubuntu/Debian)                                          │
│    sudo apt install python3 python3-pip python3-venv libsecret-1-dev │
│    cd ~/Desktop/herbal-master-factory                           │
│    python3 -m venv .venv                                        │
│    source .venv/bin/activate                                    │
│    pip install -r requirements_web.txt                          │
│    python app_web.py                                            │
│                                                                 │
│  OPEN BROWSER                                                   │
│    http://127.0.0.1:5000                                        │
│                                                                 │
│  PHONE ACCESS (same WiFi)                                       │
│    http://192.168.x.x:5000                                      │
└────────────────────────────────────────────────────────────────┘
```

---

## 🌟 Credits

- **Framework:** Flask + Jinja2
- **Image processing:** Pillow
- **HTTP client:** Requests
- **Slug generation:** python-slugify
- **Credential storage:** keyring
- **UI:** Vanilla JS + Modern CSS

---

**Built with ❤️ for Pakistani herbal store owners.**

*Khan Herbal Stores — Authentic Herbal Remedies in Pakistan*