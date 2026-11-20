# PR-58 : dépouillement de la lecture à l'aveugle des 12 lettres de 343 (inscription du 20/11 13:05).
# Mesure principale par carte : lectures justes sur 48, intervalle à 95 % (rééchantillonnage des lettres puis des
# lectures, 10 000 tirages), critère « lisible à l'aveugle » = au moins 6 sur 48 (hasard 1/24 : P = 0,014).
# Mesures secondaires : Reader V3 − Argus V3, Reader V3 − s43, Argus V3 − s43 ; permutation exacte des signes par
# lettre (2^12), unilatérale (premier nommé devant), et intervalle à 95 %.
# usage : c343_score.py CLE.json DOSSIER_REPONSES
import sys, json, re, itertools, collections, numpy as np
from math import comb

NOMS = ('alpha beta gamma delta epsilon zeta eta theta iota kappa lambda mu nu xi omicron pi rho sigma tau upsilon '
        'phi chi psi omega unreadable').split()


def lit(f):
    r = {}
    for l in open(f, encoding='utf-8'):
        m = re.match(r'\s*`?(\d+)\s*:(.*)', l)
        if m:
            mots = re.findall(r'[a-z]+', m.group(2).lower())
            r[int(m.group(1))] = next((w for w in mots if w in NOMS), '?')
    return r


def binsf(k, n, p):
    return sum(comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k, n + 1))


cle = json.load(open(sys.argv[1], encoding='utf-8'))
REC = list(cle['cartes'])
J = collections.defaultdict(lambda: collections.defaultdict(list))   # J[lettre][carte] = [0/1...]
nonlu = collections.Counter(); tot = collections.Counter()
par_case = collections.defaultdict(list)                              # (lettre, carte) -> noms donnés
lecteurs = sorted(k for k in cle if k.startswith('lecteur'))
for lk in lecteurs:
    rep = lit('%s/reponse_%s.txt' % (sys.argv[2], lk[-2:]))
    assert len(rep) == 12, (lk, len(rep))
    for c, (lid, nom, m) in cle[lk].items():
        x = rep.get(int(c), '?')
        J[lid][m].append(int(x == nom)); tot[m] += 1; nonlu[m] += x == 'unreadable'
        par_case[(lid, m)].append(x)
L = sorted(J, key=int)
print('lecteurs :', len(lecteurs), '| lettres :', len(L))
rng = np.random.default_rng(58)
print('\nMESURE PRINCIPALE (critere : >= 6 justes sur 48)')
for m in REC:
    k = sum(sum(J[l][m]) for l in L); n = sum(len(J[l][m]) for l in L)
    boot = []
    for _ in range(10000):
        s = 0
        for i in rng.integers(0, len(L), len(L)):
            x = np.array(J[L[i]][m]); s += x[rng.integers(0, len(x), len(x))].sum()
        boot.append(s / n)
    lo, hi = np.percentile(boot, [2.5, 97.5])
    print('%-11s %2d / %d = %4.1f %%  [IC 95 %% %4.1f ; %4.1f]  P(hasard >= k) = %.2e  illisible %d/%d  -> %s'
          % (m, k, n, 100 * k / n, 100 * lo, 100 * hi, binsf(k, n, 1 / 24), nonlu[m], tot[m],
             'LISIBLE A L AVEUGLE' if k >= 6 else 'non lisible'))
print('\nMESURES SECONDAIRES (permutation exacte des signes par lettre, unilaterale)')
signes = np.array(list(itertools.product([-1, 1], repeat=len(L))))
PAIRES = ([('v8in', 'readerv3'), ('v8in', 'argusv3'), ('readerv3', 'argusv3')] if 'v8in' in REC   # PR-59
          else [('readerv3', 'argusv3'), ('readerv3', 'ink9um_s43'), ('argusv3', 'ink9um_s43')])  # PR-58
for a, b in PAIRES:
    d = np.array([sum(J[l][a]) - sum(J[l][b]) for l in L]); S = int(d.sum())
    p = float(((signes * d).sum(1) >= S).mean())
    boot = []
    for _ in range(10000):
        t = 0
        for i in rng.integers(0, len(L), len(L)):
            xa, xb = np.array(J[L[i]][a]), np.array(J[L[i]][b])
            t += xa[rng.integers(0, len(xa), len(xa))].sum() - xb[rng.integers(0, len(xb), len(xb))].sum()
        boot.append(t / 48)
    lo, hi = np.percentile(boot, [2.5, 97.5])
    print('%-10s - %-10s : %+d lectures (%+.1f points) [IC 95 %% %+.1f ; %+.1f], p = %.4f'
          % (a, b, S, 100 * S / 48, 100 * lo, 100 * hi, p))
print('\nPAR LETTRE (justes sur 4, par carte)')
print('id nom       ' + ' '.join('%-10s' % m for m in REC))
for l in L:
    nom = cle['lettres'][str(l)] if str(l) in cle['lettres'] else cle['lettres'][l]
    print('%2s %-9s ' % (l, nom) + ' '.join('%d/%d       ' % (sum(J[l][m]), len(J[l][m])) for m in REC))
print('\nACCORD ENTRE LECTEURS DU MEME COUPLE (lettre, carte) : paires identiques hors "illisible"')
for m in REC:
    acc = tot_p = 0
    for l in L:
        v = par_case[(l, m)]
        for x, y in itertools.combinations(v, 2):
            tot_p += 1; acc += (x == y and x != 'unreadable')
    print('%-11s %d / %d paires' % (m, acc, tot_p))
