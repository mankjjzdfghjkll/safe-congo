from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    PageBreak,
)
from reportlab.platypus.flowables import Flowable


BLUE = colors.HexColor("#1a5276")
LIGHT_BLUE = colors.HexColor("#dbeaf4")
VERY_LIGHT = colors.HexColor("#f7fbfd")
GRAY = colors.HexColor("#aab7c4")
BLACK = colors.black
WHITE = colors.white


def S(name, **kw):
    defaults = dict(
        fontName="Times-Roman",
        fontSize=11,
        leading=16,
        textColor=BLACK,
        spaceAfter=6,
    )
    defaults.update(kw)
    return ParagraphStyle(name, **defaults)


body = S("body", alignment=TA_JUSTIFY)
h1 = S("h1", fontName="Times-Bold", fontSize=12, alignment=TA_LEFT, spaceBefore=6, spaceAfter=4)
small = S("small", fontName="Helvetica", fontSize=9.2, leading=12)
cell = S("cell", fontName="Times-Roman", fontSize=9.3, leading=12)
cell_b = S("cell_b", fontName="Times-Bold", fontSize=9.3, leading=12)
label = S("label", fontName="Helvetica-Bold", fontSize=9, alignment=TA_CENTER, textColor=BLUE)


STEPS = [
    {
        "title": "1. Demande du besoin",
        "role": "Service demandeur",
        "tools": "Oral, téléphone, WhatsApp, e-mail",
        "io": "Besoin métier -> demande transmise",
        "value": "Rend le besoin explicite",
        "transfer": "Transfert vers le Chef du Service Informatique",
    },
    {
        "title": "2. Qualification",
        "role": "Chef Service Informatique",
        "tools": "Échanges directs, notes, agenda",
        "io": "Demande transmise -> demande priorisée",
        "value": "Décide si le besoin entre dans le flux IT",
        "transfer": "Transfert vers la Cellule de Développement",
    },
    {
        "title": "3. Analyse et cadrage",
        "role": "Stagiaire + encadreur + utilisateur",
        "tools": "Observation, cahier, Word/Excel",
        "io": "Demande priorisée -> règles métier clarifiées",
        "value": "Transforme une demande floue en exigences utilisables",
        "transfer": "Transfert vers la conception technique",
    },
    {
        "title": "4. Conception technique",
        "role": "Cellule Développement",
        "tools": "StarUML, schémas papier, réunion courte",
        "io": "Règles métier -> diagrammes et structure BD",
        "value": "Réduit les ambiguïtés avant le codage",
        "transfer": "Transfert vers le développement",
    },
    {
        "title": "5. Développement interne",
        "role": "Stagiaire développeuse + référent",
        "tools": "PHP, HTML/CSS, MySQL, XAMPP",
        "io": "Diagrammes -> prototype testable",
        "value": "Produit un module utilisable et une base structurée",
        "transfer": "Transfert vers le test métier",
    },
    {
        "title": "6. Test et corrections",
        "role": "Service demandeur + IT",
        "tools": "Démo locale, retours verbaux, annotations",
        "io": "Prototype -> version validée",
        "value": "Vérifie l'adéquation au travail réel",
        "transfer": "Transfert vers la mise en service",
    },
    {
        "title": "7. Mise en service et appui",
        "role": "Service Informatique",
        "tools": "XAMPP, poste local, assistance directe",
        "io": "Version validée -> module utilisé",
        "value": "Intègre la solution dans le travail quotidien",
        "transfer": "Boucle de retour si incident ou nouveau besoin",
    },
]


