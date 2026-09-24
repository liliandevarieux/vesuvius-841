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
