# PR-62 : capacité du tri, calculée AVANT l'inscription, exactement (lois binomiales), et données de PR-61 qui ont fixé
# les seuils. usage : python capacite_pr62.py [chemin de results/pr61]
import sys, json
from math import comb


def queue(n, k, p):
    return sum(comb(n, j) * p ** j * (1 - p) ** (n - j) for j in range(k, n + 1))


print('== Porte de l etape 1 : >= 10 des 12 lectures directes connues ressortent, et <= 2 des 12 inverses')
for p in (0.95, 0.9, 0.85, 0.8, 0.7):
    print('   p(lecture directe connue ressort) = %.2f -> P(>= 10 / 12) = %.3f' % (p, queue(12, 10, p)))
for q in (0.0, 0.05, 0.1, 0.2):
    print('   p(lecture inverse connue ressort) = %.2f -> P(<= 2 / 12) = %.3f' % (q, 1 - queue(12, 3, q)))
print('\n== Une fenêtre de 0800 qui porte un texte lu comme celui d Erwin : P(ressortir) dans son sens, une lecture')
for p in (0.95, 0.9, 0.8, 0.6):
    print('   p = %.2f -> ressort : %.2f' % (p, p))
print('== Fausses sorties attendues sur N lectures sans texte, au taux f')
for f in (1 / 180, 0.01, 0.02):
    print('   f = %.4f : sur 500 lectures, %.1f attendues' % (f, 500 * f))
if len(sys.argv) > 1:
    sys.path.insert(0, sys.argv[1] + '/../../scripts')
    import c0800_score_fenetres as F
    cle = json.load(open(sys.argv[1] + '/cle_pr61.json', encoding='utf-8'))
    pan = {p['nom']: p for u in cle['plan']['unites'] for p in u['panneaux']}
    n = {}
    I = {}
    for r, L in cle['lecteurs'].items():
        b, _ = F.lit(sys.argv[1] + '/reponses/reponse_%s.txt' % r)
        for e in L:
            k = (pan[e['panneau']]['zone'], e['sens'])
            n.setdefault(k, []).append(len(b[e['image']]))
            I.setdefault((e['panneau'], e['sens']), []).append(b[e['image']])
    print('\n== PR-61, lectures isolées qui nomment >= 4 lettres (seuil de l etape 1)')
    for k in sorted(n):
        print('   %-6s %-7s : %d / %d' % (k[0], k[1], sum(x >= 4 for x in n[k]), len(n[k])))
    print('== PR-61, formes constantes propres à un sens, par panneau et sens (seuil de l etape 2 : >= 3)')
    for z in ('erwin', '0009B', '0800'):
        v = [len(F.formes(F.repete(I, w, o))) for (w, o) in sorted(I) if pan[w]['zone'] == z]
        print('   %-6s : %s' % (z, sorted(v, reverse=True)))
