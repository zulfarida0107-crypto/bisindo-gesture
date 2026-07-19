# BISINDO Gesture Recognition v2.0 (ML-Based)

## Deskripsi Proyek
BISINDO Gesture Recognition adalah proyek pengenalan gerakan Bahasa Isyarat Indonesia (BISINDO) berbasis Computer Vision + Machine Learning.

### Teknologi
- **Python** — bahasa pemrograman utama
- **OpenCV** — menangkap dan menampilkan video kamera
- **MediaPipe** — deteksi kerangka tangan (21 titik landmark per tangan)
- **scikit-learn (Random Forest)** — model ML untuk klasifikasi gesture
- **gTTS / pyttsx3** — Text-to-Speech untuk output suara

## Arsitektur Sistem
Kamera → MediaPipe → Normalisasi → ML Model → Stabilizer → TTS + Teks
 (OpenCV)  (21 titik    (relatif ke    (Random    (confidence    (output)
            × 3 coord    wrist)        Forest)     filtering)
            per tangan)

**Alur data per frame:**
1. **Kamera** → ambil frame video
2. **MediaPipe** → deteksi 2 tangan → 21 titik × 3 koordinat = 63 angka per tangan
3. **Normalisasi** → koordinat relatif ke pergelangan tangan (agar posisi bebas)
4. **Gabung** → 63 (kiri) + 63 (kanan) = **126 fitur** (tangan tidak terdeteksi = 0)
5. **ML Model** → `model.predict([126 fitur])` → huruf + confidence
6. **Stabilizer** → filter noise, hanya output jika confidence > threshold
7. **TTS** → baca huruf/kata yang terbentuk


### 1 Tangan (9 huruf statis + 1 dinamis)
- **Statis:** C, E, I, L, O, R, U, V, Z
- **Dinamis:** J (Dideteksi menggunakan gerakan nyata melengkung dari kelingking kiri via `JDetector`)

### 2 Tangan (16 huruf statis)
A, B, D, F, G, H, K, M, N, P, Q, S, T, W, X, Y

> **Catatan:** Untuk huruf statis, cukup tahan posisi tangan saat merekam. Khusus huruf **J**, sistem melacak lintasan gerakan secara dinamis sehingga tidak memerlukan rekam data gambar statis.


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

## Tips Pengumpulan Data
1. **Pencahayaan** — pastikan ruangan terang dan merata
2. **Latar belakang** — gunakan latar polos (bukan ramai)
3. **Variasi** — geser tangan sedikit (atas/bawah/kiri/kanan) saat merekam agar model lebih robust
4. **Jarak** — variasikan jarak tangan ke kamera (dekat dan jauh)
5. **Kedua tangan** — untuk huruf 2 tangan, pastikan **kedua** tangan terlihat
6. **Cek sampel** — jika akurasi huruf tertentu rendah, tambahkan sampel baru
