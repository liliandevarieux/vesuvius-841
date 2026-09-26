# PR-32 : forme de l encre sur les lettres etiquetees d un segment 1,2 m (mesure de lisibilite sans lecteur).
# Carte ramenee sur la grille des etiquettes 20260918 niveau 2 (~9,6 um, interpolation lineaire) ; lettres = composantes
# etiquetees dans la supervision ; seuil = 30e centile de la carte sous toutes les lettres du segment (70 % de
# remplissage, comme PR-18) ; allongement par lettre = mediane ponderee par l aire de aire / r^2 des composantes
# seuillees (r = rayon inscrit max), definition de PR-18 ; on rapporte la mediane sur les lettres.
# usage : eval_forme.py CARTE.tif SEGMENT
import sys, os, numpy as np, tifffile, zarr
from scipy import ndimage

S = '/home/slusarska_holding/vesuvius/ft12m/src/' + sys.argv[2]


def niv2(n):
    a = np.asarray(zarr.open('%s/%s.zarr' % (S, n), mode='r')['2'][:]).squeeze()
    return (a.any(axis=0) if a.ndim == 3 else a) > 0


def allongement(b):
    lab, n = ndimage.label(b)
    if n == 0:
        return float('nan')
    d = ndimage.distance_transform_edt(b)
    a = np.bincount(lab.ravel())[1:].astype(float)
    r = np.asarray(ndimage.maximum(d, lab, range(1, n + 1)))
    g = a >= 12
    if not g.any():
        return float('nan')
    e = a[g] / np.maximum(r[g], 1.0) ** 2
    o = np.argsort(e)
    return float(e[o][np.searchsorted(np.cumsum(a[g][o]), a[g].sum() / 2.0)])


L = niv2('inklabels') & niv2('supervision')
P = tifffile.imread(sys.argv[1]).astype(np.float32)
if P.ndim == 3:
    P = P[0] if P.shape[0] < P.shape[-1] else P[..., 0]
G = ndimage.zoom(P, (L.shape[0] / P.shape[0], L.shape[1] / P.shape[1]), order=1)[:L.shape[0], :L.shape[1]]
lab, n = ndimage.label(L)
objs = [(k + 1, s) for k, s in enumerate(ndimage.find_objects(lab)) if max(s[0].stop - s[0].start, s[1].stop - s[1].start) >= 150]
t = np.quantile(np.concatenate([G[s][lab[s] == k] for k, s in objs]), 0.30)
e = [allongement(G[s] >= t) for k, s in objs]
lab_e = [allongement(lab[s] == k) for k, s in objs]
print('%-40s %-9s lettres %2d  ALLONGEMENT carte %6.2f  (etiquettes %6.2f)' % (os.path.basename(sys.argv[1])[:40], sys.argv[2],
      len(objs), np.nanmedian(e), np.nanmedian(lab_e)))
