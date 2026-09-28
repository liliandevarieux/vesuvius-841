#!/bin/bash
# PR-53, mesure rapportee sans juger (regle 1) : detection (eval_sup.py, AUC sur la supervision) de chaque sauvegarde
# de R4 (1 000, 2 000, 3 000 et 4 000 etapes ; graines 42, 43, 44) sur les trois feuillets de 841 et sur 0009B, dans
# les deux sens des couches. Le sens retenu est celui au p99-p50 le plus haut, comme au banc. Processeur seulement.
C=/home/slusarska_holding/vesuvius
PY=$C/villa/vesuvius/.venv/bin/python
exec >> $C/logs/pr53_detection.log 2>&1
echo "== PR-53 detection demarre $(date +%F' '%T)"
cd $C
for pli in 0841 0009B; do
  case $pli in 0841) test="841_w00 841_segA 841_segB";; *) test=$pli;; esac
  for s in $test; do
    for f in pr53_R42_1000 pr53_R43_1000 pr53_R44_1000 pr53_R42_2000 pr53_R43_2000 pr53_R44_2000 \
             pr53_R42_3000 pr53_R43_3000 pr53_R44_3000 pr34_R4 pr35_R43 pr48_R44; do
      for d in "" _reverse; do
        g=$C/predictions/${f}_${pli}_$s$d.tif
        [ -s "$g" ] && $PY $C/eval_sup.py $g $s || echo "== ECHEC $(basename $g) absent -- ne pas conclure"
      done
    done
  done
done
echo "== PR-53 detection fini $(date +%F' '%T)"
