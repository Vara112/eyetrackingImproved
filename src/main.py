
import cv2
import numpy as np

THRESHOLD_VAL   = 50
FRAME_HEIGHT    = 480
FRAME_WIDTH     = 640

MASK_SIZE = 150

CORNER_BLOCK_WIDTH  = 100                   #There is an issue with the top right of each frame being detected as a pupil
CORNER_BLOCK_HEIGHT = 100                   #Bandaid fix: Chop that part of the frame off


def block_top_right(frame):
    """
    Sets the top-right rectangular region of a grayscale frame to white (255) so 
    it is ignored in calculations
 
    Inputs:
        frame: grayscale frame numpy array
        width, height: size in pixels of the corner region to block, measured
                        from the top-right corner inward
    Output:
        frame with the top-right corner blanked out
    """
    frame[0:CORNER_BLOCK_HEIGHT, frame.shape[1] - CORNER_BLOCK_WIDTH:frame.shape[1]] = 255
    return frame



def find_darkest_area(frame):
    '''
    Input:
        Gray scale frame
        
        
        Slide window across frame -> Sum windowSkip * window Area pixels -> Calculates if darkest window found

    Returns:
        Center of darkest window + average darkest value of that window
    '''
    #Make sure values are multiples of the frame dimensions
    border          = 30             #Border around frame to be ignored
    windowSize      = 20             #Window size used for scanning
    windowSkip      = 10             #How far the window can jump when scanning (windowSkip < windowSize = overlapping scanning)
    #innerWindowSkip = 5              #Step size for within a window

    #frame[y, x]

    integral = cv2.integral(frame)                                          #Pre-processing

    #calc the last top left of a window that is valid (prevent indexing out of bounds)
    lastY = FRAME_HEIGHT - border - windowSize                              
    lastX = FRAME_WIDTH - border - windowSize

    #Returns arrays for all valid window frame top-left corners up until last window
    windowsY = np.arange(border, lastY + 1, windowSkip)
    windowsX = np.arange(border, lastX + 1, windowSkip)

    #To avoid issues where windowSkip doesnt divide evenly into frame size
    if windowsY[-1] != lastY: windowsY = np.append(windowsY, lastY)
    if windowsX[-1] != lastX: windowsX = np.append(windowsX, lastX)

    #Create 4 2D arrays. X/Y left most point, and X/Y right most point per window i
    YLeft, XLeft = np.meshgrid(windowsY, windowsX, indexing='ij')
    YRight, XRight = YLeft + windowSize, XLeft + windowSize


    #Use inclusion-exclusion sum to only return bounds 
    A = integral[YLeft, XLeft]
    B = integral[YLeft, XRight]
    C = integral[YRight, XLeft]
    D = integral[YRight, XRight]
    windowSums = D - B - C + A

    #Find darkest window
    darkY, darkX = np.unravel_index(np.argmin(windowSums), windowSums.shape)


    centerX = windowsX[darkX] + windowSize // 2
    centerY = windowsY[darkY] + windowSize // 2

    avgDark = windowSums[darkY, darkX]/(windowSize * windowSize)

    return (centerX, centerY), avgDark


def bin_threshold(frame, darkestVal, addedThreshold):
    """
    Applies a tailored threshold filter to a frame

    Inputs:
        frame: frame numpy array
        darkestVal: The 'estimated' darkest value of the frame
        addedThreshold: Some value to be added to the threshold
    
    Output:
        threshFrame: The frame with threshold applied
    """

    threshold = darkestVal + addedThreshold
    _, threshFrame = cv2.threshold(frame, threshold, 255, cv2.THRESH_BINARY_INV)
    return threshFrame


