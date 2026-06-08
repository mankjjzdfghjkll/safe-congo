from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
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

# ── Palette ──────────────────────────────────────────────────────────────────
BLUE       = colors.HexColor("#1a5276")
MID_BLUE   = colors.HexColor("#2471a3")
LIGHT_BLUE = colors.HexColor("#d6eaf8")
VERY_LIGHT = colors.HexColor("#f0f7fb")
GREEN      = colors.HexColor("#1e8449")
LIGHT_GRN  = colors.HexColor("#d5f5e3")
ORANGE     = colors.HexColor("#e67e22")
LIGHT_ORG  = colors.HexColor("#fdebd0")
GRAY       = colors.HexColor("#85929e")
LGRAY      = colors.HexColor("#eaecee")
BLACK      = colors.black
WHITE      = colors.white

# ── Style factory ─────────────────────────────────────────────────────────────
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
small   = S("small", fontName="Helvetica", fontSize=9, leading=12)
cell    = S("cell", fontName="Times-Roman", fontSize=9, leading=12)
cell_b  = S("cell_b", fontName="Times-Bold", fontSize=9, leading=12)
cell_it = S("cell_it", fontName="Times-Italic", fontSize=8.5, leading=12, textColor=colors.HexColor("#555555"))
label   = S("label", fontName="Helvetica-Bold", fontSize=8.5,
            alignment=TA_CENTER, textColor=BLUE)
note_s  = S("note", fontName="Helvetica-Oblique", fontSize=8, leading=11,
            textColor=colors.HexColor("#555555"))

# ── Données de chaque étape ───────────────────────────────────────────────────
STEPS = [
    {
        "num":  "1",
        "title": "Demande du besoin",
        "role":  "Service demandeur\n(Formation, RH, Direction)",
        "tools": "Oral, téléphone, WhatsApp, e-mail",
        "input": "Besoin métier ou difficulté opérationnelle",
        "output":"Demande transmise au Chef SI",
        "value": "Rend le besoin explicite et traçable",
        "data":  "Non capturée (message vocal / WhatsApp) — risque de perte",
        "freq":  "2 à 4 demandes / mois",
        "transfer": "→ Chef Service Informatique",
    },
    {
        "num":  "2",
        "title": "Qualification & priorisation",
        "role":  "Chef du Service Informatique",
        "tools": "Échanges directs, notes manuelles, agenda papier",
        "input": "Demande reçue (verbale ou écrite)",
        "output":"Demande priorisée et affectée à la Cellule Dev",
        "value": "Filtre les demandes non pertinentes ; alloue les ressources",
        "data":  "Notes manuelles — partiellement stockées dans un cahier",
        "freq":  "Même fréquence que l'étape 1",
        "transfer": "→ Cellule de Développement",
    },
    {
        "num":  "3",
        "title": "Analyse et cadrage métier",
        "role":  "Stagiaire + encadreur + utilisateur métier",
        "tools": "Observation directe, cahier de notes, Word / Excel",
        "input": "Demande priorisée + explications de l'utilisateur",
        "output":"Règles métier, liste de champs, écrans attendus",
        "value": "Transforme un besoin flou en exigences exploitables",
        "data":  "Capturée dans Word/Excel — stockée localement sur le poste",
        "freq":  "1 à 3 séances de 1–2 h par demande",
        "transfer": "→ Conception technique",
    },
    {
        "num":  "4",
        "title": "Conception technique",
        "role":  "Cellule de Développement (stagiaire + référent)",
        "tools": "StarUML, schémas papier, réunion courte",
        "input": "Règles métier et champs clarifiés",
        "output":"Diagrammes UML, structure de base de données",
        "value": "Réduit les ambiguïtés avant le codage",
        "data":  "Capturée dans fichiers StarUML (.mdj) — stockée localement",
        "freq":  "0,5 à 1 jour par module",
        "transfer": "→ Développement",
    },
    {
        "num":  "5",
        "title": "Développement du module",
        "role":  "Stagiaire développeuse + référent technique",
        "tools": "PHP 8, HTML/CSS, MySQL 8, XAMPP, VS Code",
        "input": "Diagrammes UML + logique métier validée",
        "output":"Prototype fonctionnel hébergé sur XAMPP local",
        "value": "Produit la solution numérique utilisable",
        "data":  "Données saisies stockées dans MySQL — tables structurées",
        "freq":  "3 à 10 jours selon la complexité",
        "transfer": "→ Test métier avec utilisateur",
    },
    {
        "num":  "6",
        "title": "Test et corrections itératives",
        "role":  "Service demandeur + IT (stagiaire)",
        "tools": "Démonstration locale XAMPP, retours verbaux, annotations papier",
        "input": "Prototype fonctionnel",
        "output":"Version corrigée et validée par l'utilisateur",
        "value": "Aligne le système sur le travail réel",
        "data":  "Retours non formalisés — risque de perte si non consignés",
        "freq":  "1 à 3 cycles de correction par module",
        "transfer": "→ Mise en service",
    },
    {
        "num":  "7",
        "title": "Mise en service et appui",
        "role":  "Service Informatique + stagiaire (phase de déploiement)",
        "tools": "XAMPP, poste local dédié, assistance directe sur site",
        "input": "Version validée du module",
        "output":"Module utilisé en production locale ; incidents signalés",
        "value": "Intègre la solution dans le travail quotidien",
        "data":  "Données de production stockées dans MySQL — base opérationnelle",
        "freq":  "Continu ; appui ponctuel sur demande",
        "transfer": "↩ Boucle vers étape 2 si incident ou nouvelle demande",
    },
]

