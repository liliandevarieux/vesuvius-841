import json, glob, os
import numpy as np
import zarr

H, W = 1140, 3200
base = os.path.expanduser("~/vesuvius/c0800")
plan = json.load(open(os.path.join(base, "pr61/plan_fenetres.json")))
surfs = [l.split("\t")[0].strip() for l in open(os.path.expanduser("~/vesuvius/c0800_surfaces14.tsv")) if l.strip()]
print("surfaces in tsv (first col):", len(surfs), surfs)

wins = []
for u in plan["unites"]:
    for p in u["panneaux"]:
        if p.get("zone") == "0800":
            wins.append((u.get("id", u.get("nom", "?")), p["surface"], int(p["y0"]), int(p["x0"])))
print("number of 0800 windows:", len(wins))

masks = {}
def mask(m):
    if m not in masks:
        zs = glob.glob(os.path.join(base, "atlas", m, "surface-volumes", "*.zarr"))
        assert len(zs) == 1, (m, zs)
        a = zarr.open(zs[0], mode="r")["0"]
        masks[m] = np.asarray(a[15]) > 0
    return masks[m]

surf_with = sorted(set(w[1] for w in wins))
print("(a) distinct surfaces with >=1 0800 window:", len(surf_with), surf_with)
missing = [s for s in surf_with if s not in surfs]
if missing:
    print("   WARNING surfaces not in tsv:", missing)

covered_tot = 0
mask_tot = 0
for m in surfs:
    mk = mask(m)
    n = int(mk.sum())
    mask_tot += n
    cov = np.zeros_like(mk)
    for _, s, y0, x0 in wins:
        if s == m:
            cov[max(0, y0):max(0, y0 + H), max(0, x0):max(0, x0 + W)] = True
    c = int((mk & cov).sum())
    covered_tot += c
    print(f"   {m}: shape={mk.shape} mask={n} covered={c}")
print(f"(b) covered={covered_tot} total_mask={mask_tot} pct={100*covered_tot/mask_tot:.1f}")

print("(c) per-window mask fraction:")
for uid, s, y0, x0 in wins:
    mk = mask(s)
    sub = mk[max(0, y0):max(0, y0 + H), max(0, x0):max(0, x0 + W)]
    print(f"   unit={uid} surface={s} y0={y0} x0={x0}: {sub.sum()/(H*W):.2f}")
