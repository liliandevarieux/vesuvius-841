# PR-30 : config d affinage d ink_9um sur le type de scan 1,2 m, derivee de la recette officielle
# aligned21_hybrid_3d2d.json : memes modele, fenetre 17 couches a decalage +-2, normalisation, perte, augmentations.
# Change : les donnees (5 segments etiquetes hors entrainement d ink_9um + l ancre officielle 0139 w035), le depart
# (poids ink_9um graine 42 etape 75 000), le taux d apprentissage (0,002 au lieu de 0,01 : on affine), le lot (16 au lieu
# de 64 : 8 Go de GPU), la duree, et AUCUNE validation pendant l entrainement (0343P reste hors de tout, evalue apres).
# usage : ft12m_config.py SORTIE.json ITERATIONS [ROULEAU_EXCLU NOM_RUN [JSON]]   (PR-31 : un rouleau laisse de cote ;
#         PR-32/33 : JSON = variante, cles 'label_smoothing', 'learning_rate', 'labels_dir', 'anchors' ;
#         PR-36 : 'pseudo_dir', 'checkpoint', 'counts' ; PR-38 : 'corpus' {dir, vol_dir, segs, suffixe})
import sys, json

C = '/home/slusarska_holding/vesuvius'
R = '%s/villa/vesuvius/src/vesuvius/ink_detection/configs/aligned21_hybrid_3d2d.json' % C
c = json.load(open(R))
lab = '%s/ft12m/labels' % C
src = '%s/ft12m/src' % C


def entree(scroll, segs):
    return {'segments_path': lab, 'segments': segs, 'volume_scale': 0, 'sampling_scroll': scroll,
            'sampling_physical_segment_keys': {s: '%s:%s' % (scroll, s) for s in segs},
            'sampling_representation_keys': {s: 'native_1p2m:%s' % s for s in segs},
            'surface_volume_paths': {s: '%s/%s/vol.zarr' % (src, s) for s in segs}}


c['datasets'] = [
    entree('0841', ['841_w00', '841_segA', '841_segB']),
    entree('0009B', ['0009B']),
    entree('0500P2', ['0500P2']),
    {'segments_path': '%s/ft12m/ref' % C, 'segments': ['w035'], 'volume_scale': 0, 'sampling_scroll': '0139',
     'sampling_physical_segment_keys': {'w035': '0139:w035'},
     'sampling_representation_keys': {'w035': 'native_9p362_level0:w035'},
     'surface_volume_paths': {'w035': '%s/ink-dataset/ref_12m/w035.zarr' % C}},
]
c['fixed_scroll_prior'] = {'seed': 42, 'target_batch_counts': {'0841': 6, '0009B': 3, '0500P2': 3, '0139': 4}}
EXCLU = sys.argv[3] if len(sys.argv) > 3 else None
if EXCLU:                                   # PR-31 : le rouleau exclu sort des donnees, les deux autres se partagent 12
    c['datasets'] = [d for d in c['datasets'] if d['sampling_scroll'] != EXCLU]
    restants = [d['sampling_scroll'] for d in c['datasets'] if d['sampling_scroll'] != '0139']
    c['fixed_scroll_prior']['target_batch_counts'] = dict({r: 6 for r in restants}, **{'0139': 4})
c['batch_size'] = 16
c['learning_rate'] = 0.002
c['warmup_steps'] = 200
c['num_iterations'] = int(sys.argv[2])
c['save_every'] = 1000
c['val_every'] = 10 ** 9
c['dataloader_workers'] = 4
c['checkpoint'] = '%s/checkpoints/ink_9um/hybrid_3d2d-seed42/step-075000.pth' % C
c['weights_only'] = True
c['out_dir'] = '%s/runs/%s' % (C, sys.argv[4] if len(sys.argv) > 4 else 'pr30_ft12m')
c['description'] = 'PR-30 : ink_9um s42 75k affine sur scans 1,2 m (841 x3, 0009B, 0500P2, ancre 0139 w035)'
V = json.loads(sys.argv[5]) if len(sys.argv) > 5 else {}
if 'label_smoothing' in V:
    c['loss']['bce_label_smoothing'] = V['label_smoothing']
if 'learning_rate' in V:
    c['learning_rate'] = V['learning_rate']
if 'seed' in V:                             # PR-35 : replication a une autre graine (echantillonnage, augmentations)
    c['seed'] = V['seed']
    c['fixed_scroll_prior']['seed'] = V['seed']
if V.get('add0814'):                        # PR-34 : un quatrieme rouleau etiquete a 1,2 m (diversite entre rouleaux)
    c['datasets'].insert(0, entree('0814', ['0814']))
    restants = [d['sampling_scroll'] for d in c['datasets'] if d['sampling_scroll'] != '0139']
    c['fixed_scroll_prior']['target_batch_counts'] = dict({r: 12 // len(restants) for r in restants}, **{'0139': 16 - 12 // len(restants) * len(restants)})
if 'anchors' in V:                          # PR-33 : ancre 0139 elargie aux segments natifs 1,2 m etiquetes
    for d in c['datasets']:
        if d['sampling_scroll'] == '0139':
            d['segments'] = V['anchors']
            d['sampling_physical_segment_keys'] = {w: '0139:%s' % w for w in V['anchors']}
            d['sampling_representation_keys'] = {w: 'native_9p362_level0:%s' % w for w in V['anchors']}
            d['surface_volume_paths'] = {w: '%s/ink-dataset/ref_12m/%s.zarr' % (C, w) for w in V['anchors']}
if 'labels_dir' in V:                       # etiquettes variantes (l ancre 0139 w035 garde les siennes)
    for d in c['datasets']:
        if d['segments_path'] == lab:
            d['segments_path'] = V['labels_dir']
if 'pseudo_dir' in V:                       # PR-36 : le rouleau exclu revient, avec ses pseudo-etiquettes seulement
    segs = {'0841': ['841_w00', '841_segA', '841_segB']}.get(EXCLU, [EXCLU])
    e = entree(EXCLU, segs)
    e['segments_path'] = V['pseudo_dir']
    c['datasets'].insert(0, e)
if 'corpus' in V:                           # PR-38 : corpus d ink_9um (2,4 um poole), eventuellement floute
    K = V['corpus']
    par = {}
    for sg in K['segs']:
        par.setdefault({'pherc0139': '0139', 'pherc1667': '1667', 'phercparis4': 'Paris4', 'pherc0814': '0814'}[sg.split('-')[0]], []).append(sg)
    rep = 'public_2p4_level2_zmean4' + K.get('suffixe', '')
    for sc, segs in par.items():
        c['datasets'].append({'segments_path': K['dir'], 'segments': segs, 'volume_scale': 0, 'sampling_scroll': sc,
                              'sampling_physical_segment_keys': {x: '%s:%s' % (sc, x) for x in segs},
                              'sampling_representation_keys': {x: '%s:%s' % (rep, x) for x in segs},
                              'surface_volume_paths': {x: '%s/%s/surface-volume.zarr' % (K.get('vol_dir', K['dir']), x) for x in segs}})
if 'checkpoint' in V:                       # PR-36 : depart = modele du pli (poids seuls, optimiseur neuf)
    c['checkpoint'] = V['checkpoint']
if 'counts' in V:
    c['fixed_scroll_prior']['target_batch_counts'] = V['counts']
if 'seed' in V:
    c['fixed_scroll_prior']['seed'] = V['seed']
c['description'] += ' | variante %s' % json.dumps(V)
json.dump(c, open(sys.argv[1], 'w'), indent=1)
print('config ecrite', sys.argv[1], c['num_iterations'], 'iterations')
