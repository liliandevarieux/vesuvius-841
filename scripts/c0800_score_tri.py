# Dépouillement du tri à un lecteur (étape 1), figé avant toute lecture. Entrées : cle_tri.json, reponses/reponse_NN.txt.
# Une lecture = un panneau lu par un lecteur ; elle « ressort » si le lecteur y nomme au moins 4 lettres (lignes
# « case: nom (confiance) » lisibles, doublons de même case et même nom comptés une fois).
# Porte de l'étape 1 : les 12 lectures directes des panneaux connus (E1, E2, B, 4 fois chacun) ressortent au moins 10
# fois, et les 12 lectures inverses au plus 2 fois.
# Sortie : la porte, puis les fenêtres de 0800 qui ressortent, avec leur sens, et le nombre de noms par lecture.
# usage : c0800_score_tri.py CLE.json DOSSIER_REPONSES
import sys, re, json, collections

NOMS = set('alpha beta gamma delta epsilon zeta eta theta iota kappa lambda mu nu xi omicron pi rho sigma tau upsilon '
           'phi chi psi omega'.split())
SEUIL = 4


def lit(f, n):
    blocs, k, rejet = {}, None, 0
    for ligne in open(f, encoding='utf-8', errors='replace').read().splitlines():
        t = re.sub(r'[*`_#]', '', ligne).strip()
        m = re.match(r'(?i)image\s*(\d+)\s*:?\s*$', t)
        if m:
            k = int(m.group(1)); blocs.setdefault(k, set()); continue
        if not t or k is None or re.fullmatch(r'(?i)none\.?', t):
            continue
        m = re.match(r'(?i)^[-*\s]*([A-H])\s*([1-9])\s*[:\-]\s*(.*)$', t)
        nom = m and next((w for w in re.findall(r'[a-z]+', m.group(3).lower()) if w in NOMS), None)
        if m and nom and 1 <= int(m.group(2)) <= 3:
            blocs[k].add((m.group(1).upper(), int(m.group(2)), nom))
        else:
            rejet += 1
    return (blocs if all(i in blocs for i in range(1, n + 1)) else None), rejet


if __name__ == '__main__':
    cle = json.load(open(sys.argv[1], encoding='utf-8'))
    D = sys.argv[2].rstrip('/') + '/'
    connus = set(cle['connus'])
    surf = {f['nom']: f['surface'] for f in cle['plan']['fenetres']}
    lect, incidents = [], []
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
            lect.append((e['panneau'], e['sens'], r, len(b[e['image']]), sorted(b[e['image']])))
    print('lecteurs :', len(cle['lecteurs']), '; lectures :', len(lect), '; incidents :', '; '.join(incidents) or 'aucun')
    kd = [x for x in lect if x[0] in connus and x[1] == 'direct']
    ki = [x for x in lect if x[0] in connus and x[1] == 'inverse']
    a, b = sum(x[3] >= SEUIL for x in kd), sum(x[3] >= SEUIL for x in ki)
    porte = len(kd) == 12 and len(ki) == 12 and a >= 10 and b <= 2
    print('\n== PORTE : panneaux connus qui ressortent (>= %d noms) : direct %d / %d, inverse %d / %d -> %s'
          % (SEUIL, a, len(kd), b, len(ki), 'TENUE' if porte else 'ECHOUE'))
    for x in sorted(kd + ki):
        print('   %-3s %-7s lecteur %s : %d noms' % x[:4])
    z = [x for x in lect if x[0] not in connus]
    print('\n== 0800 : %d lectures ; noms par lecture :' % len(z),
          dict(sorted(collections.Counter(x[3] for x in z).items())))
    for s in ('direct', 'inverse'):
        print('   %s : %d noms en tout' % (s, sum(x[3] for x in z if x[1] == s)))
    R = sorted((x for x in z if x[3] >= SEUIL), key=lambda x: (-x[3], x[0], x[1]))
    print('\n== FENETRES QUI RESSORTENT : %d' % len(R))
    for w, s, r, n, it in R:
        print('   %s %-11s %-7s lecteur %s : %d noms : %s' % (w, surf[w], s, r, n, ' '.join('%s%d %s' % t for t in it)))
    print('\nDECISION :', 'porte echoue : le tri ne dit rien' if not porte else
          ('aucune fenetre ne ressort' if not R else '%d fenetre(s) vers l etape 2' % len({x[0] for x in R})))