# ── Diagramme VSM (Flowable custom) ──────────────────────────────────────────
class ValueStreamMap(Flowable):
    BOX_H = 2.7 * cm
    ARROW_H = 0.6 * cm

    def __init__(self, width):
        super().__init__()
        self.width = width
        n = len(STEPS)
        self.height = 1.4*cm + n*(self.BOX_H + self.ARROW_H) + 0.4*cm

    def wrap(self, aw, ah):
        return self.width, self.height

    def _draw_box(self, c, x, y, w, step):
        h = self.BOX_H
        # shadow
        c.setFillColor(colors.HexColor("#c8d6e5"))
        c.setStrokeColor(colors.HexColor("#c8d6e5"))
        c.roundRect(x+3, y-3, w, h, 6, stroke=0, fill=1)
        # box
        c.setStrokeColor(BLUE)
        c.setFillColor(VERY_LIGHT)
        c.setLineWidth(0.9)
        c.roundRect(x, y, w, h, 6, stroke=1, fill=1)
        # title bar
        c.setFillColor(BLUE)
        c.roundRect(x, y+h-0.62*cm, w, 0.62*cm, 6, stroke=0, fill=1)
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 8.5)
        c.drawString(x+8, y+h-0.45*cm, f"Étape {step['num']} — {step['title']}")
        # body lines
        c.setFillColor(BLACK)
        lh = 10
        base = y + h - 0.75*cm
        lines = [
            ("Rôle :", step["role"].replace("\n", " ")),
            ("Outils :", step["tools"]),
            ("E→S :", f"{step['input']}  ➜  {step['output']}"),
            ("Données :", step["data"]),
            ("Valeur :", step["value"]),
        ]
        for i, (lbl, val) in enumerate(lines):
            yy = base - i*lh
            c.setFont("Helvetica-Bold", 7)
            c.drawString(x+8, yy, lbl)
            c.setFont("Helvetica", 7)
            # truncate if needed
            txt = val if len(val) < 90 else val[:88]+"…"
            c.drawString(x+8+c.stringWidth(lbl, "Helvetica-Bold", 7)+3, yy, txt)

    def _draw_arrow(self, c, cx, y_top, label):
        ay_start = y_top
        ay_end   = y_top - self.ARROW_H + 0.15*cm
        c.setStrokeColor(MID_BLUE)
        c.setFillColor(MID_BLUE)
        c.setLineWidth(1.2)
        c.line(cx, ay_start, cx, ay_end + 0.3*cm)
        # arrowhead
        p = c.beginPath()
        p.moveTo(cx, ay_end)
        p.lineTo(cx-5, ay_end+0.32*cm)
        p.lineTo(cx+5, ay_end+0.32*cm)
        p.close()
        c.drawPath(p, fill=1, stroke=0)
        c.setFont("Helvetica-Oblique", 6.5)
        c.setFillColor(MID_BLUE)
        c.drawCentredString(cx, ay_end + 0.35*cm, label)

    def draw(self):
        c = self.canv
        margin = 0.5 * cm
        w = self.width - 2*margin
        x = margin
        cx = x + w/2

        # Trigger
        ty = self.height - 1.3*cm
        c.setStrokeColor(GREEN)
        c.setFillColor(LIGHT_GRN)
        c.setLineWidth(1)
        c.roundRect(x, ty, w, 1.1*cm, 6, stroke=1, fill=1)
        c.setFillColor(GREEN)
        c.setFont("Helvetica-Bold", 8.5)
        c.drawString(x+8, ty+0.72*cm, "⚡ DÉCLENCHEUR")
        c.setFillColor(BLACK)
        c.setFont("Helvetica", 7.5)
        c.drawString(x+8, ty+0.25*cm,
            "Un service interne identifie un besoin de suivi, de rapport ou de numérisation d'une activité manuelle.")

        cursor = ty  # bottom of trigger box

        for i, step in enumerate(STEPS):
            # arrow from previous element bottom to box top
            self._draw_arrow(c, cx, cursor,
                             "Début du flux" if i == 0 else STEPS[i-1]["transfer"])
            box_y = cursor - self.ARROW_H - self.BOX_H
            self._draw_box(c, x, box_y, w, step)
            cursor = box_y

        # Final return arrow
        c.setStrokeColor(ORANGE)
        c.setFillColor(ORANGE)
        c.setFont("Helvetica-Oblique", 7)
        c.drawCentredString(cx, cursor - 0.22*cm, STEPS[-1]["transfer"])


