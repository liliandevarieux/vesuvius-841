# PR-28 : entree ink_9um pour un volume de surface deja a ~9 um (scans 1,2 m : 9,362 um / 28 couches, 8,64 um /
# 31 couches). La preparation OFFICIELLE (prepare_9um_isotropic_input) est reutilisee telle quelle avec POOL_Z = 1 et
# INPUT_Z = 21 : les 21 couches centrees (debut = ceil((D - 21) / 2)), sans moyenne en z, sans reechantillonnage XY
# (Korkmaz, experiment2 : natif 9,362 et derive 9,6 um ne different pas de facon mesurable).
# usage : prep_12m.py VOLUME.zarr SORTIE.zarr
import sys
from pathlib import Path
from vesuvius.ink_detection.preprocessing import prepare_9um_isotropic_input as p

p.POOL_Z = 1
p.INPUT_Z = p.OUTPUT_Z
p.prepare_isotropic_input(sys.argv[1], Path(sys.argv[2]), level='0', workers=8)

import zarr
g = zarr.open(sys.argv[2], mode='r+')
g.attrs['z_pool'] = 'none: 21 centred native layers (PR-28, prep_12m.py)'
g.attrs['format'] = 'native-9um-21slice-pr28'
print('entree', g['0'].shape, g.attrs['source_z_slice'])
