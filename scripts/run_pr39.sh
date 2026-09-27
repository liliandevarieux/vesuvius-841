#!/bin/bash
# PR-39 : meme rouleau, autre feuillet. La recette PR-34 ou le quatrieme rouleau (0814 x4 par lot) est remplace par le
# ou les autres feuillets de 841 (841 x4 par lot). w00 et segA se touchent dans le rouleau (recouvrement_841.py) :
#   pli B  = segB tenu a l ecart, entrainement avec w00 + segA ;
#   pli WA = w00 et segA tenus a l ecart, entrainement avec segB seul (un modele par graine, mesure sur les deux).
# Graines 42 et 43, 4 000 iterations, depart ink_9um graine 42 etape 75 000 (poids seuls), comme PR-34 / PR-35.
# Temoins deja mesures (fixes dans l enregistrement) : pr34_R4_0841_* (graine 42) et pr35_R43_0841_* (graine 43).
# Regles du projet cablees : chemins absolus, pas d evaluation pendant l entrainement, reprise apres panne CUDA,
# passe de reparation des inferences, sorties verifiees sur disque (« ECHEC ... ne pas conclure » sinon).
C=/home/slusarska_holding/vesuvius
PY=$C/villa/vesuvius/.venv/bin/python
TOT=4000
exec >> $C/logs/pr39.log 2>&1
echo "== PR-39 demarre $(date +%F' '%T)"

entree () { local P9=$C/crops/pr31/$1_in.zarr
  if [ ! -d "$P9/0" ]; then rm -rf "$P9.partial"; cd $C/villa/vesuvius && $PY $C/prep_12m.py $C/ft12m/src/$1/vol.zarr "$P9" > /dev/null; fi; echo $P9; }
infere () { [ -s "$3" ] && [ -s "${3%.tif}_reverse.tif" ] && return 0
  local P9=$(entree $2); cd $C/villa/vesuvius && $PY -m vesuvius.ink_detection.inference.infer "$P9" "$1" "$3" \
    --overlap 0.5 --blend-mode hann --batch-size 4 --num-workers 4 --no-compile --direction both > /dev/null; }
mesure () { cd $C; for f in $1 ${1%.tif}_reverse.tif; do
    [ -s "$f" ] && { $PY $C/eval_sup.py $f $2; $PY $C/eval_forme.py $f $2; $PY $C/eval_forme_fond.py $f $2; } \
      || echo "== ECHEC $(basename $f) absent -- ne pas conclure"; done; }

for graine in 42 43; do
  for pli in B WA; do
    case $pli in
      B)  F='["841_w00", "841_segA"]'; test="841_segB";;
      WA) F='["841_segB"]';            test="841_w00 841_segA";;
    esac
    run=pr39_${pli}${graine}; RUN=$C/runs/$run; CFG=$C/configs/$run.json
    $PY $C/ft12m_config.py $CFG $TOT aucun $run \
      "{\"seed\": $graine, \"sheets_841\": $F, \"counts\": {\"0841\": 4, \"0009B\": 4, \"0500P2\": 4, \"0139\": 4}}" > /dev/null
    dernier() { ls $RUN/ckpt_*.pth 2>/dev/null | sort | tail -1; }
    niter()  { local d=$(dernier); [ -n "$d" ] && echo $((10#$(basename "$d" .pth | sed 's/ckpt_//'))) || echo 0; }
    for essai in 1 2 3 4; do
      n=$(niter); [ "$n" -ge "$TOT" ] && break
      cfg=$CFG
      if [ "$n" -gt 0 ]; then cfg=$C/configs/${run}_reprise$essai.json
        $PY -c "import json; c=json.load(open('$CFG')); c['checkpoint']='$(dernier)'; c['weights_only']=False; json.dump(c,open('$cfg','w'),indent=1)"; fi
      echo "== pli $pli graine $graine essai $essai (depart $n) $(date +%T)"
      bash $C/train.sh "$cfg"
      [ "$(niter)" -le "$n" ] && { echo "== pli $pli graine $graine AUCUN PROGRES"; break; }
    done
    k=ckpt_$(printf %06d $TOT)
    [ -s $RUN/$k.pth ] || { echo "== ECHEC $run sans $k -- ne pas conclure"; continue; }
    for s in $test; do
      for passe in 1 2; do infere $RUN/$k.pth $s $C/predictions/${run}_$s.tif; done
      mesure $C/predictions/${run}_$s.tif $s
    done
  done
done
echo "--- rappel : PRIMAIRE = moyenne sur 3 feuillets x 2 graines, sens choisi sans etiquette (p99-p50) ; W - C >= +2,0 en"
echo "--- allongement ET AUC W >= AUC C - 0,01 ; temoins pr34_R4_0841_* (42) et pr35_R43_0841_* (43) : 11,38 / 0,7798 ---"
echo "== PR-39 fini $(date +%F' '%T)"
