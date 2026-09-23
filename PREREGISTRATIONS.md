# Pre-registrations

What we intend to measure, written **before** the result is known, with what would count as a failure. Results get
posted whichever way they come out. Practice borrowed from [@AndreasHad04](https://github.com/AndreasHad04), who does
the same in [villa-apple-silicon](https://github.com/AndreasHad04/villa-apple-silicon).

---

## PR-1 — Does the depth direction belong to the array or to the segment?

*Registered 2026-09-23, before the run. Scripts: `scripts/prep_seau.py`, `scripts/mesure_seau.py`,
`scripts/run4_queue24.sh`.*

**Claim under test.** Our w00-trained model needed the published 2.403 µm surface volume of ag174 reversed. If that is
a property of the *array* and not of the segment, then on the **label-bucket render** of ag174 — the same 65-plane
4.681 µm array family our model was trained on — the model should prefer the **stored** order instead.

**Design.** Same checkpoint (`ink_841_human7n`, step 16 000). Two windows chosen on the bucket canvas by label
density, 1500×1500. Both directions. Scored against that bucket's own `_inklabels_v2`.

**Prediction.** Stored order wins on the bucket render, by a margin comparable to the one reversing won by on the
published volume.

**What would invalidate it.** Stored order scoring at or below reversed on the bucket render. That would mean the
array explanation does not account for our model's behaviour, and something segment-specific is left unexplained.

**Note.** @AndreasHad04 has since run a wider version of this — three segments, three array families, both directions,
a label-free direction rule — and reports the same conclusion. Ours is now a check, not news, and is kept registered
because it was written before that comment landed.

---

## PR-2 — Are we training on the wrong array?

*Registered 2026-09-23, run not started.*

**Claim under test.** We train on the 4.681 µm label-bucket render, with a 2 µm-family prediction reprojected as
teacher. @AndreasHad04's table shows the render is a harder surface even for the organisers' own models: on the w00
render, their 2 µm-family canonical prediction scores 0.8229 while their render-trained `ps48` prediction scores
0.9492, on the same labels. That suggests our array and our teacher are mismatched.

**Design.** Retrain on the published **2.403 µm surface volume** of w00 — same hand labels, same seed, same number of
steps, same teacher, only the training array changing. Evaluate on the same three held-out windows of ag144 and ag174
used in `MEASUREMENTS.md`, with the same metric.

**Prediction.** Separation improves on the held-out segments, and the direction question disappears because training
and evaluation then share an array family.

**What would invalidate it.** No improvement, or a drop. That would mean the render is not the handicap, and the gap
between 0.8229 and 0.9492 is about the teacher's own training surface rather than about ours.

**Cost, stated in advance so it cannot be quietly abandoned — and measured, not guessed.**

```
python opendata_to_villa.py --scroll PHerc0841 --segment 20260220213127-w00     --volume 2.403um-0.22m-77keV-volume-20260319124803 --labels 20260918     --out /tmp/w00 --region inspected --dry-run

volume 109x16460x18560, chunks 109x128x128, 18705 chunks in the plane
region 'inspected': 1904 chunks of 18705 (3.17 GB uncompressed)
```

**3.17 GB** and one training run — `--region labels` would be 1.67 GB. When this was first written it said "of the
order of 20 GB", which was the size of a *whole sheet* fetched for reading, not of the zone a training run needs. The
correction makes the experiment six times cheaper than registered, so there is no cost argument for not doing it.

**Open question, and its answer, both recorded here.** Our runs combine the organisers' prediction as teacher with
~0.36 cm² of hand labels, and those labels live on the render's canvas. Carrying them to a different array unchanged
would not be legitimate, so before registering the run as single-variable we measured both label sets:

| | canvas | labelled fraction |
|---|---|---|
| hand labels used for training, on the 4.681 µm render | 15872 × 18944 | 2.07 % |
| published `20260918` labels, on the 2.403 µm surface volume | 16460 × 18560 | 2.02 % |

The same region of the sheet, to within the difference between the two canvases. So the published label release can be
used directly on the 2.403 µm volume and the comparison stays single-variable, with no hand re-projection. The teacher
also exists natively on that canvas
(`PHerc0841-…-20260417190342-new_canon_autoresearch_recipe-tile256-stride128.tif`), so it does not have to be
re-projected either — our current teacher is a reprojection *of that file* into the render's geometry.

One thing this does **not** settle: which 65 of the 109 planes to train on. The measured optimum of 50–54 was found
with a render-trained model evaluated on this volume, so it does not transfer to a model trained on the volume itself.
The run will use villa's centred window and that choice is recorded here as a default, not as a measurement.

---

## PR-3 — Is the aligned group of blobs on segment B a line of text?

*Registered 2026-09-23 at 15:10, **before** the equivalent data exists for the second segment: its census had not been
computed when this was written (its inference queue was still waiting on the GPU). Scripts:
`scripts/cand_plein.py`, `scripts/verdict_ligne2.py` (the selection control), `scripts/align_test.py` (the
permutation test).*

**What happened first, including the part that failed.** A whole-sheet census of one segment produced 117 blobs of
letter size lying outside the organisers' label mask, each seen by two independent readers. Three of them fell close
to a single line whose angle matched the independently measured text-line angle. Our model's response inside those
blobs (69.4) was higher than on the certain labelled letters (47.7), and we first read that as confirmation.

**That reading does not survive its control.** The 117 blobs were *selected* for being visible to both readers, so
they start ahead of unselected letters by construction. The comparison that keeps the selection fixed is on-line
blobs against off-line blobs, and area turns out to drive the score (correlation of +0.378 between log area and
response):

| area | on the line | off the line | difference |
|---|---|---|---|
| all | 69.4 (n=16) | 55.5 (n=101) | +13.9 ± 6.6 |
| ≥ 0.2 Mpx | 77.6 (n=5) | 78.8 (n=18) | **−1.2 ± 7.7** |

At matched size there is no difference. **The model's response says nothing about the line**; it reflects how the
blobs were picked and how big they are.

**What is left is geometry alone, and it is ambiguous.** Permutation test, 2000 draws, breaking the link between each
blob's two coordinates while keeping both distributions, counting the most blobs within 150 px of any line at the
measured text angle:

| set | best alignment | p |
|---|---|---|
| all 117 blobs | 8 blobs | **0.354** |
| the 13 blobs of ≥ 0.3 Mpx | 4 blobs | **0.018** |

The second row is the interesting one and it is also the one chosen *after* seeing the data, on two thresholds tried.
It is a hypothesis, not a result.

The instrument does pass its own negative control, which is the one thing here that was not chosen after the fact:
run on the same 13 blobs at a nonsense angle of 45° instead of the measured 8.0°, it returns 2 blobs and **p = 0.748**.
It is not an alignment-finding machine that fires on any point cloud; it is specific to the angle it is given.

```
python scripts/align_test.py cand_<segment>.txt 8.0  0.3 150 2000   ->  4 blobs, p = 0.018
python scripts/align_test.py cand_<segment>.txt 45.0 0.3 150 2000   ->  2 blobs, p = 0.748
```

**The pre-registered test.** The second segment of this scroll is being read now and its census has not been computed.
When it is, the same procedure will be run on it, with **the threshold fixed here at 0.3 Mpx**, the same 150 px
tolerance, the same 2000-draw permutation, and that segment's own independently measured text-line angle.

**Prediction.** If these aligned groups are lines of text, the second segment shows an alignment of at least 4
letter-sized blobs at p < 0.05.

**What would invalidate it.** p ≥ 0.05 on the second segment. Then the first segment's 0.018 is what picking the best
of two thresholds on one dataset buys, the line is not established, and it will be said so in those words.

**What is not claimed either way.** That any of these blobs is a letter. That question belongs to the eye and to the
scan, not to this test.
