
import cv2
import numpy as np
import random
import math


def compute_gaze_vector(eyeCenter, radius, pupilCenter):
    '''
        Casting the x and y onto a 3d sphere. 
        We know dx and dy relative to the spheres radius, therefore:
        dz = sqrt(1 - dy^2 - dy^2) (the point needs to actually lie on the sphere, not on a 2D plane)
    
    '''

    if radius <= 0:
        return None
    
    dx = (pupilCenter[0] - eyeCenter[0]) / radius
    dy = (pupilCenter[1] - eyeCenter[1]) / radius  

    #Clamp for if point exceeds speheres edge 
    r2 = dx**2 + dy**2
    if r2 > 1.0:
        norm = np.sqrt(r2)
        dx, dy = dx / norm, dy / norm
        r2 = 1.0

    dz = np.sqrt(max(0.0, 1.0 - r2))

    gaze = np.array([dx, dy, dz])
    return gaze / np.linalg.norm(gaze)