# ── Chemins ───────────────────────────────────────────────────────────────────
OUT  = r"C:\Users\PC\Desktop\SAFE CONGO\TP machine learning\MANKAND-A-MUTEB_JOSEE_MAL1471_Phase1b.pdf"
LOGO = r"C:\Users\PC\Desktop\logo-unh.png"

doc = SimpleDocTemplate(
    OUT,
    pagesize=A4,
    leftMargin=2.2*cm, rightMargin=2.2*cm,
    topMargin=1.8*cm,  bottomMargin=2.1*cm,
    title="MAL1471 Phase 1b – Value Stream Map",
    author="MANKAND-A-MUTEB JOSEE",
)
W = doc.width
story = []

# ══════════════════════════════════════════════════════════════════════════════
# PAGE DE GARDE
# ══════════════════════════════════════════════════════════════════════════════
story.append(Spacer(1, 0.15*cm))
if os.path.exists(LOGO):
    logo = Image(LOGO, width=6.6*cm, height=6.6*cm, kind="proportional")
    story.append(Table([[logo]], colWidths=[W],
                       style=[("ALIGN",(0,0),(0,0),"CENTER")]))
story.append(Spacer(1, 0.25*cm))

def cov(txt, **kw):
    return Paragraph(txt, S("_cov", alignment=TA_CENTER, **kw))

