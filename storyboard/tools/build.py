import glob, os
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
s = open(f'{root}/src/shell.html').read()
figs = ''.join(open(f).read() + '\n' for f in sorted(glob.glob(f'{root}/src/figs/*.js')))
assert '</script' not in figs
s = s.replace('/*@FIGS@*/', figs, 1)
open(f'{root}/data-mesh-storyboard.html', 'w').write(s)
print('built', len(s), 'bytes')
