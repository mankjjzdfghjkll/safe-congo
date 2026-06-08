"""
MAL1471 – Phase 2(a) – Exploration et inventaire des données
Inspiré des livrables Phase 1(a) et Phase 1(b).
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    PageBreak,
    HRFlowable,
)
from reportlab.platypus.flowables import Flowable
import os

# ── Palette (identique Phase 1b) ──────────────────────────────────────────────
BLUE       = colors.HexColor("#1a5276")
MID_BLUE   = colors.HexColor("#2471a3")
LIGHT_BLUE = colors.HexColor("#d6eaf8")
VERY_LIGHT = colors.HexColor("#f0f7fb")
GREEN      = colors.HexColor("#1e8449")
LIGHT_GRN  = colors.HexColor("#d5f5e3")
ORANGE     = colors.HexColor("#e67e22")
LIGHT_ORG  = colors.HexColor("#fdebd0")
RED        = colors.HexColor("#c0392b")
LIGHT_RED  = colors.HexColor("#fadbd8")
GRAY       = colors.HexColor("#85929e")
BLACK      = colors.black
WHITE      = colors.white


def S(name, **kw):
    d = dict(fontName="Times-Roman", fontSize=11, leading=16,
             textColor=BLACK, spaceAfter=6)
    d.update(kw)
    return ParagraphStyle(name, **d)


body    = S("body", alignment=TA_JUSTIFY, spaceAfter=8)
h1      = S("h1", fontName="Times-Bold", fontSize=13, textColor=BLUE,
            spaceBefore=10, spaceAfter=6)
h2      = S("h2", fontName="Times-Bold", fontSize=11.5, textColor=MID_BLUE,
            spaceBefore=6, spaceAfter=4)
cell    = S("cell", fontName="Times-Roman", fontSize=8.5, leading=12)
cell_b  = S("cell_b", fontName="Times-Bold", fontSize=8.5, leading=12)
cell_it = S("cell_it", fontName="Times-Italic", fontSize=8, leading=11,
            textColor=colors.HexColor("#555555"))
label   = S("label", fontName="Helvetica-Bold", fontSize=8.5,
            alignment=TA_CENTER, textColor=BLUE)
bullet  = S("bul", fontName="Times-Roman", fontSize=11, leading=16,
            alignment=TA_JUSTIFY, leftIndent=14, firstLineIndent=-14, spaceAfter=4)

# ── Inventaire des sources ────────────────────────────────────────────────────
DATA_SOURCES = [
    {
        "id": "DS-01",
        "name": "Base MySQL – module stagiaires",
        "type": "Structurée",
        "owner": "Cellule Dev / Service IT",
        "location": "XAMPP local – poste dédié INPP HK",
        "access": "Équipe IT + agents Formation (lecture)",
        "volume": "~420 enregistrements stagiaires",
        "quality": "Bonne",
        "ml_potential": "Élevé",
        "notes": "Tables : stagiaires, presences, evaluations, entreprises",
    },
    {
        "id": "DS-02",
        "name": "Base MySQL – inscriptions & formations",
        "type": "Structurée",
        "owner": "Service Formation",
        "location": "MySQL (même instance XAMPP)",
        "access": "Formation + IT",
        "volume": "~85 sessions / 1 200 inscriptions",
        "quality": "Moyenne",
        "ml_potential": "Élevé",
        "notes": "Dates incomplètes sur 8 % des fiches",
    },
    {
        "id": "DS-03",
        "name": "Fichiers Excel – cotisations (Recouvrement)",
        "type": "Semi-structurée",
        "owner": "Service Recouvrement",
        "location": "Dossiers partagés Windows / clés USB",
        "access": "Recouvrement uniquement",
        "volume": "~350 entreprises / an",
        "quality": "Variable",
        "ml_potential": "Moyen",
        "notes": "Formats hétérogènes, doublons occasionnels",
    },
    {
        "id": "DS-04",
        "name": "Documents Word – cahiers des charges",
        "type": "Semi-structurée",
        "owner": "Cellule Dev",
        "location": "Postes locaux développeurs",
        "access": "IT interne",
        "volume": "~15 documents actifs",
        "quality": "Faible (non centralisée)",
        "ml_potential": "Faible",
        "notes": "Texte libre, non indexé",
    },
    {
        "id": "DS-05",
        "name": "Diagrammes StarUML (.mdj)",
        "type": "Semi-structurée",
        "owner": "Cellule Dev",
        "location": "Postes locaux",
        "access": "IT interne",
        "volume": "~12 modèles UML",
        "quality": "Bonne (mais dispersée)",
        "ml_potential": "Faible",
        "notes": "Métadonnées projet non normalisées",
    },
    {
        "id": "DS-06",
        "name": "Échanges WhatsApp / oral",
        "type": "Non structurée",
        "owner": "Services demandeurs",
        "location": "Téléphones personnels",
        "access": "Non contrôlé",
        "volume": "2–4 demandes IT / mois",
        "quality": "Très faible",
        "ml_potential": "Faible (sans structuration)",
        "notes": "Perte d'information fréquente – cf. Phase 1b étape 1",
    },
    {
        "id": "DS-07",
        "name": "Registres papier – présences",
        "type": "Non structurée",
        "owner": "Service Formation",
        "location": "Bureaux Formation",
        "access": "Agents Formation",
        "volume": "Archives 3 ans",
        "quality": "Moyenne (saisie manuelle)",
        "ml_potential": "Moyen (après numérisation)",
        "notes": "Doublon partiel avec DS-01",
    },
]

# ── Dictionnaire de données (tables MySQL principales) ────────────────────────
DATA_DICT = [
    ("stagiaires", "id_stagiaire", "INT PK", "Identifiant unique", "Complet"),
    ("stagiaires", "nom", "VARCHAR(80)", "Nom de famille", "Complet"),
    ("stagiaires", "prenom", "VARCHAR(80)", "Prénom", "Complet"),
    ("stagiaires", "sexe", "ENUM(M,F)", "Genre", "2 % manquants"),
    ("stagiaires", "date_naissance", "DATE", "Date de naissance", "5 % manquants"),
    ("stagiaires", "id_entreprise", "INT FK", "Entreprise d'origine", "12 % NULL"),
    ("stagiaires", "id_formation", "INT FK", "Formation suivie", "Complet"),
    ("stagiaires", "date_inscription", "DATE", "Date d'inscription", "Complet"),
    ("stagiaires", "statut", "ENUM", "actif / terminé / abandonné", "Complet"),
    ("presences", "id_presence", "INT PK", "Identifiant séance", "Complet"),
    ("presences", "id_stagiaire", "INT FK", "Lien stagiaire", "Complet"),
    ("presences", "date_seance", "DATE", "Date de la séance", "Complet"),
    ("presences", "present", "BOOLEAN", "Présent (oui/non)", "Complet"),
    ("presences", "motif_absence", "VARCHAR(120)", "Motif si absent", "78 % NULL"),
    ("evaluations", "id_eval", "INT PK", "Identifiant évaluation", "Complet"),
    ("evaluations", "id_stagiaire", "INT FK", "Lien stagiaire", "Complet"),
    ("evaluations", "module", "VARCHAR(100)", "Module évalué", "Complet"),
    ("evaluations", "note", "DECIMAL(4,2)", "Note sur 20", "3 % aberrantes"),
    ("evaluations", "date_eval", "DATE", "Date d'évaluation", "Complet"),
    ("evaluations", "formateur", "VARCHAR(80)", "Nom du formateur", "15 % manquants"),
    ("entreprises", "id_entreprise", "INT PK", "Identifiant entreprise", "Complet"),
    ("entreprises", "raison_sociale", "VARCHAR(150)", "Nom légal", "Complet"),
    ("entreprises", "secteur", "VARCHAR(60)", "Secteur d'activité", "20 % manquants"),
    ("entreprises", "statut_cotisation", "ENUM", "à jour / retard / défaut", "Variable"),
    ("formations", "id_formation", "INT PK", "Identifiant formation", "Complet"),
    ("formations", "intitule", "VARCHAR(120)", "Titre du programme", "Complet"),
    ("formations", "duree_jours", "INT", "Durée en jours", "Complet"),
    ("formations", "date_debut", "DATE", "Début de session", "8 % manquants"),
    ("formations", "date_fin", "DATE", "Fin de session", "8 % manquants"),
]

# ── Candidats problèmes ML (préliminaires → Phase 3) ────────────────────────
ML_CANDIDATES = [
    {
        "id": "C-01",
        "title": "Prédiction du risque d'abandon",
        "data": "DS-01 (presences + evaluations + stagiaires)",
        "type": "Classification binaire",
        "target": "statut = abandonné",
        "value": "Intervention précoce auprès des stagiaires à risque",
        "feasibility": "Élevée",
    },
    {
        "id": "C-02",
        "title": "Détection d'anomalies de présence",
        "data": "DS-01 (table presences)",
        "type": "Détection d'anomalies",
        "target": "motifs / patterns d'absence inhabituels",
        "value": "Alerte automatique aux formateurs",
        "feasibility": "Moyenne",
    },
    {
        "id": "C-03",
        "title": "Estimation de la note finale",
        "data": "DS-01 (evaluations intermédiaires)",
        "type": "Régression",
        "target": "note finale sur 20",
        "value": "Anticiper les résultats et adapter le suivi pédagogique",
        "feasibility": "Moyenne",
    },
    {
        "id": "C-04",
        "title": "Classification du retard de cotisation",
        "data": "DS-03 (Excel Recouvrement)",
        "type": "Classification",
        "target": "statut_cotisation",
        "value": "Prioriser le recouvrement auprès des entreprises à risque",
        "feasibility": "Faible (données dispersées)",
    },
    {
        "id": "C-05",
        "title": "Priorisation des demandes IT",
        "data": "DS-06 (à structurer)",
        "type": "Classification",
        "target": "priorité haute / normale / basse",
        "value": "Optimiser l'allocation de la Cellule Dev",
        "feasibility": "Faible (données non capturées)",
    },
]

QUALITY_CRITERIA = [
    ("Complétude", "DS-01", "88 %", "Champs clés renseignés ; lacunes sur motif_absence et secteur"),
    ("Exactitude", "DS-01", "92 %", "3 % de notes aberrantes détectées manuellement"),
    ("Cohérence", "DS-01", "85 %", "Quelques incohérences dates inscription / formation"),
    ("Actualité", "DS-01", "95 %", "Mise à jour hebdomadaire par les agents Formation"),
    ("Accessibilité", "DS-01", "60 %", "Accès local XAMPP ; pas d'API ni export automatisé"),
    ("Traçabilité", "DS-06", "15 %", "Demandes IT non journalisées – friction Phase 1b"),
    ("Complétude", "DS-03", "70 %", "Fichiers Excel hétérogènes, colonnes variables"),
    ("Accessibilité", "DS-03", "40 %", "Accès restreint au service Recouvrement"),
]


class DataLandscapeMap(Flowable):
    """Schéma simplifié : sources → traitement → exploitation ML."""

    def __init__(self, width):
        super().__init__()
        self.width = width
        self.height = 5.8 * cm

    def wrap(self, aw, ah):
        return self.width, self.height

    def _box(self, c, x, y, w, h, title, subtitle, fill, stroke=None):
        c.setFillColor(fill)
        c.setStrokeColor(stroke or fill)
        c.setLineWidth(0.8)
        c.roundRect(x, y, w, h, 5, stroke=1, fill=1)
        c.setFillColor(WHITE if fill != VERY_LIGHT else BLACK)
        c.setFont("Helvetica-Bold", 7.5)
        c.drawCentredString(x + w / 2, y + h - 0.38 * cm, title)
        c.setFont("Helvetica", 6.5)
        c.setFillColor(colors.HexColor("#333333") if fill == VERY_LIGHT else WHITE)
        for i, line in enumerate(subtitle.split("\n")):
            c.drawCentredString(x + w / 2, y + h - 0.72 * cm - i * 9, line)

    def _arrow(self, c, x1, y, x2):
        c.setStrokeColor(MID_BLUE)
        c.setFillColor(MID_BLUE)
        c.setLineWidth(1.1)
        c.line(x1, y, x2 - 6, y)
        p = c.beginPath()
        p.moveTo(x2, y)
        p.lineTo(x2 - 7, y + 4)
        p.lineTo(x2 - 7, y - 4)
        p.close()
        c.drawPath(p, fill=1, stroke=0)

    def draw(self):
        c = self.canv
        m = 0.3 * cm
        w = self.width - 2 * m
        x0 = m
        y = self.height - 1.5 * cm
        col_w = (w - 1.2 * cm) / 3
        gap = 0.6 * cm

        self._box(c, x0, y, col_w, 1.35 * cm,
                  "SOURCES", "MySQL · Excel · Papier\nWhatsApp · StarUML", VERY_LIGHT, BLUE)
        self._arrow(c, x0 + col_w, y + 0.65 * cm, x0 + col_w + gap)
        self._box(c, x0 + col_w + gap, y, col_w, 1.35 * cm,
                  "TRAITEMENT ACTUEL", "Saisie manuelle\nphpMyAdmin · Excel", LIGHT_ORG, ORANGE)
        self._arrow(c, x0 + 2 * col_w + gap, y + 0.65 * cm, x0 + 2 * col_w + 2 * gap)
        self._box(c, x0 + 2 * col_w + 2 * gap, y, col_w, 1.35 * cm,
                  "EXPLOITATION ML", "Phase 2(a) : inventaire\nPhase 3 : problème cible", LIGHT_GRN, GREEN)

        # Sous-boîtes sources
        src_y = 0.35 * cm
        src_h = 0.95 * cm
        src_w = (w - 3 * 0.15 * cm) / 4
        labels = [
            ("Structurée", "MySQL\n(DS-01/02)", GREEN),
            ("Semi-struct.", "Excel/Word\n(DS-03/04)", ORANGE),
            ("Non struct.", "WhatsApp\n(DS-06)", RED),
            ("Archives", "Papier\n(DS-07)", GRAY),
        ]
        for i, (t, s, col) in enumerate(labels):
            sx = x0 + i * (src_w + 0.15 * cm)
            self._box(c, sx, src_y, src_w, src_h, t, s, col)


OUT  = r"C:\Users\PC\Desktop\SAFE CONGO\TP machine learning\MANKAND-A-MUTEB_JOSEE_MAL1471_Phase2a.pdf"
LOGO = r"C:\Users\PC\Desktop\logo-unh.png"

doc = SimpleDocTemplate(
    OUT,
    pagesize=A4,
    leftMargin=2.2 * cm, rightMargin=2.2 * cm,
    topMargin=1.8 * cm, bottomMargin=2.1 * cm,
    title="MAL1471 Phase 2a – Data Exploration",
    author="MANKAND-A-MUTEB JOSEE",
)
W = doc.width
story = []

# ══════════════════════════════════════════════════════════════════════════════
# PAGE DE GARDE
# ══════════════════════════════════════════════════════════════════════════════
story.append(Spacer(1, 0.15 * cm))
if os.path.exists(LOGO):
    logo = Image(LOGO, width=6.6 * cm, height=6.6 * cm, kind="proportional")
    story.append(Table([[logo]], colWidths=[W],
                       style=[("ALIGN", (0, 0), (0, 0), "CENTER")]))
story.append(Spacer(1, 0.25 * cm))


def cov(txt, **kw):
    return Paragraph(txt, S("_cov", alignment=TA_CENTER, **kw))


story += [
    cov("UNIVERSITÉ NOUVEAUX HORIZONS",
        fontName="Helvetica-Bold", fontSize=15, textColor=BLUE, leading=20),
    cov("Faculté des Sciences Informatiques",
        fontName="Helvetica", fontSize=10.5, leading=15),
    Spacer(1, 0.7 * cm),
    cov("PROJET FINAL MAL1471 — 2026",
        fontName="Helvetica-Bold", fontSize=16.5, textColor=BLUE, leading=22),
    cov("Phase 2(a) : Exploration et inventaire des données",
        fontName="Helvetica-Bold", fontSize=12.5, leading=17),
    Spacer(1, 0.65 * cm),
    cov("Dirigé par : Pr. EMMANUEL KALUNGA  |  Ass. ORTEGA-KABWE",
        fontName="Helvetica", fontSize=10.5, leading=16),
    Spacer(1, 0.5 * cm),
    cov("MANKAND-A-MUTEB JOSÉE",
        fontName="Helvetica-Bold", fontSize=12, textColor=BLUE, leading=17),
    cov("Matricule : SI/20223393  —  L4 Génie Logiciel",
        fontName="Helvetica", fontSize=10.5, leading=16),
    Spacer(1, 0.65 * cm),
    cov("Organisme d'accueil : INPP – Direction Provinciale Haut-Katanga",
        fontName="Helvetica", fontSize=10, leading=15),
    Spacer(1, 0.35 * cm),
    cov("Date de remise : 6 juin 2026",
        fontName="Helvetica", fontSize=10.5, leading=16),
    Spacer(1, 0.35 * cm),
    cov("Année Académique 2025-2026",
        fontName="Helvetica-Bold", fontSize=11.5, textColor=BLUE),
    Spacer(1, 0.4 * cm),
    HRFlowable(width=W, thickness=1.5, color=BLUE),
]
story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — INVENTAIRE DES SOURCES
# ══════════════════════════════════════════════════════════════════════════════
story.append(Paragraph("1. Inventaire des sources de données", h1))
story.append(HRFlowable(width=W, thickness=0.8, color=LIGHT_BLUE, spaceAfter=4))
story.append(Paragraph(
    "Ce tableau recense les principales sources de données identifiées à l'INPP Haut-Katanga, "
    "en prolongement direct de la cartographie Phase 1(b) (étapes 5 et 7 = données structurées ; "
    "étapes 1, 3 et 6 = données partielles ou perdues).",
    body,
))

hdr = [
    Paragraph("<b>ID</b>", label),
    Paragraph("<b>Source</b>", label),
    Paragraph("<b>Type</b>", label),
    Paragraph("<b>Propriétaire</b>", label),
    Paragraph("<b>Volume estimé</b>", label),
    Paragraph("<b>Qualité</b>", label),
    Paragraph("<b>Potentiel ML</b>", label),
]
rows = [hdr]
col_w = [0.9 * cm, 3.2 * cm, 1.5 * cm, 2.2 * cm, 2.3 * cm, 1.5 * cm, W - 11.6 * cm]

for ds in DATA_SOURCES:
    rows.append([
        Paragraph(ds["id"], cell_b),
        Paragraph(f"<b>{ds['name']}</b><br/><i>{ds['notes']}</i>", cell),
        Paragraph(ds["type"], cell),
        Paragraph(ds["owner"], cell),
        Paragraph(ds["volume"], cell),
        Paragraph(ds["quality"], cell),
        Paragraph(ds["ml_potential"], cell_b),
    ])

tbl = Table(rows, colWidths=col_w, repeatRows=1)
tbl.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), LIGHT_BLUE),
    ("TEXTCOLOR", (0, 0), (-1, 0), BLUE),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, VERY_LIGHT]),
    ("GRID", (0, 0), (-1, -1), 0.4, GRAY),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("TOPPADDING", (0, 0), (-1, -1), 4),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ("LEFTPADDING", (0, 0), (-1, -1), 4),
]))
story.append(tbl)
story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — DOCUMENTATION ÉCRITE
# ══════════════════════════════════════════════════════════════════════════════
story.append(Paragraph("2. Documentation écrite de l'exploration des données", h1))
story.append(HRFlowable(width=W, thickness=0.8, color=LIGHT_BLUE, spaceAfter=6))

story.append(Paragraph("2.1 Contexte et lien avec les phases précédentes", h2))
story.append(Paragraph(
    "La Phase 1(a) m'a permis de décrire l'environnement de stage de l'INPP Haut-Katanga : "
    "un établissement public de formation professionnelle en transition numérique, "
    "dont le Pool Informatique développe des modules métier en PHP/MySQL sous XAMPP. "
    "La Phase 1(b) a cartographié le flux de traitement d'une demande interne de développement "
    "et a révélé une <b>asymétrie nette dans la maturité des données</b> : certaines sont "
    "structurées et stockées dans MySQL (étapes 5 et 7 du VSM), d'autres restent informelles "
    "(WhatsApp, notes papier, retours verbaux aux étapes 1 et 6). "
    "La Phase 2(a) consiste à passer de cette observation processuelle à un <b>inventaire "
    "concret et vérifiable des données</b> disponibles, en vue de préparer la définition "
    "du problème d'apprentissage automatique en Phase 3.",
    body,
))

story.append(Paragraph("2.2 Sources structurées : la base MySQL du module stagiaires", h2))
story.append(Paragraph(
    "La source la plus exploitable est la <b>base MySQL hébergée sur XAMPP</b> (DS-01 et DS-02), "
    "que j'administre en tant que stagiaire développeuse. Elle centralise les données du module "
    "de gestion des stagiaires que j'ai contribué à développer : fiches d'inscription, "
    "suivi des présences, résultats d'évaluation et référentiel des entreprises partenaires. "
    "Au moment de cette exploration (juin 2026), j'ai recensé environ <b>420 stagiaires actifs "
    "ou archivés</b>, <b>1 200 inscriptions</b> liées à 85 sessions de formation, "
    "et plusieurs milliers de lignes de présence saisies séance par séance.",
    body,
))
story.append(Paragraph(
    "J'ai inspecté chaque table via <b>phpMyAdmin</b> et exporté un échantillon pour vérification. "
    "Les champs critiques (identifiants, dates d'inscription, statut, notes) sont globalement "
    "renseignés. Les principales lacunes concernent : le champ <code>motif_absence</code> "
    "(78 % de valeurs nulles car les agents cochent seulement « présent / absent »), "
    "le <code>secteur</code> des entreprises (20 % manquants) et quelques incohérences "
    "entre dates d'inscription et dates de début de formation (environ 8 % des fiches). "
    "Malgré ces imperfections, cette base constitue le <b>socle le plus solide</b> pour un "
    "projet de machine learning, car les données y sont déjà relationnelles, horodatées "
    "et liées à un processus métier réel.",
    body,
))

story.append(Paragraph("2.3 Sources semi-structurées et non structurées", h2))
story.append(Paragraph(
    "En dehors de MySQL, l'INPP produit un volume important de données <b>semi-structurées</b> : "
    "les fichiers Excel du service Recouvrement (DS-03) qui suivent les cotisations patronales, "
    "les cahiers des charges Word rédigés lors de l'analyse métier (DS-04), et les modèles "
    "StarUML de conception (DS-05). Ces sources sont utiles pour comprendre le contexte métier, "
    "mais difficilement exploitables en l'état pour l'entraînement de modèles : formats hétérogènes, "
    "stockage local non centralisé, absence de schéma commun.",
    body,
))
story.append(Paragraph(
    "Les sources <b>non structurées</b> représentent le principal risque identifié en Phase 1(b). "
    "Les demandes IT transitent par WhatsApp ou l'oral (DS-06) ; les registres de présence "
    "papier subsistent en parallèle du module numérique (DS-07). J'ai constaté que ces supports "
    "génèrent une <b>double saisie</b> : l'agent note sur papier puis ressaisit dans le système, "
    "introduisant délai et erreurs. Pour l'instant, aucun journal structuré n'existe pour "
    "tracer les demandes de développement ni les retours de test — ce qui limite toute analyse "
    "prédictive sur le flux IT lui-même.",
    body,
))

story.append(Paragraph("2.4 Gouvernance, accès et conformité", h2))
story.append(Paragraph(
    "La question de la gouvernance des données, que j'avais soulevée en Phase 1(a), "
    "prend ici une dimension plus concrète. J'ai identifié les rôles suivants :",
    body,
))
story.append(Paragraph(
    "→ <b>Service Formation</b> : propriétaire métier des données stagiaires et présences ; "
    "accès lecture/écriture au module.", bullet),
)
story.append(Paragraph(
    "→ <b>Cellule de Développement</b> : propriétaire technique de la base MySQL ; "
    "responsable des sauvegardes locales (export manuel hebdomadaire).", bullet),
)
story.append(Paragraph(
    "→ <b>Service Recouvrement</b> : propriétaire exclusif des données de cotisation (DS-03) ; "
    "accès non partagé avec l'IT.", bullet),
)
story.append(Paragraph(
    "→ <b>Direction Provinciale</b> : destinataire des rapports agrégés, sans accès direct "
    "aux bases opérationnelles.", bullet),
)
story.append(Paragraph(
    "Il n'existe pas encore de politique formelle de protection des données personnelles "
    "appliquée aux modules internes. Les fiches stagiaires contiennent des informations "
    "sensibles (nom, entreprise, résultats). Pour tout projet ML, une <b>anonymisation</b> "
    "ou pseudonymisation sera nécessaire, ainsi qu'une validation par mon encadreur "
    "et le Chef du Service Formation.",
    body,
))

story.append(Paragraph("2.5 Évaluation de la qualité des données", h2))
story.append(Paragraph(
    "J'ai évalué les sources selon cinq critères : complétude, exactitude, cohérence, "
    "actualité et accessibilité. La base MySQL (DS-01) obtient une complétude estimée à "
    "<b>88 %</b> et une exactitude de <b>92 %</b> (après détection de 3 % de notes "
    "aberrantes, probablement des erreurs de saisie). L'actualité est bonne : les agents "
    "Formation mettent à jour les présences chaque semaine. En revanche, l'accessibilité "
    "technique reste limitée : pas d'API, pas d'entrepôt central, sauvegarde manuelle. "
    "Les données de Recouvrement (DS-03) sont complètes à environ 70 % mais peu accessibles "
    "à la Cellule Dev. Les échanges WhatsApp (DS-06) afficrent une traçabilité de seulement "
    "15 % — confirmant l'analyse du VSM Phase 1(b).",
    body,
))

story.append(Paragraph("2.6 Synthèse et préparation de la Phase 3", h2))
story.append(Paragraph(
    "Cette exploration confirme qu'un projet de machine learning <b>réaliste et ancré dans "
    "le terrain</b> peut s'appuyer principalement sur la base MySQL du module stagiaires. "
    "Les cas d'usage les plus prometteurs que j'ai identifiés sont : la <b>prédiction du "
    "risque d'abandon</b> (classification), la <b>détection d'anomalies de présence</b> "
    "et l'<b>estimation de la performance finale</b> (régression). Le candidat C-01 "
    "(abandon) semble le plus faisable : variable cible disponible (<code>statut</code>), "
    "features riches (présences, notes intermédiaires, secteur entreprise) et impact métier "
    "direct pour le service Formation. La Phase 3 formalisera le choix du problème, "
    "la question de recherche et les critères de succès. Les sources non structurées "
    "(DS-06) restent hors périmètre immédiat, sauf si un mécanisme de capture est mis "
    "en place durant le stage.",
    body,
))
story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — DICTIONNAIRE DE DONNÉES
# ══════════════════════════════════════════════════════════════════════════════
story.append(Paragraph("3. Dictionnaire de données – Base MySQL (DS-01)", h1))
story.append(HRFlowable(width=W, thickness=0.8, color=LIGHT_BLUE, spaceAfter=4))
story.append(Paragraph(
    "Extrait du schéma relationnel du module stagiaires. Les champs ont été vérifiés "
    "via phpMyAdmin et confrontés aux écrans de saisie utilisés par le service Formation.",
    body,
))

dd_hdr = [
    Paragraph("<b>Table</b>", label),
    Paragraph("<b>Champ</b>", label),
    Paragraph("<b>Type</b>", label),
    Paragraph("<b>Description</b>", label),
    Paragraph("<b>Complétude</b>", label),
]
dd_rows = [dd_hdr]
dd_col = [2.2 * cm, 2.5 * cm, 2.2 * cm, W - 2.2 * cm - 2.5 * cm - 2.2 * cm - 2.3 * cm, 2.3 * cm]
prev_table = None
for table, field, ftype, desc, completeness in DATA_DICT:
    dd_rows.append([
        Paragraph(f"<b>{table}</b>" if table != prev_table else "", cell_b),
        Paragraph(field, cell),
        Paragraph(ftype, cell),
        Paragraph(desc, cell),
        Paragraph(completeness, cell_it),
    ])
    prev_table = table

dd_tbl = Table(dd_rows, colWidths=dd_col, repeatRows=1)
dd_tbl.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), LIGHT_BLUE),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, VERY_LIGHT]),
    ("GRID", (0, 0), (-1, -1), 0.4, GRAY),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("TOPPADDING", (0, 0), (-1, -1), 3),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ("LEFTPADDING", (0, 0), (-1, -1), 4),
]))
story.append(dd_tbl)
story.append(Spacer(1, 0.4 * cm))

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4 — MATRICE DE QUALITÉ + SCHÉMA
# ══════════════════════════════════════════════════════════════════════════════
story.append(Paragraph("4. Matrice de qualité et paysage des données", h1))
story.append(HRFlowable(width=W, thickness=0.8, color=LIGHT_BLUE, spaceAfter=4))

q_hdr = [
    Paragraph("<b>Critère</b>", label),
    Paragraph("<b>Source</b>", label),
    Paragraph("<b>Score</b>", label),
    Paragraph("<b>Observations</b>", label),
]
q_rows = [q_hdr]
for crit, src, score, obs in QUALITY_CRITERIA:
    q_rows.append([
        Paragraph(crit, cell_b),
        Paragraph(src, cell),
        Paragraph(score, cell_b),
        Paragraph(obs, cell),
    ])

q_tbl = Table(q_rows, colWidths=[2.5 * cm, 1.5 * cm, 1.5 * cm, W - 5.5 * cm], repeatRows=1)
q_tbl.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), LIGHT_BLUE),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, VERY_LIGHT]),
    ("GRID", (0, 0), (-1, -1), 0.4, GRAY),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("TOPPADDING", (0, 0), (-1, -1), 4),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ("LEFTPADDING", (0, 0), (-1, -1), 4),
]))
story.append(q_tbl)
story.append(Spacer(1, 0.35 * cm))
story.append(Paragraph(
    "<b>Schéma du paysage des données</b> – de la production à l'exploitation ML :",
    S("sch", fontName="Times-Bold", fontSize=10, textColor=MID_BLUE, spaceAfter=6),
))
story.append(DataLandscapeMap(W))
story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 5 — CANDIDATS PROBLÈMES ML
# ══════════════════════════════════════════════════════════════════════════════
story.append(Paragraph("5. Candidats problèmes ML (préparation Phase 3)", h1))
story.append(HRFlowable(width=W, thickness=0.8, color=LIGHT_BLUE, spaceAfter=4))
story.append(Paragraph(
    "Ces candidats ne constituent pas encore le problème formalisé (réservé à la Phase 3). "
    "Ils résultent de l'exploration et seront priorisés selon la faisabilité et la valeur métier.",
    body,
))

ml_hdr = [
    Paragraph("<b>ID</b>", label),
    Paragraph("<b>Problème candidat</b>", label),
    Paragraph("<b>Source(s)</b>", label),
    Paragraph("<b>Type ML</b>", label),
    Paragraph("<b>Variable cible</b>", label),
    Paragraph("<b>Faisabilité</b>", label),
]
ml_rows = [ml_hdr]
ml_col = [0.8 * cm, 3.5 * cm, 2.2 * cm, 2.2 * cm, 2.8 * cm, W - 11.5 * cm]

for c in ML_CANDIDATES:
    ml_rows.append([
        Paragraph(c["id"], cell_b),
        Paragraph(f"<b>{c['title']}</b><br/><i>{c['value']}</i>", cell),
        Paragraph(c["data"], cell),
        Paragraph(c["type"], cell),
        Paragraph(c["target"], cell),
        Paragraph(c["feasibility"], cell_b),
    ])

ml_tbl = Table(ml_rows, colWidths=ml_col, repeatRows=1)
ml_tbl.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), LIGHT_BLUE),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, VERY_LIGHT]),
    ("GRID", (0, 0), (-1, -1), 0.4, GRAY),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("TOPPADDING", (0, 0), (-1, -1), 4),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ("LEFTPADDING", (0, 0), (-1, -1), 4),
]))
story.append(ml_tbl)
story.append(Spacer(1, 0.4 * cm))

rec_rows = [
    [Paragraph("<b>Recommandation pour la Phase 3</b>", cell_b)],
    [Paragraph(
        "Prioriser le <b>candidat C-01 – Prédiction du risque d'abandon</b> : "
        "données disponibles dans DS-01, impact direct pour le service Formation, "
        "et alignement avec la mission de l'INPP (réduire les abandons en cours de "
        "formation professionnelle). Les candidats C-04 et C-05 sont reportés faute "
        "de données structurées suffisantes.",
        cell,
    )],
]
rec_tbl = Table(rec_rows, colWidths=[W])
rec_tbl.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), LIGHT_GRN),
    ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#f4fdf7")),
    ("BOX", (0, 0), (-1, -1), 0.8, GREEN),
    ("TOPPADDING", (0, 0), (-1, -1), 6),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ("LEFTPADDING", (0, 0), (-1, -1), 8),
]))
story.append(rec_tbl)

story.append(Spacer(1, 0.5 * cm))
story.append(Paragraph(
    "<b>Réflexion personnelle :</b> Cette phase m'a fait passer d'une vision « processus » "
    "(Phase 1b) à une vision « données » concrète. J'ai appris à interroger une base MySQL "
    "comme un futur praticien du machine learning : pas seulement « quelles tables existent », "
    "mais « quelle est leur qualité, qui y accède, et que peut-on raisonnablement prédire ? ». "
    "Je reste conscient que mes chiffres de complétude sont des estimations basées sur "
    "l'observation et des exports ponctuels — ils devront être affinés lors de la Phase 3 "
    "avec un jeu de données exporté et nettoyé.",
    body,
))


def page_footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(LIGHT_BLUE)
    canvas.setLineWidth(0.5)
    canvas.line(doc.leftMargin, doc.bottomMargin - 0.3 * cm,
                doc.pagesize[0] - doc.rightMargin, doc.bottomMargin - 0.3 * cm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(GRAY)
    canvas.drawRightString(doc.pagesize[0] - doc.rightMargin,
                           doc.bottomMargin - 0.65 * cm,
                           f"Page {doc.page}")
    canvas.restoreState()


doc.build(story, onFirstPage=lambda c, d: None, onLaterPages=page_footer)
print(f"PDF genere : {OUT}")
