# Numbers, chart data and plain photos for the rewritten article. Run inside Ubuntu with evo's python.
# Writes CSV files for the charts and two photos with no words baked in, and prints every number the text uses.
# Usage: article_assets.py <output folder>
import glob, os, re, sys
from math import comb
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from evo.tools import file_interface
from evo.core import sync

out = sys.argv[1]
os.makedirs(out, exist_ok=True)
home = os.path.expanduser("~/tks-slam")
FOLDERS = {"MH01": "MH_01_easy", "MH02": "MH_02_easy", "MH03": "MH_03_medium", "MH04": "MH_04_difficult", "MH05": "MH_05_difficult"}

def rmse(f):
    for line in open(f):
        if line.split() and line.split()[0] == "rmse":
            return float(line.split()[1]) * 100

def scores(root, version, fl):
    # Keyed by run number so two versions pair up correctly
    r = {}
    for f in glob.glob(f"{home}/results/{root}/{version}/{fl}/run*/evo_score.txt"):
        r[int(re.search(r"run(\d+)", f).group(1))] = rmse(f)
    return r

print("== final check, middle of 10 and wins")
total = 0
for fl in FOLDERS:
    a, b = scores("final", "baseline", fl), scores("final", "corners2000", fl)
    wins = sum(b[k] < a[k] for k in a)
    total += wins
    print(fl, f"normal {np.median(list(a.values())):.2f} ({min(a.values()):.2f}-{max(a.values()):.2f})  2000 {np.median(list(b.values())):.2f} ({min(b.values()):.2f}-{max(b.values()):.2f})  wins {wins}/{len(a)}")
print("total wins", total, "luck odds 1 in", round(2**50 / sum(comb(50, k) for k in range(total, 51))))

print("== day 2, middle of 5 per version")
for v in ["baseline", "clahe", "imu_more", "imu_less", "clahe_v2", "gamma_dark", "corners2000", "corners2500", "corners3000"]:
    print(v, " ".join(f"{fl} {np.median(list(scores('day2', v, fl).values())):.2f}" for fl in ["MH04", "MH05"]))

print("== silent jumps over 20 cm, every run ever made")
paths = sorted(glob.glob(f"{home}/results/*/*/*/run*/f_*_seconds.txt") + glob.glob(f"{home}/results/stereo*/*/run*/f_*_seconds.txt"))
real = {os.path.realpath(p) for p in paths}
late = []
for p in sorted(real):
    g = file_interface.read_tum_trajectory_file(p)
    step = np.linalg.norm(np.diff(g.positions_xyz, axis=0), axis=1) * 100
    k = int(np.argmax(step))
    if step[k] > 20:
        late.append((p.split("results/")[1], round(step[k], 1), round(g.timestamps[k] - g.timestamps[0], 1)))
print("runs checked", len(real)); print(*late, sep="\n")

def aligned(path, fl):
    truth = file_interface.read_euroc_csv_trajectory(f"{home}/datasets/euroc/{FOLDERS[fl]}/mav0/state_groundtruth_estimate0/data.csv")
    guess = file_interface.read_tum_trajectory_file(path)
    truth, guess = sync.associate_trajectories(truth, guess)
    guess.align(truth, correct_scale=False)
    return truth, guess

def first_photo(fl):
    return int(open(f"{home}/ORB_SLAM3/Examples/Stereo-Inertial/EuRoC_TimeStamps/{fl}.txt").readline().split()[0]) / 1e9

# Map of Flight 5, one normal run, gap drawn 10 times bigger
truth, guess = aligned(f"{home}/results/stereo_inertial/MH05/run1/f_MH05_seconds.txt", "MH05")
P, G = truth.positions_xyz, guess.positions_xyz
S = P + 10 * (G - P)
with open(f"{out}/flight5_map.csv", "w") as f:
    f.write("x,y,gx,gy\n")
    for i in range(0, len(P), 5):
        f.write(f"{P[i,0]:.2f},{P[i,1]:.2f},{S[i,0]:.2f},{S[i,1]:.2f}\n")

