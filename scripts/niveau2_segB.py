# PR-23, etape 1 : fabriquer le « niveau 2 » (XY / 4) que le volume publie de segB n a pas.
#
# POURQUOI CETTE ETAPE ET PAS UNE PREPARATION MAISON COMPLETE. La fiche du modele dit, pour un volume a 2,4 um :
# « XY pyramid level 2, 4x z mean-pooling ». L outil officiel prepare_9um_isotropic_input fait la partie Z --
# choix des 84 plans centres (avec un ceil : plans 13 a 96 sur 109, et non 12 a 95 comme je l avais ecrit dans
# l enregistrement), moyenne de 4, arrondi, etiquette de format. Mais il lit un niveau 2 existant, et segB.zarr n a
# que le niveau 0. Ce script fabrique donc SEULEMENT le niveau 2, par moyenne 4 x 4 en XY sur les 109 plans, et
# l outil officiel fait tout le reste. Le moins de code maison possible sur ce qui conditionne l entree du modele.
#
# Les niveaux publies sont faits de moyennes successives par 2 ; une moyenne 4 x 4 directe en differe par
# l arrondi intermediaire. Korkmaz (experiment2) ne mesure aucune difference entre entree derivee et native :
# une difference d arrondi est tres en dessous de ce seuil.
#
# Memoire bornee : bandes de 256 lignes, et la moyenne est calculee par paquets de 16 plans.
import sys, time, numpy as np, zarr
from numcodecs import Blosc

H = '/home/slusarska_holding/vesuvius'
SRC = sys.argv[2] if len(sys.argv) > 2 else '%s/ink-dataset/841/segB/segB.zarr' % H   # 2e argument : autre segment (PR-26 : segA)
DST = sys.argv[1] if len(sys.argv) > 1 else '%s/crops/segB_niv2.zarr' % H
BANDE, PAQ = 256, 16

src = zarr.open(SRC, mode='r')['0']
Z, Y, X = src.shape
Y4, X4 = Y // 4, X // 4
print('source %s %s -> niveau 2 (%d, %d, %d)' % (src.shape, src.dtype, Z, Y4, X4), flush=True)
g = zarr.open_group(DST, mode='w', zarr_format=2)
dst = g.create_array('2', shape=(Z, Y4, X4), chunks=(Z, 128, 128), dtype='uint8', fill_value=0,
                     compressors=Blosc(cname='zstd', clevel=5, shuffle=Blosc.BITSHUFFLE))   # zarr 3 : un seul des deux
t0 = time.time()
for y in range(0, Y4 * 4, BANDE):
    y1 = min(y + BANDE, Y4 * 4)
    b = np.asarray(src[:, y:y1, :X4 * 4])
    out = np.empty((Z, (y1 - y) // 4, X4), np.uint8)
    for z in range(0, Z, PAQ):
        f = b[z:z + PAQ].astype(np.float32).reshape(-1, (y1 - y) // 4, 4, X4, 4).mean(axis=(2, 4))
        out[z:z + PAQ] = np.rint(f).astype(np.uint8)
    dst[:, y // 4:y1 // 4, :] = out
    if (y // BANDE) % 8 == 0:
        print('  lignes %5d / %d  (%.0f s)' % (y1, Y4 * 4, time.time() - t0), flush=True)
print('ecrit %s en %.0f s' % (DST, time.time() - t0), flush=True)
