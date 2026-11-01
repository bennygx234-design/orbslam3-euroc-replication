#!/bin/bash
# One full stereo-inertial run: ORB-SLAM3 guesses the path, we convert the times, evo scores it.
# Usage: run_flight.sh <flight folder> <short name> [run number]
#   e.g. run_flight.sh MH_01_easy MH01 1
set -e
ORB=$HOME/tks-slam/ORB_SLAM3
export LD_LIBRARY_PATH=$HOME/tks-slam/local/lib:$ORB/lib:$ORB/Thirdparty/DBoW2/lib:$ORB/Thirdparty/g2o/lib
FLIGHT=$1; SHORT=$2; RUN=${3:-1}
DATA=$HOME/tks-slam/datasets/euroc/$FLIGHT
OUT=$HOME/tks-slam/results/stereo_inertial/$SHORT/run$RUN
mkdir -p "$OUT" && cd "$OUT"

# 1. ORB-SLAM3 replays the flight and saves its guessed path as f_<short>.txt
$ORB/Examples/Stereo-Inertial/stereo_inertial_euroc \
  $ORB/Vocabulary/ORBvoc.txt $ORB/Examples/Stereo-Inertial/EuRoC.yaml \
  "$DATA" $ORB/Examples/Stereo-Inertial/EuRoC_TimeStamps/$SHORT.txt $SHORT > orbslam3_log.txt 2>&1

# 2. Nanoseconds to seconds so evo can pair up the moments
python3 $HOME/tks-slam/scripts/convert_timestamps.py f_$SHORT.txt f_${SHORT}_seconds.txt

# 3. evo lines the guess up with the true path (move + rotate only) and measures the gap
$HOME/.local/bin/evo_ape euroc "$DATA/mav0/state_groundtruth_estimate0/data.csv" f_${SHORT}_seconds.txt \
  --align --save_results ape_results.zip > evo_score.txt 2>&1
echo "$SHORT run $RUN:"; grep -E "rmse|mean|max" evo_score.txt
