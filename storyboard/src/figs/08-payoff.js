/* Shot 8 — The parcel is thrown in, received gladly, opened; data lights up the desk and the laptop pays out like a slot machine. */
FIGS.push({
  id: 'payoff', name: 'Received gladly', shot: 'Shot 8', settle: 6600,
  vo: 'So remember: data products are like parcels of data, and data contracts are like sender labels.',
  visual: 'The van arrives at the office and throws the parcel to the receiver. Received gladly. Taken inside, opened. Data lights up the desk and laptop, making money like a slot machine.',
  hint: 'Space or click the desk: deliver · r resets',
  aria: 'Isometric office room cutaway. A labelled parcel is thrown through the door onto a desk, opened, and data icons burst out. The laptop screen lights up and three reels spin and land on dollar signs. Press space or click the desk to play, r to reset.',
  css: `[data-fig="payoff"] .go{cursor:pointer}`,
  mount(stage, api) {
    const K = api.iso.frame([[0, 0, 0], [200, 0, 0], [0, 170, 0], [200, 170, 0], [0, 0, 92]], .035), { TOP, FRONT, SIDE, box, rect, poly } = K, slits = api.iso.slits;
    const PX = 150, PY = 78, SC = 1.4, HX = 100, HY = 58, HZ = 27, BW = 14, BD = 12, BH = 10;
    let svg = plate(K, 0, 0, 200, 170, 6, { r: 8 }) + box(0, 0, 6, 200, 6, 84, 0) + box(0, 6, 6, 6, 164, 84, 0);
    svg += `<g transform="${FRONT(0, 6, 90)}"><rect class="face recess" x="140" y="34" width="30" height="50"/><line class="detail" x1="140" y1="34" x2="170" y2="34"/>
      ${[[22, 62], [76, 116]].map(([a, b]) => `<rect class="face recess" x="${a}" y="14" width="${b - a}" height="38" rx="1.5"/><line class="detail" x1="${(a + b) / 2}" y1="14" x2="${(a + b) / 2}" y2="52"/><line class="detail" x1="${a}" y1="33" x2="${b}" y2="33"/>`).join('')}</g>`;
    svg += `<g transform="${SIDE(6, 150, 86)}"><rect class="face recess" x="6" y="12" width="52" height="34" rx="1.5"/>${slits(24, 40, 10, 12, 46, false)}<rect class="detail" x="70" y="18" width="30" height="40"/><line class="detail" x1="74" y1="26" x2="96" y2="26"/><line class="detail" x1="74" y1="32" x2="90" y2="32"/></g>`;
    // desk
    [[36, 54], [36, 80], [118, 54], [118, 80]].forEach(([x, y]) => { svg += box(x, y, 6, 4, 4, 18, 0); });
    svg += box(34, 52, 24, 90, 34, 3, 1) + `<g transform="${TOP(34, 52, 27)}"><rect class="halo" id="pay-halo" width="90" height="34" rx="6" filter="url(#bloom)"/></g>`;
    // laptop: lid at back, base in front
    svg += box(52, 62, 29, 34, 2, 22, 1);
    svg += `<g transform="${FRONT(52, 64, 51)}"><rect class="halo" id="pay-lhalo" x="1" y="1" width="32" height="18" rx="1.5" filter="url(#bloom)"/><rect class="face glass" id="pay-screen" x="1" y="1" width="32" height="18" rx="1.5" filter="url(#soft)"/>
      <g id="pay-scr" style="opacity:0" filter="url(#soft)">${[3.4, 12.7, 22].map((x, i) => `<rect class="face recess" x="${x}" y="3" width="8.6" height="9.4" rx="1"/><text class="scr" id="pay-r${i}" x="${x + 4.3}" y="10.6" font-size="8" text-anchor="middle">$</text>`).join('')}<text class="scr" id="pay-amt" x="17" y="17.2" font-size="3.2" text-anchor="middle">PAYOUT 0000</text></g></g>`;
    svg += box(52, 64, 27, 34, 20, 2, 1) + `<g transform="${TOP(52, 64, 29)}"><rect class="detail" x="6" y="4" width="22" height="9" rx="1"/></g>`;
    const bx = HX, by = HY, zt = HZ + BH, fl = (pts) => poly(pts, 'face top');
    svg += `<g id="pay-box" style="opacity:0">${parcel(K, bx, by, HZ, BW, BD, BH)}<g id="pay-open" style="display:none"><g transform="${TOP(bx + 1, by + 1, zt)}"><rect class="face recess" width="${BW - 2}" height="${BD - 2}"/><rect class="halo hot" width="${BW - 2}" height="${BD - 2}" filter="url(#bloom)"/></g>
      ${fl([[bx, by, zt], [bx + BW, by, zt], [bx + BW, by - 5, zt + 4], [bx, by - 5, zt + 4]])}${fl([[bx, by, zt], [bx, by + BD, zt], [bx - 5, by + BD, zt + 4], [bx - 5, by, zt + 4]])}${fl([[bx + BW, by, zt], [bx + BW, by + BD, zt], [bx + BW + 5, by + BD, zt + 4], [bx + BW + 5, by, zt + 4]])}${fl([[bx, by + BD, zt], [bx + BW, by + BD, zt], [bx + BW, by + BD + 5, zt + 4], [bx, by + BD + 5, zt + 4]])}</g></g>`;
    svg += `<g class="go" id="pay-person">${big(K, PX, PY, 6, SC, `<g id="pay-down">${person(K, PX, PY, 6, {})}</g><g id="pay-up" style="display:none">${person(K, PX, PY, 6, { up: true })}</g>`)}</g>`;
    svg += '<g id="pay-fl0"></g><g id="pay-fl1"></g>';
    stage.setAttribute('viewBox', K.viewBox); stage.innerHTML = svg;

    const q = s => stage.querySelector(s), boxEl = q('#pay-box'), em0 = emitter(api, K, q('#pay-fl0'), [[bx + 7, by + 6, zt + 4]], { n: 6, rise: 52, s: 1, period: 3000, drift: 14, on: false, kinds: ['heart', 'play', 'bars', 'chat', 'pin', 'ticket'] }),
      em1 = emitter(api, K, q('#pay-fl1'), [[69, 74, 52]], { n: 5, rise: 40, s: .95, period: 2200, drift: 12, on: false, kinds: ['coin'] });
    const reels = [0, 1, 2].map(i => q('#pay-r' + i)), SYM = ['$', '7', '%', '#', '$', '@'], START = [148, 10, 44], st = { t0: -1e9 }; let T = 0, lastSig = '';
    api.loop(t => {
      T = t; const a = T - st.t0, active = a >= 0;
      const toss = clamp((a - 300) / 800), open = active && a > 1600, lit = active && a > 2200, stop = [3700, 4100, 4500], done = active && a > 4500, up = active && (a < 1300 || done);
      let p = START, op = active && a > 300 ? 1 : 0;
      if (active && a <= 1100) p = [lerp(START[0], HX, toss), lerp(START[1], HY, toss), lerp(START[2], HZ, toss) + 26 * 4 * toss * (1 - toss)]; else p = [HX, HY, HZ];
      if (!active) p = [HX, HY, HZ]; boxEl.style.opacity = op; setTr(K, boxEl, p[0] - HX, p[1] - HY, p[2] - HZ);
      reels.forEach((r, i) => { if (lit && a < stop[i]) r.textContent = SYM[Math.floor(T / 70 + i * 2) % SYM.length]; else r.textContent = '$'; });
      const amt = done ? Math.min(7777, Math.floor((a - 4500) / 1200 * 7777)) : 0; q('#pay-amt').textContent = 'PAYOUT ' + String(amt).padStart(4, '0');
      const sig = [active, open, lit, done, up].join(); if (sig !== lastSig) { lastSig = sig;
        q('#pay-open').style.display = open ? '' : 'none'; q('#pay-up').style.display = up ? '' : 'none'; q('#pay-down').style.display = up ? 'none' : '';
        q('#pay-screen').classList.toggle('hot', lit); q('#pay-lhalo').classList.toggle('hot', lit); q('#pay-halo').classList.toggle('hot', lit); q('#pay-scr').style.opacity = lit ? 1 : 0;
        em0.set(open); em1.set(done); api.power(lit);
        api.readout(!active ? 'idle · press space' : done ? 'jackpot · data pays out' : lit ? 'data lights up the desk' : open ? 'opened' : 'received!'); }
    });
    const start = () => { if (T - st.t0 > 7000 || st.t0 < -1e8) st.t0 = T; }, reset = () => { st.t0 = -1e9; };
    stage.addEventListener('click', e => { if (e.target.closest('.go') || e.target.closest('#pay-box')) start(); });
    api.readout('idle · press space');
    return { key: e => { if (e.key === ' ' || e.key === 'Enter') { start(); return true; } if (e.key === 'r' || e.key === 'R') { reset(); return true; } return false; }, demo: () => api.after(200, start) };
  },
});
