#!/bin/bash
# Day 2 refinement round 2: push the one helpful fix further (2500 and 3000 corners per photo),
# on the dark, difficult flights. Starts by itself after the earlier queues, so runs never overlap.
sleep 60
while pgrep -f "day2_tests.sh|day2_refine1.sh|day2_reorder.sh" > /dev/null; do sleep 20; done
R=$HOME/tks-slam/scripts/run_variant.sh
for run in 1 2 3 4 5; do
  for v in corners2500 corners3000; do
    for f in MH_04_difficult:MH04 MH_05_difficult:MH05; do $R $v ${f%%:*} ${f##*:} $run || echo "$v ${f##*:} run $run FAILED"; done
  done
done
echo "REFINE 2 DONE"
