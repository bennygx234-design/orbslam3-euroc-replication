# Day 2 run notes (31 Oct 2026): what went wrong or right, run by run

Written as the runs finish, to tell the story later: how each fix did at first, what we learned, what we changed. The numbers come from `run-table.md` (rebuilt automatically after each round). "Normal" = the unchanged ORB-SLAM3 from Day 1 (MH04 4.35 cm, MH05 4.75 cm on its first run).

## Round 1 (run 1 of every version, MH04 and MH05)

**Contrast boost, MH04: 4.58 cm (normal 4.35), slightly worse.**
- Its worst slip is in the same place as normal (17.4 cm at 47 s), so the boost didn't fix the hardest moment.
- Dark moments: 4.0 cm average gap vs 3.9 normal, so no help in the dark. Bright moments: 3.9 vs 3.4, worse.
- It kept more reference photos (194 vs 164) and got going earlier (9.5 s vs 12.3 s).

**Contrast boost, MH05: 6.70 cm (normal 4.75), clearly worse.**
- Worse in both dark (7.4 vs 5.4) and bright moments (5.5 vs 3.6), so the damage isn't limited to the dark stretches.
- Nothing broke: one map, no extra "lost" messages, more reference photos (178 vs 153).
- It started producing positions much earlier (4.0 s vs 9.7 s). Those early seconds, while the motion sensor is still being calibrated, are usually the roughest, and they now count toward its score.
- Possible reasons, not yet tested:
  1. The boost stretches camera grain too, which creates fake corners and makes fingerprints less stable.
  2. Each tile of each photo is stretched on its own, so the same spot can look slightly different in the left vs right photo, and from one photo to the next.
  3. EuRoC's cameras already adjust exposure automatically, so the photos may need less help than the brightness numbers suggest.
  4. Single-run luck.

**2000 corners, MH04: 4.10 cm (normal 4.35), slightly better.**
- Better in dark moments (3.3 vs 3.9), same in bright (3.4 vs 3.4). This is the pattern we hoped the contrast boost would show.
- Worst slip in the same place as normal (18.0 cm at 47 s).

**2000 corners, MH05: 4.97 cm (normal 4.75), slightly worse.**
- Dark and bright about the same as normal (5.6 / 3.7 vs 5.4 / 3.6).
- It started later (13.8 s vs 9.7 s). Its worst slip moved to the sharpest turn (13.4 cm at 62 s), and is smaller than normal's start-up slip (15.9 cm at 10 s).
- Verdict so far: about even. Run-to-run wobble could explain the whole difference.

**What round 1 tells us:** the contrast boost, my top pick, is doing worse, not better, so far. One run each isn't enough to judge. The next 4 rounds will show whether that holds.

**Trust motion sensor more, MH04: 7.82 cm (normal 4.35). Much worse, the worst result so far.**
- Worse everywhere: dark 9.3 vs 3.9, bright 5.6 vs 3.4. Worst slip 23.7 cm at 62 s, the sharpest-turn stretch, vs 17.4 normal.
- It started very late (20.5 s vs 12.3 s). The motion-sensor setup step ("VIBA") ran 3 times, the same as normal on MH04, so the late start comes from earlier start-up retries, not that step.
- Why: we told the optimizer the motion sensor is 3x less noisy than it really is. So it believes the sensor over the cameras even when the sensor's small errors pile up, and the cameras can't pull the path back. This fits Day 1's finding that the motion sensor helps most when it backs up the cameras, not when it overrules them.

**Trust motion sensor more, MH05: 6.30 cm (normal 4.75). Worse again.**
- Worse in dark (7.1 vs 5.4) and bright (4.8 vs 3.6) moments. Worst slip 20.0 cm at 63 s, the same sharpest-turn stretch as on MH04, vs 15.9 normal.
- It started earlier this time (4.0 s vs 9.7 s), so the late start on MH04 wasn't the cause.
- Two flights in a row clearly worse, with the biggest slip during the fastest turn: over-trusting the motion sensor hurts most exactly where the cameras should be correcting it.

**Trust motion sensor less, MH04: 4.35 cm (normal 4.35). Exactly even.**
- Better in dark moments (3.3 vs 3.9), slightly worse in bright (3.7 vs 3.4). Worst slip in the same place (19.2 cm at 47 s vs 17.4).
- Leaning more on the cameras didn't hurt, unlike leaning more on the motion sensor. So the original setting is close to the right balance, maybe slightly over-trusting the motion sensor.

**Trust motion sensor less, MH05: 5.10 cm (normal 4.75), slightly worse.**
- Its worst slip is the same start-up slip as normal, at 10 s, and a bit bigger (18.1 vs 15.9 cm). It started at the same time (9.7 s).
- Slightly better in dark moments (5.1 vs 5.4), worse in bright (4.2 vs 3.6). On both flights, leaning more on the cameras helped a little in the dark and cost a little in good light.

### Round 1 summary (1 run each, MH04 / MH05, normal = 4.35 / 4.75 cm)

