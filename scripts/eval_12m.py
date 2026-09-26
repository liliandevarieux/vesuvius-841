# PR-28 : AUC d une carte ink_9um faite sur un volume 1,2 m (~9 um) contre des etiquettes sur la grille 2,4 um.
# Etiquettes au niveau 3 (8x) ; chaque pixel L3 (i, j) lit la carte au pixel round((8i + 4) / R), R = rapport des
# tailles de voxel (ex. 9,366 / 2,403). Encre = etiquette ; fond = a plus de 40 px L3 (320 px pleine resolution) de
# toute etiquette, sur le papyrus (carte > 0) -- meme definition que eval_segB.py.
# Imprime aussi le score SANS etiquette du sens : p99 - p50 de la carte sur le papyrus.
# usage : eval_12m.py CARTE.tif ETIQUETTES.zarr R     (ETIQUETTES = - : pas d etiquette, score du sens seul)
import sys, os, numpy as np, tifffile, zarr
from scipy import ndimage, stats

P = tifffile.imread(sys.argv[1]).astype(np.float32)
if P.ndim == 3:
    P = P[0] if P.shape[0] < P.shape[-1] else P[..., 0]
if sys.argv[2] == '-':                               # rouleau sans etiquette (PHerc0800) : le sens seulement
    pap = P[P > 0]
    print('%-44s sans etiquette  sens p99-p50 %.1f' % (os.path.basename(sys.argv[1])[:44],
          np.percentile(pap, 99) - np.percentile(pap, 50)))
    sys.exit(0)
L = np.asarray(zarr.open(sys.argv[2], mode='r')['3'][:]).squeeze()
L = (L.any(axis=0) if L.ndim == 3 else L) > 0
R = float(sys.argv[3])
iy = np.rint((8 * np.arange(L.shape[0]) + 4) / R).astype(int)
ix = np.rint((8 * np.arange(L.shape[1]) + 4) / R).astype(int)
ky, kx = iy < P.shape[0], ix < P.shape[1]
L = L[ky][:, kx]
g = P[np.ix_(iy[ky], ix[kx])]
hors = ~ndimage.binary_dilation(L, iterations=40) & (g > 0)
vi, vh = g[L], g[hors]
rk = stats.rankdata(np.concatenate([vi, vh]))
auc = (rk[:len(vi)].sum() - len(vi) * (len(vi) + 1) / 2.0) / (len(vi) * len(vh))
pap = P[P > 0]
print('%-44s AUC %.4f  (encre %d px, fond %d px, gris %.1f / %.1f)  sens sans etiquette p99-p50 %.1f'
      % (os.path.basename(sys.argv[1])[:44], auc, len(vi), len(vh), vi.mean(), vh.mean(),
         np.percentile(pap, 99) - np.percentile(pap, 50)))
