#!/bin/bash
# PR-30 : affinage d ink_9um sur le type de scan 1,2 m, puis evaluation de chaque checkpoint sur le TEMOIN 0343P
# (jamais vu : ni par ink_9um, ni par cet affinage). Regles du projet cablees : chemins absolus, pas d evaluation
# pendant l entrainement, reprise complete jusqu a 5 fois apres une panne CUDA, sorties verifiees sur disque.
C=/home/slusarska_holding/vesuvius
PY=$C/villa/vesuvius/.venv/bin/python
TOT=${TOT:-6000}
CFG=$C/configs/pr30_ft12m.json
RUN=$C/runs/pr30_ft12m
exec >> $C/logs/pr30.log 2>&1
echo "== PR-30 demarre $(date +%F' '%T), $TOT iterations"
dernier() { ls $RUN/ckpt_*.pth 2>/dev/null | sort | tail -1; }
niter()  { local d=$(dernier); [ -n "$d" ] && echo $((10#$(basename "$d" .pth | sed 's/ckpt_//'))) || echo 0; }

for essai in 1 2 3 4 5 6; do
  n=$(niter)
  [ "$n" -ge "$TOT" ] && { echo "== entrainement complet a $n iterations"; break; }
  cfg=$CFG
  if [ "$n" -gt 0 ]; then
    cfg=$C/configs/pr30_ft12m_reprise$essai.json
    $PY -c "import json,sys; c=json.load(open('$CFG')); c['checkpoint']='$(dernier)'; c['weights_only']=False; json.dump(c,open('$cfg','w'),indent=1)"
  fi
  echo "== essai $essai : $cfg (depart a $n) $(date +%T)"
  bash $C/train.sh "$cfg"
  echo "== essai $essai rendu $(date +%T), on est a $(niter) iterations"
  [ "$(niter)" -le "$n" ] && { echo "== AUCUN PROGRES, arret des relances"; break; }
done

echo "== evaluation sur le temoin 0343P $(date +%T)"
P9=$C/crops/pr28/p343_in.zarr
for passe in 1 2; do                                   # passe 2 = reparation
  for ck in $RUN/ckpt_*.pth; do
    k=$(basename $ck .pth)
    OUT=$C/predictions/pr30_p343_$k.tif
    if [ ! -s "$OUT" ] || [ ! -s "${OUT%.tif}_reverse.tif" ]; then
      cd $C/villa/vesuvius && $PY -m vesuvius.ink_detection.inference.infer "$P9" "$ck" "$OUT" \
        --overlap 0.5 --blend-mode hann --batch-size 4 --num-workers 4 --no-compile --direction both > /dev/null
    fi
  done
done
cd $C
for ck in $RUN/ckpt_*.pth; do
  k=$(basename $ck .pth)
  for f in $C/predictions/pr30_p343_$k.tif $C/predictions/pr30_p343_${k}_reverse.tif; do
    [ -s "$f" ] && $PY $C/eval_12m.py $f $C/ink-dataset/p343/20250511003658_inklabels.zarr 3.901 || echo "== ECHEC $f absent -- ne pas conclure"
  done
done
echo "--- rappel : PRIMAIRE = dernier checkpoint ($TOT) ; AUC >= 0,80 dans le sens choisi sans etiquette ET formes de lettres ---"
echo "== PR-30 fini $(date +%F' '%T)"
