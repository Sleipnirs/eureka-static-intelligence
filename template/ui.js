/* ══════════════ UI layer ══════════════ */
const S = { visited: [], depth: 0, fallbackIdx: 0 };
const T = {
  en: { placeholder: 'Ask me anything…', quick: 'Quick Questions', toolbox: 'Toolbox', powered: 'Powered by', reset: 'New chat',
        didYouMean: 'I might not have caught that exactly — did you mean one of these? Or search it directly.',
        aeoChip: 'Search this with Google AI', aeoLead: 'All set — confirm below to open it in a new tab:',
        aeoTitle: 'Google AI Mode Search', aeoDesc: 'Continue this question with free AI search. Opens in a new tab — this chat stays right here.',
        aeoCta: 'Open ↗', follow: 'Following up on that — ',
        ack: ['Glad that helps! Ask me anything else below.', 'Happy to hear it — I am right here for the next question.'],
        fallback: ['I may not have that answer — try a suggested question, or search it directly.', 'That is a bit outside my map — the chips below can help.'],
        toolCalc: 'Calculator', toolJson: 'JSON Validator', toolTs: 'Timestamp', toolUnits: 'Units', toolStats: 'Text Stats + SHA-256', toolImg: 'Image tools (soon)',
        calcTip: 'Tip: type an expression straight into the chat.', jsonBtn: 'Validate & pretty-print', statsBtn: 'Compute SHA-256', now: 'Now' },
  zh: { placeholder: '随便问我什么…', quick: '快捷问题', toolbox: '工具箱', powered: '技术支持', reset: '新会话',
        didYouMean: '我可能没有完全对上你的问题——你是想问下面哪个？也可以直接外部搜索。',
        aeoChip: '用 Google AI 搜索这个问题', aeoLead: '好——搜索已备好，确认后在新标签页打开：',
        aeoTitle: 'Google AI 模式搜索', aeoDesc: '用免费 AI 搜索继续这个问题。新标签页打开，本对话原地保留。',
        aeoCta: '打开 ↗', follow: '接着刚才的话题——',
        ack: ['很高兴有帮助！还有问题随时问。', '收到！下一个问题我在这儿等你。'],
        fallback: ['这个可能超出我的知识图——试试推荐问题，或直接外部搜索。', '这有点超纲了——下面的选项可以帮到你。'],
        toolCalc: '计算器', toolJson: 'JSON 校验', toolTs: '时间戳', toolUnits: '单位换算', toolStats: '文本统计 + SHA-256', toolImg: '图像工具（预留）',
        calcTip: '小技巧：直接在对话框敲算式也行。', jsonBtn: '校验并美化', statsBtn: '计算 SHA-256', now: '当前' },
};
const SVG = {
  spark: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2l2.4 7.2L22 12l-7.6 2.8L12 22l-2.4-7.2L2 12l7.6-2.8L12 2z"/></svg>',
  refresh: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12a9 9 0 1 1-2.64-6.36"/><path d="M21 3v6h-6"/></svg>',
  sun: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"/></svg>',
  moon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>',
  send: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 2L11 13"/><path d="M22 2l-7 20-4-9-9-4 20-7z"/></svg>',
  q: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M9.1 9a3 3 0 0 1 5.8 1c0 2-3 3-3 3"/><path d="M12 17h.01"/></svg>',
  flow: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 6h16"/><path d="M4 12h10"/><path d="M4 18h7"/></svg>',
  caret: '<svg class="esi-caret" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 9l6 6 6-6"/></svg>',
  check: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6L9 17l-5-5"/></svg>',
};
const $ = (s2, el) => (el || document).querySelector(s2);
const app = $('#app');
function h(tag, cls, html) { const e = document.createElement(tag); if (cls) e.className = cls; if (html !== undefined) e.innerHTML = html; return e; }
const esc = (s2) => String(s2).replace(/[&<>"']/g, (c) => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

function build() {
  const B = PACK.brand;
  app.innerHTML = '';
  // ── header: FinChip banner style ──
  const head = h('div', 'esi-header');
  head.insertAdjacentHTML('beforeend', SVG.spark);
  head.append(h('span', 'esi-brand', esc(B.name)));
  head.append(h('span', 'esi-tag', esc(B.tag || 'Beta')));
  if (B.tagline) head.append(h('span', 'esi-tagline', esc(B.tagline[LOC] || B.tagline.en || '')));
  head.append(h('div', 'esi-spacer'));
  const rBtn = h('button', 'esi-orb', SVG.refresh); rBtn.title = T[LOC].reset; rBtn.onclick = reset; head.append(rBtn);
  const dBtn = h('button', 'esi-orb', document.body.classList.contains('esi-dark') ? SVG.moon : SVG.sun);
  dBtn.onclick = () => { document.body.classList.toggle('esi-dark'); dBtn.innerHTML = document.body.classList.contains('esi-dark') ? SVG.moon : SVG.sun; };
  head.append(dBtn);
  if (LANGS.length > 1) {
    const lBtn = h('button', 'esi-orb', LOC === 'zh' ? 'Zh' : 'En');
    lBtn.title = 'En / Zh';
    lBtn.onclick = () => { LOC = LOC === LANGS[0] ? LANGS[1] : LANGS[0]; build(); botSay(PACK.brand.welcome[LOC] || PACK.brand.welcome.en, welcomeChips()); };
    head.append(lBtn);
  }
  app.append(head);

  const main = h('div', 'esi-main');
  const left = h('div', 'esi-left');
  const chatEl = h('div', 'esi-chat'); chatEl.id = 'chat'; left.append(chatEl);
  // ── composer ──
  const comp = h('div', 'esi-composer');
  const row = h('div', 'esi-inrow');
  const ta = h('textarea', 'esi-input'); ta.id = 'input'; ta.rows = 1; ta.placeholder = T[LOC].placeholder;
  ta.onkeydown = (e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); } };
  ta.oninput = () => { ta.style.height = 'auto'; ta.style.height = Math.min(ta.scrollHeight, 160) + 'px'; };
  const sb = h('button', 'esi-send', SVG.send); sb.onclick = send;
  row.append(ta, sb); comp.append(row);
  // foot: three default quick minis + version dropdown
  const foot = h('div', 'esi-foot');
  QUICK.slice(0, 3).forEach(id => {
    if (!NODES[id]) return;
    const m = h('button', 'esi-mini', esc(qOf(id))); m.title = qOf(id);
    m.onclick = () => { userSay(qOf(id)); answer(id); };
    foot.append(m);
  });
  const vw = h('span', 'esi-ver-wrap');
  const vb = h('button', 'esi-version');
  vb.innerHTML = '<span class="esi-verdot"></span>Eureka Static Intelligence 2.0 High' + SVG.caret;
  vb.onclick = () => toggleVerMenu(vw);
  vw.append(vb); foot.append(vw);
  comp.append(foot); left.append(comp); main.append(left);

  // ── rail: two locked panels with icons ──
  const rail = h('div', 'esi-rail');
  const p1 = h('div', 'esi-panel');
  const ph1 = h('div', 'esi-phead'); ph1.innerHTML = SVG.q + esc(T[LOC].quick); p1.append(ph1);
  const b1 = h('div', 'esi-pbody');
  QUICK.forEach(id => { if (!NODES[id]) return; const q = h('button', 'esi-qq', esc(qOf(id))); q.onclick = () => { userSay(qOf(id)); answer(id); }; b1.append(q); });
  p1.append(b1); rail.append(p1);
  const p2 = h('div', 'esi-panel');
  const ph2 = h('div', 'esi-phead'); ph2.innerHTML = SVG.flow + esc(PACK.flow ? 'Flow' : T[LOC].toolbox); p2.append(ph2);
  const b2 = h('div', 'esi-pbody');
  if (!PACK.flow) {
    const tools = [
      ['calculator', '🧮', T[LOC].toolCalc], ['json', '{}', T[LOC].toolJson], ['timestamp', '🕑', T[LOC].toolTs],
      ['units', '⇄', T[LOC].toolUnits], ['textstats', '𝚺', T[LOC].toolStats],
    ].filter(([k]) => (PACK.toolbox || []).includes(k));
    tools.forEach(([k, ico, label]) => { const btn = h('button', 'esi-tool'); btn.innerHTML = '<span class="esi-tool-ico">' + ico + '</span>' + esc(label); btn.onclick = () => showTool(k); b2.append(btn); });
    const img = h('button', 'esi-tool dis'); img.innerHTML = '<span class="esi-tool-ico">🖼</span>' + esc(T[LOC].toolImg); b2.append(img);
  }
  p2.append(b2); rail.append(p2); main.append(rail); app.append(main);
}
function toggleVerMenu(wrap) {
  const old = wrap.querySelector('.esi-ver-menu');
  const bd = document.querySelector('.esi-ver-backdrop');
  if (old) { old.remove(); if (bd) bd.remove(); return; }
  const backdrop = h('div', 'esi-ver-backdrop');
  backdrop.onclick = () => { backdrop.remove(); const m = wrap.querySelector('.esi-ver-menu'); if (m) m.remove(); };
  document.body.append(backdrop);
  const menu = h('div', 'esi-ver-menu');
  const hi = h('button', 'esi-ver-item on'); hi.innerHTML = 'High ' + SVG.check;
  hi.onclick = () => { menu.remove(); backdrop.remove(); };
  const med = h('button', 'esi-ver-item', 'Medium'); med.disabled = true;
  const lo = h('button', 'esi-ver-item', 'Low'); lo.disabled = true;
  menu.append(hi, med, lo); wrap.append(menu);
}
const qOf = (id) => (NODES[id].q[LOC] || NODES[id].q.en);
const aOf = (id) => (NODES[id].a[LOC] || NODES[id].a.en);
function chat() { return $('#chat'); }
function scroll2() { chat().scrollTop = chat().scrollHeight; }
function userSay(text) { const m = h('div', 'esi-msg user'); m.append(h('div', 'esi-bubble', esc(text))); chat().append(m); scroll2(); }
function botSay(text, chips, widget) {
  const m = h('div', 'esi-msg bot');
  m.append(h('div', 'esi-avatar', esc(PACK.brand.name[0] || 'E')));
  m.append(h('div', 'esi-bubble', esc(text)));
  chat().append(m);
  if (widget) { const w = h('div', 'esi-widget'); w.append(widget); chat().append(w); }
  if (chips && chips.length) {
    const c = h('div', 'esi-chips');
    chips.forEach(([label, fn]) => { const b = h('button', 'esi-chip', esc(label)); b.onclick = fn; c.append(b); });
    chat().append(c);
  }
  scroll2();
}
function welcomeChips() {
  return QUICK.slice(0, 2).map(id => [qOf(id), () => { userSay(qOf(id)); answer(id); }]).concat([anchorChip()]);
}
function anchorChip() {
  const A = PACK.brand.anchor;
  const label = A.label[LOC] || A.label.en;
  return [label, () => { if (A.action === 'link') window.open(A.target, '_blank', 'noopener'); else { userSay(label); answer(A.target); } }];
}
function chipsFor(id) {
  const n = NODES[id]; const fresh = (arr) => arr.filter(x => !S.visited.includes(x) && NODES[x]);
  const kids = (n.children || []).filter(x => x !== id && NODES[x]);
  let out = [];
  if (S.depth < 2) {
    const pool = QUICK.filter(q => q !== id); out = fresh(pool).concat(pool).slice(0, 2);
  } else {
    const grand = kids.flatMap(k => NODES[k].children || []).filter(x => x !== id && !kids.includes(x));
    const nonQ = (a) => a.filter(x => !QUICK.includes(x));
    let branch = fresh(nonQ(kids))[0] || fresh(nonQ(grand))[0] || fresh(kids)[0];
    if (!branch) { const pool = fresh(nonQ(IDS.filter(x => x !== id))); branch = pool[Math.floor(Math.random() * pool.length)] || kids[0]; }
    const mains = QUICK.filter(q => q !== id && q !== branch);
    const main = fresh(mains)[0] || mains[S.depth % mains.length];
    out = [branch, main].filter(Boolean);
  }
  const uniq = [...new Set(out)];
  return uniq.map(cid => [qOf(cid), () => { userSay(qOf(cid)); answer(cid); }]).concat([anchorChip()]);
}
function answer(id) {
  const n = NODES[id];
  const last = S.visited[S.visited.length - 1];
  const same = S.depth >= 2 && last && last !== id && (last.split('-')[0] === id.split('-')[0] || (NODES[last] && (NODES[last].children || []).includes(id)) || (PARENTS[last] || []).includes(id));
  const lead = same ? T[LOC].follow : '';
  let widget = null;
  if (n.link) { widget = null; }
  const chips = chipsFor(id);
  if (n.link) chips.unshift([n.link.label[LOC] || n.link.label.en, () => window.open(n.link.href, '_blank', 'noopener')]) && chips.splice(2, 1);
  setTimeout(() => botSay(lead + aOf(id), chips.slice(0, 3), widget), 260);
  if (!S.visited.includes(id)) S.visited.push(id);
  S.depth++;
}
function aeoCard(query) {
  const card = h('div', 'esi-card');
  card.append(h('div', 'esi-card-title', esc(T[LOC].aeoTitle)));
  const row = h('div', 'esi-linkcard');
  const img = h('img');
  img.src = 'https://www.google.com/favicon.ico';
  img.alt = '';
  img.onerror = () => { img.style.display = 'none'; };
  row.append(img);
  const body = h('div', 'esi-lc-body');
  body.append(h('div', 'esi-lc-d', esc(T[LOC].aeoDesc)));
  body.append(h('div', 'esi-lc-q', '“' + esc(query) + '”'));
  body.append(h('div', 'esi-meta', 'google.com · AI Mode'));
  row.append(body);
  const open = h('button', 'esi-open', esc(T[LOC].aeoCta));
  open.onclick = () => window.open('https://www.google.com/search?udm=50&q=' + encodeURIComponent(query), '_blank', 'noopener');
  row.append(open); card.append(row); return card;
}
function send() {
  const ta = $('#input'); const text = ta.value.trim(); if (!text) return;
  ta.value = ''; ta.style.height = 'auto'; userSay(text);
  const v = evalExpr(text.replace(/[?？!！=]+$/g, ''));
  if (v !== null && /[+\-*/%^×÷]/.test(text)) { setTimeout(() => { botSay(text.replace(/\s+/g, '') + ' = ' + (Math.round(v * 1e10) / 1e10), [anchorChip()], toolCalc()); }, 200); return; }
  if (isSmallTalk(text)) { const a = T[LOC].ack; setTimeout(() => botSay(a[S.fallbackIdx++ % a.length], welcomeChips()), 200); return; }
  const scored = score(text, S);
  const top = scored[0];
  if (top && top.sc >= 4) { answer(top.id); return; }
  if (top && top.sc >= 2) {
    const cands = scored.slice(0, 2).map(x => [qOf(x.id), () => { userSay(qOf(x.id)); answer(x.id); }]);
    cands.push([T[LOC].aeoChip, () => setTimeout(() => botSay(T[LOC].aeoLead, [anchorChip()], aeoCard(text)), 150)]);
    setTimeout(() => botSay(T[LOC].didYouMean, cands.slice(0, 3)), 260);
    return;
  }
  const f = T[LOC].fallback;
  const chips = [[T[LOC].aeoChip, () => setTimeout(() => botSay(T[LOC].aeoLead, [anchorChip()], aeoCard(text)), 150)], welcomeChips()[0], anchorChip()];
  setTimeout(() => botSay(f[S.fallbackIdx++ % f.length], chips), 260);
}
/* ── toolbox cards ── */
function toolCalc() {
  const card = h('div', 'esi-card'); card.append(h('div', 'esi-card-title', esc(T[LOC].toolCalc)));
  const disp = h('input', 'esi-ti'); disp.placeholder = '23*45+12';
  const grid = h('div', 'esi-grid4');
  'C ( ) ⌫ 7 8 9 ÷ 4 5 6 × 1 2 3 - 0 . % + ^ ='.split(' ').forEach(k => {
    const b = h('button', 'esi-key' + (k === '=' ? ' eq' : /[÷×%^+()\-]|⌫|C/.test(k) ? ' op' : ''), esc(k));
    b.onclick = () => {
      if (k === 'C') disp.value = '';
      else if (k === '⌫') disp.value = disp.value.slice(0, -1);
      else if (k === '=') { const v = evalExpr(disp.value); disp.value = v === null ? 'Error' : String(Math.round(v * 1e10) / 1e10); }
      else disp.value += k;
    };
    grid.append(b);
  });
  card.append(disp, grid, h('div', 'esi-meta', esc(T[LOC].calcTip)));
  return card;
}
function toolJson() {
  const card = h('div', 'esi-card'); card.append(h('div', 'esi-card-title', esc(T[LOC].toolJson)));
  const ta = h('textarea', 'esi-ta'); ta.rows = 4; ta.placeholder = '{"a": 1}';
  const out = h('pre', 'esi-hash'); out.style.display = 'none';
  const btn = h('button', 'esi-btn pri', esc(T[LOC].jsonBtn));
  btn.onclick = () => { out.style.display = 'block'; try { out.textContent = JSON.stringify(JSON.parse(ta.value), null, 2); out.style.color = ''; } catch (e) { out.textContent = '✗ ' + e.message; out.style.color = '#dc2626'; } };
  card.append(ta, btn, out); return card;
}
function toolTs() {
  const card = h('div', 'esi-card'); card.append(h('div', 'esi-card-title', esc(T[LOC].toolTs)));
  const inp = h('input', 'esi-ti'); inp.value = String(Math.floor(Date.now() / 1000));
  const out = h('div', 'esi-row'); const meta = h('span', 'esi-meta');
  const upd = () => { const n2 = /^\d{13}$/.test(inp.value.trim()) ? Number(inp.value) / 1000 : Number(inp.value); if (isFinite(n2) && n2 > 0 && n2 < 4e12) { const d = new Date(n2 * 1000); meta.textContent = d.toISOString().replace('T', ' ').replace(/\..+/, ' UTC · ') + d.toLocaleString(); } else meta.textContent = '—'; };
  inp.oninput = upd; upd(); out.append(h('span', '', 'UTC/Local'), meta);
  const nowB = h('button', 'esi-btn', esc(T[LOC].now)); nowB.onclick = () => { inp.value = String(Math.floor(Date.now() / 1000)); upd(); };
  card.append(inp, out, nowB); return card;
}
function toolUnits() {
  const card = h('div', 'esi-card'); card.append(h('div', 'esi-card-title', esc(T[LOC].toolUnits)));
  const inp = h('input', 'esi-ti'); inp.value = '1';
  const sel = h('select', 'esi-ti'); ['eth', 'gwei', 'wei'].forEach(u => { const o = h('option', '', u); o.value = u; sel.append(o); });
  const rows = h('div');
  const pow = { wei: 0, gwei: 9, eth: 18 };
  const upd = () => { rows.innerHTML = ''; const n2 = Number(inp.value); ['wei', 'gwei', 'eth'].filter(u => u !== sel.value).forEach(u => { const v = n2 * Math.pow(10, pow[sel.value] - pow[u]); const r = h('div', 'esi-row'); r.append(h('span', '', u.toUpperCase()), h('span', 'esi-meta', !isFinite(v) ? '—' : Math.abs(v) >= 1e15 || (v !== 0 && Math.abs(v) < 1e-6) ? v.toExponential(4) : v.toLocaleString('en-US', { maximumFractionDigits: 9 }))); rows.append(r); }); };
  inp.oninput = upd; sel.onchange = upd; upd();
  card.append(inp, sel, rows); return card;
}
function toolStats() {
  const card = h('div', 'esi-card'); card.append(h('div', 'esi-card-title', esc(T[LOC].toolStats)));
  const ta = h('textarea', 'esi-ta'); ta.rows = 3;
  const out = h('div', 'esi-row'); const meta = h('span', 'esi-meta');
  const upd = () => { const s2 = ta.value; const cjk = (s2.match(/[一-鿿]/g) || []).length; meta.textContent = s2.length + ' / ' + ((s2.match(/[a-zA-Z0-9]+/g) || []).length + cjk) + ' / ' + (s2 ? s2.split('\n').length : 0) + ' / ' + new TextEncoder().encode(s2).length; };
  ta.oninput = upd; upd(); out.append(h('span', '', 'chars/words/lines/bytes'), meta);
  const hres = h('div', 'esi-hash'); hres.style.display = 'none';
  const btn = h('button', 'esi-btn pri', esc(T[LOC].statsBtn));
  btn.onclick = async () => { const buf = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(ta.value)); hres.style.display = 'block'; hres.textContent = '0x' + [...new Uint8Array(buf)].map(b => b.toString(16).padStart(2, '0')).join(''); };
  card.append(ta, out, btn, hres); return card;
}
function showTool(k) {
  const map = { calculator: toolCalc, json: toolJson, timestamp: toolTs, units: toolUnits, textstats: toolStats };
  const label = { calculator: T[LOC].toolCalc, json: T[LOC].toolJson, timestamp: T[LOC].toolTs, units: T[LOC].toolUnits, textstats: T[LOC].toolStats }[k];
  botSay(label + ':', [anchorChip()], map[k]());
}
function reset() { S.visited = []; S.depth = 0; S.fallbackIdx = 0; build(); botSay(PACK.brand.welcome[LOC] || PACK.brand.welcome.en, welcomeChips()); }
build();
botSay(PACK.brand.welcome[LOC] || PACK.brand.welcome.en, welcomeChips());
