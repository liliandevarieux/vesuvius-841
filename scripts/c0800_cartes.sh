#!/bin/bash
# PR-60 (inscrit 20/11 18:36, a0e9af5) : cartes de 0800 sur les 14 surfaces approuvées, après les cartes témoins de 0009B.
# Reader V3 et Argus V3 (commande des auteurs, --direction both), puis v8-in (v8in_zarr.py, deux sens). Ce qui existe déjà
# est sauté ; deux passes (la seconde répare un échec CUDA de la première) ; compte final des 84 cartes attendues.
# Personne ne regarde ces cartes : elles ne servent qu'à fabriquer les planches de lecture.
H=/home/slusarska_holding/vesuvius; D=$H/c0800/cartes; mkdir -p $D; P=$H/villa/vesuvius/.venv/bin/python
until grep -q "^FINI" $H/c0800/temoins.log 2>/dev/null; do sleep 30; done
date "+debut %F %T"
cp "/mnt/c/Users/SLUSARSKA HOLDING/vesuvius/scripts/v8in_zarr.py" $H/
for passe in 1 2; do
  for m in $(cut -f1 $H/c0800_surfaces14.tsv); do
    Z=$(ls -d $H/c0800/atlas/$m/surface-volumes/*.zarr)
    for k in reader_v3/reader-v3 argus_v3/argus-v3; do
      n=$(basename $k); o=$D/${m}_$n.tif
      [ -s $o ] && [ -s ${o%.tif}_reverse.tif ] && continue
      cd $H/villa/vesuvius
      $P -m vesuvius.ink_detection.inference.infer $Z $H/checkpoints/$k.pth $o --overlap 0.5 --blend-mode hann \
         --direction both --batch-size 2 --num-workers 2 --no-compile > $D/${m}_$n.log 2>&1
      echo "passe $passe $m $n exit=$? $(date +%T)"
    done
  done
  for m in $(cut -f1 $H/c0800_surfaces14.tsv); do
    Z=$(ls -d $H/c0800/atlas/$m/surface-volumes/*.zarr)
    [ -s $D/${m}_v8in_direct.tif ] && [ -s $D/${m}_v8in_inverse.tif ] && continue
    cd $H; $P -u v8in_zarr.py $Z $D/${m}_v8in 4 > $D/${m}_v8in.log 2>&1
    echo "passe $passe $m v8in exit=$? $(date +%T)"
  done
done
n=$(ls $D/*.tif | wc -l); echo "cartes presentes : $n / 84"
date "+FINI %F %T"
