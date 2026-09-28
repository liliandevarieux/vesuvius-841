# Capacite du test de PR-53 (lisibilite selon la duree d entrainement), meme modele que PR-48 et PR-52 :
# difficulte par lettre N(mu, 1,75) sur l echelle logit, 23 lettres, 6 lectures par lettre et par carte (2 par graine),
# test unilateral par inversion de signe sur les lettres, p < 0,05. Difference avec PR-52 : les DEUX bras ont un bruit
# de graine N(0, 0,3), tire independamment (prudent : en vrai, 1000 et 4000 pas d une meme graine sont correles).
# mu est recale pour que le bras 4000 pas ait la precision de R4 dans PR-52 (27 bonnes lectures sur 138).
import numpy as np

rng = np.random.default_rng(53)
SD, SEED_SD, NL, NR = 1.75, 0.3, 23, 6
sig = lambda x: 1 / (1 + np.exp(-x))
precision = lambda mu, n=400000: sig(rng.normal(mu, SD, n)).mean()

lo, hi = -5.0, 1.0
for _ in range(40):
    mid = (lo + hi) / 2
    lo, hi = (mid, hi) if precision(mid) < 27 / 138 else (lo, mid)
mu = (lo + hi) / 2
print('mu recale = %.3f, precision du bras 4000 = %.3f (PR-52 : %.3f)' % (mu, precision(mu), 27 / 138))


def gain_lettres(d, n=400000):
    a = rng.normal(mu, SD, n)
    return NL * (sig(a) - sig(a - d)).mean()


def capacite(d, nsim=3000, nperm=2000):
    ok = 0
    signes = rng.choice([-1.0, 1.0], size=(nperm, NL))
    for _ in range(nsim):
        a = rng.normal(mu, SD, NL)
        s4 = np.repeat(rng.normal(0, SEED_SD, 3), NR // 3)
        s1 = np.repeat(rng.normal(0, SEED_SD, 3), NR // 3)
        p4 = sig(a[:, None] + s4[None, :])
        p1 = sig(a[:, None] - d + s1[None, :])
        dj = (rng.random((NL, NR)) < p4).sum(1) - (rng.random((NL, NR)) < p1).sum(1)
        t = dj.sum()
        p = (1 + ((signes * dj).sum(1) >= t).sum()) / (nperm + 1)
        ok += (p < 0.05) and t > 0
    return ok / nsim


for d in (0.0, 0.35, 0.55, 0.75, 1.0, 1.3):
    print('ecart logit %.2f : 4000 devant de %.1f lettres sur 23 par lecture, detecte %.0f %% du temps'
          % (d, gain_lettres(d), 100 * capacite(d)))
