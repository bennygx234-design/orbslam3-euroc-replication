"""Draws the build article's 8 figures as PNGs from the saved results.

Run from tks-orbslam3-research/:  python scripts/article_figures.py
Needs matplotlib. Output goes to article/figures/. Font: Arial.
Positions are in pixels on a 760-wide canvas, with y counted from the top.
"""
import csv
import glob
import os
import re
import statistics

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle

OUT = "article/figures"
INK = "#111111"
SOFT = "#555555"
MUTED = "#b4b4b4"
GRID = "#e4e4e4"
PT = 0.72  # one canvas pixel in points

plt.rcParams["font.family"] = ["Arial", "Helvetica", "DejaVu Sans"]

FLIGHTS = ["MH01", "MH02", "MH03", "MH04", "MH05"]
NAMES = ["Flight 1", "Flight 2", "Flight 3", "Flight 4", "Flight 5"]
LEVELS = ["easy", "easy", "medium", "hard", "hard"]


class Canvas:
    def __init__(self, height):
        self.fig = plt.figure(figsize=(7.6, height / 100), dpi=220)
        self.ax = self.fig.add_axes([0, 0, 1, 1])
        self.ax.set_xlim(0, 760)
        self.ax.set_ylim(height, 0)
        self.ax.axis("off")

    def line(self, x1, y1, x2, y2, color=INK, w=1.0, dash=None):
        kwargs = {"linestyle": (0, dash)} if dash else {}
        self.ax.plot([x1, x2], [y1, y2], color=color, lw=w * PT, solid_capstyle="butt", **kwargs)

    def path(self, xs, ys, color=INK, w=1.0):
        self.ax.plot(xs, ys, color=color, lw=w * PT, solid_joinstyle="round")

    def text(self, x, y, words, size=13, color=INK, bold=False, ha="left", rotation=0):
        return self.ax.text(x, y, words, fontsize=size * PT, color=color, ha=ha, va="baseline",
                            fontweight="bold" if bold else "normal", rotation=rotation,
                            rotation_mode="anchor")

    def dot(self, x, y, r=3.0, fill=None, edge=INK, w=1.0, marker="o", z=3):
        self.ax.plot([x], [y], marker=marker, ms=2 * r * PT, mfc=fill if fill else "white",
                     mec=edge, mew=w * PT, ls="none", zorder=z)

    def box(self, x, y, w, h, edge=INK, lw=1.0, fill="none", dash=None):
        kwargs = {"linestyle": (0, dash)} if dash else {}
        self.ax.add_patch(Rectangle((x, y), w, h, fc=fill, ec=edge, lw=lw * PT, **kwargs))

    def arrow(self, x, y, way):
        points = {
            "r": [(x, y), (x - 8, y - 4), (x - 8, y + 4)],
            "d": [(x, y), (x - 4, y - 8), (x + 4, y - 8)],
            "u": [(x, y), (x - 4, y + 8), (x + 4, y + 8)],
        }[way]
        self.ax.add_patch(Polygon(points, fc=INK, ec="none"))

    def title(self, number, words):
        label = self.text(0, 18, f"Figure {number}. ", size=14, bold=True)
        self.fig.canvas.draw()
        box = label.get_window_extent().transformed(self.ax.transData.inverted())
        self.text(box.x1 + 4, 18, words, size=14)

    def y_axis(self, ticks, Y, left, right, base, y0, label):
        for t in ticks:
            self.line(left, Y(t), right, Y(t), GRID, 0.7)
            self.line(left - 5, Y(t), left, Y(t))
            self.text(left - 9, Y(t) + 4, str(t), ha="right")
        self.line(left, y0, left, base)
        self.line(left, base, right, base)
        self.ax.text(14, (y0 + base) / 2, label, fontsize=13 * PT, color=INK, rotation=90,
                     ha="center", va="center")

    def save(self, name):
        self.fig.savefig(f"{OUT}/{name}.png", facecolor="white", bbox_inches="tight", pad_inches=0.06)
        plt.close(self.fig)


