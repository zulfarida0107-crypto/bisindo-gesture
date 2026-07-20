# 📋 Product Requirements Document (PRD)
# BISINDO Gesture Recognition System

> **Versi Dokumen:** 2.0  
> **Tanggal:** 20 Juli 2026  
> **Status Proyek:** 🟢 Selesai (100% - Siap Produksi)  
> **Platform:** Desktop — Python / OpenCV / MediaPipe / Scikit-Learn

---

## 1. Ringkasan Proyek

### 1.1 Latar Belakang
Bahasa Isyarat Indonesia (BISINDO) merupakan sistem komunikasi utama yang digunakan oleh komunitas Tuli di Indonesia. Namun, kendala komunikasi timbul karena sebagian besar masyarakat dengar tidak memahami bahasa isyarat ini. Hal ini menimbulkan kesenjangan interaksi sosial dan aksesibilitas bagi teman-teman Tuli.

Proyek ini menghadirkan sistem penerjemah isyarat tangan alfabet BISINDO secara **real-time** menggunakan teknologi *Computer Vision* dan *Machine Learning*. Sistem ini mendeteksi pergerakan tangan melalui kamera, mengonversinya menjadi teks, dan menghasilkan *output* suara (*Text-to-Speech*) guna mewujudkan komunikasi yang lebih inklusif dan lancar.

### 1.2 Tujuan Produk
- Mendeteksi dan mengklasifikasikan gesture tangan alfabet BISINDO secara **real-time** dengan akurasi tinggi.
- Mengonversi hasil klasifikasi gesture menjadi susunan teks (kata/kalimat) yang dapat dibaca di layar.
- Menyediakan *output* suara (*Text-to-Speech*) otomatis guna mempermudah interaksi langsung.
- Menjadi pustaka atau fondasi aplikasi aksesibilitas bagi komunitas Tuli di lingkungan publik maupun edukasi.

### 1.3 Target Pengguna
- **Teman-teman Tuli & Bisu:** Sebagai alat bantu komunikasi mandiri dengan masyarakat umum.
- **Guru, Terapis, & Relawan:** Media bantu pengajaran dan pembelajaran interaktif BISINDO.
- **Masyarakat Umum:** Membantu memahami dan berkomunikasi dua arah dengan komunitas Tuli.
- **Pengembang & Peneliti:** Sebagai referensi arsitektur *hand tracking* berbasis landmark 3D dan klasifikasi *ensemble*.

---

## 2. Ruang Lingkup (Scope)

### 2.1 Fitur yang Diimplementasikan (In Scope)
- ✅ **Klasifikasi Alfabet Lengkap (A–Z):** Deteksi seluruh 26 huruf alfabet BISINDO resmi.
- ✅ **Akurasi & Ketahanan Tinggi:** Model klasifikasi *Ensemble* (Random Forest + SVM) dengan fitur geometri sudut sendi.
- ✅ **Augmentasi Data Otomatis:** Pembuatan data sintetis (rotasi, noise, skala, shear) di memori saat latihan untuk meningkatkan ketahanan posisi dan sudut kamera.
- ✅ **Dukungan Dua Tangan (Multi-Hand):** Klasifikasi akurat untuk huruf yang memerlukan interaksi dua tangan sesuai kaidah asli BISINDO.
- ✅ **Dua Metode Deteksi Huruf J:**
  - Metode dinamis: Berbasis arah lintasan gerakan jari kelingking kiri via `JDetector`.
  - Metode statis: Menahan posisi huruf "I" selama 3 detik (dilengkapi visual *timer pointer*).
- ✅ **Engine TTS Stabil & Tanpa Hambatan:** Pemanfaatan Windows SAPI (via PowerShell `System.Speech`) yang bebas *crash* untuk Windows, serta gTTS + pygame untuk non-Windows.
- ✅ **Stabilisasi Gesture:** Algoritma voting frame dan *confidence filtering* guna mereduksi getaran (*jitter*).

### 2.2 Fitur di Luar Cakupan (Out of Scope)
- ❌ Pengenalan gesture kalimat dinamis (frasa kontinu terintegrasi).
- ❌ Penerjemahan ke bahasa isyarat negara lain (seperti ASL, BSL).
- ❌ Deteksi ekspresi wajah atau pembacaan bibir.
- ❌ Aplikasi berbasis Mobile (Android/iOS) atau Web (di luar cakupan rilis desktop ini).

---

## 3. Arsitektur Sistem

### 3.1 Pipeline Pengolahan Data
```
┌─────────┐      ┌──────────────┐      ┌────────────────┐      ┌─────────────────────┐
│  Kamera │───▶  │  MediaPipe   │───▶  │ Normalisasi &  │───▶  │   Model Klasifikasi │
│ (OpenCV)│      │  Landmarker  │      │ Sudut Sendi    │      │   Ensemble (RF+SVM) │
└─────────┘      └──────┬───────┘      │ (156 Fitur)    │      └──────────┬──────────┘
                        │              └────────────────┘                 │
                        │                                                 ▼
                        │                                      ┌─────────────────────┐
                        │                                      │     Stabilizer      │
                        │                                      │ (Confidence Filter) │
                        │                                      └──────────┬──────────┘
                        │                                                 │
                        ▼                                                 ▼
             ┌─────────────────────┐                           ┌─────────────────────┐
             │  Lintasan Dinamis   │                           │    Output Teks &    │
             │     (JDetector)     │──────────────────────────▶│  Text-to-Speech     │
             └─────────────────────┘                           └─────────────────────┘
```

