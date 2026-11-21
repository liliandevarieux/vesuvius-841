# PR-61 : fenêtres de lecture « fenêtres v3 » (repli de PR-60) — plan, essai à blanc, panneaux de test et clé.
# Fenêtre = 1140 x 3200 px (3 rangées de 380 px x 8 colonnes de 400 px : les cases de PR-47), réduite x 0,5 (moyenne
# 2 x 2), grille rouge A-H x 1-3, repères en marge, aucun nom de carte. Les surfaces de 0800 sont des bandes de 1120 à
# 1560 px de haut : la fenêtre de PR-47 (1900 px) n'y entre pas.
# Carte : Reader V3, deux sens. Contraste : 1er au 99,5e centile des pixels de la surface dans la fenêtre ; hors surface
# en noir. Masques : 0800 et 0009B = couche 15 du volume > 0 ; Erwin = carte Reader V3 des organisateurs > 0 (PR-60).
# Placement sur 0800 : fenêtre centrée sur le carré de PR-60, décalée pour rester dans la carte ; « empreinte » = cases
# dont le centre tombe dans le carré. Signalés : carrés 3 et 30 (sens direct), 16 (sens inverse). Témoins : carrés de
# PR-60 tirés au hasard (graine 61) parmi les 49 autres, acceptés si leur fenêtre ne chevauche aucune fenêtre déjà prise,
# jusqu'à 12.
# Erwin : E1 lignes 980-2120, colonnes 300-3500 (lettres 1-7) ; E2 lignes 417-1557, colonnes 2441-5641 (lettres 8-12).
# 0009B : lignes 5230-6370, colonnes 1600-4800 (fenêtre de PR-47 ramenée à 1140 lignes ; ses 10 lettres).
# Carré latin : 17 unités (E = E1 + E2, B, 3 signalées, 12 témoins) ; le lecteur r (0..11) voit l'unité u dans le sens
# (u + r) mod 2 ; 18 panneaux par lecteur, ordre mélangé (graine 61 + r), noms de fichier neutres.
# usage : c0800_fenetres.py plan | essai | test
import sys, os, json, glob, random, string, numpy as np, tifffile, zarr
from PIL import Image, ImageDraw
sys.path.insert(0, '/home/slusarska_holding/vesuvius')
from banc_lisibilite import F

H = '/home/slusarska_holding/vesuvius/'
OUT = H + 'c0800/pr61/'
PANNEAUX = '/mnt/c/Users/SLUSAR~1/AppData/Local/Temp/claude/4203fc70abe36c49/ae02ffb6-78ce-4316-b98c-3d5acece68c1/scratchpad/pr61/'
FH, FW, NR, NCOL, M, T = 1140, 3200, 3, 8, 40, 1024
SENS = ('direct', 'inverse')
SIGNALES = {3: 'direct', 30: 'direct', 16: 'inverse'}
NTEMOINS, LECTEURS = 12, 12
E_FEN = {'E1': (980, 300, range(1, 8)), 'E2': (417, 2441, range(8, 13))}
B_FEN = (5230, 1600)
REF_B = {1: (5470.0, 2095.5), 2: (5453.0, 3508.0), 3: (5426.5, 2995.5), 4: (5416.5, 2558.0), 5: (5497.5, 3893.5),
         6: (5534.0, 4341.0), 7: (6161.0, 2128.0), 8: (6125.0, 2646.5), 9: (6184.0, 3586.0), 10: (6169.0, 3119.0)}
NOMS_B = {1: 'nu', 2: 'alpha', 3: 'mu', 4: 'omicron', 5: 'zeta', 6: 'epsilon', 7: 'eta', 8: 'sigma', 9: 'omicron',
          10: 'delta'}                                                   # score_pr47.py, inchangés


