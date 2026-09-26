# PR-26 : la preparation 9 um OFFICIELLE (prepare_9um_isotropic_input), fenetre de 84 plans decalee de K plans.
# Seule centered_slice est remplacee : meme moyenne de 4, meme arrondi, meme etiquette de format ; l attribut
# source_z_slice enregistre la fenetre reellement lue.
# usage : prep_decale.py NIVEAU2.zarr SORTIE.zarr K
import sys
from pathlib import Path
from vesuvius.ink_detection.preprocessing import prepare_9um_isotropic_input as p

K = int(sys.argv[3])
centre = p.centered_slice


def decale(length, requested):
    z0, z1 = centre(length, requested)
    if z0 + K < 0 or z1 + K > length:
        raise ValueError('decalage %d hors du volume (%d plans, fenetre %d-%d)' % (K, length, z0, z1))
    return z0 + K, z1 + K


p.centered_slice = decale
p.prepare_isotropic_input(sys.argv[1], Path(sys.argv[2]), level='2', workers=8)
