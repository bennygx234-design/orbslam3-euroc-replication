# Draws what ORB-SLAM3's camera side looks for, using the output of dump_orb:
#   A: every corner it found in one photo
#   B: one example corner blown up, C: that corner's 256-bit fingerprint
#   D: the same corner in the right camera (the shift gives distance)
#   E: the same corners found again 1 second later (how it measures motion)
# Usage: plot_camera_sees.py <folder dump_orb wrote to>
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, ConnectionPatch

d = sys.argv[1]
CORNER, PICK, INK, MUTED, BG = "#1baf7a", "#eb6834", "#0b0b0b", "#52514e", "#fcfcfb"
plt.rcParams.update({"font.size": 9.5, "axes.titlesize": 11, "axes.titleweight": "bold"})

left, right, later = (plt.imread(f"{d}/rect_{n}.png") for n in ("left", "right", "later"))
cL, cR, cN = (np.loadtxt(f"{d}/corners_{n}.txt") for n in ("left", "right", "later"))
stereo = np.loadtxt(f"{d}/stereo_matches.txt")      # left index, right index, shift (px), fingerprint difference
track = np.loadtxt(f"{d}/track_matches.txt")        # left index, later index, fingerprint difference
fx, baseline = np.loadtxt(f"{d}/info.txt")
bits = lambda row: np.unpackbits(row[5:].astype(np.uint8))   # 32 bytes -> 256 yes/no answers

# Pick the example: a full-size corner, away from the edges, matched in the right photo AND 1 s later
st = {int(r[0]): r for r in stereo}
tr = {int(r[0]): r for r in track}
cands = [i for i in st if i in tr and cL[i, 2] == 0 and 90 < cL[i, 0] < 662 and 70 < cL[i, 1] < 410
         and 5 < st[i][2] < 60]
clear = [i for i in cands if st[i][3] <= 30 and tr[i][2] <= 40] or cands   # clearly-matched fingerprints
ex = max(clear, key=lambda i: st[i][2])            # the closest one, so the left/right shift is easiest to see
x, y, angle = cL[ex, 0], cL[ex, 1], cL[ex, 3]
xr, yr = cR[int(st[ex][1]), :2]
xn, yn = cN[int(tr[ex][1]), :2]
shift = x - xr
dist = fx * baseline / shift

fig = plt.figure(figsize=(15, 16.5), facecolor=BG)
gs = fig.add_gridspec(3, 3, height_ratios=[1.5, 1, 1.05], hspace=0.42, wspace=0.12)
LABEL = dict(color="white", fontweight="bold", bbox=dict(boxstyle="round", fc="#0b0b0bcc", ec="none"))
axA = fig.add_subplot(gs[0, :])
axB, axC, axD = fig.add_subplot(gs[1, 0]), fig.add_subplot(gs[1, 1]), fig.add_subplot(gs[1, 2])
axE = fig.add_subplot(gs[2, :])

def note(ax, text, y=-0.03):
    ax.text(0, y, text, transform=ax.transAxes, va="top", fontsize=9, color=MUTED, wrap=True)

# ---- A: every corner in one photo ----
axA.imshow(left, cmap="gray", vmin=0, vmax=1)
for cx, cy, lvl in cL[:, :3]:
    axA.add_patch(Circle((cx, cy), 2.5 * 1.2 ** lvl, fill=False, ec=CORNER, lw=0.9))
axA.add_patch(Circle((x, y), 14, fill=False, ec=PICK, lw=2.5))
axA.annotate("example corner\n(blown up below)", (x, y), xytext=(30, -30), textcoords="offset points", color=PICK,
             fontweight="bold", fontsize=10, arrowprops=dict(arrowstyle="-", color=PICK, lw=1.5),
             bbox=dict(boxstyle="round", fc=BG, ec=PICK))
axA.set_axis_off()
axA.set_title(f"A.  One photo from the left camera (MH_01, 75 s in): the {len(cL):,} corners ORB-SLAM3 picked out", loc="left")
note(axA, "Each green circle is a corner: a spot where brightness changes sharply in two directions (a bolt, the tip of a pipe, two edges meeting).\n"
          "Corners can be pinned to an exact pixel; a blank wall or a long straight edge can't, so ORB-SLAM3 ignores those.\n"
          "Bigger circle = found on a shrunken copy of the photo (it searches 8 sizes, so it knows the same corner up close or far away).\n"
          "Found with ORB-SLAM3's own code and settings: about 1,200 corners per photo.", y=-0.015)

# ---- B: the example corner blown up ----
r = 15                                               # ORB-SLAM3 looks at a circle of radius 15 px around each corner
xi, yi = int(round(x)), int(round(y))
axB.imshow(left[yi - r:yi + r + 1, xi - r:xi + r + 1], cmap="gray", vmin=0, vmax=1, interpolation="nearest",
           extent=(-r - 0.5, r + 0.5, r + 0.5, -r - 0.5))
axB.add_patch(Circle((x - xi, y - yi), r, fill=False, ec=PICK, lw=1.5, ls="--"))
axB.plot(x - xi, y - yi, "+", color=PICK, ms=18, mew=2.5)
a = np.deg2rad(angle)
axB.annotate("", (x - xi + 11 * np.cos(a), y - yi + 11 * np.sin(a)), (x - xi, y - yi),
             arrowprops=dict(arrowstyle="-|>", color=PICK, lw=2.5, mutation_scale=18))
