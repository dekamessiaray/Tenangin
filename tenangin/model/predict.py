"""
Wrapper inferensi untuk Tenang.in.

Pipeline preprocessing di bawah ini SENGAJA dibuat identik langkah-demi-
langkah dengan fungsi referensi `predict_risk()` pada notebook training
(Tenangin_Final.ipynb, cell terakhir):

    1. Susun ulang kolom input persis sesuai `feature_columns.pkl`
       (urutan yang sama dipakai saat fit scaler & model - reindexing
       dengan artifact ini menjamin urutan benar apa pun urutan input
       dari pemanggil, termasuk dari wizard UI).
    2. Encode setiap kolom kategorikal memakai objek LabelEncoder yang
       SAMA (dimuat dari label_encoders.pkl, bukan dibuat ulang/refit).
       Nilai yang tidak dikenali (di luar `le.classes_`) di-fallback ke
       0, PERSIS seperti logika pada notebook - bukan penanganan baru.
    3. Transform dengan StandardScaler yang SAMA (scaler.pkl, bukan
       instance baru) - satu kali, tidak ada scaling berulang.
    4. `model.predict_proba()` satu kali pada StackingClassifier yang
       sudah dilatih (model.pkl) - tidak ada kalibrasi atau modifikasi
       probabilitas apa pun setelahnya.

Artifact yang dimuat (semua hasil training asli, tidak dibuat ulang di
sini):
    model/artifacts/model.pkl             -> StackingClassifier terlatih
    model/artifacts/scaler.pkl            -> StandardScaler terlatih
    model/artifacts/label_encoders.pkl    -> dict[kolom] -> LabelEncoder
    model/artifacts/feature_columns.pkl   -> urutan kolom fitur saat fit
    model/artifacts/metrics.json          -> metrik evaluasi (referensi)

CATATAN AUDIT (lihat juga PROJECT_AUDIT.md):
Base learner StackingClassifier yang sesungguhnya tersimpan di model.pkl
adalah XGBoost, CatBoost, dan LightGBM (terverifikasi langsung dari
`model.named_estimators_`), BUKAN SVM/Extra Trees seperti disebut pada
sebagian draf proposal. Kode di modul ini murni memuat dan menjalankan
artifact yang ada apa adanya (tidak melatih ulang / tidak mengubah
arsitektur), sehingga selalu konsisten dengan model yang benar-benar
tersimpan. Diskrepansi itu perlu diselaraskan pada dokumen proposal,
bukan pada kode - lihat PROJECT_AUDIT.md untuk detail lengkap.
"""

import json
import os

import numpy as np
import pandas as pd
import joblib

_ARTIFACT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "artifacts")
_cache = {}

# ---------------------------------------------------------------------------
# Ambang batas kategori risiko (Prioritas 2 audit: hindari magic number).
# NILAI TIDAK DIUBAH dari rancangan penelitian - hanya dipindah menjadi
# konstanta bernama, satu sumber kebenaran, dipakai di seluruh modul ini.
#   probability < LOW_THRESHOLD                      -> "Low"
#   LOW_THRESHOLD <= probability < HIGH_THRESHOLD     -> "Medium"
#   probability >= HIGH_THRESHOLD                     -> "High"
# ---------------------------------------------------------------------------
LOW_THRESHOLD = 0.40
HIGH_THRESHOLD = 0.70

# Skala normalisasi untuk agreement score (lihat docstring predict_risk).
# Standar deviasi maksimum teoretis dari 3 probabilitas yang masing-masing
# berada di rentang [0, 1] dipakai sebagai pembagi normalisasi ke [0, 1].
_AGREEMENT_NORMALIZATION_SCALE = 0.5
_FALLBACK_AGREEMENT_SCORE = 0.75  # dipakai hanya jika base_probs gagal dihitung


class ArtifactLoadError(RuntimeError):
    """Error eksplisit saat artifact model/scaler/encoder gagal dimuat,
    supaya pesan error jelas (bukan traceback pickle mentah yang
    membingungkan) apabila terjadi masalah lingkungan deployment
    (mis. versi Python/library yang tidak cocok)."""


def _load_artifacts() -> dict:
    if "bundle" in _cache:
        return _cache["bundle"]

    paths = {
        "model": os.path.join(_ARTIFACT_DIR, "model.pkl"),
        "scaler": os.path.join(_ARTIFACT_DIR, "scaler.pkl"),
        "encoders": os.path.join(_ARTIFACT_DIR, "label_encoders.pkl"),
        "feature_columns": os.path.join(_ARTIFACT_DIR, "feature_columns.pkl"),
    }
    bundle = {}
    for key, path in paths.items():
        if not os.path.exists(path):
            raise ArtifactLoadError(
                f"Artifact '{key}' tidak ditemukan di {path}. "
                "Pastikan folder model/artifacts/ ter-upload lengkap."
            )
        try:
            bundle[key] = joblib.load(path)
        except ModuleNotFoundError as e:
            raise ArtifactLoadError(
                f"Gagal memuat artifact '{key}' karena modul Python "
                f"'{e.name}' tidak tersedia di environment ini. "
                "Biasanya berarti versi Python/scikit-learn/xgboost/"
                "catboost/lightgbm di server berbeda dari saat model "
                "dilatih - cek requirements.txt & runtime.txt."
            ) from e
        except Exception as e:
            raise ArtifactLoadError(
                f"Gagal memuat artifact '{key}' dari {path}: {e}"
            ) from e

    _cache["bundle"] = bundle
    return bundle


