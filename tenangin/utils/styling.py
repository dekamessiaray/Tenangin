
import streamlit as st

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@500;700&display=swap');

:root {
    color-scheme: light only;
    --canvas-a: #EEF4FC;
    --canvas-b: #F7FAFF;
    --ink: #1E293B;
    --ink-soft: #64748B;
    --ink-faint: #94A3B8;
    --primary: #2563EB;
    --primary-dark: #1D4ED8;
    --primary-soft: #EAF1FE;
    --accent: #38BDF8;
    --low: #16A34A;
    --medium: #D97706;
    --high: #DC2626;
    --border: rgba(148,163,184,0.28);
    --glass-bg: rgba(255,255,255,0.62);
    --glass-bg-strong: rgba(255,255,255,0.8);
    --glass-border: rgba(255,255,255,0.55);
    --radius: 24px;
    --radius-sm: 16px;
}

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
p, li, label, .stMarkdown, [data-testid="stMarkdownContainer"],
[data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] li,
.stText, .stCaption, .stAlert, .stRadio label, .stSelectbox label,
.stNumberInput label, .stTextInput label, button, input, select, textarea {
    font-family: 'Inter', sans-serif !important;
}
h1, h2, h3, h4, h5, h6,
[data-testid="stMarkdownContainer"] h1, [data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h3, [data-testid="stMarkdownContainer"] h4 {
    font-family: 'Space Grotesk', sans-serif !important;
}

/* Chevron expander dibuat murni CSS (bukan font ikon) supaya tidak pernah
   tampil sebagai teks mentah ("keyboard_arrow_down") bila font ikon gagal
   dimuat karena koneksi jaringan pengguna. Selector dibuat lebar (beberapa
   kemungkinan testid/struktur) supaya tetap kena di berbagai versi Streamlit. */
[data-testid="stExpander"] summary [data-testid="stIconMaterial"],
[data-testid="stExpander"] summary [data-testid*="Icon"],
[data-testid="stExpander"] summary span[class*="material"] {
    font-size: 0 !important;
    color: transparent !important;
    width: 16px !important; height: 16px !important;
    min-width: 16px !important;
    display: inline-flex !important; align-items: center; justify-content: center;
    overflow: hidden;
    flex-shrink: 0;
}
[data-testid="stExpander"] summary [data-testid="stIconMaterial"]::after,
[data-testid="stExpander"] summary [data-testid*="Icon"]::after,
[data-testid="stExpander"] summary span[class*="material"]::after {
    content: "";
    width: 7px; height: 7px;
    border-right: 2px solid var(--ink-soft);
    border-bottom: 2px solid var(--ink-soft);
    transform: rotate(45deg);
    transition: transform 0.2s ease;
}
[data-testid="stExpander"] details[open] summary [data-testid="stIconMaterial"]::after,
[data-testid="stExpander"] details[open] summary [data-testid*="Icon"]::after,
[data-testid="stExpander"] details[open] summary span[class*="material"]::after {
    transform: rotate(-135deg);
}

html, body {
    color-scheme: light only;
}

.stApp {
    color-scheme: light only;
    background:
        radial-gradient(circle at 12% 8%, rgba(56,189,248,0.16) 0%, transparent 42%),
        radial-gradient(circle at 88% 18%, rgba(37,99,235,0.12) 0%, transparent 45%),
        radial-gradient(circle at 50% 100%, rgba(37,99,235,0.08) 0%, transparent 50%),
        linear-gradient(180deg, var(--canvas-b) 0%, var(--canvas-a) 100%);
    color: var(--ink);
}

h1, h2, h3, h4, .display-font {
    font-family: 'Space Grotesk', sans-serif !important;
    color: var(--ink);
    letter-spacing: -0.01em;
    font-weight: 600;
}

.mono-num {
    font-family: 'JetBrains Mono', monospace;
    font-weight: 700;
}

#MainMenu, footer, header {visibility: hidden;}
.block-container { padding-top: 2.4rem; padding-bottom: 4rem; max-width: 900px; }

/* ---------- Nav bar ---------- */
.tenangin-nav {
    display: flex;
    justify-content: center;
    gap: 0.5rem;
    flex-wrap: wrap;
    margin-bottom: 2rem;
}
.tenangin-brand {
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 700;
    font-size: 1.75rem;
    color: var(--primary-dark);
    text-align: center;
    margin-bottom: 0.5rem;
}
.tenangin-brand span.dot { color: var(--accent); }
.nav-brand-row {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.7rem;
    margin-bottom: 0.8rem;
}
.nav-brand-row img { height: 84px; width: 84px; object-fit: contain; }

div[data-testid="stHorizontalBlock"] .stButton button {
    border-radius: var(--radius-sm);
    border: 1px solid var(--glass-border);
    background: var(--glass-bg);
    backdrop-filter: blur(16px) saturate(160%);
    -webkit-backdrop-filter: blur(16px) saturate(160%);
    color: var(--ink-soft);
    font-weight: 500;
    padding: 0.55rem 1rem;
    box-shadow: 0 4px 18px rgba(30,58,95,0.05);
    transition: all 0.15s ease;
}
@media (hover: hover) and (pointer: fine) {
    div[data-testid="stHorizontalBlock"] .stButton button:hover {
        border-color: var(--primary);
        color: var(--primary-dark);
        transform: translateY(-1px);
    }
}
@media not all and (hover: hover) {
    div[data-testid="stHorizontalBlock"] .stButton button:hover {
        border-color: var(--primary);
        color: var(--primary-dark);
    }
}

/* Progress bar dibuat pill/rounded penuh + gradien, bukan kotak polos
   bawaan Streamlit yang terasa "menabrak" estetika kaca membulat. */
[data-testid="stProgress"] [data-testid="stMarkdownContainer"] {
    display: none;
}
[data-testid="stProgressBarTrack"] {
    background: rgba(148,163,184,0.18) !important;
    border-radius: 999px !important;
    height: 10px !important;
    overflow: hidden !important;
}
[data-testid="stProgressBarTrack"] > div {
    background: linear-gradient(90deg, var(--primary), var(--accent)) !important;
    border-radius: 999px !important;
    height: 100% !important;
}
[data-testid="stProgress"] { margin-bottom: 0 !important; }

/* Primary CTA buttons */
.stButton button[kind="primary"] {
    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: var(--radius-sm) !important;
    padding: 0.75rem 1.7rem !important;
    font-weight: 600 !important;
    box-shadow: 0 10px 26px rgba(37,99,235,0.28);
}
@media (hover: hover) and (pointer: fine) {
    .stButton button[kind="primary"]:hover { transform: translateY(-1px); box-shadow: 0 14px 30px rgba(37,99,235,0.34); }
}

.stDownloadButton button {
    border-radius: var(--radius-sm) !important;
    border: 1px solid var(--glass-border) !important;
    background: var(--glass-bg) !important;
    backdrop-filter: blur(16px);
    box-shadow: 0 4px 18px rgba(30,58,95,0.05);
}

/* ---------- Glass cards ---------- */
.card {
    background: var(--glass-bg);
    backdrop-filter: blur(26px) saturate(190%);
    -webkit-backdrop-filter: blur(26px) saturate(190%);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius);
    padding: 2rem 2.2rem;
    margin-bottom: 1.6rem;
    box-shadow: 0 8px 32px rgba(30,58,95,0.08);
}
.card-soft {
    background: var(--primary-soft);
    border-radius: var(--radius);
    padding: 1.6rem 1.9rem;
    margin-bottom: 1.2rem;
}

