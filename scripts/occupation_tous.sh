#!/bin/bash
# occupation en profondeur de tous les segments locaux (scripts/occupation.py)
cd /home/slusarska_holding/vesuvius
for s in phercparis4/w02_20231031143852/w02_20231031143852 phercparis4/w00_20231016151002/w00_20231016151002 \
         1667/w018_20240304144031_2um/w018_20240304144031_2um 841/segB/segB 841/segA/segA 841/w00/w00 841/w00v24/w00v24 \
         0139/w035_2026031718/w035_2026031718 814/814_46527_2um_try2/814_46527_2um_try2 \
         0009b/auto_grown_20250919055754487_inp_hr_2um/auto_grown_20250919055754487_inp_hr_2um 0500p2/-1/-1; do
  villa/vesuvius/.venv/bin/python occupation.py ink-dataset/$s.zarr 2>&1 | tail -1
done
