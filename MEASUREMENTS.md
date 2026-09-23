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

| centre plane | 32 | **50** | 54 | 66 | 78 | all 109 → 65 |
|---|---|---|---|---|---|---|
| separation | 70.1 | **107.0** | 106.2 | 84.7 | 54.7 | 83.9 |

Single-peaked. The worst correct-direction slice (54.7) is close to the best wrong-direction one.

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