/* ---------- st.container(border=True, key="card_*") sebagai kartu kaca ----------
   Dipakai untuk kartu yang berisi widget native Streamlit (form, chart, metric),
   karena tag <div> yang dibuka/ditutup lewat panggilan st.markdown() TERPISAH
   tidak benar-benar saling membungkus (setiap panggilan di-parse browser secara
   independen), sehingga hanya cara ini yang menghasilkan kartu bersarang valid. */
div[data-testid="stVerticalBlock"][class*="st-key-card_"] {
    background: var(--glass-bg) !important;
    backdrop-filter: blur(26px) saturate(190%);
    -webkit-backdrop-filter: blur(26px) saturate(190%);
    border: 1px solid var(--glass-border) !important;
    border-radius: var(--radius) !important;
    padding: 2rem 2.2rem !important;
    margin-bottom: 1.6rem;
    box-shadow: 0 8px 32px rgba(30,58,95,0.08);
}

/* ---------- Hero ---------- */
.hero-wrap {
    position: relative;
    text-align: center;
    padding: 4rem 1.5rem 3rem 1.5rem;
    margin-bottom: 1.4rem;
    overflow: hidden;
    border-radius: 32px;
    background: var(--glass-bg);
    backdrop-filter: blur(24px) saturate(180%);
    -webkit-backdrop-filter: blur(24px) saturate(180%);
    border: 1px solid var(--glass-border);
    box-shadow: 0 12px 40px rgba(30,58,95,0.10);
}
.breathing-rings {
    position: absolute;
    top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    width: 520px; height: 520px;
    pointer-events: none;
    z-index: 0;
}
.breathing-rings .ring {
    position: absolute;
    border-radius: 50%;
    border: 1.5px solid rgba(37,99,235,0.14);
    top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    animation: breathe 6s ease-in-out infinite;
}
.ring.r1 { width: 170px; height: 170px; animation-delay: 0s; }
.ring.r2 { width: 280px; height: 280px; animation-delay: 0.6s; }
.ring.r3 { width: 390px; height: 390px; animation-delay: 1.2s; }
.ring.r4 { width: 500px; height: 500px; animation-delay: 1.8s; }
@keyframes breathe {
    0%, 100% { transform: translate(-50%, -50%) scale(0.92); opacity: 0.3; }
    50% { transform: translate(-50%, -50%) scale(1.05); opacity: 0.85; }
}
.hero-content { position: relative; z-index: 1; }
.hero-eyebrow {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    font-size: 0.78rem;
    letter-spacing: 0.07em;
    text-transform: uppercase;
    color: var(--primary-dark);
    background: var(--primary-soft);
    padding: 0.4rem 1rem;
    border-radius: 999px;
    margin-bottom: 1.3rem;
    font-weight: 600;
}
.hero-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2.7rem;
    font-weight: 700;
    color: var(--ink);
    line-height: 1.15;
    margin-bottom: 1.1rem;
}
.hero-title .accent { color: var(--primary); }
.hero-sub {
    font-size: 1.06rem;
    color: var(--ink-soft);
    max-width: 580px;
    margin: 0 auto 2rem auto;
    line-height: 1.65;
}

