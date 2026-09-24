# Measurements

Everything here has been posted publicly in
[ScrollPrize/villa#1867](https://github.com/ScrollPrize/villa/issues/1867). Model, metric and windows are described in
the README. Segment names are abbreviated: `ag174` = `auto_grown_20260220174252405`, `ag144` =
`auto_grown_20260220144552896`. Both are published surface volumes, 2.403 µm, 109 planes.

## 1. Depth direction — `scripts/mesure_sens.py`

Separation / correlation, per window and in the mean.

| segment | window | layers as published | layers reversed |
|---|---|---|---|
| ag174 | 1 | 43.0 / 0.280 | 44.2 / 0.573 |
| ag174 | 2 | 31.3 / 0.427 | **106.2 / 0.853** |
| ag174 | 3 | 7.6 / −0.014 | 77.1 / 0.704 |
| ag174 | **mean** | **27.3 / 0.231** | **75.9 / 0.710** |
| ag144 | 1 | 61.6 / 0.522 | **131.8 / 0.852** |
| ag144 | 2 | 67.6 / 0.568 | 102.3 / 0.795 |
| ag144 | 3 | **−9.2 / −0.055** | 34.8 / 0.581 |
| ag144 | **mean** | **40.0 / 0.345** | **89.7 / 0.743** |

Reference: the same model on w00, its own training surface, three held-out windows — 66.6 / 78.4 / 90.2.

The ag144 window 3 row is the one worth looking at: in the published order the model is confidently **anti**-correlated
with the truth, and nothing in the output image looks wrong.

**Read this as** the cost of running a render-trained model on a differently ordered array — not as a claim that these
segments are published upside down. See the correction in the README.

## 2. Which 65 of the 109 planes — `scripts/mesure_zc.py`

Same model, same window (ag174 window 2, reversed), only the slice centre changing.

| centre plane | 32 | 37 | 44 | **50** | 54 | 58 | 66 | 78 | full |
|---|---|---|---|---|---|---|---|---|---|
| separation | 70.1 | 83.9 | 99.1 | **107.0** | 106.2 | 101.8 | 84.7 | 54.7 | 84.6 |

Single-peaked; `full` means all 109 planes interpolated down to 65. The worst correct-direction slice (54.7) is close to the best wrong-direction one.

Every number in the two tables above is re-derived from `results/*.json` by `verify_claims.py`, which exits non-zero if any of them drifts. The JSON is written by the measurement scripts themselves (`JSON=<path> python mesure_sens.py ...`), not transcribed by hand.

**Read this as** the same cross-array cost as §1, traced as a curve — not as a general statement about slice choice.
For a model that stays on its own array, the centred window is safe (measured by @AndreasHad04: no window beats
villa's centred one by more than 0.0138).

## 3. Filenames, before any inference

All three PHerc0841 segments carry the same three prediction files in the label bucket, with the same naming:

```
<segment>_canonical_030726_reverse_070326.tif
<segment>_canonical_2um_20250807020208.tif
ps48_640_640_smooth_0.1_<segment>_ckpt_130000_forward_210326.tif
```

The word `reverse` is attached to the render campaign, identically for w00, ag144 and ag174, and the three `meta.json`
give the same `volume` and a `uuid` of the form `<segment>_transformed`. The direction is a property of the array, and
it is readable in the filenames.

## 4. The same segment on two arrays, in opposite directions — `scripts/prep_seau.py`, `scripts/mesure_seau.py`

The test registered as PR-1. Same model, same segment (`ag174`), scored against the labels belonging to each array.

| window | stored order | reversed |
|---|---|---|
| 1 | 27.5 | 35.5 |
| 2 | 86.4 | 25.2 |
| mean | **56.9** | 30.3 |

On the **label-bucket render** (65 planes, 4.681 µm — the array family our model was trained on) it prefers the
**stored** order. On the **published surface volume** of the same segment (109 planes, 2.403 µm, §1 above) the same
model prefers the **reversed** order, 75.9 against 27.3. Same segment, opposite answers: the direction belongs to the
array.

**The weakness, stated rather than buried.** Only two windows, and they disagree: window 1 slightly prefers reversed
(35.5 against 27.5), window 2 strongly prefers stored (86.4 against 25.2), and the mean is carried by window 2. This
is thinner than the three-window result of §1. @AndreasHad04's ablation — three segments, three array families, both
directions, a label-free direction rule — is the stronger evidence for the same conclusion, and ours agrees with it in
the mean. Treat this as a check, not as the demonstration.

## 5. A negative control on the human reader — `scripts/leurres.py`, `scripts/score_aveugle.py`

The reader had just scored 12 candidate stacks: 7 *certain ink*, 5 *don't know*, **0** *no ink*. He said so himself —
"I feel like I find ink almost every time, is that normal?" A batch made only of candidates cannot answer that. It
cannot separate an eye that detects ink from a rendering in which everything eventually looks like ink.

So the next batch was mixed and blind. Twelve stacks: **6 real candidates** from the census and **6 decoys** drawn
from places where neither reader responds at all, shuffled, with neither the number nor the proportion disclosed. A
decoy had to be at least 900 px from any candidate and have its central 320 px below both readers' medians. The index
image showed **only the scan** — the readers' panels would have given the decoys away. The key was written to a
separate directory and `score_aveugle.py`, which is the only thing that opens it, was **written before the answers
existed**, including its reading of the outcome in both directions.

| | certain ink | don't know | no ink |
|---|---|---|---|
| real candidates (6) | **5** | 1 | 0 |
| decoys (6) | **0** | 1 | 5 |

Fisher exact test, one-sided, on the *certain ink* rate: **p = 0.008**. No false positive: not one *certain ink* on a
decoy. No miss: not one *no ink* on a candidate. The two *don't know* fell one on each side.

**What this licenses.** The reader's verdicts carry information at this rendering, so his 7 *certain ink* from the
previous batch cannot be dismissed as an artefact of the rendering. **What it does not license.** That any of those
blobs is a letter — that is a different question, and it belongs to the transcription, not to a detection test. And
the control is about *this* rendering: a different depth, contrast or magnification would need its own.

**What we would have concluded had it failed**, written down before it ran: that the rendering does not allow a
decision, that the previous batch's verdicts support nothing, and that the fix is to change the rendering rather than
to press the reader.
