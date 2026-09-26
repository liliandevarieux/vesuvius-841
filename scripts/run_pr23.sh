#!/bin/bash
# PR-23 : les modeles ink_9um publies, sur PHerc. 841 segB. Aucun entrainement.
# Trois lecons des dernieres 24 h cablees ici : chemins ABSOLUS partout (deux files mortes sur des chemins
# relatifs), script depose par mv (un cp sur un script en cours a failli casser PR-20), et chaque sortie VERIFIEE
# sur disque plutot que crue sur un exit=0 (infer imprime exit=0 quand il echoue).
C=/home/slusarska_holding/vesuvius
PY=$C/villa/vesuvius/.venv/bin/python
N2=$C/crops/segB_niv2.zarr
P9=$C/crops/segB_9um.zarr
exec >> $C/logs/pr23.log 2>&1
echo "== PR-23 demarre $(date +%F' '%T)"

# 1. niveau 2 (XY / 4) sur les 109 plans
if [ ! -d "$N2/2" ]; then
  $PY $C/niveau2_segB.py $N2 || { echo "== ARRET etape 1"; exit 1; }
fi
[ -d "$N2/2" ] || { echo "== ARRET : pas de niveau 2 ecrit"; exit 1; }

# 2. preparation OFFICIELLE : 84 plans centres, moyenne de 4 -> 21 tranches, etiquette de format
if [ ! -d "$P9/0" ]; then
  rm -rf "$P9.partial"
  cd $C/villa/vesuvius && $PY -m vesuvius.ink_detection.preprocessing.prepare_9um_isotropic_input "$N2" "$P9" --level 2 --workers 8 \
    || { echo "== ARRET etape 2"; exit 1; }
fi
$PY -c "import zarr; g=zarr.open('$P9',mode='r'); print('entree 9 um :', g['0'].shape, dict(g.attrs).get('format'), dict(g.attrs).get('source_z_slice'))"

# 3. inference, deux graines, deux sens (--direction both ecrit <sortie>.tif et <sortie>_reverse.tif)
cd $C/villa/vesuvius
for s in 42 43; do
  ck=$C/checkpoints/ink_9um/hybrid_3d2d-seed$s/step-075000.pth
  out=$C/predictions/pr23_segB_s${s}_75k.tif
  if [ ! -s "$out" ] || [ ! -s "${out%.tif}_reverse.tif" ]; then
    echo "== inference graine $s $(date +%T)"
    $PY -m vesuvius.ink_detection.inference.infer "$P9" "$ck" "$out" \
      --overlap 0.5 --blend-mode hann --batch-size 4 --num-workers 4 --no-compile --direction both
  fi
  for f in "$out" "${out%.tif}_reverse.tif"; do
    [ -s "$f" ] && echo "   ecrit $(basename $f)" || echo "== ECHEC : $(basename $f) absent -- ne pas conclure"
  done
done

# 4. la mesure, meme code que la reference (etiquettes 24,95 ; carte publiee 15,09 / AUC 0,8656)
echo "== mesures $(date +%T)"
cd $C
for f in $C/predictions/pr23_segB_s42_75k_reverse.tif $C/predictions/pr23_segB_s42_75k.tif \
         $C/predictions/pr23_segB_s43_75k_reverse.tif $C/predictions/pr23_segB_s43_75k.tif; do
  [ -s "$f" ] && $PY $C/eval_segB.py "$f" 4
done
echo "--- rappel : ETIQUETTES 24,95 | carte publiee 15,09 AUC 0,8656 | PRIMAIRE = s42_75k_reverse ---"
echo "== PR-23 fini $(date +%F' '%T)"
