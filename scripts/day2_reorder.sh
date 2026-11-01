#!/bin/bash
# Moves the refined photo-cleanup tests ahead of the extra normal runs on the easy flights.
# 1. Waits until the first queue finishes its fix tests ("PART 1 DONE"), then stops that queue
#    before its easy-flight part, and removes the one easy-flight run it had just started.
# 2. The refinement queue (day2_refine1.sh) then starts by itself.
# 3. After the refinement queue finishes, runs the postponed easy-flight normal runs.
until grep -q "PART 1 DONE" ~/tks-slam/logs/day2_tests.log; do sleep 5; done
pkill -f day2_tests.sh
pkill -f "run_variant.sh baseline MH_0[123]"
pkill -f "stereo_inertial_euroc .*MH_0[123]"
sleep 3
for d in ~/tks-slam/results/day2/baseline/MH0[123]/run[2-5]; do
  [ -d "$d" ] && [ ! -f "$d/evo_score.txt" ] && rm -rf "$d" && echo "removed half-finished $d"
done
echo "EASY BASELINES POSTPONED"

sleep 30                                             # let the refinement queue start
while pgrep -f day2_refine1.sh > /dev/null; do sleep 20; done
R=$HOME/tks-slam/scripts/run_variant.sh
for run in 2 3 4 5; do
  for f in MH_01_easy:MH01 MH_02_easy:MH02 MH_03_medium:MH03; do
    $R baseline ${f%%:*} ${f##*:} $run || echo "baseline ${f##*:} run $run FAILED"
  done
done
echo "EASY BASELINES DONE"
