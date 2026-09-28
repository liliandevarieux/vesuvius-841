# PR-4 : lit le carre 2x2 tableau x graine et applique le critere enregistre, sans interpretation.
#
# POURQUOI CE SCRIPT EXISTE, ET POURQUOI IL EST ECRIT AVANT LES CHIFFRES. PR-4 dit : « |effet du tableau| >
# |effet de la graine| ». Cette phrase se decide de plusieurs facons selon qu on moyenne, qu on prend le pire cas,
# ou qu on regarde un segment plutot que l autre -- et le choix fait apres avoir vu les nombres n est plus un
# critere, c est un resultat qu on fabrique. Le script est ecrit et commite pendant que la premiere cellule
# s entraine, et il ne sera pas modifie pour lire le carre.
#
# AMENDEMENT DU 23/09 23:30, ecrit alors qu AUCUNE mesure des cellules graine 43 n existait (cellule 1 au pas
# 3 858 sur 16 000). En tracant la provenance des labels de chaque cellule, il apparait que les deux LIGNES du
# carre n ont pas ete construites avec le meme professeur ni avec la meme regle de seuil :
#   ligne rendu  (human7, w00_s43) : professeur ps48..., seuils absolus 190/131, labels w00_inklabels_human7
#   ligne volume (pr2v24, v24_s43) : professeur new_canon natif, aire egale +/-8, labels w00v24_inklabels_v2
# La difference entre lignes melange donc le tableau, le professeur, la regle de seuil et la version des labels
# humains. Ce qui reste propre, et c est ce que PR-4 apporte : la difference de GRAINE a l interieur de chaque
# ligne, ou tout est tenu sauf seed.
#
# CORRECTION DU 23/09 23:55. La premiere version de cet amendement disait que PR-2 n etait pas touche, parce que
# ses deux bras partageaient la regle de seuil. C etait faux : human7n a ete fabrique avec T_HI=190 T_LO=131
# (run4_queue10.sh ligne 24, transmis par run4_launch.sh ligne 12, ou T_HI/T_LO ont la priorite finale dans
# mkteacher.py), et pr2v24 avec T_EQ=1 DELTA=8. La phrase venait d un resume ecrit plus tard dans JOURNAL.md,
# de memoire. Le script est la trace, le resume avait tort. PR-2 varie donc trois choses a la fois.
#
# D OU LA REGLE POUR L EFFET DU TABLEAU : on prend la paire APPARIEE de PR-5 (w00m contre pr2v24) des qu elle
# existe -- meme professeur, meme regle de seuil, memes labels humains, seul le tableau change. Tant qu elle
# n existe pas, on imprime celle de PR-2 (human7n contre pr2v24) EN LA MARQUANT confondue, et le verdict le dit.
#
# LA REGLE, telle qu amendee : l effet du tableau survit a un changement de graine si, sur CHAQUE segment,
# l effet du tableau (appariee de PR-5 si elle existe) depasse LES DEUX effets de graine mesures sur ce segment.
# La difference entre lignes du carre est imprimee quand meme, marquee « confondue », pour ne rien cacher.
#
# usage: carre_pr4.py
import re, json, os

H = '/home/slusarska_holding/vesuvius'
CASES = {
    ('rendu 4,681 um',         42): ('ink_841_human7',  'h7'),
    ('rendu 4,681 um',         43): ('ink_841_w00_s43', 'w00s43'),
    ('volume publie 2,403 um', 42): ('ink_841_pr2v24',  'pr2v24'),
    ('volume publie 2,403 um', 43): ('ink_841_v24_s43', 'v24s43'),
}
LIGNES = ['rendu 4,681 um', 'volume publie 2,403 um']
GRAINES = [42, 43]
# la paire qui donne l effet du tableau. PR-5 d abord (appariee), PR-2 ensuite (confondue) si PR-5 n a pas fini.
APPARIEE = ('w00m', 'pr2v24')
CONFONDUE = ('human7n', 'pr2v24')


def primaire(tag, loc):
    """Ecart encre/fond moyen sur les trois fenetres tenues a l ecart, COUCHES INVERSEES.

    C est le sens qui lit ; le sens direct sert de controle et il est imprime a part. Les fichiers portent deux
    prefixes selon la file qui les a ecrits : pr2_ pour les files 29 a 31, pr4_ pour la 32 et la 33, pr5_ pour
    la 34. On accepte les trois plutot que de renommer des mesures deja faites."""
    for p in ('pr5', 'pr4', 'pr2'):
        f = '%s/results/%s_%s_%s.json' % (H, p, loc, tag)
        if os.path.exists(f):
            d = json.load(open(f))
            return d['mean']['reversed']['sep'], d['mean']['direct']['sep']
    return None, None


def secondaire(run, ckpt=16000):
    """Moyenne des trois fenetres du rendu, lue dans le journal et nulle part ailleurs."""
    e = {}
    for l in open('%s/logs/841_run4.log' % H, errors='replace'):
        m = re.match(r'(\S+) ckpt (\d+) fenetre (\d+) notre pred:.*sur encre ([\d.]+) vs hors encre ([\d.]+)', l)
        if m and m.group(1) == run and int(m.group(2)) == ckpt:
            e[int(m.group(3))] = float(m.group(4)) - float(m.group(5))
    return round(sum(e.values()) / 3, 1) if len(e) == 3 else None


