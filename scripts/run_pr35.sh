#!/bin/bash
# PR-35 : replication a la graine 43 des recettes PR-31 (B43) et PR-34 (R43), meme validation croisee rouleau par rouleau (841 / 0009B / 0500P2),
# 4 000 iterations ; mesure au checkpoint 4 000 : AUC dans la supervision ET allongement des lettres tenues a l ecart.
C=/home/slusarska_holding/vesuvius
PY=$C/villa/vesuvius/.venv/bin/python
TOT=4000
exec >> $C/logs/pr35.log 2>&1
echo "== PR-35 demarre $(date +%F' '%T)"

entree () { local P9=$C/crops/pr31/$1_in.zarr
  if [ ! -d "$P9/0" ]; then rm -rf "$P9.partial"; cd $C/villa/vesuvius && $PY $C/prep_12m.py $C/ft12m/src/$1/vol.zarr "$P9" > /dev/null; fi; echo $P9; }
infere () { [ -s "$3" ] && [ -s "${3%.tif}_reverse.tif" ] && return 0
  local P9=$(entree $2); cd $C/villa/vesuvius && $PY -m vesuvius.ink_detection.inference.infer "$P9" "$1" "$3" \
    --overlap 0.5 --blend-mode hann --batch-size 4 --num-workers 4 --no-compile --direction both > /dev/null; }
mesure () { cd $C; for f in $1 ${1%.tif}_reverse.tif; do
    [ -s "$f" ] && { $PY $C/eval_sup.py $f $2; $PY $C/eval_forme.py $f $2; } || echo "== ECHEC $(basename $f) absent -- ne pas conclure"; done; }

for v in B43 R43; do
  case $v in
    B43) J='{"seed": 43}';;
    R43) J='{"seed": 43, "add0814": true}';;
  esac
  for pli in 0841 0009B 0500P2; do
    case $pli in 0841) test="841_w00 841_segA 841_segB";; *) test=$pli;; esac
    run=pr35_${v}_sans$pli; RUN=$C/runs/$run; CFG=$C/configs/$run.json
    $PY $C/ft12m_config.py $CFG $TOT $pli $run "$J" > /dev/null
    for essai in 1 2 3; do
      n=$(ls $RUN/ckpt_*.pth 2>/dev/null | wc -l); [ -s $RUN/ckpt_004000.pth ] && break
      cfg=$CFG; d=$(ls $RUN/ckpt_*.pth 2>/dev/null | sort | tail -1)
      if [ -n "$d" ]; then cfg=$C/configs/${run}_reprise$essai.json
        $PY -c "import json; c=json.load(open('$CFG')); c['checkpoint']='$d'; c['weights_only']=False; json.dump(c,open('$cfg','w'),indent=1)"; fi
      echo "== $v pli $pli essai $essai $(date +%T)"
      bash $C/train.sh "$cfg"
    done
    ck=$RUN/ckpt_004000.pth
    [ -s $ck ] || { echo "== ECHEC $v pli $pli : pas de checkpoint 4000"; continue; }
    for s in $test; do infere $ck $s $C/predictions/pr35_${v}_${pli}_$s.tif; mesure $C/predictions/pr35_${v}_${pli}_$s.tif $s; done
  done
done
echo "== PR-35 fini $(date +%F' '%T)"
