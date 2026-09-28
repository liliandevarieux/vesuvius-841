# Capacite de PR-55 (format « fenetre » de PR-47, lu avec la consigne « premiere impression »), critere (ii) :
# total des lettres touchees par les 6 lecteurs de R4 moins celui des 6 lecteurs de la base >= 4.
# Modele : pour chaque lettre et chaque carte, probabilite qu un lecteur la touche tiree d une loi beta ajustee sur
# PR-47 (3 lecteurs : R4 touche 9 et 10 trois fois, 8 deux fois, 5 une fois ; la base touche 9 trois fois), puis
# multipliee par r, la perte de precision du format rapide (PR-51 : r entre 0,67 et 0,86 selon la carte).
import numpy as np
rng = np.random.default_rng(55)
R4 = {9: 3, 10: 3, 8: 2, 5: 1}
BASE = {9: 3}
def p_tirees(h, n=3):
    return np.array([rng.beta(h.get(k, 0) + 0.5, n - h.get(k, 0) + 0.5) for k in range(1, 11)])
for r in (1.0, 0.8, 0.67):
    ok, diffs = 0, []
    for _ in range(20000):
        a = np.clip(p_tirees(R4) * r, 0, 1); b = np.clip(p_tirees(BASE) * r, 0, 1)
        d = (rng.random((6, 10)) < a).sum() - (rng.random((6, 10)) < b).sum()
        diffs.append(d); ok += d >= 4
    print('r = %.2f : ecart moyen %.1f lettres touchees, critere (ii) atteint %.0f %% du temps' % (r, np.mean(diffs), 100 * ok / 20000))
# Sous l hypothese nulle (les deux cartes egales, au niveau de la base) :
ok = 0
for _ in range(20000):
    b1 = np.clip(p_tirees(BASE), 0, 1)
    d = (rng.random((6, 10)) < b1).sum() - (rng.random((6, 10)) < b1).sum()
    ok += d >= 4
print('cartes egales (niveau de la base) : critere atteint par hasard %.1f %% du temps' % (100 * ok / 20000))