| Version | MH04 | MH05 | First impression |
|---|---|---|---|
| Contrast boost | 4.58 | 6.70 | Worse, even in the dark moments it was meant to fix |
| 2000 corners | **4.10** | 4.97 | About even. Helped dark moments on MH04 |
| Trust motion sensor more | 7.82 | 6.30 | Clearly worse on both, biggest slips in the fastest turn |
| Trust motion sensor less | 4.35 | 5.10 | About even |

Round 1 lesson: the two fixes that made the biggest change to how ORB-SLAM3 sees the world (brighter photos, a louder motion sensor) made it worse. The gentler ones (more corners, a slightly quieter motion sensor) are close to even. Rounds 2-5 will show which differences are real.

## Round 2

**Normal, MH04 run 2: 3.98 cm (run 1 was 4.35).** The same unchanged program on the same flight scored 0.37 cm differently. That's the run-to-run wobble, and it's about as big as the gaps between "2000 corners", "trust less" and normal in round 1. So small differences can't be trusted from one run.

**Normal, MH05 run 2: 4.63 cm (run 1 was 4.75).** Consistent with run 1. So Day 1's surprise (4.75 vs the paper's 8.2) wasn't a one-off lucky run.

**Contrast boost, MH04 run 2: 5.36 cm (normal so far 4.35 / 3.98).** Worse again, now 3 of 3 contrast-boost runs worse than normal. Dark moments 5.2 cm vs normal's 3.1-3.9: the boost is hurting the very moments it was meant to fix. It again kept more reference photos (190 vs ~165), so the boost makes ORB-SLAM3 *see* more but *track* worse. That fits the grain explanation: more corners pass the test, but more of them are grain that doesn't match reliably from photo to photo.

**Contrast boost, MH05 run 2: 5.23 cm (normal 4.75 / 4.63).** Less bad than run 1 (6.70) but still worse. 4 of 4 contrast-boost runs are now worse than normal.

**2000 corners, MH04 run 2: 4.03 cm (normal 4.35 / 3.98).** About even, the same as run 1 (4.10).

**2000 corners, MH05 run 2: 5.69 cm (normal 4.75 / 4.63).** Worse this time (run 1 was 4.97). So far, more corners doesn't help on MH05.

### Refining the contrast boost (decided after 4 of 4 contrast-boost runs came out worse)

Benny said: keep testing, keep what helps, refine what doesn't. Working theory for why the first boost failed:
1. It boosted **every** photo, including the 80%+ that were already fine, and at full strength (clip 3.0). That pumps up camera grain into fake corners.
2. CLAHE stretches each of 64 tiles **on its own**, and separately for the left and right photo. So the same spot can come out slightly different in left vs right. ORB-SLAM3 fine-tunes each left/right match by comparing small 11x11 pixel windows, which is thrown off when the two photos were stretched differently.

Two refined versions, built into one adjustable program (`day2/stereo_inertial_euroc_tks.cc`, settings in `day2/configs/versions/*.env`):
- **Contrast boost v2:** only photo pairs with average brightness under 60, half strength (clip 1.5). Fixes reason 1.
- **Brightness curve (gamma 0.6):** dark pairs only. One smooth curve over the whole photo, the same curve on both photos. Dark areas get lifted while bright ones barely change, and brighter-than order is kept everywhere. Fixes reasons 1 and 2.
Both queued for 5 runs each on MH04/MH05, starting automatically after the first test queue.

**Trust motion sensor more, MH04 run 2: 8.39 cm (run 1: 7.82, normal ~4.2).** Clearly worse again. 3 of 3 trust-more runs are now well above normal. It's the clearest result of the day so far: over-trusting the motion sensor hurts.

**Trust motion sensor more, MH05 run 2: 6.19 cm (run 1: 6.30, normal ~4.7).** 4 of 4 trust-more runs worse, and the two MH05 runs nearly identical. A clear, repeatable result.

**Trust motion sensor less, MH04 run 2: 4.34 cm (run 1: 4.35, normal 4.35 / 3.98).** Even with normal again, and very steady (4.35, 4.34).

