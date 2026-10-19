# =============================================================================
# patch_editor_part3_v2.py — Part 3 with EXACT markers
# =============================================================================
# Fixes:
#   - Tax edit: "coming IN next update" (was "coming next update")
#   - Save-post: Uses function start/end range, not full body match
# =============================================================================

import sys
from pathlib import Path

APP_FILE = Path("app_web.py")


# =============================================================================
# NEW POST EDITOR HTML
# =============================================================================
NEW_POST_HTML = '''<div id="editor-post-form" class="hidden">
        <div class="card">
            <h2>📰 <span id="post-edit-title-display">Blog Post</span> <span class="text-muted text-sm" id="post-edit-id-display"></span></h2>
            <div class="form-row"><label>Title</label>
                <input type="text" id="post-edit-title"></div>
            <div class="form-row-2">
                <div class="form-row"><label>Status</label>
                    <select id="post-edit-status">
                        <option value="draft">Draft</option>
                        <option value="publish">Publish</option>
                        <option value="pending">Pending</option>
                        <option value="private">Private</option>
                    </select></div>
                <div class="form-row"><label>Slug</label>
                    <input type="text" id="post-edit-slug" placeholder="auto from title"></div>
            </div>
            <div class="form-row"><label>Excerpt</label>
                <textarea id="post-edit-excerpt" rows="2"></textarea></div>
            <div class="form-row"><label>Focus Keyword</label>
                <input type="text" id="post-edit-focus-kw" placeholder="e.g. herbal remedies for hair"></div>
            <div class="form-row"><label>Content (HTML)</label>
                <textarea id="post-edit-content" rows="12" style="font-family:Consolas,monospace;font-size:12px"></textarea></div>
        </div>

        <div class="card">
            <h2>🏷️ Categories & Tags</h2>
            <div class="form-row">
                <label>Categories</label>
                <div class="chips-container" id="post-edit-categories-chips"></div>
                <input type="text" id="post-edit-categories-input" list="wp-categories-datalist" placeholder="Type + Enter to add category" onkeypress="if(event.key==='Enter'){event.preventDefault();addChipFromInput('categories')}">
                <datalist id="wp-categories-datalist"></datalist>
            </div>
            <div class="form-row">
                <label>Tags</label>
                <div class="chips-container" id="post-edit-tags-chips"></div>
                <input type="text" id="post-edit-tags-input" list="wp-tags-datalist" placeholder="Type + Enter to add tag" onkeypress="if(event.key==='Enter'){event.preventDefault();addChipFromInput('tags')}">
                <datalist id="wp-tags-datalist"></datalist>
            </div>
        </div>

        <div class="card">
            <h2>🖼️ Featured Image</h2>
            <div style="display:flex;gap:12px;align-items:center">
                <div id="post-edit-featured-preview" class="image-thumb">No image</div>
                <div>
                    <button class="btn btn-sm" onclick="changePostFeaturedImage()">📷 Change</button>
                    <button class="btn btn-sm btn-danger" onclick="removePostFeaturedImage()">🗑️ Remove</button>
                    <div class="text-muted text-sm mt-8" id="post-edit-featured-id"></div>
                </div>
            </div>
        </div>

        <div class="card">
            <h2>🔍 SEO / Meta</h2>
            <div class="form-row"><label>Meta Title (max 60)</label>
                <input type="text" id="post-edit-meta-title" maxlength="60"></div>
            <div class="form-row"><label>Meta Description (max 160)</label>
                <textarea id="post-edit-meta-desc" rows="2" maxlength="160"></textarea></div>
        </div>

        <div class="card">
            <div class="btn-row">
                <button class="btn" onclick="previewPostChanges()">👁️ Preview Changes</button>
                <button class="btn btn-primary btn-lg" onclick="savePostChanges()">💾 Save Changes</button>
                <button class="btn btn-danger" onclick="deleteCurrentItem()">🗑️ Delete Post</button>
            </div>
            <div id="post-diff-box" class="hidden mt-16">
                <h3>Changes Preview</h3>
                <pre class="log" id="post-diff-content" style="max-height:400px"></pre>
            </div>
        </div>
    </div>

    '''


