#!/bin/bash
# PR-26 : ink_9um graine 42, etape 75 000, sens forward, sur segB puis segA, fenetre decalee de K plans
# (K = -12 -6 0 6 12), puis la carte composite a profondeur choisie sans etiquette, puis les mesures.
# Chemins absolus, sorties verifiees sur disque (infer imprime exit=0 quand il echoue).
C=/home/slusarska_holding/vesuvius
PY=$C/villa/vesuvius/.venv/bin/python
CK=$C/checkpoints/ink_9um/hybrid_3d2d-seed42/step-075000.pth
exec >> $C/logs/pr26.log 2>&1
echo "== PR-26 demarre $(date +%F' '%T)"

for SEG in segB segA; do
  case $SEG in
    segB) ETIQ=$C/ink-dataset/841/canon_autres/auto_grown_20260220174252405/inklabels.zarr ;;
    segA) ETIQ=$C/ink-dataset/841/canon_autres/auto_grown_20260220144552896/inklabels.zarr ;;
  esac
  N2=$C/crops/${SEG}_niv2.zarr
  if [ ! -d "$N2/2" ]; then
    echo "== niveau 2 $SEG $(date +%T)"
    $PY $C/niveau2_segB.py $N2 $C/ink-dataset/841/$SEG/$SEG.zarr || { echo "== ARRET niveau 2 $SEG"; exit 1; }
  fi
  [ -d "$N2/2" ] || { echo "== ARRET : pas de niveau 2 pour $SEG"; exit 1; }
  CARTES=""
  for K in -12 -6 0 6 12; do
    P9=$C/crops/${SEG}_9um_k${K}.zarr
    OUT=$C/predictions/pr26_${SEG}_k${K}.tif
    if [ ! -d "$P9/0" ]; then
      rm -rf "$P9.partial"
      cd $C/villa/vesuvius && $PY $C/prep_decale.py "$N2" "$P9" $K > /dev/null || { echo "== ECHEC prep $SEG k$K"; continue; }
    fi
    $PY -c "import zarr; g=zarr.open('$P9',mode='r'); print('   entree $SEG k$K :', g['0'].shape, dict(g.attrs).get('source_z_slice'))"
    if [ ! -s "$OUT" ]; then
      echo "== inference $SEG k$K $(date +%T)"
      cd $C/villa/vesuvius && $PY -m vesuvius.ink_detection.inference.infer "$P9" "$CK" "$OUT" \
        --overlap 0.5 --blend-mode hann --batch-size 4 --num-workers 4 --no-compile --direction forward > /dev/null
    fi
    if [ -s "$OUT" ]; then echo "   ecrit $(basename $OUT)"; CARTES="$CARTES $OUT"
    else echo "== ECHEC : $(basename $OUT) absent -- ne pas conclure"; fi
  done
  NC=$(echo $CARTES | wc -w)
  [ "$NC" -eq 5 ] || { echo "== ARRET $SEG : $NC cartes sur 5 -- pas de composite"; continue; }
  $PY $C/pr26_composite.py $C/predictions/pr26_${SEG}_composite.tif $CARTES
  echo "== mesures $SEG $(date +%T)"
  cd $C
  for f in $CARTES $C/predictions/pr26_${SEG}_composite.tif; do
    ETIQ=$ETIQ $PY $C/eval_segB.py "$f" 4
  done
done
echo "--- rappel : PRIMAIRE composite - k0 >= +0,010 d AUC sur segB ET sur segA ---"
echo "== PR-26 fini $(date +%F' '%T)"
