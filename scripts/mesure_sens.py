# Couches directes contre couches inversees sur un segment de l open-data, mesure contre les labels des organisateurs.
# usage: mesure_sens.py <nom_local> <dossier_labels>    (ex. mesure_sens.py segA auto_grown_20260220144552896)
import sys, os, json, numpy as np, zarr, tifffile
from scipy import ndimage
loc, lab = sys.argv[1], sys.argv[2]
H='/home/slusarska_holding/vesuvius'; D=f'{H}/ink-dataset/841/canon_autres/{lab}'
L3=np.asarray(zarr.open(f'{D}/inklabels.zarr',mode='r')['3'][:])>0
S3=np.asarray(zarr.open(f'{D}/supervision.zarr',mode='r')['3'][:])>0
P3=tifffile.imread(f'{D}/pred.tif')[::8,::8].astype(np.float32)
wins=[tuple(map(int,l.split())) for l in open(f'/home/slusarska_holding/fenetres_{loc}.txt')]
def mes(k,suf):
    a=tifffile.imread(f'{H}/predictions/{loc}_win{k}{suf}_human7n.tif').astype(np.float32)[::8,::8]
    Y0,Y1,X0,X1=wins[k-1]; i0,j0=Y0//8,X0//8
    L=L3[i0:i0+a.shape[0], j0:j0+a.shape[1]]; S=S3[i0:i0+a.shape[0], j0:j0+a.shape[1]]; P=P3[i0:i0+a.shape[0], j0:j0+a.shape[1]]
    m=[min(x.shape[0] for x in (a,L,S,P)),min(x.shape[1] for x in (a,L,S,P))]
    a,L,S,P=[x[:m[0],:m[1]] for x in (a,L,S,P)]
    f=S&~ndimage.binary_dilation(L,iterations=3)
    return a[L].mean(), a[f].mean(), np.corrcoef(a[S].ravel(),P[S].ravel())[0,1]
print(f'{loc} ({lab})')
print(f'{"fenetre":9s} | {"DIRECTES  encre    fond   ecart   corr":38s} | {"INVERSEES encre    fond   ecart   corr":38s}')
d,r=[],[]
for k in range(1,len(wins)+1):
    try: e1,f1,c1=mes(k,''); e2,f2,c2=mes(k,'r')
    except FileNotFoundError: print(f'{k:9d} | (pas encore infere)'); continue
    d.append((e1,f1,c1)); r.append((e2,f2,c2))
    print(f'{k:9d} | {e1:14.1f} {f1:7.1f} {e1-f1:7.1f} {c1:6.3f} | {e2:14.1f} {f2:7.1f} {e2-f2:7.1f} {c2:6.3f}')
if d:
    d=np.array(d); r=np.array(r)
    print(f'{"moyenne":>9s} | {d[:,0].mean():14.1f} {d[:,1].mean():7.1f} {d[:,0].mean()-d[:,1].mean():7.1f} {d[:,2].mean():6.3f} | {r[:,0].mean():14.1f} {r[:,1].mean():7.1f} {r[:,0].mean()-r[:,1].mean():7.1f} {r[:,2].mean():6.3f}')
    g=lambda a: a[:,0].mean()-a[:,1].mean()
    # Les chiffres publies doivent etre re-derivables : JSON=<chemin> ecrit la mesure brute,
    # que verify_claims.py confronte aux tables du depot public.
    if os.environ.get('JSON'):
        o={'segment':lab,'local':loc,'windows':[],
           'mean':{'direct':{'sep':round(float(g(d)),1),'corr':round(float(d[:,2].mean()),3)},
                   'reversed':{'sep':round(float(g(r)),1),'corr':round(float(r[:,2].mean()),3)}}}
        for k in range(len(d)):
            o['windows'].append({'window':k+1,
                'direct':{'sep':round(float(d[k,0]-d[k,1]),1),'corr':round(float(d[k,2]),3)},
                'reversed':{'sep':round(float(r[k,0]-r[k,1]),1),'corr':round(float(r[k,2]),3)}})
        json.dump(o, open(os.environ['JSON'],'w'), indent=1)
        print(f"JSON ecrit : {os.environ['JSON']}")
    print(f'\nverdict : sens {"INVERSE" if g(r)>g(d) else "DIRECT"} ; gain {abs(g(r)-g(d)):.1f} d ecart. Repere w00 : ecart 66-90, corr 0,62-0,79.')
