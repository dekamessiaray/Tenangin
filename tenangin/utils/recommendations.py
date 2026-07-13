
RECOMMENDATIONS = {
    "Low": {
        "icon": "shield_check",
        "color": "#16A34A",
        "bg": "rgba(22,163,74,0.10)",
        "title": "Risiko Rendah",
        "summary": "Kondisimu saat ini terpantau baik.",
        "points": [
            "Pertahankan pola hidup sehat yang sudah kamu jalani.",
            "Terus jaga rutinitas tidur dan aktivitas fisik.",
            "Tetap terhubung dengan keluarga dan teman terdekat.",
            "Lakukan self-assessment secara berkala untuk memantau kondisimu.",
        ],
    },
    "Medium": {
        "icon": "activity",
        "color": "#D97706",
        "bg": "rgba(217,119,6,0.10)",
        "title": "Risiko Sedang",
        "summary": "Ada beberapa indikasi yang perlu kamu perhatikan.",
        "points": [
            "Kelola stres dengan teknik relaksasi (coba Ruang Tenang di aplikasi ini).",
            "Pastikan waktu tidur cukup, sekitar 7-9 jam per malam.",
            "Luangkan waktu untuk olahraga ringan secara rutin.",
            "Bicarakan perasaanmu dengan orang yang kamu percaya.",
        ],
    },
    "High": {
        "icon": "circle_alert",
        "color": "#DC2626",
        "bg": "rgba(220,38,38,0.10)",
        "title": "Risiko Tinggi",
        "summary": "Hasil skrining menunjukkan indikasi risiko yang perlu perhatian serius.",
        "points": [
            "Disarankan untuk berkonsultasi dengan tenaga profesional (psikolog/psikiater).",
            "Jangan ragu untuk bercerita kepada orang terdekat yang kamu percaya.",
            "Jika dalam kondisi darurat, segera hubungi layanan bantuan kesehatan jiwa terdekat.",
            "Ingat, mencari bantuan adalah langkah yang kuat, bukan tanda kelemahan.",
        ],
    },
}

DISCLAIMER = (
    "Tenang.in bukan alat diagnosis medis. Hasil skrining ini bersifat non-diagnostik "
    "dan hanya berfungsi sebagai alat refleksi awal berbasis data. Untuk penilaian dan "
    "penanganan yang akurat, silakan berkonsultasi dengan tenaga profesional kesehatan mental."
)


def get_recommendation(category: str) -> dict:
    return RECOMMENDATIONS.get(category, RECOMMENDATIONS["Medium"])