axB.set_xticks([]); axB.set_yticks([])
axB.set_title("B.  The example corner, 31 x 31 pixels", loc="left")
note(axB, "Each square is one pixel. The + is the corner.\nThe dashed circle is the patch ORB-SLAM3 reads\n"
          "to describe it. The arrow is the way the brightness\n'leans', so the description still matches if the\ndrone tilts.")

# ---- C: its fingerprint ----
fp = bits(cL[ex]).reshape(8, 32)
axC.imshow(fp, cmap="gray_r", vmin=0, vmax=1, interpolation="nearest")
axC.set_xticks(np.arange(-0.5, 32, 1), minor=True); axC.set_yticks(np.arange(-0.5, 8, 1), minor=True)
axC.grid(which="minor", color="#8a8985", lw=0.4); axC.tick_params(which="both", length=0)
axC.set_xticks([]); axC.set_yticks([])
axC.set_title("C.  Its fingerprint: 256 yes/no answers", loc="left")
note(axC, "For 256 fixed pairs of pixels inside the patch, it asks\n'is pixel 1 brighter than pixel 2?' Black = yes, white = no.\n"
          "Two corners count as the same one when their fingerprints\ndisagree in only a few of the 256 boxes.\n"
          f"This corner's twin in the right photo disagreed in {int(st[ex][3])}.\n"
          f"Its twin 1 second later disagreed in {int(tr[ex][2])}.")

# ---- D: same corner in the right camera ----
w, h = 56, 36                                         # tight crop so a few pixels of shift are visible
cropL = left[yi - h:yi + h, xi - w:xi + w]
cropR = right[yi - h:yi + h, xi - w:xi + w]
axD.imshow(np.vstack([cropL, np.ones((4, 2 * w)), cropR]), cmap="gray", vmin=0, vmax=1, interpolation="nearest",
           extent=(xi - w - 0.5, xi + w - 0.5, yi + h + 4 + 2 * h - 0.5, yi - h - 0.5))
off = 2 * h + 4                                       # right crop is drawn below the left one
axD.plot(x, y, "+", color=PICK, ms=14, mew=2.5); axD.plot(xr, yr + off, "+", color=PICK, ms=14, mew=2.5)
axD.axvline(x, color=PICK, ls=":", lw=1.2)
axD.annotate("", (xr, yr + off - 7), (x, yr + off - 7), arrowprops=dict(arrowstyle="-|>", color=PICK, lw=2))
axD.text(xi - w + 3, yi - h + 8, "left camera", fontsize=9, **LABEL)
axD.text(xi - w + 3, yi + h + 4 + 8, "right camera", fontsize=9, **LABEL)
axD.set_axis_off()
axD.set_title("D.  Same corner, same instant, right camera", loc="left")
note(axD, f"The right camera sits 11 cm to the right, so it sees\nthe corner {shift:.1f} pixels further left.\n"
          f"Distance = focal length x camera gap / shift\n"
          f"         = {fx:.0f} px x {baseline:.3f} m / {shift:.1f} px = {dist:.2f} m away.\n"
          "Close things shift a lot, far things barely shift.\nThis is how 2 cameras give real-world size.")

# ---- E: the same corners 1 second later ----
both = np.hstack([left, np.ones((left.shape[0], 12)), later])
gap = left.shape[1] + 12
axE.imshow(both, cmap="gray", vmin=0, vmax=1)
for iL, iN, _ in track:
    (ax0, ay0), (ax1, ay1) = cL[int(iL), :2], cN[int(iN), :2]
    axE.plot([ax0, ax1 + gap], [ay0, ay1], color=CORNER, lw=0.7, alpha=0.8)
    axE.plot(ax0, ay0, "o", ms=3, color=CORNER); axE.plot(ax1 + gap, ay1, "o", ms=3, color=CORNER)
axE.plot([x, xn + gap], [y, yn], color=PICK, lw=2.5)
axE.plot(x, y, "o", ms=8, mfc="none", mec=PICK, mew=2.5); axE.plot(xn + gap, yn, "o", ms=8, mfc="none", mec=PICK, mew=2.5)
axE.text(10, 26, "reference photo (75 s)", fontsize=10, **LABEL)
axE.text(gap + 10, 26, "1 second later (76 s)", fontsize=10, **LABEL)
axE.set_axis_off()
axE.set_title(f"E.  The same fingerprints found again 1 second later: {len(track)} corners", loc="left")
note(axE, "Each green line joins one corner in the reference photo to the same corner a second later (orange = the example). "
          "How all the corners slid tells it how the drone moved.\nHere it is shown photo-to-photo to make the idea visible. "
          "The real program does this 20 times a second, matching each new photo against its 3D map of corners\n"
          "(built from reference photos like the left one, called keyframes).", y=-0.015)

fig.suptitle("What ORB-SLAM3's cameras look for", fontsize=15, fontweight="bold", color=INK, y=0.92)
out = f"{d}/what_the_camera_sees.png"
fig.savefig(out, dpi=105, bbox_inches="tight", facecolor=BG)
print(out, f"example corner at ({x:.0f},{y:.0f}) shift {shift:.1f}px dist {dist:.2f}m")
