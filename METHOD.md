# Method rules

Rules this project works by. Each one exists because ignoring it cost us a measurement.

## 1. A control that cannot be executed is a failed control

Before trusting an instrument, it must be shown to light up where something is known to be (positive control) and to
go quiet where nothing is (negative control). If the positive control cannot be constructed at all, the instrument is
rejected — not used with a caveat.

**And the control comes before the conclusion, not after it.** On 2026-09-25 two full sheets were searched for
letters and the finding — *"almost no letter-shaped structure outside the labelled zone"* — was written down before
anyone checked that the criterion fires where letters are **known** to be. It was missing one known letter in five,
and at the threshold where it misses none the same search returns three times as many candidates. An absence found
by an instrument whose sensitivity has not been measured is a property of the instrument. The check cost one loop
over six thresholds.

Two instruments were built and thrown away this way:

- A per-layer grey-level profile meant to detect ink depth. Its negative control — the same measurement with the label
  mask displaced by a few hundred pixels — came out just as strong (24.1 / 28.6 against 14.9 / 11.0). It was measuring
  sheet geometry, not ink.
- A line-periodicity test meant to confirm that blobs fall on text lines. No positive control could be built: there
  was no region where the answer was independently known at the right scale. Rejected, kept in the repository with the
  reason written inside it.

## 2. Two runs may only be compared if they share the referee

When a model is scored against another model's prediction, both compared runs must be scored by the *same* referee,
and the referee's identity is checked before the comparison, not assumed. A teacher silently changing between two
runs invalidates the comparison even when every other setting matches.

## 3. Three values, never a transcription

Human judgements are collected as exactly one of **"ink for sure" / "no ink" / "I don't know"**, on one designated
spot at a time. Never "read this line". "I don't know" is a valid and informative answer.

Measured on one calibration set, the human reader here was ~93 % precise and ~58 % complete. That shape of eye can
*confirm* a candidate and cannot *reject* one, so rejections are never inferred from a human "no".

## 4. When the reader hesitates, fix the image

A hesitation is information about the rendering, not about the reader. First failure of this kind: a triage plate
built with 900-pixel windows for a scroll whose letters are ~1000 pixels across — everything looked shapeless *by
construction*. Re-rendered at 4000 pixels, three of the candidates turned out to be letter sequences.

## 5. Claims are separated from what supports them

Every result statement is written in two halves: what is asserted, and what is explicitly *not* asserted. Example, on
finding legible letters outside the label mask: asserted — Greek letters legible outside the mask, seen by two
independent readers, with the same signal strength as the certain letters; not asserted — that they are new, since
they also appear in the organisers' published prediction, and "unlabelled" is not "never read".

## 6. Corrections are published where the claim was made

A wrong public statement is corrected in the thread where people engaged with it, naming the wrong sentence as it was
written. Deleting is acceptable only where nobody has replied; where someone has, the reply must not be left dangling.

## 7. The zone that holds the answer is not a sample

Anything measured only where the labels are is measured where the teacher is strongest and where the thresholds were
tuned. It does not count until it is repeated, **paired**, on windows held out from every choice.

This is not a hypothetical. On 2026-09-24 an evening of measurement in the control zone produced a precision ranking
with a 12-point lead, a mechanism to explain it, and a costless read-out to exploit it. Repeated on six held-out
windows, paired: the 12-point lead became **+1.1 points, t = 0.55**. Precision varies from 53 % to 96 % from window
to window, which swamps every effect that had been claimed. All three findings were withdrawn the same night.

## 8. A blind panel is inspected as an image before anyone is shown it

Four blinding defects in two days, and the scripts were correct every time — they randomised, they matched the fill,
they drew what they were asked to draw:

- a randomisation that fell the same way on four rows out of four (one chance in eight; fixed with block randomisation);
- a frame that cut the third letter, so a reader answered about the cropping;
- a panel that included the **ground truth**, rendered identically to the maps under test and placed first, which
  told the reader which three letters to look for and exactly where — the same defect as drawing a contour, except
  it supplies the answer as well as the location;
- a random control that overlapped its own candidate zone by 72.5 %, so the protocol compared a zone with itself.

Not one was findable by re-reading the code. All four were found by opening the PNG. **Rendering a panel and reading
its caption is part of the experiment, not a formality after it.** The caption is included: it has twice announced
the wrong number of panels, and it once stated how many letters were in the frame — which answers half of the
question the reader is being asked.
