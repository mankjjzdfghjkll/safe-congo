"""
MAL1471 – Phase 1(a) – PDF Report Generator
Student : MANKAND-A-MUTEB JOSEE
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm, mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, KeepTogether
)
from reportlab.platypus.flowables import Flowable
from reportlab.graphics.shapes import (
    Drawing, Rect, String, Line, Polygon, Group
)
from reportlab.graphics import renderPDF
from reportlab.graphics.charts.barcharts import VerticalBarChart

# ── Colour palette ────────────────────────────────────────────────────────────
DARK_BLUE   = colors.HexColor("#1a3a5c")
MID_BLUE    = colors.HexColor("#2563a8")
LIGHT_BLUE  = colors.HexColor("#dbeafe")
ACCENT      = colors.HexColor("#e67e22")
GRAY_LINE   = colors.HexColor("#b0bec5")
WHITE       = colors.white
TEXT_DARK   = colors.HexColor("#1a202c")
ROW_ALT     = colors.HexColor("#eef4fb")

W, H = A4   # 595.27 x 841.89 pt

# ─────────────────────────────────────────────────────────────────────────────
# CUSTOM FLOWABLE – Section header banner
# ─────────────────────────────────────────────────────────────────────────────
class SectionBanner(Flowable):
    def __init__(self, number, title, width=None):
        super().__init__()
        self.number = number
        self.title  = title
        self.width  = width or (W - 4*cm)
        self.height = 1.1*cm

    def draw(self):
        w, h = self.width, self.height
        # background
        self.canv.setFillColor(DARK_BLUE)
        self.canv.roundRect(0, 0, w, h, 6, fill=1, stroke=0)
        # accent left bar
        self.canv.setFillColor(ACCENT)
        self.canv.rect(0, 0, 0.5*cm, h, fill=1, stroke=0)
        # number circle
        cx, cy, r = 1.3*cm, h/2, 0.38*cm
        self.canv.setFillColor(ACCENT)
        self.canv.circle(cx, cy, r, fill=1, stroke=0)
        self.canv.setFillColor(WHITE)
        self.canv.setFont("Helvetica-Bold", 11)
        self.canv.drawCentredString(cx, cy - 4, self.number)
        # title
        self.canv.setFillColor(WHITE)
        self.canv.setFont("Helvetica-Bold", 12)
        self.canv.drawString(2.3*cm, h/2 - 5, self.title)


# ─────────────────────────────────────────────────────────────────────────────
# CUSTOM FLOWABLE – Org Chart
# ─────────────────────────────────────────────────────────────────────────────
class OrgChart(Flowable):
    def __init__(self, width=None, height=8*cm):
        super().__init__()
        self.width  = width or (W - 4*cm)
        self.height = height

    def _box(self, canv, x, y, w, h, text, fill, text_color=WHITE, subtext=None, border_color=None):
        canv.setFillColor(fill)
        canv.setStrokeColor(border_color or fill)
        canv.setLineWidth(1.2)
        canv.roundRect(x, y, w, h, 5, fill=1, stroke=1)
        canv.setFillColor(text_color)
        canv.setFont("Helvetica-Bold", 8.5)
        canv.drawCentredString(x + w/2, y + h/2 + (5 if subtext else 2), text)
        if subtext:
            canv.setFont("Helvetica", 7)
            canv.drawCentredString(x + w/2, y + h/2 - 6, subtext)

    def _arrow(self, canv, x1, y1, x2, y2):
        canv.setStrokeColor(MID_BLUE)
        canv.setLineWidth(1.5)
        canv.line(x1, y1, x2, y2)
        # arrowhead via path
        canv.setFillColor(MID_BLUE)
        dx, dy = 4, 4
        p = canv.beginPath()
        p.moveTo(x2, y2)
        p.lineTo(x2 - dx, y2 + dy)
        p.lineTo(x2 + dx, y2 + dy)
        p.close()
        canv.drawPath(p, fill=1, stroke=0)

    def draw(self):
        canv = self.canv
        W, H = self.width, self.height

        bw  = 4.8*cm   # box width
        bh  = 1.1*cm   # box height
        cx  = W / 2    # center x
        gap = 1.2*cm   # vertical gap between rows

        y4 = H - bh - 0.3*cm   # row 1 top
        y3 = y4 - bh - gap
        y2 = y3 - bh - gap
        y1 = y2 - bh - gap

        # ── Row 1 – Direction Générale
        self._box(canv, cx - bw/2, y4, bw, bh,
                  "Direction Générale – Kinshasa", DARK_BLUE)

        # ── Arrow 1→2
        self._arrow(canv, cx, y4, cx, y3 + bh)

        # ── Row 2 – Direction Provinciale
        self._box(canv, cx - bw/2, y3, bw, bh,
                  "Direction Provinciale", MID_BLUE,
                  subtext="Haut-Katanga – Lubumbashi")

        # ── Arrow 2 → 3 (fan out)
        # centre line down
        self._arrow(canv, cx, y3, cx, y2 + bh)

        # ── Row 3 – 3 services side by side
        sw   = 3.4*cm
        gap3 = 0.4*cm
        total3 = 3*sw + 2*gap3
        x3a  = cx - total3/2
        x3b  = x3a + sw + gap3
        x3c  = x3b + sw + gap3

        fill3 = colors.HexColor("#3b82f6")
        self._box(canv, x3a, y2, sw, bh, "Recouvrement", fill3)
        self._box(canv, x3b, y2, sw, bh, "Formation /", fill3, subtext="Technique")
        self._box(canv, x3c, y2, sw, bh, "RH / Logistique", fill3)

        # horizontal connector
        canv.setStrokeColor(MID_BLUE)
        canv.setLineWidth(1.2)
        mid_y = y2 + bh + gap/2
        canv.line(x3a + sw/2, mid_y, x3c + sw/2, mid_y)
        for xc in [x3a + sw/2, x3b + sw/2, x3c + sw/2]:
            canv.line(xc, mid_y, xc, y2 + bh)

        # ── Row 4 – IT (highlighted)
        it_w = 5.2*cm
        it_x = cx - it_w/2
        self._box(canv, it_x, y1, it_w, bh,
                  "◉  Service Informatique / Pool IT",
                  colors.HexColor("#0f4c81"),
                  subtext="← MON ÉQUIPE")

        # Arrow from row 2 to IT (diagonal left)
        self._arrow(canv, x3b + sw/2, y2, cx, y1 + bh)

        # ── MY ROLE badge
        badge_y = y1 - 0.9*cm
        badge_h = 0.7*cm
        badge_w = 6*cm
        canv.setFillColor(ACCENT)
        canv.roundRect(cx - badge_w/2, badge_y, badge_w, badge_h, 4, fill=1, stroke=0)
        canv.setFillColor(WHITE)
        canv.setFont("Helvetica-Bold", 8)
        canv.drawCentredString(cx, badge_y + badge_h/2 - 3,
                               "Cellule Développement ← MON POSTE")


# ─────────────────────────────────────────────────────────────────────────────
# STYLES
# ─────────────────────────────────────────────────────────────────────────────
styles = getSampleStyleSheet()

body_style = ParagraphStyle(
    "body", fontName="Times-Roman", fontSize=11,
    leading=16, alignment=TA_JUSTIFY,
    textColor=TEXT_DARK, spaceAfter=8
)
body_bold = ParagraphStyle(
    "bodyB", parent=body_style, fontName="Times-Bold"
)
center_style = ParagraphStyle(
    "center", fontName="Times-Roman", fontSize=11,
    alignment=TA_CENTER, textColor=TEXT_DARK
)
title_main = ParagraphStyle(
    "titleMain", fontName="Helvetica-Bold", fontSize=20,
    textColor=WHITE, alignment=TA_CENTER, leading=26
)
title_sub = ParagraphStyle(
    "titleSub", fontName="Helvetica", fontSize=13,
    textColor=colors.HexColor("#cfe2ff"), alignment=TA_CENTER, leading=18
)
label_style = ParagraphStyle(
    "label", fontName="Helvetica-Bold", fontSize=9,
    textColor=WHITE, alignment=TA_CENTER, leading=12
)
cell_style = ParagraphStyle(
    "cell", fontName="Times-Roman", fontSize=9.5,
    leading=13, alignment=TA_JUSTIFY, textColor=TEXT_DARK
)
bullet_style = ParagraphStyle(
    "bullet", fontName="Times-Roman", fontSize=11,
    leading=16, alignment=TA_JUSTIFY, textColor=TEXT_DARK,
    leftIndent=14, firstLineIndent=-14, spaceAfter=5
)

# ─────────────────────────────────────────────────────────────────────────────
# HEADER / FOOTER CANVAS
# ─────────────────────────────────────────────────────────────────────────────
def header_footer(canvas, doc):
    canvas.saveState()
    pw = doc.pagesize[0]

    # ── Header bar (not on page 1)
    if doc.page > 1:
        canvas.setFillColor(DARK_BLUE)
        canvas.rect(0, H - 1.2*cm, pw, 1.2*cm, fill=1, stroke=0)
        canvas.setFillColor(ACCENT)
        canvas.rect(0, H - 1.2*cm, 0.6*cm, 1.2*cm, fill=1, stroke=0)
        canvas.setFillColor(WHITE)
        canvas.setFont("Helvetica-Bold", 8.5)
        canvas.drawString(1*cm, H - 0.75*cm, "MAL1471 – Phase 1(a) – Environnement du Stage")
        canvas.setFont("Helvetica", 8.5)
        canvas.drawRightString(pw - 1*cm, H - 0.75*cm, "MANKAND-A-MUTEB JOSEE | INPP Haut-Katanga")

    # ── Footer
    canvas.setFillColor(DARK_BLUE)
    canvas.rect(0, 0, pw, 0.9*cm, fill=1, stroke=0)
    canvas.setFillColor(ACCENT)
    canvas.rect(0, 0, 0.6*cm, 0.9*cm, fill=1, stroke=0)
    canvas.setFillColor(WHITE)
    canvas.setFont("Helvetica", 8)
    canvas.drawString(1*cm, 0.35*cm,
                      "Institut National de Préparation Professionnelle (INPP) – Direction Provinciale Haut-Katanga")
    canvas.setFont("Helvetica-Bold", 8)
    canvas.drawRightString(pw - 1*cm, 0.35*cm, f"Page {doc.page}")
    canvas.restoreState()


# ─────────────────────────────────────────────────────────────────────────────
# BUILD DOCUMENT
# ─────────────────────────────────────────────────────────────────────────────
output = r"C:\Users\PC\Desktop\TP machine learning\MANKAND-A-MUTEB_JOSEE_MAL1471_Phase1a.pdf"

doc = SimpleDocTemplate(
    output, pagesize=A4,
    leftMargin=2.5*cm, rightMargin=2*cm,
    topMargin=2*cm,    bottomMargin=1.8*cm,
    title="MAL1471 Phase1a – MANKAND-A-MUTEB JOSEE",
    author="MANKAND-A-MUTEB JOSEE",
    subject="Environnement du stage – INPP Haut-Katanga"
)

story = []

# ══════════════════════════════════════════════════════════════════════════════
# COVER PAGE
# ══════════════════════════════════════════════════════════════════════════════
cover_data = [
    [""],   # row 0 – spacer
]
cover_table = Table(
    [[Paragraph("MAL1471 – Projet Final 2026", title_main)],
     [Paragraph("Phase 1(a) · Environnement du Stage", title_sub)],
     [Spacer(1, 0.5*cm)],
     [Paragraph("MANKAND-A-MUTEB JOSEE", ParagraphStyle(
         "n", fontName="Helvetica-Bold", fontSize=22,
         textColor=ACCENT, alignment=TA_CENTER))],
     [Paragraph("Matricule : SI/20223393", ParagraphStyle(
         "m", fontName="Helvetica", fontSize=12,
         textColor=colors.HexColor("#cfe2ff"), alignment=TA_CENTER))],
     [Spacer(1, 0.8*cm)],
     [Paragraph("Organisme d'accueil", ParagraphStyle(
         "ol", fontName="Helvetica", fontSize=11,
         textColor=colors.HexColor("#cfe2ff"), alignment=TA_CENTER))],
     [Paragraph("Institut National de Préparation Professionnelle (INPP)", ParagraphStyle(
         "on", fontName="Helvetica-Bold", fontSize=14,
         textColor=WHITE, alignment=TA_CENTER))],
     [Paragraph("Direction Provinciale du Haut-Katanga – Lubumbashi, RDC", ParagraphStyle(
         "oc", fontName="Helvetica", fontSize=11,
         textColor=colors.HexColor("#cfe2ff"), alignment=TA_CENTER))],
     [Spacer(1, 0.8*cm)],
     [Paragraph("27 mai 2026", ParagraphStyle(
         "date", fontName="Helvetica-Oblique", fontSize=11,
         textColor=colors.HexColor("#93c5fd"), alignment=TA_CENTER))],
     [Paragraph("Université Nouveaux Horizons · Faculté des Sciences Informatiques", ParagraphStyle(
         "uni", fontName="Helvetica", fontSize=10,
         textColor=colors.HexColor("#93c5fd"), alignment=TA_CENTER))],
    ],
    colWidths=[doc.width],
)
cover_table.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,-1), DARK_BLUE),
    ("ROWBACKGROUNDS", (0,0), (-1,-1), [DARK_BLUE]),
    ("ALIGN",       (0,0), (-1,-1), "CENTER"),
    ("VALIGN",      (0,0), (-1,-1), "MIDDLE"),
    ("TOPPADDING",  (0,0), (-1,-1), 6),
    ("BOTTOMPADDING",(0,0),(-1,-1), 6),
    ("LEFTPADDING", (0,0), (-1,-1), 10),
    ("RIGHTPADDING",(0,0), (-1,-1), 10),
]))

# Wrap cover in full-page blue rect
full_cover = Table([[cover_table]], colWidths=[doc.width])
full_cover.setStyle(TableStyle([
    ("BACKGROUND", (0,0),(-1,-1), DARK_BLUE),
    ("TOPPADDING", (0,0),(-1,-1), 40),
    ("BOTTOMPADDING",(0,0),(-1,-1), 40),
    ("LEFTPADDING", (0,0),(-1,-1), 0),
    ("RIGHTPADDING",(0,0),(-1,-1), 0),
]))
story.append(full_cover)
story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 – L'ORGANISATION
# ══════════════════════════════════════════════════════════════════════════════
story.append(SectionBanner("1", "L'Organisation"))
story.append(Spacer(1, 0.3*cm))

story.append(Paragraph(
    "L'<b>Institut National de Préparation Professionnelle (INPP)</b> est un établissement "
    "public congolais placé sous la tutelle du Ministère de l'Emploi, du Travail et de la "
    "Prévoyance Sociale. Sa vocation première est d'assurer la <b>formation continue, le "
    "perfectionnement et la reconversion professionnelle</b> des travailleurs salariés du "
    "secteur formel en République Démocratique du Congo.", body_style))

story.append(Paragraph(
    "Sur le plan de la taille et de la portée géographique, l'INPP dispose d'une présence "
    "<b>nationale</b> : une Direction Générale basée à Kinshasa, des Directions Provinciales "
    "dans les principales provinces, et des antennes locales dans plusieurs villes. "
    "La <b>Direction Provinciale du Haut-Katanga</b>, où j'effectue mon stage, est implantée "
    "à Lubumbashi – capitale économique et minière de la province.", body_style))

story.append(Paragraph(
    "Son financement repose principalement sur des <b>cotisations patronales obligatoires</b> "
    "comprises entre <b>0,5 % et 3 %</b> de la masse salariale brute des entreprises "
    "assujetties. Ce modèle lui confère une relative autonomie financière et l'ancre "
    "fortement dans le tissu économique local, notamment auprès des grandes entreprises "
    "minières et de leurs sous-traitants.", body_style))

# Info boxes
info_data = [
    ["Secteur", "Domaine", "Présence", "Financement"],
    ["Formation\nProfessionnelle\n(Public)", "Emploi &\nCapital Humain", "Nationale\n(DG Kinshasa\n+ provinciales)", "Cotisations\npatronales\n0,5 % – 3 %"],
]
info_tbl = Table(info_data, colWidths=[doc.width/4]*4, rowHeights=[0.7*cm, 1.8*cm])
info_tbl.setStyle(TableStyle([
    ("BACKGROUND",   (0,0),(3,0), DARK_BLUE),
    ("BACKGROUND",   (0,1),(3,1), LIGHT_BLUE),
    ("TEXTCOLOR",    (0,0),(3,0), WHITE),
    ("TEXTCOLOR",    (0,1),(3,1), DARK_BLUE),
    ("FONTNAME",     (0,0),(3,0), "Helvetica-Bold"),
    ("FONTNAME",     (0,1),(3,1), "Helvetica"),
    ("FONTSIZE",     (0,0),(3,-1), 9),
    ("ALIGN",        (0,0),(-1,-1), "CENTER"),
    ("VALIGN",       (0,0),(-1,-1), "MIDDLE"),
    ("GRID",         (0,0),(-1,-1), 0.5, GRAY_LINE),
    ("ROUNDEDCORNERS", [4]),
]))
story.append(info_tbl)
story.append(Spacer(1, 0.4*cm))

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 – MISSION ET STRATÉGIE
# ══════════════════════════════════════════════════════════════════════════════
story.append(SectionBanner("2", "Mission et Stratégie (observée)"))
story.append(Spacer(1, 0.3*cm))

story.append(Paragraph(
    "La mission que j'ai pu observer au quotidien se traduit concrètement par <b>trois "
    "axes stratégiques</b> complémentaires :", body_style))

axes = [
    ("① Adaptation aux besoins réels",
     "L'INPP calibre ses programmes de formation sur les demandes effectives des entreprises "
     "locales, en particulier dans les secteurs minier et de la sous-traitance qui dominent "
     "l'économie katangaise."),
    ("② Modernisation des outils",
     "La direction affiche clairement l'objectif de <b>digitaliser les processus internes</b> "
     "– gestion des stagiaires, suivi des cotisations, reporting – pour accroître l'efficacité "
     "opérationnelle."),
    ("③ Partenariats internationaux",
     "Un partenariat actif avec la <b>JICA</b> (Agence Japonaise de Coopération Internationale) "
     "est régulièrement évoqué en réunion comme levier d'innovation technique et de transfert "
     "de bonnes pratiques."),
]
for titre, desc in axes:
    story.append(Paragraph(f"<b>{titre}</b> — {desc}", bullet_style))

story.append(Spacer(1, 0.2*cm))
story.append(Paragraph(
    "Ces priorités expliquent pourquoi le <b>Pool Informatique</b> occupe une place "
    "croissante au sein de la structure : il est le vecteur opérationnel de cette "
    "transformation numérique. J'ai pu constater que chaque réunion hebdomadaire de "
    "direction intègre un point sur l'avancement des projets informatiques en cours.",
    body_style))

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3 – STRUCTURE ET ORGANIGRAMME
# ══════════════════════════════════════════════════════════════════════════════
story.append(SectionBanner("3", "Structure et Organigramme"))
story.append(Spacer(1, 0.3*cm))

story.append(Paragraph(
    "La Direction Provinciale du Haut-Katanga s'articule autour de "
    "<b>six services fonctionnels</b> principaux :", body_style))

# Services table
srv_headers = [
    Paragraph("<b>Service</b>", label_style),
    Paragraph("<b>Mission principale</b>", label_style),
    Paragraph("<b>Lien avec le Pool IT</b>", label_style),
]
srv_data = [
    srv_headers,
    ["Direction Provinciale",
     "Pilotage stratégique, représentation institutionnelle, validation des orientations",
     "Destinataire des tableaux de bord numériques"],
    ["Recouvrement",
     "Contrôle et collecte des cotisations patronales des entreprises assujetties",
     "Automatisation des relances et des états de recouvrement"],
    ["Formation / Technique",
     "Conception et délivrance des programmes de formation, gestion des stagiaires",
     "Fournisseur principal des données à numériser"],
    ["Ressources Humaines",
     "Gestion du personnel, recrutement, évaluation des agents",
     "Demande d'applications de gestion du personnel"],
    ["Logistique",
     "Gestion du matériel, des locaux et des équipements",
     "Inventaire numérique du parc matériel"],
    ["Informatique (Pool IT) ◉",
     "Maintenance des systèmes, numérisation des processus, développement applicatif",
     "Service transversal au service de tous les autres"],
]

srv_tbl_data = []
for i, row in enumerate(srv_data):
    if i == 0:
        srv_tbl_data.append(row)
    else:
        srv_tbl_data.append([
            Paragraph(f"<b>{row[0]}</b>" if i == len(srv_data)-1 else row[0], cell_style),
            Paragraph(row[1], cell_style),
            Paragraph(row[2], cell_style),
        ])

srv_tbl = Table(srv_tbl_data,
                colWidths=[3.8*cm, 6.5*cm, 5*cm],
                repeatRows=1)
tbl_style = TableStyle([
    ("BACKGROUND",  (0,0),(2,0), DARK_BLUE),
    ("TEXTCOLOR",   (0,0),(2,0), WHITE),
    ("FONTNAME",    (0,0),(2,0), "Helvetica-Bold"),
    ("FONTSIZE",    (0,0),(2,0), 9),
    ("ALIGN",       (0,0),(2,0), "CENTER"),
    ("VALIGN",      (0,0),(-1,-1), "MIDDLE"),
    ("GRID",        (0,0),(-1,-1), 0.5, GRAY_LINE),
    ("TOPPADDING",  (0,0),(-1,-1), 4),
    ("BOTTOMPADDING",(0,0),(-1,-1), 4),
    ("LEFTPADDING", (0,0),(-1,-1), 5),
    ("RIGHTPADDING",(0,0),(-1,-1), 5),
    ("ROWBACKGROUNDS", (0,1),(-1,-1), [WHITE, ROW_ALT]),
    # highlight IT row
    ("BACKGROUND",  (0,len(srv_data)-1),(2,len(srv_data)-1), colors.HexColor("#0f4c81")),
    ("TEXTCOLOR",   (0,len(srv_data)-1),(2,len(srv_data)-1), WHITE),
    ("FONTNAME",    (0,len(srv_data)-1),(2,len(srv_data)-1), "Helvetica-Bold"),
])
srv_tbl.setStyle(tbl_style)
story.append(srv_tbl)
story.append(Spacer(1, 0.5*cm))

# Org chart
story.append(Paragraph("<b>Organigramme – Positionnement de l'équipe Informatique</b>",
                        ParagraphStyle("oc_title", fontName="Helvetica-Bold", fontSize=10,
                                       textColor=DARK_BLUE, alignment=TA_CENTER,
                                       spaceAfter=4)))
story.append(OrgChart(width=doc.width, height=7.5*cm))
story.append(Spacer(1, 0.3*cm))

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4 – MON STAGE ET MON ÉQUIPE
# ══════════════════════════════════════════════════════════════════════════════
story.append(SectionBanner("4", "Mon Stage et Mon Équipe"))
story.append(Spacer(1, 0.3*cm))

story.append(Paragraph(
    "J'effectue mon stage au sein du <b>Pool Informatique / Cellule de Développement</b> "
    "de l'INPP Haut-Katanga. Cette cellule, composée d'environ <b>six collaborateurs</b> "
    "(développeurs, techniciens réseau et administrateurs systèmes), constitue le centre "
    "névralgique de la transformation numérique de la Direction Provinciale.", body_style))

story.append(Paragraph(
    "La cellule est rattachée directement au Service Informatique, lui-même sous "
    "l'autorité du Chef de Service, qui rend compte au Directeur Provincial. "
    "Cette ligne hiérarchique courte (trois niveaux) favorise des échanges directs "
    "et une réactivité appréciable.", body_style))

story.append(Paragraph(
    "En termes d'interactions transversales, le Pool IT collabore étroitement avec :", body_style))

interactions = [
    ("Service Formation / Technique",
     "dématérialisation des dossiers de stagiaires, génération automatique d'attestations"),
    ("Service Recouvrement",
     "automatisation des états de cotisations et des relances d'entreprises"),
    ("Ressources Humaines",
     "gestion numérique des dossiers du personnel et des évaluations"),
    ("Direction Provinciale",
     "production de tableaux de bord et de rapports d'activité consolidés"),
]
for svc, desc in interactions:
    story.append(Paragraph(f"• <b>{svc}</b> : {desc}", bullet_style))

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 5 – MON RÔLE
# ══════════════════════════════════════════════════════════════════════════════
story.append(Spacer(1, 0.2*cm))
story.append(SectionBanner("5", "Mon Rôle et Mes Responsabilités"))
story.append(Spacer(1, 0.3*cm))

story.append(Paragraph(
    "Mon titre de poste est <b>Stagiaire Développeuse</b> au sein de la Cellule de "
    "Développement. Mes responsabilités quotidiennes couvrent quatre domaines :", body_style))

tasks_data = [
    [Paragraph("<b>Tâche</b>", label_style),
     Paragraph("<b>Description détaillée</b>", label_style),
     Paragraph("<b>Outils / Technologies</b>", label_style)],
    [Paragraph("Développement\nd'applications\ninternes", cell_style),
     Paragraph("Conception et codage d'un module de gestion des dossiers de stagiaires : "
               "enregistrement, suivi des présences, génération d'attestations de formation.", cell_style),
     Paragraph("Python (Flask), HTML/CSS, Bootstrap", cell_style)],
    [Paragraph("Administration\nde bases de\ndonnées", cell_style),
     Paragraph("Mise à jour et maintenance de la base de données centralisant les inscriptions "
               "de stagiaires, les résultats d'évaluation et les fiches d'entreprises partenaires.", cell_style),
     Paragraph("MySQL, phpMyAdmin", cell_style)],
    [Paragraph("Support\ntechnique", cell_style),
     Paragraph("Assistance aux agents des autres services pour l'utilisation des outils informatiques "
               "existants ; rédaction de guides utilisateurs simplifiés.", cell_style),
     Paragraph("Documentation Office, tutoriels internes", cell_style)],
    [Paragraph("Analyse\ndes besoins", cell_style),
     Paragraph("Participation aux réunions inter-services pour recueillir les besoins applicatifs "
               "et les traduire en spécifications fonctionnelles exploitables.", cell_style),
     Paragraph("UML (diagrammes de cas d'usage)", cell_style)],
]

tasks_tbl = Table(tasks_data,
                  colWidths=[3*cm, 8.3*cm, 4*cm],
                  repeatRows=1)
tasks_tbl.setStyle(TableStyle([
    ("BACKGROUND",  (0,0),(2,0), DARK_BLUE),
    ("TEXTCOLOR",   (0,0),(2,0), WHITE),
    ("FONTNAME",    (0,0),(2,0), "Helvetica-Bold"),
    ("FONTSIZE",    (0,0),(2,0), 9),
    ("ALIGN",       (0,0),(2,0), "CENTER"),
    ("VALIGN",      (0,0),(-1,-1), "MIDDLE"),
    ("GRID",        (0,0),(-1,-1), 0.5, GRAY_LINE),
    ("TOPPADDING",  (0,0),(-1,-1), 5),
    ("BOTTOMPADDING",(0,0),(-1,-1), 5),
    ("LEFTPADDING", (0,0),(-1,-1), 5),
    ("RIGHTPADDING",(0,0),(-1,-1), 5),
    ("ROWBACKGROUNDS", (0,1),(-1,-1), [WHITE, ROW_ALT]),
    ("ALIGN",       (0,1),(0,-1), "CENTER"),
    ("FONTNAME",    (0,1),(0,-1), "Helvetica-Bold"),
    ("FONTSIZE",    (0,1),(0,-1), 8.5),
    ("TEXTCOLOR",   (0,1),(0,-1), DARK_BLUE),
]))
story.append(tasks_tbl)
story.append(Spacer(1, 0.3*cm))

story.append(Paragraph(
    "Ces tâches m'ont exposée à une réalité opérationnelle cruciale : une grande partie "
    "des données de l'INPP reste saisie manuellement sur papier ou dans des fichiers "
    "Excel non standardisés, dispersés entre les services. Cette observation constitue "
    "le point de départ de ma réflexion pour les phases 2 et 3 du projet.", body_style))

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 6 – PERSONNES CLÉS
# ══════════════════════════════════════════════════════════════════════════════
story.append(SectionBanner("6", "Personnes Clés – Tableau des Parties Prenantes"))
story.append(Spacer(1, 0.3*cm))

stake_headers = [
    Paragraph("<b>Prénom / Titre</b>", label_style),
    Paragraph("<b>Poste / Fonction</b>", label_style),
    Paragraph("<b>Ma relation avec eux</b>", label_style),
]
stake_rows = [
    ["M. le Directeur Prov.",
     "Directeur Provincial de l'INPP Haut-Katanga",
     "Responsable hiérarchique ultime ; présente les résultats des projets IT en réunion de direction."],
    ["M. Kalombo\n(Chef SI)",
     "Chef du Service Informatique · Encadreur direct de stage",
     "Superviseur immédiat : valide mes livrables, oriente mes tâches, évalue mon travail hebdomadairement."],
    ["M. Ilunga\n(Dev Senior)",
     "Développeur senior – Cellule de Développement",
     "Mentor technique : revoit mon code, m'accompagne sur les modules complexes et les choix d'architecture."],
    ["Mme Numbi\n(RH)",
     "Responsable des Ressources Humaines",
     "Partie prenante fonctionnelle principale : exprime les besoins en numérisation des dossiers du personnel."],
    ["M. Kyungu\n(Formation)",
     "Chef du Service Formation / Technique",
     "Utilisateur final des modules que je développe ; principal fournisseur des données de formation."],
    ["Mme Tshomba\n(Recouvrement)",
     "Responsable du Service Recouvrement",
     "Interlocutrice pour l'automatisation des états de cotisations ; fournit les spécifications métier."],
]

stake_data = [stake_headers]
for i, row in enumerate(stake_rows):
    stake_data.append([
        Paragraph(f"<b>{row[0]}</b>", cell_style),
        Paragraph(row[1], cell_style),
        Paragraph(row[2], cell_style),
    ])

stake_tbl = Table(stake_data,
                  colWidths=[3.2*cm, 5.3*cm, 6.8*cm],
                  repeatRows=1)
stake_tbl.setStyle(TableStyle([
    ("BACKGROUND",  (0,0),(2,0), DARK_BLUE),
    ("TEXTCOLOR",   (0,0),(2,0), WHITE),
    ("FONTNAME",    (0,0),(2,0), "Helvetica-Bold"),
    ("FONTSIZE",    (0,0),(2,0), 9),
    ("ALIGN",       (0,0),(2,0), "CENTER"),
    ("VALIGN",      (0,0),(-1,-1), "MIDDLE"),
    ("GRID",        (0,0),(-1,-1), 0.5, GRAY_LINE),
    ("TOPPADDING",  (0,0),(-1,-1), 5),
    ("BOTTOMPADDING",(0,0),(-1,-1), 5),
    ("LEFTPADDING", (0,0),(-1,-1), 5),
    ("RIGHTPADDING",(0,0),(-1,-1), 5),
    ("ROWBACKGROUNDS", (0,1),(-1,-1), [WHITE, ROW_ALT]),
    ("BACKGROUND",  (0,2),(2,2), colors.HexColor("#fffbeb")),  # highlight supervisor
]))
story.append(stake_tbl)
story.append(Spacer(1, 0.5*cm))

# ══════════════════════════════════════════════════════════════════════════════
# RÉFLEXION PERSONNELLE
# ══════════════════════════════════════════════════════════════════════════════
story.append(SectionBanner("✦", "Réflexion Personnelle et Perspective ML"))
story.append(Spacer(1, 0.3*cm))

story.append(Paragraph(
    "Ce stage m'a offert une immersion dans le fonctionnement réel d'un établissement "
    "public congolais en pleine transition numérique. Plusieurs constats m'ont "
    "particulièrement frappée :", body_style))

reflections = [
    ("<b>Écart ambition / réalité</b>",
     "La direction affiche de fortes ambitions de digitalisation, mais au quotidien, "
     "les données restent majoritairement sur papier ou dans des tableurs non structurés. "
     "Cet écart constitue à la fois un défi et une opportunité réelle pour l'apprentissage automatique."),
    ("<b>Richesse des données potentielles</b>",
     "L'INPP génère un volume non négligeable de données : présences des stagiaires, "
     "résultats d'évaluation, historiques de cotisations, profils d'entreprises. "
     "Ces données existent mais ne sont pas encore structurées de manière exploitable."),
    ("<b>Questions encore ouvertes</b>",
     "Je ne comprends pas encore pleinement la gouvernance des données : qui est propriétaire "
     "de quelle donnée et quels services ont l'autorisation d'y accéder ? "
     "Ces questions de droits d'accès et de qualité seront centrales en Phase 2."),
]
for titre, desc in reflections:
    story.append(Paragraph(f"{titre} — {desc}", bullet_style))

story.append(Spacer(1, 0.4*cm))

# Closing note
note_tbl = Table(
    [[Paragraph(
        "📌 <b>Note pour les phases suivantes :</b> L'INPP dispose d'au moins trois sources "
        "de données numériques exploitables (base MySQL des stagiaires, fichiers Excel du "
        "Recouvrement, registres de présence). La Phase 2 vérifiera leur complétude et leur "
        "qualité pour identifier un problème d'apprentissage automatique pertinent.",
        ParagraphStyle("note", fontName="Helvetica", fontSize=9.5,
                       leading=14, textColor=DARK_BLUE))]],
    colWidths=[doc.width]
)
note_tbl.setStyle(TableStyle([
    ("BACKGROUND",  (0,0),(0,0), LIGHT_BLUE),
    ("BOX",         (0,0),(0,0), 1.5, MID_BLUE),
    ("TOPPADDING",  (0,0),(0,0), 8),
    ("BOTTOMPADDING",(0,0),(0,0), 8),
    ("LEFTPADDING", (0,0),(0,0), 10),
    ("RIGHTPADDING",(0,0),(0,0), 10),
    ("ROUNDEDCORNERS", [4]),
]))
story.append(note_tbl)

# ── Build ──────────────────────────────────────────────────────────────────────
doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
print(f"✅  PDF créé avec succès : {output}")
