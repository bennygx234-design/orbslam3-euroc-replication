# For each scored moment: how dark the photo was, how fast the drone turned, and how far off ORB-SLAM3 was
import os, numpy as np, matplotlib.image as mpimg
from evo.tools import file_interface
from evo.core import sync
home = os.path.expanduser("~/tks-slam")
for flight, short in [("MH_03_medium","MH03"), ("MH_04_difficult","MH04"), ("MH_05_difficult","MH05")]:
    d = f"{home}/datasets/euroc/{flight}/mav0"
    truth = file_interface.read_euroc_csv_trajectory(f"{d}/state_groundtruth_estimate0/data.csv")
    for mode in ["stereo_inertial", "stereo"]:
        g = file_interface.read_tum_trajectory_file(f"{home}/results/{mode}/{short}/run1/f_{short}_seconds.txt")
        t2, g2 = sync.associate_trajectories(truth, g)
        g2.align(t2, correct_scale=False)
        err = np.linalg.norm(g2.positions_xyz - t2.positions_xyz, axis=1) * 100
        ts = g2.timestamps[::5]; e = err[::5]
        names = {int(n[:-4]): n for n in os.listdir(f"{d}/cam0/data")}
        keys = np.array(sorted(names))
        bright = np.array([mpimg.imread(f"{d}/cam0/data/{names[keys[np.argmin(abs(keys - t*1e9))]]}").mean()*255 for t in ts])
        imu = np.loadtxt(f"{d}/imu0/data.csv", delimiter=",", comments="#")
        rate = np.convolve(np.degrees(np.linalg.norm(imu[:,1:4], axis=1)), np.ones(50)/50, mode="same")
        turn = np.interp(ts, imu[:,0]/1e9, rate)
        dark, fast = bright < 50, turn > 25
        def m(mask): return f"{e[mask].mean():5.1f} cm ({mask.mean()*100:3.0f}% of moments)" if mask.any() else "   -"
        print(f"{short} {mode:15s} dark+slow {m(dark & ~fast)} | bright+fast {m(~dark & fast)} | dark+fast {m(dark & fast)} | bright+slow {m(~dark & ~fast)}")