**Trust motion sensor less, MH05 run 2: 6.59 cm (run 1: 5.10, normal 4.75 / 4.63). Worse.**
- Both trust-less MH05 runs have their worst slip at 10 s, right after the motion sensor gets set up (18.1 and 18.5 cm, vs normal's 15.9 and 12.7). Dark moments got much worse this run (8.2 vs ~5.2).
- Pattern: telling ORB-SLAM3 the motion sensor is noisier seems to hurt the start-up, when it is still estimating the sensor's built-in offsets (bias) and which way gravity points. Those estimates lean on the same noise numbers, so a "noisier" sensor gives a sloppier start that the rest of the flight inherits.

### Round 2 summary: middle score after 2 runs (cm)

| Version | MH04 | MH05 |
|---|---|---|
| Normal | 4.16 | 4.69 |
| Contrast boost | 4.97 | 5.96 |
| 2000 corners | **4.07** | 5.33 |
| Trust motion sensor more | 8.11 | 6.24 |
| Trust motion sensor less | 4.34 | 5.85 |

Round 2 lesson: on MH05, **every** change so far is worse than normal ORB-SLAM3. Only "2000 corners" on MH04 is slightly ahead, and that's within the wobble. The authors' own EuRoC settings look already close to the best, which is a real finding in itself. Rounds 3-5 and the refined photo-cleanup versions are still to come.

## Round 3

**Normal, MH04 run 3: 4.27 cm.** Normal's three MH04 runs are 4.35 / 3.98 / 4.27, a spread of 0.37 cm.

**Normal, MH05 run 3: 5.60 cm (runs 1-2: 4.75 / 4.63).** The unchanged program had a bad run too, almost 1 cm worse than its other two. So MH05's wobble is about 1 cm, much bigger than MH04's. Some MH05 results that looked "worse" for the fixes (2000 corners 4.97, trust-less 5.10) fall inside that normal range. Only clearly bigger gaps (trust-more at 6.2-6.3, contrast boost at 6.70) can be trusted as real.

**Contrast boost, MH04 run 3: 4.36 cm (runs 1-2: 4.58 / 5.36, normal 3.98-4.35).** Its best run so far, level with normal's runs. Still not better than normal.

**Contrast boost, MH05 run 3: 8.59 cm (runs 1-2: 6.70 / 5.23, normal 4.63-5.60). The worst MH05 run of the day.**
- Dark moments averaged 10.9 cm (normal ~5-6.5). Bright moments 6.7 (normal ~3.6-4.3).
- Worst slip 19.6 cm at 63 s, the fastest turn. Nothing crashed (one map, no restarts).
- 3 of 3 contrast-boost runs on MH05 are worse than every normal run. On the darkest, hardest flight, the full-strength boost clearly hurts. This is the result the refined versions have to beat.

**2000 corners, MH04 run 3: 4.08 cm (runs 1-2: 4.10 / 4.03; normal 4.35 / 3.98 / 4.27).** Very steady: 3 runs within 0.07 cm, all at or below normal's middle (4.27). The most consistent small gain so far, on MH04 only.

**2000 corners, MH05 run 3: 4.99 cm (runs 1-2: 4.97 / 5.69; normal 4.75 / 4.63 / 5.60).** Inside normal's range. On MH05, 2000 corners is about even with normal (middle 4.99 vs 4.75).

**Trust motion sensor more, MH04 run 3: 7.33 cm (runs 1-2: 7.82 / 8.39).** Still far worse than normal (~4.2). 5 of 5 trust-more runs are worse.

**Progress check (Benny asked "are we making progress"):** progress in what we've learned, not yet in the score. Clear: trusting the motion sensor more is worse (5/5), and the full contrast boost is worse on MH05 (3/3, every run worse than every normal run). Small: 2000 corners about 0.2 cm better on MH04 (4.10 / 4.03 / 4.08 vs normal's middle 4.27), even on MH05. The authors' EuRoC settings are already well tuned. To get the refined photo-cleanup answers sooner, the easy-flight normal runs were moved after them (`scripts/day2_reorder.sh`).

**Trust motion sensor more, MH05 run 3: 7.92 cm (runs 1-2: 6.30 / 6.19).** 6 of 6 worse than normal. Settled.

**Trust motion sensor less, MH04 run 3: 4.02 cm (runs 1-2: 4.35 / 4.34; normal 4.35 / 3.98 / 4.27).** Its best MH04 run. Still inside normal's range.

**Trust motion sensor less, MH05 run 3: 5.56 cm (runs 1-2: 5.10 / 6.59; normal 4.75 / 4.63 / 5.60).** At the top edge of normal's range.

### Round 3 summary: middle score after 3 runs (cm)

| Version | MH04 | MH05 |
|---|---|---|
| Normal | 4.27 | 4.75 |
| Contrast boost | 4.58 | 6.70 |
| 2000 corners | **4.08** | 4.99 |
| Trust motion sensor more | 7.82 | 6.30 |
| Trust motion sensor less | 4.34 | 5.56 |

No version beats normal on both flights yet. 2000 corners is the only one ahead (MH04, -0.19 cm, steady across all 3 runs).

## Round 4

**Normal, MH04 run 4: 4.28 cm.** Normal on MH04 so far: 4.35 / 3.98 / 4.27 / 4.28.

**Normal, MH05 run 4: 6.09 cm.** Normal on MH05 so far: 4.75 / 4.63 / 5.60 / 6.09, middle about 5.2. Day 1's 4.75 was on the lucky side of normal's range. The full set of runs will give a fairer number than one run, as the paper's median of 10 does.

**Contrast boost, MH04 run 4: 5.14 cm (runs 1-3: 4.58 / 5.36 / 4.36; normal 3.98-4.35).** Worse again. 3 of its 4 MH04 runs are above normal's whole range.

