# PR-23 : mesure sur les lettres CONNUES de PHerc. 841 segB (auto_grown_20260220174252405), pour n importe quelle
# carte -- publiee a 2,4 um, ou sortie des modeles ink_9um a ~9,6 um.
#
# FORME : allongement (aire / r carre, mediane ponderee par l aire), identique a PR-18..PR-22. Toutes les cartes
# sont ramenees sur la MEME grille avant la mesure : une carte a 9,6 um est agrandie x4 (bilineaire) vers la
# grille 2,4 um, puis sous-echantillonnee ::2 comme les autres. Un seul chemin de mesure pour toutes.
#
# GARDE : l AUC encre / hors encre, et non plus l ecart en niveaux de gris. Raison ecrite AVANT la mesure : les
# modeles ink_9um sont entraines avec un lissage d etiquette de 0,5, leur « pas d encre » sort a 0,25 et leur
# encre plafonne vers 0,75 -- un ecart en gris est compresse par construction, et la barre de 133 d hier serait
# inatteignable meme pour un modele parfait. L AUC ne depend pas de l echelle des gris.
#
# usage: eval_segB.py <carte.tif> [ECHELLE]     ECHELLE = 1 (grille 2,4 um) ou 4 (grille 9,6 um)
#        eval_segB.py --etiquettes                (l allongement des etiquettes elles-memes)
import os, sys, numpy as np, tifffile, zarr
from scipy import ndimage, stats

H = '/home/slusarska_holding/vesuvius'
LAB = os.environ.get('ETIQ', '%s/ink-dataset/841/canon_autres/auto_grown_20260220174252405/inklabels.zarr' % H)   # ETIQ : autre segment (PR-26)
PAS, AIRE_MIN, CIBLE, COTE = 2, 50, 0.70, (900, 3000)


def mesures(b):
    lab, n = ndimage.label(b)
    if n == 0:
        return float('nan'), float('nan')
    d = ndimage.distance_transform_edt(b)
    a = np.bincount(lab.ravel())[1:].astype(float)
    r = np.asarray(ndimage.maximum(d, lab, range(1, n + 1)))
    g = a >= AIRE_MIN
    if not g.any():
        return float('nan'), float('nan')
    e = a[g] / np.maximum(r[g], 1.0) ** 2
    o = np.argsort(e)
    med = float(e[o][np.searchsorted(np.cumsum(a[g][o]), a[g].sum() / 2.0)])
    return med, 2.0 * float(d[np.isin(lab, 1 + np.nonzero(g)[0])].mean()) * PAS


z = zarr.open(LAB, mode='r')
L3 = np.asarray(z['3'][:]).squeeze()
if L3.ndim == 3:
    L3 = L3.any(axis=0)
L3 = L3 > 0
lab3, n3 = ndimage.label(L3)
lettres = [(i + 1, s) for i, s in enumerate(ndimage.find_objects(lab3))
           if COTE[0] <= max(s[0].stop - s[0].start, s[1].stop - s[1].start) * 8 <= COTE[1]]

if sys.argv[1] == '--etiquettes':
    e, t = [], []
    for k, s in lettres:
        a0 = z['0']                              # w00 range ses etiquettes en 3D, segB en 2D
        sy, sx = slice(s[0].start * 8, s[0].stop * 8), slice(s[1].start * 8, s[1].stop * 8)
        b = np.asarray(a0[:, sy, sx] if a0.ndim == 3 else a0[sy, sx])
        b = (b.any(axis=0) if b.ndim == 3 else b)[::PAS, ::PAS] > 0
        a, w = mesures(b)
        e.append(a); t.append(w)
    print('%-40s %d lettres  ALLONGEMENT %7.2f  epaisseur %6.1f px' % ('ETIQUETTES segB', len(lettres),
          float(np.nanmedian(e)), float(np.nanmedian(t))))
    sys.exit(0)

carte = sys.argv[1]
SC = int(sys.argv[2]) if len(sys.argv) > 2 else 1
P = tifffile.imread(carte)
if P.ndim == 3:
    P = P[0] if P.shape[0] < P.shape[-1] else P[..., 0]
e, t, crops = [], [], []
for k, s in lettres:
    y0, y1, x0, x1 = s[0].start * 8, s[0].stop * 8, s[1].start * 8, s[1].stop * 8
    m = np.repeat(np.repeat(lab3[s] == k, 8 // PAS, 0), 8 // PAS, 1)
    if SC == 1:
        g = P[y0:y1:PAS, x0:x1:PAS].astype(np.float32)
    else:
        g = ndimage.zoom(P[y0 // SC:-(-y1 // SC), x0 // SC:-(-x1 // SC)].astype(np.float32), SC / PAS, order=1)
    h = (min(g.shape[0], m.shape[0]), min(g.shape[1], m.shape[1]))
    crops.append((g[:h[0], :h[1]], m[:h[0], :h[1]]))
seuil = float(np.quantile(np.concatenate([g[m] for g, m in crops]), 1.0 - CIBLE))
for g, m in crops:
    a, w = mesures(g >= seuil)
    e.append(a); t.append(w)

# GARDE : AUC a la grille niveau 3. Encre = etiquettes ; hors encre = a plus de 320 px de toute etiquette.
g3 = (P[::8, ::8] if SC == 1 else P[::8 // SC, ::8 // SC]).astype(np.float32)
hh = (min(g3.shape[0], L3.shape[0]), min(g3.shape[1], L3.shape[1]))
g3, enc = g3[:hh[0], :hh[1]], L3[:hh[0], :hh[1]]
hors = ~ndimage.binary_dilation(enc, iterations=40) & (g3 > 0)      # hors du papyrus = 0 dans la carte, exclu
vi, vh = g3[enc], g3[hors]
rng = np.random.default_rng(0)
vi = rng.choice(vi, min(len(vi), 200000), replace=False)
vh = rng.choice(vh, min(len(vh), 200000), replace=False)
rk = stats.rankdata(np.concatenate([vi, vh]))
auc = (rk[:len(vi)].sum() - len(vi) * (len(vi) + 1) / 2.0) / (len(vi) * len(vh))
print('%-40s %d lettres  seuil %6.1f  ALLONGEMENT %7.2f  epaisseur %6.1f px  GARDE AUC %.4f  (gris %.1f / %.1f)'
      % (os.path.basename(carte)[:40], len(lettres), seuil, float(np.nanmedian(e)), float(np.nanmedian(t)),
         auc, float(vi.mean()), float(vh.mean())))