def final_scores(version):
    """All 10 final-test scores per flight, in centimeters."""
    scores = {}
    for path in glob.glob(f"results/final/{version}/MH0*/run*/evo_score.txt"):
        flight = path.split(os.sep)[3]
        rmse = re.search(r"rmse\s+([\d.]+)", open(path).read())
        scores.setdefault(flight, []).append(float(rmse.group(1)) * 100)
    return [sorted(scores[f]) for f in FLIGHTS]


def figure1():
    c = Canvas(456)
    c.title(1, "How ORB-SLAM3 estimates the path, and how I scored it.")
    c.box(12, 60, 185, 302, SOFT, 0.8, dash=(3, 3))
    c.box(200, 60, 548, 96, SOFT, 0.8, dash=(3, 3))
    c.box(559, 268, 189, 180, SOFT, 0.8, dash=(3, 3))
    c.text(20, 52, "RECORDED FLIGHT", 11, SOFT, True)
    c.text(204, 52, "ORB-SLAM3", 11, SOFT, True)
    c.text(567, 260, "SCORING", 11, SOFT, True)
    blocks = [
        (24, 84, "Two cameras", "20 photos per second", 1),
        (206, 84, "Find corners", "and fingerprint them", 1),
        (388, 84, "Match corners", "across cameras and photos", 1),
        (571, 84, "Work out the path", "that fits all the data", 2),
        (24, 172, "Motion sensor", "200 readings per second", 1),
        (24, 290, "Laser tracker", "accurate to about 1 mm", 1),
        (571, 290, "Compare the paths", "gap at every moment", 1),
        (571, 378, "Score", "error in centimeters", 1),
    ]
    for x, y, head, sub, lw in blocks:
        c.box(x, y, 165, 58, lw=lw)
        c.text(x + 82.5, y + 24, head, bold=True, ha="center")
        c.text(x + 82.5, y + 41, sub, 12, SOFT, ha="center")
    for x1, x2 in ((189, 198), (371, 380), (553, 563)):
        c.line(x1, 113, x2, 113)
    c.path([189, 615, 615], [201, 201, 150])
    c.line(695, 142, 695, 282)
    c.line(189, 319, 563, 319)
    c.line(653.5, 348, 653.5, 370)
    for x, y, way in ((206, 113, "r"), (388, 113, "r"), (571, 113, "r"), (615, 142, "u"),
                      (695, 290, "d"), (571, 319, "r"), (653.5, 378, "d")):
        c.arrow(x, y, way)
    c.text(360, 194, "every turn and push", 12, SOFT, ha="center")
    c.text(687, 232, "estimated path", 12, SOFT, ha="right")
    c.text(376, 312, "true path (the program never sees this)", 12, SOFT, ha="center")
    c.save("fig1-how-it-works")


def figure2():
    rows = list(csv.DictReader(open("article/assets/flight5_map.csv")))
    x = [float(r["x"]) for r in rows]
    y = [float(r["y"]) for r in rows]
    gx = [float(r["gx"]) for r in rows]
    gy = [float(r["gy"]) for r in rows]
    x_lo, x_hi, y_lo, y_hi = -5, 20, -10, 15
    assert min(x + gx) >= x_lo and max(x + gx) <= x_hi and min(y + gy) >= y_lo and max(y + gy) <= y_hi
    scale = min(500 / (x_hi - x_lo), 440 / (y_hi - y_lo))
    left, y0 = 56, 44
    px = lambda v: left + (v - x_lo) * scale
    py = lambda v: y0 + (y_hi - v) * scale
    base, edge = py(y_lo), px(x_hi)
    c = Canvas(int(base + 52))
    c.title(2, "Flight 5 seen from above. The gaps between the paths are drawn 10 times bigger.")
    for v in range(x_lo, x_hi + 1, 5):
        c.line(px(v), y0, px(v), base, GRID, 0.7)
        c.line(px(v), base, px(v), base + 5)
        c.text(px(v), base + 19, str(v), ha="center")
    for v in range(y_lo, y_hi + 1, 5):
        c.line(left, py(v), edge, py(v), GRID, 0.7)
        c.line(left - 5, py(v), left, py(v))
        c.text(left - 9, py(v) + 4, str(v), ha="right")
    c.box(left, y0, edge - left, base - y0)
    c.text((left + edge) / 2, base + 40, "Meters", ha="center")
    c.ax.text(14, (y0 + base) / 2, "Meters", fontsize=13 * PT, color=INK, rotation=90, ha="center", va="center")
    c.path([px(v) for v in x], [py(v) for v in y], MUTED, 4)
    c.path([px(v) for v in gx], [py(v) for v in gy], INK, 1)
    c.dot(px(x[0]), py(y[0]), 4, INK, INK, marker="s")
    c.line(edge + 20, 66, edge + 46, 66, MUTED, 4)
    c.text(edge + 54, 70, "True path (laser)", 12)
    c.line(edge + 20, 90, edge + 46, 90)
    c.text(edge + 54, 94, "Program's estimate", 12)
    c.dot(edge + 33, 114, 4, INK, INK, marker="s")
    c.text(edge + 54, 118, "Start", 12)
    c.save("fig2-flight5-map")