**Contrast boost, MH05 run 4: 6.91 cm (runs 1-3: 6.70 / 5.23 / 8.59; normal 4.63-6.09).** Worse again. Its middle on MH05 (~6.8) is above every normal run.

**2000 corners, MH04 run 4: 4.34 cm (runs 1-3: 4.10 / 4.03 / 4.08; normal 4.35 / 3.98 / 4.27 / 4.28).** Its first MH04 run that isn't below normal's middle. The small MH04 gain is getting thinner.

**2000 corners, MH05 run 4: 4.72 cm (runs 1-3: 4.97 / 5.69 / 4.99; normal 4.75 / 4.63 / 5.60 / 6.09).** Its best MH05 run. With normal's MH05 middle now about 5.2, 2000 corners (middle about 4.98) is slightly *ahead* on MH05 too. Small, but it's the only version ahead on both flights.

**Trust motion sensor more, MH04 run 4: 7.09 cm.** 7 of 7 worse.

**Trust motion sensor more, MH05 run 4: 8.99 cm.** 8 of 8 worse, and its worst run.

**Trust motion sensor less, MH04 run 4: 4.14 cm (runs 1-3: 4.35 / 4.34 / 4.02).** Inside normal's range. Even.

**Trust motion sensor less, MH05 run 4: 5.62 cm.** Middle about 5.6, slightly worse than normal's about 5.2.

### Round 4 summary: middle score after 4 runs (cm)

| Version | MH04 | MH05 |
|---|---|---|
| Normal | 4.27 | 5.17 |
| Contrast boost | 4.86 | 6.80 |
| 2000 corners | **4.09** | **4.98** |
| Trust motion sensor more | 7.57 | 7.11 |
| Trust motion sensor less | 4.24 | 5.59 |

- **2000 corners is now ahead on both flights** (about 0.2 cm each), and it helps mostly in dark moments (MH04 dark gap 2.9-3.3 vs normal 3.1-3.9). That's what the contrast boost was meant to do. More real corners works better than brightening the photo.
- **It's still fair:** runs take the same time as normal (MH04 ~110 s, MH05 ~123 s, measured from start to score), so ORB-SLAM3 keeps up with the live flight.
- **Next refinement:** push it further, to 2500 and 3000 corners (`day2_refine2.sh`, 5 runs each on MH04/MH05, after the photo-cleanup refinements and the easy-flight normal runs).

## Round 5

**Normal, MH04 run 5: 4.86 cm.** Normal's worst MH04 run. All 5: 4.35 / 3.98 / 4.27 / 4.28 / 4.86, middle 4.28, spread about 0.9 cm.

**Normal, MH05 run 5: 5.36 cm.** All 5 normal MH05 runs: 4.75 / 4.63 / 5.60 / 6.09 / 5.36, middle **5.36 cm**. The paper's median of 10 is 8.2 cm, so the "beat the paper on MH05" finding holds with 5 runs, by about 2.8 cm instead of Day 1's 3.45.

**Contrast boost, MH04 run 5: 4.59 cm.** All 5: 4.58 / 5.36 / 4.36 / 5.14 / 4.59, middle 4.59 vs normal's 4.28. **Verdict: worse.**

**Contrast boost, MH05 run 5: 8.09 cm.** All 5: 6.70 / 5.23 / 8.59 / 6.91 / 8.09, middle 6.91 vs normal's 5.36. **Verdict: clearly worse, by about 1.5 cm, on the flight it was meant to help most.**

**2000 corners, MH04 run 5: 4.55 cm.** All 5: 4.10 / 4.03 / 4.08 / 4.34 / 4.55, middle **4.10** vs normal's 4.28. About 0.2 cm better, but the last two runs drifted up. Same pattern as normal (whose run 5 was also its worst, 4.86), so it may be a slower PC moment late in the queue hitting all versions alike.

**2000 corners, MH05 run 5: 5.48 cm.** All 5: 4.97 / 5.69 / 4.99 / 4.72 / 5.48, middle **4.99** vs normal's 5.36. About 0.4 cm better on MH05. **Verdict: a small but consistent win on both hard flights** (MH04 -0.18, MH05 -0.37 cm), at the same speed. The only one of the first 4 fixes that helps.

**Trust motion sensor more, MH04 run 5: 7.32 cm.** All 5: 7.82 / 8.39 / 7.33 / 7.09 / 7.32, middle 7.33 vs normal's 4.28. **Verdict: much worse (+3.0 cm).**

**Trust motion sensor more, MH05 run 5: 9.43 cm.** All 5: 6.30 / 6.19 / 7.92 / 8.99 / 9.43, middle 7.92 vs normal's 5.36. **Verdict: much worse (+2.6 cm), 10 of 10 runs worse than normal's middle.**

**Trust motion sensor less, MH04 run 5: 4.05 cm.** All 5: 4.35 / 4.34 / 4.02 / 4.14 / 4.05, middle 4.14 vs normal's 4.28. Slightly better on MH04 (-0.14), and very steady (spread 0.33 cm, vs normal's 0.88).

