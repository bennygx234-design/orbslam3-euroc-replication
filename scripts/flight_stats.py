import os, numpy as np
from evo.tools import file_interface
home = os.path.expanduser("~/tks-slam")
for f, s in [("MH_01_easy","MH01"),("MH_02_easy","MH02"),("MH_03_medium","MH03"),("MH_04_difficult","MH04"),("MH_05_difficult","MH05")]:
    gt = file_interface.read_euroc_csv_trajectory(f"{home}/datasets/euroc/{f}/mav0/state_groundtruth_estimate0/data.csv")
    photos = sum(1 for l in open(f"{home}/ORB_SLAM3/Examples/Stereo-Inertial/EuRoC_TimeStamps/{s}.txt") if l.strip())
    scored = {m: sum(1 for l in open(f"{home}/results/{m}/{s}/run1/f_{s}_seconds.txt") if l.strip()) for m in ["stereo_inertial","stereo"]}
    print(f"{s} photos {photos} ({photos/20:.0f} s)  flown {gt.path_length:.1f} m  top speed {np.max(np.linalg.norm(np.diff(gt.positions_xyz,axis=0),axis=1)/np.diff(gt.timestamps)):.1f} m/s  path-saved stereo_inertial {scored['stereo_inertial']} stereo {scored['stereo']}")
