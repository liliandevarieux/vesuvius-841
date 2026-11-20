# PR-59 : sens des couches sans etiquette, p99 - p50 sur le papyrus (pixels > 0, comme eval_12m.py / banc_lisibilite.py),
# pour les deux ordres de v8-in, sur 0343P et sur la zone d'Erwin. Imprime seulement.
import numpy as np, tifffile
D = '/home/slusarska_holding/vesuvius/c343/pr59/'
for z in ('0343P', 'erwin'):
    for s in ('direct', 'inverse'):
        P = tifffile.imread(D + 'v8in_%s_%s.tif' % (z, s)).astype(np.float32)
        v = P[P > 0]
        print('%-6s %-8s papyrus %8d px  p50 %5.1f  p99 %5.1f  p99-p50 %5.1f' % (
            z, s, v.size, np.percentile(v, 50), np.percentile(v, 99), np.percentile(v, 99) - np.percentile(v, 50)))
