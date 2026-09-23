# Prepare le test d orientation d un segment de l open-data : choisit les 3 fenetres les plus encrees de la zone inspectee et
# ecrit la liste des chunks du volume de surface a telecharger. usage: prep_seg.py <nom_local> <prefixe_s3_du_segment>
import sys, os, json, urllib.request, numpy as np, zarr
from scipy import ndimage
loc, s3 = sys.argv[1], sys.argv[2]
H='/home/slusarska_holding/vesuvius'; B='https://vesuvius-challenge-open-data.s3.us-east-1.amazonaws.com'
V=f'PHerc0841/segments/{s3}/surface-volumes/2.403um-0.22m-77keV-volume-20260319124803.zarr'
za=json.loads(urllib.request.urlopen(f'{B}/{V}/0/.zarray').read())
Z,HH,WW=za['shape']; cz,cy,cx=za['chunks']
print(f'{loc} : volume {za["shape"]}, chunks {za["chunks"]}, {-(-HH//cy)*-(-WW//cx)} chunks au total')
D=f'{H}/ink-dataset/841/canon_autres/{s3.split("-",1)[1]}'
L=np.asarray(zarr.open(f'{D}/inklabels.zarr',mode='r')['3'][:])>0
S=np.asarray(zarr.open(f'{D}/supervision.zarr',mode='r')['3'][:])>0
W=1500//8; dens=ndimage.uniform_filter(L.astype(np.float32),W)
d=dens.copy(); d[~ndimage.binary_erosion(S,iterations=W//2)]=0
pris=[]
for k in range(3):
    i,j=np.unravel_index(np.argmax(d),d.shape)
    if d[i,j]<=0: break
    pris.append((max(0,(i-W//2))*8, max(0,(j-W//2))*8, float(dens[i,j])))
    d[max(0,i-W):i+W, max(0,j-W):j+W]=0
ch=set()
for Y0,X0,f in pris:
    print(f'  fenetre : Y {Y0}-{Y0+1500} X {X0}-{X0+1500}, encre {100*f:.0f} %')
    for a in range((Y0-128)//cy, (Y0+1500+128)//cy+1):
        for b in range((X0-128)//cx, (X0+1500+128)//cx+1):
            if 0<=a<-(-HH//cy) and 0<=b<-(-WW//cx): ch.add((a,b))
open(f'/home/slusarska_holding/chunks_{loc}.txt','w').write('\n'.join(f'{a} {b}' for a,b in sorted(ch))+'\n')
open(f'/home/slusarska_holding/fenetres_{loc}.txt','w').write('\n'.join(f'{Y0} {Y0+1500} {X0} {X0+1500}' for Y0,X0,_ in pris)+'\n')
open(f'/home/slusarska_holding/s3_{loc}.txt','w').write(f'{V}\n{Z}\n')
print(f'  {len(ch)} chunks a telecharger ({len(ch)*cz*cy*cx/1048576:.0f} Mo), {Z} couches')
