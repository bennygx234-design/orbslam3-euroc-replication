#!/bin/bash
# One Day 2 run: pick a version of ORB-SLAM3 (the original, or one with a fix), run one flight,
# convert the times, and score it with evo. Same steps as run_flight.sh.
# Usage: run_variant.sh <version> <flight folder> <short name> <run number>
#   versions: baseline     original program and settings
#             clahe        fix 1: contrast boost on every photo
#             corners2000  fix 2: 2000 corners per photo instead of 1200
#             imu_more     fix 4a: trust the motion sensor more
#             imu_less     fix 4b: trust the motion sensor less
#             combined     the winning fixes together (program and settings named in configs/combined.env)
#             any other    defined by configs/versions/<version>.env (sets PROG, YAML and photo-cleanup settings)
#   e.g. run_variant.sh clahe MH_04_difficult MH04 1
set -e
ORB=$HOME/tks-slam/ORB_SLAM3
CFG=$HOME/tks-slam/configs
export LD_LIBRARY_PATH=$HOME/tks-slam/local/lib:$ORB/lib:$ORB/Thirdparty/DBoW2/lib:$ORB/Thirdparty/g2o/lib
VERSION=$1; FLIGHT=$2; SHORT=$3; RUN=$4

PROG=$ORB/Examples/Stereo-Inertial/stereo_inertial_euroc
YAML=$ORB/Examples/Stereo-Inertial/EuRoC.yaml
case $VERSION in
  baseline)    ;;
  clahe)       PROG=${PROG}_clahe ;;
  corners2000) YAML=$CFG/EuRoC_corners2000.yaml ;;
  imu_more)    YAML=$CFG/EuRoC_imu_trust_more.yaml ;;
  imu_less)    YAML=$CFG/EuRoC_imu_trust_less.yaml ;;
  combined)    source $CFG/combined.env ;;          # sets PROG and YAML
  *)           [ -f $CFG/versions/$VERSION.env ] || { echo "unknown version: $VERSION"; exit 1; }
               source $CFG/versions/$VERSION.env ;;
esac

DATA=$HOME/tks-slam/datasets/euroc/$FLIGHT
OUT=${OUTROOT:-$HOME/tks-slam/results/day2}/$VERSION/$SHORT/run$RUN    # OUTROOT lets the final check keep its runs separate
mkdir -p "$OUT" && cd "$OUT"
echo "$PROG $YAML clip=${TKS_CLAHE_CLIP:-} gamma=${TKS_GAMMA:-} dark=${TKS_DARK:-}" > version_used.txt
$PROG $ORB/Vocabulary/ORBvoc.txt $YAML "$DATA" $ORB/Examples/Stereo-Inertial/EuRoC_TimeStamps/$SHORT.txt $SHORT > orbslam3_log.txt 2>&1 \
  || echo "note: $VERSION $SHORT run $RUN exited with an error code"
[ -s f_$SHORT.txt ] || { echo "$VERSION $SHORT run $RUN FAILED: no path saved"; exit 1; }
python3 $HOME/tks-slam/scripts/convert_timestamps.py f_$SHORT.txt f_${SHORT}_seconds.txt > /dev/null
$HOME/.local/bin/evo_ape euroc "$DATA/mav0/state_groundtruth_estimate0/data.csv" f_${SHORT}_seconds.txt --align --save_results ape_results.zip > evo_score.txt 2>&1
echo "$VERSION $SHORT run $RUN: $(awk '$1=="rmse"{printf "%.2f cm", $2*100}' evo_score.txt)"
