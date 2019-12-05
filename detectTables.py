import cv2, os

def buscarTablas(path=''):
    # Read input image
    img = cv2.imread(path, cv2.IMREAD_COLOR)
    try:
        os.stat("data/")
    except:
        os.mkdir("data/")

    # Convert to gray scale image
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    # Simple threshold
    _, thr = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)

    # Morphological closing to improve mask
    close = cv2.morphologyEx(255 - thr, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)))

    # Find only outer contours
    contours, _ = cv2.findContours(close, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    # Save images for large enough contours
    areaThr = 3000
    i = 0
    saved = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if (area > areaThr):
            i = i + 1
            x, y, width, height = cv2.boundingRect(cnt)
            cv2.imwrite('data/output' + str(i) + '.png', img[y:y+height-1, x:x+width-1])
            saved.append('data/output' + str(i) + '.png')
    return saved