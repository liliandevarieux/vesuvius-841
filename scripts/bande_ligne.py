# Extrait la BANDE suivant une ligne de texte, sur toute la largeur du feuillet, a l echelle ou une lettre se lit.
# On ne fait pas tourner l image : pour chaque colonne on prend les lignes centrees sur y = a + b*x, ce qui redresse
# exactement et sans interpolation. Coupee en morceaux empiles, du gauche vers la droite.
# usage: bande_ligne.py <dossier_labels> <Y1> <X1> <Y2> <X2> <sortie.png>   env HB=900 (demi-hauteur) RED=2 MORC=2000 XMIN XMAX PRED
import sys, os, numpy as np, zarr, tifffile
from PIL import Image, ImageDraw
from scipy import ndimage
lab = sys.argv[1]; Y1, X1, Y2, X2 = map(int, sys.argv[2:6]); out = sys.argv[6]
HH = int(os.environ.get('HB', 900))          # HB et non H : H sert deja au chemin du projet dans les scripts shell; RED = int(os.environ.get('RED', 2)); MORC = int(os.environ.get('MORC', 2000))
H = '/home/slusarska_holding/vesuvius'; D = f'{H}/ink-dataset/841/canon_autres/{lab}'
# PRED= : lire une autre prediction que celle des organisateurs (la notre, pour comparer les deux lecteurs
# sur exactement la meme ligne et la meme geometrie)
P = tifffile.imread(os.environ.get('PRED', f'{D}/pred.tif')).astype(np.float32)
L = np.asarray(zarr.open(f'{D}/inklabels.zarr', mode='r')['0'][:]) > 0
V8 = np.asarray(zarr.open(f'{D}/validation.zarr', mode='r')['3'][:]) > 0
b = (Y2 - Y1) / max(X2 - X1, 1); a = Y1 - b * X1
print(f'ligne : y = {a:.0f} + {b:.4f} x  (angle {np.degrees(np.arctan(b)):+.2f} deg)')
cols = np.nonzero(V8.any(0))[0] * 8
XA, XB = int(cols.min()), int(cols.max())
# XMIN / XMAX : se limiter a la partie qui porte du texte (le reste du feuillet est vide et gaspille des morceaux)
XA = max(XA, int(os.environ.get('XMIN', XA))); XB = min(XB, int(os.environ.get('XMAX', XB)))
W = XB - XA
bande = np.zeros((2 * HH, W), np.float32); mlab = np.zeros((2 * HH, W), bool)
for j, x in enumerate(range(XA, XB)):
    y0 = int(round(a + b * x)) - HH
    ya, yb = max(0, y0), min(P.shape[0], y0 + 2 * HH)
    if yb <= ya: continue
    bande[ya - y0:yb - y0, j] = P[ya:yb, x]
    mlab[ya - y0:yb - y0, j] = L[ya:yb, x]
bande = bande[:, ::RED][::RED]; mlab = mlab[:, ::RED][::RED]
v = bande[bande > 0]
lo, hi = np.percentile(v, [2, 99.5]) if v.size else (0, 255)
g = np.clip((bande - lo) / max(hi - lo, 1) * 255, 0, 255).astype(np.uint8)
c = np.stack([g] * 3, -1)
bord = mlab & ~ndimage.binary_erosion(mlab, iterations=2)
c[bord] = (255, 60, 60)
nm = -(-c.shape[1] // MORC); TT = 22
o = Image.new('RGB', (MORC, nm * (c.shape[0] + TT) + 26), (12, 12, 12)); dr = ImageDraw.Draw(o)
dr.text((6, 6), f'{lab} — bande suivant la ligne, gauche vers droite, {nm} morceaux ; rouge = deja labellise ; '
                f'1 px = {19*RED/2:.0f} um, une lettre fait ~{1000//RED} px', fill=(255, 255, 0))
for i in range(nm):
    seg = c[:, i * MORC:(i + 1) * MORC]
    im = Image.new('RGB', (MORC, c.shape[0]), (12, 12, 12))
    im.paste(Image.fromarray(seg), (0, 0))
    y = 26 + i * (c.shape[0] + TT)
    dr.text((6, y), f'morceau {i+1}/{nm} — X {XA + i*MORC*RED} a {XA + (i+1)*MORC*RED}', fill=(120, 220, 255))
    o.paste(im, (0, y + TT))
    for xk in range(0, MORC, 1000 // RED):                 # un repere par millier de px pleins = une lettre
        xr = XA + (i * MORC + xk) * RED
        dr.line([(xk, y + TT), (xk, y + TT + 14)], fill=(255, 200, 0), width=2)
        dr.text((xk + 3, y + TT + 2), str(xr), fill=(255, 200, 0))
o.save(out); print('bande', out, o.size)
