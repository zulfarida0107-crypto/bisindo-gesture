"""
collect_data.py — Script koleksi data landmark BISINDO
Letakkan file ini di: bisindo-gesture/src/collect_data.py

Cara pakai:
  python src/collect_data.py
"""

import cv2
import mediapipe as mp
import csv
import os
import time
import sys

# ─── Konfigurasi ────────────────────────────────────────────────
DATASET_DIR = "dataset"          # folder output CSV
SAMPLES_TARGET = 80              # target sampel per gesture (lebih banyak = lebih akurat)
COUNTDOWN_SEC = 3                # hitungan mundur sebelum rekam
# ────────────────────────────────────────────────────────────────

# Semua huruf BISINDO + ON dan OFF
BISINDO_LABELS = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ") + ["ON", "OFF"]

# ── Kategorisasi tangan per huruf BISINDO ───────────────────────
# 1 tangan kiri saja
ONE_HAND_LEFT_LETTERS = {"C", "E", "I", "L", "O", "R", "U", "V", "Z"}

# 2 tangan (kiri + kanan)
TWO_HAND_LETTERS = {"A", "B", "D", "F", "G", "H", "K", "M", "N", "P", "Q", "S", "T", "W", "X", "Y"}

# Gesture dinamis — belum didukung di versi ini (butuh motion tracker)
DYNAMIC_LETTERS  = {"J"}  # gerakan 0° → 90°

mp_hands = mp.solutions.hands
mp_draw  = mp.solutions.drawing_utils


def get_landmarks_flat(hand_landmarks):
    """
    Ambil 21 titik × 3 koordinat (x, y, z), normalisasi relatif
    ke titik pergelangan tangan (landmark[0]) dan scale-invariant.
    Hasil: list 63 angka
    """
    wrist = hand_landmarks.landmark[0]
    
    # Hitung jarak relatif terhadap wrist
    coords = []
    max_dist = 1e-6
    for lm in hand_landmarks.landmark:
        dx = lm.x - wrist.x
        dy = lm.y - wrist.y
        dz = lm.z - wrist.z
        dist = (dx**2 + dy**2 + dz**2)**0.5
        if dist > max_dist:
            max_dist = dist
        coords.append((dx, dy, dz))
        
    # Normalisasi dengan membagi terhadap jarak maksimal
    row = []
    for dx, dy, dz in coords:
        row.extend([
            round(dx / max_dist, 6),
            round(dy / max_dist, 6),
            round(dz / max_dist, 6),
        ])
    return row  # 63 nilai


def make_empty_hand():
    """Return 63 angka nol (placeholder saat tangan tidak terdeteksi)."""
    return [0.0] * 63


def get_csv_path(label):
    os.makedirs(DATASET_DIR, exist_ok=True)
    return os.path.join(DATASET_DIR, f"bisindo_{label}.csv")


def count_existing_samples(label):
    path = get_csv_path(label)
    if not os.path.exists(path):
        return 0
    with open(path, "r") as f:
        return sum(1 for _ in csv.reader(f))


