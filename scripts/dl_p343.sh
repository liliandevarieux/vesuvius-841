#!/bin/bash
# PR-29 : temoin PHerc0343P (meme scan que 0800 : 8,64 um / 1,2 m / 116 keV), volume + etiquettes + masque
cd /home/slusarska_holding/vesuvius
mkdir -p ink-dataset/p343
timeout 3000 uvx --from awscli aws s3 sync "s3://vesuvius-challenge-open-data/PHerc0343P/segments/20250511003658-tifxyz/surface-volumes/8.64um-1.2m-116keV-volume-20250521134555.zarr/" ink-dataset/p343/vol_12m.zarr/ --no-sign-request --only-show-errors > logs/dl_p343.log 2>&1
echo "volume fin=$?" >> logs/dl_p343.log
for z in 20250511003658_inklabels.zarr 20250511003658_supervision_mask.zarr; do
  for l in .zattrs .zgroup 3/.zarray 3/.zattrs; do
    mkdir -p "ink-dataset/p343/$z/3"
    uvx --from huggingface_hub hf buckets cp "hf://buckets/scrollprize/datasets/ink/unused/P343p/20250511003658/$z/$l" "ink-dataset/p343/$z/$l" >> logs/dl_p343.log 2>&1
  done
  uvx --from huggingface_hub hf buckets sync "hf://buckets/scrollprize/datasets/ink/unused/P343p/20250511003658/$z/3" "ink-dataset/p343/$z/3" >> logs/dl_p343.log 2>&1
  echo "$z fin=$?" >> logs/dl_p343.log
done
du -sh ink-dataset/p343/*
