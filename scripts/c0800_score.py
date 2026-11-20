# PR-60 (inscrit 20/11 18:36, a0e9af5) : dépouillement, tel qu'inscrit.
# Principal : par carré de 0800, Yf = oui sur ses 24 lectures sens direct (4 cartes), Yr = sur ses 24 sens inverse ;
# bf, br = taux de oui sur les 52 carrés de 0800 ; p_t = P(Bin(24,bf) - Bin(24,br) >= Yf - Yr), exacte ; Holm sur 52 ;
# retenu si p corrigée <= 0,05. Porte : même test sur les 6 carrés d'Erwin avec lettre, bf et br de 0800, Holm sur 6 ;
# tient si au moins 3 retenus.
# Secondaires : chaque carte seule (6 contre 6, fond propre à la carte) avec sa porte ; taux de oui d'Erwin (carrés avec
# lettre, sens direct) par carte ; 0009B par carte et sens ; fonds ; lettres nommées.
# usage : c0800_score.py CLE.json DOSSIER_REPONSES   (réponses : reponse_01.txt ... reponse_48.txt)
import sys, re, json, collections, numpy as np
from scipy.stats import binom

NOMS = set(('alpha beta gamma delta epsilon zeta eta theta iota kappa lambda mu nu xi omicron pi rho sigma tau upsilon '
            'phi chi psi omega').split())


def lit(f):
    r = {}
    for l in open(f, encoding='utf-8'):
        m = re.match(r'\s*`?\s*(\d+)\s*[:.)]\s*\**\s*(yes|no)\b(.*)', l, re.I)
        if m:
            r[int(m.group(1))] = (m.group(2).lower() == 'yes', [w for w in re.findall(r'[a-z]+', m.group(3).lower()) if w in NOMS])
    return r


def p_diff(d, bf, br, n):
    pf = binom.pmf(np.arange(n + 1), n, bf); pr = binom.pmf(np.arange(n + 1), n, br)
    dist = np.convolve(pf, pr[::-1])
    return float(dist[max(0, d + n):].sum())


def holm(p):
    p = np.asarray(p, float); o = np.argsort(p); m = len(p); adj = np.empty(m); run = 0.0
    for i, k in enumerate(o):
        run = max(run, min(1.0, (m - i) * p[k])); adj[k] = run
    return adj


cle = json.load(open(sys.argv[1], encoding='utf-8'))
COND = [tuple(c) for c in cle['conditions']]; PL = cle['carres']
oui = collections.defaultdict(list); noms = collections.defaultdict(list); incidents = []
for r, k in sorted(cle['lecteurs'].items()):
    rep = lit('%s/reponse_%s.txt' % (sys.argv[2], r))
    if len(rep) != len(k):
        incidents.append('lecteur %s : %d lignes lisibles sur %d' % (r, len(rep), len(k)))
    for n, (j, c) in k.items():
        if int(n) in rep:
            y, nm = rep[int(n)]; oui[(j, c)].append(int(y))
            if y and nm:
                noms[j].append('%s/%s:%s' % (COND[c][0], COND[c][1][:3], '+'.join(nm)))
Z = {z: [j for j, t in enumerate(PL) if t['zone'] == z] for z in ('0800', 'erwin', '0009B')}
EL = [j for j in Z['erwin'] if PL[j]['lettres']]; EN = [j for j in Z['erwin'] if not PL[j]['lettres']]
print('lecteurs : %d ; incidents : %s' % (len(cle['lecteurs']), incidents or 'aucun'))


def teste(cartes, titre):
    cf = [COND.index((m, 'direct')) for m in cartes]; cr = [COND.index((m, 'inverse')) for m in cartes]
    Y = lambda j, cs: (sum(sum(oui[(j, c)]) for c in cs), sum(len(oui[(j, c)]) for c in cs))
    F = [Y(j, cf) for j in Z['0800']]; Rv = [Y(j, cr) for j in Z['0800']]
    bf = sum(a for a, _ in F) / sum(b for _, b in F); br = sum(a for a, _ in Rv) / sum(b for _, b in Rv)
    n = 6 * len(cartes)
    p = [p_diff(f[0] - r[0], bf, br, n) for f, r in zip(F, Rv)]; ph = holm(p)
    ret = [(Z['0800'][i], F[i][0], Rv[i][0], ph[i]) for i in range(len(p)) if ph[i] <= 0.05]
    pe = [p_diff(Y(j, cf)[0] - Y(j, cr)[0], bf, br, n) for j in EL]; peh = holm(pe)
    ne = int((peh <= 0.05).sum())
    print('\n== %s (%d lectures par sens et par carre)' % (titre, n))
    print('fond 0800 : oui direct bf = %.3f, oui inverse br = %.3f' % (bf, br))
    print('PORTE Erwin : %d carres avec lettre retenus sur %d -> %s' % (ne, len(EL), 'TIENT' if ne >= 3 else 'ECHOUE'))
    for j, ph_ in zip(EL, peh):
        print('   erwin carre %2d lettres %-12s direct %2d/%d inverse %2d/%d  p Holm %.4f'
              % (j, PL[j]['lettres'], Y(j, cf)[0], n, Y(j, cr)[0], n, ph_))
    print('0800 : %d carre(s) retenu(s) sur %d' % (len(ret), len(Z['0800'])))
    for j, f, r, q in ret:
        print('   RETENU carre %2d %s y %d x %d : direct %d/%d inverse %d/%d p Holm %.4g ; noms : %s'
              % (j, PL[j]['surface'], PL[j]['y'], PL[j]['x'], f, n, r, n, q, ' '.join(noms[j]) or '-'))
    meil = sorted(range(len(p)), key=lambda i: p[i])[:5]
    print('   5 plus petites p brutes :', ', '.join('carre %d (%s) %d-%d p %.3g' % (Z['0800'][i], PL[Z['0800'][i]]['surface'],
                                                                         F[i][0], Rv[i][0], p[i]) for i in meil))
    return ne, ret


ne, ret = teste(['moyenne', 'readerv3', 'argusv3', 'v8in'], 'PRINCIPAL : 4 cartes reunies')
print('\nDECISION :', 'porte echoue : rien n est conclu sur 0800' if ne < 3 else
      ('%d carre(s) candidat(s) sur 0800' % len(ret) if ret else 'aucun carre retenu sur 0800'))
print('\n== SECONDAIRE 1 : chaque carte seule')
for m in ('moyenne', 'readerv3', 'argusv3', 'v8in'):
    teste([m], m)
taux = lambda js, c: (sum(sum(oui[(j, c)]) for j in js), sum(len(oui[(j, c)]) for j in js))
print('\n== Taux de oui par condition (oui / lectures)')
print('%-20s %14s %14s %14s %14s' % ('condition', 'erwin lettre', 'erwin sans', '0009B', '0800'))
for c, k in enumerate(COND):
    print('%-20s %14s %14s %14s %14s' % ('%s %s' % k, '%d/%d' % taux(EL, c), '%d/%d' % taux(EN, c),
                                        '%d/%d' % taux(Z['0009B'], c), '%d/%d' % taux(Z['0800'], c)))
print('\n== Lettres nommees sur les carres d Erwin')
for j in Z['erwin']:
    print('   carre %2d lettres de reference %-14s : %s' % (j, PL[j]['lettres'], ' '.join(noms[j]) or '-'))
