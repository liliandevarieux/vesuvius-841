# PR-45, controle de contamination : notre segment etiquete de 0009B (20250919125754) repasse-t-il sur la meme surface
# que l un des 14 segments de 0009B sur lesquels Reader v2 s est entraine ? Meme methode que recouvrement_841.py :
# distance de chaque point de maillage (tifxyz 8,64 um ; un point = 20 px de canevas) au point le plus proche de l autre
# maillage, puis la meme distance pour les seuls points sous nos lettres etiquetees. Deux copies de la meme surface
# restent a moins de ~15 voxels l une de l autre (pas de la grille) ; deux spires voisines, plus loin.
# usage : recouvrement_0009B.py        (imprime ; rien n est ecrit)
import glob, numpy as np, tifffile, zarr
from scipy.spatial import cKDTree

D = '/home/slusarska_holding/vesuvius/ft12m/mesh0009B/'
NOUS = '20250919125754'
LES14 = ['20250510172804', '20250511200236', '20250919064353', '20250919123506', '20250919124722', '20250919124917',
         '20250919125302', '20250919125605', '20250919130642', '20250919131352', '20250919131642', '20250919132115',
         '20250919135433', '20250919135915']


def maillage(i):
    d = sorted(glob.glob(D + i + '/*8.64um.tifxyz/'))
    if not d:
        return None
    x, y, z = (tifffile.imread(d[0] + c + '.tif').astype(np.float64) for c in 'xyz')
    return x, y, z


def points(x, y, z, ok):
    return np.stack([x[ok], y[ok], z[ok]], 1)


x, y, z = maillage(NOUS)
ok = np.isfinite(x) & ~((x == -1) & (y == -1) & (z == -1)) & (x > 0)
P = points(x, y, z, ok)
m = np.asarray(zarr.open('/home/slusarska_holding/vesuvius/ft12m/src/0009B/inklabels.zarr', mode='r')['2'][:]).squeeze()
m = (m.max(axis=0) if m.ndim == 3 else m) > 0
r, c = np.nonzero(m)
gi = np.clip(np.rint(r * x.shape[0] / m.shape[0]).astype(int), 0, x.shape[0] - 1)
gj = np.clip(np.rint(c * x.shape[1] / m.shape[1]).astype(int), 0, x.shape[1] - 1)
cel = np.unique(np.stack([gi, gj], 1), axis=0)
cel = cel[ok[cel[:, 0], cel[:, 1]]]
Q = np.stack([x[cel[:, 0], cel[:, 1]], y[cel[:, 0], cel[:, 1]], z[cel[:, 0], cel[:, 1]]], 1)
print('nous %s : grille %s, %d points de surface, %d sous les lettres (etiquettes %s)' % (NOUS, x.shape, len(P), len(Q), m.shape))
print('boite englobante (x, y, z) : %s -> %s' % (P.min(0).round(), P.max(0).round()))
tous_P, tous_Q = np.full(len(P), np.inf), np.full(len(Q), np.inf)
for i in LES14:
    t = maillage(i)
    if t is None:
        print('%s : pas de maillage 8,64 um -- non mesure' % i)
        continue
    okt = np.isfinite(t[0]) & ~((t[0] == -1) & (t[1] == -1) & (t[2] == -1)) & (t[0] > 0)
    T = cKDTree(points(*t, okt))
    d, _ = T.query(P, k=1)
    dq, _ = T.query(Q, k=1)
    tous_P, tous_Q = np.minimum(tous_P, d), np.minimum(tous_Q, dq)
    print('%s : surface min %7.1f p1 %7.1f mediane %7.1f vx ; < 15 vx %5.2f %%, < 40 vx %5.2f %% | lettres min %7.1f, < 15 vx %5.2f %%'
          % (i, d.min(), np.percentile(d, 1), np.median(d), 100 * (d < 15).mean(), 100 * (d < 40).mean(),
             dq.min(), 100 * (dq < 15).mean()))
print('LES 14 ENSEMBLE : surface < 15 vx %5.2f %%, < 40 vx %5.2f %% | lettres < 15 vx %5.2f %%, < 40 vx %5.2f %%, min %.1f vx'
      % (100 * (tous_P < 15).mean(), 100 * (tous_P < 40).mean(), 100 * (tous_Q < 15).mean(), 100 * (tous_Q < 40).mean(),
         tous_Q.min()))

# --- lettre par lettre, numerotees comme panneau_lettres_841.py (etiquettes & supervision, niveau 2, cote >= 150 px) ---
from scipy import ndimage


def niv2(n):
    a = np.asarray(zarr.open('/home/slusarska_holding/vesuvius/ft12m/src/0009B/%s.zarr' % n, mode='r')['2'][:]).squeeze()
    return (a.any(axis=0) if a.ndim == 3 else a) > 0


L = niv2('inklabels') & niv2('supervision')
lab, _ = ndimage.label(L)
objs = [(k + 1, s) for k, s in enumerate(ndimage.find_objects(lab)) if max(s[0].stop - s[0].start, s[1].stop - s[1].start) >= 150]
dg = np.full(x.shape, np.inf)
dg[ok] = tous_P
for i, (k, s) in enumerate(objs):
    r, c = np.nonzero(lab[s] == k)
    gi = np.clip(np.rint((r + s[0].start) * x.shape[0] / L.shape[0]).astype(int), 0, x.shape[0] - 1)
    gj = np.clip(np.rint((c + s[1].start) * x.shape[1] / L.shape[1]).astype(int), 0, x.shape[1] - 1)
    cel = np.unique(np.stack([gi, gj], 1), axis=0)
    d = dg[cel[:, 0], cel[:, 1]]
    d = d[np.isfinite(d)]
    print('lettre %2d : %4d points de maillage, < 15 vx des 14 : %5.1f %%, min %6.1f vx' % (i + 1, len(d), 100 * (d < 15).mean(), d.min()))
