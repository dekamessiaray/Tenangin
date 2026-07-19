# Tenang.in - Skrining Dini Risiko Kesehatan Mental (Streamlit)

Prototipe web untuk penelitian **Tenang.in**: sistem deteksi dini risiko
kesehatan mental berbasis **stacked ensemble machine learning**
(XGBoost + CatBoost + LightGBM, meta-learner Logistic Regression),
dibangun dengan **Streamlit**.

Fokus: alat skrining (tidak ada halaman "Tentang Riset" terpisah).
Desain: glassmorphism putih dan biru kental (blur 22-28px), ikon Lucide
(bukan emoji), heading Space Grotesk, body Inter, radius 24px, spacing
longgar. Laporan PDF pakai Times New Roman dengan kop surat logo besar.

## Struktur Proyek

```
tenangin/
├── app.py                        # Aplikasi utama (routing semua halaman)
├── requirements.txt
├── .streamlit/
│   └── config.toml                # Kunci tema light (penting, lihat catatan di bawah)
├── assets/
│   ├── logo.png                    # Logo asli (resolusi penuh)
│   ├── logo_nav.png                 # Logo untuk nav bar (260px)
│   └── logo_pdf.png                 # Logo untuk kop surat laporan PDF (700px, >490 DPI)
├── model/
│   ├── predict.py                  # Wrapper prediksi (load artifacts, encode, predict)
│   └── artifacts/
│       ├── model.pkl               # StackingClassifier terlatih (dari Tenangin_Final.ipynb)
│       ├── scaler.pkl              # StandardScaler
│       ├── label_encoders.pkl      # dict LabelEncoder per kolom kategorikal
│       └── feature_columns.pkl     # urutan 23 kolom fitur
└── utils/
    ├── questions.py                # Skema wizard self-assessment (23 fitur)
    ├── recommendations.py          # Rekomendasi per kategori risiko + disclaimer
    ├── pdf_report.py                # Generator laporan PDF (Times New Roman, kop surat besar)
    ├── assets.py                   # Helper load logo sebagai base64/path
    ├── icons.py                    # Ikon Lucide sebagai inline SVG (pengganti emoji)
    └── styling.py                  # CSS tema visual (glassmorphism, font, radius)
```

## Menjalankan Secara Lokal

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Fitur

| Fitur | Status |
|---|---|
| Landing Page (hero, mengapa memilih, cara kerja AI dengan panah, tips) | selesai |
| Self Assessment (wizard 4 langkah, progress indicator) | selesai |
| AI Prediction (loading state bertahap sebelum hasil) | selesai |
| Result Dashboard (gauge SVG kustom, kategori, confidence) | selesai |
| Recommendation (per kategori Low/Medium/High + disclaimer) | selesai |
| Therapeutic Space (box breathing dengan tombol Mulai/Berhenti) | selesai |
| Download Report (PDF Times New Roman, kop surat logo besar) | selesai |
| Mental Health Education (expander tanpa bug ikon tumpang tindih) | selesai |
| Ikon Lucide menggantikan seluruh emoji | selesai |
| Glassmorphism putih/biru kental, Space Grotesk + Inter | selesai |

## Model & Dataset

- **Dataset**: OSMI Mental Health in Tech Survey (Kaggle), 1.259 entri, 23 fitur.
- **Model**: Stacked ensemble, base learners XGBoost, CatBoost, LightGBM,
  meta-learner Logistic Regression (`model/artifacts/model.pkl`, hasil training
  di `Tenangin_Final.ipynb`).

## Catatan Penting

- **Gauge hasil skrining memakai SVG kustom (bukan Plotly).** Komponen
  Plotly di Streamlit di-*lazy-load* (diambil terpisah lewat JavaScript
  setelah render awal), yang bisa menyebabkan angka pada gauge terpotong
  atau kartu tampak kosong sesaat sebelum chart selesai dimuat. SVG kustom
  di `render_gauge()` (app.py) dirender langsung sebagai bagian dari HTML,
  jadi selalu tampil instan dan utuh.
- **Kartu kaca (glassmorphism) memakai `st.container(border=True, key="card_*")`,
  BUKAN membuka/menutup tag `<div class="card">` lewat dua panggilan
  `st.markdown()` terpisah.** Pola lama menghasilkan kartu kosong karena
  browser mem-parse tiap panggilan `st.markdown()` secara independen. Kalau
  menambah kartu baru berisi widget native, selalu pakai
  `with st.container(border=True, key="card_xxx"):` (key diawali `card_`
  supaya kena CSS `[class*="st-key-card_"]` di `styling.py`).
- **`.streamlit/config.toml` mengunci tema ke light**, memperbaiki bug label
  radio/selectbox transparan saat browser/OS memakai dark mode.
- **Ikon expander dibuat murni CSS (chevron), tiga lapis proteksi**
  (`font-size:0` + `color:transparent` + `overflow:hidden`) supaya nama
  ikon ("keyboard_arrow_down") tidak pernah tampil sebagai teks mentah
  menimpa label, walau font ikon gagal dimuat.
