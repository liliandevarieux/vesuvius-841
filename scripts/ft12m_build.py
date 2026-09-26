# PR-30 : jeu d entrainement « scan 1,2 m » au format des etiquettes natives d ink_9um
# (hf://buckets/scrollprize/datasets/ink_9um/labels/native9-scrollprizeorg-21slices) : par segment, <seg>_inklabels.zarr
# et <seg>_supervision_mask.zarr, zarr v2, forme = celle du volume (D, H, W), encre SEULEMENT sur la couche D // 2
# (le chargeur y lit les etiquettes et centre la fenetre de 17 couches dessus), valeurs 0 / 255, chunks (D, 128, 128).
# Etiquettes 20260918 au niveau 2 (grille du volume 2,4 um / 4) reportees au plus proche voisin sur la grille 1,2 m,
# par le rapport des tailles de canevas (egal au rapport des voxels a 0,3 % pres).
# usage : ft12m_build.py NOM   (lit ft12m/src/NOM/{vol.zarr, inklabels.zarr, supervision.zarr}, ecrit ft12m/labels/NOM/)
import sys, os, shutil, numpy as np, zarr
from numcodecs import Blosc

H = '/home/slusarska_holding/vesuvius/ft12m'
nom = sys.argv[1]
src = '%s/src/%s' % (H, nom)
vol = zarr.open(src + '/vol.zarr', mode='r')['0']
D, Hh, W = vol.shape


def niveau2(chemin):
    g = zarr.open(chemin, mode='r')
    a = np.asarray(g['2'][:]).squeeze()
    return (a.any(axis=0) if a.ndim == 3 else a) > 0


def reporte(a):
    iy = np.minimum((np.arange(Hh) + 0.5) * a.shape[0] / Hh, a.shape[0] - 1).astype(int)
    ix = np.minimum((np.arange(W) + 0.5) * a.shape[1] / W, a.shape[1] - 1).astype(int)
    return a[np.ix_(iy, ix)]


out = '%s/labels/%s' % (H, nom)
shutil.rmtree(out, ignore_errors=True)
os.makedirs(out)
comp = Blosc(cname='zstd', clevel=5, shuffle=Blosc.BITSHUFFLE)
for quoi, fichier in (('inklabels', 'inklabels'), ('supervision_mask', 'supervision')):
    n2 = niveau2('%s/%s.zarr' % (src, fichier))
    plan = reporte(n2)
    g = zarr.open_group('%s/%s_%s.zarr' % (out, nom, quoi), mode='w', zarr_format=2)
    arr = g.create_array('0', shape=(D, Hh, W), chunks=(D, 128, 128), dtype='u1', compressors=comp, fill_value=0)
    arr[D // 2] = plan.astype(np.uint8) * 255
    g.attrs['canvas_size'] = [Hh, W]
    g.attrs['pr30'] = 'etiquettes 20260918 niveau 2 reportees sur la grille 1,2 m, couche %d' % (D // 2)
    print('%-10s %-17s forme %s  couche %d  pixels %d  (niveau 2 %s)' % (nom, quoi, (D, Hh, W), D // 2, int(plan.sum()),
          n2.shape))
