# PR-24 : corrige une lecture (table "P01 | verdict | tuile | lettres | ...") avec la cle, selon les regles
# enregistrees : sensibilite >= 3/5 lettres etiquetees, specificite <= 1/5 papyrus sans rien.
# usage : pr24_score.py CLE.json LECTURE.txt [LECTURE2.txt]
import sys, json, re

cle = {p['panneau']: p for p in json.load(open(sys.argv[1]))['panneaux']}


def lire(f):
    r = {}
    for ligne in open(f, encoding='utf-8'):
        m = re.match(r'\s*\|?\s*(P\d\d)\s*\|\s*([A-Za-z\' ]+?)\s*\|\s*([^|]*)\|\s*([^|]*)', ligne)
        if m:
            v = m.group(2).upper().replace(' ', '').replace("'", '')
            r[m.group(1)] = ('STROKES' if v.startswith('STROKE') else 'NOTHING' if v.startswith('NOTHING') else
                             'DONTKNOW', m.group(3).strip(), m.group(4).strip())
    assert set(r) == set(cle), 'panneaux lus %d / %d, manquants %s' % (len(r), len(cle), sorted(set(cle) - set(r)))
    return r


lectures = [lire(f) for f in sys.argv[2:]]
ok = []
for f, r in zip(sys.argv[2:], lectures):
    fam = lambda nom: [p for p in cle if cle[p]['famille'] == nom]
    sens = sum(r[p][0] == 'STROKES' for p in fam('lettre_etiquetee'))
    faux = sum(r[p][0] == 'STROKES' for p in fam('papyrus_sans_rien'))
    cib = [p for p in fam('cible_ibara') if r[p][0] == 'STROKES']
    passe = sens >= 3 and faux <= 1
    ok.append(passe)
    print('%s : sensibilite %d/5  faux positifs %d/5  -> %s ; cibles STROKES %d/%d'
          % (f, sens, faux, 'PASSE' if passe else 'ECHOUE', len(cib), len(fam('cible_ibara'))))
    for p in sorted(cle):
        print('   %s %-18s %-8s tuile %-4s lettres %s' % (p, cle[p]['famille'], r[p][0], r[p][1], r[p][2]))
if len(lectures) == 2:
    a, b = lectures
    communs = [p for p in cle if cle[p]['famille'] == 'cible_ibara' and a[p][0] == b[p][0] == 'STROKES']
    print('cibles STROKES pour les deux lecteurs :', communs if all(ok) else '(non compte : un lecteur echoue)')
    for p in communs:
        print('   %s  %s  y0 %d x0 %d' % (p, cle[p]['ref'], cle[p]['y0'], cle[p]['x0']))
