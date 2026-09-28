# PR-50 : moyenne pixel a pixel de deux cartes d encre de meme forme (uint8), arrondie, ecrite au meme format.
# usage : moyenne_cartes.py A.tif B.tif SORTIE.tif
import sys, numpy as np, tifffile

a, b = tifffile.imread(sys.argv[1]), tifffile.imread(sys.argv[2])
assert a.shape == b.shape and a.dtype == b.dtype, (a.shape, b.shape, a.dtype, b.dtype)
m = np.round((a.astype(np.float32) + b.astype(np.float32)) / 2).astype(a.dtype)
tifffile.imwrite(sys.argv[3], m)
print(sys.argv[3], m.shape, m.dtype)
