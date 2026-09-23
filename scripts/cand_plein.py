# Recensement des lettres NON LABELLISEES sur toute la surface d un segment, avec DEUX lecteurs independants :
# la prediction publiee des organisateurs et la notre (human7n, entraine uniquement sur w00, qui n a jamais vu ce
# segment). Une candidate doit etre vue par les deux. Justification du second lecteur : sur ce segment, human7n fait
# 106,2 de separation contre 66-90 sur son propre terrain.
# usage: cand_plein.py <nom_local> <dossier_labels>   env AMIN=<px pleins, defaut = plus petite lettre labellisee>
import sys, os, numpy as np, zarr, tifffile
from scipy import ndimage
loc, lab = sys.argv[1], sys.argv[2]
H = '/home/slusarska_holding/vesuvius'; D = f'{H}/ink-dataset/841/canon_autres/{lab}'; R = 8
g = lambda k: np.asarray(zarr.open(f'{D}/{k}.zarr', mode='r')['3'][:]) > 0
L, S, V = g('inklabels'), g('supervision'), g('validation')
P = tifffile.imread(f'{D}/pred.tif')[::R, ::R].astype(np.float32)          # lecteur 1 : les organisateurs
A = tifffile.imread(f'{H}/predictions/{loc}_human7n_plein.tif')[::R, ::R].astype(np.float32)  # lecteur 2 : nous
n = [min(x.shape[0] for x in (L, S, V, P, A)), min(x.shape[1] for x in (L, S, V, P, A))]
L, S, V, P, A = [x[:n[0], :n[1]] for x in (L, S, V, P, A)]
vu = (A > 0) & V                                    # la ou notre lecteur a effectivement tourne
dens = L[S].mean()                                  # densite d encre de reference
T1 = float(np.percentile(P[S], 100 * (1 - dens)))
T2 = float(np.percentile(A[vu], 100 * (1 - dens)))
print(f'{loc} : surface lue par les deux lecteurs {vu.sum()*R*R/1e6:.0f} Mpx ; seuils {T1:.0f} (eux) / {T2:.0f} (nous)')
B = (P >= T1) & (A >= T2) & vu
print(f'accord des deux lecteurs sur {100*B[vu].mean():.2f} % de cette surface (densite de reference {100*dens:.2f} %)')
# Taille d une lettre : NE PAS la deduire des composantes de ces labels-ci. Sur segA et segB les labels des
# organisateurs sont soudes en 5 ou 6 blocs (un pave de texte = une composante), donc leur percentile donne la
# taille d un paragraphe et le recensement ne trouve rien. Reference prise sur w00, dont les labels sont separes :
# 219 composantes, aires 0,006 / 0,037 / 0,144 Mpx aux 10e, 50e et 90e centiles. Seuil par defaut : 0,04 Mpx.
lbl, nl = ndimage.label(L); al = ndimage.sum(L, lbl, range(1, nl + 1)) * R * R
AMIN = int(os.environ.get('AMIN', 40000))
Ld = ndimage.binary_dilation(L, iterations=25)      # 200 px de marge autour des labels
lb, nn = ndimage.label(B & ~Ld)
aire = ndimage.sum(B & ~Ld, lb, range(1, nn + 1)) * R * R
objs = ndimage.find_objects(lb)
ok = [k for k in np.argsort(aire)[::-1] if aire[k] >= AMIN]
print(f'{nn} taches hors labels ; {len(ok)} de taille de lettre (>= {AMIN/1e6:.2f} Mpx ; une lettre de w00 fait 0,04 Mpx en mediane)')
print(f'{"no":>3} {"aire Mpx":>9} | {"centre Y,X":>15} | {"eux":>6} {"nous":>6} | hors zone inspectee')
lignes = []
for i, k in enumerate(ok[:40], 1):
    m = (lb[objs[k]] == k + 1)
    cy = int((objs[k][0].start + objs[k][0].stop) / 2 * R); cx = int((objs[k][1].start + objs[k][1].stop) / 2 * R)
    hs = float((~S)[objs[k]][m].mean())
    print(f'{i:3d} {aire[k]/1e6:9.2f} | {cy:7d},{cx:7d} | {P[objs[k]][m].mean():6.0f} {A[objs[k]][m].mean():6.0f} | {100*hs:3.0f} %')
    lignes.append(f'{cy} {cx} {aire[k]:.0f} {hs:.2f}')
if nl: print(f'\nrepere : les lettres labellisees de ce segment font {al.min()/1e6:.2f} a {al.max()/1e6:.2f} Mpx')
open(f'/home/slusarska_holding/cand2_{loc}.txt', 'w').write('\n'.join(lignes) + '\n')
# fenetres de 640 px centrees sur les candidates, pour les planches et les piles Fiji
open(f'/home/slusarska_holding/fenetres_{loc}c2.txt', 'w').write('\n'.join(
    f'{max(0,int(l.split()[0])-320)} {max(0,int(l.split()[0])-320)+640} '
    f'{max(0,int(l.split()[1])-320)} {max(0,int(l.split()[1])-320)+640}' for l in lignes) + '\n')
print(f'ecrit : cand2_{loc}.txt et fenetres_{loc}c2.txt')
