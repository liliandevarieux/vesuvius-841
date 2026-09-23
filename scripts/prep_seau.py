# Prepare le test « le sens appartient-il au TABLEAU ou au SEGMENT ? » (question d AndreasHad04, issue #1867).
# Notre modele a ete entraine sur le rendu 65 plans 4,681 um de w00 pris dans son ordre stocke. Si le sens appartient
# au tableau, il doit lire le rendu 65 plans du MEME seau pour ag174 en ordre stocke lui aussi — alors qu il fallait
# retourner le volume de surface publie 109 plans 2,403 um du meme segment. Ici on choisit les fenetres de test sur le
# canevas du seau (different de celui du volume publie : 14268x19413 contre 14660x19100) et on liste les chunks.
# usage: prep_seau.py <racine locale> <nb fenetres=2>
import sys, os, json, numpy as np, tifffile
racine = sys.argv[1]; NF = int(sys.argv[2]) if len(sys.argv) > 2 else 2
za = json.load(open(f'{racine}/0/.zarray')); Z, HH, WW = za['shape']; cz, cy, cx = za['chunks']
L = tifffile.imread(f'{racine}/labels_v2.tif') > 0
S = tifffile.imread(f'{racine}/supervision_v2.tif') > 0
n = min(L.shape[0], S.shape[0], HH), min(L.shape[1], S.shape[1], WW)
L, S = L[:n[0], :n[1]], S[:n[0], :n[1]]
print(f'seau : volume {Z}x{HH}x{WW}, chunks {cz}x{cy}x{cx} ; labels {100*L.mean():.2f} % ; inspecte {100*S.mean():.2f} %')
P = 1500; pas = 500; best = []
d = L[::8, ::8]
for y in range(0, n[0] - P, pas):
    for x in range(0, n[1] - P, pas):
        v = d[y//8:(y+P)//8, x//8:(x+P)//8].mean()
        if v > 0.05: best.append((v, y, x))
best.sort(reverse=True)
pris = []
for v, y, x in best:
    if all(abs(y - a) > P or abs(x - b) > P for a, b in pris): pris.append((y, x))
    if len(pris) == NF: break
fen = [(y, y + P, x, x + P) for y, x in pris]
open(f'{racine}/fenetres.txt', 'w').write('\n'.join(f'{a} {b} {c} {d_}' for a, b, c, d_ in fen) + '\n')
ch = set()
for Y0, Y1, X0, X1 in fen:
    for a in range((Y0 - 128) // cy, (Y1 + 128) // cy + 1):
        for b in range((X0 - 128) // cx, (X1 + 128) // cx + 1):
            if 0 <= a < -(-HH // cy) and 0 <= b < -(-WW // cx): ch.add((a, b))
open(f'{racine}/chunks.txt', 'w').write('\n'.join(f'{a} {b}' for a, b in sorted(ch)) + '\n')
for i, f in enumerate(fen, 1): print(f'  fenetre {i} : Y {f[0]}-{f[1]} X {f[2]}-{f[3]}')
print(f'{len(ch)} chunks a prendre = {len(ch)*cz*cy*cx/1048576:.0f} Mo')
