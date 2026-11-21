import json, re, sys, os
from math import comb
base = sys.argv[1]
d = json.load(open(os.path.join(base, 'pr61_cle.json'), encoding='utf-8'))
plan = d['plan']; lect = d['lecteurs']
# parse answers
rep = {}
for r in lect:
    txt = open(os.path.join(base, 'pr61', 'reponses', f'reponse_{r}.txt'), encoding='utf-8').read()
    cur = None; blocks = {}
    for line in txt.splitlines():
        line = line.strip()
        if not line: continue
        m = re.match(r'^Image (\d+)$', line)
        if m: cur = int(m.group(1)); blocks[cur] = set(); continue
        if line == 'none': continue
        m = re.match(r'^([A-H])([1-3]):\s*(\S+)\s*\((\d)\)$', line)
        if not m: print('UNPARSED', r, repr(line)); continue
        blocks[cur].add((m.group(1), int(m.group(2)), m.group(3)))
    rep[r] = blocks
# panel,order -> {reader: set}
PO = {}
for r, lst in lect.items():
    for e in lst:
        PO.setdefault((e['panneau'], e['sens']), {})[r] = rep[r].get(e['image'], set())
panels = {}
for u in plan['unites']:
    for p in u['panneaux']: panels[p['nom']] = (u, p)
OTHER = {'direct': 'inverse', 'inverse': 'direct'}
def cell(c): return (c[0], int(c[1:]))
def support(w, o, c, n):
    col, row = c
    k = 0
    for r, items in PO.get((w, o), {}).items():
        if any(nm == n and abs(ord(cc) - ord(col)) <= 1 and abs(rr - row) <= 1 for cc, rr, nm in items): k += 1
    return k
def repeats(w, o, c, n):
    return support(w, o, c, n) >= 4 and support(w, OTHER[o], c, n) < 4
def fmt(c): return f'{c[0]}{c[1]}'
print('Readers per (panel, order):')
for w in panels:
    print(f'  {w}: direct={len(PO.get((w,"direct"),{}))} ({",".join(sorted(PO.get((w,"direct"),{})))}) inverse={len(PO.get((w,"inverse"),{}))} ({",".join(sorted(PO.get((w,"inverse"),{})))})')
print('\n1. Erwin letters')
nrep = 0
for w in ['E1', 'E2']:
    for lid, c in panels[w][1]['lettres'].items():
        n = plan['noms_erwin'][lid]; cc = cell(c)
        sd, si = support(w, 'direct', cc, n), support(w, 'inverse', cc, n)
        rp = sd >= 4 and si < 4; nrep += rp
        print(f'  {w} letter {lid} {c} {n}: direct={sd} inverse={si} repeats_forward={rp}')
print(f'  Letters repeating forward: {nrep}/12')
print('\n2. Flagged vs control')
def names_all(w):
    s = set()
    for o in ('direct', 'inverse'):
        for items in PO.get((w, o), {}).values():
            s |= {nm for _, _, nm in items}
    return s
def rep_list(w, o):
    p = panels[w][1]; out = []
    for c in p['empreinte']:
        for n in sorted(names_all(w)):
            cc = cell(c)
            if repeats(w, o, cc, n): out.append((c, n, support(w, o, cc, n), support(w, OTHER[o], cc, n)))
    return out
Rf = 0; Rc = 0; nflag = 0; nctrl = 0
for u in plan['unites']:
    nm = u['unite']
    if nm.startswith('S'):
        o = u['sens_signale']; L = rep_list(nm, o); nflag += 1; Rf += bool(L)
        print(f'  {nm} ({o}): repeats={bool(L)} {L}')
for u in plan['unites']:
    nm = u['unite']
    if nm.startswith('T'):
        for o in ('direct', 'inverse'):
            L = rep_list(nm, o); nctrl += 1; Rc += bool(L)
            print(f'  {nm} ({o}): repeats={bool(L)} {L}')
N = nflag + nctrl; K = Rf + Rc
p = sum(comb(K, x) * comb(N - K, nflag - x) for x in range(Rf, min(K, nflag) + 1)) / comb(N, nflag)
num = sum(comb(K, x) * comb(N - K, nflag - x) for x in range(Rf, min(K, nflag) + 1))
print(f'  Rf={Rf}/{nflag}  Rc={Rc}/{nctrl}  N={N} K={K}  p=P(X>={Rf})={num}/{comb(N,nflag)}={p:.6f}')
print('\n3. Panel B')
for lid, c in panels['B'][1]['lettres'].items():
    n = plan['noms_0009B'][lid]; cc = cell(c)
    print(f'  B letter {lid} {c} {n}: direct={support("B","direct",cc,n)} inverse={support("B","inverse",cc,n)}')
print('\n4. Items per reader')
tot = {}
for w, (u, p) in panels.items():
    s = []
    for o in ('direct', 'inverse'):
        R = PO.get((w, o), {}); t = sum(len(v) for v in R.values())
        grp = '0800' if p['zone'] == '0800' else ('E' if w in ('E1', 'E2') else w)
        tot[(grp, o)] = tot.get((grp, o), 0) + t
        s.append(f'{o}: {t} items / {len(R)} readers = {t/len(R):.3f}' if R else f'{o}: no readers')
    print(f'  {w}: ' + ' | '.join(s))
for g in ('0800', 'E', 'B'):
    print(f'  Total {g}: direct={tot.get((g,"direct"),0)} inverse={tot.get((g,"inverse"),0)}')
print('\n5. All (c,n) with support>=4')
for w in panels:
    for o in ('direct', 'inverse'):
        L = []
        for col in 'ABCDEFGH':
            for row in (1, 2, 3):
                for n in sorted(names_all(w)):
                    s = support(w, o, (col, row), n)
                    if s >= 4: L.append(f'{col}{row}:{n}={s}(other {support(w, OTHER[o], (col,row), n)})')
        print(f'  {w} {o}: ' + (', '.join(L) if L else '-'))
