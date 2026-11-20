# Contrôle 343 (PR-58) : ramène une carte posée sur le maillage final des organisateurs (2660 x 6780) dans le repère de
# lecture d'Erwin (zone de lecture de son image, 5641 x 2455), par la géométrie 3D, sans regarder la carte.
#   repère de lecture (zone) -> lecture plein cadre : x + 699, y + 0 (sidecar d'Erwin, area.reading_px)
#   lecture -> rendu brut d'Erwin : col = 6720 - x, ligne = 2560 - y (flip_lr et flip_ud du sidecar)
#   rendu brut -> noeud de son tifxyz : / 20 (scale 0,05), interpolation bilinéaire de x, y, z
#   point 3D -> noeud du tifxyz final des organisateurs : plus proche noeud puis Gauss-Newton sur la bilinéaire
# Le champ de correspondance est calculé sur la grille des noeuds d'Erwin, puis interpolé aux pixels.
# usage : c343_recale.py champ            -> champ.npz + contrôle (écart 3D, sens de la transformation)
#         c343_recale.py carte F.tif OUT  -> carte F rééchantillonnée dans la zone de lecture (uint8, 0 hors maillage)
import sys, json, numpy as np, tifffile
from scipy import ndimage
from scipy.spatial import cKDTree

D = '/home/slusarska_holding/vesuvius/c343/'
ZX0, RW, RH = 699, 6720, 2560        # décalage de la zone ; taille du rendu brut d'Erwin
ZW, ZH = 5641, 2455                  # taille de la zone de lecture


def xyz(dossier):
    return np.stack([tifffile.imread(dossier + c + '.tif').astype(np.float64) for c in 'xyz'], -1)


def bilin(G, r, c):
    r0 = np.clip(np.floor(r).astype(int), 0, G.shape[0] - 2); c0 = np.clip(np.floor(c).astype(int), 0, G.shape[1] - 2)
    fr = (r - r0)[..., None]; fc = (c - c0)[..., None]
    return (G[r0, c0] * (1 - fr) * (1 - fc) + G[r0 + 1, c0] * fr * (1 - fc)
            + G[r0, c0 + 1] * (1 - fr) * fc + G[r0 + 1, c0 + 1] * fr * fc)


def champ():
    E = xyz(D + 'erwin/tifxyz/'); T = xyz(D + 'equipe/mesh_final/')
    vE = (E > -0.5).all(-1); vT = (T > -0.5).all(-1)
    print('noeuds Erwin', E.shape[:2], vE.sum(), '| noeuds equipe', T.shape[:2], vT.sum())
    rT, cT = np.nonzero(vT); arbre = cKDTree(T[rT, cT])
    rE, cE = np.nonzero(vE); P = E[rE, cE]
    d0, k = arbre.query(P)
    r = rT[k].astype(float); c = cT[k].astype(float)
    Tf = np.where(vT[..., None], T, np.nan)
    for _ in range(8):                      # Gauss-Newton sur la position (r, c) dans la grille de l'équipe
        Q = bilin(Tf, r, c); h = 0.05
        Jr = (bilin(Tf, r + h, c) - bilin(Tf, r - h, c)) / (2 * h); Jc = (bilin(Tf, r, c + h) - bilin(Tf, r, c - h)) / (2 * h)
        J = np.stack([Jr, Jc], -1); res = P - Q
        ok = np.isfinite(J).all((1, 2)) & np.isfinite(res).all(1)
        JtJ = np.einsum('nki,nkj->nij', J[ok], J[ok]); Jtr = np.einsum('nki,nk->ni', J[ok], res[ok])
        dlt = np.linalg.solve(JtJ + 1e-9 * np.eye(2), Jtr[..., None])[..., 0]
        r[ok] += np.clip(dlt[:, 0], -1, 1); c[ok] += np.clip(dlt[:, 1], -1, 1)
    Q = bilin(Tf, r, c); ecart = np.linalg.norm(P - Q, axis=1)
    bon = np.isfinite(ecart) & (r >= 0) & (c >= 0) & (r <= T.shape[0] - 1) & (c <= T.shape[1] - 1)
    print('ecart 3D apres ajustement (voxels) : mediane %.3f, p95 %.3f, max %.3f, noeuds hors maillage equipe %d'
          % (np.median(ecart[bon]), np.percentile(ecart[bon], 95), ecart[bon].max(), (~bon).sum()))
    R = np.full(vE.shape, np.nan); C = np.full(vE.shape, np.nan)
    R[rE[bon], cE[bon]] = r[bon]; C[rE[bon], cE[bon]] = c[bon]
    # sens : jacobienne moyenne (grille Erwin -> grille equipe)
    dRr = np.nanmedian(np.diff(R, axis=0)); dCc = np.nanmedian(np.diff(C, axis=1))
    dRc = np.nanmedian(np.diff(R, axis=1)); dCr = np.nanmedian(np.diff(C, axis=0))
    print('jacobienne mediane [[dR/dr dR/dc],[dC/dr dC/dc]] = [[%.3f %.3f],[%.3f %.3f]], determinant %.3f'
          % (dRr, dRc, dCr, dCc, dRr * dCc - dRc * dCr))
    np.savez(D + 'champ.npz', R=R, C=C)
    return R, C


def carte(f, out):
    z = np.load(D + 'champ.npz'); R, C = z['R'], z['C']
    M = tifffile.imread(f).astype(np.float32)
    ys, xs = np.mgrid[0:ZH, 0:ZW].astype(np.float64)
    col = RW - (xs + ZX0); lig = RH - ys                 # pixel du rendu brut d'Erwin
    nr, nc = lig / 20.0, col / 20.0                       # noeud d'Erwin
    ok = ~np.isnan(R)
    Rf = np.where(ok, R, 0); Cf = np.where(ok, C, 0)
    tr = ndimage.map_coordinates(Rf, [nr, nc], order=1, mode='nearest')
    tc = ndimage.map_coordinates(Cf, [nr, nc], order=1, mode='nearest')
    val = ndimage.map_coordinates(ok.astype(np.float32), [nr, nc], order=1, mode='constant') > 0.999
    py, px = tr * 20.0, tc * 20.0                          # pixel de la carte de l'equipe
    S = ndimage.map_coordinates(M, [py, px], order=1, mode='constant', cval=0)
    S[~val] = 0
    tifffile.imwrite(out, np.clip(S, 0, 255).astype(np.uint8))
    print(out, S.shape, 'couvert %.3f' % val.mean())


if __name__ == '__main__':
    if sys.argv[1] == 'champ':
        champ()
    else:
        carte(sys.argv[2], sys.argv[3])
