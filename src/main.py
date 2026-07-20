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
import warnings

# Suppress google.protobuf deprecation warnings yang banjiri terminal
warnings.filterwarnings("ignore", category=UserWarning, module="google.protobuf")
warnings.filterwarnings("ignore", category=FutureWarning)

from gesture_classifier import GestureClassifier
from stabilizer import GestureStabilizer
from motion_tracker import JDetector
from tts import speak

# Simpan fungsi asli sebelum dirusak oleh monkey-patching ultralytics
original_imshow = cv2.imshow

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

# 5. J Detector (gerakan kelingking kiri)
j_detector = JDetector(
    window_sec=1.2,
    min_travel=0.04,
    angle_threshold=40,
)
j_detected_flash = 0  # timestamp untuk flash UI saat J terdeteksi

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
NO_GESTURE_TIMEOUT = 5.0       # detik
last_gesture_time = time.time()
text_spoken = False            # apakah teks sudah dibaca

# FPS counter
fps_time = time.time()
fps = 0

# ─── State I → J Timer ──────────────────────────────────────────
# Logika: huruf I dan J posturnya mirip.
# Jika gesture "I" ditahan >= 3 detik → dicatat sebagai J.
# Jika dilepas < 3 detik → dicatat sebagai I.
I_HOLD_FOR_J   = 3.0      # detik tahan untuk jadi J
i_hold_start   = None     # waktu mulai tahan pose I
i_pending      = False    # apakah sedang menunggu konfirmasi I vs J

# ═══════════════════════════════════════════════════════════════════
#  HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════

def get_display_text():
    """Gabungkan accumulated_text menjadi string untuk display."""
    return "".join(accumulated_text) if accumulated_text else ""