def mask_eye(frame, x, y, size):
    """
    There can be random noise caused from shadows and other interference. This function aims to reduce that by applying
    a mask around the center of the darkest area.

    Inputs:
        frame: frame numpy array
        x, y: x and y cords for the middle of the darkest window found earlier
        size: Size of the mask to be applied around the center
    
    Output:
        frame with data around the center of darkest area removed
    """   

    mask = np.zeros_like(frame)         #2D array of 0's to match frame size

    leftX = x-(size//2) if x-(size//2) > 0 else 0
    leftY = y-(size//2) if y-(size//2) > 0 else 0

    rightX = x+(size//2) if x+(size//2) < frame.shape[1] else frame.shape[1]
    rightY = y+(size//2) if y+(size//2) < frame.shape[0] else frame.shape[0]

    mask[leftY:rightY, leftX:rightX] = 255

    return cv2.bitwise_and(frame, mask)


def largest_contour(contours, pixelThresh, ratio):

    maxFound = 0
    maxContour = None

    for contour in contours:
        area = cv2.contourArea(contour)

        if area >= pixelThresh:
            x, y, w, h = cv2.boundingRect(contour)
            
            if max(w/h, h/w) <= ratio:

                if area > maxFound:
                    maxFound = area
                    maxContour = contour
    
    return maxContour


def check_ellipse_area_quality(frame, contour):

    ellipseQuality = 0

    ellipse = cv2.fitEllipse(contour)


    mask = np.zeros_like(frame)
    cv2.ellipse(mask, ellipse, (255), -1)

    ellipseArea = np.sum(mask == 255)
    covered_pixels = np.sum((frame == 255) & (mask == 255))         #Tellys up all pixels of elipse that is actually placed on a white pixel

    if ellipseArea == 0:
        return ellipseQuality

    ellipseQuality = covered_pixels / ellipseArea                                       #Ratio of inside the ellipse actually on the threshold
    return ellipseQuality


def check_ellipse_boundary_quality(contour, imgShape):

    contourMask = np.zeros(imgShape, dtype=np.uint8)
    cv2.drawContours(contourMask, [contour], -1, 255, 1)

    ellipse = cv2.fitEllipse(contour)
    ellipse_mask_thick = np.zeros(imgShape, dtype=np.uint8)
    ellipse_mask_thin = np.zeros(imgShape, dtype=np.uint8)
    cv2.ellipse(ellipse_mask_thick, ellipse, 255, 10)
    cv2.ellipse(ellipse_mask_thin, ellipse, 255, 4)

    thickCount = np.sum(cv2.bitwise_and(contourMask, ellipse_mask_thick) > 0)
    thinCount = np.sum(cv2.bitwise_and(contourMask, ellipse_mask_thin) > 0)

    total_border_pixels = np.sum(contourMask > 0)
    ratio_under_ellipse = thinCount / total_border_pixels if total_border_pixels > 0 else 0

    return thickCount, ratio_under_ellipse



def process_frame(frame):

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = block_top_right(gray)

    (darkX, darkY), darkness = find_darkest_area(gray)

    threshStrict = bin_threshold(gray, darkness, 5)
    threshMed = bin_threshold(gray, darkness, 15)
    threshRelax = bin_threshold(gray, darkness, 25)

    threshStrict = mask_eye(threshStrict, darkX, darkY, MASK_SIZE)
    threshMed = mask_eye(threshMed, darkX, darkY, MASK_SIZE)
    threshRelax = mask_eye(threshRelax, darkX, darkY, MASK_SIZE)

    #return threshStrict, threshMed, threshRelax

    kernel = np.ones((5, 5), np.uint8)   #Grow why by roughly 2
    bestScore = 0
    bestEllipse = None
    for img in [threshStrict, threshMed, threshRelax]:

        dilate = cv2.dilate(img, kernel, iterations=2)  #Maybe help with artifacting?
        contours, _ = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        contour = largest_contour(contours, pixelThresh=1000, ratio=3)  #TODO tweak values

        if contour is None or len(contour) < 5:
            continue

        areaQuality = check_ellipse_area_quality(dilate, contour)
        thickCount, boundaryRatio = check_ellipse_boundary_quality(contour, dilate.shape)

        score = areaQuality * (thickCount ** 2) * boundaryRatio

        if score > bestScore:
            bestScore = score
            bestEllipse = cv2.fitEllipse(contour)

    return bestEllipse, (darkX, darkY), bestScore
    

#def alt_pupil_detection(vidPtr):

def visualize_test(cap):
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        bestEllipse, (darkX, darkY), score = process_frame(frame)

        # Mark the darkest-area center (sanity check this is tracking the pupil)
        cv2.circle(frame, (darkX, darkY), 4, (0, 0, 255), -1)

        if bestEllipse is not None:
            cv2.ellipse(frame, bestEllipse, (0, 255, 0), 2)
            center = tuple(map(int, bestEllipse[0]))
            cv2.circle(frame, center, 3, (255, 255, 0), -1)

        cv2.putText(frame, f"score: {score:.2f}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        cv2.imshow('Pupil Detection', frame)

        key = cv2.waitKey(30) & 0xFF
        if key == ord('q'):
            break
        elif key == ord(' '):
            cv2.waitKey(0)  # pause on spacebar

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    '''
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 120)
    '''


    cap = cv2.VideoCapture('vids/eye_normal.avi')

    visualize_test(cap)

