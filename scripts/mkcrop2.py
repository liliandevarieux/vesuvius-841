# Variante de mkcrop.py pour un segment dont le volume de surface n a pas 65 couches (le segment de la spire voisine de 841 en a 109) :
# on prend les ZN couches centrees sur le milieu, pour retomber sur l entree attendue par nos modeles.
# usage: mkcrop2.py <sortie.zarr> Y0 Y1 X0 X1 [marge=128]   env SCROLL SEG ZN=65 ZC=<centre, defaut milieu>
import sys, os, numpy as np, zarr
out = sys.argv[1]; Y0, Y1, X0, X1 = map(int, sys.argv[2:6]); M = int(sys.argv[6]) if len(sys.argv) > 6 else 128
name = os.environ.get('SEG', 'segB'); seg = f'/home/slusarska_holding/vesuvius/ink-dataset/{os.environ.get("SCROLL", "841")}/{name}'
src = zarr.open(f'{seg}/{name}.zarr', mode='r'); s0 = src['0']
ZN = int(os.environ.get('ZN', 65)); ZC = int(os.environ.get('ZC', s0.shape[0] // 2))
FULL = os.environ.get('FULL', '0') == '1'   # toute la profondeur ramenee a ZN couches par interpolation
if FULL:
    z0, z1 = 0, s0.shape[0]
    f = np.linspace(0, z1 - z0 - 1, ZN); lo = np.floor(f).astype(int)
    hi = np.minimum(lo + 1, z1 - z0 - 1); wz = (f - lo)[:, None, None]
else:
    z0 = max(0, min(s0.shape[0] - ZN, ZC - ZN // 2)); z1 = z0 + ZN
print(f'volume {s0.shape} -> couches {z0}-{z1} ({ZN} couches centrees sur {ZC})')
y0, x0 = max(0, Y0 - M) // 128 * 128, max(0, X0 - M) // 128 * 128
y1, x1 = min(s0.shape[1], -(-(Y1 + M) // 128) * 128), min(s0.shape[2], -(-(X1 + M) // 128) * 128)
H, W = y1 - y0, x1 - x0
attrs = dict(src.attrs); attrs['canvas_size'] = [W, H]
dst = zarr.open_group(out, mode='w', zarr_format=2); dst.attrs.update(attrs)
def mk(n, shape):
    return dst.create_array(n, shape=shape, chunks=(ZN, 128, 128), dtype='uint8', compressors=s0.compressors,
                            chunk_key_encoding={'name': 'v2', 'separator': '.'}, fill_value=0)
lvl = mk('0', (ZN, H, W))
for r in range(0, H, 512):
    band = s0[z0:z1, y0 + r:min(y0 + r + 512, y1), x0:x1]
    if FULL:
        band = (band[lo] * (1 - wz) + band[hi] * wz).astype(np.uint8)
    lvl[:, r:r + 512] = band[::-1] if os.environ.get('REV', '0') == '1' else band
cur = np.asarray(lvl[:])
for n in range(1, 6):
    h, w = cur.shape[1] // 2, cur.shape[2] // 2
    cur = cur[:, :2 * h, :2 * w].reshape(ZN, h, 2, w, 2).mean(axis=(2, 4)).astype(np.uint8)
    mk(str(n), cur.shape)[:] = cur
open(out + '.origin', 'w').write(f'{y0} {x0}\n')
print(f'{out} : {H} x {W}, origine {y0} {x0}, niveaux 0-5, non vide {(lvl[ZN // 2] > 0).mean() * 100:.0f}%')
