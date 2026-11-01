# Article charts, made from the saved scores (evo_score.txt) and paths. Run only when no ORB-SLAM3 run is going.
#   1. reproduction.png    paper vs your PC (normal ORB-SLAM3, 10 final-check runs per flight)
#   2. every_fix.png       every run of every Day 2 version on MH04 and MH05 (shows the wobble and the winner)
#   3. final_check.png     normal vs 2000 corners, 10 runs each on all 5 flights, with the win count
#   4. silent_jump.png     the MH02 run where the guess teleported 87 cm
# Usage: make_visuals.py <output folder>
import os, sys, glob
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from evo.tools import file_interface
from evo.core import sync

out = sys.argv[1]
home = os.path.expanduser("~/tks-slam")
FLIGHTS = ["MH01", "MH02", "MH03", "MH04", "MH05"]
FOLDERS = {"MH01": "MH_01_easy", "MH02": "MH_02_easy", "MH03": "MH_03_medium", "MH04": "MH_04_difficult", "MH05": "MH_05_difficult"}
LABELS = {"MH01": "MH01\neasy", "MH02": "MH02\neasy", "MH03": "MH03\nmedium", "MH04": "MH04\ndifficult", "MH05": "MH05\ndifficult"}
PAPER = {"MH01": 3.6, "MH02": 3.3, "MH03": 3.5, "MH04": 5.1, "MH05": 8.2}
NORMAL, MINE, PAPERC, INK, MUTED, FAINT, BG = "#2a78d6", "#1baf7a", "#eb6834", "#0b0b0b", "#52514e", "#c3c2b7", "#fcfcfb"
plt.rcParams.update({"axes.edgecolor": FAINT, "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED,
                     "axes.grid": True, "grid.color": "#ebeae6", "font.size": 12, "axes.titlesize": 15,
                     "axes.titleweight": "bold", "axes.titlelocation": "left", "figure.facecolor": BG, "axes.facecolor": BG})

def scores(root, version, flight):
    """RMS gap (cm) of every finished run of one version on one flight."""
    s = []
    for f in sorted(glob.glob(f"{home}/results/{root}/{version}/{flight}/run*/evo_score.txt")):
        for line in open(f):
            if line.split() and line.split()[0] == "rmse":
                s.append(float(line.split()[1]) * 100)
    return np.array(s)

def dots(ax, x, values, color, label=None, cap=None):
    """One dot per run (spread sideways a little so they don't hide each other) plus a bar at the middle score."""
    shown = np.minimum(values, cap) if cap else values
    jitter = np.linspace(-0.12, 0.12, len(values)) if len(values) > 1 else [0]
    ax.scatter(x + np.array(jitter), shown, s=36, color=color, alpha=0.75, edgecolor=BG, linewidth=0.8, zorder=3, label=label)
    if cap is not None and (values > cap).any():
        for j, v in zip(jitter, values):
            if v > cap:
                ax.annotate(f"{v:.0f} cm\n(off chart)", (x + j, cap), xytext=(0, 6), textcoords="offset points",
                            ha="center", fontsize=9, color=MUTED)
    ax.plot([x - 0.2, x + 0.2], [np.median(values)] * 2, color=color, lw=3, zorder=4)

# ---- 1. Reproduction: paper vs your PC ----
fig, ax = plt.subplots(figsize=(11, 6))
for i, fl in enumerate(FLIGHTS):
    s = scores("final", "baseline", fl)
    dots(ax, i, s, NORMAL, "My PC: each run (dot) and middle score (bar)" if i == 0 else None, cap=9)
    ax.plot([i - 0.2, i + 0.2], [PAPER[fl]] * 2, color=PAPERC, lw=3, ls=(0, (3, 2)), zorder=5,
            label="Paper: middle of its 10 runs" if i == 0 else None)
    ax.annotate(f"{np.median(s):.2f}", (i + 0.22, np.median(s)), va="center", fontsize=10.5, color=NORMAL, fontweight="bold")
    ax.annotate(f"{PAPER[fl]:.1f}", (i - 0.22, PAPER[fl]), ha="right", va="center", fontsize=10.5, color=PAPERC, fontweight="bold")