def case(y, x, y0, x0):
    """case (colonne, rangée) qui contient le point (y, x) d'une fenêtre d'origine (y0, x0), ou None."""
    j, i = int((x - x0) // (FW / NCOL)), int((y - y0) // (FH / NR))
    return ('ABCDEFGH'[j] + str(i + 1)) if 0 <= j < NCOL and 0 <= i < NR else None


def place(forme, ty, tx):
    cy, cx = ty + T // 2, tx + T // 2
    y0 = min(max(cy - FH // 2, 0), max(forme[0] - FH, 0))
    x0 = min(max(cx - FW // 2, 0), max(forme[1] - FW, 0))
    emp = [c for i in range(NR) for j in range(NCOL)
           for c in [case(y0 + (i + 0.5) * FH / NR, x0 + (j + 0.5) * FW / NCOL, y0, x0)]
           if ty <= y0 + (i + 0.5) * FH / NR < ty + T and tx <= x0 + (j + 0.5) * FW / NCOL < tx + T]
    return int(y0), int(x0), emp


def carte_0800(m, s):
    return H + 'c0800/cartes/%s_reader-v3%s.tif' % (m, '' if s == 'direct' else '_reverse')


def plan():
    carres = json.load(open(H + 'c0800/plan_carres.json'))['carres']
    formes = {}
    def forme(m):
        if m not in formes:
            formes[m] = tifffile.TiffFile(carte_0800(m, 'direct')).pages[0].shape
        return formes[m]
    U = [dict(unite='E', panneaux=[dict(nom=k, zone='erwin', y0=v[0], x0=v[1],
                                         lettres={str(l): None for l in v[2]}) for k, v in E_FEN.items()])]
    U.append(dict(unite='B', panneaux=[dict(nom='B', zone='0009B', y0=B_FEN[0], x0=B_FEN[1],
                                            lettres={str(l): case(y, x, *B_FEN) for l, (y, x) in REF_B.items()})]))
    pris = []
    def libre(m, y0, x0):
        return all(not (m == m2 and abs(x0 - x2) < FW and abs(y0 - y2) < FH) for m2, y2, x2 in pris)
    for j, s in SIGNALES.items():
        t = carres[j]; y0, x0, emp = place(forme(t['surface']), t['y'], t['x'])
        pris.append((t['surface'], y0, x0))
        U.append(dict(unite='S%d' % j, carre=j, sens_signale=s, panneaux=[dict(nom='S%d' % j, zone='0800',
                      surface=t['surface'], y0=y0, x0=x0, empreinte=emp)]))
    cand = [j for j, t in enumerate(carres) if t['zone'] == '0800' and j not in SIGNALES]
    random.Random(61).shuffle(cand)
    n = 0
    for j in cand:
        t = carres[j]; y0, x0, emp = place(forme(t['surface']), t['y'], t['x'])
        if n < NTEMOINS and libre(t['surface'], y0, x0):
            pris.append((t['surface'], y0, x0)); n += 1
            U.append(dict(unite='T%d' % j, carre=j, panneaux=[dict(nom='T%d' % j, zone='0800', surface=t['surface'],
                          y0=y0, x0=x0, empreinte=emp)]))
    # lettres d'Erwin : case du centre de chaque boîte de référence
    ref = json.load(open(H + 'c343/reference_12_lettres.json'))
    for p in U[0]['panneaux']:
        for l in ref:
            if str(l['id']) in p['lettres']:
                z = l['zone']
                p['lettres'][str(l['id'])] = case((z[1] + z[3]) / 2, (z[0] + z[2]) / 2, p['y0'], p['x0'])
    noms = {str(l['id']): l['nom'] for l in ref}
    return dict(fenetre=[FH, FW], unites=U, noms_erwin=noms,
                noms_0009B={str(k): v for k, v in NOMS_B.items()})


def etire(a, masque):
    v = a[masque]
    lo, hi = np.percentile(v, [1, 99.5]) if v.size else (0, 1)
    return np.where(masque, np.clip((a - lo) / max(hi - lo, 1e-6), 0, 1), 0).astype(np.float32)


def decoupe(a, y0, x0):
    b = np.zeros((FH, FW), a.dtype)
    c = a[y0:y0 + FH, x0:x0 + FW]
    b[:c.shape[0], :c.shape[1]] = c
    return b


def panneau(a, masque, chemin):
    e = etire(a.astype(np.float32), masque)
    r = e.reshape(FH // 2, 2, FW // 2, 2).mean((1, 3))
    im = Image.fromarray(np.round(r * 255).astype(np.uint8)).convert('RGB')
    out = Image.new('RGB', (im.width + M, im.height + M), (255, 255, 255))
    out.paste(im, (M, M))
    d = ImageDraw.Draw(out)
    for j in range(NCOL + 1):
        x = M + int(j * FW / NCOL / 2); d.line([(x, M), (x, M + im.height)], fill=(255, 60, 60), width=1)
    for i in range(NR + 1):
        y = M + int(i * FH / NR / 2); d.line([(M, y), (M + im.width, y)], fill=(255, 60, 60), width=1)
    for j in range(NCOL):
        d.text((M + int((j + 0.5) * FW / NCOL / 2) - 7, 6), 'ABCDEFGH'[j], fill=(0, 0, 0), font=F)
    for i in range(NR):
        d.text((12, M + int((i + 0.5) * FH / NR / 2) - 13), str(i + 1), fill=(0, 0, 0), font=F)
    out.save(chemin)


def source(p, s):
    """(carte, masque) découpées pour le panneau p dans le sens s."""
    if p['zone'] == '0800':
        z = glob.glob(H + 'c0800/atlas/%s/surface-volumes/*.zarr' % p['surface'])[0]
        mq = np.asarray(zarr.open(z, mode='r')['0'][15]) > 0
        a = tifffile.imread(carte_0800(p['surface'], s))
    elif p['zone'] == 'erwin':
        mq = tifffile.imread(H + 'c0800/pr60/erwin/masque_readerv3_organisateurs.tif') > 0
        a = tifffile.imread(H + 'c0800/pr60/erwin/readerv3_%s.tif' % s)
    else:
        mq = np.asarray(zarr.open(H + 'ft12m/src/0009B/vol.zarr', mode='r')['0'][15]) > 0
        a = tifffile.imread(H + 'c0800/temoins/reader-v3_0009B%s.tif' % ('' if s == 'direct' else '_reverse'))
    return decoupe(a, p['y0'], p['x0']), decoupe(mq, p['y0'], p['x0'])


def nom_neutre(rng, pris):
    while True:
        n = ''.join(rng.choice(string.ascii_lowercase) for _ in range(6))
        if n not in pris:
            pris.add(n); return n


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True); os.makedirs(PANNEAUX, exist_ok=True)
    if sys.argv[1] == 'plan':
        P = plan()
        json.dump(P, open(OUT + 'plan_fenetres.json', 'w'), indent=1, ensure_ascii=False)
        for u in P['unites']:
            for p in u['panneaux']:
                print(u['unite'], p['zone'], p.get('surface', ''), 'y0', p['y0'], 'x0', p['x0'],
                      'empreinte', p.get('empreinte'), 'lettres', p.get('lettres'))
        print(len(P['unites']), 'unites,', sum(len(u['panneaux']) for u in P['unites']), 'panneaux par lecteur')
    elif sys.argv[1] == 'essai':
        # hors test : Argus V3 sur 0009B, bandes de 1140 lignes au-dessus de la fenêtre témoin, deux sens
        mq = np.asarray(zarr.open(H + 'ft12m/src/0009B/vol.zarr', mode='r')['0'][15]) > 0
        items = []
        for s in SENS:
            a = tifffile.imread(H + 'c0800/temoins/argus-v3_0009B%s.tif' % ('' if s == 'direct' else '_reverse'))
            for y0 in (0, 1140, 2280, 3420):
                for x0 in (0, 2500):
                    items.append((a, y0, x0))
        items += items[:2]
        rng = random.Random(6199); vus = set(); noms = []
        for a, y0, x0 in items:
            n = nom_neutre(rng, vus); noms.append(n)
            panneau(decoupe(a, y0, x0), decoupe(mq, y0, x0), PANNEAUX + 'essai_%s.png' % n)
        json.dump(noms, open(OUT + 'essai_noms.json', 'w'))
        print('essai a blanc :', len(noms), 'panneaux Argus V3 0009B hors fenetre temoin ->', PANNEAUX)
    elif sys.argv[1] == 'test':
        P = json.load(open(OUT + 'plan_fenetres.json'))
        U = P['unites']
        cache = {}
        for u in U:
            for p in u['panneaux']:
                for s in SENS:
                    cache[(p['nom'], s)] = source(p, s)
        cle = dict(plan=P, lecteurs={})
        for r in range(LECTEURS):
            liste = [(p['nom'], SENS[(ui + r) % 2]) for ui, u in enumerate(U) for p in u['panneaux']]
            random.Random(61 + r).shuffle(liste)
            rng = random.Random(6100 + r); vus = set(); L = []
            for k, (nom, s) in enumerate(liste, 1):
                f = nom_neutre(rng, vus)
                panneau(*cache[(nom, s)], PANNEAUX + 'l%02d_%s.png' % (r + 1, f))
                L.append(dict(image=k, fichier='l%02d_%s.png' % (r + 1, f), panneau=nom, sens=s))
            cle['lecteurs']['%02d' % (r + 1)] = L
        json.dump(cle, open(OUT + 'cle_pr61.json', 'w'), indent=1, ensure_ascii=False)
        n = {}
        for L in cle['lecteurs'].values():
            for e in L:
                n[(e['panneau'], e['sens'])] = n.get((e['panneau'], e['sens']), 0) + 1
        print(LECTEURS, 'lecteurs ; lectures par (panneau, sens) :', sorted(set(n.values())), '; couples', len(n))
