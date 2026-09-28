# PR-18 : l allongement, septieme candidat a une mesure de lisibilite.
#
# allongement = aire / r2, ou r est le rayon du plus grand disque inscrit dans la composante (max de la transformee
# de distance). Sans echelle : un disque donne pi = 3,14 quelle que soit sa taille, un trait de largeur t et de
# longueur L donne 4L/t, soit quatre fois son rapport d aspect. Une lettre est faite de traits, une tache est un
# disque.
#
# CE QUI EST MESURE, dans l ordre du pre-enregistrement :
#   PRIMAIRE  - les 10 panneaux de Paris 4 w02 qui ont un verdict de lecteur (4 lus, 6 non lus). C est le seul test
#               qui peut echouer : meme feuillet, meme carte, meme seuil, seul le verdict change.
#   SECONDAIRE- les 4 panneaux de 841 w00 contre les 10 de Paris 4. Attendu d apres les figures, donc sans valeur
#               probante seul ; enregistre pour qu un echec soit visible.
#   TROISIEME - les lettres CONNUES seules, encre contre encre, sans dependance au lecteur ni au tirage des zones.
#
# Travail a la demi-resolution (::2) : les traits font plus de 100 px de large a pleine resolution, donc rien n est
# rompu, et l allongement est sans echelle de toute facon. Aire minimale 50 px dans cette grille = 200 px pleins.
import os, json, numpy as np, tifffile, zarr
from scipy import ndimage, stats

H = '/home/slusarska_holding/vesuvius'
PAS, AIRE_MIN, SEUIL_ALLONGE = 2, 50, 12.0

JEUX = {
 'w00': dict(src='%s/ink-dataset/841/w00/preds/w00_canonical_2um_20250807020208.tif' % H,
             lab='%s/ink-dataset/841/w00/w00_inklabels_human7.zarr' % H, seuil=104.0, nom='PHerc. 841 w00',
             pan={'A': (640, 8176, 8350, 16678), 'B': (7578, 15114, 153, 8481),
                  'C': (8218, 15754, 9992, 18320), 'D': (19, 7555, 107, 8435)},
             lus=set()),
 'p4': dict(src='%s/ink-dataset/phercparis4/w02_20231031143852/preds/'
                'tile256_stride128_layers1_63_hann_fwd.tif' % H,
            lab='%s/ink-dataset/phercparis4/w02_20231031143852/w02_20231031143852_inklabels.zarr' % H,
            seuil=227.0, nom='PHerc. Paris 4 w02',
            pan={'Q': (9280, 11792, 17672, 23224), 'R': (15236, 17748, 16299, 21851),
                 'S': (11282, 13794, 419, 5971), 'T': (5733, 8245, 17458, 23010),
                 'U': (6544, 9056, 24584, 30136), 'V': (104, 2616, 17144, 22696),
                 'J': (22451, 29987, 29901, 38229), 'K': (2062, 9598, 28285, 36613),
                 'L': (13587, 21123, 34686, 43014), 'M': (4849, 12385, 10510, 18838)},
            lus={'R', 'V', 'J', 'M'}),
}


def allongement(b):
    """(mediane ponderee par l aire, part de l aire en composantes allongees, nombre de composantes) sur un binaire."""
    lab, n = ndimage.label(b)
    if n == 0:
        return float('nan'), float('nan'), 0
    aires = np.bincount(lab.ravel())
    d = ndimage.distance_transform_edt(b)
    rmax = ndimage.maximum(d, lab, range(1, n + 1))
    a = aires[1:]
    garde = a >= AIRE_MIN
    if not garde.any():
        return float('nan'), float('nan'), 0
    a, r = a[garde].astype(float), np.asarray(rmax)[garde]
    e = a / np.maximum(r, 1.0) ** 2
    o = np.argsort(e)
    cum = np.cumsum(a[o])
    med = float(e[o][np.searchsorted(cum, cum[-1] / 2.0)])
    return med, float(a[e >= SEUIL_ALLONGE].sum() / a.sum()), int(garde.sum())


