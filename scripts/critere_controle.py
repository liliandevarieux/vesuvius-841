# LE CRITERE DE FORME TROUVE-T-IL LES LETTRES QU ON SAIT ETRE LA ?
#
# POURQUOI CETTE VERIFICATION PASSE AVANT TOUT LE RESTE. PR-14 repose sur un chiffre : sur la carte des
# organisateurs il n y a que 8 formes de lettre hors zone labellisee sur segB et 10 sur segA. Ce chiffre dit que
# l objectif du projet est peut-etre ferme. Il ne vaut RIEN tant qu on n a pas montre que le critere se declenche
# la ou des lettres existent vraiment. Un detecteur qui ne trouve pas ce qu il a ete calibre a trouver ne prouve
# pas une absence, il prouve qu il ne detecte pas.
#
# LE CONTROLE POSITIF : appliquer le critere DANS la zone labellisee. S il n y flambe pas, l absence ailleurs ne
# veut rien dire.
#
# LA SENSIBILITE AU SEUIL : le compte est fait a un remplissage de 53,4 %. Si un autre seuil en revele dix fois
# plus, la recherche etait simplement trop severe et la conclusion « il n y a rien » etait une conclusion sur le
# seuil, pas sur le rouleau.
#
# usage: critere_controle.py
import os, numpy as np, tifffile, zarr
from scipy import ndimage

H = '/home/slusarska_holding/vesuvius'
SEGS = (('segB', 'auto_grown_20260220174252405'), ('segA', 'auto_grown_20260220144552896'))
COTE = (900, 3000)          # plus grand cote, px pleine resolution ; les 5 vraies lettres : 1 368 a 2 128
OCC = (0.20, 0.55)          # occupation de la boite ; les 5 vraies : 36 % de mediane ; un disque : 79 %


def formes(m):
    """(nombre d objets, nombre qui passent le critere de forme de lettre)"""
    lab, n = ndimage.label(m)
    ok = 0
    for i, sl in enumerate(ndimage.find_objects(lab), 1):
        c = (lab[sl] == i)
        if c.sum() < 50:
            continue
        if COTE[0] <= max(c.shape) * 8 <= COTE[1] and OCC[0] <= c.sum() / (c.shape[0] * c.shape[1]) <= OCC[1]:
            ok += 1
    return n, ok


for seg, lab in SEGS:
    D = '%s/ink-dataset/841/canon_autres/%s' % (H, lab)
    L = np.asarray(zarr.open('%s/inklabels.zarr' % D, mode='r')['3'][:]).squeeze()
    if L.ndim == 3:
        L = L.any(axis=0)
    L = L > 0
    a = tifffile.imread('%s/pred.tif' % D)[::8, ::8].astype(np.float32)
    k = (min(a.shape[0], L.shape[0]), min(a.shape[1], L.shape[1]))
    a, L = a[:k[0], :k[1]], L[:k[0], :k[1]]
    dans = ndimage.binary_dilation(L, iterations=40)      # la zone labellisee et son voisinage
    nlet = ndimage.label(L)[1]
    print('=== %s : %d lettre(s) labellisee(s), feuille %s au niveau 3' % (seg, nlet, a.shape))
    print('%9s %7s %9s %26s %26s' % ('remplis.', 'seuil', 'marque', 'DANS la zone labellisee', 'HORS zone labellisee'))
    for cible in (0.30, 0.40, 0.534, 0.70, 0.85, 0.95):
        v = np.unique(np.round(a[L])); s, e = v[0], 1e9
        for t in v:
            d = abs(float((a[L] >= t).mean()) - cible)
            if d < e:
                s, e = t, d
        m = a >= s
        nd, od = formes(m & dans)
        nh, oh = formes(m & ~dans)
        print('%8.1f %% %7.0f %8.2f %% %10d objets %6d formes %10d objets %6d formes'
              % (100 * float((a[L] >= s).mean()), s, 100 * m.mean(), nd, od, nh, oh))
    print()
