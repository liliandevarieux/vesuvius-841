# PHerc. 841 — ink detection, measured

An independent, single-laptop attempt at reading PHerc. 841, and the measurements that came out of it.
Ink detection only: no virtual unwrapping. Everything here runs on one RTX 4060 Laptop (8 GB).

**Goal:** publish the first reading of PHerc. 841. The organisers have surfaced ink on this scroll and published
labels and predictions for it, but no transcription of its text has been published. That is the target.

**Status, honestly:** the model reads the labelled ink of all three published segments, and we are working outside the
labelled area. Nothing is claimed here about unpublished letters — when there is something to claim it will be stated
with its evidence, not implied by a repository.

## What is in here

The scripts behind numbers posted publicly in
[ScrollPrize/villa#1867](https://github.com/ScrollPrize/villa/issues/1867), plus the working notes.

| | |
|---|---|
| `scripts/mesure_sens.py` | depth-direction test: mean prediction inside labelled ink minus mean over inspected non-ink, and correlation with the organisers' published `pred.tif` |
| `scripts/mesure_zc.py` | sweep of which 65 of the 109 planes are taken |
| `scripts/mkseg65.py`, `mkcrop2.py` | build a villa-format dataset from a published surface volume, either direction, either slice |
| `scripts/prep_seg.py`, `prep_sup.py`, `prep_feuille.py` | fetch only the chunks of a segment that are actually needed |
| `scripts/prep_seau.py`, `mesure_seau.py` | the array-vs-segment test on the label-bucket renders |
| `scripts/blobs_seg.py` (one reader), `cand_plein.py` (two readers) | find letter-sized blobs outside the labels |
| `scripts/planche_117.py`, `verdict_ligne.py`, `bande_ligne.py` | judge them |
| `scripts/page_lecture.py`, `lignes_zoom.py`, `cmp_lecteurs.py`, `coudre_pred.py` | stitch a whole segment and render it as a readable page |
| `scripts/run4_queue*.sh` | the drivers, kept as worked examples of how the pieces are chained |
| `METHOD.md` | the rules this project works by, and the instruments rejected for failing their controls |
| `opendata_to_villa.py` | build a villa `ink_detection` dataset from any published open-data segment |
| `results/*.json` | the raw measurements, written by the measurement scripts themselves (`JSON=<path> python scripts/mesure_sens.py ...`) |
| `verify_claims.py` | re-derives all 41 numbers in `MEASUREMENTS.md` from those JSON files and exits non-zero if any of them has drifted |

## The setup these numbers come from

- **Model:** villa's `vesuvius.ink_detection`, trained on one segment only — `PHerc0841/w00`, from the label-bucket
  render (65 planes, 4.681 µm, `w00_transformed`), in stored order. Teacher: the organisers' April 2026 prediction
  reprojected into our geometry, plus ~0.36 cm² of hand labels. Checkpoint 16 000 steps.
- **Evaluated on:** the two other published segments of the same scroll, which it has never seen, against the
  organisers' own `inklabels` (the 2026-09-18 release) on the published 2.403 µm surface volumes.
- **Metric:** separation = mean prediction inside labelled ink − mean prediction over inspected non-ink; plus
  correlation with the organisers' published prediction over the inspected region. Three 1500×1500 windows per
  segment.

## What we got wrong, in public

Both corrections are in the issue thread, and both came from a reviewer
([@AndreasHad04](https://github.com/AndreasHad04)) checking our claims:

1. We wrote that two PHerc0841 **segments** are published with the depth axis reversed. Wrong attribution: the
   direction belongs to the **array**, not the segment. Our model is trained on the label-bucket render in stored
   order, and that render campaign is itself reversed — the word `reverse` is in the organisers' own canonical
   prediction filename for all three segments. A model silently inherits the convention of whichever array it was
   trained on.
2. We reported a large dependence on which 65 of the 109 planes are taken, as if it were a property of the slice.
   It is not: for a model that stays on its own array the centred window is safe. Our direction effect and our slice
   effect are the same phenomenon measured twice — the cost of running a model off the array it was trained on.

The measurements themselves stand; only their explanation changed. Keeping the wrong version visible with the
correction next to it is deliberate.

## The tool: `opendata_to_villa.py`

villa's `ink_detection` reads datasets shaped like the ones in the organisers' label bucket. The open data publishes
something else — surface volumes with their own plane count and resolution, and labels as separate zarr arrays. Going
from one to the other is what let a model trained on `w00` read two segments it had never seen, and it is not
documented anywhere, so it is packaged here.

```
# what does this segment actually have?
python opendata_to_villa.py --scroll PHerc0841     --segment 20260221022814-auto_grown_20260220174252405 --list

surface volumes:
    2.403um-0.22m-77keV-volume-20260319124803.zarr
    9.366um-1.2m-113keV-volume-20250821151531.zarr
label releases:
    2.403um-volume-20260319124803/20260918
published predictions:
    PHerc0841-...-new_canon_autoresearch_recipe-tile256-stride128.tif
```

```
# how much would the inspected zone cost? (fetches only the labels, a few MB)
python opendata_to_villa.py --scroll PHerc0841     --segment 20260221022814-auto_grown_20260220174252405     --volume 2.403um-0.22m-77keV-volume-20260319124803 --labels 20260918     --out /tmp/t --region inspected --dry-run

volume 109x14660x19100, chunks 109x128x128, 17250 chunks in the plane
region 'inspected': 1573 chunks of 17250 (2.62 GB uncompressed)
```

Drop `--dry-run` to build it. `--region` takes `inspected` (the supervision mask), `labels`, or `Y0,Y1,X0,X1`;
`--planes`, `--centre`, `--full` and `--reverse` decide which planes are taken and in which order. Only the chunks the
region needs are fetched, and a missing chunk is treated as empty rather than as an error.

Two things it does on purpose:

- **It writes `build.json`** next to the dataset, recording the source volume, the plane window and the direction. A
  model inherits the convention of the array it was trained on, silently, and that is what cost us a day
  ([#1648](https://github.com/ScrollPrize/villa/issues/1648)). A dataset that cannot say how it was built is a trap.
- **It refuses to cross label releases with the wrong volume.** The 2.403 µm labels on the 9.366 µm canvas would crop
  silently and misplace every letter, so it checks the two canvases *before* fetching anything and stops:

  ```
  labels are 14660x19100 but the volume is 3760x4900: this label release belongs to a different
  surface volume of this segment. Pick the matching --volume, or drop --labels.
  ```

## Checking the numbers

```
python verify_claims.py
41 claims checked against results/*.json
OK
```

It parses the tables in `MEASUREMENTS.md`, compares every cell to `results/*.json`, and exits 1 on any mismatch — so a
number cannot drift out of the documentation unnoticed. It has been checked to fail: altering one cell from 70.1 to
70.2 produces `DRIFT: slice centre 32 separation: document says 70.2, measurement says 70.1` and exit code 1. The
first run of it found a real error, a slice value copied into the wrong column, which is why it exists.

## Running any of this

The scripts assume WSL with a checkout of [villa](https://github.com/ScrollPrize/villa) at `~/vesuvius/villa` and its
venv, a data root at `~/vesuvius/ink-dataset/<scroll>/<segment>/`, and write their images to a Windows path under
`/mnt/c/...`. Two constants at the top of each file carry that; adapt them and nothing else should need changing.
They are working scripts, not a package.

## License

MIT. See `LICENSE`.
