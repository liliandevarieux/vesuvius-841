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

**Cost, stated in advance so it cannot be quietly abandoned.** The inspected zone of w00's 2.403 µm volume has to be
fetched (of the order of 20 GB, as for the other two segments) and one training run repeated.
