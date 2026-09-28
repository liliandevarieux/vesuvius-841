#!/bin/bash
# PR-53 (a inscrire avant toute mesure) : la lisibilite monte-t-elle avec la duree d entrainement ? Cartes seulement :
# sauvegardes intermediaires (1 000, 2 000, 3 000 etapes) de R4, graines 42, 43 et 44, plis sans 0841 et sans 0009B,
# chacune sur le rouleau qu elle n a pas vu. Les cartes a 4 000 etapes existent deja (PR-34, PR-35, PR-48). Aucune
# mesure ici : detection et lecture a l aveugle viendront apres l inscription.
C=/home/slusarska_holding/vesuvius
PY=$C/villa/vesuvius/.venv/bin/python
exec >> $C/logs/pr53.log 2>&1
echo "== PR-53 cartes demarre $(date +%F' '%T)"
infere () { [ -s "$3" ] && [ -s "${3%.tif}_reverse.tif" ] && return 0
  cd $C/villa/vesuvius && $PY -m vesuvius.ink_detection.inference.infer "$C/crops/pr31/$2_in.zarr" "$1" "$3" \
    --overlap 0.5 --blend-mode hann --batch-size 4 --num-workers 4 --no-compile --direction both > /dev/null; }
for pli in 0841 0009B; do
  case $pli in 0841) test="841_w00 841_segA 841_segB";; *) test=$pli;; esac
  for r in pr34_R4 pr35_R43 pr48_R44; do
    g=${r#*_R}; [ $g = 4 ] && g=42
    for k in 1000 2000 3000; do
      ck=$C/runs/${r}_sans$pli/ckpt_00$k.pth
      [ -s $ck ] || { echo "== ECHEC $ck absent"; continue; }
      for s in $test; do
        OUT=$C/predictions/pr53_R${g}_${k}_${pli}_$s.tif
        for passe in 1 2; do infere $ck $s $OUT; done
        [ -s "$OUT" ] && [ -s "${OUT%.tif}_reverse.tif" ] || echo "== ECHEC $(basename $OUT) -- ne pas conclure"
      done
      echo "== graine $g, $k etapes, pli $pli fait $(date +%T)"
    done
  done
done
echo "== PR-53 cartes fini $(date +%F' '%T)"
