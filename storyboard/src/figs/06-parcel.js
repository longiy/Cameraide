/* Shot 6 — A parcel with no information lands on the office steps. */
FIGS.push({
  id: 'parcel', name: 'The mystery parcel', shot: 'Shot 6', settle: 6200,
  vo: 'But imagine that you receive a parcel without any information about what is inside, where it came from, or who sent it?',
  visual: 'The van arrives and tosses a box to the entrance steps of an office. The person at the door picks it up and is confused.',
  hint: 'Space or click: deliver the parcel · r resets',
  aria: 'Isometric office with entrance steps. A delivery van arrives and tosses an unlabelled parcel onto the steps; the person at the door picks it up and looks confused. Press space or click the van to play. Press r to reset.',
  css: `[data-fig="parcel"] .go{cursor:pointer}`,
  mount(stage, api) {
    const K = api.iso.frame([[0, 0, 0], [260, 0, 0], [0, 200, 0], [260, 200, 0], [30, 16, 108]], .03), { TOP, FRONT, SIDE, box, rect } = K, rnd = seeded(23);
    const VX = 36, YC = 166, SC = 1.5, PX = 115, PY = 80, PZ = 15;
    let svg = plate(K, 0, 0, 260, 200, 6, { r: 10 }) + road(K, 0, 150, 260, 32, 6, 'x');
    svg += `<g transform="${FRONT(0, 200, 6)}"><text class="label" x="14" y="4.6" font-size="3.8">OFFICE · RECEIVING</text></g>`;
    svg += box(30, 16, 6, 170, 60, 100, 2) + `<g transform="${TOP(30, 16, 106)}"><rect class="detail" x="3" y="3" width="164" height="54"/></g>`;
    svg += wins(FRONT(36, 76, 102), 158, 40, 14, 4, rnd, false) + wins(FRONT(36, 76, 50), 52, 32, 4, 3, rnd, false) + wins(FRONT(142, 76, 50), 52, 32, 4, 3, rnd, false) + wins(SIDE(200, 70, 102), 58, 84, 6, 8, rnd, false);
    svg += `<g transform="${FRONT(30, 76, 106)}"><rect class="halo" id="parcel-halo" x="70" y="53" width="32" height="38" filter="url(#bloom)"/><rect class="face glass" id="parcel-door" x="70" y="53" width="32" height="38" rx="1.5" filter="url(#soft)"/><line class="detail" x1="86" y1="53" x2="86" y2="91"/></g>`;
    svg += box(92, 76, 55, 46, 10, 2, 0);
    svg += box(96, 76, 6, 38, 8, 9, .5) + box(96, 84, 6, 38, 8, 6, .5) + box(96, 92, 6, 38, 8, 3, .5);
    [[48, 96], [196, 100], [212, 130], [20, 100]].forEach(([x, y]) => { svg += tree(K, x, y, 6, 6); });
    const idle = person(K, PX, PY, PZ, { tone: 'w' }), hold = person(K, PX, PY, PZ, { tone: 'w', hold: [PX, PY + 7, PZ + 12] });
    svg += `<g id="parcel-person">${big(K, PX, PY, PZ, SC, `<g id="parcel-idle">${idle}</g><g id="parcel-hold" style="display:none">${hold}</g>`)}</g>`;
    const v = van(K, VX, YC, 6, { lamp: 'parcel-lamp', open: true });
    svg += `<g class="go" id="parcel-van"><g id="parcel-vb">${v.back}</g><g id="parcel-vf">${v.front}</g></g>`;
    const HX = 108, HY = 94, HZ = 9, PW = 10, PD = 8, PH = 7;
    svg += `<g id="parcel-box" style="opacity:0">${parcel(K, HX, HY, HZ, PW, PD, PH)}<g transform="${FRONT(HX, HY + PD, HZ + PH)}"><rect class="detail dash" x="2" y="1.3" width="6" height="4"/></g></g>`;
    svg += `<g id="parcel-q" style="opacity:0"><rect class="tag hot" x="-9" y="-10" width="18" height="15" rx="4.5"/><path class="tag hot" d="M-2 5L0 9L2 5Z"/><text class="scr" x="0" y="2.4" font-size="11" text-anchor="middle">?</text></g>`;
    stage.setAttribute('viewBox', K.viewBox); stage.innerHTML = svg;

    const q = s => stage.querySelector(s), box_ = q('#parcel-box'), vb = q('#parcel-vb'), vf = q('#parcel-vf'), pp = q('#parcel-person'), foot = K.P(PX, PY, PZ);
    const st = { t0: -1e9 }; let T = 0, phase = '', door = false;
    const START = [66, 160, 22], LAND = [HX, HY, HZ], HOLD = [PX - PW / 2, PY + 7 * SC - PD / 2 + 3, PZ + 12 * SC - PH / 2];
    const setPhase = (p, text) => { if (p === phase) return; phase = p; api.readout(text); const hold_ = p === 'hold' || p === 'confused', lit = p !== 'idle' && p !== 'arrive' && p !== 'toss';
      q('#parcel-idle').style.display = hold_ ? 'none' : ''; q('#parcel-hold').style.display = hold_ ? '' : 'none';
      q('#parcel-door').classList.toggle('hot', lit); q('#parcel-halo').classList.toggle('hot', lit); api.power(lit);
      stage.querySelectorAll('.parcel-lamp').forEach(l => l.classList.toggle('hot', p === 'arrive')); };
    api.loop(t => {
      T = t; const a = T - st.t0, active = a >= 0;
      if (!active) { vb.style.opacity = vf.style.opacity = 0; box_.style.opacity = 0; q('#parcel-q').style.opacity = 0; pp.removeAttribute('transform'); setPhase('idle', 'idle · press space to deliver'); return; }
      const arr = clamp(a / 1500), dx = -90 * (1 - easeOut(arr)); setTr(K, vb, dx, 0, 0); setTr(K, vf, dx, 0, 0); vb.style.opacity = vf.style.opacity = clamp(arr * 3);
      let p = START, op = 1, qop = 0;
      if (a < 1800) { setPhase('arrive', 'van arriving'); p = START; }
      else if (a < 2700) { setPhase('toss', 'toss!'); const u = (a - 1800) / 900; p = [lerp(START[0], LAND[0], u), lerp(START[1], LAND[1], u), lerp(START[2], LAND[2], u) + 42 * 4 * u * (1 - u)]; }
      else if (a < 3300) { setPhase('landed', 'landed on the steps'); p = LAND; }
      else if (a < 4100) { setPhase('hold', 'picking it up'); const u = ease((a - 3300) / 800); p = [lerp(LAND[0], HOLD[0], u), lerp(LAND[1], HOLD[1], u), lerp(LAND[2], HOLD[2], u)]; }
      else { setPhase('confused', 'no label · who sent this? what is inside?'); p = HOLD; qop = clamp((a - 4100) / 300); const w = Math.sin(a / 170) * 2.2 * qop; pp.setAttribute('transform', `rotate(${w.toFixed(2)} ${foot[0].toFixed(1)} ${foot[1].toFixed(1)})`); }
      box_.style.opacity = a < 1500 ? 0 : 1; setTr(K, box_, p[0] - HX, p[1] - HY, p[2] - HZ);
      if (a < 1800) { setTr(K, box_, START[0] - HX, START[1] - HY, START[2] - HZ); box_.style.opacity = arr >= 1 ? 1 : 0; }
      const qq = q('#parcel-q'); bill(K, qq, PX, PY, PZ + 36 * SC + 8, 1.1 + .08 * Math.sin(a / 180), qop);
    });
    const start = () => { if (T - st.t0 > 8000 || st.t0 < -1e8) st.t0 = T; }, reset = () => { st.t0 = -1e9; };
    stage.addEventListener('click', e => { if (e.target.closest('#parcel-van')) start(); });
    setPhase('idle', 'idle · press space to deliver');
    return { key: e => { if (e.key === ' ' || e.key === 'Enter') { start(); return true; } if (e.key === 'r' || e.key === 'R') { reset(); return true; } return false; }, demo: () => api.after(200, start) };
  },
});