class ValueStreamMap(Flowable):
    def __init__(self, width):
        super().__init__()
        self.width = width
        self.height = 19.2 * cm

    def wrap(self, availWidth, availHeight):
        return self.width, self.height

    def draw_box(self, canvas, x, y, w, h, title, role, tools, io_line, value):
        canvas.setStrokeColor(BLUE)
        canvas.setFillColor(VERY_LIGHT)
        canvas.setLineWidth(0.8)
        canvas.roundRect(x, y, w, h, 5, stroke=1, fill=1)

        canvas.setFillColor(BLUE)
        canvas.setFont("Helvetica-Bold", 8.5)
        canvas.drawString(x + 7, y + h - 12, title)

        canvas.setFillColor(BLACK)
        canvas.setFont("Helvetica", 7.3)
        canvas.drawString(x + 7, y + h - 24, f"Rôle : {role}")
        canvas.drawString(x + 7, y + h - 35, f"Outils : {tools}")
        canvas.drawString(x + 7, y + h - 46, f"E/S : {io_line}")
        canvas.drawString(x + 7, y + h - 57, f"Valeur : {value}")

    def arrow(self, canvas, x, y1, y2, label):
        canvas.setStrokeColor(GRAY)
        canvas.setFillColor(GRAY)
        canvas.setLineWidth(1)
        canvas.line(x, y1, x, y2 + 5)
        p = canvas.beginPath()
        p.moveTo(x, y2)
        p.lineTo(x - 4, y2 + 7)
        p.lineTo(x + 4, y2 + 7)
        p.close()
        canvas.drawPath(p, fill=1, stroke=0)
        canvas.setFont("Helvetica-Oblique", 7)
        canvas.drawCentredString(x, y2 + 11, label)

    def draw(self):
        c = self.canv
        w = self.width
        box_w = w - 1.2 * cm
        box_h = 2.05 * cm
        x = 0.6 * cm
        cursor_y = self.height - 1.4 * cm

        c.setStrokeColor(BLUE)
        c.setFillColor(LIGHT_BLUE)
        c.roundRect(x, cursor_y, box_w, 1.1 * cm, 5, stroke=1, fill=1)
        c.setFillColor(BLUE)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(x + 7, cursor_y + 18, "Déclencheur")
        c.setFillColor(BLACK)
        c.setFont("Helvetica", 8)
        c.drawString(
            x + 7,
            cursor_y + 7,
            "Un service interne signale un besoin de suivi, de rapport ou de numérisation.",
        )

        top = cursor_y
        cursor_y -= 1.8 * cm

        for index, step in enumerate(STEPS):
            self.draw_box(
                c,
                x,
                cursor_y,
                box_w,
                box_h,
                step["title"],
                step["role"],
                step["tools"],
                step["io"],
                step["value"],
            )
            if index == 0:
                self.arrow(c, x + box_w / 2, top, cursor_y + box_h, "Début du flux")
            if index < len(STEPS) - 1:
                next_y = cursor_y - 0.8 * cm
                self.arrow(c, x + box_w / 2, cursor_y, next_y + box_h, step["transfer"])
                cursor_y = next_y - box_h


OUT = r"C:\Users\PC\Desktop\TP machine learning\MANKAND-A-MUTEB_JOSEE_MAL1471_Phase1b.pdf"
LOGO = r"C:\Users\PC\Desktop\logo-unh.png"

doc = SimpleDocTemplate(
    OUT,
    pagesize=A4,
    leftMargin=2.3 * cm,
    rightMargin=2.3 * cm,
    topMargin=1.8 * cm,
    bottomMargin=2.1 * cm,
    title="MAL1471 Phase1b",
    author="MANKAND-A-MUTEB JOSEE",
)

story = []

# Page de garde simple
story.append(Spacer(1, 0.4 * cm))
logo = Image(LOGO, width=8.2 * cm, height=8.2 * cm, kind="proportional")
logo_tbl = Table([[logo]], colWidths=[doc.width])
logo_tbl.setStyle(TableStyle([("ALIGN", (0, 0), (0, 0), "CENTER")]))
story.append(logo_tbl)
story.append(Spacer(1, 0.5 * cm))
story.append(Paragraph("UNIVERSITÉ NOUVEAUX HORIZONS", S("c1", fontName="Helvetica-Bold", fontSize=14, alignment=TA_CENTER, textColor=BLUE, leading=20)))
story.append(Paragraph("Faculté des Sciences Informatiques", S("c2", fontName="Helvetica", fontSize=11, alignment=TA_CENTER, leading=18)))
story.append(Spacer(1, 1.2 * cm))
story.append(Paragraph("PROJET FINAL MAL1471 - 2026", S("c3", fontName="Helvetica-Bold", fontSize=17, alignment=TA_CENTER, textColor=BLUE, leading=24)))
story.append(Paragraph("Phase 1(b) : Cartographie de la chaîne de valeur", S("c4", fontName="Helvetica-Bold", fontSize=13, alignment=TA_CENTER, leading=20)))
story.append(Spacer(1, 1.2 * cm))
story.append(Paragraph("DIRIGÉ PAR : Pr. EMMANUEL KALUNGA", S("c5", fontName="Helvetica", fontSize=11, alignment=TA_CENTER, leading=19)))
story.append(Paragraph("Ass. ORTEGA-KABWE", S("c6", fontName="Helvetica", fontSize=11, alignment=TA_CENTER, leading=19)))
story.append(Spacer(1, 0.6 * cm))
story.append(Paragraph("FAIT PAR : MANKAND-A-MUTEB JOSEE", S("c7", fontName="Helvetica-Bold", fontSize=11, alignment=TA_CENTER, leading=19)))
story.append(Paragraph("Matricule : SI/20223393", S("c8", fontName="Helvetica", fontSize=11, alignment=TA_CENTER, leading=19)))
story.append(Paragraph("L4 Génie Logiciel", S("c9", fontName="Helvetica", fontSize=11, alignment=TA_CENTER, leading=19)))
story.append(Spacer(1, 0.8 * cm))
story.append(Paragraph("Année Académique 2025-2026", S("c10", fontName="Helvetica-Bold", fontSize=12, alignment=TA_CENTER, textColor=BLUE)))
story.append(PageBreak())

