# Controle du biais de selection de verdict_ligne.py. Ce dernier compare les taches DE LA LIGNE aux labels certains et
# les trouve plus contrastees (69,4 contre 47,7) -- mais les 117 candidates ont ete RETENUES parce que le lecteur qui
# les a trouvees les voyait : blobs_seg.py les tire de la prediction publiee par les organisateurs, seuillee. (Corrige
# le 23/09 a 17:00 : ce commentaire disait "les deux lecteurs", c est faux, le recensement a deux lecteurs est
# cand_plein.py et il en rend 2, pas 117. Le biais de selection, lui, est le meme.)
# Elles partent donc gagnantes par construction, et la comparaison ne prouve rien.
# Le controle juste compare les candidates SUR la ligne aux candidates HORS de la ligne : meme selection des deux
# cotes, seule la position change. Si les deux groupes se valent, la ligne n apporte rien de plus que la selection.
# usage: verdict_ligne2.py <dossier_labels>
import sys, numpy as np, zarr, tifffile
from scipy import ndimage
lab = sys.argv[1]
H = '/home/slusarska_holding/vesuvius'; D = f'{H}/ink-dataset/841/canon_autres/{lab}'; R = 8
A = tifffile.imread(f'{H}/predictions/b841_human7n_feuille.tif')
P = tifffile.imread(f'{D}/pred.tif')
L = np.asarray(zarr.open(f'{D}/inklabels.zarr', mode='r')['0'][:]) > 0
S8 = np.asarray(zarr.open(f'{D}/supervision.zarr', mode='r')['3'][:]) > 0
L8 = np.asarray(zarr.open(f'{D}/inklabels.zarr', mode='r')['3'][:]) > 0
P8 = P[::R, ::R]
n = [min(P8.shape[0], S8.shape[0], L8.shape[0]), min(P8.shape[1], S8.shape[1], L8.shape[1])]
T = float(np.percentile(P8[:n[0], :n[1]][S8[:n[0], :n[1]]], 100 * (1 - L8[:n[0], :n[1]][S8[:n[0], :n[1]]].mean())))
a, b = 6526.0, 0.1643
cand = [tuple(map(int, map(float, l.split()))) for l in open(f'/home/slusarska_holding/cand_{lab}.txt') if l.strip()]


def mesure(cy, cx):
    """Ecart de notre modele entre la tache et un ruban de 8 a 60 px autour -- protocole de verdict_ligne.py."""
    y0, x0 = max(0, cy - 1200), max(0, cx - 1200)
    q = P[y0:y0 + 2400, x0:x0 + 2400]; m = q >= T
    lb, nn = ndimage.label(m)
    if nn == 0:
        return None
    k = lb[min(1200, q.shape[0] - 1), min(1200, q.shape[1] - 1)]
    if k == 0:
        k = int(np.argmax(ndimage.sum(m, lb, range(1, nn + 1)))) + 1
    blob = lb == k
    ring = ndimage.binary_dilation(blob, iterations=60) & ~ndimage.binary_dilation(blob, iterations=8)
    w = A[y0:y0 + blob.shape[0], x0:x0 + blob.shape[1]].astype(np.float32)
    if w.shape != blob.shape or blob.sum() < 2000:
        return None
    return float(w[blob].mean()) - float(w[ring[:w.shape[0], :w.shape[1]]].mean())


groupes = {'sur la ligne (< 700 px)': [], 'hors ligne (>= 700 px)': []}
aires = {k: [] for k in groupes}
for cy, cx, ar in cand:
    g = 'sur la ligne (< 700 px)' if abs(cy - (a + b * cx)) < 700 else 'hors ligne (>= 700 px)'
    v = mesure(cy, cx)
    if v is not None:
        groupes[g].append(v); aires[g].append(ar)

print(f'{"groupe":>24s} | {"n":>3s} | {"ecart moyen":>11s} {"mediane":>8s} {"ecart-type":>10s} | {"aire moy Mpx":>12s}')
for g, v in groupes.items():
    if v:
        print(f'{g:>24s} | {len(v):3d} | {np.mean(v):11.1f} {np.median(v):8.1f} {np.std(v):10.1f} | '
              f'{np.mean(aires[g]) / 1e6:12.2f}')

# temoin historique : les labels certains, qui eux n ont pas ete selectionnes par les deux lecteurs
lbl, nl = ndimage.label(L)
tem = []
for k in np.argsort(ndimage.sum(L, lbl, range(1, nl + 1)))[::-1][:6]:
    sl = ndimage.find_objects(lbl)[k]
    blob = lbl[sl] == k + 1
    ring = ndimage.binary_dilation(blob, iterations=60) & ~ndimage.binary_dilation(blob, iterations=8)
    w = A[sl].astype(np.float32)
    if w.shape == blob.shape:
        tem.append(float(w[blob].mean()) - float(w[ring].mean()))
if tem:
    print(f'{"labels certains (non selectionnes)":>24.24s} | {len(tem):3d} | {np.mean(tem):11.1f} '
          f'{np.median(tem):8.1f} {np.std(tem):10.1f} |')

s, h = groupes['sur la ligne (< 700 px)'], groupes['hors ligne (>= 700 px)']
if s and h:
    d = np.mean(s) - np.mean(h)
    se = (np.std(s) ** 2 / len(s) + np.std(h) ** 2 / len(h)) ** 0.5
    print(f'\ndifference ligne - hors ligne : {d:+.1f}, erreur type {se:.1f} ({abs(d) / se:.1f} ecarts types)')
    print('Lecture : les deux groupes ont subi LA MEME selection (vus par les deux lecteurs). Si la difference')
    print('tient dans l erreur type, la ligne n apporte rien de plus que la selection, et la seule preuve')
    print('qui reste pour la ligne est geometrique : trois taches alignees a 9,3 deg contre 8,0 mesures.')
