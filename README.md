# 🤟 BISINDO Gesture Recognition
> Sistem Penerjemah Alfabet Bahasa Isyarat Indonesia (BISINDO) Berbasis Computer Vision & Machine Learning.

[![Python Version](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11-blue.svg)](https://www.python.org/)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10.14-green.svg)](https://developers.google.com/mediapipe)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-Ensemble-orange.svg)](https://scikit-learn.org/)
[![TTS Engine](https://img.shields.io/badge/TTS-Windows%20SAPI%20%7C%20gTTS-red.svg)](https://learn.microsoft.com/en-us/dotnet/api/system.speech.synthesis)

Sistem ini dirancang untuk menjembatani komunikasi antara teman-teman Tuli dan masyarakat dengar dengan menerjemahkan gesture alfabet Bahasa Isyarat Indonesia (BISINDO) secara langsung (*real-time*) menjadi teks dan suara (*Text-to-Speech*).

---

## 📹 Video Demonstrasi Real-Time
Berikut adalah rekaman demonstrasi langsung dari sistem saat dijalankan (*raw screen record* tanpa edit):

👉 **[Tonton Video Demo Aplikasi (video-dokumentasi-bisindo.mp4)](./video-dokumentasi-bisindo.mp4)**

*(Tips: Rekam layar Anda saat menjalankan program, simpan hasilnya dengan nama `video-dokumentasi-bisindo.mp4` di folder utama proyek agar tautan di atas otomatis terhubung secara lokal).*

---


## 🚀 Fitur Utama
1. **Klasifikasi 26 Huruf BISINDO Lengkap (A–Z):** Mendukung gesture satu tangan maupun dua tangan sesuai kaidah BISINDO asli (GERKATIN & LINKSOS).
2. **Model Machine Learning Ensemble:** Menggabungkan kekuatan **Random Forest (300 estimator)** dan **Support Vector Machine (SVM RBF)** menggunakan metode *Soft Voting* untuk akurasi klasifikasi yang tangguh.
3. **Representasi Fitur 156 Dimensi:** Kombinasi 126 koordinat landmark tangan 3D yang dinormalisasi (*scale & position invariant*) dan 30 fitur sudut sendi jari untuk membedakan huruf dengan gesture mirip (seperti A, T, dan X).
4. **Augmentasi Data di Memori:** Melatih model dengan variasi buatan (noise $\sigma=0.012$, rotasi $\pm15^\circ$, skala $\pm10\%$, dan shear $\pm0.05$) agar deteksi tetap akurat pada berbagai sudut kamera dan jarak.
5. **Dua Metode Deteksi Huruf J:** Melalui lintasan dinamis jari kelingking kiri (`JDetector`) atau menahan posisi huruf "I" selama 3 detik dengan indikator *timer* visual di layar.
6. **Engine TTS Windows SAPI:** Menggunakan API suara internal Windows via PowerShell, memberikan ketahanan tinggi untuk pemanggilan suara berulang kali tanpa risiko *crash* atau *freezing*.

---

## 💻 Teknologi yang Digunakan (Tech Stack)

Aplikasi ini dibangun menggunakan kombinasi pustaka pemrosesan citra (*computer vision*), analisis data, dan kecerdasan buatan berikut:

| Pustaka / Teknologi | Peran & Fungsi dalam Sistem |
| :--- | :--- |
| **Python (3.9 - 3.11)** | Bahasa pemrograman utama sebagai pengintegrasi seluruh modul pemrosesan video, model klasifikasi, dan *output* suara. |
| **OpenCV (`opencv-python`)** | Mengambil aliran *feed* video dari kamera (*webcam*) secara *real-time*, merender elemen UI (seperti teks terjemahan dan bar indikator visual), serta menampilkan jendela interaksi. |
| **MediaPipe (`mediapipe`)** | Kerangka kerja deteksi tubuh dari Google yang bertugas melacak 21 titik koordinat landmark 3D (X, Y, Z) pada tangan kiri dan kanan secara instan. |
| **Scikit-Learn (`scikit-learn`)** | Digunakan untuk mengonfigurasi dan melatih model klasifikasi *Ensemble* (kombinasi *Random Forest* dengan 300 pepohonan keputusan dan *Support Vector Machine* RBF) untuk memprediksi huruf berdasarkan bentuk landmark tangan. |
| **NumPy (`numpy`)** | Pustaka komputasi numerik yang mengolah koordinat landmark tangan 3D, melakukan normalisasi geometris (*scale & position invariant*), dan menghitung nilai cosinus sudut sendi jari. |
| **Windows SAPI (`System.Speech`)** | Mesin suara utama (*Text-to-Speech*) berbasis sistem Windows (via *PowerShell subprocess*) yang bekerja secara *offline*, hemat memori, dan bebas *crash* saat dipanggil berulang kali. |
| **gTTS & Pygame** | Pustaka *Text-to-Speech* daring (*Google Translate API*) bersama pemutar audio *Pygame* sebagai alternatif cadangan (*fallback*) untuk platform non-Windows. |

---

## 🛠️ Persiapan & Instalasi

### 1. Inisialisasi Environment
Direkomendasikan menggunakan Python 3.9 s.d 3.11. Buka terminal atau PowerShell pada direktori proyek:

```powershell
# Membuat virtual environment
python -m venv venv

# Aktivasi virtual environment (Windows)
.\venv\Scripts\Activate.ps1
```

### 2. Pemasangan Dependensi
Pasang semua pustaka yang diperlukan ke dalam *virtual environment*:

```powershell
pip install opencv-python mediapipe numpy scikit-learn
pip install gTTS pygame pyttsx3
```

---

## 📖 Panduan Alur Kerja (Workflow)

### Langkah 1: Pengumpulan Dataset Landmark
Jika Anda ingin merekam data gesture Anda sendiri atau melengkapi data yang kurang:

```powershell
python src/collect_data.py
```
* **Pilih Opsi 2** untuk merekam huruf tertentu (misal: `ADFTX`).
* **Pilih Opsi 3** untuk melanjutkan perekaman sampel yang belum mencapai target.
* Tekan **SPACE** untuk mulai merekam, tunjukkan gesture di depan kamera, dan tekan **Q** untuk berlanjut ke huruf berikutnya.

### Langkah 2: Pelatihan Model
Latih ulang model klasifikasi ensemble dengan dataset terbaru:

```powershell
python src/train_model.py
```
Proses ini akan membaca semua berkas CSV di folder `dataset/`, melakukan augmentasi data 5 kali lipat di memori (~24.000 sampel total), mengekstrak sudut sendi, melatih model ensemble, dan mengekspor model siap pakai ke `src/gesture_model.pkl`.

### Langkah 3: Menjalankan Aplikasi Utama
Mulai aplikasi penerjemah real-time:

```powershell
python src/main.py
```

---

## ⌨️ Kontrol Keyboard & Antarmuka

Aplikasi utama menyediakan visualisasi informasi di layar kamera serta kontrol keyboard interaktif:

| Tombol | Fungsi Aksi |
| :--- | :--- |
| `SPACE` | Menyisipkan karakter spasi (pemisah kata). |
| `BACKSPACE` | Menghapus satu huruf terakhir dari kalimat terjemahan. |
| `ENTER` | Melafalkan kalimat terjemahan yang terkumpul menggunakan suara (TTS). |
| `R` | Menghapus seluruh kalimat terjemahan di layar (Reset). |
| `ESC` | Menghentikan aliran kamera dan menutup aplikasi dengan aman. |

> 💡 **Auto-TTS:** Sistem secara otomatis melafalkan kalimat terjemahan jika kamera tidak mendeteksi tangan apa pun selama 5 detik berturut-turut.

---

## 📂 Struktur Direktori Proyek

```
bisindo-gesture/
├── dataset/                   # Dataset landmark tangan dalam bentuk berkas CSV
│   ├── bisindo_A.csv
│   ├── bisindo_B.csv
│   └── ...
├── src/                       # Source code utama aplikasi
│   ├── main.py                # Loop aplikasi utama (real-time camera stream & UI)
│   ├── gesture_classifier.py  # Pemuatan model & normalisasi landmark (156 fitur)
│   ├── train_model.py         # Skrip augmentasi data & pelatihan model (RF + SVM)
│   ├── motion_tracker.py      # JDetector untuk lacak lintasan dinamis kelingking kiri
│   ├── stabilizer.py          # Modul anti-jitter (Voting stabilizer)
│   ├── tts.py                 # Engine Text-to-Speech (Windows SAPI & fallback gTTS)
│   └── gesture_model.pkl      # Model klasifikasi ensemble tersimpan (biner)
├── PRDBisindoGesture.md       # Product Requirements Document (PRD)
├── Workflow.md                # Dokumentasi alur kerja proyek lengkap
└── README.md                  # Panduan ringkas penggunaan sistem 
```

---

## ⚙️ Pemecahan Masalah (Troubleshooting)

### 1. Suara TTS Tidak Terdengar (Atau Hanya Berbunyi Sekali)
* **Penyebab:** Driver COM `pyttsx3` sering mengalami kegagalan *state* pada OS Windows saat dipanggil berulang.
* **Solusi:** Sistem saat ini menggunakan Windows SAPI via PowerShell. Pastikan PowerShell terpasang dan dapat dijalankan tanpa hambatan hak akses pada perangkat Anda.

### 2. Huruf Tertentu Sulit Terdeteksi atau Sering Tertukar
* **Penyebab:** Sudut tangan saat berpose di depan kamera berbeda dengan sudut saat data direkam.
* **Solusi:** Lakukan perekaman tambahan untuk huruf tersebut menggunakan `collect_data.py` (Opsi 2). Variasikan jarak tangan, sudut kemiringan, dan pencahayaan sewaktu merekam. Kemudian jalankan `train_model.py` kembali.

### 3. Error `AttributeError` atau `ModuleNotFound` pada MediaPipe
* **Penyebab:** Python menggunakan *environment* global atau terjadi konflik versi library.
* **Solusi:** Selalu jalankan skrip melalui virtual environment yang telah diaktivasi (`.\venv\Scripts\Activate.ps1`).

---

## 📚 Referensi & Media Visual
* **Panduan Gesture BISINDO:** Gambar panduan dan poster media visual alfabet isyarat diperoleh dari [Vektor Premium Alfabet Bahasa Isyarat BISINDO - Magnific Indonesia](https://www.magnific.com/idn/vektor-premium/alfabet-bahasa-isyarat-bisindo-jari-manusia_402829456.htm).

---
*Dikembangkan dengan penuh dedikasi untuk mendukung inklusivitas komunikasi teman-teman Tuli di Indonesia.* 🤟