# Reader instructions, word for word

From PR-46 on, the blind readers in this registry are AI agents: fresh Claude subagents, each given one image and the
instructions below, and nothing else. The one exception is PR-47: its first three readers of Reader v2's window were
also sent one neutral message to continue. Earlier entries used human readers, mostly Lilian, for example:
- PR-10's reading was not blind;
- PR-17's reader was blind to the key but not naive;
- PR-24 used Lilian and an AI reader, whose instructions are not in this file.

One unregistered test on 24 September used a reader with no connection to the project.

This file gives the instructions of the AI readers from PR-46 on, word for word. They were extracted on 28 September
2026 from the session log in which the readers were launched. Only the image path is replaced by `<image>`.

It was published on 28 September in the evening, after a re-check found that no public file gave the sheet format's
instructions. The window format's first version was already public as `results/pr47_consigne.txt`.

## Which version each test used

| version | tests |
|---|---|
| Reference readers, tracings | PR-46; PR-48's reference readers 2 and 3 |
| Sheet, version 1 | PR-46; the two diagnostic readers of PR-46's sheet cited in PR-51; PR-48's dry runs (for half and quarter sheets, the same text with the crop count changed) |
| Sheet, version 2a: the first-impression sentence inside the instructions | PR-51, PR-52, and the diagnostic readers of PR-48's dry-run sheet |
| Sheet, version 2b: the same sentence moved to the very end | PR-53, PR-54 |
| Window, version 1 | PR-47 |
| Window, version 2: the first-impression sentence at the end | PR-55, PR-49 |

Versions 2a and 2b differ only in where that sentence sits. PR-53 and PR-54 did not disclose the move; see the
correction of 28 September at the end of `PREREGISTRATIONS.md`.

## Reference readers, tracings

```
You are taking part in a letter-recognition test. Open exactly one file with the Read tool:
<image>
Do not open, list or search any other file or folder, and use no other tool.

The image is a sheet of 28 numbered crops. Each crop is a white-on-black tracing of one handwritten letter from an ancient Greek manuscript, centred in the crop.

The script is Greek capital letters as written on papyrus: sigma looks like C, epsilon like a rounded Є (a C with a middle bar), omega often like ω, mu may be rounded like μ, and letters can be slanted.

For each crop, 1 to 28, give your single best guess using the Greek letter name (alpha, beta, gamma, delta, epsilon, zeta, eta, theta, iota, kappa, lambda, mu, nu, xi, omicron, pi, rho, sigma, tau, upsilon, phi, chi, psi, omega), or "unreadable" if you cannot make a reasonable guess, plus a confidence: 1 = guess, 2 = probable, 3 = sure. Judge each crop on its own.

Reply with exactly 28 lines in the form `N: name (confidence)` and nothing else.
```

## Sheet, version 1

```
You are taking part in a letter-recognition test. Open exactly one file with the Read tool:
<image>
Do not open, list or search any other file or folder, and use no other tool.

The image is a sheet of 28 numbered grayscale crops. Each crop comes from an image of a damaged ancient Greek manuscript and is centred on one handwritten letter. Bright means ink, dark means no ink. The images are noisy: strokes may be broken, blurred or partial, there may be stray bright spots, and parts of neighbouring letters may appear at the edges.

The script is Greek capital letters as written on papyrus: sigma looks like C, epsilon like a rounded Є (a C with a middle bar), omega often like ω, mu may be rounded like μ, and letters can be slanted.

For each crop, 1 to 28, give your single best guess using the Greek letter name (alpha, beta, gamma, delta, epsilon, zeta, eta, theta, iota, kappa, lambda, mu, nu, xi, omicron, pi, rho, sigma, tau, upsilon, phi, chi, psi, omega), or "unreadable" if you cannot make a reasonable guess, plus a confidence: 1 = guess, 2 = probable, 3 = sure. Judge each crop on its own.

Reply with exactly 28 lines in the form `N: name (confidence)` and nothing else.
```

## Sheet, version 2a

