"""
train_model.py — Latih model ML dari dataset landmark BISINDO
Letakkan file ini di: bisindo-gesture/src/train_model.py

Cara pakai:
  python src/train_model.py
"""

import os
import glob
import csv
import pickle
import numpy as np

DATASET_DIR  = "dataset"
SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
MODEL_OUTPUT = os.path.join(SCRIPT_DIR, "gesture_model.pkl")


def load_dataset():
    """Gabungkan semua CSV di folder dataset/ menjadi X, y."""
    csv_files = glob.glob(os.path.join(DATASET_DIR, "bisindo_*.csv"))
    if not csv_files:
        raise FileNotFoundError(
            f"Tidak ada file CSV di folder '{DATASET_DIR}/'. "
            "Jalankan collect_data.py dulu."
        )

    X, y = [], []
    label_counts = {}

    for path in sorted(csv_files):
        with open(path, "r") as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) != 127:          # 63 kiri + 63 kanan + 1 label
                    continue
                features = list(map(float, row[:126]))
                label    = row[126].strip().upper()
                X.append(features)
                y.append(label)
                label_counts[label] = label_counts.get(label, 0) + 1

    print("\nDataset dimuat:")
    for lbl in sorted(label_counts):
        print(f"  Huruf {lbl}: {label_counts[lbl]} sampel")
    print(f"\nTotal: {len(X)} sampel, {len(set(y))} kelas\n")

    return np.array(X, dtype=np.float32), np.array(y)


def augment_dataset(X, y, augment_factor=5):
    """
    Buat variasi buatan dari dataset untuk membuat model lebih robust.

    Strategi augmentasi (per sampel, per tangan):
      1. Noise posisi  — simulasi getaran tangan / kamera
      2. Rotasi 2D     — simulasi perubahan sudut pandang kamera
      3. Skala         — simulasi tangan lebih dekat/jauh ke kamera
      4. Mirror kecil  — simulasi sedikit kemiringan

    Args:
        X: array (N, 126) fitur landmark
        y: array (N,) label
        augment_factor: berapa kali lipat jumlah data (default 5×)

    Returns:
        X_aug, y_aug yang sudah termasuk data asli
    """
    rng = np.random.default_rng(seed=42)
    X_aug_list = [X]
    y_aug_list = [y]

    n_samples = len(X)
    n_generate = augment_factor * n_samples

    print(f"Augmentasi data: {n_samples} → ~{n_samples + n_generate} sampel ({augment_factor+1}×)...")

    for _ in range(augment_factor):
        X_new = X.copy()

        for i in range(len(X_new)):
            for hand_start in [0, 63]:  # 0=kiri, 63=kanan
                hand = X_new[i, hand_start:hand_start + 63].reshape(21, 3)

                # 1. Noise kecil — simulasi jitter tangan (σ = 0.01)
                noise = rng.normal(0, 0.012, hand.shape).astype(np.float32)
                hand = hand + noise

                # 2. Rotasi 2D (di bidang XY) — ±15 derajat
                angle = rng.uniform(-15, 15) * np.pi / 180
                cos_a, sin_a = np.cos(angle), np.sin(angle)
                rot = np.array([[cos_a, -sin_a], [sin_a, cos_a]], dtype=np.float32)
                hand[:, :2] = hand[:, :2] @ rot.T

                # 3. Skala — simulasi jarak ke kamera (±10%)
                scale = rng.uniform(0.90, 1.10)
                hand = hand * scale

                # 4. Sedikit kemiringan (shear kecil di sumbu X terhadap Y)
                shear = rng.uniform(-0.05, 0.05)
                hand[:, 0] = hand[:, 0] + shear * hand[:, 1]

                # Normalisasi ulang agar tetap scale-invariant
                max_dist = np.max(np.linalg.norm(hand, axis=1))
                if max_dist > 1e-9:
                    hand = hand / max_dist

                X_new[i, hand_start:hand_start + 63] = hand.reshape(63)

        X_aug_list.append(X_new)
        y_aug_list.append(y.copy())

    X_augmented = np.concatenate(X_aug_list, axis=0)
    y_augmented = np.concatenate(y_aug_list, axis=0)

    # Shuffle
    idx = rng.permutation(len(X_augmented))
    print(f"Total setelah augmentasi: {len(X_augmented)} sampel\n")
    return X_augmented[idx], y_augmented[idx]


