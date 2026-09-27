#!/bin/bash
# PR-38 : corpus d entrainement d ink_9um (24 segments, 4 rouleaux), au format du loader : etiquettes
# hf://buckets/scrollprize/datasets/ink_9um/labels/aligned-scrollprizeorg-21slices/<seg>/ et, a cote, surface-volume.zarr
# prepare comme le script officiel (niveau 2 XY + moyenne 4x en z, 21 couches) mais seulement sous la supervision (corpus_prep.py).
C=/home/slusarska_holding/vesuvius
PY=$C/villa/vesuvius/.venv/bin/python
D=$C/ft12m/corpus24
S3=https://vesuvius-challenge-open-data.s3.amazonaws.com
exec >> $C/logs/dl_corpus24.log 2>&1
echo "== debut $(date +%F' '%T)"
mkdir -p $D
while read seg src; do
  [ -z "$seg" ] && continue
  timeout 900 uvx --from huggingface_hub hf buckets sync "hf://buckets/scrollprize/datasets/ink_9um/labels/aligned-scrollprizeorg-21slices/$seg" $D/$seg > /dev/null 2>&1
  if [ ! -f $D/$seg/surface-volume.zarr/.ok ]; then
    rm -rf $D/$seg/surface-volume.zarr
    timeout 7200 $PY $C/corpus_prep.py $seg $src && touch $D/$seg/surface-volume.zarr/.ok
  fi
  echo "$seg $(date +%T) etiquettes: $(ls $D/$seg | grep -c zarr) volume: $([ -f $D/$seg/surface-volume.zarr/.ok ] && du -sh $D/$seg/surface-volume.zarr | cut -f1 || echo ECHEC)"
done <<'LISTE'
pherc1667-w013 PHerc1667/segments/20240304141531-w013_20240304141531_flatboi/surface-volumes/2.399um-0.22m-78keV-volume-20251217075048.zarr
pherc1667-w018 PHerc1667/segments/20240304144031-w018_20240304144031_flatboi/surface-volumes/2.399um-0.22m-78keV-volume-20251217075048.zarr
pherc1667-w023 PHerc1667/segments/20240304161941-w023_20240304161941_flatboi/surface-volumes/2.399um-0.22m-78keV-volume-20251217075048.zarr
pherc1667-w028 PHerc1667/segments/20251208130119-w028_20251208130119156_flatboi/surface-volumes/2.399um-0.22m-78keV-volume-20251217075048.zarr
pherc1667-w029 PHerc1667/segments/20251212185248-w029_20251212185248662_flatboi/surface-volumes/2.399um-0.22m-78keV-volume-20251217075048.zarr
pherc1667-w031 PHerc1667/segments/20251223230000-w031_2025122323_flatboi/surface-volumes/2.399um-0.22m-78keV-volume-20251217075048.zarr
phercparis4-w00 PHercParis4/segments/20231016151002/surface-volumes/2.4um-0.22m-78keV-volume-20260411134726.zarr
phercparis4-w01 PHercParis4/segments/20230702185753/surface-volumes/2.4um-0.22m-78keV-volume-20260411134726.zarr
phercparis4-w02 PHercParis4/segments/20231031143852/surface-volumes/2.4um-0.22m-78keV-volume-20260411134726.zarr
phercparis4-w03 PHercParis4/segments/20231106155351/surface-volumes/2.4um-0.22m-78keV-volume-20260411134726.zarr
phercparis4-w05 PHercParis4/segments/20231012184424/surface-volumes/2.4um-0.22m-78keV-volume-20260411134726.zarr
phercparis4-w06 PHercParis4/segments/20231210121321/surface-volumes/2.4um-0.22m-78keV-volume-20260411134726.zarr
phercparis4-w07 PHercParis4/segments/20231007101619/surface-volumes/2.4um-0.22m-78keV-volume-20260411134726.zarr
phercparis4-w09 PHercParis4/segments/20230929220926/surface-volumes/2.4um-0.22m-78keV-volume-20260411134726.zarr
pherc0814-46527 PHerc0814/segments/20260226000000-46527_2um_try2/surface-volumes/2.399um-0.22m-78keV-volume-20260309142202.zarr
pherc0139-w016 PHerc0139/segments/20250108000004-w029_2025010827/surface-volumes/2.399um-0.22m-78keV-volume-20260102150214.zarr
pherc0139-w017 PHerc0139/segments/20250108000005-w030_2025010818/surface-volumes/2.399um-0.22m-78keV-volume-20260102150214.zarr
pherc0139-w028 PHerc0139/segments/20260115000000-w044_2026011522/surface-volumes/2.399um-0.22m-78keV-volume-20260102150214.zarr
pherc0139-w029 PHerc0139/segments/20260126000000-w045_2026012619/surface-volumes/2.399um-0.22m-78keV-volume-20260102150214.zarr
pherc0139-w035 PHerc0139/segments/20260317000000-w035_2026031718/surface-volumes/2.399um-0.22m-78keV-volume-20260102150214.zarr
pherc0139-w039 PHerc0139/segments/20260302000000-w039_2026030210/surface-volumes/2.399um-0.22m-78keV-volume-20260102150214.zarr
pherc0139-w040 PHerc0139/segments/20250831000000-w040_2025083102/surface-volumes/2.399um-0.22m-78keV-volume-20260102150214.zarr
pherc0139-w041 PHerc0139/segments/20260108000000-w041_2026010816/surface-volumes/2.399um-0.22m-78keV-volume-20260102150214.zarr
pherc0139-w043 PHerc0139/segments/20260112000000-w043_2026011217/surface-volumes/2.399um-0.22m-78keV-volume-20260102150214.zarr
LISTE
echo "== fin $(date +%F' '%T)"
