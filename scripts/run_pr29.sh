#!/bin/bash
# PR-29 : ink_9um graine 42, les deux sens, sur PHerc0343P 1,2 m (temoin hors entrainement, meme scan que 0800)
C=/home/slusarska_holding/vesuvius
PY=$C/villa/vesuvius/.venv/bin/python
CK=$C/checkpoints/ink_9um/hybrid_3d2d-seed42/step-075000.pth
exec >> $C/logs/pr29.log 2>&1
echo "== PR-29 demarre $(date +%F' '%T)"
P9=$C/crops/pr28/p343_in.zarr; OUT=$C/predictions/pr29_p343.tif
if [ ! -d "$P9/0" ]; then rm -rf "$P9.partial"; cd $C/villa/vesuvius && $PY $C/prep_12m.py $C/ink-dataset/p343/vol_12m.zarr "$P9" | grep entree; fi
cd $C/villa/vesuvius && $PY -m vesuvius.ink_detection.inference.infer "$P9" "$CK" "$OUT" \
  --overlap 0.5 --blend-mode hann --batch-size 4 --num-workers 4 --no-compile --direction both > /dev/null
cd $C
for f in $OUT ${OUT%.tif}_reverse.tif; do
  [ -s "$f" ] && $PY $C/eval_12m.py $f $C/ink-dataset/p343/20250511003658_inklabels.zarr 3.901 || echo "== ECHEC $f absent"
done
echo "== PR-29 fini $(date +%F' '%T)"
