/* Shot 2 — The event: security, camera and phone each create data. */
FIGS.push({
  id: 'event', name: 'The event', shot: 'Shot 2',
  vo: 'Our data mesh is a way of organizing all this data into something useful. For example, measuring the success of an event like this one. Where fans attend, and content is created, published and watched by audiences all over the world.',
  visual: 'Zoom in further: a security person clicking attendance, a camera person filming, someone on their phone. All creating data, shown with floating icons.',
  hint: 'Click a person (or press 1 · 2 · 3) · space pauses the data',
  aria: 'Isometric live music event. A security guard counts entries, a camera operator films, a fan posts from a phone; each creates floating data icons. Click a person or press 1, 2 or 3 to log an entry, a clip or a post. Space pauses the data.',
  css: `[data-fig="event"] .who{cursor:pointer}[data-fig="event"] .who:hover .face{stroke:var(--ink-hi)}`,
  mount(stage, api) {
    const K = api.iso.frame([[0, 0, 0], [220, 0, 0], [0, 170, 0], [220, 170, 0], [16, 8, 56]], .04);
    const { TOP, FRONT, SIDE, box, rect, P } = K;
    let svg = plate(K, 0, 0, 220, 170, 6, { r: 10 });
    // stage + LED wall + speakers + truss
    svg += box(16, 8, 6, 188, 22, 7, 1) + box(28, 9, 13, 164, 3, 36, 0);
    svg += `<g transform="${FRONT(28, 12, 49)}"><rect class="halo hot" id="event-halo" width="164" height="36" rx="2" filter="url(#bloom)"/><rect class="face glass hot" id="event-screen" width="164" height="36" rx="2" filter="url(#soft)"/>
      <g id="event-eq" filter="url(#soft)">${Array.from({ length: 24 }, (_, b) => `<rect class="scr-accent" x="${5 + b * 6.5}" y="20" width="4.2" height="14"/>`).join('')}</g>
      <text class="scr" x="6" y="9" font-size="6">WORLD TOUR · LIVE</text></g>`;
    [[18, 10], [194, 10]].forEach(([a, b]) => { svg += box(a, b, 6, 9, 10, 28, 1) + `<g transform="${FRONT(a, b + 10, 34)}"><circle class="detail" cx="4.5" cy="7" r="2.6"/><circle class="detail" cx="4.5" cy="18" r="3.6"/></g>`; });
    svg += box(14, 9, 6, 2, 2, 50, 0) + box(204, 9, 6, 2, 2, 50, 0) + box(14, 9, 54, 192, 2, 2, 0);
    // barrier + crowd
    svg += box(14, 104, 6, 192, 2, 6, 0) + `<g transform="${FRONT(14, 106, 12)}">${api.iso.slits(6, 186, 8, 0, 6)}</g>`;
    const r2 = seeded(9);
    [42, 52, 62, 72, 82, 92].forEach(yy => { for (let xx = 22; xx <= 198; xx += 11) svg += spectator(K, xx + (r2() - .5) * 3, yy, 6, r2() < .22); });
    // the three data makers
    const SC = 1.7, W = [{ x: 46, y: 130 }, { x: 108, y: 134 }, { x: 170, y: 128 }];
    svg += `<g class="who press" data-w="0">${big(K, W[0].x, W[0].y, 6, SC, person(K, W[0].x, W[0].y, 6, { hat: 'cap', vest: true, hold: [W[0].x + 2, W[0].y + 4, 19] }) + box(W[0].x - 1.5, W[0].y + 4, 17, 3, 2, 3.4, .5) + `<g transform="${FRONT(W[0].x - 1.5, W[0].y + 6, 20.4)}"><rect class="led" id="event-clk" filter="url(#soft)" x="1" y="1" width="1.2" height="1.4"/></g>`)}</g>`;
    svg += `<g class="who press" data-w="1">${big(K, W[1].x, W[1].y, 6, SC, person(K, W[1].x, W[1].y, 6, { hat: 'cap', hold: [W[1].x + 2, W[1].y + 1, 24] }) + box(W[1].x - 5, W[1].y - 3, 24, 11, 8, 6, 1) + `<g transform="${FRONT(W[1].x - 5, W[1].y + 5, 30)}"><rect class="face glass hot" id="event-vf" x="1.5" y="1" width="5" height="3.4" rx=".6"/><rect class="led hot blink" id="event-rec" filter="url(#soft)" x="8" y="1.4" width="1.6" height="1.6"/></g>`)}</g>`;
    svg += `<g class="who press" data-w="2">${big(K, W[2].x, W[2].y, 6, SC, person(K, W[2].x, W[2].y, 6, { hold: [W[2].x + 1, W[2].y + 4, 22] }) + box(W[2].x - 2.4, W[2].y + 4, 22, 4.8, 1, 8, .4) + `<g transform="${FRONT(W[2].x - 2.4, W[2].y + 5, 30)}"><rect class="face glass hot" x=".4" y=".6" width="4" height="6.8" rx=".6" filter="url(#soft)"/></g>`)}</g>`;
    const TAGS = [['ENTRIES', 'event-n0'], ['CLIPS', 'event-n1'], ['POSTS', 'event-n2']];
    TAGS.forEach(([lab, id], k) => { svg += `<g class="tagb" id="event-tag${k}"><rect class="tag hot" x="-13" y="-6.5" width="26" height="12" rx="2.6"/><text class="scr" id="${id}" x="0" y="2.2" font-size="6" text-anchor="middle">0000</text><text class="label" x="0" y="-9" font-size="3.8" text-anchor="middle">${lab}</text></g>`; });
    svg += '<g id="event-fl0"></g><g id="event-fl1"></g><g id="event-fl2"></g><g id="event-fl3"></g>';
    stage.setAttribute('viewBox', K.viewBox); stage.innerHTML = svg;

    const q = s => stage.querySelector(s), st = { on: true, n: [128, 24, 56], rec: true };
    const kinds = [['ticket', 'pin', 'ticket'], ['cam', 'play', 'cam'], ['heart', 'chat', 'heart']];
    const ems = W.map((w, k) => emitter(api, K, q('#event-fl' + k), [[w.x, w.y, 6 + 38 * SC]], { n: 3, rise: 52, s: 1.15, period: 3000, kinds: kinds[k], drift: 9 }));
    ems.push(emitter(api, K, q('#event-fl3'), [[70, 60, 22], [120, 70, 22], [160, 55, 22], [96, 84, 22]], { n: 4, rise: 62, s: 1.1, period: 4200, kinds: ['heart', 'chat', 'play', 'bars'], drift: 14 }));
    W.forEach((w, k) => bill(K, q('#event-tag' + k), w.x, w.y, 6 + 34 * SC, 1, 1));
    const eq = [...stage.querySelectorAll('#event-eq rect')];
    function render() {
      TAGS.forEach(([, id], k) => { q('#' + id).textContent = String(st.n[k]).padStart(4, '0'); });
      ems.forEach(e => e.set(st.on)); api.power(st.on);
      q('#event-screen').classList.toggle('hot', st.on); q('#event-halo').classList.toggle('hot', st.on);
      q('#event-rec').classList.toggle('hot', st.rec); q('#event-rec').classList.toggle('blink', st.rec);
      api.readout(`${st.on ? 'live' : 'paused'} · entries ${st.n[0]} · clips ${st.n[1]} · posts ${st.n[2]}`);
    }
    function act(k) {
      st.n[k]++; if (k === 1) st.rec = !st.rec || true;
      const g = q(`.who[data-w="${k}"]`); api.flash(g);
      if (k === 0) { const c = q('#event-clk'); c.classList.add('hot'); api.after(280, () => c.classList.remove('hot')); }
      render();
    }
    api.loop(t => { eq.forEach((b, i) => { const h = st.on ? 3 + 24 * Math.abs(Math.sin(t / 260 + i * .8)) * (.4 + .6 * Math.abs(Math.sin(t / 1100 + i * .3))) : 2; b.setAttribute('height', h.toFixed(1)); b.setAttribute('y', (34 - h).toFixed(1)); }); });
    stage.addEventListener('click', e => { const g = e.target.closest('.who'); if (g) act(+g.dataset.w); });
    render();
    return {
      key: e => { if (e.key === ' ') { st.on = !st.on; render(); return true; } if ('123'.includes(e.key) && e.key) { act(+e.key - 1); return true; } return false; },
      demo: () => { [0, 0, 1, 2, 0, 2].forEach((k, i) => api.after(250 + i * 320, () => act(k))); },
    };
  },
});
