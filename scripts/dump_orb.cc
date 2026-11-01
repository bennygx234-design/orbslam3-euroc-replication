// dump_orb.cc: shows what ORB-SLAM3's camera side "sees" in one moment of a flight.
// It runs ORB-SLAM3's own corner finder (src/ORBextractor.cc, compiled in unchanged)
// with the same settings as Examples/Stereo-Inertial/EuRoC.yaml, on:
//   - the left photo, the right photo (same instant), and the left photo 1 second later.
// Like ORB-SLAM3, it first straightens ("rectifies") the photos so a point in the left
// photo sits on the same row in the right photo.
// It writes the straightened photos, every corner + its 256-bit fingerprint, and the matches.
//
// Usage: dump_orb <EuRoC.yaml> <left.png> <right.png> <later_left.png> <output folder>
#include <fstream>
#include <iostream>
#include <opencv2/core.hpp>
#include <opencv2/calib3d.hpp>
#include <opencv2/features2d.hpp>
#include <opencv2/imgcodecs.hpp>
#include <opencv2/imgproc.hpp>
#include "ORBextractor.h"

using namespace std;

// Writes one line per corner: x y pyramid_level angle size, then the 32 fingerprint bytes
static void saveCorners(const string& path, const vector<cv::KeyPoint>& keys, const cv::Mat& desc) {
    ofstream out(path);
    for (size_t i = 0; i < keys.size(); i++) {
        const cv::KeyPoint& k = keys[i];
        out << k.pt.x << " " << k.pt.y << " " << k.octave << " " << k.angle << " " << k.size;
        for (int b = 0; b < 32; b++) out << " " << (int)desc.at<uchar>(i, b);
        out << "\n";
    }
}

