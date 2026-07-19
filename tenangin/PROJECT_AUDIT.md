# Audit Ilmiah Pipeline Inferensi Tenang.in

**Peran audit:** Senior Machine Learning Engineer / Research Reviewer / Software Engineer
**Ruang lingkup:** `model/predict.py`, `utils/pdf_report.py`, `app.py` (bagian tampilan hasil)
**Batasan yang dipatuhi:** tidak ada retraining, tidak ada perubahan dataset,
tidak ada perubahan arsitektur model, tidak ada perubahan nilai probabilitas
atau threshold, tidak ada perubahan alur aplikasi.

---

## Ringkasan Eksekutif

| # | Temuan | Tingkat | Status |
|---|---|---|---|
| 0 | Base learner **sesungguhnya** adalah XGBoost + CatBoost + LightGBM, bukan XGBoost + SVM + Extra Trees | **Kritis (dokumentasi)** | Dilaporkan, lihat detail |
| 1 | Pipeline inferensi (urutan fitur, scaler, encoder, preprocessing) | Diperiksa | **Lolos audit** - identik dengan training |
| 2 | Threshold kategori memakai magic number | Sedang | **Diperbaiki** |
| 3 | "Confidence" sebenarnya adalah agreement antar base learner | Sedang | **Diperbaiki** (nama + dokumentasi) |
| 4 | Metrik evaluasi hardcoded di Python | Rendah | **Diperbaiki** (dipindah ke JSON) |
| 5 | Preprocessing/scaling/encoding ganda, pembulatan prematur | Diperiksa | **Lolos audit** - tidak ditemukan |
| 6 | Probabilistic Risk Score vs `predict_proba()` | Diperiksa | **Lolos audit** - identik |
| 7 | Robustness (input kosong, artifact gagal load, dst.) | Sedang | **Diperbaiki** |
| 8 | Dead code, konstanta terduplikasi | Rendah | **Diperbaiki** |

---

## TEMUAN 0 (PALING PENTING): Diskrepansi Arsitektur antara Proposal dan Model Terlatih

### Fakta yang diverifikasi langsung dari `model/artifacts/model.pkl`

```python
>>> model.named_estimators_.keys()
dict_keys(['xgb', 'cat', 'lgbm'])
>>> type(model.named_estimators_['xgb'])   # XGBClassifier
>>> type(model.named_estimators_['cat'])   # CatBoostClassifier
>>> type(model.named_estimators_['lgbm'])  # LGBMClassifier
>>> type(model.final_estimator_)           # LogisticRegression
```

**Base learner yang benar-benar tersimpan dan dijalankan saat inferensi
adalah XGBoost, CatBoost, dan LightGBM** - bukan XGBoost, SVM, dan Extra
Trees seperti disebutkan pada instruksi audit maupun sebagian draf proposal.
Meta-learner (Logistic Regression) sudah sesuai.

### Alasan ilmiah kenapa ini penting dilaporkan

Sebagai reviewer, saya **tidak bisa mengubah kode untuk "berpura-pura"**
base learner-nya SVM + Extra Trees, karena:

1. `model.pkl` adalah artifact hasil training asli yang di-upload sendiri
   dari notebook (`Tenangin_Final.ipynb`, cell 8-9). Mengubah kode
   `predict.py` agar men-*declare* SVM/Extra Trees tanpa mengubah isi
   binary model.pkl akan membuat **dokumentasi kode berbohong tentang apa
   yang sebenarnya dieksekusi** - ini justru menurunkan validitas ilmiah,
   bukan menaikkan.
2. Instruksi eksplisit "jangan retrain model" dan "jangan ubah arsitektur"
   berarti satu-satunya pilihan yang jujur adalah: kode mengikuti apa yang
   ada di `model.pkl` apa adanya (yang memang sudah benar sejak awal - lihat
   Temuan 1), dan **diskrepansi ini diselesaikan di level dokumen
   proposal/laporan penelitian**, bukan di kode.

### Yang TIDAK saya lakukan
- Tidak mengubah `model.pkl`
- Tidak retrain
- Tidak mengubah `predict.py` untuk "menyamarkan" base learner sesungguhnya

