# PR-30 : config d affinage d ink_9um sur le type de scan 1,2 m, derivee de la recette officielle
# aligned21_hybrid_3d2d.json : memes modele, fenetre 17 couches a decalage +-2, normalisation, perte, augmentations.
# Change : les donnees (5 segments etiquetes hors entrainement d ink_9um + l ancre officielle 0139 w035), le depart
# (poids ink_9um graine 42 etape 75 000), le taux d apprentissage (0,002 au lieu de 0,01 : on affine), le lot (16 au lieu
# de 64 : 8 Go de GPU), la duree, et AUCUNE validation pendant l entrainement (0343P reste hors de tout, evalue apres).
# usage : ft12m_config.py SORTIE.json ITERATIONS
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
c['batch_size'] = 16
c['learning_rate'] = 0.002
c['warmup_steps'] = 200
c['num_iterations'] = int(sys.argv[2])
c['save_every'] = 1000
c['val_every'] = 10 ** 9
c['dataloader_workers'] = 4
c['checkpoint'] = '%s/checkpoints/ink_9um/hybrid_3d2d-seed42/step-075000.pth' % C
c['weights_only'] = True
c['out_dir'] = '%s/runs/pr30_ft12m' % C
c['description'] = 'PR-30 : ink_9um s42 75k affine sur scans 1,2 m (841 x3, 0009B, 0500P2, ancre 0139 w035)'
json.dump(c, open(sys.argv[1], 'w'), indent=1)
print('config ecrite', sys.argv[1], c['num_iterations'], 'iterations')
