# =============================================================================
# patch_editor_part2.py — FIXED v2
# =============================================================================

import sys
from pathlib import Path

APP_FILE = Path("app_web.py")


NEW_HTML = r'''<!-- ========== TAB 11: UNIVERSAL EDITOR ========== -->
<section class="tab-content" id="tab-editor">
    <div class="card">
        <h2>✏️ Universal Content Editor <span class="text-muted text-sm" style="font-weight:400">v2.0</span></h2>
        <p class="text-muted mb-16">Edit live products or blog posts. All changes preview before saving.</p>
        <div class="form-row-2">
            <div class="form-row"><label>Content Type</label>
                <select id="editor-type" onchange="toggleEditorType()">
                    <option value="product">Product</option>
                    <option value="post">Blog Post</option>
                </select></div>
            <div class="form-row"><label>Select Item</label>
                <select id="editor-item" onchange="loadEditorItem()"></select></div>
        </div>
        <button class="btn btn-info" onclick="loadEditorList()">🔄 Load List</button>
        <span id="editor-load-status" class="text-muted" style="margin-left:12px"></span>
    </div>

    <div id="editor-product-form" class="hidden">
        <div class="card">
            <h2>📦 <span id="prod-edit-name-display">Product</span> <span class="text-muted text-sm" id="prod-edit-id-display"></span></h2>
            <div class="form-row-3">
                <div class="form-row"><label>Name</label><input type="text" id="prod-edit-name"></div>
                <div class="form-row"><label>SKU</label><input type="text" id="prod-edit-sku"></div>
                <div class="form-row"><label>Status</label>
                    <select id="prod-edit-status">
                        <option value="draft">Draft</option>
                        <option value="publish">Published</option>
                        <option value="pending">Pending</option>
                        <option value="private">Private</option>
                    </select></div>
            </div>
        </div>

        <div class="card">
            <h2>💰 Pricing & Stock</h2>
            <div class="form-row-3">
                <div class="form-row"><label>Regular Price (Rs)</label><input type="number" id="prod-edit-regular-price" step="0.01" min="0"></div>
                <div class="form-row"><label>Sale Price (Rs)</label><input type="number" id="prod-edit-sale-price" step="0.01" min="0"></div>
                <div class="form-row"><label>Stock Quantity</label><input type="number" id="prod-edit-stock" step="1" min="0"></div>
            </div>
            <div class="form-row-2">
                <div class="form-row"><label>Stock Status</label>
                    <select id="prod-edit-stock-status">
                        <option value="instock">In Stock</option>
                        <option value="outofstock">Out of Stock</option>
                        <option value="onbackorder">On Backorder</option>
                    </select></div>
                <div class="form-row" style="display:flex;align-items:flex-end;padding-bottom:10px">
                    <label style="display:flex;align-items:center;gap:8px;cursor:pointer;margin:0">
                        <input type="checkbox" id="prod-edit-manage-stock" style="width:auto;margin:0">
                        <span>Manage stock quantity</span>
                    </label>
                </div>
            </div>
        </div>

        <div class="card">
            <h2>📝 Content</h2>
            <div class="form-row"><label>Short Description</label><textarea id="prod-edit-short-desc" rows="2"></textarea></div>
            <div class="form-row"><label>Full Description (HTML)</label><textarea id="prod-edit-desc" rows="10" style="font-family:Consolas,monospace;font-size:12px"></textarea></div>
        </div>

        <div class="card">
            <h2>🏷️ Categories, Tags & Brand</h2>
            <div class="form-row">
                <label>Categories</label>
                <div class="chips-container" id="prod-edit-categories-chips"></div>
                <input type="text" id="prod-edit-categories-input" list="categories-datalist" placeholder="Type + Enter to add category" onkeypress="if(event.key==='Enter'){event.preventDefault();addChipFromInput('categories')}">
                <datalist id="categories-datalist"></datalist>
            </div>
            <div class="form-row">
                <label>Tags</label>
                <div class="chips-container" id="prod-edit-tags-chips"></div>
                <input type="text" id="prod-edit-tags-input" list="tags-datalist" placeholder="Type + Enter to add tag" onkeypress="if(event.key==='Enter'){event.preventDefault();addChipFromInput('tags')}">
                <datalist id="tags-datalist"></datalist>
            </div>
            <div class="form-row">
                <label>Brand</label>
                <div class="chips-container" id="prod-edit-brand-chips"></div>
                <input type="text" id="prod-edit-brand-input" list="brands-datalist" placeholder="Type + Enter to add brand" onkeypress="if(event.key==='Enter'){event.preventDefault();addChipFromInput('brand')}">
                <datalist id="brands-datalist"></datalist>
            </div>
        </div>

        <div class="card">
            <h2>⚙️ Attributes</h2>
            <div id="prod-edit-attributes-container"></div>
            <p class="text-muted mt-8" style="font-size:11px">Comma-separated values. Example: 100ml, 200ml</p>
        </div>

        <div class="card">
            <h2>🖼️ Images</h2>
            <div class="form-row">
                <label>Featured Image</label>
                <div style="display:flex;gap:12px;align-items:center">
                    <div id="prod-edit-featured-preview" class="image-thumb">No image</div>
                    <div>
                        <button class="btn btn-sm" onclick="changeFeaturedImage()">📷 Change</button>
                        <button class="btn btn-sm btn-danger" onclick="removeFeaturedImage()">🗑️ Remove</button>
                        <div class="text-muted text-sm mt-8" id="prod-edit-featured-id"></div>
                    </div>
                </div>
            </div>
            <div class="form-row">
                <label>Gallery Images</label>
                <div id="prod-edit-gallery-container" style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:8px"></div>
                <button class="btn btn-sm" onclick="addGalleryImage()">➕ Add Gallery Image</button>
            </div>
        </div>

        <div class="card">
            <h2>🔍 SEO / Meta</h2>
            <div class="form-row"><label>Meta Title (max 60)</label><input type="text" id="prod-edit-meta-title" maxlength="60"></div>
            <div class="form-row"><label>Meta Description (max 160)</label><textarea id="prod-edit-meta-desc" rows="2" maxlength="160"></textarea></div>
        </div>

        <div class="card">
            <div class="btn-row">
                <button class="btn" onclick="previewProductChanges()">👁️ Preview</button>
                <button class="btn btn-primary btn-lg" onclick="saveProductChanges()">💾 Save Changes</button>
                <button class="btn btn-danger" onclick="deleteCurrentItem()">🗑️ Delete Product</button>
            </div>
            <div id="product-diff-box" class="hidden mt-16">
                <h3>Changes Preview</h3>
                <pre class="log" id="product-diff-content" style="max-height:400px"></pre>
            </div>
        </div>
    </div>

    <div id="editor-post-form" class="hidden">
        <div class="card">
            <h2>📰 <span id="post-edit-title-display">Blog Post</span></h2>
            <div class="form-row"><label>Title</label><input type="text" id="post-edit-title"></div>
            <div class="form-row"><label>Content (HTML)</label><textarea id="post-edit-content" rows="12" style="font-family:Consolas,monospace;font-size:12px"></textarea></div>
            <div class="btn-row">
                <button class="btn btn-primary" onclick="savePostChanges()">💾 Save Changes</button>
                <button class="btn btn-danger" onclick="deleteCurrentItem()">🗑️ Delete Post</button>
            </div>
            <p class="text-muted mt-8">Full post editor in Part 3.</p>
        </div>
    </div>

    <div id="editor-empty-state">
        <div class="card">
            <p class="text-muted">Select content type, click "Load List", then select an item.</p>
        </div>
    </div>
</section>

'''


