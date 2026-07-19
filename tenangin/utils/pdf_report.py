import io
import random
from datetime import datetime
from zoneinfo import ZoneInfo

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame,
    Paragraph, Spacer, Table, TableStyle, HRFlowable, Image
)
from reportlab.lib.enums import TA_RIGHT, TA_CENTER
from reportlab.graphics.shapes import Drawing, Rect, Polygon, String

from utils.recommendations import get_recommendation, DISCLAIMER
from utils.assets import logo_path
from model.predict import LOW_THRESHOLD, HIGH_THRESHOLD

FONT_REGULAR = "Helvetica"
FONT_BOLD = "Helvetica-Bold"
FONT_ITALIC = "Helvetica-Oblique"

INK = colors.HexColor("#1F2937")
INK_SOFT = colors.HexColor("#6B7280")
INK_FAINT = colors.HexColor("#9CA3AF")
PRIMARY = colors.HexColor("#1D4ED8")
LINE = colors.HexColor("#E5E7EB")

BADGE_STYLES = {
    "Low": {"bg": colors.HexColor("#DCFCE7"), "fg": colors.HexColor("#15803D"), "label": "LOW"},
    "Medium": {"bg": colors.HexColor("#FEF3C7"), "fg": colors.HexColor("#B45309"), "label": "MEDIUM"},
    "High": {"bg": colors.HexColor("#FEE2E2"), "fg": colors.HexColor("#B91C1C"), "label": "HIGH"},
}

BAR_ZONE_COLORS = [colors.HexColor("#BBF7D0"), colors.HexColor("#FDE68A"), colors.HexColor("#FECACA")]
# Batas zona warna pada score bar VISUAL SAMA PERSIS dengan ambang kategori
# di model/predict.py (satu sumber kebenaran, bukan salinan hardcoded
# terpisah - lihat audit Prioritas 2 & 8).
BAR_ZONE_BOUNDS = [0.0, LOW_THRESHOLD, HIGH_THRESHOLD, 1.0]

PAGE_W, PAGE_H = A4
LEFT_MARGIN = 2.2 * cm
RIGHT_MARGIN = 2.2 * cm
TOP_MARGIN = 1.8 * cm
FOOTER_RESERVED = 3.6 * cm  # ruang tetap di bawah utk disclaimer + info generate


def _generate_report_id(generated_at: datetime) -> str:
    suffix = f"{random.randint(0, 999999):06d}"
    return f"TNG-{generated_at.strftime('%Y%m%d')}-{suffix}"


def _build_header(styles):
    name_style = ParagraphStyle(
        "OrgName", parent=styles["Normal"], fontName=FONT_BOLD,
        fontSize=17, textColor=PRIMARY, leading=20,
    )
    tagline_style = ParagraphStyle(
        "OrgTagline", parent=styles["Normal"], fontName=FONT_REGULAR,
        fontSize=8.5, textColor=INK_SOFT, leading=11,
    )
    doctitle_style = ParagraphStyle(
        "DocTitle", parent=styles["Normal"], fontName=FONT_REGULAR,
        fontSize=9.5, textColor=INK_SOFT, alignment=TA_RIGHT, leading=12,
    )

    logo_size = 1.95 * cm
    logo_img = Image(logo_path(), width=logo_size, height=logo_size)
    name_block = [
        Spacer(1, 4),
        Paragraph("Tenang.in", name_style),
        Paragraph("Skrining Kesehatan Mental Berbasis AI", tagline_style),
    ]
    right_block = Paragraph("Laporan Hasil<br/>Self-Assessment", doctitle_style)

    header_table = Table(
        [[logo_img, name_block, right_block]],
        colWidths=[2.35 * cm, 9.15 * cm, 4.5 * cm],
    )
    header_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (0, 0), "LEFT"),
        ("ALIGN", (2, 0), (2, 0), "RIGHT"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    return header_table


def _build_report_meta_row(report_id, generated_at, styles):
    meta_style = ParagraphStyle(
        "MetaCaption", parent=styles["Normal"], fontName=FONT_REGULAR,
        fontSize=8, textColor=INK_FAINT, leading=10,
    )
    meta_style_right = ParagraphStyle("MetaCaptionRight", parent=meta_style, alignment=TA_RIGHT)
    row = Table(
        [[
            Paragraph(f"No. Laporan&nbsp;&nbsp;<b>{report_id}</b>", meta_style),
            Paragraph(generated_at.strftime("%d %B %Y, %H:%M WIB"), meta_style_right),
        ]],
        colWidths=[8 * cm, 8 * cm],
    )
    row.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return row


def _build_category_badge(category):
    style = BADGE_STYLES.get(category, BADGE_STYLES["Medium"])
    badge_style = ParagraphStyle(
        "BadgeText", fontName=FONT_BOLD, fontSize=9,
        textColor=style["fg"], alignment=TA_CENTER, leading=11,
    )
    t = Table([[Paragraph(style["label"], badge_style)]], colWidths=[2.6 * cm], rowHeights=[0.62 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), style["bg"]),
        ("VALIGN", (0, 0), (0, 0), "MIDDLE"),
        ("ALIGN", (0, 0), (0, 0), "CENTER"),
        ("ROUNDEDCORNERS", [8, 8, 8, 8]),
        ("TOPPADDING", (0, 0), (0, 0), 0),
        ("BOTTOMPADDING", (0, 0), (0, 0), 0),
    ]))
    return t