def collect_gesture(label):
    """Buka kamera dan rekam sampel untuk satu gesture/huruf."""

    is_two_hand  = label in TWO_HAND_LETTERS
    is_left_only = label in ONE_HAND_LEFT_LETTERS
    is_dynamic   = label in DYNAMIC_LETTERS

    if is_two_hand:
        hand_mode = "2 TANGAN"
    elif is_dynamic:
        hand_mode = "DINAMIS (belum didukung)"
    else:
        hand_mode = "1 TANGAN KIRI"

    # Panduan spesifik per huruf BISINDO (bukan ASL!)
    GESTURE_TIPS = {
        "A": "2 TANGAN: ibu jari + telunjuk kedua tangan saling menyentuh, membentuk BERLIAN di atas.",
        "B": "2 TANGAN: kedua telapak tangan menghadap ke depan, jari-jari rapat lurus ke atas.",
        "D": "2 TANGAN: telunjuk kanan lurus ke atas, tangan kiri membentuk huruf C di sekitarnya.",
        "F": "1 TANGAN: telunjuk satu-satunya yang menunjuk ke atas, ibu jari & jari lain melingkar.",
        "T": "1 TANGAN: kepalan, ibu jari MENYELIP di celah antara telunjuk & jari tengah.",
        "X": "2 TANGAN: jari-jari kedua tangan saling MENYILANG satu sama lain membentuk X.",
        "K": "2 TANGAN: telunjuk kanan ke atas, tangan kiri menopang dari bawah.",
        "S": "2 TANGAN: telapak tangan saling bertumpuk / bersilangan di depan dada.",
        "G": "2 TANGAN: kedua tangan dalam posisi menunjuk, saling berhadapan.",
        "H": "2 TANGAN: kedua telunjuk menunjuk ke samping, sejajar horizontal.",
        "M": "1 TANGAN: semua jari terbuka lebar menghadap ke depan seperti kipas.",
        "N": "2 TANGAN: tangan kanan mengepal kecil, tangan kiri menopang dari bawah.",
        "P": "2 TANGAN: telunjuk kanan ke bawah, tangan kiri membentuk lingkaran.",
        "Q": "2 TANGAN: kedua tangan membentuk lingkaran O yang saling berhadapan.",
        "W": "2 TANGAN: kedua tangan saling bersilang di pergelangan tangan.",
    }

    print(f"\n==================================================")
    print(f" MEREKAM GESTURE: {label} [{hand_mode}]")
    print(f"==================================================")
    if label in GESTURE_TIPS:
        print(f" ★ TIPS: {GESTURE_TIPS[label]}")
    print(f" - Target: {SAMPLES_TARGET} sampel.")
    print(f" - Tekan SPACE di kamera untuk memulai hitung mundur.")
    print(f" - Tekan Q di kamera untuk selesai / lanjut.")
    print(f"==================================================")

    # Inisialisasi detektor MediaPipe Hands
    hands_detector = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=2,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.6
    )

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    if not cap.isOpened():
        print("Error: Kamera tidak dapat dibuka.")
        return 0

    samples_collected = count_existing_samples(label)
    
    # Buka file CSV untuk append
    csv_path = get_csv_path(label)
    with open(csv_path, "a", newline="") as csv_file:
        writer = csv.writer(csv_file)

        recording = False
        countdown_start = None

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Mirror frame agar natural saat user melihat ke layar
            frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Deteksi hands
            results = hands_detector.process(rgb)

            left_row  = None
            right_row = None

            if results.multi_hand_landmarks and results.multi_handedness:
                for hand_lm, hand_info in zip(
                    results.multi_hand_landmarks, results.multi_handedness
                ):
                    label_hand = hand_info.classification[0].label
                    # Default MediaPipe mapping (swapped back)
                    if label_hand == "Left":
                        left_row = get_landmarks_flat(hand_lm)
                    else:
                        right_row = get_landmarks_flat(hand_lm)

                    mp_draw.draw_landmarks(
                        frame, hand_lm, mp_hands.HAND_CONNECTIONS
                    )

            # ── Susun baris CSV ─────────────────────────────────
            # Format: [63 kiri] + [63 kanan] + [label]  = 127 kolom
            row_left  = left_row  if left_row  is not None else make_empty_hand()
            row_right = right_row if right_row is not None else make_empty_hand()
            full_row  = row_left + row_right + [label]

            # ── Cek apakah tangan cukup terdeteksi ──────────────
            if label == "OFF":
                hand_ok = (left_row is None and right_row is None)
                hint    = "Sembunyikan tangan dari kamera"
            elif label == "ON":
                hand_ok = (left_row is not None and right_row is not None)
                hint    = "Tunjukkan KEDUA tangan (pose istirahat)"
            elif is_two_hand:
                hand_ok = (left_row is not None and right_row is not None)
                hint    = "Tunjukkan KEDUA tangan (kiri + kanan)"
            elif is_left_only:
                hand_ok = (left_row is not None)
                hint    = "Tunjukkan tangan KIRI saja"
            else:
                hand_ok = (right_row is not None or left_row is not None)
                hint    = "Tunjukkan SATU tangan"

            # ── Countdown sebelum rekam ─────────────────────────
            if countdown_start is not None:
                elapsed  = time.time() - countdown_start
                remaining = COUNTDOWN_SEC - elapsed
                if remaining > 0:
                    recording = False   # masih countdown, belum simpan
                    cv2.putText(frame, f"Bersiap... {int(remaining)+1}",
                                (20, 80), cv2.FONT_HERSHEY_SIMPLEX,
                                1.4, (0, 165, 255), 3)
                else:
                    recording = True    # countdown selesai, mulai rekam
                    countdown_start = None

            # ── Simpan sampel ────────────────────────────────────
            if recording and hand_ok:
                writer.writerow(full_row)
                csv_file.flush()
                samples_collected += 1

            # ── UI overlay ──────────────────────────────────────
            progress  = min(samples_collected, SAMPLES_TARGET)
            bar_width = int((progress / SAMPLES_TARGET) * 300)
            color_bar = (0, 200, 100) if samples_collected >= SAMPLES_TARGET else (0, 140, 255)

            cv2.rectangle(frame, (20, 20), (320, 50), (50, 50, 50), -1)
            cv2.rectangle(frame, (20, 20), (20 + bar_width, 50), color_bar, -1)
            cv2.putText(frame, f"{samples_collected}/{SAMPLES_TARGET} sampel",
                        (25, 43), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)

            status_color = (0, 230, 80) if hand_ok else (0, 80, 230)
            rec_color    = (0, 0, 220) if recording else (180, 180, 180)

            cv2.putText(frame, f"Huruf: {label}  [{hand_mode}]",
                        (20, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            cv2.putText(frame, hint,
                        (20, 145), cv2.FONT_HERSHEY_SIMPLEX, 0.65, status_color, 2)
            cv2.putText(frame, "● REC" if recording else "○ PAUSE",
                        (20, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.7, rec_color, 2)

            # Tampilkan tips di layar kamera jika ada
            if label in GESTURE_TIPS:
                tip_text = GESTURE_TIPS[label]
                # Potong teks jika terlalu panjang
                if len(tip_text) > 65:
                    tip_text = tip_text[:62] + "..."
                cv2.putText(frame, f"TIPS: {tip_text}",
                            (20, 215), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 215, 255), 1)

            cv2.putText(frame, "SPACE=mulai  Q=selesai",
                        (20, 460), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 200, 200), 1)


            if samples_collected >= SAMPLES_TARGET:
                cv2.putText(frame, "TARGET TERCAPAI!",
                            (160, 300), cv2.FONT_HERSHEY_SIMPLEX,
                            1.2, (0, 255, 100), 3)

            cv2.imshow(f"BISINDO Collector — Huruf {label}", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord(' '):
                recording      = True
                countdown_start = time.time()
            elif key == ord('q') or key == ord('Q'):
                break

    cap.release()
    cv2.destroyAllWindows()
    hands_detector.close()
    print(f"  Selesai. Total sampel huruf {label}: {samples_collected}")
    return samples_collected


def main():
    print("\n" + "="*50)
    print("  BISINDO Gesture — Koleksi Data Landmark")
    print("="*50)
    print("\nPilih mode:")
    print("  1. Kumpulkan SEMUA huruf (A–Z) satu per satu")
    print("  2. Pilih huruf tertentu")
    print("  3. Lanjutkan dari huruf yang belum cukup sampel")
    print("  4. Persiapan (Kumpulkan kelas ON dan OFF)")

    mode = input("\nMasukkan pilihan (1/2/3/4): ").strip()

    if mode == "1":
        targets = BISINDO_LABELS

    elif mode == "2":
        raw     = input("Masukkan huruf (contoh: A B C atau ABC): ").upper()
        targets = [c for c in raw if c in BISINDO_LABELS]
        if not targets:
            print("Huruf tidak valid.")
            return

    elif mode == "3":
        targets = []
        for lbl in BISINDO_LABELS:
            existing = count_existing_samples(lbl)
            if existing < SAMPLES_TARGET:
                print(f"  {lbl}: {existing}/{SAMPLES_TARGET} sampel")
                targets.append(lbl)
        if not targets:
            print("Semua huruf sudah mencapai target!")
            return
        print(f"\nAkan mengumpulkan: {targets}")
        input("Tekan Enter untuk mulai...")

    elif mode == "4":
        targets = ["ON", "OFF"]

    else:
        print("Pilihan tidak valid.")
        return

    for label in targets:
        # Huruf J dilewati karena dinamis
        if label == "J":
            print("\nHuruf J adalah gesture dinamis (dideteksi otomatis via motion tracker). Dilewati.")
            continue
        collect_gesture(label)

    print("\nProses selesai. Silakan jalankan training model dengan:")
    print("  python src/train_model.py")


if __name__ == "__main__":
    main()
