/* Shot 9 — Recap: the parcel, then the label sticks to it; zoom out on Data City. */
FIGS.push({
  id: 'recap', name: 'Recap: zoom out', shot: 'Shot 9', settle: 6800,
  vo: 'This is how we can make sure that our data around the organization is used confidently.',
  visual: 'Visual recap: first the parcel, then the label is stuck to it. Zoom out on Data City.',
  hint: 'Space or click: next step (parcel → label → zoom out) · r resets',
  aria: 'Isometric data parcel on a pedestal in the middle of Data City. Press space or click to step: first the parcel, then the data-contract label sticks to it, then the view zooms out to the whole city lighting up. Press r to reset.',
  css: `[data-fig="recap"] .go{cursor:pointer}`,
  mount(stage, api) {
    const T = 70, G = 8, N = 5, EXT = N * T + (N - 1) * G;
    const K = api.iso.frame([[0, 0, 0], [EXT, 0, 0], [0, EXT, 0], [EXT, EXT, 0], [0, 0, 60]], .03), { TOP, FRONT, box, P } = K;
    const slots = [[6, 6, 26, 24], [38, 8, 26, 22], [6, 38, 24, 26], [38, 36, 26, 28]];
    const order = []; for (let s = 0; s <= 2 * (N - 1); s++) for (let i = 0; i < N; i++) { const j = s - i; if (j >= 0 && j < N) order.push([i, j]); }
    const cx0 = 2 * (T + G), cy0 = 2 * (T + G), PW = 18, PD = 16, PH = 14, PXc = cx0 + 26, PYc = cy0 + 27, PZ = 9;
    let svg = '';
    order.forEach(([i, j]) => {
      const ox = i * (T + G), oy = j * (T + G), ring = Math.max(Math.abs(i - 2), Math.abs(j - 2)), rnd = seeded(31 + i * 5 + j * 11);
      svg += `<g class="tile" data-ring="${ring}">` + plate(K, ox, oy, T, T, 6, { r: 6, noscrew: true });
      if (ring > 0) slots.forEach((sl, k) => { if (k >= 2 && rnd() < .3) return; const h = (i + j > 4 ? 14 : 18) + Math.round(rnd() * (i + j > 4 ? 14 : 30)); svg += bldg(K, ox + sl[0], oy + sl[1], sl[2], sl[3], h, rnd, { rh: 7, cw: 6 }); });
      else {
        svg += `<g transform="${TOP(ox, oy, 6)}"><circle class="halo" id="recap-halo" cx="35" cy="35" r="34" filter="url(#bloom)"/></g>` + box(ox + 18, oy + 19, 6, 28, 26, 3, 3);
        svg += `<g transform="${TOP(ox + 18, oy + 19, 9)}"><rect class="detail" x="3" y="3" width="22" height="20" rx="2"/></g>`;
        svg += `<g class="go" id="recap-parcel">${parcel(K, PXc, PYc, PZ, PW, PD, PH)}<g transform="${FRONT(PXc, PYc + PD, PZ + PH)}"><g id="recap-st" style="opacity:0"><rect class="tag hot" x="2" y="1.6" width="14" height="9.6" rx="1"/><rect class="scr-accent" x="3.6" y="3" width="7" height=".8"/>${[0, 1, 2, 3, 4].map(r => `<circle class="led" id="recap-d${r}" cx="4" cy="${5.6 + r * 1.2}" r=".42"/><rect class="scr-accent" x="5.4" y="${5.3 + r * 1.2}" width="${6 + (r % 3)}" height=".55"/>`).join('')}</g></g></g>`;
      }
      svg += '</g>';
    });
    stage.setAttribute('viewBox', K.viewBox); stage.innerHTML = svg;

    const q = s => stage.querySelector(s), stk = q('#recap-st'), dots = [0, 1, 2, 3, 4].map(r => q('#recap-d' + r)), ringWins = [1, 2].map(r => [...stage.querySelectorAll(`.tile[data-ring="${r}"] .wins`)]);
    const c = K.P(PXc + PW / 2, PYc + PD / 2, PZ + PH / 2), Wz = 120, Wf = K.vb[2], f = [K.vb[0] + K.vb[2] / 2, K.vb[1] + K.vb[3] / 2];
    const st = { step: 0, t: [0, -1e9, -1e9] }; let T0 = 0, lastSig = '';
    api.loop(t => {
      T0 = t; const lp = clamp((t - st.t[1]) / 1000), zp = ease(clamp((t - st.t[2]) / 2600)), zl = st.step < 2 && t - st.t[2] > 3000 ? 0 : zp;
      const W = Math.exp(lerp(Math.log(Wz), Math.log(Wf), zl)), H = W * .75, cxv = lerp(c[0], f[0], zl), cyv = lerp(c[1], f[1], zl);
      stage.setAttribute('viewBox', `${(cxv - W / 2).toFixed(2)} ${(cyv - H / 2).toFixed(2)} ${W.toFixed(2)} ${H.toFixed(2)}`);
      const e = st.step >= 1 ? easeOut(lp) : 0; stk.setAttribute('transform', `translate(9 6.4) scale(${(e * (1.35 - .35 * e)).toFixed(3)}) translate(-9 -6.4) translate(0 ${(-(1 - e) * 10).toFixed(2)})`); stk.style.opacity = st.step >= 1 ? clamp(lp * 3) : 0;
      const dn = dots.map((_, r) => st.step >= 1 && lp > .35 + r * .12), r1 = st.step >= 2 && zp > .12, r2 = st.step >= 2 && zp > .4;
      const sig = [...dn, r1, r2, st.step, zl > .97].join(); if (sig !== lastSig) { lastSig = sig;
        dots.forEach((d, i) => d.classList.toggle('hot', dn[i])); ringWins[0].forEach(w => w.classList.toggle('lit', r1)); ringWins[1].forEach(w => w.classList.toggle('lit', r2));
        q('#recap-halo').classList.toggle('hot', st.step >= 1); api.power(st.step >= 1);
        api.readout(['a data product · a parcel of data', 'data contract attached · the label sticks', zl > .97 ? 'data city · used confidently' : 'zooming out…'][st.step]); }
    });
    const next = () => { if (st.step === 2) { st.step = 0; st.t = [0, -1e9, -1e9]; return; } st.step++; st.t[st.step] = T0; }, reset = () => { st.step = 0; st.t = [0, -1e9, -1e9]; };
    stage.addEventListener('click', () => next());
    api.readout('a data product · a parcel of data');
    return { key: e => { if (e.key === ' ' || e.key === 'Enter') { next(); return true; } if (e.key === 'r' || e.key === 'R') { reset(); return true; } return false; }, demo: () => { reset(); api.after(500, next); api.after(2600, next); } };
  },
});
