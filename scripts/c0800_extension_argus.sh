#!/bin/bash
# File de la carte graphique, 21/11 (règle 6) : Argus V3, deux sens, sur les 81 surfaces de 0800 de l'atlas qui ne sont
# PAS parmi les 14 approuvées à l'oeil (pscamillo/vesuvius-eligible-meshes ; rendus rodriguescarson, CC BY-NC 4.0).
# Seuls les volumes de surface sont téléchargés, jamais les dossiers ink-detection. PERSONNE NE REGARDE CES CARTES :
# elles préparent une lecture future, qui sera inscrite avant tout panneau. Aucune conclusion ne vient de ce calcul.
# Une surface à la fois (téléchargement puis carte) ; deux passes (la seconde refait ce qui manque) ; compte final.
# usage : bash c0800_extension.sh   (journal : ~/vesuvius/c0800/extension.log)
set -u
H=/home/slusarska_holding/vesuvius; A=$H/c0800/atlas; D=$H/c0800/cartes_ext_argus; mkdir -p $D
P=$H/villa/vesuvius/.venv/bin/python; L=$H/c0800_surfaces_ext.tsv
cp "/mnt/c/Users/SLUSARSKA HOLDING/vesuvius/scripts/c0800_surfaces_ext.tsv" $L
date "+debut %F %T"
for passe in 1 2; do
  while IFS=$'\t' read -r m url; do
    if [ ! -f $A/$m/.ok ]; then
      mkdir -p $A/$m && cd $A/$m
      curl -sSL -o surface-volumes.tar "$url" && tar xf surface-volumes.tar && rm surface-volumes.tar && touch .ok
      echo "passe $passe $m volume $( [ -f .ok ] && du -sh . | cut -f1 || echo ECHEC) $(date +%T)"
    fi
    [ -f $A/$m/.ok ] || continue
    o=$D/${m}_argus-v3.tif
    [ -s $o ] && [ -s ${o%.tif}_reverse.tif ] && continue
    Z=$(ls -d $A/$m/surface-volumes/*.zarr | head -1)
    cd $H/villa/vesuvius
    $P -m vesuvius.ink_detection.inference.infer $Z $H/checkpoints/argus_v3/argus-v3.pth $o --overlap 0.5 \
       --blend-mode hann --direction both --batch-size 2 --num-workers 2 --no-compile > $D/${m}_argus-v3.log 2>&1
    echo "passe $passe $m argus-v3 exit=$? deux_sens=$( [ -s $o ] && [ -s ${o%.tif}_reverse.tif ] && echo oui || echo NON) $(date +%T)"
  done < $L
done
n=$(ls $D/*_argus-v3.tif $D/*_argus-v3_reverse.tif 2>/dev/null | wc -l); echo "cartes presentes : $n / $((2 * $(wc -l < $L)))"
date "+FINI %F %T"
