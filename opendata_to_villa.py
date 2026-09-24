#!/usr/bin/env python3
"""Turn any published Vesuvius open-data segment into a villa `ink_detection` dataset.

villa's ink_detection reads datasets shaped like the ones in the organisers' label bucket: a zarr volume of N planes
plus `<name>_inklabels_v2` and `<name>_supervision_mask_v2` broadcast over those planes. The open data publishes
something else - surface volumes with their own plane count and resolution, and labels as separate zarr arrays. This
bridges the two, fetching only the chunks the requested region actually needs.

    # what volumes and label releases does this segment have?
    opendata_to_villa.py --scroll PHerc0841 --segment 20260221022814-auto_grown_20260220174252405 --list

    # build a 65-plane dataset over the inspected zone, layers reversed
    opendata_to_villa.py --scroll PHerc0841 --segment 20260221022814-auto_grown_20260220174252405 \
        --volume 2.403um-0.22m-77keV-volume-20260319124803 --labels 20260918 \
        --out ~/vesuvius/ink-dataset/841/segB --name segB --planes 65 --centre 50 --reverse

`--centre` picks which window of planes is taken; `--full` interpolates the whole depth down to `--planes` instead.
Both the plane window and the direction are printed and written into `build.json`, because a model silently inherits
the convention of the array it was trained on - see https://github.com/ScrollPrize/villa/issues/1648.
"""
import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor

B = 'https://vesuvius-challenge-open-data.s3.us-east-1.amazonaws.com'


def get(url, binary=True):
    with urllib.request.urlopen(url, timeout=120) as r:
        return r.read() if binary else r.read().decode()


def ls(prefix, delimiter=True):
    """Keys (and common prefixes) under `prefix`, following continuation tokens."""
    out, token = [], None
    while True:
        u = B + '/?list-type=2&prefix=' + urllib.parse.quote(prefix) + '&max-keys=1000'
        if delimiter:
            u += '&delimiter=/'
        if token:
            u += '&continuation-token=' + urllib.parse.quote(token, safe='')
        x = ET.fromstring(get(u, binary=False))
        ns = {'s': x.tag[1:x.tag.index('}')]}
        out += [e.text for e in x.findall('s:CommonPrefixes/s:Prefix', ns)]
        out += [e.text for e in x.findall('s:Contents/s:Key', ns)]
        t = x.find('s:NextContinuationToken', ns)
        if t is None:
            return out
        token = t.text


def fetch_dir(prefix, dest, jobs):
    """Download every key under `prefix` into `dest`, keeping the relative layout."""
    keys = [k for k in ls(prefix, delimiter=False) if not k.endswith('/')]

    def one(k):
        p = os.path.join(dest, k[len(prefix):])
        os.makedirs(os.path.dirname(p), exist_ok=True)
        if os.path.exists(p) and os.path.getsize(p):
            return
        blob = get(B + '/' + urllib.parse.quote(k))          # the bytes first: see the note on the chunk fetcher
        with open(p + '.part', 'wb') as fh:
            fh.write(blob)
        os.replace(p + '.part', p)

    with ThreadPoolExecutor(jobs) as ex:
        list(ex.map(one, keys))
    return len(keys)


