# Banc d essai de lisibilite, version 1 (regle 7 de notes/14-methode.md) : le protocole de PR-46 rendu fixe et
# reutilisable. Une configuration JSON par test (configs/banc_<test>.json) dit quelles recettes comparer et avec
# quelles cartes (une par graine). Deux commandes :
#   planches CONFIG.json : les 28 lettres etiquetees de PR-46 (841 w00/segA/segB, 0009B ; etiquettes & supervision
#     niveau 2, cote >= 150 px, marge 40 px, vignettes 200 px, contraste 1-99,5 %), une planche de 28 vignettes par
#     lecteur ; carre latin : le lecteur r lit la lettre j sur la recette (j + r) mod nb_recettes ; graine de la carte
#     equilibree : indice (r div nb_recettes) mod nb_cartes. Sens des couches choisi sans etiquette (p99-p50 le plus haut
#     sur le papyrus, comme eval_sup.py). Planche d essai a blanc : memes cadres decales vers la droite, non comptee.
#     La cle (case -> feuillet, lettre, recette, carte) va dans un fichier que les lecteurs ne voient pas.
#   score CONFIG.json : reference = majorite des 3 lecteurs de traces (lettre ecartee sans majorite) ; lectures justes
#     par lettre et par recette sur les lettres propres ; comparaison de deux recettes : permutation des signes par
#     lettre (unilaterale, 10 000 tirages) et intervalle a 95 % par reechantillonnage des lettres puis des lectures.
# usage : banc_lisibilite.py planches|score CONFIG.json
import sys, json, random, re, collections, numpy as np, tifffile, zarr
from scipy import ndimage
from PIL import Image, ImageDraw, ImageFont

C = '/home/slusarska_holding/vesuvius/'
FEUILLETS = ['841_w00', '841_segA', '841_segB', '0009B']
NOMS = ('alpha beta gamma delta epsilon zeta eta theta iota kappa lambda mu nu xi omicron pi rho sigma tau upsilon '
        'phi chi psi omega unreadable').split()
T, M = 200, 40
try:
    F = ImageFont.load_default(size=20)
except TypeError:
    F = ImageFont.load_default()


def niv2(s, n):
    a = np.asarray(zarr.open('%sft12m/src/%s/%s.zarr' % (C, s, n), mode='r')['2'][:]).squeeze()
    return (a.any(axis=0) if a.ndim == 3 else a) > 0


def fichier(gabarit, s):
    pli = '0009B' if s == '0009B' else '0841'
    rv2 = 'pr45_readerv2_0009B.tif' if s == '0009B' else 'pr44_readerv2_%s.tif' % s
    return gabarit.format(pli=pli, s=s, rv2=rv2)


def carte(f):
    P = tifffile.imread(C + 'predictions/' + f).astype(np.float32)
    return P[0] if P.ndim == 3 and P.shape[0] < P.shape[-1] else (P[..., 0] if P.ndim == 3 else P)


def sens(f):
    """Sens des couches sans etiquette : garde la carte (directe ou _reverse) au p99-p50 le plus haut."""
    best = None
    for g in (f, f.replace('.tif', '_reverse.tif')):
        P = carte(g)
        v = P[P > 0]
        s = np.percentile(v, 99) - np.percentile(v, 50)
        if best is None or s > best[0]:
            best = (s, g, P)
    return best[1], best[2]


def vignette(a):
    lo, hi = np.percentile(a, [1, 99.5])
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


