# Accord entre NOTRE prediction et la REFERENCE des organisateurs (modele canonique, tile256_stride128_layers1_63_hann_fwd) sur une region.
# Sorties : <prefixe>_notre.png, <prefixe>_ref.png (meme echelle, a empiler dans Fiji) et <prefixe>_accord.png
# (vert = encre pour les deux, rouge = nous seuls, bleu = reference seule, gris = fond). Imprime IoU, parts d'accord, et la meme chose
# par gros carreaux pour reperer les zones de desaccord. usage: agree.py <pred.tif> <Y0> <Y1> <X0> <X1> <prefixe> [seuil_notre=180] [d=2]
import sys, os, numpy as np, zarr, tifffile
from PIL import Image
pred = sys.argv[1]; Y0, Y1, X0, X1 = map(int, sys.argv[2:6]); outp = sys.argv[6]
thr = int(sys.argv[7]) if len(sys.argv) > 7 else 180; d = int(sys.argv[8]) if len(sys.argv) > 8 else 2
import os; seg = f'/home/slusarska_holding/vesuvius/ink-dataset/{os.environ.get("SCROLL", "phercparis4")}/' + os.environ.get('SEG', 'w00_20231016151002')  # SEG=w02_... autre segment, SCROLL=1667 autre rouleau
def crop_tif(path):
    oy, ox = (map(int, open(path + '.origin').read().split()) if os.path.exists(path + '.origin') else (0, 0))
    with tifffile.TiffFile(path) as tf: return np.asarray(zarr.open(tf.aszarr(), mode='r')[Y0 - oy:Y1 - oy, X0 - ox:X1 - ox])
ours = crop_tif(pred).astype(np.float32); refp = f'{seg}/preds/{os.environ.get("REF", "tile256_stride128_layers1_63_hann_fwd.tif")}'
if os.environ.get('REF', '') == 'none' or not os.path.exists(refp):  # pas de reference : rien a comparer
    print(f'region {Y0}-{Y1}/{X0}-{X1} : pas de reference ({refp})'); print('IoU - | pas de reference'); sys.exit(0)
ref = crop_tif(refp).astype(np.float32)
if ref.max() == 0: print(f'region {Y0}-{Y1}/{X0}-{X1} : reference vide sur la region'); print('IoU - | reference vide'); sys.exit(0)
if ref.max() > 255: ref = ref / ref.max() * 255
a = ours > thr; frac = a.mean()
tr = np.percentile(ref, 100 * (1 - frac))  # seuil de la reference donnant la meme surface d'encre que la notre : comparaison equitable
b = ref > tr
inter, union = (a & b).sum(), (a | b).sum()
print(f'region {Y0}-{Y1}/{X0}-{X1} : notre encre (> {thr}) = {100 * frac:.1f}% des pixels ; seuil equivalent reference = {tr:.0f}')
print(f'IoU {inter / max(1, union):.3f} | de notre encre, {100 * inter / max(1, a.sum()):.0f}% est aussi encre pour la reference | de l encre de la reference, {100 * inter / max(1, b.sum()):.0f}% est encre pour nous')
print(f'correlation brute {np.corrcoef(ours.ravel()[::7], ref.ravel()[::7])[0, 1]:.3f}')
# par carreaux de 500 px : ou sont les desaccords ?
S = 500; H, W = a.shape; print('carreaux (ligne, colonne en px de la region) avec le plus de desaccord (nous seuls / ref seule, en % du carreau) :')
rows = []
for y in range(0, H - S + 1, S):
    for x in range(0, W - S + 1, S):
        ca, cb = a[y:y + S, x:x + S], b[y:y + S, x:x + S]
        rows.append((100 * (ca & ~cb).mean() + 100 * (cb & ~ca).mean(), y, x, 100 * (ca & ~cb).mean(), 100 * (cb & ~ca).mean(), 100 * (ca & cb).mean()))
for tot, y, x, ro, rb, g in sorted(rows, reverse=True)[:6]: print(f'  y {y:4d}-{y + S:4d} x {x:4d}-{x + S:4d} : nous seuls {ro:4.1f}%  ref seule {rb:4.1f}%  accord {g:4.1f}%')
def im(v): return Image.fromarray(np.clip(v, 0, 255).astype(np.uint8)).resize((W // d, H // d), Image.BILINEAR)
im(ours).save(outp + '_notre.png'); im(ref).save(outp + '_ref.png')
rgb = np.zeros((H, W, 3), np.uint8); rgb[...] = (np.clip(ours, 0, 255) * 0.25)[..., None].astype(np.uint8)
rgb[a & b] = (40, 200, 40); rgb[a & ~b] = (230, 50, 50); rgb[b & ~a] = (60, 100, 255)
Image.fromarray(rgb).resize((W // d, H // d), Image.NEAREST).save(outp + '_accord.png'); print('images', outp + '_{notre,ref,accord}.png')
