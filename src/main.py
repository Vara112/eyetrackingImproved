
import cv2
import numpy as np

THRESHOLD_VAL   = 50
FRAME_HEIGHT    = 480
FRAME_WIDTH     = 640

def threshold_test(vidPtr):
    #cv2.namedWindow('controls')
    #cv2.createTrackbar('thresh', 'controls', 50, 255, lambda x: None)

    prevCenter = None
    maxJump = 150    #TODO

    
    while True:
        ret, frame = vidPtr.read()

        if not ret:
            #if frame was failed to be pulled
            print("Error pulling frame")
            break

        #Cam is upside down TODO
        #frame = cv2.rotate(frame, cv2.ROTATE_180)

        #threshVal = cv2.getTrackbarPos('thresh', 'controls') #Takes the value from slider
        #50 seems to work the best

        #print(threshVal)
        _, mask = cv2.threshold(frame, THRESHOLD_VAL, 255, cv2.THRESH_BINARY_INV)


        #Dark shadow in corner causing issues, so 0 the top right so contour doesnt pick it up
        h, w = mask.shape[:2]
        mask[0:100, w-100:w] = 0


        #Edge finding

        edges = cv2.Canny(mask, 0, 255, 3)  #3 is default (aperturesize not sure what that does)


        contours, hierarchy = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        #Not sure if hierarchy is needed. Maybe for some filtering later?

        dispFrame = frame.copy()

        if contours:
            #Theoretically the largest contour will be the pupil
            largestContour = max(contours, key=cv2.contourArea)

            #Tries to smooth out noise (spatial noise rejection)
            M = cv2.moments(largestContour)
            if M['m00'] != 0:
                cx = int(M['m10'] / M['m00'])
                cy = int(M['m01'] / M['m00'])


                realisticJump = True
                if prevCenter is not None:
                    dist = ((cx - prevCenter[0])**2 + (cy - prevCenter[1])**2) ** 0.5   #Calcs distance of pupil jump
                    if dist > maxJump:
                        realisticJump = False #Too far
                
                if realisticJump:
                    prevCenter = (cx, cy)
                    if len(largestContour) >= 5:
                        ellipse = cv2.fitEllipse(largestContour)
                        cv2.ellipse(dispFrame, ellipse, (0, 255, 0), 2)
                        cv2.circle(dispFrame, prevCenter, 5, (0, 0, 255), -1)
                    else: #Rejected
                        if prevCenter is not None:

                            cv2.circle(dispFrame, prevCenter, 5, (0, 165, 255), -1)     #Make orange to show using old data DEBUGGING




        cv2.imshow('frame', dispFrame)
        cv2.imshow('mask', mask)
        cv2.imshow('edges', edges)

        key = cv2.waitKey(30) & 0xFF 
        if key == ord('q'):
            vidPtr.release()
            cv2.destroyAllWindows()
            exit()

def process_frame():


def find_darkest_area(frame):
    '''
    Input:
        Gray scale frame
        
        
        Slide window across frame -> Sum windowSkip * window Area pixels -> Calculates if darkest window found

    Returns:
        Center of darkest window
    '''
    border          = 20             #Border around frame to be ignored
    windowSize      = 20             #Window size used for scanning
    windowSkip      = 10             #How far the window can jump when scanning (windowSkip < windowSize = overlapping scanning)
    innerWindowSkip = 5              #Step size for within a window

    #frame[y, x]

    for y in range(FRAME_HEIGHT)



def alt_pupil_detection(vidPtr):



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