NEW_JS = r'''// TAB 11: UNIVERSAL EDITOR v2.0
let _editorState = {
    type: 'product', id: null, item: null,
    options: {categories:[], tags:[], attributes:[], brands:[]},
    categories: [], tags: [], brands: [], attributes: [],
    images: {featured: null, gallery: []},
    original: null,
};

function toggleEditorType(){
    _editorState.type = document.getElementById('editor-type').value;
    loadEditorList();
}

async function loadEditorList(){
    const type = document.getElementById('editor-type').value;
    _editorState.type = type;
    const sel = document.getElementById('editor-item');
    sel.innerHTML = '<option value="">Loading...</option>';
    const endpoint = type === 'product' ? '/api/live/list' : '/api/blog/list';
    const d = await api(endpoint, {body:{status:'any'}});
    sel.innerHTML = '';
    if (!d.ok){
        sel.innerHTML = '<option value="">(error)</option>';
        document.getElementById('editor-load-status').textContent = '❌ ' + d.error;
        return;
    }
    const items = type === 'product' ? (d.products || []) : (d.posts || []);
    if (!items.length){
        sel.innerHTML = '<option value="">(no items)</option>';
        document.getElementById('editor-load-status').textContent = '0 items';
        return;
    }
    items.forEach(it => {
        const opt = document.createElement('option');
        opt.value = it.id;
        opt.textContent = type === 'product' ? `#${it.id} — ${it.name}` : `#${it.id} — ${it.title}`;
        sel.appendChild(opt);
    });
    document.getElementById('editor-load-status').textContent = `${items.length} items`;
}

async function loadEditorItem(){
    const type = document.getElementById('editor-type').value;
    const id = document.getElementById('editor-item').value;
    if (!id) return;
    _editorState.type = type;
    _editorState.id = parseInt(id);
    _editorState.options = {categories:[], tags:[], attributes:[], brands:[]};
    _editorState.categories = []; _editorState.tags = []; _editorState.brands = [];
    _editorState.attributes = [];
    _editorState.images = {featured: null, gallery: []};
    document.getElementById('editor-load-status').textContent = 'Loading...';
    const d = await api('/api/editor/load', {body:{type, id: _editorState.id}});
    if (!d.ok){
        document.getElementById('editor-load-status').textContent = '❌ ' + d.error;
        toast(d.error, 'error');
        return;
    }
    _editorState.item = d.item;
    _editorState.options = d.options || {categories:[], tags:[], attributes:[], brands:[]};
    _editorState.original = JSON.parse(JSON.stringify(d.item));
    document.getElementById('editor-load-status').textContent = '✅ Loaded';
    if (type === 'product') renderProductEditor();
    else renderPostEditor();
}

function renderProductEditor(){
    const p = _editorState.item;
    document.getElementById('editor-product-form').classList.remove('hidden');
    document.getElementById('editor-post-form').classList.add('hidden');
    document.getElementById('editor-empty-state').classList.add('hidden');
    document.getElementById('prod-edit-name-display').textContent = p.name;
    document.getElementById('prod-edit-id-display').textContent = `#${p.id}`;
    document.getElementById('prod-edit-name').value = p.name || '';
    document.getElementById('prod-edit-sku').value = p.sku || '';
    document.getElementById('prod-edit-status').value = p.status || 'draft';
    document.getElementById('prod-edit-regular-price').value = p.regular_price || '';
    document.getElementById('prod-edit-sale-price').value = p.sale_price || '';
    document.getElementById('prod-edit-stock').value = p.stock || 0;
    document.getElementById('prod-edit-stock-status').value = p.stock_status || 'instock';
    document.getElementById('prod-edit-manage-stock').checked = !!p.manage_stock;
    document.getElementById('prod-edit-short-desc').value = p.short_description || '';
    document.getElementById('prod-edit-desc').value = p.description || '';
    _editorState.categories = (p.categories || []).map(c => ({id: c.id, name: c.name}));
    _editorState.tags = (p.tags || []).map(t => ({id: t.id, name: t.name}));
    _editorState.brands = [];
    _editorState.attributes = (p.attributes || []).map(a => ({name: a.name, values: (a.options || []).join(', ')}));
    _editorState.images = {featured: null, gallery: []};
    if (p.images && p.images.length){
        _editorState.images.featured = {id: p.images[0].id, src: p.images[0].src};
        p.images.slice(1).forEach(img => _editorState.images.gallery.push({id: img.id, src: img.src}));
    }
    fillDatalist('categories-datalist', _editorState.options.categories || []);
    fillDatalist('tags-datalist', _editorState.options.tags || []);
    fillDatalist('brands-datalist', _editorState.options.brands || []);
    renderChips('categories');
    renderChips('tags');
    renderChips('brand');
    renderAttributes();
    renderImagePreviews();
}

function renderPostEditor(){
    const p = _editorState.item;
    document.getElementById('editor-post-form').classList.remove('hidden');
    document.getElementById('editor-product-form').classList.add('hidden');
    document.getElementById('editor-empty-state').classList.add('hidden');
    document.getElementById('post-edit-title-display').textContent = p.title;
    document.getElementById('post-edit-title').value = p.title || '';
    document.getElementById('post-edit-content').value = p.content || '';
}

function fillDatalist(id, items){
    const dl = document.getElementById(id);
    if (!dl) return;
    dl.innerHTML = '';
    items.forEach(it => {
        const opt = document.createElement('option');
        opt.value = it.name; opt.dataset.id = it.id;
        dl.appendChild(opt);
    });
}

function renderChips(kind){
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
}

function addChipFromInput(kind){
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
}

function removeChip(kind, id){
    const list = kind === 'categories' ? _editorState.categories
              : kind === 'tags' ? _editorState.tags
              : _editorState.brands;
    const idx = list.findIndex(x => x.id === id);
    if (idx >= 0) list.splice(idx, 1);
    renderChips(kind);
}

function renderAttributes(){
    const container = document.getElementById('prod-edit-attributes-container');
    container.innerHTML = '';
    if (!_editorState.attributes.length){
        container.innerHTML = '<p class="text-muted">No attributes.</p>';
        return;
    }
    _editorState.attributes.forEach((attr, idx) => {
        const row = document.createElement('div');
        row.className = 'attr-row';
        row.innerHTML = `<label style="min-width:100px;margin:0">${attr.name}</label>
            <input type="text" value="${attr.values || ''}" placeholder="Values (comma-separated)"
                   onchange="_editorState.attributes[${idx}].values = this.value">`;
        container.appendChild(row);
    });
}

function renderImagePreviews(){
    const featBox = document.getElementById('prod-edit-featured-preview');
    const featId = document.getElementById('prod-edit-featured-id');
    if (_editorState.images.featured){
        featBox.innerHTML = `<img src="${_editorState.images.featured.src}" style="width:100%;height:100%;object-fit:cover">`;
        featId.textContent = `Media ID: ${_editorState.images.featured.id}`;
    } else {
        featBox.innerHTML = 'No image'; featId.textContent = '';
    }
    const galBox = document.getElementById('prod-edit-gallery-container');
    galBox.innerHTML = '';
    _editorState.images.gallery.forEach((img, idx) => {
        const div = document.createElement('div');
        div.className = 'image-thumb';
        div.style.position = 'relative';
        div.innerHTML = `<img src="${img.src}" style="width:100%;height:100%;object-fit:cover">
            <span onclick="removeGalleryImage(${idx})" style="position:absolute;top:2px;right:2px;background:rgba(0,0,0,.7);color:#fff;width:20px;height:20px;border-radius:50%;display:flex;align-items:center;justify-content:center;cursor:pointer;font-size:14px">×</span>`;
        galBox.appendChild(div);
    });
}

function changeFeaturedImage(){
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
                renderImagePreviews(); toast('✅ Featured image updated');
            } else toast(d.error, 'error');
        } catch(e){ toast('Upload failed', 'error'); }
    };
    input.click();
}

function addGalleryImage(){
    const input = document.createElement('input');
    input.type = 'file'; input.accept = 'image/*'; input.multiple = true;
    input.onchange = async (e) => {
        const files = e.target.files; if (!files.length) return;
        for (const file of files){
            toast('Uploading...', 'info');
            const fd = new FormData(); fd.append('file', file);
            try {
                const res = await fetch('/api/media/upload', {method:'POST', body:fd});
                const d = await res.json();
                if (d.ok){
                    _editorState.images.gallery.push({id: d.media_id, src: d.url});
                    renderImagePreviews(); toast('✅ Gallery image added');
                } else toast(d.error, 'error');
            } catch(e){ toast('Upload failed', 'error'); }
        }
    };
    input.click();
}

function removeFeaturedImage(){ _editorState.images.featured = null; renderImagePreviews(); }
function removeGalleryImage(idx){ _editorState.images.gallery.splice(idx, 1); renderImagePreviews(); }

function previewProductChanges(){
    const p = _editorState.original || {};
    const changes = [];
    const newName = document.getElementById('prod-edit-name').value;
    if (newName !== (p.name || '')) changes.push(`Name: "${p.name}" → "${newName}"`);
    const newPrice = document.getElementById('prod-edit-regular-price').value;
    if (String(newPrice) !== String(p.regular_price || '')) changes.push(`Regular Price: ${p.regular_price} → ${newPrice}`);
    const newStock = document.getElementById('prod-edit-stock').value;
    if (String(newStock) !== String(p.stock || 0)) changes.push(`Stock: ${p.stock} → ${newStock}`);
    const newDesc = document.getElementById('prod-edit-desc').value;
    if (newDesc !== (p.description || '')) changes.push(`Description: changed`);
    const origCats = (p.categories || []).map(c => c.id).sort().join(',');
    const newCats = _editorState.categories.map(c => c.id).sort().join(',');
    if (origCats !== newCats) changes.push(`Categories: changed`);
    const origTags = (p.tags || []).map(t => t.id).sort().join(',');
    const newTags = _editorState.tags.map(t => t.id).sort().join(',');
    if (origTags !== newTags) changes.push(`Tags: changed`);
    document.getElementById('product-diff-content').textContent = changes.length ? changes.join('\n\n') : 'No changes.';
    document.getElementById('product-diff-box').classList.remove('hidden');
}

async function saveProductChanges(){
    const id = _editorState.id; if (!id) return;
    const payload = {
        id,
        name: document.getElementById('prod-edit-name').value,
        status: document.getElementById('prod-edit-status').value,
        regular_price: document.getElementById('prod-edit-regular-price').value,
        sale_price: document.getElementById('prod-edit-sale-price').value,
        stock_quantity: document.getElementById('prod-edit-stock').value,
        stock_status: document.getElementById('prod-edit-stock-status').value,
        manage_stock: document.getElementById('prod-edit-manage-stock').checked,
        short_description: document.getElementById('prod-edit-short-desc').value,
        description: document.getElementById('prod-edit-desc').value,
        categories: _editorState.categories.map(c => ({id: c.id})),
        tags: _editorState.tags.map(t => ({id: t.id})),
        attributes: _editorState.attributes.map(a => ({
            name: a.name,
            options: (a.values || '').split(',').map(v => v.trim()).filter(v => v)
        })),
    };
    const imgs = [];
    if (_editorState.images.featured) imgs.push({id: _editorState.images.featured.id, position: 0});
    _editorState.images.gallery.forEach((img, idx) => imgs.push({id: img.id, position: idx + 1}));
    if (imgs.length) payload.images = imgs;
    toast('Saving...', 'info');
    const d = await api('/api/editor/save-product', {body: payload});
    if (d.ok){
        toast('✅ Product saved');
        _editorState.item = d.product;
        _editorState.original = JSON.parse(JSON.stringify(d.product));
        document.getElementById('product-diff-box').classList.add('hidden');
    } else toast(d.error, 'error');
}

async function savePostChanges(){
    const id = _editorState.id; if (!id) return;
    const payload = {
        id,
        title: document.getElementById('post-edit-title').value,
        content: document.getElementById('post-edit-content').value,
    };
    toast('Saving...', 'info');
    const d = await api('/api/editor/save-post', {body: payload});
    if (d.ok) toast('✅ Post saved'); else toast(d.error, 'error');
}

async function deleteCurrentItem(){
    const type = _editorState.type;
    const id = _editorState.id;
    if (!id) return;
    if (!confirm(`Delete this ${type}? Cannot be undone.`)) return;
    const endpoint = type === 'product' ? '/api/live/delete' : '/api/blog/delete';
    const d = await api(endpoint, {body:{id, force: true}});
    if (d.ok){
        toast('✅ Deleted');
        _editorState.id = null; _editorState.item = null;
        document.getElementById('editor-product-form').classList.add('hidden');
        document.getElementById('editor-post-form').classList.add('hidden');
        document.getElementById('editor-empty-state').classList.remove('hidden');
        loadEditorList();
    } else toast(d.error, 'error');
}

'''


