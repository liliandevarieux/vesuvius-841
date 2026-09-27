# PR-38 : un zarr d etiquettes du corpus est-il complet ? (nombre de fichiers de chunks = nombre attendu d apres .zarray ;
# les fichiers vides laisses par une synchronisation coupee sont retires, donc comptes manquants)
# usage : corpus_complet.py SEGMENT   -> imprime OK ou INCOMPLET ; code de sortie 0 si OK
import sys, os, json, math
D = '/home/slusarska_holding/vesuvius/ft12m/corpus24/' + sys.argv[1]
ok = True
for q in ('supervision_mask', 'inklabels'):
    z = '%s/%s_%s.zarr/0' % (D, sys.argv[1], q)
    try:
        m = json.load(open(z + '/.zarray'))
    except OSError:
        ok = False; continue
    att = math.prod(math.ceil(s / c) for s, c in zip(m['shape'], m['chunks']))
    vides = [f for f in os.listdir(z) if not f.startswith('.') and os.path.getsize(os.path.join(z, f)) == 0]
    for f in vides:                                   # restes de synchronisations coupees : a retelecharger
        os.remove(os.path.join(z, f))
    n = sum(1 for f in os.listdir(z) if not f.startswith('.'))
    if vides:
        print(q, len(vides), 'fichiers vides retires')
    ok &= n >= att
    print(q, n, '/', att)
print('OK' if ok else 'INCOMPLET')
sys.exit(0 if ok else 1)
