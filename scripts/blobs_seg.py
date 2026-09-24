# Recherche de lettres NON LABELLISEES sur un segment de l open-data, a partir de la prediction publiee par les organisateurs
# (deja sur le disque, aucun GPU) : taches connexes de taille de lettre hors du masque des labels, comme la nuit du 22 au 23/09
# sur w00. usage: blobs_seg.py <dossier_labels>    env AMIN=300000 (px pleins) SEUIL=<0-255, defaut : seuil a aire egale>
import sys, os, numpy as np, zarr, tifffile
from scipy import ndimage
lab=sys.argv[1]; H='/home/slusarska_holding/vesuvius'; D=f'{H}/ink-dataset/841/canon_autres/{lab}'
AMIN=int(os.environ.get('AMIN',300000)); R=8
L=np.asarray(zarr.open(f'{D}/inklabels.zarr',mode='r')['3'][:])>0
S=np.asarray(zarr.open(f'{D}/supervision.zarr',mode='r')['3'][:])>0
V=np.asarray(zarr.open(f'{D}/validation.zarr',mode='r')['3'][:])>0      # la feuille
P=tifffile.imread(f'{D}/pred.tif')[::R,::R].astype(np.float32)
n=[min(x.shape[0] for x in (L,S,V,P)),min(x.shape[1] for x in (L,S,V,P))]; L,S,V,P=[x[:n[0],:n[1]] for x in (L,S,V,P)]
T=float(os.environ['SEUIL']) if os.environ.get('SEUIL') else float(np.percentile(P[S],100*(1-L[S].mean())))
B=(P>=T)&V
print(f'{lab} : seuil {T:.0f} ; encre sure {100*B.mean():.2f} % de la feuille ; labels {100*L.mean():.2f} %')
Ld=ndimage.binary_dilation(L,iterations=25)
lb,nn=ndimage.label(B); aire=ndimage.sum(B,lb,range(1,nn+1))*R*R; objs=ndimage.find_objects(lb)
print(f'{nn} taches ; {(aire>=AMIN).sum()} de taille de lettre (>= {AMIN/1e6:.2f} Mpx)')
dedans=[];dehors=[]
for k in np.argsort(aire)[::-1]:
    if aire[k]<AMIN: break
    m=(lb[objs[k]]==k+1); rec=float(Ld[objs[k]][m].mean())
    cy,cx=int((objs[k][0].start+objs[k][0].stop)/2*R),int((objs[k][1].start+objs[k][1].stop)/2*R)
    hors_sup=float((~S)[objs[k]][m].mean())
    (dedans if rec>=0.5 else dehors).append((aire[k],cy,cx,rec,hors_sup))
print(f'\n{len(dedans)} deja labellisees ; {len(dehors)} HORS labels :')
print(f'{"aire Mpx":>9} | {"centre Y,X":>15} | {"dans les labels":>15} | hors zone inspectee')
for a,cy,cx,rec,hs in dehors[:20]:
    print(f'{a/1e6:9.2f} | {cy:7d},{cx:7d} | {100*rec:14.0f} % | {100*hs:3.0f} %')
if dedans:
    ad=np.array([d[0] for d in dedans]); print(f'\nrepere : les lettres labellisees de ce segment font {ad.min()/1e6:.2f} a {ad.max()/1e6:.2f} Mpx')
open(f'/home/slusarska_holding/cand_{lab}.txt','w').write('\n'.join(f'{cy} {cx} {a:.0f}' for a,cy,cx,_,_ in dehors)+'\n')