NEW_CSS = r'''
.chips-container{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:8px;min-height:28px}
.chip{display:inline-flex;align-items:center;gap:6px;padding:4px 10px;background:var(--primary-l);color:var(--primary);border-radius:14px;font-size:12px;font-weight:600}
[data-theme=dark] .chip{background:#14321e;color:#86efac}
.chip-x{cursor:pointer;font-weight:700;font-size:14px;line-height:1}
.chip-x:hover{color:var(--danger)}
.attr-row{display:flex;gap:12px;align-items:center;margin-bottom:10px;padding:8px;background:var(--bg-elev);border-radius:6px}
.attr-row label{flex-shrink:0;color:var(--text);font-weight:600}
.attr-row input{flex:1}
.image-thumb{width:100px;height:100px;border-radius:6px;border:2px dashed var(--border);background:var(--bg-elev);display:flex;align-items:center;justify-content:center;font-size:11px;color:var(--muted);overflow:hidden;flex-shrink:0}

'''


NEW_ROUTES = r'''# ---------- EDITOR DATA ----------
@app.route("/api/editor/load", methods=["POST"])
def api_editor_load():
    s = get_session_data()
    d = request.json or {}
    item_type = d.get("type", "product")
    item_id = d.get("id")
    if not item_id:
        return jsonify({"ok": False, "error": "Item ID required"})
    if not CUSTOM_MODULES or not wp_client:
        return jsonify({"ok": False, "error": "wp_client.py missing"})
    if item_type == "product":
        if not s["wc"]["connected"]:
            return jsonify({"ok": False, "error": "Connect WC first"})
        ok, result, err = wp_client.get_editor_data(
            s["wp"]["url"], s["wp"]["user"], s["wp"]["pass"],
            s["wc"]["url"], s["wc"]["ck"], s["wc"]["cs"],
            item_type="product", item_id=item_id)
    else:
        if not s["wp"]["connected"]:
            return jsonify({"ok": False, "error": "Connect WP first"})
        wc_url = s["wc"]["url"] if s["wc"]["connected"] else s["wp"]["url"]
        wc_ck = s["wc"]["ck"] if s["wc"]["connected"] else ""
        wc_cs = s["wc"]["cs"] if s["wc"]["connected"] else ""
        ok, result, err = wp_client.get_editor_data(
            s["wp"]["url"], s["wp"]["user"], s["wp"]["pass"],
            wc_url, wc_ck, wc_cs, item_type="post", item_id=item_id)
    if not ok:
        return jsonify({"ok": False, "error": err})
    return jsonify({"ok": True, **result})


@app.route("/api/editor/save-product", methods=["POST"])
def api_editor_save_product():
    s = get_session_data()
    if not s["wc"]["connected"]:
        return jsonify({"ok": False, "error": "Connect WC first"})
    if not CUSTOM_MODULES or not wp_client:
        return jsonify({"ok": False, "error": "wp_client.py missing"})
    d = request.json or {}
    pid = d.get("id")
    if not pid:
        return jsonify({"ok": False, "error": "Product ID required"})
    fields = {}
    for k in ["name", "status", "description", "short_description",
              "regular_price", "sale_price", "stock_status"]:
        if k in d and d[k] is not None:
            fields[k] = str(d[k]) if k in ("regular_price", "sale_price") else d[k]
    if "stock_quantity" in d:
        try: fields["stock_quantity"] = int(d["stock_quantity"])
        except: fields["stock_quantity"] = 0
    if "manage_stock" in d:
        fields["manage_stock"] = bool(d["manage_stock"])
    if "categories" in d:
        fields["categories"] = [{"id": int(c["id"])} for c in d["categories"]]
    if "tags" in d:
        fields["tags"] = [{"id": int(t["id"])} for t in d["tags"]]
    if "attributes" in d:
        fields["attributes"] = [
            {"name": a["name"], "options": a.get("options", []),
             "visible": True, "variation": False}
            for a in d["attributes"] if a.get("name")
        ]
    if "images" in d:
        fields["images"] = d["images"]
    ok, product, err = wp_client.update_product(
        s["wc"]["url"], s["wc"]["ck"], s["wc"]["cs"], pid, **fields)
    if not ok:
        return jsonify({"ok": False, "error": err})
    log_activity("editor_save_product", "ok", f"id={pid}")
    return jsonify({"ok": True, "product": product})


@app.route("/api/editor/save-post", methods=["POST"])
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
    for k in ["title", "content", "status", "excerpt"]:
        if k in d and d[k] is not None:
            fields[k] = d[k]
    if not fields:
        return jsonify({"ok": False, "error": "No fields to update"})
    ok, post, err = wp_client.update_post(
        s["wp"]["url"], s["wp"]["user"], s["wp"]["pass"], pid, **fields)
    if not ok:
        return jsonify({"ok": False, "error": err})
    log_activity("editor_save_post", "ok", f"id={pid}")
    return jsonify({"ok": True, "post": post})


@app.route("/api/media/upload", methods=["POST"])
def api_media_upload():
    s = get_session_data()
    if not s["wp"]["connected"]:
        return jsonify({"ok": False, "error": "Connect WP first"})
    if not CUSTOM_MODULES or not media:
        return jsonify({"ok": False, "error": "media.py missing"})
    if "file" not in request.files:
        return jsonify({"ok": False, "error": "No file"})
    file = request.files["file"]
    raw_name = f"{uuid.uuid4().hex}_{file.filename}"
    raw_path = UPLOAD_DIR / raw_name
    file.save(str(raw_path))
    try:
        ok, final = media.process_image_pipeline(
            str(raw_path), (1200, 1200), aspect="1:1", quality=82)
        if not ok:
            return jsonify({"ok": False, "error": final})
        ok2, media_obj, err = media.upload_single_media(
            s["wp"]["url"], s["wp"]["user"], s["wp"]["pass"],
            final, filename=Path(raw_name).stem + ".webp")
        if not ok2:
            return jsonify({"ok": False, "error": err})
        return jsonify({"ok": True, "media_id": media_obj["id"],
                        "url": media_obj["source_url"]})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)[:200]})


# ---------- EXPORT ----------'''


