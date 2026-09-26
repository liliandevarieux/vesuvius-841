#!/bin/bash
# PR-27, temoins sur le meme type de scan (9,36 um / 1,2 m) : deux rouleaux lisibles et 841 segB
cd /home/slusarska_holding/vesuvius
tail -2 logs/dl_ref_12m.log
du -sh ink-dataset/ref_12m/* ink-dataset/841_12m
PY=villa/vesuvius/.venv/bin/python
$PY occupation2.py ink-dataset/ref_12m/PHerc0139.zarr 9.362 1 "0139 w025 1,2 m (lisible)" 1024
$PY occupation2.py ink-dataset/ref_12m/PHerc0814.zarr 9.362 1 "0814 ag1616 1,2 m (lisible)" 1024
$PY occupation2.py ink-dataset/841_12m/segB.zarr 9.366 1 "841 segB 1,2 m" 1024
