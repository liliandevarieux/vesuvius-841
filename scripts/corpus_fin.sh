#!/bin/bash
# PR-38 : fin du corpus. Remplace la boucle de dl_corpus24.sh (arretee) : relance les etiquettes incompletes,
# prepare chaque volume des que ses etiquettes sont completes (corpus_complet.py), deux a la fois, puis ecrit "== fin".
C=/home/slusarska_holding/vesuvius; PY=$C/villa/vesuvius/.venv/bin/python; D=$C/ft12m/corpus24
L=$C/logs/dl_corpus24.log
fait () { [ -f $D/$1/surface-volume.zarr/.ok ]; }
for tour in $(seq 1 90); do
  n=0
  while read seg src; do
    fait $seg && continue
    if ! $PY $C/corpus_complet.py $seg > /dev/null; then
      pgrep -f "[a]ligned-scrollprizeorg-21slices/$seg " > /dev/null || \
        ( timeout 3600 uvx --from huggingface_hub hf buckets sync "hf://buckets/scrollprize/datasets/ink_9um/labels/aligned-scrollprizeorg-21slices/$seg" $D/$seg --exclude "*validation_mask*" > /dev/null 2>&1 & )
      continue
    fi
    rm -rf $D/$seg/surface-volume.zarr
    ( timeout 7200 $PY $C/corpus_prep.py $seg $src >> $L 2>&1 && touch $D/$seg/surface-volume.zarr/.ok
      echo "$seg $(date +%T) volume: $(fait $seg && du -sh $D/$seg/surface-volume.zarr | cut -f1 || echo ECHEC)" >> $L ) &
    n=$((n + 1)); [ $((n % 2)) -eq 0 ] && wait
  done < $D/liste.txt
  wait
  [ $(ls $D/*/surface-volume.zarr/.ok 2>/dev/null | wc -l) -ge 24 ] && break
  sleep 60
done
echo "== fin $(date +%F' '%T) : $(ls $D/*/surface-volume.zarr/.ok 2>/dev/null | wc -l) volumes prets sur 24" >> $L
