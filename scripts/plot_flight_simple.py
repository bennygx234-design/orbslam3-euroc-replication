# Simple version of the flight picture: one idea per chart.
#   Top:    the path the drone really flew vs where ORB-SLAM3 thought it was,
#           with the gap blown up 10x so you can actually see where they split.
#   Bottom: how far off ORB-SLAM3 was at every moment, plus your score and the paper's.
#   Letters A, B, C mark the same 3 biggest slips on both charts.
# Usage: plot_flight_simple.py <flight folder> <short name> <paper rmse in m> [run number]
import sys, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from evo.tools import file_interface
from evo.core import sync

flight, short, paper = sys.argv[1], sys.argv[2], float(sys.argv[3])
run = sys.argv[4] if len(sys.argv) > 4 else "1"
home = os.path.expanduser("~/tks-slam")
gt_path = f"{home}/datasets/euroc/{flight}/mav0/state_groundtruth_estimate0/data.csv"
photo_list = f"{home}/ORB_SLAM3/Examples/Stereo-Inertial/EuRoC_TimeStamps/{short}.txt"
out_dir = f"{home}/results/stereo_inertial/{short}/run{run}"
BLOW_UP = 10

TRUTH, GUESS, SCORE, PAPER, INK, MUTED, BG = "#a8a7a2", "#2a78d6", "#184f95", "#eb6834", "#0b0b0b", "#52514e", "#fcfcfb"
plt.rcParams.update({"axes.edgecolor": "#c3c2b7", "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED,
                     "axes.grid": True, "grid.color": "#ebeae6", "font.size": 12, "axes.titlesize": 15,
                     "axes.titleweight": "bold", "axes.titlelocation": "left"})

truth = file_interface.read_euroc_csv_trajectory(gt_path)
guess = file_interface.read_tum_trajectory_file(f"{out_dir}/f_{short}_seconds.txt")
truth, guess = sync.associate_trajectories(truth, guess)
guess.align(truth, correct_scale=False)
P, G = truth.positions_xyz, guess.positions_xyz
err_cm = np.linalg.norm(G - P, axis=1) * 100
score_cm = np.sqrt(np.mean(err_cm ** 2))
t = truth.timestamps - int(open(photo_list).readline().split()[0]) / 1e9
t_end = sum(1 for line in open(photo_list) if line.strip()) / 20.0

# The 3 biggest slips, at least 8 seconds apart
slips = []
for i in np.argsort(err_cm)[::-1]:
    if all(abs(t[i] - t[j]) > 8 for j in slips):
        slips.append(i)
    if len(slips) == 3:
        break
slips.sort(key=lambda i: t[i])

def bubble(ax, xy, letter, dx, dy):
    ax.annotate(letter, xy, xytext=(dx, dy), textcoords="offset points", ha="center", va="center",
                fontsize=12, fontweight="bold", color="white", zorder=10,
                bbox=dict(boxstyle="circle,pad=0.3", fc=INK, ec="none"),
                arrowprops=dict(arrowstyle="-", color=INK, lw=1.2))

fig, (ax_map, ax_err) = plt.subplots(2, 1, figsize=(12, 15), facecolor=BG, gridspec_kw={"height_ratios": [1.5, 1], "hspace": 0.28})
for a in (ax_map, ax_err):
    a.set_facecolor(BG)

# ---- Top: the two paths ----
shown = P + BLOW_UP * (G - P)
ax_map.plot(P[:, 0], P[:, 1], color=TRUTH, lw=5, solid_capstyle="round", label="Where the drone really flew (laser tracker)")
ax_map.plot(shown[:, 0], shown[:, 1], color=GUESS, lw=1.6, label=f"Where ORB-SLAM3 thought it was (gap blown up {BLOW_UP}x)")
ax_map.plot(*P[0, :2], "o", ms=12, color=INK, mec=BG, zorder=6, label="Start")
for n, i in enumerate(slips):
    bubble(ax_map, P[i, :2], "ABC"[n], 28, 28)
ax_map.set_aspect("equal", adjustable="datalim")
ax_map.set_xlabel("meters"); ax_map.set_ylabel("meters")
ax_map.set_title("1.  The flight seen from above", pad=52)
ax_map.legend(loc="lower left", fontsize=11.5, framealpha=0.95)
ax_map.text(0, 1.015, f"Where the blue line leaves the gray one, ORB-SLAM3 was off. Real gaps are {BLOW_UP}x smaller than drawn "
            "(a few cm),\nso without blowing them up the two lines would sit exactly on top of each other.",
            transform=ax_map.transAxes, fontsize=11, color=MUTED, va="bottom")

# ---- Bottom: how far off, moment by moment ----
ax_err.axvspan(0, t[0], color="#ebeae6", lw=0)
ax_err.text(t[0] / 2, 0.5, "warming\nup\n(not\nscored)", transform=ax_err.get_xaxis_transform(), ha="center", va="center", fontsize=10, color=MUTED)
ax_err.fill_between(t, err_cm, color=GUESS, alpha=0.15, lw=0)
ax_err.plot(t, err_cm, color=GUESS, lw=1.3)
ax_err.axhline(score_cm, color=SCORE, ls="--", lw=2)
ax_err.axhline(paper * 100, color=PAPER, ls="--", lw=2)
paper_higher = paper * 100 >= score_cm             # put the higher label above its line, the lower one below
ax_err.annotate(f"Your score\n{score_cm:.2f} cm", (t_end, score_cm), xytext=(8, -4 if paper_higher else 4), textcoords="offset points",
                color=SCORE, fontsize=12, fontweight="bold", va="top" if paper_higher else "bottom", annotation_clip=False)
ax_err.annotate(f"Paper's score\n{paper*100:.1f} cm", (t_end, paper * 100), xytext=(8, 4 if paper_higher else -4), textcoords="offset points",
                color=PAPER, fontsize=12, fontweight="bold", va="bottom" if paper_higher else "top", annotation_clip=False)
for n, i in enumerate(slips):
    bubble(ax_err, (t[i], err_cm[i]), "ABC"[n], 0, 22)
    ax_err.annotate(f"{err_cm[i]:.0f} cm", (t[i], err_cm[i]), xytext=(18, 22), textcoords="offset points", va="center", fontsize=11, color=INK)
ax_err.set_xlim(0, t_end); ax_err.set_ylim(0, max(err_cm.max(), paper * 100) * 1.35)
ax_err.set_xlabel("seconds into the flight"); ax_err.set_ylabel("off by (cm)")
ax_err.set_title("2.  How far off ORB-SLAM3 was, moment by moment")

fig.suptitle(f"{flight}: did ORB-SLAM3 know where the drone was?", fontsize=18, fontweight="bold", color=INK, x=0.125, ha="left", y=0.975)
png = f"{out_dir}/{short}_run{run}_simple.png"
fig.savefig(png, dpi=100, bbox_inches="tight", facecolor=BG)
print(png, "slips:", ", ".join(f"{'ABC'[n]} {t[i]:.0f}s {err_cm[i]:.1f}cm" for n, i in enumerate(slips)))
