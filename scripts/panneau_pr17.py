# PR-17 : les memes cartes, des fenetres assez hautes pour contenir plusieurs lignes.
#
# DEUX CORRECTIONS AU DESIGN, faites avant qu un lecteur ait rien vu :
#
# 1. PAS DE CANDIDATES NI DE TEMOINS. PR-16 a tue le critere de forme (une candidate lue sur trois, un temoin lu
#    sur trois). Garder la distinction ferait croire qu on teste encore quelque chose avec elle. Les zones sont
#    donc TIREES AU HASARD, et la seule question est : combien de fenetres se lisent sur chaque feuillet.
#
# 2. FENETRES DISJOINTES. Reprendre les memes centres qu en PR-15/PR-16 en agrandissant produisait des
#    recouvrements de 74 et 78 % : six volets montrant en grande partie la meme chose ne sont pas six
#    echantillons, et un lecteur qui lit l un « lit » ses voisins. Les zones sont retirees au hasard avec un test
#    de recouvrement, comme pour les temoins de PR-14 apres la meme faute.
#
# TAILLE : 7536 x 8328 px, soit ~4,2 hauteurs de lettre sur ~4,7 largeurs -- trois a quatre lignes d ecriture au
# lieu d une seule. Plus grand ne tient pas : w00 ne fait que 15827 px de haut, donc une fenetre de 10048 en
# couvrirait deja les deux tiers et il serait impossible d en poser quatre sans recouvrement.
#
# usage: panneau_pr17.py <aveugle.png> <cle.txt>   JEU=w00|p4  GRAINE=  N=4
import sys, os, numpy as np, tifffile, zarr
from scipy import ndimage
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

H = '/home/slusarska_holding/vesuvius'
out, cle = sys.argv[1], sys.argv[2]
JEU = os.environ.get('JEU', 'w00')
GR = int(os.environ.get('GRAINE', 20260926))
N = int(os.environ.get('N', 4))
HT, LG = 7536, 8328

JEUX = {
 'w00': ('%s/ink-dataset/841/w00/preds/w00_canonical_2um_20250807020208.tif' % H, 104.0,
         '%s/ink-dataset/841/w00/w00_inklabels_human7.zarr' % H, 'Feuillet A', 'ABCDEFGH'),
 'p4': ('%s/ink-dataset/phercparis4/w02_20231031143852/preds/tile256_stride128_layers1_63_hann_fwd.tif' % H, 227.0,
        '%s/ink-dataset/phercparis4/w02_20231031143852/w02_20231031143852_inklabels.zarr' % H,
        'Feuillet B', 'JKLMNPQR'),
}
SRC, SEUIL, LABP, TITRE, LETTRES = JEUX[JEU]
L = np.asarray(zarr.open(LABP, mode='r')['3'][:]).squeeze()
if L.ndim == 3:
    L = L.any(axis=0)
hors = ~ndimage.binary_dilation(L > 0, iterations=40)
P = tifffile.imread(SRC)
print('%s : %s  seuil %.0f  feuille %s  fenetre %d x %d' % (TITRE, os.path.basename(SRC)[:34], SEUIL, P.shape, HT, LG))

rng = np.random.default_rng(GR)
zones, essais = [], 0
while len(zones) < N and essais < 300000:
    essais += 1
    y = int(rng.integers(0, max(1, P.shape[0] - HT))); x = int(rng.integers(0, max(1, P.shape[1] - LG)))
    i, j = (y + HT // 2) // 8, (x + LG // 2) // 8
    if not (i < hors.shape[0] and j < hors.shape[1] and hors[i, j]):
        continue                       # centre hors du voisinage des labels
    z = (y, y + HT, x, x + LG)
    if any(max(0, min(z[1], b[1]) - max(z[0], b[0])) * max(0, min(z[3], b[3]) - max(z[2], b[2])) > 0.02 * HT * LG
           for b in zones):
        continue                       # aucun recouvrement au-dela de 2 %
    # LA FENETRE DOIT TOMBER SUR LE PAPYRUS. Une carte de prediction vaut 0 hors de la feuille deroulee : un
    # tirage uniforme sur le tableau attrape donc du vide et des bords. Le premier essai a produit un panneau
    # aux trois quarts blanc avec un artefact de bord en diagonale -- un volet qui ne montre pas de papyrus ne
    # peut ni confirmer ni infirmer quoi que ce soit, et il dilue le compte.
    if float((P[y:y + HT:16, x:x + LG:16] > 0).mean()) < 0.85:
        continue
    zones.append(z)
if len(zones) < N:
    raise SystemExit('ARRET : %d fenetres disjointes seulement sur %d demandees en %d tirages -- la feuille est '
                     'trop petite pour cette taille de fenetre.' % (len(zones), N, essais))
print('%d fenetres disjointes tirees au hasard, hors voisinage des labels' % len(zones))

cols = 2
fig, axes = plt.subplots(int(np.ceil(N / cols)), cols, figsize=(22, 10.0 * np.ceil(N / cols)))
axes = np.atleast_2d(axes)
rep = []
for n, (y0, y1, x0, x1) in enumerate(zones):
    g = 255 - (P[y0:y1, x0:x1] >= SEUIL).astype(np.float32) * 255
    g = np.clip(ndimage.rotate(g, 7.0, order=1, reshape=True, cval=255), 0, 255).astype(np.uint8)
    ax = axes[n // cols, n % cols]
    ax.imshow(g[::2, ::2], cmap='gray', vmin=0, vmax=255); ax.set_xticks([]); ax.set_yticks([])
    ax.set_title('panneau %s' % LETTRES[n], fontsize=17)
    rep.append('panneau %s = Y %5d-%5d X %5d-%5d' % (LETTRES[n], y0, y1, x0, x1))
for n in range(N, axes.size):
    axes[n // cols, n % cols].axis('off')
fig.suptitle('%s — %d endroits tires au hasard, le meme rendu.\n'
             'UNE SEULE QUESTION : voyez-vous des lettres, et ou ? Si oui, sur quel panneau, et montrez ou.\n'
             '« Je ne vois rien » est une reponse complete et utile.\n'
             'Ces fenetres sont TROIS FOIS plus hautes que celles d hier : trois a quatre lignes d ecriture\n'
             'peuvent y tenir au lieu d une seule. Cherchez des SUITES de formes alignees, pas des taches isolees.'
             % (TITRE, N), fontsize=16)
fig.tight_layout(rect=[0, 0, 1, 0.95])
fig.savefig(out, dpi=70)
open(cle, 'w').write('CLE PR-17 %s\ngraine %d\ncarte %s\nseuil %.0f\nfenetre %d x %d\n\n%s\n\n%s\n'
                     % (TITRE, GR, os.path.basename(SRC), SEUIL, HT, LG, '\n'.join(rep),
                        'Zones tirees au hasard : il n y a ni candidates ni temoins. La seule lecture du resultat '
                        'est le NOMBRE de fenetres lues, compare entre les deux feuillets.'))
print('ecrit', out, 'et', cle)
