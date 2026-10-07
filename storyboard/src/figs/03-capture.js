/* Shot 3 — Capture machine: a giant data sucker pulls floating data in, a conveyor belt carries it on. */
FIGS.push({
  id: 'capture', name: 'Capture machine', shot: 'Shot 3',
  vo: 'Videos generate reactions, which can be used to measure success, giving a clear purpose to collecting this data.',
  visual: 'Another isometric square: a machine with a giant data sucker, connected to a conveyor belt. A worker presses a button and floating data is captured and ingested into the machine.',
  hint: 'Press the big button · or click the worker · space',
  aria: 'Isometric capture machine with a large funnel-shaped data sucker and a conveyor belt. A worker stands at a console. Click the console button, the worker, or press space to suck the floating data icons into the machine.',
  css: `[data-fig="capture"] .go{cursor:pointer}`,
  mount(stage, api) {
    const K = api.iso.frame([[0, 0, 0], [262, 0, 0], [0, 140, 0], [262, 140, 0], [14, 20, 76]], .04), { TOP, FRONT, SIDE, box, P } = K, slits = api.iso.slits;
    let svg = plate(K, 0, 0, 262, 140, 6, { r: 10 });
    svg += `<g transform="${FRONT(0, 140, 6)}"><text class="label" x="14" y="4.6" font-size="3.8">CAPTURE · INGEST</text></g>`;
    // machine
    svg += box(14, 20, 6, 64, 66, 56, 3) + box(58, 24, 62, 9, 9, 9, 1.5);
    svg += `<g transform="${FRONT(14, 86, 62)}">
      <rect class="face recess" x="5" y="5" width="54" height="31" rx="3"/>
      <rect class="halo" id="capture-halo" x="7" y="7" width="50" height="27" rx="2" filter="url(#bloom)"/>
      <rect class="face glass" id="capture-screen" x="7" y="7" width="50" height="27" rx="2" filter="url(#soft)"/>
      <g id="capture-scr" filter="url(#soft)"><text class="scr" x="10" y="14.5" font-size="4.2">DATA INTAKE</text>
        <text class="scr" id="capture-n" x="10" y="26" font-size="9">00/07</text>
        <rect class="face recess" x="10" y="29.6" width="44" height="2.6"/><rect class="scr-accent" id="capture-bar" x="10" y="29.6" width="0" height="2.6"/></g>
      ${slits(8, 54, 5, 42, 54)}
      <circle class="led" id="capture-l0" filter="url(#soft)" cx="9" cy="39" r="1.3"/><circle class="led" id="capture-l1" filter="url(#soft)" cx="14" cy="39" r="1.3"/><circle class="led" id="capture-l2" filter="url(#soft)" cx="19" cy="39" r="1.3"/>
    </g>`;
    // the sucker: a translucent funnel along +x, red rim at the mouth
    const cone = []; for (let k = 0; k < 48; k++) { const a = k / 48 * 2 * Math.PI; cone.push(P(80, 53 + 9 * Math.cos(a), 34 + 9 * Math.sin(a)), P(124, 53 + 25 * Math.cos(a), 34 + 25 * Math.sin(a))); }
    svg += `<defs><linearGradient id="capture-gfun" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#FFFFFF" stop-opacity=".95"/><stop offset=".65" stop-color="#FFFFFF" stop-opacity=".55"/><stop offset="1" stop-color="#C4C9D1" stop-opacity=".25"/></linearGradient></defs>`;
    svg += box(74, 45, 26, 8, 16, 16, 2);
    svg += `<polygon points="${hull2(cone).map(p => p.map(f1).join(',')).join(' ')}" style="fill:url(#capture-gfun);stroke:rgba(255,255,255,.7);stroke-width:.8"/>`;
    svg += `<g transform="${SIDE(124, 78, 59)}"><circle cx="25" cy="25" r="25" style="fill:rgba(0,22,63,.45);stroke:var(--red);stroke-width:4.5"/><circle class="detail" cx="25" cy="25" r="16"/><circle class="detail" cx="25" cy="25" r="8"/>
      <g id="capture-swirl" class="sweep" style="opacity:0" filter="url(#soft)"><path d="M7 25H16M25 7V16M43 25H34M25 43V34"/></g></g>`;
    // conveyor
    svg += box(34, 88, 6, 24, 48, 6, 1);
    svg += `<g transform="${TOP(34, 88, 12)}"><clipPath id="capture-belt"><rect x="1" y="1" width="22" height="46"/></clipPath><g clip-path="url(#capture-belt)"><g id="capture-stripes">${slits(0, 66, 6, 1, 23, false)}</g></g></g>`;
    svg += box(32, 88, 12, 2, 48, 3, 0) + box(58, 88, 12, 2, 48, 3, 0);
    svg += `<g id="capture-pcs">${parcel(K, 40, 90, 12, 12, 10, 8)}</g><g id="capture-pcs2">${parcel(K, 39, 90, 12, 10, 9, 11)}</g>`;
    // console + button + worker
    svg += box(146, 114, 6, 10, 10, 22, 1) + `<g transform="${FRONT(146, 124, 28)}"><rect class="face glass hot" x="1.5" y="3" width="7" height="8" rx="1"/></g>`;
    svg += `<g class="press go" id="capture-btn">${box(148, 116, 28, 6, 6, 3, 2.5)}</g>`;
    svg += `<g class="go" id="capture-worker">${person(K, 132, 124, 6, { hat: 'hard', vest: true, tone: 'y', hold: [151, 119, 31.5] })}</g>`;
    svg += '<g id="capture-fl"></g>';
    stage.setAttribute('viewBox', K.viewBox); stage.innerHTML = svg;

    const q = s => stage.querySelector(s), N = 7;
    const home = [[165, 50, 40], [190, 74, 52], [172, 98, 36], [216, 46, 56], [208, 104, 46], [232, 76, 40], [186, 30, 60]], mouth = [124, 53, 34];
    const root = q('#capture-fl'); root.innerHTML = home.map((_, i) => icon(KINDS[i % KINDS.length])).join('');
    const els = [...root.children], done = new Array(N).fill(false), st = { n: 0 };
    let T = 0, t0 = -1e9;
    const leds = [0, 1, 2].map(i => q('#capture-l' + i)), stripes = q('#capture-stripes'), pc = [q('#capture-pcs'), q('#capture-pcs2')];
    function render() {
      const run = T - t0 < 4600, live = st.n > 0 || run;
      q('#capture-screen').classList.toggle('hot', live); q('#capture-halo').classList.toggle('hot', live);
      leds.forEach(l => l.classList.toggle('hot', live)); api.power(live);
      q('#capture-n').textContent = String(st.n).padStart(2, '0') + '/0' + N; q('#capture-bar').setAttribute('width', (44 * st.n / N).toFixed(1));
      q('#capture-swirl').style.opacity = run && T - t0 < 3000 ? 1 : 0;
      api.readout(`ingested ${st.n}/${N}` + (run ? ' · belt running' : ''));
    }
    function suck() { if (T - t0 < 3600) return; t0 = T; st.n = 0; done.fill(false); render(); }
    api.loop(t => {
      T = t; const a = T - t0;
      els.forEach((el, k) => {
        const h = home[k], u = (a - k * 170) / 1100, bob = Math.sin(T / 520 + k * 1.7) * 2.5; let p = [h[0], h[1], h[2] + bob], s = 1.15, op = 1;
        if (a >= 0 && u >= 0 && u < 1) { const e = u * u * (3 - 2 * u), sw = (1 - e) * Math.sin(e * 9) * 7; p = [lerp(h[0], mouth[0], e), lerp(h[1], mouth[1], e) + sw, lerp(h[2], mouth[2], e) + sw * .5]; s = 1.15 * (1 - .7 * e); op = u > .85 ? (1 - u) / .15 : 1; }
        else if (a >= 0 && u >= 1 && a < 3200) { op = 0; if (!done[k]) { done[k] = true; st.n++; render(); } }
        else if (a >= 3200 && a < 3700) { op = (a - 3200) / 500; }
        bill(K, el, p[0], p[1], p[2], s, op);
      });
      const run = a >= 0 && a < 4600; stripes.setAttribute('transform', `translate(0 ${run ? ((T / 55) % 6).toFixed(2) : 0})`);
      pc.forEach((g, i) => { const dy = ((T / 90 + i * 19) % 38); g.style.opacity = run || (a >= 0 && a < 6000) ? 1 : 0; setTr(K, g, 0, dy, 0); });
      if (a >= 4600 && a < 4700) render();
    });
    ['#capture-btn', '#capture-worker'].forEach(s => q(s).addEventListener('click', () => { api.flash(q('#capture-btn')); suck(); }));
    render();
    return { key: e => (e.key === ' ' || e.key === 'Enter') ? (api.flash(q('#capture-btn')), suck(), true) : false, demo: () => api.after(200, suck) };
  },
});
