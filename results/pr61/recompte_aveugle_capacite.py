from fractions import Fraction as F
from math import comb

NF, NC = 3, 24
N = NF + NC

def fisher_p(rf, rc):
    k = rf + rc
    tot = comb(N, k)
    return sum(F(comb(NF, x) * comb(NC, k - x), tot) for x in range(rf, min(NF, k) + 1))

passing = [(rf, rc) for rf in range(NF + 1) for rc in range(NC + 1) if fisher_p(rf, rc) <= F(5, 100)]
print("Part 1a passing pairs (Rf, Rc, p):")
for rf, rc in passing:
    print(f"  ({rf},{rc})  p={float(fisher_p(rf, rc)):.5f}")

def binpmf(n, k, p):
    return comb(n, k) * p**k * (1 - p)**(n - k)

def ppass(rho, pi):
    rho, pi = F(rho), F(pi)
    return sum(binpmf(NF, rf, rho) * binpmf(NC, rc, pi) for rf, rc in passing)

print("\nPart 1b pass probability (rows rho, cols pi):")
pis = ["0", "0.05", "0.10", "0.20", "0.30"]
print("rho\\pi " + " ".join(f"{p:>6}" for p in pis))
for rho in ["0.5", "0.7", "0.9", "1.0"]:
    print(f"{rho:>6} " + " ".join(f"{float(ppass(rho, p)):6.2f}" for p in pis))

print("\nPart 1c rho = pi:")
for p in ["0.05", "0.10", "0.20", "0.30"]:
    print(f"  pi={p}: {float(ppass(p, p)):.3f}  ({float(ppass(p, p)):.6f})")

# Part 2
ns = [4, 0, 5, 1, 3, 8, 8, 0, 6, 0, 0, 0]
print("\nPart 2:")
for L in ["1.0", "0.8", "0.6", "0.4"]:
    Lf = F(L)
    hold = []
    for n in ns:
        q = min(F(1), F(n, 8) * Lf)
        hold.append(sum(binpmf(6, k, q) for k in range(4, 7)))
    # Poisson-binomial distribution
    dist = [F(1)]
    for h in hold:
        new = [F(0)] * (len(dist) + 1)
        for i, d in enumerate(dist):
            new[i] += d * (1 - h)
            new[i + 1] += d * h
        dist = new
    p3 = sum(dist[3:])
    exp = sum(hold)
    print(f"  L={L}: P(>=3 hold)={float(p3):.2f} ({float(p3):.5f})  E[hold]={float(exp):.2f} ({float(exp):.5f})")
    print("     per-letter hold probs:", [round(float(h), 4) for h in hold])
