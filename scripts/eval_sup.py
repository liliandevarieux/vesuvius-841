# PR-31 : AUC d une carte (grille 1,2 m) DANS la zone de supervision : encre = etiquette, fond = supervision sans
# etiquette, a plus de 2 px (niveau 2, ~20 um) de toute etiquette (bord de trace exclu). Etiquettes et supervision
# 20260918 au niveau 2 (ft12m/src/<seg>/{inklabels,supervision}.zarr) ; la carte est lue au pixel correspondant par
# le rapport des canevas. C est la mesure « on supervision » d AndreasHad04 (#1898) : le fond ne contient pas
# d encre non etiquetee (question d ibara).
# usage : eval_sup.py CARTE.tif SEGMENT
import sys, os, numpy as np, tifffile, zarr
from scipy import ndimage

S = '/home/slusarska_holding/vesuvius/ft12m/src/' + sys.argv[2]


def niv2(n):
    a = np.asarray(zarr.open('%s/%s.zarr' % (S, n), mode='r')['2'][:]).squeeze()
    return (a.any(axis=0) if a.ndim == 3 else a) > 0


L, Sup = niv2('inklabels'), niv2('supervision')
P = tifffile.imread(sys.argv[1]).astype(np.float32)
if P.ndim == 3:
    P = P[0] if P.shape[0] < P.shape[-1] else P[..., 0]
iy = np.minimum(((np.arange(L.shape[0]) + 0.5) * P.shape[0] / L.shape[0]).astype(int), P.shape[0] - 1)
ix = np.minimum(((np.arange(L.shape[1]) + 0.5) * P.shape[1] / L.shape[1]).astype(int), P.shape[1] - 1)
g = P[np.ix_(iy, ix)]
enc = L & Sup
fond = Sup & ~ndimage.binary_dilation(L, iterations=2)
hi = np.histogram(g[enc], bins=256, range=(0, 256))[0].astype(float)
hf = np.histogram(g[fond], bins=256, range=(0, 256))[0].astype(float)
auc = (hi * (np.cumsum(hf) - hf / 2)).sum() / (hi.sum() * hf.sum())     # P(encre > fond), egalites a moitie
pap = P[P > 0]
print('%-40s %-9s AUC-sup %.4f  (encre %d, fond %d, gris %.1f / %.1f)  sens p99-p50 %.1f'
      % (os.path.basename(sys.argv[1])[:40], sys.argv[2], auc, enc.sum(), fond.sum(), g[enc].mean(), g[fond].mean(),
         np.percentile(pap, 99) - np.percentile(pap, 50)))
