#!/bin/bash
# Day 2 refinement round 1: two gentler photo-cleanup versions on the dark, difficult flights.
# Starts by itself once the first test queue (day2_tests.sh) has finished, so runs never overlap.
while pgrep -f day2_tests.sh > /dev/null; do sleep 20; done
R=$HOME/tks-slam/scripts/run_variant.sh
for run in 1 2 3 4 5; do
  for v in clahe_v2 gamma_dark; do
    for f in MH_04_difficult:MH04 MH_05_difficult:MH05; do $R $v ${f%%:*} ${f##*:} $run || echo "$v ${f##*:} run $run FAILED"; done
  done
done
echo "REFINE 1 DONE"
