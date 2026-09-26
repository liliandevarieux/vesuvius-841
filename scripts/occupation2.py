# Occupation en profondeur a resolution COMPARABLE (voir occupation.py pour la formule, reprise du « readability
# gate » de robertlangdonn). Pour comparer des scans de resolutions differentes (2,4 / 4,68 / 8,64 um), on moyenne
# POOL couches en une, on prend une fenetre de N couches centree (~150 um physiques), et le lissage gaussien garde
# sa largeur physique : sigma = 1,5 couche a 2,4 um = 3,6 um, soit SIGMA = 3,6 / (taille de couche apres moyenne).
# usage : occupation2.py VOLUME.zarr TAILLE_COUCHE_UM POOL [NOM] [SAUT]
import sys, numpy as np, zarr
from scipy.ndimage import gaussian_filter1d

FEN_UM, SIG_UM, T, SAUT, PAS = 150.0, 3.6, 1024, 4096, 32
if len(sys.argv) > 5:
    SAUT = int(sys.argv[5])      # petits volumes (PHerc0800) : tous les carreaux
v = zarr.open(sys.argv[1], mode='r')
v = v['0'] if hasattr(v, 'keys') and '0' in v else v
UM, POOL = float(sys.argv[2]), int(sys.argv[3])
NOM = sys.argv[4] if len(sys.argv) > 4 else sys.argv[1].split('/')[-1][:30]
couche = UM * POOL
N = int(round(FEN_UM / couche))
D, H, W = v.shape
Dp = D // POOL
z0 = max(0, (Dp - N) // 2)
vals = []
for y in range(0, H, SAUT):
    for x in range(0, W, SAUT):
        a = np.asarray(v[z0 * POOL:(z0 + N) * POOL, y:y + T:PAS, x:x + T:PAS]).astype(np.float32)
        if a.shape[0] < N * POOL:
            continue
        a = a.reshape(N, POOL, -1).mean(1)
        a = a[:, a.max(0) > 0]
        if a.shape[1] == 0:
            continue
        p = gaussian_filter1d(a, SIG_UM / couche, axis=0)
        p /= p.max(0) + 1e-6
        vals.append((p > 0.5).mean(0))
o = np.concatenate(vals) if vals else np.array([np.nan])
print('%-32s couche %5.2f um  fenetre %2d couches (%3.0f um)  colonnes %6d  mediane %.3f  p90 %.3f  propre %.3f'
      % (NOM, couche, N, N * couche, o.size, np.median(o), np.percentile(o, 90), (o <= 0.5).mean()))