def main():
    a = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    a.add_argument('--scroll', required=True, help='e.g. PHerc0841')
    a.add_argument('--segment', required=True, help='segment directory name under <scroll>/segments/')
    a.add_argument('--volume', help='surface-volume directory name, without the .zarr suffix')
    a.add_argument('--labels', help='label release date under ink-labels/<volume>/, e.g. 20260918')
    a.add_argument('--out', help='destination directory')
    a.add_argument('--name', help='dataset name inside --out (defaults to its basename)')
    a.add_argument('--planes', type=int, default=65, help='planes in the produced volume (default 65)')
    a.add_argument('--centre', type=int, help='centre plane of the window taken (default: middle of the stack)')
    a.add_argument('--full', action='store_true', help='interpolate the whole depth down to --planes instead')
    a.add_argument('--reverse', action='store_true', help='store the planes in reverse order')
    a.add_argument('--region', default='inspected',
                   help='"inspected" (the supervision mask), "labels" (their bounding box), or Y0,Y1,X0,X1')
    a.add_argument('--jobs', type=int, default=8)
    a.add_argument('--list', action='store_true', help='show the volumes and label releases of the segment, then stop')
    a.add_argument('--dry-run', action='store_true', help='report what would be fetched, fetch nothing')
    o = a.parse_args()

    seg = '%s/segments/%s/' % (o.scroll, o.segment)
    if o.list:
        print('surface volumes:')
        for p in ls(seg + 'surface-volumes/'):
            print('   ', p.rstrip('/').rsplit('/', 1)[-1])
        print('label releases:')
        for p in ls(seg + 'ink-labels/'):
            for q in ls(p):
                print('   ', '/'.join(q.rstrip('/').split('/')[-2:]))
        print('published predictions:')
        for p in ls(seg + 'ink-detection/'):
            print('   ', p.rstrip('/').rsplit('/', 1)[-1])
        return 0

    if not o.volume or not o.out:
        a.error('--volume and --out are required unless --list is given')
    import numpy as np
    import zarr
    from numcodecs import Blosc

    vpre = seg + 'surface-volumes/' + o.volume + '.zarr/'
    za = json.loads(get(B + '/' + urllib.parse.quote(vpre) + '0/.zarray', binary=False))
    Z, HH, WW = za['shape']
    cz, cy, cx = za['chunks']
    sepa = za.get('dimension_separator', '.')
    ny, nx = -(-HH // cy), -(-WW // cx)
    print('volume %dx%dx%d, chunks %dx%dx%d, %d chunks in the plane' % (Z, HH, WW, cz, cy, cx, ny * nx))

    out = os.path.expanduser(o.out)
    name = o.name or os.path.basename(out.rstrip('/'))
    os.makedirs(out, exist_ok=True)

    # --- labels ---------------------------------------------------------------------------------------------------
    lab = None
    if o.labels:
        found = [q for p in ls(seg + 'ink-labels/') for q in ls(p) if q.rstrip('/').endswith('/' + o.labels)]
        if not found:
            a.error('no label release %r under %sink-labels/' % (o.labels, seg))
        # Labels are a few MB and they are what sizes the region, so --dry-run fetches them too: the point of a dry
        # run is to print the real number of gigabytes, not a guess.
        ldir = os.path.join(out, '_labels')
        print('labels: %d files from %s' % (fetch_dir(found[0], ldir, o.jobs), found[0]))
        lab = ldir
        # Labels are published on one volume's canvas. Cropping them onto another would misplace every letter and
        # nothing downstream would complain, so check now, before anything is fetched or written.
        ls_ = zarr.open(os.path.join(lab, 'inklabels.zarr'), mode='r')['0'].shape
        if tuple(ls_) != (HH, WW):
            sys.exit('labels are %dx%d but the volume is %dx%d: this label release belongs to a different surface '
                     'volume of this segment. Pick the matching --volume, or drop --labels.'
                     % (ls_[0], ls_[1], HH, WW))

    # --- which chunks ---------------------------------------------------------------------------------------------
    if ',' in o.region:
        Y0, Y1, X0, X1 = [int(v) for v in o.region.split(',')]
        want = set((y, x)
                   for y in range(max(0, (Y0 - cy) // cy), min(ny, (Y1 + cy) // cy + 1))
                   for x in range(max(0, (X0 - cx) // cx), min(nx, (X1 + cx) // cx + 1)))
    else:
        if not lab:
            a.error('--region inspected/labels needs --labels')
        src = 'supervision' if o.region == 'inspected' else 'inklabels'
        M = np.asarray(zarr.open(os.path.join(lab, src + '.zarr'), mode='r')['3'][:]) > 0  # level 3 = 1/8 scale
        ii, jj = np.nonzero(M)
        want = set()
        for y, x in zip(ii * 8 // cy, jj * 8 // cx):
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    if 0 <= y + dy < ny and 0 <= x + dx < nx:
                        want.add((y + dy, x + dx))
    print('region %r: %d chunks of %d (%.2f GB uncompressed)'
          % (o.region, len(want), ny * nx, len(want) * cz * cy * cx / 1073741824))
    if o.dry_run:
        return 0

    # --- fetch the volume chunks ----------------------------------------------------------------------------------
    raw = os.path.join(out, '_raw', '0')
    os.makedirs(raw, exist_ok=True)
    open(os.path.join(raw, '.zarray'), 'w').write(json.dumps(za))

    def one(t):
        y, x = t
        rel = '0.%d.%d' % (y, x) if sepa == '.' else '0/%d/%d' % (y, x)
        p = os.path.join(raw, *rel.split('/'))
        os.makedirs(os.path.dirname(p), exist_ok=True)
        if os.path.exists(p) and os.path.getsize(p):
            return
        # `open(p, 'wb').write(get(...))` creates and truncates the file BEFORE the request is made, so a chunk that
        # 404s - and on a whole-sheet region most corner chunks do - left a 0-byte file behind. zarr then read that
        # file instead of treating the chunk as absent and died on `cannot reshape array of size 0`. 5212 such files
        # out of 18705 on the first whole-sheet fetch. An absent chunk must be an absent FILE, so the bytes are
        # fetched first and the file only appears, whole, once they are in hand.
        try:
            blob = get(B + '/' + urllib.parse.quote(vpre + '0/' + rel))
        except Exception:
            return        # an absent chunk is an absent file; zarr then fills it with fill_value
        with open(p + '.part', 'wb') as fh:
            fh.write(blob)
        os.replace(p + '.part', p)

    with ThreadPoolExecutor(o.jobs) as ex:
        list(ex.map(one, sorted(want)))
    print('fetched: %d chunk files' % sum(len(f) for _, _, f in os.walk(raw)))

    # --- write the villa-format dataset ---------------------------------------------------------------------------
    S = zarr.open(raw, mode='r')
    N = o.planes
    lo = hi = w = None
    if o.full:
        f = np.linspace(0, Z - 1, N)
        lo = np.floor(f).astype(int)
        hi = np.minimum(lo + 1, Z - 1)
        w = (f - lo)[:, None, None]
        z0, z1 = 0, Z
        how = 'all %d planes interpolated to %d' % (Z, N)
    else:
        c = o.centre if o.centre is not None else Z // 2
        z0 = max(0, min(Z - N, c - N // 2))
        z1 = z0 + N
        how = 'planes %d-%d (centre %d) of %d' % (z0, z1, c, Z)
    print('writing %s: %s, order %s' % (name, how, 'REVERSED' if o.reverse else 'as stored'))

    blosc = Blosc(cname='zstd', clevel=3, shuffle=2)

    def grp(nm, comp, sep):
        g = zarr.open_group(os.path.join(out, nm + '.zarr'), mode='w', zarr_format=2)
        for n in range(6):
            g.create_array(str(n), shape=(N, -(-HH // 2 ** n), -(-WW // 2 ** n)), chunks=(N, 128, 128), dtype='uint8',
                           compressors=comp, chunk_key_encoding={'name': 'v2', 'separator': sep}, fill_value=0)
        return g

    gv = grp(name, None, '.')
    written = 0
    for k, (y, x) in enumerate(sorted(want)):
        y0, x0 = y * cy, x * cx
        y1, x1 = min(y0 + cy, HH), min(x0 + cx, WW)
        blk = np.asarray(S[z0:z1, y0:y1, x0:x1])
        if blk.max() == 0:
            continue
        if o.full:
            blk = (blk[lo] * (1 - w) + blk[hi] * w).astype(np.uint8)
        gv['0'][:, y0:y1, x0:x1] = blk[::-1] if o.reverse else blk
        written += 1
        if k % 200 == 0:
            print('  volume %d/%d' % (k, len(want)), flush=True)
    print('  volume: %d non-empty chunks written' % written)

    # Pyramide du volume. villa ne s en sert pas pour entrainer (volume_scale 0) mais son choix de patchs lit le
    # niveau 3 pour savoir ou il y a de la matiere : sans pyramide, le jeu de donnees est vu comme vide et aucun
    # patch n est retenu. On ne descend que la ou le niveau precedent a ete ecrit.
    prev = set((y * cy // 128, x * cx // 128) for y, x in want)
    for n in range(1, 6):
        src, dst = gv[str(n - 1)], gv[str(n)]
        cur = set((a // 2, b // 2) for a, b in prev)
        for i, (a, b) in enumerate(sorted(cur)):
            y0, x0 = a * 128, b * 128
            blk = np.asarray(src[:, 2 * y0:2 * y0 + 256, 2 * x0:2 * x0 + 256])
            if blk.size == 0 or blk.max() == 0:
                continue
            h, w2 = blk.shape[1] // 2 * 2, blk.shape[2] // 2 * 2
            if h == 0 or w2 == 0:
                continue
            red = blk[:, :h, :w2].reshape(N, h // 2, 2, w2 // 2, 2).max(axis=(2, 4))
            dst[:, y0:y0 + red.shape[1], x0:x0 + red.shape[2]] = red
            if i % 500 == 0:
                print('  niveau %d : %d/%d' % (n, i, len(cur)), flush=True)
        print('  niveau %d : %d chunks' % (n, len(cur)))
        prev = cur

    if lab:
        for nm, src in ((name + '_inklabels_v2', 'inklabels'), (name + '_supervision_mask_v2', 'supervision')):
            g = grp(nm, blosc, '/')
            A = np.asarray(zarr.open(os.path.join(lab, src + '.zarr'), mode='r')['0'][:]) > 0
            if A.shape != (HH, WW):
                # Labels are published on one volume's canvas. Cropping them onto another would misplace every
                # letter and nothing downstream would complain, so refuse instead.
                sys.exit('labels are %dx%d but the volume is %dx%d: this label release belongs to a different '
                         'surface volume of this segment. Pick the matching --volume, or drop --labels.'
                         % (A.shape[0], A.shape[1], HH, WW))
            for y in range(0, HH, 128):
                b = A[y:y + 128]
                if b.any():
                    g['0'][:, y:y + b.shape[0], :b.shape[1]] = np.broadcast_to(b[None] * np.uint8(255), (N,) + b.shape)
            cur = A
            for n in range(1, 6):
                h, w2 = cur.shape[0] // 2, cur.shape[1] // 2
                cur = cur[:2 * h, :2 * w2].reshape(h, 2, w2, 2).max(axis=(1, 3))
                for y in range(0, h, 128):
                    bb = cur[y:y + 128]
                    if bb.any():
                        g[str(n)][:, y:y + bb.shape[0], :bb.shape[1]] = np.broadcast_to(bb[None] * np.uint8(255),
                                                                                        (N,) + bb.shape)
            print('  %s: %.2f %% of the canvas' % (nm, 100 * A.mean()))

    # --- coordinate maps (tifxyz) -------------------------------------------------------------------------------
    # villa SILENTLY SKIPS a segment that has no x.tif: gather_segments() tests `any(segment_dir.rglob("x.tif"))`
    # and does `continue`. The dataset then builds perfectly, training finds zero segments, and the error it prints
    # is "InkDataset produced no training patches after applying supervision masking" - which accuses the
    # supervision mask of a fault in a segment that was never looked at. Cost an evening on 2026-09-23.
    # The real maps are published under mesh/ for each surface volume, they weigh 9 MB, and they carry that
    # volume's own canvas. We fetch those rather than linking the render's, which describe a DIFFERENT flattening
    # of the same sheet and would put a wrong geometry behind a name that looks right.
    import shutil, tifffile
    stamp = o.volume.rsplit('-', 1)[-1]
    mesh = [p for p in ls(seg + 'mesh/') if stamp in p and p.rstrip('/').endswith('.tifxyz')]
    meta = {}
    if len(mesh) == 1:
        td = os.path.join(out, '_tifxyz')
        print('tifxyz: %d files from %s' % (fetch_dir(mesh[0], td, o.jobs), mesh[0]))
        for f in ('x.tif', 'y.tif', 'z.tif'):
            os.replace(os.path.join(td, f), os.path.join(out, f))
        meta = json.load(open(os.path.join(td, 'meta.json')))
        shutil.rmtree(td, ignore_errors=True)
        sc = meta.get('scale') or [1, 1]
        sc = sc if isinstance(sc, (list, tuple)) else [sc, sc]
        xs = tifffile.imread(os.path.join(out, 'x.tif')).shape
        got = (round(xs[0] / sc[0]), round(xs[1] / sc[1]))
        # A map whose canvas is not this volume's canvas is worse than no map: it passes villa's check and puts
        # every patch at the wrong place. Checked, not assumed.
        if abs(got[0] - HH) > 2 or abs(got[1] - WW) > 2:
            sys.exit('the coordinate maps describe a %dx%d canvas and the volume is %dx%d: this tifxyz does not '
                     'belong to this volume.' % (got[0], got[1], HH, WW))
        print('  canvas %dx%d, matches the volume' % got)
    else:
        print('WARNING: no single tifxyz matching %r under mesh/ (%d found). Without x.tif, villa will skip this '
              'segment in silence and training will report an unrelated error.' % (stamp, len(mesh)))
    meta.update({'scroll_source': o.scroll, 'segment': o.segment, 'volume': o.volume, 'type': 'seg',
                 'format': 'tifxyz', 'tifxyz_source': mesh[0] if len(mesh) == 1 else None})
    json.dump(meta, open(os.path.join(out, 'meta.json'), 'w'), indent=1)
    json.dump({'source': B + '/' + vpre, 'source_shape': [Z, HH, WW], 'planes': N, 'plane_window': how,
               'order': 'reversed' if o.reverse else 'as stored', 'labels': o.labels, 'region': o.region,
               'chunks_fetched': len(want)}, open(os.path.join(out, 'build.json'), 'w'), indent=1)
    print('%s ready. What was built is recorded in build.json.' % out)
    return 0


if __name__ == '__main__':
    sys.exit(main())
