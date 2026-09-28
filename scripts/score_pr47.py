# PR-47 : depouillement. Lettres de reference : centre de la boite de chaque lettre etiquetee sur la carte 8,64 um, nom
# lu par le lecteur des traces de PR-46. Un lecteur « touche » une lettre en la nommant a une case pres (ecart de case
# <= 1 en ligne et en colonne) de la case de son centre ; chaque ligne ne touche qu une lettre, la plus proche. Une ligne
# qui ne touche rien et dont la case a son centre dans la zone supervisee est une fausse alerte ; ailleurs, non comptee.
# usage : score_pr47.py CARTE=LECTEUR1.txt,LECTEUR2.txt,LECTEUR3.txt [...]   (CARTE = R4, base ou readerv2)
import sys, re, numpy as np, zarr

Y0, X0, CW, RH = 4800, 1600, 400, 380
NOMS = ('alpha beta gamma delta epsilon zeta eta theta iota kappa lambda mu nu xi omicron pi rho sigma tau upsilon '
        'phi chi psi omega').split()
# lettre : (y, x) du centre sur la carte, nom de reference
REF = {1: (5470.0, 2095.5, 'nu'), 2: (5453.0, 3508.0, 'alpha'), 3: (5426.5, 2995.5, 'mu'), 4: (5416.5, 2558.0, 'omicron'),
       5: (5497.5, 3893.5, 'zeta'), 6: (5534.0, 4341.0, 'epsilon'), 7: (6161.0, 2128.0, 'eta'), 8: (6125.0, 2646.5, 'sigma'),
       9: (6184.0, 3586.0, 'omicron'), 10: (6169.0, 3119.0, 'delta')}
PROPRES_RV2 = {2, 5, 6, 9, 10}
S = np.asarray(zarr.open('/home/slusarska_holding/vesuvius/ft12m/src/0009B/supervision.zarr', mode='r')['2'][:]).squeeze()
S = (S.any(axis=0) if S.ndim == 3 else S) > 0
FY, FX = 7040 / S.shape[0], 5700 / S.shape[1]


def case(y, x):
    return int((x - X0) // CW), int((y - Y0) // RH)


def lit(f):
    items = []
    for l in open(f, encoding='utf-8'):
        m = re.match(r'\s*`?\s*([A-Ha-h])\s*([1-5])\s*`?\s*:(.*)', l)
        if not m:
            continue
        nom = next((w for w in re.findall(r'[a-z]+', m.group(3).lower()) if w in NOMS), None)
        if nom:
            items.append(('ABCDEFGH'.index(m.group(1).upper()), int(m.group(2)) - 1, nom))
    return items


for arg in sys.argv[1:]:
    carte, fs = arg.split('=')
    lettres = PROPRES_RV2 if carte == 'readerv2' else set(REF)
    touches, fa = {k: 0 for k in lettres}, []
    for n, f in enumerate(fs.split(',')):
        vu, fausses, detail = set(), 0, []
        for c, r, nom in lit(f):
            cand = [(np.hypot(case(*REF[k][:2])[0] - c, case(*REF[k][:2])[1] - r), k) for k in REF
                    if REF[k][2] == nom and max(abs(case(*REF[k][:2])[0] - c), abs(case(*REF[k][:2])[1] - r)) <= 1 and k not in vu]
            if cand:
                k = min(cand)[1]
                vu.add(k)
                detail.append('%s%d %s -> lettre %d' % ('ABCDEFGH'[c], r + 1, nom, k))
            else:
                yc, xc = Y0 + (r + 0.5) * RH, X0 + (c + 0.5) * CW
                dedans = S[min(int(yc / FY), S.shape[0] - 1), min(int(xc / FX), S.shape[1] - 1)]
                fausses += bool(dedans)
                detail.append('%s%d %s -> %s' % ('ABCDEFGH'[c], r + 1, nom, 'FAUSSE ALERTE' if dedans else 'hors zone'))
        for k in vu & lettres:
            touches[k] += 1
        fa.append(fausses)
        print('%-8s lecteur %d : %d lettres touchees %s, %d fausses alertes | %s'
              % (carte, n + 1, len(vu & lettres), sorted(vu & lettres), fausses, ' ; '.join(detail)))
    maj = sorted(k for k, v in touches.items() if v >= 2)
    print('%-8s : lettres touchees par >= 2 lecteurs sur 3 : %d sur %d %s ; par un seul : %s ; fausses alertes %s'
          % (carte, len(maj), len(lettres), maj, sorted(k for k, v in touches.items() if v == 1), fa))
    if carte == 'R4':
        print('PRIMAIRE : %d (>= 3 : la porte de 0800 et 1447 s ouvre)' % len(maj))
