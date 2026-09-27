#!/bin/bash
# PR-33 : les 4 autres segments natifs 9,362 um / 1,2 m de PHerc0139, deja etiquetes par les organisateurs
# (hf://buckets/scrollprize/datasets/ink_9um/labels/native9-scrollprizeorg-21slices, README d ink_9um).
cd /home/slusarska_holding/vesuvius
for p in "w039 20260302000000-w039_2026030210" "w040 20250831000000-w040_2025083102" "w041 20260108000000-w041_2026010816" "w044 20260115000000-w044_2026011522"; do
  w=${p%% *}; seg=${p##* }
  [ -d ink-dataset/ref_12m/$w.zarr/0 ] || timeout 3000 uvx --from awscli aws s3 sync \
    "s3://vesuvius-challenge-open-data/PHerc0139/segments/$seg/surface-volumes/9.362um-1.2m-113keV-volume-20250728140407.zarr/" \
    ink-dataset/ref_12m/$w.zarr/ --no-sign-request --only-show-errors
  timeout 900 uvx --from huggingface_hub hf buckets sync "hf://buckets/scrollprize/datasets/ink_9um/labels/native9-scrollprizeorg-21slices/$w" ft12m/ref/$w > /dev/null 2>&1
  echo "$w volume $(du -sh ink-dataset/ref_12m/$w.zarr | cut -f1) etiquettes $(ls ft12m/ref/$w | tr '\n' ' ')"
done
