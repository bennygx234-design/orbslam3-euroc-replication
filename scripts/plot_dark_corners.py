# Three views of one dark MH05 photo: the corners normal ORB-SLAM3 finds, the corners with a 2000 limit,
# and the corners after the contrast boost (shown on the boosted photo, where the grain becomes visible).
# Also prints how many corners land in the darkest part of the photo for each.
# Usage: plot_dark_corners.py <folder dark_corners wrote to> <seconds into flight> <brightness>
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle

d, when, level = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
CORNER, INK, MUTED, BG = "#1baf7a", "#0b0b0b", "#52514e", "#fcfcfb"
photo, boosted = plt.imread(f"{d}/photo.png"), plt.imread(f"{d}/photo_boosted.png")
panels = [(photo, "corners_normal.txt", "Normal: 1,200 corners"),
          (photo, "corners_2000.txt", "My version: 2,000 corners"),
          (boosted, "corners_boosted.txt", "Contrast boost: 1,200 corners on the boosted photo")]
dark_mask = photo * 255 < 30                          # the darkest parts of the original photo

fig, axes = plt.subplots(1, 3, figsize=(19, 4.6), facecolor=BG)
for ax, (img, name, title) in zip(axes, panels):
    c = np.loadtxt(f"{d}/{name}")
    ax.imshow(img, cmap="gray", vmin=0, vmax=1)
    for x, y, lvl in c:
        ax.add_patch(Circle((x, y), 2.5 * 1.2 ** lvl, fill=False, ec=CORNER, lw=0.8))
    in_dark = int(sum(dark_mask[min(int(y), dark_mask.shape[0] - 1), min(int(x), dark_mask.shape[1] - 1)] for x, y, _ in c))
    ax.set_title(title, fontsize=13, fontweight="bold", loc="left", color=INK)
    ax.text(0, -0.04, f"{len(c):,} corners, {in_dark:,} of them in the darkest areas", transform=ax.transAxes,
            va="top", fontsize=11, color=MUTED)
    ax.set_axis_off()
    print(title, len(c), "corners,", in_dark, "in dark areas")
fig.suptitle(f"One dark photo from MH05 ({when:.0f} s in, average brightness {level:.0f} out of 255): what ORB-SLAM3 picks out",
             fontsize=15, fontweight="bold", color=INK, x=0.07, ha="left", y=1.0)
fig.savefig(f"{d}/dark_corners.png", dpi=105, bbox_inches="tight", facecolor=BG)
print("saved", f"{d}/dark_corners.png")
