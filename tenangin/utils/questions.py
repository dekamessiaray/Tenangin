
STEPS = [
    {
        "title": "Data Diri",
        "icon": "user",
        "fields": ["Age", "Gender", "Country"],
    },
    {
        "title": "Pekerjaan dan Riwayat",
        "icon": "briefcase",
        "fields": [
            "self_employed", "family_history", "work_interfere",
            "no_employees", "remote_work", "tech_company",
        ],
    },
    {
        "title": "Dukungan dan Kebijakan di Tempat Kerja",
        "icon": "building_2",
        "fields": [
            "benefits", "care_options", "wellness_program",
            "seek_help", "anonymity", "leave",
        ],
    },
    {
        "title": "Persepsi dan Keterbukaan",
        "icon": "message_circle",
        "fields": [
            "mental_health_consequence", "phys_health_consequence",
            "coworkers", "supervisor",
            "mental_health_interview", "phys_health_interview",
            "mental_vs_physical", "obs_consequence",
        ],
    },
]

_COUNTRIES = [
    "Australia", "Austria", "Bahamas, The", "Belgium", "Bosnia and Herzegovina",
    "Brazil", "Bulgaria", "Canada", "China", "Colombia", "Costa Rica", "Croatia",
    "Czech Republic", "Denmark", "Finland", "France", "Georgia", "Germany",
    "Greece", "Hungary", "India", "Ireland", "Israel", "Italy", "Japan", "Latvia",
    "Mexico", "Moldova", "Netherlands", "New Zealand", "Nigeria", "Norway",
    "Philippines", "Poland", "Portugal", "Romania", "Russia", "Singapore",
    "Slovenia", "South Africa", "Spain", "Sweden", "Switzerland", "Thailand",
    "United Kingdom", "United States", "Uruguay", "Zimbabwe",
]