# Flight 5 gap over time, with and without the motion sensor, twice a second
t0 = first_photo("MH05")
gaps = {}
with open(f"{out}/flight5_gap.csv", "w") as f:
    f.write("series,t,gap\n")
    for name, root in [("with", "stereo_inertial"), ("without", "stereo")]:
        tr, gu = aligned(f"{home}/results/{root}/MH05/run1/f_MH05_seconds.txt", "MH05")
        e = np.linalg.norm(gu.positions_xyz - tr.positions_xyz, axis=1) * 100
        t = gu.timestamps - t0
        gaps[name] = (t, e)
        for i in range(0, len(t), 10):
            f.write(f"{name},{t[i]:.1f},{e[i]:.1f}\n")
imu = np.loadtxt(f"{home}/datasets/euroc/MH_05_difficult/mav0/imu0/data.csv", delimiter=",", comments="#")
turn = np.convolve(np.degrees(np.linalg.norm(imu[:, 1:4], axis=1)), np.ones(50) / 50, mode="same")
timu = imu[:, 0] / 1e9 - t0
k = int(np.argmax(turn[100:-100])) + 100
print(f"== fastest turn on Flight 5: {turn[k]:.0f} deg/s at {timu[k]:.1f} s")
for name, (t, e) in gaps.items():
    w = (t > 55) & (t < 65)
    print(name, f"first position {t[0]:.1f} s, gap 55-65 s: max {e[w].max():.1f}, avg {e[w].mean():.1f} cm")

# Flight 2, the run with the silent jump: how far the guess moved between photos
g = file_interface.read_tum_trajectory_file(f"{home}/results/day2/baseline/MH02/run4/f_MH02_seconds.txt")
step = np.linalg.norm(np.diff(g.positions_xyz, axis=0), axis=1) * 100
t = g.timestamps[1:] - first_photo("MH02")
k = int(np.argmax(step))
keep = sorted(set(range(0, len(step), 3)) | {k - 1, k, k + 1})
with open(f"{out}/flight2_jump.csv", "w") as f:
    f.write("t,step\n")
    for i in keep:
        f.write(f"{t[i]:.2f},{step[i]:.2f}\n")
print(f"== jump {step[k]:.1f} cm at {t[k]:.1f} s; normal step {np.median(step):.1f} cm; score {rmse(home + '/results/day2/baseline/MH02/run4/evo_score.txt'):.1f} cm")

# Photos with no words on them
def corner_photo(img, corners, ax, size=2.5):
    ax.imshow(img, cmap="gray", vmin=0, vmax=1)
    for x, y, lvl in corners[:, :3]:
        ax.add_patch(Circle((x, y), size * 1.2 ** lvl, fill=False, ec="#ffd21f", lw=0.9))
    ax.set_axis_off()

c = f"{home}/results/what_camera_sees"
img = plt.imread(f"{c}/rect_left.png")
cs = np.loadtxt(f"{c}/corners_left.txt")
fig = plt.figure(figsize=(9.4, 6.0), dpi=120)
ax = fig.add_axes([0, 0, 1, 1])
corner_photo(img, cs, ax)
fig.savefig(f"{out}/corners_photo.png")
plt.close(fig)
print("== corners in the example photo:", len(cs))

d = f"{home}/results/visuals/dark"
fig = plt.figure(figsize=(12, 3.84), dpi=120)
a1 = fig.add_axes([0, 0, 0.495, 1]); a2 = fig.add_axes([0.505, 0, 0.495, 1])
n, b = np.loadtxt(f"{d}/corners_normal.txt"), np.loadtxt(f"{d}/corners_boosted.txt")
corner_photo(plt.imread(f"{d}/photo.png"), n, a1)
corner_photo(plt.imread(f"{d}/photo_boosted.png"), b, a2)
fig.savefig(f"{out}/dark_compare.png")
plt.close(fig)
print("wrote", os.listdir(out))
