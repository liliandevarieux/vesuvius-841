# Les quatre professeurs, en aveugle, pour l oeil de Lilian -- PR-8.
#
# POURQUOI. Le professeur est le plus gros levier mesure du projet : 25 points d ecart entre le meilleur et le pire
# des quatre, contre 4 a 5 pour le tableau et 3 pour la recette de labels. Et la regle qui sert a le choisir
# (pick_teacher.py, IoU contre les labels humains) vient d etre prise en defaut par PR-7 : le professeur classe
# 3e sur 4 par l IoU donne le meilleur modele. Nous n avons donc AUCUN instrument pour choisir un professeur.
#
# L oeil de Lilian, lui, a marche : le 24/09 en aveugle, il a vu 3 fois sur 3 l ecart de 16 points entre deux
# modeles, et 1 fois sur 2 l ecart de 4 a 5. L ecart entre professeurs est de 25 points. La question est donc
# legitime : est-ce que son oeil, pose sur le PROFESSEUR et pas sur le modele, ordonne ce que l IoU n ordonne pas ?
#
# CE QU IL VOIT, ET CE QU IL NE VOIT PAS.
#  - pas de labels humains a cote. Montrer les labels ferait juger « accord avec les labels », c est-a-dire
#    exactement la regle qui a echoue. La question est « est-ce que ca ressemble a de l encre », pas « est-ce que
#    ca ressemble aux labels ».
#  - pas de noms, pas de chiffres, ordre melange a graine verifiee non monotone (lecon de quatre_bras.py, ou la
#    graine 2609 affichait les bras dans l ordre exact du meilleur au pire et rendait le test sans valeur).
#  - gris brut, vmin=0 vmax=255, sans egalisation. C est fidele : les trois bras mesures ont ete fabriques avec
#    des SEUILS ABSOLUS (encre >= 190, fond <= 131), donc la luminosite du professeur compte vraiment. Un
#    professeur plus sombre fait moins d encre, et c est un vrai defaut, pas un artefact d affichage.
#
# CE QUE CA NE PROUVERA PAS. Quatre professeurs, un observateur, un segment. Un succes ne fait pas un instrument :
# il rend un cinquieme professeur interessant a mesurer. Un echec tue l idee pour le prix d une image.
#
# usage: professeurs_aveugle.py <sortie.png>     GRAINE=<n> pour changer le melange
import sys, os, json, random, numpy as np, tifffile
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

H = '/home/slusarska_holding/vesuvius'
PRE = '%s/ink-dataset/841/w00/preds' % H
out = sys.argv[1]
# CROP : pixels pleine resolution. Premiere version a 1200, soit 5,6 mm a 4,681 um -- j avais estime « une
# vingtaine de lettres » de tete, et l image rendue en montrait UNE. Les lettres de ce rouleau font ~1 800 px (mediane mesuree le 24/09 ; le chiffre qui suivait, 500 a 800,
# pixels, soit 2 a 4 mm. 5000 px = 23 mm, une ligne de texte : c est la bonne echelle pour juger une FORME.
CROP = int(os.environ.get('CROP', 5000))
NZ = 3               # zones

# (fichier, nom court). Le nom court ne sort que dans la cle json, jamais sur l image.
PROFS = [('ps48_640_640_smooth_0.1_w00_ckpt_130000_forward_210326.tif', 'ps48_forward'),
         ('new_canon_20260417_recale.tif',                              'new_canon_recale'),
         ('w00_canonical_030726_reverse_070326.tif',                    'canonical_reverse'),
         ('w00_canonical_2um_20250807020208.tif',                       'canonical_2um')]

# Valeurs en aval DEJA mesurees (ecart encre/fond sur segB, couches inversees). Elles servent uniquement a
# verifier que la graine ne range pas les professeurs dans l ordre du resultat ; elles ne sont pas affichees.
# canonical_2um n a pas encore de valeur : c est la moitie prospective du test.
AVAL = {'ps48_forward': 59.8, 'new_canon_recale': 75.9, 'canonical_reverse': 84.4, 'canonical_2um': None}


