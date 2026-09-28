# Repli ecrit dans l inscription de PR-48 : si l essai a blanc ne repond pas en 600 s, chaque planche de 28 vignettes est
# coupee en deux moities de 14 (vignettes 1-14 et 15-28). Les vignettes sont recopiees au pixel pres depuis la planche
# d origine (case de 212 x 228 px : numero + vignette 200 px, geometrie de banc_lisibilite.planche), numeros d origine
# gardes, meme disposition en 4 colonnes. Aucune carte n est relue : memes vignettes, meme repartition.
# usage : moities_planches.py PLANCHE.png [...]  ->  PLANCHE_a.png (1-14) et PLANCHE_b.png (15-28)
import sys
from PIL import Image

T, COLS = 200, 4
W, H = T + 12, T + 28

for f in sys.argv[1:]:
    src = Image.open(f)
    n = (src.width // W) * (src.height // H)
    assert (src.width, src.height) == (COLS * W, 7 * H) and n == 28, (f, src.size)
    for suffixe, cases in (('a', range(0, 14)), ('b', range(14, 28))):
        out = Image.new(src.mode, (COLS * W, 4 * H), 255)
        for k, c in enumerate(cases):
            x, y = (c % COLS) * W, (c // COLS) * H
            out.paste(src.crop((x, y, x + W, y + H)), ((k % COLS) * W, (k // COLS) * H))
        g = f[:-4] + '_' + suffixe + '.png'
        out.save(g)
        print(g, out.size)
