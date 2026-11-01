// dark_corners.cc: what ORB-SLAM3's corner finder picks out in one dark photo, three ways:
//   normal (1200 corners), 2000 corners (Benny's version), and contrast boost (CLAHE 3.0, 8x8) + 1200 corners.
// Uses ORB-SLAM3's own src/ORBextractor.cc, unchanged, with the EuRoC.yaml settings.
// Usage: dark_corners <EuRoC.yaml> <photo.png> <output folder>
#include <fstream>
#include <iostream>
#include <opencv2/core.hpp>
#include <opencv2/imgcodecs.hpp>
#include <opencv2/imgproc.hpp>
#include "ORBextractor.h"

using namespace std;

// Runs the corner finder with a given corner limit and writes x y pyramid_level per corner
static void findAndSave(const cv::Mat& im, int nFeatures, cv::FileStorage& fs, const string& path) {
    ORB_SLAM3::ORBextractor finder(nFeatures, fs["ORBextractor.scaleFactor"], fs["ORBextractor.nLevels"],
                                   fs["ORBextractor.iniThFAST"], fs["ORBextractor.minThFAST"]);
    vector<cv::KeyPoint> keys;
    cv::Mat desc;
    vector<int> noOverlap = {0, 0};
    finder(im, cv::Mat(), keys, desc, noOverlap);
    ofstream out(path);
    for (const cv::KeyPoint& k : keys) out << k.pt.x << " " << k.pt.y << " " << k.octave << "\n";
    cout << path << ": " << keys.size() << " corners" << endl;
}

int main(int argc, char** argv) {
    if (argc != 4) { cerr << "usage: dark_corners <yaml> <photo> <outdir>\n"; return 1; }
    cv::FileStorage fs(argv[1], cv::FileStorage::READ);
    string outdir = argv[3];
    cv::Mat photo = cv::imread(argv[2], cv::IMREAD_GRAYSCALE);
    cv::Mat boosted;
    cv::createCLAHE(3.0, cv::Size(8, 8))->apply(photo, boosted);   // the Day 2 contrast boost
    cv::imwrite(outdir + "/photo.png", photo);
    cv::imwrite(outdir + "/photo_boosted.png", boosted);
    findAndSave(photo, 1200, fs, outdir + "/corners_normal.txt");
    findAndSave(photo, 2000, fs, outdir + "/corners_2000.txt");
    findAndSave(boosted, 1200, fs, outdir + "/corners_boosted.txt");
    return 0;
}
