const $ = s => document.querySelector(s), root = document.documentElement;
const ic = n => `<svg class="i" aria-hidden="true"><use href="#i-${n}"/></svg>`;

/* ---------- appearance ---------- */
document.querySelectorAll('.darkBtn').forEach(b => b.onclick = () => {
  root.dataset.dark = root.dataset.dark === '1' ? '0' : '1'; localStorage.dark = root.dataset.dark; });
const syncSwatches = () => document.querySelectorAll('.sw').forEach(s => s.setAttribute('aria-pressed', s.dataset.theme === root.dataset.theme));
document.querySelectorAll('.sw').forEach(s => s.onclick = () => {
  root.dataset.theme = s.dataset.theme; localStorage.theme = s.dataset.theme; syncSwatches(); });
syncSwatches();

/* ---------- auth ---------- */
const pwToggle = $('#pwToggle');
if (pwToggle) pwToggle.onclick = () => {
  const f = $('#pw'), show = f.type === 'password';
  f.type = show ? 'text' : 'password';
  pwToggle.setAttribute('aria-pressed', show); pwToggle.setAttribute('aria-label', show ? 'Hide password' : 'Show password');
  pwToggle.innerHTML = ic(show ? 'eye-off' : 'eye');
};
const authForm = $('form.auth');
if (authForm) authForm.addEventListener('submit', () => {
  const b = $('#authSubmit'); b.classList.add('loading'); setTimeout(() => b.disabled = true, 0); });
addEventListener('pageshow', e => { if (e.persisted) { const b = $('#authSubmit'); if (b) { b.disabled = false; b.classList.remove('loading'); } } });

if ($('#chatApp')) initChat();

