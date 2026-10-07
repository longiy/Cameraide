/* ---- shared helpers for the Data Mesh storyboard figures ---- */
const KINDS = ['heart', 'play', 'bars', 'chat', 'pin', 'ticket', 'cam'];
const ICONS = {
  heart: '<path class="ico f" d="M0 4 C-6 -1 -4.5 -5 0 -2 C4.5 -5 6 -1 0 4Z"/>',
  play: '<path class="ico f" d="M-2.2 -3.4L3.2 0L-2.2 3.4Z"/>',
  bars: '<path class="ico" d="M-3.5 3.5V0M0 3.5V-3M3.5 3.5V-1.5"/>',
  chat: '<path class="ico" d="M-4 -3.5H4V1.5H-0.5L-3 4V1.5H-4Z"/>',
  pin: '<path class="ico" d="M0 4.5L-3 -0.5A3.4 3.4 0 1 1 3 -0.5Z"/><circle class="ico" cx="0" cy="-1.6" r="1"/>',
  ticket: '<path class="ico" d="M-4.5 -2.5H4.5V3H-4.5Z M1 -2.5V3"/>',
  cam: '<rect class="ico" x="-4.5" y="-2.5" width="9" height="6" rx="1"/><circle class="ico" cx="0" cy="0.5" r="1.6"/>',
  coin: '<circle class="ico f" r="3.4"/><path class="ico" d="M0 -1.6V1.6" style="stroke:var(--recess)"/>',
};
const icon = (kind, cls = 'hot') => `<g class="ic ${cls}"><rect class="face" x="-7" y="-7" width="14" height="14" rx="3.5"/>${ICONS[kind]}</g>`;
const seeded = s => () => (s = (s * 16807) % 2147483647) / 2147483647;
const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
const lerp = (a, b, t) => a + (b - a) * t;
const ease = t => t < .5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;
const easeOut = t => 1 - Math.pow(1 - t, 3);
const f1 = v => (+v).toFixed(2);
const tr = (K, dx, dy, dz = 0) => { const p = K.D(dx, dy, dz); return `translate(${f1(p[0])} ${f1(p[1])})`; };
const setTr = (K, el, dx, dy, dz = 0) => el.setAttribute('transform', tr(K, dx, dy, dz));
const bill = (K, el, x, y, z, s = 1, op = 1) => { const p = K.P(x, y, z); el.setAttribute('transform', `translate(${f1(p[0])} ${f1(p[1])}) scale(${f1(s)})`); el.style.opacity = op; };

