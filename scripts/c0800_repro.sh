#!/bin/bash
# Point 3, préalable : notre installation reproduit-elle les cartes Reader V3 et Argus V3 publiées par les organisateurs sur
# la zone d'Erwin (343, même grille 2660 x 6780) ? Commande des auteurs : infer --overlap 0.5 --blend-mode hann
# --direction both. Mesure : corrélation de Pearson pixel à pixel (pixels > 0 des deux côtés), pour chaque sens.
# Aucune carte de 0800 n'est calculée ici. usage : bash c0800_repro.sh
H=/home/slusarska_holding/vesuvius; D=$H/c0800/repro; mkdir -p $D; P=$H/villa/vesuvius/.venv/bin/python
until grep -q "^poids" $H/c0800/telecharge.log 2>/dev/null; do sleep 20; done
date "+debut %F %T"
for m in reader_v3/reader-v3 argus_v3/argus-v3; do
  n=$(basename $m)
  cd $H/villa/vesuvius
  $P -m vesuvius.ink_detection.inference.infer $H/c343/vol_erwin $H/checkpoints/$m.pth $D/${n}_erwin.tif \
     --overlap 0.5 --blend-mode hann --direction both --batch-size 2 --num-workers 2 --no-compile > $D/${n}_erwin.log 2>&1
  echo "$n exit=$? $(date +%T)"
done
cd $H/c343
$P - <<'PY'
import glob, numpy as np, tifffile
D='/home/slusarska_holding/vesuvius/c0800/repro/'
REF={'reader-v3':'equipe/cartes/20261019111505-reader-v3-tile384-stride192.tif','argus-v3':'equipe/cartes/20261117205746-argus-v3-tile384-stride192.tif'}
for n,f in REF.items():
    R=tifffile.imread(f).astype(np.float32)
    for s in ('', '_reverse'):
        g=D+'%s_erwin%s.tif'%(n,s)
        try: A=tifffile.imread(g).astype(np.float32)
        except Exception as e: print(n,s,'absent',e); continue
        if A.shape!=R.shape: print(n,s,'forme',A.shape,R.shape); continue
        v=(A>0)&(R>0)
        r=np.corrcoef(A[v],R[v])[0,1]; d=np.abs(A[v]-R[v])
        print('%-9s %-8s r = %.4f  |ecart| moyen %.2f  p99 %.0f  pixels %d' % (n, s or 'direct', r, d.mean(), np.percentile(d,99), v.sum()))
PY
date "+FINI %F %T"
