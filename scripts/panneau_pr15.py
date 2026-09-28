# PR-15 : le dernier endroit ou chercher sur PHerc. 841 -- les zones de w00 sur sa carte publiee la plus riche.
#
# UNE SEULE CARTE, declaree d avance : w00_canonical_2um_20250807020208.tif, a 69,9 % de remplissage, la ou elle
# retrouve 7 des 7 lettres connues de w00 et montre 8 formes hors zone lue. Les trois autres cartes publiees de
# w00 (1, 2 et 3 formes) ne peuvent pas former de fenetre contenant deux objets : elles sont rapportees par leur
# compte, pas par un panneau.
#
# SEUIL FIXE UNE FOIS sur les lettres CONNUES de w00, jamais par zone. Temoins en nombre egal, tires au hasard,
# meme carte, meme rendu, aucun recouvrement -- verifie sur ce qui part a l ecran.
#
# usage: panneau_pr15.py <aveugle.png> <cle.txt>     GRAINE=
import sys, os, math, numpy as np, tifffile, zarr
from scipy import ndimage
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

H = '/home/slusarska_holding/vesuvius'
out, cle = sys.argv[1], sys.argv[2]
GR = int(os.environ.get('GRAINE', 20260925))
CIBLE = float(os.environ.get('CIBLE', 0.699))
# Parametrable depuis PR-16 : le meme script sert le controle positif sur PHerc. Paris 4 w02, pour qu une
# difference de resultat ne puisse pas venir d une difference de fabrication. Meme format, meme plafond, memes
# lettres de panneau interdites de collision avec les tests precedents.
SRC = os.environ.get('SRC', '%s/ink-dataset/841/w00/preds/w00_canonical_2um_20250807020208.tif' % H)
LABP = os.environ.get('LABP', '%s/ink-dataset/841/w00/w00_inklabels_human7.zarr' % H)
ZF = os.environ.get('ZF', '%s/zones_w00c.txt' % H)
MAXC = int(os.environ.get('MAXC', 99))
LETTRES = os.environ.get('LETTRES', 'IJKLMNOP')
TITRE = os.environ.get('TITRE', 'PHerc. 841, feuillet w00')

L = np.asarray(zarr.open(LABP, mode='r')['3'][:]).squeeze()
if L.ndim == 3:
    L = L.any(axis=0)
L = L > 0
P = tifffile.imread(SRC)
p3 = P[::8, ::8].astype(np.float32)
k = (min(p3.shape[0], L.shape[0]), min(p3.shape[1], L.shape[1]))
p3, Lk = p3[:k[0], :k[1]], L[:k[0], :k[1]]
v = np.unique(np.round(p3[Lk])); s, e = v[0], 1e9
for t in v:
    d = abs(float((p3[Lk] >= t).mean()) - CIBLE)
    if d < e:
        s, e = t, d
print('%s : seuil %.0f -> %.1f %% des lettres connues' % (os.path.basename(SRC)[:40], s, 100 * float((p3[Lk] >= s).mean())))

cand = [tuple(int(x) for x in l.split()[1:5]) for l in open(ZF) if l.startswith('cand')]
tem = [tuple(int(x) for x in l.split()[1:5]) for l in open(ZF) if l.startswith('temoin')]
n = min(len(cand), len(tem), MAXC)
paq = [('cand', z) for z in cand[:n]] + [('temoin', z) for z in tem[:n]]
nc = sum(1 for f, _ in paq if f == 'cand')
if nc * 2 != len(paq):
    raise SystemExit('ARRET : %d candidates pour %d volets -- la parade exige autant de temoins' % (nc, len(paq)))
for x in range(len(paq)):
    for y in range(x + 1, len(paq)):
        (ay0, ay1, ax0, ax1), (by0, by1, bx0, bx1) = paq[x][1], paq[y][1]
        h = max(0, min(ay1, by1) - max(ay0, by0)); w_ = max(0, min(ax1, bx1) - max(ax0, bx0))
        r = 100.0 * h * w_ / ((ay1 - ay0) * (ax1 - ax0))
        if r > 2:
            raise SystemExit('ARRET : %s et %s se recouvrent a %.1f %%' % (paq[x], paq[y], r))
print('%d volets : %d candidates, %d temoins, aucun recouvrement au-dela de 2 pour cent' % (len(paq), nc, len(paq) - nc))

ordre = list(np.random.default_rng(GR).permutation(len(paq)))
noms = LETTRES[:len(paq)]        # des lettres jamais utilisees ailleurs, pour ne pas melanger deux tests
cols = 2
fig, axes = plt.subplots(int(np.ceil(len(paq) / cols)), cols, figsize=(22, 5.6 * np.ceil(len(paq) / cols)))
axes = np.atleast_2d(axes)
rep = []
for n, i in enumerate(ordre):
    fam, (Y0, Y1, X0, X1) = paq[i]
    g = 255 - (P[Y0:Y1, X0:X1] >= s).astype(np.float32) * 255
    g = np.clip(ndimage.rotate(g, 7.0, order=1, reshape=True, cval=255), 0, 255).astype(np.uint8)
    ax = axes[n // cols, n % cols]
    ax.imshow(g, cmap='gray', vmin=0, vmax=255); ax.set_xticks([]); ax.set_yticks([])
    ax.set_title('panneau %s' % noms[n], fontsize=16)
    # LE JETON DE SOURCE SUIT SRC. Il valait 'w00' en dur, et l en-tete de la cle, lui, suivait bien SRC. Quand
    # ce script a servi a PR-16 sur Paris 4 w02, la cle a donc annonce Paris 4 en en-tete et w00 sur ses six
    # lignes de panneaux : une cle qui se contredit sur la seule chose qu elle a a dire. Trouve le 2026-09-25 par
    # un sous-agent a qui on ne demandait que de recompter, pas de verifier. Une constante en dur dans une ligne
    # de rapport ne survit pas a la generalisation du script qui l entoure.
    rep.append('panneau %s = %-8s %-8s  Y %5d-%5d X %5d-%5d' % (noms[n], fam, os.path.basename(SRC)[:8], Y0, Y1, X0, X1))
for n in range(len(paq), axes.size):
    axes[n // cols, n % cols].axis('off')
fig.suptitle(TITRE + ' — %d endroits, le meme rendu, melanges.\n'
             'UNE SEULE QUESTION : voyez-vous des lettres, et ou ? Si oui, sur quel panneau, et montrez ou.\n'
             '« Je ne vois rien » est une reponse complete et utile.\n'
             'AUCUNE de ces zones n est dans le masque de labels.' % len(paq),
             fontsize=16)
fig.tight_layout(rect=[0, 0, 1, 0.955])
fig.savefig(out, dpi=80)
open(cle, 'w').write('CLE — ne pas ouvrir avant la reponse\ngraine %d\ncarte %s\nseuil %.0f\n\n%s\n\n%s\n'
                     % (GR, os.path.basename(SRC), s, '\n'.join(rep),
                        'Au hasard, tomber exactement sur les %d candidates parmi %d a 1 chance sur %d.'
                        % (nc, len(paq), math.comb(len(paq), nc))))
print('ecrit', out, 'et', cle)