def add_angle_features(X):
    """
    Tambahkan fitur sudut antar ruas jari untuk membedakan gestur serupa.
    
    Gestur seperti A, T, dan X memiliki posisi jari yang mirip namun sudut
    antar ruas berbeda. Fitur ini membantu model memisahkannya.
    
    Setiap tangan: 21 landmark × 3 (x,y,z) = 63 fitur
    Format X kolom: [0..62] = kiri, [63..125] = kanan
    """
    # Pasangan landmark yang membentuk "ruas" jari
    # (landmark_a, landmark_b, landmark_c) → sudut di titik b
    FINGER_JOINTS = [
        # Jempol
        (1, 2, 3), (2, 3, 4),
        # Telunjuk
        (5, 6, 7), (6, 7, 8),
        # Jari Tengah
        (9, 10, 11), (10, 11, 12),
        # Jari Manis
        (13, 14, 15), (14, 15, 16),
        # Kelingking
        (17, 18, 19), (18, 19, 20),
        # Metacarpal - MCP
        (0, 5, 9), (0, 9, 13), (0, 13, 17),
        # MCP spread
        (5, 9, 13), (9, 13, 17),
    ]

    def compute_angles(landmarks_63):
        """Hitung sudut untuk satu tangan (63 nilai)."""
        lm = landmarks_63.reshape(21, 3)
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
                cos_angle = np.clip(np.dot(ba, bc) / (norm_ba * norm_bc), -1.0, 1.0)
                angles.append(cos_angle)  # cos sudut, bukan derajat (lebih stabil)
        return np.array(angles, dtype=np.float32)  # 15 nilai

    n = X.shape[0]
    extra = []
    for i in range(n):
        left_63  = X[i, :63]
        right_63 = X[i, 63:126]
        angles_left  = compute_angles(left_63)
        angles_right = compute_angles(right_63)
        extra.append(np.concatenate([angles_left, angles_right]))  # 30 nilai

    extra = np.array(extra, dtype=np.float32)
    X_augmented = np.concatenate([X, extra], axis=1)  # 126 + 30 = 156 fitur
    print(f"Fitur ditambah: {X.shape[1]} → {X_augmented.shape[1]} (+ 30 sudut sendi)")
    return X_augmented


def train(X, y):
    from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier, VotingClassifier
    from sklearn.svm import SVC
    from sklearn.preprocessing import StandardScaler
    from sklearn.pipeline import Pipeline
    from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
    from sklearn.metrics import classification_report, confusion_matrix

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print("Membangun model ensemble (RF + SVM)...")

    # ── Model 1: Random Forest yang diperkuat ────────────────────
    rf = RandomForestClassifier(
        n_estimators=300,
        max_depth=None,
        min_samples_leaf=2,
        min_samples_split=3,
        max_features="sqrt",
        class_weight="balanced",  # atasi ketidakseimbangan kelas
        random_state=42,
        n_jobs=-1,
    )

    # ── Model 2: SVM dengan kernel RBF ──────────────────────────
    svm_pipe = Pipeline([
        ("scaler", StandardScaler()),
        ("svm", SVC(
            kernel="rbf",
            C=10.0,
            gamma="scale",
            probability=True,       # diperlukan untuk VotingClassifier
            class_weight="balanced",
            decision_function_shape="ovr",
            random_state=42,
        ))
    ])

    # ── Ensemble: soft voting ────────────────────────────────────
    ensemble = VotingClassifier(
        estimators=[
            ("rf",  rf),
            ("svm", svm_pipe),
        ],
        voting="soft",          # rata-rata probabilitas, lebih akurat
        weights=[1, 2],         # SVM lebih diberi bobot karena lebih baik di fitur normalisasi
    )

    print("Melatih model ensemble (RF + SVM)... ini mungkin ~30 detik\n")
    ensemble.fit(X_train, y_train)

    # ── Evaluasi ─────────────────────────────────────────────────
    acc = ensemble.score(X_test, y_test)
    print(f"\n{'='*55}")
    print(f"  Akurasi test set: {acc:.2%}")
    print(f"{'='*55}\n")

    y_pred = ensemble.predict(X_test)
    print("Laporan per huruf:")
    print(classification_report(y_test, y_pred))

    # Tampilkan confusion matrix untuk kelas yang sering salah
    classes = ensemble.classes_
    cm = confusion_matrix(y_test, y_pred, labels=classes)
    print("\nKelas yang sering salah prediksi (non-diagonal > 0):")
    for i, true_cls in enumerate(classes):
        for j, pred_cls in enumerate(classes):
            if i != j and cm[i, j] > 0:
                print(f"  {true_cls} → {pred_cls}: {cm[i, j]} kali salah")

    return ensemble


def save_model(model):
    os.makedirs(os.path.dirname(MODEL_OUTPUT), exist_ok=True)
    with open(MODEL_OUTPUT, "wb") as f:
        pickle.dump(model, f)
    size_kb = os.path.getsize(MODEL_OUTPUT) // 1024
    print(f"\nModel disimpan ke: {MODEL_OUTPUT}  ({size_kb} KB)")


if __name__ == "__main__":
    X, y = load_dataset()

    # Augmentasi SEBELUM add_angle_features (agar sudut juga ikut tervariasi)
    X, y = augment_dataset(X, y, augment_factor=5)

    # Tambah fitur sudut sendi (30 fitur ekstra)
    X = add_angle_features(X)

    model = train(X, y)
    save_model(model)
    print("\nSelesai! Sekarang jalankan: python src/main.py")
