import numpy as np, json
from PIL import Image
from scipy import ndimage
P='/mnt/c/Users/SLUSARSKA HOLDING/AppData/Local/Temp/claude/4203fc70abe36c49/ae02ffb6-78ce-4316-b98c-3d5acece68c1/scratchpad/post343/'
D='/home/slusarska_holding/vesuvius/c343/erwin/outputs/'
post=np.asarray(Image.open(P+'lecture.png').convert('RGB')).astype(float)
H=post.shape[0]//2
haut, bas = post[:H], post[H:]
# 1) recalage panneau haut de l'annonce -> panneau de donnees d'Erwin (echelle + decalage), sur la luminance
er=np.asarray(Image.open(D+'erwin.png').convert('L')).astype(float)
s=json.load(open(D+'concat_w047-w048_R5B2_z9500-11000.json')); dp=s['outputs']['image']['data_panel']
erp=er[dp['y']:dp['y']+dp['height'], dp['x']:dp['x']+dp['width']]
gm=(bas[...,1]>180)&(bas[...,0]<120)&(bas[...,2]<120)
hl=bas.mean(2).copy(); hl[ndimage.binary_dilation(gm,iterations=6)]=hl.mean()
print('panneau bas recale seul')
best=None
for sc in np.arange(0.340,0.362,0.001):
    small=np.asarray(Image.fromarray(erp.astype(np.uint8)).resize((round(erp.shape[1]*sc),round(erp.shape[0]*sc)),Image.BILINEAR)).astype(float)
    # correlation par FFT de hl (cible) avec small
    from scipy.signal import fftconvolve
    a=(hl-hl.mean())/hl.std(); b=(small-small.mean())/small.std()
    c=fftconvolve(a,b[::-1,::-1],mode='full')
    k=np.unravel_index(c.argmax(),c.shape); val=c[k]/b.size
    dy=k[0]-(b.shape[0]-1); dx=k[1]-(b.shape[1]-1)
    if best is None or val>best[0]: best=(val,sc,dx,dy)
print('recalage: corr %.3f echelle %.4f dx %d dy %d'%best)
val,sc,dx,dy=best
# 2) traces verts du panneau bas
g=(bas[...,1]>180)&(bas[...,0]<120)&(bas[...,2]<120)
g=ndimage.binary_closing(g,iterations=3)
lab,n=ndimage.label(g); objs=ndimage.find_objects(lab)
comps=[]
for i,o in enumerate(objs):
    area=(lab[o]==i+1).sum()
    if area<300: continue
    y0,y1,x0,x1=o[0].start,o[0].stop,o[1].start,o[1].stop
    comps.append(dict(x0=x0,y0=y0,x1=x1,y1=y1,aire=int(area)))
comps.sort(key=lambda c:(c['y0']>H*0.5 and 0 or 1, c['x0']))
for c in sorted(comps,key=lambda c:c['x0']):
    # coordonnees zone de lecture d'Erwin : (post - decalage)/echelle
    c['zone']=[int(v) for v in [round((c['x0']-dx)/sc),round((c['y0']-dy)/sc),round((c['x1']-dx)/sc),round((c['y1']-dy)/sc)]]
    print(c)
json.dump(dict(echelle=float(sc),dx=int(dx),dy=int(dy),corr=float(val),composantes=comps),open(P+'verts.json','w'),indent=1)
m=Image.fromarray((g*255).astype(np.uint8)); m.save(P+'verts_masque.png')
