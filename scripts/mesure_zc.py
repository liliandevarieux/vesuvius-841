# Quelle tranche de profondeur notre modele lit-il le mieux ? Meme modele, meme fenetre, on ne change que
# les 65 couches prises dans le volume de 109. Juge : les labels des organisateurs + leur prediction publiee.
# usage: mesure_zc.py <nom_local> <dossier_labels> <no_fenetre> <fichier_fenetres> <etiquette...>
import sys, numpy as np, zarr, tifffile
from scipy import ndimage
loc, lab, k, fw = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
H = '/home/slusarska_holding/vesuvius'; D = f'{H}/ink-dataset/841/canon_autres/{lab}'
L3 = np.asarray(zarr.open(f'{D}/inklabels.zarr', mode='r')['3'][:]) > 0
S3 = np.asarray(zarr.open(f'{D}/supervision.zarr', mode='r')['3'][:]) > 0
P3 = tifffile.imread(f'{D}/pred.tif')[::8, ::8].astype(np.float32)
Y0, Y1, X0, X1 = [tuple(map(int, l.split())) for l in open(fw)][k - 1]
i0, j0 = Y0 // 8, X0 // 8
print(f'{loc} fenetre {k} : Y {Y0}-{Y1} X {X0}-{X1}')
print(f'{"tranche":>12s} | {"encre":>7s} {"fond":>7s} {"ecart":>7s} {"corr":>7s}')
res = []
for tag in sys.argv[5:]:
    try: a = tifffile.imread(f'{H}/predictions/{loc}_zc{tag}_human7n.tif').astype(np.float32)[::8, ::8]
    except FileNotFoundError: print(f'{tag:>12s} | (absent)'); continue
    L = L3[i0:i0 + a.shape[0], j0:j0 + a.shape[1]]; S = S3[i0:i0 + a.shape[0], j0:j0 + a.shape[1]]
    P = P3[i0:i0 + a.shape[0], j0:j0 + a.shape[1]]
    m = [min(x.shape[0] for x in (a, L, S, P)), min(x.shape[1] for x in (a, L, S, P))]
    a, L, S, P = [x[:m[0], :m[1]] for x in (a, L, S, P)]
    if L.sum() < 50: print(f'{tag:>12s} | (pas d encre labellisee dans la fenetre)'); continue
    f = S & ~ndimage.binary_dilation(L, iterations=3)
    e, b = a[L].mean(), a[f].mean(); c = np.corrcoef(a[S].ravel(), P[S].ravel())[0, 1]
    res.append((tag, e - b, c)); print(f'{tag:>12s} | {e:7.1f} {b:7.1f} {e-b:7.1f} {c:7.3f}')
if res:
    best = max(res, key=lambda t: t[1])
    print('')
    print(f'MEILLEURE TRANCHE : {best[0]}  (ecart {best[1]:.1f}, corr {best[2]:.3f})')
    print('Repere w00 : ecart 66 a 90, corr 0,62 a 0,79.')