def _build_info_table(probability, category, agreement_score, generated_at, styles):
    label_style = ParagraphStyle(
        "InfoLabel", parent=styles["Normal"], fontName=FONT_REGULAR,
        fontSize=9.5, textColor=INK_SOFT, leading=13,
    )
    value_style = ParagraphStyle(
        "InfoValue", parent=styles["Normal"], fontName=FONT_BOLD,
        fontSize=11, textColor=INK, leading=14,
    )
    score_value_style = ParagraphStyle("ScoreValue", parent=value_style, fontSize=15, textColor=PRIMARY)

    rows = [
        [Paragraph("Tanggal Pemeriksaan", label_style),
         Paragraph(generated_at.strftime("%d %B %Y"), value_style)],
        [Paragraph("Probabilistic Risk Score", label_style),
         Paragraph(f"{probability * 100:.1f}%", score_value_style)],
        [Paragraph("Kategori Risiko", label_style), _build_category_badge(category)],
    ]
    if agreement_score is not None:
        rows.append([
            Paragraph("Model Agreement*", label_style),
            Paragraph(f"{agreement_score * 100:.1f}%", value_style),
        ])

    t = Table(rows, colWidths=[6.5 * cm, 9.5 * cm])
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 11),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 11),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("LINEBELOW", (0, 0), (-1, -2), 0.6, LINE),
    ]))
    return t


def _build_score_bar(probability, width=15.5 * cm):
    bar_h = 0.4 * cm
    top_pad = 0.32 * cm
    bottom_pad = 0.3 * cm
    d = Drawing(width, bar_h + top_pad + bottom_pad)
    bar_y = bottom_pad

    for i in range(3):
        x0 = width * BAR_ZONE_BOUNDS[i]
        seg_w = width * (BAR_ZONE_BOUNDS[i + 1] - BAR_ZONE_BOUNDS[i])
        d.add(Rect(x0, bar_y, seg_w, bar_h, fillColor=BAR_ZONE_COLORS[i], strokeColor=None))

    pct = max(0.012, min(0.988, probability))
    marker_x = width * pct
    marker_top = bar_y + bar_h + top_pad
    d.add(Polygon(
        points=[marker_x - 4.2, marker_top, marker_x + 4.2, marker_top, marker_x, bar_y + bar_h + 2],
        fillColor=INK, strokeColor=None,
    ))

    scale_points = [
        (0.0, "0"),
        (LOW_THRESHOLD, f"{LOW_THRESHOLD * 100:.0f}"),
        (HIGH_THRESHOLD, f"{HIGH_THRESHOLD * 100:.0f}"),
        (1.0, "100"),
    ]
    for frac, label in scale_points:
        x = width * frac
        anchor = "start" if frac == 0 else ("end" if frac == 1.0 else "middle")
        d.add(String(x, 0, label, fontSize=7, fillColor=INK_FAINT, textAnchor=anchor, fontName=FONT_REGULAR))

    return d


def _draw_footer(canvas_obj, doc, report_id, generated_at):
    """Footer sungguhan: digambar di posisi TETAP dekat dasar setiap
    halaman (bukan mengikuti alur konten), supaya selalu berada di
    paling bawah halaman seperti dokumen formal pada umumnya."""
    canvas_obj.saveState()

    left = LEFT_MARGIN
    right = PAGE_W - RIGHT_MARGIN
    line_y = FOOTER_RESERVED - 0.55 * cm

    canvas_obj.setStrokeColor(LINE)
    canvas_obj.setLineWidth(0.6)
    canvas_obj.line(left, line_y, right, line_y)

    disclaimer_style = ParagraphStyle(
        "Disclaimer", fontName=FONT_ITALIC, fontSize=7.8, leading=11.5, textColor=INK_SOFT,
    )
    p = Paragraph(DISCLAIMER, disclaimer_style)
    avail_w = right - left
    p_w, p_h = p.wrap(avail_w, 2 * cm)
    disclaimer_top = line_y - 0.32 * cm
    p.drawOn(canvas_obj, left, disclaimer_top - p_h)

    gen_y = disclaimer_top - p_h - 0.45 * cm
    canvas_obj.setFont(FONT_REGULAR, 7.8)
    canvas_obj.setFillColor(INK_FAINT)
    canvas_obj.drawString(left, gen_y, "Dihasilkan oleh Tenang.in")
    canvas_obj.drawString(left, gen_y - 10.5, "tenangin.com")
    canvas_obj.drawRightString(right, gen_y, f"Dibuat pada {generated_at.strftime('%d %B %Y, %H:%M WIB')}")
    canvas_obj.drawRightString(right, gen_y - 10.5, report_id)

    canvas_obj.restoreState()


