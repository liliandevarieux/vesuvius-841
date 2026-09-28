# PR-46 : depouillement de la lecture a l aveugle. Lit la cle (case -> feuillet, lettre, modele) et les reponses des
# lecteurs (fichiers texte, lignes « N: nom (confiance) »), prend la lecture du trace comme reference (lettre ecartee si
# le lecteur de reference repond « unreadable »), et compte les lettres bien lues par modele ; les 5 lettres de 0009B
# que Reader v2 a vues a l entrainement (PR-45, controle de contamination) sont comptees a part.
# usage : score_pr46.py CLE.json TRACES.txt LECTEUR1.txt LECTEUR2.txt LECTEUR3.txt
import sys, re, json

NOMS = ('alpha beta gamma delta epsilon zeta eta theta iota kappa lambda mu nu xi omicron pi rho sigma tau upsilon '
        'phi chi psi omega unreadable').split()
VUES = {('0009B', i) for i in (1, 3, 4, 7, 8)}


def lit(f):
    r = {}
    for l in open(f, encoding='utf-8'):
        m = re.match(r'\s*`?(\d+)\s*:(.*)', l)
        if not m:
            continue
        mots = re.findall(r'[a-z]+', m.group(2).lower())
        nom = next((w for w in mots if w in NOMS), '?')
        conf = re.search(r'\((\d)\)', m.group(2))
        r[m.group(1)] = (nom, int(conf.group(1)) if conf else 0)
    return r


cle = json.load(open(sys.argv[1]))
rep0 = lit(sys.argv[2])
ref = {}
for c, (s, n, _) in cle['traces'].items():
    a = rep0.get(c, ('?', 0))[0]
    print('reference %-8s lettre %2d : %s (%d)' % (s, n, a, rep0.get(c, ('?', 0))[1]))
    if a not in ('unreadable', '?'):
        ref[(s, n)] = a
res, detail = {}, []
for r in (1, 2, 3):
    rep = lit(sys.argv[2 + r])
    for c, (s, n, m) in cle['lecteur%d' % r].items():
        if (s, n) not in ref:
            continue
        a, conf = rep.get(c, ('?', 0))
        ok = a == ref[(s, n)]
        g = 'vues' if (s, n) in VUES else ('propres_841' if s.startswith('841') else 'propres_0009B')
        t = res.setdefault((m, g), [0, 0])
        t[0] += ok
        t[1] += 1
        detail.append((s, n, ref[(s, n)], m, r, a, conf, ok))
for d in sorted(detail):
    print('%-8s lettre %2d  ref %-8s  %-8s lecteur %d : %-10s (%d) %s' % (d[0], d[1], d[2], d[3], d[4], d[5], d[6], 'JUSTE' if d[7] else ''))
print()
for m in ('base', 'R4', 'readerv2'):
    p841, p9, v = (res.get((m, g), [0, 0]) for g in ('propres_841', 'propres_0009B', 'vues'))
    print('%-8s : propres %2d / %2d  (841 %2d / %2d, 0009B %d / %d)  |  vues par Reader v2 %d / %d'
          % (m, p841[0] + p9[0], p841[1] + p9[1], p841[0], p841[1], p9[0], p9[1], v[0], v[1]))
j = {m: sum(res.get((m, g), [0, 0])[0] for g in ('propres_841', 'propres_0009B')) for m in ('base', 'R4', 'readerv2')}
print('PRIMAIRE : Reader v2 - R4 sur les lettres propres = %+d  (>= +4 : Reader v2 plus lisible ; <= -4 : R4 plus lisible)'
      % (j['readerv2'] - j['R4']))