ax.set_xticks(range(5)); ax.set_xticklabels([LABELS[f] for f in FLIGHTS])
ax.set_ylim(0, 9.8); ax.set_ylabel("how far off (cm), lower is better")
ax.set_title("ORB-SLAM3 on my PC vs the published paper (10 runs per flight)")
ax.legend(loc="upper left", frameon=False, fontsize=11)
fig.savefig(f"{out}/reproduction.png", dpi=110, bbox_inches="tight"); plt.close(fig)

# ---- 2. Every run of every Day 2 version on the two hard flights ----
versions = [("baseline", "Normal\n(authors'\nsettings)"), ("clahe", "Contrast\nboost"), ("imu_more", "Trust motion\nsensor more"),
            ("imu_less", "Trust motion\nsensor less"), ("clahe_v2", "Gentle\nboost"), ("gamma_dark", "Brightness\ncurve"),
            ("corners2000", "2000\ncorners"), ("corners2500", "2500\ncorners"), ("corners3000", "3000\ncorners")]
fig, axes = plt.subplots(2, 1, figsize=(13, 10), sharex=True, gridspec_kw={"hspace": 0.18})
for ax, fl in zip(axes, ["MH04", "MH05"]):
    base = np.median(scores("day2", "baseline", fl))
    ax.axhline(base, color=NORMAL, lw=1.2, ls="--", zorder=1)
    ax.annotate("normal's middle score", (len(versions) - 0.5, base), xytext=(0, 4), textcoords="offset points",
                ha="right", fontsize=10, color=NORMAL)
    for i, (v, _) in enumerate(versions):
        s = scores("day2", v, fl)
        if not len(s):
            continue
        color = NORMAL if v == "baseline" else (MINE if v == "corners2000" else "#8a8985")
        dots(ax, i, s, color)
        ax.annotate(f"{np.median(s):.2f}", (i, np.median(s)), xytext=(17, 0), textcoords="offset points", va="center",
                    fontsize=9.5, color=color if v in ("baseline", "corners2000") else MUTED, fontweight="bold")
    ax.set_ylabel(f"{fl}: how far off (cm)")
    ax.set_title(f"{FOLDERS[fl]}: every run of every version (5 runs each, bar = middle score)", fontsize=13)
axes[1].set_xticks(range(len(versions))); axes[1].set_xticklabels([n for _, n in versions], fontsize=10.5)
fig.suptitle("Day 2: what helped and what hurt", fontsize=17, fontweight="bold", color=INK, x=0.125, ha="left", y=0.97)
fig.savefig(f"{out}/every_fix.png", dpi=110, bbox_inches="tight"); plt.close(fig)

# ---- 3. Final check: normal vs 2000 corners ----
fig, ax = plt.subplots(figsize=(12, 6.5))
wins = ties = total = 0
lines = []
for i, fl in enumerate(FLIGHTS):
    a, b = scores("final", "baseline", fl), scores("final", "corners2000", fl)
    n = min(len(a), len(b))
    wins += int(np.sum(b[:n] < a[:n])); ties += int(np.sum(b[:n] == a[:n])); total += n
    dots(ax, i - 0.22, a, NORMAL, "Normal (authors' settings)" if i == 0 else None, cap=9)
    dots(ax, i + 0.22, b, MINE, "My version (2000 corners)" if i == 0 else None, cap=9)
    lines.append(f"{fl}: normal {np.median(a):.2f}, 2000 corners {np.median(b):.2f} ({(np.median(b) / np.median(a) - 1) * 100:+.0f}%)")
