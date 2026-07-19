# 🔄 Workflow — BISINDO Gesture Recognition System

> **Versi Dokumen:** 1.0  
> **Tanggal:** 19 Juli 2026  
> **Berdasarkan:** PRDBisindoGesture.md v1.0  
> **Status Proyek:** 🟡 In Progress (±75%)

---

## Gambaran Umum Workflow

Proyek ini memiliki **3 workflow utama** yang berjalan secara bertahap:

```
┌──────────────────────────────────────────────────────────────────┐
│                   WORKFLOW BISINDO GESTURE                       │
├──────────────────┬───────────────────┬───────────────────────────┤
│  WF-1            │  WF-2             │  WF-3                     │
│  SETUP &         │  DATA &           │  OPERASIONAL              │
│  ENVIRONMENT     │  TRAINING         │  (Penggunaan Harian)      │
│                  │                   │                           │
│  Dilakukan       │  Dilakukan        │  Dilakukan setiap         │
│  sekali saja     │  per sesi rekam   │  kali mau pakai           │
└──────────────────┴───────────────────┴───────────────────────────┘
```

---

## WF-1 · Setup & Environment

> **Kapan:** Pertama kali clone/download project  
> **Dilakukan:** Sekali saja

```
[START]
   │
   ▼
┌─────────────────────────────────────┐
│  1. Clone / download project        │
│     bisindo-gesture/                │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│  2. Buat Virtual Environment        │
│                                     │
│  python -m venv venv                │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│  3. Aktivasi Virtual Environment    │
│                                     │
│  .\venv\Scripts\Activate.ps1        │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│  4. Install Dependencies            │
│                                     │
│  pip install opencv-python          │
│              mediapipe==0.10.14     │
│              scikit-learn           │
│              numpy                  │
│              gtts pygame            │
│              pyttsx3                │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│  5. Verifikasi Instalasi            │
│                                     │
│  python -c "import mediapipe,       │
│  cv2, sklearn; print('OK')"         │
└──────────────────┬──────────────────┘
                   │
                   ▼
                [SELESAI]
            Lanjut ke WF-2
```

### Checklist Setup

- [ ] Python 3.9+ terinstall
- [ ] Folder `venv/` berhasil dibuat
- [ ] Semua package terinstall tanpa error
- [ ] `import mediapipe` berhasil (tidak ada AttributeError)
- [ ] Kamera terdeteksi (`python src/camera_test.py`)

---

## WF-2 · Data Collection & Model Training

> **Kapan:** Pertama kali, atau saat menambah huruf baru  
> **Status saat ini:** A–F ✅ sudah ada · G–Z 🔴 belum

### WF-2A · Pengumpulan Data (`collect_data.py`)

```
[START]
   │
   ▼
┌─────────────────────────────────────────┐
│  1. Aktifkan venv                       │
│     .\venv\Scripts\Activate.ps1         │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│  2. Jalankan script koleksi data        │
│     python src/collect_data.py          │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│  3. Pilih mode koleksi                  │
│                                         │
│  [1] Semua huruf A–Z (dari awal)        │
│  [2] Huruf tertentu saja                │
│  [3] Lanjutkan yang belum cukup ← Ini  │
│  [4] Kumpulkan kelas ON dan OFF         │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│  4. Per huruf — lakukan ini:            │
│                                         │
│  a) Siapkan pose tangan (lihat ref)     │
│  b) Tekan [SPACE] → countdown 3 detik  │
│  c) Tahan pose → rekam 150 sampel       │
│  d) Tekan [Q] → lanjut huruf berikut   │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│  5. Cek hasil di folder dataset/        │
│                                         │
│  dataset/bisindo_G.csv  ← baru          │
│  dataset/bisindo_H.csv  ← baru          │
│  dst...                                 │
└──────────────────┬──────────────────────┘
                   │
                   ▼
            Lanjut ke WF-2B
```

#### Tips Rekam Data (dari PRD §7.2)

| Tips | Detail |
|------|--------|
| 💡 **Pencahayaan** | Ruangan terang dan merata |
| 🎭 **Latar belakang** | Gunakan latar polos (bukan ramai) |
| ↔️ **Variasi posisi** | Geser tangan sedikit saat merekam |
| 📏 **Variasi jarak** | Dekat dan jauh ke kamera |
| 🤲 **2 tangan** | Untuk huruf A, B, D, F, K, P, Q, T, W, X — pastikan keduanya terlihat |

#### Target Sampel Per Huruf

| Kondisi | Sampel | Estimasi Waktu |
|---------|--------|----------------|
| Minimal (cukup jalan) | 50 sampel | ~1–2 mnt/huruf |
| Standar (direkomendasikan) | 150 sampel | ~3–5 mnt/huruf |
| Optimal (akurasi tinggi) | 200–300 sampel | ~5–10 mnt/huruf |

---

### WF-2B · Pelatihan Model (`train_model.py`)

