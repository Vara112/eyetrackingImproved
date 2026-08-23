
import cv2
import numpy as np

THRESHOLD_VAL   = 50
FRAME_HEIGHT    = 480
FRAME_WIDTH     = 640

MASK_SIZE = 150


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

def process_frame(frame):

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    (darkX, darkY), darkness = find_darkest_area(gray)

    threshStrict = bin_threshold(gray, darkness, 5)
    threshMed = bin_threshold(gray, darkness, 15)
    threshRelax = bin_threshold(gray, darkness, 25)

    threshStrict = mask_eye(threshStrict, darkX, darkY, MASK_SIZE)
    threshMed = mask_eye(threshMed, darkX, darkY, MASK_SIZE)
    threshRelax = mask_eye(threshRelax, darkX, darkY, MASK_SIZE)

    return threshStrict, threshMed, threshRelax   
    

#def alt_pupil_detection(vidPtr):

def threshold_test(cap):
    """
    Just for testing. Holds logic for displaying windows for the video
    """
    while True:
        ret, frame = cap.read()
        if not ret:
            break
 
        threshStrict,threshMed, threshRelax = process_frame(frame)
 
        cv2.imshow('Strict Threshold', threshStrict)
        cv2.imshow('Medium Threshold', threshMed)
        cv2.imshow('Relaxed Threshold', threshRelax)

        if cv2.waitKey(30) & 0xFF == ord('q'):
            break
 
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

    threshold_test(cap)
