// Client-side search over the per-language index.json (see layouts/index.json).
(() => {
  const input = document.getElementById('search-input');
  const list = document.getElementById('search-results');
  const status = document.getElementById('search-status');
  if (!input) return;
  const T = { found: input.dataset.found, none: input.dataset.none };
  let index = null;
  const esc = s => s.replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
  const load = () => index || (index = fetch(input.dataset.index).then(r => r.json()).then(items =>
    items.map(p => ({ ...p, title: p.t.toLowerCase(), meta: (p.c + ' ' + p.g + ' ' + p.s).toLowerCase(), body: p.x.toLowerCase() }))));
  function score(p, terms) {
    let total = 0;
    for (const t of terms) {
      if (p.title.includes(t)) total += 10;
      else if (p.meta.includes(t)) total += 5;
      else if (p.body.includes(t)) total += 1;
      else return 0;              // every term must match somewhere
    }
    return total;
  }
  function highlight(text, terms) {
    let out = esc(text);
    for (const t of terms) out = out.replace(new RegExp(t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'gi'), m => '<mark>' + m + '</mark>');
    return out;
  }
  async function run() {
    const q = input.value.trim();
    history.replaceState(null, '', q ? '?q=' + encodeURIComponent(q) : location.pathname);
    if (!q) { list.innerHTML = ''; status.textContent = ''; return; }
    const terms = q.toLowerCase().split(/\s+/).filter(Boolean);
    const hits = (await load()).map(p => [score(p, terms), p]).filter(([s]) => s > 0)
      .sort((a, b) => b[0] - a[0] || b[1].d.localeCompare(a[1].d)).slice(0, 50);
    status.textContent = hits.length ? T.found.replace('{n}', hits.length) : T.none;
    list.innerHTML = hits.map(([, p]) =>
      `<li><time datetime="${p.d}">${p.d}</time><a href="${p.u}">${highlight(p.t, terms)}</a>${p.c ? `<span class="home2-tag">${esc(p.c)}</span>` : ''}</li>`).join('');
  }
  let timer;
  input.addEventListener('input', () => { clearTimeout(timer); timer = setTimeout(run, 120); });
  const q0 = new URLSearchParams(location.search).get('q');
  if (q0) { input.value = q0; run(); }
  input.focus();
})();
