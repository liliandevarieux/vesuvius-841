# LA SENSIBILITE, MESUREE CORRECTEMENT CETTE FOIS.
#
# LA FAUTE QUE CE SCRIPT CORRIGE. Le 25/09 j ai « mesure la sensibilite » du critere de forme en comptant les
# objets qui passent le critere DANS la zone labellisee. Ce n est pas une sensibilite : une seule lettre peut
# produire plusieurs objets qui passent, et la zone dilatee deborde autour. Le chiffre a fini par imprimer
# « 10/7 lettres retrouvees » sur w00 -- impossible, et c est ce qui a rendu la faute visible. Sur segA et segB il
# n avait jamais depasse le nombre de lettres, donc il est passe inapercu et c est lui qui a servi a choisir le
# seuil de 70 % de PR-14.
#
# LA BONNE DEFINITION : une lettre est RETROUVEE si au moins un objet passant le critere la recouvre. La
# sensibilite est la part des lettres retrouvees. Elle ne peut pas depasser 100 %.
#
# DENOMINATEUR : seules les composantes de label de TAILLE DE LETTRE (900-3000 px de plus grand cote) comptent.
# Un fragment de 272 px ne peut pas etre retrouve par un critere qui exige 900 px -- l inclure mesurerait la
# granularite des labels, pas le detecteur.
#
# usage: sensibilite.py
import os, numpy as np, tifffile, zarr
from scipy import ndimage

H = '/home/slusarska_holding/vesuvius'
COTE, OCC = (900, 3000), (0.20, 0.55)
CIBLES = (0.30, 0.40, 0.534, 0.70, 0.85, 0.95)


def labels(ch, k='3'):
    a = np.asarray(zarr.open(ch, mode='r')[k][:]).squeeze()
    return ((a.any(axis=0) if a.ndim == 3 else a) > 0)


def passe(c):
    return COTE[0] <= max(c.shape) * 8 <= COTE[1] and OCC[0] <= c.sum() / (c.shape[0] * c.shape[1]) <= OCC[1]


def mesure(a, L):
    """(sensibilite par seuil, nombre de formes hors zone lue par seuil). L = labels booleens."""
    lab, n = ndimage.label(L)
    sl = ndimage.find_objects(lab)
    lettres = [i + 1 for i in range(n)
               if COTE[0] <= max(sl[i][0].stop - sl[i][0].start, sl[i][1].stop - sl[i][1].start) * 8 <= COTE[1]]
    dans = ndimage.binary_dilation(L, iterations=40)
    out = []
    for cible in CIBLES:
        v = np.unique(np.round(a[L])); s, e = v[0], 1e9
        for t in v:
            d = abs(float((a[L] >= t).mean()) - cible)
            if d < e:
                s, e = t, d
        m = a >= s
        mo, nm = ndimage.label(m)
        # les objets qui passent le critere, et quelles lettres ils recouvrent
        trouvees, dehors = set(), 0
        for i, sli in enumerate(ndimage.find_objects(mo), 1):
            c = (mo[sli] == i)
            if c.sum() < 50 or not passe(c):
                continue
            sous = lab[sli][c]
            touchees = set(int(x) for x in np.unique(sous) if x in lettres)
            if touchees:
                trouvees |= touchees
            elif not dans[sli][c].any():
                dehors += 1
        out.append((100 * float((a[L] >= s).mean()), s, len(trouvees), len(lettres), dehors))
    return out


JEUX = [('segB', '%s/ink-dataset/841/canon_autres/auto_grown_20260220174252405/pred.tif' % H,
         '%s/ink-dataset/841/canon_autres/auto_grown_20260220174252405/inklabels.zarr' % H),
        ('segA', '%s/ink-dataset/841/canon_autres/auto_grown_20260220144552896/pred.tif' % H,
         '%s/ink-dataset/841/canon_autres/auto_grown_20260220144552896/inklabels.zarr' % H)]
for f in ('new_canon_20260417_recale.tif', 'ps48_640_640_smooth_0.1_w00_ckpt_130000_forward_210326.tif',
          'w00_canonical_030726_reverse_070326.tif', 'w00_canonical_2um_20250807020208.tif'):
    JEUX.append(('w00/' + f[:34], '%s/ink-dataset/841/w00/preds/%s' % (H, f),
                 '%s/ink-dataset/841/w00/w00_inklabels_human7.zarr' % H))

print('%-38s %10s %6s %14s %9s' % ('carte', 'remplis.', 'seuil', 'lettres vues', 'dehors'))
for nom, fp, fl in JEUX:
    if not os.path.exists(fp):
        print('%-38s ABSENTE' % nom); continue
    L = labels(fl)
    a = tifffile.imread(fp)[::8, ::8].astype(np.float32)
    k = (min(a.shape[0], L.shape[0]), min(a.shape[1], L.shape[1]))
    a, Lk = a[:k[0], :k[1]], L[:k[0], :k[1]]
    res = mesure(a, Lk)
    meilleur = max(res, key=lambda r: (r[2], -r[0]))
    for rem, s, tr, nl, deh in res:
        mark = '   <-- sensibilite maximale' if (rem, s, tr, nl, deh) == meilleur else ''
        print('%-38s %8.1f %% %6.0f %8d / %-3d %9d%s' % (nom[:38], rem, s, tr, nl, deh, mark))
    print()
    del a
