# Page de lecture d un segment : une prediction au 1/8 (QUI= nomme son auteur dans le titre) (une lettre y fait ~125 px, donc tout le feuillet tient
# en une image lisible), avec les labels existants en rouge et l angle des lignes mesure puis redresse.
# usage: page_lecture.py <dossier_labels> <nom_court>
import sys, os, numpy as np, zarr, tifffile
from PIL import Image, ImageDraw
from scipy import ndimage
lab, court = sys.argv[1], sys.argv[2]
H='/home/slusarska_holding/vesuvius'; D=f'{H}/ink-dataset/841/canon_autres/{lab}'
# PRED permet de lire NOTRE prediction au lieu de celle des organisateurs ; SUF distingue la sortie
P=tifffile.imread(os.environ.get('PRED', f'{D}/pred.tif'))[::8,::8].astype(np.float32)
L=np.asarray(zarr.open(f'{D}/inklabels.zarr',mode='r')['3'][:])>0
V=np.asarray(zarr.open(f'{D}/validation.zarr',mode='r')['3'][:])>0
n=[min(x.shape[0] for x in (P,L,V)),min(x.shape[1] for x in (P,L,V))]; P,L,V=[x[:n[0],:n[1]] for x in (P,L,V)]
T=float(np.percentile(P[V],97))
B=(P>=T)&V
# angle des lignes : celui qui range l encre sure en bandes (profil de projection le plus contraste)
def force(a):
    r=ndimage.rotate(B.astype(np.float32),a,order=1,reshape=True,cval=0); p=r.sum(1)
    nz=np.nonzero(p>0.01*p.max())[0]
    if len(nz)<50: return 0.0
    q=p[nz[0]:nz[-1]+1]; q=q-ndimage.uniform_filter1d(q,40)
    return float((q**2).mean()/max(p.mean()**2,1e-9))
gr=np.arange(-40,40.1,2.0); sc=[force(a) for a in gr]; a0=gr[int(np.argmax(sc))]
fi=np.arange(a0-2,a0+2.01,0.5); sf=[force(a) for a in fi]; ANG=float(fi[int(np.argmax(sf))])
# ANGLE= force l angle : la mesure automatique se fait piéger quand la prediction ne couvre qu une
# petite part de la toile (elle accroche les bords des paves d inference).
if os.environ.get('ANGLE'): ANG=float(os.environ['ANGLE']); sf=[1.0]; sc=[1.0]
print(f'{court} : seuil {T:.0f} ; angle des lignes {ANG:+.1f} deg (force {max(sf)/max(np.median(sc),1e-12):.1f}x)')
g=np.clip(P,0,255).astype(np.uint8); rgb=np.stack([g,g,g],-1)
e=L&~ndimage.binary_erosion(L,iterations=2); rgb[e]=(255,60,60)
rgb[~V]=(0,0,0)
r=ndimage.rotate(rgb,ANG,order=1,reshape=True,cval=0).astype(np.uint8)
im=Image.fromarray(r)
out=Image.new('RGB',(im.width,im.height+34),(15,15,15)); out.paste(im,(0,30)); dr=ImageDraw.Draw(out)
QUI=os.environ.get('QUI','des organisateurs')
dr.text((6,8),f'{court} — feuillet entier, prediction {QUI} au 1/8, redresse de {ANG:+.1f} deg ; rouge = deja labellise ; 1 px = 19 um, une lettre fait ~125 px',fill=(255,255,0))
o=f'/mnt/c/Users/SLUSARSKA HOLDING/vesuvius/images/841_segments/2026-09-23_page_{court}{os.environ.get("SUF","")}.png'
out.save(o); print('page',o,out.size)
