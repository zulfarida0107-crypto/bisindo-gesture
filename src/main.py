"""
main.py — BISINDO Gesture Recognition (ML-Based)
Pipeline: Kamera → MediaPipe → Normalisasi → ML Model → Stabilizer → TTS

Kontrol:
  SPACE     = tambah spasi (kata baru)
  BACKSPACE = hapus huruf terakhir
  ENTER     = baca teks sekarang (TTS)
  R         = reset semua teks
  ESC       = keluar
"""

import cv2
import mediapipe as mp
import time
import sys

from gesture_classifier import GestureClassifier
from stabilizer import GestureStabilizer
from tts import speak

# ═══════════════════════════════════════════════════════════════════
#  INISIALISASI
# ═══════════════════════════════════════════════════════════════════

print("\n" + "=" * 55)
print("  BISINDO Gesture Recognition v2.0 (ML-Based)")
print("=" * 55)

# 1. Load ML Model
try:
    classifier = GestureClassifier()
except FileNotFoundError as e:
    print(str(e))
    sys.exit(1)

# 2. MediaPipe Hands
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
mp_styles = mp.solutions.drawing_styles

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.6,
)

# 3. Kamera
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

if not cap.isOpened():
    print("\n  ERROR: Kamera tidak tersedia!")
    print("  Pastikan kamera terhubung dan tidak dipakai aplikasi lain.")
    sys.exit(1)

# 4. Stabilizer
stabilizer = GestureStabilizer(
    buffer_size=7,
    min_confidence=0.55,
    switch_threshold=3,
)

print("\n  Sistem BISINDO Aktif!")
print("  Kontrol: SPACE=spasi | BACKSPACE=hapus | ENTER=baca | R=reset | ESC=keluar")
print("=" * 55 + "\n")

# ═══════════════════════════════════════════════════════════════════
#  STATE
# ═══════════════════════════════════════════════════════════════════

accumulated_text = []          # list huruf/spasi yang sudah terkumpul
last_added_gesture = None      # gesture terakhir yang ditambahkan
current_gesture = None         # gesture stabil saat ini
current_confidence = 0.0       # confidence saat ini
last_add_time = time.time()    # waktu terakhir huruf ditambahkan

# Timeout: jika tidak ada gesture selama N detik → TTS baca teks
NO_GESTURE_TIMEOUT = 2.0       # detik
last_gesture_time = time.time()
text_spoken = False            # apakah teks sudah dibaca

# FPS counter
fps_time = time.time()
fps = 0

# ═══════════════════════════════════════════════════════════════════
#  HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════


def get_display_text():
    """Gabungkan accumulated_text menjadi string untuk display."""
    return "".join(accumulated_text) if accumulated_text else ""


def draw_confidence_bar(frame, x, y, width, height, confidence, label=""):
    """Gambar bar confidence dengan warna gradient."""
    # Background bar
    cv2.rectangle(frame, (x, y), (x + width, y + height), (50, 50, 50), -1)

    # Filled bar berdasarkan confidence
    fill_w = int(width * confidence)
    if confidence >= 0.8:
        color = (0, 220, 80)      # hijau = sangat yakin
    elif confidence >= 0.6:
        color = (0, 200, 255)     # kuning = cukup yakin
    else:
        color = (0, 80, 230)      # merah = kurang yakin

    cv2.rectangle(frame, (x, y), (x + fill_w, y + height), color, -1)

    # Border
    cv2.rectangle(frame, (x, y), (x + width, y + height), (100, 100, 100), 1)

    # Label
    if label:
        cv2.putText(
            frame, label,
            (x + 5, y + height - 5),
            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1,
        )


