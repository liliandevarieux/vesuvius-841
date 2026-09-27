# PR-38 : donne a une entree 21 couches ~9,6 um issue d un scan 2,4 um l aspect d un scan eligible 1,2 m : flou gaussien
# fixe, 0,69 px a plat (AndreasHad04, #1898 : 0,675-0,700) et 0,70 couche en profondeur. Andreas donne 0,550-0,575
# couche, cale sur 841 (correlation 0,812) ; reproduit ici sur pherc1667-w013 (brut 0,693 -> 0,810 a 0,56). Nos entrees
# eligibles d entrainement sont plus floues (0009B 0,863, 841 segB 0,840, 0500P2 0,825 ; 0800 0,873 chez Andreas) :
# 0,70 couche vise leur moyenne 0,843 (0,6 -> 0,821, 0,8 -> 0,862). Regle sans etiquette, fixee avant tout entrainement.
# Applique a TOUT le volume (donc a chaque patch). Traitement par bandes de Y avec marge.
# Controle imprime : correlation moyenne entre couches voisines avant / apres, sur le papyrus (valeur > 0) d une bande
# centrale (Andreas : 0,699 pour l entree 2,4 um, 0,812 pour l eligible).
# usage : ft12m_flou.py ENTREE.zarr SORTIE.zarr   |   ft12m_flou.py --corr ENTREE.zarr   (correlation seule)
import sys, os, shutil, json, numpy as np, zarr
from scipy import ndimage
from numcodecs import Blosc

SZ, SXY, BANDE, MARGE = 0.70, 0.69, 512, 8


def correlation(a):
    a = a.astype(np.float32)
    m = (a > 0).all(axis=0)
    if m.sum() < 1000:
        return float('nan')
    c = [np.corrcoef(a[k][m], a[k + 1][m])[0, 1] for k in range(a.shape[0] - 1)]
    return float(np.mean(c))


def bande_centrale(z):
    H = z.shape[1]
    return np.asarray(z[:, H // 2 - 256:H // 2 + 256, :])


if sys.argv[1] == '--corr':
    print('%s correlation couches voisines %.3f' % (sys.argv[2], correlation(bande_centrale(zarr.open(sys.argv[2], mode='r')['0']))))
    sys.exit()

src, dst = sys.argv[1], sys.argv[2]
g = zarr.open(src, mode='r')
a = g['0']
D, H, W = a.shape
tmp = dst + '.partial'
shutil.rmtree(tmp, ignore_errors=True)
out = zarr.open_group(tmp, mode='w', zarr_format=2)
b = out.create_array('0', shape=a.shape, chunks=a.chunks, dtype='u1', fill_value=0,
                     compressors=Blosc(cname='zstd', clevel=5, shuffle=Blosc.BITSHUFFLE))
for y0 in range(0, H, BANDE):
    ya, yb = max(0, y0 - MARGE), min(H, y0 + BANDE + MARGE)
    u = np.asarray(a[:, ya:yb, :])
    cols = np.nonzero(u.any(axis=(0, 1)))[0]
    if cols.size == 0:                                # bande vide (volume creux du corpus) : rien a ecrire
        continue
    xa, xb = max(0, cols[0] - MARGE), min(W, cols[-1] + 1 + MARGE)
    x = u[:, :, xa:xb].astype(np.float32)
    papyrus = x > 0
    f = ndimage.gaussian_filter(x, (SZ, SXY, SXY), mode='nearest')
    f[~papyrus] = 0                                   # hors papyrus reste 0 (le chargeur s en sert)
    b[:, y0:min(H, y0 + BANDE), xa:xb] = np.clip(np.rint(f[:, y0 - ya:y0 - ya + min(BANDE, H - y0), :]), 0, 255).astype(np.uint8)
out.attrs.update(dict(g.attrs))
out.attrs['pr38_flou'] = 'gaussien fixe sigma z %.2f couche, xy %.2f px (calibrage #1898)' % (SZ, SXY)
shutil.rmtree(dst, ignore_errors=True)
os.replace(tmp, dst)
print('%s -> %s  forme %s  correlation couches voisines %.3f -> %.3f' % (os.path.basename(os.path.dirname(src)) or src, dst, a.shape,
      correlation(bande_centrale(a)), correlation(bande_centrale(zarr.open(dst, mode='r')['0']))))
