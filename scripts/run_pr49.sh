#!/bin/bash
# PR-49 : auto-apprentissage sur 1447 (le levier de l annonce du 24/09 : sans affinage sur le rouleau, quelques traits ;
# avec, une dizaine de lettres), juge a l aveugle contre la lecture des papyrologues. Attend la fin de PR-48, puis :
#   bras P : poids publies de Reader v2 + nos etiquettes humaines des 4 rouleaux (0814, 0841, 0009B, 0500P2, ancre 0139)
#            + pseudo-etiquettes du segment du texte de 1447 (tirees de la carte de Reader v2, seuils de PR-36) ;
#   bras T : la meme suite sans 1447 ;
# graines 42 et 43, 3 000 iterations ; cartes du segment du texte (1447_t) ; carte P42 du segment eloigne 1447_e
# (essai a blanc du format de lecture). Meme chaine que run_pr48.sh.
C=/home/slusarska_holding/vesuvius
PY=$C/villa/vesuvius/.venv/bin/python
TOT=3000
RV2=$C/checkpoints/reader_v2/reader-v2-step040000.pth
exec >> $C/logs/pr49.log 2>&1
echo "== PR-49 attend la fin de PR-48 $(date +%F' '%T)"
until grep -q "== PR-48 fini" $C/logs/pr48.log; do sleep 60; done
echo "== PR-49 demarre $(date +%F' '%T)"

entree () { local P9=$C/crops/pr31/$1_in.zarr
  if [ ! -d "$P9/0" ]; then rm -rf "$P9.partial"; cd $C/villa/vesuvius && $PY $C/prep_12m.py $C/ft12m/src/$1/vol.zarr "$P9" > /dev/null; fi; echo $P9; }
infere () { [ -s "$3" ] && [ -s "${3%.tif}_reverse.tif" ] && return 0
  local P9=$(entree $2); cd $C/villa/vesuvius && $PY -m vesuvius.ink_detection.inference.infer "$P9" "$1" "$3" \
    --overlap 0.5 --blend-mode hann --batch-size 4 --num-workers 4 --no-compile --direction both > /dev/null; }

for v in P42 T42 P43 T43; do
  g=${v:1}
  case ${v:0:1} in
    P) J='{"seed": '$g', "add0814": true, "checkpoint": "'$RV2'", "pseudo_extra": {"scroll": "1447", "segs": ["1447_t"], "dir": "'$C'/ft12m/pseudo1447"}, "counts": {"1447": 4, "0814": 2, "0841": 2, "0009B": 2, "0500P2": 2, "0139": 4}}';;
    T) J='{"seed": '$g', "add0814": true, "checkpoint": "'$RV2'", "counts": {"0814": 3, "0841": 3, "0009B": 3, "0500P2": 3, "0139": 4}}';;
  esac
  run=pr49_$v; RUN=$C/runs/$run; CFG=$C/configs/$run.json
  $PY $C/ft12m_config.py $CFG $TOT aucun $run "$J" > /dev/null
  for essai in 1 2 3; do
    [ -s $RUN/ckpt_003000.pth ] && break
    cfg=$CFG; d=$(ls $RUN/ckpt_*.pth 2>/dev/null | sort | tail -1)
    if [ -n "$d" ]; then cfg=$C/configs/${run}_reprise$essai.json
      $PY -c "import json; c=json.load(open('$CFG')); c['checkpoint']='$d'; c['weights_only']=False; json.dump(c,open('$cfg','w'),indent=1)"; fi
    echo "== $v essai $essai $(date +%T)"
    bash $C/train.sh "$cfg"
  done
  ck=$RUN/ckpt_003000.pth
  [ -s $ck ] || { echo "== ECHEC $v : pas de checkpoint 3000"; continue; }
  infere $ck 1447_t $C/predictions/pr49_${v}_1447_t.tif
  [ $v = P42 ] && infere $ck 1447_e $C/predictions/pr49_P42_1447_e.tif
  echo "== $v cartes faites $(date +%T)"
done
echo "== PR-49 fini $(date +%F' '%T)"
