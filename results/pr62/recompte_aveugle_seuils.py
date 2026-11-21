import json, re, os, sys
from fractions import Fraction
from math import comb
from collections import defaultdict
base = r"..\pr61"
key = json.load(open(os.path.join(base, "cle_pr61.json"), encoding="utf-8"))
zone = {}
for u in key["plan"]["unites"]:
    for p in u["panneaux"]:
        assert p["nom"] not in zone or zone[p["nom"]] == p["zone"]
        zone[p["nom"]] = p["zone"]
print("panels per zone:", {z: sorted(n for n in zone if zone[n] == z) for z in sorted(set(zone.values()))})
cellre = re.compile(r"^([A-H])([1-3]):\s*(.+?)\s*\((.*)\)\s*$")
def parse(path):
    out = {}; cur = None; bad = []
    for line in open(path, encoding="utf-8"):
        s = line.strip()
        if not s: continue
        m = re.match(r"^Image\s+(\d+)$", s)
        if m:
            cur = int(m.group(1)); assert cur not in out; out[cur] = []; continue
        if s.lower() == "none": continue
        m = cellre.match(s)
        if m and cur is not None:
            out[cur].append((m.group(1) + m.group(2), m.group(3).strip()))
        else:
            bad.append(s)
    return out, bad
answers = {}
allnames = set()
for rid in key["lecteurs"]:
    a, bad = parse(os.path.join(base, "reponses", f"reponse_{rid}.txt"))
    if bad: print("UNPARSED", rid, bad)
    answers[rid] = a
    for v in a.values():
        for c, n in v: allnames.add(n)
low = defaultdict(set)
for n in allnames: low[n.lower()].add(n)
print("case variants:", {k: v for k, v in low.items() if len(v) > 1} or "none")
# coverage check
for rid, ents in key["lecteurs"].items():
    ks = {e["image"] for e in ents}
    if ks != set(answers[rid]): print("IMAGE MISMATCH", rid, sorted(ks ^ set(answers[rid])))
# Part 1
print("\nPART 1: single readings with >=4 distinct (cell,name)")
tot = defaultdict(int); hit = defaultdict(int)
for rid, ents in key["lecteurs"].items():
    for e in ents:
        pairs = set(answers[rid].get(e["image"], []))
        k = (zone[e["panneau"]], e["sens"])
        tot[k] += 1
        if len(pairs) >= 4: hit[k] += 1
for z in ["erwin", "0009B", "0800"]:
    for o in ["direct", "inverse"]:
        print(f"  {z:6s} {o:8s}: {hit[(z,o)]} / {tot[(z,o)]}")
# Part 2
readers = defaultdict(dict)  # (w,o) -> rid -> set of (cell,name)
for rid, ents in key["lecteurs"].items():
    for e in ents:
        readers[(e["panneau"], e["sens"])].setdefault(rid, set()).update(answers[rid].get(e["image"], []))
def cc(c): return "ABCDEFGH".index(c[0]), int(c[1])
cells = [a + str(r) for a in "ABCDEFGH" for r in (1, 2, 3)]
def near(c1, c2):
    x1, y1 = cc(c1); x2, y2 = cc(c2); return abs(x1 - x2) <= 1 and abs(y1 - y2) <= 1
def support(w, o, c, n):
    return sum(1 for rid, ps in readers.get((w, o), {}).items() if any(nn == n and near(cx, c) for cx, nn in ps))
other = {"direct": "inverse", "inverse": "direct"}
print("\nPART 2: forms per (panel, sens)")
res = {}
for (w, o) in sorted(readers):
    names = {n for ps in readers[(w, o)].values() for _, n in ps}
    rep = []
    for c in cells:
        for n in names:
            if support(w, o, c, n) >= 4 and support(w, other[o], c, n) < 4:
                rep.append((c, n))
    # connected components
    seen = set(); forms = []
    for x in rep:
        if x in seen: continue
        comp = []; stack = [x]; seen.add(x)
        while stack:
            y = stack.pop(); comp.append(y)
            for z in rep:
                if z not in seen and z[1] == y[1] and near(z[0], y[0]):
                    seen.add(z); stack.append(z)
        forms.append(sorted(comp))
    res[(w, o)] = len(forms)
    print(f"  {w:5s} {zone[w]:6s} {o:8s} readers={len(readers[(w,o)])} repeating={len(rep)} forms={len(forms)}  " + "; ".join(f"{f[0][1]}@{','.join(c for c,_ in f)}" for f in forms))
print("\n  per zone (descending):")
for z in ["erwin", "0009B", "0800"]:
    for o in ["direct", "inverse"]:
        v = sorted((res[(w, oo)] for (w, oo) in res if zone[w] == z and oo == o), reverse=True)
        print(f"   {z:6s} {o:8s}: {v}  (sum {sum(v)}, n={len(v)})")
# Part 3
def ge(n, k, p):
    p = Fraction(p); return sum(comb(n, i) * p**i * (1 - p)**(n - i) for i in range(k, n + 1))
def le(n, k, p):
    p = Fraction(p); return sum(comb(n, i) * p**i * (1 - p)**(n - i) for i in range(0, k + 1))
print("\nPART 3")
for p in ["0.95", "0.90", "0.85", "0.80", "0.70"]:
    v = ge(12, 10, p); print(f"  P(X>=10 | Bin(12,{p})) = {float(v):.3f}  ({float(v):.6f})")
for q in ["0", "0.05", "0.10", "0.20"]:
    v = le(12, 2, q); print(f"  P(X<=2  | Bin(12,{q})) = {float(v):.3f}  ({float(v):.6f})")
print(f"  488/180 = {488/180:.1f}  ({488/180:.4f})")