story.append(Paragraph("Cartographie de la chaîne de valeur observée", S("t1", fontName="Helvetica-Bold", fontSize=13, alignment=TA_CENTER, textColor=BLUE, leading=18)))
story.append(Spacer(1, 0.2 * cm))
story.append(Paragraph(
    "Flux choisi : traitement d'une demande interne de développement ou d'amélioration d'un module métier au sein du Pool Informatique / Cellule de Développement de l'INPP Haut-Katanga.",
    body,
))
story.append(Spacer(1, 0.2 * cm))
story.append(ValueStreamMap(doc.width))
story.append(PageBreak())

story.append(Paragraph("Tableau récapitulatif du processus", h1))
rows = [
    [
        Paragraph("<b>Étape</b>", label),
        Paragraph("<b>Rôle responsable</b>", label),
        Paragraph("<b>Entrée primaire</b>", label),
        Paragraph("<b>Sortie primaire</b>", label),
        Paragraph("<b>Outils / valeur ajoutée</b>", label),
    ]
]

table_data = [
    (
        "1. Demande du besoin",
        "Service demandeur (Formation, RH, Direction)",
        "Besoin métier ou difficulté opérationnelle",
        "Demande exprimée au service informatique",
        "Oral, téléphone, WhatsApp, e-mail. Valeur : fait remonter le besoin réel.",
    ),
    (
        "2. Qualification",
        "Chef du Service Informatique",
        "Demande reçue",
        "Demande priorisée et orientée",
        "Échanges directs, notes manuelles. Valeur : filtre et priorise.",
    ),
    (
        "3. Analyse et cadrage",
        "Stagiaire développeuse + encadreur + utilisateur",
        "Demande priorisée",
        "Règles métier et champs de données clarifiés",
        "Observation, cahier, Word/Excel. Valeur : transforme le besoin en exigences.",
    ),
    (
        "4. Conception technique",
        "Cellule de Développement",
        "Exigences clarifiées",
        "Diagrammes et structure de base de données",
        "StarUML, schémas papier. Valeur : prépare le codage sans ambiguïté.",
    ),
    (
        "5. Développement interne",
        "Stagiaire développeuse + référent technique",
        "Diagrammes et logique métier",
        "Prototype fonctionnel",
        "PHP, HTML/CSS, MySQL, XAMPP. Valeur : produit le module.",
    ),
    (
        "6. Test et corrections",
        "Service demandeur + IT",
        "Prototype fonctionnel",
        "Version corrigée et validée",
        "Démo locale, retours verbaux. Valeur : aligne le système sur la réalité.",
    ),
    (
        "7. Mise en service et appui",
        "Service Informatique",
        "Version validée",
        "Module utilisé et incidents remontés",
        "XAMPP, poste local, assistance directe. Valeur : met la solution en production locale.",
    ),
]

for item in table_data:
    rows.append([
        Paragraph(item[0], cell_b),
        Paragraph(item[1], cell),
        Paragraph(item[2], cell),
        Paragraph(item[3], cell),
        Paragraph(item[4], cell),
    ])

tbl = Table(rows, colWidths=[2.4 * cm, 3.2 * cm, 3.1 * cm, 3.1 * cm, doc.width - 11.8 * cm], repeatRows=1)
tbl.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), LIGHT_BLUE),
    ("TEXTCOLOR", (0, 0), (-1, 0), BLUE),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("ALIGN", (0, 0), (-1, 0), "CENTER"),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, VERY_LIGHT]),
    ("GRID", (0, 0), (-1, -1), 0.5, GRAY),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("TOPPADDING", (0, 0), (-1, -1), 4),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ("LEFTPADDING", (0, 0), (-1, -1), 5),
    ("RIGHTPADDING", (0, 0), (-1, -1), 5),
]))
story.append(tbl)
story.append(Spacer(1, 0.5 * cm))

story.append(Paragraph("Documentation écrite", h1))