```
[START — setelah dataset tersedia]
   │
   ▼
┌─────────────────────────────────────────┐
│  1. Pastikan venv aktif                 │
│     .\venv\Scripts\Activate.ps1         │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│  2. Jalankan training                   │
│     python src/train_model.py           │
│                                         │
│     Proses otomatis:                    │
│     - Baca semua CSV di dataset/        │
│     - Gabungkan menjadi satu dataset    │
│     - Split train/test (80/20)          │
│     - Latih Random Forest (200 trees)   │
│     - Simpan model ke gesture_model.pkl │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│  3. Evaluasi hasil training             │
│                                         │
│  Cek output di terminal:                │
│  - Akurasi keseluruhan                  │
│  - Akurasi per huruf (precision/recall) │
│  - Confusion matrix                     │
└──────────────────┬──────────────────────┘
                   │
            ┌──────┴──────┐
            │             │
            ▼             ▼
    [Akurasi ≥ 85%]  [Akurasi < 85%]
            │             │
            ▼             ▼
       Lanjut ke     Kembali ke WF-2A
         WF-3        Tambah sampel untuk
                     huruf yang akurasinya
                     rendah
```

#### Output Training

| File | Lokasi | Keterangan |
|------|--------|------------|
| `gesture_model.pkl` | `src/gesture_model.pkl` | Model siap pakai (~735 KB) |

#### Target Performa (dari PRD §5.1)

| Metrik | Target |
|--------|--------|
| Akurasi per huruf | ≥ 85% |
| Waktu training | < 60 detik |

---

## WF-3 · Operasional (Penggunaan Harian)

> **Kapan:** Setiap kali ingin menggunakan aplikasi  
> **Prasyarat:** WF-1 & WF-2 sudah selesai, model sudah ada

```
[START]
   │
   ▼
┌─────────────────────────────────────────┐
│  1. Buka Terminal / PowerShell          │
│     di folder project                   │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│  2. Jalankan aplikasi via venv          │
│                                         │
│  .\venv\Scripts\python.exe src/main.py  │
│                                         │
│  (PENTING: harus dari terminal sendiri, │
│   bukan dari background agent)          │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│  3. Jendela kamera terbuka              │
│     Sistem aktif dan siap digunakan     │
│                                         │
│  Tampilan UI:                           │
│  ┌───────────────────────────────────┐  │
│  │ Kanan: ON/OFF   Kiri: ON/OFF  FPS │  │
│  │ Gesture: [HURUF]                  │  │
│  │ ████████░░░░ Confidence: 87%      │  │
│  │ Raw: A (0.87)                     │  │
│  ├───────────────────────────────────┤  │
│  │        [Video Kamera]             │  │
│  ├───────────────────────────────────┤  │
│  │ Terjemahan: HALO                  │  │
│  └───────────────────────────────────┘  │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│  4. GUNAKAN APLIKASI                    │
│                                         │
│  → Tunjukkan gesture tangan ke kamera   │
│  → Huruf muncul otomatis di layar       │
│  → Kata/kalimat terakumulasi            │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│  5. Kontrol Keyboard                    │
│                                         │
│  [SPACE]     → Tambah spasi             │
│  [BACKSPACE] → Hapus huruf terakhir     │
│  [ENTER]     → Baca teks sekarang (TTS) │
│  [R]         → Reset semua teks         │
│  [ESC]       → Keluar dari aplikasi     │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│  6. Output Suara (TTS) — Otomatis       │
│                                         │
│  Trigger: tangan tidak terdeteksi       │
│           selama 2 detik                │
│  Engine: gTTS (online) → pyttsx3 (off)  │
│  Bahasa: Bahasa Indonesia               │
└──────────────────┬──────────────────────┘
                   │
                   ▼
                [SELESAI]
              Tekan ESC untuk keluar
```

---

## WF-4 · Pipeline Data Per Frame (Internal)

> **Ini workflow yang terjadi di dalam sistem setiap frame video**

```
Frame Video (dari kamera)
         │
         ▼
  ┌─────────────────┐
  │   OpenCV        │  Capture frame 1280×720
  │   cv2.read()    │  Flip (mirror mode)
  └────────┬────────┘
           │
           ▼
  ┌─────────────────┐
  │   MediaPipe     │  Deteksi hingga 2 tangan
  │   mp.Hands()    │  → 21 landmark per tangan
  └────────┬────────┘  → Label: "Left" / "Right"
           │
           ▼
  ┌─────────────────┐
  │   Normalisasi   │  Per tangan:
  │   (Classifier)  │  - Relatif ke wrist (lm[0])
  │                 │  - Scale-invariant
  │                 │  → 63 fitur per tangan
  └────────┬────────┘
           │
           ▼
  ┌─────────────────┐
  │   Feature       │  [63 kiri] + [63 kanan]
  │   Concatenation │  = 126 fitur total
  │                 │  (0.0 jika tangan tidak ada)
  └────────┬────────┘
           │
           ▼
  ┌─────────────────┐
  │   Random Forest │  model.predict([126 fitur])
  │   Classifier    │  → huruf (A/B/C/.../OFF/ON)
  │                 │  → confidence (0.0–1.0)
  └────────┬────────┘
           │
           ▼
  ┌─────────────────┐
  │   Stabilizer    │  Voting 7 frame terakhir
  │                 │  Filter confidence ≥ 0.55
  │                 │  Hysteresis: 3 frame konsisten
  └────────┬────────┘
           │
           ▼
  ┌─────────────────────────────────┐
  │         OUTPUT LAYER            │
  │                                 │
  │  ┌────────────┐ ┌────────────┐  │
  │  │ Teks       │ │    TTS     │  │
  │  │ Overlay    │ │  (Suara)   │  │
  │  │ (OpenCV)   │ │  Thread    │  │
  │  └────────────┘ └────────────┘  │
  └─────────────────────────────────┘
```

