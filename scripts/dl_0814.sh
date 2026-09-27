#!/bin/bash
# PR-34 : PHerc0814, seul segment etiquete publie avec un volume 1,2 m
cd /home/slusarska_holding/vesuvius
d=ft12m/src/0814; mkdir -p $d
S=s3://vesuvius-challenge-open-data/PHerc0814/segments/20260226000000-46527_2um_try2
[ -d $d/vol.zarr/0 ] || uvx --from awscli aws s3 sync "$S/surface-volumes/9.362um-1.2m-113keV-volume-20250804134230.zarr/" $d/vol.zarr/ --no-sign-request --only-show-errors
for z in inklabels supervision; do
  uvx --from awscli aws s3 sync "$S/ink-labels/2.399um-volume-20260309142202/20260918/$z.zarr/" $d/$z.zarr/ --no-sign-request --only-show-errors --exclude "*" --include "zarr.json" --include "2/*"
done
villa/vesuvius/.venv/bin/python ft12m_build.py 0814 2>&1 | grep -v Warn
