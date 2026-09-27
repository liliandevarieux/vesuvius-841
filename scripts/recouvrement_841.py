# PR-39 : les trois feuillets etiquetes de 841 (w00, segA, segB) sont-ils des surfaces distinctes du rouleau ?
# Si deux feuillets repassaient sur la meme surface, une lettre tenue a l ecart dans l un aurait ete vue a l entrainement
# dans l autre, et le test "meme rouleau, autre feuillet" serait truque. Mesure : distance de chaque point de surface
# (maillages tifxyz, volume 2,403 um) au point le plus proche des autres feuillets. Un point de maillage = 20 px de
# canevas, donc deux copies de la meme surface restent a ~15 voxels l une de l autre ; deux spires voisines, bien plus.
# usage : recouvrement_841.py        (imprime ; rien n est ecrit)
import numpy as np, tifffile
from scipy.spatial import cKDTree

B = '/home/slusarska_holding/vesuvius/ink-dataset/841/'
F = {'w00': B + 'w00v24/', 'segA': B + 'a841/', 'segB': B + 'b841/'}
P = {}
for k, d in F.items():
    x, y, z = (tifffile.imread(d + c + '.tif').astype(np.float64) for c in 'xyz')
    ok = np.isfinite(x) & ~((x == -1) & (y == -1) & (z == -1))
    P[k] = np.stack([x[ok], y[ok], z[ok]], 1)
    print('%-5s grille %s, %d points de surface' % (k, x.shape, ok.sum()))
T = {k: cKDTree(v) for k, v in P.items()}
for a in P:
    for b in P:
        if a != b:
            d, _ = T[b].query(P[a], k=1)
            print('%-5s -> %-5s : min %6.1f  p1 %6.1f  p5 %6.1f  mediane %6.1f voxels ; < 15 vx %5.2f %%, < 40 vx %5.2f %%'
                  % (a, b, d.min(), *np.percentile(d, [1, 5, 50]), 100 * (d < 15).mean(), 100 * (d < 40).mean()))

# --- les LETTRES etiquetees (niveau 3 = 1/8 du canevas ; un point de maillage = 20 px de canevas) --------------------
import zarr
from scipy import ndimage
LAB = {'w00': ['w00v24/w00v24_inklabels_v2.zarr'], 'segA': ['a841/a841_inklabels.zarr', 'a841/a841_inklabels_v2.zarr'],
       'segB': ['b841/b841_inklabels.zarr', 'b841/b841_inklabels_v2.zarr']}
Q, NL = {}, {}
for k, d in F.items():
    x, y, z = (tifffile.imread(d + c + '.tif').astype(np.float64) for c in 'xyz')
    m = None
    for f in LAB[k]:
        try:
            a = np.asarray(zarr.open(B + f, mode='r')['3']).max(axis=0) > 0
        except Exception:
            continue
        m = a if m is None else (m | a)
    NL[k] = ndimage.label(m)[1]
    r, c = np.nonzero(m)
    gi = np.clip(np.rint(r * 8 / 20).astype(int), 0, x.shape[0] - 1)
    gj = np.clip(np.rint(c * 8 / 20).astype(int), 0, x.shape[1] - 1)
    cel = np.unique(np.stack([gi, gj], 1), axis=0)
    pts = np.stack([x[cel[:, 0], cel[:, 1]], y[cel[:, 0], cel[:, 1]], z[cel[:, 0], cel[:, 1]]], 1)
    Q[k] = pts[~((pts == -1).all(1)) & np.isfinite(pts).all(1)]
    print('%-5s etiquettes : %d composantes, %d points de maillage sous etiquette' % (k, NL[k], len(Q[k])))
TQ = {k: cKDTree(v) for k, v in Q.items()}
for a in Q:
    for b in Q:
        if a != b:
            ds, _ = T[b].query(Q[a], k=1)
            dl, _ = TQ[b].query(Q[a], k=1)
            print('lettres %-5s -> surface %-5s : min %6.1f mediane %6.1f, < 15 vx %5.2f %% | -> lettres %-5s : min %6.1f, < 40 vx %5.2f %%'
                  % (a, b, ds.min(), np.median(ds), 100 * (ds < 15).mean(), b, dl.min(), 100 * (dl < 40).mean()))
