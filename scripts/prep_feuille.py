# Liste les chunks du volume couvrant TOUTE la feuille d un segment (validation.zarr = masque de feuillet), moins ceux
# deja pris pour la zone inspectee. C est la partie du segment que personne n a labellisee ni inspectee : 91 % de segB.
# Ecrit aussi le pavage d inference restreint a la feuille. usage: prep_feuille.py <nom_local> <dossier_labels>
import sys, os, numpy as np, zarr
from scipy import ndimage
loc, lab = sys.argv[1], sys.argv[2]
H = '/home/slusarska_holding/vesuvius'; C = f'{H}/ink-dataset/841/canon_autres/{lab}'
g = lambda k: np.asarray(zarr.open(f'{C}/{k}.zarr', mode='r')['3'][:]) > 0
S, V = g('supervision'), g('validation')
n = min(S.shape[0], V.shape[0]), min(S.shape[1], V.shape[1]); S, V = S[:n[0], :n[1]], V[:n[0], :n[1]]
deja = set()
for a, b in zip(*[x * 8 // 128 for x in np.nonzero(ndimage.binary_dilation(S, iterations=2))]):
    for da in (-1, 0, 1):
        for db in (-1, 0, 1): deja.add((a + da, b + db))
feuille = set(zip(*[x * 8 // 128 for x in np.nonzero(V)]))
neuf = sorted(feuille - deja)
open(f'/home/slusarska_holding/chunks_{loc}feuille.txt', 'w').write('\n'.join(f'{a} {b}' for a, b in neuf) + '\n')
print(f'{loc} : feuille {V.sum()*64/1e6:.0f} Mpx, inspectee par eux {100*S.sum()/V.sum():.0f} % ; '
      f'{len(neuf)} chunks a prendre = {len(neuf)*109*128*128/1073741824:.1f} Go')
# pavage d inference : pavés de 1400 px avec 100 px de recouvrement, gardes s ils touchent la feuille
ys, xs = np.nonzero(V); Y0, Y1, X0, X1 = ys.min()*8, (ys.max()+1)*8, xs.min()*8, (xs.max()+1)*8
P, R = 1400, 100; f = []
for y in range(Y0, Y1, P - R):
    for x in range(X0, X1, P - R):
        y2, x2 = min(y + P, Y1), min(x + P, X1)
        if y2 - y < 200 or x2 - x < 200: continue
        if V[y//8:y2//8, x//8:x2//8].mean() < 0.15: continue
        f.append((y, y2, x, x2))
open(f'/home/slusarska_holding/fenetres_{loc}_feuille.txt', 'w').write('\n'.join(f'{a} {b} {c} {d}' for a, b, c, d in f) + '\n')
print(f'{loc} : {len(f)} paves de 1400 px couvrant la feuille (~{len(f)*55/60:.0f} min d inference)')
