import json, re, sys, os
from collections import defaultdict, Counter
from scipy.stats import binom
import numpy as np

D = sys.argv[1]
cle = json.load(open(os.path.join(D, "cle_pr60.json")))
conds = cle["conditions"]
carres = cle["carres"]
lect = cle["lecteurs"]
print("conditions:", conds)
print("n tiles:", len(carres), Counter(c["zone"] for c in carres))

# 1. parse
pat = re.compile(r"^\s*(\d+)\s*:\s*(yes|no)\b", re.I)
readings = []  # (reader, tile, cond, yes)
pair_count = Counter()
for r in sorted(lect):
    path = os.path.join(D, f"reponse_{r}.txt")
    lines = [l for l in open(path, encoding="utf-8").read().splitlines() if l.strip()]
    ans = {}
    bad = []
    for l in lines:
        m = pat.match(l)
        if m:
            n = int(m.group(1))
            if n in ans: bad.append("dup " + l)
            ans[n] = m.group(2).lower() == "yes"
        else:
            bad.append(l)
    missing = [n for n in range(1, 69) if n not in ans]
    extra = [n for n in ans if not (1 <= n <= 68)]
    print(f"reader {r}: lines={len(lines)} parsed={len(ans)} missing={missing} extra={extra} bad={bad[:3]}")
    for n in range(1, 69):
        if n not in ans: continue
        t, c = lect[r][str(n)]
        readings.append((r, t, c, ans[n]))
        pair_count[(t, c)] += 1
print("total readings:", len(readings))
print("pairs distinct:", len(pair_count), "min", min(pair_count.values()), "max", max(pair_count.values()))

fwd = [i for i, (m, o) in enumerate(conds) if o == "direct"]
rev = [i for i, (m, o) in enumerate(conds) if o == "inverse"]

def tally(cf, cr):
    Yf = defaultdict(int); Nf = defaultdict(int); Yr = defaultdict(int); Nr = defaultdict(int)
    for r, t, c, y in readings:
        if c in cf: Nf[t] += 1; Yf[t] += y
        elif c in cr: Nr[t] += 1; Yr[t] += y
    return Yf, Nf, Yr, Nr

def pval(d, n, bf, br):
    # P(X - Y >= d), X~Bin(n,bf), Y~Bin(n,br)
    k = np.arange(n + 1)
    px = binom.pmf(k, n, bf); py = binom.pmf(k, n, br)
    s = 0.0
    for x in k:
        for y in k:
            if x - y >= d: s += px[x] * py[y]
    return min(s, 1.0)

def holm(ps):
    m = len(ps); order = sorted(range(m), key=lambda i: ps[i])
    adj = [0.0] * m; run = 0.0
    for rank, i in enumerate(order):
        run = max(run, (m - rank) * ps[i]); adj[i] = min(run, 1.0)
    return adj

def analysis(cf, cr, n, label):
    print(f"\n===== {label}: forward conds {cf}, reverse conds {cr}, binomial size {n}")
    Yf, Nf, Yr, Nr = tally(cf, cr)
    t08 = [i for i, c in enumerate(carres) if c["zone"] == "0800"]
    sYf = sum(Yf[t] for t in t08); sNf = sum(Nf[t] for t in t08)
    sYr = sum(Yr[t] for t in t08); sNr = sum(Nr[t] for t in t08)
    bf = sYf / sNf; br = sYr / sNr
    print(f"bf = {sYf}/{sNf} = {bf:.6f}   br = {sYr}/{sNr} = {br:.6f}")
    nf_set = Counter(Nf[t] for t in t08); nr_set = Counter(Nr[t] for t in t08)
    print("0800 per-tile forward readings counts:", dict(nf_set), "reverse:", dict(nr_set))
    ps = [pval(Yf[t] - Yr[t], n, bf, br) for t in t08]
    adj = holm(ps)
    sig = [(t, Yf[t], Yr[t], ps[j], adj[j]) for j, t in enumerate(t08) if adj[j] <= 0.05]
    print("0800 tiles adj p <= 0.05:", len(sig))
    for s in sig: print(f"  tile {s[0]}: Yf={s[1]} Yr={s[2]} raw p={s[3]:.3e} adj p={s[4]:.3e}")
    best = sorted(range(len(t08)), key=lambda j: ps[j])[:5]
    print("  5 smallest raw p (0800):", [(t08[j], Yf[t08[j]], Yr[t08[j]], f"{ps[j]:.3e}", f"{adj[j]:.3e}") for j in best])
    gate = [i for i, c in enumerate(carres) if c["zone"] == "erwin" and c.get("lettres")]
    gp = [pval(Yf[t] - Yr[t], n, bf, br) for t in gate]
    gadj = holm(gp)
    print(f"gate: {len(gate)} erwin letter tiles")
    for j, t in enumerate(gate):
        print(f"  tile {t} lettres={carres[t]['lettres']}: Yf={Yf[t]}/{Nf[t]} Yr={Yr[t]}/{Nr[t]} raw p={gp[j]:.3e} adj p={gadj[j]:.3e}")
    print("  gate passes (adj<=0.05):", sum(a <= 0.05 for a in gadj), "/", len(gate))
    return Yf, Nf, Yr, Nr

Yf, Nf, Yr, Nr = analysis(fwd, rev, 24, "POOLED")

print("\n===== per-tile Yf/Nf Yr/Nr (pooled)")
for i, c in enumerate(carres):
    print(f"tile {i:2d} {c['zone']:5s} lettres={c.get('lettres')}: Yf={Yf[i]}/{Nf[i]} Yr={Yr[i]}/{Nr[i]}")

print("\n===== yes per condition by group")
groups = {
    "erwin with letters": [i for i, c in enumerate(carres) if c["zone"] == "erwin" and c.get("lettres")],
    "erwin without letters": [i for i, c in enumerate(carres) if c["zone"] == "erwin" and not c.get("lettres")],
    "0009B all": [i for i, c in enumerate(carres) if c["zone"] == "0009B"],
    "0800 all": [i for i, c in enumerate(carres) if c["zone"] == "0800"],
}
for g, ts in groups.items():
    ts = set(ts)
    row = []
    for ci, cd in enumerate(conds):
        y = sum(v for r, t, c, v in readings if c == ci and t in ts)
        n = sum(1 for r, t, c, v in readings if c == ci and t in ts)
        row.append(f"{cd[0]}-{cd[1]}: {y}/{n}")
    print(f"{g} ({len(ts)} tiles): " + " | ".join(row))

maps = sorted(set(m for m, o in conds), key=lambda m: [x[0] for x in conds].index(m))
for mp in maps:
    cf = [i for i, (m, o) in enumerate(conds) if m == mp and o == "direct"]
    cr = [i for i, (m, o) in enumerate(conds) if m == mp and o == "inverse"]
    analysis(cf, cr, 6, f"MAP {mp}")
