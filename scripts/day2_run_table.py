# Builds a table of every Day 2 run finished so far, so we can see what went wrong or right in each one.
# For each run: score, change vs the normal version's middle score, worst slip (size and when),
# when positions started, reference photos kept, start-up retries, and the average gap in dark vs bright photos.
# Usage: day2_run_table.py <output markdown file>
import os, sys, glob, re
import numpy as np
import matplotlib.image as mpimg
from evo.tools import file_interface
from evo.core import sync

home = os.path.expanduser("~/tks-slam")
FLIGHTS = {"MH01": "MH_01_easy", "MH02": "MH_02_easy", "MH03": "MH_03_medium", "MH04": "MH_04_difficult", "MH05": "MH_05_difficult"}
ORDER = ["baseline", "clahe", "clahe_v2", "gamma_dark", "corners2000", "imu_more", "imu_less", "combined"]
NAMES = {"baseline": "normal", "clahe": "contrast boost", "clahe_v2": "contrast boost v2 (dark only, gentle)",
         "gamma_dark": "brightness curve (dark only)", "corners2000": "2000 corners",
         "imu_more": "trust motion sensor more", "imu_less": "trust motion sensor less", "combined": "combined"}

def brightness(short):
    """Average brightness (0-255) of every left photo in a flight, cached after the first time."""
    cache = f"{home}/results/day2/brightness_{short}.npy"
    if os.path.exists(cache):
        return np.load(cache)
    d = f"{home}/datasets/euroc/{FLIGHTS[short]}/mav0/cam0/data"
    names = sorted(os.listdir(d))
    out = np.array([[int(n[:-4]) / 1e9, mpimg.imread(f"{d}/{n}").mean() * 255] for n in names])
    np.save(cache, out)
    return out

def one_run(version, short, run_dir):
    truth = file_interface.read_euroc_csv_trajectory(
        f"{home}/datasets/euroc/{FLIGHTS[short]}/mav0/state_groundtruth_estimate0/data.csv")
    guess = file_interface.read_tum_trajectory_file(f"{run_dir}/f_{short}_seconds.txt")
    truth, guess = sync.associate_trajectories(truth, guess)
    guess.align(truth, correct_scale=False)
    err = np.linalg.norm(guess.positions_xyz - truth.positions_xyz, axis=1) * 100
    b = brightness(short)
    t = guess.timestamps - b[0, 0]                    # seconds since the first photo
    bright = np.interp(guess.timestamps, b[:, 0], b[:, 1])
    dark = bright < 50
    log = open(f"{run_dir}/orbslam3_log.txt", errors="ignore").read()
    kfs = re.search(r"has (\d+) KFs", log)
    w = int(np.argmax(err))
    return {
        "score": np.sqrt(np.mean(err ** 2)), "worst": err[w], "worst_t": t[w], "start": t[0],
        "kfs": int(kfs.group(1)) if kfs else 0,
        "retries": len(re.findall(r"Not enough motion|not enough acceleration", log)),
        "dark": err[dark].mean() if dark.any() else float("nan"), "bright": err[~dark].mean(),
    }

rows = []
for run_dir in glob.glob(f"{home}/results/day2/*/*/run*"):
    version, short, run = run_dir.split("/")[-3:]
    if os.path.exists(f"{run_dir}/evo_score.txt") and os.path.exists(f"{run_dir}/f_{short}_seconds.txt"):
        rows.append((version, short, int(run[3:]), one_run(version, short, run_dir)))
for version in sorted({r[0] for r in rows}):         # versions added later go at the end, named as-is
    if version not in ORDER:
        ORDER.append(version)
        NAMES[version] = version
rows.sort(key=lambda r: (r[1], ORDER.index(r[0]), r[2]))

normal_mid = {}
for s in FLIGHTS:
    scores = [r[3]["score"] for r in rows if r[0] == "baseline" and r[1] == s]
    if scores:
        normal_mid[s] = float(np.median(scores))

lines = ["# Day 2 run table (made automatically by `day2_run_table.py`)", "",
         "Score = RMS gap over the flight. 'vs normal' compares with the middle (median) score of the normal version's runs so far on that flight.",
         "Dark = photos with average brightness under 50 (out of 255). Gaps in cm, times in seconds since the first photo.", "",
         "| Flight | Version | Run | Score | vs normal | Worst slip | Positions from | Ref. photos | Start-up retries | Avg gap dark | Avg gap bright |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
for version, short, run, r in rows:
    vs = f"{r['score'] - normal_mid[short]:+.2f}" if short in normal_mid else "-"
    lines.append(f"| {short} | {NAMES[version]} | {run} | {r['score']:.2f} | {vs} | {r['worst']:.1f} @ {r['worst_t']:.0f} s | "
                 f"{r['start']:.1f} s | {r['kfs']} | {r['retries']} | {r['dark']:.1f} | {r['bright']:.1f} |")

used = [v for v in ORDER if any(r[0] == v for r in rows)]
lines += ["", "## Middle (median) score per version so far", "", "| Flight | " + " | ".join(NAMES[v] for v in used) + " |",
          "|---|" + "---|" * len(used)]
for s in FLIGHTS:
    cells = []
    for v in used:
        sc = [r[3]["score"] for r in rows if r[0] == v and r[1] == s]
        cells.append(f"{np.median(sc):.2f} ({len(sc)} runs)" if sc else "-")
    if any(c != "-" for c in cells):
        lines.append(f"| {s} | " + " | ".join(cells) + " |")

open(sys.argv[1], "w").write("\n".join(lines) + "\n")
print("\n".join(lines))