def patch():
    if not APP_FILE.exists():
        print("❌ app_web.py not found")
        return 1

    content = APP_FILE.read_text(encoding="utf-8")

    if "editor-product-form" in content and "prod-edit-name-display" in content:
        print("⚠️  Already patched. Skipping.")
        return 0

    print("🔍 Pre-checking markers...")
    markers = {
        "HTML start": "<!-- ========== TAB 11: UNIVERSAL EDITOR ========== -->",
        "HTML end": "<!-- ========== TAB 12: EXPORT ========== -->",
        "JS start": "// ================================================================\n// TAB 11: UNIVERSAL EDITOR",
        "JS end": "// ================================================================\n// TAB 12: EXPORT",
        "CSS anchor": 'HTML_BODY = r"""',
        "Flask route": "# ---------- EXPORT ----------",
    }
    missing = []
    for name, marker in markers.items():
        if marker in content:
            print(f"   ✅ {name}")
        else:
            print(f"   ❌ {name} MISSING")
            missing.append(name)

    if missing:
        print(f"\n❌ {len(missing)} markers missing: {', '.join(missing)}")
        print("⚠️  FILE NOT MODIFIED")
        return 1

    print("\n✅ All markers found\n")

    backup = APP_FILE.with_suffix(".py.bak")
    backup.write_text(content, encoding="utf-8")
    print(f"✅ Backup: {backup}\n")

    html_start = content.find(markers["HTML start"])
    html_end = content.find(markers["HTML end"])
    content = content[:html_start] + NEW_HTML + content[html_end:]
    print("✅ [1/4] HTML replaced")

    js_start = content.find(markers["JS start"])
    js_end = content.find(markers["JS end"])
    content = content[:js_start] + NEW_JS + content[js_end:]
    print("✅ [2/4] JS replaced")

    html_body_pos = content.find(markers["CSS anchor"])
    css_close = content.rfind('"""', 0, html_body_pos)
    content = content[:css_close] + NEW_CSS + "\n" + content[css_close:]
    print("✅ [3/4] CSS added")

    route_pos = content.find(markers["Flask route"])
    content = content[:route_pos] + NEW_ROUTES + content[route_pos + len(markers["Flask route"]):]
    print("✅ [4/4] Routes added")

    APP_FILE.write_text(content, encoding="utf-8")
    print(f"\n✅ Patch complete")
    print(f"   Old: {len(backup.read_text(encoding='utf-8').splitlines())} lines")
    print(f"   New: {len(content.splitlines())} lines")
    return 0


if __name__ == "__main__":
    sys.exit(patch())