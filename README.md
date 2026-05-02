# BISINDO Gesture Recognition v2.0 (ML-Based)

## Deskripsi Proyek
BISINDO Gesture Recognition adalah proyek pengenalan gerakan Bahasa Isyarat Indonesia (BISINDO) berbasis Computer Vision + Machine Learning.

### Teknologi
- **Python** — bahasa pemrograman utama
- **OpenCV** — menangkap dan menampilkan video kamera
- **MediaPipe** — deteksi kerangka tangan (21 titik landmark per tangan)
- **scikit-learn (Random Forest)** — model ML untuk klasifikasi gesture
- **gTTS / pyttsx3** — Text-to-Speech untuk output suara

---

## Arsitektur Sistem

```
Kamera → MediaPipe → Normalisasi → ML Model → Stabilizer → TTS + Teks
 (OpenCV)  (21 titik    (relatif ke    (Random    (confidence    (output)
            × 3 coord    wrist)        Forest)     filtering)
            per tangan)
```

**Alur data per frame:**
1. **Kamera** → ambil frame video
2. **MediaPipe** → deteksi 2 tangan → 21 titik × 3 koordinat = 63 angka per tangan
3. **Normalisasi** → koordinat relatif ke pergelangan tangan (agar posisi bebas)
4. **Gabung** → 63 (kiri) + 63 (kanan) = **126 fitur** (tangan tidak terdeteksi = 0)
5. **ML Model** → `model.predict([126 fitur])` → huruf + confidence
6. **Stabilizer** → filter noise, hanya output jika confidence > threshold
7. **TTS** → baca huruf/kata yang terbentuk

---

## Huruf BISINDO

### 1 Tangan (16 huruf)
C, E, G, H, I, J, L, M, N, O, R, S, U, V, Y, Z

### 2 Tangan (10 huruf)
A, B, D, F, K, P, Q, T, W, X

> **Catatan:** J dan Z adalah gesture dinamis (ada gerakan). Untuk v2.0, cukup tahan posisi akhir gesture saat merekam data.

---

## Cara Pakai

### Persiapan (Sekali saja)

```powershell
# 1. Aktifkan virtual environment
.\venv\Scripts\Activate.ps1

# 2. Install dependencies
pip install opencv-python mediapipe scikit-learn numpy
pip install gTTS pygame          # untuk TTS online
pip install pyttsx3              # (opsional) TTS offline, lebih cepat
```

### Langkah 1: Kumpulkan Data (±2-4 jam untuk 26 huruf)

```powershell
python src/collect_data.py
```

- Pilih mode: semua huruf (1), huruf tertentu (2), atau lanjutkan yang kurang (3)
- Untuk setiap huruf:
  - Tekan **SPACE** untuk mulai merekam
  - Tunjukkan gesture sesuai referensi BISINDO
  - Target: **150 sampel per huruf**
  - Tekan **Q** untuk lanjut ke huruf berikutnya
- Data tersimpan di folder `dataset/`

### Langkah 2: Latih Model (±5-30 detik)

```powershell
python src/train_model.py
```

- Membaca semua CSV di folder `dataset/`
- Melatih Random Forest (200 trees)
- Menampilkan akurasi per huruf
- Menyimpan model ke `src/gesture_model.pkl`

### Langkah 3: Jalankan Aplikasi

```powershell
python src/main.py
```

**Kontrol keyboard:**
|     Tombol    |           Fungsi         |
|---------------|--------------------------|
| **SPACE**     | Tambah spasi (kata baru) |
| **BACKSPACE** | Hapus huruf terakhir     |
| **ENTER**     | Baca teks sekarang (TTS) |
| **R**         | Reset semua teks         |
| **ESC**       | Keluar                   |

**Otomatis:** Jika tangan dilepas selama 2 detik, TTS akan membaca teks yang sudah terkumpul.

---

## Struktur File

```
bisindo-gesture/
├── dataset/                    # CSV data landmark (hasil collect_data.py)
│   ├── bisindo_A.csv
│   ├── bisindo_B.csv
│   └── ...
├── src/
│   ├── collect_data.py         # Script pengumpulan data landmark
│   ├── train_model.py          # Script pelatihan model ML
│   ├── gesture_model.pkl       # Model ML terlatih (hasil train_model.py)
│   ├── main.py                 # Aplikasi utama (real-time detection)
│   ├── gesture_classifier.py   # ML classifier (load model + predict)
│   ├── stabilizer.py           # Gesture stabilizer (anti-jitter)
│   ├── tts.py                  # Text-to-Speech engine
│   ├── finger_utils.py         # Utilitas geometri jari (legacy)
│   ├── bisindo_rule.py         # Rule-based classifier (legacy, tidak dipakai)
│   └── ...
├── venv/                       # Virtual environment Python
└── README.md
```

---

## Tips Pengumpulan Data

1. **Pencahayaan** — pastikan ruangan terang dan merata
2. **Latar belakang** — gunakan latar polos (bukan ramai)
3. **Variasi** — geser tangan sedikit (atas/bawah/kiri/kanan) saat merekam agar model lebih robust
4. **Jarak** — variasikan jarak tangan ke kamera (dekat dan jauh)
5. **Kedua tangan** — untuk huruf 2 tangan, pastikan **kedua** tangan terlihat
6. **Cek sampel** — jika akurasi huruf tertentu rendah, tambahkan sampel baru

---

## Troubleshooting

|         Masalah         |                            Solusi                                  |
|-------------------------|--------------------------------------------------------------------|
| "Model tidak ditemukan" | Jalankan `collect_data.py` lalu `train_model.py` dulu              |
| Akurasi rendah (<80%)   | Tambahkan lebih banyak sampel per huruf (200-300)                  |
| Kamera tidak terdeteksi | Pastikan tidak dipakai aplikasi lain, coba restart                 |
| TTS tidak bersuara      | Install `pyttsx3` (offline) atau pastikan koneksi internet (gTTS)  |
| Gesture berkedip-kedip  | Ini normal untuk gesture yang mirip, model butuh lebih banyak data |