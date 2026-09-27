# PR-36 : critere primaire lu dans logs/pr36.log. Par carte : sens choisi sans etiquette (plus grand p99-p50),
# puis moyennes sur les 5 segments et les 2 graines, bras P (pseudo-etiquettes) contre T (temoin).
import re, collections

L = open('/home/slusarska_holding/vesuvius/logs/pr36.log').read().splitlines()
auc, sens, forme = {}, {}, {}
for l in L:
    m = re.match(r'(pr36_([PT])(\d+)_\w+?_(841_w00|841_segA|841_segB|0009B|0500P2)(_reverse)?\.tif)\s+(\S+)\s+AUC-sup ([\d.]+).*p99-p50 ([\d.]+)', l)
    if m:
        k = (m.group(2), m.group(3), m.group(4), bool(m.group(5)))
        auc[k], sens[k] = float(m.group(7)), float(m.group(8))
    m = re.match(r'(pr36_([PT])(\d+)_\w+?_(841_w00|841_segA|841_segB|0009B|0500P2)(_reverse)?\.tif)\s+(\S+)\s+lettres\s+\d+\s+ALLONGEMENT carte\s+([\d.na]+)', l)
    if m:
        forme[(m.group(2), m.group(3), m.group(4), bool(m.group(5)))] = float(m.group(7))
choix = collections.defaultdict(dict)
for (b, g, s, r) in auc:
    if r:
        continue
    kf, kr = (b, g, s, False), (b, g, s, True)
    if kr in sens and kf in forme and kr in forme:
        k = kr if sens[kr] > sens[kf] else kf
        choix[(b, g)][s] = (auc[k], forme[k], 'rev' if k[3] else 'fwd')
SEGS = ['841_w00', '841_segA', '841_segB', '0009B', '0500P2']
moy = {}
for (b, g) in sorted(choix):
    d = choix[(b, g)]
    print('%s%s ' % (b, g) + '  '.join('%s A%.3f E%.2f %s' % (s, *d[s]) if s in d else '%s -' % s for s in SEGS))
    if all(s in d for s in SEGS):
        moy[(b, g)] = (sum(d[s][1] for s in SEGS) / 5, sum(d[s][0] for s in SEGS) / 5)
        print('     moyenne allongement %.2f  AUC %.4f' % moy[(b, g)])
bras = {b: [moy[k] for k in moy if k[0] == b] for b in 'PT'}
if len(bras['P']) == 2 and len(bras['T']) == 2:
    eP, aP = [sum(x[i] for x in bras['P']) / 2 for i in (0, 1)]
    eT, aT = [sum(x[i] for x in bras['T']) / 2 for i in (0, 1)]
    ok = eP - eT >= 2.0 and aP >= aT - 0.01
    print('PRIMAIRE : allongement P %.2f  T %.2f  (P-T %+.2f, barre +2,0) ; AUC P %.4f  T %.4f  (P-T %+.4f, barre -0,01) -> %s'
          % (eP, eT, eP - eT, aP, aT, aP - aT, 'TIENT' if ok else 'ECHOUE'))
else:
    print('primaire incomplet :', {b: len(v) for b, v in bras.items()})
