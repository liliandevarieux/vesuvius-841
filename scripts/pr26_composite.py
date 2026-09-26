# PR-26 : carte composite a profondeur choisie SANS etiquette, par carreau de 256 px (grille 9,6 um).
# Score d un decalage dans un carreau = p95 - p50 de la carte sur le papyrus (carte > 0) ; on garde le meilleur.
# usage : pr26_composite.py SORTIE.tif carte_k1.tif carte_k2.tif ...   (meme grille pour toutes)
import sys, collections, numpy as np, tifffile

T = 256
noms = sys.argv[2:]
cartes = []
for f in noms:
    P = tifffile.imread(f)
    if P.ndim == 3:
        P = P[0] if P.shape[0] < P.shape[-1] else P[..., 0]
    cartes.append(P)
h = min(c.shape[0] for c in cartes); w = min(c.shape[1] for c in cartes)
cartes = [c[:h, :w] for c in cartes]
out = np.zeros_like(cartes[0])
choix = collections.Counter()
for y in range(0, h, T):
    for x in range(0, w, T):
        best, bk = -1.0, 0
        for k, c in enumerate(cartes):
            t = c[y:y + T, x:x + T].astype(np.float32)
            v = t[t > 0]
            if v.size < 100:
                continue
            s = float(np.percentile(v, 95) - np.percentile(v, 50))
            if s > best:
                best, bk = s, k
        out[y:y + T, x:x + T] = cartes[bk][y:y + T, x:x + T]
        if best >= 0:
            choix[bk] += 1
tifffile.imwrite(sys.argv[1], out)
print('composite %s  carreaux choisis par carte : %s' % (sys.argv[1].split('/')[-1],
      ', '.join('%s %d' % (noms[k].split('/')[-1], choix[k]) for k in range(len(noms)))))