- Ikon lain memakai Lucide (lisensi ISC), di-*bundle* sebagai inline SVG di
  `utils/icons.py`, bukan dependensi eksternal saat runtime.
- Font PDF memakai Times-Roman/Times-Bold/Times-Italic bawaan reportlab
  (setara Times New Roman, tidak perlu file font eksternal).
- Kolom `Country` di wizard mengikuti daftar negara pada dataset training
  (belum termasuk Indonesia). Jawaban di luar daftar diarahkan ke opsi
  "Lainnya" dan diproses sebagai kategori tak dikenal (fallback).
- Untuk melatih ulang model dengan dataset baru, jalankan ulang
  `Tenangin_Final.ipynb` dan timpa isi `model/artifacts/`.

## Deploy ke Streamlit Community Cloud

**Penting**: proyek ini mengunci versi Python dan seluruh dependency secara
presisi (`runtime.txt` dan `requirements.txt` dengan tanda `==`, bukan `>=`).
Ini WAJIB dipertahankan, karena Streamlit Community Cloud secara default bisa
memakai versi Python terbaru (mis. 3.14) yang belum tentu punya *wheel*
terkompilasi untuk `catboost`/`lightgbm`/`xgboost`, menyebabkan
`ModuleNotFoundError` saat `model.pkl` dibuka (unpickle) walau kodenya benar
dan berjalan mulus di lokal.

Langkah redeploy setelah update repo:
1. Push perubahan `requirements.txt`, `runtime.txt`, dan `utils/styling.py` ke GitHub.
2. Di dashboard Streamlit Cloud, buka app > menu titik tiga > **Reboot app**
   (supaya environment benar-benar dibangun ulang dari awal, bukan sekadar
   restart proses lama).
3. Kalau masih ada opsi "Python version" di **Advanced settings**, pastikan
   sesuai `runtime.txt` (3.12) dan tidak ada override manual ke versi lain.
4. Cek juga tidak ada **Theme** kustom yang di-set manual lewat dashboard
   Streamlit Cloud (Settings > Theme) yang bisa menimpa `.streamlit/config.toml`
   di repo.

## Troubleshooting

- **`ModuleNotFoundError` saat load `model.pkl` di Cloud tapi aman di lokal**:
  hampir selalu berarti versi Python atau versi library (xgboost/catboost/
  lightgbm/scikit-learn) di Cloud berbeda dari yang dipakai saat model
  di-*pickle*. Solusi: pertahankan `runtime.txt` + `requirements.txt` yang
  sudah dikunci presisi di proyek ini, lalu **Reboot app** (bukan cuma push
  ulang) supaya Cloud membangun environment baru dari nol.
- **Label/teks input tidak terbaca (putih di atas putih) hanya di Cloud,
  aman di lokal**: berarti versi Streamlit di Cloud berbeda dari yang
  ditargetkan CSS custom, atau browser/OS pengguna memaksa dark mode dan
  Cloud mengabaikan `config.toml`. Sudah ditambahkan lapisan pertahanan
  `color-scheme: light only` di `utils/styling.py` yang memaksa seluruh
  kontrol native browser (dropdown, input) tetap terang apa pun preferensi
  sistem penggunanya. Kalau tetap muncul setelah redeploy, kemungkinan ada
  Theme override manual di dashboard Streamlit Cloud (lihat poin 4 di atas).

## PENTING: Lokasi `.streamlit/config.toml` relatif terhadap `app.py`

Dari traceback error yang pernah dilaporkan, `app.py` di repo GitHub berada
di dalam subfolder (`Tenangin_Web/app.py`), bukan langsung di root repo.
**Streamlit mencari folder `.streamlit/` di direktori yang SAMA dengan file
yang dijalankan** (atau working directory saat `streamlit run` dipanggil).

Jadi struktur di GitHub harus seperti ini (config SEJAJAR dengan app.py):

```
nama-repo/
└── Tenangin_Web/          <- folder yang berisi app.py (sesuai "Main file path" di Streamlit Cloud)
    ├── app.py
    ├── requirements.txt
    ├── runtime.txt
    ├── .streamlit/
    │   └── config.toml
    ├── assets/
    ├── model/
    └── utils/
```

Kalau `.streamlit/config.toml` ada di root repo tapi `app.py` ada di
subfolder, Streamlit Cloud TIDAK akan membaca config itu sama sekali, dan
tema akan kembali ke default Streamlit (ini kemungkinan besar penyebab
warna merah pada radio button dan dropdown gelap yang muncul di Streamlit
Cloud padahal aman di lokal). Pastikan seluruh isi folder `tenangin/` di
zip proyek ini di-upload sebagai SATU folder utuh ke repo (jangan dipecah
atau dipindah isinya ke lokasi lain), dan "Main file path" di pengaturan
Streamlit Cloud menunjuk ke `<nama-folder>/app.py` yang benar.

## Perbaikan Terbaru (Senior Review Pass)

