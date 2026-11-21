# PR-61 : dépouillement, figé avant toute lecture. Entrées : cle_pr61.json et reponses/reponse_NN.txt.
# Réponse d'un lecteur : un bloc « Image k » par panneau (k = 1..18), puis des lignes « case: nom (confiance) » ou « none ».
# Soutien s(w, o, c, n) = nombre de lecteurs distincts du panneau w dans le sens o qui nomment n dans une case à une case
# près de c (écart de colonne et de rangée <= 1). Forme constante : s >= 4 (sur 6 lecteurs).
# « Se répète » : forme constante dans le sens o, et s < 4 au même endroit, même nom, dans l'autre sens.
# Porte (Erwin) : lettre l (1-7 dans E1, 8-12 dans E2) qui se répète en sens direct à sa case, sous son nom ; >= 3 sur 12.
# Principal : signalés (3 dans son sens signalé) qui se répètent dans leur empreinte, contre les 12 témoins x 2 sens ;
# Fisher exact unilatéral, p <= 0,05.
# usage : c0800_score_fenetres.py CLE.json DOSSIER_REPONSES
import sys, re, json, random
from math import comb

NOMS = set('alpha beta gamma delta epsilon zeta eta theta iota kappa lambda mu nu xi omicron pi rho sigma tau upsilon '
           'phi chi psi omega'.split())
K, NPAN = 4, 18
COLS = 'ABCDEFGH'


def lit(f):
    """{k: set((col, rang, nom))} ou None si la réponse n'a pas ses 18 blocs ; et le nombre de lignes rejetées."""
    blocs, k, rejet = {}, None, 0
    for ligne in open(f, encoding='utf-8', errors='replace').read().splitlines():
        t = re.sub(r'[*`_#]', '', ligne).strip()                   # mise en forme (gras, code) ignorée
        m = re.match(r'(?i)image\s*(\d+)\s*:?\s*$', t)
        if m:
            k = int(m.group(1)); blocs.setdefault(k, set()); continue
        if not t or k is None or re.fullmatch(r'(?i)none\.?', t):
            continue
        m = re.match(r'(?i)^[-*\s]*([A-H])\s*([1-9])\s*[:\-]\s*(.*)$', t)
        nom = m and next((w for w in re.findall(r'[a-z]+', m.group(3).lower()) if w in NOMS), None)
        if m and nom and 1 <= int(m.group(2)) <= 3:
            blocs[k].add((COLS.index(m.group(1).upper()), int(m.group(2)) - 1, nom))
        else:
            rejet += 1
    return (blocs if all(i in blocs for i in range(1, NPAN + 1)) else None), rejet


def c2(c):
    return COLS.index(c[0]), int(c[1]) - 1


def soutien(items, c, n):
    """items : liste (par lecteur) d'ensembles (col, rang, nom)."""
    return sum(1 for it in items if any(nm == n and abs(a - c[0]) <= 1 and abs(b - c[1]) <= 1 for a, b, nm in it))


def constantes(items):
    return sorted({(a, b, n) for a in range(8) for b in range(3) for n in NOMS if soutien(items, (a, b), n) >= K})


def formes(cs):
    """regroupe les (case, nom) constants voisins de même nom en formes."""
    reste, out = list(cs), []
    while reste:
        g = [reste.pop()]; i = 0
        while i < len(g):
            v = [x for x in reste if x[2] == g[i][2] and abs(x[0] - g[i][0]) <= 1 and abs(x[1] - g[i][1]) <= 1]
            for x in v:
                reste.remove(x)
            g += v; i += 1
        out.append(g)
    return out


def repete(I, w, o, cases=None):
    """(case, nom) constants de w en sens o (dans cases si donné) absents (s < 4) en sens opposé."""
    oo = 'inverse' if o == 'direct' else 'direct'
    return [(a, b, n) for a, b, n in constantes(I[(w, o)]) if (cases is None or (a, b) in cases)
            and soutien(I[(w, oo)], (a, b), n) < K]


def p_fisher(rf, rc, nf, nch):
    N, Kt = nf + nch, rf + rc
    return sum(comb(Kt, x) * comb(N - Kt, nf - x) for x in range(rf, min(Kt, nf) + 1)) / comb(N, nf)


