# PR-62, étape 2 : dépouillement, publié avant la construction des panneaux de l'étape 2.
# Mesure de PR-61 (c0800_score_fenetres.py) : soutien à une case près, forme constante = au moins 4 lecteurs sur 6,
# « se répète » = moins de 4 au même endroit dans l'autre sens ; les (case, nom) qui se répètent sont regroupés en formes.
# Porte 2 : E1 et E2 montrent chacun au moins 3 formes qui se répètent en sens direct.
# Principal : une fenêtre gardée est « comme du texte » si elle montre au moins 3 formes qui se répètent dans le sens où
# elle est ressortie à l'étape 1.
# usage : c0800_score_tri2.py CLE.json DOSSIER_REPONSES FENETRE:SENS [FENETRE:SENS ...]
import sys, json
sys.path.insert(0, __file__.rsplit('/', 1)[0] if '/' in __file__ else '.')
import c0800_score_fenetres as F
from c0800_score_tri import lit


if __name__ == '__main__':
    cle = json.load(open(sys.argv[1], encoding='utf-8'))
    D = sys.argv[2].rstrip('/') + '/'
    gardees = dict(a.split(':') for a in sys.argv[3:])
    I, incidents = {}, []
    for r, L in sorted(cle['lecteurs'].items()):
        try:
            b, rejet = lit(D + 'reponse_%s.txt' % r, len(L))
        except FileNotFoundError:
            b, rejet = None, 0
        if b is None:
            incidents.append('lecteur %s : reponse absente ou incomplete' % r); continue
        if rejet:
            incidents.append('lecteur %s : %d ligne(s) non lisible(s), ignoree(s)' % (r, rejet))
        for e in L:
            I.setdefault((e['panneau'], e['sens']), []).append(
                {(F.COLS.index(c), n - 1, nom) for c, n, nom in b[e['image']]})
    print('lecteurs :', len(cle['lecteurs']), '; incidents :', '; '.join(incidents) or 'aucun')
    print('lectures par (panneau, sens) :', sorted({len(v) for v in I.values()}))

    def detail(w, o):
        fs = F.formes(F.repete(I, w, o))
        oo = 'inverse' if o == 'direct' else 'direct'
        txt = []
        for g in fs:
            s = {(a, b): F.soutien(I[(w, o)], (a, b), g[0][2]) for a, b, _ in g}
            pic = [c for c in s if s[c] == max(s.values())]
            txt.append('%s pic %s %d/6 (autre sens %d/6)' % (g[0][2], '+'.join(F.nom_case(*c) for c in pic),
                       max(s.values()), max(F.soutien(I[(w, oo)], c, g[0][2]) for c in pic)))
        return len(fs), ' ; '.join(txt) or 'aucune'

    print('\n== PORTE 2 : formes qui se repetent en sens direct (>= 3 chacune)')
    ok = True
    for w in ('E1', 'E2'):
        n, t = detail(w, 'direct'); ok &= n >= 3
        print('   %s : %d : %s' % (w, n, t))
    print('PORTE 2 :', 'TENUE' if ok else 'ECHOUE')
    print('\n== PRINCIPAL : fenetres gardees, dans le sens ou elles sont ressorties (>= 3 formes)')
    comme = []
    for g, o in gardees.items():
        n, t = detail(g, o)
        comme += [g] if n >= 3 else []
        print('   %s %s : %d forme(s) : %s -> %s' % (g, o, n, t, 'COMME DU TEXTE' if n >= 3 else 'non'))
    print('\n== TOUS LES PANNEAUX ET SENS')
    for (w, o) in sorted(I):
        n, t = detail(w, o)
        print('   %-5s %-7s : %d forme(s), %.1f noms par lecteur : %s'
              % (w, o, n, sum(len(x) for x in I[(w, o)]) / len(I[(w, o)]), t))
    print('\nDECISION :', 'porte 2 echoue : l etape 2 ne dit rien' if not ok else
          ('candidat(s) : ' + ', '.join(comme) if comme else 'aucune fenetre comme du texte'))