---

## WF-5 · Troubleshooting & Perbaikan

### Masalah Umum dan Solusi

```
Masalah terdeteksi?
       │
       ├─ Error: "Model tidak ditemukan"
       │    └→  Jalankan WF-2A (collect_data) lalu WF-2B (train_model)
       │
       ├─ Error: mediapipe AttributeError / ImportError
       │    └→  Gunakan venv: .\venv\Scripts\python.exe src/main.py
       │        Jangan pakai python system global
       │
       ├─ Kamera tidak terbuka / layar hitam
       │    └→  Pastikan kamera tidak dipakai aplikasi lain
       │        Restart program, coba restart PC
       │
       ├─ Gesture berkedip-kedip / tidak stabil
       │    └→  Normal untuk huruf yang mirip
       │        Tambah sampel untuk huruf tersebut
       │        Jalankan ulang train_model.py
       │
       ├─ Akurasi rendah (< 80%) untuk huruf tertentu
       │    └→  python src/collect_data.py (Mode 3)
       │        Tambah 50–100 sampel dengan variasi
       │        Latih ulang model
       │
       └─ TTS tidak bersuara
            ├─ Online (gTTS): Cek koneksi internet
            └─ Offline: pip install pyttsx3 (di venv)
```

---

## Status & Roadmap

### Progress Saat Ini

| Tahap | Komponen | Status |
|-------|----------|--------|
| WF-1 | Setup & Environment | ✅ Selesai |
| WF-2A | Koleksi data A–F | ✅ Selesai |
| WF-2A | Koleksi data G–Z | 🔴 Belum |
| WF-2B | Training model (A–F) | ✅ Selesai |
| WF-2B | Training model (A–Z) | 🔴 Belum |
| WF-3 | Aplikasi berjalan | ✅ Berfungsi |
| — | Gesture dinamis J, Z | 🔴 Belum |
| — | Testing end-to-end | 🟡 Parsial |

### Langkah Selanjutnya (Prioritas)

```
🔴 SEKARANG — Wajib untuk selesaikan proyek:
   1. Rekam data huruf G–Z (20 huruf)
      → python src/collect_data.py → pilih Mode 1 atau 3
      → Target: minimal 50 sampel/huruf (lebih cepat)
      → Estimasi waktu: ±30–60 menit

   2. Latih ulang model
      → python src/train_model.py
      → Cek akurasi per huruf ≥ 85%

   3. Validasi real-time
      → .\venv\Scripts\python.exe src/main.py
      → Uji semua 26 huruf secara langsung

🟡 SETELAH ITU — Peningkatan kualitas:
   4. Tambah variasi sampel (200–300/huruf)
   5. Uji dengan orang lain (bukan hanya developer)
   6. Tuning confidence threshold

🟢 OPSIONAL — Nice to have:
   7. Gesture dinamis J dan Z
   8. Export teks ke .txt
   9. Simpan riwayat percakapan
```

---

## Kriteria Selesai (dari PRD §11)

Proyek dianggap **100% selesai** jika semua checklist ini terpenuhi:

- [ ] Semua 26 huruf BISINDO terdeteksi dengan akurasi ≥ 85%
- [ ] Sistem berjalan real-time ≥ 15 FPS
- [ ] TTS berfungsi (Bahasa Indonesia, online & offline)
- [ ] Huruf terakumulasi menjadi kata/kalimat dengan benar
- [ ] Auto-TTS aktif saat tangan turun selama 2 detik
- [ ] Semua kontrol keyboard berfungsi (SPACE, BACKSPACE, ENTER, R, ESC)
- [ ] Tidak ada crash selama 30 menit pemakaian

---

## Quick Reference — Perintah Penting

```powershell
# Aktifkan venv (wajib sebelum apapun)
.\venv\Scripts\Activate.ps1

# ── atau tanpa aktivasi, gunakan langsung: ──────────────────

# Jalankan aplikasi utama
.\venv\Scripts\python.exe src/main.py

# Kumpulkan data baru
.\venv\Scripts\python.exe src/collect_data.py

# Latih ulang model
.\venv\Scripts\python.exe src/train_model.py

# Test kamera saja
.\venv\Scripts\python.exe src/camera_test.py

# Test MediaPipe / hand tracking
.\venv\Scripts\python.exe src/hand_tracking_test.py

# Test TTS / audio
.\venv\Scripts\python.exe src/test_audio.py
```

---

*Dokumen ini mengacu pada PRDBisindoGesture.md v1.0*  
*Update jika ada perubahan signifikan pada arsitektur, workflow, atau scope.*