/* rounded ground plate with inset line + screws */
function plate(K, x, y, w, d, h = 6, o = {}) {
  let s = K.box(x, y, 0, w, d, h, o.r === undefined ? 10 : o.r);
  s += `<g transform="${K.TOP(x, y, h)}"><rect class="detail" x="6" y="6" width="${w - 12}" height="${d - 12}" rx="5"/>`;
  if (!o.noscrew) [[11, 11], [w - 11, 11], [11, d - 11], [w - 11, d - 11]].forEach(([a, b]) => { s += `<circle class="face recess" cx="${a}" cy="${b}" r="2.2"/><line class="detail" x1="${a - 1.4}" y1="${b}" x2="${a + 1.4}" y2="${b}"/>`; });
  return s + '</g>';
}
/* flat road strip on a plate top. axis 'x': runs along x */
function road(K, x, y, w, d, z, axis = 'x') {
  let s = `<g transform="${K.TOP(x, y, z)}"><rect class="face recess" width="${w}" height="${d}"/>`;
  s += axis === 'x' ? `<line class="detail dash" x1="4" y1="${d / 2}" x2="${w - 4}" y2="${d / 2}"/>` : `<line class="detail dash" x1="${w / 2}" y1="4" x2="${w / 2}" y2="${d - 4}"/>`;
  return s + '</g>';
}
/* window panes on a plane */
function wins(t, w, h, cols, rows, rnd, lit = false) {
  const pw = w / cols, ph = h / rows; let s = `<g class="wins${lit ? ' lit' : ''}" transform="${t}">`;
  for (let r = 0; r < rows; r++) for (let c = 0; c < cols; c++) { const v = rnd(); s += `<rect class="pn${v < .12 ? ' x' : v < .3 ? ' d' : v < .42 ? ' h' : ''}" x="${f1(c * pw + .7)}" y="${f1(r * ph + .8)}" width="${f1(pw - 1.4)}" height="${f1(ph - 1.6)}"/>`; }
  return s + '</g>';
}
/* a building: box with window grids on FRONT and SIDE */
function bldg(K, x, y, w, d, h, rnd, o = {}) {
  const z = o.z === undefined ? 6 : o.z, pad = 3, cw = o.cw || 7, rh = o.rh || 8;
  let s = K.box(x, y, z, w, d, h, o.r === undefined ? 1.5 : o.r);
  s += `<g transform="${K.TOP(x, y, z + h)}"><rect class="detail" x="2.5" y="2.5" width="${w - 5}" height="${d - 5}"/></g>`;
  const cF = Math.max(2, Math.round((w - 2 * pad) / cw)), cS = Math.max(2, Math.round((d - 2 * pad) / cw)), rows = Math.max(2, Math.floor((h - 8) / rh));
  s += wins(K.FRONT(x + pad, y + d, z + h - 5), w - 2 * pad, rows * rh - 2, cF, rows, rnd, o.lit);
  s += wins(K.SIDE(x + w, y + d - pad, z + h - 5), d - 2 * pad, rows * rh - 2, cS, rows, rnd, o.lit);
  return s;
}
function tree(K, x, y, z = 6, r = 7) {
  const a = K.P(x, y, z + 1), b = K.P(x, y, z + 9), c = K.P(x, y, z + 9 + r * .8);
  return `<path class="mast" d="M${a.map(f1).join(' ')}L${b.map(f1).join(' ')}"/><circle class="face" cx="${f1(c[0])}" cy="${f1(c[1])}" r="${r}"/><circle class="detail" cx="${f1(c[0] - r * .2)}" cy="${f1(c[1] - r * .2)}" r="${f1(r * .5)}"/>`;
}
/* little person, feet at (x,y,z). o: hat 'cap'|'hard', vest, hold [x,y,z], up, cls */
function person(K, x, y, z, o = {}) {
  const { box, P, FRONT } = K; let s = `<g class="person ${o.cls || ''}">`;
  s += box(x - 3.2, y - 1.8, z, 6.4, 3.6, 9, .8);
  s += `<g transform="${FRONT(x - 3.2, y + 1.8, z + 9)}"><line class="detail" x1="3.2" y1="1" x2="3.2" y2="9"/></g>`;
  s += box(x - 3.8, y - 2.2, z + 9, 7.6, 4.4, 9.5, 1.2);
  if (o.vest) s += `<g transform="${FRONT(x - 3.8, y + 2.2, z + 18.5)}"><line class="detail" x1="2" y1="0" x2="2" y2="9.5"/><line class="detail" x1="5.6" y1="0" x2="5.6" y2="9.5"/><line class="detail" x1="0" y1="6" x2="7.6" y2="6"/></g>`;
  const L = P(x - 4.2, y, z + 17.6), R = P(x + 4.2, y, z + 17.6);
  const hl = o.hold ? P(o.hold[0] - 1.6, o.hold[1], o.hold[2]) : o.up ? P(x - 5.5, y, z + 25.5) : P(x - 4.6, y, z + 9.5);
  const hr = o.hold ? P(o.hold[0] + 1.6, o.hold[1], o.hold[2]) : o.up ? P(x + 5.5, y, z + 25.5) : P(x + 4.6, y, z + 9.5);
  s += `<path class="limb" d="M${L.map(f1).join(' ')}L${hl.map(f1).join(' ')}M${R.map(f1).join(' ')}L${hr.map(f1).join(' ')}"/>`;
  const h = P(x, y, z + 22.8);
  s += `<circle class="face" cx="${f1(h[0])}" cy="${f1(h[1])}" r="3.6"/>`;
  if (o.hat) s += `<path class="face" d="M${f1(h[0] - 3.9)} ${f1(h[1] - .4)}A3.9 3.9 0 0 1 ${f1(h[0] + 3.9)} ${f1(h[1] - .4)}Z"/>` + (o.hat === 'hard' ? `<line class="detail" x1="${f1(h[0] - 5)}" y1="${f1(h[1] - .4)}" x2="${f1(h[0] + 5)}" y2="${f1(h[1] - .4)}"/>` : '');
  return s + '</g>';
}
/* a seated/standing spectator: head + shoulders */
function spectator(K, x, y, z, up) {
  const h = K.P(x, y, z + 11), sh = K.P(x, y, z + 7);
  return K.box(x - 2.2, y - 1.6, z, 4.4, 3.2, 8, 1.1) + `<circle class="face" cx="${f1(h[0])}" cy="${f1(h[1])}" r="2.5"/>` + (up ? `<path class="limb" style="stroke-width:1.5" d="M${K.P(x + 2.2, y, z + 7).map(f1).join(' ')}L${K.P(x + 3.4, y, z + 14).map(f1).join(' ')}"/>` : '');
}
/* parcel box with tape; z = base */
function parcel(K, x, y, z, w, d, h, cls = '') {
  return `<g class="parcel ${cls}">` + K.box(x, y, z, w, d, h, 0.6) +
    `<g transform="${K.TOP(x, y, z + h)}"><line class="detail" x1="${f1(w / 2)}" y1="0" x2="${f1(w / 2)}" y2="${d}"/></g>` +
    `<g transform="${K.FRONT(x, y + d, z + h)}"><line class="detail" x1="${f1(w / 2)}" y1="0" x2="${f1(w / 2)}" y2="${f1(h * .45)}"/></g></g>`;
}
/* delivery van parked with its rear at x0, cab toward +x, centre line yc, ground zb. Returns {back, front}; boxes live between. */
function van(K, x0, yc, zb = 6, o = {}) {
  const { box, FRONT, SIDE, rect } = K, W = 28, y0 = yc - W / 2;
  const back = box(x0, y0, zb + 4, 75, W, 6, 1.5) + box(x0, y0, zb + 10, 50, 2, 9, 0) + (o.open ? '' : box(x0, y0, zb + 10, 2, W, 9, 0));
  let front = box(x0, y0 + W - 2, zb + 10, 50, 2, 9, 0) + box(x0 + 50, y0, zb + 10, 25, W, 18, 3);
  front += rect(FRONT(x0 + 54, y0 + W, zb + 26.5), 17, 7, 1.5, 'face glass') + rect(SIDE(x0 + 75, y0 + W - 3, zb + 26.5), 16, 7, 1.5, 'face glass');
  front += `<g transform="${SIDE(x0 + 75, y0 + W - 3, zb + 15)}"><rect class="led ${o.lamp || ''}" filter="url(#soft)" x="0" y="0" width="4" height="2.4" rx="1"/><rect class="led ${o.lamp || ''}" filter="url(#soft)" x="18" y="0" width="4" height="2.4" rx="1"/></g>`;
  [12, 62].forEach(wx => { front += `<g transform="${FRONT(x0 + wx - 5, y0 + W, zb + 9)}"><circle class="face" cx="5" cy="3.5" r="5"/><circle class="detail" cx="5" cy="3.5" r="2"/></g>`; });
  return { back, front };
}
/* floating data icons rising from source points; returns {set(on), burst()} */
function emitter(api, K, root, src, o = {}) {
  const n = o.n || 6, rise = o.rise || 60, per = o.period || 3600, kinds = o.kinds || KINDS, sc0 = o.s || 1;
  root.innerHTML = Array.from({ length: n }, (_, i) => icon(kinds[i % kinds.length])).join('');
  const els = [...root.children]; els.forEach(e => { e.style.opacity = 0; });
  let on = o.on !== false, gain = on ? 1 : 0, last = 0;
  api.loop(t => {
    const dt = Math.min(64, t - last); last = t; gain += ((on ? 1 : 0) - gain) * Math.min(1, dt / 260);
    els.forEach((el, i) => {
      const s = src[i % src.length], u = (t / per + i / n) % 1, a = Math.pow(Math.sin(Math.PI * u), .55) * gain;
      const sc = sc0 * (.5 + .5 * easeOut(clamp(u * 3)));
      bill(K, el, s[0] + Math.sin(u * 6.3 + i * 2) * 3 + ((i % 3) - 1) * (o.drift || 0) * u, s[1] + Math.cos(u * 5 + i) * 3 + ((i % 2) * 2 - 1) * (o.drift || 0) * u * .7, s[2] + u * rise, sc, a);
    });
  });
  return { set(v) { on = !!v; }, get on() { return on; } };
}

/* scale a group of 3D markup about the screen-space foot point (x,y,z) */
const big = (K, x, y, z, s, inner) => { const p = K.P(x, y, z); return `<g transform="translate(${f1(p[0])} ${f1(p[1])}) scale(${s}) translate(${f1(-p[0])} ${f1(-p[1])})">${inner}</g>`; };