### Rekomendasi
Selaraskan teks proposal/laporan penelitian agar menyebutkan base learner
**XGBoost + CatBoost + LightGBM**, sesuai artifact yang benar-benar dipakai.
Ini mudah dijelaskan ke pembimbing sebagai *hyperparameter/model selection
iteration* yang wajar dalam proses penelitian (banyak penelitian ML
mengalami pergantian kandidat base learner setelah eksperimen), selama
laporan akhir mencerminkan model yang benar-benar dievaluasi dan dipakai.

---

## PRIORITAS 1: Audit Pipeline Inferensi

### Metodologi audit
Dibandingkan baris-per-baris dengan fungsi referensi `predict_risk()` pada
`Tenangin_Final.ipynb` (cell terakhir, notebook training), ditambah
verifikasi langsung terhadap isi artifact:

```python
# Verifikasi urutan fitur
>>> from utils.questions import ALL_FEATURE_KEYS
>>> feature_columns = joblib.load('model/artifacts/feature_columns.pkl')
>>> ALL_FEATURE_KEYS == feature_columns
True   # 23/23 fitur, urutan identik
```

```python
# Verifikasi validitas nilai kategorikal wizard vs label encoder
>>> 'Male' in encoders['Gender'].classes_       # True
>>> 'Female' in encoders['Gender'].classes_     # True
>>> 'non-binary' in encoders['Gender'].classes_ # True
```

### Hasil
- **Urutan fitur**: identik (23/23), dan lebih kuat lagi - kode
  `_encode_input()` melakukan `input_df[feature_columns]` yang secara
  eksplisit MENYUSUN ULANG kolom sesuai `feature_columns.pkl` sebagai
  satu sumber kebenaran, sehingga urutan selalu benar apa pun urutan input
  dari wizard.
- **Scaler**: dimuat langsung dari `scaler.pkl` (obyek `StandardScaler`
  hasil `.fit()` asli saat training), tidak pernah dibuat ulang/di-fit ulang.
- **Label encoder**: dimuat langsung dari `label_encoders.pkl`, encoding
  nilai tak dikenal fallback ke 0 - PERSIS logika pada notebook, bukan
  penanganan baru.
- **Preprocessing**: urutan operasi (reindex kolom -> encode kategorikal ->
  `pd.to_numeric` + `fillna(0)` -> `scaler.transform()`) identik dengan
  notebook.

**Kesimpulan: Tidak ditemukan bug/inkonsistensi pada pipeline inferensi.
Tidak ada perubahan kode diperlukan untuk temuan ini** - hanya ditambahkan
dokumentasi (docstring) yang menjelaskan kesetaraan ini secara eksplisit,
supaya mudah ditunjukkan ke pembimbing/juri.

---

## PRIORITAS 2: Threshold Kategori sebagai Konstanta

### Sebelum
```python
def categorize(probability: float) -> str:
    if probability < 0.40:
        return "Low"
    elif probability < 0.70:
        return "Medium"
    else:
        return "High"
```

### Sesudah
```python
LOW_THRESHOLD = 0.40
HIGH_THRESHOLD = 0.70

def categorize(probability: float) -> str:
    if probability < LOW_THRESHOLD:
        return "Low"
    elif probability < HIGH_THRESHOLD:
        return "Medium"
    else:
        return "High"
```

`LOW_THRESHOLD`/`HIGH_THRESHOLD` sekarang juga diimpor oleh
`utils/pdf_report.py` untuk menggambar zona warna pada score bar visual di
laporan PDF (`BAR_ZONE_BOUNDS = [0.0, LOW_THRESHOLD, HIGH_THRESHOLD, 1.0]`),
menggantikan salinan hardcoded terpisah yang sebelumnya ada di file itu.

**Verifikasi tidak ada perubahan nilai:**
```
categorize(0.39) -> Low     categorize(0.40) -> Medium
categorize(0.69) -> Medium  categorize(0.70) -> High
```
Identik dengan spesifikasi asli.

---

## PRIORITAS 3: Audit "Confidence"

### Evaluasi algoritma
```python
spread = np.std(list(base_probs.values()))
confidence = np.clip(1.0 - (spread / 0.5), 0.0, 1.0)
```
Ini menghitung **standar deviasi probabilitas kelas positif di antara
ketiga base learner**, lalu menormalisasinya jadi skor 0-1 (std kecil =
base learner sepakat = skor tinggi).

**Apakah algoritmanya benar?** Ya - ini adalah heuristik *variance-based
ensemble disagreement* yang lazim dipakai di literatur ensemble learning
sebagai proksi keandalan prediksi. **Algoritma TIDAK diubah.**