ax.set_xticks(range(5)); ax.set_xticklabels([LABELS[f] for f in FLIGHTS])
ax.set_ylim(0, 9.8); ax.set_ylabel("how far off (cm), lower is better")
ax.set_title("Final check: normal vs my version, 10 fresh runs each (bar = middle score)")
ax.legend(loc="upper left", frameon=False, fontsize=11)
ax.text(0.99, 0.97, f"My version won {wins} of {total} head-to-head runs" + (f" ({ties} ties)" if ties else ""),
        transform=ax.transAxes, ha="right", va="top", fontsize=12, color=INK, fontweight="bold")
fig.savefig(f"{out}/final_check.png", dpi=110, bbox_inches="tight"); plt.close(fig)
print("final check:", f"2000 corners won {wins}/{total}, ties {ties}"); print("\n".join(lines))

# ---- 4. The silent jump (MH02 normal, Day 2 run 4) ----
truth = file_interface.read_euroc_csv_trajectory(f"{home}/datasets/euroc/MH_02_easy/mav0/state_groundtruth_estimate0/data.csv")
guess = file_interface.read_tum_trajectory_file(f"{home}/results/day2/baseline/MH02/run4/f_MH02_seconds.txt")
truth, guess = sync.associate_trajectories(truth, guess)
guess.align(truth, correct_scale=False)
P, G = truth.positions_xyz, guess.positions_xyz
first_photo = int(open(f"{home}/ORB_SLAM3/Examples/Stereo-Inertial/EuRoC_TimeStamps/MH02.txt").readline().split()[0]) / 1e9
t = guess.timestamps - first_photo                    # seconds since the flight's first photo, like the other charts
gap = np.linalg.norm(G - P, axis=1) * 100
step = np.linalg.norm(np.diff(G, axis=0), axis=1) * 100
k = int(np.argmax(step))
fig, (a1, a2) = plt.subplots(1, 2, figsize=(14, 6), gridspec_kw={"width_ratios": [1.1, 1]})
a1.plot(P[:, 0], P[:, 1], color="#a8a7a2", lw=4, label="Where the drone really flew")
a1.plot(G[:, 0], G[:, 1], color=NORMAL, lw=1.3, label="Where ORB-SLAM3 thought it was")
a1.plot([G[k, 0], G[k + 1, 0]], [G[k, 1], G[k + 1, 1]], color=PAPERC, lw=4, zorder=5)
a1.annotate(f"jumped {step[k]:.0f} cm between\ntwo photos at {t[k]:.1f} s", G[k, :2], xytext=(40, 40), textcoords="offset points",
            fontsize=11, color=INK, fontweight="bold", arrowprops=dict(arrowstyle="->", color=PAPERC, lw=1.5))
a1.set_aspect("equal", adjustable="datalim"); a1.set_xlabel("meters"); a1.set_ylabel("meters")
a1.set_title("The run where ORB-SLAM3 teleported"); a1.legend(loc="lower left", fontsize=10, framealpha=0.95)
a2.plot(t[1:], step, color=NORMAL, lw=1)
a2.set_yscale("log"); a2.set_ylim(0.1, 200)
a2.annotate(f"{step[k]:.0f} cm in one step\n(normal step: {np.median(step):.1f} cm)\nno warning printed", (t[k + 1], step[k]),
            xytext=(-170, -10), textcoords="offset points", fontsize=11, color=INK, fontweight="bold",
            arrowprops=dict(arrowstyle="->", color=PAPERC, lw=1.5))
a2.set_xlabel("seconds into the flight"); a2.set_ylabel("how far the guess moved between photos (cm, log scale)")
a2.set_title("How far the guess moved, photo to photo")
fig.suptitle(f"MH02 (easy), one of ~80 runs: score {np.sqrt(np.mean(gap ** 2)):.0f} cm instead of the usual 2-3 cm",
             fontsize=15, fontweight="bold", color=INK, x=0.125, ha="left", y=1.0)
fig.savefig(f"{out}/silent_jump.png", dpi=110, bbox_inches="tight"); plt.close(fig)
print("saved 4 charts to", out)