FIELDS = {
    "Age": {
        "label": "Usia (tahun)",
        "type": "number",
        "min": 15, "max": 75, "default": 25,
    },
    "Gender": {
        "label": "Jenis Kelamin",
        "type": "select",
        "options": [
            ("Laki-laki", "Male"),
            ("Perempuan", "Female"),
            ("Lainnya", "non-binary"),
        ],
    },
    "Country": {
        "label": "Negara tempat tinggal/bekerja",
        "type": "select",
        "options": [(c, c) for c in _COUNTRIES] + [("Lainnya (tidak tercantum)", "__OTHER__")],
        "help": "Dataset yang dipakai bersumber dari survei global (belum mencakup semua negara). Pilih 'Lainnya' bila negaramu tidak ada.",
    },
    "self_employed": {
        "label": "Apakah kamu wirausaha / bekerja mandiri (freelance)?",
        "type": "radio",
        "options": [("Tidak", "No"), ("Ya", "Yes")],
    },
    "family_history": {
        "label": "Apakah ada anggota keluarga dengan riwayat gangguan kesehatan mental?",
        "type": "radio",
        "options": [("Tidak", "No"), ("Ya", "Yes")],
    },
    "work_interfere": {
        "label": "Jika pernah mengalami kondisi kesehatan mental, seberapa sering itu mengganggu pekerjaanmu?",
        "type": "select",
        "options": [
            ("Tidak pernah", "Never"),
            ("Jarang", "Rarely"),
            ("Kadang-kadang", "Sometimes"),
            ("Sering", "Often"),
        ],
    },
    "no_employees": {
        "label": "Berapa jumlah karyawan di perusahaan tempatmu bekerja?",
        "type": "select",
        "options": [
            ("1-5 orang", "1-5"),
            ("6-25 orang", "6-25"),
            ("26-100 orang", "26-100"),
            ("100-500 orang", "100-500"),
            ("500-1000 orang", "500-1000"),
            ("Lebih dari 1000 orang", "More than 1000"),
        ],
    },
    "remote_work": {
        "label": "Apakah kamu bekerja jarak jauh (remote) minimal 50% waktu kerja?",
        "type": "radio",
        "options": [("Tidak", "No"), ("Ya", "Yes")],
    },
    "tech_company": {
        "label": "Apakah perusahaanmu bergerak di bidang teknologi?",
        "type": "radio",
        "options": [("Tidak", "No"), ("Ya", "Yes")],
    },
    "benefits": {
        "label": "Apakah perusahaanmu menyediakan tunjangan kesehatan mental?",
        "type": "select",
        "options": [("Ya", "Yes"), ("Tidak", "No"), ("Tidak tahu", "Don't know")],
    },
    "care_options": {
        "label": "Apakah kamu tahu pilihan layanan kesehatan mental yang disediakan perusahaan?",
        "type": "select",
        "options": [("Ya", "Yes"), ("Tidak", "No"), ("Tidak yakin", "Not sure")],
    },
    "wellness_program": {
        "label": "Apakah kesehatan mental pernah dibahas dalam program wellness perusahaan?",
        "type": "select",
        "options": [("Ya", "Yes"), ("Tidak", "No"), ("Tidak tahu", "Don't know")],
    },
    "seek_help": {
        "label": "Apakah perusahaanmu menyediakan informasi/cara mencari bantuan kesehatan mental?",
        "type": "select",
        "options": [("Ya", "Yes"), ("Tidak", "No"), ("Tidak tahu", "Don't know")],
    },
    "anonymity": {
        "label": "Apakah identitasmu terlindungi jika memanfaatkan layanan kesehatan mental/pengobatan?",
        "type": "select",
        "options": [("Ya", "Yes"), ("Tidak", "No"), ("Tidak tahu", "Don't know")],
    },
    "leave": {
        "label": "Seberapa mudah mengambil cuti untuk alasan kesehatan mental?",
        "type": "select",
        "options": [
            ("Sangat mudah", "Very easy"),
            ("Agak mudah", "Somewhat easy"),
            ("Tidak tahu", "Don't know"),
            ("Agak sulit", "Somewhat difficult"),
            ("Sangat sulit", "Very difficult"),
        ],
    },
    "mental_health_consequence": {
        "label": "Apakah menurutmu membicarakan kesehatan mental ke atasan akan berdampak negatif?",
        "type": "select",
        "options": [("Ya", "Yes"), ("Tidak", "No"), ("Mungkin", "Maybe")],
    },
    "phys_health_consequence": {
        "label": "Apakah menurutmu membicarakan kesehatan fisik ke atasan akan berdampak negatif?",
        "type": "select",
        "options": [("Ya", "Yes"), ("Tidak", "No"), ("Mungkin", "Maybe")],
    },
    "coworkers": {
        "label": "Apakah kamu nyaman membicarakan kesehatan mental dengan rekan kerja?",
        "type": "select",
        "options": [("Ya", "Yes"), ("Tidak", "No"), ("Dengan sebagian dari mereka", "Some of them")],
    },
    "supervisor": {
        "label": "Apakah kamu nyaman membicarakan kesehatan mental dengan atasan langsung?",
        "type": "select",
        "options": [("Ya", "Yes"), ("Tidak", "No"), ("Dengan sebagian dari mereka", "Some of them")],
    },
    "mental_health_interview": {
        "label": "Apakah kamu akan membahas kesehatan mental dalam wawancara kerja?",
        "type": "select",
        "options": [("Ya", "Yes"), ("Tidak", "No"), ("Mungkin", "Maybe")],
    },
    "phys_health_interview": {
        "label": "Apakah kamu akan membahas kesehatan fisik dalam wawancara kerja?",
        "type": "select",
        "options": [("Ya", "Yes"), ("Tidak", "No"), ("Mungkin", "Maybe")],
    },
    "mental_vs_physical": {
        "label": "Apakah menurutmu perusahaan menganggap kesehatan mental sepenting kesehatan fisik?",
        "type": "select",
        "options": [("Ya", "Yes"), ("Tidak", "No"), ("Tidak tahu", "Don't know")],
    },
    "obs_consequence": {
        "label": "Pernahkah kamu melihat rekan kerja lain mendapat dampak negatif karena kondisi kesehatan mentalnya?",
        "type": "radio",
        "options": [("Tidak", "No"), ("Ya", "Yes")],
    },
}

ALL_FEATURE_KEYS = [f for step in STEPS for f in step["fields"]]
