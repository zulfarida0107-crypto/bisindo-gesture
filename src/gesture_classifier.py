"""
gesture_classifier.py — ML-based BISINDO gesture classifier
Menggunakan model ensemble (RF + SVM) yang dilatih dari data landmark MediaPipe.

Pipeline:
  MediaPipe landmarks → normalisasi → 126 fitur posisi + 30 fitur sudut sendi
  → 156 fitur total → model.predict() → huruf + confidence
"""

import pickle
import numpy as np
import os


# Resolve path relatif ke lokasi script ini
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_MODEL_PATH = os.path.join(SCRIPT_DIR, "gesture_model.pkl")

# Pasangan landmark yang membentuk sudut sendi (sama persis dengan train_model.py)
FINGER_JOINTS = [
    (1, 2, 3), (2, 3, 4),
    (5, 6, 7), (6, 7, 8),
    (9, 10, 11), (10, 11, 12),
    (13, 14, 15), (14, 15, 16),
    (17, 18, 19), (18, 19, 20),
    (0, 5, 9), (0, 9, 13), (0, 13, 17),
    (5, 9, 13), (9, 13, 17),
]


class GestureClassifier:
    """Classifier gesture BISINDO berbasis ML (RF + SVM Ensemble)."""

    def __init__(self, model_path=None):
        path = model_path or DEFAULT_MODEL_PATH

        if not os.path.exists(path):
            raise FileNotFoundError(
                f"\n{'='*55}\n"
                f"  Model tidak ditemukan: {path}\n"
                f"  Jalankan langkah berikut dulu:\n"
                f"    1. python src/collect_data.py   (kumpulkan data)\n"
                f"    2. python src/train_model.py    (latih model)\n"
                f"{'='*55}\n"
            )

        with open(path, "rb") as f:
            self.model = pickle.load(f)

        self.labels = self.model.classes_
        print(f"  Model dimuat: {path}")
        print(f"  Kelas: {list(self.labels)}")

    # ─── Normalisasi Landmark ────────────────────────────────────

    @staticmethod
    def get_landmarks_flat(hand_landmarks):
        """
        Ambil 21 titik × 3 koordinat (x, y, z),
        normalisasi relatif ke pergelangan tangan (landmark[0])
        dan disesuaikan dengan skala tangan (scale-invariant).
        Hasil: list 63 angka.
        """
        wrist = hand_landmarks.landmark[0]

        coords = []
        max_dist = 1e-6
        for lm in hand_landmarks.landmark:
            dx = lm.x - wrist.x
            dy = lm.y - wrist.y
            dz = lm.z - wrist.z
            dist = (dx**2 + dy**2 + dz**2) ** 0.5
            if dist > max_dist:
                max_dist = dist
            coords.append((dx, dy, dz))

        row = []
        for dx, dy, dz in coords:
            row.extend([
                round(dx / max_dist, 6),
                round(dy / max_dist, 6),
                round(dz / max_dist, 6),
            ])
        return row  # 63 nilai

    @staticmethod
    def make_empty_hand():
        """Return 63 angka nol (placeholder saat tangan tidak terdeteksi)."""
        return [0.0] * 63

    @staticmethod
    def compute_angle_features(landmarks_63):
        """
        Hitung fitur sudut cos antar ruas jari dari 63 nilai landmark.
        Membantu membedakan gestur yang posisi jarinya mirip (A vs T vs X).
        Hasil: 15 nilai (cos sudut tiap sendi).
        """
        lm = np.array(landmarks_63, dtype=np.float32).reshape(21, 3)
        angles = []
        for a_idx, b_idx, c_idx in FINGER_JOINTS:
            a = lm[a_idx]
            b = lm[b_idx]
            c = lm[c_idx]
            ba = a - b
            bc = c - b
            norm_ba = np.linalg.norm(ba)
            norm_bc = np.linalg.norm(bc)
            if norm_ba < 1e-9 or norm_bc < 1e-9:
                angles.append(0.0)
            else:
                cos_angle = np.clip(
                    np.dot(ba, bc) / (norm_ba * norm_bc), -1.0, 1.0
                )
                angles.append(float(cos_angle))
        return angles  # 15 nilai

    # ─── Prediksi ────────────────────────────────────────────────

    def predict(self, right_hand, left_hand):
        """
        Prediksi gesture dari landmark 2 tangan.

        Args:
            right_hand: MediaPipe hand_landmarks (atau None)
            left_hand:  MediaPipe hand_landmarks (atau None)

        Returns:
            tuple: (huruf: str, confidence: float)
                   Contoh: ("A", 0.92)
                   Atau ("OFF", 1.0) jika tidak ada tangan
        """
        if right_hand is None and left_hand is None:
            return "OFF", 1.0

        # Ekstrak + normalisasi fitur posisi (126 nilai)
        left_feat = (
            self.get_landmarks_flat(left_hand)
            if left_hand is not None
            else self.make_empty_hand()
        )
        right_feat = (
            self.get_landmarks_flat(right_hand)
            if right_hand is not None
            else self.make_empty_hand()
        )

        # Hitung fitur sudut sendi (30 nilai = 15 kiri + 15 kanan)
        left_angles  = self.compute_angle_features(left_feat)
        right_angles = self.compute_angle_features(right_feat)

        # Gabung: 63 kiri + 63 kanan + 15 sudut kiri + 15 sudut kanan = 156 fitur
        features = np.array(
            left_feat + right_feat + left_angles + right_angles,
            dtype=np.float32
        ).reshape(1, -1)

        # Prediksi
        prediction   = self.model.predict(features)[0]
        probabilities = self.model.predict_proba(features)[0]
        confidence   = float(np.max(probabilities))

        return prediction, confidence
