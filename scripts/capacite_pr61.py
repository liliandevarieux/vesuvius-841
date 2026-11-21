# PR-61 : capacité, calculée AVANT l'inscription, par énumération exacte (aucun tirage au sort).
# 1. Principal : les 3 carrés signalés par PR-60 « se répètent » chacun avec la probabilité rho ; chacune des 2 x NC
#    chances témoins (NC fenêtres témoins, deux sens) se répète à tort avec la probabilité pi. Test exact de Fisher
#    unilatéral (hypergéométrique), seuil 0,05. Puissance = P(p <= 0,05).
# 2. Porte : lettre l d'Erwin lue juste par un lecteur avec la probabilité p_l * L (p_l = lectures justes de Reader V3 sur
#    vignettes, PR-58 + PR-59, sur 8 ; L = perte du format fenêtre) ; forme constante si au moins 4 des 6 lecteurs.
#    Porte tenue si au moins 3 des 12 lettres. Le sens inverse est supposé ne pas reproduire la forme (PR-60 : 0 « oui »
#    sur 144 lectures inverses des carrés d'Erwin avec lettre).
# usage : python capacite_pr61.py
from math import comb

NF, NC = 3, 12
SEUIL = 0.05


def binom(n, k, p):
    return comb(n, k) * p ** k * (1 - p) ** (n - k)


def p_fisher(rf, rc, nf=NF, nch=2 * NC):
    N, K = nf + nch, rf + rc
    return sum(comb(K, x) * comb(N - K, nf - x) for x in range(rf, min(K, nf) + 1)) / comb(N, nf)


def puissance(rho, pi):
    return sum(binom(NF, rf, rho) * binom(2 * NC, rc, pi)
               for rf in range(NF + 1) for rc in range(2 * NC + 1) if p_fisher(rf, rc) <= SEUIL)


print('== PRINCIPAL : %d signalés contre %d chances témoins (%d fenêtres x 2 sens), Fisher unilatéral <= %.2f'
      % (NF, 2 * NC, NC, SEUIL))
print('couples (rf, rc) significatifs :', [(rf, rc) for rf in range(NF + 1) for rc in range(2 * NC + 1)
                                          if p_fisher(rf, rc) <= SEUIL])
PIS = (0.0, 0.05, 0.10, 0.20, 0.30)
print('rho \\ pi  ' + '  '.join('%5.2f' % p for p in PIS))
for rho in (0.5, 0.7, 0.9, 1.0):
    print('  %.1f     ' % rho + '  '.join('%5.2f' % puissance(rho, p) for p in PIS))
print('faux signal (rho = pi) : ' + ', '.join('pi %.2f -> %.3f' % (p, puissance(p, p)) for p in PIS[1:]))

print('\n== PORTE : au moins 3 des 12 lettres d\'Erwin, forme constante = au moins 4 lecteurs sur 6')
JUSTES = {1: 4, 2: 0, 3: 5, 4: 1, 5: 3, 6: 8, 7: 8, 8: 0, 9: 6, 10: 0, 11: 0, 12: 0}   # Reader V3, PR-58 + PR-59, sur 8


def p_porte(L, seuil=3, k=4):
    q = [sum(binom(6, j, min(1.0, n / 8 * L)) for j in range(k, 7)) for n in JUSTES.values()]
    d = [1.0]                                     # loi du nombre de lettres tenues (Poisson-binomiale exacte)
    for x in q:
        d = [a * (1 - x) + (d[i - 1] * x if i else 0) for i, a in enumerate(d + [0.0])]
    return sum(d[seuil:]), sum(i * a for i, a in enumerate(d))


for L in (1.0, 0.8, 0.6, 0.4):
    p, e = p_porte(L)
    print('perte L = %.1f : P(porte tenue) = %.2f ; lettres attendues %.2f' % (L, p, e))
