# Ordre stocke contre ordre inverse, sur le rendu 65 plans du seau de labels, juge par les labels v2 du meme seau.
# Meme mesure que mesure_sens.py : moyenne dans l encre moins moyenne dans le fond inspecte (dilate de 3 pour ecarter
# les bords). Pas de correlation ici : le seau ne porte pas de prediction publiee pour ce segment.
# usage: mesure_seau.py <racine locale>
import sys, numpy as np, tifffile
from scipy import ndimage
R = sys.argv[1]; H = '/home/slusarska_holding/vesuvius'
L = tifffile.imread(f'{R}/labels_v2.tif') > 0
S = tifffile.imread(f'{R}/supervision_v2.tif') > 0
fen = [tuple(map(int, l.split())) for l in open(f'{R}/fenetres.txt')]
print(f'{"fenetre":>8s} | {"ORDRE STOCKE  encre    fond   ecart":36s} | {"INVERSE  encre    fond   ecart":32s}')
d, r = [], []
def mes(k, suf):
    a = tifffile.imread(f'{H}/predictions/seau174_w{k}{suf}_human7n.tif').astype(np.float32)
    Y0, Y1, X0, X1 = fen[k - 1]
    l = L[Y0:Y0 + a.shape[0], X0:X0 + a.shape[1]]; s = S[Y0:Y0 + a.shape[0], X0:X0 + a.shape[1]]
    m = [min(a.shape[0], l.shape[0]), min(a.shape[1], l.shape[1])]
    a, l, s = a[:m[0], :m[1]], l[:m[0], :m[1]], s[:m[0], :m[1]]
    f = s & ~ndimage.binary_dilation(l, iterations=3)
    if l.sum() < 500 or f.sum() < 500: return None
    return a[l].mean(), a[f].mean()
for k in range(1, len(fen) + 1):
    try: x, y = mes(k, ''), mes(k, 'r')
    except FileNotFoundError: print(f'{k:8d} | (pas encore infere)'); continue
    if x is None or y is None: print(f'{k:8d} | (fenetre sans encre labellisee)'); continue
    d.append(x); r.append(y)
    print(f'{k:8d} | {x[0]:16.1f} {x[1]:7.1f} {x[0]-x[1]:7.1f} | {y[0]:12.1f} {y[1]:7.1f} {y[0]-y[1]:7.1f}')
if d:
    d, r = np.array(d), np.array(r)
    gd = d[:, 0].mean() - d[:, 1].mean(); gr = r[:, 0].mean() - r[:, 1].mean()
    print(f'{"moyenne":>8s} | {d[:,0].mean():16.1f} {d[:,1].mean():7.1f} {gd:7.1f} | {r[:,0].mean():12.1f} {r[:,1].mean():7.1f} {gr:7.1f}')
    print(f'\nSur le rendu du SEAU, notre modele prefere l ordre {"STOCKE" if gd > gr else "INVERSE"} (ecart {abs(gd-gr):.1f}).')
    print('Rappel : sur le VOLUME DE SURFACE PUBLIE du meme segment, il preferait l ordre INVERSE (27,3 -> 75,9).')
    print('Si les deux preferences different, le sens appartient au TABLEAU et non au SEGMENT.')
