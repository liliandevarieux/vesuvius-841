# PR-60 : capacité du test, calculée avant l'inscription (règle 2 de notes/14-methode.md).
# Plan : 8 conditions (4 cartes x 2 sens), carré latin, 6 lecteurs par carré et par condition ; par carré, toutes cartes
# réunies : Yf = oui sur 24 lectures dans le sens direct, Yr = oui sur 24 lectures dans le sens inverse.
# Test par carré (mesure principale) : les taux de fond bf et br sont estimés sur l'ensemble des carrés de 0800 (un biais
# de sens réparti partout est ainsi absorbé) ; p_t = P(Bin(24,bf) - Bin(24,br) >= d_t), exact ; correction de Holm sur
# les carrés ; un carré est « retenu » si sa p corrigée <= 0,05.
# Hypothèses : carré sans écriture P(oui) = b dans les deux sens (+ artefact a dans le sens direct, partout) ; carré avec
# écriture P(oui) = qf dans le sens direct, b dans le sens inverse.
# Une version précédente (somme des écarts sur tous les carrés, inversion des signes) a été écartée avant l'inscription :
# trop faible (~10 carrés sur 40 pour 80 %) et sensible à un biais de sens (26 à 44 % de faux signal pour +0,05).
# usage : capacite_pr60.py N_0800
import sys, numpy as np
from scipy.stats import binom

L = 24
rng = np.random.default_rng(60)


def p_diff(d, bf, br):
    """P(Bin(L,bf) - Bin(L,br) >= d), exacte."""
    pf = binom.pmf(np.arange(L + 1), L, bf); pr = binom.pmf(np.arange(L + 1), L, br)
    dist = np.convolve(pf, pr[::-1])                       # indice i <-> différence i - L
    return dist[max(0, d + L):].sum()


def holm(p):
    o = np.argsort(p); m = len(p); adj = np.empty(m); run = 0
    for i, k in enumerate(o):
        run = max(run, min(1, (m - i) * p[k])); adj[k] = run
    return adj


def retenus(Yf, Yr):
    bf = Yf.sum() / (L * len(Yf)); br = Yr.sum() / (L * len(Yr))
    p = np.array([p_diff(int(f - r), bf, br) for f, r in zip(Yf, Yr)])
    return holm(p) <= 0.05


def simule(N, k, b, qf, a=0.0, sims=2000):
    au_moins_un = vrais = faux = 0
    for _ in range(sims):
        pf = np.full(N, min(1, b + a)); pf[:k] = qf
        R = retenus(rng.binomial(L, pf), rng.binomial(L, b, N))
        au_moins_un += R[:k].any() if k else 0; vrais += R[:k].sum(); faux += R[k:].any()
    return au_moins_un / sims, (vrais / (sims * k) if k else 0), faux / sims


N0 = int(sys.argv[1]) if len(sys.argv) > 1 else 40
print('%d carres de 0800 ; par carre 24 lectures sens direct contre 24 sens inverse ; Holm sur les carres' % N0)
for b, qf in ((0.1, 0.3), (0.1, 0.5), (0.25, 0.5), (0.25, 0.7), (0.4, 0.7), (0.4, 0.9)):
    cel = []
    for k in (1, 2, 3, 5):
        u, v, f = simule(N0, k, b, qf)
        cel.append('k=%d : >=1 retenu %3.0f%% (par carre %3.0f%%)' % (k, 100 * u, 100 * v))
    print('b=%.2f qf=%.2f | %s' % (b, qf, ' | '.join(cel)))
print()
for b in (0.1, 0.25, 0.4):
    for a in (0.0, 0.05, 0.10):
        print('sans ecriture b=%.2f, biais de sens +%.2f partout : au moins un carre retenu %.1f%%'
              % (b, a, 100 * simule(N0, 0, b, b, a=a)[2]))
