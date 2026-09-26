#!/bin/bash
# PR-30 : volumes 1,2 m + etiquettes 20260918 (niveau 2) des segments etiquetes hors entrainement d ink_9um
cd /home/slusarska_holding/vesuvius
mkdir -p ft12m/src
S3=s3://vesuvius-challenge-open-data
dl () {  # $1 nom, $2 chemin segment, $3 volume 1,2 m, $4 dossier etiquettes
  local d=ft12m/src/$1
  mkdir -p $d
  [ -d $d/vol.zarr/0 ] || timeout 3000 uvx --from awscli aws s3 sync "$S3/$2/surface-volumes/$3/" $d/vol.zarr/ --no-sign-request --only-show-errors
  for z in inklabels supervision; do
    timeout 600 uvx --from awscli aws s3 sync "$S3/$2/ink-labels/$4/20260918/$z.zarr/" $d/$z.zarr/ --no-sign-request --only-show-errors \
      --exclude "*" --include "zarr.json" --include "2/*"
  done
  echo "$1 fin $(du -sh $d | cut -f1)"
}
dl 841_w00  PHerc0841/segments/20260220213127-w00 9.366um-1.2m-113keV-volume-20250821151531.zarr 2.403um-volume-20260319124803
dl 841_segA PHerc0841/segments/20260220214732-auto_grown_20260220144552896 9.366um-1.2m-113keV-volume-20250821151531.zarr 2.403um-volume-20260319124803
dl 841_segB PHerc0841/segments/20260221022814-auto_grown_20260220174252405 9.366um-1.2m-113keV-volume-20250821151531.zarr 2.403um-volume-20260319124803
dl 0009B    PHerc0009B/segments/20250919125754-auto_grown_20250919055754487_inp_hr 8.64um-1.2m-116keV-volume-20250521125136.zarr 2.401um-volume-20250820154339
dl 0500P2   PHerc0500P2/segments/20250825181859--1 9.362um-1.2m-113keV-volume-20250820143440.zarr 2.215um-volume-20250526151718
