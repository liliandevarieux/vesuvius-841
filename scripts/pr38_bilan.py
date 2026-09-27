# PR-38 : critere primaire. B et U lus dans logs/pr38.log ; temoin T = recette PR-31 aux memes graines, cartes existantes
# (graine 42 : predictions/pr31_<pli>_ckpt_004000_<seg>.tif ; graine 43 : predictions/pr35_B43_<pli>_<seg>.tif),
# mesurees ici avec les memes scripts (eval_sup, eval_forme, eval_forme_fond). Sens choisi sans etiquette (p99-p50).
import re, subprocess, collections

C = '/home/slusarska_holding/vesuvius'
PY = C + '/villa/vesuvius/.venv/bin/python'
SEGS = ['841_w00', '841_segA', '841_segB', '0009B', '0500P2']


def pli(s):
    return '0841' if s.startswith('841') else s


def mesure(f, s):
    o = ''.join(subprocess.run([PY, C + '/' + e, f, s], capture_output=True, text=True).stdout
                for e in ('eval_sup.py', 'eval_forme.py', 'eval_forme_fond.py'))
    g = lambda r: float(re.search(r, o).group(1))
    return g(r'AUC-sup ([\d.]+)'), g(r'p99-p50 ([\d.]+)'), g(r'ALLONGEMENT carte\s+([\d.na]+)'), g(r'FOND ALLONGEMENT\s+([\d.na]+)')


R = r'(pr38_([BU])(\d+)_\w+?_(841_w00|841_segA|841_segB|0009B|0500P2)(_reverse)?\.tif)\s+\S+\s+'
lu = collections.defaultdict(dict)
for l in open(C + '/logs/pr38.log').read().splitlines():
    for cle, r in (('auc', R + r'AUC-sup ([\d.]+).*p99-p50 ([\d.]+)'), ('forme', R + r'lettres\s+\d+\s+ALLONGEMENT carte\s+([\d.na]+)'),
                   ('fond', R + r'FOND ALLONGEMENT\s+([\d.na]+)')):
        m = re.match(r, l)
        if m:
            k = (m.group(2), m.group(3), m.group(4), bool(m.group(5)))
            if cle == 'auc':
                lu[k]['auc'], lu[k]['sens'] = float(m.group(6)), float(m.group(7))
            else:
                lu[k][cle] = float(m.group(6))
res = collections.defaultdict(dict)
for b in 'BU':
    for g in ('42', '43'):
        for s in SEGS:
            kf, kr = lu.get((b, g, s, False), {}), lu.get((b, g, s, True), {})
            if len(kf) == 4 and len(kr) == 4:
                k = kr if kr['sens'] > kf['sens'] else kf
                res[(b, g)][s] = (k['auc'], k['forme'], k['fond'])
for g, modele in (('42', 'pr31_%s_ckpt_004000_%s'), ('43', 'pr35_B43_%s_%s')):
    for s in SEGS:
        f = '%s/predictions/%s.tif' % (C, modele % (pli(s), s))
        a, b = mesure(f, s), mesure(f.replace('.tif', '_reverse.tif'), s)
        k = b if b[1] > a[1] else a
        res[('T', g)][s] = (k[0], k[2], k[3])
moy = {}
for (b, g) in sorted(res):
    d = res[(b, g)]
    print('%s%s ' % (b, g) + '  '.join('%s A%.3f E%.2f F%.2f' % (s, *d[s]) if s in d else '%s -' % s for s in SEGS))
    if all(s in d for s in SEGS):
        moy[(b, g)] = [sum(d[s][i] for s in SEGS) / 5 for i in range(3)]
        print('     moyennes AUC %.4f  lettres %.2f  fond %.2f' % tuple(moy[(b, g)]))
av = {b: [(moy[(b, '42')][i] + moy[(b, '43')][i]) / 2 for i in range(3)] for b in 'BUT' if (b, '42') in moy and (b, '43') in moy}
for b in ('B', 'U'):
    if b in av and 'T' in av:
        dl, df, da = av[b][1] - av['T'][1], av[b][2] - av['T'][2], av[b][0] - av['T'][0]
        print('%s - T : lettres %+.2f ; lettres-fond %+.2f ; AUC %+.4f%s' % (b, dl, dl - df, da,
              ('  -> PRIMAIRE %s' % ('TIENT' if dl >= 2.0 and dl - df >= 1.0 and da >= -0.01 else 'ECHOUE')) if b == 'B' else ''))
if 'B' in av and 'U' in av:
    print('B - U (effet du flou) : lettres %+.2f ; AUC %+.4f' % (av['B'][1] - av['U'][1], av['B'][0] - av['U'][0]))
