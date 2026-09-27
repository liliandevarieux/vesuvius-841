#!/bin/bash
# Nuit du 27 au 28/09 : file enchainee apres PR-39 (Lilian : « enchaine un maximum d entrainements cette nuit »).
# PR-40 : PR-39 repliquee aux graines 44 et 45, avec ses temoins (recette PR-34 : 0814 a la place de 841) aux memes graines.
# PR-41 : combien de lettres du meme rouleau ? segB tenu a l ecart, entrainement avec UN seul autre feuillet (w00 ou segA).
# PR-42 : le modele « tous rouleaux » (l outil d octobre), juge sur le temoin 0343P ; et les modeles des plis sur 0343P.
# PR-43 : entrainement deux fois plus long (8 000 iterations) pour le pli B et son temoin, mesure a 4 000 et 8 000.
# Attend la fin de PR-39 : deux entrainements ne tiennent pas ensemble sur 8 Go. Regles du projet cablees : chemins
# absolus, reprise apres panne CUDA, passe de reparation des inferences, sorties verifiees (« ECHEC ... ne pas
# conclure » sinon) ; chaque etape saute ce qui existe deja, donc la file se relance telle quelle apres une coupure.
C=/home/slusarska_holding/vesuvius
PY=$C/villa/vesuvius/.venv/bin/python
exec >> $C/logs/nuit_2728.log 2>&1
echo "== file de nuit en attente de PR-39 $(date +%F' '%T)"
while pgrep -f "[r]un_pr39.sh" > /dev/null; do sleep 60; done
echo "== PR-39 termine, file de nuit demarre $(date +%F' '%T)"

K='"counts": {"0841": 4, "0009B": 4, "0500P2": 4, "0139": 4}'
entree () { local P9=$C/crops/pr31/$1_in.zarr
  if [ ! -d "$P9/0" ]; then rm -rf "$P9.partial"; cd $C/villa/vesuvius && $PY $C/prep_12m.py $C/ft12m/src/$1/vol.zarr "$P9" > /dev/null; fi; echo $P9; }
infere () { [ -s "$3" ] && [ -s "${3%.tif}_reverse.tif" ] && return 0
  local P9=$(entree $2); cd $C/villa/vesuvius && $PY -m vesuvius.ink_detection.inference.infer "$P9" "$1" "$3" \
    --overlap 0.5 --blend-mode hann --batch-size 4 --num-workers 4 --no-compile --direction both > /dev/null; }
mesure () { cd $C; for f in $1 ${1%.tif}_reverse.tif; do
    [ -s "$f" ] && { $PY $C/eval_sup.py $f $2; $PY $C/eval_forme.py $f $2; $PY $C/eval_forme_fond.py $f $2; } \
      || echo "== ECHEC $(basename $f) absent -- ne pas conclure"; done; }
