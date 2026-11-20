# PR-58 : planches de lecture à l'aveugle des 12 lettres de 343 sur trois cartes (inscription du 20/11 13:05).
# Cartes de l'équipe ramenées dans le repère de lecture d'Erwin (c343_recale.py), vignettes du banc v2
# (boîte + 40 px, 200 px, contraste 1-99,5 %), ordre mélangé par lecteur (graine 58 + r), carré latin
# (lecteur r lit la lettre j sur la carte (j + r) mod 3). Planche d'essai à blanc : cadres décalés de 700 px vers le bas,
# cartes en alternance, non comptée. La clé va dans un fichier que les lecteurs ne voient pas.
import sys, json, random, numpy as np, tifffile
sys.path.insert(0, '/home/slusarska_holding/vesuvius')
import c343_recale as K
from banc_lisibilite import vignette, planche

D = K.D
CARTES = {'readerv3': '20261019111505-reader-v3-tile384-stride192',
          'argusv3': '20261117205746-argus-v3-tile384-stride192',
          'ink9um_s43': '20260814010243-ink9um-hybrid3d2d-s43-20k-tile128-stride64'}
REC = list(CARTES)
M, LECTEURS, GRAINE, DECALE = 40, 12, 58, 700
OUT = D + 'pr58/'

if __name__ == '__main__':
    import os
    os.makedirs(OUT, exist_ok=True)
    L = json.load(open(D + 'reference_12_lettres.json'))
    Z = {}
    for m, f in CARTES.items():
        o = OUT + 'lecture_%s.tif' % m
        if not os.path.exists(o):
            K.carte(D + 'equipe/cartes/%s.tif' % f, o)
        Z[m] = tifffile.imread(o).astype(np.float32)
    def cadre(l, dy=0):
        x0, y0, x1, y1 = l['zone']
        y0, y1 = y0 + dy, y1 + dy
        return slice(max(0, y0 - M), min(K.ZH, y1 + M)), slice(max(0, x0 - M), min(K.ZW, x1 + M))
    V = {(j, m): vignette(Z[m][cadre(l)]) for j, l in enumerate(L) for m in REC}
    cle = {'cartes': CARTES, 'lettres': {l['id']: l['nom'] for l in L}}
    for r in range(LECTEURS):
        ordre = list(range(len(L)))
        random.Random(GRAINE + r).shuffle(ordre)
        k = {}
        for c, j in enumerate(ordre):
            k[c + 1] = [L[j]['id'], L[j]['nom'], REC[(j + r) % len(REC)]]
        planche([(c, V[(j, k[c][2])]) for c, j in zip(k, ordre)], OUT + 'planche_%02d.png' % (r + 1))
        cle['lecteur%02d' % (r + 1)] = k
    ordre = list(range(len(L)))
    random.Random(GRAINE - 1).shuffle(ordre)
    planche([(c + 1, vignette(Z[REC[c % 3]][cadre(L[j], DECALE)])) for c, j in enumerate(ordre)], OUT + 'essai_blanc.png')
    json.dump(cle, open(OUT + 'cle_pr58.json', 'w'), indent=1, ensure_ascii=False)
    print(len(L), 'lettres,', LECTEURS, 'planches + essai a blanc ; cle :', OUT + 'cle_pr58.json')
