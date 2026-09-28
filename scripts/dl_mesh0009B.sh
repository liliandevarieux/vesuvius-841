#!/bin/bash
# PR-45, controle de contamination : maillages 8,64 um (tifxyz) de notre segment etiquete de 0009B et des 14 segments de
# 0009B sur lesquels Reader v2 s est entraine (liste de son train_config.json). Donnees publiques, lecture seule.
# usage : bash -l dl_mesh0009B.sh
S3=s3://vesuvius-challenge-open-data/PHerc0009B/segments
D=/home/slusarska_holding/vesuvius/ft12m/mesh0009B
mkdir -p $D && cd $D
L=$(timeout 120 uvx --from awscli aws s3 ls $S3/ --no-sign-request | awk '{print $2}')
for id in 20250919125754 20250510172804 20250511200236 20250919064353 20250919123506 20250919124722 20250919124917 \
          20250919125302 20250919125605 20250919130642 20250919131352 20250919131642 20250919132115 20250919135433 \
          20250919135915; do
  dos=$(echo "$L" | grep "^$id" | head -1)
  [ -n "$dos" ] || { echo "$id : absent du depot public"; continue; }
  timeout 300 uvx --from awscli aws s3 sync "$S3/${dos}mesh/" "$id" --exclude '*' --include '*8.64um.tifxyz/*' \
    --no-sign-request --only-show-errors
  echo "$id ($dos) : $(find $id -name x.tif | wc -l) maillage(s) 8,64 um"
done