def figure3():
    runs = final_scores("baseline")
    middles = [3.81, 3.59, 3.27, 4.24, 5.33]
    published = [3.6, 3.3, 3.5, 5.1, 8.2]
    left, right, y0, base = 56, 744, 84, 356
    Y = lambda v: base - (v - 2) / 7 * (base - y0)
    band = (right - left) / 5
    cx = lambda i: left + band * (i + 0.5)
    c = Canvas(410)
    c.title(3, "My 10 runs of each flight against the published score. Lower is better.")
    c.dot(60, 48, 3, None, SOFT)
    c.text(70, 52, "One of my runs", 12)
    c.line(172, 48, 192, 48, w=2)
    c.text(198, 52, "My middle score", 12)
    c.dot(320, 48, 4, INK, INK, marker="D")
    c.text(332, 52, "Published score", 12)
    c.y_axis(range(2, 10), Y, left, right, base, y0, "Error (cm, lower is better)")
    for i in range(5):
        for j, score in enumerate(runs[i]):
            c.dot(cx(i) - 20 + (j % 3) * 7, Y(score), 3, None, SOFT)
        c.line(cx(i) - 26, Y(middles[i]), cx(i) + 8, Y(middles[i]), w=2)
        c.text(cx(i) - 30, Y(middles[i]) + 4, f"{middles[i]:.2f}", 12, bold=True, ha="right")
        c.dot(cx(i) + 28, Y(published[i]), 4, INK, INK, marker="D")
        c.text(cx(i) + 38, Y(published[i]) + 4, f"{published[i]:.1f}", 12)
        c.text(cx(i), base + 20, NAMES[i], ha="center")
        c.text(cx(i), base + 37, LEVELS[i], 12, SOFT, ha="center")
    c.save("fig3-mine-vs-published")


def figure4():
    both = [3.44, 2.94, 3.45, 4.35, 4.75]
    cameras = [3.93, 4.04, 5.07, 5.44, 6.44]
    left, right, y0, base = 56, 744, 74, 306
    Y = lambda v: base - (v - 2) / 5 * (base - y0)
    band = (right - left) / 5
    cx = lambda i: left + band * (i + 0.5)
    c = Canvas(360)
    c.title(4, "Error with and without the motion sensor. One run per setup, so these are rough.")
    c.dot(60, 48, 4, INK, INK)
    c.text(70, 52, "Cameras + motion sensor", 12)
    c.dot(226, 48, 4, None, INK)
    c.text(236, 52, "Cameras only", 12)
    c.y_axis(range(2, 8), Y, left, right, base, y0, "Error (cm)")
    for i in range(5):
        c.line(cx(i), Y(cameras[i]), cx(i), Y(both[i]))
        c.dot(cx(i), Y(cameras[i]), 4.5, None, INK)
        c.dot(cx(i), Y(both[i]), 4.5, INK, INK)
        c.text(cx(i) + 10, Y(cameras[i]) + 4, f"{cameras[i]:.2f}", 12, SOFT)
        c.text(cx(i) + 10, Y(both[i]) + 4, f"{both[i]:.2f}", 12, bold=True)
        c.text(cx(i), base + 20, NAMES[i], ha="center")
        c.text(cx(i), base + 37, LEVELS[i], 12, SOFT, ha="center")
    c.save("fig4-motion-sensor")


