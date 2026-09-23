# Piles Fiji des candidates du recensement a deux lecteurs sur TOUTE la feuille (cand_plein.py). Difference avec
# piles_cand.py : les fenetres viennent de fenetres_<loc>c2.txt, et l indice montre trois panneaux — le scan brut, la
# prediction publiee des organisateurs, et la notre recousue sur tout le segment.
# usage: piles_cand2.py <nom_local b841|a841> <source_brute segB|segA> <dossier_labels> <prefixe_sortie>
import sys, os, numpy as np, zarr, tifffile
from PIL import Image, ImageDraw
loc, brut, lab, pre = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
H = '/home/slusarska_holding/vesuvius'; D = f'{H}/ink-dataset/841/canon_autres/{lab}'
vol = zarr.open(f'{H}/ink-dataset/841/{brut}/{brut}.zarr/0', mode='r')
P = tifffile.imread(f'{D}/pred.tif')
A = tifffile.imread(f'{H}/predictions/{loc}_human7n_plein.tif')
wins = [tuple(map(int, l.split())) for l in open(f'/home/slusarska_holding/fenetres_{loc}c2.txt')]
PILES = f'/mnt/c/Users/SLUSARSKA HOLDING/vesuvius_arbitrage/{pre}'
IMG = f'/mnt/c/Users/SLUSARSKA HOLDING/vesuvius/images/arbitrage/{pre}'
os.makedirs(PILES, exist_ok=True); os.makedirs(IMG, exist_ok=True)
T = 640; lignes = []
for k, (Y0, Y1, X0, X1) in enumerate(wins, 1):
    cy, cx = (Y0 + Y1) // 2, (X0 + X1) // 2
    y0, x0 = max(0, cy - T // 2), max(0, cx - T // 2)
    y1, x1 = min(y0 + T, vol.shape[1]), min(x0 + T, vol.shape[2])
    pile = np.asarray(vol[:, y0:y1, x0:x1])
    if pile.max() == 0: print(f'c{k:02d} : volume absent, saute'); continue
    tifffile.imwrite(f'{PILES}/{pre}_c{k:02d}_pile.tif', pile, imagej=True, metadata={'axes': 'ZYX'})
    q = P[y0:y1, x0:x1].astype(np.uint8); a = A[y0:y1, x0:x1].astype(np.uint8)
    m = np.asarray(pile[pile.shape[0] // 2]).astype(np.float32)
    lo, hi = np.percentile(m, [1, 99]); sc = np.clip((m - lo) / max(hi - lo, 1) * 255, 0, 255).astype(np.uint8)
    pans = [('scan (couche 54 sur 109)', sc), ('lecteur 1 : les organisateurs', q), ('lecteur 2 : notre modele', a)]
    W = 380; out = Image.new('RGB', (3 * (W + 8), W + 34), (20, 20, 20)); dr = ImageDraw.Draw(out)
    for j, (t, im) in enumerate(pans):
        out.paste(Image.fromarray(np.stack([im] * 3, -1)).resize((W, W)), (j * (W + 8), 28))
        dr.text((j * (W + 8) + 4, 8), t, fill=(255, 255, 0))
    out.save(f'{IMG}/{pre}_c{k:02d}_indice.png')
    lignes.append((k, y0, x0))
    print(f'c{k:02d} : Y {y0}-{y1} X {x0}-{x1}, pile {pile.shape}')
with open(f'{IMG}/{pre}_reponses.txt', 'w') as f:
    f.write("Candidates du recensement sur TOUTE la feuille : taches de taille de lettre, hors des labels des\n")
    f.write("organisateurs, et vues par les DEUX lecteurs independants (leur prediction publiee et la notre).\n")
    f.write("La plupart sont dans la partie du segment que personne n'a jamais inspectee ni labellisee.\n\n")
    f.write("ATTENTION : 109 couches, dans l'ordre publie (non inverse). La couche du feuillet varie d'un endroit\n")
    f.write("a l'autre du segment : Lilian a mesure 37, 37, 40 et 47 sur les 4 encres sures du lot precedent.\n")
    f.write("Balaye toute la pile et note la couche ou c'est le plus net.\n\n")
    f.write("Question : est-ce de l'encre ? Trois reponses : « encre sure » / « pas d'encre » / « je ne sais pas ».\n")
    f.write("Deuxieme question, facultative : est-ce que tu y lis une lettre ? Laquelle ?\n\n")
    for k, y0, x0 in lignes:
        f.write(f'c{k:02d}  (Y {y0} X {x0}) : ................  couche : ......  lettre ? : ......\n')
print(f'\n{len(lignes)} piles : {PILES}\nindices + reponses : {IMG}')
