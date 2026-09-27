# PR-36 : pseudo-etiquettes sur le rouleau LAISSE DE COTE, tirees de la carte du modele du pli (qui ne l a jamais vu),
# sans aucune etiquette humaine de ce rouleau. Zone d evaluation = supervision humaine du segment dilatee de 128 px
# (carre de 257 px) : rien n y est supervise, et aucun patch 128 contenant un pixel supervise ne la touche.
# Hors de cette zone, sur le papyrus (carte > 0) : encre = carte >= 92e centile, fond = carte <= 60e centile, le reste
# inconnu (hors supervision) ; composantes d encre de moins de 30 px retirees. Centiles pris hors zone d evaluation.
# Format identique a ft12m_build.py : zarr v2 (D, H, W), 0 / 255 sur la couche D // 2.
# usage : ft12m_pseudo.py NOM CARTE.tif SORTIE_DIR   (ecrit SORTIE_DIR/NOM/NOM_{inklabels,supervision_mask}.zarr)
import sys, os, shutil, numpy as np, tifffile, zarr
from scipy import ndimage
from numcodecs import Blosc

H = '/home/slusarska_holding/vesuvius/ft12m'
nom, carte, sortie = sys.argv[1], sys.argv[2], sys.argv[3]
vol = zarr.open('%s/src/%s/vol.zarr' % (H, nom), mode='r')['0']
D, Hh, W = vol.shape
P = tifffile.imread(carte)
if P.ndim == 3:
    P = P[0] if P.shape[0] < P.shape[-1] else P[..., 0]
assert P.shape == (Hh, W), (P.shape, vol.shape)


def reporte(a):
    iy = np.minimum((np.arange(Hh) + 0.5) * a.shape[0] / Hh, a.shape[0] - 1).astype(int)
    ix = np.minimum((np.arange(W) + 0.5) * a.shape[1] / W, a.shape[1] - 1).astype(int)
    return a[np.ix_(iy, ix)]


s2 = np.asarray(zarr.open('%s/src/%s/supervision.zarr' % (H, nom), mode='r')['2'][:]).squeeze()
s2 = (s2.any(axis=0) if s2.ndim == 3 else s2) > 0
zone = ndimage.maximum_filter(reporte(s2).astype(np.uint8), size=257) > 0
libre = (P > 0) & ~zone
q60, q92 = np.percentile(P[libre], [60, 92])
encre = libre & (P >= q92)
lab, n = ndimage.label(encre)
taille = np.bincount(lab.ravel())
encre &= (taille >= 30)[lab]
fond = libre & (P <= q60)
sup = encre | fond

out = '%s/%s' % (sortie, nom)
shutil.rmtree(out, ignore_errors=True)
os.makedirs(out)
comp = Blosc(cname='zstd', clevel=5, shuffle=Blosc.BITSHUFFLE)
for quoi, plan in (('inklabels', encre), ('supervision_mask', sup)):
    g = zarr.open_group('%s/%s_%s.zarr' % (out, nom, quoi), mode='w', zarr_format=2)
    arr = g.create_array('0', shape=(D, Hh, W), chunks=(D, 128, 128), dtype='u1', compressors=comp, fill_value=0)
    arr[D // 2] = plan.astype(np.uint8) * 255
    g.attrs['canvas_size'] = [Hh, W]
    g.attrs['pr36'] = 'pseudo-etiquettes de %s, seuils %d / %d, zone d evaluation exclue' % (os.path.basename(carte), q60, q92)
print('%-9s seuils fond<=%d encre>=%d  encre %.2f Mpx  fond %.2f Mpx  zone eval %.2f Mpx  (touche la zone : %d px)'
      % (nom, q60, q92, encre.sum() / 1e6, fond.sum() / 1e6, zone.sum() / 1e6, int((sup & zone).sum())))