**Trust motion sensor less, MH05 run 5: 5.02 cm.** All 5: 5.10 / 6.59 / 5.56 / 5.62 / 5.02, middle 5.56 vs normal's 5.36. Slightly worse on MH05 (+0.2), mostly from rougher start-ups.

### Final result for the first 4 fixes (middle of 5 runs each, cm)

| Version | MH04 | vs normal | MH05 | vs normal | Verdict |
|---|---|---|---|---|---|
| Normal (unchanged ORB-SLAM3) | 4.28 | - | 5.36 | - | - |
| Contrast boost (CLAHE, every photo, clip 3.0) | 4.59 | +0.31 | 6.91 | +1.55 | **Worse**, most on the darkest flight |
| 2000 corners per photo | **4.10** | **-0.18** | **4.99** | **-0.37** | **Better on both**, same speed. Keep |
| Trust motion sensor 9x more | 7.33 | +3.05 | 7.92 | +2.56 | **Much worse** |
| Trust motion sensor 9x less | 4.14 | -0.14 | 5.56 | +0.20 | Even (better MH04, worse MH05 start-up) |

**What the first 4 fixes taught us:**
1. **More real corners beats brighter photos.** Both aimed at the dark stretches. Adding corners helped; artificially boosting contrast hurt, likely by turning camera grain into fake corners and stretching left and right photos differently.
2. **The motion sensor's trust setting is already about right.** Trusting it more is the single worst change of the day. Trusting it less is a wash: slightly better tracking in the dark, but a rougher start, because the start-up estimates of the sensor's offsets and of gravity depend on the same numbers.
3. **Run-to-run wobble is big.** The unchanged program ranged 3.98-4.86 cm on MH04 and 4.63-6.09 cm on MH05. Without 5 runs each, round 1 would have suggested different winners.
4. **With 5 runs, the normal version's middle on MH05 is 5.36 cm**, still well below the paper's 8.2 cm. The "beat the paper" finding holds, by a smaller margin than Day 1's single run suggested.

**Next (running now, in this order):** contrast boost v2 and brightness curve (refined photo cleanup), the postponed easy-flight normal runs, then 2500 and 3000 corners. After that, the winners are combined into Benny's version and checked on all 5 flights.

## Refinement 1: gentler photo cleanup (5 runs each on MH04/MH05)

Both versions only touch dark photo pairs (average brightness under 60): 411 of MH04's 2,032 pairs and 479 of MH05's 2,273 (about 20%). Checked in each run's log.

