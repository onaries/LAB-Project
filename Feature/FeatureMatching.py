import numpy
import cv2

import sys
import random
import glob
from matplotlib import pyplot

def match_images(img1, img2):
    """Given two images, returns the matches"""
    detector = cv2.SURF(400, 5, 5)
    matcher = cv2.BFMatcher(cv2.NORM_L2)

    kp1, desc1 = detector.detectAndCompute(img1, None)
    print len(kp1)
    kp2, desc2 = detector.detectAndCompute(img2, None)
    # print 'img1 - %d features, img2 - %d features' % (len(kp1), len(kp2))

    raw_matches = matcher.knnMatch(desc1, trainDescriptors=desc2, k=2)  # 2
    kp_pairs = filter_matches(kp1, kp2, raw_matches)
    return kp_pairs

def filter_matches(kp1, kp2, matches, ratio=0.75):
    mkp1, mkp2 = [], []
    for m in matches:
        if len(m) == 2 and m[0].distance < m[1].distance * ratio:
            m = m[0]
            mkp1.append(kp1[m.queryIdx])
            mkp2.append(kp2[m.trainIdx])
    kp_pairs = zip(mkp1, mkp2)
    return kp_pairs

def explore_match(win, img1, img2, kp_pairs, status=None, H=None):
    h1, w1 = img1.shape[:2]
    h2, w2 = img2.shape[:2]
    vis = numpy.zeros((max(h1, h2), w1 + w2), numpy.uint8)
    # vis = numpy.zeros((h1, w1), numpy.uint8)
    vis[:h1, :w1] = img1
    vis[:h2, w1:w1 + w2] = img2
    vis = cv2.cvtColor(vis, cv2.COLOR_GRAY2BGR)

    if H is not None:
        corners = numpy.float32([[0, 0], [w1, 0], [w1, h1], [0, h1]])
        corners = numpy.int32(cv2.perspectiveTransform(corners.reshape(1, -1, 2), H).reshape(-1, 2) + (w1, 0))
        cv2.polylines(vis, [corners], True, (255, 255, 255))

    if status is None:
        status = numpy.ones(len(kp_pairs), numpy.bool_)
    p1 = numpy.int32([kpp[0].pt for kpp in kp_pairs])
    p2 = numpy.int32([kpp[1].pt for kpp in kp_pairs]) + (w1, 0)

    random_color = (random.randrange(0,255), random.randrange(0,255), random.randrange(0,255))
    green = (0, 255, 0)
    green = random_color
    red = (0, 0, 255)
    white = (255, 255, 255)
    kp_color = (51, 103, 236)
    for (x1, y1), (x2, y2), inlier in zip(p1, p2, status):
        if inlier:
            col = green
            cv2.circle(vis, (x1, y1), 2, col, -1)
            # cv2.circle(vis, (x2, y2), 2, col, -1)
        else:
            col = red
            r = 2
            thickness = 3

            cv2.line(vis, (x1 - r, y1 - r), (x1 + r, y1 + r), col, thickness)
            cv2.line(vis, (x1 - r, y1 + r), (x1 + r, y1 - r), col, thickness)
            cv2.line(vis, (x2 - r, y2 - r), (x2 + r, y2 + r), col, thickness)
            cv2.line(vis, (x2 - r, y2 + r), (x2 + r, y2 - r), col, thickness)
    vis0 = vis.copy()
    for (x1, y1), (x2, y2), inlier in zip(p1, p2, status):
        if inlier:
            random_color = (random.randrange(0, 255), random.randrange(0, 255), random.randrange(0, 255))
            green = random_color
            cv2.line(vis, (x1, y1), (x2, y2), green, 2)

    # cv2.imshow(win, vis)

    pyplot.imshow(vis)
    pyplot.show()

def draw_matches(window_name, kp_pairs, img1, img2):
    """Draws the matches for """
    mkp1, mkp2 = zip(*kp_pairs)

    p1 = numpy.float32([kp.pt for kp in mkp1])
    p2 = numpy.float32([kp.pt for kp in mkp2])

    if len(kp_pairs) >= 4:
        H, status = cv2.findHomography(p1, p2, cv2.RANSAC, 5.0)
        # print '%d / %d  inliers/matched' % (numpy.sum(status), len(status))


        dst = cv2.warpPerspective(img1, H, (300, 225))
        # cv2.imshow("test", dst)

        pyplot.gray()
        pyplot.imshow(dst)
        pyplot.show()

        # im2 = cv2.warpPerspective(img2, H, numpy.array([1000, 750]))
        # cv2.imshow('test', im2)

    else:
        H, status = None, None
        # print '%d matches found, not enough for homography estimation' % len(p1)

    if len(p1):
        explore_match(window_name, img1, img2, kp_pairs, status, H)


if __name__ == '__main__':

    img_list = glob.glob('../data/images/marker/*')

    img1 = cv2.imread('../data/images/marker/right5.png', 0)
    img2 = cv2.imread('../data/images/test/test2.jpg', 0)

    # img1 = cv2.imread('../data/images/marker/front1.png', 0)
    # img2 = cv2.imread('../data/images/test/test4.png', 0)

    # img1 = cv2.imread('../data/images/marker/left2.png', 0)
    # img2 = cv2.imread('../data/images/test/test7.png', 0)

    if img1 is None:
        print 'Failed to load img1', img1
        sys.exit(1)

    if img2 is None:
        print 'Failed to load img2', img2
        sys.exit(1)

    kp_pairs = match_images(img1, img2)

    if kp_pairs:
        draw_matches('test', kp_pairs, img1, img2)
        cv2.waitKey()
        cv2.destroyAllWindows()
