#!/bin/bash
# Final check: normal ORB-SLAM3 vs Benny's version (2000 corners per photo), head to head.
# 10 runs each on all 5 Machine Hall flights, like the paper's median of 10.
# Fresh runs (none were used to pick the winner). One run at a time, nothing else running.
# Each round alternates which version goes first, so both get the same PC conditions.
export OUTROOT=$HOME/tks-slam/results/final
R=$HOME/tks-slam/scripts/run_variant.sh
FLIGHTS="MH_01_easy:MH01 MH_02_easy:MH02 MH_03_medium:MH03 MH_04_difficult:MH04 MH_05_difficult:MH05"
for run in 1 2 3 4 5 6 7 8 9 10; do
  if [ $((run % 2)) = 1 ]; then ORDER="baseline corners2000"; else ORDER="corners2000 baseline"; fi
  for f in $FLIGHTS; do
    for v in $ORDER; do $R $v ${f%%:*} ${f##*:} $run || echo "$v ${f##*:} run $run FAILED"; done
  done
done
echo "FINAL CHECK DONE"
