# Average brightness (0 = black, 255 = white) of the left-camera photos, every 10th photo
import os, numpy as np, matplotlib.image as mpimg
base = os.path.expanduser("~/tks-slam/datasets/euroc")
for f in ["MH_01_easy", "MH_02_easy", "MH_03_medium", "MH_04_difficult", "MH_05_difficult"]:
    d = f"{base}/{f}/mav0/cam0/data"
    names = sorted(os.listdir(d))[::10]
    b = np.array([mpimg.imread(f"{d}/{n}").mean() * 255 for n in names])
    print(f"{f:16s} average {b.mean():5.1f}   darkest {b.min():5.1f}   share of photos darker than 40: {np.mean(b < 40)*100:4.0f}%")