# =============================================================================
# TAXONOMY EDIT — EXACT MARKER (with "in")
# =============================================================================
TAX_EDIT_FIND = "function openTaxEditModal(id){ toast('Edit feature — coming in next update', 'info'); }"

TAX_EDIT_REPLACE = '''let _taxEditMode = 'create';
let _taxEditId = null;

function openTaxEditModal(id){
    const item = currentTaxItems.find(x => x.id === id);
    if (!item){ toast('Item not found', 'warning'); return; }
    _taxEditMode = 'edit';
    _taxEditId = id;
    document.getElementById('modal-tax-title').textContent = 'Edit ' + currentTaxType;
    document.getElementById('modal-tax-name').value = item.name || '';
    document.getElementById('modal-tax-slug').value = item.slug || '';
    document.getElementById('modal-tax-description').value = item.description || '';
    document.getElementById('modal-tax-parent').value = item.parent || 0;
    document.getElementById('modal-tax-parent-row').style.display =
        (currentTaxType === 'wc_categories' || currentTaxType === 'wp_categories') ? '' : 'none';
    openModal('modal-tax-create');
}'''


# =============================================================================
# POST HTML — Insert new form replacing old
# =============================================================================
POST_HTML_START = '<div id="editor-post-form" class="hidden">'
POST_HTML_END = '<div id="editor-empty-state">'


# =============================================================================
# JS FUNCTIONS — Exact replacements
# =============================================================================
JS_RENDER_POST_FIND = '''function renderPostEditor(){
    const p = _editorState.item;
    document.getElementById('editor-post-form').classList.remove('hidden');
    document.getElementById('editor-product-form').classList.add('hidden');
    document.getElementById('editor-empty-state').classList.add('hidden');
    document.getElementById('post-edit-title-display').textContent = p.title;
    document.getElementById('post-edit-title').value = p.title || '';
    document.getElementById('post-edit-focus-kw').value = _editorState.focus_keyword || '';
    document.getElementById('post-edit-content').value = p.content || '';
}'''

JS_RENDER_POST_REPLACE = '''function renderPostEditor(){
    const p = _editorState.item;
    document.getElementById('editor-post-form').classList.remove('hidden');
    document.getElementById('editor-product-form').classList.add('hidden');
    document.getElementById('editor-empty-state').classList.add('hidden');
    document.getElementById('post-edit-title-display').textContent = p.title;
    document.getElementById('post-edit-id-display').textContent = `#${p.id}`;
    document.getElementById('post-edit-title').value = p.title || '';
    document.getElementById('post-edit-slug').value = p.slug || '';
    document.getElementById('post-edit-status').value = p.status || 'draft';
    document.getElementById('post-edit-excerpt').value = stripHtml(p.excerpt || '');
    document.getElementById('post-edit-focus-kw').value = _editorState.focus_keyword || '';
    document.getElementById('post-edit-content').value = p.content || '';
    const catOptions = _editorState.options.categories || [];
    _editorState.categories = (p.categories || []).map(id => {
        const c = catOptions.find(x => x.id === id);
        return c ? {id: c.id, name: c.name} : {id, name: `Category #${id}`};
    });
    const tagOptions = _editorState.options.tags || [];
    _editorState.tags = (p.tags || []).map(id => {
        const t = tagOptions.find(x => x.id === id);
        return t ? {id: t.id, name: t.name} : {id, name: `Tag #${id}`};
    });
    _editorState.brands = [];
    _editorState.attributes = [];
    _editorState.images = {featured: null, gallery: []};
    if (p.featured_media && p.featured_media > 0){
        _editorState.images.featured = {id: p.featured_media, src: ''};
    }
    fillDatalist('wp-categories-datalist', catOptions);
    fillDatalist('wp-tags-datalist', tagOptions);
    renderChips('categories');
    renderChips('tags');
    renderPostImagePreview();
    if (_editorState.images.featured && _editorState.images.featured.id){
        loadFeaturedMediaPreview();
    }
}'''

JS_SAVE_POST_FIND = '''async function savePostChanges(){
    const id = _editorState.id; if (!id) return;
    const payload = {
        id,
        title: document.getElementById('post-edit-title').value,
        content: document.getElementById('post-edit-content').value,
        focus_keyword: document.getElementById('post-edit-focus-kw').value,
    };
    toast('Saving...', 'info');
    const d = await api('/api/editor/save-post', {body: payload});
    if (d.ok) toast('✅ Post saved'); else toast(d.error, 'error');
}'''