manque = []
for loc in ('segB', 'segA'):
    print()
    print('=== %s — mesure PRIMAIRE (trois fenetres tenues a l ecart, couches inversees) ===' % loc)
    print('%-24s %10s %10s %14s' % ('', 'graine 42', 'graine 43', 'effet GRAINE'))
    v = {}
    for lg in LIGNES:
        c = []
        for g in GRAINES:
            run, tag = CASES[(lg, g)]
            s, _ = primaire(tag, loc)
            if s is None:
                manque.append('%s / %s (graine %d) : aucun results/pr?_%s_%s.json' % (loc, run, g, loc, tag))
            c.append(s)
        v[lg] = c
        eg = abs(c[0] - c[1]) if None not in c else None
        print('%-24s %10s %10s %14s' % (lg,
              '-' if c[0] is None else '%.1f' % c[0],
              '-' if c[1] is None else '%.1f' % c[1],
              '-' if eg is None else '%.1f' % eg))

    # --- l effet du tableau : la paire appariee de PR-5 si elle existe, sinon celle de PR-2, marquee confondue
    paire, appariee = APPARIEE, True
    t_ref, _ = primaire(paire[0], loc)
    if t_ref is None:
        paire, appariee = CONFONDUE, False
        t_ref, _ = primaire(paire[0], loc)
        manque.append('%s : PR-5 (%s) pas encore mesure ; effet du tableau lu sur la paire confondue de PR-2'
                      % (loc, APPARIEE[0]))
    e_ref, _ = primaire(paire[1], loc)
    if t_ref is None or e_ref is None:
        manque.append('%s : aucune paire complete pour l effet du tableau' % loc)
    a, b = v[LIGNES[0]], v[LIGNES[1]]

    if None not in a and None not in b:
        conf = [b[i] - a[i] for i in range(2)]
        print('   difference entre lignes du carre, CONFONDUE (tableau + professeur + regle de seuil), imprimee')
        print('   pour ne rien cacher et non utilisee : %+.1f (g42)  %+.1f (g43)' % tuple(conf))

    graine = [abs(x[0] - x[1]) if None not in x else None for x in (a, b)]
    if None in graine or t_ref is None or e_ref is None:
        print('   carre incomplet : verdict impossible.')
        continue
    tableau = e_ref - t_ref
    print()
    print('   effet du TABLEAU, paire %s (%s -> %s) : %+.1f'
          % ('APPARIEE de PR-5' if appariee else 'CONFONDUE de PR-2 (tableau + seuils + labels humains)',
             paire[0], paire[1], tableau))
    print('   effet de la GRAINE (43 contre 42, tout tenu)         : %.1f (rendu)  %.1f (volume)' % tuple(graine))
    marge = tableau - max(graine)
    print('   l effet du tableau (%.1f) depasse les DEUX effets de graine (%.1f et %.1f) : %s'
          % (tableau, graine[0], graine[1], 'OUI' if marge > 0 else 'NON'))
    # --- mesure gratuite, offerte par PR-5 : l effet de la RECETTE de labels a tableau constant.
    # w00m et human7n sont tous deux le RENDU, avec le meme professeur (new_canon recale) ; ils different par la
    # regle de seuil (aire egale +/-8 contre absolus 190/131) et par la version des labels humains. Si l ecart est
    # petit, la recette pesait peu et le chiffre de PR-2 etait surtout du tableau ; s il est grand, il pesait.
    # Ecrit avant que w00m existe, pour ne pas choisir apres coup s il faut le montrer.
    w_m, _ = primaire('w00m', loc)
    w_h, _ = primaire('human7n', loc)
    if w_m is not None and w_h is not None:
        print('   effet de la RECETTE de labels, a tableau constant (human7n -> w00m) : %+.1f' % (w_m - w_h))

    if not appariee:
        print('   ATTENTION : cet effet du tableau n est pas apparie. Tant que PR-5 n a pas rendu, le verdict')
        print('   ci-dessous porte sur « tableau + regle de seuil + version des labels humains », pas sur le')
        print('   tableau seul.')
    print('   -> %s' % (('sur %s, l effet du tableau survit a un changement de graine (marge %.1f). '
                         'Formulation autorisee : « survit », pas « prouve ».' % (loc, marge)) if marge > 0 else
                        ('sur %s, la graine deplace autant que le tableau : ce plan n etablit pas l effet du '
                         'tableau. La suite est de refaire des runs, pas de parler plus fort.' % loc)))

print()
print('=== mesure SECONDAIRE (trois fenetres du rendu, ckpt 16000) — rappel, bruit connu 5,2 ===')
print('%-24s %10s %10s' % ('', 'graine 42', 'graine 43'))
for lg in LIGNES:
    c = [secondaire(CASES[(lg, g)][0]) for g in GRAINES]
    print('%-24s %10s %10s' % (lg, '-' if c[0] is None else c[0], '-' if c[1] is None else c[1]))
print('   (l ecart-type d un bras vaut 5,2 sur cette metrique : elle est rappelee, elle ne tranche rien.)')

print()
print('=== sens direct, controle (doit rester bas ; un bras qui lirait dans les deux sens serait suspect) ===')
for loc in ('segB', 'segA'):
    o = []
    for lg in LIGNES:
        for g in GRAINES:
            _, d = primaire(CASES[(lg, g)][1], loc)
            o.append('%s g%d %s' % (lg.split()[0], g, '-' if d is None else '%.1f' % d))
    print('   %s : %s' % (loc, '  |  '.join(o)))

if manque:
    print()
    print('CASES MANQUANTES (%d) :' % len(manque))
    for m in manque:
        print('   ' + m)
