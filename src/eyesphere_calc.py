
import cv2
import numpy as np
import random





stored_intersections = []
MAX_STORED_INTERSECTIONS = 1500
MIN_ANGLE_DIFF = 8                          #Ignore ellipses with similar angles 
PIXEL_AGREEMENT_LIMIT = 30



def ellipse_to_line(ellipse, length=200):
    """
    Returns two points defining a line through the ellipse center oriented along its angle 

    The gaze line seems to always pass through (or get close) to a point roughly in the center.
    We need to estimate that point which will be used as our eye center.

    """
    (cx, cy), (_, minor_axis), angle = ellipse
    angleRad = np.deg2rad(angle)

    dx = np.cos(angleRad)
    dy = np.sin(angleRad)

    #p1 = (c_x - length * cos(Theta), cy - length*sin(theta))
    #p2 = (c_x + length * cos(Theta), cy + length*sin(theta))
    p1 = (int(cx - dx * length), int(cy - dy * length))
    p2 = (int(cx + dx * length), int(cy + dy * length))
    return p1, p2

def find_line_intersection(ellipse1, ellipse2):
    (cx1, cy1), (_, _), angle1 = ellipse1
    (cx2, cy2), (_, _), angle2 = ellipse2

    angle1_rad = np.deg2rad(angle1)
    angle2_rad = np.deg2rad(angle2)

    dx1, dy1 = np.cos(angle1_rad), np.sin(angle1_rad)
    dx2, dy2 = np.cos(angle2_rad), np.sin(angle2_rad)

    #Solve (cx1,cy1) + t1*(dx1,dy1) = (cx2,cy2) + t2*(dx2,dy2)
    A = np.array([[dx1, -dx2], [dy1, -dy2]])
    B = np.array([cx2 - cx1, cy2 - cy1])

    if np.linalg.det(A) == 0:
        return None 

    t1, t2 = np.linalg.solve(A, B)

    intersection_x = cx1 + t1 * dx1
    intersection_y = cy1 + t1 * dy1

    return (int(intersection_x), int(intersection_y))


def estimate_eye_center(frameShape, ray_lines):
    """

    Every time function is called, it takes two random ellipses stored from previous frames and calculates the intersection
    of their gaze line. This intersection is added to a list where the average intersection is found to try to best estimate
    the eye center.

    """
    global stored_intersections

    if len(ray_lines) <= 1:
        return None 
    
    height, width = frameShape[:2]
    
    a, b = random.sample(ray_lines, 2)  #Take 2 random eclipses 
    angle_diff = abs(a[2] - b[2])

    if angle_diff < MIN_ANGLE_DIFF:
        return None 
    intersection = find_line_intersection(a, b)

    if intersection is None:
        return None

    if not (0 <= intersection[0] < width and 0 <= intersection[1] < height):
        return None  #nonsense point outside the frame -> discard

    stored_intersections.append(intersection)

    if len(stored_intersections) > MAX_STORED_INTERSECTIONS:
        stored_intersections = stored_intersections[-MAX_STORED_INTERSECTIONS:]

    avg_x = np.mean([p[0] for p in stored_intersections])
    avg_y = np.mean([p[1] for p in stored_intersections])

    return (int(avg_x), int(avg_y))