# Occupation en profondeur (« readability gate » de robertlangdonn, github.com/robertlangdonn/vesuvius-readability-gate,
# cite dans villa #1180) : pour chaque colonne, part de la fenetre de 62 couches plus claire que 0,5 x son maximum
# apres lissage gaussien sigma 1,5 -- formule reprise telle quelle (occupancy_column), vectorisee.
# Lisible chez lui : mediane ~0,35, part propre (<= 0,5) >= 0,70 ; illisible (PHerc1203) : 0,97-1,00.
# Colonnes tirees sur une grille de PAS px ; colonnes sans donnee (max = 0) exclues, comme chez lui.
# usage : occupation.py VOLUME.zarr [PAS] [MASQUE_ETIQUETTES.zarr]   (masque : ne garder que les colonnes sur l encre)
import sys, numpy as np, zarr
from scipy.ndimage import gaussian_filter1d

N, T = 62, 1024
SAUT = 4 * T    # un carreau sur 16 sans masque (volumes de 17 Go) ; avec masque, tous

v = zarr.open(sys.argv[1], mode='r')['0']
PAS = int(sys.argv[2]) if len(sys.argv) > 2 else 32
D, H, W = v.shape
z0 = max(0, (D - N) // 2)
m = None
if len(sys.argv) > 3:
    m = np.asarray(zarr.open(sys.argv[3], mode='r')['3'][:]).squeeze()
    m = (m.any(axis=0) if m.ndim == 3 else m) > 0
    SAUT = T
vals = []
for y in range(0, H, SAUT):
    for x in range(0, W, SAUT):
        a = np.asarray(v[z0:z0 + N, y:y + T:PAS, x:x + T:PAS]).astype(np.float32)
        if m is not None:
            yy, xx = np.meshgrid(np.arange(y, min(y + T, H), PAS), np.arange(x, min(x + T, W), PAS), indexing='ij')
            k = m[np.minimum(yy // 8, m.shape[0] - 1), np.minimum(xx // 8, m.shape[1] - 1)]
            a = a[:, k]
        else:
            a = a.reshape(a.shape[0], -1)
        a = a[:, a.max(0) > 0]
        if a.shape[1] == 0:
            continue
        p = gaussian_filter1d(a, 1.5, axis=0)
        p /= p.max(0) + 1e-6
        vals.append((p > 0.5).mean(0))
o = np.concatenate(vals) if vals else np.array([np.nan])
print('%-58s couches %3d (fenetre %d-%d)  colonnes %7d  mediane %.3f  p90 %.3f  propre %.3f  sature %.3f'
      % (sys.argv[1].split('ink-dataset/')[-1][:58] + (' [encre]' if m is not None else ''), D, z0, z0 + N - 1,
         o.size, np.median(o), np.percentile(o, 90), (o <= 0.5).mean(), (o >= 0.6).mean()))
