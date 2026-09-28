# PR-47 : une fenetre de texte par carte sur 0009B (lignes 4800-6700, colonnes 1600-4800 de la carte 8,64 um : les deux
# lignes des dix lettres etiquetees et toute la zone supervisee), contraste 1-99,5 %, grille rouge 8 colonnes (A-H,
# 400 px) x 5 rangees (1-5, 380 px), sans trace ni nom de modele. Le lecteur cherche et nomme les lettres.
# Image a mi-resolution (1 600 x 950 px de carte, plus la marge des reperes).
# usage : panneau_pr47.py CARTE.tif SORTIE.png
import sys, numpy as np, tifffile
from PIL import Image, ImageDraw, ImageFont

Y0, Y1, X0, X1, CW, RH, R, M = 4800, 6700, 1600, 4800, 400, 380, 0.5, 40
try:
    F = ImageFont.load_default(size=24)
except TypeError:
    F = ImageFont.load_default()
P = tifffile.imread(sys.argv[1]).astype(np.float32)
if P.ndim == 3:
    P = P[0] if P.shape[0] < P.shape[-1] else P[..., 0]
a = P[Y0:Y1, X0:X1]
lo, hi = np.percentile(a, [1, 99.5])
b = np.clip((a - lo) / max(hi - lo, 1e-6) * 255, 0, 255).astype(np.uint8)
im = Image.fromarray(b).resize((int(b.shape[1] * R), int(b.shape[0] * R)), Image.BILINEAR).convert('RGB')
out = Image.new('RGB', (im.width + M, im.height + M), (255, 255, 255))
out.paste(im, (M, M))
d = ImageDraw.Draw(out)
for j in range(9):
    x = M + int(j * CW * R)
    d.line([(x, M), (x, M + im.height)], fill=(255, 60, 60), width=1)
for i in range(6):
    y = M + int(i * RH * R)
    d.line([(M, y), (M + im.width, y)], fill=(255, 60, 60), width=1)
for j in range(8):
    d.text((M + int((j + 0.5) * CW * R) - 7, 6), 'ABCDEFGH'[j], fill=(0, 0, 0), font=F)
for i in range(5):
    d.text((12, M + int((i + 0.5) * RH * R) - 13), str(i + 1), fill=(0, 0, 0), font=F)
out.save(sys.argv[2])
print(sys.argv[2], out.size)
