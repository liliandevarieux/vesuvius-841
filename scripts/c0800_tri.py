# Tri à un lecteur des 81 autres surfaces de 0800 (Reader V3, deux sens), format « fenêtres v3 » de PR-61.
# plan     : fenêtres de 1140 x 3200 px posées en grille au coin haut-gauche de la boîte du masque (couche 15 > 0) de
#            chaque surface, pas de 1140 lignes et 3200 colonnes ; gardées si au moins 30 % de la fenêtre est sur la surface.
#            Ne lit que le masque du scanner et la forme des cartes, aucune valeur d'encre.
# panneaux : un panneau par fenêtre et par sens, plus les panneaux connus de PR-61 (E1, E2, B, deux sens), chacun 4 fois ;
#            répartis par 18 entre lecteurs (graine 62), sans qu'un lecteur voie deux fois la même fenêtre ou le même
#            panneau connu ; noms de fichier neutres.
# usage : c0800_tri.py plan | panneaux
import sys, os, json, glob, random, numpy as np, tifffile, zarr
sys.path.insert(0, '/home/slusarska_holding/vesuvius')
import c0800_fenetres as W

H = '/home/slusarska_holding/vesuvius/'
OUT = H + 'c0800/tri/'
PANNEAUX = W.PANNEAUX.rstrip('/').rsplit('/', 1)[0] + '/tri/'
COUV, PAR_LECTEUR, COPIES_CONNUS = 0.30, 18, 4


def carte(m, s):
    return H + 'c0800/cartes_ext/%s_reader-v3%s.tif' % (m, '' if s == 'direct' else '_reverse')


def masque(m):
    z = glob.glob(H + 'c0800/atlas/%s/surface-volumes/*.zarr' % m)[0]
    return np.asarray(zarr.open(z, mode='r')['0'][15]) > 0


def plan():
    surf = [l.split('\t')[0] for l in open(H + 'c0800_surfaces_ext.tsv') if l.strip()]
    F, manque, tot, dedans = [], [], 0, 0
    for m in surf:
        if not (os.path.exists(carte(m, 'direct')) and os.path.exists(carte(m, 'inverse'))):
            manque.append(m); continue
        S = masque(m); tot += int(S.sum()); cov = np.zeros_like(S)
        ys, xs = np.nonzero(S)
        for y0 in range(ys.min(), ys.max() + 1, W.FH):
            for x0 in range(xs.min(), xs.max() + 1, W.FW):
                c = S[y0:y0 + W.FH, x0:x0 + W.FW].sum() / (W.FH * W.FW)
                if c >= COUV:
                    F.append(dict(nom='F%03d' % len(F), surface=m, y0=int(y0), x0=int(x0), part=round(float(c), 3)))
                    cov[y0:y0 + W.FH, x0:x0 + W.FW] = True
        dedans += int((S & cov).sum())
    P = dict(fenetres=F, manquantes=manque, pixels_surface=tot, pixels_couverts=dedans)
    json.dump(P, open(OUT + 'plan_tri.json', 'w'), indent=1)
    print(len(F), 'fenetres sur', len(surf) - len(manque), 'surfaces ; couverture %.1f %%' % (100 * dedans / max(tot, 1)),
          '; surfaces sans carte :', manque or 'aucune')


def panneaux():
    P = json.load(open(OUT + 'plan_tri.json'))
    connus = json.load(open(H + 'c0800/pr61/plan_fenetres.json'))
    kp = {p['nom']: p for u in connus['unites'] for p in u['panneaux'] if p['nom'] in ('E1', 'E2', 'B')}
    items = [(f['nom'], s) for f in P['fenetres'] for s in W.SENS]
    items += [(k, s) for k in kp for s in W.SENS for _ in range(COPIES_CONNUS)]
    rng = random.Random(62); rng.shuffle(items)
    n = -(-len(items) // PAR_LECTEUR)
    L = [[] for _ in range(n)]
    for i, it in enumerate(items):         # tour de rôle ; on saute un lecteur plein ou qui a déjà vu ce panneau
        for d in range(n):
            r = (i + d) % n
            if len(L[r]) < PAR_LECTEUR and all(it[0] != x[0] for x in L[r]):
                L[r].append(it); break
        else:
            raise SystemExit('repartition impossible pour %s' % (it,))
    os.makedirs(PANNEAUX, exist_ok=True)
    cache = {}
    def src(nom, s):
        if nom in kp:
            return W.source(kp[nom], s)
        f = next(x for x in P['fenetres'] if x['nom'] == nom)
        if f['surface'] not in cache:
            cache.clear(); cache[f['surface']] = masque(f['surface'])
        a = tifffile.imread(carte(f['surface'], s))
        return W.decoupe(a, f['y0'], f['x0']), W.decoupe(cache[f['surface']], f['y0'], f['x0'])
    cle = dict(plan=P, connus={k: v for k, v in kp.items()}, lecteurs={})
    for r, lst in enumerate(L):
        rng = random.Random(6200 + r); vus = set(); out = []
        for k, (nom, s) in enumerate(lst, 1):
            f = 't%02d_%s.png' % (r + 1, W.nom_neutre(rng, vus))
            W.panneau(*src(nom, s), PANNEAUX + f)
            out.append(dict(image=k, fichier=f, panneau=nom, sens=s))
        cle['lecteurs']['%02d' % (r + 1)] = out
    json.dump(cle, open(OUT + 'cle_tri.json', 'w'), indent=1, ensure_ascii=False)
    print(len(items), 'lectures,', n, 'lecteurs, tailles', sorted({len(x) for x in L}))


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    {'plan': plan, 'panneaux': panneaux}[sys.argv[1]]()
