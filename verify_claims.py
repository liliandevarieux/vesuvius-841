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

# 3. the best slice named in the prose
m = re.search(r'no window beats\s+villa.s centred one by more than ([\d.]+)', DOC)
if not m:
    bad.append("the sentence quoting @AndreasHad04's 0.0138 bound is gone from the document")

# --- verdict -------------------------------------------------------------------------------------------------------
for label, measured, printed in claims:
    if abs(measured - printed) > 1e-9:
        bad.append(f'{label}: document says {printed}, measurement says {measured}')

print(f'{len(claims)} claims checked against results/*.json')
for b in bad:
    print('  DRIFT:', b)
print('OK' if not bad else f'{len(bad)} problem(s)')
sys.exit(1 if bad else 0)