```
You are taking part in a letter-recognition test. Open exactly one file with the Read tool:
<image>
Do not open, list or search any other file or folder, and use no other tool.

The image is a sheet of 28 numbered grayscale crops. Each crop comes from an image of a damaged ancient Greek manuscript and is centred on one handwritten letter. Bright means ink, dark means no ink. The images are noisy: strokes may be broken, blurred or partial, there may be stray bright spots, and parts of neighbouring letters may appear at the edges.

The script is Greek capital letters as written on papyrus: sigma looks like C, epsilon like a rounded Є (a C with a middle bar), omega often like ω, mu may be rounded like μ, and letters can be slanted.

For each crop, 1 to 28, give your single best guess using the Greek letter name (alpha, beta, gamma, delta, epsilon, zeta, eta, theta, iota, kappa, lambda, mu, nu, xi, omicron, pi, rho, sigma, tau, upsilon, phi, chi, psi, omega), or "unreadable" if you cannot make a reasonable guess, plus a confidence: 1 = guess, 2 = probable, 3 = sure. Judge each crop on its own. Go by your first impression of each crop: do not deliberate at length over any of them.

Reply with exactly 28 lines in the form `N: name (confidence)` and nothing else.
```

## Sheet, version 2b

```
You are taking part in a letter-recognition test. Open exactly one file with the Read tool:
<image>
Do not open, list or search any other file or folder, and use no other tool.

The image is a sheet of 28 numbered grayscale crops. Each crop comes from an image of a damaged ancient Greek manuscript and is centred on one handwritten letter. Bright means ink, dark means no ink. The images are noisy: strokes may be broken, blurred or partial, there may be stray bright spots, and parts of neighbouring letters may appear at the edges.

The script is Greek capital letters as written on papyrus: sigma looks like C, epsilon like a rounded Є (a C with a middle bar), omega often like ω, mu may be rounded like μ, and letters can be slanted.

For each crop, 1 to 28, give your single best guess using the Greek letter name (alpha, beta, gamma, delta, epsilon, zeta, eta, theta, iota, kappa, lambda, mu, nu, xi, omicron, pi, rho, sigma, tau, upsilon, phi, chi, psi, omega), or "unreadable" if you cannot make a reasonable guess, plus a confidence: 1 = guess, 2 = probable, 3 = sure. Judge each crop on its own.

Reply with exactly 28 lines in the form `N: name (confidence)` and nothing else.

Go by your first impression of each crop: do not deliberate at length over any of them.
```

## Window, version 1

```
You are taking part in a reading test. Open exactly one file with the Read tool:
<image>
Do not open, list or search any other file or folder, and use no other tool.

The image is a map of ink on a piece of papyrus from a carbonized ancient scroll, computed from an X-ray scan: bright means ink, dark means no ink. The map is noisy: strokes may be broken, blurred or partial, and there are stray bright spots. A red grid is drawn over it: columns A to H from left to right, rows 1 to 5 from top to bottom.

If there is text, it is Greek, in capital letters as written on papyrus: sigma looks like C, epsilon like a rounded Є (a C with a middle bar), omega often like ω, mu may be rounded like μ, and letters can be slanted.

List every letter you can read, one per line, in the form `cell: name (confidence)`, where cell is the grid cell that contains the centre of the letter (for example C4), name is the Greek letter name (alpha, beta, gamma, delta, epsilon, zeta, eta, theta, iota, kappa, lambda, mu, nu, xi, omicron, pi, rho, sigma, tau, upsilon, phi, chi, psi, omega), and confidence is 1 = guess, 2 = probable, 3 = sure. List only letters you actually see. If you can read nothing, reply `none`. Reply with the list and nothing else.
```

## Window, version 2

```
You are taking part in a reading test. Open exactly one file with the Read tool:
<image>
Do not open, list or search any other file or folder, and use no other tool.

The image is a map of ink on a piece of papyrus from a carbonized ancient scroll, computed from an X-ray scan: bright means ink, dark means no ink. The map is noisy: strokes may be broken, blurred or partial, and there are stray bright spots. A red grid is drawn over it: columns A to H from left to right, rows 1 to 5 from top to bottom.

If there is text, it is Greek, in capital letters as written on papyrus: sigma looks like C, epsilon like a rounded Є (a C with a middle bar), omega often like ω, mu may be rounded like μ, and letters can be slanted.

List every letter you can read, one per line, in the form `cell: name (confidence)`, where cell is the grid cell that contains the centre of the letter (for example C4), name is the Greek letter name (alpha, beta, gamma, delta, epsilon, zeta, eta, theta, iota, kappa, lambda, mu, nu, xi, omicron, pi, rho, sigma, tau, upsilon, phi, chi, psi, omega), and confidence is 1 = guess, 2 = probable, 3 = sure. List only letters you actually see. If you can read nothing, reply `none`. Reply with the list and nothing else.

Go by your first impression of each letter: do not deliberate at length over any of them.
```