story += [
    cov("UNIVERSITÉ NOUVEAUX HORIZONS",
        fontName="Helvetica-Bold", fontSize=15, textColor=BLUE, leading=20),
    cov("Faculté des Sciences Informatiques",
        fontName="Helvetica", fontSize=10.5, leading=15),
    Spacer(1, 0.7*cm),
    cov("PROJET FINAL MAL1471 — 2026",
        fontName="Helvetica-Bold", fontSize=16.5, textColor=BLUE, leading=22),
    cov("Phase 1(b) : Cartographie de la chaîne de valeur",
        fontName="Helvetica-Bold", fontSize=12.5, leading=17),
    Spacer(1, 0.65*cm),
    cov("Dirigé par : Pr. EMMANUEL KALUNGA  |  Ass. ORTEGA-KABWE",
        fontName="Helvetica", fontSize=10.5, leading=16),
    Spacer(1, 0.5*cm),
    cov("MANKAND-A-MUTEB JOSÉE",
        fontName="Helvetica-Bold", fontSize=12, textColor=BLUE, leading=17),
    cov("Matricule : SI/20223393  —  L4 Génie Logiciel",
        fontName="Helvetica", fontSize=10.5, leading=16),
    Spacer(1, 0.65*cm),
    cov("Année Académique 2025-2026",
        fontName="Helvetica-Bold", fontSize=11.5, textColor=BLUE),
    Spacer(1, 0.4*cm),
    HRFlowable(width=W, thickness=1.5, color=BLUE),
]
story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — TABLEAU RÉCAPITULATIF
# ══════════════════════════════════════════════════════════════════════════════
story.append(Paragraph("1. Tableau récapitulatif du processus", h1))
story.append(HRFlowable(width=W, thickness=0.8, color=LIGHT_BLUE, spaceAfter=4))

hdr = [
    Paragraph("<b>N°</b>", label),
    Paragraph("<b>Étape</b>", label),
    Paragraph("<b>Rôle responsable</b>", label),
    Paragraph("<b>Entrée primaire</b>", label),
    Paragraph("<b>Sortie primaire</b>", label),
    Paragraph("<b>Outils & valeur ajoutée</b>", label),
    Paragraph("<b>Données générées</b>", label),
]
rows = [hdr]
col_w = [0.6*cm, 2.5*cm, 2.8*cm, 2.6*cm, 2.6*cm, 3.5*cm, W-14.6*cm]

for s in STEPS:
    rows.append([
        Paragraph(s["num"], cell_b),
        Paragraph(f"<b>{s['title']}</b>", cell_b),
        Paragraph(s["role"].replace("\n","<br/>"), cell),
        Paragraph(s["input"], cell),
        Paragraph(s["output"], cell),
        Paragraph(f"{s['tools']}<br/><i>Valeur : {s['value']}</i>", cell),
        Paragraph(s["data"], cell_it),
    ])

tbl = Table(rows, colWidths=col_w, repeatRows=1)
tbl.setStyle(TableStyle([
    ("BACKGROUND",(0,0),(-1,0), LIGHT_BLUE),
    ("TEXTCOLOR",(0,0),(-1,0), BLUE),
    ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
    ("ALIGN",(0,0),(-1,0),"CENTER"),
    ("ROWBACKGROUNDS",(0,1),(-1,-1),[WHITE, VERY_LIGHT]),
    ("GRID",(0,0),(-1,-1),0.4, GRAY),
    ("VALIGN",(0,0),(-1,-1),"TOP"),
    ("TOPPADDING",(0,0),(-1,-1),4),
    ("BOTTOMPADDING",(0,0),(-1,-1),4),
    ("LEFTPADDING",(0,0),(-1,-1),4),
    ("RIGHTPADDING",(0,0),(-1,-1),4),
]))
story.append(tbl)
story.append(Spacer(1, 0.3*cm))

