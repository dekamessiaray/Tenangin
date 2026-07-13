import time
import sys
import os
import math

import streamlit as st

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from utils.styling import inject_css, hero_rings_html
from utils.questions import STEPS, FIELDS
from utils.recommendations import get_recommendation, DISCLAIMER
from utils.pdf_report import generate_pdf_report
from utils.assets import logo_data_uri
from utils.icons import icon
from model.predict import predict_risk

st.set_page_config(
    page_title="Tenang.in - Skrining Kesehatan Mental",
    page_icon="assets/logo_nav.png",
    layout="centered",
    initial_sidebar_state="collapsed",
)
inject_css()


def md(html: str):
    flattened = "\n".join(line.lstrip() for line in html.strip("\n").split("\n"))
    st.markdown(flattened, unsafe_allow_html=True)


defaults = {
    "page": "home",
    "step": 0,
    "answers": {},
    "result": None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


def goto(page, **kwargs):
    st.session_state.page = page
    st.session_state["_scroll_top"] = True
    for k, v in kwargs.items():
        st.session_state[k] = v
    st.rerun()


def reset_assessment():
    st.session_state.answers = {}
    st.session_state.step = 0
    st.session_state.result = None


def section_heading(icon_name: str, text: str):
    md(f"""
    <div style="display:flex; align-items:center; gap:0.7rem; margin-bottom:0.3rem;">
        <div class="icon-box" style="margin-bottom:0;">{icon(icon_name, size=22)}</div>
        <h3 style="margin:0;">{text}</h3>
    </div>
    """)


def disclaimer_card():
    md(f"""
    <div class="disclaimer-card">
        <div class="icon-box">{icon('info', size=22)}</div>
        <div>
            <div class="eyebrow">Catatan Penting</div>
            <h4>Bukan Alat Diagnosis</h4>
            <p>{DISCLAIMER}</p>
        </div>
    </div>
    """)


NAV_ITEMS = [
    ("home", "Beranda"),
    ("assessment", "Skrining"),
    ("therapeutic", "Ruang Tenang"),
    ("education", "Edukasi"),
]


def render_nav():
    md(f"""
    <div class="nav-brand-row">
        <img src="{logo_data_uri()}" alt="Tenang.in" />
        <span class="tenangin-brand">Tenang<span class="dot">.</span>in</span>
    </div>
    """)
    with st.container(border=True, key="navdock"):
        cols = st.columns(len(NAV_ITEMS))
        for col, (key, label) in zip(cols, NAV_ITEMS):
            with col:
                active_page = st.session_state.page
                is_current = (active_page == key) or (
                    key == "assessment" and active_page in ("assessment", "analyzing", "result")
                )
                if st.button(
                    label, key=f"nav_{key}", use_container_width=True,
                    type="primary" if is_current else "secondary",
                ):
                    if key == "assessment" and active_page not in ("assessment", "analyzing", "result"):
                        reset_assessment()
                    goto(key)


def render_home():
    md(f"""
    <div class="hero-wrap">
        {hero_rings_html()}
        <div class="hero-content">
            <span class="hero-eyebrow">Skrining Dini, Berbasis Machine Learning</span>
            <div class="hero-title">Kenali risikonya lebih awal.<br>
                Rawat dirimu dengan <span class="accent">tenang</span>.</div>
            <div class="hero-sub">
                Tenang.in adalah alat skrining awal risiko kesehatan mental yang
                memakai model AI stacked ensemble untuk memberi gambaran risiko
                secara cepat, privat, dan berbasis data. Alat ini bukan pengganti
                diagnosis profesional.
            </div>
        </div>
    </div>
    """)
    c1, c2, c3 = st.columns([1, 1.3, 1])
    with c2:
        if st.button("Mulai Skrining", type="primary", use_container_width=True):
            reset_assessment()
            goto("assessment")

    st.markdown("<br>", unsafe_allow_html=True)


    md("""
    <h3 style="text-align:center; margin-bottom:0.3rem;">Mengapa Memilih Tenang.in</h3>
    <p style="text-align:center; color:#64748B; max-width:520px; margin:0 auto 1.8rem auto;">
        Pendekatan kami menggabungkan kecanggihan model machine learning dengan
        empati untuk kesehatan mentalmu.
    </p>
    """)
    why_items = [
        ("brain", "AI-Based Screening", "Analisis berbasis model stacked ensemble (XGBoost, CatBoost, LightGBM) yang telah dilatih pada data survei kesehatan mental."),
        ("zap", "Cepat dan Mudah", "Hanya butuh waktu kurang dari 5 menit untuk mendapatkan gambaran awal kondisimu."),
        ("shield_check", "Privasi Terjaga", "Jawabanmu diproses secara lokal di sesi ini dan tidak disebarkan ke pihak lain."),
        ("heart", "Edukatif dan Suportif", "Dilengkapi rekomendasi dan edukasi untuk membantu langkah selanjutnya."),
    ]
    cols = st.columns(4)
    for col, (icon_name, title, desc) in zip(cols, why_items):
        with col:
            md(f"""
            <div class="feature-card">
                <div class="icon-box">{icon(icon_name, size=22)}</div>
                <h4>{title}</h4>
                <p>{desc}</p>
            </div>
            """)

    st.markdown("<br><br>", unsafe_allow_html=True)


    md("""
    <h3 style="text-align:center; margin-bottom:0.3rem;">Cara Kerja AI di Balik Tenang.in</h3>
    <p style="text-align:center; color:#64748B; max-width:480px; margin:0 auto 1.8rem auto;">
        Langkah mudah untuk mulai memahami kondisi kesehatan mentalmu.
    </p>
    """)
    steps_info = [
        ("clipboard_list", "Isi Screening", "Jawab pertanyaan singkat mengenai kondisi psikososial dan lingkungan kerjamu."),
        ("settings", "AI Menganalisis", "Sistem menormalisasi jawabanmu lalu memprosesnya lewat model stacking."),
        ("bar_chart_3", "Lihat Risk Score", "Dapatkan hasil probabilistic risk score dalam bentuk visual yang mudah dipahami."),
        ("lightbulb", "Dapatkan Rekomendasi", "Langkah-langkah yang disarankan untuk menjaga kesehatan mentalmu."),
    ]
    n = len(steps_info)
    col_spec = []
    for i in range(n):
        col_spec.append(1)
        if i < n - 1:
            col_spec.append(0.18)
    cols = st.columns(col_spec)
    col_idx = 0
    for i, (icon_name, title, desc) in enumerate(steps_info):
        with cols[col_idx]:
            md(f"""
            <div class="feature-card">
                <div class="icon-box">{icon(icon_name, size=22)}</div>
                <h4>{title}</h4>
                <p>{desc}</p>
            </div>
            """)
        col_idx += 1
        if i < n - 1:
            with cols[col_idx]:
                md(f"""
                <div class="cara-kerja-arrow" style="display:flex; align-items:center; justify-content:center; height:100%; min-height:150px; color:#93B4EE;">
                    {icon('arrow_right', size=22, color="#93B4EE")}
                </div>
                """)
            col_idx += 1

    st.markdown("<br><br>", unsafe_allow_html=True)


    md("""
    <h3 style="text-align:center; margin-bottom:0.3rem;">Menjaga Kesehatan Mental Dimulai dari Kesadaran</h3>
    <p style="text-align:center; color:#64748B; max-width:480px; margin:0 auto 1.8rem auto;">
        Tips sederhana yang bisa kamu lakukan setiap hari.
    </p>
    """)
    tips = [
        ("tip-dark", "moon", "Sleep Well", "Tidur cukup 7-9 jam untuk memulihkan fungsi otak harian."),
        ("tip-blue1", "trending_up", "Manage Stress", "Lakukan teknik pernapasan atau hobi yang menenangkan."),
        ("tip-blue2", "users", "Stay Connected", "Berbagi cerita dengan orang yang kamu percayai secara teratur."),
        ("tip-blue3", "life_buoy", "Seek Help", "Jangan ragu berkonsultasi dengan psikolog atau profesional."),
    ]
    cols = st.columns(4)
    for col, (cls, icon_name, title, desc) in zip(cols, tips):
        with col:
            md(f"""
            <div class="tip-card {cls}">
                <div class="icon-circle">{icon(icon_name, size=20, color="white")}</div>
                <h4>{title}</h4>
                <p>{desc}</p>
            </div>
            """)

    st.markdown("<br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.3, 1])
    with c2:
        if st.button("Coba Skrining Sekarang", key="cta_bottom", type="primary", use_container_width=True):
            reset_assessment()
            goto("assessment")

    disclaimer_card()


def render_field(key):
    spec = FIELDS[key]
    current = st.session_state.answers.get(key, spec.get("default"))
    label = spec["label"]

    if spec["type"] == "number":
        val = st.number_input(
            label, min_value=spec["min"], max_value=spec["max"],
            value=int(current) if current is not None else spec["default"],
            step=1, key=f"w_{key}", help=spec.get("help"),
        )
    elif spec["type"] in ("select", "radio"):
        options = spec["options"]
        display_labels = [d for d, _ in options]
        raw_values = [r for _, r in options]
        idx = raw_values.index(current) if current in raw_values else 0
        widget = st.selectbox if spec["type"] == "select" else st.radio
        kwargs = {"horizontal": True} if spec["type"] == "radio" else {}
        chosen_label = widget(
            label, display_labels, index=idx, key=f"w_{key}",
            help=spec.get("help"), **kwargs,
        )
        val = raw_values[display_labels.index(chosen_label)]
    else:
        val = st.text_input(label, value=current or "", key=f"w_{key}")

    st.session_state.answers[key] = val


def render_assessment():
    step_idx = st.session_state.step
    total_steps = len(STEPS)
    step = STEPS[step_idx]

    md(f'<span class="step-pill">Langkah {step_idx + 1} dari {total_steps}</span>')
    st.progress((step_idx + 1) / total_steps)

    with st.container(border=True, key="card_wizard"):
        section_heading(step["icon"], step["title"])
        st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)
        for field_key in step["fields"]:
            render_field(field_key)

    col_back, col_spacer, col_next = st.columns([1, 2, 1])
    with col_back:
        if step_idx > 0:
            if st.button("Kembali", use_container_width=True):
                st.session_state.step -= 1
                st.rerun()
        else:
            if st.button("Beranda", use_container_width=True):
                goto("home")
    with col_next:
        is_last = step_idx == total_steps - 1
        label = "Lihat Hasil" if is_last else "Lanjut"
        if st.button(label, type="primary", use_container_width=True):
            if is_last:
                goto("analyzing")
            else:
                st.session_state.step += 1
                st.rerun()


def render_analyzing():
    md(f"""
    <div class="card" style="text-align:center; padding:3.2rem 1.5rem;">
        <div style="display:flex; justify-content:center; margin-bottom:1rem;">
            <div class="icon-box" style="width:60px; height:60px; margin-bottom:0;">
                {icon('cpu', size=28)}
            </div>
        </div>
        <h3 style="margin:0;">AI sedang menganalisis jawabanmu</h3>
    </div>
    """)
    placeholder = st.empty()
    progress = st.progress(0)

    stages = [
        ("Memproses dan menormalisasi jawabanmu...", 25),
        ("Menjalankan model XGBoost, CatBoost, dan LightGBM...", 60),
        ("Menggabungkan hasil lewat meta-learner...", 85),
        ("Menghitung probabilistic risk score...", 100),
    ]
    for text, pct in stages:
        placeholder.markdown(f"<p style='text-align:center; color:#64748B;'>{text}</p>", unsafe_allow_html=True)
        progress.progress(pct)
        time.sleep(0.7)

    result = predict_risk(st.session_state.answers)
    st.session_state.result = result
    time.sleep(0.3)
    goto("result")


def render_gauge(probability, category, color):
    r = 74
    stroke_w = 16
    circumference = 2 * math.pi * r
    pct = max(0.0, min(1.0, probability))
    offset = circumference * (1 - pct)

    svg = f"""
    <div style="display:flex; justify-content:center; padding:0.4rem 0;">
        <svg viewBox="0 0 200 200" width="200" height="200">
            <circle cx="100" cy="100" r="{r}" fill="none" stroke="#E7EEFB" stroke-width="{stroke_w}"/>
            <circle cx="100" cy="100" r="{r}" fill="none" stroke="{color}" stroke-width="{stroke_w}"
                stroke-linecap="round"
                stroke-dasharray="{circumference:.2f}" stroke-dashoffset="{offset:.2f}"
                transform="rotate(-90 100 100)" />
            <text x="100" y="96" text-anchor="middle" font-family="JetBrains Mono, monospace"
                font-weight="700" font-size="34" fill="{color}">{probability*100:.1f}%</text>
            <text x="100" y="122" text-anchor="middle" font-family="Inter, sans-serif"
                font-size="12.5" fill="#64748B">Risk Score</text>
        </svg>
    </div>
    """
    md(svg)


def render_result():
    result = st.session_state.result
    if result is None:
        goto("assessment")
        return

    category = result["category"]
    probability = result["probability"]
    confidence = result.get("confidence")
    rec = get_recommendation(category)

    section_heading("bar_chart_3", "Hasil Skrining Kamu")
    with st.container(border=True, key="card_result_score"):
        left, right = st.columns([1, 1])
        with left:
            render_gauge(probability, category, rec["color"])
        with right:
            md(f"""
            <div style="padding-top:1.6rem;">
                <p style="color:#64748B; margin-bottom:0.4rem;">Kategori Risiko</p>
                <span class="risk-badge" style="background:{rec['bg']}; color:{rec['color']};">
                    {icon(rec['icon'], size=22, color=rec['color'])} {rec['title']}
                </span>
                <p style="color:#64748B; margin-top:1.5rem; margin-bottom:0.3rem;">Probabilistic Risk Score</p>
                <p class="mono-num" style="font-size:1.6rem; color:{rec['color']};">{probability*100:.1f}%</p>
            </div>
            """)
            if confidence is not None:
                st.markdown("<p style='color:#64748B; margin-bottom:0.3rem;'>Confidence Model</p>", unsafe_allow_html=True)
                st.progress(confidence)
                st.markdown(f"<p class='mono-num' style='font-size:0.95rem;'>{confidence*100:.1f}%</p>", unsafe_allow_html=True)


    with st.container(border=True, key="card_result_reco"):
        md(f'<div style="height:4px; background:{rec["color"]}; border-radius:4px; margin:-1px -1px 1.2rem -1px;"></div>')
        section_heading("lightbulb", "Rekomendasi untuk Kamu")
        st.markdown(f"**{rec['summary']}**")
        for point in rec["points"]:
            st.markdown(f"- {point}")

    if category in ("Medium", "High"):
        st.info("Coba **Ruang Tenang** untuk latihan pernapasan singkat yang bisa membantu meredakan stres saat ini.")


    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("Ulangi Skrining", use_container_width=True):
            reset_assessment()
            goto("assessment")
    with c2:
        pdf_bytes = generate_pdf_report(result)
        st.download_button(
            "Unduh Laporan PDF", data=pdf_bytes,
            file_name="tenangin_hasil_skrining.pdf", mime="application/pdf",
            use_container_width=True,
        )
    with c3:
        if st.button("Ruang Tenang", use_container_width=True):
            goto("therapeutic")

    disclaimer_card()


def render_therapeutic():
    section_heading("wind", "Ruang Tenang")
    st.markdown(
        "Tekan **Mulai** untuk latihan pernapasan kotak (*box breathing*). "
        "Duduk senyaman mungkin, dan biarkan napasmu mengikuti irama lingkaran."
    )

    breathing_html = """
    <div style="display:flex; flex-direction:column; align-items:center; padding:1.2rem 0 0.5rem 0; font-family:'Inter',sans-serif;">
        <div style="height:270px; width:100%; display:flex; align-items:center; justify-content:center;">
            <div id="breath-circle" style="
                width:150px; height:150px; border-radius:50%;
                background: radial-gradient(circle at 38% 32%, #DBEAFE, #2563EB 70%);
                box-shadow: 0 20px 45px rgba(37,99,235,0.35);
                transition: transform 4s ease-in-out;
                transform-origin: center;
            "></div>
        </div>
        <p id="breath-label" style="margin-top:0.5rem; font-size:1.2rem; font-weight:600; color:#1E293B; font-family:'Space Grotesk',sans-serif;">
            Siap saat kamu mulai
        </p>
        <p id="breath-count" style="color:#64748B; font-size:0.9rem; margin-bottom:1.1rem;">Siklus: 0</p>
        <div style="display:flex; gap:0.7rem;">
            <button id="breath-play-btn" style="
                background:linear-gradient(135deg,#2563EB,#1D4ED8); color:white; border:none;
                padding:0.65rem 1.6rem; border-radius:16px; font-weight:600; font-size:0.95rem;
                font-family:'Inter',sans-serif; cursor:pointer; box-shadow:0 10px 26px rgba(37,99,235,0.28);
            ">Mulai</button>
            <button id="breath-stop-btn" style="
                background:rgba(255,255,255,0.7); color:#64748B; border:1px solid rgba(148,163,184,0.35);
                padding:0.65rem 1.6rem; border-radius:16px; font-weight:600; font-size:0.95rem;
                font-family:'Inter',sans-serif; cursor:pointer; display:none;
            ">Berhenti</button>
        </div>
    </div>
    <script>
        const circle = document.getElementById('breath-circle');
        const label = document.getElementById('breath-label');
        const countEl = document.getElementById('breath-count');
        const playBtn = document.getElementById('breath-play-btn');
        const stopBtn = document.getElementById('breath-stop-btn');
        const phases = [
            {name: "Tarik Napas...", scale: 1.55, duration: 4000},
            {name: "Tahan...", scale: 1.55, duration: 4000},
            {name: "Hembuskan...", scale: 0.85, duration: 4000},
            {name: "Tahan...", scale: 0.85, duration: 4000},
        ];
        let phaseIdx = 0;
        let cycles = 0;
        let running = false;
        let timeoutId = null;

        function runPhase() {
            if (!running) return;
            const phase = phases[phaseIdx];
            label.textContent = phase.name;
            circle.style.transform = `scale(${phase.scale})`;
            timeoutId = setTimeout(() => {
                phaseIdx = (phaseIdx + 1) % phases.length;
                if (phaseIdx === 0) {
                    cycles += 1;
                    countEl.textContent = "Siklus: " + cycles;
                }
                runPhase();
            }, phase.duration);
        }

        function startBreathing() {
            running = true;
            playBtn.style.display = 'none';
            stopBtn.style.display = 'inline-block';
            runPhase();
        }

        function stopBreathing() {
            running = false;
            if (timeoutId) clearTimeout(timeoutId);
            phaseIdx = 0;
            cycles = 0;
            countEl.textContent = "Siklus: 0";
            label.textContent = "Siap saat kamu mulai";
            circle.style.transform = 'scale(1)';
            playBtn.style.display = 'inline-block';
            stopBtn.style.display = 'none';
        }

        playBtn.addEventListener('click', startBreathing);
        stopBtn.addEventListener('click', stopBreathing);
    </script>
    """
    st.components.v1.html(breathing_html, height=470)

    md(f"""
    <div class="card-soft" style="display:flex; gap:1rem; align-items:flex-start;">
        <div class="icon-box" style="margin-bottom:0; flex-shrink:0;">{icon('wand_sparkles', size=20)}</div>
        <div>
            <b>Teknik ini disebut box breathing:</b> tarik napas 4 detik, tahan 4 detik,
            hembuskan 4 detik, tahan lagi 4 detik. Teknik sederhana ini banyak dipakai
            untuk membantu menenangkan sistem saraf saat merasa cemas atau tertekan.
        </div>
    </div>
    """)


def render_education():
    section_heading("book_open", "Edukasi Singkat Kesehatan Mental")
    st.markdown("Beberapa hal dasar yang baik untuk dipahami, singkat, padat, dan mudah dicerna.")

    with st.expander("Apa itu kesehatan mental?", expanded=True):
        st.write(
            "Kesehatan mental adalah kondisi kesejahteraan yang memungkinkan seseorang "
            "menyadari potensi dirinya, mengatasi tekanan hidup sehari-hari secara wajar, "
            "bekerja atau belajar secara produktif, dan berkontribusi pada lingkungan sekitarnya."
        )

    with st.expander("Apa itu stres?"):
        st.write(
            "Stres adalah respons alami tubuh terhadap tekanan atau tuntutan tertentu. "
            "Dalam kadar wajar, stres bisa memicu motivasi. Namun stres yang berlangsung "
            "terus-menerus tanpa dikelola dapat berdampak pada kondisi fisik dan mental."
        )

    with st.expander("Apa itu depresi?"):
        st.write(
            "Depresi adalah gangguan suasana hati yang ditandai dengan perasaan sedih, "
            "kehilangan minat, atau kehilangan energi yang berlangsung lama dan mengganggu "
            "aktivitas sehari-hari. Depresi berbeda dari sekadar 'sedih biasa' karena "
            "intensitas dan durasinya."
        )

    with st.expander("Kapan harus mencari bantuan?"):
        st.write(
            "Jika perasaan tertekan, cemas, atau sedih berlangsung lebih dari dua minggu, "
            "mengganggu aktivitas sehari-hari, atau muncul pikiran untuk menyakiti diri "
            "sendiri, segera cari bantuan tenaga profesional (psikolog/psikiater) atau "
            "layanan bantuan kesehatan jiwa terdekat."
        )

    disclaimer_card()


render_nav()

if st.session_state.pop("_scroll_top", False):
    st.components.v1.html(
        """<script>
        try {
            const mainSection = window.parent.document.querySelector('[data-testid="stMain"]');
            if (mainSection) { mainSection.scrollTo({top: 0, left: 0, behavior: 'instant'}); }
            window.parent.scrollTo({top: 0, left: 0, behavior: 'instant'});
        } catch (e) {}
        </script>""",
        height=0,
    )

page = st.session_state.page
if page == "home":
    render_home()
elif page == "assessment":
    render_assessment()
elif page == "analyzing":
    render_analyzing()
elif page == "result":
    render_result()
elif page == "therapeutic":
    render_therapeutic()
elif page == "education":
    render_education()
else:
    render_home()
