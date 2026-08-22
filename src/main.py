
import cv2
import numpy as np



def threshold_test(vidPtr):
    cv2.namedWindow('controls')
    cv2.createTrackbar('thresh', 'controls', 50, 255, lambda x: None)

    while True:
        ret, frame = vidPtr.read()

        if not ret:
            #if frame was failed to be pulled
            print("Error pulling frame")
            break

        #Cam is upside down TODO
        #frame = cv2.rotate(frame, cv2.ROTATE_180)

        threshVal = cv2.getTrackbarPos('thresh', 'controls') #Takes the value from slider
        #50 seems to work the best
        
        #print(threshVal)
        _, mask = cv2.threshold(frame, threshVal, 255, cv2.THRESH_BINARY_INV)



        #Edge finding

        edges = cv2.Canny(mask, 0, 255, 3)  #3 is default (aperturesize not sure what that does)




        cv2.imshow('frame', frame)
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
