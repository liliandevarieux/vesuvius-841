import numpy as np, tifffile, json
from PIL import Image, ImageDraw, ImageFont
D='/home/slusarska_holding/vesuvius/c343/'
F=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',34)
L=json.load(open(D+'reference_12_lettres.json'))
pan=[]
for m,t in [('readerv3','Reader V3'),('argusv3','Argus V3'),('ink9um_s43','ink_9um graine 43')]:
    a=tifffile.imread(D+'pr58/lecture_%s.tif'%m).astype(float)[400:1950,450:4900]
    v=a[a>0]; lo,hi=np.percentile(v,[1,99.5]); b=np.clip((a-lo)/(hi-lo)*255,0,255).astype(np.uint8)
    im=Image.fromarray(b).convert('RGB').resize((b.shape[1]//3,b.shape[0]//3)); d=ImageDraw.Draw(im)
    for l in L:
        x0,y0,x1,y1=l['zone']; d.text(((x0-450)//3,(y1-400)//3+4),'ΠΑΝΤΟΓΙΝΟΜΜΕ'[l['id']-1],fill=(0,220,0),font=F)
    d.text((10,8),t,fill=(255,200,0),font=F); pan.append(im)
W=pan[0].width; H=sum(p.height for p in pan)+20
out=Image.new('RGB',(W,H),(40,40,40)); y=0
for p in pan: out.paste(p,(0,y)); y+=p.height+10
out.save('/mnt/c/Users/SLUSARSKA HOLDING/vesuvius/images/2026-11-20_pr58_trois_cartes.png'); print(out.size)
