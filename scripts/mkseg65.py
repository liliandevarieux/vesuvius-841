# Construit, pour un segment de l open-data, un jeu de donnees au format du pipeline villa : volume 65 couches en ordre
# INVERSE (sens etabli le 23/09), labels et masque de supervision des organisateurs, meta.json. Seule la zone inspectee est
# ecrite (le reste des chunks reste absent, fill_value 0). usage: mkseg65.py <source_locale> <dossier_labels> <nom_cible>
import sys, os, json, shutil, numpy as np, zarr
from numcodecs import Blosc
src_loc, lab, dst = sys.argv[1], sys.argv[2], sys.argv[3]
H='/home/slusarska_holding/vesuvius'; R=f'{H}/ink-dataset/841'
S=zarr.open(f'{R}/{src_loc}/{src_loc}.zarr/0', mode='r'); Z,HH,WW=S.shape
# La tranche n est plus supposee : ZC vient d une mesure (balayage run4_queue15). FULL=1 prend toute la
# profondeur ramenee a 65 couches par interpolation. Par defaut, l ancien comportement (milieu de la pile).
FULL = os.environ.get('FULL', '0') == '1'
zc = int(os.environ.get('ZC', Z // 2))
if FULL:
    z0, z1 = 0, Z
    fz = np.linspace(0, Z - 1, 65); lo = np.floor(fz).astype(int)
    hi = np.minimum(lo + 1, Z - 1); wz = (fz - lo)[:, None, None]
    print(f'{dst} : source {S.shape} -> toute la profondeur ramenee a 65 couches, inversees')
else:
    z0 = max(0, min(Z - 65, zc - 32)); z1 = z0 + 65
    print(f'{dst} : source {S.shape} -> 65 couches {z0}-{z1} (centre {zc}), inversees')
D=f'{R}/{dst}'; os.makedirs(D, exist_ok=True)
attrs=json.load(open(f'{R}/{src_loc}/{src_loc}.zarr/.zattrs'))
cz=Blosc(cname='zstd', clevel=3, shuffle=2)
def grp(name, comp, sep):
    g=zarr.open_group(f'{D}/{name}.zarr', mode='w', zarr_format=2); g.attrs.update(attrs)
    for n in range(6):
        g.create_array(str(n), shape=(65, -(-HH//2**n), -(-WW//2**n)), chunks=(65,128,128), dtype='uint8',
                       compressors=comp, chunk_key_encoding={'name':'v2','separator':sep}, fill_value=0)
    return g
# --- volume : seulement les chunks de la zone inspectee ---
gv=grp(dst, None, '.')
ch=[tuple(map(int,l.split())) for l in open(f'/home/slusarska_holding/chunks_{src_loc}sup.txt') if l.strip()]
present=0
for n,(a,b) in enumerate(ch):
    y0,x0=a*128,b*128; y1,x1=min(y0+128,HH),min(x0+128,WW)
    blk=np.asarray(S[z0:z1, y0:y1, x0:x1])
    if blk.max()==0: continue
    if FULL: blk=(blk[lo]*(1-wz)+blk[hi]*wz).astype(np.uint8)
    gv['0'][:, y0:y1, x0:x1]=blk[::-1]; present+=1
    if n%200==0: print(f'  volume {n}/{len(ch)}', flush=True)
print(f'  volume : {present} chunks ecrits')
# --- labels et masque de supervision, diffuses sur les 65 couches ---
C=f'{R}/canon_autres/{lab}'
for nom,zsrc in ((f'{dst}_inklabels_v2','inklabels'),(f'{dst}_supervision_mask_v2','supervision')):
    g=grp(nom, cz, '/')
    A=np.asarray(zarr.open(f'{C}/{zsrc}.zarr',mode='r')['0'][:])>0
    A=A[:HH,:WW]
    for y in range(0,HH,128):
        b=A[y:y+128]
        if not b.any(): continue
        g['0'][:, y:y+b.shape[0], :b.shape[1]]=np.broadcast_to(b[None]*np.uint8(255),(65,)+b.shape)
    cur=A
    for n in range(1,6):
        h,w=cur.shape[0]//2,cur.shape[1]//2
        cur=cur[:2*h,:2*w].reshape(h,2,w,2).max(axis=(1,3))
        for y in range(0,h,128):
            bb=cur[y:y+128]
            if not bb.any(): continue
            g[str(n)][:, y:y+bb.shape[0], :bb.shape[1]]=np.broadcast_to(bb[None]*np.uint8(255),(65,)+bb.shape)
    print(f'  {nom} : {100*A.mean():.2f} % de la surface')
# --- meta.json et tifxyz ---
shutil.copy(f'{C}/tifxyz/meta.json', f'{D}/meta.json')
for c in 'xyz':
    p=f'{C}/tifxyz/{c}.tif'
    if os.path.exists(p): shutil.copy(p, f'{D}/{c}.tif')
print(f'{D} pret')