JS_SAVE_POST_REPLACE = '''async function savePostChanges(){
    const id = _editorState.id; if (!id) return;
    const payload = {
        id,
        title: document.getElementById('post-edit-title').value,
        slug: document.getElementById('post-edit-slug').value,
        status: document.getElementById('post-edit-status').value,
        excerpt: document.getElementById('post-edit-excerpt').value,
        content: document.getElementById('post-edit-content').value,
        focus_keyword: document.getElementById('post-edit-focus-kw').value,
        categories: _editorState.categories.map(c => c.id),
        tags: _editorState.tags.map(t => t.id),
        featured_media: _editorState.images.featured ? _editorState.images.featured.id : 0,
    };
    toast('Saving...', 'info');
    const d = await api('/api/editor/save-post', {body: payload});
    if (d.ok){
        toast('✅ Post saved');
        if (d.warning) toast(d.warning, 'warning', 6000);
        _editorState.item = d.post;
        _editorState.original = JSON.parse(JSON.stringify(d.post));
        document.getElementById('post-diff-box').classList.add('hidden');
    } else {
        toast(d.error, 'error');
    }
}'''

# Chips - dynamic prefix
JS_RENDER_CHIPS_FIND = '''function renderChips(kind){
    const container = document.getElementById(`prod-edit-${kind}-chips`);
    if (!container) return;
    const list = kind === 'categories' ? _editorState.categories
              : kind === 'tags' ? _editorState.tags
              : _editorState.brands;
    container.innerHTML = '';
    list.forEach(item => {
        const chip = document.createElement('span');
        chip.className = 'chip';
        chip.innerHTML = `${item.name} <span class="chip-x" onclick="removeChip('${kind}', ${item.id})">×</span>`;
        container.appendChild(chip);
    });
}'''

JS_RENDER_CHIPS_REPLACE = '''function _editPrefix(){ return _editorState.type === 'product' ? 'prod-edit' : 'post-edit'; }

function renderChips(kind){
    const prefix = _editPrefix();
    const container = document.getElementById(`${prefix}-${kind}-chips`);
    if (!container) return;
    const list = kind === 'categories' ? _editorState.categories
              : kind === 'tags' ? _editorState.tags
              : _editorState.brands;
    container.innerHTML = '';
    list.forEach(item => {
        const chip = document.createElement('span');
        chip.className = 'chip';
        chip.innerHTML = `${item.name} <span class="chip-x" onclick="removeChip('${kind}', ${item.id})">×</span>`;
        container.appendChild(chip);
    });
}'''

JS_ADD_CHIP_FIND = '''function addChipFromInput(kind){
    const input = document.getElementById(`prod-edit-${kind}-input`);
    const value = input.value.trim();
    if (!value) return;
    const options = kind === 'categories' ? (_editorState.options.categories || [])
                  : kind === 'tags' ? (_editorState.options.tags || [])
                  : (_editorState.options.brands || []);
    const list = kind === 'categories' ? _editorState.categories
              : kind === 'tags' ? _editorState.tags
              : _editorState.brands;
    const match = options.find(o => o.name.toLowerCase() === value.toLowerCase());
    if (match){
        if (!list.find(x => x.id === match.id)) list.push({id: match.id, name: match.name});
        input.value = '';
        renderChips(kind);
    } else {
        toast(`"${value}" not found. Create in Taxonomy Manager first.`, 'warning');
    }
}'''

JS_ADD_CHIP_REPLACE = '''function addChipFromInput(kind){
    const prefix = _editPrefix();
    const input = document.getElementById(`${prefix}-${kind}-input`);
    if (!input) return;
    const value = input.value.trim();
    if (!value) return;
    const options = kind === 'categories' ? (_editorState.options.categories || [])
                  : kind === 'tags' ? (_editorState.options.tags || [])
                  : (_editorState.options.brands || []);
    const list = kind === 'categories' ? _editorState.categories
              : kind === 'tags' ? _editorState.tags
              : _editorState.brands;
    const match = options.find(o => o.name.toLowerCase() === value.toLowerCase());
    if (match){
        if (!list.find(x => x.id === match.id)) list.push({id: match.id, name: match.name});
        input.value = '';
        renderChips(kind);
    } else {
        toast(`"${value}" not found. Create in Taxonomy Manager first.`, 'warning');
    }
}'''

