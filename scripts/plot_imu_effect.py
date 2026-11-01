# What the motion sensor (IMU) did on one flight.
#   Top:    how far off ORB-SLAM3 was with the motion sensor (camera + IMU) and without it (camera only).
#           Orange shading = how much the motion sensor helped at that moment.
#   Bottom: how fast the drone was turning, straight from the motion sensor's spin reading.
# Usage: plot_imu_effect.py <flight folder> <short name>
import sys, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from evo.tools import file_interface
from evo.core import sync

flight, short = sys.argv[1], sys.argv[2]
home = os.path.expanduser("~/tks-slam")
gt_path = f"{home}/datasets/euroc/{flight}/mav0/state_groundtruth_estimate0/data.csv"
photo_list = f"{home}/ORB_SLAM3/Examples/Stereo-Inertial/EuRoC_TimeStamps/{short}.txt"
WITH, WITHOUT, TURN, INK, MUTED, BG = "#2a78d6", "#eb6834", "#8a8985", "#0b0b0b", "#52514e", "#fcfcfb"
plt.rcParams.update({"axes.edgecolor": "#c3c2b7", "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED,
                     "axes.grid": True, "grid.color": "#ebeae6", "font.size": 12, "axes.titlesize": 15,
                     "axes.titleweight": "bold", "axes.titlelocation": "left"})

t0 = int(open(photo_list).readline().split()[0]) / 1e9          # clock starts at the first photo
t_end = sum(1 for line in open(photo_list) if line.strip()) / 20.0

def gaps(mode):
    """Gap (cm) between ORB-SLAM3's guess and the true path at every scored moment, plus the score."""
    truth = file_interface.read_euroc_csv_trajectory(gt_path)
    guess = file_interface.read_tum_trajectory_file(f"{home}/results/{mode}/{short}/run1/f_{short}_seconds.txt")
    truth, guess = sync.associate_trajectories(truth, guess)
    guess.align(truth, correct_scale=False)
    err = np.linalg.norm(guess.positions_xyz - truth.positions_xyz, axis=1) * 100
    return truth.timestamps - t0, err, np.sqrt(np.mean(err ** 2))

def broken(t, y):
    """Break the line wherever ORB-SLAM3 gave no position for over half a second (lost or restarting)."""
    jumps = np.where(np.diff(t) > 0.5)[0] + 1
    return np.insert(t, jumps, np.nan), np.insert(y, jumps, np.nan)

t_i, e_i, s_i = gaps("stereo_inertial")
t_c, e_c, s_c = gaps("stereo")

# Camera-only gap at the same instants as the with-sensor gap (only where both had a position)
k = np.clip(np.searchsorted(t_c, t_i), 1, len(t_c) - 1)
both = np.minimum(abs(t_c[k] - t_i), abs(t_c[k - 1] - t_i)) < 0.2
e_c_same = np.interp(t_i, t_c, e_c)

# Turning speed from the motion sensor's gyro (200 readings a second), smoothed over a quarter second
imu = np.loadtxt(f"{home}/datasets/euroc/{flight}/mav0/imu0/data.csv", delimiter=",", comments="#")
t_imu = imu[:, 0] / 1e9 - t0
turn = np.convolve(np.degrees(np.linalg.norm(imu[:, 1:4], axis=1)), np.ones(50) / 50, mode="same")

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13, 11), sharex=True, facecolor=BG,
                               gridspec_kw={"height_ratios": [1.6, 1], "hspace": 0.25})
for a in (ax1, ax2):
    a.set_facecolor(BG)

ax1.fill_between(t_i, e_i, e_c_same, where=both & (e_c_same > e_i), color=WITHOUT, alpha=0.2, lw=0,
                 label="How much the motion sensor helped")
ax1.fill_between(t_i, e_i, e_c_same, where=both & (e_c_same < e_i), color=WITH, alpha=0.2, lw=0,
                 label="Camera alone did better here")
ax1.plot(*broken(t_c, e_c), color=WITHOUT, lw=1.4, label=f"Camera only (motion sensor off)   score {s_c:.2f} cm")
ax1.plot(*broken(t_i, e_i), color=WITH, lw=1.4, label=f"Camera + motion sensor   score {s_i:.2f} cm")
ax1.set_ylim(0, max(e_c.max(), e_i.max()) * 1.12)
ax1.set_ylabel("off by (cm)")
ax1.set_title("1.  How far off ORB-SLAM3 was, with and without the motion sensor", pad=12)
handles, labels = ax1.get_legend_handles_labels()
order = [3, 2, 0, 1]
ax1.legend([handles[i] for i in order], [labels[i] for i in order], loc="upper left", fontsize=11, framealpha=0.95)

ax2.fill_between(t_imu, turn, color=TURN, alpha=0.35, lw=0)
ax2.plot(t_imu, turn, color=TURN, lw=1)
ax2.set_ylim(0, turn.max() * 1.1)
ax2.set_ylabel("degrees per second")
ax2.set_xlabel("seconds into the flight")
ax2.set_xlim(0, t_end)
ax2.set_title("2.  How fast the drone was turning (the motion sensor's own spin reading)", pad=12)
ax2.text(0, -0.3, "Fast turns blur the photos and make every corner jump far between photos. "
         "Lines stop where ORB-SLAM3 had no position (still starting up, or lost).",
         transform=ax2.transAxes, fontsize=10.5, color=MUTED)

fig.suptitle(f"{flight}: what the motion sensor did", fontsize=18, fontweight="bold", color=INK, x=0.125, ha="left", y=0.96)
out = f"{home}/results/stereo/{short}/run1/{short}_imu_effect.png"
fig.savefig(out, dpi=100, bbox_inches="tight", facecolor=BG)
helped = np.mean(e_c_same[both] > e_i[both]) * 100
print(out, f"with {s_i:.2f} cm, camera-only {s_c:.2f} cm, sensor helped {helped:.0f}% of shared moments, "
           f"camera-only scored {len(e_c)} moments vs {len(e_i)}")
