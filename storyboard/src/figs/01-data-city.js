/* Shot 1 — Data City: nine city blocks around an event plaza; blocks part, data floats up. */
FIGS.push({
  id: 'data-city', name: 'Data City', shot: 'Shot 1',
  vo: 'Every day across Global Media Services, teams create valuable data points.',
  visual: 'Open on Data City, zooming into a live music event. Isometric squares move away. Data icons float up from the event.',
  hint: 'Click the stage: data on/off · click any block: part the city · z',
  aria: 'Isometric city of nine blocks around a live music event. Click the event plaza to switch the floating data icons on or off. Click any other block, or press z, to part the city blocks.',
  css: `[data-fig="data-city"] .tile{cursor:pointer}[data-fig="data-city"] .tile:hover > .face.top{stroke:var(--ink)}`,
  mount(stage, api) {
    const T = 96, G = 10, N = 3, MAXSP = 40, EXT = N * T + (N - 1) * G;
    const K = api.iso.frame([[-MAXSP, -MAXSP, 0], [EXT + MAXSP, -MAXSP, 0], [-MAXSP, EXT + MAXSP, 0], [EXT + MAXSP, EXT + MAXSP, 0], [0, 0, 100]], .02);
    const { TOP, FRONT, box, rect, P } = K;
    const slots = [[8, 8, 36, 32], [50, 10, 36, 30], [10, 52, 32, 34], [52, 54, 34, 32]];
    const order = [];
    for (let s = 0; s <= 4; s++) for (let i = 0; i < N; i++) { const j = s - i; if (j >= 0 && j < N) order.push([i, j]); }
    let svg = '', ex = '';
    const cx0 = 1 * (T + G), cy0 = 1 * (T + G);
    order.forEach(([i, j]) => {
      const ox = i * (T + G), oy = j * (T + G), center = i === 1 && j === 1, rnd = seeded(17 + i * 7 + j * 13);
      svg += `<g class="tile" data-i="${i}" data-j="${j}" data-c="${center ? 1 : 0}">` + plate(K, ox, oy, T, T, 6, { r: 8 });
      if (!center) {
        slots.forEach((sl, k) => {
          if (k >= 2 && rnd() < .35) return;
          const h = i + j > 2 ? 14 + Math.round(rnd() * 16) : 22 + Math.round(rnd() * 44) + (i + j < 2 ? 10 : 0);
          svg += bldg(K, ox + sl[0], oy + sl[1], sl[2], sl[3], h, rnd, { lit: true });
        });
        if (rnd() < .6) svg += tree(K, ox + 44, oy + 46, 6, 5);
      } else {
        const x = ox, y = oy;
        svg += `<g transform="${FRONT(x, y + T, 6)}"><text class="label" x="8" y="4.6" font-size="3.8">EVENT PLAZA · LIVE</text></g>`;
        svg += box(x + 12, y + 8, 6, 72, 20, 6, 1);
        svg += box(x + 14, y + 8, 12, 68, 3, 30, 0);
        svg += `<g transform="${FRONT(x + 14, y + 11, 42)}">
          <rect class="halo" id="data-city-halo" width="68" height="30" rx="2" filter="url(#bloom)"/>
          <rect class="face glass" id="data-city-screen" width="68" height="30" rx="2" filter="url(#soft)"/>
          <g id="data-city-eq" filter="url(#soft)">${Array.from({ length: 12 }, (_, b) => `<rect class="scr-accent" x="${4 + b * 5.2}" y="14" width="3.4" height="14"/>`).join('')}</g>
          <text class="scr" x="4" y="9" font-size="5">LIVE ▸ 21:04</text></g>`;
        [[x + 4, y + 12], [x + 84, y + 12]].forEach(([a, b]) => {
          svg += box(a, b, 6, 8, 8, 22, 1) + `<g transform="${FRONT(a, b + 8, 28)}"><circle class="detail" cx="4" cy="6" r="2.6"/><circle class="detail" cx="4" cy="15" r="3.4"/></g>`;
        });
        svg += box(x + 10, y + 9, 6, 2, 2, 40, 0) + box(x + 84, y + 9, 6, 2, 2, 40, 0) + box(x + 10, y + 9, 44, 76, 2, 2, 0);
        svg += `<g transform="${TOP(x, y, 6)}"><line class="detail dash" x1="8" y1="38" x2="88" y2="38"/></g>`;
        const r2 = seeded(5);
        [48, 58, 68, 78, 88].forEach(yy => { for (let xx = 12; xx <= 86; xx += 9) svg += spectator(K, x + xx + (r2() - .5) * 2, y + yy, 6, r2() < .25); });
      }
      svg += '</g>';
    });
    svg += '<g id="data-city-fl"></g>';
    stage.setAttribute('viewBox', K.viewBox); stage.innerHTML = svg;

    const q = s => stage.querySelector(s), tiles = [...stage.querySelectorAll('.tile')], eq = [...stage.querySelectorAll('#data-city-eq rect')];
    const src = [[30, 50], [48, 60], [66, 50], [22, 72], [74, 70], [48, 82], [36, 66], [60, 78]].map(([a, b]) => [cx0 + a, cy0 + b, 18]);
    const em = emitter(api, K, q('#data-city-fl'), src, { n: 9, rise: 95, s: 1.9, period: 5200, drift: 26 });
    const st = { on: true, sp: 0, target: 0 };
    function render() {
      q('#data-city-screen').classList.toggle('hot', st.on); q('#data-city-halo').classList.toggle('hot', st.on);
      stage.querySelectorAll('.wins').forEach(w => w.classList.toggle('lit', st.on));
      em.set(st.on); api.power(st.on);
      api.readout((st.on ? 'data flowing' : 'data off') + ' · ' + (st.target > 5 ? 'city parted' : 'city closed'));
    }
    let last = 0;
    api.loop(t => {
      const dt = Math.min(64, t - last); last = t;
      st.sp += (st.target - st.sp) * Math.min(1, dt / 320);
      tiles.forEach(el => {
        if (el.dataset.c === '1') return; const i = +el.dataset.i - 1, j = +el.dataset.j - 1;
        setTr(K, el, i * st.sp, j * st.sp, 0);
      });
      eq.forEach((b, k) => { const h = st.on ? 3 + 22 * Math.abs(Math.sin(t / 240 + k * 1.1)) * (.5 + .5 * Math.sin(t / 900 + k)) ** 2 + 3 : 2; b.setAttribute('height', h.toFixed(1)); b.setAttribute('y', (28 - h).toFixed(1)); });
    });
    const toggleData = () => { st.on = !st.on; render(); }, part = () => { st.target = st.target > 5 ? 0 : MAXSP; render(); };
    stage.addEventListener('click', e => { const t = e.target.closest('.tile'); if (!t) return; if (t.dataset.c === '1') toggleData(); else part(); });
    render();
    return {
      key: e => { if (e.key === ' ' || e.key === 'Enter') { toggleData(); return true; } if (e.key === 'z' || e.key === 'Z') { part(); return true; } return false; },
      demo: () => { st.target = 34; render(); },
    };
  },
});