**Apakah namanya tepat?** Tidak. "Confidence" secara konvensional
mengacu pada probabilitas kalibrasi atau confidence interval statistik -
bukan variasi antar model. Menyebutnya "Confidence Model" berisiko
disalahpahami (oleh juri/pembimbing) sebagai "probabilitas bahwa prediksi
ini benar", padahal bukan itu yang dihitung.

### Perubahan
- Nama kunci dict: `"confidence"` -> **`"agreement_score"`**
- Label di UI web: "Confidence Model" -> **"Model Agreement"**, dengan
  keterangan kecil "(bukan probabilitas kebenaran)" dan `st.caption()`
  yang menjelaskan metodologinya.
- Label di PDF: "Prediction Confidence" -> **"Model Agreement\*"**, dengan
  catatan kaki:
  > *Model Agreement mengukur seberapa sepakat ketiga base learner
  > (XGBoost, CatBoost, LightGBM) terhadap hasil ini, dihitung dari
  > variasi probabilitas antar model. Ini BUKAN probabilitas kebenaran
  > prediksi maupun confidence interval statistik.
- Docstring lengkap ditambahkan di `predict_risk()` menjelaskan definisi,
  formula, dan interpretasi yang benar - siap dipakai sebagai bahan
  menjawab pertanyaan pembimbing/juri.

**Verifikasi nilai numerik tidak berubah**: skenario uji yang sama
menghasilkan `agreement_score = 0.9611497250403398`, identik dengan nilai
`confidence` sebelum perubahan nama.

---

## PRIORITAS 4: Metrik Evaluasi

### Sebelum (`model/predict.py`)
```python
def get_model_metrics() -> dict:
    return {
        "accuracy": 0.8333,
        "precision": 0.7867,
        ...
    }
```

### Sesudah
Nilai dipindah ke `model/artifacts/metrics.json` (satu sumber kebenaran):
```json
{
  "accuracy": 0.8333,
  "precision": 0.7867,
  "recall": 0.9219,
  "f1_score": 0.8489,
  "roc_auc": 0.8953,
  "n_samples": 1259,
  "n_features": 23,
  "n_test_samples": 252
}
```
```python
def get_model_metrics() -> dict:
    path = os.path.join(_ARTIFACT_DIR, "metrics.json")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    data.pop("_comment", None)
    return data
```
**Nilai metrik TIDAK diubah sama sekali** - hanya dipindah lokasi
penyimpanan. Jika model dievaluasi ulang di masa depan, cukup edit satu
file JSON tanpa menyentuh kode Python.

**Catatan transparansi**: `get_model_metrics()` saat ini **tidak dipanggil
di mana pun** dalam aplikasi (halaman "Tentang Riset" yang dulu
menampilkannya sudah dihapus pada revisi UI sebelumnya). Fungsi ini
dipertahankan (bukan dihapus) karena benar, terdokumentasi, dan berguna
bila ingin ditampilkan kembali - tapi ditandai di sini sebagai *currently
unused* demi transparansi penuh.

---

## PRIORITAS 5 & 6: Audit Preprocessing Ganda dan Kesetaraan Risk Score

Diperiksa baris-per-baris pada `predict_risk()`:
- `scaler.transform()` dipanggil **satu kali** (`input_scaled`), dipakai
  ulang untuk base learner individual (`base_probs`) - tidak ada scaling
  kedua.
- Encoding kategorikal terjadi **satu kali** di `_encode_input()`.
- `proba = float(model.predict_proba(input_scaled)[0][1])` - nilai ini
  **adalah** output mentah `predict_proba()`, `float()` hanya konversi tipe
  (numpy.float64 -> Python float), bukan transformasi nilai.
- `categorize(proba)` dipanggil pada `proba` **sebelum** ada pembulatan
  apa pun - urutan operasi menjamin threshold dievaluasi pada presisi
  penuh.
- Konversi ke persen (`probability * 100`) **hanya** terjadi di lapisan
  tampilan (`app.py`, `pdf_report.py`) via f-string formatting, tidak
  pernah memengaruhi nilai `probability` maupun `category` yang sudah
  dihitung sebelumnya.

**Kesimpulan: tidak ditemukan preprocessing ganda, scaling ganda, encoding
ganda, atau pembulatan yang memengaruhi klasifikasi.** Tidak ada perubahan
kode diperlukan - hanya ditambahkan komentar penjelas di docstring.

