# Testing ORB-SLAM3 on the EuRoC Machine Hall flights

This is the code and data from my TKS build project. I ran ORB-SLAM3 on the 5 EuRoC Machine Hall drone flights to see if I could match the accuracy in the paper, then tested 8 changes to see if any of them made it better.

ORB-SLAM3 is a free program that works out where a camera is as it moves, using only the video and, if you want, a motion sensor. EuRoC is a public set of real drone flights recorded by ETH Zurich, where a separate system measured where the drone really was. That lets you score the guess in centimeters.

## What I found

All scores are in centimeters of error, and lower is better. "Normal" is the official ORB-SLAM3 with its own settings. "2000 corners" is the only change I kept: it looks for 2,000 corners per photo instead of 1,200, which is one line in the settings file. Both columns are the middle score of 10 fresh runs, using two cameras plus the motion sensor. The paper's numbers are also the middle of 10 runs.

| Flight | Difficulty | Paper | Normal | 2000 corners | Change vs normal |
|---|---|---|---|---|---|
| MH01 | easy | 3.6 | 3.81 | 3.47 | 9% better |
| MH02 | easy | 3.3 | 3.59 | 2.98 | 17% better |
| MH03 | medium | 3.5 | 3.27 | 2.76 | 16% better |
| MH04 | difficult | 5.1 | 4.24 | 4.16 | 2% better |
| MH05 | difficult | 8.2 | 5.33 | 5.11 | 4% better |

- **I got close to the paper.** Normal ORB-SLAM3 on my PC came within 0.3 cm of the paper on the two easy flights and beat it on the other three.
- **2000 corners won.** Out of 100 fresh runs, it won 37 of the 50 head-to-head matchups. The odds of that by luck are about 1 in 2,100. It was about 10% better on average and better than the paper on all 5 flights.
- **It kept up with the flight.** Whole runs took about the same time for both versions (for example, MH04 took 109.6 s normal and 109.7 s with 2000 corners). The program waits on purpose to stay at 20 photos a second and never prints the time per photo, so this only shows that both kept up. It does not measure how much harder the computer worked.
- **Most changes did not help.** I tested 8 changes, 5 runs each on MH04 and MH05: contrast boost (worse), trusting the motion sensor more (much worse), trusting it less (even), a gentler contrast boost (not a win), a brightness curve (mixed), 2000 corners (better on both), and 2500 and 3000 corners (mixed).
- **The gains showed up in a surprising place.** The biggest gains were on the easy flights I never tuned on. On the dark flights I picked it on, the gain shrank in the final test, which is a classic sign that part of a tuning gain was luck.
- **ORB-SLAM3 can fail silently.** In 1 of 210 runs it jumped 87 cm in one step in the middle of a flight (MH02, 79.3 s) and gave no warning.
- **Darkness matters, but how much depends on the flight.** This is the average gap in dark vs bright photos during slow turns, from one run each. MH05: 8.4 vs 4.5 cm with cameras only, 5.1 vs 3.6 with the motion sensor. MH04: 6.0 vs 4.7, and 3.9 vs 3.3. MH03: 3.9 vs 4.7, and 4.1 vs 2.9, with only 3% of moments dark.

**Limits.** The comparison with the paper mixes a newer code version (1.0, commit `4452a3c`, which came after the paper) and a different computer, so I can't say how much of the difference comes from either one. I only used the Machine Hall flights, not the other EuRoC flights.

## What's in each folder

| Path | What it is |
|---|---|
| `scripts/` | Everything I used to run flights, score them and draw charts |
| `day2/configs/` | Settings files for the versions I tested, each a copy of the official `EuRoC.yaml` with only a few lines changed |
| `day2/stereo_inertial_euroc_clahe.cc` | The official EuRoC example program plus a contrast boost |
| `day2/stereo_inertial_euroc_tks.cc` | The same idea with adjustable photo cleanup |
| `day2/cmakelists-day2.patch` | Adds the contrast boost program to the official build |
| `docs/orbslam3-code-changes.patch` | The 4 fixes I needed to get the official code to build. None of them change how it tracks |
| `day2/run-notes.md` | My notes on each run, written as I went |
| `day2/run-table.md` | A table of the day 2 runs, made by `scripts/day2_run_table.py` |
| `day2/final-check-log.md` | The final 100 runs, one line each |
| `results/final/` | The score from each of the 100 final runs, plus `final_check.log` |
| `results/stereo/` | My first runs with cameras only: score, log and guessed paths |
| `results/stereo_inertial/` | My first runs with cameras and the motion sensor: score, log and guessed paths |
| `article/assets/` | The data behind three charts in my write-up |
| `LICENSE` | GPLv3 |

