#!/bin/bash
# PR-48 : notre recette R4 (PR-34 : ft12m + 0814, 4 000 iterations) partant des poids publies de Reader v2
# (V42, V43, V44 = « RV2+ »), et la 3e graine de R4 partant d ink_9um (R44) ; plis 0841 et 0009B seulement (les
# lettres lues sont sur 841 et 0009B). Cartes sur le rouleau tenu a l ecart ; detection (eval_sup) et allongement
# (descriptif, ne juge rien : notes/14-methode.md, regle 1). Meme chaine que run_pr35.sh.
C=/home/slusarska_holding/vesuvius
PY=$C/villa/vesuvius/.venv/bin/python
TOT=4000
RV2=$C/checkpoints/reader_v2/reader-v2-step040000.pth
exec >> $C/logs/pr48.log 2>&1
echo "== PR-48 demarre $(date +%F' '%T)"

entree () { local P9=$C/crops/pr31/$1_in.zarr
  if [ ! -d "$P9/0" ]; then rm -rf "$P9.partial"; cd $C/villa/vesuvius && $PY $C/prep_12m.py $C/ft12m/src/$1/vol.zarr "$P9" > /dev/null; fi; echo $P9; }
infere () { [ -s "$3" ] && [ -s "${3%.tif}_reverse.tif" ] && return 0
  local P9=$(entree $2); cd $C/villa/vesuvius && $PY -m vesuvius.ink_detection.inference.infer "$P9" "$1" "$3" \
    --overlap 0.5 --blend-mode hann --batch-size 4 --num-workers 4 --no-compile --direction both > /dev/null; }
mesure () { cd $C; for f in $1 ${1%.tif}_reverse.tif; do
    [ -s "$f" ] && { $PY $C/eval_sup.py $f $2; $PY $C/eval_forme.py $f $2; } || echo "== ECHEC $(basename $f) absent -- ne pas conclure"; done; }

# ordre : une graine de RV2+ et la graine de R4 d abord, pour que chaque recette ait vite une carte par pli
for v in V42 R44 V43 V44; do
  case $v in
    V42) J='{"seed": 42, "add0814": true, "checkpoint": "'$RV2'"}';;
    V43) J='{"seed": 43, "add0814": true, "checkpoint": "'$RV2'"}';;
    V44) J='{"seed": 44, "add0814": true, "checkpoint": "'$RV2'"}';;
    R44) J='{"seed": 44, "add0814": true}';;
  esac
  for pli in 0841 0009B; do
    case $pli in 0841) test="841_w00 841_segA 841_segB";; *) test=$pli;; esac
    run=pr48_${v}_sans$pli; RUN=$C/runs/$run; CFG=$C/configs/$run.json
    $PY $C/ft12m_config.py $CFG $TOT $pli $run "$J" > /dev/null
    for essai in 1 2 3; do
      [ -s $RUN/ckpt_004000.pth ] && break
      cfg=$CFG; d=$(ls $RUN/ckpt_*.pth 2>/dev/null | sort | tail -1)
      if [ -n "$d" ]; then cfg=$C/configs/${run}_reprise$essai.json
        $PY -c "import json; c=json.load(open('$CFG')); c['checkpoint']='$d'; c['weights_only']=False; json.dump(c,open('$cfg','w'),indent=1)"; fi
      echo "== $v pli $pli essai $essai $(date +%T)"
      bash $C/train.sh "$cfg"
    done
    ck=$RUN/ckpt_004000.pth
    [ -s $ck ] || { echo "== ECHEC $v pli $pli : pas de checkpoint 4000"; continue; }
    for s in $test; do infere $ck $s $C/predictions/pr48_${v}_${pli}_$s.tif; mesure $C/predictions/pr48_${v}_${pli}_$s.tif $s; done
  done
done
echo "== PR-48 fini $(date +%F' '%T)"