/* ---------- Badges & category pills ---------- */
.risk-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.6rem 1.5rem;
    border-radius: 999px;
    font-weight: 700;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.3rem;
}
.step-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: var(--primary-soft);
    color: var(--primary-dark);
    padding: 0.4rem 1rem;
    border-radius: 999px;
    font-size: 0.82rem;
    font-weight: 600;
    margin-bottom: 0.3rem;
}

/* ---------- Disclaimer card ---------- */
.disclaimer-card {
    display: flex;
    gap: 1.1rem;
    align-items: flex-start;
    background: var(--glass-bg);
    backdrop-filter: blur(26px) saturate(190%);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius);
    padding: 1.7rem 1.9rem;
    margin-top: 1.6rem;
    box-shadow: 0 8px 28px rgba(30,58,95,0.07);
}
.disclaimer-card .icon-box {
    background: var(--primary-soft); color: var(--primary);
    width: 46px; height: 46px; margin-bottom: 0;
    flex-shrink: 0;
}
.disclaimer-card .eyebrow {
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-size: 0.72rem;
    font-weight: 700;
    color: var(--primary);
    margin-bottom: 0.3rem;
}
.disclaimer-card h4 {
    font-family: 'Space Grotesk', sans-serif;
    margin: 0 0 0.5rem 0;
    font-size: 1.12rem;
    color: var(--ink);
}
.disclaimer-card p {
    margin: 0; font-size: 0.9rem; color: var(--ink-soft); line-height: 1.65;
}
.disclaimer-card b { color: var(--ink); }

