# 📋 Product Requirements Document (PRD)
# BISINDO Gesture Recognition System

> **Versi Dokumen:** 1.0  
> **Tanggal:** 3 Juni 2026  
> **Status Proyek:** 🟡 In Progress (±75%)  
> **Platform:** Desktop — Python / OpenCV  

---

## 1. Ringkasan Proyek

### 1.1 Latar Belakang

Bahasa Isyarat Indonesia (BISINDO) adalah sistem komunikasi utama yang digunakan oleh komunitas Tuli di Indonesia. Namun, sebagian besar masyarakat umum tidak memahami BISINDO, sehingga menciptakan hambatan komunikasi yang signifikan antara pengguna BISINDO dan non-pengguna.

Proyek ini bertujuan membangun sistem penerjemah isyarat tangan secara **real-time** menggunakan Computer Vision dan Machine Learning, agar pengguna BISINDO dapat berkomunikasi dengan lebih mudah.

### 1.2 Tujuan Produk

- Mendeteksi gesture tangan BISINDO secara **real-time** melalui kamera
- Mengonversi gesture menjadi **teks** yang dapat dibaca
- Menghasilkan **output suara** (TTS) dari teks yang terbentuk
- Menjadi **alat bantu komunikasi** antara pengguna BISINDO dan non-pengguna

### 1.3 Target Pengguna

| Pengguna | Kebutuhan |
|----------|-----------|
| **Pengguna BISINDO** (Tuli/bisu) | Berkomunikasi dengan orang yang tidak mengerti isyarat |
| **Guru/Terapis** | Alat bantu pembelajaran BISINDO |
| **Peneliti/Developer** | Platform eksperimen dan pengembangan lebih lanjut |
| **Masyarakat Umum** | Memahami komunikasi dasar dengan komunitas Tuli |

---

## 2. Ruang Lingkup (Scope)

### 2.1 Yang Ada di Dalam Scope (In Scope)

- ✅ Deteksi gesture alfabet BISINDO (A–F, minimal; target A–Z)
- ✅ Preprocessing landmark tangan via MediaPipe
- ✅ Klasifikasi gesture menggunakan model ML (Random Forest)
- ✅ Akumulasi huruf menjadi kata/kalimat
- ✅ Output Text-to-Speech (TTS) dalam Bahasa Indonesia
- ✅ UI overlay pada video real-time (OpenCV)
- ✅ Pengumpulan data (collect_data.py)
- ✅ Pelatihan model (train_model.py)

### 2.2 Yang Di Luar Scope (Out of Scope)

- ❌ Gesture dinamis (kata, frasa lengkap)
- ❌ Penerjemahan bahasa isyarat ke bahasa lain (Inggris, dll.)
- ❌ Versi mobile/web
- ❌ Deteksi ekspresi wajah
- ❌ Pengenalan suara → isyarat (arah sebaliknya)

---

## 3. Arsitektur Sistem

### 3.1 Pipeline Data

```
┌─────────┐    ┌──────────┐    ┌─────────────┐    ┌────────────┐
│  Kamera │───▶│MediaPipe │───▶│  Normalisasi │───▶│  ML Model  │
│ (OpenCV)│    │(21 titik)│    │ (126 fitur)  │    │(Random     │
└─────────┘    └──────────┘    └─────────────┘    │ Forest)    │
                                                   └─────┬──────┘
                                                         │
                                               ┌─────────▼──────────┐
                                               │    Stabilizer       │
                                               │  (Confidence +      │
                                               │   Voting Filter)    │
                                               └─────────┬──────────┘
                                                         │
                                          ┌──────────────▼─────────────┐
                                          │   Output Layer             │
                                          │  ┌─────────┐  ┌─────────┐  │
                                          │  │  Teks   │  │   TTS   │  │
                                          │  │ Overlay │  │ (Suara) │  │
                                          │  └─────────┘  └─────────┘  │
                                          └────────────────────────────┘
```

### 3.2 Komponen Sistem

| Komponen | File | Fungsi |
|----------|------|--------|
| **Main App** | `src/main.py` | Loop utama, integrasi semua modul |
| **Classifier** | `src/gesture_classifier.py` | Load model + prediksi gesture |
| **Stabilizer** | `src/stabilizer.py` | Anti-jitter (voting + confidence) |
| **TTS Engine** | `src/tts.py` | Text-to-Speech (gTTS / pyttsx3) |
| **Data Collector** | `src/collect_data.py` | Kumpulkan dataset landmark |
| **Model Trainer** | `src/train_model.py` | Latih Random Forest dari CSV |
| **Dataset** | `dataset/bisindo_*.csv` | Data landmark terlatih |
| **Saved Model** | `src/gesture_model.pkl` | Model ML siap pakai |