# Tax create/submit fixes
JS_OPEN_CREATE_FIND = '''function openTaxCreateModal(){
    document.getElementById('modal-tax-title').textContent = 'Create New ' + currentTaxType;
    document.getElementById('modal-tax-name').value = '';
    document.getElementById('modal-tax-slug').value = '';
    document.getElementById('modal-tax-description').value = '';
    document.getElementById('modal-tax-parent').value = '0';
    document.getElementById('modal-tax-parent-row').style.display =
        (currentTaxType === 'wc_categories' || currentTaxType === 'wp_categories') ? '' : 'none';
    openModal('modal-tax-create');
}'''

JS_OPEN_CREATE_REPLACE = '''function openTaxCreateModal(){
    _taxEditMode = 'create';
    _taxEditId = null;
    document.getElementById('modal-tax-title').textContent = 'Create New ' + currentTaxType;
    document.getElementById('modal-tax-name').value = '';
    document.getElementById('modal-tax-slug').value = '';
    document.getElementById('modal-tax-description').value = '';
    document.getElementById('modal-tax-parent').value = '0';
    document.getElementById('modal-tax-parent-row').style.display =
        (currentTaxType === 'wc_categories' || currentTaxType === 'wp_categories') ? '' : 'none';
    openModal('modal-tax-create');
}'''

JS_SUBMIT_TAX_FIND = '''async function submitTaxCreate(){
    const name = document.getElementById('modal-tax-name').value.trim();
    if (!name){ toast('Name is required', 'warning'); return; }
    const d = await api('/api/taxonomy/create', {body:{
        type: currentTaxType, name,
        slug: document.getElementById('modal-tax-slug').value,
        parent_id: parseInt(document.getElementById('modal-tax-parent').value) || 0,
        description: document.getElementById('modal-tax-description').value,
    }});
    if (d.ok){
        toast('Created: ' + name);
        closeModal('modal-tax-create');
        refreshTaxonomy();
    } else {
        toast(d.error, 'error');
    }
}'''

JS_SUBMIT_TAX_REPLACE = '''async function submitTaxCreate(){
    const name = document.getElementById('modal-tax-name').value.trim();
    if (!name){ toast('Name is required', 'warning'); return; }
    const payload = {
        type: currentTaxType,
        name,
        slug: document.getElementById('modal-tax-slug').value,
        description: document.getElementById('modal-tax-description').value,
    };
    if (currentTaxType === 'wc_categories' || currentTaxType === 'wp_categories'){
        payload.parent_id = parseInt(document.getElementById('modal-tax-parent').value) || 0;
    }
    let d;
    if (_taxEditMode === 'edit'){
        payload.id = _taxEditId;
        d = await api('/api/taxonomy/update', {body: payload});
    } else {
        d = await api('/api/taxonomy/create', {body: payload});
    }
    if (d.ok){
        toast(_taxEditMode === 'edit' ? '✅ Updated' : '✅ Created: ' + name);
        closeModal('modal-tax-create');
        refreshTaxonomy();
    } else {
        toast(d.error, 'error');
    }
}'''

