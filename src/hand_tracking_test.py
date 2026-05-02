import cv2
import mediapipe as mp

# ====== INIT MEDIAPIPE ======
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# ====== INIT CAMERA ======
cap = cv2.VideoCapture(0)

# SET RESOLUSI HD
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# WINDOW FULL FRAME
cv2.namedWindow("BISINDO Hand Tracking", cv2.WINDOW_NORMAL)
cv2.resizeWindow("BISINDO Hand Tracking", 1280, 720)

print("Hand tracking running (Left & Right) — tekan ESC untuk keluar")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Kamera tidak terdeteksi")
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    if results.multi_hand_landmarks and results.multi_handedness:
        for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):

            # Gambar landmark
            mp_draw.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS
            )

            # Label Left / Right
            handedness = results.multi_handedness[idx].classification[0].label

            # Posisi wrist
            h, w, _ = frame.shape
            wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
            x, y = int(wrist.x * w), int(wrist.y * h)

            cv2.putText(
                frame,
                handedness,
                (x - 40, y - 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (0, 255, 0),
                2
            )

    cv2.imshow("BISINDO Hand Tracking", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