**Round 1:**
- **Contrast boost v2, MH04: 4.03 cm (normal middle 4.28).** Better, and its dark-moment gap is 3.0 cm vs normal's 3.1-3.9. The first time a contrast boost has beaten normal.
- **Contrast boost v2, MH05: 6.51 cm (normal 5.36). Worse, in an odd way:** dark moments got *better* (4.5 vs normal's ~5-6.5), but bright moments got much *worse* (6.3 vs ~3.6-4.3), even though bright photos weren't touched. Possible cause: the boost switches on and off as the drone passes in and out of dark areas, so the same corner looks different depending on whether that photo was boosted. ORB-SLAM3 then has trouble re-matching corners it mapped in a boosted photo when it sees them again unboosted, and the drift carries into the bright stretches.
- **Brightness curve, MH04: 4.73 cm. Worse.** It started late (15.9 s vs ~11-12 s).
- **Brightness curve, MH05: 5.22 cm.** Slightly better than normal's middle (5.36), inside the wobble.

**Round 2:**
- **Contrast boost v2, MH04: 4.49 cm** (run 1: 4.03; normal 3.98-4.86, middle 4.28). Back inside normal's range.
- **Contrast boost v2, MH05: 5.14 cm** (run 1: 6.51; normal middle 5.36). Slightly better than normal this time. Wobbling a lot.
- **Brightness curve, MH04: 3.97 cm** (run 1: 4.73; normal middle 4.28). Its best so far, below every normal MH04 run.
- **Brightness curve, MH05: 6.41 cm** (run 1: 5.22; normal 4.63-6.09). Above normal's whole range this time.

**Round 3:**
- **Contrast boost v2, MH04: 4.44 cm** (runs 1-2: 4.03 / 4.49; normal middle 4.28). Slightly above normal's middle.

### Why these results happened (written up when Benny asked, for the article)
1. **Run-to-run wobble:** ORB-SLAM3 runs several jobs at once (tracking each photo, building the map, tidying the map). Their timing differs slightly each run, which changes which reference photos get saved and which corners get matched. Those small differences grow over the flight. Unchanged program: 3.98-4.86 cm on MH04, 4.63-6.09 cm on MH05.
2. **2000 corners helped:** in dark or plain areas, a 1,200 limit leaves too few strong anchors. 2,000 lets it keep weaker but real corners, spread across the whole photo. The gain is almost all in dark moments (MH04 dark gap 2.9-3.3 vs 3.1-3.9), at the same speed.
3. **Contrast boost hurt:** (a) it stretches grain into fake corners that don't match between photos; more reference photos (~190 vs ~165) with worse accuracy shows ORB-SLAM3 kept feeling it was losing track; (b) tile-by-tile stretching, done separately for each camera, makes left and right disagree, which throws off the left/right patch comparison that measures distance; (c) it changed every photo, including the 80% that were fine.
4. **Trusting the motion sensor more hurt badly:** the sensor's small built-in errors pile up. Over-trusting it stops the cameras from correcting it, so the biggest slips came at the fastest turns.
5. **Trusting it less was a wash:** slightly better in the dark, but the start-up uses the same numbers to estimate the sensor's offsets and gravity, so starts got sloppier (worst slips at 10 s on MH05).
6. **The gentler photo cleanups are mixed:** boosting only dark photos helps the dark moments, but switching the boost on and off makes the same corner look different between boosted and unboosted photos, which hurts re-recognition in the bright stretches.
**Big picture:** the authors' settings were already well tuned. More *real* information (corners) helps. Anything that makes the same scene look different from photo to photo, or overrides the cameras, hurts.
- **Contrast boost v2, MH05: 6.75 cm** (runs 1-2: 6.51 / 5.14; normal 4.63-6.09). 2 of 3 MH05 runs are above normal's whole range. Leaning worse.
- **Brightness curve, MH04: 3.89 cm** (runs 1-2: 4.73 / 3.97; normal 3.98-4.86). Below every normal MH04 run again. 2 of 3 MH04 runs better than normal's best.
- **Brightness curve, MH05: 5.73 cm** (runs 1-2: 5.22 / 6.41; normal middle 5.36). Middle so far 5.73, slightly worse than normal on MH05.

### Plan agreed with Benny (31 Oct, afternoon)
1. Finish refinements (gentler photo cleanup, easy-flight normal runs, 2500/3000 corners).
2. Pick his version: best corner count, plus any photo cleanup that wins on both hard flights.
3. Confirm the win: his version vs normal, 10 runs each on all 5 flights (like the paper), alternating between the two versions. Report how often his version wins, not just the medians.
4. Visuals: paper vs normal vs his version; every run for every fix (shows the wobble); before/after path charts; a dark photo with corners for normal vs more corners vs contrast boost; the existing motion-sensor charts.
5. Article draft with visuals built in, from the research log and run notes. Benny reviews; nothing gets published (Medium, GitHub) without his OK.
6. Organize the project: tidy folders and a README, mirrored in the brain.

**Round 4:**
- **Contrast boost v2, MH04: 4.44 cm** (runs 1-3: 4.03 / 4.49 / 4.44). Middle 4.44 vs normal's 4.28. Not a win on MH04.
- **Contrast boost v2, MH05: 4.58 cm** (runs 1-3: 6.51 / 5.14 / 6.75). Its best run, but its runs swing from 4.58 to 6.75: wobbles more than normal (4.63-6.09).
- **Brightness curve, MH04: 4.26 cm** (runs 1-3: 4.73 / 3.97 / 3.89). Middle about 4.1 vs normal's 4.28.
- **Brightness curve, MH05: 4.24 cm** (runs 1-3: 5.22 / 6.41 / 5.73). The best single MH05 run of any version today (normal's best: 4.63). But its runs range from 4.24 to 6.41, middle about 5.5, so it's not a clear win on MH05 yet.

**Round 5:**
- **Contrast boost v2, MH04: 4.26 cm.** All 5: 4.03 / 4.49 / 4.44 / 4.44 / 4.26, middle 4.44 vs normal's 4.28. **Verdict on MH04: no gain.**
- **Contrast boost v2, MH05: 5.13 cm.** All 5: 6.51 / 5.14 / 6.75 / 4.58 / 5.13, middle 5.14 vs normal's 5.36. Slightly better middle on MH05 (-0.22), but a much wider spread (4.58-6.75). **Verdict: not a win.** Even on MH04, slightly ahead on MH05, and less predictable. Not going into Benny's version.
- **Brightness curve, MH04: 4.01 cm.** All 5: 4.73 / 3.97 / 3.89 / 4.26 / 4.01, middle **4.01** vs normal's 4.28 (-0.27). Better than 2000 corners on MH04 (4.10).
- **Brightness curve, MH05: 5.81 cm.** All 5: 5.22 / 6.41 / 5.73 / 4.24 / 5.81, middle 5.73 vs normal's 5.36 (+0.37). **Verdict: mixed.** Best on MH04 (-0.27) but worse on MH05 (+0.37), so it fails the "win on both hard flights" rule and stays out of Benny's version.

### Refinement 1 result: gentler photo cleanup (middle of 5 runs, cm)

| Version | MH04 | MH05 | Verdict |
|---|---|---|---|
| Normal | 4.28 | 5.36 | - |
| Contrast boost (original) | 4.59 | 6.91 | Worse |
| Contrast boost v2 (dark only, half strength) | 4.44 | 5.14 | Not a win: even, and less predictable (MH05 4.58-6.75) |
| Brightness curve (dark only) | **4.01** | 5.73 | Mixed: best on MH04, worse on MH05 |
| 2000 corners | 4.10 | **4.99** | **Only version better on both** |

**What refining the photo cleanup taught us:** making it gentler and dark-only fixed most of the damage from the original contrast boost (MH05 6.91 down to 5.14-5.73), but never turned it into a clear win. Changing the photos, even carefully, makes the same scene look different between photos, which is the one thing ORB-SLAM3's matching depends on. **More corners (changing what ORB-SLAM3 looks for, not what it looks at) stays the only consistent improvement.** Next: 2500/3000 corners (after the easy-flight normal runs, now running).

## Easy-flight normal runs (for the final comparison)
- Normal, MH01 run 2: 3.05 cm (run 1: 3.44; paper 3.6).
- Normal, MH02 run 2: 2.25 cm (run 1: 2.94; paper 3.3).
- Normal, MH03 run 2: 3.56 cm (run 1: 3.45; paper 3.5).
- Normal, MH01 run 3: 4.00 cm (runs so far 3.44 / 3.05 / 4.00).
- Normal, MH02 run 3: 2.28 cm (runs so far 2.94 / 2.25 / 2.28).
- Normal, MH03 run 3: 3.39 cm (runs so far 3.45 / 3.56 / 3.39).
- Normal, MH01 run 4: 3.96 cm.
- **Normal, MH02 run 4: 54.09 cm. A silent failure.**
  - The path is the right size (best-fit scale 1.003; guessed length 74.4 m vs true 73.4 m) and nothing was lost: one map, all 3,032 photos saved, no lost-track or reset messages after start-up.
  - But at **78.9 s the guess teleported 87 cm between two photos** (normal step: 2.5 cm). The before and after halves don't line up, so the best alignment splits the difference and the gap is about 40-55 cm for the whole flight. Run 3 on the same flight: 2.3 cm with no jump.
  - **ORB-SLAM3 printed no warning at all.** It didn't know it had jumped.
  - Checked all 81 runs so far for jumps over 20 cm: this is the only mid-flight one (plus a 21 cm jump in MH05 run 1 at 0.4 s, during start-up). So about **1 in 80 runs fails silently like this**. Cause not identified; most likely a wrong corner match that got accepted and pulled the map.
  - Why it matters: (1) it's why the paper (and we) use the **median**, which ignores one wild run; an average would have been wrecked. (2) For a real drone, a silent 87 cm jump in a tight space is dangerous. This ties straight into Benny's original Day 2 question, "how sure am I that I'm right?": ORB-SLAM3 has no idea when it's wrong.
- Normal, MH03 run 4: 3.00 cm.
- Normal, MH01 run 5: 4.21 cm. All 5: 3.44 / 3.05 / 4.00 / 3.96 / 4.21, middle 3.96 (paper 3.6).
- Normal, MH02 run 5: 2.21 cm. All 5: 2.94 / 2.25 / 2.28 / 54.09 (silent jump) / 2.21, middle 2.28 (paper 3.3).
- Normal, MH03 run 5: 2.80 cm. All 5: 3.45 / 3.56 / 3.39 / 3.00 / 2.80, middle 3.39 (paper 3.5).

### The reproduction with 5 runs each (normal ORB-SLAM3 vs the paper's median of 10, cm)

| Flight | Your PC, middle of 5 | Range of your 5 runs | Paper | Difference |
|---|---|---|---|---|
| MH01 easy | 3.96 | 3.05-4.21 | 3.6 | +0.36 (slightly worse) |
| MH02 easy | 2.28 | 2.21-2.94 (one silent-jump run at 54.09) | 3.3 | -1.02 |
| MH03 medium | 3.39 | 2.80-3.56 | 3.5 | -0.11 |
| MH04 difficult | 4.28 | 3.98-4.86 | 5.1 | -0.82 |
| MH05 difficult | 5.36 | 4.63-6.09 | 8.2 | -2.84 |

**Updated reproduction verdict:** with proper repeats, your PC matches the paper closely on the easy and medium flights (within about ±0.4 cm on MH01 and MH03) and beats it on MH02, MH04 and especially MH05. Day 1's single runs had made MH01 look better than it is (3.44 vs a true middle of 3.96).

## Refinement 2: even more corners (2500 and 3000), 5 runs each on MH04/MH05
- **2500 corners, MH04 run 1: 4.53 cm** (2000 corners middle 4.10, normal 4.28). Worse than both on its first run.
- **2500 corners, MH05 run 1: 5.17 cm** (2000 corners middle 4.99, normal 5.36). Between the two.
- **3000 corners, MH04 run 1: 4.02 cm** (2000 middle 4.10, normal 4.28). Good first run.
- **3000 corners, MH05 run 1: 5.34 cm** (2000 middle 4.99, normal 5.36). About even with normal.
- **Speed check and a caveat:** 3000 corners kept up with the live flight (MH04 111 s, MH05 127 s, vs normal 110 / 123). 2500 corners' first runs took longer (126 / 141 s). That's because my run-table script (which re-scores every run, about a minute of heavy work) ran at the same moment as 2500's MH04 run 1, and the brain sync was running during its MH05 run. So **2500 run 1 (4.53 / 5.17) may have been slowed by my own analysis.** The median of 5 limits the damage. From now on, heavy analysis only runs between queues, never during a run, and not at all during the final check.
- **2500 corners, MH04 run 2: 4.22 cm** (run 1, possibly slowed: 4.53).
- **2500 corners, MH05 run 2: 4.83 cm** (run 1: 5.17; 2000 middle 4.99, normal 5.36).
- **3000 corners, MH04 run 2: 3.84 cm** (run 1: 4.02). Best MH04 run of any version today, and both 3000 runs are below normal's best (3.98).
- **3000 corners, MH05 run 2: 6.09 cm** (run 1: 5.34; normal 4.63-6.09). At the top of normal's range. Great on MH04, so far no help on MH05.
- **2500 corners, MH04 run 3: 4.48 cm** (runs 1-2: 4.53 / 4.22). Middle so far 4.48, behind normal's 4.28.
- **2500 corners, MH05 run 3: 5.83 cm** (runs 1-2: 5.17 / 4.83). Middle so far 5.17, slightly ahead of normal's 5.36.
- **3000 corners, MH04 run 3: 4.77 cm** (runs 1-2: 4.02 / 3.84). Its first bad MH04 run. Middle so far 4.02.
- **3000 corners, MH05 run 3: 5.67 cm** (runs 1-2: 5.34 / 6.09). Middle so far 5.67, behind normal's 5.36.
- **2500 corners, MH04 run 4: 4.31 cm** (runs 1-3: 4.53 / 4.22 / 4.48).
- **2500 corners, MH05 run 4: 6.38 cm** (runs 1-3: 5.17 / 4.83 / 5.83). Above normal's range.
- **3000 corners, MH04 run 4: 4.04 cm** (runs 1-3: 4.02 / 3.84 / 4.77). Middle about 4.03.
- **3000 corners, MH05 run 4: 6.26 cm** (runs 1-3: 5.34 / 6.09 / 5.67). Middle about 5.9, worse than normal on MH05.
- **2500 corners, MH04 run 5: 4.46 cm.** All 5: 4.53 / 4.22 / 4.48 / 4.31 / 4.46, middle 4.46 vs normal's 4.28. Worse on MH04.
- **2500 corners, MH05 run 5: 4.68 cm.** All 5: 5.17 / 4.83 / 5.83 / 6.38 / 4.68, middle 5.17 vs normal's 5.36. Slightly ahead on MH05, behind on MH04. **Verdict: mixed, not a win.**
- **3000 corners, MH04 run 5: 4.66 cm.** All 5: 4.02 / 3.84 / 4.77 / 4.04 / 4.66, middle 4.04 vs normal's 4.28 (-0.24).
- **3000 corners, MH05 run 5: 5.04 cm.** All 5: 5.34 / 6.09 / 5.67 / 6.26 / 5.04, middle 5.67 vs normal's 5.36. **Verdict: mixed** (better MH04 -0.24, worse MH05 +0.31).

### Refinement 2 result: how many corners? (middle of 5 runs, cm)

| Corners per photo | MH04 | MH05 | |
|---|---|---|---|
| 1200 (normal) | 4.28 | 5.36 | |
| **2000** | **4.10** | **4.99** | Only one better on both |
| 2500 | 4.46 | 5.17 | Mixed |
| 3000 | 4.04 | 5.67 | Mixed |

**Lesson:** more corners isn't simply "more is better". 2000 is a sweet spot: enough extra anchors for the dark stretches. Past that, the extra corners are increasingly weak ones (the corner finder lowers its standards to hit the count), which add noise as well as anchors. The results also jump around more than a smooth trend would. (2500's first runs may have been slowed by my analysis running at the same time; see the caveat above.)

## Decision: Benny's version = normal ORB-SLAM3 + 2000 corners per photo
Out of 9 versions tested (5 runs each on MH04/MH05), only 2000 corners beat normal on **both** hard flights. One-line change: `ORBextractor.nFeatures: 2000` in the settings file. Same speed as normal.

## Final check (started 31 Oct, ~16:35)
Fresh, head-to-head: normal vs 2000 corners, **10 runs each on all 5 flights** (like the paper), alternating which version goes first each round so both get the same PC conditions. None of these runs were used to pick the winner, so it's a fair test. Nothing else runs on the PC during it. Results go to `~/tks-slam/results/final/`. About 4 hours.

**Correction (silent jump timing):** measured from the flight's first photo, as in all the other charts, the 87 cm jump happens at **79.3 s**. The 78.9 s above was measured from ORB-SLAM3's first saved position.

**Correction (1 Nov):** the "about 1 in 80 runs" figure above was only true when written. Across all 210 runs, the silent jump happened once.