# Post helpers inserted before deleteCurrentItem
JS_HELPERS = '''function stripHtml(html){ if (!html) return ''; const tmp = document.createElement('div'); tmp.innerHTML = html; return tmp.textContent || tmp.innerText || ''; }

function renderPostImagePreview(){
    const box = document.getElementById('post-edit-featured-preview');
    const idBox = document.getElementById('post-edit-featured-id');
    if (!box) return;
    if (_editorState.images.featured){
        const src = _editorState.images.featured.src;
        if (src) box.innerHTML = `<img src="${src}" style="width:100%;height:100%;object-fit:cover">`;
        else box.innerHTML = 'Loading...';
        idBox.textContent = `Media ID: ${_editorState.images.featured.id}`;
    } else {
        box.innerHTML = 'No image';
        idBox.textContent = '';
    }
}

async function loadFeaturedMediaPreview(){
    const mediaId = _editorState.images.featured ? _editorState.images.featured.id : null;
    if (!mediaId) return;
    const d = await api(`/api/media/${mediaId}`, {method:'GET'});
    if (d.ok && d.url && _editorState.images.featured && _editorState.images.featured.id === mediaId){
        _editorState.images.featured.src = d.url;
        renderPostImagePreview();
    }
}

function changePostFeaturedImage(){
    const input = document.createElement('input');
    input.type = 'file'; input.accept = 'image/*';
    input.onchange = async (e) => {
        const file = e.target.files[0]; if (!file) return;
        toast('Uploading...', 'info');
        const fd = new FormData(); fd.append('file', file);
        try {
            const res = await fetch('/api/media/upload', {method:'POST', body:fd});
            const d = await res.json();
            if (d.ok){
                _editorState.images.featured = {id: d.media_id, src: d.url};
                renderPostImagePreview();
                toast('✅ Featured image updated');
            } else toast(d.error, 'error');
        } catch(e){ toast('Upload failed', 'error'); }
    };
    input.click();
}

function removePostFeaturedImage(){
    _editorState.images.featured = null;
    renderPostImagePreview();
}

function previewPostChanges(){
    const p = _editorState.original || {};
    const changes = [];
    const newTitle = document.getElementById('post-edit-title').value;
    if (newTitle !== (p.title || '')) changes.push(`Title: changed`);
    const newSlug = document.getElementById('post-edit-slug').value;
    if (newSlug !== (p.slug || '')) changes.push(`Slug: ${p.slug} → ${newSlug}`);
    const newStatus = document.getElementById('post-edit-status').value;
    if (newStatus !== (p.status || 'draft')) changes.push(`Status: ${p.status} → ${newStatus}`);
    const newContent = document.getElementById('post-edit-content').value;
    if (newContent !== (p.content || '')) changes.push(`Content: changed`);
    const newExcerpt = document.getElementById('post-edit-excerpt').value;
    if (newExcerpt !== stripHtml(p.excerpt || '')) changes.push(`Excerpt: changed`);
    const origCats = (p.categories || []).sort().join(',');
    const newCats = _editorState.categories.map(c => c.id).sort().join(',');
    if (origCats !== newCats) changes.push(`Categories: changed`);
    const origTags = (p.tags || []).sort().join(',');
    const newTags = _editorState.tags.map(t => t.id).sort().join(',');
    if (origTags !== newTags) changes.push(`Tags: changed`);
    const origFeat = p.featured_media || 0;
    const newFeat = _editorState.images.featured ? _editorState.images.featured.id : 0;
    if (origFeat !== newFeat) changes.push(`Featured image: ${origFeat} → ${newFeat}`);
    document.getElementById('post-diff-content').textContent = changes.length ? changes.join('\\n\\n') : 'No changes.';
    document.getElementById('post-diff-box').classList.remove('hidden');
}

async function deleteCurrentItem(){'''


# =============================================================================
# FLASK ROUTES — new media + taxonomy update + save-post via function boundary
# =============================================================================
NEW_MEDIA_AND_TAX_ROUTES = '''# ---------- MEDIA GET + TAXONOMY UPDATE ----------
@app.route("/api/media/<int:media_id>", methods=["GET"])
def api_media_get(media_id):
    s = get_session_data()
    if not s["wp"]["connected"]:
        return jsonify({"ok": False, "error": "Connect WP first"})
    try:
        r = requests.get(
            f"{s['wp']['url'].rstrip('/')}/wp-json/wp/v2/media/{media_id}",
            auth=(s["wp"]["user"], s["wp"]["pass"]), timeout=15)
        if r.status_code != 200:
            return jsonify({"ok": False, "error": f"HTTP {r.status_code}"})
        data = r.json()
        return jsonify({"ok": True, "url": data.get("source_url", "")})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)[:100]})


@app.route("/api/taxonomy/update", methods=["POST"])
def api_taxonomy_update():
    if not CUSTOM_MODULES or not taxonomy:
        return jsonify({"ok": False, "error": "taxonomy.py missing"})
    s = get_session_data()
    if not s["wc"]["connected"]:
        return jsonify({"ok": False, "error": "Connect WC first"})
    d = request.json or {}
    tax_type = d.get("type")
    item_id = d.get("id")
    if not item_id:
        return jsonify({"ok": False, "error": "ID required"})
    fields = {}
    if "name" in d and d["name"]:
        fields["name"] = d["name"]
    if "slug" in d and d["slug"] is not None:
        fields["slug"] = d["slug"]
    if "description" in d and d["description"] is not None:
        fields["description"] = d["description"]
    if "parent_id" in d and tax_type in ("wc_categories", "wp_categories"):
        try:
            fields["parent"] = int(d["parent_id"]) if d["parent_id"] else 0
        except Exception:
            fields["parent"] = 0
    if not fields:
        return jsonify({"ok": False, "error": "No fields to update"})
    ok, item, err = taxonomy.update_one(
        s["wc"]["url"], s["wc"]["ck"], s["wc"]["cs"], tax_type, item_id, **fields)
    if not ok:
        return jsonify({"ok": False, "error": err})
    log_activity("taxonomy_update", "ok", f"{tax_type} id={item_id}")
    return jsonify({"ok": True, "item": item})


# ---------- EDITOR DATA ----------'''

