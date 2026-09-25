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

**RESULT, 2026-09-23 15:14 — the prediction holds.** On the bucket render of `ag174`, separation 56.9 in stored order
against 30.3 reversed: it prefers the **stored** order, the opposite of what the same model needed on the published
surface volume of the same segment (27.3 stored against 75.9 reversed). Same segment, opposite answers, so the
direction belongs to the array. Numbers, per window and with their weakness, in `MEASUREMENTS.md` §4 and
`results/array_ag174.json`.

**The part that does not support the conclusion, said here rather than left out.** The two windows disagree: window 1
mildly prefers reversed (35.5 against 27.5) and only window 2 carries the mean (86.4 against 25.2). Two windows, split
one each way, is thin. The conclusion rests on @AndreasHad04's wider ablation; this is a check that agrees with it, and
it would not stand on its own.

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

### PR-2 — interim, and two declared deviations (2026-09-23, 16:35)

**The premise checks out, measured on our own data.** The teacher, scored against the same human labels, reaches
**IoU 0.713** on the published 2.403 µm volume against **0.583** for the best teacher on the 4.681 µm render
(precision 84 %, recall 82 %). +0.13 with nothing changing but the array. That is an independent confirmation of
@AndreasHad04's 0.8229-against-0.9492 observation, on different data and a different metric, and it is why this
experiment is worth running rather than merely registering.

**Deviation 1 — the held-out windows could not be transposed, so new ones were chosen.** The plan said "same hand
labels, same seed, same number of steps, only the training array changing", which implied holding out the same three
physical windows. Registering the two canvases by their label masks fails: best IoU **0.125**, reached *at the edge*
of the search range. The render and the published volume are not two samplings of one grid, they are **two different
flattenings of the same sheet** — which the current teacher's filename, `new_canon_20260417_recale`, said all along.
Three new 1500×1500 windows are therefore chosen on the published canvas by the same rule as the originals (densest in
labels, separated). Same count, same size. The primary evaluation is on the two other segments, never seen under
either arm, so it is unaffected.

**Deviation 2 — the first build was rejected for being five times too small, before any training.** Fetching only the
inspected zone gave a dataset covering 10.2 % of the canvas against 72.7 % for the render dataset, and 0.91 % of the
canvas in sampleable ink against 4.83 %. A drop in performance would have been indistinguishable from a shortage of
training data, so the run would have measured nothing. The whole sheet (~23 GB) is being fetched instead. Recorded
here because the discarded build is the kind of thing that quietly becomes the published result.

### PR-2 — two more notes, written while the run was starting (2026-09-23, 19:15 and 19:45)

**Note 3 — the training array is built in reversed layer order, and this was nearly got wrong.** The registered
design says "only the training array changing". It does not say in which *layer order* that array is built, and the
first build took the published volume as stored. That would have been wrong, and wrong in a way that produced a
number rather than an error. PR-1 measured, on this very data, that the published surface volumes run in the layer
order opposite to the render's — on ag174's published volume, reversed scores **106.2** against **31.3** direct.
The `20260918` labels and the native teacher live in the render's order, the starting checkpoint was trained in it,
and our own evaluation crops for ag144 and ag174 are already built with `REV=1`. Trained as stored, the run would
have measured a **layer direction** while claiming to measure an **array**, and the drop would have been published
here as "the 2.403 µm volume is the worse surface". Caught at 19:15, before any training; `build.json` now records
`"order": "reversed"`. The single-variable construction is the one that puts the training array in the same order as
its own labels. That this needed saying — a day after we published the measurement that says it — is itself worth
recording.

**Note 4 — the primary evaluation had to be written, because the chain did not do it.** The registered design
evaluates on "the same three held-out windows of ag144 and ag174, with the same metric". The training chain's
evaluation script is hard-coded to the render's own test windows. Left alone, PR-2 would have been concluded on a
**secondary** measurement that looks exactly like a result. Both are now produced and labelled: the primary on
ag144 and ag174, same metric and the **same crops as the control arm**, so the two arms see byte-identical inputs;
the secondary on the render's windows, which is where the control arm was scored and is therefore a fair comparison
of its own. The primary is measured **in both layer orders**, because the registered prediction has two halves —
"separation improves **and** the direction question disappears" — and inferring only the reversed order would have
left the second half untestable. A prediction of which only one half is measured can neither succeed nor fail.
Before the test arm existed, the instrument was run against the published table and reproduced it exactly:
**27.3 / 75.9** on ag174 and **40.0 / 89.7** on ag144.

**One fact about the tool, for anyone reusing it.** `opendata_to_villa.py` did not fetch the segment's coordinate
maps, and villa silently skips a segment whose directory has no `x.tif` — the training error it then prints blames
the supervision mask of a segment that was never looked at. The maps are published under `mesh/` for each surface
volume, weigh 9 MB, and carry that volume's own canvas; the tool now fetches them and **verifies that their canvas
matches the volume** before keeping them. Linking the render's maps instead would have passed villa's check and put
every patch in the wrong place, which is worse than the missing file.

---

## PR-3 — Is the aligned group of blobs on segment B a line of text?

*Registered 2026-09-23 at 15:10, **before** the equivalent data exists for the second segment: its census had not been
computed when this was written (its inference queue was still waiting on the GPU). Scripts:
`scripts/blobs_seg.py` (the census that produced the 117), `scripts/verdict_ligne2.py` (the selection control),
`scripts/align_test.py` (the
permutation test).*

**What happened first, including the part that failed.** A whole-sheet census of one segment produced 117 blobs of
letter size lying outside the organisers' label mask. Three of them fell close
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

> **Correction, 2026-09-23 17:00.** This section first said the 117 blobs were *"each seen by two independent
> readers"*. That is wrong, and it was wrong in our favour. The census (`scripts/blobs_seg.py`) uses a **single**
> reader: the organisers' published prediction, thresholded, letter-sized, outside the label mask. The two-reader
> census is a different set entirely — `scripts/cand_plein.py`, which requires our model to respond as well. When
> this was written our model had only read the inspected strip of that segment, so that census returned 2 blobs;
> run the same evening on the whole sheet it returns 95 of letter size out of 560 outside the labels. Either way,
> the 117 come from one reader, and our own model was used to *score* the blobs afterwards, never to select them.
>
> What this changes: the candidate set is weaker than described, so a reader should trust it less. What it does not
> change: every number above was computed on the file that actually exists, and the selection-bias argument stands
> unaltered — blobs chosen for being visible to *one* reader are just as selected as blobs chosen for being visible
> to two. It also removes a circularity we did not have: had our model both picked and scored the blobs, the 69.4
> would have meant nothing at all.
>
> The error is left visible rather than edited away. A pre-registration that is quietly rewritten is not one.

> **Second correction, same day, 17:45 — and this one was found by a control built to protect this very test.**
> Above, the aligned blobs are said to lie at an angle matching *"the independently measured text-line angle"*, +8.0°.
> Before running the pre-registered test on the second segment, we checked that the angle instrument reproduces that
> known value. It does — but it also showed where +8.0° had come from: `page_lecture.py` run on **the organisers'
> prediction**, which is the same source as the 117 blobs. The angle was therefore *not* independent of the blobs,
> and the segB geometry was partly circular.
>
> The same instrument run on **our** model's prediction of that whole sheet — a model that never saw this segment —
> returns **+7.0°** (contrast 1.6×, against 1.7× for theirs). So a genuinely independent measurement agrees to
> within 1°, which is two steps of the instrument's own 0.5° grid. The circularity was real and the number survives
> it.
>
> On the second segment the angle is taken from our prediction and the blobs from theirs, so the two instruments are
> distinct by construction. That was already how the pre-registered run was built, before this was found.

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

### RESULT, 2026-09-23 18:17 — the prediction fails

The second segment was read in full that afternoon (147 tiles), its census computed with the same script and the same
0.04 Mpx letter threshold, and its text-line angle measured with the same instrument on our own whole-sheet
prediction: **+8.0°**, contrast 1.6× — the same angle as the first segment, measured independently of it.

| | blobs of ≥ 0.3 Mpx | best alignment | p |
|---|---|---|---|
| segment A, at its measured +8.0° | 15 of 103 | 3 blobs | **0.405** |
| segment A, negative control at 45° | 15 of 103 | 2 blobs | 0.850 |

**p = 0.405.** The registered invalidation criterion was p ≥ 0.05. So, in the words registered before the run: the
first segment's 0.018 is what picking the best of two thresholds on one dataset buys, **the line is not established**.

The test had comparable power on both segments — 15 letter-sized blobs here against 13 there — so this is not a
failure to look. The instrument passes its negative control on this segment too, returning p = 0.850 at a nonsense
angle, so it is not broken either. It simply found nothing.

**What survives.** Nothing about the line. The angle of the text lines, +8.0° on one segment and +7.0° on the other
measured by an instrument independent of both censuses, is a real property of this flattening; it says nothing about
whether any group of blobs lies on one. And the 117 and 103 blobs remain what they always were — places where a
model responds outside the labels, not letters.

**What this cost and what it bought.** One afternoon of GPU. It bought the removal of a claim we would otherwise
have carried into everything built afterwards, and which looked, for about five hours, like our best result.

---

## PR-4 — Is PR-2's array effect larger than the effect of changing the seed?

*Registered 2026-09-23 22:20, before the run started and before the primary measurement of PR-2 had been read.
Written because PR-2, as registered, compares one run against one run, and tonight showed that a single number on
these metrics carries an uncertainty of the same order as the effect being looked for.*

**What tonight established, and what it did not.** On the secondary metric (the render's three held-out windows),
the volume-trained arm scores **89.0** at 16 000 steps against **78.4** for the registered render-trained control:
**+10.6**. But the same arm's own trajectory across its eight checkpoints has a standard deviation of **5.2**, and
the control run `ink_841_human7` — same configuration as the control, different execution — swings by **12.7**
between its last two checkpoints. An effect of +10.6 measured once on each side is about two standard deviations of
a noise we have measured. That is a signal. It is not a result.

**A second problem, found while checking the first.** The registered control `ink_841_human7n` trained before the
w00 teacher labels were rebuilt at 00:55 on 2026-09-23; those labels no longer exist. **The registered control is
therefore not reproducible.** `ink_841_human7` is the same configuration trained after that rebuild, on the labels
still on disk, and it scores 65.9. Taking it as the control would turn +10.6 into +23.1. Choosing between the two
after seeing both numbers is exactly what a pre-registration exists to prevent, so PR-2 keeps `human7n`, the
reference declared at 11:28 today, and this note records the alternative rather than using it.

**Claim under test.** The difference between training arrays is larger than the difference between two seeds of the
same array.

**Design — a 2×2, array × seed, every cell on labels that still exist.**

| | seed 42 | seed 43 |
|---|---|---|
| render, 4.681 µm (`w00`) | `ink_841_human7` — already trained on the current labels | `ink_841_w00_s43` — to run |
| published volume, 2.403 µm reversed (`w00v24`) | `ink_841_pr2v24` — already trained | `ink_841_v24_s43` — to run |

Two new runs. Everything else is held: same starting checkpoint (`ink_w00_128_acc4/ckpt_080000.pth`), same 16 000
steps, same teacher, same configuration but for `out_dir`, `seed` and — between rows — the training array. Both new
runs are evaluated at step 16 000 on **both** metrics: the render's three windows (secondary) and the three held-out
windows of ag144 and ag174 in both layer orders (primary).

**Prediction.** |array effect| > |seed effect| in both directions: the two volume cells stay above the two render
cells, and the gap between rows exceeds the gap within each row.

**What would invalidate it.** If the seed effect within either row is as large as the effect between rows, this
design does not establish an array effect, and PR-2's result must be reported as compatible with run-to-run
variation. That would not mean the published volume is not the better surface — it would mean one run per arm
cannot show it, and that the honest next step is replicates, not a louder claim.

**Stated in advance so it cannot be quietly dropped.** Four cells is the smallest design that separates the two
effects at all, and it still gives one run per cell: it can show that the array effect is *not* established, but it
cannot establish it tightly. If PR-4 comes out favourable, the correct wording is "the array effect survives a seed
change", not "the array effect is proven".

**Cost.** Two trainings of 1 h 50 and two evaluations of about 20 minutes, on a GPU that would otherwise be idle
overnight. No new data is fetched.

### PR-4, amendment — the render row and the volume row were not built from the same teacher

*Written 2026-09-23 23:30, while the first new cell was at step 3 858 of 16 000. **No number exists for either
seed-43 cell**, and none will until about 00:45. Two of the four cells were already measured when PR-4 was
registered, and they still are; what this amendment changes is how the square is read, and it is written before the
half of the square that PR-4 actually adds exists.*

**What was found, and how.** Writing the reader that will print the square, the provenance of each cell's training
labels was traced back to the command that built them. They are not the same across rows:

| cell | array | teacher used to build the labels | threshold rule |
|---|---|---|---|
| `ink_841_human7n` — PR-2's registered control | render | `new_canon_20260417_recale.tif` | **absolute, `T_HI=190 T_LO=131`** |
| `ink_841_pr2v24` — PR-2's test arm | published volume | `new_canon_natif.tif` (same teacher, native canvas) | equal area, `T_EQ=1 DELTA=8` |
| `ink_841_human7` — PR-4's render / seed 42 | render | **`ps48_640_640_smooth_0.1_w00_ckpt_130000_forward_210326.tif`** | **absolute, `T_HI=190 T_LO=131`** |
| `ink_841_w00_s43` — PR-4's render / seed 43 | render | same as `human7` (the 00:55 labels, untouched since) | same as `human7` |
| `ink_841_v24_s43` — PR-4's volume / seed 43 | published volume | same as `pr2v24` (the 19:40 labels, untouched since) | same as `pr2v24` |

The render row was rebuilt at 00:55 on 2026-09-23 by `run4_queue11.sh`, which deliberately reverted the teacher to
`ps48` in order to isolate a different effect — the lot-9 label corrections — and which set absolute thresholds at
the same time. That rebuild is the reason PR-2's registered control is not reproducible; what had not been noticed
is that it also makes **PR-4's two rows differ by three things at once: the array, the teacher, and the rule that
turns the teacher into labels.**

**What this does and does not break.**

- ~~**PR-2 is unaffected.** Its two arms, `human7n` and `pr2v24`, share the teacher and the threshold rule.~~
  **Struck 23:55, forty minutes after being written, and the correction is the reason PR-5 exists.** Checking the
  command that actually built `human7n`'s labels (`run4_queue10.sh` line 24, forwarded through `run4_launch.sh`
  line 12, where `T_HI`/`T_LO` take final precedence in `mkteacher.py`) shows `T_HI=190 T_LO=131` — absolute
  thresholds, not equal area. The claim above came from a summary written later in `JOURNAL.md`, from memory,
  which said the volume arm was built "with the same settings as `human7n` (`T_EQ=1, DELTA=8`)". The script is the
  record and the summary was wrong. **PR-2's two arms differ by three things, not one**: the array, the rule that
  turns the teacher into labels, and the version of the human labels underneath (`w00_inklabels_human7`, which
  carries our lot-9 arbitration corrections, against `w00v24_inklabels_v2`, the published labels of 2026-09-18
  without them). The +7.1 and +9.0 are real measurements of *something*; they do not isolate the array.
- **PR-4's within-row seed comparison is unaffected**, in both rows: `human7` vs `w00_s43` share the 00:55 labels
  and differ only in `seed`; `pr2v24` vs `v24_s43` share the 19:40 labels and differ only in `seed`. This is the
  quantity PR-4 exists to produce, and it is clean.
- **PR-4's row difference is confounded** and will not be used as an array effect.

**How the square will therefore be read.** PR-4 supplies the **seed effect**, measured twice, once inside each row.
The **array effect** it is compared against is PR-2's matched pair, not PR-4's row difference. The claim under test
is unchanged — *the difference between training arrays is larger than the difference between two seeds of the same
array* — and the decision rule becomes: the array effect is established as surviving a seed change if PR-2's matched
effect on a segment exceeds **both** seed effects measured on that segment. If either seed effect is of the same
order, this design does not establish an array effect and the next step is replicates.

**The reader prints both.** `scripts/carre_pr4.py` still prints the naive row difference, labelled as confounded, so
that nothing is hidden by the change of rule; the verdict is taken from the matched comparison.

**What is deliberately not done tonight.** A matched render row is buildable — rebuild `w00`'s teacher labels from
`new_canon_20260417_recale.tif` with `T_EQ=1 DELTA=8` and retrain two cells, about four hours. It is not done now
because rebuilding those labels would overwrite `ink-dataset-teacher/841/w00`, which is the training input of the
second cell already queued for tonight. Changing an experiment's inputs while it runs is how a result becomes
unreadable without anyone noticing.

**Stated so it cannot be claimed later.** This amendment was possible only because the seed cells had not been
measured. Had it been found tomorrow, after the square was printed, the correct action would have been to report
the confound and the naive square together, and to trust neither.


---

## PR-5 — A render arm matched to the volume arm, so that PR-2 measures the array and nothing else

*Registered 2026-09-24 00:05, before the run starts. It exists because the check written for PR-4 showed that PR-2's
two arms were not built the same way, and a confounded effect is not repaired by restating it.*

**The provenance of every cell, as the commands that built them record it.** Not as any later summary describes
them: `JOURNAL.md` said the two PR-2 arms shared a threshold rule, and it was wrong.

| run | array | teacher raster | threshold rule | human labels underneath |
|---|---|---|---|---|
| `ink_841_human7n` (PR-2 control) | render 4.681 µm | `new_canon_20260417_recale.tif` | absolute 190 / 131 | `w00_inklabels_human7` (published + our lot-9 corrections) |
| `ink_841_pr2v24` (PR-2 test) | published volume 2.403 µm, reversed | `new_canon_natif.tif` | equal area ±8 → 177 / 161 | `w00v24_inklabels_v2` (published 2026-09-18, no corrections) |
| `ink_841_human7` (PR-4 render, seed 42) | render | `ps48_…_ckpt_130000` | absolute 190 / 131 | `w00_inklabels_human7` |
| `ink_841_w00_s43` (PR-4 render, seed 43) | render | `ps48_…_ckpt_130000` | absolute 190 / 131 | `w00_inklabels_human7` |
| `ink_841_v24_s43` (PR-4 volume, seed 43) | published volume | `new_canon_natif.tif` | equal area ±8 | `w00v24_inklabels_v2` |

So PR-2's comparison varies three things at once, and PR-4's row difference varies four.

**Which way the confounds push is not known.** The human-label axis arguably favours the render arm, which carries
corrections the volume arm does not; the threshold axis has no obvious sign. An effect of +7.1 and +9.0 measured
across three simultaneous changes is not an array effect, whatever its size.

**Claim under test.** With the teacher, the threshold rule and the human labels held equal, training on the
published surface volume still separates ink from background better than training on the render.

**Design — one new arm, matched to `ink_841_pr2v24` on every axis but the array.**

`ink_841_w00m` : render array, teacher `new_canon_20260417_recale.tif` (the same model's prediction, expressed on
the render canvas — two canvases cannot carry the same raster, and this resampling is the one difference that
cannot be removed), threshold rule `T_EQ=1 DELTA=8`, human labels `w00_inklabels_v2` / `w00_supervision_mask_v2`,
same starting checkpoint, same 16 000 steps, same seed 42, the same three excluded render windows.