ckn () { ls $C/runs/$1/ckpt_*.pth 2>/dev/null | sort | tail -1; }
nit () { local d=$(ckn $1); [ -n "$d" ] && echo $((10#$(basename "$d" .pth | sed 's/ckpt_//'))) || echo 0; }

entraine () {   # entraine RUN ITERATIONS ROULEAU_EXCLU JSON
  local run=$1 tot=$2 cfg0=$C/configs/$1.json
  $PY $C/ft12m_config.py $cfg0 $tot $3 $run "$4" > /dev/null
  for essai in 1 2 3 4; do
    local n=$(nit $run); [ "$n" -ge "$tot" ] && break
    local cfg=$cfg0
    if [ "$n" -gt 0 ]; then cfg=$C/configs/${run}_reprise$essai.json
      $PY -c "import json; c=json.load(open('$cfg0')); c['checkpoint']='$(ckn $run)'; c['weights_only']=False; json.dump(c,open('$cfg','w'),indent=1)"; fi
    echo "== $run essai $essai (depart $n) $(date +%T)"
    bash $C/train.sh "$cfg"
    [ "$(nit $run)" -le "$n" ] && { echo "== $run AUCUN PROGRES"; break; }
  done
  [ -s $C/runs/$run/ckpt_$(printf %06d $tot).pth ] || { echo "== ECHEC $run incomplet -- ne pas conclure"; return 1; }
}
feuillets () {  # feuillets RUN CHECKPOINT FEUILLET...
  local run=$1 k=$(printf %06d $2); shift 2
  for s in "$@"; do
    for passe in 1 2; do infere $C/runs/$run/ckpt_$k.pth $s $C/predictions/${run}_ck${k}_$s.tif; done
    mesure $C/predictions/${run}_ck${k}_$s.tif $s
  done
}
p343 () {       # p343 RUN CHECKPOINT : temoin 0343P (meme scan que 0800), comme PR-29 / PR-30
  local k=$(printf %06d $2); local ck=$C/runs/$1/ckpt_$k.pth OUT=$C/predictions/p343_$1_ck$k.tif P9=$C/crops/pr28/p343_in.zarr
  [ -s $ck ] || { echo "== ECHEC $ck absent -- ne pas conclure"; return; }
  for passe in 1 2; do
    if [ ! -s "$OUT" ] || [ ! -s "${OUT%.tif}_reverse.tif" ]; then
      cd $C/villa/vesuvius && $PY -m vesuvius.ink_detection.inference.infer "$P9" "$ck" "$OUT" \
        --overlap 0.5 --blend-mode hann --batch-size 4 --num-workers 4 --no-compile --direction both > /dev/null
    fi
  done
  cd $C
  for f in $OUT ${OUT%.tif}_reverse.tif; do
    [ -s "$f" ] && $PY $C/eval_12m.py $f $C/ink-dataset/p343/20250511003658_inklabels.zarr 3.901 \
      || echo "== ECHEC $(basename $f) absent -- ne pas conclure"
  done
}

echo "== PR-40 demarre $(date +%T)"
for g in 44 45; do
  entraine pr40_C${g}_sans0841 4000 0841 "{\"add0814\": true, \"seed\": $g}" && feuillets pr40_C${g}_sans0841 4000 841_w00 841_segA 841_segB
  entraine pr40_B$g 4000 aucun "{\"seed\": $g, \"sheets_841\": [\"841_w00\", \"841_segA\"], $K}" && feuillets pr40_B$g 4000 841_segB
  entraine pr40_WA$g 4000 aucun "{\"seed\": $g, \"sheets_841\": [\"841_segB\"], $K}" && feuillets pr40_WA$g 4000 841_w00 841_segA
done
echo "== PR-40 fini $(date +%T)"

echo "== PR-41 demarre $(date +%T)"
for g in 42 43; do
  entraine pr41_Bw$g 4000 aucun "{\"seed\": $g, \"sheets_841\": [\"841_w00\"], $K}" && feuillets pr41_Bw$g 4000 841_segB
  entraine pr41_Ba$g 4000 aucun "{\"seed\": $g, \"sheets_841\": [\"841_segA\"], $K}" && feuillets pr41_Ba$g 4000 841_segB
done
echo "== PR-41 fini $(date +%T)"

echo "== PR-42 demarre $(date +%T)"
for g in 42 43; do
  entraine pr42_tout$g 4000 aucun "{\"add0814\": true, \"seed\": $g}" && for k in 1000 2000 3000 4000; do p343 pr42_tout$g $k; done
done
for r in pr31_sans0841 pr31_sans0009B pr31_sans0500P2 pr34_R4_sans0841 pr34_R4_sans0009B pr34_R4_sans0500P2 \
         pr35_R43_sans0841 pr35_R43_sans0009B pr35_R43_sans0500P2; do p343 $r 4000; done
echo "== PR-42 fini $(date +%T)"

echo "== PR-43 demarre $(date +%T)"
for g in 42 43; do
  entraine pr43_C${g}_8k 8000 0841 "{\"add0814\": true, \"seed\": $g}" && for k in 4000 8000; do feuillets pr43_C${g}_8k $k 841_segB; done
  entraine pr43_B${g}_8k 8000 aucun "{\"seed\": $g, \"sheets_841\": [\"841_w00\", \"841_segA\"], $K}" && for k in 4000 8000; do feuillets pr43_B${g}_8k $k 841_segB; done
done
echo "== PR-43 fini $(date +%T)"
echo "== file de nuit finie $(date +%F' '%T)"
