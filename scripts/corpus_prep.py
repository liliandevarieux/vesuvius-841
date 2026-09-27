# PR-38 : entree 21 couches d un segment du corpus d ink_9um, SEULEMENT sous sa supervision (+ 1 chunk de marge) :
# le niveau 2 d un volume 2,4 um pese ~20 Go, la zone etiquetee ~4 % (idee de la PR villa #1821). Recette identique au
# script officiel prepare_9um_isotropic_input.py (niveau 2, 84 couches centrees, moyenne arrondie par 4 -> 21 couches,
# zarr v2 uint8 chunks (21, 128, 128) Blosc zstd 5 bitshuffle) ; hors des chunks retenus, 0 (= hors papyrus pour le chargeur).
# Chunks bruts telecharges en HTTPS avec reprises, gardes dans <seg>/src2/ (reprise possible).
# usage : corpus_prep.py SEGMENT CHEMIN_S3_DU_VOLUME     (dossier : ft12m/corpus24/SEGMENT)
import sys, os, json, math, shutil, time, urllib.request, numpy as np, zarr
from concurrent.futures import ThreadPoolExecutor
from scipy import ndimage
from numcodecs import Blosc

seg, chemin = sys.argv[1], sys.argv[2]
D = '/home/slusarska_holding/vesuvius/ft12m/corpus24/' + seg
URL = 'https://vesuvius-challenge-open-data.s3.amazonaws.com/' + chemin.rstrip('/') + '/2/'


def get(u, essais=8):
    for k in range(essais):
        try:
            with urllib.request.urlopen(u, timeout=120) as r:
                return r.read()
        except Exception as e:
            if getattr(e, 'code', None) == 404:
                return None
            time.sleep(min(60, 2 ** k))
    raise RuntimeError('echec ' + u)


src = D + '/src2'
os.makedirs(src, exist_ok=True)
if not os.path.exists(src + '/.zarray'):
    open(src + '/.zarray', 'wb').write(get(URL + '.zarray'))
meta = json.load(open(src + '/.zarray'))
Z, H, W = meta['shape']
assert meta['chunks'][0] == Z and meta['dtype'] == '|u1', meta
cy, cx = meta['chunks'][1:]
sep = meta.get('dimension_separator', '.')

s = zarr.open(D + '/%s_supervision_mask.zarr' % seg, mode='r')['0']
assert tuple(s.shape[1:]) == (H, W), (s.shape, meta['shape'])
m = np.asarray(s[s.shape[0] // 2]) > 0
c = np.zeros((-(-H // cy), -(-W // cx)), bool)
yy, xx = np.nonzero(m)
c[yy // cy, xx // cx] = True
c = ndimage.binary_dilation(c, iterations=1)
cles = [(i, j) for i, j in zip(*np.nonzero(c))]


def charge(ij):
    f = '%s/0%s%d%s%d' % (src, sep, ij[0], sep, ij[1])
    if not os.path.exists(f):
        b = get(URL + '0%s%d%s%d' % (sep, ij[0], sep, ij[1]))
        if b is not None:
            open(f + '.tmp', 'wb').write(b)
            os.replace(f + '.tmp', f)


t0 = time.time()
with ThreadPoolExecutor(8) as p:
    list(p.map(charge, cles))
print('%s : %d chunks sur %d (%.1f %%), %.0f Mo, %.0f s' % (seg, len(cles), c.size, 100 * len(cles) / c.size,
      sum(os.path.getsize(os.path.join(src, f)) for f in os.listdir(src)) / 1e6, time.time() - t0), flush=True)

a = zarr.open_array(src, mode='r')
z0 = math.ceil((Z - 84) / 2)
out = D + '/surface-volume.zarr'
tmp = out + '.partial'
shutil.rmtree(tmp, ignore_errors=True)
g = zarr.open_group(tmp, mode='w', zarr_format=2)
t = g.create_array('0', shape=(21, H, W), chunks=(21, 128, 128), dtype='u1', fill_value=0,
                   compressors=Blosc(cname='zstd', clevel=5, shuffle=Blosc.BITSHUFFLE))
assert (cy, cx) == (128, 128)
for i, j in cles:
    y0, y1, x0, x1 = i * 128, min(H, i * 128 + 128), j * 128, min(W, j * 128 + 128)
    b = np.asarray(a[z0:z0 + 84, y0:y1, x0:x1], dtype=np.float32)
    t[:, y0:y1, x0:x1] = np.rint(b.reshape(21, 4, y1 - y0, x1 - x0).mean(axis=1)).astype(np.uint8)
g.attrs.update({'format': 'level2-zmean4-21slice-v1', 'source': URL, 'source_level': '2', 'source_shape_zyx': [Z, H, W],
                'source_z_slice': [z0, z0 + 84], 'z_pool': 'rounded mean of 4 centered source planes',
                'pr38': 'seulement les %d chunks sous supervision + 1 de marge ; ailleurs 0' % len(cles)})
shutil.rmtree(out, ignore_errors=True)
os.replace(tmp, out)
print('%s : surface-volume.zarr ecrit (21, %d, %d), z %d-%d' % (seg, H, W, z0, z0 + 84), flush=True)
