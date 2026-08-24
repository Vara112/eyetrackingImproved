import sys
import os

import cv2
import numpy as np
import random

from eyesphere_calc import ellipse_to_line, find_line_intersection, estimate_eye_center, update_eye_radius, center_is_stable
from pupil_tracking import process_frame
from gaze_calc import compute_gaze_vector

ray_lines = []                      #Accumulates confident ellipses over time
MAX_RAY_LINES = 100

PUPIL_CONFIDENCE_THRESHOLD_SPHERE = 0.65


#def alt_pupil_detection(vidPtr):


def visualize_test(cap):
    global ray_lines
    while True:

        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.rotate(frame, cv2.ROTATE_180)
        bestEllipse, (darkX, darkY), score, boundaryRatio = process_frame(frame)

        # Mark the darkest-area center (sanity check this is tracking the pupil)
        cv2.circle(frame, (darkX, darkY), 4, (0, 0, 255), -1)

        if bestEllipse is not None:
            cv2.ellipse(frame, bestEllipse, (0, 255, 0), 2)

            p1, p2 = ellipse_to_line(bestEllipse)
            cv2.line(frame, p1, p2, (255, 0, 255), 1)
            center = tuple(map(int, bestEllipse[0]))
            cv2.circle(frame, center, 3, (255, 255, 0), -1)


        if bestEllipse is not None and boundaryRatio > PUPIL_CONFIDENCE_THRESHOLD_SPHERE:   #TODO
            ray_lines.append(bestEllipse)
            if len(ray_lines) > MAX_RAY_LINES:
                ray_lines = ray_lines[-MAX_RAY_LINES:]
        eye_center = estimate_eye_center(frame.shape, ray_lines)
        if eye_center is not None:
            cv2.circle(frame, eye_center, 6, (255, 255, 0), -1)

        if bestEllipse is not None and boundaryRatio > PUPIL_CONFIDENCE_THRESHOLD_SPHERE and eye_center is not None:
            radius = update_eye_radius(eye_center, bestEllipse)
            if radius is not None:
                cv2.circle(frame, eye_center, int(radius), (255, 50, 50), 2) 


        if eye_center is not None and radius is not None and bestEllipse is not None:
            gaze = compute_gaze_vector(eye_center, radius, bestEllipse[0])
            if gaze is not None:
                # Draw the gaze direction as a line extending from eye_center
                end_x = int(eye_center[0] + gaze[0] * 100)
                end_y = int(eye_center[1] + gaze[1] * 100)
                cv2.line(frame, eye_center, (end_x, end_y), (0, 200, 255), 2)

                cv2.putText(frame, f"gaze: ({gaze[0]:.2f}, {gaze[1]:.2f}, {gaze[2]:.2f})",
                            (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 200, 255), 2)
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


def calibration(cap):

    global ray_lines

    eyeCenter = None
    radius = None

    while True:

        ret, frame = cap.read()

        if not ret:
            #Error when grabbing frame
            break
        
        frame = cv2.rotate(frame, cv2.ROTATE_180)   #Mounted upside-down (woops)

        bestEllipse, (darkX, darkY), score, boundaryRatio = process_frame(frame)

        if bestEllipse is not None:
            #Draw best fitting ellipse around pupil
            cv2.ellipse(frame, bestEllipse, (0, 255, 0), 2)
            p1, p2 = ellipse_to_line(bestEllipse)   #Grab ellipse direction line
            cv2.line(frame, p1, p2, (255, 0, 255), 1)

        if bestEllipse is not None and boundaryRatio > PUPIL_CONFIDENCE_THRESHOLD_SPHERE:  
            ray_lines.append(bestEllipse) #
            if len(ray_lines) > MAX_RAY_LINES:
                ray_lines = ray_lines[-MAX_RAY_LINES:]

        eye_center = estimate_eye_center(frame.shape, ray_lines)
        if eye_center is not None:
            #Draw current guess for eye sphere center
            cv2.circle(frame, eye_center, 6, (255, 255, 0), -1)

            if bestEllipse is not None and boundaryRatio > PUPIL_CONFIDENCE_THRESHOLD_SPHERE:
                radius = update_eye_radius(eye_center, bestEllipse) #Tries to update sphere radius if worthy ellipse
                if radius is not None:
                    cv2.circle(frame, eye_center, int(radius), (255, 50, 50), 2)

        stable = center_is_stable()
        if not stable:
            cv2.putText(frame, "Calibrating... keep looking around",(10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        else:
            cv2.putText(frame, "CALIBRATION COMPLETE. Press any key to continue...", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        cv2.imshow('Eye Tracker', frame)



        if cv2.waitKey(30) & 0xFF == ord('q'):
            return None, None  #Terminate
        
        key = cv2.waitKey(30) & 0xFF
        if key != 255 and stable:  #any key pressed
            break


if __name__ == "__main__":

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 120)
    

    #cap = cv2.VideoCapture('vids/eye_around.avi')

    calibration(cap)