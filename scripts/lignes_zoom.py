# Les lignes de texte du segment B, coupees en moitiés pour que les lettres soient a taille reelle (~250 px).
import os, numpy as np, zarr, tifffile
from PIL import Image, ImageDraw
from scipy import ndimage
H='/home/slusarska_holding/vesuvius'; D=f'{H}/ink-dataset/841/canon_autres/auto_grown_20260220174252405'
ANG=8.0; R=4
P=tifffile.imread(os.environ.get('PRED', f'{D}/pred.tif'))[::R,::R].astype(np.float32)
L8=np.asarray(zarr.open(f'{D}/inklabels.zarr',mode='r')['3'][:])>0
V8=np.asarray(zarr.open(f'{D}/validation.zarr',mode='r')['3'][:])>0
up=lambda a: np.repeat(np.repeat(a,8//R,0),8//R,1)[:P.shape[0],:P.shape[1]]
L,V=up(L8),up(V8)
n=[min(P.shape[0],L.shape[0],V.shape[0]),min(P.shape[1],L.shape[1],V.shape[1])]; P,L,V=[x[:n[0],:n[1]] for x in (P,L,V)]
T=float(np.percentile(P[V],97))
g=np.clip(P,0,255).astype(np.uint8); rgb=np.stack([g,g,g],-1); rgb[~V]=(0,0,0)
e=L&~ndimage.binary_erosion(L,iterations=2); rgb[e]=(255,60,60)
rot=lambda a,o=1: ndimage.rotate(a,ANG,order=o,reshape=True,cval=0)
RGB=rot(rgb).astype(np.uint8); Bm=rot(((P>=T)&V).astype(np.float32))>0.5
prof=ndimage.uniform_filter1d(Bm.sum(1).astype(np.float32),25); dans=prof>0.35*prof.max()
bandes=[]; i=0
while i<len(dans):
    if dans[i]:
        j=i
        while j<len(dans) and dans[j]: j+=1
        if j-i>90: bandes.append((i,j))
        i=j
    else: i+=1
W=1760; morceaux=[]
for k,(a,b) in enumerate(bandes,1):
    m=int(0.30*(b-a)); y0,y1=max(0,a-m),min(RGB.shape[0],b+m)
    col=Bm[y0:y1].sum(0); nz=np.nonzero(col>0)[0]
    x0,x1=max(0,nz[0]-40),min(RGB.shape[1],nz[-1]+40)
    larg=x1-x0; nmor=max(1,int(np.ceil(larg/2100)))
    pas=int(np.ceil(larg/nmor))
    for p in range(nmor):
        xa,xb=x0+p*pas,min(x1,x0+(p+1)*pas)
        morceaux.append((f'ligne {k}' + (f' — partie {p+1}/{nmor}' if nmor>1 else ''), Image.fromarray(RGB[y0:y1,xa:xb])))
tot=sum(int(im.height*W/im.width)+32 for _,im in morceaux)+30
out=Image.new('RGB',(W,tot),(12,12,12)); dr=ImageDraw.Draw(out); y=6
dr.text((6,6),'841, segment de la spire voisine — ROUGE = deja labellise par les humains ; blanc = encre vue par la prediction, non labellisee',fill=(255,255,0)); y=26
for t,im in morceaux:
    h=int(im.height*W/im.width); out.paste(im.resize((W,h)),(0,y+24)); dr.text((6,y+5),t,fill=(255,255,0)); y+=h+32
o='/mnt/c/Users/SLUSARSKA HOLDING/vesuvius/images/841_segments/2026-09-23_lignes_segB_zoom'+os.environ.get('SUF','')+'.png'
out.save(o); print('image',o,out.size,f'({len(morceaux)} morceaux)')
