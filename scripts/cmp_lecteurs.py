# Les deux lecteurs cote a cote sur la MEME zone, chacun avec son propre etalement de contraste (percentiles 2/98
# calcules dans la zone lue, pas sur toute la toile : notre prediction ne couvre que 9 % du segment, un contraste
# global l ecrase). Rouge = labels des organisateurs. usage: cmp_lecteurs.py <loc> <dossier_labels> <sortie.png>
import sys, numpy as np, zarr, tifffile
from PIL import Image, ImageDraw
from scipy import ndimage
loc, lab, out = sys.argv[1], sys.argv[2], sys.argv[3]
H = '/home/slusarska_holding/vesuvius'; D = f'{H}/ink-dataset/841/canon_autres/{lab}'
L8 = np.asarray(zarr.open(f'{D}/inklabels.zarr', mode='r')['3'][:]) > 0
ys, xs = np.nonzero(L8); M = 25
Y0, Y1 = max(0, ys.min() - M) * 8, (ys.max() + M) * 8
X0, X1 = max(0, xs.min() - M) * 8, (xs.max() + M) * 8
print(f'zone des labels : Y {Y0}-{Y1} X {X0}-{X1} ({(Y1-Y0)}x{(X1-X0)} px)')
R = 4
def prep(p, nom):
    a = tifffile.imread(p)[Y0:Y1, X0:X1][::R, ::R].astype(np.float32)
    v = a[a > 0]
    if v.size == 0: return None
    lo, hi = np.percentile(v, [2, 98])
    print(f'  {nom} : lu sur {100*(a>0).mean():.0f} % de la zone, etalement {lo:.0f}-{hi:.0f}')
    return np.clip((a - lo) / max(hi - lo, 1) * 255, 0, 255).astype(np.uint8)
im1 = prep(f'{D}/pred.tif', 'organisateurs')
im2 = prep(f'{H}/predictions/{loc}_human7n_plein.tif', 'nous')
Lc = np.asarray(zarr.open(f'{D}/inklabels.zarr', mode='r')['0'][Y0:Y1, X0:X1])[::R, ::R] > 0
bord = Lc & ~ndimage.binary_erosion(Lc, iterations=2)
def colore(im):
    c = np.stack([im] * 3, -1); c[bord[:im.shape[0], :im.shape[1]]] = (255, 40, 40); return c
LARG = 1500
def redim(c):
    i = Image.fromarray(c); return i.resize((LARG, int(i.height * LARG / i.width)), Image.LANCZOS)
a, b = redim(colore(im1)), redim(colore(im2))
ANG = 8.0
a, b = a.rotate(-ANG, expand=True, resample=Image.BICUBIC), b.rotate(-ANG, expand=True, resample=Image.BICUBIC)
titre = 26
o = Image.new('RGB', (a.width, a.height + b.height + 3 * titre), (15, 15, 15)); dr = ImageDraw.Draw(o)
dr.text((6, 6), f'{loc} - la MEME zone lue par les deux lecteurs, chacun avec son propre contraste ; rouge = labels des organisateurs', fill=(255, 255, 0))
dr.text((6, titre), 'LECTEUR 1 : prediction publiee par les organisateurs', fill=(120, 220, 255)); o.paste(a, (0, titre + 18))
dr.text((6, titre + 18 + a.height + 4), 'LECTEUR 2 : notre modele (entraine sur w00 seul, ne connait pas ce segment)', fill=(120, 255, 160))
o.paste(b, (0, titre + 18 + a.height + titre))
o.save(out); print('image', out, o.size)
