# PR-49 : depouillement. Chaque lecteur liste « case : lettre (confiance) » sur la fenetre du texte de 1447. Sa
# transcription = ses lettres rangees par rangee (1-5) puis par colonne (A-H). Score = plus longue sous-suite commune
# (LCS) avec la lecture publiee des papyrologues, lignes 2 et 3 bout a bout : π ε ρ ι ε π ι λ ε γ ε ι (12 lettres).
# Primaire : moyenne P - moyenne T sur les 6 lecteurs de chaque bras, permutation exacte unilaterale (924 partages),
# tient si p < 0,05 avec P devant. Secondaires : chaque ligne a part (περιε, πιλεγει), score au hasard pour le meme
# nombre de lettres nommees (2 000 tirages uniformes sur 24 lettres), chaque graine.
# usage : score_pr49.py P=f1,f2,... T=f1,f2,...
import sys, re, itertools, numpy as np

NOMS = ('alpha beta gamma delta epsilon zeta eta theta iota kappa lambda mu nu xi omicron pi rho sigma tau upsilon '
        'phi chi psi omega').split()
L2 = ['pi', 'epsilon', 'rho', 'iota', 'epsilon']
L3 = ['pi', 'iota', 'lambda', 'epsilon', 'gamma', 'epsilon', 'iota']
REF = L2 + L3
rng = np.random.default_rng(49)


def lcs(a, b):
    t = np.zeros((len(a) + 1, len(b) + 1), int)
    for i in range(len(a)):
        for j in range(len(b)):
            t[i + 1, j + 1] = t[i, j] + 1 if a[i] == b[j] else max(t[i, j + 1], t[i + 1, j])
    return int(t[-1, -1])


def lit(f):
    items = []
    for l in open(f, encoding='utf-8'):
        m = re.match(r'\s*`?\s*([A-Ha-h])\s*([1-5])\s*`?\s*:(.*)', l)
        if m:
            nom = next((w for w in re.findall(r'[a-z]+', m.group(3).lower()) if w in NOMS), None)
            if nom:
                items.append((int(m.group(2)), 'ABCDEFGH'.index(m.group(1).upper()), nom))
    return [n for _, _, n in sorted(items, key=lambda x: (x[0], x[1]))]


bras = {}
for arg in sys.argv[1:]:
    nom, fs = arg.split('=')
    bras[nom] = []
    for f in fs.split(','):
        t = lit(f)
        s, s2, s3 = lcs(t, REF), lcs(t, L2), lcs(t, L3)
        hasard = [lcs(list(rng.choice(NOMS, len(t))), REF) for _ in range(2000)] if t else [0]
        bras[nom].append(s)
        print('%-2s %-40s %2d lettres nommees : LCS %d (ligne 2 : %d, ligne 3 : %d) ; hasard moyen %.2f, 95e centile %d | %s'
              % (nom, f.split('/')[-1], len(t), s, s2, s3, np.mean(hasard), np.percentile(hasard, 95), ' '.join(t)))
for nom, v in bras.items():
    print('%-2s : LCS moyen %.2f sur %d lecteurs %s' % (nom, np.mean(v), len(v), v))
if 'P' in bras and 'T' in bras:
    a, b = np.array(bras['P']), np.array(bras['T'])
    x = np.concatenate([a, b])
    obs = a.mean() - b.mean()
    null = [x[list(c)].mean() - np.delete(x, list(c)).mean() for c in itertools.combinations(range(len(x)), len(a))]
    p = float(np.mean(np.array(null) >= obs - 1e-9))
    print('PRIMAIRE : P - T = %+.2f lettres dans l ordre, p unilateral exact = %.4f -> %s'
          % (obs, p, 'TIENT' if p < 0.05 and obs > 0 else 'echoue'))
