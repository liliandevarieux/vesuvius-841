# PR-60 : plan des carrés, fixé AVANT tout calcul de carte de 0800, à partir du seul scanner (aucune carte d'encre).
# 0800 : pour chaque surface, masque = couche 15 (la surface) non nulle au niveau 0 ; grille de carrés de 1024 px posée au
# coin haut-gauche de la boîte du masque ; on garde les carrés couverts à 50 % au moins.
# Erwin (343) : repère de lecture (2455 x 5641), cadre centré 2048 x 5120, 2 x 5 carrés ; « avec lettre » = contient le
# centre d'au moins une des 12 lettres de référence.
# 0009B : fenêtre de PR-47 élargie à 2048 x 3072 (lignes 4726-6774, colonnes 1664-4736), 2 x 3 carrés ; « avec lettre »
# = contient le centre d'au moins une des 10 lettres étiquetées (score_pr47.py).
# Sortie : c0800/plan_carres.json. usage : c0800_carres.py
import glob, json, numpy as np, zarr

H = '/home/slusarska_holding/vesuvius/'
T, PART = 1024, 0.5
plan = {'taille': T, 'carres': []}
for f in sorted(open(H + 'c0800_surfaces14.tsv').read().split('\n')):
    if not f.strip():
        continue
    m = f.split('\t')[0]
    z = glob.glob(H + 'c0800/atlas/%s/surface-volumes/*.zarr' % m)
    assert len(z) == 1, (m, z)
    a = zarr.open(z[0], mode='r')['0']
    S = np.asarray(a[15]) > 0
    ys, xs = np.nonzero(S); y0, x0 = ys.min(), xs.min()
    n = 0
    for Y in range(y0, ys.max() + 1, T):
        for X in range(x0, xs.max() + 1, T):
            c = S[Y:Y + T, X:X + T]
            if c.size == T * T and c.mean() >= PART or c.size < T * T and c.sum() >= PART * T * T:
                plan['carres'].append(dict(zone='0800', surface=m, zarr=z[0], y=int(Y), x=int(X), couvert=round(float(c.sum()) / T / T, 3)))
                n += 1
    print('%-12s volume %s  masque %.2f Mpx  carres %d' % (m, a.shape, S.sum() / 1e6, n))
REF_E = json.load(open(H + 'c343/reference_12_lettres.json'))
CE = [((l['zone'][1] + l['zone'][3]) / 2, (l['zone'][0] + l['zone'][2]) / 2, l['id']) for l in REF_E]
for i in range(2):
    for j in range(5):
        Y, X = 203 + T * i, 260 + T * j
        dedans = [k for y, x, k in CE if Y <= y < Y + T and X <= x < X + T]
        plan['carres'].append(dict(zone='erwin', y=Y, x=X, lettres=dedans))
REF_B = {1: (5470.0, 2095.5), 2: (5453.0, 3508.0), 3: (5426.5, 2995.5), 4: (5416.5, 2558.0), 5: (5497.5, 3893.5),
         6: (5534.0, 4341.0), 7: (6161.0, 2128.0), 8: (6125.0, 2646.5), 9: (6184.0, 3586.0), 10: (6169.0, 3119.0)}
for i in range(2):
    for j in range(3):
        Y, X = 4726 + T * i, 1664 + T * j
        dedans = [k for k, (y, x) in REF_B.items() if Y <= y < Y + T and X <= x < X + T]
        plan['carres'].append(dict(zone='0009B', y=Y, x=X, lettres=dedans))
for zn in ('0800', 'erwin', '0009B'):
    C = [c for c in plan['carres'] if c['zone'] == zn]
    print(zn, len(C), 'carres' + ('' if zn == '0800' else ', dont %d avec lettre' % sum(1 for c in C if c['lettres'])))
json.dump(plan, open(H + 'c0800/plan_carres.json', 'w'), indent=1)
