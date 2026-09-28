# PR-49 : capacite du test et niveau du hasard, calcules le 28/09 a 13:56:48 (heure de Paris), avant l inscription
# de 14:03. Ce code a tourne en ligne de commande, sans fichier ; il est publie tel quel le 28/09 au soir, extrait du
# journal de la seance, apres qu une revérification a trouve que le registre ne citait aucun script pour ce tableau.
# Seules ces lignes de tete sont ajoutees. Sortie : hasard pour 4, 6, 8 et 12 lettres nommees, puis capacite pour
# quatre ecarts entre bras (6 lecteurs par bras, test de permutation exact unilateral, 400 tirages).
import numpy as np, itertools
rng = np.random.default_rng(49)
REF = ['pi', 'epsilon', 'rho', 'iota', 'epsilon', 'pi', 'iota', 'lambda', 'epsilon', 'gamma', 'epsilon', 'iota']
ALPH = ('alpha beta gamma delta epsilon zeta eta theta iota kappa lambda mu nu xi omicron pi rho sigma tau upsilon '
        'phi chi psi omega').split()
def lcs(a, b):
    t = np.zeros((len(a) + 1, len(b) + 1), int)
    for i in range(len(a)):
        for j in range(len(b)):
            t[i + 1, j + 1] = t[i, j] + 1 if a[i] == b[j] else max(t[i, j + 1], t[i + 1, j])
    return t[-1, -1]
# hasard : un lecteur nomme k lettres au hasard (uniforme sur 24), dans un ordre quelconque
for k in (4, 6, 8, 12):
    v = [lcs(list(rng.choice(ALPH, k)), REF) for _ in range(4000)]
    print('hasard, %2d lettres nommees : LCS moyen %.2f, 95e centile %d' % (k, np.mean(v), np.percentile(v, 95)))
# capacite : chaque lettre de la reference est trouvee et bien nommee avec la probabilite q (dans l ordre),
# plus 3 lettres parasites au hasard inserees ; 6 lecteurs par bras ; test de permutation exact unilateral
def lecteur(q):
    t = [x for x in REF if rng.random() < q]
    for _ in range(3):
        t.insert(rng.integers(0, len(t) + 1), rng.choice(ALPH))
    return lcs(t, REF)
combs = list(itertools.combinations(range(12), 6))
def puissance(qP, qT, n=400):
    ok = 0
    for _ in range(n):
        a = np.array([lecteur(qP) for _ in range(6)]); b = np.array([lecteur(qT) for _ in range(6)])
        x = np.concatenate([a, b]); obs = a.mean() - b.mean()
        null = [x[list(c)].mean() - np.delete(x, c).mean() for c in combs]
        ok += (np.mean(np.array(null) >= obs - 1e-9) < 0.05)
    return ok / n
for qT, qP in ((0.1, 0.3), (0.1, 0.4), (0.1, 0.5), (0.2, 0.5)):
    print('lettres trouvees : T %.0f %%, P %.0f %%  (ecart attendu %.1f lettres) -> puissance %.0f %%'
          % (qT * 100, qP * 100, 12 * (qP - qT), 100 * puissance(qP, qT)))