**The labels are built into a separate directory** (`ink-dataset-teacher-m/`), not over `ink-dataset-teacher/`.
Overwriting the latter is what made PR-2's control unreproducible on 2026-09-23 at 00:55, and it is the input of
runs queued tonight. The same mistake is not made twice in the same week.

**Prediction.** `pr2v24` − `w00m` stays positive on both segments on the primary metric, and of the same order as
the +7.1 / +9.0 measured against the unmatched control.

**What would invalidate it.** If the matched difference is near zero, or negative, then what PR-2 measured was the
labelling recipe and not the array, and every sentence written tonight about "the published volume is the better
surface" must be withdrawn. If it is positive but much smaller, the array effect is real and smaller than announced.

**Stated in advance.** `w00m` is a new arm, not a replacement for the registered control. PR-2 keeps `human7n` and
its numbers stand as published, with the confound now attached to them. PR-5 is what tells us what those numbers
were measuring.

**Cost.** One label build of about ten minutes, one training of 1 h 50, one evaluation of about 20 minutes, in the
window where PR-4 has finished and the GPU would otherwise be idle until morning. No new data is fetched.

### PR-5, note added 2026-09-24 03:30 — a bound on what PR-5 can conclude, read off the label build

*Written after the labels were built and before the training finished, i.e. before any PR-5 number exists.*

`mkteacher.py` prints, for each build, how well the teacher agrees with the published human labels inside the human
mask. The two builds say:

| build | canvas | teacher | ink in mask, human / teacher | precision | recall | IoU |
|---|---|---|---|---|---|---|
| `w00v24` (volume arm) | published volume 2.403 µm | `new_canon_natif` | 22.2 % / 21.7 % | 84 % | 82 % | **0.713** |
| `w00m` (PR-5's render arm) | render 4.681 µm | `new_canon_…_recale` | 22.2 % / 21.7 % | 74 % | 73 % | **0.579** |

The same teacher model, the same published human labels, agree markedly better on the published volume than on the
render — **before anything is trained**.

*This is a reproduction, not a discovery, and the distinction matters.* The same comparison was made on 2026-09-23
at 16:20, before PR-2 ran, and recorded in `PLAN.md` as PR-2's premise: 0.713 against **0.583**. PR-5's build,
made independently from a different label source, returns **0.579**. What it adds is that the number is stable
across two builds four points apart in the pipeline — which is worth having, and is not the same as a new result.

**But it also bounds PR-5.** The render arm's teacher raster is the *warped* one; the volume arm's is native. Part
of the 0.713 → 0.579 drop is the render surface being a worse place to put ink, and part is the warping degrading
the teacher. PR-5 cannot separate those two, because a raster cannot exist on both canvases at once. So PR-5's
result should be read as **"the render pipeline, teacher warping included, is worse than the published volume"** —
which is the practically useful statement — and not as "the flattened surface itself is worse".

Recorded here, before the number, because after the number this reads like an excuse.



### PR-5 — RESULT, 2026-09-24 05:31

**The prediction held in sign and failed in magnitude, and the shortfall is fully accounted for.**

| | control | recipe change | array change | total |
|---|---|---|---|---|
| | `human7n` | → `w00m` | → `pr2v24` | |
| segB | 75.9 | 79.0 (**+3.1**) | 83.0 (**+4.0**) | +7.1 |
| segA | 89.7 | 93.3 (**+3.6**) | 98.7 (**+5.4**) | +9.0 |

The +7.1 and +9.0 announced on 2026-09-23 split cleanly: **44 % and 40 % of them were the labelling recipe**, and
the rest is the array. The matched array effect is **+4.0 and +5.4**.

**Against the registered prediction.** "Stays positive on both segments": held. "Of the same order as +7.1 / +9.0":
**not held** — it is 1.8 and 1.7 times smaller. The outcome this pre-registration named for that case applies:
*"the array effect is real and smaller than announced."*

**Against PR-4.** The seed effect measured the same night is 0.3 and 1.3 on the render row, 1.3 and 0.8 on the
volume row. The matched array effect clears it by 2.7 on segB and 4.6 on segA, so it survives a seed change on both
segments — with the margin now three times smaller than the unmatched comparison suggested.

**What the corrected sentence is.** Training on the published surface volume rather than on the render improves
ink/background separation by **about 4 to 5 points** on held-out windows of two segments the model never saw,
against a control matched on teacher, threshold rule and human labels. It is not 7 to 9. The earlier figure mixed
in a labelling recipe worth 3 to 3.6.

**The bound stated at 03:30 still applies**: the render arm's teacher is the warped raster, the volume arm's is
native, and no experiment can separate those on two canvases. The claim is about the render *pipeline*, warping
included.

**An open question this result raises, recorded but not answered.** `w00m` uses the published human labels with
equal-area thresholds; `human7n` uses our lot-9 arbitration corrections with absolute 190/131 thresholds — and
`w00m` scores 3.1 and 3.6 *higher*. Either the absolute thresholds hurt, or our corrections do, or both. These two
axes were changed together and this experiment cannot separate them. It matters well beyond PR-2: it is the
question of whether the hours spent arbitrating labels are paying, and it deserves its own pre-registration and one
training, not a guess.

**Cost.** As planned: ten minutes of labels, 1 h 50 of training, twenty minutes of evaluation, on an idle GPU.


---

## PR-6 — Do our own label corrections pay, and which half of the "recipe effect" are they?

*Registered 2026-09-24 09:00, before the run starts. PR-5 measured a "recipe effect" of +3.1 and +3.6 with two
things changed at once; this splits it.*

**Where it comes from.** `w00m` (published labels `w00_inklabels_v2`, equal-area thresholds) scores 79.0 and 93.3.
`human7n` (our lot-9 arbitration corrections `w00_inklabels_human7`, absolute thresholds 190/131) scores 75.9 and
89.7. Two axes moved together, so the +3.1 / +3.6 cannot be attributed. One of those axes is **whether the hours
Lilian spends arbitrating labels improve the model** — which governs how he spends about twenty hours a week, so
guessing is not acceptable.

**Design — one new arm that differs from `w00m` by the human labels alone.**

`ink_841_w00m_h7lab` : render array, teacher `new_canon_20260417_recale.tif`, threshold rule `T_EQ=1 DELTA=8`,
human labels **`w00_inklabels_human7`** (ours, with the corrections). Everything else held: same starting
checkpoint, same 16 000 steps, same seed 42, same three excluded windows. Labels built into
`ink-dataset-teacher-h7lab/`, never over an existing dataset.

It then sits between two runs that already exist:

| comparison | what it isolates |
|---|---|
| `w00m_h7lab` − `w00m` | **our corrections**, at constant teacher and threshold rule |
| `w00m_h7lab` − `human7n` | the **threshold rule**, at constant teacher and human labels |

and the two differences must add up to PR-5's +3.1 / +3.6. **If they do not add up, the experiment is wrong, not
the arithmetic** — that is the built-in check.

**Prediction.** Our corrections are worth **more than zero** on both segments: `w00m_h7lab` > `w00m`.

**What would invalidate it.** `w00m_h7lab` ≤ `w00m` on both segments would mean our corrections do not help this
model, and the whole +3.1 / +3.6 was the threshold rule. That would not mean the arbitration was worthless — it
would mean it does not show up this way, and the honest reaction is to say so and to rethink what the labelling is
for, not to keep doing it out of habit.

**Cost.** One label build, one training of 1 h 50, one evaluation of about 20 minutes.

---

## PR-7 — Does the rule we use to choose a teacher predict anything?

*Registered 2026-09-24 09:00, before the run starts, with the predictor variable measured and written down first.*

**Why this exists.** The night of 23–24 September showed the teacher raster is worth **+16.1 and +18.1** — twice the
array effect, and the largest factor measured so far. It is chosen by `pick_teacher.py`, on IoU against the human
labels. That rule has never been checked against a downstream result.

**The predictor, measured this morning and recorded before any training.** IoU against the labels the choice was
actually made with (`w00_inklabels_human7`):

| teacher | IoU | downstream (segB / segA) |
|---|---|---|
| `new_canon_20260417_recale` | **0.583** | 75.9 / 89.7 (`human7n`) |
| `ps48_…_ckpt_130000` | **0.569** | 59.8 / 71.6 (`human7`) |
| `w00_canonical_030726_reverse_070326` | **0.482** | to run |
| `w00_canonical_2um_20250807020208` | **0.479** | to run |

*The instrument reproduces*: 0.583 against 0.569 are exactly the numbers `pick_teacher` printed on 2026-09-22 at
22:17 when it made the choice.

**A fragility found while measuring it, recorded because it bears on the answer.** Evaluated against the
*published* labels `w00_inklabels_v2` instead, the same rule ranks `ps48` **first** (0.640 against 0.585) — the
opposite order, and the one that would have cost 16 points. The rule's verdict on this pair depends on which human
label set it is given.

**Claim under test.** The IoU ordering of teachers predicts the ordering of the models trained from them.

**Design.** Two new arms, teacher raster the only thing that changes: `ink_841_t_rev` and `ink_841_t_2um`, render
array, labels `w00_inklabels_human7`, thresholds 190/131, seed 42, 16 000 steps, same starting checkpoint, same
three excluded windows — exactly `human7`'s and `human7n`'s recipe. Labels in their own directories.

**Prediction.** Both land **below `ps48`'s 59.8 / 71.6**, since both score about 0.09 of IoU below it.

**What would invalidate it.** Either new arm landing at or above `human7n` (75.9 / 89.7) means the rule does not
order teachers, and every teacher choice made with it — including the one that gave us our best model — was luck.
Four points on a line is little, but a rule that inverts on one of four pairs is not a rule.

**Stated in advance.** A confirmation here would be weak (four teachers, one segment pair, one seed). A refutation
would be strong, because it takes one inversion to break a selection rule. This experiment is worth running for its
refutation, not for its confirmation.

**Cost.** Two label builds, two trainings of 1 h 50, two evaluations of about 20 minutes.


### PR-6 — RESULT, 2026-09-24 11:01

**The prediction fails, the built-in check passes, and the result is more interesting than the prediction was.**

`ink_841_w00m_h7lab` (our labels, equal-area thresholds) scores **81.8** on segB and **89.5** on segA. With the two
runs that already existed, the +3.1 / +3.6 splits as:

| | segB | segA |
|---|---|---|
| `human7n` — our labels, absolute 190/131 | 75.9 | 89.7 |
| `w00m_h7lab` — our labels, equal area | **81.8** | **89.5** |
| `w00m` — published labels, equal area | 79.0 | 93.3 |
| **threshold rule** (equal area − absolute) | **+5.9** | **−0.2** |
| **our corrections** (ours − published) | **+2.8** | **−3.8** |
| sum (must equal PR-5's recipe effect) | +3.1 ✓ | +3.6 ✓ |

**The arithmetic check passes on both segments**, so the pipeline is consistent.

**Against the registered prediction.** "Our corrections are worth more than zero on both segments": **failed**.
They are worth +2.8 on segB and **−3.8** on segA. Neither does the threshold rule hold up: +5.9 on one segment,
−0.2 on the other. **Both axes change sign between the two segments.**

**What this does not say.** It does not say the arbitration is worthless. Two segments, one seed, one metric cannot
show that, and the honest reading is that *these corrections do not reliably improve this model on held-out
segments*, which is a different sentence.

**What it does say, and it costs us something.** The seed test of PR-4 put run-to-run noise at **≤1.3 points**, but
that test holds the training data fixed. Here, two small changes to the training data move the result by **−3.8 to
+5.9**. So the right error bar for a comparison that *changes the dataset* is several points, not 1.3 — and PR-2 /
PR-5's array effect is exactly such a comparison.

**What still separates the array effect from these.** +4.0 and +5.4, **the same sign on both segments**. Every
effect measured here flips sign between segments. Sign agreement across two independent segments is the thing the
array effect has and the recipe effects do not — and it is now the criterion to apply, having been forced on us by
a result rather than chosen in advance.

**Consequence recorded immediately.** The sentence written at 05:31 — "improves separation by about 4 to 5 points"
— keeps its numbers, but its margin is not comfortable: it is 4 to 5 against a dataset-change spread of the same
order, saved only by agreeing in sign on both segments. Anything published about it must say so.


### PR-7 — RESULT, first arm, 2026-09-24 13:17 (second arm still training)

**The prediction fails on the first arm, and it fails in the direction that breaks the rule.**

`ink_841_t_rev` — teacher `w00_canonical_030726_reverse_070326`, ranked **third of four** by the IoU rule at
0.482 — scores **84.4** on segB and **87.6** on segA.

| teacher | IoU (the selection rule) | segB | segA |
|---|---|---|---|
| `new_canon_20260417_recale` | 0.583 — rank 1 | 75.9 | **89.7** |
| `ps48_…_forward_210326` | 0.569 — rank 2 | 59.8 | 71.6 |
| `w00_canonical_030726_reverse_070326` | 0.482 — rank 3 | **84.4** | 87.6 |
| `w00_canonical_2um_20250807020208` | 0.479 — rank 4 | training | training |

**Against the registered prediction.** "Both land below `ps48`'s 59.8 / 71.6": the first arm lands **24.6 points
above it on segB and 16.0 above on segA**. 84.4 is the highest segB value of the eight arms measured so far.

**Against the registered invalidation clause, read strictly.** The clause says "either new arm landing at or above
`human7n` (75.9 / 89.7)". On segB, 84.4 is above 75.9. On segA, 87.6 is **2.1 below** 89.7. One component of the
pair is met and the other is not, and the clause did not say which reading applies — that is a defect in how it was
written, recorded here rather than resolved in the convenient direction. The main prediction, however, fails with no
ambiguity at all.

**The built-in check passes.** The direct-order control for this arm stays at 31.1 / 28.7, in line with every other
arm (17.9–43.9). The high number is not an arm that reads in both directions, which would have signalled a leak.

**Verified blind.** The four values of this section (84.4 / 87.6 for `t_rev`, 81.8 / 89.5 for `w00m_h7lab`) were
recomputed from the raw rasters by a separate agent given only the file paths and an operational definition, with
the repository's prose withheld. They match to the decimal.

**What this costs us.** The IoU rule inverts on **2 of the 3 pairs on segB** and **1 of 3 on segA**. The teacher in
service — the one worth +16 points, the largest effect in the project — was not selected. It was drawn. Every
sentence we have written about "choosing a teacher" describes an operation we cannot perform.

**An observation, on two points, that we cannot currently test.** The worst teacher's filename ends in `forward`;
the best one's ends in `reverse`. Both words name the layer order of the rendering campaign that produced the
raster — the same distinction that carries +50 points of separation in our own models. A teacher produced by a
model that read in the right direction being a better teacher is a plausible mechanism, and it would explain why
IoU against human labels fails to rank them: it rewards agreement with one human's partial coverage, not
correctness. **It is two points.** `new_canon_recale`, which sits between them, comes from a third campaign with no
direction word in its name, so the pattern cannot be extended to it. Recorded as an observation, not a finding, and
explicitly not welded to the result above — the same error was made on 2026-09-24 with the brightness periodicity.


## PR-8 — Does a human eye rank teachers where the IoU rule cannot?

*Registered 2026-09-24 14:05: after `t_rev`'s result, before `t_2um`'s number exists, and before the observer has
looked at the image.*

**Why this exists.** PR-7 leaves us with the largest lever in the project — 25 points between the best and worst
teacher — and **no instrument to choose one**. The IoU rule inverts. Training a candidate costs 2 hours. The one
instrument that has worked on this project is the observer's eye: on 2026-09-24, judging blind, he ranked a
16-point model difference correctly 3 times out of 3, and a 4-to-5-point difference 1 time out of 2. The teacher
spread is 25 points.

**Design.** `scripts/professeurs_aveugle.py` renders the four teacher rasters over three identical 5 000-pixel
zones (~23 mm, one line of text), chosen automatically as the three highest human-label-density windows, no
overlap. Columns are labelled A to D, shuffled with a seed *verified before use* not to reproduce the downstream
order of the three measured teachers. No names, no numbers, no human labels displayed — showing the labels would
make the observer judge agreement-with-labels, which is precisely the rule that failed. Raw grey, `vmin=0`,
`vmax=255`, because these three arms were built with **absolute** thresholds (ink ≥ 190, background ≤ 131), so a
dimmer teacher really does produce less ink and that is a genuine defect, not a display artefact.

**Aggregation rule, fixed in advance.** Three zones, three rankings. If they agree, that is the answer. If they
differ, each pair is decided by majority across the three zones. A Condorcet cycle is declared inconclusive and
reported as such.

**The bar to beat, stated as a number.** Against the segB downstream order (`reverse` > `new_canon` > `ps48`), the
IoU rule gets **1 of 3 pairs**; on segA (`new_canon` > `reverse` > `ps48`) it gets **2 of 3**.

**Prediction, in two parts.**
1. *Retrospective.* His ranking of the three measured teachers matches their segB order exactly. Chance: **1 in 6**.
2. *Prospective, and this is the real test.* The slot he gives `canonical_2um` among the other three predicts which
   of the four intervals — above 84.4, between 75.9 and 84.4, between 59.8 and 75.9, below 59.8 — the `t_2um` segB
   score falls into. Chance: **1 in 4**. This number does not exist at the time of writing.

Both parts together: **1 in 24** by luck.

**What would invalidate it.** His ranking scoring 1 of 3 pairs or worse on segB — no better than the broken rule.
The consequence is then accepted rather than argued around: teachers cannot be pre-screened, and each candidate
costs a 2-hour training run.

**Contamination control.** `t_2um`'s score is expected around 15:30. Until his answer is received, no number
concerning any teacher is to be mentioned to him, and the report will state whether his answer arrived before or
after the number existed.

**Stated in advance.** Four teachers, one observer, one segment pair. A success does not establish an instrument;
it makes a fifth teacher worth measuring. A failure closes the idea for the price of one image.


### PR-8 — RESULT, retrospective half, 2026-09-24 14:15

**The eye fails, and it fails by reproducing the rule that already failed.**

The observer answered at 14:15, with one ranking for the whole image rather than one per zone — unambiguous under
the aggregation rule, which asks for a per-pair majority only when the zones disagree. His answer: **C > B > D > A**.

| shown | teacher | his rank | segB | IoU (the rule) |
|---|---|---|---|---|
| C | `ps48_…_forward_210326` | **1st** | **59.8** (last) | 0.569 |
| B | `new_canon_20260417_recale` | 2nd | 75.9 | 0.583 |
| D | `w00_canonical_030726_reverse_070326` | 3rd | **84.4** (first) | 0.482 |
| A | `w00_canonical_2um_20250807020208` | 4th | not yet measured | 0.479 |

**Registered prediction 1 — failed, and failed maximally.** His order of the three measured teachers is
`C > B > D`; the truth is `D > B > C`. That is the exact reversal: **0 of 3 pairs**, against 1 of 3 for the IoU
rule and 1.5 expected from a random ranking. The registered invalidation clause — "1 of 3 or worse" — is met.

**The finding is not "his eye is bad". It is that his eye and the broken rule are the same instrument.** Ranked by
`pick_teacher`'s IoU, the four teachers go B (0.583) > C (0.569) > D (0.482) > A (0.479). His ranking agrees with
that on **5 of the 6 pairs** — everything but the B/C swap, whose IoU values differ by 0.014. A human judging
"which of these looks most like ink", with no labels shown and no numbers, reproduces an automatic agreement score
he has never seen. Both then fail on the same pairs.

**Consequence, accepted rather than argued around.** There is no cheap screen for teachers: not IoU, not the eye.
A candidate teacher costs a 2-hour training run, and that is the price. What *looks* like better ink is not what
makes a better teacher — three teachers is too few to say why, and the honest next step is more teachers, not more
statistics computed on four.

**Registered prediction 2 stands, and its number still does not exist.** `ink_841_t_2um` was killed at 14:08:45 by
a CUDA failure during Windows modern standby, with no checkpoint; it is queued to be re-run tonight after the
reading. The observer placed `canonical_2um` **last**, so the registered prediction is: **`t_2um` lands below 59.8
on segB.** It was made before the number existed and will be scored as written.

**A second reading, recorded now and explicitly marked as invented after seeing 0 of 3.** If the eye is not random
but systematically inverted on this task, the same answer predicts the opposite: `t_2um` lands **above 84.4**. This
is a post-hoc hypothesis with one supporting observation, written down before the measurement only so that it
cannot be adopted afterwards as if it had been registered. If `t_2um` lands between 59.8 and 84.4, both readings
are wrong and the eye carries no signal on teachers at all — which is the most likely outcome.


### PR-7 — RESULT, second arm, 2026-09-24 18:31: the rule is not useless, it is useless *where it matters*

`ink_841_t_2um` — teacher `w00_canonical_2um_20250807020208`, ranked **fourth of four** by the IoU rule at 0.479 —
scores **52.4** on segB and **52.7** on segA. Verified blind: an agent given only the file paths and an operational
definition, with the repository's prose withheld, returned 52.4 and 52.7 to the decimal (and 24.0 / 17.1 for the
direct-order control).

| teacher | IoU (rule) | rank by rule | segB | segA |
|---|---|---|---|---|
| `w00_canonical_030726_reverse_070326` | 0.482 | 3rd | **84.4** | 87.6 |
| `new_canon_20260417_recale` | 0.583 | 1st | 75.9 | **89.7** |
| `ps48_…_forward_210326` | 0.569 | 2nd | 59.8 | 71.6 |
| `w00_canonical_2um_20250807020208` | 0.479 | 4th | **52.4** | **52.7** |

**The registered prediction was "both land below `ps48`'s 59.8 / 71.6".** It is **right for this arm** (52.4 and
52.7, below on both segments) and **wrong by 25 points for the other**. Half a prediction.

**Correction to what was written here at 13:20.** That section said "the rule does not order teachers" and "the
teacher in service was not selected, it was drawn". Over the full four, the IoU rule gets **4 of 6 pairs** right —
against 3 expected from a coin. It is not noise. What it does is **order correctly at the bottom and invert at the
top**: it identifies the starving teacher (the 2 µm raster marks ink on only 36 % of the human mask, and produces
the worst model by 7 points) and it inverts on the pair that decides which teacher we actually use. A rule that is
right about the candidate nobody would pick and wrong about the one we would is still unusable for selection — but
"unusable for selection" is a narrower and truer sentence than "orders nothing", and the earlier one is withdrawn.


### PR-8 — RESULT, prospective half, 2026-09-24 18:31

**The registered prospective prediction is correct.** The observer placed `canonical_2um` **last** among the four
teacher rasters, judging the rasters alone with no names, no numbers and no labels shown. The registered
consequence — *`t_2um` lands below 59.8 on segB* — is met: **52.4**. Chance for that half alone: **1 in 4**.

**The two halves, scored separately and not averaged into a verdict that suits.**

| | result | chance |
|---|---|---|
| retrospective — exact order of the 3 measured teachers | **failed**, 0 of 3 pairs (the exact reversal) | 1 in 6 |
| prospective — interval of the unmeasured teacher | **correct** | 1 in 4 |
| both, as registered | **not met** | 1 in 24 |
| all 4 teachers, pairwise | **3 of 6** — exactly chance | 3 expected |

**The post-hoc "inverted eye" hypothesis, recorded before the measurement precisely so it could not be adopted
afterwards, is refuted.** It predicted `t_2um` above 84.4. It is 52.4.

**What the eye and the rule share.** Both put `canonical_2um` last, and it is last by a wide margin. That was the
easy pair. At the top of the ranking, where a selection would actually be made, neither separates anything.


## Not preregistered — an unregistered test, 2026-09-24 17:40, and its result is the most important of the day

*Recorded here with the fact that it was **not** registered in advance. It was improvised while the observer was
looking at an image, and it is reported because it decides more than the four preregistrations above.*

**The question.** Our whole metric is a contrast: mean over labelled ink minus mean far from ink. It can rise
without any letter becoming more complete. So: **is the full-sheet prediction legible as text?**

**What was done.** The zone containing the three labelled letters of segB, rendered at four thresholds
(28.9 %, 47.2 %, 53.1 %, 61.4 % of known ink marked — measured, printed below), shuffled, **without the label
outlines**, because an outline tells the reader where the letter is and destroys the question. Shown to a person
with no connection to the project and no knowledge of what was in the image.

**Result: she found no letters in any of the four panels**, including the one where 61.4 % of the known ink is
marked. The project's own observer, who had seen the same zone an hour earlier *with the answer outlined on it*,
identified one letter — in the panel that was exactly the setting he had already been shown. He stated his own bias
before answering, which is what makes his answer usable as a demonstration of the bias rather than as evidence.

**Supporting measurements.**

| | value |
|---|---|
| known ink marked, threshold 240 | 28.9 % |
| known ink marked, threshold 180 | 53.1 % |
| far-from-ink marked, threshold 180 | 10.1 % |
| ink marked in the 0–48 px ring around letters | 24.6 % |
| best rigid offset between prediction and labels | 16 px (0.04 mm), +0.9 % IoU — **no misalignment** |
| median letter size, measured on the labels | **1 808 px = 4.34 mm** |
| the model's input window | **128 px = 0.31 mm** |

**The model never sees more than a fourteenth of a letter.** That is a measured ratio, not an estimate: letter size
comes from connected components of the label mask, the window from `patch_size` in the training config at
`volume_scale: 0`.

**Stated as a lead, not a cause.** Run 2 of this project produced readable letters on another scroll at a ratio of
about 1/7 — twice better, not categorically different. So the field of view is a measured candidate explanation
that a controlled test has not yet isolated.

**What this costs the rest of this document.** Every separation figure above — the +16 to +25 of the teacher, the
+4 to +5 of the array, the +3 of the label recipe — is a contrast that does not demonstrate legibility. Nothing
here is retracted: the measurements stand as measurements. But the sentence "we read PHerc. 841" cannot be written,
and what we have is **a full-sheet ink map, validated where labels exist, that a naive reader cannot read**.


## PR-9 — Did the quantity we optimised for 24 hours track letter completeness at all?

*Registered 2026-09-24 19:20, before the computation is run. No training is involved: every prediction this uses
already exists on disk.*

**Why this exists.** Everything measured on 23–24 September moves one number: the separation, `mean(A[L]) −
mean(A[F])`, a **contrast** between labelled ink and far background. On 2026-09-24 at 17:40 a reader with no
connection to the project found **no letters** in the full-sheet prediction at any of four thresholds, up to 61.4 %
of known ink marked. So the contrast rose by 25 points across our arms while legibility stayed at zero. The
question this raises is narrower and answerable: does that contrast track even the **completeness** of the letters,
which is one necessary ingredient of legibility?

**The second quantity, defined here before it is computed.** For each arm, on the same three held-out windows of
each segment, in reversed layer order, at level 3:
1. find the threshold `t` at which the arm marks exactly **10.0 %** of the far-from-ink pixels
   (`F = S & ~dilate(L, 3)`), by interpolation on the empirical distribution — a **fixed false-positive rate**, so
   that arms are compared at matched noise and not at matched threshold;
2. report the fraction of label pixels `L` at or above `t`. That is **fill at 10 % noise**.

This is computed per window and averaged over the three, exactly as the separation is.

**The arms**, all of which already have predictions: `human7n`, `pr2v24`, `w00m`, `h7`, `w00s43`, `v24s43`,
`w00mh7`, `trev`, `t2um` — nine, on segB and segA.

**Claim under test.** The two orderings are the same ordering.

**Prediction.** Spearman ρ between the separation ranking and the fill ranking is **≥ 0.8 on segB**.

**What would invalidate it.** ρ < 0.8. Then the 25 points of separation bought something other than completeness,
the arm chosen to produce the published reading (`pr2v24`) was chosen on a quantity that does not order
completeness, and every comparison in this document needs the second column printed next to the first.

**Stated in advance.** Nine arms is a small sample and Spearman on nine is noisy; ρ ≥ 0.8 is a bar chosen to be
passable, not a significance test. A pass means "these two measures do not visibly disagree here", not "the metric
was right". A failure is the informative outcome, and it is cheap: no GPU, no training, existing files only.

**Also stated in advance, so it cannot be claimed afterwards.** Whatever ρ comes out, this test says nothing about
legibility. Completeness is necessary, not sufficient — the neutral reader found nothing at 61.4 % fill.


### PR-9 — RESULT, 2026-09-24 19:35: the prediction fails, and the table says more than the coefficient

**Spearman ρ = 0.617 on segB**, against the registered bar of 0.80. **Failed.** On segA, ρ = 0.883 — the
segment-dependence that every other result in this document has shown.

| arm | separation (segB) | fill at 10 % noise (segB) |
|---|---|---|
| `trev` | **84.4** | 55.8 % |
| `v24s43` | 84.3 | 57.0 % |
| `pr2v24` | 83.0 | 56.7 % |
| `w00mh7` | 81.8 | **57.9 %** |
| `w00m` | 79.0 | 56.1 % |
| `human7n` | 75.9 | 56.5 % |
| `w00s43` | 60.1 | 50.9 % |
| `h7` | 59.8 | 51.1 % |
| `t2um` | **52.4** | 55.4 % |

**The coefficient is not the finding. The two spreads are.** Separation ranges over **32 points** (52.4 to 84.4).
Fill ranges over **7 points** (50.9 % to 57.9 %). Twenty-four hours of work moved the first by a third of its range
and the second by almost nothing.

**The single most telling row is the last one.** `t2um` has the worst separation of all nine arms, by 7 points —
and its fill, **55.4 %**, is mid-table, above `h7` and `w00s43` whose separation is 7 points better. And the best
arm by separation, `trev`, is **seventh of nine** by fill. The ordering is not preserved where it matters.

**What this costs.** The arm chosen to produce the published full-sheet reading, `pr2v24`, was chosen on
separation. On fill it is third of nine, 1.2 points below `w00mh7` — inside any reasonable error bar, so the choice
was not *wrong*; it was made on a quantity that does not order the one that matters. Every table in this document
that ranks arms by separation alone should be read as ranking them by contrast, and by nothing else.

**What was written in advance and is repeated here so it cannot be quietly dropped.** This says nothing about
legibility. Fill is necessary, not sufficient: no arm exceeds 58 %, and a naive reader found no letters at 61 %.
The honest summary of 23–24 September is that we moved a contrast by 32 points, moved completeness by 7, and moved
legibility from zero to zero.

**Verified blind.** The eighteen values and both coefficients were recomputed by a separate agent given only the
file paths and an operational definition, with the repository's prose withheld. It wrote its own rank-correlation
from scratch and cross-checked it against SciPy: **0.617 and 0.883**, identical. It also confirmed that the label
and far-from-ink masks are pixel-for-pixel identical across all nine arms in every window, which is the property
that makes the nine numbers comparable at all.


### The control on the control, 2026-09-24 19:50 — and it holds

The finding above ("a naive reader found no letters") is worthless unless a reader *does* read the ground truth
rendered the same way. So: two panels, same zone, same rotation, same black-on-white, no outlines, shuffled —
one the **human labels**, one the **model at 53.1 % fill**. The observer was not told which was which.

**He read the letters immediately in the label panel and nothing in the model panel**, and added, unprompted, that
in the model panel "the ink is not in the same places".

So the rendering is not the obstacle: three Greek letters drawn by hand and shown as a flat black mask are read at
a glance. The model's output, at the fill rate where its known letters are best represented, is not. **The missing
information is shape, and it is missing from the model, not from the display.**

This is the last piece of 2026-09-24, and it is what licenses the sentence that closes the day: we produced a
full-sheet ink map of PHerc. 841, validated where labels exist, that a reader cannot read — and we now know that
is a property of the map and not of how we drew it.

## PR-10 — Is the model blind to letter *shape* because its window is 1/14 of a letter?

*Registered 2026-09-24 21:0x, before the training is launched and before any number from it exists. This is the
first preregistration in this document whose primary endpoint is a **human reading**, not a separation.*

**Why this exists.** Every arm of 23–24 September raised the ink/background contrast and none of them produced a
readable letter. On 2026-09-24, measured from the connected components of the human labels on segB, a letter of
this scroll is **1 808 px across at 2.403 µm/px = 4.34 mm**. The network's input window is 128 × 128 px in the
plane, i.e. **0.31 mm — one fourteenth of a letter**. It is asked to draw shapes it has never seen: at that scale
a stroke crossing the window is a band of ink from edge to edge, indistinguishable from a blot. The one model in
this project that ever produced readable letters — run 2 on PHerc. Paris 4 — worked at **≈ 1/7** of a letter.

**The change, and it is the only one.** The data are read at **half resolution**. Nothing else moves: same teacher
(`w00v24`), same labels, same supervision mask, same thresholds, same seed 42, same 16 000 iterations, same
starting checkpoint `ink_w00_128_acc4/ckpt_080000.pth`, same patch size `[64, 128, 128]`, same batch 2 × grad-acc 4,
same learning rate. The window then covers **0.62 mm = 1/7 of a letter**, run 2's ratio.

**How the half-resolution dataset was built, and why nothing was recomputed.** The training zarrs already carry a
full pyramid (levels 0–5); the trainer opens `<zarr>/0` and ignores the rest. The dataset is therefore the same
pyramid **re-rooted one rung**: new level 0 = old level 1, for the volume, the ink labels and the supervision mask
alike. No resampling was written by us, so the labels are not our downsampling of the labels — they are the ones
already in the file. Verified before launch, plane by plane over all 65 planes of both label arrays: **0 differing
pixels**, source `[65, 8230, 9280]` against copy `[65, 8230, 9280]`, ink density 0.0941 % and supervision density
1.0261 % on both sides.

**Claim under test.** The absence of letter shapes is caused by the field of view, not by the contrast.

**Primary endpoint — a blind human reading, defined here so it cannot be moved afterwards.** A reader with no
connection to the project, who has not seen the answer, is shown the **control zone** (the one containing the
already-labelled letters, *without* the red outlines) rendered from **both** arms — `pr2v24` at full resolution and
`demi` at half — in randomised order, unlabelled, at the same four thresholds used on 2026-09-24 at 17:40. They are
asked one question: *do you see letters, and where?*

**Prediction.** On the half-resolution arm the reader reports **at least one letter shape whose position falls on a
labelled letter**; on the full-resolution arm they report none, as the reader of 2026-09-24 did.

**What would invalidate it.** The reader finds nothing on either arm. Then field of view is not the obstacle — or
not the only one — and the next lead is not "a larger window".

**Secondary quantities, reported but not the verdict.** Separation and fill at 10 % noise on the same three
held-out windows of segB and segA, as for every other arm. Registered in advance: **a drop in separation does not
refute this claim, and I may not present it as if it did.** The arm starts from a checkpoint trained at full
resolution, so its input statistics are shifted on step 1; separation is exactly the quantity PR-9 showed does not
order completeness.

**Stated in advance, because each of these weakens the conclusion in a different direction.**
1. **The inherited checkpoint is trained at the wrong resolution.** A success is therefore strong evidence (it
   worked *despite* the shift); a failure is weak (the shift alone could explain it). Making it clean would mean
   retraining the base model at half resolution — days, not hours.
2. **Half resolution destroys detail as surely as it adds context.** At 4.8 µm/px the crackle texture that the ink
   signal may rest on is thinner than a pixel. This is the competing explanation for a failure and it cannot be
   separated from hypothesis 1 by this arm alone.
3. **Four times fewer distinct patch positions** for the same 16 000 iterations: more repetition, more room to
   memorise. Relevant if the arm looks good on labelled ink and blank elsewhere.
4. **One arm, one seed.** PR-4 measured the seed effect on this pipeline; this is a single draw.

### PR-10 — amendment, 2026-09-24 20:17, written while the run was starting and before any result exists

Limitation 3 above says "four times fewer distinct patch positions". That was arithmetic, not a measurement, and
the measurement disagrees: the patch caches the trainer wrote for the two arms hold **3 187 patches for `demi`
against 8 449 for `pr2v24`** — a factor of **2.65**, not 4. The figure that matters for the memorisation worry is
therefore: 16 000 iterations × batch 2 = 32 000 draws, so each patch is seen about **10 times** in the half-
resolution arm against about **3.8** in the full-resolution one. Still a real difference, smaller than stated.

Corrected here rather than in the text above, because the text above was registered before the run and the point of
registering it is that it does not get edited afterwards.

### PR-10 — declared deviation, 2026-09-24 20:35, while the run is training and before any prediction exists

The primary endpoint above says the two arms are shown "at the same four thresholds used on 2026-09-24 at 17:40".
Those thresholds are recovered: **240, 200, 180, 150**, marking **28.9 / 47.2 / 53.1 / 61.4 %** of the known
letters on the whole sheet.

Applying those four raw numbers to the half-resolution arm would be a mistake, and it is the exact mistake PR-9's
method note warns about: two arms whose predictions do not share a grey scale cannot be compared at a shared
threshold, because the comparison then measures the scale. The `pr2v24` panels keep the registered thresholds —
they are literally the same images as 2026-09-24 — and the `demi` panels use whatever thresholds mark **the same
four fractions of the known letters**: 28.9, 47.2, 53.1, 61.4 %. The reader then judges shape at matched
completeness, which is the only way the question "do letters appear?" has an answer.

Registered consequence, so it cannot be claimed later: the reader will see the demi arm at **its** thresholds, and
the fill figures printed in the answer key are matched by construction, not measured as a result. Fill is not
evidence in this test. Only the reading is.

One property of the display that cannot be removed and is stated instead: the half-resolution panels have half the
pixels, so shown at the same physical size they are blockier. A reader could in principle tell the arms apart by
that. They are still not told which is which, and the question asked is about letters, not sharpness.

### PR-10 — the premise re-derived blind, 2026-09-24 21:00, still before any result

PR-10 rests on one measured number: the size of a letter. It was re-derived by an agent told only to measure the
connected components of a label array, not why. Level 3 of `inklabels.zarr` for `auto_grown_20260220174252405`
(1833 × 2388, 69 742 marked pixels) holds **5 connected components**, none below the 30-pixel speckle floor, whose
largest bounding-box dimensions in full-resolution pixels are 2128, 1824, 1808, 1592, 1368 — **median 1808 px =
4.345 mm**, mean 1744 px = 4.191 mm. The 128-pixel window is 0.3076 mm, so 1808/128 = **14.1**; at half resolution
the window spans 256 full-resolution pixels, so 1808/256 = **7.1**. The two ratios PR-10 is built on hold.

The same agent was asked, without being told the expected answer, which 2×2 rule turns level 0 of the training
volume into its stored level 1. **Maximum, 100.0000 % of pixels on 11 regions** spanning 11 z-planes and both
array corners, 6 815 744 level-1 pixels compared, of which 5 869 739 lay in blocks where the rules genuinely
differ. Minimum and mean-floored match 0 % of those blocks, mean-rounded 2.7–4.0 %, plain subsampling ~29 %. An
explicit odd-offset control reproduced the alignment trap: the same test at a one-pixel shift drops max to 8–19 %.

**One thing this caught that had nothing to do with the check.** Three scripts of this project carried the sentence
"a letter is 500 to 800 px", a head estimate never measured, and it had been copied into the caption of the very
figure a naive reader is about to judge. It is wrong by a factor of about 2.5, and it would have sent the reader
looking for shapes three times too small on a test whose whole endpoint is what they see. Corrected in all of them.

### PR-10 — a confound bounded before the result, 2026-09-24 21:10

Limitation 1 above says the arm inherits a checkpoint trained at full resolution. There is a second half to that
which was not stated: the pyramid pools by **maximum**, so the half-resolution images are not only coarser, they
are **brighter** than the ones the base checkpoint was trained on. If that shift were large, a failure could be
blamed on brightness rather than on field of view, and the arm would answer nothing.

Measured on 2048 × 2048 windows at three z-planes, level 0 against the stored level 1:

| plane | level 0 mean | level 1 (max 2×2) mean | median shift | p99 shift |
|---|---|---|---|---|
| 10 | 76.0 | 79.6 | +6 | +12 |
| 32 | 84.4 | 88.0 | +5 | +8 |
| 50 | 83.4 | 86.9 | +5 | +7 |

**About +3.5 grey levels on the mean, roughly 4 %.** For comparison, a mean-pooled level 1 would sit within 0.4 of
level 0. So the brightness shift is real but small, and it is registered here as a **weak** explanation for a
failure: if this arm fails, the resolution change remains the large variable and brightness cannot carry the
result. Registered now so it cannot be promoted to a cause afterwards.

### PR-10 — how each outcome will be read, registered 2026-09-24 21:35, before the arm has finished training

Written now so the reading of the result is not chosen after seeing it. `demi` = the half-resolution arm,
`plein` = `pr2v24`, the matched full-resolution arm. "Letters" means the naive reader reports at least one letter
shape **and** its position falls on a labelled letter.

| reader finds | how it is read |
|---|---|
| letters on `demi`, none on `plein` | The registered prediction holds. Field of view was the obstacle. Strong, because the arm succeeded **despite** inheriting a checkpoint trained at the wrong resolution. Next step: retrain the base model at half resolution and read the whole sheet again. |
| letters on neither | The prediction fails. Field of view is not the obstacle, or not the only one — but the failure is **weak evidence**, because limitations 1 and 2 (inherited checkpoint, lost detail) are alive and this arm cannot separate them. It does not license "a larger window is useless"; it licenses "a larger window obtained this cheap way does not suffice". |
| letters on both | Something outside both arms changed — most likely the rendering or the zone, since the reader of 2026-09-24 saw none on `plein` at the same four fill levels. The first thing to check is whether this reader is really naive, and the second whether the panels differ from the 17:40 ones. Not evidence for the hypothesis. |
| letters on `plein`, none on `demi` | The prediction fails and the change actively hurt. Reading: half resolution destroyed more detail than the context it bought — limitation 2, not limitation 1. |

**Symmetric statement about the secondary numbers, and this is the half that was missing.** It is already
registered that a **drop** in separation does not refute the claim. The same must hold the other way: a **rise** in
separation or in fill does not confirm it, and will not be reported as a success. PR-9 measured that separation
does not order even completeness; nothing about this arm changes that. The only outcome that moves PR-10 is what
the reader sees.

**And a floor on the claim.** One reader, one zone, one arm, one seed. Whatever the answer, it is a single
observation, and the write-up will say so in the sentence that states it.

### PR-10 — RESULT, secondary half only, 2026-09-24 22:15. **The primary endpoint is not yet measured.**

The arm trained cleanly: 16 000 iterations in 1 h 46 min 55, `exit=0`, twelve of twelve held-out windows inferred
at half resolution, control zone written, queue closed at 22:10:37.

| | segB | segA |
|---|---|---|
| `demi` — half resolution, reversed layer order | 116.6 | 122.4 |
| `pr2v24` — the matched full-resolution arm | 83.0 | 98.7 |

*The segA figure in the row above was first written as 89.2, a number I asserted from memory instead of
reading it. `verify_claims.py` rejected the pair within a minute of the text being written — the first time
the automatic check has caught an error in a **fresh** claim rather than drift in an old one. The gap is
+33.6 on segB and +23.7 on segA, not the wider one the wrong figure implied.*

Correlation with the reference render: 0.794 on segB, 0.809 on segA. In the direct layer order the same arm gives
32.8 on segB — the reversed/direct gap is wider than for any previous arm, which is consistent with everything
this document has measured about layer order and is not news.

**This is +33.6 and +23.7 points, and it is not a result.** It is written here as a number because the arm produced it, and
that is all. Registered before the launch, twice: a drop in separation would not refute the claim, and a **rise
does not confirm it**. PR-9 measured that separation does not order even letter completeness; nothing about this
arm changes that. **The endpoint of PR-10 is what a naive reader sees, and no reader has looked yet.**

**Verified blind.** Both figures were re-derived by an agent given the file paths, the subsampling rule and nothing
else — not what the numbers were for, not what was expected. It returned 116.6 and 32.8 to the decimal. It also
reported, unasked, that for all six files the prediction, the label crop and the supervision crop came out at
exactly (188, 188) with zero disagreement, and that the predictions are **not saturated** — min 1, max 254, no
pixel at 0 or at 255 — so the separation is not an artefact of a binarised output.

**A near miss it also caught.** Asked to compute the same statistic with the *wrong* subsampling — `[::8]`, the
value that was hard-coded in `mesure_sens.py` until this afternoon — it gets **8.8 instead of 58.4** on window 1.
A half-resolution prediction subsampled by 8 is compared against a quarter of the label region: the number stays
plausible and is silently wrong. Had the `SS` parameter not been added before the run, this arm's secondary
numbers would have read as a catastrophic failure. Same class as the max-versus-mean pyramid trap, on the same
day: **a scale error returns a believable number instead of crashing.**

**What happens next, and it is the only thing that matters.** Eight panels, the same zone, two arms, four fill
levels matched to within 0.3 points (30.7/30.4, 47.7/47.8, 53.3/53.2, 62.1/62.2), randomised, no outlines. One
question to a reader who has seen nothing of this project: *do you see letters, and where?*

### PR-10 — RESULT, primary endpoint, 2026-09-24 22:45. **The prediction fails, and the reader is still owed.**

The reader who looked was **Lilian himself, and he was no longer blind**: he had asked for the answer key to be
opened half an hour earlier, before anyone had looked. That is recorded because the order of events is part of the
result. His verdict on the eight panels: *"on ne voit rien, aucune lettre, seulement des taches noires, rien de
plus."*

**Registered prediction: letters on the half-resolution arm, none on the full-resolution one. Neither shows any.
PR-10 fails.** Read as registered in advance: this does **not** license "a larger window is useless" — the arm
inherits a checkpoint trained at full resolution and half resolution destroys detail as surely as it adds context,
and this arm cannot separate those. It licenses only: *a larger field of view obtained this cheaply does not
suffice.*

**The weight of this verdict is low and it is stated as such.** One reader, contaminated, on a frame that turned
out to be wrong (below). A naive reader on a corrected frame is prepared and still owed.

### The finding that outranks PR-10, 2026-09-24 22:45 — the target is not the ceiling

A second blind test, two panels, same zone and rendering, matched at 53.4 % fill: **the human labels against the
published reference** — the map every arm in this project is trained to imitate. The positive control is the one
that already worked on 2026-09-24 at 19:50: hand-traced letters rendered this way are read instantly.

| panel | what it was | what the reader said |
|---|---|---|
| M | the human labels | Η and Κ read immediately; the third letter "looks cut" |
| N | **the published reference** | "compared to usual, this time you can make out Η and Κ — not perfect, the Η more than the Κ, but with a little effort you could see it"; the third letter illegible |

**So the published reference carries letter shape that our own maps do not.** Every arm of this project has been
trained toward a target that is partially legible, and none of them is. The ceiling is not in the data or in the
target: it is in our models. That reverses the hypothesis this test was built to check — it was built expecting to
find the target unreadable.

**Same contamination caveat, and it is serious here**: the reader knew these three letters. "With effort you could
see it" is exactly the sentence a contaminated reader produces. This is why the test is being rerun tomorrow with a
naive reader on four maps at once.

**A framing bug the reader found in one sentence.** "The third letter looks cut" — on the panel showing the *truth*,
where nothing can be blamed on the model. The control zone ran to X 12210; the third labelled component ends at
X 12576. It was cut by 366 px. Every legibility test run on that zone since 2026-09-24 17:40, including the
neutral reader's, showed a truncated third letter. Corrected: the new frame is Y 4260–6772, X 7324–12876, which
holds all three letters entirely with 300 px of margin.

### Shape, measured two ways, 2026-09-24 22:40 — one way worked, the other came out null

Neither separation nor fill says anything about **shape**. Two descriptive measures, computed after seeing the
maps and therefore not tests, both at 53.4 % matched fill in the control zone:

| map | connected shapes | median shape size | max inscribed thickness |
|---|---|---|---|
| the human labels | **5** | 7 912 px | 445 px |
| published reference | 17 | 509 px | 390 px |
| `demi` (PR-10) | 45 | 50 px | 591 px |
| `pr2v24` | **192** | **3 px** | 398 px |

**The component count works and orders the maps**: truth 5 < reference 17 < demi 45 < pr2v24 192. The
half-resolution arm produces **four times less debris** than its full-resolution twin — the direction PR-10
predicted, obtained without any letter becoming readable. All four maps carry 3 or 4 shapes of letter size; what
separates them is the confetti around those shapes.

**The thickness measure came out null, and that is reported rather than dropped.** It was designed specifically to
replace a contaminated eye: a letter is a stroke, a blob is a mass, and the largest inscribed disc should tell
them apart. It does not — 445, 390, 398 px for truth, reference and `pr2v24`. The difference a reader sees between
the reference's forked Κ and `pr2v24`'s lump is **topological**, not a matter of thickness, and this measure does
not capture it. The eye is still the instrument here.

**Removing the debris does not recover the letters.** Deleting every component smaller than half a labelled letter
and re-thresholding to the same fill leaves 3–4 large shapes in each map: the reference's are still letter-like,
`pr2v24`'s and `demi`'s are still lumps. The noise is not what hides the letters.

## PR-11 — Is our model's output the teacher's, plus noise?

*Registered 2026-09-24 23:15, before any reader has seen a smoothed map. No training is involved: every prediction
this uses already exists on disk, and the operation under test is a one-line post-process.*

**The cascade that raises the question.** Measured tonight in the control zone, all at matched fill (53.4 % of the
known letters marked), counting connected components:

| map | objects | per letter | median object size | box occupancy |
|---|---|---|---|---|
| the human labels | 5 | **1** | 1 808 px | 36 % |
| the organisers' prediction, inside the labelled zone — segB | 15 | ~3 | 424 px | 53 % |
| the organisers' prediction, inside the labelled zone — w00 | 24 | ~3 | 672 px | 54 % |
| `demi` (PR-10) | 112 | ~37 | 222 px | — |
| `pr2v24` | **489** | **~160** | 56 px | — |

Two things follow. The teacher **already** breaks each letter into about three pieces, and it does so equally on the
training segment and the evaluation segment — so that is not a property of the segment we chose. And our student
then fragments **twenty to a hundred times further**. The second gap is not a ceiling in the data.

**What a Gaussian blur does to it**, re-thresholded after each blur so the fill stays at 53.4 %:

| blur σ (full-res px) | `pr2v24` objects | median size |
|---|---|---|
| 0 | 489 | 56 px |
| 8 | 33 | 122 px |
| 16 | 23 | 228 px |
| **32** | **14** | **427 px** |
| 128 | 9 | 363 px |

**At σ = 32 px our model reaches the teacher's fragmentation exactly** — 14 objects of 427 px against the teacher's
15 of 424 px — at the same fill, with no retraining.

**Claim under test.** The difference between our maps and the teacher's, in everything that governs legibility, is
pixel-scale noise and nothing else.

**Primary endpoint, defined here before anyone looks.** A reader with no connection to the project, shown the same
zone rendered from four maps in randomised order at matched fill — the human labels, the organisers' prediction,
`pr2v24` blurred at σ = 32, and `demi` blurred at σ = 32 — is asked: *do you see letters, and where?*

**Prediction.** The reader reports letters on the **blurred** maps at least as often as on the organisers'
prediction, and in the same places.

**What would invalidate it.** The reader reads the organisers' map and not the blurred ones. Then matching the
component count does not match what makes a letter readable, and the remaining difference is shape, not noise —
which sends the next experiment back to training, not to post-processing.

**Stated in advance.** A blur is a cosmetic operation: it cannot add information. If it makes our maps readable,
what that shows is that the information was **already there and buried**, not that the model improved — and the
honest use of that result is a better read-out, not a claim of a better model. Conversely, matching the teacher's
object count is not the same as matching its shape; PR-9 and PR-10 both punished the assumption that one number
standing in for legibility would behave.

**Also registered, because tonight produced two of them.** Two earlier hypotheses of mine died on measurement and
are recorded so they are not silently revived: *the training labels are scattered noise* — false, they sit on the
writing lines at 4.9 σ above a position-shuffled control; and *our threshold shattered the letters* — false, no
threshold from 40 to 200 produces letter-sized objects, lowering it only adds more specks.

## PR-12 — Does the smoothed map show letters where no one has labelled any? *(conditional on PR-11)*

*Registered 2026-09-24 23:20, before any reader has seen any of these zones, and before PR-11 has been answered.*

**This test is not run unless PR-11 passes.** If a naive reader does not read the smoothed maps in the zone where
the letters are known, there is no reason to ask where else they appear, and running this anyway would be fishing.

**Why it exists.** Everything measured on 841 so far happens where labels already exist — that is, where the answer
is known. A *new* reading means letters somewhere nobody has marked. The smoothed `pr2v24` sheet, thresholded at
53.3 % fill on the known letters, holds 516 objects, of which **19** pass a shape criterion calibrated on the five
real letters and nothing else: largest dimension 900–3 000 px (the real ones: 1 368–2 128) and bounding-box
occupancy 20–55 % (the real ones: 36 % median; a disc would be 79 %).

**The circularity, and what neutralises it.** Selecting the zones that most look like letters and then asking a
reader whether they see letters is circular by construction. The criterion cannot be trusted on its own. What
makes the test informative is the **control arm**: four zones drawn at random from the marked sheet, outside the
labelled region, the same size, shuffled with the four best candidates, rendered identically. The reader is not
told there are two kinds.

**Endpoint.** A naive reader, eight panels, one question: *do you see letters, and where?*

**Prediction.** Letters reported on more candidate zones than control zones, by at least **3 to 1**.

**What would invalidate it.** Letters reported on candidates and controls at similar rates — the criterion selects
appearance, not writing. Or nothing anywhere — the criterion selects nothing at all.

**Stated in advance.** Eight panels is a small test and one reader is one reader; a 3:1 split on eight panels is
not a significance claim, it is a bar chosen to be interpretable. And a positive result is **not a reading**: it
would say "these zones deserve a real transcription attempt", not "these are letters".

**Zones, fixed here so they cannot be reselected after seeing the answer** (full-resolution, Y0 Y1 X0 X1):
candidates 8256 10768 9936 15488 · 6128 8640 8568 14120 · 6688 9200 11344 16896 · 8256 10768 12712 18264;
controls 7491 10003 2647 8199 · 1100 3612 2356 7908 · 5533 8045 2587 8139 · 8509 11021 12899 18451.

### PR-11 — correction, 2026-09-24 23:30, before any reader has looked

The sentence *"at σ = 32 px our model reaches the teacher's fragmentation exactly — 14 objects of 427 px against
the teacher's 15 of 424"* is **wrong, and it was the sentence the registration was built around.** It compared two
measurements that are not the same measurement: our arms were counted in the reading frame at full resolution,
the teacher was counted in a dilated neighbourhood of the labels across the whole segment at level 3. Caught by a
blind re-derivation asked only to apply one procedure to all three maps.

Measured identically — same frame (Y 4260–6772, X 7324–12876), full resolution, threshold chosen so that 53.4 % of
the 3 labelled letters are marked:

| map | blur σ | threshold | fill | components | median largest dimension |
|---|---|---|---|---|---|
| the organisers' prediction | — | 235 | 52.9 % | **19** | **142.5 px** |
| `pr2v24` | — | 209 | 53.3 % | 489 | 56.0 px |
| `pr2v24` | 8 | 206.5 | 53.4 % | 33 | 122.0 px |
| `pr2v24` | 16 | 202.7 | 53.4 % | 24 | 228.0 px |
| `pr2v24` | **32** | 195.2 | 53.4 % | **14** | **426.5 px** |
| `demi` | — | 229 | 53.4 % | 112 | 222.0 px |
| `demi` | 32 | 210.4 | 53.4 % | **14** | **287.0 px** |

**What survives.** Our raw map is fragmented far beyond the teacher's — 489 pieces against 19 — and a blur removes
that gap at a cost of nothing. **What does not survive**: at σ = 32 our maps do not *match* the teacher, they
overshoot it. They end up with fewer pieces (14 against 19) and pieces three times larger (426 against 142).

**And that makes the teacher's legibility harder to explain, not easier.** The teacher is read with effort at 19
components of 142 px median; our blurred map has 14 components of 426 px and is the thing under test. So the
component count does not predict what a reader sees — the second measure tonight to fail at standing in for
legibility, after the inscribed-thickness one. That is now two independent failures, and the lesson is the same
one PR-9 taught: **no single shape number has yet predicted a reading.** PR-11's endpoint stays what it was, a
reader, and the registered prediction is unchanged; only my description of what σ = 32 achieves is corrected.

### PR-11 — a second prediction, registered 2026-09-24 23:40, still before any reader has looked

Every comparison since 2026-09-24 has been made **at matched fill** — the threshold of each map is set so that it
marks 53.4 % of the labelled letter pixels. That fixes **recall** and makes it identical everywhere. The other half
was never looked at: **precision**, the share of what a map blackens that actually falls on a letter. Two maps can
cover the same half of the letters while one blackens three times more background than the other.

Measured in the PR-11 frame, at that same matched recall:

| map | recall | **precision** | IoU |
|---|---|---|---|
| the organisers' prediction | 52.9 % | **85.8 %** | 0.486 |
| `demi`, blurred σ = 32 | 53.5 % | 77.2 % | 0.462 |
| `demi`, raw | 53.4 % | 76.3 % | 0.458 |
| `pr2v24`, blurred σ = 32 | 53.5 % | 66.2 % | 0.420 |
| `pr2v24`, raw | 53.3 % | **64.0 %** | 0.410 |

A third of what our full-resolution arm blackens is not on a letter. And this is the first number in this project
that orders the maps the same way the one legibility observation does: the teacher was read with effort, ours was
not, and `demi` sits between them. (At fixed recall, IoU is a monotone function of precision, so it carries the
same information here and is printed only for continuity with earlier tables.)

**Registered prediction, second and independent of the first.** When the naive reader judges PR-11's four panels,
**the panels they report letters on will be the higher-precision ones**, in that order. Specifically: the
organisers' panel is read at least as often as `demi` blurred, which is read at least as often as `pr2v24`
blurred.

**What would invalidate it.** The reader reads `pr2v24` blurred as readily as the organisers' panel, or reads none
of them. Then precision joins component count and inscribed thickness on the list of shape numbers that do not
predict a reading, and the honest conclusion is that we still have no measurable proxy for legibility at all.

**Stated in advance.** One legibility observation is what suggested this ordering, and a prediction fitted to one
observation is worth very little until it survives a second. It is registered precisely so that it can fail.

**A non-finding, recorded so it is not rediscovered.** Our maps looked systematically shifted by −40 px in Y
against the labels while the teacher sat at 0 — which would have meant a registration bug in our stitching. It is
an artefact of a 40-pixel search step: at 8-pixel resolution the teacher is itself at −16 px, our sheets at −24 to
−32, and correcting the shift buys between 0.003 and 0.022 of IoU. Against a 22-point precision gap that is
nothing. **There is no registration bug.**

### Explored and closed the same night, 2026-09-24 23:45 — combining our maps does not help

Measured in the PR-11 frame at matched recall, so directly comparable to the precision table above. *(Object counts
are deliberately omitted here: they were computed at level 3, not at full resolution, and mixing those two is the
error corrected earlier tonight.)*

| map | precision |
|---|---|
| `demi` alone | **76.3 %** |
| mean of `pr2v24` and `demi` | 72.1 % |
| minimum — both arms agree | 71.5 % |
| maximum — either arm | 71.6 % |
| mean, then blurred σ = 32 | 73.7 % |
| minimum, then blurred σ = 32 | 74.0 % |

**Every combination lands between the two arms and none beats the better one.** The weaker arm drags the stronger
one down; there is no free ensemble gain here. Combining with the organisers' map reaches 83–86 %, which is simply
the organisers' map back again (85.8 % alone), so there is nothing there either.

**What this leaves.** `demi` alone, at 76.3 % precision, is the best map this project has produced, and nothing
costless improves it. That deserves stating precisely, because it sits next to a failure: **PR-10 failed its
registered prediction** — no reader saw letters on either arm — **and the arm it produced is nevertheless our best
map by the only quantity that has so far tracked the one legibility observation we have.** Both sentences are
true, the first is the registered result, and the second is not a rescue of it.

### Explored the same night, 2026-09-24 23:50 — where the wrong ink goes, and one read-out that helps a little

**Where the wrongly-marked ink sits**, decomposed by distance to the nearest labelled letter, at matched recall:

| map | precision | < 200 px (hugging the stroke) | 400–800 px | beyond a letter's width |
|---|---|---|---|---|
| the organisers' prediction | 85.8 % | **73 %** | 19 % | 0 % |
| `pr2v24` | 64.0 % | **43 %** | **37 %** | 0 % |
| `demi` | 76.3 % | 65 % | 18 % | 0 % |

**No map invents ink far from the letters** — nothing beyond one letter's width, on any of them. The difference is
entirely in the 200–800 px band: the teacher's surplus **thickens the stroke**, ours **fills the gaps inside the
letter**. Ink 400–800 px from a stroke is exactly what closes the fork of a Κ and turns it into a lump. This is
the first mechanism proposed tonight that explains what a reader sees, and `demi` halves the defect (37 % → 18 %),
which is where its 12 points of precision come from.

**Hysteresis thresholding**, the classical remedy for that defect — keep weak ink only where it touches strong ink
— tuned on the control zone at matched recall: `pr2v24` 64.0 → **74.5 %**, `demi` 76.3 → **81.1 %**.

**And the honest version of that number.** Those thresholds were tuned where the answer is known. Applied
unchanged to the three held-out windows, the average gain reads +9.1 points for `pr2v24` and +2.7 for `demi` —
**but that average is not the result.** It is dominated by window 1, where the fixed thresholds land at 8–23 %
recall instead of 53 %, and precision rises mechanically when recall falls. On the two windows where recall is
comparable, the gain is **+1.6 and +2.6 points** for `pr2v24`, **+0.2 and +0.7** for `demi`.

**So: hysteresis helps, modestly, and the fixed thresholds do not transfer their operating point.** A read-out
tuned on the zone that holds the answer is worth what it is worth, and quoting the +9.1 would have been quoting an
artefact of a shifted operating point. Anything built on this needs thresholds set per zone by a rule that does
not look at the labels.

### The night's correction, 2026-09-24 23:55 — almost nothing measured in the control zone replicates

Every number produced tonight — the precision ranking, the halo decomposition, the hysteresis gain — was measured
in **one zone of one segment**, the control zone, which is also the zone whose answer is known and on which
thresholds were tuned. The segA sheet finished at 23:20 and made the replication possible: the same precision
measurement on the **six held-out windows**, three per segment, which were never used to set anything.

| | control zone (one place) | six held-out windows |
|---|---|---|
| the organisers' prediction | 85.8 % | 82.9 % ± 12.7 |
| `demi` | 76.3 % | 78.2 % ± 14.6 |
| `pr2v24` | 64.0 % | 77.1 % ± 15.4 |

Window-to-window variation (precision runs from 53 % to 96 %) dwarfs every gap, so the comparison must be paired:

| paired difference | mean | t, 5 d.f. | verdict |
|---|---|---|---|
| teacher − `pr2v24` | **+5.8 pt** | 2.30 | a tendency; the 5 % bar is 2.571 |
| teacher − `demi` | +4.7 pt | 1.77 | a tendency |
| **`demi` − `pr2v24`** | **+1.1 pt** | **0.55** | **nothing** |

**What this destroys.** The sentence written two hours earlier — *"`demi` alone, at 76.3 % precision, is the best
map this project has produced"* — does not survive. The 12-point gap between `demi` and `pr2v24` is a property of
the control zone and of nowhere else; on six windows that never set anything, the two arms are indistinguishable.
So PR-10's arm is not measurably better than its twin after all, and the consolation offered alongside PR-10's
failure is withdrawn.

**What survives, weakly.** The teacher is ahead of both our arms by about 5 points of precision, consistently in
sign on 4 of 6 windows but not significantly on 6. That is compatible with the one legibility observation and
proves nothing on its own.

**What this says about the last two days of method.** The control zone was chosen because it holds the labelled
letters — which is exactly what makes it unrepresentative. Every quantity measured there is measured where the
teacher is strongest and where our thresholds were tuned. **The halo decomposition (43 % against 73 % hugging the
stroke) and the hysteresis gain (+10.5 points) were measured there too, and neither has been replicated.** They
are hypotheses, not findings, and they are labelled as such from here.

**The instruction that follows, for tomorrow.** Nothing measured in the control zone counts until it is repeated
on the six held-out windows. That is one line of code away every time, it was skipped all night, and it changed
the answer.

### PR-11 — amendment, 2026-09-25 morning, still before any reader has looked

**The panel as first generated would have answered its own question.** PR-11 registers four maps shown together in
randomised order, one of them being *the human labels*. Rendered exactly like the other three and stacked in one
image, that panel shows Eta Kappa Alpha, clean and unambiguous, in the same frame and at the same three positions
as the maps under test. A reader meets it first and then looks at the others already knowing which three letters
to find and exactly where. Whatever they say next is guided recognition, not reading, and the primary endpoint —
*do you see letters, and where?* — can no longer be answered honestly.

This is the failure PR-10's generator already forbade under the name *no red outlines*: a contour tells the reader
where the letter is and destroys the question. A truth panel is worse, because it also supplies the answer.

**What changed.** The blind image now carries **three** panels — the organisers' prediction, `pr2v24` blurred at
σ = 32, `demi` blurred at σ = 32 — randomised, at matched fill (52.9 / 53.4 / 53.4 % of the known letter pixels,
a spread of 0.5 points, well inside the 3-point bar this project uses). The labels are kept in the *legended*
version, which is only looked at after the reader has answered.

**Why this does not weaken the test.** The truth panel was serving as a positive control — a check that letters
rendered this way can be read at all. That control already exists and is dated: on 2026-09-24 at 19:50 the same
letters, traced by hand and rendered identically, were read instantly. It does not need to be paid for a second
time in blindness.

**Two other leaks removed from the caption**, which said *"the three letters fit entirely in the frame"*. That
sentence asserts there are letters and says how many, in a test whose whole question is whether any are visible,
and it sits one line below *"I see nothing is a complete answer"* — which it contradicts. The caption now states
only what it needed to state: that the frame cuts nothing. It also said *four panels* and there are three.

**What is unchanged.** Both registered predictions, the frame, the seed, the matched fill, the σ = 32 setting, and
the conditional status of PR-12. No reader had seen any version of this image when it was regenerated, so this is
an amendment before data, not after. The flawed image is kept on disk as
`2026-09-25_PR11_PERIME_verite_visible.png` rather than deleted.

**The general point, for the record.** Every blinding defect this project has found — the unbalanced draw on
2026-09-24 that fell the same way four times out of four, the frame that cut the third letter, and now a panel
that gave the answer away — was found by *looking at the image*, not by reading the script that produced it. The
script was correct each time: it randomised, it matched the fill, it rendered what it was asked to render.

## PR-13 — a model that was dismissed on the wrong criterion

*Registered 2026-09-25, before any map from this checkpoint has been rendered or looked at. No training: the
checkpoint has been on disk since 2026-09-21 10:14.*

**What happened.** `ink_841_ctx192` is the one run of this project that enlarges the network's field of view
**without losing resolution**: patch 64x192x192 instead of 64x128x128, batch 1 with 8 accumulation steps, same
recipe otherwise. It finished on 2026-09-21 at 10:18 and was closed the same morning with the sentence *"more
context does not break the ceiling"*, on this evidence: mean IoU 0.599 at its best checkpoint against 0.586 for
the previous best, **+0.013, inside the +/-0.03 noise between neighbouring checkpoints.**

That judgement used IoU. By 2026-09-25 this project has six quantities that fail to track what an eye sees —
separation, fill at matched noise, object count, median object size, precision at matched recall, and per-letter
IoU. **Its map was never rendered and never looked at.** A run was closed on the strength of a number that has
since been shown, six times over, not to measure the thing the project is trying to produce.

**Why it is worth re-opening now, and not any of the other closed runs.** PR-10 tested field of view by halving
the resolution, and confounded two causes: it added context and destroyed detail in the same move, so its failure
closes only *"field of view obtained that way, at that cost"*. `ctx192` changes field of view **alone**, at full
resolution — 1/9.3 of a letter instead of 1/14. It is the clean arm of the experiment PR-10 ran dirty, and it has
already been paid for.

**Primary endpoint.** A reader with no connection to the project, shown the PR-11 frame rendered from `ctx192`
and from the organisers' published prediction at matched fill, in randomised order, is asked *do you see letters,
and where?*

**Prediction, and it is a prediction of failure.** The reader does **not** read `ctx192` as well as the
organisers' map. Base rates say so: PR-9 and PR-10 both failed, the organisers' map has now been picked out twice
by the same eye without knowing which it was, and a 1.5x change in field of view is small next to the 14x that
separates the window from a letter. Registering a failure in advance is not pessimism — it is what makes a
success, if it comes, worth something.

**Secondary, and this one is informative whichever way the primary falls.** Object count per letter at matched
fill: `pr2v24` (full resolution, 128 px window) fragments each letter into about 160 pieces, `demi` (half
resolution, same window, so 2x the field of view) into about 37. **Prediction: `ctx192` fragments less than
`pr2v24`.** If it does, field of view is what reduced fragmentation in PR-10, not the loss of resolution, and
the two causes PR-10 confounded are separated. If it does not, the reduction seen in `demi` was the resolution
change — or an artefact of counting objects on a grid with half the pixels, which is checked below.

**A confound declared before measuring it.** `demi`'s object count was measured on a half-resolution grid, where
a speck smaller than one coarse pixel simply disappears. Part of the 160 -> 37 drop may be the counting grid and
not the model. Both maps are therefore counted on the same full-resolution grid before this secondary is read.

**What would make this whole test void.** `ctx192` was trained on `ink-dataset-teacher/841` segment w00 and is
here applied to segB, a segment it never saw. So were the other arms, so the comparison is fair — but if its map
is empty or saturated on segB, that is a transfer failure, not a legibility result, and it is reported as such.

### PR-13 — RESULT, secondary, 2026-09-25 09:20. The prediction is refuted, and in the informative direction

**Transfer works.** `ctx192` had never seen segB. Its map on the PR-11 frame has mean 108, standard deviation 60,
no saturated pixel at either end. This is not a transfer failure, so what follows reads as a legibility result.

**Objects per letter at matched fill, all counted on the same full-resolution grid:**

| map | window | resolution | objects per letter |
|---|---|---|---|
| the organisers' prediction | — | — | **6** |
| `demi` (PR-10) | 128 px | half | 37 |
| `pr2v24` | 128 px | full | 163 |
| **`ctx192`** | **192 px** | **full** | **316** |

**The registered secondary said `ctx192` would fragment less than `pr2v24`. It fragments about twice as much.**
A wider window at full resolution did not reduce fragmentation; it increased it. So the reduction seen in `demi`
was not the field of view — which is the one thing this arm was re-opened to establish, and it establishes the
opposite of what was predicted.

**And the confound I declared, checked properly the second time.** The first check was vacuous and printed a
reassuring number: I upsampled `demi` to full resolution by pixel replication and re-counted. A 2x2 replication
cannot split or merge a connected component, so the count is identical *by construction* — the verification
verified nothing. Done the right way round, by taking the full-resolution maps **down** to the half grid and
re-thresholding at matched fill there:

| map | full grid | half grid | what the grid alone removes |
|---|---|---|---|
| the organisers' prediction | 6 /letter | 6 /letter | **0 %** |
| `pr2v24` | 163 /letter | 65 /letter | 60 % |
| `ctx192` | 316 /letter | 140 /letter | 56 % |

**So `demi`'s 37 against `pr2v24`'s 163 is really 37 against 65 once both are counted on the same grid.** About
half of that arm's apparent advantage in fragmentation was the counting grid. The declared confound was real and
it was worth declaring. Note also what the first row says: the organisers' map loses **nothing** to the coarser
grid, because it has no pixel-scale specks to lose. That is the difference, stated in one number.

**A limitation that is not an excuse, because it was knowable in advance.** `ctx192`'s best checkpoint by IoU was
step 6 000; only step 16 000 survives on disk, and the run's own profile was *"best early, then oscillates"*. This
result therefore tests the checkpoint that exists, not the run's best. It does not rescue the prediction — a
factor of two in the wrong direction is not a checkpoint effect — but a re-run keeping step 6 000 would be the
honest way to close the field-of-view question for good.

**The primary endpoint is untouched and still pending**: a naive reader on `2026-09-25_PR13_AVEUGLE.png`, two
panels, matched fill, randomised. The registered prediction there was also failure.

### PR-13 — RESULT, primary, 2026-09-25. The prediction of failure holds, and the pattern is now three for three

**The reading.** Panel T, "sans hesitation". **T is the organisers' published prediction.** `ctx192` was panel U.

**The third time the same map has been picked out without knowing which it was:**

| date | test | panels | picked | what it was |
|---|---|---|---|---|
| 24/09 | truth vs target | M, N | **N** | the organisers' prediction |
| 25/09 | PR-11 | P, Q, R | **R** | the organisers' prediction |
| 25/09 | PR-13 | T, U | **T** | the organisers' prediction |

Three images, three randomisations, three different panel letters, one map. **What this is worth on its own:**
under a null of random choice the two clean comparative picks give 1/3 x 1/2 = **p = 0.167**, which is not
significant and is not claimed to be. What carries the weight is that the direction never varies and that it
agrees with a measurement taken independently — objects per letter, 6 for the organisers against 163 and 316 for
our two arms.

**A limitation that is now the project's binding constraint, and it is stated plainly.** The readers were Lilian
and his partner, and both already knew which three letters are in this frame. The registered question — *do you
see letters, and where?* — cannot be answered honestly by either of them. What survives contamination is the
**comparative ranking**: knowing which letters to look for does not tell you which rendering restores their shape
at matched fill and identical rendering. That is what was asked and that is what is reported. The primary endpoint
of PR-11 and PR-13, as registered, has **not** been answered by a naive reader and is recorded as unanswered
rather than as passed or failed.

**What the field-of-view question now looks like, closed from both ends.** Widening the window by halving
resolution (PR-10) produced no letters. Widening it at full resolution (`ctx192`) produced twice the
fragmentation. Both directions of the only lever this project had on field of view make things worse or do
nothing. That lever is closed until there is a reason to reopen it that is not "the window is small".

## PR-14 — Does the map that actually reads show letters anywhere else?

*Registered 2026-09-25, before any of these zones has been rendered or looked at by anyone. No GPU: the
organisers' prediction has been on disk since the dataset was downloaded.*

**Why this test and not another.** The project's goal, set on 2026-09-23, is to publish the first reading of
PHerc. 841. Three blind comparative readings now point the same way: the map that reads is the organisers', not
ours. Nothing in the goal requires the reading to come from our model. So the direct question is: **outside the
zone that is already labelled, does the organisers' map show letter-shaped structure anywhere on these two
sheets?** That is the only thing that would produce a *new* reading.

**Why Lilian can be the reader here, when he cannot for PR-11 and PR-13.** Contamination is local. He knows the
three letters in the control frame because he has seen them. **Nobody knows what is in these zones** — they have
never been labelled, by anyone. A reader who knows Eta Kappa Alpha in one frame carries no knowledge into a frame
he has never seen. This is what makes the test runnable at all, now that the pool of naive readers is two people
who have both seen the answer.

**The search, and the guard against its own circularity.** Zones are ranked by how many objects pass a shape
criterion calibrated on the *known* letters, not chosen by eye: largest side 900-3000 px (the five real ones:
1 368-2 128) and box occupancy 20-55 % (the five real ones: 36 % median; a disc is 79 %). Selecting the zones
that look most like letters and then asking whether letters are visible there is circular. **The guard is in the
protocol, not the criterion**: the same number of zones is drawn **at random**, same size, same rendering, and
the two families are mixed. If the reader reads the selected ones and not the controls, the signal is real; if
both or neither, the criterion is worth nothing.

**What the search found, and it is thin.** On the whole of segB the organisers' map has 212 objects at matched
fill, of which **8** pass the shape criterion, and they cluster in **one** zone outside the labelled area. On segA,
201 objects, **10** pass, in **two** zones. Three candidate zones on two full sheets. That number is itself a
result and it is registered as such before anyone looks: *the map that reads shows almost no letter-shaped
structure outside the zone that was already labelled.*

**A bug found and fixed during the search, recorded because it would have manufactured evidence.** The first run
returned four candidate zones on segB that were the same place seen four times — the exclusion radius after
picking a peak was half a window, so consecutive zones overlapped by 50 %. Showing those as four panels would
have counted four successes for one observation. The radius is now the full window.

**Primary endpoint.** Six panels — three candidates, three controls drawn at random, matched per segment so the
segment itself is not a tell — same threshold per segment (set on that segment's known letters at 53.4 % fill),
same rendering, randomised order. The reader is asked: *do you see letters, and where?*

**Prediction.** The reader reads letters on the candidate zones and not on the controls. Under a null of random
choice, picking exactly the three candidates out of six has probability **1/20 = 0.05**.

**What would make it void, stated now.** If the reader reads all six, the rendering itself suggests letters and
the criterion means nothing. If the reader reads none, the honest conclusion is that **there is no second reading
to be had from this map on these two sheets** — which closes the goal as stated and forces a change of target,
not another experiment.

### PR-14 — amendment, 2026-09-25, before any reader has looked: the search was run with a blunt detector

**The positive control that should have come first.** PR-14 rests on a count: how many letter-shaped objects the
organisers' map carries outside the labelled zone. That count is worthless until the criterion is shown to fire
where letters are *known* to be. Measured (`scripts/critere_controle.py`), by applying the same criterion **inside**
the labelled zone across a sweep of thresholds:

| fill on the known letters | segB: shapes found among 5 known letters | segA: among 6 | shapes found outside, segB | segA |
|---|---|---|---|---|
| 29.8 % | 2 | 2 | 1 | 1 |
| 40.7 % | 3 | 2 | 6 | 2 |
| **53.4 %** *(what the search used)* | **4** | **4** | 4 | 5 |
| **70.0 %** | **5** | **5** | **13** | **13** |
| 85.4 % | 5 | 4 | 37 | 19 |
| 94.5 % | 3 | 3 | 12 | 30 |

**At 53.4 % the detector misses one known letter in five.** The whole sheet was searched with it. And 53.4 % was
never a detection threshold: it is the project's matched-fill constant, chosen to **compare two maps at equal
recall**. Carrying it into a **detection** problem was importing a number from a different question because it was
the number at hand.

**What is amended, and on what rule.** The threshold becomes the one where sensitivity on the *known* letters is
maximal, reached independently on both sheets at **70 %** (5 of 5 on segB, 5 of 6 on segA — segA never reaches
6 of 6 at any threshold). The rule is stated so it cannot be shopped: **the threshold is set on measured
sensitivity over known letters, never on how many candidates it produces outside.** That the count outside also
rises is a consequence, not the reason, and if the rule had pointed at 40 % it would have been taken there.

**What this withdraws.** This morning's registration said, before any reader looked: *"Three candidate zones on
two full sheets. That number is itself a result — the map that reads shows almost no letter-shaped structure
outside the zone that was already labelled."* **That is withdrawn.** It was a statement about a threshold that
misses a fifth of the letters it was calibrated on, not about the scroll. At full sensitivity the same search
returns **4 candidate zones on segB and 3 on segA**, and the honest version of the sentence is that nobody has yet
established how much is out there.

**The panel that results.** Eight panels: the two richest candidate zones per segment and four controls drawn at
random, none overlapping any other by more than 2 % — verified on the zones that actually reach the screen, not
only at the drawing stage. The cap of two candidates per segment is a **reader constraint** — seven candidates and
seven controls make fourteen panels that nobody examines carefully to the end — and it is fixed before looking at
which zones they are. Under a null of random choice, reading exactly the four candidates among eight has
probability **1/70 = 0.014**.

**Still unsearched, and stated so it is not forgotten.** A third sheet exists: the organisers' prediction for w00,
stored binarised as the teacher pseudo-labels (`ink-dataset-teacher/841/w00`). It has never been put through this
search. Any conclusion of the form *"there is nothing more to read on 841"* is premature while it sits there.

**The caption bug, for the third time.** The panel's heading said *"six endroits"* while showing eight, because
the count was written by hand. It is now computed. The same defect appeared on 2026-09-25 morning on PR-11
(*"quatre panneaux"* for three) and was fixed there and not here.

### PR-14 — RESULT, 2026-09-25. Null, and a measurement error of mine found while reporting it

**The reading.** *"Je ne vois aucune lettre."* Nothing on any of the eight panels. Four of them were the candidate
zones (A, E, G, H), four were controls. The registered prediction — the reader reads the candidates and not the
controls — **fails**, and it fails in the one direction that was written down in advance as conclusive:

> *"If the reader reads none, the honest conclusion is that there is no second reading to be had from this map on
> these two sheets — which closes the goal as stated and forces a change of target, not another experiment."*

**That conclusion stands for segA and segB, and it is correctly narrow.** It does not say there is no text there;
it says this map does not render anything a reader can read, in the places where its letter-shaped structure is
densest, at a threshold set for full sensitivity.

**But the sentence "not another experiment" was written when I believed three sheets carried one published map
each. Both halves of that were wrong**, and I found out while writing up the null.

**Error 1 — the sensitivity metric.** I "measured sensitivity" by counting the objects that pass the shape
criterion **inside** the labelled zone. That is not a sensitivity: one letter can produce several passing objects,
and the dilated zone spills around them. It only became visible when the count printed **10 of 7 letters found** on
w00 — impossible. On segA and segB it had never exceeded the letter count, so it passed unnoticed, and **it is
what chose PR-14's 70 % threshold**. Correct definition, now implemented in `scripts/sensibilite.py`: a letter is
found if at least one passing object overlaps it; only label components of letter size (900-3000 px) count in the
denominator, since a 272 px fragment cannot be found by a criterion that demands 900.

Re-measured properly, the calibrated point for segA is **53.3 % (4 of 6)**, not 70 %. PR-14 therefore ran segA's
zones at a more permissive threshold than the rule prescribes — which yields **more** candidates, not fewer, so
the null result is if anything generous and stands.

**Error 2 — four published maps never searched.** Each 841 segment carries three prediction files in the bucket;
the project's own notes recorded this on 2026-09-23 and I searched one map per sheet anyway. For w00 there are
**four greyscale published predictions on disk**, in `preds/`, and I had searched only the *binarised* copy filed
as training pseudo-labels in `ink-dataset-teacher` — the version that exists to be a target, not to be read.

**What they show, at properly calibrated sensitivity:**

| published map | best sensitivity | at fill | letter-shaped objects outside the read zone |
|---|---|---|---|
| segB `pred.tif` | 5 / 5 | 70.0 % | 11 |
| segA `pred.tif` | 4 / 6 | 53.3 % | 5 |
| w00 `new_canon_20260417_recale` | **7 / 7** | 52.7 % | **1** |
| w00 `ps48_640_640_smooth_0.1_…` | **7 / 7** | 53.6 % | **2** |
| w00 `w00_canonical_030726_reverse` | **7 / 7** | 53.5 % | **3** |
| w00 `w00_canonical_2um_…` | **7 / 7** | 69.9 % | **8** |

**Three of the four w00 maps reach full sensitivity** — better than segA's map ever does — and at that point they
show between **one and eight** letter-shaped objects outside everything that has already been read. That is a
sharper version of the original claim than the one I withdrew this morning, because this time the detector is
known to find every letter it is shown.

**So the goal is not closed, but it is now measurably narrow.** One test remains before the question is genuinely
settled: those one-to-eight objects on w00, put to a reader the same way. If they read as nothing, three sheets
and six published maps have been searched at declared sensitivity and the answer is no.

## PR-15 — the last place left to look on PHerc. 841

*Registered 2026-09-25, before any zone of w00 has been rendered or seen by anyone. No GPU. This is the test named
at the end of PR-14's result as the one that settles the question.*

**Where this sits.** PR-14 returned null on segA and segB: a reader saw no letters in the zones where the
organisers' map carries its densest letter-shaped structure. Writing that up uncovered four greyscale published
predictions for w00 that had never been searched, because the only copy of w00's prediction the project had ever
touched was the **binarised** one filed as training pseudo-labels. Three of the four reach **7 of 7** sensitivity
on w00's known letters — better than segA's map reaches at any threshold — and at that point they show 1, 2, 3 and
8 letter-shaped objects outside everything already read.

**The map under test and why that one.** `w00_canonical_2um_20250807020208.tif`, at 69.9 % fill, where it finds
7 of 7 known letters and shows **8** objects outside. It is the only one of the four with enough to form a zone;
the other three, with 1, 2 and 3 objects, cannot produce a window containing two and are reported by their counts
rather than by a panel. Choosing the richest map is declared here rather than justified afterwards.

**Protocol, unchanged from PR-14 because it worked.** Candidate zones ranked by density of shape-criterion
objects; the same number of controls drawn at random, same size, same map, same rendering, none overlapping any
other by more than 2 %, checked on the zones that reach the screen. Threshold fixed once on the *known* letters,
never per zone. Randomised order, key sealed.

**Prediction.** The reader reads letters on the candidate zones and not on the controls.

**And the prediction I actually hold**, recorded separately so the first cannot be softened afterwards: **I expect
null.** PR-14 was null, the shape counts here are smaller still, and eight objects on a whole sheet is not a
paragraph. This is registered as the test that closes a question, not one that is expected to open it.

**What a null means this time, and it is stronger than PR-14's.** Three sheets, six published maps, every one
searched at a threshold where its sensitivity on known letters was measured rather than assumed, with the reading
done blind against random controls. A null then means: **the published maps of PHerc. 841 do not carry a second
readable passage that this method can find.** The goal set on 2026-09-23 — publish the first reading of
PHerc. 841 — would not be reachable from the existing maps, and the honest move is to say so publicly with the
measurements attached, not to run a seventh variant.

### Explored and closed, 2026-09-25 midday — agreement between the published maps is chance

**A criterion better than the one PR-14 used, and it fails its own control.** Every search in this project asks
one map whether an object has the size and shape of a letter. w00 carries **four independent published
predictions**. Where several of them show a letter-shaped object at the same place, that is agreement between
differently-trained models, and one model's noise does not land where another's does.

Each map thresholded at its own maximal sensitivity (7 of 7 known letters, all four): 1 + 2 + 3 + 8 = 14
letter-shaped objects outside the read zone, clustered at one letter width (1 808 px) → **3 places where two maps
agree, 2 where three do**, two of them involving `ps48`, a visibly different recipe from the `canonical` family.

**Chance, measured before announcing anything** (20 000 draws, same counts per map, same clustering):

| null | p(≥ 3 two-map clusters) | p(≥ 2 three-map clusters) |
|---|---|---|
| **uniform** — points drawn anywhere on the sheet | 0.185 | **0.007** |
| **structured** — positions drawn from the real object positions | 0.541 | **0.135** |

**The naive null says p = 0.007. The right one says p = 0.135.** Letter-shaped objects are not spread uniformly:
they concentrate where the papyrus carries signal, so they land near each other **by themselves**, on every map at
once, with no letter involved. Three maps agreeing is unremarkable when all three are looking at the same damaged
sheet.

**Closed:** agreement between published maps does not beat chance on w00 as a search criterion.

**The methodological point, and it is the second time in one day.** The uniform null is the one that comes to
mind, it is three lines to write, and here it would have produced a publishable finding. The correct null
preserves the spatial distribution of the real data. *When testing whether points coincide, the reference chance
must have the same spatial distribution as the real points — otherwise you measure the structure of the substrate
and call it a signal.* Writing both takes ten lines, and only the comparison shows the gap.

### PR-15 — RESULT, 2026-09-25. Null. The search is finished.

**The reading.** *"Je ne vois aucune lettre."* Nothing on any of the six panels. Candidates were I, M, N;
controls J, K, L. The registered prediction fails, and it fails as the separately-recorded expectation said it
would — that expectation was written down precisely so this sentence could not be softened afterwards.

**The search, complete.** Three sheets, six published maps, each thresholded where its sensitivity on the *known*
letters was **measured** rather than assumed, each read blind against controls drawn at random:

| sheet | published map | sensitivity | letter-shaped objects outside | outcome |
|---|---|---|---|---|
| segB | `pred.tif` | 5 / 5 | 11 | PR-14, null |
| segA | `pred.tif` | 4 / 6 | 5 | PR-14, null |
| w00 | `new_canon_20260417_recale` | 7 / 7 | 1 | no zone possible |
| w00 | `ps48_640_640_smooth_0.1_…` | 7 / 7 | 2 | no zone possible |
| w00 | `w00_canonical_030726_reverse` | 7 / 7 | 3 | no zone possible |
| w00 | `w00_canonical_2um_…` | 7 / 7 | 8 | **PR-15, null** |

Agreement between those four maps, tested separately as a stronger criterion than any single map's shape rule:
**p = 0.135** against a null that preserves the real spatial distribution. Nothing.

**The conclusion, in the words registered before the data.** *The published maps of PHerc. 841 do not carry a
second readable passage that this method can find.* The goal set on 2026-09-23 — publish the first reading of
PHerc. 841 — **is not reachable from the existing maps**, and the honest move is to say so publicly with the
measurements attached rather than run a seventh variant.

**What this does not claim.** Not that PHerc. 841 has no more text: it has a great deal, and the maps simply do
not render it legibly. Not that no model could: only that the six published maps, and the two we trained, do not.
Not that the shape criterion is the right filter: it is calibrated on five to seven letters, and a criterion that
finds every known letter on three sheets can still be the wrong instrument for letters it has never seen.

**And the comparison that puts the number in context.** At identical sheet coverage (10.6 % marked), PHerc. Paris 4
segment w02 shows **158** letter-shaped objects outside its labels for 16 known letters; 841's w00 shows **8** for
7. Nine times poorer. Paris 4 w02 is the segment on which this project's own run 2 read ΤΗΟΚΑΤ outside the labels
on 2026-09-20, so it serves as the positive control for the entire search method: the detector finds a great deal
where text is known to be, and almost nothing on 841.

**Status of this repository, therefore.** It documents a failed attempt, in full, with everything that was
predicted before it was measured. That is what it is for.

## PR-16 — the positive control this whole search method never had

*Registered 2026-09-25, before any zone of PHerc. Paris 4 w02 has been rendered or seen. No GPU.*

**Why this must be run, and why it should have been run first.** PR-14 and PR-15 both returned null, and the
conclusion drawn from them is that PHerc. 841's published maps carry no second readable passage. **That conclusion
is only worth what the search method is worth, and the method has never been shown to work.** A blind panel of
candidate zones against random controls has produced two nulls and zero positives. If it produces a null where
text is *known* to be, then it measures nothing and both 841 results collapse — which is the exact mistake made
earlier the same day with an uncalibrated shape detector, repeated one level up. `METHOD.md` rule 1 says an
instrument must be shown to light up where something is known to be. It was never applied to this instrument.

**The segment and why it is the right one.** PHerc. Paris 4, segment w02. At the same sheet coverage that 841's
w00 reaches (10.6 % marked), its published prediction shows **158** letter-shaped objects outside its labels
against 841's **8**, with sensitivity **16 of 16** on its known letters. And it is the segment on which this
project's own run 2 read ΤΗΟΚΑΤ outside the label mask on 2026-09-20, confirmed against the organisers'
prediction — so text outside the labels is not hypothetical there, it has already been read once.

**Protocol, identical to PR-14 and PR-15 in every respect** so that a difference in outcome cannot be attributed
to a difference in method: candidate zones ranked by density of shape-criterion objects, an equal number of
controls drawn at random, same size, same map, same threshold — fixed once on the *known* letters at the fill
where sensitivity is maximal — same rendering, none overlapping any other by more than 2 %, randomised order,
sealed key, one question.

**Prediction.** The reader reads letters on the candidate zones and not on the controls.

**What each outcome means, written before the reading:**

- **Reader reads the candidates** → the method works. The two nulls on 841 are then statements about 841, and the
  conclusion registered in PR-15 stands.
- **Reader reads nothing** → the method does not detect letters even where they are known to exist. **PR-14 and
  PR-15 are then void**, the conclusion that 841's maps carry no second passage is withdrawn, and what needs
  replacing is the search, not the scroll.
- **Reader reads both candidates and controls** → the rendering suggests letters on its own; the shape criterion
  contributes nothing and the ranking is worthless.

**Stated plainly so it cannot be claimed later.** If this reads, it is **not** a new reading of Paris 4. That
scroll is the most worked-on in the field, its text is published, and "outside our label mask" does not mean
"never read by anyone". This panel is a control on our instrument and nothing else.

### PR-16 — RESULT, 2026-09-25. The control splits the method in two: the reading works, the criterion does not

**The reading.** *"Ce qui est sûr, je ne lis pas sur 4 panneaux, qui sont les Q S T U. Pour le panneau R je vois
peut-être un E et un T, et pour le panneau [V] je lis peut-être C I N."*

| panel | family | read |
|---|---|---|
| Q | **candidate** | nothing |
| R | control | **"maybe an E and a T"** |
| S | control | nothing |
| T | control | nothing |
| U | **candidate** | nothing |
| V | **candidate** | **"maybe C, I, N"** |

**One candidate read of three. One control read of three.** This is the third outcome registered in advance:
*the shape criterion contributes nothing and the ranking is worthless.* It is dead, and with it the premise of
PR-12, PR-14 and PR-15's zone selection. A criterion calibrated to find every known letter on three sheets does
not concentrate unknown letters into the zones it picks.

**But the other half passed, and that is what the control was for.** Shown a sheet where text is known to lie
outside the label mask, the reader **named letters** — not "I see something", but E, T, C, I, N. Shown fourteen
panels of PHerc. 841 across PR-14 and PR-15, the same reader named nothing at all. The rendering, the threshold,
the framing and the question do detect letters. They found none on 841.

**What the two scrolls give, once the worthless criterion is set aside and every panel counts as a sample:**

| | panels read | panels shown |
|---|---|---|
| PHerc. Paris 4 w02 | **2** | 6 |
| PHerc. 841 (PR-14 + PR-15) | **0** | 14 |

Fisher, one-sided: **p = 0.079.** Above the 5 % bar. A tendency, not a proof, and it is reported as one.

**What this does to PR-14 and PR-15.** Their conclusion survives, on a weaker and more honest basis than the one
registered. Not *"the densest letter-shaped zones of 841 were searched and found empty"* — that reading depended
on a criterion now known to select nothing. Instead: *fourteen zones of 841, effectively arbitrary, were read
blind and yielded nothing, while six zones of a sheet carrying text yielded two.* The direction is the same, the
evidence is thinner than claimed this morning, and the difference is stated rather than absorbed.

**What this does not claim.** Not that Paris 4 w02's panels are a new reading: that scroll's text is published and
this project's own run 2 read a line there on 2026-09-20. They are a control on our instrument. And "maybe" is the
reader's own word, kept.

**The lesson, and it is the fifth of the day.** Two nulls were interpreted for several hours as a fact about
PHerc. 841. They were only worth what the instrument was worth, and the instrument had never been shown to produce
a single positive. Running the positive control cost one panel and one question, and it changed what the nulls
mean. **A negative result should not be interpreted before the instrument that produced it has returned a
positive somewhere.**

## PR-17 — every panel this project has shown holds one line of text

*Registered 2026-09-25, before any enlarged panel has been rendered. No GPU, no new map: the same predictions,
the same thresholds, the same zones. One variable changes.*

**The measurement that raises it.** A panel in PR-10 through PR-16 is 2 512 px tall. The median letter is
**1 790 px** on PHerc. Paris 4 w02 and **1 808 px** on 841's segB. Every blind panel this project has ever shown a
reader therefore contains **1.4 letter heights — at most one line of text**.

**How it was found, which matters.** Not by inspection: by building an alignment score — the idea that letters sit
on lines, so their centres band along a common direction — and watching it fail. It failed because with a band of
half a letter height and a panel of 1.4 letter heights there are fewer than three bands: there is no line
structure *inside* a panel to detect. The failed instrument diagnosed the panel.

**Why this is the same mistake twice.** `METHOD.md` rule 4 already records it: a triage plate built with 900-pixel
windows for a scroll whose letters are ~1 000 px across, where everything looked shapeless *by construction*, and
where re-rendering at 4 000 px turned three candidates into letter sequences. The project fixed *window smaller
than a letter* and never asked *window smaller than a few lines*. A human reading damaged script uses the line: a
row of marks tells the eye where letters must be. A panel holding one line withholds exactly that.

**Claim under test.** The nulls of PR-14 and PR-15 are partly a property of the panel size, not only of the map.

**Design, paired, one variable.** The **same zones** already shown and already answered — PR-15's six on 841 w00
and PR-16's six on Paris 4 w02 — re-rendered from the same maps at the same thresholds, centred on the same
points, in windows of **10 048 × 11 104 px** instead of 2 512 × 5 552. That is ~5.6 letter heights by ~6.2 letter
widths: about five lines instead of one. Nothing else changes. Randomised afresh, sealed key, same question.

**Predictions, both registered:**

1. **On Paris 4 w02**, where the reader named letters on 2 of 6 small panels, the enlarged panels are read **at
   least as often** — 2 or more of 6. If enlargement *lost* readings, the rendering at this scale is wrong and the
   test says so.
2. **On 841 w00**, where the reader named nothing on 6 of 6, **at least one enlarged panel is read.** This is the
   prediction that carries the experiment, and it is a prediction *against* the conclusion published earlier
   today.

**What each outcome does.** If 841 reads at the larger scale, PR-14 and PR-15's conclusion — *the published maps
of 841 carry no second readable passage* — is **withdrawn**, and the finding becomes that the project spent two
days asking a question through a window too small to answer it. If 841 still reads nothing while Paris 4 does, the
conclusion stands and is strengthened, since both scrolls were then given the same fair chance.

**Declared in advance.** Lilian has now seen all twelve of these zones at the small scale, and read two of them.
He is no longer blind to *those two*. That contaminates panels R and V of the Paris 4 set upward: he may recognise
them. It does not contaminate the 841 set, where he saw nothing to remember, and prediction 2 is the one that
carries the experiment. The key is re-randomised so position cannot be used to match the old panels.

### PR-17 — amendment, 2026-09-25, before any reader has looked: three defects in the design as registered

**1. Candidates and controls are gone.** The registration reused PR-15's and PR-16's zones, which carry the
candidate/control labelling. PR-16 killed that criterion two hours earlier — keeping the labels would suggest
something is still being tested with them. The zones are now **drawn at random**, and the only reading of the
result is the **number of windows read on each sheet**.

**2. The same zones could not be kept.** Enlarging PR-15's and PR-16's centres to the new window size produced
overlaps of up to **74 % and 78 %**: six panels showing largely the same ground are not six samples, and a reader
who reads one "reads" its neighbours. This is the defect found this morning on a control that overlapped its own
candidate at 72.5 %, reappearing systematically the moment the window grew. Zones are now redrawn with an overlap
test, and the paired design is lost — stated rather than hidden.

**3. The window is 7 536 × 8 328, not 10 048 × 11 104.** w00 is only 15 827 px tall, so the registered size would
have covered two thirds of the sheet and made four disjoint windows impossible. The delivered size is ~4.2 letter
heights by ~4.7 letter widths: three to four lines instead of one.

**And a fourth defect, found by looking at the first render.** One panel came out three quarters blank with a
diagonal edge artefact: a prediction map is 0 off the unrolled sheet, so a uniform draw over the array catches
void and borders. A panel showing no papyrus can neither confirm nor refute anything and it dilutes the count.
Windows are now required to fall **85 % on papyrus**. Fifth time in two days that opening the PNG found something
re-reading the script would not.

**What survives unchanged:** the claim under test, the two maps, the two thresholds, the question, the sealed
keys, and prediction 2 — *at least one window of 841 w00 is read* — which is the one that carries the experiment
and is a prediction against the conclusion published earlier today. Prediction 1 is restated for the new design:
**Paris 4 w02 yields at least as many read windows as 841 w00.**

### PR-17 — result, 2026-09-25: the reader named letters on the control scroll and nothing on 841. Prediction 2 fails.

**The reading, sealed and committed before either key was opened** (`images/841_segments/2026-09-25_PR17_LECTURE.txt`,
commit `09a0da0`). Verbatim, in the reader's French:

> Sur PR17 A non on ne voit aucune lettre, par contre sur PR17B on voit sur le panneau J je pense un N mais c'est a
> peu pres la seule chose que je peux imaginer pour le panneau L je ne vois rien pour la panneau je vois des
> strucutures qui ressemble a des lettres pour le panneau M je pense lire un T un A peut etre plusieurs T dans
> l'image je ne suis pas sure

*Sheet A: no letter at all. Sheet B: an N on panel J; nothing on L; "structures that look like letters" on an
unnamed panel; a T and an A, maybe several Ts, on M.*

**Then the keys.** Sheet A was **841 w00**. Sheet B was **Paris 4 w02**.

| sheet | map | panels | windows read | letters named |
|---|---|---|---|---|
| A = **841 w00** | `w00_canonical_2um_20250807020208.tif`, threshold 104 | A B C D | **0 of 4** | none |
| B = **Paris 4 w02** | `tile256_stride128_layers1_63_hann_fwd.tif`, threshold 227 | J K L M | **2 of 4** | N (J); T, A (M) |

**Prediction 1 — confirmed.** Paris 4 w02 yields at least as many read windows as 841 w00: 2 against 0.

**Prediction 2 — refuted.** No window of 841 w00 was read. This was the prediction that carried the experiment and
it was a prediction *against* the conclusion published earlier the same day. It fails. **PR-14 and PR-15 are not
withdrawn.** They survive a test designed to break them.

**What this settles.** The defect found this afternoon was real: every blind panel from PR-10 to PR-16 was 2 512 px
tall against a letter height of 1 790–1 808 px, i.e. **1.4 letter heights — at most one line of text**, and the
reader was being asked to recognise letters with the line context removed. PR-17's panels are 8 328 px, **4.6 letter
heights**. Enlargement did what it should on a scroll that has text: Paris 4 went from 2 read of 6 to 2 read of 4.
It did nothing on 841: still 0, on four more windows. So **the small window was not what was hiding 841's text**.
That explanation is spent.

**Scoring, by the rule set before the reading.** The unnamed panel — K by elimination, and the inference is written
in the sealed file rather than supplied afterwards — said "structures that look like letters" without naming one.
It is scored **not read**: since PR-10 this protocol counts a reading only when a letter is *named*, because an
impression of shape is exactly what noise produces. Scored the other way, Paris 4 would be 3 of 4 and the direction
would be unchanged.

**The statistics, stated as what they are.** PR-17's own registered comparison, 2 of 4 against 0 of 4, gives
**Fisher one-sided p = 0.21** — four windows a side is too few to conclude from alone, and that is a limitation of
the design as registered, not a finding. Pooling PR-16 and PR-17 gives 4 of 10 against 0 of 18 and **p = 0.010**,
but *that pooling was not registered in advance*. It is reported here as a post-hoc figure indicating a direction,
and it does not have the standing of the registered test. The registered results are: PR-16 p = 0.079, PR-17
p = 0.21, both in the same direction, neither individually conclusive.

**Cumulative count across the blind protocol.** On PHerc. 841 — 8 panels in PR-14 (segA, segB), 6 in PR-15 (w00),
4 in PR-17 (w00) — **18 windows, not one letter named**. On the positive control PHerc. Paris 4 w02 — 6 in PR-16,
4 in PR-17 — **10 windows, 4 read, 5 letters named** (E, T, C, I, N, then N, T, A).

**A defect in PR-16's key, found the same hour and reported here because it could have inverted this result.** The
key file for PR-16 contradicted itself: its header named the Paris 4 map, its six panel lines each said `w00`. Had
the panel lines been right, the letters read on 2026-09-25 morning would have been on 841 and every conclusion of
that day inverted. The header is right, by three independent proofs: (1) `scripts/panneau_pr15.py` wrote the token
`w00` as a **hardcoded literal** in each panel line while building the header from `os.path.basename(SRC)`, so
generalising the script to a second map moved one and not the other; (2) the six windows appear line for line in
`zones_p4w02.txt` and none is in `zones_w00c.txt`; (3) w00's map is 15 827 × 18 868 px and PR-16's panel U extends
to X = 30 136, which cannot exist on it. No published result changes — the scoring already treated those panels as
Paris 4. The script is fixed, the key annotated in place without altering its sealed lines.
**It was found by a subagent asked only to re-count panels, deliberately not told what the count was for.** The
rule that caught it is not "check your keys", which nobody does; it is **have the arithmetic re-derived by someone
with no stake in the answer**, who then reports the contradiction as a matter of course.
Transferable form for `METHOD.md`: *a constant hardcoded into a reporting line does not survive the generalisation
of the script around it.* `scripts/panneau_pr17.py` never had the defect: it writes the key from the same variable
it reads the pixels from, and carries no per-panel token at all.

**Limits of this result, declared.** The reader is not naive — he knows the project, and he had seen twelve
small-scale zones of both sheets before. What he did not know, and could not infer from the images, is **which
sheet was which**; that is the blinding this comparison depends on and it held. The two sheets differ in more than
their scroll: different segment, different model lineage, different threshold. This experiment shows that *the
published maps of 841 w00 do not yield letters to a reader who reads the control maps at the same protocol*. It
does not isolate why.

### PR-17 — addendum, 2026-09-25, two hours after the result above: the positive control on 841 was run by accident, and it failed. **The interpretation published above is withdrawn.**

**What was found.** The label-exclusion test in `scripts/panneau_pr17.py` constrains only the window's **centre**:

```python
hors = ~ndimage.binary_dilation(L > 0, iterations=40)
i, j = (y + HT // 2) // 8, (x + LG // 2) // 8
if not (i < hors.shape[0] and j < hors.shape[1] and hors[i, j]):
    continue                       # centre hors du voisinage des labels
```

A window is 942 × 1041 px at level 3 and the dilation is 40 px. Requiring the centre to be 40 px clear of a label
excludes almost nothing: the rest of the window is free to contain labelled ink. It did.

| sheet | panel | known letter-sized letters inside | their fill at the panel's threshold | panel marked | reader |
|---|---|---|---|---|---|
| 841 w00 | A | **3** (nos. 1, 2, 5) | 72.4 %, 65.8 %, 65.6 % | 17.2 % | nothing |
| 841 w00 | B | 0 | — | 8.4 % | nothing |
| 841 w00 | C | **4** (nos. 8, 10, 11, 14) | 75.6 %, 59.0 %, 72.8 %, 74.3 % | 14.0 % | nothing |
| 841 w00 | D | 0 | — | 4.4 % | nothing |
| Paris 4 w02 | J | 0 | — | 3.5 % | **N** |
| Paris 4 w02 | K | 0 | — | 8.4 % | shapes, no letter named |
| Paris 4 w02 | L | 0 | — | 6.6 % | nothing |
| Paris 4 w02 | M | **2** (nos. 4, 7) | 68.6 %, 78.3 % | 12.3 % | **T, A** |

w00 has exactly seven label components of letter size (900–3 000 px). **Panels A and C between them contained all
seven**, each filled to 59–76 % by the map at the threshold under test. The reader, blind, said *"on ne voit aucune
lettre"* — no letter at all — about the sheet. The same thing had already happened in PR-15, whose panel I
contained letter no. 1 at 72.4 % fill and was likewise read as nothing.

On the control scroll the opposite: the one panel containing known letters is the one where the reader **named two
of them**, and a second panel with **no** labelled ink yielded a named letter outside the labelled zone.

**Inspection of the images confirms it** (`images/841_segments/2026-09-25_CONTROLE_841_lettres_connues.png` and
`..._p4_...`, the same panels with the known letters boxed in red). Inside the boxes on 841 the letters are clumps
of blobs indistinguishable from everything around them. Inside the boxes on Paris 4 they are letters, in rows.

**It is not a coverage difference.** 841's panel C marks 14.0 % of its area, Paris 4's panel M marks 12.3 % — and
841's sparsest panel, D at 4.4 %, is sparser than Paris 4's panel K at 8.4 %, which shows three rows of letter
shapes. The hypothesis "841's map is simply over-marked" is **refuted by its own numbers**. What differs is the
*shape* of what is marked: strokes on one scroll, lumps on the other, at equal fill of the known letters.

**What is withdrawn.** The conclusion recorded above, and in PR-14 and PR-15 before it — *the published maps of 841
carry no second readable passage* — is withdrawn **as an interpretation**. The observation stands: nothing was read.
But the instrument has **no measured sensitivity on 841**. On the only ground where its sensitivity can be checked,
the labelled letters, it renders them illegibly. A null from an instrument with unmeasured — here, demonstrably
zero — sensitivity carries no information about what is or is not present elsewhere on the sheet.

PR-16's comparison survives and is in fact sharpened, but it must be restated. It does **not** show that 841 has
less unlabelled text than Paris 4. It shows that **the published map of 841 w00 does not render letters legibly,
including letters that are labelled**, while the published map of Paris 4 w02 does. That is a statement about the
maps, not about the scrolls' contents.

**What replaces the closed question.** The bottleneck on PHerc. 841 is not where to look, it is that no available
map of it renders a stroke. That is a modelling and data question rather than a reading-protocol question, and
unlike "is there more text out there" it can be attacked directly.

**The process failure, stated plainly.** This check — *can the reader read the letters we already know are there?* —
is the same check whose absence invalidated the shape criterion nine hours earlier, on the same day, and which was
written up then as `METHOD.md`'s lesson *a detector is controlled before it is used*. It was then not applied to the
reading protocol itself. The rule existed, was freshly written, and was not carried across. Worse, the control was
available at zero cost the whole time: the panels already contained the letters. What was missing was not an
experiment, it was the question.

## PR-18 — registration, 2026-09-25, before any measurement: a seventh candidate for legibility, and this one comes from a failure rather than a guess

**Why another one.** Six quantities have been tried as stand-ins for *can a person read this* — separation, fill at
matched noise, object count, median object size, precision at matched recall, per-letter IoU — and a seventh,
line alignment, failed this afternoon. Not one tracks what an eye sees. Every one of them was chosen because it was
easy to compute. This one is chosen because the eye, looking at two figures side by side, said what the difference
was: **strokes against lumps**, at equal fill of the known letters and comparable coverage.

**The quantity.** For each connected component of the thresholded map, let `A` be its area in pixels and `r` the
maximum of the Euclidean distance transform inside it — the radius of the largest disc the component contains.
Define

```
elongation = A / r²
```

It is scale-free. A disc gives π ≈ 3.14 whatever its size. A stroke of width `t` and length `L` gives `4L/t`, i.e.
four times its aspect ratio: 32 for a stroke eight times longer than it is wide. A letter is made of strokes; a
blob is a disc. Per panel, the reported statistic is the **area-weighted median elongation** over components of at
least 200 px, and, as a secondary, the **share of marked area sitting in components with elongation ≥ 12** (aspect
ratio 3 or more).

**The test that matters, and why it is not the obvious one.** The obvious comparison — 841 against Paris 4 — is
worthless on its own: every 841 panel is unread and most Paris 4 panels are read, so any quantity that separates
the two scrolls at all will appear to "track legibility". The test that can fail is **within the control scroll**,
where the reader's verdicts differ across panels of the same sheet, the same map and the same threshold.

**Primary, registered.** On the ten PHerc. Paris 4 w02 panels that have a reader verdict — Q, R, S, T, U, V from
PR-16 and J, K, L, M from PR-17, of which **four were read** (R, V, J, M) and six were not — the area-weighted
median elongation is **higher on the read panels than on the unread ones**. One-sided Mann–Whitney on 4 against 6,
reported with its exact p value whatever it is.

**Secondary, registered.** Across sheets: the four 841 w00 panels have **lower** elongation than the ten Paris 4
panels. This is expected from the figures and is therefore not evidence of anything by itself; it is recorded so
that a failure of it would be visible.

**Third, and the one with teeth.** Restricted to the **known labelled letters only** — 7 on 841 w00, 16 on Paris 4
w02, each measured inside its own bounding box at its own sheet's threshold — 841's letters have lower elongation
than Paris 4's. This compares ink against ink, with no dependence on the reader, on panel choice or on where the
windows fell. If it fails, the eye's account of the two figures is wrong and this quantity should be abandoned like
the other six.

**Declared in advance, because it is the obvious objection.** This quantity was chosen *after* seeing the two
figures. It is therefore not independent of them, and the third test above is close to a restatement of what was
seen. That is exactly why the primary is the within-scroll one, which the figures say nothing about. **If the
primary fails, the quantity is recorded as a seventh failure and not rescued by the other two.**

**What a success would be worth, stated before knowing.** Not a reading. A number that tracks legibility can be
optimised, and every training decision on this project so far has been steered by separation or IoU — quantities
now known not to track it. That is the whole value of it, and it is enough.

### PR-18 — result, 2026-09-25: the primary fails. Elongation is the seventh quantity that does not predict legibility — and the third test gives the first number for what does differ.

| test | registered prediction | result |
|---|---|---|
| **primary** — within Paris 4 w02, 4 read panels vs 6 unread | read > unread | **U = 17.0, p = 0.176 — fails** |
| secondary — 841 w00's 4 panels vs Paris 4's 10 | 841 lower | U = 2.0, p = 0.0040 |
| third — known labelled letters, ink against ink | 841 lower | U = 12.0, **p = 0.0010** |

**The primary fails and the registration said what to do about it:** *"If the primary fails, the quantity is
recorded as a seventh failure and not rescued by the other two."* It is so recorded. **Elongation does not predict
which panel a reader reads.** The clearest counter-example is panel K of Paris 4 — unread, and the second highest
elongation of all ten at 28.3, above three of the four read panels.

Per-panel values, area-weighted median elongation:

| sheet | panel | read? | elongation | share of marked area with elongation ≥ 12 | components |
|---|---|---|---|---|---|
| Paris 4 w02 | M | **read** | 32.97 | 82.5 % | 171 |
| Paris 4 w02 | K | no | 28.27 | 82.2 % | 140 |
| Paris 4 w02 | V | **read** | 25.86 | 95.6 % | 23 |
| Paris 4 w02 | R | **read** | 24.78 | 83.8 % | 25 |
| Paris 4 w02 | T | no | 24.73 | 62.9 % | 32 |
| Paris 4 w02 | U | no | 23.75 | 81.2 % | 47 |
| Paris 4 w02 | L | no | 19.52 | 70.4 % | 127 |
| Paris 4 w02 | Q | no | 17.94 | 79.3 % | 35 |
| Paris 4 w02 | J | **read** | 17.83 | 51.0 % | 103 |
| Paris 4 w02 | S | no | 13.17 | 69.7 % | 11 |
| 841 w00 | A | no | 14.23 | 60.1 % | 269 |
| 841 w00 | C | no | 13.28 | 53.8 % | 255 |
| 841 w00 | B | no | 7.93 | 19.3 % | 286 |
| 841 w00 | D | no | 7.03 | 12.8 % | 158 |

**What the third test gives, and it is the first number the day's finding has had.** Measured on the labelled
letters alone — 7 on 841 w00, 16 on Paris 4 w02, each inside its own bounding box, each at its own sheet's
threshold, each threshold already matched to ~70 % fill of those same letters:

- **841 w00: median elongation 18.3** (range 9.8–28.6) — components roughly **4.6 times longer than wide**
- **Paris 4 w02: median elongation 50.7** (range 16.0–96.1) — roughly **12.7 times longer than wide**

A perfect disc scores 3.14. The published map of 841 renders its known ink as near-round chunks; the published map
of Paris 4 renders the same kind of thing as strokes. Factor 2.8, U = 12.0, p = 0.0010, with no dependence on the
reader, on which windows were drawn, or on which panels were shown.

**The two outcomes are consistent and they say different things.** Elongation measures *how well ink is rendered*,
not *whether a window is legible*. A window is legible when it contains text **and** that text is rendered as
strokes; elongation sees only the second term. Panel J of Paris 4 has the lowest elongation of the four read panels
(17.83) and was read — it contains one clear letter in a sparse field. Panel K has the second highest and was not
read, though the figure shows three rows of letter-like forms in it: the reader named no letter, which by this
protocol is not a reading.

**What this is worth, measured against what was claimed for it in advance.** The registration said a working
quantity would be worth having because every training decision on this project has been steered by separation or
IoU, which do not track legibility. Elongation does not track legibility either, so it cannot serve that purpose.
What it can do is narrower and still useful: it turns *"841's map gives lumps where Paris 4's gives strokes"* from
an impression into a reader-independent measurement with a p value, and it gives a target that can be optimised —
render ink at elongation 50 rather than 18 — without claiming that hitting the target would make the sheet
readable.

**Method note.** Computed at half resolution (`::2`); strokes here are over 100 px wide at full resolution, so
nothing is broken by it, and elongation is scale-free in any case. Minimum component area 200 px full-resolution.
`scripts/allongement.py`; raw values in `allongement.json`.

### PR-18 — exploratory follow-up, 2026-09-25, declared exploratory before it was run: the degradation of 841's map is not recoverable by post-processing

Two questions, neither registered as a test, both stated here as exploration rather than as evidence.

**1. Stroke width, the concrete version of the elongation number.** Twice the mean Euclidean distance transform over
marked pixels, inside the known letters, at the same matched 70 % fill:

| sheet | stroke width | as a share of a letter | letter height |
|---|---|---|---|
| PHerc. Paris 4 w02 | **56.4 px** | 3.2 % | 1 790 px |
| PHerc. 841 w00 | **96.5 px** | 5.3 % | 1 808 px |

841's marks are **1.7 times thicker relative to the letter** than the control's. Combined with PR-18's elongation
figures, the marks on 841 are both thicker and shorter: they are blobs, and now with a size.

**2. Is it blur?** Blurring the control map and re-calibrating the threshold to 70 % fill at every step:

| Gaussian σ (full-res px) | 0 | 2 | 4 | 8 | 16 | 32 | 48 | 64 |
|---|---|---|---|---|---|---|---|---|
| elongation of known letters | 43.6 | 33.2 | 25.5 | 23.9 | 23.6 | 23.5 | 19.6 | 18.7 |

Elongation falls steeply to about 25 and then **sits on a plateau across σ = 8–32**, reaching 841's 18.3 only at
**σ ≈ 64 px** — a blur whose standard deviation is larger than the control's entire stroke width, and comparable to
841's. So the gap is not a mild loss of resolution; the control map has to be destroyed at the scale of a whole
stroke before it looks like 841's. Caveat: blurring then re-thresholding is indistinguishable here from simple
over-thick marking, and this test does not separate the two.

**3. Can it be undone? No.** Unsharp masking of 841's map — `out = in + force × (in − gaussian(in, σ))` — swept over
σ ∈ {2, 4, 8, 16} and force ∈ {0.5, 1, 2, 4}, sixteen settings, threshold re-calibrated to 70 % fill at every one:

- elongation stays between **17.0 and 20.9**, against a baseline of 18.29 and a target of 43.6. Best gain **+14 %**
  where **+140 %** is needed.
- stroke width does respond, falling from 96.5 px to 72.9 px at the strongest setting.

**The marks thin without lengthening.** Sharpening a blob gives a smaller blob, not a stroke. There are no strokes
in this map to be recovered, so no post-processing of the published prediction will make 841 legible. Whatever is
to be fixed is upstream of the map — in the model, or in the segmentation and flattening that feed it — and not in
the rendering.

**A caveat on the absolute numbers, found while running this.** PR-18's third test used each sheet's fixed
published threshold; this follow-up re-derives the threshold as the quantile giving exactly 70 % fill. For 841 the
two agree exactly (18.29 both ways, threshold 104 both ways). For Paris 4 the threshold moves from 227 to 226.0 and
the median elongation moves from **50.7 to 43.6** — a 14 % swing from one grey level, because that map's thin
strokes sit close to the threshold. **The absolute elongation of the control is threshold-sensitive; the comparison
is not**, since 841 is at 18.3 under either convention and the gap remains a factor of 2.4–2.8. Reported because a
number that moves 14 % under a convention change should not be quoted as if it were stable.

## PR-19 — registration, 2026-09-25, before the measurement: is the blobbiness in 841's data or in the model that mapped it?

**Where this comes from.** PR-18 established that the published map of PHerc. 841 w00 renders its own known letters
at elongation 18.3 against the control map's 43.6–50.7, with marks 1.7× thicker relative to the letter, and that no
post-processing recovers it. The repair is therefore upstream. Upstream splits in two, and the two call for
completely different work:

- **the model** — 841's ink signal is there and stroke-shaped, and the network smears it; or
- **the data** — 841's letters, on the segmented and flattened surface available, are not stroke-shaped at all,
  and no model can render what is not in its input.

**The measurement that separates them, and it costs nothing.** The *human labels* are people tracing letters by
hand. They are the shape of the letters as a human sees them in the volume, independent of any model. Measure their
elongation exactly as PR-18 measured the maps': per labelled letter, area-weighted median of `A / r²`, same minimum
component area, same half-resolution grid, at the labels' own full resolution rather than level 3.

**Prediction, registered.** **841's human labels have an elongation comparable to Paris 4's human labels** — both
are tracings of Greek letters, so both should be stroke-like and well above 30 — **while only the maps differ.**
If that holds, the loss happens in the model and the data still carries the letters.

**The outcome that would refute it, and what it would mean.** If 841's *labels* are themselves near 18 while Paris
4's are near 50, then at this resolution and on this flattened surface 841's letters genuinely are blob-shaped, the
published map is faithful to its input, and the project's target is unreachable by any modelling work on the
existing segmentation. That is the more consequential answer of the two, and it is the reason to measure before
spending a week training.

**Declared in advance.** The label sets were made by different people with different conventions and possibly
different brush widths; a difference in elongation could be a difference in annotation style rather than in the
letters. Stroke width is therefore reported alongside, and a large gap in stroke width with no gap in elongation
would point at the brush and not at the scroll. This confound cannot be removed with the data at hand and is stated
rather than hidden.

### PR-19 — result, 2026-09-25: the prediction holds. Both scrolls' letters are equally stroke-like in the ground truth; the whole gap is created by the mapping.

Human labels measured exactly as PR-18 measured the maps, at the labels' own full resolution, same half-resolution
grid, same minimum component area:

| | **human labels** | **published map** | map ÷ labels |
|---|---|---|---|
| **841 w00** — elongation | **22.02** (n = 7) | 18.29 | **0.83** |
| **Paris 4 w02** — elongation | **23.04** (n = 16) | 43.63 | **1.89** |
| 841 w00 — stroke width | 149.6 px (8.3 % of a letter) | 96.5 px | 0.65 |
| Paris 4 w02 — stroke width | 132.3 px (7.4 % of a letter) | 56.4 px | 0.43 |

**The registered prediction is confirmed.** The two label sets are 4 % apart in elongation — 22.0 against 23.0 —
while the two maps are a factor 2.4 apart. The people who traced 841's seven letters traced strokes, exactly as the
people who traced Paris 4's sixteen did. **The letters are in the data on both scrolls.**

**The refuting outcome did not occur**, and it was the consequential one: 841's labels are not near 18. So it is
*not* the case that 841's letters are blob-shaped on this flattened surface. The published map is not faithful to
its input; it loses shape its own input carries.

**The sharpest form of the result is the last column.** On the control scroll the map is **1.89 times more
elongated than the human tracing of the same letters** — the model renders thinner, more stroke-like marks than the
generous hand-drawn outline, i.e. it finds the ink inside the annotation. On 841 the map is **0.83**, less elongated
than the tracing: the model returns something rounder than the coarse human outline it was given.

**What this does to the project's direction.** The target is not out of reach on the available segmentation. What is
missing is a model that does on 841 what the control's model does on Paris 4. And for the first time there is a
quantity to aim at that is neither separation nor IoU — the two that have steered every training decision here and
that are now known not to track legibility:

> **raise 841's map elongation from 18 past its own labels' 22, then toward 40.**

It is not claimed that hitting this makes the sheet readable. It is claimed that it is measurable, that it is not
satisfied today, and that it is satisfied on a scroll where the same reader does read.

**Two caveats, one declared in advance and one found while measuring.**
1. The declared one: different annotators, possibly different brushes. 841's label strokes are 13 % thicker
   (149.6 px against 132.3 px). But elongation differs by 4 %, so the brush does not account for the result.
2. The found one: the map is thresholded to 70 % fill of the labelled pixels, which necessarily yields a thinner
   mask than the label itself. Part of "the map is more elongated than its labels" is that shrinkage, not model
   skill. Both sheets get the identical treatment, so the comparison between them is unaffected — but the ratio
   1.89 should not be read as "the model sharpens by 89 %".
3. n = 7 on 841. Seven letters is a small sample and the median of seven is a fragile statistic.

### PR-19 — survey, 2026-09-25, exploratory: every published map of 841 w00 renders below its own labels, including ours, and the one used for the blind search was already the best of them

**Why this had to be checked.** The map searched blind in PR-15 and PR-17, `w00_canonical_2um_20250807020208.tif`,
was chosen on 2026-09-25 morning for its **sensitivity** — it recovers 7 of the 7 known letters at 69.9 % fill —
and never for how it renders them. PR-18 has just shown that sensitivity says nothing about shape. If another
published map of the same sheet rendered strokes, the blind search was run on the wrong map and its null would
apply only to that one.

All maps of w00 on disk, measured on the **same seven known letters**, each at its own threshold calibrated to the
same 70 % fill, half-resolution grid, minimum component 200 px full-resolution:

| map | origin | threshold | elongation | stroke width |
|---|---|---|---|---|
| **human labels** | hand-traced | — | **22.02** | 149.6 px |
| `w00_canonical_2um_20250807020208.tif` | published | 104 | **18.29** | 96.5 px |
| `ps48_640_640_smooth_0.1_w00_ckpt_130000_forward_210326.tif` | published | 170 | 17.86 | 121.5 px |
| `w00_full_human4_ckpt016000.tif` | **ours** (run 4, 2026-09-22) | 165 | 17.65 | 94.2 px |
| `new_canon_20260417_recale.tif` | published | 201 | 17.62 | 133.2 px |
| `w00_full_human3_ckpt016000.tif` | **ours** (run 4, 2026-09-22) | 167 | 15.85 | 91.7 px |
| `w00_canonical_030726_reverse_070326.tif` | published | 103 | 15.80 | 124.1 px |
| *for comparison* — Paris 4 w02 labels | hand-traced | — | 23.04 | 132.3 px |
| *for comparison* — Paris 4 w02 map | published | 226 | **43.63** | 56.4 px |

**Three things fall out, and none of them was visible from any number the project had before today.**

**1. The map used for the blind search was already the best of the six.** Its 18.29 is the top of a range running
from 15.80 to 18.29. So PR-15's and PR-17's null is **not** an artifact of map choice, and choosing differently
would have made the rendering worse. The negative stands on that count.

**2. Every single map of 841 falls below the sheet's own labels (22.02), while the control's map reaches nearly
double its labels (43.63 against 23.04).** The gap is not that 841's models are somewhat weaker. They are on the
wrong side of their own ground truth: they return something rounder than the coarse hand tracing they were given,
where the control's model returns something finer than its tracing.

**3. Our own fine-tuning improved IoU and did not improve the rendering.** `w00_full_human3` and `w00_full_human4`
are this project's run-4 checkpoints, recorded at the time as gaining roughly +0.03 to +0.05 IoU over their
teacher. They score **15.85 and 17.65**, below the published `canonical_2um` at 18.29. Two days of training,
steered by IoU, moved the quantity being optimised and left legibility where it was — or slightly worse. This is
the day's lesson demonstrated on our own runs rather than argued: **IoU and stroke rendering are not the same
direction**, and until today the project had no way to see that.

**One map could not be measured and it is the one lead this survey leaves.** `w00v24/preds/new_canon_natif.tif` is
a different segmentation of the same sheet, on a grid of 16 460 × 18 560 against the labels' 15 872 × 18 944. It
cannot be compared against these labels without warping them, so it is untested. If the difference between 841 and
the control lies in the flattening rather than in the network, a different segmentation of the same sheet is where
it would show — and that is the cheapest remaining thing to check.

### PR-19 — the decisive paired comparison, 2026-09-25: our own recipe has never produced strokes, anywhere

**The question this answers.** Every measurement so far compared *scroll against scroll* using maps made by other
people. That cannot separate "841 is harder" from "our recipe is behind". The separation needs our own model
measured against a better map **on the same scroll, on the same letters** — and the obvious place is PHerc. Paris 4
w02, where this project's run-2 checkpoint (`ink_w00_128_acc4`, ckpt 80 000) demonstrably reads: on 2026-09-20 it
rendered the line ΤΗΟΚΑΤ outside the labelled area, correlation 0.79–0.84 with the published prediction. That is
the best thing this project has produced.

Our block covers y 26 000–30 500, x 19 500–31 000, which contains exactly two known letters entirely — components
12 and 13. Both maps thresholded to 70 % fill on those same two letters:

| map | threshold | elongation | stroke width |
|---|---|---|---|
| published `tile256_stride128_layers1_63_hann_fwd.tif` | 229 | **114.74** | **34.4 px** |
| **ours**, run 2 `ink_w00_128_acc4` ckpt 80 000 | 206 | **28.89** | **97.8 px** |
| *for reference* — the hand-drawn labels of this sheet | — | 23.04 | 132.3 px |

Per letter: letter 12 — 124.05 against 32.00; letter 13 — 105.43 against 25.78. The direction is the same on both.

**A factor of 4 in elongation and 2.8 in stroke width, on the scroll where our model reads.** Our map sits at
28.89, barely above the hand tracing's 23.04 and in the same region as every map of 841 (15.8–18.3). The published
map sits at 114.74, five times thinner than the tracing it was learned from.

**What this settles.** The gap is not "841 is a hard scroll and Paris 4 is an easy one". **This project's training
recipe has never produced stroke-shaped output anywhere, including where it succeeds.** The community's recipe
does, by a factor of four, on the identical letters. That also explains the run-4 result recorded above — the
fine-tunes gained IoU and lost elongation — without needing any hypothesis about 841: a recipe that paints regions
gains region-overlap and cannot gain shape.

**Verified blind.** Re-derived by a subagent told only what to compute, which wrote its own code from scratch and
then re-implemented steps 4–5 a second time by a different route (`np.kron` instead of repeated `np.repeat`,
explicit per-label loops, no `bincount`). Every figure reproduced exactly: 114.73684 / 34.3533 and 28.89269 /
97.7794.

**A caveat the blind check found, and it works against the conclusion.** The images are uint8, so the 30th-percentile
threshold lands on an integer shared by many pixels. The realised fill is **71.6 %** for the published map and
**70.0 %** for ours. A higher fill thickens and rounds what is measured, so the published map is scored at a mild
disadvantage and still wins fourfold. Reported because a tie effect that had gone the other way would have needed
the result withdrawn.

**n = 2.** Two letters is a very small sample and the median of two values is the mean of two values. What carries
the result is the size of the effect and the fact that it is paired — same letters, same labels, same threshold
rule, same rendering code — not the number of letters.

**Consequence for the plan, stated here because it reverses the project's direction.** Training further on PHerc.
841 is the wrong next move: there is no reference map on 841 against which progress could be measured. On Paris 4
w02 there is one, four times better than ours, on data already downloaded, and elongation on known letters is
computed in seconds with no blind reader involved. **The development loop moves to the control scroll**, and the
recipe that closes the gap there is what will then be applied to 841.

## PR-20 — registration, 2026-09-25, before the run starts: does the thickness of the label set the thickness of the prediction?

**The measured situation.** On PHerc. Paris 4 w00, the human labels this project trained on have a thickness of
**132.4 px**. Run 2, trained on them, predicts at **97.8 px** on the unseen sheet w02. The published reference map
predicts at **34.4 px** on the same two letters, with **four times** the elongation. (Unit note, corrected while
building this experiment: the quantity reported throughout is `2 × mean(distance transform)`, which for a stroke of
width *t* equals *t*/2, not *t*. All figures in this document use it consistently; only the physical interpretation
of the absolute value changes.)

**Hypothesis.** A region-overlap loss (Dice + BCE) computed against a label that is four times thicker than the ink
is **maximised by painting the blob**. The network reproduces the thickness it is given, and that is why this
project's output has never been stroke-shaped anywhere — including on the sheet where it reads.

**The manipulation, and it is the only one.** The same volume, the same letters, the same architecture, the same
patch size, the same 80 000 iterations, the same learning rate, the same seed, the same grad-accumulation. Only the
label changes: each labelled component is **skeletonised and re-dilated to a thickness of 34**, matching the
reference map, and clipped so it can never extend beyond the original annotation. Achieved: 125 → **36**, 35.5 % of
the labelled pixels kept, 24 of 24 components surviving. Config `ink_w00_fin.json` differs from `ink_w00_128_acc4.json`
in exactly two keys, `out_dir` and the dataset path.

**Patch composition, checked before launching as this project's own rule requires.** Run 2: 8 098 patches, 63.2 %
ink / 34.9 % sure background / 2.4 % ignored. This run: 5 113 patches, 33.2 % / 66.8 % / 0.0 %. Neither is
degenerate — the failure mode that destroyed `teacher1` (0 % background in the patches) does not recur.

**PRIMARY, registered.** On **w02**, a sheet this model never trains on, letters 12 and 13, threshold calibrated to
70 % fill exactly as everywhere in PR-18 and PR-19: the new checkpoint's **elongation is higher than run 2's
28.89**. Ceiling for reference: the published map scores 114.74 on those same two letters.

**GUARD, co-primary and registered.** The ink/non-ink separation on the same crop **must not fall below run 2's**.
A model can win elongation by drawing a thin line in the wrong place; without this guard the primary is gameable
and would be passed by a model that has stopped finding ink at all. If the guard fails, the run is recorded as a
failure whatever the elongation does.

**Secondary.** Predicted stroke thickness falls from 97.8 toward 34.

**What each outcome means, written before the result.**
- *Elongation rises and the guard holds:* label thickness is the lever. The same thinning is then applied to 841's
  labels and the recipe carried over — which is the point of the whole experiment.
- *Elongation does not move:* label thickness is **not** the lever, the gap is architectural (the reference is a
  2.5D ResNet-152 at tile 256; ours is a 3D U-Net at patch 128), and no further loss tinkering is warranted. That
  would be an expensive negative but a clean one, and it redirects the work to reproducing the community
  architecture instead.
- *Elongation rises and the guard fails:* the model has thinned by losing the ink. Recorded as a failure.

**Declared in advance.**
1. The patch pool shrinks from 8 098 to 5 113. This is a consequence of thinning under a fixed
   `patch_min_labeled_coverage` of 0.05, not an independent change; it is not corrected for, because correcting it
   would introduce a second variable. The run sees the same number of patches, drawn from a smaller pool.
2. Measuring *thickness* on a model trained to produce a given thickness would be circular. That is why the primary
   is **elongation**, a shape quantity, measured on a **sheet that is not in the training set**.
3. n = 2 letters, the only two known letters of w02 that fall entirely inside the evaluation crop. The median of
   two values is their mean. What carries the comparison is that it is paired and that the baseline and the ceiling
   were measured with the identical code.
4. This tests a mechanism on the **control scroll**, not on 841. Nothing here claims anything about 841 until the
   recipe is carried over and measured there.