# Note sur le statut des données
note_rows = [
    [Paragraph("<b>📌 Analyse du statut des données (essentiel pour la Phase 2)</b>", cell_b)],
    [Paragraph(
        "Étapes 1 et 6 : données <b>non ou peu capturées</b> (échanges WhatsApp, retours verbaux) "
        "— perte d'information fréquente.<br/>"
        "Étapes 3 et 4 : données capturées dans Word/Excel/StarUML sur poste local "
        "— <b>non centralisées</b>, accès limité.<br/>"
        "Étapes 5 et 7 : données <b>structurées et stockées</b> dans MySQL via XAMPP "
        "— base exploitable pour une analyse future.", cell)],
]
note_tbl = Table(note_rows, colWidths=[W])
note_tbl.setStyle(TableStyle([
    ("BACKGROUND",(0,0),(-1,0), LIGHT_ORG),
    ("BACKGROUND",(0,1),(-1,1), colors.HexColor("#fffbf5")),
    ("BOX",(0,0),(-1,-1),0.8, ORANGE),
    ("TOPPADDING",(0,0),(-1,-1),5),
    ("BOTTOMPADDING",(0,0),(-1,-1),5),
    ("LEFTPADDING",(0,0),(-1,-1),7),
]))
story.append(note_tbl)
story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — DOCUMENTATION ÉCRITE (700–1000 mots)
# ══════════════════════════════════════════════════════════════════════════════
story.append(Paragraph("2. Documentation écrite de la chaîne de valeur", h1))
story.append(HRFlowable(width=W, thickness=0.8, color=LIGHT_BLUE, spaceAfter=6))

# ── 3.1 Introduction & choix du flux
story.append(Paragraph("2.1 Choix du flux et contexte d'observation", h2))
story.append(Paragraph(
    "Le flux que j'ai choisi de cartographier est celui du <b>traitement d'une demande interne de développement "
    "ou d'amélioration d'un module métier</b> au sein du Pool Informatique / Cellule de Développement de l'INPP "
    "Haut-Katanga (cf. <i>Étapes 1 à 7 du VSM, Section 1</i>). Ce choix est délibéré : il correspond précisément "
    "à mon activité quotidienne en tant que stagiaire développeuse et il couvre l'intégralité du cycle de vie "
    "d'une solution numérique dans ce contexte institutionnel. "
    "Ce flux intervient en moyenne <b>deux à quatre fois par mois</b>, selon les urgences remontées par les services. "
    "Il n'existe pas de système de ticketing formalisé ; la demande transite le plus souvent par <b>WhatsApp ou "
    "par échange oral</b> — ce qui constitue déjà un premier point de fragilité documentaire.",
    body,
))

