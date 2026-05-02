"""
stabilizer.py — Confidence-aware gesture stabilizer
Mencegah output berkedip-kedip (jitter) dengan voting + confidence filtering.
"""

from collections import deque


class GestureStabilizer:
    """
    Stabilizer yang lebih smooth:
    - Hanya menerima prediksi dengan confidence di atas threshold
    - Voting dari N frame terakhir (majority wins)
    - Hysteresis: butuh beberapa frame berbeda sebelum ganti huruf
    """

    def __init__(self, buffer_size=7, min_confidence=0.55, switch_threshold=3):
        """
        Args:
            buffer_size:      jumlah frame untuk voting
            min_confidence:   confidence minimum dari ML model (0.0 - 1.0)
            switch_threshold: minimal berapa frame gesture baru sebelum switch
        """
        self.buffer = deque(maxlen=buffer_size)
        self.min_confidence = min_confidence
        self.switch_threshold = switch_threshold
        self.current_gesture = None
        self.switch_counter = 0

    def update(self, gesture, confidence=1.0):
        """
        Update stabilizer dengan prediksi frame baru.

        Args:
            gesture:    huruf hasil prediksi (str atau None)
            confidence: confidence score dari ML model (float)

        Returns:
            str atau None: gesture stabil, atau None jika belum stabil
        """
        # Filter berdasarkan confidence
        if gesture is None or confidence < self.min_confidence:
            self.buffer.append(None)
        else:
            self.buffer.append(gesture)

        # Butuh minimal 3 frame sebelum menghasilkan output
        valid_entries = [g for g in self.buffer if g is not None]
        if len(valid_entries) < 3:
            return self.current_gesture

        # Voting: ambil gesture yang paling sering muncul
        winner = max(set(valid_entries), key=valid_entries.count)
        winner_count = valid_entries.count(winner)
        total_valid = len(valid_entries)

        # Winner harus muncul di > 50% dari valid entries
        if winner_count / total_valid < 0.5:
            return self.current_gesture

        # Hysteresis: cegah switch terlalu cepat
        if winner != self.current_gesture:
            self.switch_counter += 1
            if self.switch_counter >= self.switch_threshold:
                self.current_gesture = winner
                self.switch_counter = 0
        else:
            self.switch_counter = 0

        return self.current_gesture

    def reset(self):
        """Reset semua state."""
        self.buffer.clear()
        self.current_gesture = None
        self.switch_counter = 0