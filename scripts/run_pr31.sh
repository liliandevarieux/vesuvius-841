#!/bin/bash
# PR-31 : validation croisee rouleau par rouleau sur le type de scan 1,2 m. Pour chaque rouleau (841, 0009B, 0500P2) :
# affinage d ink_9um (s42 75k) sur les deux autres + ancre 0139 w035, 4 000 iterations, puis AUC dans la zone de
# supervision du rouleau laisse de cote, contre ink_9um publie sur le meme rouleau. 0343P n est PAS utilise.
C=/home/slusarska_holding/vesuvius
PY=$C/villa/vesuvius/.venv/bin/python
CK0=$C/checkpoints/ink_9um/hybrid_3d2d-seed42/step-075000.pth
TOT=4000
exec >> $C/logs/pr31.log 2>&1
echo "== PR-31 demarre $(date +%F' '%T)"
mkdir -p $C/crops/pr31

entree () {  # $1 segment -> chemin de l entree 21 couches
  local P9=$C/crops/pr31/$1_in.zarr
  if [ ! -d "$P9/0" ]; then rm -rf "$P9.partial"; cd $C/villa/vesuvius && $PY $C/prep_12m.py $C/ft12m/src/$1/vol.zarr "$P9" > /dev/null; fi
  echo $P9
}
infere () {  # $1 checkpoint, $2 segment, $3 sortie
  [ -s "$3" ] && [ -s "${3%.tif}_reverse.tif" ] && return 0
  local P9=$(entree $2)
  cd $C/villa/vesuvius && $PY -m vesuvius.ink_detection.inference.infer "$P9" "$1" "$3" \
    --overlap 0.5 --blend-mode hann --batch-size 4 --num-workers 4 --no-compile --direction both > /dev/null
}
mesure () {  # $1 carte, $2 segment
  for f in $1 ${1%.tif}_reverse.tif; do
    [ -s "$f" ] && $PY $C/eval_sup.py $f $2 || echo "== ECHEC $(basename $f) absent -- ne pas conclure"
  done
}

echo "== reference : ink_9um publie $(date +%T)"
for s in 841_w00 841_segA 841_segB 0009B 0500P2; do
  infere $CK0 $s $C/predictions/pr31_base_$s.tif; mesure $C/predictions/pr31_base_$s.tif $s
done

for pli in 0841 0009B 0500P2; do
  case $pli in 0841) test="841_w00 841_segA 841_segB";; *) test=$pli;; esac
  run=pr31_sans$pli; RUN=$C/runs/$run; CFG=$C/configs/$run.json
  $PY $C/ft12m_config.py $CFG $TOT $pli $run > /dev/null
  dernier() { ls $RUN/ckpt_*.pth 2>/dev/null | sort | tail -1; }
  niter()  { local d=$(dernier); [ -n "$d" ] && echo $((10#$(basename "$d" .pth | sed 's/ckpt_//'))) || echo 0; }
  for essai in 1 2 3 4; do
    n=$(niter); [ "$n" -ge "$TOT" ] && break
    cfg=$CFG
    if [ "$n" -gt 0 ]; then cfg=$C/configs/${run}_reprise$essai.json
      $PY -c "import json; c=json.load(open('$CFG')); c['checkpoint']='$(dernier)'; c['weights_only']=False; json.dump(c,open('$cfg','w'),indent=1)"; fi
    echo "== pli $pli essai $essai (depart $n) $(date +%T)"
    bash $C/train.sh "$cfg"
    [ "$(niter)" -le "$n" ] && { echo "== pli $pli AUCUN PROGRES"; break; }
  done
  echo "== pli $pli entraine a $(niter) iterations, test sur $test $(date +%T)"
  for ck in $RUN/ckpt_*.pth; do
    k=$(basename $ck .pth)
    for s in $test; do infere $ck $s $C/predictions/pr31_${pli}_${k}_$s.tif; mesure $C/predictions/pr31_${pli}_${k}_$s.tif $s; done
  done
done
echo "--- rappel : PRIMAIRE = checkpoint 4000 de chaque pli, sens choisi sans etiquette ; gain >= +0,03 sur >= 2 plis sur 3 ---"
echo "== PR-31 fini $(date +%F' '%T)"
