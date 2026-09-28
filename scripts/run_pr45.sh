#!/bin/bash
# PR-45 : Reader v2 sur le segment etiquete de 0009B (20250919125754), absent de son entrainement, scanne comme 0800 et
# 1447 (8,64 um, 116 keV) : ses lettres jamais vues sont-elles des traits ? Meme CLI et memes entrees 21 couches que
# PR-31 a PR-44, deux sens, sens choisi sans etiquette ; mesures eval_sup / eval_forme / eval_forme_fond. Pour memoire,
# les memes mesures sur les cartes deja faites (base ink_9um, pli PR-31 sans 0009B, pli R4 de PR-34 sans 0009B).
# Puis le panneau lettre par lettre, que l auteur regarde avant de donner un chiffre.
C=/home/slusarska_holding/vesuvius
PY=$C/villa/vesuvius/.venv/bin/python
CK=$C/checkpoints/reader_v2/reader-v2-step040000.pth
s=0009B
exec >> $C/logs/pr45.log 2>&1
echo "== PR-45 demarre $(date +%F' '%T)"
P9=$C/crops/pr31/${s}_in.zarr; OUT=$C/predictions/pr45_readerv2_$s.tif
[ -d "$P9/0" ] || { echo "== ECHEC entree $P9 absente -- ne pas conclure"; exit 1; }
for passe in 1 2; do
  if [ ! -s "$OUT" ] || [ ! -s "${OUT%.tif}_reverse.tif" ]; then
    cd $C/villa/vesuvius && $PY -m vesuvius.ink_detection.inference.infer "$P9" "$CK" "$OUT" \
      --overlap 0.5 --blend-mode hann --batch-size 4 --num-workers 4 --no-compile --direction both > /dev/null
  fi
done
cd $C
for m in pr45_readerv2_$s pr31_base_$s pr31_0009B_ckpt_004000_$s pr34_R4_0009B_$s; do
  for f in $C/predictions/$m.tif $C/predictions/${m}_reverse.tif; do
    [ -s "$f" ] && { $PY $C/eval_sup.py $f $s; $PY $C/eval_forme.py $f $s; $PY $C/eval_forme_fond.py $f $s; } \
      || echo "== ECHEC $(basename $f) absent -- ne pas conclure"
  done
done
echo "--- rappel : PRIMAIRE = allongement de Reader v2 (sens choisi sans etiquette) >= 16,0 ET > son allongement du fond ---"
$PY $C/panneau_lettres_841.py $s "/mnt/c/Users/SLUSARSKA HOLDING/vesuvius/images/2026-09-28_pr45_0009B_lettres.png" \
  "base ink_9um=$C/predictions/pr31_base_$s.tif" "notre R4 sans 0009B=$C/predictions/pr34_R4_0009B_$s.tif" \
  "Reader v2=$OUT"
echo "== PR-45 fini $(date +%F' '%T)"
