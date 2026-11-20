from fractions import Fraction
from math import comb
import numpy as np, itertools

n=48; p=Fraction(1,24)
def tail(k): return sum(Fraction(comb(n,j))*p**j*(1-p)**(n-j) for j in range(k,n+1))
for k in (5,6):
    t=tail(k); print(f"P(X>={k}) = {float(t):.6f}  (exact fraction denominator 24^48)")
thr=Fraction(5,100)/3
kmin=next(k for k in range(n+1) if tail(k)<thr)
print("threshold",float(thr),"smallest k:",kmin, float(tail(kmin)), "k-1:",float(tail(kmin-1)))

SEED=20261120; NSIM=4000
rng=np.random.default_rng(SEED)
signs=np.array(list(itertools.product([1,-1],repeat=12)),dtype=np.int32)  # 4096x12
def logit(x): return np.log(x/(1-x))
def sig(x): return 1/(1+np.exp(-x))
def power(pA,pB,k):
    u=rng.standard_normal((NSIM,12))
    a=rng.binomial(k,sig(logit(pA)+u)); b=rng.binomial(k,sig(logit(pB)+u))
    d=(a-b).astype(np.int32); S=d.sum(1)
    sums=np.abs(d)@signs.T
    pv=(sums>=S[:,None]).mean(1)
    return np.mean((S>0)&(pv<0.05))
for k in (2,4,6):
    for pB in (0.05,0.15,0.30):
        i=1; res=None
        while True:
            pA=round(pB+0.05*i,2)
            if pA>=1: break
            pw=power(pA,pB,k)
            if pw>=0.80: res=(pA,pw); break
            i+=1
        print(f"k={k} pB={pB:.2f} -> smallest pA={res[0] if res else None} power={res[1] if res else None}")