res = {}
for cle, J in JEUX.items():
    P = tifffile.imread(J['src'])
    print('%s : carte %s, seuil %.0f' % (J['nom'], P.shape, J['seuil']))
    res[cle] = {'panneaux': {}, 'lettres': []}
    for nom, (y0, y1, x0, x1) in J['pan'].items():
        med, part, nc = allongement(P[y0:y1:PAS, x0:x1:PAS] >= J['seuil'])
        res[cle]['panneaux'][nom] = dict(med=med, part=part, ncomp=nc, lu=nom in J['lus'])
        print('  panneau %s  %-6s allongement median %6.2f   part allongee %5.1f %%   %4d composantes'
              % (nom, 'LU' if nom in J['lus'] else 'non lu', med, 100 * part, nc))
    L = np.asarray(zarr.open(J['lab'], mode='r')['3'][:]).squeeze()
    if L.ndim == 3:
        L = L.any(axis=0)
    lab3, n3 = ndimage.label(L > 0)
    for i, s in enumerate(ndimage.find_objects(lab3)):
        cote = max(s[0].stop - s[0].start, s[1].stop - s[1].start) * 8
        if not (900 <= cote <= 3000):
            continue
        b = P[s[0].start * 8:s[0].stop * 8:PAS, s[1].start * 8:s[1].stop * 8:PAS] >= J['seuil']
        med, part, nc = allongement(b)
        if nc:
            res[cle]['lettres'].append(dict(no=i + 1, cote=int(cote), med=med, part=part, ncomp=nc))
    v = [x['med'] for x in res[cle]['lettres']]
    print('  %d lettres connues : allongement median %.2f (min %.2f, max %.2f)'
          % (len(v), float(np.median(v)), min(v), max(v)))

# --- PRIMAIRE : dans le rouleau temoin, lus contre non lus
p4 = res['p4']['panneaux']
lus = [p4[k]['med'] for k in p4 if p4[k]['lu']]
non = [p4[k]['med'] for k in p4 if not p4[k]['lu']]
u, p = stats.mannwhitneyu(lus, non, alternative='greater')
print()
print('PRIMAIRE  Paris 4, %d lus %s contre %d non lus %s' % (len(lus), np.round(lus, 2), len(non), np.round(non, 2)))
print('          Mann-Whitney unilateral (lus > non lus) : U = %.1f, p = %.4f' % (u, p))
# --- SECONDAIRE : 841 contre Paris 4, par panneau
w = [res['w00']['panneaux'][k]['med'] for k in res['w00']['panneaux']]
a = [p4[k]['med'] for k in p4]
u2, p2 = stats.mannwhitneyu(w, a, alternative='less')
print('SECONDAIRE 841 %s contre Paris 4 %s : U = %.1f, p = %.4f' % (np.round(w, 2), np.round(a, 2), u2, p2))
# --- TROISIEME : les lettres connues, encre contre encre
lw = [x['med'] for x in res['w00']['lettres']]
lp = [x['med'] for x in res['p4']['lettres']]
u3, p3 = stats.mannwhitneyu(lw, lp, alternative='less')
print('TROISIEME  lettres connues : 841 mediane %.2f (n=%d) contre Paris 4 %.2f (n=%d) : U = %.1f, p = %.4f'
      % (float(np.median(lw)), len(lw), float(np.median(lp)), len(lp), u3, p3))
res['tests'] = dict(primaire=dict(U=float(u), p=float(p), lus=lus, non_lus=non),
                    secondaire=dict(U=float(u2), p=float(p2)),
                    troisieme=dict(U=float(u3), p=float(p3),
                                   med_841=float(np.median(lw)), med_p4=float(np.median(lp))))
if os.environ.get('JSON'):
    json.dump(res, open(os.environ['JSON'], 'w'), indent=1)
    print('ecrit', os.environ['JSON'])
