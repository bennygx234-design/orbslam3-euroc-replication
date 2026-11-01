# Bar chart: paper's error vs our error on each Machine Hall flight (stereo-inertial, run 1)
import re, os
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
home = os.path.expanduser("~/tks-slam/results/stereo_inertial")
flights = ["MH01", "MH02", "MH03", "MH04", "MH05"]
labels = ["MH_01\neasy", "MH_02\neasy", "MH_03\nmedium", "MH_04\ndifficult", "MH_05\ndifficult"]
paper = [3.6, 3.3, 3.5, 5.1, 8.2]
ours = [float(re.search(r"rmse\s+([\d.]+)", open(f"{home}/{f}/run1/evo_score.txt").read()).group(1)) * 100 for f in flights]
x = range(len(flights)); w = 0.38
fig, ax = plt.subplots(figsize=(9, 5))
b1 = ax.bar([i - w/2 for i in x], paper, w, color="#9aa5b1", label="Paper (median of 10 runs)")
b2 = ax.bar([i + w/2 for i in x], ours, w, color="#6f42c1", label="Your PC (1 run)")
for bars in (b1, b2):
    for b in bars:
        ax.text(b.get_x() + b.get_width()/2, b.get_height() + 0.1, f"{b.get_height():.1f}", ha="center", fontsize=9)
ax.set_xticks(list(x)); ax.set_xticklabels(labels)
ax.set_ylabel("average error (cm)"); ax.set_ylim(0, 9.5)
ax.set_title("ORB-SLAM3 (2 cameras + motion sensor) on EuRoC Machine Hall: paper vs your PC")
ax.legend(); ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout(); out = f"{home}/machine_hall_summary.png"; fig.savefig(out, dpi=120); print(out, [round(o, 2) for o in ours])
