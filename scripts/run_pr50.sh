#!/bin/bash
# PR-50 : le gain de detection de notre affinage (R4) depasse-t-il la loterie des sauvegardes d ink_9um elle-meme ?
# La seconde sauvegarde finale d ink_9um (graine 43, etape 75 000, deja sur le disque) passe sur les cinq segments tenus
# a l ecart, avec la meme chaine que PR-31 et PR-48 (entrees crops/pr31, deux sens ; le sens se choisit sans etiquette,
# par p99-p50, au depouillement). Puis la moyenne pixel a pixel des cartes graine 42 (pr31_base_*) et graine 43.
# Detection : eval_sup.py, comme pour R4. Attend la fin de PR-49 (carte graphique).
C=/home/slusarska_holding/vesuvius
PY=$C/villa/vesuvius/.venv/bin/python
B43=$C/checkpoints/ink_9um/hybrid_3d2d-seed43/step-075000.pth
exec >> $C/logs/pr50.log 2>&1
echo "== PR-50 attend la fin de PR-49 $(date +%F' '%T)"
until grep -q "== PR-49 fini" $C/logs/pr49.log; do sleep 60; done
echo "== PR-50 demarre $(date +%F' '%T)"

entree () { local P9=$C/crops/pr31/$1_in.zarr
  if [ ! -d "$P9/0" ]; then rm -rf "$P9.partial"; cd $C/villa/vesuvius && $PY $C/prep_12m.py $C/ft12m/src/$1/vol.zarr "$P9" > /dev/null; fi; echo $P9; }
infere () { [ -s "$3" ] && [ -s "${3%.tif}_reverse.tif" ] && return 0
  local P9=$(entree $2); cd $C/villa/vesuvius && $PY -m vesuvius.ink_detection.inference.infer "$P9" "$1" "$3" \
    --overlap 0.5 --blend-mode hann --batch-size 4 --num-workers 4 --no-compile --direction both > /dev/null; }
mesure () { cd $C; for f in $1 ${1%.tif}_reverse.tif; do
    [ -s "$f" ] && $PY $C/eval_sup.py $f $2 || echo "== ECHEC $(basename $f) absent -- ne pas conclure"; done; }

for s in 841_w00 841_segA 841_segB 0009B 0500P2; do
  echo "== $s $(date +%T)"
  infere $B43 $s $C/predictions/pr50_base43_$s.tif
  mesure $C/predictions/pr50_base43_$s.tif $s
  for d in "" _reverse; do
    $PY $C/moyenne_cartes.py $C/predictions/pr31_base_$s$d.tif $C/predictions/pr50_base43_$s$d.tif $C/predictions/pr50_moy_$s$d.tif
  done
  mesure $C/predictions/pr50_moy_$s.tif $s
done
echo "== PR-50 fini $(date +%F' '%T)"
