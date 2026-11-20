import json, re, sys, itertools
from fractions import Fraction
from math import comb
from collections import defaultdict, Counter
D = sys.argv[1]
key = json.load(open(D+"/cle_pr58.json", encoding="utf-8"))
maps = list(key["cartes"].keys())
letters = {int(k): v for k, v in key["lettres"].items()}
GREEK = "alpha beta gamma delta epsilon zeta eta theta iota kappa lambda mu nu xi omicron pi rho sigma tau upsilon phi chi psi omega".split()
VALID = set(GREEK) | {"unreadable"}
readers = sorted(k for k in key if k.startswith("lecteur"))
print("readers:", readers, "maps:", maps)
rows = []  # (reader, crop, letter, correct, map, answer)
problems = []
for r in readers:
    num = r[-2:]
    lines = open(f"{D}/reponse_{num}.txt", encoding="utf-8").read().splitlines()
    ans = {}
    for ln in lines:
        m = re.match(r"\s*(\d+)\s*[:.)]\s*(.*)$", ln)
        if not m: continue
        n = int(m.group(1)); words = re.findall(r"[A-Za-z]+", m.group(2).lower())
        a = next((w for w in words if w in VALID), None)
        if n in ans: problems.append(f"{r} duplicate crop {n}")
        ans[n] = a
        if a is None: problems.append(f"{r} crop {n} no valid answer: {ln!r}")
    sheet = key[r]
    if len(sheet) != 12 or sorted(map(int, sheet)) != list(range(1,13)): problems.append(f"{r} sheet crops {sorted(sheet)}")
    if sorted(ans) != list(range(1,13)): problems.append(f"{r} answers crops {sorted(ans)}")
    lids = [v[0] for v in sheet.values()]
    if sorted(lids) != list(range(1,13)): problems.append(f"{r} letters {sorted(lids)}")
    for c, (lid, name, mp) in sheet.items():
        if letters[lid] != name: problems.append(f"{r} crop {c} name mismatch {name} vs {letters[lid]}")
        if mp not in maps: problems.append(f"{r} unknown map {mp}")
        rows.append((r, int(c), lid, name, mp, ans.get(int(c))))
print("total rows", len(rows))
pair = Counter((x[2], x[4]) for x in rows)
bad = {k: v for k, v in pair.items() if v != 4}
print("(letter,map) pairs:", len(pair), "with count!=4:", bad)
print("problems:", problems or "none")
p = Fraction(1, 24)
print("\n== per map ==")
for mp in maps:
    R = [x for x in rows if x[4] == mp]
    n = len(R); k = sum(x[5] == x[3] for x in R); u = sum(x[5] == "unreadable" for x in R)
    tail = sum(comb(n, i) * p**i * (1-p)**(n-i) for i in range(k, n+1))
    # agreement pairs
    agree = tot = 0
    for lid in range(1, 13):
        a = [x[5] for x in R if x[2] == lid]
        for i, j in itertools.combinations(range(len(a)), 2):
            tot += 1
            if a[i] == a[j] and a[i] != "unreadable": agree += 1
    print(f"{mp}: correct {k}/{n}, unreadable {u}, P(X>={k}) = {float(tail):.6g} (exact {tail.numerator}/{tail.denominator if len(str(tail.denominator))<40 else '...'}), identical non-unreadable pairs {agree}/{tot}")
print("\n== per letter ==")
cc = defaultdict(int); nn = defaultdict(int)
for x in rows:
    nn[(x[2], x[4])] += 1; cc[(x[2], x[4])] += x[5] == x[3]
print("id name " + " ".join(maps))
for lid in range(1, 13):
    print(lid, letters[lid], " ".join(f"{cc[(lid,m)]}/{nn[(lid,m)]}" for m in maps), "| answers:", {m: [x[5] for x in rows if x[2]==lid and x[4]==m] for m in maps})
print("\n== sign permutation ==")
for a, b in [("readerv3","argusv3"),("readerv3","ink9um_s43"),("argusv3","ink9um_s43")]:
    d = [cc[(l,a)] - cc[(l,b)] for l in range(1,13)]
    S = sum(d); cnt = 0
    for signs in itertools.product((1,-1), repeat=12):
        if sum(s*x for s, x in zip(signs, d)) >= S: cnt += 1
    print(f"{a}-{b}: d={d} S={S} p={cnt}/4096={cnt/4096:.6g}")
