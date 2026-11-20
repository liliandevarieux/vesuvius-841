# Capacite du test PR-58 : 12 lettres, 3 cartes, carre latin -> k lectures par (lettre, carte) = lecteurs/3.
# Test : permutation exacte des signes par lettre (2^12 combinaisons), unilateral, alpha 0,05 ; effet aleatoire par lettre
# (logit normal, ecart-type 1). Puissance = part des 2000 simulations ou le test tient.
import numpy as np, itertools
rng=np.random.default_rng(58)
L=12; signes=np.array(list(itertools.product([-1,1],repeat=L)))
def p_exact(d):
    S=d.sum(); return ((signes*d).sum(1)>=S).mean()
lg=lambda p:np.log(p/(1-p)); ex=lambda x:1/(1+np.exp(-x))
for lect in (6,12,18):
    k=lect//3
    for pb in (0.05,0.15,0.30):
        res=[]
        for pa in np.arange(pb+0.05,0.96,0.05):
            ok=0
            for _ in range(2000):
                u=rng.normal(0,1,L); a=rng.binomial(k,ex(lg(pa)+u)); b=rng.binomial(k,ex(lg(pb)+u))
                d=a-b
                ok+= (d.sum()>0) and p_exact(d)<0.05
            res.append((round(pa,2),ok/2000))
            if ok/2000>=0.8: break
        print('lecteurs %2d (k=%d) carte B a %.2f : plus petite carte A detectee 8 fois sur 10 = %s'%(lect,k,pb,res[-1]))