int main(int argc, char** argv) {
    if (argc != 6) { cerr << "usage: dump_orb <yaml> <left> <right> <later_left> <outdir>\n"; return 1; }
    string outdir = argv[5];

    // 1. Read the camera measurements from the same settings file ORB-SLAM3 uses
    cv::FileStorage fs(argv[1], cv::FileStorage::READ);
    cv::Mat K1 = (cv::Mat_<double>(3, 3) << (double)fs["Camera1.fx"], 0, (double)fs["Camera1.cx"],
                                            0, (double)fs["Camera1.fy"], (double)fs["Camera1.cy"], 0, 0, 1);
    cv::Mat K2 = (cv::Mat_<double>(3, 3) << (double)fs["Camera2.fx"], 0, (double)fs["Camera2.cx"],
                                            0, (double)fs["Camera2.fy"], (double)fs["Camera2.cy"], 0, 0, 1);
    cv::Mat D1 = (cv::Mat_<double>(4, 1) << (double)fs["Camera1.k1"], (double)fs["Camera1.k2"],
                                            (double)fs["Camera1.p1"], (double)fs["Camera1.p2"]);
    cv::Mat D2 = (cv::Mat_<double>(4, 1) << (double)fs["Camera2.k1"], (double)fs["Camera2.k2"],
                                            (double)fs["Camera2.p1"], (double)fs["Camera2.p2"]);
    cv::Mat T12;                                   // where the right camera sits relative to the left
    fs["Stereo.T_c1_c2"] >> T12;
    T12.convertTo(T12, CV_64F);
    cv::Mat T21 = T12.inv();                       // ORB-SLAM3 passes the inverse (Settings.cc)
    cv::Mat R = T21(cv::Rect(0, 0, 3, 3)).clone(), t = T21(cv::Rect(3, 0, 1, 3)).clone();
    cv::Size size((int)fs["Camera.width"], (int)fs["Camera.height"]);

    // 2. Straighten the photos exactly the way Settings::precomputeRectificationMaps does
    cv::Mat R1, R2, P1, P2, Q, M1l, M2l, M1r, M2r;
    cv::stereoRectify(K1, D1, K2, D2, size, R, t, R1, R2, P1, P2, Q, cv::CALIB_ZERO_DISPARITY, -1, size);
    cv::initUndistortRectifyMap(K1, D1, R1, P1.rowRange(0, 3).colRange(0, 3), size, CV_32F, M1l, M2l);
    cv::initUndistortRectifyMap(K2, D2, R2, P2.rowRange(0, 3).colRange(0, 3), size, CV_32F, M1r, M2r);
    cv::Mat left, right, later;
    cv::remap(cv::imread(argv[2], cv::IMREAD_GRAYSCALE), left, M1l, M2l, cv::INTER_LINEAR);
    cv::remap(cv::imread(argv[3], cv::IMREAD_GRAYSCALE), right, M1r, M2r, cv::INTER_LINEAR);
    cv::remap(cv::imread(argv[4], cv::IMREAD_GRAYSCALE), later, M1l, M2l, cv::INTER_LINEAR);
    cv::imwrite(outdir + "/rect_left.png", left);
    cv::imwrite(outdir + "/rect_right.png", right);
    cv::imwrite(outdir + "/rect_later.png", later);

    // 3. Find corners with ORB-SLAM3's own finder: 1200 corners, 8 zoom levels each 1.2x smaller,
    //    FAST threshold 20 (drops to 7 in dull areas). Same numbers as EuRoC.yaml.
    ORB_SLAM3::ORBextractor finder(fs["ORBextractor.nFeatures"], fs["ORBextractor.scaleFactor"],
                                   fs["ORBextractor.nLevels"], fs["ORBextractor.iniThFAST"],
                                   fs["ORBextractor.minThFAST"]);
    vector<int> noOverlap = {0, 0};                // pinhole cameras: no fisheye overlap zone
    vector<cv::KeyPoint> kL, kR, kN;
    cv::Mat dL, dR, dN;
    finder(left, cv::Mat(), kL, dL, noOverlap);
    finder(right, cv::Mat(), kR, dR, noOverlap);
    finder(later, cv::Mat(), kN, dN, noOverlap);
    saveCorners(outdir + "/corners_left.txt", kL, dL);
    saveCorners(outdir + "/corners_right.txt", kR, dR);
    saveCorners(outdir + "/corners_later.txt", kN, dN);

    // 4. Left vs right: same corner must sit on (almost) the same row, shifted left in the right photo
    double fx = P1.at<double>(0, 0), baseline = cv::norm(t);
    ofstream st(outdir + "/stereo_matches.txt");
    int nStereo = 0;
    for (size_t i = 0; i < kL.size(); i++) {
        int best = 256, second = 256, bestJ = -1;
        for (size_t j = 0; j < kR.size(); j++) {
            float dy = fabs(kL[i].pt.y - kR[j].pt.y), d = kL[i].pt.x - kR[j].pt.x;
            if (dy > 2.0f * pow(1.2f, kL[i].octave) || d <= 0 || d > fx) continue;
            int h = (int)cv::norm(dL.row(i), dR.row(j), cv::NORM_HAMMING);
            if (h < best) { second = best; best = h; bestJ = (int)j; } else if (h < second) second = h;
        }
        if (bestJ >= 0 && best < 75 && best < 0.8 * second) {   // 75 = ORB-SLAM3's stereo threshold
            st << i << " " << bestJ << " " << kL[i].pt.x - kR[bestJ].pt.x << " " << best << "\n";
            nStereo++;
        }
    }

    // 5. Now vs 1 second later: find each corner again by its fingerprint, then keep only
    //    matches that agree with one single camera motion (RANSAC throws out the odd ones)
    cv::BFMatcher matcher(cv::NORM_HAMMING);
    vector<vector<cv::DMatch>> knn;
    matcher.knnMatch(dL, dN, knn, 2);
    vector<cv::DMatch> good;
    vector<cv::Point2f> a, b;
    for (auto& m : knn)
        if (m.size() == 2 && m[0].distance < 50 && m[0].distance < 0.8 * m[1].distance) {  // 50 = ORB-SLAM3's TH_LOW
            good.push_back(m[0]);
            a.push_back(kL[m[0].queryIdx].pt);
            b.push_back(kN[m[0].trainIdx].pt);
        }
    vector<uchar> inlier;
    cv::findFundamentalMat(a, b, cv::FM_RANSAC, 1.0, 0.999, inlier);
    ofstream tr(outdir + "/track_matches.txt");
    int nTrack = 0;
    for (size_t k = 0; k < good.size(); k++)
        if (inlier[k]) { tr << good[k].queryIdx << " " << good[k].trainIdx << " " << good[k].distance << "\n"; nTrack++; }

    ofstream info(outdir + "/info.txt");
    info << fx << " " << baseline << "\n";
    cout << "corners: left " << kL.size() << ", right " << kR.size() << ", 1 s later " << kN.size() << "\n"
         << "left-right matches: " << nStereo << ", found again 1 s later: " << nTrack << "\n"
         << "focal length " << fx << " px, camera gap " << baseline << " m\n";
    return 0;
}
