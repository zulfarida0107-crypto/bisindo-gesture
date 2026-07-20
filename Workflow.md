# 🔄 Dokumen Alur Kerja (Workflow)
# BISINDO Gesture Recognition System


---

## 1. Pendahuluan

Dokumen ini memuat panduan langkah demi langkah (*standard operating procedure*) dalam mempersiapkan, mengumpulkan data, melatih model, menjalankan, serta memelihara sistem klasifikasi isyarat BISINDO. Alur kerja dibagi menjadi empat tahapan utama:

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│     WF-1        │      │     WF-2        │      │     WF-3        │      │     WF-4        │
│    Setup &      │───▶  │  Pengumpulan    │───▶  │ Latihan Model & │───▶  │  Operasional    │
│  Environment    │      │ Data Landmark   │      │   Evaluasi ML   │      │    Aplikasi     │
└─────────────────┘      └─────────────────┘      └─────────────────┘      └─────────────────┘
```

---

## 2. WF-1 · Setup & Environment

Tahap instalasi dependensi dan penyiapan lingkungan kerja terisolasi (*virtual environment*). Dilakukan sekali saja saat pertama kali memasang aplikasi.

```
[Mulai]
   │
   ▼
┌──────────────────────────────────────────────┐
│ 1. Buat Lingkungan Virtual (Virtual Env)     │
│    python -m venv venv                       │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│ 2. Aktivasi Virtual Environment              │
│    .\venv\Scripts\Activate.ps1               │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│ 3. Pemasangan Pustaka Dependensi (Pip)       │
│    pip install opencv-python mediapipe numpy │
│    pip install scikit-learn gTTS pygame      │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│ 4. Pengujian Akses Kamera dan MediaPipe      │
│    python -c "import cv2, mediapipe, sklearn;│
│    print('Setup Berhasil')"                  │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
                   [Selesai]
```

### Checklist Verifikasi Setup
- [x] Python terpasang (versi yang didukung: 3.9 s.d 3.11).
- [x] Folder `venv/` berhasil dibuat pada root direktori proyek.
- [x] Modul MediaPipe terpasang dengan versi yang tepat (bebas dari error `protobuf` / `AttributeError`).
- [x] Sistem operasi memiliki hak akses penuh untuk mengeksekusi skrip PowerShell (untuk TTS Windows SAPI).

---

## 3. WF-2 · Pengumpulan Data Landmark (`collect_data.py`)

Prosedur pengumpulan sampel koordinat titik sendi tangan menggunakan MediaPipe Hands. Koordinat X, Y, Z dari 21 landmark per tangan direkam ke dalam berkas CSV.

```
[Mulai]
   │
   ▼
┌──────────────────────────────────────────────┐
│ 1. Jalankan Skrip Koleksi                    │
│    python src/collect_data.py                │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│ 2. Tentukan Mode Perekaman                   │
│    [1] Rekam seluruh A-Z dari awal           │
│    [2] Rekam huruf spesifik (misal: ADFTX)   │
│    [3] Lanjutkan yang belum memenuhi target  │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│ 3. Proses Perekaman Per Huruf                │
│    a) Posisikan tangan sesuai kaidah BISINDO  │
│    b) Tekan [SPACE] untuk mulai hitung mundur │
│    c) Tahan posisi hingga 80-150 sampel      │
│    d) Tekan [Q] untuk beralih ke huruf lain  │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
                   [Selesai]
