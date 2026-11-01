#!/bin/bash
# One full camera-only (stereo, no motion sensor) run: ORB-SLAM3 guesses the path, we convert the times, evo scores it.
# Same as run_flight.sh, but uses the Stereo example instead of Stereo-Inertial.
# Usage: run_flight_stereo.sh <flight folder> <short name> [run number]
#   e.g. run_flight_stereo.sh MH_01_easy MH01 1
set -e
ORB=$HOME/tks-slam/ORB_SLAM3
export LD_LIBRARY_PATH=$HOME/tks-slam/local/lib:$ORB/lib:$ORB/Thirdparty/DBoW2/lib:$ORB/Thirdparty/g2o/lib
export DISPLAY=${DISPLAY:-:0}          # this example opens the live 3D viewer (shipped that way)
FLIGHT=$1; SHORT=$2; RUN=${3:-1}
DATA=$HOME/tks-slam/datasets/euroc/$FLIGHT
OUT=$HOME/tks-slam/results/stereo/$SHORT/run$RUN
mkdir -p "$OUT" && cd "$OUT"
# It crashes while closing the viewer, after the path is already saved, so judge success by the saved file
$ORB/Examples/Stereo/stereo_euroc $ORB/Vocabulary/ORBvoc.txt $ORB/Examples/Stereo/EuRoC.yaml "$DATA" $ORB/Examples/Stereo/EuRoC_TimeStamps/$SHORT.txt $SHORT > orbslam3_log.txt 2>&1 \
  || echo "note: ORB-SLAM3 exited with an error code while closing (path already saved)"
[ -s f_$SHORT.txt ] || { echo "$SHORT: no path saved, see orbslam3_log.txt"; exit 1; }
python3 $HOME/tks-slam/scripts/convert_timestamps.py f_$SHORT.txt f_${SHORT}_seconds.txt
$HOME/.local/bin/evo_ape euroc "$DATA/mav0/state_groundtruth_estimate0/data.csv" f_${SHORT}_seconds.txt --align --save_results ape_results.zip > evo_score.txt 2>&1
echo "$SHORT camera-only run $RUN:"; grep -E "rmse|mean|max" evo_score.txt
