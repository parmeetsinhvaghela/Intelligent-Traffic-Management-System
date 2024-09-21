import cv2
import numpy as np
import package.const as const


class ImageProc:
    def run(self):
        a = getImageDensity('A')
        b = getImageDensity('B')
        c = getImageDensity('C')
        d = getImageDensity('D')
        return getCountdownTime(a, b, c, d)


def getImageDensity(side):
    img = loadImg('C:\\Users\\Darshan\\Desktop\\proj TEST\\images\\' + side + '.jpg')
    baseImg = loadImg('C:\\Users\\Darshan\\Desktop\\proj TEST\\images\\base\\' + side + '.jpg')
    img = ptsCrop(img, side)
    baseImg = ptsCrop(baseImg, side)
    canvas = diffImg(img, baseImg)
    density = diffDensity(canvas, side)
    return density


def loadImg(path):
    return cv2.imread(path)


def showImg(img):
    cv2.imshow('Title', img)
    cv2.waitKey(0)


def ptsCrop(image, side):
    pts = np.array(const.pts[side], np.int32)
    pts = pts.reshape((-1, 1, 2))
    cv2.polylines(image, [pts], True, (0, 255, 0))
    rect = cv2.boundingRect(pts)
    x, y, w, h = rect
    image = image[y:y + h, x:x + w]
    return image


def diffImg(img, baseImg):
    diff = cv2.absdiff(img, baseImg)
    mask = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    th = 2
    imask = mask > th
    canvas = np.zeros_like(baseImg, np.uint8)
    canvas[imask] = baseImg[imask]
    canvas = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
    return canvas


def diffDensity(canvas, side):
    roadPixels = roadPixel(canvas, side)
    vehiclePixels = vehiclePixel(canvas, side)
    density = vehiclePixels / roadPixels
    return density


def roadPixel(canvas, side):
    canvas = getMask(canvas, side)
    count = cv2.countNonZero(canvas)
    return count


def vehiclePixel(canvas, side):
    mask = getMask(canvas, side)
    canvas = cv2.bitwise_and(canvas, mask)
    count = cv2.countNonZero(canvas)
    return count


def getMask(canvas, side):
    pts = np.array(const.pts[side], np.int32)
    pts = pts.reshape((-1, 1, 2))
    pts = pts - pts.min(axis=0)
    mask = np.zeros(canvas.shape[:2], np.uint8)
    mask.fill(0)
    cv2.fillPoly(mask, [pts], 255)
    return mask


def getCountdownTime(a, b, c, d):
    minTime = 40
    maxTime = 168
    totalDensity = 1 * 4
    errorTime = 2 * 4
    averageDensity = (a + b + c + d) / totalDensity
    cycleTime = averageDensity * maxTime
    if cycleTime > maxTime:
        cycleTime = maxTime
    elif cycleTime < minTime:
        cycleTime = minTime
    cycleTime -= errorTime
    inputdensity = [a, b, c, d]
    sumDensity = sum(inputdensity)
    countdownTimes = [0] * len(inputdensity)
    minCountdownTime = int((minTime - errorTime) / 4)
    for i in range(len(inputdensity)):
        if inputdensity[i] != 0:
            countdownTimes[i] = int((inputdensity[i] * cycleTime / sumDensity) / 5) * 5
        if countdownTimes[i] < minCountdownTime:
            countdownTimes[i] = minCountdownTime
    cycleTime = sum(countdownTimes) + errorTime
    return countdownTimes, cycleTime
