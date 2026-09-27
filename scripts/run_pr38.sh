#!/bin/bash
# PR-38 : plus de lettres a l aspect du scan eligible. Validation croisee de PR-31 (depart ink_9um s42 75k, 4 000 it.),
# le melange de chaque pli recoit en plus le corpus d entrainement d ink_9um (24 segments 2,4 um poole ~9,6 um, 4 rouleaux)
#   B = corpus FLOUTE (ft12m_flou.py : sigma 0,70 couche, 0,69 px) ; U = corpus net (tel qu ink_9um l a vu).
# Lot de 16 : les deux rouleaux 1,2 m du pli 3 + 3, 0139 3 (w035 natif + 9 alignes), 1667 3, Paris4 3, 0814 1.
# Graines 42 et 43 ; temoin = recette PR-31 aux memes graines (PR-31 s42, PR-35 B43). Attend PR-37 et le telechargement.
C=/home/slusarska_holding/vesuvius
PY=$C/villa/vesuvius/.venv/bin/python
TOT=4000
K=$C/ft12m/corpus24
KF=$C/ft12m/corpus24_flou
exec >> $C/logs/pr38.log 2>&1
until grep -q "PR-37 fini" $C/logs/pr37.log && grep -q "== fin" $C/logs/dl_corpus24.log; do sleep 60; done
echo "== PR-38 demarre $(date +%F' '%T)"
SEGS=$(ls -d $K/*/surface-volume.zarr/.ok 2>/dev/null | sed "s#$K/##; s#/surface-volume.zarr/.ok##" | tr '\n' ' ')
echo "== corpus : $(echo $SEGS | wc -w) segments : $SEGS"
for s in $SEGS; do
  mkdir -p $KF/$s
  [ -d $KF/$s/surface-volume.zarr/0 ] || nice -n 5 $PY $C/ft12m_flou.py $K/$s/surface-volume.zarr $KF/$s/surface-volume.zarr
done
LISTE=$(printf '"%s",' $SEGS); LISTE="[${LISTE%,}]"

segs () { case $1 in 0841) echo "841_w00 841_segA 841_segB";; *) echo $1;; esac; }
entree () {
  local P9=$C/crops/pr31/$1_in.zarr
  if [ ! -d "$P9/0" ]; then rm -rf "$P9.partial"; cd $C/villa/vesuvius && $PY $C/prep_12m.py $C/ft12m/src/$1/vol.zarr "$P9" > /dev/null; fi
  echo $P9
}
infere () {
  [ -s "$3" ] && [ -s "${3%.tif}_reverse.tif" ] && return 0
  local P9=$(entree $2)
  cd $C/villa/vesuvius && $PY -m vesuvius.ink_detection.inference.infer "$P9" "$1" "$3" \
    --overlap 0.5 --blend-mode hann --batch-size 4 --num-workers 4 --no-compile --direction both > /dev/null
}
mesure () {
  cd $C
  for f in $1 ${1%.tif}_reverse.tif; do
    if [ -s "$f" ]; then $PY $C/eval_sup.py $f $2; $PY $C/eval_forme.py $f $2; $PY $C/eval_forme_fond.py $f $2
    else echo "== ECHEC $(basename $f) absent -- ne pas conclure"; fi
  done
}

for bras in B U; do
for graine in 42 43; do
for pli in 0841 0009B 0500P2; do
  case $pli in
    0841)   N='"0009B": 3, "0500P2": 3';;
    0009B)  N='"0841": 3, "0500P2": 3';;
    0500P2) N='"0841": 3, "0009B": 3';;
  esac
  if [ $bras = B ]; then KV="\"vol_dir\": \"$KF\", \"suffixe\": \"_flou\""; else KV="\"vol_dir\": \"$K\""; fi
  V="{\"seed\": $graine, \"counts\": {$N, \"0139\": 3, \"1667\": 3, \"Paris4\": 3, \"0814\": 1}, \"corpus\": {\"dir\": \"$K\", $KV, \"segs\": $LISTE}}"
  run=pr38_${bras}${graine}_$pli; RUN=$C/runs/$run; CFG=$C/configs/$run.json
  $PY $C/ft12m_config.py $CFG $TOT $pli $run "$V" > /dev/null
  dernier() { ls $RUN/ckpt_*.pth 2>/dev/null | sort | tail -1; }
  niter()  { local d=$(dernier); [ -n "$d" ] && echo $((10#$(basename "$d" .pth | sed 's/ckpt_//'))) || echo 0; }
  for essai in 1 2 3 4; do
    n=$(niter); [ "$n" -ge "$TOT" ] && break
    cfg=$CFG
    if [ "$n" -gt 0 ]; then cfg=$C/configs/${run}_reprise$essai.json
      $PY -c "import json; c=json.load(open('$CFG')); c['checkpoint']='$(dernier)'; c['weights_only']=False; json.dump(c,open('$cfg','w'),indent=1)"; fi
    echo "== $bras$graine pli $pli essai $essai (depart $n) $(date +%T)"
    bash $C/train.sh "$cfg"
    [ "$(niter)" -le "$n" ] && { echo "== $bras$graine pli $pli AUCUN PROGRES"; break; }
  done
  k=ckpt_$(printf %06d $TOT)
  [ -s $RUN/$k.pth ] || { echo "== ECHEC $run sans $k -- ne pas conclure"; continue; }
  for s in $(segs $pli); do
    for passe in 1 2; do infere $RUN/$k.pth $s $C/predictions/${run}_$s.tif; done
    mesure $C/predictions/${run}_$s.tif $s
  done
done
done
done
echo "--- rappel : PRIMAIRE = B contre temoin PR-31/PR-35 B43, 5 segments x 2 graines, sens sans etiquette ; lettres +2,0, lettres-fond +1,0, AUC >= -0,01 ---"
echo "== PR-38 fini $(date +%F' '%T)"