# ═══════════════════════════════════════════════════════════════════
#  MAIN LOOP
# ═══════════════════════════════════════════════════════════════════

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)  # mirror
    h, w, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # ─── MediaPipe Detection ────────────────────────────────────
    results = hands.process(rgb)

    left_hand = None
    right_hand = None
    left_label_text = "OFF"
    right_label_text = "OFF"

    if results.multi_hand_landmarks and results.multi_handedness:
        for hand_lm, hand_info in zip(
            results.multi_hand_landmarks, results.multi_handedness
        ):
            label = hand_info.classification[0].label
            # MediaPipe dengan mirror: "Left" = tangan kiri user, "Right" = kanan user
            if label == "Left":
                left_hand = hand_lm
                left_label_text = "ON"
            else:
                right_hand = hand_lm
                right_label_text = "ON"

            # Gambar landmark di frame
            mp_draw.draw_landmarks(
                frame, hand_lm, mp_hands.HAND_CONNECTIONS,
                mp_styles.get_default_hand_landmarks_style(),
                mp_styles.get_default_hand_connections_style(),
            )

    # ─── ML Prediction ──────────────────────────────────────────
    raw_gesture = None
    raw_confidence = 0.0

    if left_hand is not None or right_hand is not None:
        raw_gesture, raw_confidence = classifier.predict(right_hand, left_hand)

    # ─── Stabilizer ─────────────────────────────────────────────
    stable = stabilizer.update(raw_gesture, raw_confidence)

    current_gesture = stable
    current_confidence = raw_confidence if stable == raw_gesture else 0.0

    # ─── Word Building Logic ────────────────────────────────────
    if current_gesture is not None and current_gesture != "OFF":
        last_gesture_time = time.time()
        text_spoken = False

        # Tambahkan huruf jika berbeda dari yang terakhir ditambahkan
        if current_gesture != last_added_gesture:
            if current_gesture != "ON":
                accumulated_text.append(current_gesture)
                last_add_time = time.time()
            last_added_gesture = current_gesture
        else:
            # Jika huruf sama ditahan terus selama 1.5 detik, gandakan hurufnya (Auto-Repeat)
            if current_gesture != "ON":
                if time.time() - last_add_time > 1.5:
                    accumulated_text.append(current_gesture)
                    last_add_time = time.time()

    else:
        # current_gesture == "OFF" (tidak ada tangan)
        elapsed = time.time() - last_gesture_time

        if accumulated_text and not text_spoken and elapsed >= NO_GESTURE_TIMEOUT:
            final_text = get_display_text()
            if final_text.strip():
                print(f"  TTS: \"{final_text}\"")
                speak(final_text)
            text_spoken = True

        # Jika tangan hilang ("OFF"), langsung reset penahan gesture
        # Ini memungkinkan kamu mengetik huruf yang sama berturut-turut (misal 'A' lalu 'A')
        # cukup dengan menyembunyikan tangan sesaat.
        if current_gesture == "OFF":
            last_added_gesture = "OFF"

    # ─── FPS ────────────────────────────────────────────────────
    now = time.time()
    fps = 1.0 / max(now - fps_time, 0.001)
    fps_time = now

    # ═══════════════════════════════════════════════════════════════
    #  UI OVERLAY
    # ═══════════════════════════════════════════════════════════════

    # --- Header background ---
    cv2.rectangle(frame, (0, 0), (w, 160), (20, 20, 20), -1)

    # --- Hand Status ---
    r_color = (0, 230, 80) if right_label_text == "ON" else (80, 80, 80)
    l_color = (0, 230, 80) if left_label_text == "ON" else (80, 80, 80)

    cv2.putText(frame, f"Kanan: {right_label_text}",
                (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.65, r_color, 2)
    cv2.putText(frame, f"Kiri: {left_label_text}",
                (200, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.65, l_color, 2)
    cv2.putText(frame, f"FPS: {int(fps)}",
                (w - 120, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (150, 150, 150), 1)

    # --- Current Gesture (besar di tengah header) ---
    gesture_display = current_gesture if current_gesture else "-"
    conf_display = f"{raw_confidence:.0%}" if raw_gesture else "0%"

    cv2.putText(frame, f"Gesture:",
                (20, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 1)
    cv2.putText(frame, gesture_display,
                (160, 80), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 3)

    # --- Confidence Bar ---
    draw_confidence_bar(frame, 20, 100, 300, 18, raw_confidence,
                        f"Confidence: {conf_display}")

    # --- Raw prediction (debug) ---
    raw_display = f"Raw: {raw_gesture} ({raw_confidence:.2f})" if raw_gesture else "Raw: -"
    cv2.putText(frame, raw_display,
                (20, 145), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (120, 120, 120), 1)

    # --- Footer: Accumulated Text ---
    footer_y = h - 100
    cv2.rectangle(frame, (0, footer_y), (w, h), (20, 20, 20), -1)

    cv2.putText(frame, "Terjemahan:",
                (20, footer_y + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 1)

    display_text = get_display_text()
    if display_text:
        # Potong jika terlalu panjang
        max_chars = w // 30
        if len(display_text) > max_chars:
            display_text = "..." + display_text[-(max_chars - 3):]
        cv2.putText(frame, display_text,
                    (20, footer_y + 75), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 255), 3)
    else:
        cv2.putText(frame, "-",
                    (20, footer_y + 75), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (80, 80, 80), 3)

    # --- Status TTS ---
    if text_spoken and accumulated_text:
        cv2.putText(frame, "[TTS Selesai]",
                    (w - 200, footer_y + 30), cv2.FONT_HERSHEY_SIMPLEX,
                    0.6, (0, 200, 100), 2)

    # --- Kontrol hint ---
    cv2.putText(frame, "SPACE=spasi  BACKSPACE=hapus  ENTER=baca  R=reset  ESC=keluar",
                (20, h - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (100, 100, 100), 1)

    # ═══════════════════════════════════════════════════════════════
    #  TAMPILKAN FRAME
    # ═══════════════════════════════════════════════════════════════
    cv2.imshow("BISINDO Translator v2.0", frame)

    # ═══════════════════════════════════════════════════════════════
    #  KEYBOARD INPUT
    # ═══════════════════════════════════════════════════════════════
    key = cv2.waitKey(1) & 0xFF

    if key == 27:  # ESC
        break

    elif key == ord(' '):  # SPACE → tambah spasi
        accumulated_text.append(" ")
        text_spoken = False
        print("  [SPACE] Spasi ditambahkan")

    elif key == 8 or key == 127:  # BACKSPACE → hapus karakter terakhir
        if accumulated_text:
            removed = accumulated_text.pop()
            print(f"  [BACKSPACE] Dihapus: '{removed}'")
            text_spoken = False

    elif key == 13:  # ENTER → baca teks sekarang
        text = get_display_text()
        if text.strip():
            print(f"  [ENTER] TTS: \"{text}\"")
            speak(text)
            text_spoken = True

    elif key == ord('r') or key == ord('R'):  # R → reset semua
        accumulated_text.clear()
        last_added_gesture = None
        current_gesture = None
        text_spoken = False
        stabilizer.reset()
        print("  [RESET] Teks direset")


# ═══════════════════════════════════════════════════════════════════
#  CLEANUP
# ═══════════════════════════════════════════════════════════════════

print("\n  Menutup sistem...")
cap.release()
cv2.destroyAllWindows()
hands.close()
print("  Selesai. Terima kasih!")
sys.exit(0)
