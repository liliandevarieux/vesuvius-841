# Télécharge tous les fichiers d'un préfixe du seau public vesuvius-challenge-open-data (liste S3 paginée, 16 fils).
# usage : dl_s3_prefixe.py PREFIXE DOSSIER_LOCAL   (le préfixe est retiré du chemin local)
import sys, os, re, urllib.request, urllib.parse, concurrent.futures as cf
B = 'https://vesuvius-challenge-open-data.s3.amazonaws.com/'
pre, dest = sys.argv[1], sys.argv[2]
cles, jeton = [], None
while True:
    q = {'list-type': '2', 'prefix': pre}
    if jeton:
        q['continuation-token'] = jeton
    x = urllib.request.urlopen(B + '?' + urllib.parse.urlencode(q)).read().decode()
    cles += [(k, int(s)) for k, s in re.findall(r'<Key>([^<]+)</Key>.*?<Size>(\d+)</Size>', x)]
    m = re.search(r'<NextContinuationToken>([^<]+)</NextContinuationToken>', x)
    if not m:
        break
    jeton = m.group(1)
print(len(cles), 'fichiers,', round(sum(s for _, s in cles) / 1e6, 1), 'Mo', flush=True)


def un(ks):
    k, s = ks
    f = os.path.join(dest, k[len(pre):])
    if os.path.exists(f) and os.path.getsize(f) == s:
        return 0
    os.makedirs(os.path.dirname(f), exist_ok=True)
    urllib.request.urlretrieve(B + urllib.parse.quote(k), f)
    return s


with cf.ThreadPoolExecutor(16) as ex:
    n = sum(ex.map(un, cles))
print('telecharge', round(n / 1e6, 1), 'Mo ->', dest)
