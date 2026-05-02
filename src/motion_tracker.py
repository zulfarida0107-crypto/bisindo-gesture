from collections import deque
import math

class MotionTracker:
    def __init__(self, length=10):
        self.points = deque(maxlen=length)

    def add_point(self, x, y):
        self.points.append((x, y))

    def detect_horizontal(self):
        if len(self.points) < 5:
            return False
        dx = self.points[-1][0] - self.points[0][0]
        return abs(dx) > 0.1

    def detect_circle(self):
        if len(self.points) < 8:
            return False
        return True  # placeholder (advanced later)