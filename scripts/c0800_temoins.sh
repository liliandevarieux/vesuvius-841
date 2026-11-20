#!/bin/bash
# Point 3 (0800), cartes témoins de 0009B (segment 20250919125754, 8,64 um, fenêtre de PR-47), avant inscription, sans
# rien de 0800 : Reader V3 et Argus V3 (commande des auteurs, deux sens) sur le volume entier ; v8-in (deux sens) sur la
# fenêtre de PR-47 avec une marge (lignes 4534-6966, colonnes 1472-4928 ; origine écrite à côté).
H=/home/slusarska_holding/vesuvius; D=$H/c0800/temoins; mkdir -p $D; P=$H/villa/vesuvius/.venv/bin/python
V=$H/ft12m/src/0009B/vol.zarr
date "+debut %F %T"
for m in reader_v3/reader-v3 argus_v3/argus-v3; do
  n=$(basename $m); cd $H/villa/vesuvius
  $P -m vesuvius.ink_detection.inference.infer $V $H/checkpoints/$m.pth $D/${n}_0009B.tif \
     --overlap 0.5 --blend-mode hann --direction both --batch-size 2 --num-workers 2 --no-compile > $D/${n}_0009B.log 2>&1
  echo "$n exit=$? $(date +%T)"
done
cd $H
$P - <<'PY'
import zarr, numpy as np
src = zarr.open('/home/slusarska_holding/vesuvius/ft12m/src/0009B/vol.zarr', mode='r')['0']
a = np.asarray(src[:, 4534:6966, 1472:4928])
g = zarr.open_group('/home/slusarska_holding/vesuvius/c0800/temoins/vol_0009B_fenetre', mode='w')
g.create_array('0', shape=a.shape, chunks=(a.shape[0], 128, 128), dtype='uint8')[:] = a
open('/home/slusarska_holding/vesuvius/c0800/temoins/vol_0009B_fenetre.origin', 'w').write('4534 1472\n')
print('fenetre 0009B', a.shape, 'non vide %.0f %%' % (100 * (a[15] > 0).mean()))
PY
cp "/mnt/c/Users/SLUSARSKA HOLDING/vesuvius/scripts/v8in_zarr.py" .
$P -u v8in_zarr.py c0800/temoins/vol_0009B_fenetre $D/v8in_0009B 4 > $D/v8in_0009B.log 2>&1
echo "v8in exit=$? $(date +%T)"
date "+FINI %F %T"