---

## PRIORITAS 7: Robustness

| Skenario | Sebelum | Sesudah |
|---|---|---|
| `answers` kosong/`None` | Lolos ke `pd.DataFrame([{}])`, hasil prediksi tidak jelas maknanya, tanpa peringatan | `ValueError` eksplisit dengan pesan jelas |
| Kategori tak dikenal (mis. field Country "Lainnya") | Fallback ke 0 (senyap) | Sama (perilaku training asli dipertahankan), didokumentasikan eksplisit di komentar |
| `model.pkl`/`scaler.pkl`/dll gagal dimuat (file hilang) | `FileNotFoundError` mentah dari `joblib.load` | `ArtifactLoadError` dengan pesan actionable |
| Modul Python hilang saat unpickle (persis insiden Streamlit Cloud sebelumnya - `ModuleNotFoundError`) | Traceback pickle mentah yang membingungkan pengguna | `ArtifactLoadError` menjelaskan kemungkinan penyebab (versi Python/library berbeda) dan mengarahkan ke `requirements.txt`/`runtime.txt` |

Diuji langsung (bukan hanya membaca kode):
```
>>> predict_risk({})
ValueError: predict_risk() menerima 'answers' kosong atau bukan dict...

>>> # model.pkl disembunyikan sementara
>>> predict_risk({'Age': 25})
ArtifactLoadError: Artifact 'model' tidak ditemukan di .../model.pkl...
```

---

## PRIORITAS 8: Dead Code, Import, dan Konstanta Terduplikasi

| Temuan | Tindakan |
|---|---|
| `BAR_ZONE_BOUNDS = [0.0, 0.40, 0.70, 1.0]` di `pdf_report.py` - duplikasi manual dari threshold di `predict.py` | Diganti jadi `[0.0, LOW_THRESHOLD, HIGH_THRESHOLD, 1.0]`, di-*import* dari `model.predict` |
| Label skala score bar `(0.40, "40")`, `(0.70, "70")` hardcoded | Diturunkan dari `LOW_THRESHOLD`/`HIGH_THRESHOLD` |
| Import di `model/predict.py` (`json`, `os`, `numpy`, `pandas`, `joblib`) | Diperiksa - semua terpakai, tidak ada yang dihapus |
| Import di `app.py` terkait model | Diperiksa - hanya `predict_risk` yang diimpor, tidak ada import mati |
| `get_model_metrics()` tidak dipanggil di manapun | Dipertahankan (infrastruktur benar & berguna), didokumentasikan sebagai *unused* pada Prioritas 4 di atas, bukan dihapus |

---

## Daftar File yang Diubah

| File | Jenis Perubahan |
|---|---|
| `model/predict.py` | Refactor: konstanta threshold, rename `confidence`->`agreement_score` + docstring ilmiah, error handling (`ArtifactLoadError`, validasi input), metrik dibaca dari JSON |
| `model/artifacts/metrics.json` | **Baru** - satu sumber kebenaran metrik evaluasi (nilai tidak berubah) |
| `utils/pdf_report.py` | Import konstanta threshold dari `model.predict` (hapus duplikasi), rename parameter/label `confidence`->`agreement_score`/"Model Agreement", tambah catatan kaki ilmiah |
| `app.py` | Rename variabel `confidence`->`agreement_score`, ubah label UI + tambah `st.caption()` penjelasan |

**Tidak ada perubahan pada**: `model/artifacts/model.pkl`, `scaler.pkl`,
`label_encoders.pkl`, `feature_columns.pkl`, `utils/questions.py`,
`utils/recommendations.py`, alur navigasi (`app.py` router), atau nilai
probabilitas/kategori/threshold apa pun.

---

## Verifikasi Akhir (Regresi Numerik)

Skenario uji identik dijalankan sebelum dan sesudah seluruh perubahan di
atas:

```
probability : 0.6223674330894161  (SAMA PERSIS)
category    : "Medium"             (SAMA PERSIS)
agreement   : 0.9611497250403398  (SAMA PERSIS, sebelumnya key "confidence")
base_probs  : xgb=0.7789..., cat=0.7476..., lgbm=0.7322...  (SAMA PERSIS)
```

Seluruh perubahan pada audit ini bersifat **refactoring dan dokumentasi**,
bukan perubahan hasil penelitian.
