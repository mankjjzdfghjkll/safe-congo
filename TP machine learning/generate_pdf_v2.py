"""
MAL1471 – Phase 1(a) – PDF final v3
Page de garde UNH + GL corrigé + organigramme amélioré
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm, mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, KeepTogether, PageBreak
)
from reportlab.platypus.flowables import Flowable

W, H = A4

# ── Couleurs ──────────────────────────────────────────────────────────────────
BLUE      = colors.HexColor("#1a5276")
MED_BLUE  = colors.HexColor("#2471a3")
LIGHT_BG  = colors.HexColor("#eaf0fb")
GRAY_LINE = colors.HexColor("#aab7c4")
ORANGE    = colors.HexColor("#e67e22")
BLACK     = colors.black
WHITE     = colors.white
HEADER_BG = colors.HexColor("#f0f4f8")

# ── Styles ────────────────────────────────────────────────────────────────────
def S(name, **kw):
    defaults = dict(fontName="Times-Roman", fontSize=11, leading=16,
                    textColor=BLACK, spaceAfter=6)
    defaults.update(kw)
    return ParagraphStyle(name, **defaults)

body    = S("body",  alignment=TA_JUSTIFY)
bold_c  = S("boldC", fontName="Times-Bold", alignment=TA_CENTER)
h1      = S("h1",    fontName="Times-Bold", fontSize=12, textColor=BLACK,
             spaceBefore=10, spaceAfter=4)
inst    = S("inst",  fontName="Helvetica-Bold", fontSize=10.5, alignment=TA_CENTER,
             textColor=BLACK, leading=16)
cell_s  = S("cell",  fontName="Times-Roman", fontSize=10, leading=14, alignment=TA_JUSTIFY)
cell_b  = S("cellB", fontName="Times-Bold",  fontSize=10, leading=14, alignment=TA_LEFT)
label_w = S("lw",    fontName="Helvetica-Bold", fontSize=9,
             alignment=TA_CENTER, textColor=WHITE)
bullet  = S("bul",   fontName="Times-Roman", fontSize=11, leading=16,
             alignment=TA_JUSTIFY, leftIndent=14, firstLineIndent=-14, spaceAfter=4)

# ── Organigramme Flowable (redessiné) ─────────────────────────────────────────
class OrgChart(Flowable):
    """
    Hiérarchie propre :
      DG Kinshasa
        └── Direction Provinciale HK
              ├── Recouvrement
              ├── Formation / Technique
              ├── RH / Logistique
              └── Service Informatique  ← MON ÉQUIPE
                      └── Cellule de Développement  ← MON POSTE
    """
    def __init__(self, width, height=7*cm):
        super().__init__()
        self.width  = width
        self.height = height

    def _box(self, c, x, y, w, h, line1, fill, line2=None, stroke_col=None):
        c.setFillColor(fill)
        c.setStrokeColor(stroke_col or fill)
        c.setLineWidth(0.8)
        c.roundRect(x, y, w, h, 5, fill=1, stroke=1)
        c.setFillColor(WHITE)
        if line2:
            c.setFont("Helvetica-Bold", 8)
            c.drawCentredString(x + w/2, y + h/2 + 3, line1)
            c.setFont("Helvetica", 7)
            c.drawCentredString(x + w/2, y + h/2 - 6, line2)
        else:
            c.setFont("Helvetica-Bold", 8.5)
            c.drawCentredString(x + w/2, y + h/2 - 3, line1)

    def _arrow_down(self, c, x, y_top, y_bot):
        """Flèche verticale vers le bas."""
        c.setStrokeColor(MED_BLUE)
        c.setLineWidth(1.3)
        c.line(x, y_top, x, y_bot + 5)
        c.setFillColor(MED_BLUE)
        p = c.beginPath()
        p.moveTo(x,   y_bot)
        p.lineTo(x-4, y_bot + 7)
        p.lineTo(x+4, y_bot + 7)
        p.close()
        c.drawPath(p, fill=1, stroke=0)

    def draw(self):
        c  = self.canv
        TW = self.width
        TH = self.height

        # ── dimensions boîtes ─────────────────────────────────────────────
        top_w  = 5.5*cm;  top_h  = 0.85*cm
        dp_w   = 6.5*cm;  dp_h   = 0.85*cm
        svc_w  = 2.9*cm;  svc_h  = 0.82*cm
        it_w   = 4.5*cm;  it_h   = 0.9*cm
        chef_w = 4.2*cm;  chef_h = 0.82*cm
        cd_w   = 4.8*cm;  cd_h   = 0.8*cm

        gap_v  = 0.52*cm
        cx     = TW / 2

        # ── Y positions (de haut en bas) ──────────────────────────────────
        y_dg   = TH - top_h - 0.1*cm
        y_dp   = y_dg   - dp_h   - gap_v
        y_svc  = y_dp   - svc_h  - gap_v
        y_it   = y_svc
        y_chef = y_it   - chef_h - gap_v
        y_cd   = y_chef - cd_h   - gap_v * 0.8

        # ── Ligne 1 : Direction Générale ──────────────────────────────────
        self._box(c, cx - top_w/2, y_dg, top_w, top_h,
                  "Direction Générale – Kinshasa", BLUE)

        # flèche DG → DP
        self._arrow_down(c, cx, y_dg, y_dp + dp_h)

        # ── Ligne 2 : Direction Provinciale ───────────────────────────────
        self._box(c, cx - dp_w/2, y_dp, dp_w, dp_h,
                  "Direction Provinciale Haut-Katanga",
                  colors.HexColor("#21618c"),
                  line2="Lubumbashi, RDC")

        # ── Trait horizontal depuis DP vers les 4 services + IT ──────────
        n_svc   = 4
        svc_gap = 0.25*cm
        block_w = n_svc * svc_w + (n_svc - 1) * svc_gap
        it_gap  = 0.5*cm
        total_w = block_w + it_gap + it_w
        x_start = cx - total_w / 2

        svc_xs = [x_start + i*(svc_w + svc_gap) for i in range(n_svc)]
        it_x   = x_start + block_w + it_gap
        it_cx  = it_x + it_w / 2

        h_y = y_dp - gap_v / 2
        c.setStrokeColor(MED_BLUE)
        c.setLineWidth(1.2)
        c.line(svc_xs[0] + svc_w/2, h_y, it_cx, h_y)
        c.line(cx, y_dp, cx, h_y)

        fill_svc = colors.HexColor("#5dade2")
        svc_labels = ["Recouvrement", "Formation /\nTechnique", "RH", "Logistique"]
        for i, sx in enumerate(svc_xs):
            sx_cx = sx + svc_w/2
            c.setStrokeColor(MED_BLUE)
            c.setLineWidth(1)
            c.line(sx_cx, h_y, sx_cx, y_svc + svc_h)
            lbl = svc_labels[i]
            if "\n" in lbl:
                l1, l2 = lbl.split("\n")
                self._box(c, sx, y_svc, svc_w, svc_h, l1, fill_svc, line2=l2)
            else:
                self._box(c, sx, y_svc, svc_w, svc_h, lbl, fill_svc)

        c.setStrokeColor(MED_BLUE)
        c.setLineWidth(1.4)
        c.line(it_cx, h_y, it_cx, y_it + it_h)

        # ── IT box ────────────────────────────────────────────────────────
        self._box(c, it_x, y_it, it_w, it_h,
                  "Service Informatique",
                  colors.HexColor("#1a5276"),
                  line2="Pool IT  ◉ MON ÉQUIPE",
                  stroke_col=ORANGE)
        c.setStrokeColor(ORANGE)
        c.setLineWidth(1.8)
        c.roundRect(it_x, y_it, it_w, it_h, 5, fill=0, stroke=1)

        # flèche IT → Chef Développement
        self._arrow_down(c, it_cx, y_it, y_chef + chef_h)

        # ── Chef Développement ────────────────────────────────────────────
        chef_x = it_cx - chef_w / 2
        self._box(c, chef_x, y_chef, chef_w, chef_h,
                  "Chef de la Cellule de Dév.",
                  colors.HexColor("#2e86c1"))

        # flèche Chef → Cellule Dev
        self._arrow_down(c, it_cx, y_chef, y_cd + cd_h)

        # ── Cellule de Développement ──────────────────────────────────────
        cd_x = it_cx - cd_w / 2
        c.setFillColor(ORANGE)
        c.setStrokeColor(ORANGE)
        c.setLineWidth(1)
        c.roundRect(cd_x, y_cd, cd_w, cd_h, 5, fill=1, stroke=1)
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 8)
        c.drawCentredString(it_cx, y_cd + cd_h/2 + 3, "Cellule de Développement")
        c.setFont("Helvetica", 7)
        c.drawCentredString(it_cx, y_cd + cd_h/2 - 6, "◉ MON POSTE")


# ─────────────────────────────────────────────────────────────────────────────
# DOCUMENT
# ─────────────────────────────────────────────────────────────────────────────
out  = r"C:\Users\PC\Desktop\TP machine learning\MANKAND-A-MUTEB_JOSEE_MAL1471_Phase1a.pdf"
LOGO = r"C:\Users\PC\Desktop\logo-unh.png"

doc = SimpleDocTemplate(
    out, pagesize=A4,
    leftMargin=2.5*cm, rightMargin=2.5*cm,
    topMargin=2*cm,    bottomMargin=2*cm,
    title="MAL1471 Phase1a", author="MANKAND-A-MUTEB JOSEE"
)

story = []

# ══════════════════════════════════════════════════════════════════════════════
# PAGE DE GARDE – style simple
# ══════════════════════════════════════════════════════════════════════════════

# Logo centré
story.append(Spacer(1, 0.5*cm))
logo_big = Image(LOGO, width=8.5*cm, height=8.5*cm, kind="proportional")
logo_tbl = Table([[logo_big]], colWidths=[doc.width])
logo_tbl.setStyle(TableStyle([("ALIGN", (0,0),(0,0), "CENTER")]))
story.append(logo_tbl)
story.append(Spacer(1, 0.5*cm))

# Institution
story.append(Paragraph("UNIVERSITÉ NOUVEAUX HORIZONS",
    S("cov1", fontName="Helvetica-Bold", fontSize=14,
      alignment=TA_CENTER, textColor=BLUE, leading=20)))
story.append(Paragraph("Faculté des Sciences Informatiques",
    S("cov2", fontName="Helvetica", fontSize=11,
      alignment=TA_CENTER, leading=17)))
story.append(Spacer(1, 1.2*cm))

# Titre
story.append(Paragraph("PROJET FINAL MAL1471 – 2026",
    S("cov4", fontName="Helvetica-Bold", fontSize=18,
      alignment=TA_CENTER, textColor=BLUE, leading=26)))
story.append(Spacer(1, 0.3*cm))
story.append(Paragraph("Phase 1(a) : Environnement du Stage",
    S("cov5", fontName="Helvetica-Bold", fontSize=13,
      alignment=TA_CENTER, leading=20)))
story.append(Spacer(1, 1.2*cm))

# Infos
story.append(Paragraph("DIRIGÉ PAR : Pr. EMMANUEL KALUNGA",
    S("ci1", fontName="Helvetica", fontSize=11, alignment=TA_CENTER, leading=20)))
story.append(Paragraph("Ass. ORTEGA-KABWE",
    S("ci2", fontName="Helvetica", fontSize=11, alignment=TA_CENTER, leading=20)))
story.append(Spacer(1, 0.6*cm))
story.append(Paragraph("FAIT PAR : MANKAND-A-MUTEB JOSEE",
    S("ci3", fontName="Helvetica-Bold", fontSize=11, alignment=TA_CENTER, leading=20)))
story.append(Paragraph("Matricule : SI/20223393",
    S("ci4", fontName="Helvetica", fontSize=11, alignment=TA_CENTER, leading=20)))
story.append(Paragraph("L4 Génie Logiciel",
    S("ci5", fontName="Helvetica", fontSize=11, alignment=TA_CENTER, leading=20)))
story.append(Spacer(1, 0.6*cm))
story.append(Paragraph("Date de remise : 27 mai 2026",
    S("ci6", fontName="Helvetica", fontSize=11, alignment=TA_CENTER, leading=20)))
story.append(Spacer(1, 0.5*cm))

# Année académique
story.append(Paragraph("Année Académique 2025-2026",
    S("cov6", fontName="Helvetica-Bold", fontSize=12,
      alignment=TA_CENTER, textColor=BLUE)))



# ── Saut de page ──────────────────────────────────────────────────────────────
story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════════════
# EN-TÊTE PETITE (pages de contenu)
# ══════════════════════════════════════════════════════════════════════════════
story.append(Paragraph("UNIVERSITÉ NOUVEAUX HORIZONS",
        S("hi1", fontName="Helvetica-Bold", fontSize=10,
            alignment=TA_CENTER, textColor=BLUE, leading=14)))
story.append(Paragraph("Faculté des Sciences Informatiques - L4 Génie Logiciel",
        S("hi2", fontName="Helvetica", fontSize=9.5,
            alignment=TA_CENTER, leading=13)))
story.append(Spacer(1, 0.2*cm))
story.append(Paragraph("PROJET FINAL MAL1471 – Phase 1(a) : Environnement du Stage",
    S("tl", fontName="Helvetica-Bold", fontSize=11,
      alignment=TA_CENTER, textColor=BLUE)))
story.append(Spacer(1, 0.5*cm))

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 – L'ORGANISATION
# ══════════════════════════════════════════════════════════════════════════════
story.append(KeepTogether([
    Paragraph("1. L'Organisation", h1),
    Spacer(1, 0.2*cm),
    Paragraph(
        "L'<b>Institut National de Préparation Professionnelle (INPP)</b> est un "
        "établissement public congolais placé sous la tutelle du Ministère de l'Emploi, "
        "du Travail et de la Prévoyance Sociale. Sa mission principale est d'assurer la "
        "<b>formation continue, le perfectionnement et la reconversion professionnelle</b> "
        "des travailleurs salariés du secteur formel en RDC.", body),
    Paragraph(
        "L'INPP opère dans le <b>secteur de la formation professionnelle</b>. "
        "En termes de taille, il dispose d'une présence <b>nationale</b> : une "
        "Direction Générale à Kinshasa, des Directions Provinciales dans les principales "
        "provinces du pays, et des antennes locales dans plusieurs villes. "
        "La <b>Direction Provinciale du Haut-Katanga</b>, où j'effectue mon stage, "
        "est implantée à Lubumbashi.", body),
    Paragraph(
        "Le financement repose sur des <b>cotisations patronales obligatoires</b> "
        "allant de 0,5 % à 3 % de la masse salariale brute des entreprises, "
        "ce qui lui confère une relative autonomie financière ancrée dans le tissu "
        "économique local (secteur minier, sous-traitance).", body),
]))

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 – MISSION ET STRATÉGIE
# ══════════════════════════════════════════════════════════════════════════════
story.append(KeepTogether([
    Paragraph("2. Mission et Stratégie (observée)", h1),
    Spacer(1, 0.2*cm),
    Paragraph(
        "À travers les réunions d'équipe et les échanges quotidiens, j'ai pu observer "
        "que l'INPP Haut-Katanga poursuit trois priorités stratégiques concrètes :", body),
    Paragraph(
        "→ <b>Adapter les formations aux besoins réels des entreprises</b> de la région, "
        "notamment dans les secteurs minier et de la sous-traitance.",  bullet),
    Paragraph(
        "→ <b>Moderniser et digitaliser les processus internes</b> : gestion des "
        "stagiaires, suivi des cotisations, production de rapports.", bullet),
    Paragraph(
        "→ <b>Renforcer la qualité via des partenariats internationaux</b>, notamment "
        "avec la JICA (Agence Japonaise de Coopération Internationale), régulièrement "
        "mentionnée en réunion comme levier d'innovation.", bullet),
]))

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3 – STRUCTURE ET ORGANIGRAMME
# ══════════════════════════════════════════════════════════════════════════════
story.append(Paragraph("3. Structure et Organigramme", h1))
story.append(Spacer(1, 0.2*cm))
story.append(Paragraph(
    "La Direction Provinciale du Haut-Katanga est organisée autour des services suivants :", body))

srv_data = [
    [Paragraph("<b>Service</b>", label_w),
     Paragraph("<b>Rôle principal</b>", label_w)],
    ["Direction Provinciale",    "Pilotage stratégique et représentation institutionnelle"],
    ["Recouvrement",             "Collecte et contrôle des cotisations patronales"],
    ["Formation / Technique",    "Conception et délivrance des programmes de formation"],
    ["Ressources Humaines",      "Gestion du personnel et des évaluations"],
    ["Logistique",               "Gestion du matériel et des locaux"],
    ["Informatique (Pool IT)",   "Maintenance, numérisation et développement applicatif  ← MON SERVICE"],
]
srv_rows = [srv_data[0]]
for i, r in enumerate(srv_data[1:]):
    srv_rows.append([
        Paragraph(f"<b>{r[0]}</b>" if i == 5 else r[0], cell_s),
        Paragraph(r[1], cell_s)
    ])

srv_tbl = Table(srv_rows, colWidths=[4.5*cm, doc.width - 4.5*cm], repeatRows=1)
srv_tbl.setStyle(TableStyle([
    ("BACKGROUND",  (0,0),(1,0), colors.HexColor("#aed6f1")),
    ("FONTNAME",    (0,0),(1,0), "Helvetica-Bold"),
    ("FONTSIZE",    (0,0),(1,0), 9),
    ("ALIGN",       (0,0),(1,0), "CENTER"),
    ("TEXTCOLOR",   (0,0),(1,0), BLUE),
    ("ROWBACKGROUNDS",(0,1),(-1,-1), [WHITE, colors.HexColor("#f0f7ff")]),
    ("BACKGROUND",  (0,6),(1,6), colors.HexColor("#d6eaf8")),
    ("GRID",        (0,0),(-1,-1), 0.5, GRAY_LINE),
    ("VALIGN",      (0,0),(-1,-1), "MIDDLE"),
    ("TOPPADDING",  (0,0),(-1,-1), 4),
    ("BOTTOMPADDING",(0,0),(-1,-1), 4),
    ("LEFTPADDING", (0,0),(-1,-1), 6),
]))
story.append(srv_tbl)
story.append(Spacer(1, 0.4*cm))

story.append(Paragraph(
    "<b>Organigramme simplifié – positionnement de mon équipe :</b>",
    S("oc", fontName="Times-Bold", fontSize=10, alignment=TA_CENTER,
      textColor=BLUE, spaceAfter=4)))
story.append(OrgChart(width=doc.width, height=9.5*cm))
story.append(Spacer(1, 0.3*cm))

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4 – MON STAGE ET MON ÉQUIPE
# ══════════════════════════════════════════════════════════════════════════════
story.append(KeepTogether([
    Paragraph("4. Mon Stage et Mon Équipe", h1),
    Spacer(1, 0.2*cm),
    Paragraph(
        "J'effectue mon stage au sein du <b>Pool Informatique / Cellule de Développement</b> "
        "de l'INPP Haut-Katanga. Cette cellule compte environ six collaborateurs "
        "(développeurs, techniciens réseau et administrateurs systèmes). "
        "Elle est rattachée directement au <b>Service Informatique</b>, lui-même sous "
        "l'autorité du Chef de Service qui rend compte au Directeur Provincial.", body),
    Paragraph(
        "Le Pool IT collabore de manière transversale avec tous les services de la "
        "Direction Provinciale : il digitalise les dossiers du service Formation, "
        "automatise les états du service Recouvrement et assure le support technique "
        "quotidien de l'ensemble du personnel.", body),
]))

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 5 – MON RÔLE
# ══════════════════════════════════════════════════════════════════════════════
story.append(KeepTogether([
    Paragraph("5. Mon Rôle et Mes Responsabilités", h1),
    Spacer(1, 0.2*cm),
    Paragraph(
        "Mon titre de poste est <b>Stagiaire Développeuse</b> au sein de la Cellule de "
        "Développement. Mes tâches régulières comprennent :", body),
    Paragraph(
        "→ <b>Développement d'un module de gestion des stagiaires</b> : enregistrement, "
        "suivi des présences et génération automatique d'attestations. "
        "<i>Outils : PHP, HTML/CSS, MySQL, XAMPP.</i>", bullet),
    Paragraph(
        "→ <b>Administration de la base de données</b> : mise à jour et maintenance de la "
        "base centralisant les inscriptions, résultats d'évaluation et fiches "
        "d'entreprises partenaires. <i>Outil : MySQL via XAMPP.</i>", bullet),
    Paragraph(
        "→ <b>Conception et modélisation</b> : élaboration des diagrammes de cas "
        "d'usage et de classes pour les modules développés. "
        "<i>Outil : StarUML.</i>", bullet),
    Paragraph(
        "→ <b>Support technique</b> : assistance aux agents des autres services pour "
        "l'utilisation des outils informatiques ; rédaction de guides utilisateurs.", bullet),
    Spacer(1, 0.15*cm),
    Paragraph(
        "Ces tâches m'ont permis de constater que la majorité des données de l'INPP "
        "restent encore saisies manuellement ou dans des fichiers Excel non structurés, "
        "ce qui constitue un enjeu majeur pour les phases suivantes du projet.", body),
]))

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 6 – PERSONNES CLÉS
# ══════════════════════════════════════════════════════════════════════════════
story.append(Paragraph("6. Personnes Clés – Tableau des Parties Prenantes", h1))
story.append(Spacer(1, 0.2*cm))

st_data = [
    [Paragraph("<b>Titre / Prénom</b>", label_w),
     Paragraph("<b>Poste / Fonction</b>", label_w),
     Paragraph("<b>Relation avec moi</b>", label_w)],
    [Paragraph("<b>Directeur Provincial</b>", cell_b),
     Paragraph("Directeur de la Direction Provinciale Haut-Katanga", cell_s),
     Paragraph("Responsable hiérarchique ultime ; reçoit les résultats des projets IT.", cell_s)],
    [Paragraph("<b>Chef du Service Informatique</b>", cell_b),
     Paragraph("Responsable du Pool IT · Encadreur direct de stage", cell_s),
     Paragraph("Superviseur immédiat : valide mes livrables et oriente mes tâches.", cell_s)],
    [Paragraph("<b>Référent Technique</b>", cell_b),
     Paragraph("Développeur senior – Cellule de Développement", cell_s),
     Paragraph("Mentor technique : accompagne mon travail de codage au quotidien.", cell_s)],
    [Paragraph("<b>Chef du Service\nFormation</b>", cell_b),
     Paragraph("Responsable du Service Formation / Technique", cell_s),
     Paragraph("Utilisateur final principal des modules que je développe ; fournit les données.", cell_s)],
    [Paragraph("<b>Responsable RH</b>", cell_b),
     Paragraph("Responsable des Ressources Humaines", cell_s),
     Paragraph("Exprime les besoins en numérisation des dossiers du personnel.", cell_s)],
]

st_widths = [3.8*cm, 5.5*cm, doc.width - 3.8*cm - 5.5*cm]
st_tbl = Table(st_data, colWidths=st_widths, repeatRows=1)
st_tbl.setStyle(TableStyle([
    ("BACKGROUND",  (0,0),(2,0), colors.HexColor("#aed6f1")),
    ("TEXTCOLOR",   (0,0),(2,0), BLUE),
    ("FONTNAME",    (0,0),(2,0), "Helvetica-Bold"),
    ("FONTSIZE",    (0,0),(2,0), 9),
    ("ALIGN",       (0,0),(2,0), "CENTER"),
    ("ROWBACKGROUNDS",(0,1),(-1,-1), [WHITE, colors.HexColor("#f0f7ff")]),
    ("GRID",        (0,0),(-1,-1), 0.5, GRAY_LINE),
    ("VALIGN",      (0,0),(-1,-1), "MIDDLE"),
    ("TOPPADDING",  (0,0),(-1,-1), 4),
    ("BOTTOMPADDING",(0,0),(-1,-1), 4),
    ("LEFTPADDING", (0,0),(-1,-1), 5),
]))
story.append(st_tbl)
story.append(Spacer(1, 0.5*cm))

# ── Réflexion personnelle ──────────────────────────────────────────────────────
story.append(Paragraph(
    "<b>Réflexion personnelle :</b> Ce stage m'a permis de comprendre le fonctionnement "
    "réel d'un établissement public en transition numérique. J'ai observé un écart "
    "important entre les ambitions de digitalisation affichées et la réalité des "
    "pratiques (saisies papier, Excel non structurés). L'INPP génère pourtant un volume "
    "non négligeable de données (présences des stagiaires, résultats d'évaluation, "
    "historiques de cotisations) qui ne sont pas encore exploitées de manière structurée. "
    "Je ne maîtrise pas encore totalement la gouvernance de ces données : qui en est "
    "propriétaire, qui y a accès ? Ces questions seront au cœur de la Phase 2.",
    body))

# ── Numérotation des pages (pages de contenu seulement) ───────────────────────
def page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 9)
    canvas.setFillColor(GRAY_LINE)
    canvas.drawCentredString(doc.pagesize[0] / 2,
                             doc.bottomMargin - 0.8*cm,
                             f"{doc.page}")
    canvas.restoreState()

doc.build(story, onFirstPage=lambda c, d: None, onLaterPages=page_number)
print(f"✅  PDF créé : {out}")
