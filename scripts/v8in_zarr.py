# v8-in (YoussefMoNader/ink-8um-v8in, code et poids publiés, non modifiés) sur un volume de surface OME-Zarr des
# organisateurs : niveau 0 (D, H, W) uint8 -> pile H x W x D -> les 24 couches centrales (comme predict.py) -> écrêtage
# à 200 -> predict_stack du code publié, dans les deux ordres de couches. Sortie : probabilité x 255 en uint8.
# usage : v8in_zarr.py VOLUME.zarr SORTIE_PREFIXE [taille_lot]
import sys, time, json, numpy as np, tifffile, zarr, torch
sys.path.insert(0, '/home/slusarska_holding/vesuvius/c343/v8in')
from ink8um import InkDetector
from ink8um.inference import predict_stack

vol, out = sys.argv[1], sys.argv[2]
lot = int(sys.argv[3]) if len(sys.argv) > 3 else 4
a = np.asarray(zarr.open(vol, mode='r')['0'][:])
print('volume', a.shape, a.dtype, flush=True)
d0 = (a.shape[0] - 24) // 2
pile = np.clip(a[d0:d0 + 24].transpose(1, 2, 0), 0, 200).astype(np.uint8)
print('couches %d..%d sur %d' % (d0, d0 + 23, a.shape[0]), flush=True)
modele = InkDetector.from_pretrained('/home/slusarska_holding/vesuvius/c343/v8in').cuda().eval()
journal = {}
for inverse in (False, True):
    t0 = time.time(); dernier = [0.0]

    def prog(n, tot):
        if time.time() - dernier[0] > 60 or n == tot:
            dernier[0] = time.time()
            print('  %s %d/%d tuiles (%.0f s) memoire %.2f Go' % ('inverse' if inverse else 'direct', n, tot,
                  time.time() - t0, torch.cuda.max_memory_allocated() / 1e9), flush=True)
    p = predict_stack(modele, pile, reverse=inverse, batch_size=lot, num_workers=2, progress=prog)
    f = '%s_%s.tif' % (out, 'inverse' if inverse else 'direct')
    tifffile.imwrite(f, np.round(p * 255).astype(np.uint8))
    journal['inverse' if inverse else 'direct'] = dict(fichier=f, secondes=round(time.time() - t0),
                                                       moyenne=float(p.mean()), p99=float(np.percentile(p[p > 0], 99)))
    print(f, journal, flush=True)
json.dump(journal, open(out + '_journal.json', 'w'), indent=1)
print('FINI', flush=True)
