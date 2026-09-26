# PR-24 : le scanner brut de segB, en carreaux melanges a l aveugle.
# Trois familles, meme rendu : 5 lettres etiquetees (controle positif), 5 carreaux de papyrus loin de toute
# etiquette et de toute tache candidate (controle negatif), et les taches de priorite A d ibara sur segB
# (github.com/ibarapascal/ink-disagree, liste du 23/09) dont le carreau ne touche aucune etiquette.
# Rendu : carreau 2048 px pleine resolution centre sur l objet, reduit x2 ; 8 tranches = moyenne de 8 couches
# (couches 22-85, centre du volume 109) ; contraste 1-99 % sur le papyrus du carreau.
# Sorties : panneaux PNG a numero aleatoire + pile Fiji (moyenne de 4 couches) ; la CLE reste dans WSL.
# usage : pr24_panneaux.py CSV_IBARA
import sys, os, csv, json, numpy as np, zarr, tifffile
from scipy import ndimage
from PIL import Image

H = '/home/slusarska_holding/vesuvius'
VOL = '%s/ink-dataset/841/segB/segB.zarr' % H
LAB = '%s/ink-dataset/841/canon_autres/auto_grown_20260220174252405/inklabels.zarr' % H
PRED = '%s/ink-dataset/841/canon_autres/auto_grown_20260220174252405/pred.tif' % H
SEG_IBARA = '20260221022814'
OUT = '%s/pr24' % H
COTE, Z0, NT, EP = 2048, 22, 8, 8
N_NEG, GRAINE = 5, 24

os.makedirs(OUT + '/panneaux', exist_ok=True)
os.makedirs(OUT + '/piles', exist_ok=True)
vol = zarr.open(VOL, mode='r')['0']
NZ, NY, NX = vol.shape
L3 = np.asarray(zarr.open(LAB, mode='r')['3'][:]) > 0
lab3, n3 = ndimage.label(L3)


def fenetre(cy, cx):
    y0 = int(min(max(cy - COTE // 2, 0), NY - COTE))
    x0 = int(min(max(cx - COTE // 2, 0), NX - COTE))
    return y0, x0


def touche_etiquette(y0, x0):
    return bool(L3[y0 // 8:-(-(y0 + COTE) // 8), x0 // 8:-(-(x0 + COTE) // 8)].any())


objets = []
for k, s in enumerate(ndimage.find_objects(lab3)):
    cy, cx = (s[0].start + s[0].stop) * 4, (s[1].start + s[1].stop) * 4
    objets.append(dict(famille='lettre_etiquetee', ref='composante %d' % (k + 1), fen=fenetre(cy, cx)))

toutes = [r for r in csv.DictReader(open(sys.argv[1])) if r['segment'] == SEG_IBARA]
boites = [tuple(map(int, r['bbox_level0_y0x0y1x1'].split(','))) for r in toutes if r['priority'] in 'AB']
# (les 220 taches de segB, C comprises, touchent presque tout carreau de 2048 : 6 sur 3000 y echappent ;
#  le negatif exclut donc les grandes taches, A et B, et tolere les petites)
exclues = 0
for r in toutes:
    if r['priority'] != 'A':
        continue
    y0, x0, y1, x1 = map(int, r['bbox_level0_y0x0y1x1'].split(','))
    f = fenetre((y0 + y1) // 2, (x0 + x1) // 2)
    if touche_etiquette(*f):
        exclues += 1
        continue
    objets.append(dict(famille='cible_ibara', ref=r['bbox_level0_y0x0y1x1'], fen=f,
                       accord_ink9um=float(r['ink9um_agree_frac']), aire_niv2=int(r['area_px_level2'])))

# controle negatif : papyrus (carte publiee > 0 sur 95 % du carreau), aucune etiquette, aucune grande tache d ibara
P8 = tifffile.imread(PRED)[::8, ::8]
rng = np.random.default_rng(GRAINE)
neg, essais = [], 0
while len(neg) < N_NEG and essais < 20000:
    essais += 1
    y0, x0 = int(rng.integers(0, NY - COTE)), int(rng.integers(0, NX - COTE))
    if touche_etiquette(y0, x0):
        continue
    if (P8[y0 // 8:(y0 + COTE) // 8, x0 // 8:(x0 + COTE) // 8] > 0).mean() < 0.95:
        continue
    if any(b[0] < y0 + COTE and b[2] > y0 and b[1] < x0 + COTE and b[3] > x0 for b in boites):
        continue
    if any(abs(y0 - m['fen'][0]) < COTE and abs(x0 - m['fen'][1]) < COTE for m in neg):
        continue
    neg.append(dict(famille='papyrus_sans_rien', ref='tirage graine %d' % GRAINE, fen=(y0, x0)))
objets += neg

ordre = rng.permutation(len(objets))
cle = []
for num, i in enumerate(ordre):
    o = objets[i]
    y0, x0 = o['fen']
    tranches, pile = [], []
    for t in range(NT):
        a = np.asarray(vol[Z0 + t * EP:Z0 + (t + 1) * EP, y0:y0 + COTE, x0:x0 + COTE]).astype(np.float32)
        a = a.reshape(EP, COTE // 2, 2, COTE // 2, 2).mean(axis=(2, 4))
        pile += [a[j:j + 4].mean(0) for j in range(0, EP, 4)]
        tranches.append(a.mean(0))
    pap = np.stack(tranches) > 0
    lo, hi = np.percentile(np.stack(tranches)[pap], [1, 99]) if pap.any() else (0, 1)
    u8 = lambda im: (np.clip((im - lo) / max(hi - lo, 1e-6), 0, 1) * 255).astype(np.uint8)
    tuiles = [Image.fromarray(u8(tr)).resize((512, 512), Image.LANCZOS) for tr in tranches]
    planche = Image.new('L', (4 * 512 + 3 * 8, 2 * 512 + 8), 255)
    for t, im in enumerate(tuiles):
        planche.paste(im, ((t % 4) * 520, (t // 4) * 520))
    nom = 'P%02d' % (num + 1)
    planche.save('%s/panneaux/%s.png' % (OUT, nom))
    tifffile.imwrite('%s/piles/%s_pile.tif' % (OUT, nom), np.stack([u8(p) for p in pile]))
    cle.append(dict(panneau=nom, **{k: v for k, v in o.items() if k != 'fen'}, y0=y0, x0=x0))
    print(nom, flush=True)

json.dump(dict(cibles_A_segB=sum(r['priority'] == 'A' for r in toutes), cibles_exclues_etiquette=exclues,
               essais_negatifs=essais, panneaux=cle), open(OUT + '/CLE_NE_PAS_MONTRER.json', 'w'), indent=1)
print('familles', {f: sum(o['famille'] == f for o in objets) for f in set(o['famille'] for o in objets)},
      'exclues', exclues)