### 3.3 Representasi Fitur

```
Per frame video:
  Tangan Kanan:  21 landmark × 3 (x, y, z) = 63 fitur
  Tangan Kiri:   21 landmark × 3 (x, y, z) = 63 fitur
  ─────────────────────────────────────────────────────
  Total:         126 fitur (tangan tidak terdeteksi = 0)

Normalisasi:
  - Koordinat relatif ke wrist (landmark[0])
  - Scale-invariant (dibagi jarak maksimal)
  - Tidak bergantung posisi tangan di layar
```

---

## 4. Spesifikasi Fungsional

### 4.1 Fitur Utama (Must Have)

#### F-01: Real-Time Gesture Detection
- **Deskripsi:** Sistem harus dapat mendeteksi gesture tangan dalam video streaming secara real-time
- **Input:** Frame video dari kamera (webcam/built-in)
- **Output:** Label gesture (huruf BISINDO) + confidence score
- **Performa:** Minimum 15 FPS agar terasa real-time

#### F-02: Multi-Hand Support
- **Deskripsi:** Sistem harus mendeteksi dan memproses kedua tangan secara bersamaan
- **Alasan:** Banyak huruf BISINDO memerlukan 2 tangan (A, B, D, F, K, P, Q, T, W, X)
- **Perilaku:** Jika salah satu tangan tidak terdeteksi, fiturnya diisi 0

#### F-03: Gesture Stabilization
- **Deskripsi:** Output gesture tidak boleh berkedip-kedip (jitter) antar frame
- **Mekanisme:** Voting dari 7 frame terakhir + confidence threshold ≥ 0.55
- **Hysteresis:** Butuh minimal 3 frame konsisten sebelum berganti huruf

#### F-04: Akumulasi Teks
- **Deskripsi:** Huruf yang terdeteksi terakumulasi menjadi kata/kalimat
- **Aturan penambahan:**
  - Huruf baru ditambahkan jika berbeda dari huruf terakhir
  - Huruf sama diulang jika ditahan > 1.5 detik (Auto-Repeat)
  - Sembunyikan tangan sejenak untuk mengetik huruf sama berturut-turut

#### F-05: Kontrol Keyboard
- **Deskripsi:** User dapat mengontrol sistem lewat keyboard

| Tombol | Aksi |
|--------|------|
| `SPACE` | Tambah spasi (kata baru) |
| `BACKSPACE` | Hapus huruf terakhir |
| `ENTER` | Baca teks via TTS sekarang |
| `R` | Reset semua teks |
| `ESC` | Keluar dari aplikasi |

#### F-06: Text-to-Speech (TTS)
- **Deskripsi:** Teks yang terkumpul dibaca dengan suara
- **Trigger otomatis:** Jika tangan tidak terdeteksi selama 2 detik
- **Trigger manual:** Tombol ENTER
- **Bahasa:** Bahasa Indonesia
- **Engine Priority:**
  1. `gTTS` + `pygame` — online, suara lebih natural (wanita Indonesia)
  2. `pyttsx3` — offline, fallback jika tidak ada internet

#### F-07: UI Overlay
- **Deskripsi:** Tampilan informasi pada video real-time
- **Elemen UI:**
  - Header: status tangan kanan/kiri (ON/OFF)
  - Gesture saat ini (huruf besar, terlihat jelas)
  - Confidence bar (warna: hijau/kuning/merah)
  - Raw prediction (debug info)
  - Footer: teks terakumulasi
  - FPS counter
  - Hint kontrol keyboard

### 4.2 Fitur Pengembangan Data (Developer)

#### F-08: Pengumpulan Data (collect_data.py)
- **Deskripsi:** Script interaktif untuk merekam data landmark tangan
- **Mode:**
  - Mode 1: Kumpulkan semua huruf dari awal
  - Mode 2: Kumpulkan huruf tertentu saja
  - Mode 3: Lanjutkan huruf yang sampelnya masih kurang
- **Target:** 150 sampel per huruf per kelas
- **Output:** File `dataset/bisindo_{HURUF}.csv`

#### F-09: Pelatihan Model (train_model.py)
- **Deskripsi:** Script untuk melatih ulang model ML dari dataset
- **Algoritma:** Random Forest (200 trees)
- **Output:** File `src/gesture_model.pkl`
- **Laporan:** Akurasi per kelas (classification report)

---

## 5. Spesifikasi Non-Fungsional

### 5.1 Performa

| Metrik | Target | Kondisi |
|--------|--------|---------|
| Frame Rate | ≥ 15 FPS | Laptop mid-range, kamera 720p |
| Latensi deteksi | < 200ms | Dari gesture ke output teks |
| Akurasi model | ≥ 85% | Per huruf dengan 150+ sampel |
| Waktu training | < 60 detik | Untuk 6-26 kelas, 150 sampel/kelas |

