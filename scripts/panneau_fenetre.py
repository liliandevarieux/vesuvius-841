# Panneau de lecture a l aveugle au format de PR-47, pour une fenetre quelconque d une carte : contraste 1-99,5 %,
# reduction x0,5, grille rouge 8 colonnes (A-H) x 5 rangees (1-5) qui partage la fenetre en parts egales, reperes en
# marge, aucun nom de modele. Sens des couches choisi sans etiquette (p99-p50 sur le papyrus, comme eval_sup.py).
# usage : panneau_fenetre.py CARTE.tif SORTIE.png Y0 Y1 X0 X1
import sys, numpy as np, tifffile
from PIL import Image, ImageDraw, ImageFont

R, M = 0.5, 40
try:
    F = ImageFont.load_default(size=24)
except TypeError:
    F = ImageFont.load_default()


def charge(f):
    P = tifffile.imread(f).astype(np.float32)
    return P[0] if P.ndim == 3 and P.shape[0] < P.shape[-1] else (P[..., 0] if P.ndim == 3 else P)


choix = []
for g in (sys.argv[1], sys.argv[1].replace('.tif', '_reverse.tif')):
    P = charge(g)
    v = P[P > 0]
    choix.append((np.percentile(v, 99) - np.percentile(v, 50), g, P))
s, g, P = max(choix, key=lambda c: c[0])
Y0, Y1, X0, X1 = (int(x) for x in sys.argv[3:7])
CW, RH = (X1 - X0) / 8, (Y1 - Y0) / 5
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
print(sys.argv[2], out.size, 'sens', 'inverse' if g.endswith('_reverse.tif') else 'direct',
      '(p99-p50 %s)' % ' / '.join('%.1f' % c[0] for c in choix))
