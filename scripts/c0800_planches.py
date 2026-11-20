# PR-60 (inscrit 20/11 18:36, a0e9af5) : planches de lecture « carrés v1 » et clé.
# 8 conditions = 4 cartes (moyenne, Reader V3, Argus V3, v8-in) x 2 sens (direct, inverse). Plan des carrés :
# c0800/plan_carres.json (68 carrés : 52 de 0800, 10 d'Erwin, 6 de 0009B). Carré latin : le lecteur r (0..47) voit le
# carré j dans la condition (j + r) mod 8 ; ordre mélangé par lecteur (graine 60 + r) ; numéros 1..68 sur trois planches
# de 24, 24 et 20 carrés (6 x 4).
# Affichage : chaque carte et chaque sens, étiré par surface ou zone témoin de sa médiane à son 99,5e centile sur les
# pixels de la surface, écrêté ; moyenne = moyenne des trois cartes étirées là où les trois sont valides, puis étirée de
# même ; carré de 1024 px réduit 4 x 4 (moyenne) à 256 px ; hors surface en noir.
# Masques : 0800 et 0009B = couche 15 du volume > 0 ; Erwin = carte Reader V3 des organisateurs ramenée dans son repère > 0.
# usage : c0800_planches.py essai     -> planche d'essai à blanc (0343P, v8-in, deux sens, hors test)
#         c0800_planches.py test      -> 48 x 3 planches + clé c0800/pr60/cle_pr60.json
import sys, os, json, glob, random, numpy as np, tifffile, zarr
from PIL import Image, ImageDraw
sys.path.insert(0, '/home/slusarska_holding/vesuvius')
from banc_lisibilite import F

H = '/home/slusarska_holding/vesuvius/'
OUT = H + 'c0800/pr60/'
T, R4 = 1024, 4
CARTES = ['moyenne', 'readerv3', 'argusv3', 'v8in']
COND = [(m, s) for m in CARTES for s in ('direct', 'inverse')]       # indice 0..7
LECTEURS, PAR_PLANCHE, COLS = 48, 24, 6


def etire(a, masque):
    v = a[masque]
    lo, hi = np.percentile(v, [50, 99.5])
    return np.where(masque, np.clip((a - lo) / max(hi - lo, 1e-6), 0, 1), 0).astype(np.float32)


def avec_moyenne(E, masque):
    """E[(carte, sens)] = image étirée des trois modèles ; ajoute la moyenne étirée."""
    for s in ('direct', 'inverse'):
        m = (E[('readerv3', s)] + E[('argusv3', s)] + E[('v8in', s)]) / 3
        E[('moyenne', s)] = etire(m, masque)
    return E


