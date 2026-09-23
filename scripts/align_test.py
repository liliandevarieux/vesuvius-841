# Des taches de taille de lettre alignees sur une droite : est-ce rare ? C est l instrument de PR-3.
#
# On cherche la droite d angle donne (celui des lignes de texte, mesure independamment) qui capte le plus de taches a
# moins de TOL pixels. Puis on refait le meme calcul 2000 fois en cassant le lien entre les coordonnees Y et X de
# chaque tache -- ce qui detruit tout alignement reel tout en gardant les deux distributions et la densite de points.
# La proportion de tirages qui font aussi bien que l observation est la valeur p.
#
# Le seuil d aire est un ARGUMENT et non une valeur trouvee a l usage : sur segB, p vaut 0,354 sur les 117 candidates
# et 0,018 sur les 13 de taille de lettre, et ce second seuil avait ete choisi apres avoir vu les donnees. PR-3 le
# fige a 0,3 Mpx pour le segment suivant, ou il devient une prediction.
#
# usage: align_test.py <fichier_candidates> <angle_deg> [aire_min_Mpx=0] [tol_px=150] [tirages=2000]
#        le fichier a une ligne par tache : Y X aire_px
import sys
import numpy as np

f = sys.argv[1]
ANGLE = float(sys.argv[2])
AMIN = float(sys.argv[3]) * 1e6 if len(sys.argv) > 3 else 0.0
TOL = float(sys.argv[4]) if len(sys.argv) > 4 else 150.0
N = int(sys.argv[5]) if len(sys.argv) > 5 else 2000

c = [tuple(map(float, l.split())) for l in open(f) if l.strip()]
Y = np.array([r[0] for r in c]); X = np.array([r[1] for r in c]); A = np.array([r[2] for r in c])
m = A >= AMIN
Y, X = Y[m], X[m]
PENTE = np.tan(np.radians(ANGLE))


def meilleur(y, x):
    """Le plus grand nombre de taches a moins de TOL d une meme droite de pente fixee.

    L optimum est atteint sur une droite passant par l une des taches, il suffit donc de les essayer toutes."""
    if len(y) < 2:
        return 0
    off = y - PENTE * x
    return int(max((np.abs(off - o) < TOL).sum() for o in off))


obs = meilleur(Y, X)
rng = np.random.default_rng(0)
nul = np.array([meilleur(rng.permutation(Y), X) for _ in range(N)])
p = float((nul >= obs).mean())

print(f'{f}')
print(f'  {len(Y)} taches retenues sur {len(c)} (aire >= {AMIN/1e6:.2f} Mpx), droite a {ANGLE:.1f} deg, '
      f'tolerance {TOL:.0f} px')
print(f'  alignement observe : {obs} taches')
print(f'  hasard ({N} tirages) : mediane {np.median(nul):.0f}, 95e centile {np.percentile(nul, 95):.0f}, '
      f'maximum {nul.max()}')
print(f'  p = {p:.3f}')
print(f'  => {"alignement plus fort que le hasard" if p < 0.05 else "indistinguable du hasard"} au seuil de 5 %')
