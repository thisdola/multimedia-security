import cv2
import numpy as np

def image_colorfulness(image,B,G,R):
    # Use OpenCV methods wherever possible
    rg = cv2.absdiff(R,G)
    rgMean, rgStd  = cv2.meanStdDev(rg)

    avg = cv2.addWeighted(R, 0.5, G, 0.5, 0)
    yb  = cv2.absdiff(avg, B)
    ybMean, ybStd  = cv2.meanStdDev(yb)

    # combine the mean and standard deviations
    stdRoot = np.sqrt((rgStd ** 2) + (ybStd ** 2))
    meanRoot = np.sqrt((rgMean ** 2) + (ybMean ** 2))
    # derive the "colorfulness" metric and return it
    return stdRoot + (0.3 * meanRoot), rgMean, rgStd, ybMean, ybStd