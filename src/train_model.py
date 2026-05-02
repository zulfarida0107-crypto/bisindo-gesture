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

    return np.array(X), np.array(y)


def train(X, y):
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import classification_report

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print("Melatih Random Forest...")
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=None,
        random_state=42,
        n_jobs=-1,          # pakai semua core CPU
    )
    model.fit(X_train, y_train)

    acc = model.score(X_test, y_test)
    print(f"\nAkurasi test set: {acc:.2%}")
    print("\nLaporan per huruf:")
    print(classification_report(y_test, model.predict(X_test)))

    return model


def save_model(model):
    os.makedirs(os.path.dirname(MODEL_OUTPUT), exist_ok=True)
    with open(MODEL_OUTPUT, "wb") as f:
        pickle.dump(model, f)
    size_kb = os.path.getsize(MODEL_OUTPUT) // 1024
    print(f"Model disimpan ke: {MODEL_OUTPUT}  ({size_kb} KB)")


if __name__ == "__main__":
    X, y = load_dataset()
    model = train(X, y)
    save_model(model)
    print("\nSelesai! Sekarang jalankan: python src/main.py")