NEW_SAVE_POST_FUNC = '''@app.route("/api/editor/save-post", methods=["POST"])
def api_editor_save_post():
    s = get_session_data()
    if not s["wp"]["connected"]:
        return jsonify({"ok": False, "error": "Connect WP first"})
    if not CUSTOM_MODULES or not wp_client:
        return jsonify({"ok": False, "error": "wp_client.py missing"})
    d = request.json or {}
    pid = d.get("id")
    if not pid:
        return jsonify({"ok": False, "error": "Post ID required"})
    fields = {}
    for k in ["title", "content", "status", "excerpt", "slug"]:
        if k in d and d[k] is not None:
            fields[k] = d[k]
    if "categories" in d and isinstance(d["categories"], list):
        try:
            fields["categories"] = [int(x) for x in d["categories"] if x]
        except Exception:
            pass
    if "tags" in d and isinstance(d["tags"], list):
        try:
            fields["tags"] = [int(x) for x in d["tags"] if x]
        except Exception:
            pass
    if "featured_media" in d:
        try:
            fields["featured_media"] = int(d["featured_media"]) if d["featured_media"] else 0
        except Exception:
            fields["featured_media"] = 0
    warning = ""
    if "focus_keyword" in d and d["focus_keyword"] is not None:
        fields["meta"] = {"rank_math_focus_keyword": d["focus_keyword"]}
        warning = "Focus keyword sent via meta. If not saved, verify in WP Admin."
    if not fields:
        return jsonify({"ok": False, "error": "No fields to update"})
    ok, post, err = wp_client.update_post(
        s["wp"]["url"], s["wp"]["user"], s["wp"]["pass"], pid, **fields)
    if not ok:
        return jsonify({"ok": False, "error": err})
    log_activity("editor_save_post", "ok", f"id={pid}")
    return jsonify({"ok": True, "post": post, "warning": warning})


# ---------- MEDIA GET + TAXONOMY UPDATE ----------'''