function initChat() {
  let cur = null, speak = false, busy = false, toastTimer, chats = [], listLoaded = false;
  const msgs = $('#msgs'), input = $('#input'), list = $('#chatList'), sendBtn = $('#sendBtn'), title = $('#chatTitle');
  const side = $('#side'), scrim = $('#scrim'), toBottom = $('#toBottom'), count = $('#count'), search = $('#search');
  const CSRF = document.querySelector('meta[name=csrf]').content;
  const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const MAX = +input.maxLength || 2000;

  const esc = t => t.replace(/[&<>"]/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[c]));

  /* ---------- scrolling ---------- */
  const nearBottom = () => msgs.scrollHeight - msgs.scrollTop - msgs.clientHeight < 120;
  const scroll = force => { if (force || nearBottom()) msgs.scrollTop = msgs.scrollHeight; };
  msgs.addEventListener('scroll', () => { toBottom.hidden = nearBottom(); }, {passive: true});
  toBottom.onclick = () => msgs.scrollTo({top: msgs.scrollHeight, behavior: reduceMotion ? 'auto' : 'smooth'});

  function toast(text) {
    const t = $('#toast'); t.textContent = text; t.hidden = false;
    clearTimeout(toastTimer); toastTimer = setTimeout(() => t.hidden = true, 2200);
  }
  async function copy(text) {
    try { await navigator.clipboard.writeText(text); return true; } catch { return false; }
  }

  /* ---------- lightweight, safe markdown ---------- */
  function inline(t) {
    return esc(t)
      .replace(/`([^`]+)`/g, '<code>$1</code>')
      .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
      .replace(/(^|[\s(])\*([^*\s][^*\n]*?)\*(?=$|[\s).,!?:;])/g, '$1<em>$2</em>')
      .replace(/\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>');
  }
  const cells = l => l.trim().replace(/^\||\|$/g, '').split('|').map(c => c.trim());
  const isSep = l => l.includes('-') && /^\s*\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?\s*$/.test(l);
  function md(src) {
    const code = [];
    src = src.replace(/```([\w+-]*)[^\S\n]*\n?([\s\S]*?)```/g, (_, lang, body) => {
      code.push({lang, body: body.replace(/\n$/, '')}); return `\n\u0000${code.length - 1}\u0000\n`; });
    const out = [], lines = src.split('\n'); let para = [], list = null, quote = [];
    const flushPara = () => { if (para.length) out.push('<p>' + para.map(inline).join('<br>') + '</p>'); para = []; };
    const flushList = () => { if (list) out.push(`<${list.tag}>${list.items.map(i => '<li>' + inline(i) + '</li>').join('')}</${list.tag}>`); list = null; };
    const flushQuote = () => { if (quote.length) out.push('<blockquote>' + quote.map(inline).join('<br>') + '</blockquote>'); quote = []; };
    const flush = () => { flushPara(); flushList(); flushQuote(); };
    for (let k = 0; k < lines.length; k++) {
      const line = lines[k]; let m;
      if ((m = line.match(/^\u0000(\d+)\u0000$/))) {
        flush(); const c = code[+m[1]];
        out.push(`<div class="codeblock"><div class="codehead"><span>${esc(c.lang || 'code')}</span>` +
          `<button type="button" class="copy">${ic('copy')}<span>Copy</span></button></div><pre><code>${esc(c.body)}</code></pre></div>`);
      } else if (line.includes('|') && k + 1 < lines.length && isSep(lines[k + 1]) && lines[k + 1].includes('|')) {
        flush(); const head = cells(line); k += 2; const rows = [];
        while (k < lines.length && lines[k].includes('|') && lines[k].trim()) rows.push(cells(lines[k++]));
        k--;
        out.push('<div class="tablewrap"><table><thead><tr>' + head.map(h => '<th>' + inline(h) + '</th>').join('') + '</tr></thead><tbody>' +
          rows.map(r => '<tr>' + head.map((_, i) => '<td>' + inline(r[i] || '') + '</td>').join('') + '</tr>').join('') + '</tbody></table></div>');
      } else if ((m = line.match(/^(#{1,4})\s+(.*)$/))) {
        flush(); const n = Math.min(m[1].length + 1, 4); out.push(`<h${n}>${inline(m[2])}</h${n}>`);
      } else if (/^\s*([-*_])\1{2,}\s*$/.test(line)) {
        flush(); out.push('<hr>');
      } else if ((m = line.match(/^>\s?(.*)$/))) {
        flushPara(); flushList(); quote.push(m[1]);
      } else if ((m = line.match(/^\s*[-*+]\s+(.*)$/))) {
        flushPara(); flushQuote(); if (!list || list.tag !== 'ul') { flushList(); list = {tag: 'ul', items: []}; } list.items.push(m[1]);
      } else if ((m = line.match(/^\s*\d+[.)]\s+(.*)$/))) {
        flushPara(); flushQuote(); if (!list || list.tag !== 'ol') { flushList(); list = {tag: 'ol', items: []}; } list.items.push(m[1]);
      } else if (!line.trim()) { flush(); }
      else { flushList(); flushQuote(); para.push(line); }
    }
    flush();
    return out.join('');
  }

  /* ---------- API ---------- */
  async function api(u, o = {}) {
    const r = await fetch(u, {...o, headers: {...o.headers, 'X-CSRF-Token': CSRF}});
    if (r.status === 401) { location = '/login'; throw new Error('Login required'); }
    let data = null; try { data = await r.json(); } catch {}
    if (!r.ok) throw new Error((data && data.error) || 'Request failed (' + r.status + ')');
    return data;
  }
  const post = (u, b) => api(u, {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(b || {})});

  /* ---------- messages ---------- */
  function addMsg(role, html, opts = {}) {
    const m = document.createElement('div'); m.className = 'msg ' + (role === 'user' ? 'user' : 'bot');
    if (role === 'user') m.innerHTML = '<div class="bubble">' + html + '</div>';
    else m.innerHTML = '<div class="avatar"><svg class="mark" aria-hidden="true"><use href="#mark"/></svg></div>' +
      '<div class="col"><div class="bubble' + (opts.err ? ' err' : '') + '">' + html + '</div></div>';
    msgs.appendChild(m); scroll(opts.force); return m.querySelector('.bubble');
  }
  function finishBot(bubble, text) {
    bubble.classList.remove('plain'); bubble.innerHTML = md(text);
    const col = bubble.parentElement;
    if (!col.querySelector('.actions')) {
      const a = document.createElement('div'); a.className = 'actions';
      a.innerHTML = `<button type="button" class="icon" title="Copy reply" aria-label="Copy reply">${ic('copy')}</button>`;
      a.firstChild.onclick = async () => toast(await copy(text) ? 'Reply copied' : 'Copy failed');
      col.appendChild(a);
    }
  }
  msgs.addEventListener('click', async e => {
    const b = e.target.closest('.copy'); if (!b) return;
    const ok = await copy(b.closest('.codeblock').querySelector('code').textContent);
    const label = b.querySelector('span'); label.textContent = ok ? 'Copied' : 'Failed';
    setTimeout(() => label.textContent = 'Copy', 1600);
  });

  const SUGGESTIONS = [
    ['smile', 'Tell me a joke', 'Lighten up the day', 'Tell me a joke'],
    ['bulb', 'What can you do?', 'See what Nova can help with', 'What can you do?'],
    ['calc', 'Quick maths', 'Evaluate 12*(3+4)', '12*(3+4)'],
    ['code', 'Write some code', 'A Python hello world', 'python hello world'],
  ];
  function setTitle(t) { title.textContent = t || 'New chat'; document.title = (t ? t + ' \u00b7 ' : '') + 'Nova AI'; }
  function welcome() {
    setTitle(''); toBottom.hidden = true;
    msgs.innerHTML = '<div class="welcome"><svg class="mark" aria-hidden="true"><use href="#mark"/></svg>' +
      '<h2>How can I help you today?</h2><p>Ask a question, start a task, or pick a suggestion below.</p><div class="suggest">' +
      SUGGESTIONS.map(s => `<button type="button" class="sg" data-p="${esc(s[3])}">${ic(s[0])}<span><b>${esc(s[1])}</b><small>${esc(s[2])}</small></span></button>`).join('') + '</div></div>';
    msgs.querySelectorAll('.sg').forEach(c => c.onclick = () => send(c.dataset.p));
  }

  /* ---------- sidebar: grouped, searchable history ---------- */
  function bucket(iso) {
    const d = new Date(iso); if (isNaN(d)) return 'Earlier';
    const today = new Date(); today.setHours(0, 0, 0, 0);
    const days = Math.floor((today - new Date(d.getFullYear(), d.getMonth(), d.getDate())) / 864e5);
    return days <= 0 ? 'Today' : days === 1 ? 'Yesterday' : days <= 7 ? 'Previous 7 days' : days <= 30 ? 'Previous 30 days' : 'Earlier';
  }
  function renderList() {
    const q = search.value.trim().toLowerCase();
    const shown = chats.filter(c => !q || c.title.toLowerCase().includes(q));
    list.innerHTML = '';
    if (!shown.length) { list.innerHTML = `<div class="empty">${chats.length ? 'No chats match your search.' : 'No conversations yet.'}</div>`; return; }
    let last = '';
    shown.forEach(c => {
      const g = bucket(c.created);
      if (g !== last) { const h = document.createElement('div'); h.className = 'group'; h.textContent = g; list.appendChild(h); last = g; }
      const d = document.createElement('div'); d.className = 'item' + (c.id === cur ? ' active' : '');
      d.tabIndex = 0; d.setAttribute('role', 'button');
      if (c.id === cur) { d.setAttribute('aria-current', 'true'); setTitle(c.title === 'New chat' ? '' : c.title); }
      d.innerHTML = `<span>${esc(c.title)}</span><button type="button" class="del" title="Delete chat" aria-label="Delete chat">${ic('trash')}</button>`;
      d.onclick = () => openChat(c.id);
      d.onkeydown = e => { if (e.target === d && (e.key === 'Enter' || e.key === ' ')) { e.preventDefault(); openChat(c.id); } };
      const del = d.querySelector('.del'); let t;
      del.onclick = async e => {
        e.stopPropagation();
        if (!del.classList.contains('confirm')) {
          del.classList.add('confirm'); del.textContent = 'Delete?';
          t = setTimeout(() => { del.classList.remove('confirm'); del.innerHTML = ic('trash'); }, 3000); return; }
        clearTimeout(t);
        try { await api('/api/chats/' + c.id, {method: 'DELETE'}); } catch (err) { return toast(err.message); }
        if (cur === c.id) { cur = null; welcome(); }
        toast('Chat deleted'); loadList();
      };
      list.appendChild(d);
    });
  }
  async function loadList() {
    if (!listLoaded) list.innerHTML = '<div class="skel"></div><div class="skel"></div><div class="skel"></div>';
    try { chats = await api('/api/chats'); listLoaded = true; } catch { if (!listLoaded) list.innerHTML = '<div class="empty">Could not load chats.</div>'; return; }
    renderList();
  }
  async function openChat(id) {
    closeSide();
    try {
      const rows = await api('/api/chats/' + id);
      cur = id; msgs.innerHTML = '';
      rows.forEach(m => { if (m.role === 'user') addMsg('user', esc(m.content)); else finishBot(addMsg('bot', ''), m.content); });
      if (!rows.length) welcome();
      scroll(true); toBottom.hidden = true;
    } catch (e) { toast(e.message); }
    renderList();
  }
  search.oninput = renderList;

  function typeOut(el, text) {
    if (reduceMotion) return Promise.resolve();
    el.classList.add('plain');
    return new Promise(res => {
      let i = 0; const step = Math.max(3, Math.ceil(text.length / 120));
      const t = setInterval(() => { i += step; el.textContent = text.slice(0, i); scroll();
        if (i >= text.length) { clearInterval(t); res(); } }, 16); });
  }

  /* ---------- sending ---------- */
  const refreshSend = () => {
    sendBtn.disabled = busy || !input.value.trim();
    const n = input.value.length; count.hidden = n < MAX * 0.8;
    count.textContent = (MAX - n); count.classList.toggle('warn', n >= MAX * 0.95);
  };
  async function send(text) {
    text = (text || input.value).trim(); if (!text || busy) return;
    busy = true; input.value = ''; input.style.height = 'auto'; refreshSend();
    const w = $('.welcome'); if (w) w.remove();
    addMsg('user', esc(text), {force: true});
    const t = addMsg('bot', '<span class="typing" aria-label="Nova is typing"><i></i><i></i><i></i></span>', {force: true});
    try {
      if (!cur) cur = (await post('/api/chats')).id;
      const r = await post(`/api/chats/${cur}/send`, {message: text});
      await typeOut(t, r.reply);
      finishBot(t, r.reply); scroll();
      if (speak && 'speechSynthesis' in window) speechSynthesis.speak(new SpeechSynthesisUtterance(r.reply.replace(/[`*#]/g, '')));
    } catch (e) {
      t.classList.add('err'); t.textContent = e.message || 'Something went wrong. Please try again.';
    } finally {
      busy = false; refreshSend(); input.focus(); loadList();
    }
  }

  /* ---------- UI wiring ---------- */
  sendBtn.onclick = () => send();
  input.onkeydown = e => { if (e.key === 'Enter' && !e.shiftKey && !e.isComposing) { e.preventDefault(); send(); } };
  input.oninput = () => { input.style.height = 'auto'; input.style.height = Math.min(input.scrollHeight, 160) + 'px'; refreshSend(); };
  const openSide = () => { side.classList.add('open'); scrim.hidden = false; };
  function closeSide() { side.classList.remove('open'); scrim.hidden = true; }
  const newChat = () => { cur = null; welcome(); renderList(); closeSide(); input.focus(); };
  $('#menu').onclick = openSide; $('#closeSide').onclick = closeSide; scrim.onclick = closeSide;
  $('#newChat').onclick = newChat;
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape') closeSide();
    else if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key.toLowerCase() === 'o') { e.preventDefault(); newChat(); }
    else if (e.key === '/' && !/^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement.tagName) && !e.ctrlKey && !e.metaKey) { e.preventDefault(); input.focus(); }
  });

  const speakBtn = $('#speakBtn');
  speakBtn.onclick = () => {
    speak = !speak; speakBtn.setAttribute('aria-pressed', speak);
    speakBtn.innerHTML = ic(speak ? 'volume' : 'volume-off');
    if (!speak && 'speechSynthesis' in window) speechSynthesis.cancel();
    toast(speak ? 'Replies will be read aloud' : 'Read aloud off');
  };
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition, mic = $('#mic');
  mic.onclick = () => {
    if (!SR) return toast('Voice input is not supported in this browser (try Chrome or Edge).');
    const r = new SR(); r.lang = navigator.language || 'en-US'; mic.classList.add('rec');
    r.onresult = e => { input.value = e.results[0][0].transcript; input.oninput(); send(); };
    r.onerror = () => toast('Could not capture audio. Check microphone permission.');
    r.onend = () => mic.classList.remove('rec');
    r.start();
  };

  welcome(); loadList(); input.focus();
}
