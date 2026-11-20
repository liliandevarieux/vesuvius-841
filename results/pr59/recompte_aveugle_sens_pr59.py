import numpy as np
import tifffile

base = "/home/slusarska_holding/vesuvius/c343/pr59/"
names = ["v8in_0343P_direct.tif", "v8in_0343P_inverse.tif",
         "v8in_erwin_direct.tif", "v8in_erwin_inverse.tif"]
for n in names:
    a = tifffile.imread(base + n)
    v = a[a > 0]
    p50 = np.percentile(v, 50)
    p99 = np.percentile(v, 99)
    print(f"{n}\tdtype={a.dtype}\tshape={a.shape}\tn_pos={v.size}\tp50={p50}\tp99={p99}\tp99-p50={p99 - p50}")