def planches(K):
    rec = list(K['recettes'])
    choix, lettres = {}, []
    for s in FEUILLETS:
        L = niv2(s, 'inklabels') & niv2(s, 'supervision')
        lab, _ = ndimage.label(L)
        objs = [sl for sl in ndimage.find_objects(lab) if max(sl[0].stop - sl[0].start, sl[1].stop - sl[1].start) >= 150]
        G = {}
        for m in rec:
            for i, gab in enumerate(K['recettes'][m]):
                g, P = sens(fichier(gab, s))
                choix[(m, i, s)] = g
                G[(m, i)] = ndimage.zoom(P, (L.shape[0] / P.shape[0], L.shape[1] / P.shape[1]), order=1)[:L.shape[0], :L.shape[1]]
        dx = K['essai_a_blanc']['decalage']
        for i, sl in enumerate(objs):
            y0, y1 = max(0, sl[0].start - M), min(L.shape[0], sl[0].stop + M)
            x0, x1 = max(0, sl[1].start - M), min(L.shape[1], sl[1].stop + M)
            e0, e1 = min(x0 + dx, L.shape[1] - (x1 - x0)), min(x1 + dx, L.shape[1])
            lettres.append((s, i + 1, {k: vignette(G[k][y0:y1, x0:x1]) for k in G},
                            {k: vignette(G[k][y0:y1, e0:e1]) for k in G}))
        print(s, len(objs), 'lettres')
    for (m, i, s), g in sorted(choix.items()):
        print('carte %-8s graine %d %-9s -> %s' % (m, i, s, g))
    N, cle = len(lettres), {'cartes': {'%s|%d|%s' % k: g for k, g in choix.items()}}
    for r in range(K['lecteurs']):
        ordre = list(range(N))
        random.Random(K['graine'] + r).shuffle(ordre)
        k = {}
        for c, j in enumerate(ordre):
            m = rec[(j + r) % len(rec)]
            i = (r // len(rec)) % len(K['recettes'][m])
            k[c + 1] = [lettres[j][0], lettres[j][1], m, i]
        planche([(c, lettres[j][2][(k[c][2], k[c][3])]) for c, j in zip(k, ordre)],
                '%s/%s_%s_planche_%02d.png' % (K['dossier_images'], K['date'], K['nom'], r + 1))
        cle['lecteur%02d' % (r + 1)] = k
    ordre = list(range(N))
    random.Random(K['graine'] - 1).shuffle(ordre)
    essai = K['essai_a_blanc']['cartes']
    planche([(c + 1, lettres[j][3][tuple(essai[c % len(essai)])]) for c, j in enumerate(ordre)],
            '%s/%s_%s_essai_blanc.png' % (K['dossier_images'], K['date'], K['nom']))
    json.dump(cle, open(C + K['cle'], 'w'), indent=1)
    print(N, 'lettres,', K['lecteurs'], 'planches et une planche d essai a blanc ; cle dans', K['cle'])


def lit(f):
    r = {}
    for l in open(f, encoding='utf-8'):
        m = re.match(r'\s*`?(\d+)\s*:(.*)', l)
        if m:
            mots = re.findall(r'[a-z]+', m.group(2).lower())
            r[int(m.group(1))] = next((w for w in mots if w in NOMS), '?')
    return r


def compare(J, a, b, rng, n=10000):
    ls = sorted(l for l in J if a in J[l] and b in J[l])
    d = np.array([sum(J[l][a]) - sum(J[l][b]) for l in ls])
    S = int(d.sum())
    flips = rng.choice([-1, 1], (n, len(d)))
    p = (1 + int(((flips * d).sum(1) >= S).sum())) / (n + 1)
    boot = []
    for _ in range(n):
        tot = 0
        for l in rng.choice(len(ls), len(ls)):
            xa, xb = np.array(J[ls[l]][a]), np.array(J[ls[l]][b])
            tot += xa[rng.integers(0, len(xa), len(xa))].sum() - xb[rng.integers(0, len(xb), len(xb))].sum()
        boot.append(tot)
    k = np.mean([len(J[l][a]) for l in ls])
    lo, hi = np.percentile(boot, [2.5, 97.5]) / k
    return S, S / k, lo, hi, p, len(ls)


def score(K):
    ct = json.load(open(C + K['reference']['cle_traces']))['traces']
    reps = [lit(C + f) for f in K['reference']['lecteurs']]
    ref = {}
    for c, (s, n, _) in ct.items():
        noms = [r.get(int(c), '?') for r in reps]
        nom, v = collections.Counter(noms).most_common(1)[0]
        if v >= 2 and nom not in ('unreadable', '?'):
            ref[(s, n)] = nom
        else:
            print('lettre ecartee (pas de majorite) :', s, n, noms)
    vues = {tuple(v) for v in K['vues']}
    cle = json.load(open(C + K['cle']))
    J = collections.defaultdict(lambda: collections.defaultdict(list))
    graine = collections.defaultdict(lambda: [0, 0])
    manque = []
    for r in range(1, K['lecteurs'] + 1):
        f = C + K['reponses'].format(r)
        try:
            rep = lit(f)
        except FileNotFoundError:
            manque.append(r)
            continue
        for c, (s, n, m, i) in cle['lecteur%02d' % r].items():
            if (s, n) not in ref or (s, n) in vues:
                continue
            ok = rep.get(int(c), '?') == ref[(s, n)]
            J[(s, n)][m].append(int(ok))
            graine[(m, i)][0] += ok
            graine[(m, i)][1] += 1
    if manque:
        print('REPONSES MANQUANTES, lecteurs :', manque)
    print('lettres propres comptees :', len(J))
    for m in K['recettes']:
        t = [sum(J[l][m]) for l in J]
        n = [len(J[l][m]) for l in J]
        print('%-9s : %3d lectures justes sur %3d  (%.1f lettres sur %d, a %d lectures par lettre)'
              % (m, sum(t), sum(n), sum(t) / max(1, np.mean(n)), len(J), round(np.mean(n))))
        for i in range(len(K['recettes'][m])):
            g = graine[(m, i)]
            print('            graine %d : %d / %d' % (i, g[0], g[1]))
    rng = np.random.default_rng(K['graine'])
    for a, b in [K['primaire']] + K['secondaires']:
        S, dl, lo, hi, p, nl = compare(J, a, b, rng)
        print('%-9s - %-9s : %+d lectures = %+.2f lettres [IC 95 %% %+.2f ; %+.2f], p unilateral = %.4f (%d lettres)'
              % (a, b, S, dl, lo, hi, p, nl))
        if [a, b] == K['primaire']:
            print('PRIMAIRE : %s' % ('TIENT (p < 0,05, %s devant)' % a if p < 0.05 and S > 0 else 'echoue'))


if __name__ == '__main__':
    K = json.load(open(sys.argv[2]))
    {'planches': planches, 'score': score}[sys.argv[1]](K)
