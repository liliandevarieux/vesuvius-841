# usage: cmp.py <pred.tif> <sortie.png> <Y0> <Y1> <X0> <X1> [titre]
import sys, numpy as np, zarr, tifffile
from PIL import Image, ImageDraw
pred, outp = sys.argv[1], sys.argv[2]; Y0, Y1, X0, X1 = map(int, sys.argv[3:7]); title = sys.argv[7] if len(sys.argv) > 7 else 'NOTRE modele'
import os; name = os.environ.get('SEG', 'w00_20231016151002'); seg = f'/home/slusarska_holding/vesuvius/ink-dataset/{os.environ.get("SCROLL", "phercparis4")}/{name}'  # SEG=w02_... autre segment, SCROLL=1667 autre rouleau
def crop_tif(path):  # TIFF pleine taille, ou TIFF de region accompagne de <path>.origin ("Y X" de son coin haut-gauche)
    import os; oy, ox = (map(int, open(path + '.origin').read().split()) if os.path.exists(path + '.origin') else (0, 0))
    with tifffile.TiffFile(path) as tf: return np.asarray(zarr.open(tf.aszarr(), mode='r')[Y0 - oy:Y1 - oy, X0 - ox:X1 - ox])
ours = crop_tif(pred); refp = f'{seg}/preds/{os.environ.get("REF", "tile256_stride128_layers1_63_hann_fwd.tif")}'
ref = crop_tif(refp) if os.environ.get('REF', '') != 'none' and os.path.exists(refp) else None  # REF=none ou fichier absent : pas de reference
vol = np.asarray(zarr.open(f'{seg}/{name}.zarr/0', mode='r')[32, Y0:Y1, X0:X1])
ink = np.asarray(zarr.open(f'{seg}/{name}_inklabels.zarr/0', mode='r')[32, Y0:Y1, X0:X1]) > 0
sup = np.asarray(zarr.open(f'{seg}/{name}_supervision_mask.zarr/0', mode='r')[32, Y0:Y1, X0:X1]) > 0
c = f'{np.corrcoef(ours.astype(float).ravel()[::97], ref.astype(float).ravel()[::97])[0,1]:.3f}' if ref is not None and ref.max() > 0 else '-'
print(f'notre pred: min {ours.min()} max {ours.max()} moy {ours.mean():.1f} | sur encre {ours[ink].mean():.1f} vs hors encre {ours[sup & ~ink].mean():.1f} | corr. avec ref {c}')
W = 1600; s = W / (X1 - X0); H = int((Y1 - Y0) * s)
def im(a): return Image.fromarray(a.astype(np.uint8)).resize((W, H), Image.BILINEAR).convert('RGB')
def ov(b, m, col, alpha):
    mm = Image.fromarray((m*255).astype(np.uint8)).resize(b.size, Image.NEAREST).point(lambda q: alpha if q else 0)
    return Image.composite(Image.new('RGB', b.size, col), b, mm)
# notre prediction : brute, et etiree en contraste (min..max -> 0..255) pour voir la moindre structure
stretched = ((ours.astype(float) - ours.min()) / max(1, ours.max() - ours.min()) * 255)
panels = [(f'{title} (brut, blanc = encre)', im(ours)), (f'{title} (contraste etire {ours.min()}..{ours.max()} -> 0..255)', im(stretched)),
          *([('REFERENCE des organisateurs', im(ref))] if ref is not None else []), ('volume z=32 + masque (vert) + labels (rouge)', ov(ov(im(vol), sup, (40,200,40), 90), ink, (255,40,40), 200))]
out = Image.new('RGB', (W, (H+28)*len(panels)), (20,20,20)); d = ImageDraw.Draw(out)
for k, (t, p) in enumerate(panels):
    out.paste(p, (0, k*(H+28)+24)); d.text((6, k*(H+28)+6), t, fill=(255,255,0))
out.save(outp); print('image', out.size)
