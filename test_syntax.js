const nf = new Intl.NumberFormat('en-US'), STORAGE = 'manafe_projects_archive_v3', NAV_STATE = 'manafe_nav_state', quarterLabels = ['Q1', 'Q2', 'Q3', 'Q4'], timelineColors = ['#A9847A', '#C9B08B', '#8D6E63', '#B08F7A', '#BFA58A']; let currentProjectId = null, aiGeneratedImages = [];
    const manafeLogoPath = 'manafe-logo.png';
    function toast(m) { const t = document.getElementById('toast'); t.textContent = m; t.style.display = 'block'; setTimeout(() => t.style.display = 'none', 2400) } function uid() { return 'p_' + Date.now() + '_' + Math.random().toString(16).slice(2) } function now() { return new Date().toISOString() } function money(n) { return nf.format(Math.round(Number(n) || 0)) } function num(id) { return Number(document.getElementById(id)?.value || 0) } function val(id) { return document.getElementById(id)?.value || '' } function lines(id) { return val(id).split('\n').map(x => x.trim()).filter(Boolean) }
    function saveNavState(page, extra) { localStorage.setItem(NAV_STATE, JSON.stringify({ page: page, extra: extra || null, ts: Date.now() })) } function getNavState() { try { return JSON.parse(localStorage.getItem(NAV_STATE)) } catch (e) { return null } } function clearNavState() { localStorage.removeItem(NAV_STATE) }
    function show(id) { ['homePage', 'archivePage', 'designerPage'].forEach(x => document.getElementById(x).classList.add('hidden')); document.getElementById(id).classList.remove('hidden') } function showHome() { show('homePage'); saveNavState('homePage') } function showArchive() { show('archivePage'); renderArchive(); saveNavState('archivePage') }
    function getProjects() { return JSON.parse(localStorage.getItem(STORAGE) || '[]') } function setProjects(a) { localStorage.setItem(STORAGE, JSON.stringify(a)) }
    function startNewProject() { currentProjectId = uid(); resetForm(); initNav(); show('designerPage'); document.getElementById('designerTitle').textContent = 'ØªØµÙ…ÙŠÙ… Ø¹Ø±Ø¶ Ù…Ø´Ø±ÙˆØ¹ Ø¬Ø¯ÙŠØ¯'; saveDraft(false); saveNavState('designerPage', { projectId: currentProjectId }) }
    function openProject(id) { const p = getProjects().find(x => x.id === id); if (!p) return toast('Ù„Ù… ÙŠØªÙ… Ø§Ù„Ø¹Ø«ÙˆØ± Ø¹Ù„Ù‰ Ø§Ù„Ù…Ø´Ø±ÙˆØ¹'); currentProjectId = id; resetForm(); loadDataToForm(p.data || {}); initNav(); show('designerPage'); document.getElementById('designerTitle').textContent = 'Ø£Ù†Ø´Ø§Ø¡: ' + (p.name || 'Ù…Ø´Ø±ÙˆØ¹'); saveNavState('designerPage', { projectId: currentProjectId }) }
    function upsertProject(status) { const data = collectData(); let arr = getProjects(); let p = arr.find(x => x.id === currentProjectId); if (!p) { p = { id: currentProjectId || uid(), createdAt: now() }; currentProjectId = p.id; arr.unshift(p) } p.name = data.projectName || 'Ù…Ø´Ø±ÙˆØ¹ Ø¨Ø¯ÙˆÙ† Ø§Ø³Ù…'; p.city = data.city; p.type = data.projectType; p.status = status || p.status || 'draft'; p.updatedAt = now(); p.data = data; setProjects(arr); return p }
    function saveDraft(showMsg = true) { if (!currentProjectId) currentProjectId = uid(); upsertProject('draft'); if (showMsg) toast('ØªÙ… Ø§Ù„Ø­ÙØ¸ ÙƒÙ…Ø³ÙˆØ¯Ø©') } function markGenerated() { upsertProject('generated') } function approveProject() { if (!currentProjectId) return toast('Ù„Ø§ ÙŠÙˆØ¬Ø¯ Ù…Ø´Ø±ÙˆØ¹ Ù…ÙØªÙˆØ­'); upsertProject('approved'); toast('ØªÙ… ØªØ¹Ù…ÙŠØ¯ Ø§Ù„Ù†Ø³Ø®Ø© ÙÙŠ Ø§Ù„Ø£Ø±Ø´ÙŠÙ') }
    function deleteProject(id) { if (!confirm('Ø­Ø°Ù Ø§Ù„Ù…Ø´Ø±ÙˆØ¹ Ù…Ù† Ø§Ù„Ø£Ø±Ø´ÙŠÙØŸ')) return; setProjects(getProjects().filter(x => x.id !== id)); renderArchive(); toast('ØªÙ… Ø­Ø°Ù Ø§Ù„Ù…Ø´Ø±ÙˆØ¹') } function deleteCurrentProject() { if (!currentProjectId) return showHome(); deleteProject(currentProjectId); showArchive() } function clearAllArchive() { if (!confirm('Ù‡Ù„ Ø£Ù†Øª Ù…ØªØ£ÙƒØ¯ Ù…Ù† Ù…Ø³Ø­ Ø¬Ù…ÙŠØ¹ Ø§Ù„Ù…Ø´Ø§Ø±ÙŠØ¹ Ù…Ù† Ø§Ù„Ø£Ø±Ø´ÙŠÙØŸ Ù„Ø§ ÙŠÙ…ÙƒÙ† Ø§Ù„ØªØ±Ø§Ø¬Ø¹ Ø¹Ù† Ù‡Ø°Ø§ Ø§Ù„Ø¥Ø¬Ø±Ø§Ø¡.')) return; setProjects([]); renderArchive(); toast('ØªÙ… Ù…Ø³Ø­ Ø¬Ù…ÙŠØ¹ Ø§Ù„Ù…Ø´Ø§Ø±ÙŠØ¹ Ù…Ù† Ø§Ù„Ø£Ø±Ø´ÙŠÙ') }
    function approveFromArchive(id) { const arr = getProjects(), p = arr.find(x => x.id === id); if (p) { p.status = 'approved'; p.updatedAt = now(); setProjects(arr); renderArchive(); toast('ØªÙ… ØªØ¹Ù…ÙŠØ¯ Ø§Ù„Ù…Ø´Ø±ÙˆØ¹') } }
    function renderArchive() { const q = (document.getElementById('archiveSearch')?.value || '').trim(), f = document.getElementById('archiveFilter')?.value || '', s = document.getElementById('archiveSort')?.value || 'newest'; let arr = getProjects(); if (q) arr = arr.filter(p => (p.name || '').includes(q)); if (f) arr = arr.filter(p => p.status === f); if (s === 'newest') arr.sort((a, b) => (b.updatedAt || '').localeCompare(a.updatedAt || '')); if (s === 'oldest') arr.sort((a, b) => (a.updatedAt || '').localeCompare(b.updatedAt || '')); if (s === 'name') arr.sort((a, b) => (a.name || '').localeCompare(b.name || '')); const el = document.getElementById('archiveList'); if (!arr.length) { el.innerHTML = '<p class="muted">Ù„Ø§ ØªÙˆØ¬Ø¯ Ù…Ø´Ø§Ø±ÙŠØ¹ Ù…Ø­ÙÙˆØ¸Ø© Ø­ØªÙ‰ Ø§Ù„Ø¢Ù†.</p>'; return } el.innerHTML = arr.map(p => { const st = p.status || 'draft', txt = st === 'draft' ? 'Ù…Ø³ÙˆØ¯Ø©' : st === 'generated' ? 'ØªÙ… ØªÙˆÙ„ÙŠØ¯ Ø§Ù„Ù…Ù„Ù' : 'Ù…Ø¹ØªÙ…Ø¯'; return `<div class="project-card"><span class="status ${st}">${txt}</span><h3>${p.name || 'Ù…Ø´Ø±ÙˆØ¹ Ø¨Ø¯ÙˆÙ† Ø§Ø³Ù…'}</h3><div class="project-meta">${p.type || ''} | ${p.city || ''}<br>Ø¢Ø®Ø± ØªØ­Ø¯ÙŠØ«: ${(p.updatedAt || '').slice(0, 16).replace('T', ' ')}</div><div class="card-actions"><button class="btn small primary" onclick="openProject('${p.id}')">ÙØªØ­ ÙˆØªØ¹Ø¯ÙŠÙ„</button><button class="btn small ghost" onclick="downloadProject('${p.id}')">ØªØ­Ù…ÙŠÙ„ Ø§Ù„Ù…Ù„Ù</button><button class="btn small green" onclick="approveFromArchive('${p.id}')">ØªØ¹Ù…ÙŠØ¯</button><button class="btn small danger" onclick="deleteProject('${p.id}')">Ø­Ø°Ù</button></div></div>` }).join('') }
    async function downloadProject(id) { const p = getProjects().find(x => x.id === id); if (!p) return; currentProjectId = id; resetForm(); loadDataToForm(p.data || {}); await generatePptx(false) }

    function initNav() { const nav = document.getElementById('nav'); nav.innerHTML = ''; const secs = [...document.querySelectorAll('#designerPage .section')]; secs.forEach((sec, i) => { const b = document.createElement('button'); b.innerHTML = `<span>${sec.dataset.title}</span><span>${i + 1}</span>`; b.onclick = () => showSection(i); if (i === 0) b.classList.add('active'); nav.appendChild(b); sec.classList.toggle('active', i === 0) }) }
    function showSection(i) { const secs = [...document.querySelectorAll('#designerPage .section')]; secs.forEach(s => s.classList.remove('active')); document.querySelectorAll('.nav button').forEach(b => b.classList.remove('active')); secs[i].classList.add('active'); document.querySelectorAll('.nav button')[i].classList.add('active'); calculate() }
    function resetForm() { document.querySelector('#componentsTable tbody').innerHTML = ''; document.querySelector('#timelineTable tbody').innerHTML = ''; document.querySelectorAll('#designerPage input[type="number"],#designerPage input[type="text"],#designerPage textarea').forEach(el => el.value = ''); document.querySelectorAll('#designerPage select').forEach(el => el.selectedIndex = 0); aiGeneratedImages = []; renderAIImages(); renderMiniTimeline(); calculate() }
    function addComponent(d = {}) { const tb = document.querySelector('#componentsTable tbody'), tr = document.createElement('tr'); tr.innerHTML = `<td><input value="${d.name || ''}" placeholder="Ù…Ø«Ø§Ù„: Ù…Ø¹Ø§Ø±Ø¶ ØªØ¬Ø§Ø±ÙŠØ©"></td><td><input type="number" value="${d.built || 0}"></td><td><input type="number" value="${d.leasable || 0}"></td><td><input type="number" value="${d.rent || 0}"></td><td><button class="btn danger small" onclick="this.closest('tr').remove();calculate()">Ø­Ø°Ù</button></td>`; tb.appendChild(tr); tr.querySelectorAll('input').forEach(x => x.addEventListener('input', calculate)); calculate() }
    function addTimelineRow(d = {}) { const tb = document.querySelector('#timelineTable tbody'), y = num('timelineStartYear') || 2026, tr = document.createElement('tr'); tr.innerHTML = `<td><input value="${d.name || ''}" placeholder="Ù…Ø«Ø§Ù„: Ù…Ø±Ø­Ù„Ø© Ø§Ù„Ø¨Ù†Ø§Ø¡"></td><td><input type="number" value="${d.startYear || y}"></td><td><select>${quarterLabels.map((q, i) => `<option value="${i + 1}" ${Number(d.startQuarter || 1) === i + 1 ? 'selected' : ''}>${q}</option>`).join('')}</select></td><td><input type="number" value="${d.endYear || y}"></td><td><select>${quarterLabels.map((q, i) => `<option value="${i + 1}" ${Number(d.endQuarter || 2) === i + 1 ? 'selected' : ''}>${q}</option>`).join('')}</select></td><td><select>${timelineColors.map(c => `<option value="${c}" ${d.color === c ? 'selected' : ''}>${c}</option>`).join('')}</select></td><td><button class="btn danger small" onclick="this.closest('tr').remove();renderMiniTimeline()">Ø­Ø°Ù</button></td>`; tb.appendChild(tr); tr.querySelectorAll('input,select').forEach(x => x.addEventListener('input', renderMiniTimeline)); renderMiniTimeline() }
    function components() { return [...document.querySelectorAll('#componentsTable tbody tr')].map(tr => { const i = tr.querySelectorAll('input'); return { name: i[0].value, built: Number(i[1].value || 0), leasable: Number(i[2].value || 0), rent: Number(i[3].value || 0) } }) }
    function timelineRows() { return [...document.querySelectorAll('#timelineTable tbody tr')].map(tr => { const i = tr.querySelectorAll('input,select'); return { name: i[0].value, startYear: Number(i[1].value || 0), startQuarter: Number(i[2].value || 1), endYear: Number(i[3].value || 0), endQuarter: Number(i[4].value || 1), color: i[5].value || '#A9847A' } }).filter(x => x.name) }
    function collectData() { return { projectName: val('projectName'), projectType: val('projectType'), city: val('city'), location: val('location'), idea: val('idea'), structure: val('structure'), developer: val('developer'), locationFeatures: lines('locationFeatures'), projectFeatures: lines('projectFeatures'), investmentHighlights: lines('investmentHighlights'), landArea: num('landArea'), buildingRatio: num('buildingRatio'), areaNote: val('areaNote'), components: components(), avgRent: num('avgRent'), serviceFees: num('serviceFees'), annualRevenue: num('annualRevenue'), annualOpex: num('annualOpex'), landCost: num('landCost'), developmentCost: num('developmentCost'), totalOperatingProfit: num('totalOperatingProfit'), exitValue: num('exitValue'), capRate: num('capRate'), annualROI: val('annualROI'), noiRate: val('noiRate'), payback: val('payback'), timelineStartYear: num('timelineStartYear'), timelineYearsCount: num('timelineYearsCount'), timelineTitle: val('timelineTitle'), timelineSubtitle: val('timelineSubtitle'), timelineRows: timelineRows(), risks: lines('risks'), recommendation: val('recommendation'), preparedBy: val('preparedBy'), contactInfo: val('contactInfo'), buildingName: val('buildingName'), aiImageStyle: val('aiImageStyle'), aiImagePrompt: val('aiImagePrompt'), aiGeneratedImages: aiGeneratedImages } }
    function loadDataToForm(d) { Object.keys(d).forEach(k => { const el = document.getElementById(k); if (el && !Array.isArray(d[k]) && typeof d[k] !== 'object') el.value = d[k] });['locationFeatures', 'projectFeatures', 'investmentHighlights', 'risks'].forEach(k => { if (d[k]) document.getElementById(k).value = d[k].join('\n') }); if (d.components) { document.querySelector('#componentsTable tbody').innerHTML = ''; d.components.forEach(addComponent) } if (d.timelineRows) { document.querySelector('#timelineTable tbody').innerHTML = ''; d.timelineRows.forEach(addTimelineRow) } aiGeneratedImages = d.aiGeneratedImages || []; renderAIImages(); calculate(); renderMiniTimeline() }
    function calculate() { const comps = components(), built = comps.reduce((a, x) => a + x.built, 0), leasable = comps.reduce((a, x) => a + x.leasable, 0), totalCost = num('landCost') + num('developmentCost'), totalProfit = num('totalOperatingProfit') + num('exitValue'); document.getElementById('mBuilt').textContent = money(built) + ' Ù…Â²'; document.getElementById('mLeasable').textContent = money(leasable) + ' Ù…Â²'; document.getElementById('mTotalCost').textContent = money(totalCost) + ' Ø±ÙŠØ§Ù„'; document.getElementById('mTotalProfit').textContent = money(totalProfit) + ' Ø±ÙŠØ§Ù„' } document.addEventListener('input', e => { if (e.target.closest('#designerPage')) calculate() });
    function quarterIndex(y, q) { return y * 4 + (q - 1) } function renderMiniTimeline() { const c = document.getElementById('miniTimeline'); if (!c) return; const start = num('timelineStartYear') || 2026, years = Math.max(1, Math.min(6, num('timelineYearsCount') || 3)), rows = timelineRows(), total = years * 4; let html = '<div class="mini-grid"><div class="mini-head-year"></div>'; for (let y = 0; y < years; y++)html += `<div class="mini-head-year" style="grid-column:span 4">${start + y}</div>`; html += '<div class="mini-head-q"></div>'; for (let y = 0; y < years; y++)quarterLabels.forEach(q => html += `<div class="mini-head-q">${q}</div>`); rows.forEach(r => { html += `<div class="mini-cell mini-label">${r.name}</div>`; for (let q = 0; q < total; q++)html += '<div class="mini-track"></div>' }); html += '</div>'; c.innerHTML = html; const grid = c.querySelector('.mini-grid'); rows.forEach((r, idx) => { const st = quarterIndex(r.startYear, r.startQuarter) - quarterIndex(start, 1), en = quarterIndex(r.endYear, r.endQuarter) - quarterIndex(start, 1); if (en < 0 || st > total - 1) return; const ss = Math.max(0, st), ee = Math.min(total - 1, en), bar = document.createElement('div'); bar.className = 'mini-bar'; bar.style.top = (80 + idx * 44 + 8) + 'px'; bar.style.left = (150 + ss * 80 + 4) + 'px'; bar.style.width = (((ee - ss + 1) * 80) - 8) + 'px'; bar.style.background = r.color; bar.textContent = r.name; grid.appendChild(bar) }) }
    async function fileToDataUri(id) { const f = document.getElementById(id)?.files?.[0]; if (!f) return null; return await new Promise(res => { const r = new FileReader(); r.onload = () => res(r.result); r.readAsDataURL(f) }) } async function fetchAssetDataUri(path) { const res = await fetch(path); const blob = await res.blob(); return await new Promise(res => { const r = new FileReader(); r.onload = () => res(r.result); r.readAsDataURL(blob) }) }
    function buildImagePrompt(i) { return `${val('aiImageStyle')}. ${val('aiImagePrompt')} Ø§Ø³Ù… Ø§Ù„Ù…Ø¨Ù†Ù‰ Ø§Ù„Ø¸Ø§Ù‡Ø± Ø¹Ù„Ù‰ Ø§Ù„ÙˆØ§Ø¬Ù‡Ø©: ${val('buildingName')}. Ù„Ù‚Ø·Ø© Ø±Ù‚Ù… ${i}. ÙÙˆØªÙˆØ±ÙŠØ§Ù„Ø³ØªÙƒØŒ Ø¬ÙˆØ¯Ø© Ø¹Ø§Ù„ÙŠØ©ØŒ ÙˆØ§Ø¬Ù‡Ø© Ù…Ø¹Ù…Ø§Ø±ÙŠØ© ÙˆØ§Ø¶Ø­Ø©ØŒ Ø¨Ø¯ÙˆÙ† Ù†ØµÙˆØµ Ø¥Ø¶Ø§ÙÙŠØ© ØºÙŠØ± Ø§Ø³Ù… Ø§Ù„Ù…Ø¨Ù†Ù‰.` }
    async function generateAIImages() {
      const prompts = [1, 2, 3, 4].map(buildImagePrompt);
      toast('Ø¬Ø§Ø±ÙŠ ØªÙˆÙ„ÙŠØ¯ Ø§Ù„ØµÙˆØ± Ø¨Ø§Ù„Ø°ÙƒØ§Ø¡ Ø§Ù„Ø§ØµØ·Ù†Ø§Ø¹ÙŠ...');
      try {
        const res = await fetch('/api/generate-images', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ prompts: prompts, buildingName: val('buildingName') })
        });
        if (res.ok) {
          const data = await res.json();
          if (data.success && data.images && data.images.length > 0) {
            aiGeneratedImages = data.images;
            renderAIImages();
            toast('ØªÙ… ØªÙˆÙ„ÙŠØ¯ ' + data.images.filter(function (x) { return x.url; }).length + ' ØµÙˆØ± Ø¨Ø§Ù„Ø°ÙƒØ§Ø¡ Ø§Ù„Ø§ØµØ·Ù†Ø§Ø¹ÙŠ');
            return;
          }
        }
        throw new Error('API failed');
      } catch (e) {
        toast('âŒ ÙØ´Ù„ ØªÙˆÙ„ÙŠØ¯ Ø§Ù„ØµÙˆØ±. ØªØ£ÙƒØ¯ Ù…Ù† Ø§ØªØµØ§Ù„ Ø§Ù„Ù€ Backend.');
      }
    }
    function generateImagePromptsOnly() { aiGeneratedImages = [1, 2, 3, 4].map((_, i) => ({ prompt: buildImagePrompt(i + 1), label: 'Prompt ' + (i + 1) })); renderAIImages(); showPrompts(); toast('ØªÙ… ØªÙˆÙ„ÙŠØ¯ Prompts Ø§Ù„ØµÙˆØ±') }
    function showPrompts() { const box = document.getElementById('promptBox'); box.classList.remove('hidden'); box.textContent = aiGeneratedImages.map((x, i) => `Prompt ${i + 1}: ${x.prompt || ''}`).join('\n\n') }
    function renderAIImages() { const el = document.getElementById('aiImages'); if (!el) return; const items = aiGeneratedImages.length ? aiGeneratedImages : []; el.innerHTML = items.length ? items.slice(0, 4).map((img, i) => `<div class="ai-img">${img.url ? `<img src="${img.url}">` : `<span>${(img.label || ('AI Image ' + (i + 1))).replace(/\\n/g, '<br>')}</span>`}</div>`).join('') : '<p class="muted" style="text-align:center;padding:20px">Ù„Ù… ÙŠØªÙ… ØªÙˆÙ„ÙŠØ¯ ØµÙˆØ± Ø¨Ø¹Ø¯</p>' }
    function addChat(type, text) { const log = document.getElementById('chatLog'), div = document.createElement('div'); div.className = 'msg ' + type; div.textContent = text; log.appendChild(div); log.scrollTop = log.scrollHeight }
    async function applyAIEdit() {
      const req = val('aiEditRequest').trim();
      if (!req) return toast('Ø§ÙƒØªØ¨ Ø·Ù„Ø¨ Ø§Ù„ØªØ¹Ø¯ÙŠÙ„ Ø£ÙˆÙ„Ø§Ù‹');
      addChat('user', req);
      try {
        const res = await fetch('/api/edit-deck-data', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ request: req, data: collectData() })
        });
        if (res.ok) {
          const out = await res.json();
          if (out.success && out.data) {
            loadDataToForm(out.data);
            addChat('ai', 'âœ… ØªÙ… ØªØ·Ø¨ÙŠÙ‚ Ø§Ù„ØªØ¹Ø¯ÙŠÙ„Ø§Øª Ø¨ÙˆØ§Ø³Ø·Ø© GLM5.1. ÙŠÙ…ÙƒÙ†Ùƒ Ø¥Ø¹Ø§Ø¯Ø© ØªÙˆÙ„ÙŠØ¯ Ø§Ù„Ù…Ù„Ù Ø§Ù„Ø¢Ù†.');
            saveDraft(false);
            return;
          } else {
            addChat('ai', 'âŒ ÙØ´Ù„ Ø§Ù„ØªØ¹Ø¯ÙŠÙ„: ' + (out.error || 'ØºÙŠØ± Ù…Ø¹Ø±ÙˆÙ'));
          }
        } else {
          const err = await res.json();
          addChat('ai', 'âŒ Ø®Ø·Ø£: ' + (err.error || 'ÙØ´Ù„ Ø§Ù„Ø§ØªØµØ§Ù„'));
        }
      } catch (e) {
        addChat('ai', 'âŒ Ø®Ø·Ø£ ÙÙŠ Ø§Ù„Ø§ØªØµØ§Ù„ Ø¨Ø§Ù„Ø®Ø§Ø¯Ù…: ' + e.message);
      }
    }

    let outlineData = [];

    // â”€â”€ Show Outline Page â”€â”€
    function showOutline() {
      document.getElementById('outlinePage').classList.remove('hidden');
      document.getElementById('designerPage').classList.add('hidden');
      document.getElementById('imageGenPage').classList.add('hidden');
      document.getElementById('genEditPage').classList.add('hidden');
      // If we already have outline data, show step 2
      if (outlineData.length > 0) {
        document.getElementById('outlineStep1').style.display = 'none';
        document.getElementById('outlineStep2').style.display = '';
        renderOutlineCards();
      } else {
        document.getElementById('outlineStep1').style.display = '';
        document.getElementById('outlineStep2').style.display = 'none';
      }
      saveNavState('outlinePage');
    }

    // â”€â”€ Show Designer â”€â”€
    function showDesigner() {
      document.getElementById('outlinePage').classList.add('hidden');
      document.getElementById('designerPage').classList.remove('hidden');
      document.getElementById('imageGenPage').classList.add('hidden');
      document.getElementById('genEditPage').classList.add('hidden');
      saveNavState('designerPage', { projectId: currentProjectId });
    }

    // â”€â”€ Generate Outline via AI â”€â”€
    async function generateOutlineAI() {
      var btn = document.getElementById('btnGenOutline');
      var status = document.getElementById('outlineStatus');
      btn.disabled = true;
      btn.textContent = 'â³ Ø¬Ø§Ø±ÙŠ ØªÙˆÙ„ÙŠØ¯ Ø§Ù„Ù‡ÙŠÙƒÙ„...';
      status.style.display = 'block';
      status.innerHTML = '<div style="padding:10px;background:#f0f7ff;border-radius:10px;color:#2c5f8a;font-size:13px"><div class="spinner" style="display:inline-block;width:14px;height:14px;border:2px solid #2c5f8a;border-top-color:transparent;border-radius:50%;animation:spin .8s linear infinite;vertical-align:middle;margin-left:8px"></div> Ø¬Ø§Ø±ÙŠ ØªÙˆÙ„ÙŠØ¯ Ù‡ÙŠÙƒÙ„ Ø§Ù„Ø¹Ø±Ø¶ Ø¨ÙˆØ§Ø³Ø·Ø© GLM 5.1...</div>';

      try {
        var res = await fetch('/api/generate-outline', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ projectData: collectData() })
        });
        var data = await res.json();
        if (data.success && data.outline && data.outline.length > 0) {
          outlineData = data.outline.map(function (s) {
            return { title: s.title || 'Ø´Ø±ÙŠØ­Ø©', bullets: Array.isArray(s.bullets) ? s.bullets : [] };
          });
          document.getElementById('outlineStep1').style.display = 'none';
          document.getElementById('outlineStep2').style.display = '';
          renderOutlineCards();
          toast('âœ… ØªÙ… ØªÙˆÙ„ÙŠØ¯ Ø§Ù„Ù‡ÙŠÙƒÙ„: ' + outlineData.length + ' Ø´Ø±ÙŠØ­Ø©');
          status.style.display = 'none';
        } else {
          throw new Error(data.error || 'No outline generated');
        }
      } catch (e) {
        status.innerHTML = '<div style="padding:10px;background:#fff3e0;border-radius:10px;color:#e65100;font-size:13px">âŒ ÙØ´Ù„ ØªÙˆÙ„ÙŠØ¯ Ø§Ù„Ù‡ÙŠÙƒÙ„: ' + e.message + '</div>';
        toast('âŒ ÙØ´Ù„ Ø§Ù„ØªÙˆÙ„ÙŠØ¯');
      }
      btn.disabled = false;
      btn.textContent = 'âœ¨ ØªÙˆÙ„ÙŠØ¯ Ø§Ù„Ù‡ÙŠÙƒÙ„ Ø¨Ø§Ù„Ù€ AI';
    }

    // â”€â”€ Toggle Outline Mode â”€â”€
    function toggleOutlineMode() {
      var mode = document.getElementById('outlineMode').value;
      var manualWrap = document.getElementById('manualTextWrap');
      if (mode === 'manual') {
        manualWrap.style.display = '';
      } else {
        manualWrap.style.display = 'none';
      }
    }

    // â”€â”€ Organize Manual Text via AI â”€â”€
    async function organizeManualText() {
      var rawText = document.getElementById('manualRawText').value.trim();
      if (!rawText) return toast('Ø§ÙƒØªØ¨ Ø§Ù„Ù†Øµ Ø£ÙˆÙ„Ø§Ù‹');
      var btn = document.getElementById('btnOrganize');
      btn.disabled = true;
      btn.textContent = 'â³ Ø¬Ø§Ø±ÙŠ Ø§Ù„ØªÙ†Ø¸ÙŠÙ…...';

      try {
        var res = await fetch('/api/organize-text', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            projectData: collectData(),
            rawText: rawText,
            outline: outlineData
          })
        });
        var data = await res.json();
        if (data.success && data.slides && data.slides.length > 0) {
          outlineData = data.slides.map(function (s) {
            return {
              title: s.title || 'Ø´Ø±ÙŠØ­Ø©',
              bullets: Array.isArray(s.bullets) ? s.bullets : [],
              missingInfo: s.missingInfo || ''
            };
          });
          renderOutlineCards();
          toast('âœ… ØªÙ… ØªÙ†Ø¸ÙŠÙ… Ø§Ù„Ù†Øµ Ø¹Ù„Ù‰ ' + outlineData.length + ' Ø´Ø±ÙŠØ­Ø©');
        } else {
          throw new Error(data.error || 'Failed to organize');
        }
      } catch (e) {
        toast('âŒ ÙØ´Ù„ Ø§Ù„ØªÙ†Ø¸ÙŠÙ…: ' + e.message);
      }
      btn.disabled = false;
      btn.textContent = 'ðŸ¤– ØªÙ†Ø¸ÙŠÙ… Ø§Ù„Ù†Øµ Ø¨Ø§Ù„Ù€ AI';
    }

    // â”€â”€ Render Outline Cards â”€â”€
    function renderOutlineCards() {
      var el = document.getElementById('outlineCards');
      el.innerHTML = outlineData.map(function (c, i) {
        var missingHtml = c.missingInfo ? '<div style="background:#fff3e0;border:1px solid #ffe0b2;border-radius:8px;padding:8px 12px;margin-top:8px;font-size:12px;color:#e65100">âš ï¸ Ù…Ø¹Ù„ÙˆÙ…Ø§Øª Ù†Ø§Ù‚ØµØ©: ' + c.missingInfo + '</div>' : '';
        return '<div class="outline-card" data-i="' + i + '">' +
          '<div class="card-head">' +
          '<span class="num">' + (i + 1) + '</span>' +
          '<div class="card-title" contenteditable="true" onblur="outlineData[' + i + '].title=this.textContent">' + c.title + '</div>' +
          '<button class="btn danger small" onclick="removeOutlineCard(' + i + ')" style="margin-right:auto;font-size:11px;padding:2px 8px">âœ•</button>' +
          '</div>' +
          '<ul class="card-bullets">' +
          c.bullets.map(function (b, j) {
            return '<li contenteditable="true" onblur="outlineData[' + i + '].bullets[' + j + ']=this.textContent">' + b + '</li>';
          }).join('') +
          '<li style="color:#bbb;cursor:pointer" onclick="addBulletToCard(' + i + ')">+ Ø¥Ø¶Ø§ÙØ© Ù†Ù‚Ø·Ø©</li>' +
          '</ul>' +
          missingHtml +
          '</div>';
      }).join('');
    }

    // â”€â”€ Add/Remove Bullet â”€â”€
    function addBulletToCard(i) { outlineData[i].bullets.push('Ù†Ù‚Ø·Ø© Ø¬Ø¯ÙŠØ¯Ø©'); renderOutlineCards(); }
    function removeOutlineCard(i) { outlineData.splice(i, 1); renderOutlineCards(); }

    // â”€â”€ Proceed from Outline to Content/Slides â”€â”€
    async function proceedFromOutline() {
      if (outlineData.length === 0) return toast('Ù‚Ù… Ø¨ØªÙˆÙ„ÙŠØ¯ Ø§Ù„Ù‡ÙŠÙƒÙ„ Ø£ÙˆÙ„Ø§Ù‹');
      var mode = document.getElementById('outlineMode').value;

      if (mode === 'ai') {
        // AI writes full content for all slides
        toast('Ø¬Ø§Ø±ÙŠ ØªÙˆÙ„ÙŠØ¯ Ø§Ù„Ù…Ø­ØªÙˆÙ‰ Ø§Ù„ÙƒØ§Ù…Ù„...');
        try {
          var res = await fetch('/api/generate-content', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              projectData: collectData(),
              outline: outlineData
            })
          });
          var data = await res.json();
          if (data.success && data.slides && data.slides.length > 0) {
            // Merge AI content with outline structure
            geSlidesData = data.slides.map(function (s, i) {
              return {
                icon: outlineData[i] ? getSlideIcon(i) : 'ðŸ“„',
                title: s.title || (outlineData[i] ? outlineData[i].title : 'Ø´Ø±ÙŠØ­Ø©'),
                content: s.content || '<div class="ge-slide-title">' + (s.title || 'Ø´Ø±ÙŠØ­Ø©') + '</div>'
              };
            });
            showGenEdit();
            toast('âœ… ØªÙ… ØªÙˆÙ„ÙŠØ¯ Ø§Ù„Ù…Ø­ØªÙˆÙ‰ Ù„Ù€ ' + geSlidesData.length + ' Ø´Ø±ÙŠØ­Ø©');
          } else {
            throw new Error(data.error || 'No content generated');
          }
        } catch (e) {
          toast('âŒ ÙØ´Ù„ ØªÙˆÙ„ÙŠØ¯ Ø§Ù„Ù…Ø­ØªÙˆÙ‰: ' + e.message);
        }
      } else {
        // Manual mode - use outline data as slides
        geSlidesData = outlineData.map(function (c, i) {
          var bulletsHtml = c.bullets.length > 0 ? '<ul>' + c.bullets.map(function (b) { return '<li>' + b + '</li>'; }).join('') + '</ul>' : '<p style="color:#aaa">Ù„Ù… ØªØªÙ… Ø¥Ø¶Ø§ÙØ© Ù†Ù‚Ø§Ø· Ø¨Ø¹Ø¯</p>';
          return {
            icon: getSlideIcon(i),
            title: c.title,
            content: '<div class="ge-slide-title">' + c.title + '</div><div class="ge-slide-body">' + bulletsHtml + '</div>'
          };
        });
        showGenEdit();
      }
    }

    // â”€â”€ Get slide icon by index â”€â”€
    function getSlideIcon(i) {
      var icons = ['ðŸ¢', 'ðŸ“Š', 'ðŸ’¡', 'ðŸ“', 'â­', 'ðŸ“', 'ðŸ’°', 'ðŸ—ï¸', 'ðŸ“ˆ', 'ðŸ“…', 'âš ï¸', 'ðŸŽ¨', 'ðŸ™'];
      return icons[i] || 'ðŸ“„';
    }
    function showImageGen() { const d = collectData(); document.getElementById('imageDescription').value = d.aiImagePrompt || ''; document.getElementById('imageGenPage').classList.remove('hidden'); document.getElementById('outlinePage').classList.add('hidden'); mainImageData = null; updateImagePageState(); saveNavState('imageGenPage') }
    function showOutlineFromImage() { document.getElementById('imageGenPage').classList.add('hidden'); document.getElementById('outlinePage').classList.remove('hidden'); saveNavState('outlinePage') }
    let mainImageData = null;
    function updateImagePageState() { const hasMain = !!mainImageData; document.getElementById('btnGenMain').disabled = false; document.getElementById('btnGeneratePptxFromImg').disabled = false; document.getElementById('mainImageActions').style.display = hasMain ? 'flex' : 'none' }
    async function generateMainImage() {
      const desc = document.getElementById('imageDescription').value.trim();
      if (!desc) return toast('Ø§ÙƒØªØ¨ ÙˆØµÙ Ø§Ù„Ù…Ø¨Ù†Ù‰ Ø£ÙˆÙ„Ø§Ù‹');
      const status = document.getElementById('imageStatus');
      status.style.display = 'block';
      status.innerHTML = '<div class="img-loading"><div class="spinner"></div>Ø¬Ø§Ø±ÙŠ ØªÙˆÙ„ÙŠØ¯ Ø§Ù„ØµÙˆØ±Ø© Ø§Ù„Ø£Ø³Ø§Ø³ÙŠØ© Ø¹Ø¨Ø± Gemini...</div>';
      document.getElementById('mainImageBox').innerHTML = '<div class="img-loading"><div class="spinner"></div>Ø¬Ø§Ø±ÙŠ Ø§Ù„ØªÙˆÙ„ÙŠØ¯...</div>';
      try {
        const res = await fetch('/api/generate-main-image', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ prompt: desc })
        });
        const data = await res.json();
        if (data.success && data.image) {
          mainImageData = data.image;
          document.getElementById('mainImageBox').innerHTML = '<img src="' + data.image + '" style="width:100%;height:100%;object-fit:cover">';
          status.innerHTML = 'âœ“ ØªÙ… ØªÙˆÙ„ÙŠØ¯ Ø§Ù„ØµÙˆØ±Ø© Ø¨Ù†Ø¬Ø§Ø­ Ø¹Ø¨Ø± Gemini Flash';
          status.style.background = '#e8f5e9';
          status.style.color = '#2e7d32';
          updateImagePageState();
        } else {
          throw new Error(data.error || 'No image generated');
        }
      } catch (e) {
        mainImageData = null;
        document.getElementById('mainImageBox').innerHTML = '<div style="padding:20px;text-align:center;color:#e65100">âš ï¸ ÙØ´Ù„ ØªÙˆÙ„ÙŠØ¯ Ø§Ù„ØµÙˆØ±Ø©: ' + e.message + '</div>';
        status.innerHTML = 'âŒ ÙØ´Ù„ Ø§Ù„ØªÙˆÙ„ÙŠØ¯: ' + e.message;
        status.style.background = '#fff3e0';
        status.style.color = '#e65100';
        updateImagePageState();
      }
    }
    function approveMainImage() { toast('ØªÙ…Øª Ø§Ù„Ù…ÙˆØ§ÙÙ‚Ø© Ø¹Ù„Ù‰ Ø§Ù„ØµÙˆØ±Ø© Ø§Ù„Ø£Ø³Ø§Ø³ÙŠØ©'); updateImagePageState() }
    function requestImageEdit() { document.getElementById('imageChatInput').focus() }
    async function sendImageEditRequest() {
      const input = document.getElementById('imageChatInput');
      const msg = input.value.trim();
      if (!msg) return;
      addImageChat('user', msg);
      input.value = '';
      try {
        const res = await fetch('/api/generate-slide-image', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ prompt: msg, referenceImage: mainImageData })
        });
        const data = await res.json();
        if (data.success && data.image) {
          mainImageData = data.image;
          document.getElementById('mainImageBox').innerHTML = '<img src="' + data.image + '" style="width:100%;height:100%;object-fit:cover">';
          addImageChat('ai', 'âœ… ØªÙ… ØªØ¹Ø¯ÙŠÙ„ Ø§Ù„ØµÙˆØ±Ø© Ø¨Ù†Ø¬Ø§Ø­ Ø¹Ø¨Ø± Gemini. ÙŠÙ…ÙƒÙ†Ùƒ Ø§Ù„Ø§Ø·Ù„Ø§Ø¹ Ø¹Ù„Ù‰ Ø§Ù„Ù†ØªÙŠØ¬Ø©.');
        } else {
          addImageChat('ai', 'âš ï¸ Ù„Ù… ÙŠØªÙ… ØªØ¹Ø¯ÙŠÙ„ Ø§Ù„ØµÙˆØ±Ø©. Ø­Ø§ÙˆÙ„ Ù…Ø±Ø© Ø£Ø®Ø±Ù‰ Ø£Ùˆ ØºÙŠÙ‘Ø± Ø§Ù„ÙˆØµÙ.');
        }
      } catch (e) {
        addImageChat('ai', 'âŒ Ø®Ø·Ø£ ÙÙŠ Ø§Ù„Ø§ØªØµØ§Ù„: ' + e.message);
      }
    }
    function addImageChat(type, text) { const log = document.getElementById('imageChatLog'); const div = document.createElement('div'); div.className = 'msg ' + type; div.textContent = text; log.appendChild(div); log.scrollTop = log.scrollHeight }
    /* ===== Gamma-style GenEdit Functions ===== */
    let geCurrentSlide = 0;
    let geSlidesData = [];
    function generateFromImagePage() { showGenEdit() }
    function showGenEdit() {
      document.getElementById('genEditPage').classList.remove('hidden');
      document.getElementById('imageGenPage').classList.add('hidden');
      geCurrentSlide = 0;
      saveNavState('genEditPage');
      buildGeSlidesData();
      renderGeSidebar();
      renderAllSlides();
      initGeScrollSync();
    }
    function showImageGenFromGenEdit() {
      document.getElementById('genEditPage').classList.add('hidden');
      document.getElementById('imageGenPage').classList.remove('hidden');
      saveNavState('imageGenPage');
    }
    function buildGeSlidesData() {
      const d = collectData();
      geSlidesData = [
        { icon: 'ðŸ¢', title: 'ØºÙ„Ø§Ù Ø§Ù„Ù…Ø´Ø±ÙˆØ¹', content: `<div class="ge-slide-title">${d.projectName || 'Ø§Ø³Ù… Ø§Ù„Ù…Ø´Ø±ÙˆØ¹'}</div><div class="ge-slide-subtitle">${d.projectType} | ${d.city}</div><div class="ge-slide-body">${d.location ? `<div>ðŸ“ ${d.location}</div>` : ''}</div>` },
        { icon: 'ðŸ“Š', title: 'Ø§Ù„Ù…Ù„Ø®Øµ Ø§Ù„ØªÙ†ÙÙŠØ°ÙŠ', content: `<div class="ge-slide-title">Ø§Ù„Ù…Ù„Ø®Øµ Ø§Ù„ØªÙ†ÙÙŠØ°ÙŠ</div><div class="ge-slide-subtitle">${d.projectName || ''}</div><div class="ge-slide-body">${d.recommendation || ''}</div><div class="ge-slide-metrics"><div class="ge-metric"><div class="ge-metric-label">Ø¥Ø¬Ù…Ø§Ù„ÙŠ Ø§Ù„ØªÙƒÙ„ÙØ©</div><div class="ge-metric-value">${money(d.landCost + d.developmentCost)} Ø±ÙŠØ§Ù„</div></div><div class="ge-metric"><div class="ge-metric-label">Ø§Ù„Ø¥ÙŠØ±Ø§Ø¯Ø§Øª Ø§Ù„Ø³Ù†ÙˆÙŠØ©</div><div class="ge-metric-value">${money(d.annualRevenue)} Ø±ÙŠØ§Ù„</div></div><div class="ge-metric"><div class="ge-metric-label">Ø§Ù„Ø¹Ø§Ø¦Ø¯ Ø§Ù„Ù…ØªÙˆÙ‚Ø¹</div><div class="ge-metric-value">${d.annualROI}</div></div></div>` },
        { icon: 'ðŸ’¡', title: 'ÙÙƒØ±Ø© Ø§Ù„Ù…Ø´Ø±ÙˆØ¹ ÙˆØ§Ù„Ù‡ÙŠÙƒÙ„Ø©', content: `<div class="ge-slide-title">ÙÙƒØ±Ø© Ø§Ù„Ù…Ø´Ø±ÙˆØ¹ ÙˆØ§Ù„Ù‡ÙŠÙƒÙ„Ø©</div><div class="ge-slide-metrics"><div class="ge-metric"><div class="ge-metric-label">Ø§Ù„ÙÙƒØ±Ø©</div><div class="ge-metric-value" style="font-size:14px">${d.idea || '-'}</div></div><div class="ge-metric"><div class="ge-metric-label">Ø§Ù„Ù‡ÙŠÙƒÙ„Ø©</div><div class="ge-metric-value" style="font-size:14px">${d.structure || '-'}</div></div><div class="ge-metric"><div class="ge-metric-label">Ø§Ù„Ù…Ø·ÙˆØ±</div><div class="ge-metric-value" style="font-size:14px">${d.developer || '-'}</div></div></div>` },
        { icon: 'ðŸ“', title: 'Ù…Ù…ÙŠØ²Ø§Øª Ø§Ù„Ù…ÙˆÙ‚Ø¹', content: `<div class="ge-slide-title">Ù…Ù…ÙŠØ²Ø§Øª Ø§Ù„Ù…ÙˆÙ‚Ø¹</div><div class="ge-slide-body"><ul>${(d.locationFeatures.length ? d.locationFeatures : ['Ø£Ø¯Ø®Ù„ Ù…Ù…ÙŠØ²Ø§Øª Ø§Ù„Ù…ÙˆÙ‚Ø¹']).map(f => `<li>${f}</li>`).join('')}</ul></div>` },
        { icon: 'â­', title: 'Ù…Ù…ÙŠØ²Ø§Øª Ø§Ù„Ù…Ø´Ø±ÙˆØ¹', content: `<div class="ge-slide-title">Ù…Ù…ÙŠØ²Ø§Øª Ø§Ù„Ù…Ø´Ø±ÙˆØ¹</div><div class="ge-slide-body"><ul>${(d.projectFeatures.length ? d.projectFeatures : ['Ø£Ø¯Ø®Ù„ Ù…Ù…ÙŠØ²Ø§Øª Ø§Ù„Ù…Ø´Ø±ÙˆØ¹']).map(f => `<li>${f}</li>`).join('')}</ul></div>` },
        { icon: 'ðŸ“', title: 'Ù…ÙƒÙˆÙ†Ø§Øª Ø§Ù„Ù…Ø´Ø±ÙˆØ¹ ÙˆØ§Ù„Ù…Ø³Ø§Ø­Ø§Øª', content: `<div class="ge-slide-title">Ù…ÙƒÙˆÙ†Ø§Øª Ø§Ù„Ù…Ø´Ø±ÙˆØ¹ ÙˆØ§Ù„Ù…Ø³Ø§Ø­Ø§Øª</div><div class="ge-slide-metrics">${d.components.map(c => `<div class="ge-metric"><div class="ge-metric-label">${c.name}</div><div class="ge-metric-value" style="font-size:14px">${money(c.built)} Ù…Â²</div></div>`).join('')}</div>` },
        { icon: 'ðŸ’°', title: 'Ø§Ù„Ø±Ø¨Ø­ Ø§Ù„ØªØ´ØºÙŠÙ„ÙŠ', content: `<div class="ge-slide-title">Ø§Ù„Ø±Ø¨Ø­ Ø§Ù„ØªØ´ØºÙŠÙ„ÙŠ Ø§Ù„ØªØ£Ø¬ÙŠØ±ÙŠ</div><div class="ge-slide-metrics"><div class="ge-metric"><div class="ge-metric-label">Ø¥ÙŠØ¬Ø§Ø± Ø§Ù„Ù…ØªØ±</div><div class="ge-metric-value">${money(d.avgRent)}</div></div><div class="ge-metric"><div class="ge-metric-label">Ø§Ù„Ø¥ÙŠØ±Ø§Ø¯Ø§Øª Ø§Ù„Ø³Ù†ÙˆÙŠØ©</div><div class="ge-metric-value">${money(d.annualRevenue)}</div></div><div class="ge-metric"><div class="ge-metric-label">Ø§Ù„Ù…ØµØ±ÙˆÙ Ø§Ù„ØªØ´ØºÙŠÙ„ÙŠ</div><div class="ge-metric-value">${money(d.annualOpex)}</div></div></div>` },
        { icon: 'ðŸ—ï¸', title: 'Ø§Ù„ØªÙƒØ§Ù„ÙŠÙ', content: `<div class="ge-slide-title">Ø§ÙØªØ±Ø§Ø¶Ø§Øª Ø§Ù„ØªÙƒØ§Ù„ÙŠÙ</div><div class="ge-slide-metrics"><div class="ge-metric"><div class="ge-metric-label">ØªÙƒÙ„ÙØ© Ø§Ù„Ø£Ø±Ø¶</div><div class="ge-metric-value">${money(d.landCost)} Ø±ÙŠØ§Ù„</div></div><div class="ge-metric"><div class="ge-metric-label">ØªÙƒÙ„ÙØ© Ø§Ù„ØªØ·ÙˆÙŠØ±</div><div class="ge-metric-value">${money(d.developmentCost)} Ø±ÙŠØ§Ù„</div></div><div class="ge-metric"><div class="ge-metric-label">Ø§Ù„Ø¥Ø¬Ù…Ø§Ù„ÙŠ</div><div class="ge-metric-value">${money(d.landCost + d.developmentCost)} Ø±ÙŠØ§Ù„</div></div></div>` },
        { icon: 'ðŸ“ˆ', title: 'Ø§Ù„Ø£Ø±Ø¨Ø§Ø­ ÙˆØ§Ù„ØªØ®Ø§Ø±Ø¬', content: `<div class="ge-slide-title">Ø§Ù„Ø£Ø±Ø¨Ø§Ø­ ÙˆØ§Ù„ØªØ®Ø§Ø±Ø¬</div><div class="ge-slide-metrics"><div class="ge-metric"><div class="ge-metric-label">Ø§Ù„Ø±Ø¨Ø­ Ø§Ù„ØªØ´ØºÙŠÙ„ÙŠ</div><div class="ge-metric-value">${money(d.totalOperatingProfit)} Ø±ÙŠØ§Ù„</div></div><div class="ge-metric"><div class="ge-metric-label">Ù‚ÙŠÙ…Ø© Ø§Ù„ØªØ®Ø§Ø±Ø¬</div><div class="ge-metric-value">${money(d.exitValue)} Ø±ÙŠØ§Ù„</div></div><div class="ge-metric"><div class="ge-metric-label">Ù…Ø¹Ø§Ù…Ù„ Ø§Ù„Ø±Ø³Ù…Ù„Ø©</div><div class="ge-metric-value">${d.capRate}%</div></div></div>` },
        { icon: 'ðŸ“…', title: 'Ø§Ù„Ø¬Ø¯ÙˆÙ„ Ø§Ù„Ø²Ù…Ù†ÙŠ', content: `<div class="ge-slide-title">Ø§Ù„Ø¬Ø¯ÙˆÙ„ Ø§Ù„Ø²Ù…Ù†ÙŠ ÙˆÙ…Ø±Ø§Ø­Ù„ Ø§Ù„Ù…Ø´Ø±ÙˆØ¹</div><div class="ge-slide-body"><ul>${(d.timelineRows || []).map(r => `<li>${r.name}: Q${r.startQuarter} ${r.startYear} â†’ Q${r.endQuarter} ${r.endYear}</li>`).join('')}</ul></div>` },
        { icon: 'âš ï¸', title: 'Ø§Ù„Ù…Ø®Ø§Ø·Ø±', content: `<div class="ge-slide-title">Ø§Ù„Ù…Ø®Ø§Ø·Ø± ÙˆØ§Ù„Ø§ÙØªØ±Ø§Ø¶Ø§Øª</div><div class="ge-slide-body"><ul>${(d.risks.length ? d.risks : ['Ø£Ø¯Ø®Ù„ Ø§Ù„Ù…Ø®Ø§Ø·Ø±']).map(r => `<li>${r}</li>`).join('')}</ul></div>` },
        { icon: 'ðŸŽ¨', title: 'Ø§Ù„Ù…ÙˆØ¯ Ø¨ÙˆØ±Ø¯ + Ø´ÙƒØ±Ø§Ù‹', content: `<div class="ge-slide-title">Ø§Ù„Ù…ÙˆØ¯ Ø¨ÙˆØ±Ø¯ Ø¨Ø§Ù„Ø°ÙƒØ§Ø¡ Ø§Ù„Ø§ØµØ·Ù†Ø§Ø¹ÙŠ</div><div class="ge-slide-subtitle">${d.buildingName || ''}</div><div class="ge-slide-body">${d.aiImagePrompt || ''}</div>` }
      ];
    }
    function renderGeSidebar() {
      const el = document.getElementById('geSidebar');
      // Thumbnail = exact same card as main, just CSS-scaled down
      el.innerHTML = geSlidesData.map((s, i) => `
        <div class="ge-thumb ${i === geCurrentSlide ? 'active' : ''}" onclick="geGoToSlide(${i})">
          <div class="ge-thumb-preview">
            <div class="ge-thumb-inner">
              <div class="ge-slide-card" data-thumb="1">
                <div class="ge-slide-number">${i + 1}</div>
                <div class="ge-slide-inner">${s.content}</div>
              </div>
            </div>
          </div>
          <div class="ge-thumb-content">
            <span class="ge-thumb-num">${i + 1}</span>
            <span class="ge-thumb-title">${s.title}</span>
          </div>
        </div>
      `).join('');
    }
    function renderAllSlides() {
      const el = document.getElementById('geMainScroll');
      el.innerHTML = geSlidesData.map((s, i) => {
        const sep = i > 0 ? '<div class="ge-slide-separator"></div>' : '';
        return `${sep}<div class="ge-slide-card ${i === geCurrentSlide ? 'active-slide' : ''}" id="geSlide${i}" onclick="geGoToSlide(${i})" data-idx="${i}">
          <div class="ge-slide-number">${i + 1}</div>
          <button class="ge-ai-btn" onclick="event.stopPropagation();openAiEditModal(${i},this)">
            <svg viewBox="0 0 24 24" fill="currentColor" width="16" height="16"><path d="M12 2L9.19 8.63 2 9.24l5.46 4.73L5.82 21 12 17.27 18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2z"/></svg>
            AI Edit
          </button>
          <div class="ge-slide-inner" contenteditable="true" onfocus="event.stopPropagation()" onblur="event.stopPropagation();geSaveSlideContent(${i},this.innerHTML)">${s.content}</div>
        </div>`;
      }).join('');
    }
    function geSaveSlideContent(idx, html) { geSlidesData[idx].content = html; }
    function renderGeSlide(idx) {
      geCurrentSlide = idx;
      renderGeSidebar();
      document.querySelectorAll('.ge-slide-card').forEach((c, i) => {
        c.classList.toggle('active-slide', i === idx);
      });
      const s = geSlidesData[idx];
      // Update panel subtitle if open
      const sub = document.getElementById('gePanelSub');
      if (sub) sub.textContent = 'Ø§Ù„Ø³Ù„Ø§ÙŠØ¯ Ø§Ù„Ø­Ø§Ù„ÙŠ: ' + s.title + ' (' + s.icon + ')';
      // Scroll to slide
      const slide = document.getElementById('geSlide' + idx);
      if (slide) {
        const container = document.getElementById('geMainScroll');
        const offset = slide.offsetTop - container.offsetTop - 20;
        container.scrollTo({ top: offset, behavior: 'smooth' });
      }
      // Scroll active thumb into view
      const activeThumb = document.querySelector('.ge-thumb.active');
      if (activeThumb) activeThumb.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
    function geGoToSlide(idx) { renderGeSlide(idx) }
    /* Open floating AI edit popup next to the AI Edit button */
    function openAiEditModal(slideIdx, btnEl) {
      if (typeof slideIdx === 'number') geCurrentSlide = slideIdx;
      const popup = document.getElementById('geFloatPopup');
      const input = document.getElementById('geFloatInput');
      if (!popup || !input) return;
      popup.classList.add('active');
      input.value = '';
      input.focus();
      // Position popup near the clicked button
      if (btnEl) {
        const rect = btnEl.getBoundingClientRect();
        const popW = 320;
        let top = rect.bottom + 8;
        let left = rect.left;
        // Keep within viewport
        if (left + popW > window.innerWidth) left = window.innerWidth - popW - 12;
        if (left < 12) left = 12;
        if (top + 300 > window.innerHeight) top = rect.top - 300 - 8;
        popup.style.top = top + 'px';
        popup.style.left = left + 'px';
      }
      // Update subtitle to show current slide
      document.getElementById('gePanelSub').textContent = 'Ø§Ù„Ø³Ù„Ø§ÙŠØ¯ Ø§Ù„Ø­Ø§Ù„ÙŠ: ' + geSlidesData[geCurrentSlide].title;
      // Scroll chat log to bottom
      const log = document.getElementById('geChatLog');
      if (log) log.scrollTop = log.scrollHeight;
    }
    function closeAiEditModal() {
      const popup = document.getElementById('geFloatPopup');
      if (popup) popup.classList.remove('active');
    }
    // Close popup when clicking outside
    document.addEventListener('click', function (e) {
      const popup = document.getElementById('geFloatPopup');
      if (!popup || !popup.classList.contains('active')) return;
      if (popup.contains(e.target)) return;
      if (e.target.closest('.ge-ai-btn')) return;
      closeAiEditModal();
    });
    /* Smart edit: detects if request is about image or content */
    async function applyGeSmartEdit() {
      const input = document.getElementById('geFloatInput');
      const msg = input.value.trim();
      if (!msg) return toast('Ø§ÙƒØªØ¨ Ø·Ù„Ø¨ Ø§Ù„ØªØ¹Ø¯ÙŠÙ„ Ø£ÙˆÙ„Ø§Ù‹');
      const title = geSlidesData[geCurrentSlide].title;
      const imageKeywords = ['ØµÙˆØ±Ø©', 'ØµÙˆØ±', 'image', 'Ø§Ù„ØºÙ„Ø§Ù', 'Ø§Ù„ÙˆØ§Ø¬Ù‡Ø©', 'Ø§Ù„foto', 'Ø§Ù„ØµÙˆØ±Ø©', 'Ø§Ù„Ø´ÙƒÙ„', 'ØªÙˆÙ„ÙŠØ¯', 'generate', 'ØºÙŠØ± Ø§Ù„ØµÙˆØ±Ø©', 'ØºÙŠÙ‘Ø± Ø§Ù„ØµÙˆØ±Ø©'];
      const isImage = imageKeywords.some(k => msg.includes(k));
      if (isImage) {
        addGeChat('user', 'ðŸ–¼ [' + title + '] ' + msg);
        input.value = '';
        try {
          const res = await fetch('/api/generate-slide-image', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt: 'ØµÙˆØ±Ø© ' + title + ' - ' + msg })
          });
          const data = await res.json();
          if (data.success && data.image) {
            addGeChat('ai', 'âœ… ØªÙ… ØªÙˆÙ„ÙŠØ¯ Ø§Ù„ØµÙˆØ±Ø© Ø¨Ù†Ø¬Ø§Ø­ Ø¹Ø¨Ø± Gemini.\n\nðŸ’¬ ÙŠÙ…ÙƒÙ†Ùƒ Ø§Ù„Ø§Ø·Ù„Ø§Ø¹ Ø¹Ù„Ù‰ Ø§Ù„Ù†ØªÙŠØ¬Ø© Ø£Ùˆ Ø·Ù„Ø¨ ØªØ¹Ø¯ÙŠÙ„ Ø¥Ø¶Ø§ÙÙŠ.');
            toast('ØªÙ… ØªÙˆÙ„ÙŠØ¯ Ø§Ù„ØµÙˆØ±Ø© Ø¨Ù†Ø¬Ø§Ø­');
          } else {
            addGeChat('ai', 'âš ï¸ Ù„Ù… ÙŠØªÙ… ØªÙˆÙ„ÙŠØ¯ Ø§Ù„ØµÙˆØ±Ø©. Ø­Ø§ÙˆÙ„ Ù…Ø±Ø© Ø£Ø®Ø±Ù‰ Ø£Ùˆ ØºÙŠÙ‘Ø± Ø§Ù„ÙˆØµÙ.');
          }
        } catch (e) {
          addGeChat('ai', 'âŒ Ø®Ø·Ø£ ÙÙŠ Ø§Ù„Ø§ØªØµØ§Ù„ Ø¨Ø§Ù„Ø®Ø§Ø¯Ù…: ' + e.message);
        }
      } else {
        addGeChat('user', 'âœï¸ [' + title + '] ' + msg);
        input.value = '';
        try {
          const res = await fetch('/api/ai-edit-slide', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              slideTitle: title,
              slideContent: geSlidesData[geCurrentSlide].content,
              editRequest: msg,
              projectData: collectData()
            })
          });
          const data = await res.json();
          if (data.success && data.data) {
            const edited = data.data;
            if (edited.title) geSlidesData[geCurrentSlide].title = edited.title;
            if (edited.content) geSlidesData[geCurrentSlide].content = edited.content;
            if (edited.bullets) {
              geSlidesData[geCurrentSlide].content = '<div class="ge-slide-title">' + (edited.title || title) + '</div><div class="ge-slide-body"><ul>' + edited.bullets.map(b => '<li>' + b + '</li>').join('') + '</ul></div>';
            }
            renderAllSlides();
            renderGeSidebar();
            renderGeSlide(geCurrentSlide);
            addGeChat('ai', 'âœ… ØªÙ… ØªØ¹Ø¯ÙŠÙ„ "' + (edited.title || title) + '" Ø¨ÙˆØ§Ø³Ø·Ø© GLM5.1.\n\nðŸ’¬ ÙŠÙ…ÙƒÙ†Ùƒ Ø§Ù„Ù…ØªØ§Ø¨Ø¹Ø© Ø¨Ø§Ù„ØªØ¹Ø¯ÙŠÙ„ Ø£Ùˆ Ø§Ø¶ØºØ· "Ø¥Ø¹Ø§Ø¯Ø© ØªÙˆÙ„ÙŠØ¯" Ù„ØªØ·Ø¨ÙŠÙ‚ Ø§Ù„ØªØºÙŠÙŠØ±Ø§Øª.');
          } else {
            addGeChat('ai', 'âŒ Ø­Ø¯Ø« Ø®Ø·Ø£ Ø£Ø«Ù†Ø§Ø¡ Ø§Ù„ØªØ¹Ø¯ÙŠÙ„: ' + (data.error || 'ØºÙŠØ± Ù…Ø¹Ø±ÙˆÙ'));
          }
        } catch (e) {
          addGeChat('ai', 'âŒ Ø®Ø·Ø£ ÙÙŠ Ø§Ù„Ø§ØªØµØ§Ù„ Ø¨Ø§Ù„Ø®Ø§Ø¯Ù…: ' + e.message);
        }
      }
    }
    /* Handle suggestion chip click */
    function useSuggestion(text) {
      const input = document.getElementById('geFloatInput');
      input.value = text;
      input.focus();
    }
    function applyGeContentEdit() {
      applyGeSmartEdit();
    }
    async function applyGeImageEdit() {
      const input = document.getElementById('geFloatInput');
      const msg = input.value.trim() || 'Ø£Ø¹Ø¯ ØªÙˆÙ„ÙŠØ¯ ØµÙˆØ±Ø© Ù‡Ø°Ø§ Ø§Ù„Ø³Ù„Ø§ÙŠØ¯';
      addGeChat('user', 'ðŸ–¼ [' + geSlidesData[geCurrentSlide].title + '] ' + msg);
      input.value = '';
      try {
        const res = await fetch('/api/generate-slide-image', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ prompt: msg + ' - ' + geSlidesData[geCurrentSlide].title })
        });
        const data = await res.json();
        if (data.success && data.image) {
          addGeChat('ai', 'âœ… ØªÙ… ØªÙˆÙ„ÙŠØ¯ Ø§Ù„ØµÙˆØ±Ø© Ø¨Ù†Ø¬Ø§Ø­ Ø¹Ø¨Ø± Gemini.\n\nðŸ’¬ ÙŠÙ…ÙƒÙ†Ùƒ Ø§Ù„Ø§Ø·Ù„Ø§Ø¹ Ø¹Ù„Ù‰ Ø§Ù„Ù†ØªÙŠØ¬Ø© Ø£Ùˆ Ø·Ù„Ø¨ ØªØ¹Ø¯ÙŠÙ„ Ø¥Ø¶Ø§ÙÙŠ.');
          toast('ØªÙ… ØªÙˆÙ„ÙŠØ¯ Ø§Ù„ØµÙˆØ±Ø© Ø¨Ù†Ø¬Ø§Ø­');
        } else {
          addGeChat('ai', 'âš ï¸ Ù„Ù… ÙŠØªÙ… ØªÙˆÙ„ÙŠØ¯ Ø§Ù„ØµÙˆØ±Ø©. Ø­Ø§ÙˆÙ„ Ù…Ø±Ø© Ø£Ø®Ø±Ù‰.');
        }
      } catch (e) {
        addGeChat('ai', 'âŒ Ø®Ø·Ø£ ÙÙŠ Ø§Ù„Ø§ØªØµØ§Ù„ Ø¨Ø§Ù„Ø®Ø§Ø¯Ù…: ' + e.message);
      }
    }
    async function applyGeChatEdit() {
      const input = document.getElementById('geChatInput');
      const msg = input.value.trim();
      if (!msg) return toast('Ø§ÙƒØªØ¨ Ø·Ù„Ø¨ Ø§Ù„ØªØ¹Ø¯ÙŠÙ„ Ø£ÙˆÙ„Ø§Ù‹');
      addGeChat('user', msg);
      input.value = '';
      try {
        const res = await fetch('/api/ai-chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            message: msg,
            slidesData: geSlidesData,
            currentSlideIdx: geCurrentSlide,
            projectData: collectData()
          })
        });
        const data = await res.json();
        if (data.success && data.data) {
          const result = data.data;
          if (result.action === 'edit' && typeof result.slideIdx === 'number') {
            const idx = result.slideIdx;
            if (result.changes) {
              if (result.changes.title) geSlidesData[idx].title = result.changes.title;
              if (result.changes.content) geSlidesData[idx].content = result.changes.content;
              renderAllSlides();
              renderGeSidebar();
              renderGeSlide(geCurrentSlide);
            }
            addGeChat('ai', 'âœ… ØªÙ… ØªØ¹Ø¯ÙŠÙ„ Ø§Ù„Ø´Ø±ÙŠØ­Ø© Ø±Ù‚Ù… ' + (idx + 1) + ' Ø¨ÙˆØ§Ø³Ø·Ø© GLM5.1.');
          } else {
            addGeChat('ai', 'âœ¨ ' + (result.response || msg));
          }
        } else {
          addGeChat('ai', 'âŒ Ø­Ø¯Ø« Ø®Ø·Ø£: ' + (data.error || 'ØºÙŠØ± Ù…Ø¹Ø±ÙˆÙ'));
        }
      } catch (e) {
        addGeChat('ai', 'âŒ Ø®Ø·Ø£ ÙÙŠ Ø§Ù„Ø§ØªØµØ§Ù„ Ø¨Ø§Ù„Ø®Ø§Ø¯Ù…: ' + e.message);
      }
    }
    function addGeChat(type, text) {
      const log = document.getElementById('geChatLog');
      // Hide empty state on first message
      const empty = document.getElementById('geChatEmpty');
      if (empty) empty.remove();
      const div = document.createElement('div');
      div.className = 'ge-chat-msg ' + type;
      div.innerHTML = text.replace(/\n/g, '<br>');
      log.appendChild(div);
      log.scrollTop = log.scrollHeight;
    }
    // Scroll sync: highlight sidebar + current slide as user scrolls
    function initGeScrollSync() {
      const container = document.getElementById('geMainScroll');
      if (!container) return;
      const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            const idx = Number(entry.target.dataset.idx);
            if (!isNaN(idx)) {
              geCurrentSlide = idx;
              document.querySelectorAll('.ge-slide-card').forEach((c, i) => c.classList.toggle('active-slide', i === idx));
              renderGeSidebar();
            }
          }
        });
      }, { root: container, threshold: 0.5 });
      setTimeout(() => {
        document.querySelectorAll('.ge-main .ge-slide-card').forEach(card => observer.observe(card));
      }, 100);
    }
    // Keyboard navigation when genEditPage is open
    document.addEventListener('keydown', function (e) {
      if (document.getElementById('genEditPage').classList.contains('hidden')) return;
      // Don't navigate if typing in an input
      if (document.activeElement && (document.activeElement.tagName === 'TEXTAREA' || document.activeElement.tagName === 'INPUT')) return;
      if (e.key === 'ArrowUp' || e.key === 'ArrowRight') {
        e.preventDefault();
        if (geCurrentSlide > 0) geGoToSlide(geCurrentSlide - 1);
      } else if (e.key === 'ArrowDown' || e.key === 'ArrowLeft') {
        e.preventDefault();
        if (geCurrentSlide < geSlidesData.length - 1) geGoToSlide(geCurrentSlide + 1);
      }
    });
    async function generatePptxFromGenEdit() { showDesigner(); await generatePptx() }
    async function exportPdfFromGenEdit() { showDesigner(); await exportToPdf() }

    function addText(slide, text, x, y, w, h, opts = {}) { slide.addText(text, { x, y, w, h, fontFace: 'Arial', lang: 'ar-SA', rtl: true, fit: 'shrink', margin: .06, ...opts }) } function addTitle(slide, title, subtitle) { addText(slide, title, .55, .35, 12.2, .55, { fontSize: 25, bold: true, color: '7A0C0C', align: 'right' }); if (subtitle) addText(slide, subtitle, .55, .88, 12.2, .35, { fontSize: 11, color: '777777', align: 'right' }); slide.addShape(pptx.ShapeType.line, { x: .55, y: 1.28, w: 12.2, h: 0, line: { color: '7A0C0C', width: 1.2 } }) }
    function addFooter(slide, d, n, logo) { if (logo) slide.addImage({ data: logo, x: .45, y: 6.63, w: .75, h: .45 }); addText(slide, d.preparedBy || '', 1.25, 6.9, 4, .25, { fontSize: 8, color: '999999' }); slide.addShape(pptx.ShapeType.roundRect, { x: 12.22, y: 6.88, w: .42, h: .26, rectRadius: .04, fill: { color: '7A0C0C' }, line: { color: '7A0C0C' } }); addText(slide, String(n), 12.22, 6.89, .42, .22, { fontSize: 9, color: 'FFFFFF', align: 'center' }) }
    function addMetric(slide, label, value, x, y, w, h = .75) { slide.addShape(pptx.ShapeType.roundRect, { x, y, w, h, rectRadius: .08, fill: { color: 'FBF7F4' }, line: { color: 'E7E0DC' } }); addText(slide, label, x + .15, y + .1, w - .3, .18, { fontSize: 8, color: '777777', bold: true }); addText(slide, value, x + .15, y + .3, w - .3, h - .34, { fontSize: 15, color: '7A0C0C', bold: true }) } function addBullets(slide, arr, x, y, w, h) { addText(slide, arr.map(a => 'â€¢ ' + a).join('\n'), x, y, w, h, { fontSize: 16, color: '444444', valign: 'top' }) }
    function addTable(slide, rows, x, y, w, h, colW) { const tableData = rows.map((r, idx) => r.map(c => ({ text: String(c), options: { rtl: true, bold: idx === 0, color: idx === 0 ? 'FFFFFF' : '555555', fill: idx === 0 ? { color: '7A0C0C' } : { color: 'FFFFFF' }, fontSize: idx === 0 ? 9 : 8, align: 'center', valign: 'mid' } }))); slide.addTable(tableData, { x, y, w, h, border: { type: 'solid', color: 'E7E0DC', pt: .5 }, margin: .05, colW }) }
    function drawTimelineSlide(slide, d) { const start = d.timelineStartYear || 2026, years = Math.max(1, Math.min(6, d.timelineYearsCount || 3)), rows = d.timelineRows || [], ox = 1.15, oy = 1.6, labelW = 2.15, qW = .62, yH = .42, qH = .48, rH = .55, total = years * 4; slide.addShape(pptx.ShapeType.rect, { x: .5, y: 1.38, w: 12.3, h: 5.5, fill: { color: 'F7F4EF' }, line: { color: 'E7E0DC' } }); slide.addShape(pptx.ShapeType.rect, { x: ox, y: oy, w: labelW, h: yH, fill: { color: '8D0D0D' }, line: { color: 'FFFFFF' } }); for (let y = 0; y < years; y++) { slide.addShape(pptx.ShapeType.rect, { x: ox + labelW + y * 4 * qW, y: oy, w: 4 * qW, h: yH, fill: { color: '8D0D0D' }, line: { color: 'FFFFFF' } }); addText(slide, String(start + y), ox + labelW + y * 4 * qW, oy + .04, 4 * qW, .24, { fontSize: 13, bold: true, color: 'FFFFFF', align: 'center' }) } slide.addShape(pptx.ShapeType.rect, { x: ox, y: oy + yH, w: labelW, h: qH, fill: { color: '8D0D0D' }, line: { color: 'FFFFFF' } }); for (let q = 0; q < total; q++) { slide.addShape(pptx.ShapeType.rect, { x: ox + labelW + q * qW, y: oy + yH, w: qW, h: qH, fill: { color: '8D0D0D' }, line: { color: 'FFFFFF' } }); addText(slide, quarterLabels[q % 4], ox + labelW + q * qW, oy + yH + .08, qW, .2, { fontSize: 11, bold: true, color: 'FFFFFF', align: 'center' }) } rows.forEach((r, idx) => { const y = oy + yH + qH + idx * rH; slide.addShape(pptx.ShapeType.rect, { x: ox, y, w: labelW, h: rH, fill: { color: 'EDE4D8' }, line: { color: 'F4EEE6' } }); addText(slide, r.name, ox + .08, y + .12, labelW - .16, .2, { fontSize: 10, bold: true, color: '6C5E57', align: 'center' }); for (let q = 0; q < total; q++)slide.addShape(pptx.ShapeType.rect, { x: ox + labelW + q * qW, y, w: qW, h: rH, fill: { color: 'F4EEE6' }, line: { color: 'FFFFFF', width: .5 } }); const st = quarterIndex(r.startYear, r.startQuarter) - quarterIndex(start, 1), en = quarterIndex(r.endYear, r.endQuarter) - quarterIndex(start, 1); if (en >= 0 && st <= total - 1) { const ss = Math.max(0, st), ee = Math.min(total - 1, en); slide.addShape(pptx.ShapeType.roundRect, { x: ox + labelW + ss * qW + .03, y: y + .08, w: (ee - ss + 1) * qW - .06, h: rH - .16, rectRadius: .05, fill: { color: (r.color || '#A9847A').replace('#', '') }, line: { color: (r.color || '#A9847A').replace('#', '') } }); addText(slide, r.name, ox + labelW + ss * qW + .05, y + .17, (ee - ss + 1) * qW - .1, .16, { fontSize: 9, bold: true, color: 'FFFFFF', align: 'center' }) } }) }
    function generateOutline() { showOutline(); toast('ØªÙ… Ø¥Ù†Ø´Ø§Ø¡ Ø§Ù„Ù‡ÙŠÙƒÙ„') }
    async function generatePptx(showMsg = true) {
      if (!currentProjectId) currentProjectId = uid(); upsertProject('generated'); window.pptx = new pptxgen(); pptx.layout = 'LAYOUT_WIDE'; pptx.author = val('preparedBy') || 'Ù…Ù†Ø§ÙØ¹ Ø§Ù„Ø§Ù‚ØªØµØ§Ø¯ÙŠØ©'; pptx.title = val('projectName'); pptx.lang = 'ar-SA'; pptx.theme = { headFontFace: 'Arial', bodyFontFace: 'Arial', lang: 'ar-SA' }; const d = collectData(), totalCost = d.landCost + d.developmentCost, annualProfit = d.annualRevenue - d.annualOpex, totalProfit = d.totalOperatingProfit + d.exitValue, built = d.components.reduce((a, x) => a + x.built, 0), leasable = d.components.reduce((a, x) => a + x.leasable, 0); const mainImg = await fileToDataUri('mainImageFile'), customLogo = await fileToDataUri('logoFile'), manafeLogo = await fetchAssetDataUri(manafeLogoPath), logo = customLogo || manafeLogo; let n = 1, s;
      s = pptx.addSlide(); s.background = { color: 'FBFAF8' }; s.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: 13.33, h: 1.1, fill: { color: '7A0C0C' }, line: { color: '7A0C0C' } }); addText(s, 'Ø¹Ø±Ø¶ Ù…Ø´Ø±ÙˆØ¹ Ø§Ø³ØªØ«Ù…Ø§Ø±ÙŠ', .65, .32, 12, .35, { fontSize: 18, bold: true, color: 'FFFFFF' }); if (logo) s.addImage({ data: logo, x: .65, y: 1.35, w: 1.6, h: 1.15 }); addText(s, d.projectName, 1.3, 1.65, 10.8, .65, { fontSize: 34, bold: true, color: '7A0C0C', align: 'center' }); addText(s, d.projectType + ' | ' + d.city, 1.3, 2.3, 10.8, .35, { fontSize: 15, color: '777777', align: 'center' }); if (mainImg) s.addImage({ data: mainImg, x: 1.25, y: 3.8, w: 10.85, h: 2.55 }); else { s.addShape(pptx.ShapeType.roundRect, { x: 1.25, y: 3.8, w: 10.85, h: 2.55, rectRadius: .1, fill: { color: 'F5F1ED' }, line: { color: 'E7E0DC' } }); addText(s, 'Ø§Ù„ØµÙˆØ±Ø© Ø§Ù„Ø±Ø¦ÙŠØ³ÙŠØ© Ù„Ù„Ù…Ø´Ø±ÙˆØ¹', 1.25, 4.85, 10.85, .35, { fontSize: 18, color: '999999', align: 'center' }) } addFooter(s, d, n++, manafeLogo);
      s = pptx.addSlide(); addTitle(s, 'Ø§Ù„Ù…Ù„Ø®Øµ Ø§Ù„ØªÙ†ÙÙŠØ°ÙŠ', d.projectName); addText(s, d.recommendation, .75, 1.55, 11.8, 1, { fontSize: 17, color: '444444' }); addMetric(s, 'Ø¥Ø¬Ù…Ø§Ù„ÙŠ Ø§Ù„ØªÙƒÙ„ÙØ©', money(totalCost) + ' Ø±ÙŠØ§Ù„', .75, 3, 3.8); addMetric(s, 'Ø§Ù„Ø¥ÙŠØ±Ø§Ø¯Ø§Øª Ø§Ù„Ø³Ù†ÙˆÙŠØ©', money(d.annualRevenue) + ' Ø±ÙŠØ§Ù„', 4.85, 3, 3.8); addMetric(s, 'Ø¥Ø¬Ù…Ø§Ù„ÙŠ Ø§Ù„Ø£Ø±Ø¨Ø§Ø­ Ø·ÙˆØ§Ù„ Ø§Ù„ÙØªØ±Ø©', money(totalProfit) + ' Ø±ÙŠØ§Ù„', 8.95, 3, 3.6); addMetric(s, 'Ø§Ù„Ø¹Ø§Ø¦Ø¯ Ø§Ù„Ø³Ù†ÙˆÙŠ Ø§Ù„Ù…ØªÙˆÙ‚Ø¹', d.annualROI, .75, 4.05, 3.8); addMetric(s, 'NOI Ø§Ù„Ù…ØªÙˆÙ‚Ø¹', d.noiRate, 4.85, 4.05, 3.8); addMetric(s, 'Ø§Ø³ØªØ±Ø¯Ø§Ø¯ Ø±Ø£Ø³ Ø§Ù„Ù…Ø§Ù„', d.payback, 8.95, 4.05, 3.6); addFooter(s, d, n++, manafeLogo);
      s = pptx.addSlide(); addTitle(s, 'ÙÙƒØ±Ø© Ø§Ù„Ù…Ø´Ø±ÙˆØ¹ ÙˆØ§Ù„Ù‡ÙŠÙƒÙ„Ø©', 'ØªØ¹Ø±ÙŠÙ Ù…Ø®ØªØµØ± Ø¨Ø§Ù„Ù…Ø´Ø±ÙˆØ¹ ÙˆÙ…ÙˆÙ‚Ø¹Ù‡ ÙˆÙ‡ÙŠÙƒÙ„ØªÙ‡'); addMetric(s, 'ÙÙƒØ±Ø© Ø§Ù„Ù…Ø´Ø±ÙˆØ¹', d.idea, .75, 1.55, 12, 1.05); addMetric(s, 'Ø§Ù„Ù…ÙˆÙ‚Ø¹', d.location + ' - ' + d.city, .75, 2.85, 12); addMetric(s, 'Ù‡ÙŠÙƒÙ„Ø© Ø§Ù„Ù…Ø´Ø±ÙˆØ¹', d.structure, .75, 3.85, 12); addMetric(s, 'Ù†ÙˆØ¹ Ø§Ù„Ù…Ø´Ø±ÙˆØ¹', d.projectType, .75, 4.85, 5.8); addMetric(s, 'Ø§Ù„Ù…Ø·ÙˆØ± / Ø§Ù„Ø¬Ù‡Ø©', d.developer, 6.95, 4.85, 5.8); addFooter(s, d, n++, manafeLogo);
      s = pptx.addSlide(); addTitle(s, 'Ù…Ù…ÙŠØ²Ø§Øª Ø§Ù„Ù…ÙˆÙ‚Ø¹', 'Ø£Ù‡Ù… Ø¹Ù†Ø§ØµØ± Ø§Ù„Ø¬Ø§Ø°Ø¨ÙŠØ© Ø§Ù„Ø¬ØºØ±Ø§ÙÙŠØ© ÙˆØ§Ù„ØªØ´ØºÙŠÙ„ÙŠØ©'); addBullets(s, d.locationFeatures, .95, 1.65, 11.5, 4.6); addFooter(s, d, n++, manafeLogo);
      s = pptx.addSlide(); addTitle(s, 'Ù…Ù…ÙŠØ²Ø§Øª Ø§Ù„Ù…Ø´Ø±ÙˆØ¹', 'Ù…Ø²Ø§ÙŠØ§ Ø§Ù„Ù…Ø´Ø±ÙˆØ¹ Ù…Ù† Ù…Ù†Ø¸ÙˆØ± Ø§Ø³ØªØ«Ù…Ø§Ø±ÙŠ ÙˆØªØ´ØºÙŠÙ„ÙŠ'); addBullets(s, d.projectFeatures, .95, 1.65, 11.5, 4.6); addFooter(s, d, n++, manafeLogo);
      s = pptx.addSlide(); addTitle(s, 'Ù…ÙƒÙˆÙ†Ø§Øª Ø§Ù„Ù…Ø´Ø±ÙˆØ¹ ÙˆØ§Ù„Ù…Ø³Ø§Ø­Ø§Øª', 'ØªÙØµÙŠÙ„ Ø§Ù„Ø¹Ù†Ø§ØµØ± ÙˆØ§Ù„Ù…Ø³Ø§Ø­Ø§Øª ÙˆØ§Ù„Ø¥ÙŠØ¬Ø§Ø±Ø§Øª Ø§Ù„Ø§ÙØªØ±Ø§Ø¶ÙŠØ©'); addTable(s, [['Ø§Ù„Ø¹Ù†ØµØ±', 'Ø§Ù„Ù…Ø³Ø§Ø­Ø© Ø§Ù„Ù…Ø¨Ù†ÙŠØ©', 'Ø§Ù„Ù…Ø³Ø§Ø­Ø© Ø§Ù„ØªØ£Ø¬ÙŠØ±ÙŠØ©', 'Ø§Ù„Ø¥ÙŠØ¬Ø§Ø± Ø¨Ø§Ù„Ù…ØªØ±'], ...d.components.map(c => [c.name, money(c.built), money(c.leasable), money(c.rent)]), ['Ø§Ù„Ø¥Ø¬Ù…Ø§Ù„ÙŠ / Ø§Ù„Ù…ØªÙˆØ³Ø·', money(built), money(leasable), money(d.avgRent)]], .55, 1.45, 12.2, 3.65, [3.4, 2.7, 2.7, 2.7]); addMetric(s, 'Ù…Ø³Ø§Ø­Ø© Ø§Ù„Ø£Ø±Ø¶', money(d.landArea) + ' Ù…Â²', .75, 5.45, 3.8); addMetric(s, 'Ù†Ø³Ø¨Ø© Ø§Ù„Ø¨Ù†Ø§Ø¡', d.buildingRatio + '%', 4.85, 5.45, 3.8); addMetric(s, 'Ù…Ù„Ø§Ø­Ø¸Ø©', d.areaNote, 8.95, 5.45, 3.6); addFooter(s, d, n++, manafeLogo);
      s = pptx.addSlide(); addTitle(s, 'Ø§ÙØªØ±Ø§Ø¶Ø§Øª Ø§Ù„Ø±Ø¨Ø­ Ø§Ù„ØªØ´ØºÙŠÙ„ÙŠ Ø§Ù„ØªØ£Ø¬ÙŠØ±ÙŠ', 'Ø§Ù„Ù…Ø¯Ø®Ù„Ø§Øª Ø§Ù„Ù…Ø§Ù„ÙŠØ© Ø§Ù„Ø£Ø³Ø§Ø³ÙŠØ© Ù„Ù„ØªØ´ØºÙŠÙ„'); addTable(s, [['Ø§Ù„Ø¨Ù†Ø¯', 'Ø§Ù„Ù‚ÙŠÙ…Ø©'], ['Ù…ØªÙˆØ³Ø· Ø¥ÙŠØ¬Ø§Ø± Ø§Ù„Ù…ØªØ±', money(d.avgRent)], ['Ø±Ø³ÙˆÙ… Ø§Ù„Ø®Ø¯Ù…Ø§Øª Ø¹Ù„Ù‰ Ø§Ù„Ù…Ø³ØªØ£Ø¬Ø±ÙŠÙ†', d.serviceFees + '%'], ['Ø§Ù„Ø¥ÙŠØ±Ø§Ø¯Ø§Øª Ø§Ù„Ø³Ù†ÙˆÙŠØ©', money(d.annualRevenue)], ['Ø§Ù„Ù…ØµØ±ÙˆÙ Ø§Ù„ØªØ´ØºÙŠÙ„ÙŠ Ø§Ù„Ø³Ù†ÙˆÙŠ', money(d.annualOpex)], ['Ø¥Ø¬Ù…Ø§Ù„ÙŠ Ø§Ù„Ø±Ø¨Ø­ Ø§Ù„ØªØ£Ø¬ÙŠØ±ÙŠ Ø§Ù„Ø³Ù†ÙˆÙŠ', money(annualProfit)]], 1.1, 1.6, 11.1, 3.8, [6.7, 4]); addFooter(s, d, n++, manafeLogo);
      s = pptx.addSlide(); addTitle(s, 'Ø§ÙØªØ±Ø§Ø¶Ø§Øª Ø§Ù„ØªÙƒØ§Ù„ÙŠÙ', 'ØªÙƒÙ„ÙØ© Ø§Ù„Ø£Ø±Ø¶ ÙˆØ§Ù„ØªØ·ÙˆÙŠØ± ÙˆØ¥Ø¬Ù…Ø§Ù„ÙŠ Ø§Ù„ØªÙƒÙ„ÙØ©'); addMetric(s, 'ØªÙƒÙ„ÙØ© Ø§Ù„Ø£Ø±Ø¶', money(d.landCost) + ' Ø±ÙŠØ§Ù„', 1, 1.7, 5.5); addMetric(s, 'ØªÙƒÙ„ÙØ© Ø§Ù„ØªØ·ÙˆÙŠØ±', money(d.developmentCost) + ' Ø±ÙŠØ§Ù„', 6.85, 1.7, 5.5); addMetric(s, 'Ø¥Ø¬Ù…Ø§Ù„ÙŠ Ø§Ù„ØªÙƒÙ„ÙØ©', money(totalCost) + ' Ø±ÙŠØ§Ù„', 1, 3, 11.35); addFooter(s, d, n++, manafeLogo);
      s = pptx.addSlide(); addTitle(s, 'Ø§Ù„Ø£Ø±Ø¨Ø§Ø­ ÙˆØ§Ù„ØªØ®Ø§Ø±Ø¬', 'Ø¥Ø¬Ù…Ø§Ù„ÙŠ Ø§Ù„Ø±Ø¨Ø­ Ø§Ù„ØªØ´ØºÙŠÙ„ÙŠ ÙˆÙ‚ÙŠÙ…Ø© Ø§Ù„ØªØ®Ø§Ø±Ø¬ Ø§Ù„Ù…ØªÙˆÙ‚Ø¹Ø©'); addMetric(s, 'Ø¥Ø¬Ù…Ø§Ù„ÙŠ Ø§Ù„Ø±Ø¨Ø­ Ø§Ù„ØªØ´ØºÙŠÙ„ÙŠ Ø·ÙˆØ§Ù„ Ø§Ù„ÙØªØ±Ø©', money(d.totalOperatingProfit) + ' Ø±ÙŠØ§Ù„', 1, 1.75, 11.3); addMetric(s, 'Ù‚ÙŠÙ…Ø© Ø§Ù„ØªØ®Ø§Ø±Ø¬ Ù…Ù† Ø§Ù„Ù…Ø´Ø±ÙˆØ¹', money(d.exitValue) + ' Ø±ÙŠØ§Ù„', 1, 2.95, 11.3); addMetric(s, 'Ù…Ø¹Ø§Ù…Ù„ Ø§Ù„Ø±Ø³Ù…Ù„Ø©', d.capRate + '%', 1, 4.15, 5.4); addMetric(s, 'Ø¥Ø¬Ù…Ø§Ù„ÙŠ Ø§Ù„Ø£Ø±Ø¨Ø§Ø­ Ø·ÙˆØ§Ù„ Ø§Ù„ÙØªØ±Ø©', money(totalProfit) + ' Ø±ÙŠØ§Ù„', 6.9, 4.15, 5.4); addFooter(s, d, n++, manafeLogo);
      s = pptx.addSlide(); addTitle(s, 'Ø§Ù„Ù…Ø¤Ø´Ø±Ø§Øª Ø§Ù„Ù…Ø§Ù„ÙŠØ© Ø§Ù„Ù…ØªÙˆÙ‚Ø¹Ø©', 'Ù‚Ø±Ø§Ø¡Ø© Ø£ÙˆÙ„ÙŠØ© Ù„Ø£Ø¯Ø§Ø¡ Ø§Ù„Ù…Ø´Ø±ÙˆØ¹'); addTable(s, [['Ø§Ù„Ù…Ø¤Ø´Ø±', 'Ø§Ù„Ù†ØªÙŠØ¬Ø© Ø§Ù„Ù…ØªÙˆÙ‚Ø¹Ø©'], ['Ù†Ø³Ø¨Ø© Ø§Ù„Ø¹Ø§Ø¦Ø¯ Ø§Ù„Ø³Ù†ÙˆÙŠ Ø¹Ù„Ù‰ Ø§Ù„Ø§Ø³ØªØ«Ù…Ø§Ø±', d.annualROI], ['Ù†Ø³Ø¨Ø© ØµØ§ÙÙŠ Ø§Ù„Ø±Ø¨Ø­ Ø§Ù„ØªØ´ØºÙŠÙ„ÙŠ NOI', d.noiRate], ['Ø§Ø³ØªØ±Ø¯Ø§Ø¯ Ø±Ø£Ø³ Ø§Ù„Ù…Ø§Ù„', d.payback], ['Ø¥Ø¬Ù…Ø§Ù„ÙŠ Ø§Ù„ØªÙƒÙ„ÙØ©', money(totalCost) + ' Ø±ÙŠØ§Ù„'], ['Ø¥Ø¬Ù…Ø§Ù„ÙŠ Ø§Ù„Ø£Ø±Ø¨Ø§Ø­ Ø·ÙˆØ§Ù„ Ø§Ù„ÙØªØ±Ø©', money(totalProfit) + ' Ø±ÙŠØ§Ù„']], 1, 1.55, 11.3, 4.3, [6.4, 4.6]); addFooter(s, d, n++, manafeLogo);
      s = pptx.addSlide(); addTitle(s, d.timelineTitle || 'Ø§Ù„Ø¬Ø¯ÙˆÙ„ Ø§Ù„Ø²Ù…Ù†ÙŠ ÙˆÙ…Ø±Ø§Ø­Ù„ Ø§Ù„Ù…Ø´Ø±ÙˆØ¹', d.timelineSubtitle || 'Ù…Ø±Ø§Ø­Ù„ Ø§Ù„ØªØ·ÙˆÙŠØ± ÙˆØ§Ù„ØªÙ†ÙÙŠØ° ÙˆØ§Ù„ØªØ´ØºÙŠÙ„'); drawTimelineSlide(s, d); addFooter(s, d, n++, manafeLogo);
      s = pptx.addSlide(); addTitle(s, 'ÙØ±Øµ Ø§Ù„Ø§Ø³ØªØ«Ù…Ø§Ø± ÙˆÙ†Ù‚Ø§Ø· Ø§Ù„Ù‚ÙˆØ©', 'Ø£Ø³Ø¨Ø§Ø¨ Ø¬Ø§Ø°Ø¨ÙŠØ© Ø§Ù„Ù…Ø´Ø±ÙˆØ¹'); addBullets(s, d.investmentHighlights, .95, 1.65, 11.5, 4.6); addFooter(s, d, n++, manafeLogo);
      s = pptx.addSlide(); addTitle(s, 'Ø§Ù„Ù…Ø®Ø§Ø·Ø± ÙˆØ§Ù„Ø§ÙØªØ±Ø§Ø¶Ø§Øª', 'Ù†Ù‚Ø§Ø· ÙŠØ¬Ø¨ Ø§Ù„ØªØ­Ù‚Ù‚ Ù…Ù†Ù‡Ø§ ÙÙŠ Ø§Ù„Ø¯Ø±Ø§Ø³Ø© Ø§Ù„ØªÙØµÙŠÙ„ÙŠØ©'); addBullets(s, d.risks, .95, 1.65, 11.5, 4.6); addFooter(s, d, n++, manafeLogo);
      s = pptx.addSlide(); addTitle(s, 'Ø§Ù„Ù…ÙˆØ¯ Ø¨ÙˆØ±Ø¯ Ø¨Ø§Ù„Ø°ÙƒØ§Ø¡ Ø§Ù„Ø§ØµØ·Ù†Ø§Ø¹ÙŠ', 'ØªØµÙˆØ±Ø§Øª Ø¨ØµØ±ÙŠØ© Ù…Ø¨Ø¯Ø¦ÙŠØ© Ù…Ø¨Ù†ÙŠØ© Ø¹Ù„Ù‰ Ù…Ø¯Ø®Ù„Ø§Øª Ø§Ù„Ø¹Ù…ÙŠÙ„'); addText(s, 'Ø§Ø³Ù… Ø§Ù„Ù…Ø¨Ù†Ù‰: ' + d.buildingName, .75, 1.36, 4, .28, { fontSize: 12, bold: true, color: '7A0C0C' }); addText(s, d.aiImagePrompt, .75, 1.7, 11.8, .45, { fontSize: 10, color: '6B625D' });[{ x: .75, y: 2.25, w: 5.7, h: 1.75 }, { x: 6.85, y: 2.25, w: 5.7, h: 1.75 }, { x: .75, y: 4.45, w: 5.7, h: 1.75 }, { x: 6.85, y: 4.45, w: 5.7, h: 1.75 }].forEach((slot, i) => { s.addShape(pptx.ShapeType.roundRect, { x: slot.x, y: slot.y, w: slot.w, h: slot.h, rectRadius: .05, fill: { color: 'F8F4EF' }, line: { color: 'E7E0DC' } }); const item = d.aiGeneratedImages[i]; if (item?.url) s.addImage({ data: item.url, x: slot.x + .04, y: slot.y + .04, w: slot.w - .08, h: slot.h - .08 }); else addText(s, (item?.label || ('AI Image ' + (i + 1))) + '\\n' + d.buildingName, slot.x, slot.y + .58, slot.w, .42, { fontSize: 14, bold: true, color: 'A9847A', align: 'center' }) }); addFooter(s, d, n++, manafeLogo);
      s = pptx.addSlide(); s.background = { color: '7A0C0C' }; if (manafeLogo) s.addImage({ data: manafeLogo, x: 5.55, y: 1, w: 2.2, h: 1.45 }); addText(s, 'Ø´ÙƒØ±Ø§Ù‹ Ù„ÙƒÙ…', .9, 2.6, 11.5, .7, { fontSize: 40, bold: true, color: 'FFFFFF', align: 'center' }); addText(s, d.projectName, .9, 3.45, 11.5, .4, { fontSize: 20, color: 'F5DDDD', align: 'center' }); addText(s, d.contactInfo, .9, 4.55, 11.5, .4, { fontSize: 16, color: 'FFFFFF', align: 'center' }); addText(s, d.preparedBy, .9, 5.1, 11.5, .3, { fontSize: 13, color: 'F5DDDD', align: 'center' });
      await pptx.writeFile({ fileName: `${d.projectName || 'investment-project'}_generated.pptx` }); markGenerated(); if (showMsg) { addChat('ai', 'ØªÙ… ØªÙˆÙ„ÙŠØ¯ Ù…Ù„Ù PowerPoint. ÙŠÙ…ÙƒÙ†Ùƒ Ø·Ù„Ø¨ ØªØ¹Ø¯ÙŠÙ„Ø§Øª Ù‡Ù†Ø§ Ù‚Ø¨Ù„ Ø§Ù„ØªØ¹Ù…ÙŠØ¯.'); toast('ØªÙ… ØªÙˆÙ„ÙŠØ¯ Ø§Ù„Ù…Ù„Ù ÙˆØ­ÙØ¸Ù‡ ÙÙŠ Ø§Ù„Ø£Ø±Ø´ÙŠÙ') }
    }

    async function exportToPdf() { const { jsPDF } = window.jspdf; const pdf = new jsPDF({ orientation: 'landscape', unit: 'mm', format: 'a4' }); const w = pdf.internal.pageSize.getWidth(), h = pdf.internal.pageSize.getHeight(); toast('Ø¬Ø§Ø±ÙŠ ØªØ­ÙˆÙŠÙ„ PDF...'); const sections = [...document.querySelectorAll('#designerPage .section')]; for (let i = 0; i < sections.length; i++) { if (i > 0) pdf.addPage(); const sec = sections[i]; const wasHidden = sec.classList.contains('hidden'); sec.classList.remove('hidden'); sec.classList.add('active'); await new Promise(r => setTimeout(r, 300)); const canvas = await html2canvas(sec, { scale: 2, useCORS: true, backgroundColor: '#ffffff', logging: false }); const imgData = canvas.toDataURL('image/jpeg', 0.92); const imgW = w - 10, imgH = (canvas.height * imgW) / canvas.width; const finalH = Math.min(imgH, h - 10); pdf.addImage(imgData, 'JPEG', 5, 5, imgW, finalH); sec.classList.toggle('active', false); sec.classList.toggle('hidden', wasHidden) } sections[0].classList.add('active'); pdf.save((val('projectName') || 'project') + '.pdf'); toast('ØªÙ… ØªØµØ¯ÙŠØ± PDF') }
    initNav();
    (function restorePage() {
      var nav = getNavState();
      if (!nav || !nav.page) return;
      var savedPage = nav.page;
      var validPages = ['homePage', 'archivePage', 'designerPage'];
      if (validPages.indexOf(savedPage) === -1) return;
      if (savedPage === 'designerPage') {
        var extra = nav.extra;
        if (extra && extra.projectId) {
          var p = getProjects().find(function (x) { return x.id === extra.projectId });
          if (p) {
            currentProjectId = extra.projectId;
            resetForm();
            loadDataToForm(p.data || {});
            initNav();
            show('designerPage');
            document.getElementById('designerTitle').textContent = 'ØªØ¹Ø¯ÙŠÙ„: ' + (p.name || 'Ù…Ø´Ø±ÙˆØ¹');
            saveNavState('designerPage', { projectId: currentProjectId });
          }
        } else {
          show('designerPage');
        }
      } else if (savedPage === 'archivePage') {
        show('archivePage');
        renderArchive();
      }
    })();
