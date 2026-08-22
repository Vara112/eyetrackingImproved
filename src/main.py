
import cv2
import numpy as np

THRESHOLD_VAL = 65

def threshold_test(vidPtr):
    #cv2.namedWindow('controls')
    #cv2.createTrackbar('thresh', 'controls', 50, 255, lambda x: None)

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

                cv2.drawContours(dispFrame, [largestContour], -1, (255, 0, 0), 2)
                cv2.circle(dispFrame, (cx, cy), 5, (0, 0, 255), -1)



        cv2.imshow('frame', dispFrame)
        cv2.imshow('mask', mask)
        cv2.imshow('edges', edges)

        key = cv2.waitKey(30) & 0xFF 
        if key == ord('q'):
            vidPtr.release()
            cv2.destroyAllWindows()
            exit()


if __name__ == "__main__":
    '''
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 120)
    '''


    cap = cv2.VideoCapture('vids/normal.avi')

    threshold_test(cap)
