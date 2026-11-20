import json, re, sys, itertools
from fractions import Fraction
from math import comb
from pathlib import Path

base = Path(sys.argv[1])
cle = json.loads((base / "cle_pr59.json").read_text(encoding="utf-8"))
arms = list(cle["cartes"].keys())
letters = sorted(cle["lettres"].keys(), key=int)

pat = re.compile(r"^\s*(\d+)\s*:\s*(.+?)\s*\(([^)]*)\)\s*$")
rows = []  # (reader, crop, letter_id, true, arm, answer)
checks = []
for r in range(1, 13):
    key = f"lecteur{r:02d}"
    ans = {}
    bad = []
    for line in (base / f"reponse_{r:02d}.txt").read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        m = pat.match(line)
        if not m:
            bad.append(line); continue
        n = m.group(1)
        if n in ans: bad.append("DUP " + line)
        ans[n] = m.group(2).strip()
    checks.append(f"reader {r:02d}: answers={len(ans)} crops={sorted(ans, key=int) == [str(i) for i in range(1,13)]} unparsed={bad}")
    armcount = {a: 0 for a in arms}
    for c in range(1, 13):
        lid, true, arm = cle[key][str(c)]
        assert cle["lettres"][str(lid)] == true, (key, c)
        armcount[arm] += 1
        rows.append((r, c, str(lid), true, arm, ans.get(str(c))))
    checks.append(f"reader {r:02d}: arm counts={armcount}")

def pupper(k, n, p=Fraction(1, 24)):
    return sum(comb(n, i) * p**i * (1 - p)**(n - i) for i in range(k, n + 1))

print("== 1. Per arm: correct k / n, P(X>=k), X~Bin(n,1/24)")
for a in arms:
    rs = [x for x in rows if x[4] == a]
    k = sum(1 for x in rs if x[5] == x[3])
    p = pupper(k, len(rs))
    print(f"{a}: {k}/{len(rs)}  P={float(p):.6g}  (exact {p.numerator}/{p.denominator})" if len(str(p.denominator)) < 80 else f"{a}: {k}/{len(rs)}  P={float(p):.6g}")

print("\n== 2. Per arm x letter_id: correct / readings")
cell = {}
for a in arms:
    parts = []
    for l in letters:
        rs = [x for x in rows if x[4] == a and x[2] == l]
        k = sum(1 for x in rs if x[5] == x[3])
        cell[(a, l)] = k
        parts.append(f"{l}({cle['lettres'][l]})={k}/{len(rs)}")
    print(f"{a}: " + "  ".join(parts))

print("\n== 3. Sign-permutation tests (one-sided, exact over 2^12)")
for A, B in [("v8in","readerv3"),("v8in","argusv3"),("readerv3","argusv3"),("readerv3","v8in"),("argusv3","v8in")]:
    d = [cell[(A,l)] - cell[(B,l)] for l in letters]
    S = sum(d)
    cnt = sum(1 for s in itertools.product((-1,1), repeat=12) if sum(si*di for si,di in zip(s,d)) >= S)
    print(f"({A}, {B}): d={d} S={S}  p={cnt}/4096 = {cnt/4096:.6f}")

print("\n== 4. Sanity checks")
for c in checks: print(c)
for a in arms:
    for l in letters:
        n = sum(1 for x in rows if x[4] == a and x[2] == l)
        if n != 4: print(f"CELL ({l},{a}) has {n} readings")
print("cells with != 4 readings listed above (none if empty); total cells:", len(arms)*len(letters))
print("total readings:", len(rows), " missing answers:", sum(1 for x in rows if x[5] is None))

print("\n== 5. Answer multisets per (letter_id, arm) cell")
from collections import Counter
for l in letters:
    for a in arms:
        c = Counter(x[5] for x in rows if x[4] == a and x[2] == l)
        s = ", ".join(f"{k}: {v}" for k, v in sorted(c.items(), key=lambda kv: (-kv[1], kv[0])))
        print(f"letter {l} ({cle['lettres'][l]}), {a}: {{{s}}}")
