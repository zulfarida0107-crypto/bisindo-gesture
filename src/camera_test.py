import cv2

cap = cv2.VideoCapture(0)

# Set resolusi kamera
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# Buat window fullscreen
cv2.namedWindow("Camera Test", cv2.WINDOW_NORMAL)
cv2.setWindowProperty(
    "Camera Test",
    cv2.WND_PROP_FULLSCREEN,
    cv2.WINDOW_FULLSCREEN
)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    cv2.imshow("Camera Test", frame)

    if cv2.waitKey(1) & 0xFF == 27:  # tekan ESC
        break

cap.release()
cv2.destroyAllWindows()
