# Le second lecteur voit-il les taches de LA LIGNE ? Pour chaque tache de la ligne (celles reperees par blobs_seg.py
# et situees pres de la droite ajustee), on compare la reponse de NOTRE modele dans la tache et dans un ruban de 8 a
# 60 px autour — exactement le protocole de verdict_cand.py, qui avait donne 77 sur les 6 candidates confirmees.
# Temoin obligatoire : la meme mesure sur les labels certains du segment. usage: verdict_ligne.py <dossier_labels>
import sys, numpy as np, zarr, tifffile
from scipy import ndimage
lab = sys.argv[1]
H = '/home/slusarska_holding/vesuvius'; D = f'{H}/ink-dataset/841/canon_autres/{lab}'; R = 8
A = tifffile.imread(f'{H}/predictions/b841_human7n_feuille.tif').astype(np.float32)
P = tifffile.imread(f'{D}/pred.tif').astype(np.float32)
L = np.asarray(zarr.open(f'{D}/inklabels.zarr', mode='r')['0'][:]) > 0
S8 = np.asarray(zarr.open(f'{D}/supervision.zarr', mode='r')['3'][:]) > 0
L8 = np.asarray(zarr.open(f'{D}/inklabels.zarr', mode='r')['3'][:]) > 0
P8 = P[::R, ::R]
n = [min(P8.shape[0], S8.shape[0], L8.shape[0]), min(P8.shape[1], S8.shape[1], L8.shape[1])]
T = float(np.percentile(P8[:n[0], :n[1]][S8[:n[0], :n[1]]], 100 * (1 - L8[:n[0], :n[1]][S8[:n[0], :n[1]]].mean())))
a, b = 6526.0, 0.1643                                   # la droite ajustee sur les trois candidates alignees
cand = [tuple(map(int, map(float, l.split()))) for l in open(f'/home/slusarska_holding/cand_{lab}.txt') if l.strip()]
sur = [(cy, cx, ar) for cy, cx, ar in cand if abs(cy - (a + b * cx)) < 700]
print(f'seuil d encre des organisateurs {T:.0f} ; {len(sur)} taches sur la ligne (ecart < 700 px de la droite)')
print(f'{"tache":>18s} | {"aire Mpx":>8s} | {"nous dedans":>11s} {"autour":>7s} {"ecart":>7s}')
res = []
for cy, cx, ar in sur:
    y0, x0 = max(0, cy - 1200), max(0, cx - 1200)
    q = P[y0:y0 + 2400, x0:x0 + 2400]; m = q >= T
    lb, nn = ndimage.label(m)
    if nn == 0: continue
    k = lb[min(1200, q.shape[0] - 1), min(1200, q.shape[1] - 1)]
    if k == 0:
        ar2 = ndimage.sum(m, lb, range(1, nn + 1)); k = int(np.argmax(ar2)) + 1
    blob = lb == k
    ring = ndimage.binary_dilation(blob, iterations=60) & ~ndimage.binary_dilation(blob, iterations=8)
    w = A[y0:y0 + blob.shape[0], x0:x0 + blob.shape[1]]
    if w.shape != blob.shape or blob.sum() < 2000: continue
    d, o = float(w[blob].mean()), float(w[ring[:w.shape[0], :w.shape[1]]].mean())
    res.append(d - o); print(f'{f"Y{cy} X{cx}":>18s} | {ar/1e6:8.2f} | {d:11.1f} {o:7.1f} {d-o:7.1f}')
# temoin : les memes mesures sur les labels certains
lbl, nl = ndimage.label(L)
tem = []
for k in np.argsort(ndimage.sum(L, lbl, range(1, nl + 1)))[::-1][:6]:
    sl = ndimage.find_objects(lbl)[k]
    blob = lbl[sl] == k + 1
    ring = ndimage.binary_dilation(blob, iterations=60) & ~ndimage.binary_dilation(blob, iterations=8)
    w = A[sl]
    if w.shape != blob.shape: continue
    tem.append(float(w[blob].mean()) - float(w[ring].mean()))
if res: print(f'\nligne   : ecart moyen du second lecteur {np.mean(res):.1f} sur {len(res)} taches')
if tem: print(f'temoin  : ecart moyen sur les labels certains {np.mean(tem):.1f} sur {len(tem)} zones')
if res and tem: print(f'\nLecture : si la ligne est proche du temoin, le second lecteur confirme la ligne.')