narrative = [
    "Le flux que j'ai choisi de cartographier est celui du traitement d'une demande interne de développement ou d'amélioration d'un module métier au sein du Pool Informatique / Cellule de Développement de l'INPP Haut-Katanga. J'ai retenu ce flux parce qu'il correspond à l'activité observée dans mon unité de stage et à mon rôle de stagiaire développeuse. Dans ce contexte, la transformation numérique avance à travers des demandes concrètes émises par les services lorsqu'un suivi manuel devient trop lourd, qu'un fichier Excel ne suffit plus ou qu'un rapport prend trop de temps à produire. La valeur est créée lorsque ce besoin opérationnel est capté, clarifié, transformé en solution numérique, testé puis réutilisé dans le travail quotidien.",
    "L'événement déclencheur est donc l'apparition d'un besoin métier précis. Il peut venir du service Formation, des Ressources Humaines, de la Direction ou d'un autre utilisateur interne. À ce stade, l'entrée du flux n'est pas encore une spécification technique, mais une demande exprimée oralement, par téléphone, par message WhatsApp ou parfois par e-mail. La première valeur ajoutée est l'explicitation du besoin. Les données générées à cette étape sont peu structurées : notes dans un cahier, message reçu, remarque faite en réunion ou consigne verbale. Elles existent, mais elles ne sont pas toujours centralisées dans un même support.",
    "La deuxième étape est la qualification de la demande par le Chef du Service Informatique. Le responsable vérifie si la demande relève bien du Pool IT, si elle est prioritaire et si elle peut être traitée dans l'immédiat. Le point de transfert de responsabilité est important ici, car on passe du service demandeur au service informatique. Cette étape apporte de la valeur en évitant que l'équipe technique ne travaille sur des demandes mal formulées ou non prioritaires. En pratique, cette qualification repose surtout sur des échanges directs et des notes manuelles ; je n'ai pas observé un outil formel unique de ticketing.",
    "Une fois la demande acceptée, la troisième étape consiste à analyser le besoin avec l'utilisateur métier. Avec l'encadreur direct ou un référent technique, je participe à la collecte des règles métier, à l'identification des champs nécessaires et à la compréhension du déroulement réel du travail. Les intrants sont la demande priorisée et les explications de l'utilisateur ; les extrants sont une description plus claire des écrans attendus, des données à saisir, des contrôles à faire et des résultats à produire. Les outils sont simples : observation, cahier de notes, échanges face à face, parfois Word ou Excel pour résumer les informations. La valeur ajoutée de cette étape est forte, car une mauvaise compréhension se répercute sur tout le reste du flux.",
    "La quatrième étape est la conception technique. Dans mon contexte de stage, elle prend la forme de diagrammes simples, de structuration des tables de base de données et de préparation logique des écrans. L'outil principal observé pour cette phase est StarUML, complété au besoin par des croquis papier ou des discussions courtes avec l'équipe. Ce passage est un autre point de transfert important : on quitte le langage du métier pour entrer dans celui de la solution informatique. Les données deviennent plus structurées, car elles se matérialisent en diagrammes, en listes de champs et en relations de base de données. Cette étape ajoute de la valeur en réduisant les ambiguïtés avant le développement.",
    "La cinquième étape est le développement interne du module. C'est le cœur productif du flux pour la Cellule de Développement. À partir des éléments conçus, je participe à l'implémentation des écrans, des formulaires, des requêtes et de la base de données avec PHP, HTML/CSS, MySQL et XAMPP. Les sorties deviennent tangibles : prototype fonctionnel, tables créées, écrans de saisie, affichage de rapports ou fonctions de mise à jour. À ce stade, les données techniques sont réellement capturées et stockées. La sixième étape est le test métier avec l'utilisateur, suivi des corrections. Le service demandeur vérifie si le prototype correspond au travail réel ; les retours sont généralement donnés à l'oral, par annotation ou pendant une démonstration locale, puis réinjectés dans le cycle de correction.",
    "La dernière étape est la mise en service locale et l'appui aux utilisateurs. Dans l'environnement observé, cette mise en service reste proche du terrain : installation sur un poste local, accompagnement direct des agents, petites explications d'usage et corrections si un incident apparaît. Le volume du flux n'est pas industrialisé ni suivi par un compteur formel ; il dépend des besoins exprimés par les services et de l'urgence du moment. Mon rôle se situe surtout entre l'analyse, la conception, le développement et les tests. Cette cartographie montre où la valeur est ajoutée, où les transferts de responsabilité ont lieu et où une future analyse de données pourrait plus tard s'insérer de manière pertinente.",
]

for paragraph in narrative:
    story.append(Paragraph(paragraph, body))


def page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 9)
    canvas.setFillColor(GRAY)
    canvas.drawCentredString(doc.pagesize[0] / 2, doc.bottomMargin - 0.8 * cm, f"{doc.page}")
    canvas.restoreState()


doc.build(story, onFirstPage=lambda c, d: None, onLaterPages=page_number)
print(f"PDF créé : {OUT}")