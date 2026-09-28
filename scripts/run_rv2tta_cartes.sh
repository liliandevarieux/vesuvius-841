#!/bin/bash
# File de la carte graphique apres les cartes de PR-53 (regle 6) : Reader v2 tel que publie, avec l augmentation miroir
# au moment de la prediction (--tta-mirror : chaque patch est predit tel quel et retourne selon les deux axes du plan,
# les predictions sont remises a l endroit puis moyennees). Memes reglages que les cartes Reader v2 existantes
# (pr44_readerv2, pr45_readerv2, x0800_readerv2) ; seule l augmentation change. D abord le banc (841 w00/segA/segB,
# 0009B), puis les six segments de 0800. Cartes seulement : le test de lecture sera inscrit avant toute lecture.
C=/home/slusarska_holding/vesuvius
PY=$C/villa/vesuvius/.venv/bin/python
RV2=$C/checkpoints/reader_v2/reader-v2-step040000.pth
exec >> $C/logs/rv2tta.log 2>&1
echo "== attente de la fin des cartes de PR-53 $(date +%T)"
while pgrep -f run_pr53_cartes.sh > /dev/null; do sleep 20; done
echo "== Reader v2 + miroir demarre $(date +%F' '%T)"
infere () { [ -s "$2" ] && [ -s "${2%.tif}_reverse.tif" ] && return 0
  cd $C/villa/vesuvius && $PY -m vesuvius.ink_detection.inference.infer "$1" "$RV2" "$2" \
    --overlap 0.5 --blend-mode hann --batch-size 4 --num-workers 4 --no-compile --direction both \
    --tta-mirror --tta-batch-size 2 > /dev/null; }
for s in 841_w00 841_segA 841_segB 0009B; do
  OUT=$C/predictions/rv2tta_$s.tif
  for passe in 1 2; do infere $C/crops/pr31/${s}_in.zarr $OUT; done
  [ -s "$OUT" ] && [ -s "${OUT%.tif}_reverse.tif" ] || echo "== ECHEC $(basename $OUT) -- ne pas conclure"
  echo "== $s fait $(date +%T)"
done
for P9 in $C/crops/0800/*_in.zarr; do
  s=$(basename $P9 _in.zarr)
  OUT=$C/predictions/x0800_readerv2tta_$s.tif
  for passe in 1 2; do infere $P9 $OUT; done
  [ -s "$OUT" ] && [ -s "${OUT%.tif}_reverse.tif" ] || echo "== ECHEC $(basename $OUT) -- ne pas conclure"
  echo "== 0800 $s fait $(date +%T)"
done
echo "== Reader v2 + miroir fini $(date +%F' '%T)"
