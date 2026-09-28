#!/bin/bash
# 0800 (cible First Letters) : cartes de Reader v2 (tel que publie) et de R4 (graine 42, pli sans 0841, PR-34) sur les
# six segments de PHerc0800 deja sur le disque (8,64 um, 1,2 m, 116 keV, 31 couches). Entree : les 21 couches centrees
# (prep_12m.py, comme pour 1447). Deux sens ; le sens se choisit sans etiquette (p99-p50, eval_12m.py sans etiquette).
# Branche « echoue » de PR-48 / PR-52 : Reader v2 et R4 cote a cote. Cartes seulement : le test de lecture de 0800 sera
# inscrit avant toute lecture.
C=/home/slusarska_holding/vesuvius
PY=$C/villa/vesuvius/.venv/bin/python
RV2=$C/checkpoints/reader_v2/reader-v2-step040000.pth
R4=$C/runs/pr34_R4_sans0841/ckpt_004000.pth
exec >> $C/logs/x0800.log 2>&1
echo "== 0800 demarre $(date +%F' '%T)"
mkdir -p $C/crops/0800
for d in $C/ink-dataset/0800/*/; do
  seg=$(basename $d); s=${seg%%-*}
  V=$(ls -d $d/surface-volumes/*.zarr | head -1)
  P9=$C/crops/0800/${s}_in.zarr
  [ -d "$P9/0" ] || { rm -rf "$P9.partial"; cd $C/villa/vesuvius && $PY $C/prep_12m.py "$V" "$P9" > /dev/null; }
  [ -d "$P9/0" ] || { echo "== ECHEC entree $s -- ne pas conclure"; continue; }
  for m in readerv2 R4; do
    CK=$RV2; [ $m = R4 ] && CK=$R4
    OUT=$C/predictions/x0800_${m}_$s.tif
    for passe in 1 2; do
      if [ ! -s "$OUT" ] || [ ! -s "${OUT%.tif}_reverse.tif" ]; then
        cd $C/villa/vesuvius && $PY -m vesuvius.ink_detection.inference.infer "$P9" "$CK" "$OUT" \
          --overlap 0.5 --blend-mode hann --batch-size 4 --num-workers 4 --no-compile --direction both > /dev/null
      fi
    done
    cd $C
    for f in $OUT ${OUT%.tif}_reverse.tif; do
      [ -s "$f" ] && $PY $C/eval_12m.py $f - || echo "== ECHEC $(basename $f) absent -- ne pas conclure"
    done
  done
  echo "== $s fait $(date +%T)"
done
echo "== 0800 fini $(date +%F' '%T)"
