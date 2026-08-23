import cv2
import time

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 120)

width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS) or 30

# Give the file a description right up front instead of a timestamp,
# since you'll want to know at a glance what each clip is testing
label = input("Name this clip (e.g. 'lens_adjusted', 'blink_test'): ").strip()
filename = f"eye_{label}_{int(time.time())}.avi"

fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter(filename, fourcc, fps, (width, height), isColor=False)

print(f"Recording to {filename}")
print("Press 'q' to stop recording")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    frame = cv2.rotate(frame, cv2.ROTATE_180)  # remove this line if you've since remounted right-side up
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) if len(frame.shape) == 3 else frame

    out.write(gray)
    cv2.imshow('Recording — press q to stop', gray)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
out.release()
cv2.destroyAllWindows()
print(f"Saved: {filename}")