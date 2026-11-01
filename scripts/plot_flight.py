# Draws one flight so you can see how close ORB-SLAM3's guess was to the true path.
#   Top left:  the whole flight seen from above (true path vs guess).
#   Top right: zoomed into the worst moment, so the gap is big enough to see.
#   Bottom:    the gap at every moment, and how those gaps build up into the final score.
# Uses evo to pair up moments and line the paths up (move + rotate only), same as the score.
# Usage: plot_flight.py <flight folder> <short name> <paper rmse in m> [run number]
import sys, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, ConnectionPatch
from evo.tools import file_interface
from evo.core import sync

flight, short, paper = sys.argv[1], sys.argv[2], float(sys.argv[3])
run = sys.argv[4] if len(sys.argv) > 4 else "1"
home = os.path.expanduser("~/tks-slam")
gt_path = f"{home}/datasets/euroc/{flight}/mav0/state_groundtruth_estimate0/data.csv"
photo_list = f"{home}/ORB_SLAM3/Examples/Stereo-Inertial/EuRoC_TimeStamps/{short}.txt"
out_dir = f"{home}/results/stereo_inertial/{short}/run{run}"

# Colors: gray = truth, blue = ORB-SLAM3 (light for each moment, dark for the score), orange = paper
TRUTH, GUESS, SCORE, PAPER, INK, MUTED = "#8a8985", "#2a78d6", "#184f95", "#eb6834", "#0b0b0b", "#52514e"
BG, FAINT, GRID = "#fcfcfb", "#c3c2b7", "#ebeae6"
plt.rcParams.update({"axes.edgecolor": FAINT, "axes.labelcolor": MUTED, "xtick.color": MUTED,
                     "ytick.color": MUTED, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8,
                     "axes.titlesize": 11, "axes.titleweight": "bold", "font.size": 9.5})

truth = file_interface.read_euroc_csv_trajectory(gt_path)
guess = file_interface.read_tum_trajectory_file(f"{out_dir}/f_{short}_seconds.txt")
truth, guess = sync.associate_trajectories(truth, guess)
guess.align(truth, correct_scale=False)

P, G = truth.positions_xyz, guess.positions_xyz
err_cm = np.linalg.norm(G - P, axis=1) * 100
running_cm = np.sqrt(np.cumsum(err_cm ** 2) / np.arange(1, len(err_cm) + 1))   # score so far
rmse_cm = running_cm[-1]

# Clock starts at the flight's first photo, so the start-up stretch shows up too
first_photo = int(open(photo_list).readline().split()[0]) / 1e9
n_photos = sum(1 for line in open(photo_list) if line.strip())
t = truth.timestamps - first_photo
t_end = n_photos / 20.0
w = int(np.argmax(err_cm))                       # worst moment
gap_side = np.linalg.norm(G[w, :2] - P[w, :2]) * 100
gap_up = abs(G[w, 2] - P[w, 2]) * 100

fig = plt.figure(figsize=(14, 10.5), facecolor=BG)
gs = fig.add_gridspec(2, 2, height_ratios=[1.25, 1], width_ratios=[1.35, 1], hspace=0.38, wspace=0.18)
ax_map, ax_zoom, ax_err = fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1]), fig.add_subplot(gs[1, :])
for a in (ax_map, ax_zoom, ax_err):
    a.set_facecolor(BG)

# ---- Top left: the whole flight from above ----
ax_map.plot(P[:, 0], P[:, 1], color=TRUTH, lw=3.5, solid_capstyle="round", label="True path (laser tracker)")
ax_map.plot(G[:, 0], G[:, 1], color=GUESS, lw=1.2, label="ORB-SLAM3's guess")
ax_map.plot(*P[0, :2], "o", ms=9, color=INK, mec=BG, zorder=5, label="Start")
ax_map.plot(*P[-1, :2], "s", ms=9, color=INK, mec=BG, zorder=5, label="End")
for sec in range(20, int(t[-1]), 20):            # time stamps along the path
    i = int(np.argmin(abs(t - sec)))
    ax_map.plot(*P[i, :2], "o", ms=4, color=MUTED, zorder=4)
    ax_map.annotate(f"{sec}s", P[i, :2], xytext=(4, 4), textcoords="offset points", fontsize=8, color=MUTED)
half = 0.35                                       # zoom box half-width in meters
ax_map.add_patch(Rectangle((P[w, 0] - half, P[w, 1] - half), 2 * half, 2 * half, fill=False, ec=INK, lw=1.2, zorder=6))
ax_map.set_aspect("equal", adjustable="datalim")
ax_map.set_xlabel("meters"); ax_map.set_ylabel("meters")
ax_map.set_title("Whole flight, seen from above")
ax_map.legend(loc="best", fontsize=9, framealpha=0.95)
ax_map.text(0.0, -0.12, "The two lines sit on top of each other: the gap is a few cm, the hall is many meters across.\n"
            "The black box is the worst moment, blown up on the right.", transform=ax_map.transAxes, fontsize=8.5, color=MUTED, va="top")

