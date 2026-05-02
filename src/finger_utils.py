import mediapipe as mp
import math
import numpy as np

mp_hands = mp.solutions.hands

FINGER_PHALANGES = {
    "Index": {
        "distal": mp_hands.HandLandmark.INDEX_FINGER_TIP,
        "intermediate": mp_hands.HandLandmark.INDEX_FINGER_DIP,
        "proximal": mp_hands.HandLandmark.INDEX_FINGER_PIP,
        "metacarpal": mp_hands.HandLandmark.INDEX_FINGER_MCP
    },
    "Middle": {
        "distal": mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
        "intermediate": mp_hands.HandLandmark.MIDDLE_FINGER_DIP,
        "proximal": mp_hands.HandLandmark.MIDDLE_FINGER_PIP,
        "metacarpal": mp_hands.HandLandmark.MIDDLE_FINGER_MCP
    },
    "Ring": {
        "distal": mp_hands.HandLandmark.RING_FINGER_TIP,
        "intermediate": mp_hands.HandLandmark.RING_FINGER_DIP,
        "proximal": mp_hands.HandLandmark.RING_FINGER_PIP,
        "metacarpal": mp_hands.HandLandmark.RING_FINGER_MCP
    },
    "Pinky": {
        "distal": mp_hands.HandLandmark.PINKY_TIP,
        "intermediate": mp_hands.HandLandmark.PINKY_DIP,
        "proximal": mp_hands.HandLandmark.PINKY_PIP,
        "metacarpal": mp_hands.HandLandmark.PINKY_MCP
    },
    "Thumb": {
        "distal": mp_hands.HandLandmark.THUMB_TIP,
        "intermediate": mp_hands.HandLandmark.THUMB_IP,
        "proximal": mp_hands.HandLandmark.THUMB_MCP,
        "metacarpal": mp_hands.HandLandmark.THUMB_CMC
    }
}

def detect_inter_touch(right_hand, left_hand, threshold=0.06):
    if right_hand is None or left_hand is None:
        return []

    r_lm = right_hand.landmark
    l_lm = left_hand.landmark
    found_touches = []

    for r_finger, r_parts in FINGER_PHALANGES.items():
        for r_phalange, r_idx in r_parts.items():
            r_pt = r_lm[r_idx]

            for l_finger, l_parts in FINGER_PHALANGES.items():
                for l_phalange, l_idx in l_parts.items():
                    l_pt = l_lm[l_idx]

                    dist = math.sqrt(
                        (r_pt.x - l_pt.x) ** 2 +
                        (r_pt.y - l_pt.y) ** 2
                    )

                    if dist < threshold:
                        found_touches.append({
                            "right": {"finger": r_finger, "phalange": r_phalange},
                            "left": {"finger": l_finger, "phalange": l_phalange}
                        })
    return found_touches

def calculate_angle(a, b, c):
    a = np.array([a.x, a.y])
    b = np.array([b.x, b.y])
    c = np.array([c.x, c.y])

    ba = a - b
    bc = c - b

    cosine_angle = np.dot(ba, bc) / (
        np.linalg.norm(ba) * np.linalg.norm(bc)
    )
    angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))
    return np.degrees(angle)

def is_finger_curved(hand_landmarks, finger_name, threshold=30):
    lm = hand_landmarks.landmark

    if finger_name == "Index":
        angle = calculate_angle(lm[5], lm[6], lm[8])
    elif finger_name == "Middle":
        angle = calculate_angle(lm[9], lm[10], lm[12])
    elif finger_name == "Ring":
        angle = calculate_angle(lm[13], lm[14], lm[16])
    elif finger_name == "Pinky":
        angle = calculate_angle(lm[17], lm[18], lm[20])
    else:
        return False

    return angle < (180 - threshold)

def calculate_orientation(p_base, p_tip):
    dx = p_tip.x - p_base.x
    dy = p_base.y - p_tip.y

    angle = math.degrees(math.atan2(dx, dy))
    if angle < 0:
        angle += 360

    return angle

def get_finger_points(hand_landmarks, finger):
    lm = hand_landmarks.landmark
    mapping = {
        "Thumb": (2, 4),
        "Index": (5, 8),
        "Middle": (9, 12),
        "Ring": (13, 16),
        "Pinky": (17, 20)
    }
    base, tip = mapping[finger]
    return lm[base], lm[tip]
