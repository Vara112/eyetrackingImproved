
import cv2
import numpy as np

THRESHOLD_VAL   = 50
FRAME_HEIGHT    = 480
FRAME_WIDTH     = 640

#def process_frame():


def find_darkest_area(frame):
    '''
    Input:
        Gray scale frame
        
        
        Slide window across frame -> Sum windowSkip * window Area pixels -> Calculates if darkest window found

    Returns:
        Center of darkest window
    '''
    #Make sure values are multiples of the frame dimensions
    border          = 20             #Border around frame to be ignored
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

    return (centerX, centerY)


#def alt_pupil_detection(vidPtr):



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
