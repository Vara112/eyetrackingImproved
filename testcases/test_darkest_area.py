import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
import numpy as np
import cv2

from main import find_darkest_area

FRAME_HEIGHT = 480
FRAME_WIDTH  = 640



def test_find_darkest_area():
    #Create a bright frame
    frame = np.full((FRAME_HEIGHT, FRAME_WIDTH), 200, dtype=np.uint8)

    #dark square (value 10)
    known_cx, known_cy = 300, 200
    half = 30
    frame[known_cy-half:known_cy+half, known_cx-half:known_cx+half] = 10

    result = find_darkest_area(frame)
    print("Detected center:", result)
    print("Expected near:  ", (known_cx, known_cy))

    #Loose check, should land inside the dark square
    assert abs(result[0] - known_cx) < 30
    assert abs(result[1] - known_cy) < 30
    print("PASS")

if __name__ == "__main__":
    test_find_darkest_area()