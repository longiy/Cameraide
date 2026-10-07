/* Shot 5 — Parcels of data leave the machine, ride the belt into a van, and the van drives into the city. */
FIGS.push({
  id: 'dispatch', name: 'Data products ship', shot: 'Shot 5',
  vo: 'Data can be shared and used across the organisation by people with different needs.',
  visual: 'Boxes of different shapes and sizes come out of the machine onto the conveyor belt. Loaded into a van. The van sets off, driving into the city.',
  hint: 'Press the button · or click the machine · r resets',
  aria: 'Isometric machine that produces parcels of different sizes onto a conveyor belt. The parcels load into a van, which drives off down the road into a city. Click the machine or its button, or press space, to dispatch. Press r to reset.',
  css: `[data-fig="dispatch"] .go{cursor:pointer}`,
  mount(stage, api) {
    const K = api.iso.frame([[0, 0, 0], [380, 0, 0], [0, 120, 0], [380, 120, 0], [14, 28, 72]], .03), { TOP, FRONT, SIDE, box, rect } = K, slits = api.iso.slits;
    const VX = 150, YC = 60, rnd = seeded(41);
    let svg = plate(K, 0, 0, 380, 120, 6, { r: 10 }) + road(K, VX, 44, 230, 32, 6, 'x');
    svg += `<g transform="${FRONT(0, 120, 6)}"><text class="label" x="14" y="4.6" font-size="3.8">DISPATCH · DATA PRODUCTS</text></g>`;
    [[236, 6, 34, 32, 54], [276, 8, 30, 30, 40], [314, 6, 38, 34, 62]].forEach(b => { svg += bldg(K, b[0], b[1], b[2], b[3], b[4], rnd); });
    // machine with output hatch and a small display
    svg += box(14, 28, 6, 60, 64, 56, 3);
    svg += `<g transform="${SIDE(74, 92, 62)}"><rect class="face recess" x="22" y="37" width="20" height="13" rx="2"/><rect class="halo" id="dispatch-hatch" x="22" y="37" width="20" height="13" rx="2" filter="url(#bloom)"/></g>`;
    svg += `<g transform="${FRONT(14, 92, 62)}"><rect class="face recess" x="6" y="6" width="48" height="24" rx="3"/><rect class="halo" id="dispatch-halo" x="8" y="8" width="44" height="20" rx="2" filter="url(#bloom)"/><rect class="face glass" id="dispatch-screen" x="8" y="8" width="44" height="20" rx="2" filter="url(#soft)"/>
      <g filter="url(#soft)"><text class="scr" x="12" y="15" font-size="4">OUTPUT</text><text class="scr" id="dispatch-n" x="12" y="24" font-size="8">0/5</text></g>${slits(8, 52, 5, 36, 50)}</g>`;
    svg += `<g class="press go" id="dispatch-btn">${box(36, 100, 6, 16, 12, 6, 3)}</g>`;
    // conveyor
    svg += box(74, 52, 6, 76, 16, 6, 1);
    svg += `<g transform="${TOP(74, 52, 12)}"><clipPath id="dispatch-belt"><rect x="1" y="1" width="74" height="14"/></clipPath><g clip-path="url(#dispatch-belt)"><g id="dispatch-stripes">${slits(0, 84, 6, 1, 15)}</g></g></g>`;
    svg += box(74, 50, 12, 76, 2, 3, 0) + box(74, 68, 12, 76, 2, 3, 0);
    const v = van(K, VX, YC, 6, { lamp: 'dispatch-lamp', open: true });
    svg += `<g id="dispatch-vb">${v.back}</g>`;
    const SZ = [[10, 10, 8], [12, 10, 10], [8, 8, 14], [10, 12, 7], [12, 9, 9]];
    const SLOT = [[3, 49.5], [17, 49.5], [33, 49.5], [6, 60], [24, 61.5]];
    svg += '<g id="dispatch-boxes">' + SZ.map(([w, d, h], k) => `<g class="pbox" data-k="${k}" style="opacity:0">${parcel(K, 76, YC - d / 2, 12, w, d, h)}</g>`).join('') + '</g>';
    svg += `<g id="dispatch-vf">${v.front}</g>`;
    [[240, 88, 30, 24, 16], [280, 90, 30, 22, 20], [318, 88, 36, 26, 14]].forEach(b => { svg += bldg(K, b[0], b[1], b[2], b[3], b[4], rnd, { rh: 7 }); });
    stage.setAttribute('viewBox', K.viewBox); stage.innerHTML = svg;

    const q = s => stage.querySelector(s), boxes = [...stage.querySelectorAll('.pbox')], layer = q('#dispatch-boxes'), vb = q('#dispatch-vb'), vf = q('#dispatch-vf');
    const lamps = [...stage.querySelectorAll('.dispatch-lamp')], stripes = q('#dispatch-stripes'), city = [...stage.querySelectorAll('.wins')];
    const st = { t0: -1e9 }; let T = 0, lastOrder = '', lastSig = '';
    const vanDX = a => { const td = a - 6400; return td > 0 ? td * td * 2e-5 : 0; };
    api.loop(t => {
      T = t; const a = T - st.t0, run = a >= 0 && a < 9800, dx = run ? vanDX(a) : 0;
      if (a >= 9800 && st.t0 > -1e8) { st.t0 = -1e9; }
      const keys = []; let loaded = 0, out = 0;
      boxes.forEach((el, k) => {
        const [w, d] = SZ[k], u = clamp((a - k * 900) / 2400);
        if (!run || a < k * 900) { el.style.opacity = 0; keys.push([k, -1]); return; }
        const w2 = ease(clamp((u - .78) / .22)), tx = VX + SLOT[k][0], hy = YC - d / 2;
        const x = lerp(76, tx, u) + (u >= 1 ? dx : 0), y = lerp(hy, SLOT[k][1], w2), z = 12 + 4 * w2;
        setTr(K, el, x - 76, y - hy, z - 12); el.style.opacity = dx > 140 ? clamp(1 - (dx - 140) / 50) : 1;
        keys.push([k, x + y + z * .02]); if (u >= 1) loaded++; if (u > .15) out = Math.max(out, k + 1);
      });
      const order = keys.sort((p, r) => p[1] - r[1]).map(p => p[0]).join(''); if (order !== lastOrder) { lastOrder = order; keys.forEach(p => layer.appendChild(boxes[p[0]])); }
      [vb, vf].forEach(g => { setTr(K, g, dx, 0, 0); g.style.opacity = dx > 140 ? clamp(1 - (dx - 140) / 50) : 1; });
      stripes.setAttribute('transform', `translate(${run && a < 6400 ? ((T / 40) % 6).toFixed(2) : 0} 0)`);
      const sig = [run, loaded, out, dx > 5, dx > 60].join(); if (sig !== lastSig) { lastSig = sig; draw(run, out, loaded, dx); }
    });
    function draw(run, out, loaded, dx) {
      const live = run && out > 0;
      q('#dispatch-screen').classList.toggle('hot', run); q('#dispatch-halo').classList.toggle('hot', run); q('#dispatch-hatch').classList.toggle('hot', run && out < 5);
      q('#dispatch-n').textContent = out + '/5'; lamps.forEach(l => l.classList.toggle('hot', dx > 5)); city.forEach(w => w.classList.toggle('lit', dx > 60));
      api.power(run); api.readout(!run ? 'idle · press the button' : dx > 5 ? 'en route to the city' : `loading ${loaded}/5`);
    }
    const start = () => { if (T - st.t0 > 9800 || st.t0 < -1e8) { st.t0 = T; } };
    const reset = () => { st.t0 = -1e9; };
    ['#dispatch-btn'].forEach(s => q(s).addEventListener('click', () => { api.flash(q(s)); start(); }));
    stage.addEventListener('click', e => { if (e.target.closest('#dispatch-btn')) return; if (!e.target.closest('.wins')) start(); });
    draw(false, 0, 0, 0);
    return { key: e => { if (e.key === ' ' || e.key === 'Enter') { api.flash(q('#dispatch-btn')); start(); return true; } if (e.key === 'r' || e.key === 'R') { reset(); return true; } return false; }, demo: () => api.after(250, start) };
  },
});