def zones():
    """Trois zones riches en encre humaine, bien separees, choisies sur les labels et pas a la main."""
    import zarr
    p = '%s/ink-dataset/841/w00/w00_inklabels_human7.zarr' % H
    if not os.path.exists(p):
        raise SystemExit('labels humains introuvables : les zones ne peuvent pas etre choisies sur une mesure')
    d = np.asarray(zarr.open(p, mode='r')['3'][:])
    d = d.squeeze() > 0
    # les labels de w00 sont un VOLUME de 65 couches : l encre est marquee a la profondeur ou elle est vue.
    # Pour choisir une zone, ce qui compte est son empreinte au sol, donc l union sur z.
    if d.ndim == 3:
        d = d.any(axis=0)
    if d.ndim != 2:
        raise SystemExit('labels de forme %s : je ne sais pas les lire, je ne devine pas' % (d.shape,))
    d = d.astype(np.float32)
    print('labels au 1/8 : %s, %.2f %% d encre' % (d.shape, 100 * d.mean()), flush=True)
    k = CROP // 8
    # densite integrale par fenetre, pas de boucle sur toutes les positions
    c = np.cumsum(np.cumsum(d, 0), 1)
    c = np.pad(c, ((1, 0), (1, 0)))
    S = c[k:, k:] - c[:-k, k:] - c[k:, :-k] + c[:-k, :-k]
    pris = []
    S2 = S.copy()
    for _ in range(NZ):
        i, j = np.unravel_index(int(np.argmax(S2)), S2.shape)
        # A CROP=5000 la carte au 1/8 ne fait que 1984 x 2368 : une exclusion de +/- 2k effacait tout le plan et
        # argmax renvoyait (0,0), un coin vide, sans rien signaler. Exclusion a +/- k (les zones ne se recouvrent
        # pas) et garde explicite sur le maximum.
        if S2[i, j] <= 0:
            raise SystemExit('plus de zone disponible apres %d : reduire CROP ou NZ' % len(pris))
        pris.append((int(i) * 8, int(j) * 8))
        i0, i1 = max(0, i - k), i + k
        j0, j1 = max(0, j - k), j + k
        S2[i0:i1, j0:j1] = -1          # interdit le recouvrement : trois zones, pas trois fois la meme
    return pris


def monotone(ordre):
    """Vrai si les professeurs DEJA mesures apparaissent dans l ordre du resultat (croissant ou decroissant)."""
    v = [AVAL[n] for _, n in ordre if AVAL[n] is not None]
    return v == sorted(v) or v == sorted(v, reverse=True)


g = int(os.environ.get('GRAINE', 7))
ordre = list(PROFS)
while True:
    random.Random(g).shuffle(ordre)
    if not monotone(ordre):
        break
    g += 1                              # verifie AVANT usage, pas apres
print('graine %d retenue (ordre affiche non monotone en aval)' % g)

Z = zones()
print('zones (pleine resolution, coin haut-gauche) : %s' % Z)

fig, axes = plt.subplots(NZ, len(ordre), figsize=(6.0 * len(ordre), 6.0 * NZ))
for col, (f, nom) in enumerate(ordre):
    a = tifffile.imread('%s/%s' % (PRE, f))      # un professeur a la fois : ~300 Mo en memoire, pas 1,2 Go
    for r, (Y0, X0) in enumerate(Z):
        y = min(Y0, a.shape[0] - CROP); x = min(X0, a.shape[1] - CROP)
        ax = axes[r, col]
        ax.imshow(a[y:y + CROP, x:x + CROP], cmap='gray', vmin=0, vmax=255)
        ax.set_xticks([]); ax.set_yticks([])
        if r == 0:
            ax.set_title('professeur %s' % chr(65 + col), fontsize=20)
        if col == 0:
            ax.set_ylabel('zone %d' % (r + 1), fontsize=16)
    del a

fig.suptitle('Quatre professeurs, EN AVEUGLE — meme zone sur chaque ligne, meme echelle.\n'
             'Classe-les du MEILLEUR au PIRE : « meilleur » = ce qui ressemble le plus a de l encre '
             '(traits, formes de lettres, bords nets) ; « pire » = des taches sans forme.\n'
             'Une reponse par zone, trois reponses en tout. Si les trois different, c est une information aussi.',
             fontsize=17)
fig.tight_layout(rect=[0, 0, 1, 0.94])
fig.savefig(out, dpi=100)
print('ecrit', out)

cle = '%s/results/aveugle_professeurs.json' % H
json.dump({'graine': g, 'affiche': [chr(65 + i) for i in range(len(ordre))],
           'professeur': [n for _, n in ordre], 'aval_segB': [AVAL[n] for _, n in ordre],
           'zones_pleine_res': Z, 'crop': CROP},
          open(cle, 'w'), indent=1)
print('   cle dans %s -- a ne pas ouvrir avant d avoir repondu' % cle)
