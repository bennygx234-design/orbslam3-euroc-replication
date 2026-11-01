# One bar chart: each flight's score with and without the motion sensor (your PC, run 1).
# Reads the scores evo already wrote (evo_score.txt) for both modes.
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

home = os.path.expanduser("~/tks-slam/results")
flights = ["MH01", "MH02", "MH03", "MH04", "MH05"]
names = ["MH01\neasy", "MH02\neasy", "MH03\nmedium", "MH04\ndifficult", "MH05\ndifficult"]
WITH, WITHOUT, MUTED, BG = "#2a78d6", "#eb6834", "#52514e", "#fcfcfb"

def score(mode, f):
    for line in open(f"{home}/{mode}/{f}/run1/evo_score.txt"):
        if line.split() and line.split()[0] == "rmse":
            return float(line.split()[1]) * 100

cam = [score("stereo", f) for f in flights]
both = [score("stereo_inertial", f) for f in flights]

fig, ax = plt.subplots(figsize=(11, 6), facecolor=BG)
ax.set_facecolor(BG)
x = range(len(flights))
w = 0.36
b1 = ax.bar([i - w / 2 - 0.01 for i in x], cam, w, color=WITHOUT, label="Camera only (motion sensor off)")
b2 = ax.bar([i + w / 2 + 0.01 for i in x], both, w, color=WITH, label="Camera + motion sensor")
for bars in (b1, b2):
    for b in bars:
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.1, f"{b.get_height():.2f}", ha="center", va="bottom", fontsize=11)
ax.set_xticks(list(x)); ax.set_xticklabels(names, fontsize=12)
ax.set_ylabel("score: how far off (cm), lower is better", color=MUTED)
ax.spines[["top", "right"]].set_visible(False)
ax.grid(axis="y", color="#ebeae6"); ax.set_axisbelow(True)
ax.legend(fontsize=11, frameon=False, loc="upper left")
ax.set_title("Did the motion sensor make ORB-SLAM3 more accurate? (your PC, 1 run each)",
             fontsize=14, fontweight="bold", loc="left")
out = f"{home}/imu_summary.png"
fig.savefig(out, dpi=100, bbox_inches="tight", facecolor=BG)
print(out, "camera only:", [round(c, 2) for c in cam], "with sensor:", [round(b, 2) for b in both])
