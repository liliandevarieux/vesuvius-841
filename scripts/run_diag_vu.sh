#!/bin/bash
# Diagnostic (exploratoire, apres PR-32) : la recette PR-31 dessine-t-elle des traits sur des lettres qu elle A VUES ?
# Plis PR-31 appliques aux rouleaux de leur propre entrainement ; comparer a l allongement tenu a l ecart.
C=/home/slusarska_holding/vesuvius
PY=$C/villa/vesuvius/.venv/bin/python
exec >> $C/logs/diag_vu.log 2>&1
echo "== diagnostic demarre $(date +%F' '%T)"
for paire in "0841:0009B" "0841:0500P2" "0500P2:841_segB" "0500P2:0009B" "0009B:841_segB" "0009B:0500P2"; do
  pli=${paire%%:*}; s=${paire##*:}
  ck=$C/runs/pr31_sans$pli/ckpt_004000.pth; out=$C/predictions/diag_vu_sans${pli}_$s.tif
  P9=$C/crops/pr31/${s}_in.zarr
  if [ ! -s "$out" ]; then
    cd $C/villa/vesuvius && $PY -m vesuvius.ink_detection.inference.infer "$P9" "$ck" "$out" \
      --overlap 0.5 --blend-mode hann --batch-size 4 --num-workers 4 --no-compile --direction forward > /dev/null
  fi
  cd $C && [ -s "$out" ] && { $PY $C/eval_sup.py $out $s; $PY $C/eval_forme.py $out $s; } || echo "== ECHEC $out"
done
echo "== diagnostic fini $(date +%F' '%T)"
