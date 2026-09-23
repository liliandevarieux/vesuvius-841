#!/bin/bash
# Ou est le feuillet dans les 109 couches de segB ? Lilian voit l encre vers la couche 37, mkseg65.py avait
# suppose le milieu (54) sans le mesurer. Instrument : le modele lui-meme (human7n ckpt 016000), qui est celui
# qui a etabli le sens des couches. Meme modele, meme fenetre, seule change la tranche de 65 couches prise.
# Arbitre : les labels des organisateurs et leur prediction publiee. Attend la fin de queue14 : un seul travail GPU.
export PATH="$HOME/.local/bin:$PATH"; cd ~/vesuvius
H=/home/slusarska_holding/vesuvius; CK=$H/runs/ink_841_human7n/ckpt_016000.pth
K=2   # fenetre 2 de fenetres_B.txt : inspectee a 100 %, 39 % d encre labellisee
read Y0 Y1 X0 X1 <<< "$(sed -n "${K}p" /home/slusarska_holding/fenetres_B.txt)"
{
  echo "== queue15 attente de queue14 $(date +%T)"
  while pgrep -f 'run4_queue14.s[h]|trainin[g].train|inference.infe[r]' > /dev/null; do sleep 60; done
  echo "== queue15 debut $(date +%T) : fenetre $K, Y $Y0-$Y1 X $X0-$X1"
  for tag in 32 44 54 66 78 full; do
    c=$H/crops/segB_zc$tag.zarr
    if [ "$tag" = full ]; then
      (cd villa/vesuvius && SCROLL=841 SEG=segB ZN=65 REV=1 FULL=1 .venv/bin/python $H/mkcrop2.py $c $Y0 $Y1 $X0 $X1 128 | tail -1)
    else
      (cd villa/vesuvius && SCROLL=841 SEG=segB ZN=65 REV=1 ZC=$tag .venv/bin/python $H/mkcrop2.py $c $Y0 $Y1 $X0 $X1 128 | tail -1)
    fi
    SCROLL=841 SEG=segB bash infer_crop.sh "$CK" "$H/predictions/segB_zc${tag}_human7n.tif" segB_zc$tag $Y0 $Y1 $X0 $X1 4
    echo "  tranche $tag : $( [ -f "$H/predictions/segB_zc${tag}_human7n.tif" ] && echo ok || echo ECHEC ) $(date +%T)"
    rm -rf "$c" "$c.origin"
  done
  echo "== queue15 mesure $(date +%T)"
  villa/vesuvius/.venv/bin/python $H/mesure_zc.py segB auto_grown_20260220174252405 $K /home/slusarska_holding/fenetres_B.txt 32 44 54 66 78 full
  echo "== queue15 fin $(date +%T)"
} >> logs/run4_queue15.log 2>&1
