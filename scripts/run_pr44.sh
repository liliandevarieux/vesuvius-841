#!/bin/bash
# PR-44 : Reader v2 (DomRusso2, publie le 27/09, MIT) sur les trois feuillets de 841, qu il n a jamais vus : forme des
# lettres. Inference de base (meme CLI et memes entrees 21 couches natives que PR-31 a PR-43), deux sens, sens choisi
# sans etiquette ; mesures eval_sup / eval_forme / eval_forme_fond. Passe de reparation, sorties verifiees.
C=/home/slusarska_holding/vesuvius
PY=$C/villa/vesuvius/.venv/bin/python
CK=$C/checkpoints/reader_v2/reader-v2-step040000.pth
exec >> $C/logs/pr44.log 2>&1
echo "== PR-44 demarre $(date +%F' '%T)"
for s in 841_w00 841_segA 841_segB; do
  P9=$C/crops/pr31/${s}_in.zarr; OUT=$C/predictions/pr44_readerv2_$s.tif
  [ -d "$P9/0" ] || { echo "== ECHEC entree $P9 absente -- ne pas conclure"; continue; }
  for passe in 1 2; do
    if [ ! -s "$OUT" ] || [ ! -s "${OUT%.tif}_reverse.tif" ]; then
      cd $C/villa/vesuvius && $PY -m vesuvius.ink_detection.inference.infer "$P9" "$CK" "$OUT" \
        --overlap 0.5 --blend-mode hann --batch-size 4 --num-workers 4 --no-compile --direction both > /dev/null
    fi
  done
  cd $C
  for f in $OUT ${OUT%.tif}_reverse.tif; do
    [ -s "$f" ] && { $PY $C/eval_sup.py $f $s; $PY $C/eval_forme.py $f $s; $PY $C/eval_forme_fond.py $f $s; } \
      || echo "== ECHEC $(basename $f) absent -- ne pas conclure"
  done
done
echo "--- rappel : PRIMAIRE = allongement moyen des 3 feuillets (sens choisi sans etiquette) >= 16,0 ---"
echo "== PR-44 fini $(date +%F' '%T)"
