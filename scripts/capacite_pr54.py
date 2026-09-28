# Capacite du test de PR-54 (Reader v2 avec moyenne miroir contre Reader v2 seul), meme modele que PR-52 et PR-53 :
# difficulte par lettre N(mu, 1,75) sur l echelle logit, 23 lettres, 6 lectures par lettre et par carte (2 par graine),
# test unilateral par inversion de signe sur les lettres, p < 0,05. Difference avec PR-52 : les DEUX bras ont un bruit
# de graine nul : chaque bras est une seule carte (le modele publie), lue 6 fois par lettre.
# mu est recale pour que Reader v2 seul ait sa precision de PR-52 (38 bonnes lectures sur 138).
import numpy as np

rng = np.random.default_rng(54)
SD, SEED_SD, NL, NR = 1.75, 0.0, 23, 6
sig = lambda x: 1 / (1 + np.exp(-x))
precision = lambda mu, n=400000: sig(rng.normal(mu, SD, n)).mean()

lo, hi = -5.0, 1.0
for _ in range(40):
    mid = (lo + hi) / 2
    lo, hi = (mid, hi) if precision(mid) < 38 / 138 else (lo, mid)
mu = (lo + hi) / 2
print('mu recale = %.3f, precision du Reader v2 seul = %.3f (PR-52 : %.3f)' % (mu, precision(mu), 38 / 138))


def gain_lettres(d, n=400000):
    a = rng.normal(mu, SD, n)
    return NL * (sig(a + d) - sig(a)).mean()


def capacite(d, nsim=3000, nperm=2000):
    ok = 0
    signes = rng.choice([-1.0, 1.0], size=(nperm, NL))
    for _ in range(nsim):
        a = rng.normal(mu, SD, NL)
        s4 = np.repeat(rng.normal(0, SEED_SD, 3), NR // 3)
        s1 = np.repeat(rng.normal(0, SEED_SD, 3), NR // 3)
        p4 = sig(a[:, None] + d + s4[None, :])                          # bras miroir
        p1 = sig(a[:, None] + s1[None, :])                              # Reader v2 seul, cale
        dj = (rng.random((NL, NR)) < p4).sum(1) - (rng.random((NL, NR)) < p1).sum(1)
        t = dj.sum()
        p = (1 + ((signes * dj).sum(1) >= t).sum()) / (nperm + 1)
        ok += (p < 0.05) and t > 0
    return ok / nsim


for d in (0.0, 0.35, 0.55, 0.75, 1.0, 1.3):
    print('ecart logit %.2f : miroir devant de %.1f lettres sur 23 par lecture, detecte %.0f %% du temps'
          % (d, gain_lettres(d), 100 * capacite(d)))