# ---- Top right: zoom into the worst moment ----
near = np.where(abs(t - t[w]) < 4)[0]             # 4 s either side
for i in near[::2]:                               # thin gray lines: same instant, truth vs guess
    ax_zoom.plot([P[i, 0], G[i, 0]], [P[i, 1], G[i, 1]], color=FAINT, lw=0.8, zorder=1)
ax_zoom.plot(P[near, 0], P[near, 1], ".-", color=TRUTH, lw=2.5, ms=5, label="True path", zorder=2)
ax_zoom.plot(G[near, 0], G[near, 1], ".-", color=GUESS, lw=1.2, ms=4, label="ORB-SLAM3's guess", zorder=3)
ax_zoom.plot([P[w, 0], G[w, 0]], [P[w, 1], G[w, 1]], color=INK, lw=2, zorder=4)
ax_zoom.plot(*P[w, :2], "*", ms=16, color=INK, mec=BG, zorder=5)
ax_zoom.annotate(f"worst moment, {t[w]:.1f} s\ngap {err_cm[w]:.1f} cm\n({gap_side:.1f} cm sideways, {gap_up:.1f} cm up/down)",
                 P[w, :2], xytext=(14, -40), textcoords="offset points", fontsize=9, color=INK,
                 bbox=dict(boxstyle="round", fc=BG, ec=FAINT))
ax_zoom.set_xlim(P[w, 0] - half, P[w, 0] + half); ax_zoom.set_ylim(P[w, 1] - half, P[w, 1] + half)
ax_zoom.set_aspect("equal"); ax_zoom.set_xlabel("meters")
ax_zoom.set_title(f"Zoomed in: 70 cm box around {t[w]:.0f} s")
ax_zoom.legend(loc="upper left", fontsize=8.5, framealpha=0.95)
ax_zoom.text(0.0, -0.12, "Each dot is one photo (20 per second). Each thin gray line joins where the drone\n"
             "really was and where ORB-SLAM3 guessed, at the same instant.", transform=ax_zoom.transAxes, fontsize=8.5, color=MUTED, va="top")
fig.add_artist(ConnectionPatch((P[w, 0] + half, P[w, 1]), (0, 0.5), "data", "axes fraction",
                               axesA=ax_map, axesB=ax_zoom, color=INK, lw=1))

# ---- Bottom: the gap at every moment, and the score building up ----
ax_err.axvspan(0, t[0], color=GRID, lw=0)
ax_err.text(t[0] / 2, 0.97, "starting\nup (not\nscored)", transform=ax_err.get_xaxis_transform(),
            ha="center", va="top", fontsize=8, color=MUTED)
ax_err.plot(t, err_cm, color=GUESS, lw=1, alpha=0.75, label="Gap at each moment")
ax_err.plot(t, running_cm, color=SCORE, lw=2.5, label="Your score so far (RMSE of every gap up to that moment)")
ax_err.axhline(paper * 100, color=PAPER, ls="--", lw=2,
               label=f"Paper's score: {paper*100:.1f} cm (one number per flight, nothing moment-by-moment)")
ax_err.plot(t[w], err_cm[w], "*", ms=16, color=INK, mec=BG, zorder=5)
ax_err.annotate(f"worst moment: {err_cm[w]:.1f} cm", (t[w], err_cm[w]), xytext=(10, -4), textcoords="offset points", fontsize=9, color=INK)
ax_err.annotate(f"final\nscore\n{rmse_cm:.2f} cm", (t[-1], rmse_cm), xytext=(8, 0), textcoords="offset points",
                va="center", fontsize=9.5, color=SCORE, fontweight="bold")
ax_err.set_xlim(0, t_end * 1.07);ax_err.set_ylim(0, max(err_cm.max(), paper * 100) * 1.25)
ax_err.set_xlabel("seconds since the first photo"); ax_err.set_ylabel("gap (cm)")
ax_err.set_title("How far off the guess was at every moment, and how that builds the score")
ax_err.legend(loc="upper right", fontsize=8.5, framealpha=0.95)

fig.suptitle(f"EuRoC {flight}, run {run}: ORB-SLAM3 with camera pair + motion sensor   "
             f"({len(err_cm)} of {n_photos} photos scored)", fontsize=13, fontweight="bold", color=INK, y=0.95)
png = f"{out_dir}/{short}_run{run}_plot.png"
fig.savefig(png, dpi=110, bbox_inches="tight", facecolor=fig.get_facecolor())
print(png, f"rmse={rmse_cm:.2f} cm worst={err_cm[w]:.1f} cm at {t[w]:.1f}s")
