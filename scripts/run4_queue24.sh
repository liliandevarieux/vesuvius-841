#!/bin/bash
# Le sens appartient-il au TABLEAU ou au SEGMENT ? (question soulevee par AndreasHad04, #1867)
# Notre modele est entraine sur le rendu 65 plans 4,681 um de w00, en ordre stocke. On lui donne le rendu 65 plans du
# MEME seau pour ag174 — le segment dont il fallait retourner le volume de surface publie. S il le lit en ordre stocke,
# le sens appartient au tableau et notre formulation publique de ce matin est a corriger.
# Tourne pendant que queue21 telecharge (GPU libre) : leger, ~700 Mo et 4 inferences.
export PATH="$HOME/.local/bin:$PATH"; cd ~/vesuvius
H=/home/slusarska_holding/vesuvius; CK=$H/runs/ink_841_human7n/ckpt_016000.pth
SEG=auto_grown_20260220174252405
B="hf://buckets/scrollprize/datasets/ink/841/$SEG"
R=$H/ink-dataset/841/seau174
hf() { uvx --from huggingface_hub hf "$@"; }
{
  echo "== queue24 attente de queue20 $(date +%T)"
  while pgrep -f 'run4_queue20.s[h]|inference.infe[r]' > /dev/null; do sleep 30; done
  echo "== queue24 debut $(date +%T)"
  mkdir -p $R/0
  hf buckets cp "$B/$SEG.zarr/.zattrs" "$R/.zattrs" > /dev/null 2>&1
  hf buckets cp "$B/$SEG.zarr/.zgroup" "$R/.zgroup" > /dev/null 2>&1
  hf buckets cp "$B/$SEG.zarr/0/.zarray" "$R/0/.zarray" > /dev/null 2>&1
  hf buckets cp "$B/${SEG}_inklabels_v2.tif" "$R/labels_v2.tif" > /dev/null 2>&1
  hf buckets cp "$B/${SEG}_supervision_mask_v2.tif" "$R/supervision_v2.tif" > /dev/null 2>&1
  ls -la $R $R/0 | head -12
  villa/vesuvius/.venv/bin/python $H/prep_seau.py $R 2 || exit 1
  echo "== telechargement des chunks $(date +%T) ($(wc -l < $R/chunks.txt))"
  awk '{print $1" "$2}' $R/chunks.txt | xargs -P 8 -n 2 bash -c '
    f="'"$R"'/0/0.$0.$1"; [ -s "$f" ] && exit 0
    uvx --from huggingface_hub hf buckets cp "'"$B"'/'"$SEG"'.zarr/0/0.$0.$1" "$f" > /dev/null 2>&1'
  echo "== $(find $R/0 -name '0.*' | wc -l) chunks pris, $(du -sh $R | cut -f1) $(date +%T)"
  k=0
  while read Y0 Y1 X0 X1; do
    k=$((k+1))
    for r in 0 1; do
      suf=""; [ "$r" = 1 ] && suf="r"
      c=$H/crops/seau174_w$k$suf.zarr
      (cd villa/vesuvius && SCROLL=841 SEG=seau174 ZN=65 REV=$r .venv/bin/python $H/mkcrop2.py $c $Y0 $Y1 $X0 $X1 128 | tail -1)
      SCROLL=841 SEG=seau174 bash infer_crop.sh "$CK" "$H/predictions/seau174_w$k${suf}_human7n.tif" seau174_w$k$suf $Y0 $Y1 $X0 $X1 4
      echo "  fenetre $k$suf : $( [ -f "$H/predictions/seau174_w$k${suf}_human7n.tif" ] && echo ok || echo ECHEC ) $(date +%T)"
      rm -rf "$c" "$c.origin"
    done
  done < $R/fenetres.txt
  echo "== mesure $(date +%T)"
  villa/vesuvius/.venv/bin/python $H/mesure_seau.py $R
  echo "== queue24 fin $(date +%T)"
} >> logs/run4_queue24.log 2>&1
