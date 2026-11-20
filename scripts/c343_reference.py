# Reference des 12 lettres de 343 : traces verts des papyrologues (annonce du 08/10), recales dans la zone de lecture d'Erwin.
import numpy as np, json
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage
P='/mnt/c/Users/SLUSARSKA HOLDING/AppData/Local/Temp/claude/4203fc70abe36c49/ae02ffb6-78ce-4316-b98c-3d5acece68c1/scratchpad/post343/'
D='/home/slusarska_holding/vesuvius/c343/'
V=json.load(open(P+'verts.json')); sc,dx,dy=V['echelle'],V['dx'],V['dy']
post=np.asarray(Image.open(P+'lecture.png').convert('RGB')).astype(int); H=post.shape[0]//2; bas=post[H:]
g=(bas[...,1]>180)&(bas[...,0]<120)&(bas[...,2]<120); g=ndimage.binary_closing(g,iterations=3)
lab,n=ndimage.label(g)
comps=[c for c in V['composantes']]
def zone(x0,y0,x1,y1): return [round((x0-dx)/sc),round((y0-dy)/sc),round((x1-dx)/sc),round((y1-dy)/sc)]
# ordre de lecture : ligne du bas (principale) de gauche a droite, puis ligne du haut
bas_l=sorted([c for c in comps if c['y0']>300],key=lambda c:c['x0']); haut_l=sorted([c for c in comps if c['y0']<=300],key=lambda c:c['x0'])
noms_bas=[['pi'],['alpha','nu'],['tau','omicron'],['gamma'],['iota'],['nu'],['omicron'],['mu']]; noms_haut=[['mu'],['epsilon']]
L=[]
def coupe(c,noms,ligne):
    if len(noms)==1:
        L.append(dict(nom=noms[0],ligne=ligne,post=[c['x0'],c['y0'],c['x1'],c['y1']])); return
    sub=g[c['y0']:c['y1'],c['x0']:c['x1']]; prof=sub.sum(0); w=len(prof)
    k=w//4+int(np.argmin(prof[w//4:3*w//4])); xs=c['x0']+k
    print('coupure', noms, 'a x=%d (profil %d sur max %d)'%(xs,prof[k],prof.max()))
    for (a,b),nm in zip([(c['x0'],xs),(xs,c['x1'])],noms):
        ys=np.where(g[c['y0']:c['y1'],a:b].any(1))[0]
        L.append(dict(nom=nm,ligne=ligne,post=[a,c['y0']+int(ys.min()),b,c['y0']+int(ys.max())+1]))
for c,nm in zip(bas_l,noms_bas): coupe(c,nm,'principale')
for c,nm in zip(haut_l,noms_haut): coupe(c,nm,'haut')
for i,l in enumerate(L): l['id']=i+1; l['zone']=zone(*l['post'])
json.dump(L,open(D+'reference_12_lettres.json','w'),indent=1)
for l in L: print(l['id'],l['nom'],l['ligne'],l['zone'])
s=json.load(open(D+'erwin/outputs/concat_w047-w048_R5B2_z9500-11000.json')); dp=s['outputs']['image']['data_panel']
im=Image.open(D+'erwin/outputs/erwin.png').convert('RGB'); d=ImageDraw.Draw(im); F=ImageFont.load_default(size=60)
for l in L:
    x0,y0,x1,y1=l['zone']; d.rectangle([x0+dp['x'],y0+dp['y'],x1+dp['x'],y1+dp['y']],outline=(0,255,0),width=7); d.text((x0+dp['x'],y1+dp['y']+5),'%d %s'%(l['id'],l['nom']),fill=(0,255,255),font=F)
im.crop((dp['x'],dp['y']+300,dp['x']+dp['width'],dp['y']+2200)).resize((dp['width']//3,1900//3)).save(P+'ref12.png')
