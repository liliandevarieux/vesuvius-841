#!/bin/bash
# Point 3 (0800) : poids de Reader V3 et Argus V3 (MIT), puis volumes de surface des 14 surfaces de 0800 approuvées à l'oeil
# par pscamillo, rendus par Carson Rodrigues (rodriguescarson/eligible-scroll-atlas-renders, CC BY-NC 4.0, vc_render_tifxyz
# --flip-normals). On NE télécharge PAS ses dossiers ink-detection (cartes ink_9um) : aucune carte de 0800 n'est regardée
# avant l'inscription. usage : bash c0800_telecharge.sh
set -u
H=/home/slusarska_holding/vesuvius; D=$H/c0800; mkdir -p $D/atlas $H/checkpoints/reader_v3 $H/checkpoints/argus_v3
cd $H/checkpoints
[ -s reader_v3/reader-v3.pth ] || curl -sSL -o reader_v3/reader-v3.pth https://huggingface.co/domenicor046/reader-v3/resolve/main/reader-v3.pth
[ -s argus_v3/argus-v3.pth ] || curl -sSL -o argus_v3/argus-v3.pth https://huggingface.co/ruiconte/argus-v3/resolve/main/argus-v3.pth
sha256sum reader_v3/reader-v3.pth argus_v3/argus-v3.pth | tee $D/poids_sha256.txt
grep -q 2d887d2bffaadcefae1507bea269e04e1e79c47a6320cce6071d701b4089bbe3 $D/poids_sha256.txt && echo "argus-v3 : empreinte conforme" || echo "argus-v3 : EMPREINTE NON CONFORME"
date "+poids %F %T"
while IFS=$'\t' read -r m url; do
  [ -f $D/atlas/$m/.ok ] && continue
  mkdir -p $D/atlas/$m && cd $D/atlas/$m
  curl -sSL -o surface-volumes.tar "$url" && tar xf surface-volumes.tar && rm surface-volumes.tar && touch .ok
  echo "$m : $(du -sh . | cut -f1) $(date +%T)"
done < <(tr -d '' < "/mnt/c/Users/SLUSARSKA HOLDING/vesuvius/scripts/c0800_surfaces14.tsv")
date "+volumes finis %F %T"
