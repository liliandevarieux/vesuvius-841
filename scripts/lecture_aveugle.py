# PR-46 : lecture a l aveugle. Construit 4 planches : les 28 traces humains seuls (lecteur de reference), puis 3 planches
# de 28 cartes (chaque lettre une fois par planche, modeles tournes entre planches : carre latin), melangees, sans nom de
# modele ni trace. La cle (case -> feuillet, lettre, modele) va dans un fichier a part, que les lecteurs ne voient pas.
# Lettres et cadrage comme panneau_lettres_841.py (etiquettes & supervision niveau 2, cote >= 150 px, marge 40 px).
# usage : lecture_aveugle.py DOSSIER_PLANCHES FICHIER_CLE
import sys, json, random, numpy as np, tifffile, zarr
from scipy import ndimage
from PIL import Image, ImageDraw, ImageFont

C = '/home/slusarska_holding/vesuvius/'
MODELES = ['base', 'R4', 'readerv2']
CARTE = {'base': lambda s: 'pr31_base_%s.tif' % s,
         'R4': lambda s: 'pr34_R4_%s_%s.tif' % ('0009B' if s == '0009B' else '0841', s),
         'readerv2': lambda s: ('pr45_readerv2_%s.tif' if s == '0009B' else 'pr44_readerv2_%s.tif') % s}
FEUILLETS = ['841_w00', '841_segA', '841_segB', '0009B']
T, M = 200, 40
try:
    F = ImageFont.load_default(size=20)
except TypeError:
    F = ImageFont.load_default()


def niv2(s, n):
    a = np.asarray(zarr.open('%sft12m/src/%s/%s.zarr' % (C, s, n), mode='r')['2'][:]).squeeze()
    return (a.any(axis=0) if a.ndim == 3 else a) > 0


def vignette(a, carte):
    lo, hi = np.percentile(a, [1, 99.5]) if carte else (0, 255)
    b = np.clip((a - lo) / max(hi - lo, 1e-6) * 255, 0, 255).astype(np.uint8)
    r = T / max(b.shape)
    im = Image.fromarray(b).resize((max(1, int(b.shape[1] * r)), max(1, int(b.shape[0] * r))), Image.BILINEAR)
    fond = Image.new('L', (T, T), 0)
    fond.paste(im, ((T - im.width) // 2, (T - im.height) // 2))
    return fond


def planche(items, chemin):
    cols, H = 4, T + 28
    img = Image.new('L', (cols * (T + 12), ((len(items) + cols - 1) // cols) * H), 255)
    d = ImageDraw.Draw(img)
    for j, (n, im) in enumerate(items):
        x, y = (j % cols) * (T + 12), (j // cols) * H
        d.text((x + 4, y + 2), str(n), fill=0, font=F)
        img.paste(im, (x, y + 26))
    img.save(chemin)


lettres = []
for s in FEUILLETS:
    L = niv2(s, 'inklabels') & niv2(s, 'supervision')
    lab, _ = ndimage.label(L)
    objs = [(k + 1, sl) for k, sl in enumerate(ndimage.find_objects(lab))
            if max(sl[0].stop - sl[0].start, sl[1].stop - sl[1].start) >= 150]
    G = {}
    for m in MODELES:
        P = tifffile.imread(C + 'predictions/' + CARTE[m](s)).astype(np.float32)
        if P.ndim == 3:
            P = P[0] if P.shape[0] < P.shape[-1] else P[..., 0]
        G[m] = ndimage.zoom(P, (L.shape[0] / P.shape[0], L.shape[1] / P.shape[1]), order=1)[:L.shape[0], :L.shape[1]]
    for i, (k, sl) in enumerate(objs):
        y0, y1 = max(0, sl[0].start - M), min(L.shape[0], sl[0].stop + M)
        x0, x1 = max(0, sl[1].start - M), min(L.shape[1], sl[1].stop + M)
        imgs = {'trace': vignette((lab[y0:y1, x0:x1] == k).astype(np.float32) * 255, False)}
        for m in MODELES:
            imgs[m] = vignette(G[m][y0:y1, x0:x1], True)
        lettres.append((s, i + 1, imgs))
    print(s, len(objs), 'lettres')

N, out, cle = len(lettres), sys.argv[1], {}
ordre = list(range(N))
random.Random(460).shuffle(ordre)
planche([(c + 1, lettres[j][2]['trace']) for c, j in enumerate(ordre)], out + '/2026-09-28_pr46_planche_traces.png')
cle['traces'] = {c + 1: [lettres[j][0], lettres[j][1], 'trace'] for c, j in enumerate(ordre)}
for r in range(3):
    ordre = list(range(N))
    random.Random(461 + r).shuffle(ordre)
    k = {c + 1: [lettres[j][0], lettres[j][1], MODELES[(j + r) % 3]] for c, j in enumerate(ordre)}
    planche([(c, lettres[j][2][k[c][2]]) for c, j in zip(k, ordre)], out + '/2026-09-28_pr46_planche_%d.png' % (r + 1))
    cle['lecteur%d' % (r + 1)] = k
json.dump(cle, open(sys.argv[2], 'w'), indent=1)
print(N, 'lettres, 4 planches ecrites ; cle dans', sys.argv[2])
