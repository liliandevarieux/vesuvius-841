#!/bin/bash
# 1447 comme temoin positif (annonce du 24/09 : lettres lues par les papyrologues vers le point (4144, 2742, 12557)
# du volume public 8,64 um) : maillages 8,64 um (tifxyz) de tous les segments publies de PHerc1447, pour trouver celui
# qui passe par ce point. Donnees publiques, lecture seule.
# usage : bash -l dl_mesh1447.sh
S3=s3://vesuvius-challenge-open-data/PHerc1447/segments
D=/home/slusarska_holding/vesuvius/ft12m/mesh1447
mkdir -p $D && cd $D
L=$(timeout 120 uvx --from awscli aws s3 ls $S3/ --no-sign-request | awk '{print $2}')
echo "$(echo "$L" | grep -c /) segments publies"
for dos in $L; do
  id=${dos%/}
  timeout 300 uvx --from awscli aws s3 sync "$S3/${dos}mesh/" "$id" --exclude '*' --include '*8.64um.tifxyz/*' \
    --no-sign-request --only-show-errors
  echo "$id : $(find $id -name x.tif 2>/dev/null | wc -l) maillage(s) 8,64 um"
done
