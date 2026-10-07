// Loads the built page in jsdom, mounts every figure, runs its demo, reports errors, and exports a static SVG per shot.
const { JSDOM, VirtualConsole } = require('jsdom'); const fs = require('fs'), path = require('path');
const root = path.resolve(__dirname, '..'); const only = process.argv[2];
const errs = []; const vc = new VirtualConsole(); vc.on('jsdomError', e => errs.push(String(e.detail || e.message || e))); vc.on('error', e => errs.push(String(e)));
const dom = new JSDOM(fs.readFileSync(root + '/data-mesh-storyboard.html', 'utf8'), { runScripts: 'dangerously', pretendToBeVisual: true, url: 'http://localhost/', virtualConsole: vc });
const w = dom.window, d = w.document;
w.addEventListener('error', e => errs.push('window: ' + e.message + ' @' + (e.filename || '') + ':' + e.lineno));
const sleep = ms => new Promise(r => setTimeout(r, ms));
const vocab = d.querySelector('#vocab').textContent, fx = d.querySelector('#fx').innerHTML;
const tokens = '--panel:#0c0f14;--body:#171c24;--deck:#212836;--line:#a3aebf;--detail:#4d586a;--recess:#0a0d12;--ink:#c8d0dc;--ink-hi:#fff;--glass:#0f141b;--accent:#ffb02e;--accent-hi:#ffe2a6;--glass-on:color-mix(in srgb,#ffb02e 26%,#0a0d12);--accent-dim:color-mix(in srgb,#ffb02e 38%,#0c0f14)';
(async () => {
  const btns = [...d.querySelectorAll('#nav button')]; fs.mkdirSync(root + '/svg', { recursive: true });
  for (let i = 0; i < btns.length; i++) {
    if (only && String(i + 1) !== only) continue;
    const before = errs.length; btns[i].click(); await sleep(+process.env.SETTLE || (w.eval('FIGS')[i].settle || 3000));
    const s = d.querySelector('#stage'), id = s.dataset.fig, fig = s.outerHTML;
    const bad = (fig.match(/NaN|undefined|Infinity/g) || []).length;
    const css = (d.querySelector('#figcss').textContent.split('\n').filter(l => l.includes('data-fig="' + id + '"')).join('\n'));
    const vb = s.getAttribute('viewBox').split(' ').map(Number);
    let out = fig.replace('<svg ', '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="900" ').replace(/ tabindex="0"/, '');
    out = out.replace(/(<svg[^>]*>)/, `$1<style>svg.stage{${tokens}}\n${vocab}\n${css}</style><defs>${fx}</defs><rect x="${vb[0]}" y="${vb[1]}" width="${vb[2]}" height="${vb[3]}" style="fill:var(--panel);vector-effect:none"/>`);
    fs.writeFileSync(`${root}/svg/shot-${i + 1}-${id}.svg`, out);
    console.log(`fig ${i + 1} ${id}: ${fig.length} chars, bad tokens ${bad}, new errors ${errs.length - before}, readout "${d.querySelector('#readout').textContent}"`);
  }
  errs.forEach(e => console.log('ERR', e)); w.close(); process.exit(errs.length ? 1 : 0);
})();
