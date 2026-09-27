#!/bin/bash
# PR-37 : comme le bras P de PR-36, mais seules les pseudo-etiquettes d encre EN FORME DE TRAIT (composantes d allongement
# >= 16) restent encre ; les taches rondes deviennent inconnues. Bras Q, graines 42 et 43, depart = modele du pli ;
# temoin = bras T de PR-36 (memes graines, meme depart, meme duree). Attend la fin de PR-36 (un seul processus GPU).
C=/home/slusarska_holding/vesuvius
PY=$C/villa/vesuvius/.venv/bin/python
TOT=3000
PS=$C/ft12m/labels_pseudo37
exec >> $C/logs/pr37.log 2>&1
until grep -q "PR-36 fini" $C/logs/pr36.log; do sleep 60; done
echo "== PR-37 demarre $(date +%F' '%T)"
mkdir -p $C/crops/pr31 $PS
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

echo "== pseudo-etiquettes $(date +%T)"
for pli in 0841 0009B 0500P2; do
  for s in $(segs $pli); do
    [ -d $PS/$pli/$s/${s}_supervision_mask.zarr ] || $PY $C/ft12m_pseudo.py $s $C/predictions/pr31_${pli}_ckpt_004000_$s.tif $PS/$pli 16
  done
done

for graine in 42 43; do
for pli in 0841 0009B 0500P2; do
  case $pli in
    0841)   P='{"0841": 4, "0009B": 4, "0500P2": 4, "0139": 4}';;
    0009B)  P='{"0009B": 4, "0841": 4, "0500P2": 4, "0139": 4}';;
    0500P2) P='{"0500P2": 4, "0841": 4, "0009B": 4, "0139": 4}';;
  esac
  CK=$C/runs/pr31_sans$pli/ckpt_004000.pth
  for bras in Q; do
    run=pr37_${bras}${graine}_$pli; RUN=$C/runs/$run; CFG=$C/configs/$run.json
    if [ $bras = Q ]; then V="{\"seed\": $graine, \"checkpoint\": \"$CK\", \"pseudo_dir\": \"$PS/$pli\", \"counts\": $P}"
    else V="{\"seed\": $graine, \"checkpoint\": \"$CK\"}"; fi
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
echo "--- rappel : PRIMAIRE = moyenne sur 5 segments et 2 graines, sens choisi sans etiquette ; Q - T(PR-36) >= +2,0 en allongement lettres ET >= +1,0 de plus que sur le fond ET AUC Q >= AUC T - 0,01 ---"
echo "== PR-37 fini $(date +%F' '%T)"