### 1. Fix kritis: radio button pecah huruf-per-huruf di mobile
Akar masalah: parent flex container membiarkan `<p>` label menyusut di
bawah lebar kontennya sendiri (flex-shrink default tanpa batas), sehingga
pada layar sempit browser membungkus teks per-karakter ("T-i-d-a-k" turun
ke bawah). Diperbaiki dengan mengunci `white-space: nowrap` dan
`flex-shrink: 0` di setiap level (radiogroup, option, wrapper, teks),
sehingga setiap opsi selalu utuh satu baris; kalau ruang tidak cukup,
seluruh opsi (bukan hurufnya) yang pindah baris. Diuji pada lebar
320px-480px, tidak ada lagi pecah karakter dan tidak ada horizontal
scroll.

### 2. Fix bug lingkaran radio (dari kotak/chip jadi lingkaran presisi)
CSS sebelumnya secara tidak sengaja menyasar *wrapper* pembungkus
(selebar seluruh baris) alih-alih lingkaran sesungguhnya yang berada satu
level lebih dalam di struktur DOM. Sudah diperbaiki dengan targeting
presisi + `border-radius: 50%` eksplisit + ukuran tetap 18px, sehingga
tidak lagi bergantung pada gaya bawaan Streamlit yang bisa berbeda antar
versi/deployment.

### 3. Touch target radio & area sentuh
Area klik opsi radio diperbesar dari 18px menjadi ~42px tinggi (mendekati
standar aksesibilitas 44px) lewat padding, tanpa mengubah ukuran visual
lingkarannya.

### 4. Fix animasi/clipping saat pindah tab di mobile
Dua penyebab yang diperbaiki:
- Efek hover `translateY(-1px)` pada tombol sekarang dibatasi hanya untuk
  perangkat dengan mouse (`@media (hover: hover) and (pointer: fine)`),
  karena tap di HP bisa memicu status hover yang "nyangkut" sesaat.
- Ditambahkan scroll-to-top otomatis setiap kali navigasi lewat nav pill
  (fungsi `goto()` di `app.py`), karena kontainer scroll asli Streamlit
  adalah `[data-testid="stMain"]` (bukan `window`), sehingga jika halaman
  sebelumnya di-scroll ke bawah, halaman baru sebelumnya ikut tampil
  dari posisi scroll yang sama (terlihat seperti konten "terpotong" di
  atas).

### 5. PDF Report - didesain ulang total menjadi laporan klinis profesional
- Font: Helvetica/Helvetica-Bold (bawaan reportlab, bukan Times New Roman
  lagi) untuk kesan modern-formal, bukan gaya template.
- Header lebih kecil dan proporsional (logo 1.35cm), nama "Tenang.in"
  lebih elegan, tagline kecil, dipisah garis tipis.
- Nomor laporan unik (format `TNG-YYYYMMDD-XXXXXX`) di bawah header.
- Info hasil dalam tabel bersih dengan garis tipis antar baris (bukan
  grid tebal), termasu Prediction Confidence.
- Kategori risiko sekarang badge rounded-corner dengan latar pastel +
  teks warna tua (bukan sekadar teks berwarna).
- Ditambahkan score reference bar (mirip rentang referensi laporan lab)
  menunjukkan posisi skor pada skala Low/Medium/High.
- Bagian baru "Tentang Hasil Ini" menjelaskan metodologi singkat,
  mengisi ruang kosong di bawah halaman secara proporsional dan bermakna
  (bukan filler dekoratif).
- Disclaimer dipindah ke footer, font kecil, dipisah garis tipis dari
  konten utama.
- Footer mencantumkan "Generated by Tenang.in", website, tanggal
  generate, dan nomor laporan.
- Sudah diverifikasi terprogram: 0 tabrakan teks, badge & score bar
  diposisikan tepat, whitespace bawah proporsional (~4cm, sebelumnya
  ~8cm).

## Audit Ilmiah Pipeline Inferensi

Lihat **`PROJECT_AUDIT.md`** untuk audit lengkap pipeline inferensi
(konsistensi dengan training, threshold, Model Agreement, metrik, error
handling) yang dilakukan sebagai bagian dari validasi ilmiah penelitian.
Termasuk temuan penting soal diskrepansi base learner antara proposal
(SVM + Extra Trees) dan model yang benar-benar terlatih (CatBoost +
LightGBM) - berguna sebagai bahan diskusi dengan pembimbing.

Poin kunci hasil audit:
- Pipeline inferensi (urutan fitur, scaler, encoder) **identik** dengan
  training - diverifikasi langsung terhadap artifact, bukan asumsi.
- Threshold kategori (`LOW_THRESHOLD=0.40`, `HIGH_THRESHOLD=0.70`) kini
  konstanta bernama di `model/predict.py`, dipakai ulang di seluruh kode
  (termasuk PDF) - bukan lagi angka hardcoded berulang.
- Nilai yang sebelumnya disebut "Confidence" diganti nama menjadi
  **Model Agreement** (kunci dict: `agreement_score`) karena secara
  ilmiah itu mengukur variasi/kesepakatan antar base learner, bukan
  probabilitas kebenaran prediksi - didokumentasikan lengkap di docstring
  `predict_risk()`.
- Metrik evaluasi model kini dibaca dari `model/artifacts/metrics.json`
  (satu sumber kebenaran), bukan hardcoded di Python.
