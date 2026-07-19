"""
motion_tracker.py — Deteksi gesture dinamis BISINDO
Khusus untuk huruf J: gerakan jari kelingking dari ~vertikal (0°) ke ~horizontal (90°)

Cara kerja:
  1. Lacak posisi ujung kelingking (landmark 20) dari tangan kiri
  2. Hitung sudut arah gerakan selama ~1 detik
  3. Jika gerakan > 60° (dari atas → ke samping), detect sebagai J
"""

from collections import deque
import math
import time


class JDetector:
    """
    Mendeteksi huruf J berdasarkan gerakan jari kelingking kiri.
    Gerakan yang dicari: kelingking bergerak dari posisi vertikal (atas)
    ke posisi horizontal (samping kanan/kiri) dalam 0.5–1.5 detik.
    """

    def __init__(self, window_sec=1.2, min_travel=0.04, angle_threshold=40):
        """
        Args:
            window_sec      : durasi jendela waktu yang dipantau (detik)
            min_travel      : jarak minimal yang harus ditempuh kelingking
            angle_threshold : sudut minimal perubahan arah gerakan (derajat)
        """
        self.window_sec      = window_sec
        self.min_travel      = min_travel
        self.angle_threshold = angle_threshold

        # Buffer: simpan (timestamp, x, y) ujung kelingking
        self._buf = deque()

        self._last_detected = 0      # timestamp deteksi terakhir (cooldown)
        self.cooldown_sec   = 2.0    # jeda minimal antar deteksi

    # ─── Public API ────────────────────────────────────────────────

    @staticmethod
    def is_j_posture(hand_landmarks):
        """
        Postur huruf J / I:
        - Jari kelingking (pinky) harus berada paling tinggi (Y terkecil) dibanding jari lainnya
        """
        pinky_tip = hand_landmarks.landmark[20]
        index_tip = hand_landmarks.landmark[8]
        middle_tip = hand_landmarks.landmark[12]
        ring_tip = hand_landmarks.landmark[16]

        # Kelingking harus berada lebih tinggi (Y lebih kecil) dibanding telunjuk, tengah, manis
        # dengan toleransi jarak minimal 0.05
        if pinky_tip.y > index_tip.y - 0.05 or pinky_tip.y > middle_tip.y - 0.05 or pinky_tip.y > ring_tip.y - 0.05:
            return False

        return True

    def update(self, left_hand_landmarks):
        """
        Panggil setiap frame. Berikan landmark tangan kiri.

        Args:
            left_hand_landmarks: mediapipe hand landmarks (tangan kiri), atau None

        Returns:
            True  → gerakan J terdeteksi
            False → belum / tidak terdeteksi
        """
        now = time.time()

        if left_hand_landmarks is None or not self.is_j_posture(left_hand_landmarks):
            self._buf.clear()
            return False

        # Ambil ujung kelingking (landmark 20)
        pinky_tip = left_hand_landmarks.landmark[20]
        self._buf.append((now, pinky_tip.x, pinky_tip.y))

        # Buang data di luar jendela waktu
        cutoff = now - self.window_sec
        while self._buf and self._buf[0][0] < cutoff:
            self._buf.popleft()

        # Butuh minimal 5 titik untuk analisis
        if len(self._buf) < 5:
            return False

        # Cooldown: jangan deteksi terlalu cepat berulang
        if now - self._last_detected < self.cooldown_sec:
            return False

        if self._detect_j_motion():
            self._last_detected = now
            self._buf.clear()
            return True

        return False

    def reset(self):
        """Reset semua state."""
        self._buf.clear()
        self._last_detected = 0

    # ─── Internal ──────────────────────────────────────────────────

    def _detect_j_motion(self):
        """
        Analisis buffer gerakan:
        - Bagian pertama gerakan: arah ke bawah (angle ~90° dari sumbu X)
        - Bagian akhir gerakan: arah ke kanan/kiri (angle ~0° atau ~180°)
        - Perubahan sudut cukup besar → ini adalah huruf J

        Koordinat MediaPipe: X ke kanan, Y ke bawah (origin kiri atas)
        BISINDO J: kelingking mulai dari atas → melengkung ke bawah-kanan
        """
        points = list(self._buf)
        n = len(points)

        # Hitung total jarak yang ditempuh
        total_travel = 0.0
        for i in range(1, n):
            dx = points[i][1] - points[i-1][1]
            dy = points[i][2] - points[i-1][2]
            total_travel += math.hypot(dx, dy)

        if total_travel < self.min_travel:
            return False  # kelingking tidak cukup bergerak

        # Bagi buffer jadi awal (25%) dan akhir (25%)
        quarter = max(1, n // 4)
        start_pts = points[:quarter]
        end_pts   = points[-quarter:]

        angle_start = self._mean_angle(start_pts)
        angle_end   = self._mean_angle(end_pts)

        if angle_start is None or angle_end is None:
            return False

        # Selisih sudut (absolut, modulo 180°)
        delta = abs(angle_end - angle_start)
        delta = min(delta, 180 - delta)  # ambil sudut terkecil

        return delta >= self.angle_threshold

    @staticmethod
    def _mean_angle(points):
        """
        Hitung arah gerakan rata-rata dari sekumpulan titik berurutan.
        Returns: sudut dalam derajat (0–180), atau None jika tidak cukup titik.
        """
        if len(points) < 2:
            return None

        angles = []
        for i in range(1, len(points)):
            dx = points[i][1] - points[i-1][1]
            dy = points[i][2] - points[i-1][2]
            if abs(dx) > 1e-6 or abs(dy) > 1e-6:
                a = math.degrees(math.atan2(dy, dx)) % 180
                angles.append(a)

        if not angles:
            return None

        return sum(angles) / len(angles)