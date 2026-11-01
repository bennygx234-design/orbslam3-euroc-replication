#!/bin/bash
# Day 2 test queue. One run at a time (two at once would compete for the CPU and skew results).
# Rounds are interleaved (every version gets run 1, then every version gets run 2, ...)
# so a slow PC moment hits all versions equally, and early rounds already show a trend.
R=$HOME/tks-slam/scripts/run_variant.sh
HARD="MH_04_difficult:MH04 MH_05_difficult:MH05"
EASY="MH_01_easy:MH01 MH_02_easy:MH02 MH_03_medium:MH03"

# Day 1's run counts as baseline run 1
for s in MH01 MH02 MH03 MH04 MH05; do
  mkdir -p $HOME/tks-slam/results/day2/baseline/$s
  ln -sfn $HOME/tks-slam/results/stereo_inertial/$s/run1 $HOME/tks-slam/results/day2/baseline/$s/run1
done

# Part 1: each fix on its own, on the two dark, difficult flights
for run in 1 2 3 4 5; do
  for v in baseline clahe corners2000 imu_more imu_less; do
    [ $v = baseline ] && [ $run = 1 ] && continue
    for f in $HARD; do $R $v ${f%%:*} ${f##*:} $run || echo "$v ${f##*:} run $run FAILED"; done
  done
done
echo "PART 1 DONE"

# Part 2: baseline repeats on the easy and medium flights (needed for the final comparison)
for run in 2 3 4 5; do
  for f in $EASY; do $R baseline ${f%%:*} ${f##*:} $run || echo "baseline ${f##*:} run $run FAILED"; done
done
echo "ALL DONE"
