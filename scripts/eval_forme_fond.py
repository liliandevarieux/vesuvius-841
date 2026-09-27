# PR-37 : garde-fou de eval_forme.py. Meme carte, meme seuil (30e centile de la carte sous les lettres etiquetees,
# 70 % de remplissage), mais l allongement est mesure sur le FOND supervise (supervision sans etiquette, a plus de
# 10 px niveau 2 de toute etiquette) : mediane ponderee par l aire de aire / r^2 des composantes seuillees.
# Si un modele « dessine des traits partout », ce chiffre monte autant que celui des lettres.
# usage : eval_forme_fond.py CARTE.tif SEGMENT
import sys, os, numpy as np, tifffile, zarr
from scipy import ndimage

S = '/home/slusarska_holding/vesuvius/ft12m/src/' + sys.argv[2]


def niv2(n):
    a = np.asarray(zarr.open('%s/%s.zarr' % (S, n), mode='r')['2'][:]).squeeze()
    return (a.any(axis=0) if a.ndim == 3 else a) > 0


Lb, Sup = niv2('inklabels'), niv2('supervision')
L = Lb & Sup
P = tifffile.imread(sys.argv[1]).astype(np.float32)
if P.ndim == 3:
    P = P[0] if P.shape[0] < P.shape[-1] else P[..., 0]
G = ndimage.zoom(P, (L.shape[0] / P.shape[0], L.shape[1] / P.shape[1]), order=1)[:L.shape[0], :L.shape[1]]
lab, n = ndimage.label(L)
objs = [(k + 1, s) for k, s in enumerate(ndimage.find_objects(lab)) if max(s[0].stop - s[0].start, s[1].stop - s[1].start) >= 150]
t = np.quantile(np.concatenate([G[s][lab[s] == k] for k, s in objs]), 0.30)
B = (G >= t) & Sup[:G.shape[0], :G.shape[1]] & ~ndimage.binary_dilation(Lb, iterations=10)[:G.shape[0], :G.shape[1]]
lb, m = ndimage.label(B)
a = np.bincount(lb.ravel())[1:].astype(float)
r = np.asarray(ndimage.maximum(ndimage.distance_transform_edt(B), lb, range(1, m + 1)))
g = a >= 12
e = a[g] / np.maximum(r[g], 1.0) ** 2
o = np.argsort(e)
med = float(e[o][np.searchsorted(np.cumsum(a[g][o]), a[g].sum() / 2.0)]) if g.any() else float('nan')
print('%-40s %-9s FOND ALLONGEMENT %6.2f  (composantes %d, remplissage du fond %.3f)' % (os.path.basename(sys.argv[1])[:40],
      sys.argv[2], med, int(g.sum()), B.sum() / max(1, (Sup & ~ndimage.binary_dilation(Lb, iterations=10)).sum())))
