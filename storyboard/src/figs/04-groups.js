/* Shot 4 — On the machine's screen, loose data points are assigned into groups. */
FIGS.push({
  id: 'groups', name: 'Assigning purpose', shot: 'Shot 4',
  vo: 'By assigning purpose and managing the loose data, it now becomes a data product that can help the entire organization.',
  visual: "On the screen of the machine, collected data (social media icons, event metrics) is assigned into groups.",
  hint: 'Press the button · s sort · r reset · space toggles',
  aria: 'Isometric machine with a large screen. Nine loose data icons drift on the screen. Click the console button, or press s, to assign them into three groups: social, event and reach. Press r to scatter them again.',
  css: `[data-fig="groups"] .go{cursor:pointer}[data-fig="groups"] .cell .face{fill:#e9ecf1;transition:fill .4s}[data-fig="groups"] .cell.hot .face{fill:var(--navy)}[data-fig="groups"] .cell .lab{fill:var(--navy);opacity:.55;font-size:5.4px}[data-fig="groups"] .cell.hot .lab{opacity:1;fill:var(--white)}`,
  mount(stage, api) {
    const K = api.iso.frame([[0, 0, 0], [240, 0, 0], [0, 150, 0], [240, 150, 0], [24, 24, 142]], .04), { TOP, FRONT, SIDE, box } = K, slits = api.iso.slits;
    const GR = ['SOCIAL', 'EVENT', 'REACH'], CX = [12, 70, 128];
    const items = [['heart', 0], ['ticket', 1], ['bars', 2], ['chat', 0], ['pin', 1], ['play', 2], ['play', 0], ['cam', 1], ['chat', 2]];
    const start = [[26, 44], [64, 58], [102, 42], [142, 60], [172, 46], [42, 74], [86, 72], [126, 74], [162, 72]];
    const slotIdx = [0, 0, 0, 1, 1, 1, 2, 2, 2].map((_, i) => items.slice(0, i).filter(it => it[1] === items[i][1]).length);
    const target = items.map(([, g], i) => [CX[g] + 9 + slotIdx[i] * 17, 111]);
    let svg = plate(K, 0, 0, 240, 150, 6, { r: 10 });
    svg += `<g transform="${FRONT(0, 150, 6)}"><text class="label" x="14" y="4.6" font-size="3.8">DATA PRODUCTS · GROUPING</text></g>`;
    svg += box(24, 24, 6, 192, 12, 130, 5);
    svg += `<g transform="${TOP(24, 24, 136)}">${slits(14, 178, 8, 3, 9)}</g>`;
    svg += `<g transform="${FRONT(24, 36, 136)}">
      <rect class="face recess" x="5" y="5" width="182" height="120" rx="6"/>
      <rect class="halo hot" id="groups-halo" x="8" y="8" width="176" height="114" rx="4" filter="url(#bloom)"/>
      <rect class="face glass hot" id="groups-screen" x="8" y="8" width="176" height="114" rx="4" filter="url(#soft)"/>
      <g filter="url(#soft)"><text class="scr" x="14" y="21" font-size="7">INGESTED DATA</text><text class="scr" id="groups-count" x="178" y="21" font-size="7" text-anchor="end">9 POINTS</text></g>
      <line class="detail" x1="12" y1="26" x2="180" y2="26"/>
      ${GR.map((g, k) => `<g class="cell" id="groups-c${k}"><rect class="face recess" x="${CX[k]}" y="84" width="52" height="34" rx="3"/><text class="lab scr" x="${CX[k] + 4}" y="93" font-size="5.4">${g}</text></g>`).join('')}
      <g id="groups-ic"></g></g>`;
    svg += box(100, 92, 6, 40, 24, 8, 2) + `<g transform="${TOP(100, 92, 14)}"><rect class="detail" x="4" y="4" width="32" height="16" rx="2"/></g>`;
    svg += `<g class="press go" id="groups-btn">${box(110, 100, 14, 20, 8, 4, 3)}</g>`;
    stage.setAttribute('viewBox', K.viewBox); stage.innerHTML = svg;

    const q = s => stage.querySelector(s), root = q('#groups-ic'); root.innerHTML = items.map(([k]) => icon(k)).join('');
    const els = [...root.children], cells = GR.map((_, k) => q('#groups-c' + k)), N = items.length, S = 1.0;
    const st = { dir: 0, t0: -1e9, sorted: false }; let T = 0, lastSig = '';
    api.loop(t => {
      T = t; const arrived = [0, 0, 0];
      els.forEach((el, i) => {
        let p = clamp((T - st.t0 - i * 110) / 900); if (!st.dir) p = 1 - p; if (st.t0 < 0 && !st.dir) p = 0;
        const e = ease(p), s = start[i], tg = target[i], sway = (1 - e) * 1;
        const x = lerp(s[0] + Math.sin(T / 700 + i * 1.9) * 2.2 * sway, tg[0], e), y = lerp(s[1] + Math.cos(T / 620 + i * 1.3) * 2.2 * sway, tg[1], e);
        el.setAttribute('transform', `translate(${x.toFixed(2)} ${y.toFixed(2)}) scale(${(S * (1 - .12 * e)).toFixed(3)})`);
        if (p >= 1 && st.dir) arrived[items[i][1]]++;
      });
      const sig = arrived.join(','); if (sig !== lastSig) { lastSig = sig; cells.forEach((c, k) => c.classList.toggle('hot', arrived[k] === 3)); render(); }
    });
    function render() {
      const done = lastSig === '3,3,3';
      q('#groups-count').textContent = done ? '3 DATA PRODUCTS' : st.dir ? 'SORTING…' : '9 POINTS';
      api.power(true); api.readout(done ? 'sorted · 3 groups of 3' : st.dir ? 'sorting' : 'loose · 9 points');
    }
    const sort = on => { st.dir = on ? 1 : 0; st.t0 = T; lastSig = ''; cells.forEach(c => c.classList.remove('hot')); render(); };
    q('#groups-btn').addEventListener('click', () => { api.flash(q('#groups-btn')); sort(!st.dir); });
    render();
    return {
      key: e => {
        if (e.key === 's' || e.key === 'S') { sort(true); return true; } if (e.key === 'r' || e.key === 'R') { sort(false); return true; }
        if (e.key === ' ' || e.key === 'Enter') { api.flash(q('#groups-btn')); sort(!st.dir); return true; } return false;
      },
      demo: () => api.after(300, () => sort(true)),
    };
  },
});