# ── 3.2 Déroulement étape par étape
story.append(Paragraph("2.2 Flux global et valeur ajoutée à chaque étape", h2))
story.append(Paragraph(
    "<b>Étape 1 — Demande du besoin :</b> un agent du service Formation, des Ressources Humaines ou de la Direction "
    "signale un problème opérationnel : un suivi manuel trop lourd, un fichier Excel qui ne suffit plus, ou un rapport "
    "qui prend trop de temps à produire. La demande arrive sans format prédéfini — message WhatsApp, appel téléphonique "
    "ou remarque en réunion. <b>Les données à ce stade ne sont pas capturées de façon structurée</b>, ce qui implique "
    "un risque de perte ou de malentendu. La valeur de cette étape est pourtant fondamentale : elle rend le besoin "
    "métier explicite et déclenche le flux.",
    body,
))
story.append(Paragraph(
    "<b>Étape 2 — Qualification et priorisation :</b> le Chef du Service Informatique reçoit la demande et décide "
    "si elle relève du périmètre IT, si elle est suffisamment prioritaire et si les ressources sont disponibles. "
    "Ce point de transfert de responsabilité est crucial : en l'absence de ticketing, la qualification repose "
    "entièrement sur des <b>notes manuelles dans un cahier</b> et sur la mémoire du responsable. "
    "La valeur ajoutée est d'éviter que la Cellule de Développement ne travaille sur des besoins mal formulés ou secondaires.",
    body,
))
story.append(Paragraph(
    "<b>Étape 3 — Analyse et cadrage métier :</b> avec l'encadreur direct et l'utilisateur métier, je participe "
    "à la collecte des règles de gestion, à l'identification des champs à saisir et à la compréhension du "
    "déroulement réel du travail. Cette étape mobilise l'<b>observation directe sur le terrain</b>, un cahier de notes, "
    "et parfois Word ou Excel pour résumer les informations. Les données résultantes sont stockées localement "
    "sur le poste de travail, mais ne sont pas centralisées. "
    "C'est l'étape qui conditionne la qualité de toutes les suivantes : une mauvaise compréhension à ce stade "
    "se répercute sur l'ensemble du flux (cf. <i>Tableau Section 2, ligne 3</i>). "
    "Elle mobilise généralement <b>une à trois séances de travail</b> d'une à deux heures chacune.",
    body,
))
story.append(Paragraph(
    "<b>Étape 4 — Conception technique :</b> à partir des exigences recueillies, la Cellule de Développement "
    "produit des diagrammes UML sous <b>StarUML</b> (diagramme de classes, diagramme de séquence si nécessaire) "
    "et structure les tables de la base de données MySQL. Des croquis papier complètent les diagrammes lors "
    "des réunions courtes avec le référent technique. Les fichiers <code>.mdj</code> sont sauvegardés "
    "localement. Cette étape dure généralement <b>une demi-journée à une journée</b> selon la complexité du module. "
    "Elle représente le passage du langage métier au langage technique, et ajoute de la valeur en réduisant "
    "les ambiguïtés avant que le codage ne commence.",
    body,
))
story.append(Paragraph(
    "<b>Étape 5 — Développement du module :</b> c'est le cœur productif du flux. À partir des diagrammes validés, "
    "je développe les écrans de saisie, les formulaires, les requêtes SQL et les interfaces de consultation "
    "en <b>PHP 8, HTML/CSS, MySQL 8</b> sous <b>XAMPP</b>, avec <b>VS Code</b> comme éditeur. "
    "Les données commencent ici à être réellement structurées et stockées dans des tables MySQL. "
    "Un module de complexité standard prend entre <b>trois et dix jours de développement</b>. "
    "C'est à cette étape que la valeur numérique prend forme concrètement.",
    body,
))
story.append(Paragraph(
    "<b>Étape 6 — Test et corrections itératives :</b> l'utilisateur métier teste le prototype sur le poste local "
    "XAMPP lors d'une démonstration organisée en présentiel. Les retours sont donnés à l'oral ou annotés "
    "sur papier, puis réinjectés dans le cycle de correction. <b>Cette étape se répète une à trois fois</b> "
    "selon le nombre de corrections nécessaires. Un point de fragilité notable : les retours utilisateurs "
    "ne sont pas systématiquement consignés par écrit, ce qui rend difficile la traçabilité des décisions "
    "prises (cf. <i>colonne « Données générées », Tableau Section 2</i>).",
    body,
))
story.append(Paragraph(
    "<b>Étape 7 — Mise en service et appui :</b> la version validée est déployée sur un poste local dédié "
    "via XAMPP, accessible aux agents du service concerné sur le réseau interne. "
    "La mise en service se fait avec un accompagnement direct : démonstration pratique, explication "
    "des fonctionnalités, et disponibilité pour les premières corrections post-déploiement. "
    "La base de données MySQL devient alors opérationnelle et accumule des données de production. "
    "Si un incident survient ou qu'un nouveau besoin est identifié, le flux repart depuis l'étape 2 "
    "(boucle de retour).",
    body,
))

# ── 3.3 Mon rôle personnel
story.append(Paragraph("2.3 Mon rôle personnel dans le flux", h2))
story.append(Paragraph(
    "Mon positionnement dans ce flux est principalement aux <b>étapes 3, 4, 5 et 6</b>, "
    "avec une présence ponctuelle à l'étape 7 lors de la mise en service. "
    "À l'étape 3, je participe activement aux séances d'analyse avec les utilisateurs : "
    "je prends en note les règles métier, je reformule les exigences, et je prépare "
    "les listes de champs et les maquettes d'écrans. "
    "À l'étape 4, je travaille avec mon encadreur pour structurer les tables et créer "
    "les diagrammes UML sous StarUML. "
    "À l'étape 5, j'assume l'essentiel du développement : création des tables dans "
    "<b>phpMyAdmin</b>, développement des scripts PHP, mise en forme HTML/CSS, "
    "et test de l'ensemble en local sur XAMPP. "
    "À l'étape 6, j'anime les sessions de démonstration, je note les corrections demandées "
    "et j'implémente les ajustements. "
    "Cette observation active m'a permis de constater trois zones de friction récurrentes : "
    "l'absence de capture formelle des demandes (étape 1), l'absence de centralisation "
    "des documents d'analyse (étape 3) et l'absence de journal de tests structuré (étape 6). "
    "Ces trois zones seront au cœur de mon analyse de données en Phase 2.",
    body,
))

