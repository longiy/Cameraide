// Loads the built page in jsdom, mounts every figure, runs its demo, reports errors, and exports a static SVG per shot.
const { JSDOM, VirtualConsole } = require('jsdom'); const fs = require('fs'), path = require('path');
const root = path.resolve(__dirname, '..'); const only = process.argv[2];
const errs = []; const vc = new VirtualConsole(); vc.on('jsdomError', e => errs.push(String(e.detail || e.message || e))); vc.on('error', e => errs.push(String(e)));
const dom = new JSDOM(fs.readFileSync(root + '/data-mesh-storyboard.html', 'utf8'), { runScripts: 'dangerously', pretendToBeVisual: true, url: 'http://localhost/', virtualConsole: vc });
const w = dom.window, d = w.document;
w.addEventListener('error', e => errs.push('window: ' + e.message + ' @' + (e.filename || '') + ':' + e.lineno));
const sleep = ms => new Promise(r => setTimeout(r, ms));
const vocab = d.querySelector('#vocab').textContent, fx = d.querySelector('#fx').innerHTML;
const tokens = '--navy:#001E62;--red:#DB0A40;--yellow:#FFC72C;--silver:#C4C9D1;--white:#FFFFFF;--panel:#001E62;--recess:#00163f;--ink:#C4C9D1;--ink-hi:#FFFFFF;--accent:#FFC72C;--accent-hi:#FFFFFF;--glass:#00163f;--glass-on:#FFFFFF;--detail:rgba(196,201,209,.55)';
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
    out = out.replace(/(<svg[^>]*>)/, `$1<style>svg.stage{${tokens}}\n${vocab}\n${css}</style><defs>${fx}</defs><rect x="${vb[0]}" y="${vb[1]}" width="${vb[2]}" height="${vb[3]}" style="fill:url(#g-bg);vector-effect:none"/>`);
    fs.writeFileSync(`${root}/svg/shot-${i + 1}-${id}.svg`, out);
    console.log(`fig ${i + 1} ${id}: ${fig.length} chars, bad tokens ${bad}, new errors ${errs.length - before}, readout "${d.querySelector('#readout').textContent}"`);
  }
  errs.forEach(e => console.log('ERR', e)); w.close(); process.exit(errs.length ? 1 : 0);
})();
