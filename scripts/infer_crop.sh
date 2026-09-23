#!/bin/bash
# Inference RAPIDE sur une region : construit (ou reutilise) un petit zarr de la region + marge (mkcrop.py), lance infer.py dessus,
# puis coupe la marge et ecrit <sortie.tif> (taille de la region) + <sortie.tif>.origin ("Y0 X0" dans le segment) pour cmp.py & co.
# usage: infer_crop.sh <ckpt.pth> <sortie.tif> <nom_region> <Y0> <Y1> <X0> <X1> [batch=4]   -> log ~/vesuvius/logs/infer_<sortie>.log
# Regions connues : w00_line4_half 12500 15500 14000 20000 ; w00_ctrl = coordonnees de masks/w00_ctrl.txt. Autre segment : SEG=w02_... (lu par mkcrop.py).
export PATH="$HOME/.local/bin:$PATH"
ck=$1; out=$2; reg=$3; Y0=$4; Y1=$5; X0=$6; X1=$7; bs=${8:-4}; M=128
crop=$HOME/vesuvius/crops/$reg.zarr; name=$(basename "$out" .tif)
cd ~/vesuvius/villa/vesuvius
{
  echo "== infer_crop ckpt=$ck out=$out region=$reg $Y0-$Y1/$X0-$X1 : $(date +%H:%M:%S)"
  [ -f "$crop.origin" ] || .venv/bin/python ~/vesuvius/mkcrop.py "$crop" "$Y0" "$Y1" "$X0" "$X1" "$M"
  .venv/bin/python -m vesuvius.ink_detection.inference.infer "$crop" "$ck" "$out.full.tif" \
    --overlap 0.5 --blend-mode hann --batch-size "$bs" --num-workers 4 --no-compile 2>&1
  echo "== infer exit=$? $(date +%H:%M:%S)"
  .venv/bin/python - "$out" "$crop.origin" "$Y0" "$Y1" "$X0" "$X1" <<'PY'
import sys, numpy as np, tifffile
out, orig, Y0, Y1, X0, X1 = sys.argv[1], sys.argv[2], *map(int, sys.argv[3:7])
oy, ox = map(int, open(orig).read().split())
a = tifffile.imread(out + '.full.tif')[Y0 - oy:Y1 - oy, X0 - ox:X1 - ox]
tifffile.imwrite(out, a, compression='zlib'); open(out + '.origin', 'w').write(f'{Y0} {X0}\n')
print('ecrit', out, a.shape, 'origine', Y0, X0)
PY
  rm -f "$out.full.tif"
  echo "== exit=$? $(date +%H:%M:%S)"
} > ~/vesuvius/logs/infer_$name.log 2>&1
