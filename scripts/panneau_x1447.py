# Exploratoire (pas un test inscrit) : cartes de 1447 sur la fenetre fixee le 28/09 a 13:38:23 avant tout calcul
# (lignes 340-2340, colonnes 220-3220 du segment 20250702235910, centre = point annonce le 24/09 par les organisateurs).
# Sens des couches choisi sans etiquette (sens p99-p50 le plus haut), contraste 1-99,5 %, reduction x0,25, grille rouge
# 8 x 5 de PR-47 ; une carte par bandeau, nom du modele ecrit (ce panneau n est pas pour un lecteur a l aveugle).
# usage : panneau_x1447.py SORTIE.png NOM=carte.tif [...]
import sys, numpy as np, tifffile
from PIL import Image, ImageDraw, ImageFont

Y0, Y1, X0, X1, R, M = 340, 2340, 220, 3220, 0.25, 30
try:
    F = ImageFont.load_default(size=20)
except TypeError:
    F = ImageFont.load_default()


def charge(f):
    P = tifffile.imread(f).astype(np.float32)
    return P[0] if P.ndim == 3 and P.shape[0] < P.shape[-1] else (P[..., 0] if P.ndim == 3 else P)


bandes = []
for arg in sys.argv[2:]:
    nom, f = arg.split('=')
    choix = []
    for g in (f, f.replace('.tif', '_reverse.tif')):
        P = charge(g)
        v = P[P > 0]
        choix.append((np.percentile(v, 99) - np.percentile(v, 50), g, P))
    s, g, P = max(choix, key=lambda c: c[0])
    print('%-9s sens %s (p99-p50 : %s)' % (nom, 'inverse' if g.endswith('_reverse.tif') else 'direct',
                                          ' / '.join('%.1f' % c[0] for c in choix)))
    a = P[Y0:Y1, X0:X1]
    lo, hi = np.percentile(a, [1, 99.5])
    b = np.clip((a - lo) / max(hi - lo, 1e-6) * 255, 0, 255).astype(np.uint8)
    im = Image.fromarray(b).resize((int(b.shape[1] * R), int(b.shape[0] * R)), Image.BILINEAR).convert('RGB')
    d = ImageDraw.Draw(im)
    for j in range(9):
        x = int(j * 375 * R)
        d.line([(x, 0), (x, im.height)], fill=(255, 60, 60), width=1)
    for i in range(6):
        y = int(i * 400 * R)
        d.line([(0, y), (im.width, y)], fill=(255, 60, 60), width=1)
    bandes.append((nom, im))
W = max(im.width for _, im in bandes) + M
out = Image.new('RGB', (W, sum(im.height + M for _, im in bandes)), (255, 255, 255))
d = ImageDraw.Draw(out)
y = 0
for nom, im in bandes:
    d.text((M, y + 4), nom, fill=(0, 0, 0), font=F)
    out.paste(im, (M, y + M))
    y += im.height + M
out.save(sys.argv[1])
print(sys.argv[1], out.size)
