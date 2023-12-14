import cv2
import numpy as np
from scipy import ndimage

def correct_skew(image, delta=1, limit=30):
    def determine_score(arr, angle):
        data = ndimage.rotate(arr, angle, reshape=False, order=0)
        histogram = np.sum(data, axis=1, dtype=float)
        score = np.sum((histogram[1:] - histogram[:-1]) ** 2, dtype=float)
        return histogram, score

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # show(gray)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1] 
    # show(thresh)

    scores = []
    angles = np.arange(-limit, limit + delta, delta)
    for angle in angles:
        histogram, score = determine_score(thresh, angle)
        scores.append(score)

    best_angle = angles[scores.index(max(scores))]

    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, best_angle, 1.0)
    corrected = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    return best_angle, corrected

def show(img):
    cv2.imshow('corrected', img)
    cv2.waitKey()
    

if __name__ == '__main__':
    imagename = "000000000034267_005.jpg"
    image = cv2.imread(f'./EasyOCR/demo/{imagename}')
    image = cv2.resize(image, dsize=(0, 0), fx=0.3,fy=0.3)
    angle, corrected = correct_skew(image)
    print('Skew angle:', angle)
    show(corrected)
    cv2.imwrite(f'rotated_{imagename}', corrected)