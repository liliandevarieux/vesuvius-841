# Liste les chunks du volume couvrant la ZONE INSPECTEE d un segment (+1 chunk de marge) : c est tout ce qu il faut pour
# entrainer dessus (le pipeline n entraine que sur des patchs contenant du label). usage: prep_sup.py <nom_local> <dossier_labels> <prefixe_s3>
import sys, json, urllib.request, numpy as np, zarr
from scipy import ndimage
loc, lab, s3 = sys.argv[1], sys.argv[2], sys.argv[3]
B='https://vesuvius-challenge-open-data.s3.us-east-1.amazonaws.com'
V=f'PHerc0841/segments/{s3}/surface-volumes/2.403um-0.22m-77keV-volume-20260319124803.zarr'
za=json.loads(urllib.request.urlopen(f'{B}/{V}/0/.zarray').read()); Z,HH,WW=za['shape']; cz,cy,cx=za['chunks']
D=f'/home/slusarska_holding/vesuvius/ink-dataset/841/canon_autres/{lab}'
S=np.asarray(zarr.open(f'{D}/supervision.zarr',mode='r')['3'][:])>0
S=ndimage.binary_dilation(S,iterations=2)                       # marge
ny,nx=-(-HH//cy),-(-WW//cx)
ch=set()
ii,jj=np.nonzero(S)
for a,b in zip(ii*8//cy, jj*8//cx):
    for da in (-1,0,1):
        for db in (-1,0,1):
            if 0<=a+da<ny and 0<=b+db<nx: ch.add((a+da,b+db))
open(f'/home/slusarska_holding/chunks_{loc}sup.txt','w').write('\n'.join(f'{a} {b}' for a,b in sorted(ch))+'\n')
open(f'/home/slusarska_holding/s3_{loc}sup.txt','w').write(f'{V}\n{Z} {HH} {WW}\n')
print(f'{loc} : volume {Z}x{HH}x{WW} ; zone inspectee = {len(ch)} chunks sur {ny*nx} ({len(ch)*cz*cy*cx/1073741824:.1f} Go)')
