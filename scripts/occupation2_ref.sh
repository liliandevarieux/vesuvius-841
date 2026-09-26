#!/bin/bash
# tableau de reference a ~9,6 um (occupation2.py), avant de mesurer PHerc0800
cd /home/slusarska_holding/vesuvius
PY=villa/vesuvius/.venv/bin/python
D=ink-dataset
$PY occupation2.py $D/0139/w035_2026031718/w035_2026031718.zarr 2.4 4 "0139 w035 (lisible)"
$PY occupation2.py $D/1667/w018_20240304144031_2um/w018_20240304144031_2um.zarr 2.4 4 "1667 w018 (lisible)"
$PY occupation2.py $D/phercparis4/w00_20231016151002/w00_20231016151002.zarr 2.4 4 "Paris4 w00 (lisible)"
$PY occupation2.py $D/phercparis4/w02_20231031143852/w02_20231031143852.zarr 2.4 4 "Paris4 w02 (lisible)"
$PY occupation2.py $D/841/segA/segA.zarr 2.403 4 "841 segA"
$PY occupation2.py $D/841/segB/segB.zarr 2.403 4 "841 segB"
$PY occupation2.py $D/841/w00v24/w00v24.zarr 2.403 4 "841 w00v24"
$PY occupation2.py $D/841/w00/w00.zarr 4.681 2 "841 w00 (rendu 4,68)"
$PY occupation2.py $D/0009b/auto_grown_20250919055754487_inp_hr_2um/auto_grown_20250919055754487_inp_hr_2um.zarr 2.4 4 "0009B"