### 5.2 Keandalan

- Sistem harus tetap berjalan meskipun kamera kehilangan tracking sesaat
- TTS tidak boleh memblokir (blocking) proses deteksi gesture
- Sistem harus memberikan pesan error yang informatif jika model belum dilatih

### 5.3 Kompatibilitas

| Komponen | Spesifikasi |
|----------|-------------|
| **OS** | Windows 10/11 (primary), Linux/macOS (opsional) |
| **Python** | 3.9+ |
| **Kamera** | Webcam USB atau built-in, min. 720p 30fps |
| **RAM** | Min. 4GB (rekomendasi 8GB) |
| **CPU** | Dual-core modern (tidak butuh GPU) |

### 5.4 Usability

- Aplikasi dapat dijalankan dengan satu perintah: `python src/main.py`
- Tidak memerlukan konfigurasi tambahan setelah setup awal
- Feedback visual jelas (confidence bar berwarna) tentang kualitas gesture

---

## 6. Dataset & Model

### 6.1 Dataset Saat Ini (Lokal)

| Kelas | File | Sampel (estimasi) |
|-------|------|-------------------|
| A | `dataset/bisindo_A.csv` | 253 baris |
| B | `dataset/bisindo_B.csv` | ~370 baris |
| C | `dataset/bisindo_C.csv` | ~220 baris |
| D | `dataset/bisindo_D.csv` | ~215 baris |
| E | `dataset/bisindo_E.csv` | ~215 baris |
| F | `dataset/bisindo_F.csv` | ~320 baris |
| OFF | `dataset/bisindo_OFF.csv` | 229 baris |
| ON | `dataset/bisindo_ON.csv` | ~210 baris |

> **Catatan:** Dataset saat ini baru mencakup **6 huruf** (A–F) + 2 kelas kontrol (ON/OFF).  
> Target akhir: **26 huruf** (A–Z) + ON + OFF = 28 kelas.

### 6.2 Referensi Dataset Alternatif (Roboflow)

> Tersedia dataset image-based di Roboflow Universe:
> - **URL:** https://universe.roboflow.com/cv-yjopp/sign-language-bisindo
> - **Format:** Gambar 640×640 px, bounding box, multiclass
> - **Jumlah:** 780–828 gambar, akurasi laporan 96.2%
> - **Catatan:** Format berbeda (image-based vs landmark-based). Jika digunakan, perlu ganti arsitektur ke CNN/YOLO.

### 6.3 Model

- **Algoritma:** Random Forest Classifier (scikit-learn)
- **Fitur:** 126 input (koordinat 3D landmark, ternormalisasi)
- **Trees:** 200
- **File:** `src/gesture_model.pkl` (~735 KB)
- **Pelatihan:** ~5–30 detik pada CPU standar

---

## 7. Status Pengembangan & Roadmap

### 7.1 Status Saat Ini (v2.0 — 75%)

| Komponen | Status |
|----------|--------|
| Pipeline deteksi (MediaPipe → ML) | ✅ Selesai |
| Stabilizer gesture | ✅ Selesai |
| TTS engine (gTTS + pyttsx3) | ✅ Selesai |
| UI overlay real-time | ✅ Selesai |
| collect_data.py | ✅ Selesai |
| train_model.py | ✅ Selesai |
| Dataset A–F (6 huruf) | ✅ Selesai |
| Dataset G–Z (20 huruf sisa) | 🔴 Belum |
| Semua 26 huruf terlatih | 🔴 Belum |
| Gesture dinamis (J, Z) | 🔴 Belum |
| Testing & validasi end-to-end | 🟡 Parsial |

### 7.2 Roadmap Menuju 100%

#### 🔴 Prioritas Tinggi (Untuk Selesaikan Proyek)

1. **Kumpulkan data huruf G–Z** (±2–4 jam)
   - Jalankan: `python src/collect_data.py`
   - Target: 150 sampel per huruf per tangan
   - Pastikan pencahayaan baik dan latar belakang polos

2. **Latih ulang model dengan semua 28 kelas**
   - Jalankan: `python src/train_model.py`
   - Target akurasi: ≥ 85% per kelas

3. **Validasi end-to-end**
   - Uji semua 26 huruf secara real-time
   - Perbaiki huruf dengan akurasi rendah (tambah sampel)

#### 🟡 Prioritas Menengah (Peningkatan Kualitas)

4. **Tambah sampel variasi** (posisi, jarak, pencahayaan)
   - Target: 200–300 sampel per huruf

5. **Uji coba dengan berbagai pengguna** (bukan hanya developer)

6. **Optimasi threshold confidence** per huruf

#### 🟢 Prioritas Rendah (Nice to Have)