def figure5():
    rows = list(csv.DictReader(open("article/assets/flight5_gap.csv")))
    left, right, y0, base = 56, 744, 60, 320
    t_max = max(float(r["t"]) for r in rows)
    X = lambda t: left + t / t_max * (right - left)
    Y = lambda g: base - g / 20 * (base - y0)
    c = Canvas(372)
    c.title(5, "Gap between estimate and true path during Flight 5, one run of each setup.")
    c.line(60, 44, 84, 44, w=1.5)
    c.text(90, 48, "Cameras + motion sensor", 12)
    c.line(244, 44, 268, 44, MUTED, 1.5)
    c.text(274, 48, "Cameras only", 12)
    c.y_axis((0, 5, 10, 15, 20), Y, left, right, base, y0, "Gap (cm)")
    for v in range(0, int(t_max) + 1, 20):
        c.line(X(v), base, X(v), base + 5)
        c.text(X(v), base + 19, str(v), ha="center")
    c.text((left + right) / 2, base + 40, "Time into the flight (s)", ha="center")
    c.line(X(62), y0, X(62), base, SOFT, 0.8, dash=(3, 3))
    c.text(X(62) + 6, y0 + 12, "Sharpest turn", 12, SOFT)
    for name, color in (("without", MUTED), ("with", INK)):
        part = [r for r in rows if r["series"] == name]
        c.path([X(float(r["t"])) for r in part], [Y(float(r["gap"])) for r in part], color, 1.3)
    c.save("fig5-flight5-gap")


def figure6():
    rows = [
        ("2,000 corners", -0.18, -0.37),
        ("Gentle contrast boost", 0.16, -0.22),
        ("2,500 corners", 0.18, -0.19),
        ("Trust motion sensor less", -0.14, 0.20),
        ("3,000 corners", -0.24, 0.31),
        ("Soft brightening", -0.27, 0.37),
        ("Full contrast boost", 0.31, 1.55),
        ("Trust motion sensor more", 3.05, 2.56),
    ]
    y0, step = 76, 30
    base = y0 + step * len(rows)
    zero4, zero5, scale = 262, 574, 48
    sign = lambda v: f"{'+' if v > 0 else '−'}{abs(v):.2f}"
    c = Canvas(base + 46)
    c.title(6, "Change in error from the normal program, middle of 5 runs. Left of zero is better.")
    c.text(zero4, 56, "Flight 4 (normal 4.28 cm)", bold=True, ha="center")
    c.text(zero5, 56, "Flight 5 (normal 5.36 cm)", bold=True, ha="center")
    for zero in (zero4, zero5):
        for t in (-0.5, 0, 1, 2, 3):
            x = zero + t * scale
            c.line(x, y0, x, base, GRID, 0.7)
            c.line(x, base, x, base + 5)
            c.text(x, base + 18, str(t).replace("-", "−"), 12, ha="center")
        c.line(zero - 0.5 * scale, base, zero + 3 * scale, base)
    c.text(418, base + 38, "Change in error (cm)", ha="center")
    for i, (name, f4, f5) in enumerate(rows):
        y = y0 + step * (i + 0.5)
        key = i == 0
        c.text(0, y + 4, name, bold=key)
        for zero, v in ((zero4, f4), (zero5, f5)):
            c.ax.add_patch(Rectangle((min(zero, zero + v * scale), y - 8), abs(v) * scale, 16,
                                     fc=INK if key else MUTED, ec="none"))
            c.text((zero if v < 0 else zero + v * scale) + 6, y + 4, sign(v), 12, bold=key)
    c.line(zero4, y0, zero4, base)
    c.line(zero5, y0, zero5, base)
    c.save("fig6-eight-changes")


