# Second repli inscrit pour PR-48 (additif du 28/09, commit a7a76ca) : si un essai a blanc en demi-planches ne repond pas
# en 600 s, chaque planche de 28 vignettes est coupee en quarts de 7 (vignettes 1-7, 8-14, 15-21, 22-28). Meme principe que
# moities_planches.py : vignettes recopiees au pixel pres depuis la planche d origine, numeros d origine gardes,
# 4 colonnes. Aucune carte n est relue : memes vignettes, meme repartition.
# usage : quarts_planches.py PLANCHE.png [...]  ->  PLANCHE_q1.png ... PLANCHE_q4.png
import sys
from PIL import Image

T, COLS = 200, 4
W, H = T + 12, T + 28

for f in sys.argv[1:]:
    src = Image.open(f)
    assert (src.width, src.height) == (COLS * W, 7 * H), (f, src.size)
    for q in range(4):
        out = Image.new(src.mode, (COLS * W, 2 * H), 255)
        for k, c in enumerate(range(7 * q, 7 * q + 7)):
            x, y = (c % COLS) * W, (c // COLS) * H
            out.paste(src.crop((x, y, x + W, y + H)), ((k % COLS) * W, (k // COLS) * H))
        g = '%s_q%d.png' % (f[:-4], q + 1)
        out.save(g)
        print(g, out.size)