**A note on `day2/run-notes.md`.** It's a log, so older entries show what I thought at the time, including a stronger claim about speed and a higher rate for the silent jump. The findings above replace those: 2000 corners kept up, and the jump happened in 1 of 210 runs.

## What is not in here

The flights, the full ORB-SLAM3 code, its word list (`ORBvoc.txt`), Pangolin and compiled programs are not here. Get them from the original sources below. The 100 guessed paths from the final check and the full day 2 run folders stayed on my PC, so the scripts that read them won't work from this repo alone.

## How to repeat it

**Setup note:** the scripts have these locations written into them, so they expect everything to be in `~/tks-slam` and the scoring tool to be at `~/.local/bin/evo_ape`.

I ran this on a Windows 11 PC (AMD Ryzen 5 7600X) inside WSL2 Ubuntu 24.04, with GCC 13, OpenCV 4.6 and Eigen 3.4. ORB-SLAM3's code does no graphics card calculations, so the work ran on the processor.

1. Install the scoring tool with `pipx install evo`. That is what puts `evo_ape` in `~/.local/bin`.
2. Build [Pangolin](https://github.com/stevenlovegrove/Pangolin) v0.9.6 from source into `~/tks-slam/local`, because it isn't packaged for Ubuntu 24.04. The run scripts look for its libraries there.
3. Get the official code at the exact version I used, and apply the build fixes. Replace `<this repo>` with where you cloned this repo.
   ```bash
   git clone https://github.com/UZ-SLAMLab/ORB_SLAM3 ~/tks-slam/ORB_SLAM3
   cd ~/tks-slam/ORB_SLAM3
   git checkout 4452a3c
   git apply <this repo>/docs/orbslam3-code-changes.patch
   ./build.sh
   ```
4. Download the Machine Hall flights (12.1 GB) from [ETH Zurich](https://doi.org/10.3929/ethz-b-000690084) and unzip them so that you have folders like `~/tks-slam/datasets/euroc/MH_01_easy/mav0`.
5. Copy in my scripts and settings.
   ```bash
   mkdir -p ~/tks-slam/scripts ~/tks-slam/configs
   cp <this repo>/scripts/* ~/tks-slam/scripts/
   cp <this repo>/day2/configs/*.yaml ~/tks-slam/configs/
   chmod +x ~/tks-slam/scripts/*.sh
   ```
6. Run a flight. The last number is the run number. Results go to `~/tks-slam/results/day2/`.
   ```bash
   ~/tks-slam/scripts/run_variant.sh baseline MH_04_difficult MH04 1      # normal ORB-SLAM3
   ~/tks-slam/scripts/run_variant.sh corners2000 MH_04_difficult MH04 1   # 2000 corners
   ```
   Each run takes about as long as the flight, so MH04 takes about 110 seconds. Run one at a time, because two at once compete for the processor and skew the results. `scripts/final_check.sh` runs the whole final test: both versions, 10 runs each, all 5 flights.

To redraw the charts from the saved results in this repo, install matplotlib and run `python scripts/article_figures.py` from the top folder of this repo after creating `article/figures/`.

**What I haven't tested.** The patch applies cleanly to commit `4452a3c`, but I haven't done a fresh build by following these exact steps.

**Other versions.** `baseline`, `corners2000`, `imu_more` and `imu_less` work with the steps above. These need more:

- `clahe` needs the contrast boost program. Copy it to `Examples/Stereo-Inertial/`, and add its build target from `day2/cmakelists-day2.patch`. That patch also contains the C++17 change, so it won't apply on top of the build fixes. Apply it first, then apply the build fixes with `git apply --exclude=CMakeLists.txt`.
- `clahe_v2`, `gamma_dark`, `corners2500` and `corners3000` were defined in small settings files that aren't in this repo, so `run_variant.sh` will say "unknown version". The settings are described in `day2/run-notes.md`.
- `day2/stereo_inertial_euroc_tks.cc` has no build target in the patch, so you'd need to add one yourself.

## Credit

- **ORB-SLAM3** is by Carlos Campos, Richard Elvira, Juan J. Gómez Rodríguez, José M. M. Montiel and Juan D. Tardós at the University of Zaragoza. [Code](https://github.com/UZ-SLAMLab/ORB_SLAM3), [paper](https://arxiv.org/abs/2007.11898).
- **The EuRoC flights** were recorded by ETH Zurich. [Dataset record](https://doi.org/10.3929/ethz-b-000690084).

## License

ORB-SLAM3 is under GPLv3 and some of this code is built directly from it, so this repo is under GPLv3 too. See `LICENSE`. That covers my code. I haven't confirmed the license for the EuRoC flights, so they aren't copied here. A few files here contain numbers worked out from them, such as `article/assets/flight5_map.csv`.
