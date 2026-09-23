# Fabrique le jeu de donnees "segment + labels du professeur" pour affiner un modele sur un rouleau ou il n'a qu'un point d'appui (run 4) :
#   encre    = prediction des organisateurs (professeur) >= T_hi ; fond = professeur <= T_lo ; entre les deux = ignore (hors masque) ;
#   les labels humains (encre et fond sous leur masque) remplacent le professeur la ou ils existent ; les fenetres de test (+ marge) et
#   les zones vides du volume (niveau 3, couche 32 = 0) sont hors masque. Seuils calibres sur les labels humains : T_hi = percentile P_HI du
#   professeur sur l'encre humaine (100 - P_HI % de l'encre humaine retenue), T_lo = percentile P_LO du professeur sur le fond humain.
# Ecrit <dst>/<scroll>/<seg>/ : liens vers le volume, meta.json, tifxyz, preds ; nouveaux <seg>_inklabels.zarr / <seg>_supervision_mask.zarr
# (meme structure que les depots : 65 couches, labels a z=32, niveaux 0-5, chunks 65x128x128).
# usage: SCROLL=841 SEG=w00 [LAB=w00_inklabels_v2 MSK=w00_supervision_mask_v2 P_HI=30 P_LO=90 MARGE=256 | T_EQ=1 DELTA=8 | T_HI=190 T_LO=131]
#        mkteacher.py <professeur.tif (dans preds/)> <dst_dataset_dir> <apercu.png> [Y0,Y1,X0,X1 a exclure ...]
import sys, os, numpy as np, zarr, tifffile
from PIL import Image
teach, dst, apercu = sys.argv[1:4]; EXCL = [tuple(map(int, s.split(','))) for s in sys.argv[4:]]
scroll, seg = os.environ.get('SCROLL', '841'), os.environ.get('SEG', 'w00'); M = int(os.environ.get('MARGE', 256))
P_HI, P_LO = float(os.environ.get('P_HI', 30)), float(os.environ.get('P_LO', 90))
d = f'/home/slusarska_holding/vesuvius/ink-dataset/{scroll}/{seg}'
labz = zarr.open(f'{d}/{os.environ.get("LAB", seg + "_inklabels")}.zarr/0', mode='r'); mskz = zarr.open(f'{d}/{os.environ.get("MSK", seg + "_supervision_mask")}.zarr/0', mode='r')
H, W = labz.shape[1:]; print(f'{scroll}/{seg} : {H} x {W} = {H * W / 1e6:.0f} Mpx')
with tifffile.TiffFile(f'{d}/preds/{teach}') as tf: t = np.asarray(zarr.open(tf.aszarr(), mode='r')[:H, :W])
if t.max() > 255: t = (t.astype(np.float32) / t.max() * 255).astype(np.uint8)
if t.shape != (H, W): t = np.pad(t, ((0, H - t.shape[0]), (0, W - t.shape[1])))
olab = np.asarray(labz[32]) > 0; omask = np.asarray(mskz[32]) > 0; olab &= omask
vz = zarr.open(f'{d}/{seg}.zarr/3', mode='r'); v3 = np.asarray(vz[vz.shape[0] // 2]) > 0   # zones non vides du volume (niveau 3 ; sa pyramide peut reduire z : 841 = 9 couches)
valid = np.kron(v3, np.ones((8, 8), bool))[:H, :W]
if valid.shape != (H, W): valid = np.pad(valid, ((0, H - valid.shape[0]), (0, W - valid.shape[1])))
t_hi = np.percentile(t[olab], P_HI); t_lo = np.percentile(t[omask & ~olab], P_LO)
if os.environ.get('T_EQ', '0') == '1':   # bande ignoree FINE autour du seuil a aire egale (meme surface d encre que l humain dans son masque)
    t_eq = np.percentile(t[omask], 100 * (1 - olab.sum() / omask.sum())); D = float(os.environ.get('DELTA', 8)); t_hi, t_lo = t_eq + D, t_eq - D
    print(f'seuil a aire egale {t_eq:.0f} +/- {D:.0f} (T_EQ=1) : le fond sur doit rester present dans les patchs autour de l encre (le pipeline n entraine que sur des patchs contenant de l encre)')
if os.environ.get('T_HI') and os.environ.get('T_LO'):   # seuils absolus imposes (teacher3 : coeur sur >= 190, fond <= 131 = aire egale - 8)
    t_hi, t_lo = float(os.environ['T_HI']), float(os.environ['T_LO']); print(f'seuils imposes : encre >= {t_hi:.0f}, fond <= {t_lo:.0f}')
ink = (t >= t_hi) & valid; bg = (t <= t_lo) & valid
mask = (ink | bg | omask) & valid
lab = np.where(omask, olab, ink) & mask
for y0, y1, x0, x1 in EXCL: mask[max(0, y0 - M):y1 + M, max(0, x0 - M):x1 + M] = False
lab &= mask
# qualite du professeur, mesuree la ou l humain a tranche
pi, hb = ink & omask, olab; inter = (pi & hb).sum()
print(f'professeur {teach} : seuils encre >= {t_hi:.0f}, fond <= {t_lo:.0f} (P_HI {P_HI:.0f}, P_LO {P_LO:.0f})')
print(f'  dans le masque humain ({100 * omask.mean():.2f} % du segment) : encre humaine {100 * olab.sum() / omask.sum():.1f} % ; le professeur y met {100 * pi.sum() / omask.sum():.1f} % d encre ; '
      f'precision {100 * inter / max(1, pi.sum()):.0f} %, rappel {100 * inter / max(1, hb.sum()):.0f} %, IoU {inter / max(1, (pi | hb).sum()):.3f}')
A = valid.sum()
print(f'  volume non vide : {100 * valid.mean():.1f} % du segment ; nouveau masque {100 * mask.sum() / A:.1f} % du non-vide ({mask.sum() / max(1, omask.sum()):.1f} x le masque humain) ; '
      f'encre {100 * lab.sum() / A:.2f} %, fond {100 * (mask & ~lab).sum() / A:.1f} %, ignore {100 * (valid & ~mask).sum() / A:.1f} % ; exclus : {len(EXCL)} fenetres + marge {M}')
# apercu (1/8) : gris = ignore, vert = encre du professeur, bleu fonce = fond, rouge = labels humains, noir = exclu / vide
s = 8; sub = lambda m: m[::s, ::s]
rgb = np.zeros((sub(mask).shape[0], sub(mask).shape[1], 3), np.uint8); rgb[...] = 70
rgb[sub(bg & mask)] = (30, 40, 110); rgb[sub(lab & ~omask)] = (40, 200, 40); rgb[sub(omask & mask)] = (120, 40, 40); rgb[sub(olab & mask)] = (255, 60, 60)
ex = ~valid
for y0, y1, x0, x1 in EXCL: ex[max(0, y0 - M):y1 + M, max(0, x0 - M):x1 + M] = True
rgb[sub(ex)] = (0, 0, 0); Image.fromarray(rgb).save(apercu); print('apercu', apercu)
# ecriture du jeu de donnees
out = f'{dst}/{scroll}/{seg}'; os.makedirs(out, exist_ok=True)
for f in (f'{seg}.zarr', 'meta.json', 'x.tif', 'y.tif', 'z.tif', 'preds'):
    if os.path.lexists(f'{d}/{f}') and not os.path.lexists(f'{out}/{f}'): os.symlink(f'{d}/{f}', f'{out}/{f}')
# Le nom des labels source vient de LAB comme plus haut : le coder en dur ici faisait echouer tout jeu de donnees
# dont les labels s appellent autrement (<seg>_inklabels_v2, par exemple), apres tout le calcul.
src_attrs = dict(zarr.open(f'{d}/{os.environ.get("LAB", seg + "_inklabels")}.zarr', mode='r').attrs)
def write(kind, arr2d):
    g = zarr.open_group(f'{out}/{seg}{kind}.zarr', mode='w', zarr_format=2); g.attrs.update(src_attrs)
    cur = arr2d.astype(np.uint8) * 255
    for n in range(6):
        a = g.create_array(str(n), shape=(65, -(-H // 2 ** n), -(-W // 2 ** n)), chunks=(65, 128, 128), dtype='uint8',
                           compressors=labz.compressors, chunk_key_encoding={'name': 'v2', 'separator': '.'}, fill_value=0)
        h, w = cur.shape
        for r in range(0, h, 1024): a[32, r:min(r + 1024, h), :w] = cur[r:r + 1024]
        hh, ww = h // 2, w // 2; cur = (cur[:2 * hh, :2 * ww].reshape(hh, 2, ww, 2).mean(axis=(1, 3)) > 127).astype(np.uint8) * 255
    print('ecrit', f'{out}/{seg}{kind}.zarr')
write('_inklabels', lab); write('_supervision_mask', mask)
