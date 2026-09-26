# Telecharge un ECHANTILLON d un volume zarr v2 non compresse du serveur open-data : les metadonnees, puis les
# chunks de niveau 0 couvrant un carreau de COTE px tous les PAS px. Le reste du volume reste absent (lu comme 0,
# donc exclu par occupation2.py qui ignore les colonnes vides).
# usage : dl_echantillon.py CHEMIN_S3_DU_ZARR DOSSIER_LOCAL [PAS] [COTE]
import sys, os, json, urllib.request
from concurrent.futures import ThreadPoolExecutor

B = 'https://vesuvius-challenge-open-data.s3.amazonaws.com/'
src, dst = sys.argv[1].rstrip('/'), sys.argv[2]
PAS = int(sys.argv[3]) if len(sys.argv) > 3 else 8192
COTE = int(sys.argv[4]) if len(sys.argv) > 4 else 512


def get(cle, fichier):
    if os.path.exists(fichier):
        return True
    os.makedirs(os.path.dirname(fichier), exist_ok=True)
    try:
        with urllib.request.urlopen(B + cle, timeout=120) as r:
            data = r.read()
    except Exception:
        return False
    open(fichier + '.part', 'wb').write(data)
    os.replace(fichier + '.part', fichier)
    return True


for m in ['.zattrs', '.zgroup', '0/.zarray']:
    get('%s/%s' % (src, m), '%s/%s' % (dst, m))
za = json.load(open(dst + '/0/.zarray'))
D, H, W = za['shape']
cz, cy, cx = za['chunks']
sep = za.get('dimension_separator', '.')
cles = []
for y in range(0, H, PAS):
    for x in range(0, W, PAS):
        for j in range(y // cy, min(-(-H // cy), (y + COTE) // cy)):
            for i in range(x // cx, min(-(-W // cx), (x + COTE) // cx)):
                for k in range(-(-D // cz)):
                    c = sep.join(str(v) for v in (k, j, i))
                    cles.append(('%s/0/%s' % (src, c), '%s/0/%s' % (dst, c)))
with ThreadPoolExecutor(16) as ex:
    ok = sum(ex.map(lambda a: get(*a), cles))
print('%d chunks demandes, %d presents sur le serveur, forme %s' % (len(cles), ok, za['shape']))
