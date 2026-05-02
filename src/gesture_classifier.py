"""
gesture_classifier.py — ML-based BISINDO gesture classifier
Menggunakan model Random Forest yang dilatih dari data landmark MediaPipe.

Pipeline:
  MediaPipe landmarks → normalisasi → 126 fitur → model.predict() → huruf + confidence
"""

import pickle
import numpy as np
import os


# Resolve path relatif ke lokasi script ini
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_MODEL_PATH = os.path.join(SCRIPT_DIR, "gesture_model.pkl")


class GestureClassifier:
    """Classifier gesture BISINDO berbasis ML (Random Forest)."""

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

    @staticmethod
    def make_empty_hand():
        """Return 63 angka nol (placeholder saat tangan tidak terdeteksi)."""
        return [0.0] * 63

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
                   Atau (None, 0.0) jika tidak ada tangan
        """
        # Tidak ada tangan sama sekali
        if right_hand is None and left_hand is None:
            return "OFF", 1.0

        # Ekstrak + normalisasi fitur
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

        # Gabung: 63 kiri + 63 kanan = 126 fitur
        features = np.array(left_feat + right_feat).reshape(1, -1)

        # Prediksi
        prediction = self.model.predict(features)[0]
        probabilities = self.model.predict_proba(features)[0]
        confidence = float(np.max(probabilities))

        return prediction, confidence
