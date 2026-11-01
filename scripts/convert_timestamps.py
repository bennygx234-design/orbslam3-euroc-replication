# convert_timestamps.py
# What it does: ORB-SLAM3 writes each moment in nanoseconds (billionths of a second).
# evo reads seconds. This divides the first number on every line by 1,000,000,000.
#
# How to run: python3 convert_timestamps.py <ORB-SLAM3 file> <new file for evo>
#
# Each line of ORB-SLAM3's file has 8 numbers separated by spaces:
#   time  x  y  z  qx  qy  qz  qw
#   (time, position in meters, then which way the drone faces)

import sys

input_path = sys.argv[1]    # ORB-SLAM3's file, for example f_MH01_stereoi.txt
output_path = sys.argv[2]   # the new file evo will read

with open(input_path) as infile, open(output_path, "w") as outfile:
    for line in infile:
        parts = line.split()    # split the line into a list of its 8 numbers (as text)
        if not parts:           # skip empty lines
            continue

        # STEP 1: take the first item (the time) and turn it from text into a number.
        # ORB-SLAM3 writes it like "1403636580838555648.000000", so read it as a decimal number.
        t_ns = float(parts[0])

        # STEP 2: divide it by 1,000,000,000 to get seconds
        t_s = t_ns / 1_000_000_000

        # STEP 3: put it back as the first item, written with 9 digits after the decimal point
        parts[0] = f"{t_s:.9f}"

        # STEP 4: join the items back together with spaces and write the line to the new file
        outfile.write(" ".join(parts) + "\n")

print("Done:", output_path)