def categorize(probability: float) -> str:
    """Kategorisasi risiko dari probabilitas mentah `predict_proba()`.
    Ambang batas TIDAK diubah dari rancangan penelitian - lihat
    LOW_THRESHOLD dan HIGH_THRESHOLD di atas."""
    if probability < LOW_THRESHOLD:
        return "Low"
    elif probability < HIGH_THRESHOLD:
        return "Medium"
    else:
        return "High"


def _encode_input(answers: dict) -> pd.DataFrame:
    """Samakan urutan kolom & encoding kategorikal dengan pipeline
    training. Lihat docstring modul untuk rincian tiap langkah."""
    if not isinstance(answers, dict) or not answers:
        raise ValueError(
            "predict_risk() menerima 'answers' kosong atau bukan dict. "
            "Pastikan seluruh pertanyaan wizard sudah dijawab sebelum "
            "meminta prediksi."
        )

    bundle = _load_artifacts()
    feature_columns = bundle["feature_columns"]
    encoders = bundle["encoders"]

    input_df = pd.DataFrame([answers])

    # Kolom yang tidak terisi (seharusnya tidak terjadi lewat wizard,
    # tapi dijaga untuk pemanggilan langsung/API) diberi 0, PERSIS
    # seperti fallback pada notebook training.
    for col in feature_columns:
        if col not in input_df.columns:
            input_df[col] = 0
    input_df = input_df[feature_columns]  # urutan kolom = urutan saat fit

    for col, le in encoders.items():
        if col in input_df.columns:
            value = str(input_df.loc[0, col])
            if value in le.classes_:
                input_df[col] = le.transform([value])[0]
            else:
                # Kategori tak dikenal -> fallback ke 0 (identik dengan
                # notebook). Contoh pemicu sah: field Country dengan
                # opsi "Lainnya" yang memang di luar cakupan dataset.
                input_df[col] = 0

    input_df = input_df.apply(pd.to_numeric, errors="coerce").fillna(0)
    return input_df


def predict_risk(answers: dict) -> dict:
    """
    Jalankan inferensi stacked ensemble (XGBoost + CatBoost + LightGBM,
    meta-learner Logistic Regression) atas satu set jawaban self-assessment.

    Returns dict:
        probability   : float (0-1) - OUTPUT MENTAH `model.predict_proba()`
                        untuk kelas positif, TANPA modifikasi/kalibrasi/
                        pembulatan apa pun. Konversi ke persen (x100) hanya
                        boleh dilakukan di lapisan tampilan (UI/PDF), tidak
                        pernah di sini.
        category      : "Low" / "Medium" / "High", hasil `categorize()`
                        atas `probability` MENTAH (sebelum pembulatan apa
                        pun), memakai LOW_THRESHOLD/HIGH_THRESHOLD di atas.
        agreement_score : float (0-1) - lihat catatan penting di bawah.
        base_probs    : dict nama_base_learner -> probabilitas kelas
                        positif dari masing-masing base learner (XGBoost,
                        CatBoost, LightGBM), sebelum digabung meta-learner.

    CATATAN PENTING soal `agreement_score` (dahulu dinamai "confidence"):
        Nilai ini BUKAN probabilitas bahwa prediksi benar, dan BUKAN
        tingkat keyakinan statistik dalam pengertian probabilistik baku.
        Nilai ini mengukur MODEL AGREEMENT: seberapa sepakat ketiga base
        learner terhadap kasus ini, dihitung dari variasi (standar deviasi)
        probabilitas kelas positif di antara ketiganya, dinormalisasi ke
        rentang [0, 1] lewat `1 - (std / 0.5)`. Std dekat 0 (ketiga model
        memberi probabilitas yang mirip) -> agreement mendekati 1. Std
        besar (base learner saling berbeda pendapat) -> agreement rendah.
        Ini adalah heuristik variance-based ensemble disagreement yang umum
        dipakai sebagai proksi keandalan prediksi pada literatur ensemble
        learning, TAPI secara matematis berbeda dari probabilitas kalibrasi
        (mis. hasil `CalibratedClassifierCV`) maupun confidence interval
        statistik. Istilah "confidence" sengaja tidak dipakai di kode/UI
        untuk menghindari kesan keliru bahwa ini probabilitas kebenaran.
    """
    bundle = _load_artifacts()
    model = bundle["model"]
    scaler = bundle["scaler"]

    input_df = _encode_input(answers)
    input_scaled = scaler.transform(input_df)  # satu kali, tidak berulang

    proba = float(model.predict_proba(input_scaled)[0][1])  # output mentah
    category = categorize(proba)

    base_probs = {}
    try:
        for name, est in model.named_estimators_.items():
            p = est.predict_proba(input_scaled)[0][1]  # input yang SAMA
            base_probs[name] = float(p)
        spread = float(np.std(list(base_probs.values())))
        agreement_score = float(
            np.clip(1.0 - (spread / _AGREEMENT_NORMALIZATION_SCALE), 0.0, 1.0)
        )
    except Exception:
        agreement_score = _FALLBACK_AGREEMENT_SCORE

    return {
        "probability": proba,
        "category": category,
        "agreement_score": agreement_score,
        "base_probs": base_probs,
    }


def get_model_metrics() -> dict:
    """Baca metrik evaluasi model dari satu sumber kebenaran
    (model/artifacts/metrics.json), bukan hardcode di kode Python.
    Nilai metrik itu sendiri TIDAK diubah oleh fungsi ini - murni dibaca
    dari file yang berisi hasil evaluasi asli pada notebook training."""
    path = os.path.join(_ARTIFACT_DIR, "metrics.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError as e:
        raise ArtifactLoadError(f"File metrik {path} tidak ditemukan.") from e
    data.pop("_comment", None)
    return data