def generate_pdf_report(result: dict) -> bytes:
    buffer = io.BytesIO()
    styles = getSampleStyleSheet()

    category = result["category"]
    probability = result["probability"]
    agreement_score = result.get("agreement_score")
    rec = get_recommendation(category)
    generated_at = datetime.now(ZoneInfo("Asia/Jakarta"))
    report_id = _generate_report_id(generated_at)

    frame = Frame(
        LEFT_MARGIN, FOOTER_RESERVED,
        PAGE_W - LEFT_MARGIN - RIGHT_MARGIN,
        PAGE_H - TOP_MARGIN - FOOTER_RESERVED,
        leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0,
        id="main",
    )

    def _on_page(canvas_obj, doc):
        _draw_footer(canvas_obj, doc, report_id, generated_at)

    doc = BaseDocTemplate(
        buffer, pagesize=A4,
        topMargin=TOP_MARGIN, bottomMargin=FOOTER_RESERVED,
        leftMargin=LEFT_MARGIN, rightMargin=RIGHT_MARGIN,
    )
    doc.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=_on_page)])

    section_label_style = ParagraphStyle(
        "SectionLabel", parent=styles["Normal"], fontName=FONT_BOLD,
        fontSize=10, textColor=INK, leading=13, spaceBefore=20, spaceAfter=8,
    )
    body_style = ParagraphStyle(
        "Body", parent=styles["Normal"], fontName=FONT_REGULAR,
        fontSize=10, leading=16, textColor=INK,
    )
    bullet_style = ParagraphStyle("Bullet", parent=body_style, leftIndent=12, spaceAfter=7)

    footnote_style = ParagraphStyle(
        "Footnote", parent=styles["Normal"], fontName=FONT_ITALIC,
        fontSize=7.5, leading=10.5, textColor=INK_FAINT, spaceBefore=4,
    )

    story = []
    story.append(_build_header(styles))
    story.append(Spacer(1, 12))
    story.append(HRFlowable(width="100%", thickness=0.8, color=LINE))
    story.append(Spacer(1, 6))
    story.append(_build_report_meta_row(report_id, generated_at, styles))

    story.append(Paragraph("HASIL SKRINING", section_label_style))
    story.append(_build_info_table(probability, category, agreement_score, generated_at, styles))
    if agreement_score is not None:
        story.append(Paragraph(
            "*Model Agreement mengukur seberapa sepakat ketiga base learner "
            "(XGBoost, CatBoost, LightGBM) terhadap hasil ini, dihitung dari "
            "variasi probabilitas antar model. Ini BUKAN probabilitas "
            "kebenaran prediksi maupun confidence interval statistik.",
            footnote_style,
        ))
    story.append(Spacer(1, 16))
    story.append(_build_score_bar(probability))
    story.append(Spacer(1, 6))

    story.append(Paragraph("TENTANG HASIL INI", section_label_style))
    story.append(Paragraph(
        "Probabilistic risk score di atas adalah nilai keluaran langsung "
        "dari fungsi predict_proba() model machine learning stacked "
        "ensemble (base learner XGBoost, CatBoost, LightGBM; meta-learner "
        "Logistic Regression) berdasarkan jawaban self-assessment yang "
        "diisi, tanpa modifikasi atau kalibrasi tambahan. Skor ini "
        "dikategorikan menjadi tiga tingkat risiko dan sebaiknya dimaknai "
        "sebagai gambaran awal, bukan kesimpulan akhir.",
        body_style,
    ))

    story.append(Paragraph("REKOMENDASI", section_label_style))
    story.append(Paragraph(rec["summary"], body_style))
    story.append(Spacer(1, 9))
    for point in rec["points"]:
        story.append(Paragraph(f"&#8226;&nbsp;&nbsp;{point}", bullet_style))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()