def cp(k, n, a=0.05):
    """intervalle exact de Clopper-Pearson, par bissection sur la loi binomiale."""
    def queue(p, sup):
        return sum(comb(n, j) * p ** j * (1 - p) ** (n - j) for j in (range(k, n + 1) if sup else range(0, k + 1)))
    def bis(f):
        lo, hi = 0.0, 1.0
        for _ in range(60):
            m = (lo + hi) / 2
            (lo, hi) = (m, hi) if f(m) else (lo, m)
        return (lo + hi) / 2
    bas = 0.0 if k == 0 else bis(lambda p: queue(p, True) < a / 2)
    haut = 1.0 if k == n else bis(lambda p: queue(p, False) > a / 2)
    return bas, haut


def nom_case(a, b):
    return '%s%d' % (COLS[a], b + 1)


if __name__ == '__main__':
    cle = json.load(open(sys.argv[1], encoding='utf-8'))
    D = sys.argv[2].rstrip('/') + '/'
    P = cle['plan']
    U = {u['unite']: u for u in P['unites']}
    pan = {p['nom']: p for u in P['unites'] for p in u['panneaux']}
    I = {(w, o): [] for w in pan for o in ('direct', 'inverse')}
    LECT = {(w, o): [] for w in pan for o in ('direct', 'inverse')}
    incidents = []
    for r, L in sorted(cle['lecteurs'].items()):
        try:
            blocs, rejet = lit(D + 'reponse_%s.txt' % r)
        except FileNotFoundError:
            blocs, rejet = None, 0
        if blocs is None:
            incidents.append('lecteur %s : reponse absente ou incomplete' % r); continue
        if rejet:
            incidents.append('lecteur %s : %d ligne(s) non lisible(s), ignoree(s)' % (r, rejet))
        for e in L:
            I[(e['panneau'], e['sens'])].append(blocs[e['image']])
            LECT[(e['panneau'], e['sens'])].append(r)
    print('lecteurs :', len(cle['lecteurs']), '; incidents :', '; '.join(incidents) or 'aucun')
    print('lectures par (panneau, sens) :', sorted({len(v) for v in I.values()}))

    # ---- porte
    print('\n== PORTE (Erwin, Reader V3) : lettre qui se repete en sens direct, a sa case, sous son nom')
    tenues = []
    for w in ('E1', 'E2'):
        for l, c in pan[w]['lettres'].items():
            n = P['noms_erwin'][l]
            sd, si = soutien(I[(w, 'direct')], c2(c), n), soutien(I[(w, 'inverse')], c2(c), n)
            ok = sd >= K and si < K
            tenues += [l] if ok else []
            print('   lettre %2s %-8s %s %s : direct %d/6, inverse %d/6 %s' % (l, n, w, c, sd, si, '<- SE REPETE' if ok else ''))
    porte = len(tenues) >= 3
    rng = random.Random(61); boot = []
    for _ in range(2000):
        nb = 0
        for w in ('E1', 'E2'):
            Id = [I[(w, 'direct')][rng.randrange(len(I[(w, 'direct')]))] for _ in I[(w, 'direct')]]
            Ii = [I[(w, 'inverse')][rng.randrange(len(I[(w, 'inverse')]))] for _ in I[(w, 'inverse')]]
            for l, c in pan[w]['lettres'].items():
                n = P['noms_erwin'][l]
                nb += soutien(Id, c2(c), n) >= K and soutien(Ii, c2(c), n) < K
        boot.append(nb)
    boot.sort()
    print('PORTE : %d lettre(s) sur 12 %s -> %s ; intervalle 95 %% (lecteurs reechantillonnes, 2000 tirages) %d - %d'
          % (len(tenues), tenues, 'TENUE' if porte else 'ECHOUE', boot[50], boot[1949]))

    # ---- principal
    print('\n== PRINCIPAL : se repeter dans l\'empreinte du carre de PR-60')
    def ligne(w, o):
        emp = {c2(c) for c in pan[w]['empreinte']}
        rep = repete(I, w, o, emp)
        return rep, '%-5s %-11s %-7s : %s' % (w, pan[w]['surface'], o, ', '.join(
            '%s %s (%d/6 contre %d/6)' % (nom_case(a, b), n, soutien(I[(w, o)], (a, b), n),
                                         soutien(I[(w, 'inverse' if o == 'direct' else 'direct')], (a, b), n))
            for a, b, n in rep) or 'rien')
    rf = 0
    for u in (x for x in P['unites'] if x['unite'].startswith('S')):
        rep, txt = ligne(u['unite'], u['sens_signale']); rf += bool(rep); print('   SIGNALE', txt)
    rc, nch = 0, 0
    for u in (x for x in P['unites'] if x['unite'].startswith('T')):
        for o in ('direct', 'inverse'):
            rep, txt = ligne(u['unite'], o); rc += bool(rep); nch += 1; print('   temoin ', txt)
    p = p_fisher(rf, rc, 3, nch)
    a, b = cp(rf, 3); c, d = cp(rc, nch)
    print('signales : %d / 3 (IC 95 %% %.2f - %.2f) ; temoins : %d / %d (IC 95 %% %.2f - %.2f) ; Fisher unilateral p = %.4f'
          % (rf, a, b, rc, nch, c, d, p))
    tient = p <= 0.05
    print('PRINCIPAL :', 'TIENT' if tient else 'ECHOUE')
    print('DECISION :', ('porte echoue : rien n est conclu sur 0800' if not porte else
                         'porte tenue, principal tenu : candidats = signales qui se repetent' if tient else
                         'porte tenue, principal echoue : les signalements de PR-60 ne se repetent pas mieux que des fenetres au hasard'))

    # ---- secondaires
    print('\n== SECONDAIRE 1 : toutes les formes constantes, partout, chaque panneau et chaque sens')
    for w in pan:
        for o in ('direct', 'inverse'):
            fs = formes(constantes(I[(w, o)]))
            if fs:
                oo = 'inverse' if o == 'direct' else 'direct'
                txt = []
                for g in fs:
                    s = {(a, b): soutien(I[(w, o)], (a, b), g[0][2]) for a, b, _ in g}
                    pic = [c for c in s if s[c] == max(s.values())]
                    txt.append('%s pic %s %d/6 (autre sens %d/6)' % (g[0][2], '+'.join(nom_case(*c) for c in pic),
                               max(s.values()), max(soutien(I[(w, oo)], c, g[0][2]) for c in pic)))
                print('   %-5s %-7s : %s' % (w, o, ' ; '.join(txt)))
    print('\n== SECONDAIRE 2 : temoin 0009B (rapporte seulement)')
    for l, c in pan['B']['lettres'].items():
        n = P['noms_0009B'][l]
        print('   lettre %2s %-8s %s : direct %d/6, inverse %d/6' % (l, n, c, soutien(I[('B', 'direct')], c2(c), n),
                                                               soutien(I[('B', 'inverse')], c2(c), n)))
    print('\n== SECONDAIRE 3 : Erwin, lectures justes par lettre (sur 6, a une case pres) et formes constantes fausses')
    for w in ('E1', 'E2'):
        bonnes = {(c2(c), P['noms_erwin'][l]) for l, c in pan[w]['lettres'].items()}
        for o in ('direct', 'inverse'):
            fausses = [(a, b, n) for a, b, n in constantes(I[(w, o)])
                       if not any(n == bn and abs(a - bc[0]) <= 1 and abs(b - bc[1]) <= 1 for bc, bn in bonnes)]
            print('   %s %-7s formes constantes fausses : %s' % (w, o, ', '.join('%s %s' % (nom_case(a, b), n) for a, b, n in fausses) or 'aucune'))
    print('\n== SECONDAIRE 4 : lettres nommees par lecteur (moyenne par panneau et sens)')
    for w in pan:
        print('   %-5s ' % w + '  '.join('%s %.1f' % (o, sum(len(x) for x in I[(w, o)]) / max(1, len(I[(w, o)])))
                                     for o in ('direct', 'inverse')))
