# PR-25 : dans 841, les lettres les moins tassees sont-elles rendues plus en traits ?
# Par lettre etiquetee (segA 6, segB 5) : occupation = mediane de l occupation par colonne (formule du
# « readability gate », voir occupation.py) sur la boite de la lettre, une colonne tous les 8 px, couches 23-84 ;
# allongement de la carte publiee pred.tif sur la lettre (definition de PR-18, seuil a 70 % de remplissage
# des lettres du segment). Primaire enregistre : Spearman < 0, p unilateral < 0,05.
import numpy as np, zarr, tifffile
from scipy import ndimage, stats
from scipy.ndimage import gaussian_filter1d

H = '/home/slusarska_holding/vesuvius/ink-dataset/841'
SEGS = [('segA', '%s/segA/segA.zarr' % H, '%s/canon_autres/auto_grown_20260220144552896' % H),
        ('segB', '%s/segB/segB.zarr' % H, '%s/canon_autres/auto_grown_20260220174252405' % H)]
PAS, AIRE_MIN, CIBLE, COTE, N, Z0, PASO = 2, 50, 0.70, (900, 3000), 62, 23, 8


def mesures(b):
    lab, n = ndimage.label(b)
    if n == 0:
        return float('nan')
    d = ndimage.distance_transform_edt(b)
    a = np.bincount(lab.ravel())[1:].astype(float)
    r = np.asarray(ndimage.maximum(d, lab, range(1, n + 1)))
    g = a >= AIRE_MIN
    if not g.any():
        return float('nan')
    e = a[g] / np.maximum(r[g], 1.0) ** 2
    o = np.argsort(e)
    return float(e[o][np.searchsorted(np.cumsum(a[g][o]), a[g].sum() / 2.0)])


occ, elo = [], []
for nom, VOL, D in SEGS:
    v = zarr.open(VOL, mode='r')['0']
    P = tifffile.imread(D + '/pred.tif')
    L3 = np.asarray(zarr.open(D + '/inklabels.zarr', mode='r')['3'][:]) > 0
    lab3, _ = ndimage.label(L3)
    lettres = [(i + 1, s) for i, s in enumerate(ndimage.find_objects(lab3))
               if COTE[0] <= max(s[0].stop - s[0].start, s[1].stop - s[1].start) * 8 <= COTE[1]]
    crops, oc = [], []
    for k, s in lettres:
        y0, y1, x0, x1 = s[0].start * 8, s[0].stop * 8, s[1].start * 8, s[1].stop * 8
        m = np.repeat(np.repeat(lab3[s] == k, 8 // PAS, 0), 8 // PAS, 1)
        g = P[y0:y1:PAS, x0:x1:PAS].astype(np.float32)
        h = (min(g.shape[0], m.shape[0]), min(g.shape[1], m.shape[1]))
        crops.append((g[:h[0], :h[1]], m[:h[0], :h[1]]))
        a = np.asarray(v[Z0:Z0 + N, y0:y1:PASO, x0:x1:PASO]).astype(np.float32).reshape(N, -1)
        a = a[:, a.max(0) > 0]
        p = gaussian_filter1d(a, 1.5, axis=0)
        p /= p.max(0) + 1e-6
        oc.append(float(np.median((p > 0.5).mean(0))))
    seuil = float(np.quantile(np.concatenate([g[m] for g, m in crops]), 1.0 - CIBLE))
    for (k, s), (g, m), o in zip(lettres, crops, oc):
        e = mesures(g >= seuil)
        occ.append(o); elo.append(e)
        print('%s lettre %d  boite %5d x %5d px  occupation %.3f  allongement %6.2f'
              % (nom, k, (s[0].stop - s[0].start) * 8, (s[1].stop - s[1].start) * 8, o, e))
r, p2 = stats.spearmanr(occ, elo)
p1 = p2 / 2 if r < 0 else 1 - p2 / 2
print('n %d  Spearman rho %.3f  p unilateral (rho < 0) %.4f  -> %s'
      % (len(occ), r, p1, 'TIENT' if (r < 0 and p1 < 0.05) else 'ECHOUE'))
