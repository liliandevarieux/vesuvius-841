#!/bin/bash
# PR-28 : ink_9um graine 42 etape 75 000, les deux sens, sur des volumes 1,2 m (~9 um) prepares par prep_12m.py :
# controle positif 0139 w035 (etiquete), 841 segB (etiquete), puis les 6 segments de PHerc0800 (sans etiquette).
# Chemins absolus, sorties verifiees sur disque.
C=/home/slusarska_holding/vesuvius
PY=$C/villa/vesuvius/.venv/bin/python
CK=$C/checkpoints/ink_9um/hybrid_3d2d-seed42/step-075000.pth
exec >> $C/logs/pr28.log 2>&1
echo "== PR-28 demarre $(date +%F' '%T)"
mkdir -p $C/crops/pr28

infer_un () {   # $1 = volume source, $2 = nom
  local P9=$C/crops/pr28/$2_in.zarr OUT=$C/predictions/pr28_$2.tif
  if [ ! -d "$P9/0" ]; then
    rm -rf "$P9.partial"
    cd $C/villa/vesuvius && $PY $C/prep_12m.py "$1" "$P9" | grep entree || { echo "== ECHEC prep $2"; return 1; }
  fi
  if [ ! -s "$OUT" ] || [ ! -s "${OUT%.tif}_reverse.tif" ]; then
    echo "== inference $2 $(date +%T)"
    cd $C/villa/vesuvius && $PY -m vesuvius.ink_detection.inference.infer "$P9" "$CK" "$OUT" \
      --overlap 0.5 --blend-mode hann --batch-size 4 --num-workers 4 --no-compile --direction both > /dev/null
  fi
  for f in "$OUT" "${OUT%.tif}_reverse.tif"; do
    [ -s "$f" ] && echo "   ecrit $(basename $f)" || { echo "== ECHEC : $(basename $f) absent -- ne pas conclure"; return 1; }
  done
}

cd $C
infer_un $C/ink-dataset/ref_12m/w035.zarr w035_0139 && for f in $C/predictions/pr28_w035_0139.tif $C/predictions/pr28_w035_0139_reverse.tif; do
  $PY $C/eval_12m.py $f $C/ink-dataset/0139/w035_2026031718/w035_2026031718_inklabels.zarr 3.9025; done
infer_un $C/ink-dataset/841_12m/segB.zarr segB_841 && for f in $C/predictions/pr28_segB_841.tif $C/predictions/pr28_segB_841_reverse.tif; do
  $PY $C/eval_12m.py $f $C/ink-dataset/841/canon_autres/auto_grown_20260220174252405/inklabels.zarr 3.8977; done
for v in $C/ink-dataset/0800/*/surface-volumes/*.zarr; do
  s=$(echo $v | sed 's#.*/0800/\([0-9]*\)-.*#\1#')
  infer_un $v p0800_$s && for f in $C/predictions/pr28_p0800_$s.tif $C/predictions/pr28_p0800_${s}_reverse.tif; do
    $PY $C/eval_12m.py $f - 0; done
done
echo "== PR-28 fini $(date +%F' '%T)"
