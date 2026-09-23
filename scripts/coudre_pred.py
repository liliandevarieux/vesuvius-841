# Recoud les paves d inference en une prediction de segment entier. Recouvrement resolu par le maximum.
# usage: coudre_pred.py <nom> <fichier_fenetres> <prefixe_predictions> <sortie.tif>
import sys, os, numpy as np, tifffile, zarr
nom, fw, pre, out = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
H = '/home/slusarska_holding/vesuvius'
S = zarr.open(f'{H}/ink-dataset/841/{nom}/{nom}.zarr', mode='r')['0']
HH, WW = S.shape[1], S.shape[2]
plein = np.zeros((HH, WW), np.uint8); n = 0
for k, l in enumerate(open(fw), 1):
    Y0, Y1, X0, X1 = map(int, l.split())
    p = f'{pre}{k}.tif'
    if not os.path.exists(p): print(f'  pave {k} absent'); continue
    a = tifffile.imread(p)
    h, w = min(a.shape[0], Y1 - Y0, HH - Y0), min(a.shape[1], X1 - X0, WW - X0)
    v = plein[Y0:Y0 + h, X0:X0 + w]
    plein[Y0:Y0 + h, X0:X0 + w] = np.maximum(v, a[:h, :w].astype(np.uint8)); n += 1
tifffile.imwrite(out, plein)
print(f'{nom} : {n} paves recousus -> {out} ({HH} x {WW}, {100*(plein>0).mean():.1f} % couvert)')
