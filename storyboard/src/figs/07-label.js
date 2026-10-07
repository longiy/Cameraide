/* Shot 7 — A shipping label (the data contract) is stuck on the parcel before it ships. */
FIGS.push({
  id: 'label', name: 'The data contract', shot: 'Shot 7', settle: 6400,
  vo: "This is where a 'shipping label' helps. Or in the case of data, a data contract. With information on: descriptions and meaning, owner, quality expectations, structure and origin.",
  visual: 'Back at the capture machine, a worker adds a shipping label to the box before loading it into the van.',
  hint: 'Click the printer or the worker, or press space · r resets',
  aria: 'Isometric label station on a conveyor belt. A worker prints a data contract label with five fields: description, owner, quality, structure and origin. The label flies onto the parcel and sticks. Click the printer or press space to play, r to reset.',
  css: `[data-fig="label"] .go{cursor:pointer}[data-fig="label"] .row text{fill:var(--navy);opacity:.3;font-size:4.4px}[data-fig="label"] .row .v{font-size:3.6px}[data-fig="label"] .row.on text{opacity:1}[data-fig="label"] .row.on .v{fill:var(--red)}[data-fig="label"] .row .led{transition:fill .2s}`,
  mount(stage, api) {
    const K = api.iso.frame([[0, 0, 0], [240, 0, 0], [0, 104, 0], [240, 104, 0], [12, 20, 92]], .03), { TOP, FRONT, SIDE, box } = K, slits = api.iso.slits;
    const FIELDS = [['WHAT IT MEANS', 'description'], ['OWNER', 'named team'], ['QUALITY', 'fresh · complete'], ['STRUCTURE', 'schema v3'], ['ORIGIN', 'event feed']];
    const PXH = 108, PYH = 46, PZH = 12, PW = 22, PD = 14, PH = 14;
    let svg = plate(K, 0, 0, 240, 104, 6, { r: 10 });
    svg += `<g transform="${FRONT(0, 104, 6)}"><text class="label" x="14" y="4.6" font-size="3.8">LABEL STATION · DATA CONTRACTS</text></g>`;
    svg += box(12, 20, 6, 50, 50, 44, 3) + `<g transform="${SIDE(62, 70, 50)}"><rect class="face recess" x="18" y="30" width="18" height="12" rx="2"/></g>`;
    svg += `<g transform="${FRONT(12, 70, 50)}"><rect class="face recess" x="6" y="6" width="38" height="16" rx="2"/><rect class="face glass hot" x="8" y="8" width="34" height="12" rx="1.5" filter="url(#soft)"/><text class="scr" x="11" y="16.5" font-size="5">PARCEL 01</text>${slits(8, 42, 5, 28, 40)}</g>`;
    svg += box(62, 46, 6, 150, 16, 6, 1);
    svg += `<g transform="${TOP(62, 46, 12)}"><clipPath id="label-belt"><rect x="1" y="1" width="148" height="14"/></clipPath><g clip-path="url(#label-belt)"><g id="label-stripes">${slits(0, 156, 6, 1, 15)}</g></g></g>`;
    svg += box(62, 44, 12, 150, 2, 3, 0) + box(62, 62, 12, 150, 2, 3, 0);
    svg += box(120, 42, 12, 4, 4, 34, 0);
    const lab = `<g transform="${FRONT(PXH, PYH + PD, PZH + PH)}" id="label-stick" style="opacity:0"><rect class="tag hot" x="3" y="2" width="16" height="10" rx="1"/><rect class="scr-accent" x="5" y="3.2" width="8" height=".8"/>${FIELDS.map((f, r) => `<circle class="led hot" cx="5.4" cy="${5.6 + r * 1.35}" r=".45"/><rect class="scr-accent" x="6.8" y="${5.3 + r * 1.35}" width="${7 + (r % 3)}" height=".6"/>`).join('')}</g>`;
    svg += `<g id="label-parcel">${parcel(K, PXH, PYH, PZH, PW, PD, PH)}${lab}</g>`;
    svg += box(120, 42, 44, 4, 26, 4, 0) + box(120, 64, 12, 4, 4, 34, 0);
    svg += `<g class="go" id="label-printer">${box(112, 47, 48, 20, 16, 10, 2)}<g transform="${FRONT(112, 63, 58)}"><rect class="face recess" x="3" y="3" width="14" height="4" rx="1"/><rect class="led" id="label-led" filter="url(#soft)" x="15" y="8" width="2" height="1"/></g></g>`;
    svg += `<g class="go" id="label-worker">${big(K, 100, 74, 6, 1.4, person(K, 100, 74, 6, { hat: 'hard', vest: true, tone: 'y', hold: [113, 66, 20.5] }))}</g>`;
    const cw = 78, ch = 52;
    svg += `<g id="label-card" style="opacity:0"><rect class="tag hot" x="${-cw / 2}" y="${-ch / 2}" width="${cw}" height="${ch}" rx="4"/><rect class="halo hot" x="${-cw / 2}" y="${-ch / 2}" width="${cw}" height="${ch}" rx="4" filter="url(#bloom)" style="opacity:.35"/>
      <text class="scr" x="${-cw / 2 + 6}" y="${-ch / 2 + 9}" font-size="6">DATA CONTRACT</text><line class="detail" x1="${-cw / 2 + 5}" y1="${-ch / 2 + 12}" x2="${cw / 2 - 5}" y2="${-ch / 2 + 12}"/>
      ${FIELDS.map((f, r) => `<g class="row" id="label-r${r}"><circle class="led" cx="${-cw / 2 + 8}" cy="${-ch / 2 + 19.5 + r * 7.2}" r="1.8"/><text x="${-cw / 2 + 13}" y="${-ch / 2 + 21 + r * 7.2}">${f[0]}</text><text class="v" x="${cw / 2 - 5}" y="${-ch / 2 + 21 + r * 7.2}" text-anchor="end">${f[1]}</text></g>`).join('')}</g>`;
    stage.setAttribute('viewBox', K.viewBox); stage.innerHTML = svg;

    const q = s => stage.querySelector(s), card = q('#label-card'), par = q('#label-parcel'), stick = q('#label-stick'), stripes = q('#label-stripes'), led = q('#label-led'), rows = FIELDS.map((_, r) => q('#label-r' + r));
    const from = [122, 54, 86], to = K.P(PXH + 11, PYH + PD, PZH + PH - 7);
    const st = { t0: -1e9 }; let T = 0, lastSig = '';
    api.loop(t => {
      T = t; const a = T - st.t0, active = a >= 0 && a < 9000;
      const on = active ? FIELDS.map((_, r) => a > 600 + r * 420) : FIELDS.map(() => false), stuck = active && a > 3400;
      const mv = active && a > 3600 ? ease(clamp((a - 3600) / 1800)) * 56 : 0, run = active && a > 3600 && a < 5400;
      setTr(K, par, mv, 0, 0); stripes.setAttribute('transform', `translate(${run ? ((T / 35) % 6).toFixed(2) : 0} 0)`);
      let op = 0, x = 0, y = 0, sc = 1;
      const f = K.P(from[0], from[1], from[2]);
      if (active && a < 2600) { op = clamp(a / 350); x = f[0]; y = f[1] + (1 - easeOut(clamp(a / 500))) * 8; sc = .6 + .4 * easeOut(clamp(a / 500)); }
      else if (active && a < 3400) { const u = ease((a - 2600) / 800); x = lerp(f[0], to[0], u); y = lerp(f[1], to[1], u); sc = lerp(1, .17, u); op = u > .92 ? (1 - u) / .08 : 1; }
      card.setAttribute('transform', `translate(${x.toFixed(2)} ${y.toFixed(2)}) scale(${sc.toFixed(3)})`); card.style.opacity = op;
      stick.style.opacity = stuck ? 1 : 0;
      const sig = [...on, stuck, active].join(); if (sig !== lastSig) { lastSig = sig; rows.forEach((r, i) => { r.classList.toggle('on', on[i]); r.querySelector('.led').classList.toggle('hot', on[i]); }); led.classList.toggle('hot', active && a < 3400); api.power(active);
        const n = on.filter(Boolean).length; api.readout(!active ? 'idle · print the label' : stuck ? 'label stuck · parcel ships with its contract' : `contract ${n}/5 fields`); }
    });
    const start = () => { st.t0 = T; }, reset = () => { st.t0 = -1e9; };
    ['#label-printer', '#label-worker', '#label-parcel'].forEach(s => q(s).addEventListener('click', () => { if (T - st.t0 > 5800 || st.t0 < -1e8) start(); }));
    api.readout('idle · print the label');
    return { key: e => { if (e.key === ' ' || e.key === 'Enter') { start(); return true; } if (e.key === 'r' || e.key === 'R') { reset(); return true; } return false; }, demo: () => api.after(200, start) };
  },
});
