# Triage a l oeil des candidates hors labels d un segment : les N plus grosses, chacune dans sa fenetre, a une echelle
# ou une lettre est lisible. Rendu = la prediction des organisateurs (la meilleure pour LIRE ; la notre sert de juge,
# pas de surface de lecture). Contour orange = la tache retenue. usage: planche_117.py <dossier_labels> <sortie.png>
# env N=24 (nombre de vignettes) COL=6 FEN=900 (taille de la fenetre en px pleins)
import sys, os, numpy as np, zarr, tifffile
from PIL import Image, ImageDraw
from scipy import ndimage
lab, out = sys.argv[1], sys.argv[2]
H = '/home/slusarska_holding/vesuvius'; D = f'{H}/ink-dataset/841/canon_autres/{lab}'
N, COL, FEN = int(os.environ.get('N', 24)), int(os.environ.get('COL', 6)), int(os.environ.get('FEN', 900))
P = tifffile.imread(f'{D}/pred.tif')
L8 = np.asarray(zarr.open(f'{D}/inklabels.zarr', mode='r')['3'][:]) > 0
S8 = np.asarray(zarr.open(f'{D}/supervision.zarr', mode='r')['3'][:]) > 0
P8 = P[::8, ::8].astype(np.float32)
n = min(P8.shape[0], S8.shape[0], L8.shape[0]), min(P8.shape[1], S8.shape[1], L8.shape[1])
P8, S8c, L8c = P8[:n[0], :n[1]], S8[:n[0], :n[1]], L8[:n[0], :n[1]]
# seuil d encre : la densite d encre observee DANS la zone inspectee, appliquee a toute la feuille
T = float(np.percentile(P8[S8c], 100 * (1 - L8c[S8c].mean())))
# LISTE= permet de passer une autre liste de points (par exemple un temoin pris dans les labels connus)
liste = os.environ.get('LISTE', f'/home/slusarska_holding/cand_{lab}.txt')
cand = [tuple(map(int, map(float, l.split()))) for l in open(liste) if l.strip()]
cand = cand[:N]
V = 300                                        # cote d une vignette a l ecran
lig = -(-len(cand) // COL); TT = 20
o = Image.new('RGB', (COL * (V + 6) + 6, lig * (V + TT + 6) + 30), (15, 15, 15)); dr = ImageDraw.Draw(o)
dr.text((6, 8), f'{lab} — les {len(cand)} plus grosses taches de taille de lettre HORS labels, sur la prediction des '
                f'organisateurs. Fenetre {FEN} px (une lettre fait ~1000 px). Orange = la tache.', fill=(255, 255, 0))
for i, (cy, cx, aire) in enumerate(cand):
    y0, x0 = max(0, cy - FEN // 2), max(0, cx - FEN // 2)
    a = P[y0:y0 + FEN, x0:x0 + FEN].astype(np.float32)
    if a.size == 0: continue
    lo, hi = np.percentile(a, [2, 98])
    g = np.clip((a - lo) / max(hi - lo, 1) * 255, 0, 255).astype(np.uint8)
    m = a >= T
    bord = m & ~ndimage.binary_erosion(m, iterations=3)
    c = np.stack([g] * 3, -1); c[bord] = (255, 150, 0)
    im = Image.fromarray(c).resize((V, V), Image.LANCZOS)
    x, y = 6 + (i % COL) * (V + 6), 30 + (i // COL) * (V + TT + 6)
    o.paste(im, (x, y + TT))
    dr.text((x + 2, y + 4), f'{i+1:02d}  {aire/1e6:.2f} Mpx  (Y {cy} X {cx})', fill=(180, 220, 255))
o.save(out); print('planche', out, o.size, f'; seuil d encre {T:.0f}')