```

### Panduan Teknis Perekaman yang Efektif
1. **Posisi Tangan:** Untuk huruf dua tangan (seperti A, B, D, F, K, P, Q, T, W, X), pastikan kedua tangan terdeteksi oleh sistem di layar (indikator status: `Kanan: ON` & `Kiri: ON`) sebelum menekan tombol rekam.
2. **Variasi Sudut:** Selama proses perekaman sampel (kemajuan bar berjalan), gerakkan tangan sedikit mendekat/menjauh dari kamera, serta miringkan sudut tangan beberapa derajat agar variasi data terekam dengan baik.
3. **Pencahayaan:** Hindari pencahayaan dari belakang (*backlight*) yang dapat mengganggu estimasi kedalaman landmark oleh MediaPipe.

---

## 4. WF-3 · Latihan Model & Evaluasi (`train_model.py`)

Tahap melatih kecerdasan buatan (*Machine Learning*) untuk memetakan landmark tangan menjadi huruf alfabet BISINDO.

### Detail Proses Training di Memori
1. **Pemuatan Berkas:** Skrip memuat seluruh berkas koordinat `.csv` dari direktori `dataset/`.
2. **Augmentasi Data:** Untuk setiap sampel, sistem membuat variasi buatan sebanyak 5 kali lipat (mengubah kemiringan $\pm15^\circ$, skala $\pm10\%$, dan perturbasi noise) guna meningkatkan ketahanan model.
3. **Ekstraksi Fitur Sudut Sendi:** Menghitung 30 sudut sendi jari krusial guna memperkuat pemisahan bentuk gesture yang serupa.
4. **Pelatihan Model Ensemble:** Melatih algoritma gabungan Random Forest (300 pepohonan keputusan) dan Support Vector Machine (SVM) dengan pembobotan seimbang (*balanced class weight*).
5. **Ekspor Model:** Menyimpan file model biner final ke `src/gesture_model.pkl`.

```
[Mulai]
   │
   ▼
┌──────────────────────────────────────────────┐
│ 1. Eksekusi Pelatihan                        │
│    python src/train_model.py                 │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│ 2. Evaluasi Metrik                           │
│    Periksa laporan presisi (Precision),      │
│    sensitivitas (Recall), dan F1-Score       │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
            Lolos Uji Akurasi?
            ├── Ya  ──▶ Simpan src/gesture_model.pkl (Selesai)
            └── Tidak ─▶ Kembali ke WF-2 (Tambah sampel huruf bermasalah)
```

---

## 5. WF-4 · Operasional Aplikasi Utama (`main.py`)

Prosedur penggunaan aplikasi sehari-hari untuk menerjemahkan gerakan menjadi teks dan suara secara *real-time*.

```
[Mulai]
   │
   ▼
┌──────────────────────────────────────────────┐
│ 1. Jalankan Aplikasi Utama                   │
│    python src/main.py                        │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│ 2. Hadapkan Tangan ke Kamera                 │
│    Tunjukkan isyarat alfabet BISINDO.        │
│    Sistem akan menstabilkan prediksi selama  │
│    beberapa frame dan menambahkannya ke layar.│
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│ 3. Konversi Khusus J                         │
│    Tunjukkan isyarat "I", lalu tahan selama   │
│    3 detik. Bar waktu visual akan terisi dan  │
│    otomatis mengonversi huruf menjadi "J".    │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│ 4. Operasi Keyboard                          │
│    - [SPACE]     : Tambah spasi               │
│    - [BACKSPACE] : Hapus huruf terakhir       │
│    - [ENTER]     : Suarakan kalimat via TTS   │
│    - [R]         : Hapus seluruh teks         │
│    - [ESC]       : Keluar                     │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
                   [Selesai]
```

---

## 6. Pemecahan Masalah (Troubleshooting)

| Gejala Masalah | Diagnosis Masalah | Solusi Penanganan |
| :--- | :--- | :--- |
| Terjadi error `FileNotFoundError` pada model | Model klasifikasi biner belum dibuat atau terhapus. | Jalankan proses pelatihan model terlebih dahulu melalui perintah `python src/train_model.py`. |
| Program utama terasa lambat (*lagging*) | Frame rate kamera terlalu tinggi atau pemrosesan FPS terhambat. | Pastikan kamera tidak sedang dipakai oleh aplikasi lain (seperti OBS, Zoom, dll). Tutup aplikasi berat di latar belakang. |
| Suara TTS tidak keluar setelah tombol ENTER ditekan | Gangguan konektivitas gTTS atau COM state pada pustaka pyttsx3 mengalami kegagalan fungsi di Windows. | Sistem saat ini menggunakan Windows SAPI. Pastikan fitur suara bawaan Windows aktif dan volume perangkat tidak dibisukan (*muted*). |
| Prediksi huruf sering berganti dengan cepat (*flickering*) | Kepercayaan diri (*confidence*) model berada di ambang batas bawah akibat pose tidak stabil. | Coba posisikan tangan Anda lebih tegak di depan kamera. Jika masih berlanjut, tambahkan sampel data latih untuk huruf tersebut untuk melatih ulang model. |

---
*Dokumen ini merupakan panduan operasional standar untuk BISINDO Gesture Recognition System v2.0.*
