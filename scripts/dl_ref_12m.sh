#!/bin/bash
# volumes 9,362 um / 1,2 m de deux rouleaux LISIBLES (0139, 0814) : temoins de l occupation sur le scan eligible
cd /home/slusarska_holding/vesuvius
mkdir -p ink-dataset/ref_12m
for p in PHerc0139/segments/20250108000000-w025_2025010863/surface-volumes/9.362um-1.2m-113keV-volume-20250728140407.zarr \
         PHerc0814/segments/20250925161630-auto_grown_20250925161630635/surface-volumes/9.362um-1.2m-113keV-volume-20250804134230.zarr; do
  n=${p%%/*}
  timeout 3500 uvx --from awscli aws s3 sync "s3://vesuvius-challenge-open-data/$p/" "ink-dataset/ref_12m/$n.zarr/" \
    --no-sign-request --only-show-errors >> logs/dl_ref_12m.log 2>&1
  echo "$n fin=$?" >> logs/dl_ref_12m.log
done
du -sh ink-dataset/ref_12m/* ink-dataset/841_12m
