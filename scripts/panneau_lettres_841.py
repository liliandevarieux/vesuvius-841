# PR-39 / PR-44 : regarder la FORME des lettres de 841 carte par carte, lettre par lettre (regle du projet : l auteur
# regarde avant tout lecteur). Une ligne par lettre etiquetee (composante dans la supervision, meme selection que
# eval_forme.py : cote >= 150 px au niveau 2) ; une colonne par carte, plus le trace humain en premiere colonne.
# Chaque carte est ramenee sur la grille des etiquettes niveau 2 (comme eval_forme.py) ; contraste 1-99,5 % par case.
# usage : panneau_lettres_841.py SEGMENT SORTIE.png TITRE1=CARTE1.tif [TITRE2=CARTE2.tif ...]
import sys, numpy as np, tifffile, zarr
from scipy import ndimage
from PIL import Image, ImageDraw

S = '/home/slusarska_holding/vesuvius/ft12m/src/' + sys.argv[1]


def niv2(n):
    a = np.asarray(zarr.open('%s/%s.zarr' % (S, n), mode='r')['2'][:]).squeeze()
    return (a.any(axis=0) if a.ndim == 3 else a) > 0


L = niv2('inklabels') & niv2('supervision')
lab, n = ndimage.label(L)
objs = [(k + 1, s) for k, s in enumerate(ndimage.find_objects(lab)) if max(s[0].stop - s[0].start, s[1].stop - s[1].start) >= 150]
cartes = []
for arg in sys.argv[3:]:
    titre, f = arg.split('=', 1)
    P = tifffile.imread(f).astype(np.float32)
    if P.ndim == 3:
        P = P[0] if P.shape[0] < P.shape[-1] else P[..., 0]
    G = ndimage.zoom(P, (L.shape[0] / P.shape[0], L.shape[1] / P.shape[1]), order=1)[:L.shape[0], :L.shape[1]]
    cartes.append((titre, G))
T, M = 220, 40                                             # taille d une case, marge autour de la lettre (px niveau 2)
cols = ['trace humain'] + [t for t, _ in cartes]
img = Image.new('L', (T * len(cols), 24 + T * len(objs)), 255)
d = ImageDraw.Draw(img)
for j, c in enumerate(cols):
    d.text((j * T + 6, 6), c, fill=0)
for i, (k, s) in enumerate(objs):
    y0, y1 = max(0, s[0].start - M), min(L.shape[0], s[0].stop + M)
    x0, x1 = max(0, s[1].start - M), min(L.shape[1], s[1].stop + M)
    h, w = y1 - y0, x1 - x0
    r = T / max(h, w)
    cases = [(lab[y0:y1, x0:x1] == k).astype(np.float32) * 255] + [G[y0:y1, x0:x1] for _, G in cartes]
    for j, a in enumerate(cases):
        lo, hi = np.percentile(a, [1, 99.5]) if j else (0, 255)
        b = np.clip((a - lo) / max(hi - lo, 1e-6) * 255, 0, 255).astype(np.uint8)
        im = Image.fromarray(b).resize((max(1, int(w * r)), max(1, int(h * r))), Image.BILINEAR)
        img.paste(im, (j * T + (T - im.width) // 2, 24 + i * T + (T - im.height) // 2))
    d.text((4, 24 + i * T + 4), 'lettre %d' % (i + 1), fill=128)
img.save(sys.argv[2])
print(sys.argv[2], len(objs), 'lettres x', len(cols), 'colonnes')