/* ---------- Feature / icon cards ---------- */
.feature-card {
    background: var(--glass-bg);
    backdrop-filter: blur(26px) saturate(190%);
    -webkit-backdrop-filter: blur(26px) saturate(190%);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius);
    padding: 1.7rem 1.6rem;
    height: 100%;
    box-shadow: 0 8px 26px rgba(30,58,95,0.06);
}
.feature-card h4 { margin: 0.2rem 0 0.5rem 0; font-size: 1.04rem; }
.feature-card p { margin: 0; font-size: 0.88rem; color: var(--ink-soft); line-height: 1.55; }

.icon-box {
    width: 48px; height: 48px; border-radius: var(--radius-sm);
    display: flex; align-items: center; justify-content: center;
    background: var(--primary-soft); color: var(--primary);
    margin-bottom: 0.9rem;
}

/* ---------- Tip cards ---------- */
.tip-card {
    border-radius: var(--radius);
    padding: 1.7rem 1.6rem;
    color: white;
    height: 100%;
    box-shadow: 0 10px 30px rgba(30,58,95,0.14);
}
.tip-card .icon-circle {
    width: 40px; height: 40px; border-radius: 12px;
    background: rgba(255,255,255,0.18);
    display: flex; align-items: center; justify-content: center;
    margin-bottom: 1rem; color: white;
}
.tip-card h4 { font-family: 'Space Grotesk', sans-serif; margin: 0 0 0.5rem 0; font-size: 1.05rem; }
.tip-card p { margin: 0; font-size: 0.86rem; opacity: 0.92; line-height: 1.55; }
.tip-dark  { background: linear-gradient(155deg, #1E293B 0%, #0F172A 100%); }
.tip-blue1 { background: linear-gradient(155deg, #2563EB 0%, #1D4ED8 100%); }
.tip-blue2 { background: linear-gradient(155deg, #0EA5E9 0%, #0369A1 100%); }
.tip-blue3 { background: linear-gradient(155deg, #6366F1 0%, #4338CA 100%); }

/* ---------- Efek glass sheen ala iOS ----------
   Garis highlight tipis di tepi atas, memberi kesan cahaya memantul di
   permukaan kaca (khas frosted glass iOS/macOS). */
.card, .feature-card, .hero-wrap, .disclaimer-card, .tip-card,
div[data-testid="stVerticalBlock"][class*="st-key-card_"],
div[data-testid="stVerticalBlock"][class*="st-key-navdock"] {
    position: relative;
}
.card::before, .feature-card::before, .hero-wrap::before, .disclaimer-card::before,
div[data-testid="stVerticalBlock"][class*="st-key-card_"]::before,
div[data-testid="stVerticalBlock"][class*="st-key-navdock"]::before {
    content: "";
    position: absolute;
    top: 0; left: 6%; right: 6%;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.95), transparent);
    border-radius: 999px;
}

/* ---------- Nav dock mengambang ---------- */
div[data-testid="stVerticalBlock"][class*="st-key-navdock"] {
    background: var(--glass-bg-strong) !important;
    backdrop-filter: blur(28px) saturate(190%);
    -webkit-backdrop-filter: blur(28px) saturate(190%);
    border: 1px solid var(--glass-border) !important;
    border-radius: 28px !important;
    padding: 1.2rem 1.4rem 1rem 1.4rem !important;
    box-shadow: 0 14px 38px rgba(30,58,95,0.10);
    margin-bottom: 2rem;
}
div[data-testid="stVerticalBlock"][class*="st-key-navdock"] div[data-testid="stHorizontalBlock"] .stButton button {
    box-shadow: none;
}

hr.soft { border: none; border-top: 1px solid var(--border); margin: 2rem 0; }

/* ---------- Perluasan glassmorphism: expander & alert ---------- */
[data-testid="stExpander"] {
    background: var(--glass-bg) !important;
    backdrop-filter: blur(22px) saturate(180%);
    -webkit-backdrop-filter: blur(22px) saturate(180%);
    border: 1px solid var(--glass-border) !important;
    border-radius: var(--radius-sm) !important;
    box-shadow: 0 6px 22px rgba(30,58,95,0.06);
    margin-bottom: 0.9rem;
    overflow: hidden;
}
[data-testid="stExpander"] details,
[data-testid="stExpander"] summary,
[data-testid="stExpander"] [data-testid="stExpanderDetails"] {
    background: transparent !important;
    color: var(--ink) !important;
}
[data-testid="stExpander"] summary:hover,
[data-testid="stExpander"] summary:focus,
[data-testid="stExpander"] summary:active {
    background: rgba(37,99,235,0.05) !important;
    color: var(--ink) !important;
}
[data-testid="stExpander"] summary p {
    color: var(--ink) !important;
}
[data-testid="stAlert"] {
    background: var(--glass-bg-strong) !important;
    backdrop-filter: blur(18px) saturate(170%);
    -webkit-backdrop-filter: blur(18px) saturate(170%);
    border: 1px solid var(--glass-border) !important;
    border-radius: var(--radius-sm) !important;
    box-shadow: 0 6px 20px rgba(30,58,95,0.06);
}

/* ---------- Streamlit native widget spacing (whitespace longgar) ---------- */
.stSlider, .stSelectbox, .stRadio, .stNumberInput, .stTextInput { margin-bottom: 0.4rem; }

[data-testid="stNumberInput"] input,
[data-testid="stNumberInputField"],
[data-testid="stTextInput"] input,
[data-testid="stSelectbox"] input,
[data-testid="stSelectbox"] [role="group"] {
    background-color: #FFFFFF !important;
    color: var(--ink) !important;
    border-color: var(--border) !important;
}
[data-testid="stNumberInputContainer"] {
    background-color: #FFFFFF !important;
    border-color: var(--border) !important;
}
[data-testid="stNumberInputStepDown"],
[data-testid="stNumberInputStepUp"] {
    background-color: var(--primary-soft) !important;
    color: var(--primary-dark) !important;
}
[data-testid="stNumberInputStepDown"] svg,
[data-testid="stNumberInputStepUp"] svg {
    fill: var(--primary-dark) !important;
    color: var(--primary-dark) !important;
}
[data-testid="stSelectboxVirtualDropdown"],
[data-testid="stSelectboxVirtualDropdown"] [role="listbox"],
[data-testid="stSelectboxVirtualDropdown"] [role="option"] {
    background-color: #FFFFFF !important;
    color: var(--ink) !important;
}
[data-testid="stSelectboxVirtualDropdown"] [role="option"]:hover,
[data-testid="stSelectboxVirtualDropdown"] [role="option"][data-focused="true"] {
    background-color: var(--primary-soft) !important;
}
[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] label,
[data-testid="stRadioOption"] p,
[data-testid="stRadioOption"] div {
    color: var(--ink) !important;
    opacity: 1 !important;
}
/* Pastikan input radio native (disembunyikan lewat teknik clip-rect oleh
   Streamlit) benar-benar tidak pernah terlihat di perangkat/browser manapun
   -- lapisan pertahanan tambahan selain clip bawaan, supaya tidak muncul
   sebagai "lingkaran kedua" di atas lingkaran custom kita. */
[data-testid="stRadioOption"] input[type="radio"] {
    position: absolute !important;
    opacity: 0 !important;
    width: 1px !important;
    height: 1px !important;
    padding: 0 !important;
    margin: -1px !important;
    overflow: hidden !important;
    clip: rect(0, 0, 0, 0) !important;
    clip-path: inset(50%) !important;
    white-space: nowrap !important;
    border: 0 !important;
    pointer-events: none !important;
}
[data-testid="stRadioOption"] > span:first-child {
    position: absolute !important;
    width: 1px !important;
    height: 1px !important;
    overflow: hidden !important;
    clip: rect(0, 0, 0, 0) !important;
    clip-path: inset(50%) !important;
}
/* Wrapper luar opsi radio: hapus total border/background bawaan supaya
   tidak tampil sebagai kotak/chip (bug yang muncul di beberapa deployment). */
[data-testid="stRadioOption"] > div,
[data-testid="stRadioOption"] > div > div:first-child {
    border: none !important;
    background: transparent !important;
    box-shadow: none !important;
    outline: none !important;
}
/* Lingkaran radio sesungguhnya ada SATU level lebih dalam dari wrapper
   di atas (ukuran tetap 18px, bukan selebar baris) */
[data-testid="stRadioOption"] > div > div:first-child > div {
    width: 18px !important;
    height: 18px !important;
    min-width: 18px !important;
    border-radius: 50% !important;
    border: 2px solid var(--ink-faint) !important;
    background: transparent !important;
    box-sizing: border-box !important;
}
[data-testid="stRadioOption"][data-selected="true"] > div > div:first-child > div {
    border-color: var(--primary) !important;
}
[data-testid="stRadioOption"] > div > div:first-child > div > div {
    width: 8px !important;
    height: 8px !important;
    border-radius: 50% !important;
    background: transparent !important;
}
[data-testid="stRadioOption"][data-selected="true"] > div > div:first-child > div > div {
    background: var(--primary) !important;
}

/* ---------- Fix kritis: radio button pecah huruf-per-huruf di layar sempit ----------
   Akar masalah: parent flex container memaksa <p> label menyusut di bawah lebar
   kontennya sendiri (flex-shrink default = 1 tanpa batas), sehingga browser
   membungkus teks per-karakter ("T i d a k" turun ke bawah). Perbaikan: kunci
   white-space + flex-shrink di SETIAP level (group, option, wrapper, teks)
   supaya setiap opsi selalu utuh satu baris; kalau ruang kurang, seluruh OPSI
   (bukan hurufnya) yang pindah baris via flex-wrap pada radiogroup. */
[data-testid="stRadioGroup"] {
    display: flex !important;
    flex-wrap: wrap !important;
    row-gap: 0.6rem !important;
    column-gap: 1.3rem !important;
    align-items: center !important;
}
[data-testid="stRadioOption"] {
    display: inline-flex !important;
    align-items: center !important;
    white-space: nowrap !important;
    flex: 0 0 auto !important;
    flex-shrink: 0 !important;
    width: auto !important;
    min-width: max-content !important;
    margin: 0 !important;
    padding: 0.75rem 0.6rem !important;
    border-radius: var(--radius-sm) !important;
    cursor: pointer;
}
@media (hover: hover) and (pointer: fine) {
    [data-testid="stRadioOption"]:hover {
        background: var(--primary-soft) !important;
    }
}
[data-testid="stRadioOption"] > div {
    display: inline-flex !important;
    align-items: center !important;
    gap: 0.5rem !important;
    flex-shrink: 0 !important;
    white-space: nowrap !important;
    width: auto !important;
}
[data-testid="stRadioOption"] > div > div:first-child {
    flex-shrink: 0 !important;
}
[data-testid="stRadioOption"] [data-testid="stMarkdownContainer"],
[data-testid="stRadioOption"] [data-testid="stMarkdownContainer"] p {
    white-space: nowrap !important;
    flex-shrink: 0 !important;
    width: auto !important;
    min-width: max-content !important;
    font-size: 0.95rem !important;
}

div[data-testid="stVerticalBlock"] > div { gap: 0.5rem; }



@media (max-width: 640px) {
    .feature-card, .tip-card {
        margin-bottom: 1rem;
    }

    .cara-kerja-arrow {
        min-height: 36px !important;
        transform: rotate(90deg);
    }

    div[class*="st-key-navdock"] div[data-testid="stHorizontalBlock"] {
        flex-wrap: nowrap !important;
        overflow-x: auto !important;
        gap: 0.35rem !important;
        -webkit-overflow-scrolling: touch;
        scrollbar-width: none;
    }
    div[class*="st-key-navdock"] div[data-testid="stHorizontalBlock"]::-webkit-scrollbar {
        display: none;
    }
    div[class*="st-key-navdock"] div[data-testid="stHorizontalBlock"] > div {
        min-width: auto !important;
        width: auto !important;
        flex: 0 0 auto !important;
    }
    div[class*="st-key-navdock"] .stButton button {
        padding: 0.5rem 0.85rem !important;
        font-size: 0.78rem !important;
        white-space: nowrap;
    }
    div[class*="st-key-navdock"] {
        padding: 0.8rem 0.9rem 0.8rem 0.9rem !important;
    }
    .nav-brand-row img { height: 56px !important; width: 56px !important; }
}
</style>
"""


def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)


def hero_rings_html() -> str:
    return ('<div class="breathing-rings">'
            '<div class="ring r1"></div>'
            '<div class="ring r2"></div>'
            '<div class="ring r3"></div>'
            '<div class="ring r4"></div>'
            '</div>')