### 3.2 Spesifikasi Representasi Fitur
Sistem melakukan ekstraksi fitur geometri tangan dari frame kamera secara real-time:
1. **Landmark Koordinat 3D (126 Fitur):**
   - MediaPipe mendeteksi 21 titik koordinat per tangan (X, Y, Z).
   - Diperoleh 63 nilai untuk tangan kiri dan 63 nilai untuk tangan kanan.
   - Koordinat dinormalisasi terhadap titik pergelangan (*wrist*) untuk menjamin kestabilan posisi (*position-invariant*).
2. **Fitur Sudut Sendi (30 Fitur):**
   - Menghitung nilai cosinus sudut antar ruas jari utama guna meningkatkan kemampuan model membedakan bentuk genggaman tangan yang mirip (seperti huruf A, T, dan X).
3. **Total Representasi Fitur:** 156 dimensi fitur per frame input.

---

## 4. Spesifikasi Fungsional

### 4.1 Modul Aplikasi Utama (`main.py`)
- **Real-Time Classification:** Menghasilkan prediksi huruf BISINDO secara langsung dari kamera dengan informasi visual *confidence indicator*.
- **Anti-Jitter (Stabilizer):** Melakukan voting mayoritas dari jendela 7 frame terakhir dengan threshold keyakinan minimal 55% untuk meminimalkan fluktuasi huruf.
- **Visual Timer I → J:** Ketika pengguna menunjukkan huruf "I", bar indikator waktu akan muncul. Menahan posisi tersebut selama 3 detik otomatis memicu konversi huruf menjadi "J".
- **Keyboard Control Interface:**

| Tombol | Fungsi Operasional |
| :--- | :--- |
| `SPACE` | Menyisipkan karakter spasi (pemisah kata). |
| `BACKSPACE` | Menghapus karakter terakhir pada kalimat terjemahan. |
| `ENTER` | Memicu TTS untuk mengucapkan seluruh teks yang terakumulasi. |
| `R` | Menghapus seluruh teks terakumulasi (Reset). |
| `ESC` | Menghentikan kamera dan menutup aplikasi secara aman. |

### 4.2 Modul Text-to-Speech (`tts.py`)
- **Windows SAPI Integration:** Menggunakan API internal Windows melalui PowerShell `System.Speech`. Solusi ini terbukti andal untuk pemanggilan berulang secara beruntun tanpa kebocoran memori.
- **Automatic Fallback:** Jika dijalankan di platform non-Windows, sistem beralih ke `gTTS` (Google Text-to-Speech) dengan modul pemutar audio `pygame.mixer`, atau modul offline `pyttsx3` sebagai opsi terakhir.
- **Auto-Read Timeout:** Sistem otomatis melafalkan teks saat tangan diturunkan dari area kamera selama lebih dari 5 detik.

### 4.3 Modul Pengumpulan & Latihan Data (`collect_data.py` & `train_model.py`)
- **Data Augmentation:** Skrip latihan secara otomatis menduplikasi dataset asli hingga 5 kali lipat dengan menerapkan perturbasi acak (noise posisi $\sigma=0.012$, rotasi bidang $\pm15^\circ$, variasi skala $\pm10\%$, dan efek shear $\pm0.05$). Ini meminimalkan ketergantungan model pada satu sudut kamera.
- **Ensemble Classifier:** Latihan menggunakan penggabung suara terbanyak (*Soft Voting Classifier*) dari model **Random Forest Classifier** (300 estimator) dan **Support Vector Machine (SVM)** (kernel RBF, $C=10.0$).

---

## 5. Spesifikasi Non-Fungsional

### 5.1 Performa Klasifikasi & Kecepatan
- **Frame Rate:** Berjalan stabil pada $\ge 15\text{ FPS}$ pada spesifikasi komputer standar (Intel Core i3 / RAM 4GB) tanpa memerlukan akselerasi GPU eksternal.
- **Latency:** Durasi pemrosesan frame hingga klasifikasi huruf berkisar di bawah $100\text{ ms}$.
- **Akurasi Model:** Mencapai akurasi validasi teoritis mendekati $100\%$ pada test split berkat integrasi fitur sudut sendi dan metode augmentasi variasi data.

### 5.2 Kompatibilitas Sistem
- **Sistem Operasi:** Windows 10 / 11 (Dioptimalkan), Linux, dan macOS.
- **Kamera:** Webcam internal laptop atau kamera USB eksternal standar dengan resolusi minimal 720p pada 30fps.
- **Runtime:** Python 3.9 s.d 3.11.

---

## 6. Referensi & Daftar Pustaka
- **MediaPipe Hand Landmarker:** [Google Developer Guide](https://developers.google.com/mediapipe/solutions/vision/hand_landmarker)
- **Kaidah Alfabet BISINDO:** Publikasi resmi Gerakan Kesejahteraan Tunarungu Indonesia (GERKATIN).
- **Vektor Grafis Panduan Isyarat:** [Magnific Indonesia - Vektor Premium Alfabet BISINDO](https://www.magnific.com/idn/vektor-premium/alfabet-bahasa-isyarat-bisindo-jari-manusia_402829456.htm)
- **Scikit-Learn Ensemble Methods:** [Documentation Guide](https://scikit-learn.org/stable/modules/ensemble.html)
- **Windows Speech Synthesis:** [Microsoft System.Speech Assembly](https://learn.microsoft.com/en-us/dotnet/api/system.speech.synthesis)

---
*Dokumen PRD ini mencerminkan spesifikasi final dari sistem BISINDO Gesture Recognition v2.0.*
