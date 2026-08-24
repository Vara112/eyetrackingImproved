import sys
import os

import cv2
import numpy as np
import random

from eyesphere_calc import ellipse_to_line, find_line_intersection, estimate_eye_center, distance_to_pupil_outer_edge
from pupil_tracking import process_frame



ray_lines = []                              #Accumulates confident ellipses over time
MAX_RAY_LINES = 100

PUPIL_CONFIDENCE_THRESHOLD_SPHERE = 0.65


#def alt_pupil_detection(vidPtr):


def visualize_test(cap):
    global ray_lines
    while True:
        ret, frame = cap.read()
        if not ret:
            break

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
            if bestEllipse is not None:
                distance_to_pupil_outer_edge(eye_center, bestEllipse)

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


    cap = cv2.VideoCapture('vids/eye_around.avi')

    visualize_test(cap)