# ── 3.4 Synthèse
story.append(Paragraph("2.4 Synthèse et lien avec la Phase 2", h2))
story.append(Paragraph(
    "Cette cartographie révèle un flux opérationnel fonctionnel, porté par des professionnels "
    "compétents, mais dont plusieurs maillons reposent sur des supports informels "
    "(messages WhatsApp, notes papier, retours verbaux). "
    "La valeur est bien créée à chaque étape, mais elle n'est pas toujours <b>tracée ni mesurée</b>. "
    "La phase 2 exploitera les données structurées disponibles dans MySQL (étapes 5 et 7) "
    "ainsi que les journaux d'activité pouvant être reconstitués, pour identifier "
    "des opportunités de classification, de prédiction ou de détection d'anomalies "
    "dans ce flux de développement logiciel en contexte institutionnel africain.",
    body,
))
story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — DIAGRAMME VSM
# ══════════════════════════════════════════════════════════════════════════════
story.append(Paragraph("3. Cartographie de la chaîne de valeur (VSM)", h1))
story.append(HRFlowable(width=W, thickness=0.8, color=LIGHT_BLUE, spaceAfter=4))
story.append(Paragraph(
    "<b>Flux cartographié :</b> traitement d'une demande interne de développement ou d'amélioration "
    "d'un module métier au sein du Pool Informatique / Cellule de Développement.",
    S("intro", fontName="Helvetica-Oblique", fontSize=10, leading=14,
      textColor=colors.HexColor("#333333"), spaceBefore=2, spaceAfter=8),
))
story.append(ValueStreamMap(W))
story.append(Spacer(1, 0.25*cm))

leg_data = [
    [Paragraph("<b>Légende — statut des données à chaque étape</b>", label)],
    [Table([
        [Paragraph("■ Capturée/stockée", S("lg", fontName="Helvetica", fontSize=8, textColor=GREEN)),
         Paragraph("■ Partiellement capturée", S("lg2", fontName="Helvetica", fontSize=8, textColor=ORANGE)),
         Paragraph("■ Non capturée / risque de perte", S("lg3", fontName="Helvetica", fontSize=8, textColor=colors.red))],
    ], colWidths=[W/3, W/3, W/3])],
]
leg_tbl = Table(leg_data, colWidths=[W])
leg_tbl.setStyle(TableStyle([
    ("BACKGROUND",(0,0),(-1,0), LIGHT_BLUE),
    ("BOX",(0,0),(-1,-1),0.5,GRAY),
    ("TOPPADDING",(0,0),(-1,-1),3),
    ("BOTTOMPADDING",(0,0),(-1,-1),3),
]))
story.append(leg_tbl)

# ══════════════════════════════════════════════════════════════════════════════
# PIED DE PAGE
# ══════════════════════════════════════════════════════════════════════════════
def page_footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(LIGHT_BLUE)
    canvas.setLineWidth(0.5)
    canvas.line(doc.leftMargin, doc.bottomMargin - 0.3*cm,
                doc.pagesize[0] - doc.rightMargin, doc.bottomMargin - 0.3*cm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(GRAY)
    canvas.drawRightString(doc.pagesize[0] - doc.rightMargin,
                           doc.bottomMargin - 0.65*cm,
                           f"Page {doc.page}")
    canvas.restoreState()

doc.build(story, onFirstPage=lambda c,d: None, onLaterPages=page_footer)
print(f"✅ PDF généré : {OUT}")