def draw_confidence_bar(frame, x, y, width, height, confidence, label=""):
    """Gambar bar confidence dengan warna gradient."""
    cv2.rectangle(frame, (x, y), (x + width, y + height), (50, 50, 50), -1)
    fill_w = int(width * confidence)
    if confidence >= 0.8:
        color = (0, 220, 80)      # hijau
    elif confidence >= 0.6:
        color = (0, 200, 255)     # kuning
    else:
        color = (0, 80, 230)      # merah

    cv2.rectangle(frame, (x, y), (x + fill_w, y + height), color, -1)
    cv2.rectangle(frame, (x, y), (x + width, y + height), (100, 100, 100), 1)

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
            # Default MediaPipe mapping (swapped back)
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

    # ─── J Motion Detection (kelingking kiri) ───────────────────
    j_motion = j_detector.update(left_hand)
    if j_motion:
        accumulated_text.append("J")
        last_added_gesture = "J"
        last_add_time = time.time()
        last_gesture_time = time.time()
        text_spoken = False
        j_detected_flash = time.time()
        print("  [MOTION] Huruf J terdeteksi!")

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

        if current_gesture == "I":
            # ── Logika I vs J ────────────────────────────────────
            # Saat gesture I pertama kali muncul, mulai timer
            if not i_pending:
                i_hold_start = time.time()
                i_pending    = True
                # Belum tambahkan ke teks — tunggu dulu
            else:
                held_duration = time.time() - i_hold_start
                if held_duration >= I_HOLD_FOR_J:
                    # Ditahan >= 3 detik → ini adalah J
                    if last_added_gesture != "J":
                        accumulated_text.append("J")
                        last_added_gesture = "J"
                        last_add_time = time.time()
                        j_detected_flash = time.time()
                        i_pending = False
                        i_hold_start = None
                        print("  [I→J] Pose I ditahan 3 detik → J")
        else:
            # Gesture berubah dari I ke gesture lain
            if i_pending:
                # I dilepas sebelum 3 detik → commit sebagai I
                if last_added_gesture != "I":
                    accumulated_text.append("I")
                    last_added_gesture = "I"
                    last_add_time = time.time()
                    print("  [I] Pose I dilepas cepat → I")
                i_pending    = False
                i_hold_start = None

            # Proses gesture selain I dan ON seperti biasa
            if current_gesture != last_added_gesture and current_gesture != "ON":
                accumulated_text.append(current_gesture)
                last_add_time = time.time()
                last_added_gesture = current_gesture

    else:
        # Tidak ada gesture aktif
        elapsed = time.time() - last_gesture_time

        # Jika pose I pending dan tangan diangkat → commit sebagai I
        if i_pending:
            if last_added_gesture != "I":
                accumulated_text.append("I")
                last_added_gesture = "I"
                last_add_time = time.time()
                print("  [I] Tangan dilepas saat pose I → I")
            i_pending    = False
            i_hold_start = None

        if elapsed >= 5.0:
            if accumulated_text and not text_spoken:
                final_text = get_display_text()
                if final_text.strip():
                    print(f"  TTS (Auto-Enter): \"{final_text}\"")
                    speak(final_text)
                accumulated_text.clear()
                text_spoken = True
            last_added_gesture = None
        else:
            if elapsed > 1.5:
                last_added_gesture = None

    # ─── FPS ────────────────────────────────────────────────────
    now = time.time()
    fps = 1.0 / max(now - fps_time, 0.001)
    fps_time = now

    # ═══════════════════════════════════════════════════════════════
    #  UI OVERLAY
    # ═══════════════════════════════════════════════════════════════

    cv2.rectangle(frame, (0, 0), (w, 160), (20, 20, 20), -1)

    r_color = (0, 230, 80) if right_label_text == "ON" else (80, 80, 80)
    l_color = (0, 230, 80) if left_label_text == "ON" else (80, 80, 80)

    cv2.putText(frame, f"Kanan: {right_label_text}",
                (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.65, r_color, 2)
    cv2.putText(frame, f"Kiri: {left_label_text}",
                (200, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.65, l_color, 2)
    cv2.putText(frame, f"FPS: {int(fps)}",
                (w - 120, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (150, 150, 150), 1)

    gesture_display = current_gesture if current_gesture else "-"
    conf_display = f"{raw_confidence:.0%}" if raw_gesture else "0%"

    cv2.putText(frame, f"Gesture:",
                (20, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 1)
    cv2.putText(frame, gesture_display,
                (160, 80), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 3)

    draw_confidence_bar(frame, 20, 100, 300, 18, raw_confidence,
                        f"Confidence: {conf_display}")

    raw_display = f"Raw: {raw_gesture} ({raw_confidence:.2f})" if raw_gesture else "Raw: -"
    cv2.putText(frame, raw_display,
                (20, 145), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (120, 120, 120), 1)

    if time.time() - j_detected_flash < 1.0:
        cv2.putText(frame, "[J] TERDETEKSI!",
                    (400, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 180), 2)

    # ── I → J Timer indicator ────────────────────────────────────
    if i_pending and i_hold_start is not None:
        held = time.time() - i_hold_start
        progress = min(held / I_HOLD_FOR_J, 1.0)
        bar_x, bar_y, bar_w, bar_h = 400, 60, 200, 20

        # Latar bar
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h), (40, 40, 40), -1)
        # Isi bar: kuning → hijau saat mendekati J
        fill = int(bar_w * progress)
        bar_color = (0, int(180 + 75 * progress), int(255 * (1 - progress)))
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + fill, bar_y + bar_h), bar_color, -1)
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h), (150, 150, 150), 1)

        sisa = max(0.0, I_HOLD_FOR_J - held)
        label_ij = f"I  tahan {sisa:.1f}s  J" if sisa > 0 else "→ J!"
        cv2.putText(frame, label_ij,
                    (bar_x + 5, bar_y + bar_h - 4),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)


    footer_y = h - 100
    cv2.rectangle(frame, (0, footer_y), (w, h), (20, 20, 20), -1)

    cv2.putText(frame, "Terjemahan:",
                (20, footer_y + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 1)

    display_text = get_display_text()
    if display_text:
        max_chars = w // 30
        if len(display_text) > max_chars:
            display_text = "..." + display_text[-(max_chars - 3):]
        cv2.putText(frame, display_text,
                    (20, footer_y + 75), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 255), 3)
    else:
        cv2.putText(frame, "-",
                    (20, footer_y + 75), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (80, 80, 80), 3)

    if text_spoken and accumulated_text:
        cv2.putText(frame, "[TTS Selesai]",
                    (w - 200, footer_y + 30), cv2.FONT_HERSHEY_SIMPLEX,
                    0.6, (0, 200, 100), 2)

    cv2.putText(frame, "SPACE=spasi  BACKSPACE=hapus  ENTER=baca  R=reset  ESC=keluar",
                (20, h - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (100, 100, 100), 1)

    # Tampilkan frame menggunakan original_imshow untuk membypass monkey-patching ultralytics
    original_imshow("BISINDO Translator v2.0", frame)

    # ═══════════════════════════════════════════════════════════════
    #  KEYBOARD INPUT
    # ═══════════════════════════════════════════════════════════════
    key = cv2.waitKey(1) & 0xFF

    if key == 27:  # ESC
        break

    elif key == ord(' '):
        accumulated_text.append(" ")
        text_spoken = False
        print("  [SPACE] Spasi ditambahkan")

    elif key == 8 or key == 127:
        if accumulated_text:
            removed = accumulated_text.pop()
            print(f"  [BACKSPACE] Dihapus: '{removed}'")
            text_spoken = False

    elif key == 13:
        text = get_display_text()
        if text.strip():
            print(f"  [ENTER] TTS: \"{text}\"")
            speak(text)
            text_spoken = True

    elif key == ord('j') or key == ord('J'):
        accumulated_text.append("J")
        last_added_gesture = "J"
        text_spoken = False
        print("  [MANUAL] Huruf J ditambahkan")

    elif key == ord('r') or key == ord('R'):
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
