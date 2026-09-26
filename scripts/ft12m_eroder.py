# PR-32 V2 : copie du jeu d entrainement avec les etiquettes d encre amincies d un pixel (grille 1,2 m, erosion
# binaire en croix sur la couche D // 2) ; la supervision est recopiee telle quelle.
import os, shutil, numpy as np, zarr
from scipy import ndimage
H = '/home/slusarska_holding/vesuvius/ft12m'
for nom in ['841_w00', '841_segA', '841_segB', '0009B', '0500P2']:
    src, dst = '%s/labels/%s' % (H, nom), '%s/labels_ero1/%s' % (H, nom)
    shutil.rmtree(dst, ignore_errors=True)
    shutil.copytree(src, dst)
    a = zarr.open('%s/%s_inklabels.zarr' % (dst, nom), mode='r+')['0']
    D = a.shape[0]
    plan = np.asarray(a[D // 2]) > 0
    ero = ndimage.binary_erosion(plan)
    a[D // 2] = ero.astype(np.uint8) * 255
    print(nom, 'encre', int(plan.sum()), '->', int(ero.sum()))