def figure7():
    normal = final_scores("baseline")
    more = final_scores("corners2000")
    normal_mid = [3.81, 3.59, 3.27, 4.24, 5.33]
    more_mid = [3.47, 2.98, 2.76, 4.16, 5.11]
    wins = [7, 9, 9, 5, 7]
    better = [9, 17, 16, 2, 4]
    left, right, y0, base = 76, 744, 84, 330
    Y = lambda v: base - (v - 2) / 4.5 * (base - y0)
    band = (right - left) / 5
    cx = lambda i: left + band * (i + 0.5) + 8
    c = Canvas(420)
    c.title(7, "Final test: 10 fresh runs of each version on each flight. 2,000 corners won 37 of 50.")
    c.dot(60, 48, 3, None, SOFT)
    c.text(70, 52, "Normal (1,200 corners)", 12)
    c.dot(216, 48, 3, INK, INK)
    c.text(226, 52, "2,000 corners", 12)
    c.line(326, 48, 346, 48, w=2)
    c.text(352, 52, "Middle score of 10 runs", 12)
    c.y_axis((2, 3, 4, 5, 6), Y, left, right, base, y0, "Error (cm, lower is better)")
    for i in range(5):
        for j, score in enumerate(normal[i]):
            c.dot(cx(i) - 32 + (j % 3 - 1) * 6, Y(score), 3, None, SOFT)
        for j, score in enumerate(more[i]):
            c.dot(cx(i) + 14 + (j % 3 - 1) * 6, Y(score), 3, INK, INK)
        c.line(cx(i) - 46, Y(normal_mid[i]), cx(i) - 18, Y(normal_mid[i]), w=2)
        c.line(cx(i), Y(more_mid[i]), cx(i) + 28, Y(more_mid[i]), w=2)
        c.text(cx(i) - 48, Y(normal_mid[i]) + 4, f"{normal_mid[i]:.2f}", 11, SOFT, ha="right")
        c.text(cx(i) + 32, Y(more_mid[i]) + 4, f"{more_mid[i]:.2f}", 11, bold=True)
        c.text(cx(i), base + 20, NAMES[i], ha="center")
        c.text(cx(i), base + 37, LEVELS[i], 12, SOFT, ha="center")
        c.text(cx(i), base + 56, f"won {wins[i]} of 10", 12, ha="center")
        c.text(cx(i), base + 73, f"{better[i]}% better", 12, SOFT, ha="center")
    c.save("fig7-final-test")


def figure8():
    rows = list(csv.DictReader(open("article/assets/flight2_jump.csv")))
    t = [float(r["t"]) for r in rows]
    step = [float(r["step"]) for r in rows]
    peak = max(range(len(step)), key=lambda i: step[i])
    left, right, y0, base = 56, 744, 40, 280
    X = lambda v: left + v / max(t) * (right - left)
    Y = lambda v: base - v / 100 * (base - y0)
    c = Canvas(332)
    c.title(8, "How far the estimate moved between photos in the one run of Flight 2 that jumped.")
    c.y_axis((0, 25, 50, 75, 100), Y, left, right, base, y0, "Step between photos (cm)")
    for v in range(0, int(max(t)) + 1, 20):
        c.line(X(v), base, X(v), base + 5)
        c.text(X(v), base + 19, str(v), ha="center")
    c.text((left + right) / 2, base + 40, "Time into the flight (s)", ha="center")
    c.path([X(v) for v in t], [Y(v) for v in step], INK, 1)
    c.text(X(t[peak]) + 8, Y(step[peak]) + 4, f"{step[peak]:.0f} cm jump at {t[peak]:.0f} s", 12, bold=True)
    c.text(X(100), Y(13), "Normal step: about 2.5 cm", 12, SOFT)
    c.save("fig8-silent-jump")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    figure1()
    figure2()
    figure3()
    figure4()
    figure5()
    figure6()
    figure7()
    figure8()
