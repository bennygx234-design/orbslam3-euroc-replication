#!/bin/bash
# Makes all the article visuals once the final check has finished (never while ORB-SLAM3 is running).
set -e
ORB=$HOME/tks-slam/ORB_SLAM3
PY=$HOME/.local/share/pipx/venvs/evo/bin/python
VIS=$HOME/tks-slam/results/visuals
mkdir -p $VIS/dark
pgrep -f "stereo_inertial_euroc" > /dev/null && { echo "ORB-SLAM3 is still running, not making visuals"; exit 1; }

# 1. Pick a dark (not pitch-black) MH05 photo from mid-flight: brightness closest to 30, between 20 s and 100 s
read NAME WHEN LEVEL < <($PY - <<'PY'
import numpy as np, os
b = np.load(os.path.expanduser("~/tks-slam/results/day2/brightness_MH05.npy"))
t = b[:, 0] - b[0, 0]
ok = np.where((t > 20) & (t < 100))[0]
i = ok[np.argmin(abs(b[ok, 1] - 30))]
print(f"{int(round(b[i, 0] * 1e9))}.png {t[i]:.1f} {b[i, 1]:.1f}")
PY
)
PHOTO=$(ls $HOME/tks-slam/datasets/euroc/MH_05_difficult/mav0/cam0/data/ | grep "^${NAME:0:13}" | head -1)
echo "dark photo: $PHOTO ($WHEN s, brightness $LEVEL)"

# 2. Corners in that photo: normal, 2000, contrast boost
g++ -std=c++17 -O2 $HOME/tks-slam/scripts/dark_corners.cc $ORB/src/ORBextractor.cc -I$ORB/include \
    $(pkg-config --cflags --libs opencv4) -o $HOME/tks-slam/scripts/dark_corners
$HOME/tks-slam/scripts/dark_corners $ORB/Examples/Stereo-Inertial/EuRoC.yaml \
    $HOME/tks-slam/datasets/euroc/MH_05_difficult/mav0/cam0/data/$PHOTO $VIS/dark
$PY $HOME/tks-slam/scripts/plot_dark_corners.py $VIS/dark $WHEN $LEVEL 2>&1 | grep -v Warning
cp $VIS/dark/dark_corners.png $VIS/

# 3. The other four charts
$PY $HOME/tks-slam/scripts/make_visuals.py $VIS 2>&1 | grep -v Warning
echo "VISUALS DONE"