7. **Gesture dinamis** untuk huruf J dan Z (menggunakan motion_tracker.py yang sudah ada)
8. **Simpan sesi** (riwayat percakapan)
9. **Export teks** ke file .txt
10. **Konfigurasi UI** (ukuran teks, tema gelap/terang)

---

## 8. Tech Stack

```
Python 3.9+
├── opencv-python       — Capture & tampilan video
├── mediapipe           — Deteksi 21 landmark tangan
├── scikit-learn        — Random Forest classifier
├── numpy               — Manipulasi array fitur
├── gTTS                — Text-to-Speech online (Google)
├── pygame              — Playback audio (untuk gTTS)
└── pyttsx3             — Text-to-Speech offline (fallback)
```

---

## 9. Struktur File Proyek

```
bisindo-gesture/
├── 📄 PRDBisindoGesture.md          ← Dokumen ini
├── 📄 README.md                     ← Panduan penggunaan
├── 📄 .gitignore
│
├── 📁 dataset/                      ← Data landmark CSV
│   ├── bisindo_A.csv                ← 253 sampel
│   ├── bisindo_B.csv
│   ├── bisindo_C.csv
│   ├── bisindo_D.csv
│   ├── bisindo_E.csv
│   ├── bisindo_F.csv
│   ├── bisindo_OFF.csv              ← 229 sampel (no hands)
│   └── bisindo_ON.csv
│
└── 📁 src/
    ├── main.py                      ← Aplikasi utama (entry point)
    ├── gesture_classifier.py        ← ML classifier
    ├── stabilizer.py                ← Anti-jitter
    ├── tts.py                       ← Text-to-Speech engine
    ├── collect_data.py              ← Pengumpulan data
    ├── train_model.py               ← Pelatihan model
    ├── gesture_model.pkl            ← Model tersimpan (~735KB)
    ├── finger_utils.py              ← Utilitas geometri (legacy)
    ├── bisindo_rule.py              ← Rule-based classifier (legacy)
    ├── motion_tracker.py            ← Pelacak gerak (future use)
    ├── time_buffer.py               ← Buffer waktu
    ├── stabilizer.py
    ├── camera_test.py               ← Test kamera
    ├── hand_tracking_test.py        ← Test MediaPipe
    └── test_audio.py                ← Test TTS
```

---

## 10. Risiko & Mitigasi

| Risiko | Dampak | Kemungkinan | Mitigasi |
|--------|--------|-------------|----------|
| Akurasi rendah untuk huruf mirip (B vs R) | Tinggi | Sedang | Tambah sampel variasi + tuning threshold |
| Dataset tidak merepresentasikan variasi pengguna | Tinggi | Tinggi | Kumpulkan data dari beberapa orang |
| Kamera kualitas rendah → landmark tidak akurat | Sedang | Sedang | Dokumen requirement kamera minimum |
| TTS online (gTTS) gagal tanpa internet | Sedang | Rendah | pyttsx3 sebagai fallback offline |
| Gesture dinamis (J, Z) tidak terdeteksi | Rendah | Pasti | Dokumentasikan sebagai limitasi v2.0 |
| Ketergantungan MediaPipe API changes | Rendah | Rendah | Pin versi di requirements.txt |

---

## 11. Kriteria Penerimaan (Acceptance Criteria)

Proyek dianggap **selesai (100%)** jika:

- [ ] Semua 26 huruf BISINDO dapat dideteksi dengan akurasi ≥ 85%
- [ ] Sistem berjalan real-time ≥ 15 FPS pada laptop mid-range
- [ ] TTS berfungsi dalam Bahasa Indonesia (online & offline)
- [ ] Huruf terakumulasi menjadi kata/kalimat dengan benar
- [ ] Auto-TTS aktif saat tangan diturunkan selama 2 detik
- [ ] Semua kontrol keyboard berfungsi (SPACE, BACKSPACE, ENTER, R, ESC)
- [ ] Tidak ada crash saat dijalankan selama 30 menit

---

## 12. Referensi

- [MediaPipe Hands Documentation](https://developers.google.com/mediapipe/solutions/vision/hand_landmarker)
- [BISINDO — Bahasa Isyarat Indonesia (Wikipedia)](https://id.wikipedia.org/wiki/Bahasa_Isyarat_Indonesia)
- [Roboflow BISINDO Dataset](https://universe.roboflow.com/cv-yjopp/sign-language-bisindo)
- [scikit-learn Random Forest](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html)
- [gTTS Documentation](https://gtts.readthedocs.io/)

---

*Dokumen ini dibuat berdasarkan kondisi proyek per 3 Juni 2026.*  
*Update dokumen ini setiap ada perubahan signifikan pada arsitektur atau scope proyek.*