def reduit(a):
    h, w = a.shape
    b = np.zeros((T, T), np.float32); b[:min(h, T), :min(w, T)] = a[:T, :T]
    return Image.fromarray(np.round(b.reshape(T // R4, R4, T // R4, R4).mean((1, 3)) * 255).astype(np.uint8))


def lit_tif(f, forme=None, origine=(0, 0)):
    a = tifffile.imread(f).astype(np.float32)
    if forme is None:
        return a
    b = np.zeros(forme, np.float32); y, x = origine
    b[y:y + a.shape[0], x:x + a.shape[1]] = a[:forme[0] - y, :forme[1] - x]
    return b


def zone_0800(m):
    z = glob.glob(H + 'c0800/atlas/%s/surface-volumes/*.zarr' % m)[0]
    masque = np.asarray(zarr.open(z, mode='r')['0'][15]) > 0
    C = H + 'c0800/cartes/' + m + '_'
    f = {('readerv3', 'direct'): C + 'reader-v3.tif', ('readerv3', 'inverse'): C + 'reader-v3_reverse.tif',
         ('argusv3', 'direct'): C + 'argus-v3.tif', ('argusv3', 'inverse'): C + 'argus-v3_reverse.tif',
         ('v8in', 'direct'): C + 'v8in_direct.tif', ('v8in', 'inverse'): C + 'v8in_inverse.tif'}
    E = {k: etire(lit_tif(v), masque) for k, v in f.items()}
    return avec_moyenne(E, masque)


def zone_erwin():
    import c343_recale as K
    os.makedirs(OUT + 'erwin', exist_ok=True)
    src = {('readerv3', 'direct'): H + 'c0800/repro/reader-v3_erwin.tif',
           ('readerv3', 'inverse'): H + 'c0800/repro/reader-v3_erwin_reverse.tif',
           ('argusv3', 'direct'): H + 'c0800/repro/argus-v3_erwin.tif',
           ('argusv3', 'inverse'): H + 'c0800/repro/argus-v3_erwin_reverse.tif',
           ('v8in', 'direct'): H + 'c343/pr59/v8in_erwin_direct.tif',
           ('v8in', 'inverse'): H + 'c343/pr59/v8in_erwin_inverse.tif'}
    ref = OUT + 'erwin/masque_readerv3_organisateurs.tif'
    if not os.path.exists(ref):
        K.carte(H + 'c343/equipe/cartes/20261019111505-reader-v3-tile384-stride192.tif', ref)
    masque = tifffile.imread(ref) > 0
    E = {}
    for k, f in src.items():
        o = OUT + 'erwin/%s_%s.tif' % k
        if not os.path.exists(o):
            K.carte(f, o)
        E[k] = etire(tifffile.imread(o).astype(np.float32), masque)
    return avec_moyenne(E, masque)


def zone_0009B():
    vol = zarr.open(H + 'ft12m/src/0009B/vol.zarr', mode='r')['0']
    masque = np.asarray(vol[15]) > 0
    W = np.zeros_like(masque); W[4726:6774, 1664:4736] = True        # zone témoin : les 2 x 3 carrés
    masque &= W
    C = H + 'c0800/temoins/'
    oy, ox = map(int, open(C + 'vol_0009B_fenetre.origin').read().split())
    f = {('readerv3', 'direct'): C + 'reader-v3_0009B.tif', ('readerv3', 'inverse'): C + 'reader-v3_0009B_reverse.tif',
         ('argusv3', 'direct'): C + 'argus-v3_0009B.tif', ('argusv3', 'inverse'): C + 'argus-v3_0009B_reverse.tif'}
    E = {k: etire(lit_tif(v), masque) for k, v in f.items()}
    for s in ('direct', 'inverse'):
        E[('v8in', s)] = etire(lit_tif(C + 'v8in_0009B_%s.tif' % s, masque.shape, (oy, ox)), masque)
    return avec_moyenne(E, masque)


def planche(items, chemin):
    pas, haut = T // R4 + 5, T // R4 + 26
    img = Image.new('L', (COLS * pas, ((len(items) + COLS - 1) // COLS) * haut), 255)
    d = ImageDraw.Draw(img)
    for j, (n, im) in enumerate(items):
        x, y = (j % COLS) * pas, (j // COLS) * haut
        d.text((x + 4, y + 1), str(n), fill=0, font=F)
        img.paste(im, (x, y + 24))
    img.save(chemin)


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    if sys.argv[1] == 'essai':
        items = []
        for s in ('direct', 'inverse'):
            a = tifffile.imread(H + 'c343/pr59/v8in_0343P_%s.tif' % s).astype(np.float32)
            masque = a > 0; e = etire(a, masque)
            ys, xs = np.nonzero(masque)
            for Y in range(ys.min(), ys.max() - T // 2, T // 4):          # carrés chevauchants : 0343P est petit
                for X in range(xs.min(), xs.max() - T // 2, T // 4):
                    if masque[Y:Y + T, X:X + T].mean() >= 0.5:
                        items.append(reduit(e[Y:Y + T, X:X + T]))
        random.Random(59).shuffle(items)
        n_essai = 68                                                      # même longueur que le test : 24, 24, 20
        items = (items * (n_essai // max(1, len(items)) + 1))[:n_essai]
        for p in range(0, n_essai, PAR_PLANCHE):
            planche([(i + 1, items[i]) for i in range(p, min(p + PAR_PLANCHE, n_essai))],
                    OUT + 'essai_blanc_%d.png' % (p // PAR_PLANCHE + 1))
        print('essai a blanc : 68 carres de 0343P sur 3 planches (carres distincts disponibles : %d)' % len(set(map(id, items))))
        sys.exit()
    plan = json.load(open(H + 'c0800/plan_carres.json'))['carres']
    cache = {}
    V = {}                                                    # V[(j, c)] = vignette 256 px
    for j, t in enumerate(plan):
        cle_z = t['zone'] + t.get('surface', '')
        if cle_z not in cache:
            cache.clear()
            cache[cle_z] = (zone_0800(t['surface']) if t['zone'] == '0800' else
                            zone_erwin() if t['zone'] == 'erwin' else zone_0009B())
        E = cache[cle_z]
        for c, k in enumerate(COND):
            V[(j, c)] = reduit(E[k][t['y']:t['y'] + T, t['x']:t['x'] + T])
    cle = {'conditions': COND, 'carres': plan, 'lecteurs': {}}
    for r in range(LECTEURS):
        ordre = list(range(len(plan)))
        random.Random(60 + r).shuffle(ordre)
        k = {}
        for n, j in enumerate(ordre, 1):
            k[n] = [j, (j + r) % 8]
        for p in range(0, len(ordre), PAR_PLANCHE):
            planche([(n, V[tuple(k[n])]) for n in range(p + 1, min(p + PAR_PLANCHE, len(ordre)) + 1)],
                    OUT + 'planche_%02d_%d.png' % (r + 1, p // PAR_PLANCHE + 1))
        cle['lecteurs']['%02d' % (r + 1)] = k
    json.dump(cle, open(OUT + 'cle_pr60.json', 'w'), indent=1, ensure_ascii=False)
    n = {}
    for r, k in cle['lecteurs'].items():
        for j, c in k.values():
            n[(j, c)] = n.get((j, c), 0) + 1
    print(len(plan), 'carres,', LECTEURS, 'lecteurs ; lectures par (carre, condition) :', sorted(set(n.values())),
          '; couples', len(n))
