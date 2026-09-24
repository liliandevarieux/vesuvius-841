#!/usr/bin/env python3
"""Re-derive every number printed in MEASUREMENTS.md from results/*.json, and fail if any of them has drifted.

The JSON files are written by the measurement scripts themselves (`JSON=<path> python scripts/mesure_sens.py ...`),
so this checks the documentation against the measurement, not against a second copy of the documentation.

    python verify_claims.py        # exit 0 if every claim matches, 1 otherwise
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
R = lambda n: json.load(open(os.path.join(HERE, 'results', n), encoding='utf-8'))
DOC = open(os.path.join(HERE, 'MEASUREMENTS.md'), encoding='utf-8').read()

# --- the claims, each one (label, value measured, value as the document prints it) ---------------------------------
claims, bad = [], []


def cell(x):
    return x.replace('*', '').strip()


def rows(after, ncol):
    """Markdown table rows following the given heading, as lists of cleaned cells."""
    body = DOC[DOC.index(after):]
    out = []
    for line in body.split('\n'):
        if not line.startswith('|'):
            if out:
                break
            continue
        c = [cell(x) for x in line.strip('|').split('|')]
        if len(c) == ncol and not set(''.join(c)) <= set('-: '):
            out.append(c)
    return out


def num(s):
    return float(s.replace('\u2212', '-').replace(',', '.'))


# 1. direction, per window and mean, for both segments
tab = rows('## 1. Depth direction', 4)
seen = set()
for name, jf in (('ag174', 'direction_ag174.json'), ('ag144', 'direction_ag144.json')):
    j = R(jf)
    per = {str(w['window']): w for w in j['windows']}
    per['mean'] = j['mean'] and {'direct': j['mean']['direct'], 'reversed': j['mean']['reversed']}
    for seg, win, direct, rev in tab:
        if seg != name:
            continue
        key = win if win != 'mean' else 'mean'
        if key not in per:
            bad.append(f'{name} window {win}: no measurement in {jf}')
            continue
        seen.add((name, key))
        for side, txt in (('direct', direct), ('reversed', rev)):
            sep, corr = [num(x) for x in txt.split('/')]
            m = per[key][side]
            claims.append((f'{name} w{win} {side} separation', m['sep'], sep))
            claims.append((f'{name} w{win} {side} correlation', m['corr'], corr))
    for key in list(per):
        if (name, key) not in seen:
            bad.append(f'{name} {key} is measured in {jf} but absent from the table')

# 2. slice sweep
sl = R('slice_ag174_win2.json')
tab = rows('## 2. Which 65 of the 109 planes', len(sl['slices']) + 1)
if len(tab) != 2:
    bad.append('slice table: expected a header row and a separation row, found %d rows' % len(tab))
else:
    head, sepr = tab
    if head[1:] != [s['tag'] for s in sl['slices']]:
        bad.append('slice table columns %s do not match the measured slices %s'
                   % (head[1:], [s['tag'] for s in sl['slices']]))
    for s, txt in zip(sl['slices'], sepr[1:]):
        claims.append((f"slice centre {s['tag']} separation", s['sep'], num(txt)))

# 3. the array test: same segment, two arrays
ar = R('array_ag174.json')
tab = [r for r in rows('## 4. The same segment on two arrays', 3) if r[0] != 'window']  # sans l en-tete
per = {str(w['window']): w for w in ar['windows']}
per['mean'] = ar['mean']
for win, stored, rev in tab:
    key = win if win in per else None
    if key is None:
        bad.append('array table: row %r has no counterpart in array_ag174.json' % win)
        continue
    claims.append((f'array window {win} stored', per[key]['stored']['sep'], num(stored)))
    claims.append((f'array window {win} reversed', per[key]['reversed']['sep'], num(rev)))
for key in per:
    if key not in [r[0] for r in tab]:
        bad.append('array_ag174.json has %r but the table does not' % key)
if ar['prefers'] != 'stored':
    bad.append("the text says the bucket render prefers the stored order, the measurement says %r" % ar['prefers'])

# 4. the best slice named in the prose
m = re.search(r'no window beats\s+villa.s centred one by more than ([\d.]+)', DOC)
if not m:
    bad.append("the sentence quoting @AndreasHad04's 0.0138 bound is gone from the document")

# 5. the blind batch: the six counts and the p value
bb = R('blind_batch_segB.json')
tabb = rows('## 5. A negative control on the human reader', 4)
noms = {'real candidates (6)': 'candidate', 'decoys (6)': 'LEURRE'}
vus = set()
for r in tabb:
    if r[1] == 'certain ink':      # la ligne d en-tete a elle aussi quatre cellules
        continue
    q = noms.get(r[0])
    if q is None:
        bad.append('unexpected row %r in the blind-batch table' % r[0])
        continue
    vus.add(q)
    for col, key in ((1, 'encre'), (2, 'doute'), (3, 'rien')):
        claims.append(('blind batch %s %s' % (q, key), bb['counts'][q][key], num(r[col])))
for q in ('candidate', 'LEURRE'):
    if q not in vus:
        bad.append('the blind-batch table has lost its %s row' % q)
m = re.search(r'one-sided, on the \*certain ink\* rate: \*\*p = ([\d.]+)', DOC)
if not m:
    bad.append('the blind batch p value is gone from the document')
else:
    claims.append(('blind batch Fisher p', round(bb['fisher_one_sided_p'], 3), num(m.group(1))))

# 7. PREREGISTRATIONS.md — every (segB, segA) pair printed in a table must equal the raw measurement
#
# Why this section exists. Until 2026-09-24 this file checked MEASUREMENTS.md and nothing else. Meanwhile the
# preregistration file had grown to carry every separation figure of the project, and not one of them was
# re-derived by anything automatic: they were checked once, by hand, by an agent asked to do it. A number that
# drifts in a table nobody re-derives is exactly how a wrong figure survives — and two wrong figures were caught
# by hand that same day.
#
# What it does, and what it does NOT do. It scans every markdown table row, reads the numbers cell by cell, and
# for each pair of adjacent numeric cells asks whether some measured arm has a (segB, segA) pair within 2.0 of it.
# If one does, the pair must match that measurement EXACTLY. This catches drift — a figure that has moved — in
# whatever table shape it is written in, without the script having to know the shape.
# It does NOT check that every measurement appears in the document: an arm that is simply never mentioned passes
# silently. Omission is not covered here, and saying so is part of the check.
PRE = open(os.path.join(HERE, 'PREREGISTRATIONS.md'), encoding='utf-8').read()
ARMS = {}
for fn in sorted(os.listdir(os.path.join(HERE, 'results'))):
    m = re.match(r'pr\d+_(seg[AB])_(\w+)\.json$', fn)
    if m:
        ARMS.setdefault(m.group(2), {})[m.group(1)] = R(fn)['mean']['reversed']['sep']
PAIRS = {t: (v['segB'], v['segA']) for t, v in ARMS.items() if 'segB' in v and 'segA' in v}

NUM = re.compile(r'(?<![\w.])([+−-]?\d+[.,]\d)(?![\d])')
# A pair of adjacent numeric cells only counts as an arm's (segB, segA) if the row is actually ABOUT an arm: either
# the row names one, or its table's header names both segments. Without this, the rule fires on any two numbers that
# land within 2.0 of some arm — which it did on 2026-09-24 at 21:35, on a table of grey-level means where plane 32
# reads 84.4, the exact value of `trev` on segB, and plane 50 reads 83.4 / 86.9 against its 84.4 / 87.6. Three false
# DRIFT reports out of one coincidence. A checker that cries drift when nothing drifted is worse than a gap in
# coverage: the next real drift gets read as another false alarm.
# What this does NOT weaken: every genuine results table here either labels its rows by arm or its header by segment.
# The guard is the arm count printed below — it must not fall when this filter is added (it stayed at 6).
MOTS = re.compile(r'(?<![\w-])(%s)(?![\w-])' % '|'.join(map(re.escape, sorted(PAIRS, key=len, reverse=True))))
apparies = set()
entete = ''
for line in PRE.split('\n'):
    if not line.startswith('|'):
        entete = ''
        continue
    if not entete:
        entete = line
    if not (('segB' in entete and 'segA' in entete) or MOTS.search(line)):
        continue
    vals = []
    for c in line.strip('|').split('|'):
        f = NUM.findall(cell(c))
        vals.append(num(f[0]) if len(f) == 1 else None)
    for i in range(len(vals) - 1):
        a, b = vals[i], vals[i + 1]
        if a is None or b is None:
            continue
        proches = [(t, p) for t, p in PAIRS.items() if abs(a - p[0]) <= 2.0 and abs(b - p[1]) <= 2.0]
        if not proches:
            continue
        t, p = min(proches, key=lambda x: abs(a - x[1][0]) + abs(b - x[1][1]))
        apparies.add(t)
        claims.append((f'PREREG {t} segB', p[0], a))
        claims.append((f'PREREG {t} segA', p[1], b))
# The same check on prose, in the one sentence shape these results are actually written in:
# "... **84.4** on segB and **87.6** on segA". Found by testing the section above: perturbing the figure in the
# table was caught, perturbing the SAME figure three lines higher, in the sentence, was not. A check that only
# covers the tidy half of the document gives false confidence about the other half.
# Only this shape is covered. Prose cannot be checked generically: `trev` is 84.4 and `v24s43` is 84.3 on segB,
# so any "near a measurement but not equal" rule would make two real measurements accuse each other.
PHRASE = re.compile(r'\*{0,2}([+−-]?\d+\.\d)\*{0,2} on segB and \*{0,2}([+−-]?\d+\.\d)\*{0,2} on segA')
nphr = 0
for a, b in ((num(x), num(y)) for x, y in PHRASE.findall(PRE)):
    proches = [(t, p) for t, p in PAIRS.items() if abs(a - p[0]) <= 2.0 and abs(b - p[1]) <= 2.0]
    if not proches:
        continue
    t, p = min(proches, key=lambda x: abs(a - x[1][0]) + abs(b - x[1][1]))
    apparies.add(t); nphr += 1
    claims.append((f'PREREG prose {t} segB', p[0], a))
    claims.append((f'PREREG prose {t} segA', p[1], b))
print(f'PREREGISTRATIONS: {len(PAIRS)} measured arms on disk, {len(apparies)} found '
      f'({", ".join(sorted(apparies)) or "none"}), {nphr} of them in prose; omission is not checked, only drift')

# --- verdict -------------------------------------------------------------------------------------------------------
for label, measured, printed in claims:
    if abs(measured - printed) > 1e-9:
        bad.append(f'{label}: document says {printed}, measurement says {measured}')

print(f'{len(claims)} claims checked against results/*.json')
for b in bad:
    print('  DRIFT:', b)
print('OK' if not bad else f'{len(bad)} problem(s)')
sys.exit(1 if bad else 0)
