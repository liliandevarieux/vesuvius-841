# PR-62 : contrôle des 162 cartes Reader V3 (deux sens) des 81 autres surfaces : forme du masque, valeurs finies, > 0 sur plus de la moitié du masque.
import glob, numpy as np, tifffile, zarr
H='/home/slusarska_holding/vesuvius/'
mal=0
for l in open(H+'c0800_surfaces_ext.tsv').read().split('\n'):
    if not l.strip(): continue
    m=l.split('\t')[0]
    z=glob.glob(H+'c0800/atlas/%s/surface-volumes/*.zarr'%m)[0]
    S=np.asarray(zarr.open(z,mode='r')['0'][15])>0
    for s in ('reader-v3','reader-v3_reverse'):
        a=tifffile.imread(H+'c0800/cartes_ext/%s_%s.tif'%(m,s))
        ok=a.shape==S.shape and np.isfinite(a).all() and (a[S]>0).mean()>0.5
        mal+= not ok
        if not ok: print('PROBLEME',m,s,a.shape,S.shape,(a[S]>0).mean() if a.shape==S.shape else '-')
print('cartes verifiees : 162, problemes :',mal)