# =============================================================================
# PATCHER
# =============================================================================
def patch_app():
    print("\n📄 Patching app_web.py...")
    if not APP_FILE.exists():
        print("   ❌ app_web.py not found")
        return False

    content = APP_FILE.read_text(encoding="utf-8")

    if 'id="post-edit-slug"' in content and 'id="wp-categories-datalist"' in content:
        print("   ⚠️  Already patched. Skipping.")
        return True

    # Pre-check
    print("   🔍 Pre-checking markers...")
    markers = {
        "Post HTML start": POST_HTML_START,
        "Post HTML end": POST_HTML_END,
        "Tax edit (exact)": TAX_EDIT_FIND,
        "JS renderPost": JS_RENDER_POST_FIND,
        "JS savePost": JS_SAVE_POST_FIND,
        "JS renderChips": JS_RENDER_CHIPS_FIND,
        "JS addChip": JS_ADD_CHIP_FIND,
        "JS openTaxCreate": JS_OPEN_CREATE_FIND,
        "JS submitTax": JS_SUBMIT_TAX_FIND,
        "JS deleteCurrentItem": 'async function deleteCurrentItem(){',
        "Flask save-post function": "def api_editor_save_post():",
        "Flask route insert": "# ---------- EDITOR DATA ----------",
    }
    missing = []
    for name, m in markers.items():
        if m in content:
            print(f"   ✅ {name}")
        else:
            print(f"   ❌ {name} MISSING")
            missing.append(name)

    if missing:
        print(f"\n   ❌ {len(missing)} missing — ABORTING")
        return False

    # Backup
    backup = APP_FILE.with_suffix(".py.bak")
    backup.write_text(content, encoding="utf-8")
    print(f"\n   ✅ Backup: {backup}\n")

    # 1. Replace post HTML
    start = content.find(POST_HTML_START)
    end = content.find(POST_HTML_END, start)
    if start == -1 or end == -1:
        print("   ❌ HTML boundaries lost")
        return False
    content = content[:start] + NEW_POST_HTML + content[end:]
    print("   ✅ [1/7] Post HTML replaced")

    # 2. renderPost
    content = content.replace(JS_RENDER_POST_FIND, JS_RENDER_POST_REPLACE, 1)
    print("   ✅ [2/7] renderPostEditor replaced")

    # 3. savePost
    content = content.replace(JS_SAVE_POST_FIND, JS_SAVE_POST_REPLACE, 1)
    print("   ✅ [3/7] savePostChanges replaced")

    # 4. Chips
    content = content.replace(JS_RENDER_CHIPS_FIND, JS_RENDER_CHIPS_REPLACE, 1)
    content = content.replace(JS_ADD_CHIP_FIND, JS_ADD_CHIP_REPLACE, 1)
    print("   ✅ [4/7] Chip functions dynamic prefix")

    # 5. Tax edit + create + submit
    content = content.replace(TAX_EDIT_FIND, TAX_EDIT_REPLACE, 1)
    content = content.replace(JS_OPEN_CREATE_FIND, JS_OPEN_CREATE_REPLACE, 1)
    content = content.replace(JS_SUBMIT_TAX_FIND, JS_SUBMIT_TAX_REPLACE, 1)
    print("   ✅ [5/7] Taxonomy edit implemented")

    # 6. Post helpers before deleteCurrentItem
    content = content.replace('async function deleteCurrentItem(){', JS_HELPERS, 1)
    print("   ✅ [6/7] Post helpers added")

    # 7. Flask routes - replace save-post function by finding def and next @app.route
    save_post_start = content.find("def api_editor_save_post():")
    if save_post_start == -1:
        print("   ❌ save-post start lost")
        return False
    # Find the decorator before it
    decorator_start = content.rfind("@app.route", 0, save_post_start)
    if decorator_start == -1:
        print("   ❌ save-post decorator lost")
        return False
    # Find next @app.route (or end)
    next_route = content.find("@app.route", save_post_start)
    if next_route == -1:
        print("   ❌ save-post end not found")
        return False
    # Skip the next route's decorator comment marker
    content = content[:decorator_start] + NEW_SAVE_POST_FUNC[:-len("# ---------- MEDIA GET + TAXONOMY UPDATE ----------")] + content[next_route:]
    print("   ✅ [7a/7] save-post function replaced")

    # Insert media + taxonomy update routes before EDITOR DATA
    content = content.replace("# ---------- EDITOR DATA ----------", NEW_MEDIA_AND_TAX_ROUTES, 1)
    print("   ✅ [7b/7] Media + Taxonomy update routes added")

    APP_FILE.write_text(content, encoding="utf-8")
    print(f"\n   ✅ app_web.py saved ({len(content.splitlines())} lines)")
    return True


def main():
    print("=" * 60)
    print("  Part 3 v2 — Post Editor + Taxonomy Edit (exact)")
    print("=" * 60)

    ok = patch_app()

    print("\n" + "=" * 60)
    if ok:
        print("  ✅ PATCH COMPLETE")
        print("=" * 60)
        print("\nNext:")
        print("  1. python -c \"import ast; ast.parse(open('app_web.py', encoding='utf-8').read()); print('Syntax OK')\"")
        print("  2. python app_web.py")
        return 0
    print("  ❌ PATCH FAILED")
    print("=" * 60)
    return 1


if __name__ == "__main__":
    sys.exit(main())