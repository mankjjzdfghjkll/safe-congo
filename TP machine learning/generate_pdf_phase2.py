"""
MAL1471 – Phase 2 – Data Landscape Analysis
Conforme au brief officiel + cohérent avec Phase 1(a) et Phase 1(b).
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, PageBreak, HRFlowable,
)
import os

BLUE       = colors.HexColor("#1a5276")
MID_BLUE   = colors.HexColor("#2471a3")
LIGHT_BLUE = colors.HexColor("#d6eaf8")
VERY_LIGHT = colors.HexColor("#f0f7fb")
GREEN      = colors.HexColor("#1e8449")
LIGHT_GRN  = colors.HexColor("#d5f5e3")
ORANGE     = colors.HexColor("#e67e22")
LIGHT_ORG  = colors.HexColor("#fdebd0")
GRAY       = colors.HexColor("#85929e")
BLACK      = colors.black
WHITE      = colors.white


def S(name, **kw):
    d = dict(fontName="Times-Roman", fontSize=11, leading=16,
             textColor=BLACK, spaceAfter=6)
    d.update(kw)
    return ParagraphStyle(name, **d)


body   = S("body", alignment=TA_JUSTIFY, spaceAfter=8)
h1     = S("h1", fontName="Times-Bold", fontSize=13, textColor=BLUE,
           spaceBefore=10, spaceAfter=6)
h2     = S("h2", fontName="Times-Bold", fontSize=11.5, textColor=MID_BLUE,
           spaceBefore=6, spaceAfter=4)
cell   = S("cell", fontName="Times-Roman", fontSize=8.5, leading=12)
cell_b = S("cell_b", fontName="Times-Bold", fontSize=8.5, leading=12)
label  = S("label", fontName="Helvetica-Bold", fontSize=8,
           alignment=TA_CENTER, textColor=BLUE)
bullet = S("bul", fontName="Times-Roman", fontSize=11, leading=16,
           alignment=TA_JUSTIFY, leftIndent=14, firstLineIndent=-14, spaceAfter=4)

# ── Inventaire : chaque source renvoie à une étape du VSM Phase 1(b) ─────────
INVENTORY = [
    {
        "vsm": "5 et 7",
        "source": "Base MySQL – module gestion des stagiaires",
        "contains": (
            "Fiches stagiaires (identité, entreprise d'origine, formation), "
            "présences séance par séance, notes d'évaluation par module, "
            "référentiel des entreprises partenaires. "
            "Générée lors du développement (étape 5) et enrichie en production (étape 7)."
        ),
        "format": "Relationnel – tables MySQL 8",
        "storage": "Instance XAMPP sur poste local dédié, réseau interne INPP HK",
        "owner": "Cellule de Développement (technique) ; Service Formation (métier)",
        "quality": (
            "Bonne pour les champs obligatoires de saisie (identité, dates, statut, notes). "
            "Champ motif d'absence souvent vide car les agents cochent seulement présent/absent. "
            "Sauvegarde manuelle hebdomadaire, sans entrepôt central."
        ),
    },
    {
        "vsm": "3",
        "source": "Documents Word / Excel – cahiers des charges métier",
        "contains": (
            "Règles de gestion, listes de champs, descriptions d'écrans attendus, "
            "comptes rendus de séances d'analyse avec les utilisateurs (Formation, RH)."
        ),
        "format": "Fichiers .docx et .xlsx",
        "storage": "Postes locaux des développeurs – pas de dépôt centralisé",
        "owner": "Cellule de Développement + encadreur de stage",
        "quality": (
            "Contenu riche mais hétérogène : un document par demande, formats variables, "
            "pas de schéma commun. Difficile à agréger automatiquement."
        ),
    },
    {
        "vsm": "4",
        "source": "Modèles StarUML (.mdj)",
        "contains": (
            "Diagrammes de classes, structures de tables prévues, relations entre entités "
            "métier avant codage."
        ),
        "format": "Fichiers binaires StarUML (.mdj)",
        "storage": "Postes locaux de la Cellule Dev",
        "owner": "Cellule de Développement",
        "quality": (
            "Fiable pour la conception d'un module donné, mais non lié automatiquement "
            "aux données de production. Métadonnées projet absentes (version, auteur, date)."
        ),
    },
    {
        "vsm": "2",
        "source": "Cahier de notes – qualification des demandes IT",
        "contains": (
            "Demandes reçues, niveau de priorité attribué, affectation à la Cellule Dev, "
            "notes de l'échange avec le service demandeur."
        ),
        "format": "Papier + retranscription partielle",
        "storage": "Cahier physique du Chef du Service Informatique",
        "owner": "Chef du Service Informatique",
        "quality": (
            "Partiellement capturée : seules les demandes jugées prioritaires sont notées. "
            "Pas de format structuré, pas de recherche possible, risque de perte."
        ),
    },
    {
        "vsm": "6",
        "source": "Retours de test utilisateur (démonstration XAMPP)",
        "contains": (
            "Observations des agents métier lors des sessions de test : corrections demandées, "
            "bugs signalés, validations fonctionnelles."
        ),
        "format": "Oral + annotations papier ponctuelles",
        "storage": "Non stocké de façon systématique",
        "owner": "Service demandeur + stagiaire (session de test)",
        "quality": (
            "Très faible traçabilité : les retours sont donnés à l'oral et implémentés "
            "directement sans journal structuré. Décisions non reproductibles."
        ),
    },
]

# ── Lacunes (gaps) identifiées dans le VSM Phase 1(b) ────────────────────────
GAPS = [
    {
        "vsm": "1",
        "gap": "Absence de capture formelle des demandes initiales",
        "detail": (
            "Les besoins arrivent par WhatsApp, appel téléphonique ou remarque en réunion. "
            "Aucun ticket, aucun identifiant de demande, aucun horodatage structuré n'est créé "
            "au point de déclenchement du flux (cf. Phase 1b, étape 1 – « données non capturées »)."
        ),
        "ml_enable": (
            "<b>Classification supervisée</b> de la priorité des demandes IT "
            "(haute / normale / basse) et <b>régression</b> du délai de traitement, "
            "si les champs suivants étaient capturés : service demandeur, type de besoin, "
            "urgence déclarée, date de soumission, responsable métier."
        ),
    },
    {
        "vsm": "6",
        "gap": "Absence de journal structuré des tests et corrections",
        "detail": (
            "Lors des démonstrations sur XAMPP, les retours utilisateurs ne sont pas consignés "
            "dans un système : pas d'identifiant de bug, pas de gravité, pas de statut de correction. "
            "Phase 1b identifiait cette étape comme zone de friction récurrente."
        ),
        "ml_enable": (
            "<b>Classification</b> du type de défaut (interface, logique métier, performance) "
            "et <b>régression</b> du nombre de cycles de correction par module, "
            "si chaque retour enregistrait : module concerné, description, gravité, "
            "date, auteur du retour, date de résolution."
        ),
    },
    {
        "vsm": "1 → 2",
        "gap": "Pas de lien traçable entre demande et livrable",
        "detail": (
            "Entre l'étape 1 (demande informelle) et l'étape 2 (qualification), "
            "aucun identifiant unique ne suit la demande jusqu'au module déployé. "
            "Impossible aujourd'hui de relier une demande WhatsApp au module MySQL résultant."
        ),
        "ml_enable": (
            "<b>Clustering</b> non supervisé des profils de demandes similaires "
            "(sans étiquette préalable) pour découvrir des familles de besoins récurrents, "
            "puis <b>classification</b> une fois un historique étiqueté constitué."
        ),
    },
]

# ── Tableau des opportunités ML ───────────────────────────────────────────────
OPPORTUNITIES = [
    ("S-01", "5 / 7", "Source", "MySQL stagiaires",
     "Classification binaire", "Supervisé",
     "Étiquette : statut (abandonné / terminé). Features : présences, notes intermédiaires, secteur entreprise.",
     "Élevée"),
    ("S-02", "5 / 7", "Source", "MySQL présences",
     "Détection d'anomalies", "Non supervisé",
     "Pas d'étiquette requise. Patterns d'absence atypiques par stagiaire ou par session.",
     "Moyenne"),
    ("S-03", "5 / 7", "Source", "MySQL évaluations",
     "Régression", "Supervisé",
     "Étiquette : note finale. Features : notes intermédiaires par module, assiduité.",
     "Moyenne"),
    ("G-01", "1", "Lacune", "Demandes non capturées (WhatsApp/oral)",
     "Classification", "Supervisé (si collecte mise en place)",
     "Étiquette : priorité. Nécessite création d'un formulaire de demande structuré.",
     "Faible (collecte à créer)"),
    ("G-02", "6", "Lacune", "Retours de test non journalisés",
     "Classification + régression", "Supervisé (si collecte mise en place)",
     "Étiquette : type de défaut / nombre de cycles. Nécessite un journal de tests.",
     "Faible (collecte à créer)"),
    ("G-03", "1 → 2", "Lacune", "Absence de lien demande–livrable",
     "Clustering", "Non supervisé",
     "Découverte de familles de demandes sans étiquette. Utile pour prioriser le backlog IT.",
     "Faible"),
]

OUT  = r"C:\Users\PC\Desktop\SAFE CONGO\TP machine learning\MANKAND-A-MUTEB_JOSEE_MAL1471_Phase2.pdf"
LOGO = r"C:\Users\PC\Desktop\logo-unh.png"

doc = SimpleDocTemplate(
    OUT, pagesize=A4,
    leftMargin=2.2 * cm, rightMargin=2.2 * cm,
    topMargin=1.8 * cm, bottomMargin=2.1 * cm,
    title="MAL1471 Phase 2 – Data Landscape",
    author="MANKAND-A-MUTEB JOSEE",
)
W = doc.width
story = []


def cov(txt, **kw):
    return Paragraph(txt, S("_c", alignment=TA_CENTER, **kw))


def styled_table(rows, col_widths, repeat=1):
    t = Table(rows, colWidths=col_widths, repeatRows=repeat)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), LIGHT_BLUE),
        ("TEXTCOLOR", (0, 0), (-1, 0), BLUE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, VERY_LIGHT]),
        ("GRID", (0, 0), (-1, -1), 0.4, GRAY),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t


# ══ PAGE DE GARDE ════════════════════════════════════════════════════════════
story.append(Spacer(1, 0.15 * cm))
if os.path.exists(LOGO):
    story.append(Table([[Image(LOGO, 6.6 * cm, 6.6 * cm, kind="proportional")]],
                       colWidths=[W], style=[("ALIGN", (0, 0), (-1, -1), "CENTER")]))
story.append(Spacer(1, 0.25 * cm))
story += [
    cov("UNIVERSITÉ NOUVEAUX HORIZONS", fontName="Helvetica-Bold", fontSize=15,
        textColor=BLUE, leading=20),
    cov("Faculté des Sciences Informatiques", fontName="Helvetica", fontSize=10.5, leading=15),
    Spacer(1, 0.7 * cm),
    cov("PROJET FINAL MAL1471 — 2026", fontName="Helvetica-Bold", fontSize=16.5,
        textColor=BLUE, leading=22),
    cov("Phase 2 : Analyse du paysage des données",
        fontName="Helvetica-Bold", fontSize=12.5, leading=17),
    Spacer(1, 0.65 * cm),
    cov("Dirigé par : Pr. EMMANUEL KALUNGA  |  Ass. ORTEGA-KABWE",
        fontName="Helvetica", fontSize=10.5, leading=16),
    Spacer(1, 0.5 * cm),
    cov("MANKAND-A-MUTEB JOSÉE", fontName="Helvetica-Bold", fontSize=12,
        textColor=BLUE, leading=17),
    cov("Matricule : SI/20223393  —  L4 Génie Logiciel", fontName="Helvetica",
        fontSize=10.5, leading=16),
    Spacer(1, 0.5 * cm),
    cov("Organisme : INPP – Direction Provinciale Haut-Katanga (Lubumbashi)",
        fontName="Helvetica", fontSize=10, leading=15),
    cov("Unité : Pool Informatique / Cellule de Développement",
        fontName="Helvetica", fontSize=10, leading=15),
    Spacer(1, 0.35 * cm),
    cov("Date de remise : 6 juin 2026", fontName="Helvetica", fontSize=10.5, leading=16),
    Spacer(1, 0.35 * cm),
    cov("Année Académique 2025-2026", fontName="Helvetica-Bold", fontSize=11.5, textColor=BLUE),
    Spacer(1, 0.4 * cm),
    HRFlowable(width=W, thickness=1.5, color=BLUE),
]
story.append(PageBreak())

# ══ INTRODUCTION ═════════════════════════════════════════════════════════════
story.append(Paragraph("Introduction", h1))
story.append(HRFlowable(width=W, thickness=0.8, color=LIGHT_BLUE, spaceAfter=6))
story.append(Paragraph(
    "La Phase 1(a) a décrit l'INPP Haut-Katanga : établissement public de formation "
    "professionnelle en transition numérique, où j'effectue mon stage en tant que "
    "<b>stagiaire développeuse</b> au sein du Pool Informatique / Cellule de Développement. "
    "La Phase 1(b) a cartographié le flux principal de traitement d'une demande interne "
    "de développement ou d'amélioration d'un module métier, en sept étapes (de la demande "
    "du besoin à la mise en service via XAMPP). "
    "La présente analyse adopte un autre angle : <b>les données</b> générées, consommées "
    "ou perdues à chaque étape de ce flux. Chaque source et chaque lacune ci-dessous "
    "est explicitement rattachée à une étape du VSM Phase 1(b). Il ne s'agit pas d'une "
    "modélisation : c'est un inventaire et une analyse des lacunes, fondation de la "
    "Phase 3.",
    body,
))
story.append(PageBreak())

# ══ 1. INVENTAIRE DES DONNÉES ════════════════════════════════════════════════
story.append(Paragraph("1. Inventaire des données (Data Inventory)", h1))
story.append(HRFlowable(width=W, thickness=0.8, color=LIGHT_BLUE, spaceAfter=4))
story.append(Paragraph(
    "Cinq sources majeures visibles dans la cartographie Phase 1(b). "
    "Les trois premières sont les plus structurées ; les deux dernières sont partiellement "
    "ou faiblement capturées, ce qui prépare l'analyse des lacunes.",
    body,
))

inv_hdr = [
    Paragraph("<b>Étape VSM</b>", label),
    Paragraph("<b>Source de données</b>", label),
    Paragraph("<b>Contenu</b>", label),
    Paragraph("<b>Format / Stockage</b>", label),
    Paragraph("<b>Propriétaire</b>", label),
    Paragraph("<b>Qualité</b>", label),
]
inv_rows = [inv_hdr]
cw = [1.1 * cm, 2.4 * cm, W - 1.1 * cm - 2.4 * cm - 3.8 * cm - 2.5 * cm - 3.5 * cm,
      3.8 * cm, 2.5 * cm, 3.5 * cm]
for s in INVENTORY:
    inv_rows.append([
        Paragraph(s["vsm"], cell_b),
        Paragraph(s["source"], cell_b),
        Paragraph(s["contains"], cell),
        Paragraph(f"{s['format']}<br/>{s['storage']}", cell),
        Paragraph(s["owner"], cell),
        Paragraph(s["quality"], cell),
    ])
story.append(styled_table(inv_rows, cw))
story.append(Spacer(1, 0.35 * cm))

note = Table([[
    Paragraph("<b>Source prioritaire observée (étapes 5 et 7)</b>", cell_b)],
    [Paragraph(
        "La base <b>MySQL du module stagiaires</b> est la seule source à la fois structurée, "
        "en production et directement liée à mon travail quotidien (développement PHP/MySQL "
        "sous XAMPP, administration via phpMyAdmin – cf. Phase 1a, section 5). "
        "Elle couvre les présences, les évaluations et les fiches d'entreprises partenaires "
        "mentionnées dans le questionnaire d'intégration INPP.",
        cell,
    )],
], colWidths=[W])
note.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), LIGHT_GRN),
    ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#f4fdf7")),
    ("BOX", (0, 0), (-1, -1), 0.8, GREEN),
    ("TOPPADDING", (0, 0), (-1, -1), 6),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ("LEFTPADDING", (0, 0), (-1, -1), 8),
]))
story.append(note)
story.append(PageBreak())

# ══ 2. ANALYSE DES LACUNES ═══════════════════════════════════════════════════
story.append(Paragraph("2. Analyse des lacunes (Data Gap Analysis)", h1))
story.append(HRFlowable(width=W, thickness=0.8, color=LIGHT_BLUE, spaceAfter=4))
story.append(Paragraph(
    "Trois lacunes identifiées dans le VSM Phase 1(b), aux points de friction "
    "que j'avais déjà signalés : capture des demandes (étape 1), centralisation "
    "des analyses (étape 3) et journal de tests (étape 6).",
    body,
))

for i, g in enumerate(GAPS, 1):
    story.append(Paragraph(f"2.{i} Lacune à l'étape VSM {g['vsm']}", h2))
    story.append(Paragraph(f"<b>Lacune :</b> {g['gap']}", body))
    story.append(Paragraph(g["detail"], body))
    story.append(Paragraph(f"<b>Ce que le ML permettrait si ces données étaient capturées :</b> {g['ml_enable']}", body))
    story.append(Spacer(1, 0.15 * cm))

story.append(PageBreak())

# ══ 3. TABLEAU DES OPPORTUNITÉS ML ═══════════════════════════════════════════
story.append(Paragraph("3. Tableau des opportunités ML (Data Opportunity Table)", h1))
story.append(HRFlowable(width=W, thickness=0.8, color=LIGHT_BLUE, spaceAfter=4))

opp_hdr = [
    Paragraph("<b>ID</b>", label),
    Paragraph("<b>Étape VSM</b>", label),
    Paragraph("<b>Type</b>", label),
    Paragraph("<b>Source / Lacune</b>", label),
    Paragraph("<b>Application ML</b>", label),
    Paragraph("<b>Supervisé ?</b>", label),
    Paragraph("<b>Étiquette / Features</b>", label),
    Paragraph("<b>Faisabilité</b>", label),
]
opp_rows = [opp_hdr]
ocw = [0.8 * cm, 1.1 * cm, 1.2 * cm, 2.5 * cm, 2.2 * cm, 1.5 * cm,
       W - 0.8 * cm - 1.1 * cm - 1.2 * cm - 2.5 * cm - 2.2 * cm - 1.5 * cm - 1.5 * cm,
       1.5 * cm]
for row in OPPORTUNITIES:
    opp_rows.append([Paragraph(str(c), cell_b if j == 0 else cell)
                     for j, c in enumerate(row)])
story.append(styled_table(opp_rows, ocw))
story.append(Spacer(1, 0.3 * cm))
story.append(Paragraph(
    "<b>Distinction supervisé / non supervisé :</b> les opportunités S-01 et S-03 "
    "requièrent une <b>étiquette connue</b> (statut d'abandon, note finale) — ce sont "
    "des problèmes supervisés. S-02 et G-03 n'exigent pas d'étiquette préalable : "
    "elles relèvent de l'<b>apprentissage non supervisé</b> (anomalies, clustering). "
    "Les lacunes G-01 et G-02 deviendraient supervisées uniquement après mise en place "
    "d'un mécanisme de collecte.",
    body,
))
story.append(PageBreak())

# ══ 4. PRIORISATION ══════════════════════════════════════════════════════════
story.append(Paragraph("4. Priorisation de l'opportunité ML la plus valorisable", h1))
story.append(HRFlowable(width=W, thickness=0.8, color=LIGHT_BLUE, spaceAfter=4))
story.append(Paragraph(
    "<b>Choix retenu : S-01 – Classification du risque d'abandon des stagiaires</b> "
    "(source MySQL, étapes 5 et 7 du VSM).",
    S("prio", fontName="Times-Bold", fontSize=11, textColor=GREEN, spaceAfter=8),
))
story.append(Paragraph("Justification selon quatre critères :", body))
story.append(Paragraph(
    "→ <b>Valeur métier :</b> l'INPP poursuit la qualité de la formation et la modernisation "
    "des outils (Phase 1a, mission observée). Réduire les abandons en cours de stage répond "
    "directement à la priorité du service Formation, utilisateur principal de mes modules.",
    bullet,
))
story.append(Paragraph(
    "→ <b>Disponibilité des données :</b> contrairement aux lacunes G-01 et G-02, "
    "aucune collecte supplémentaire n'est nécessaire. Les données existent déjà dans MySQL "
    "depuis le déploiement des modules (étape 7 – « base opérationnelle » en Phase 1b).",
    bullet,
))
story.append(Paragraph(
    "→ <b>Qualité et étiquette :</b> le champ <code>statut</code> (actif / terminé / abandonné) "
    "fournit une étiquette supervisée exploitable. Les features (présences, notes intermédiaires, "
    "secteur d'entreprise) sont co-saisies dans le même flux opérationnel.",
    bullet,
))
story.append(Paragraph(
    "→ <b>Faisabilité Phase 3 :</b> l'accès technique est réaliste dans le délai du projet "
    "(export CSV depuis phpMyAdmin, avec accord de mon encadreur). "
    "Les lacunes G-01/G-02 exigeraient de changer les pratiques organisationnelles "
    "(ticketing, journal de tests) — hors périmètre du stage.",
    bullet,
))
story.append(Spacer(1, 0.2 * cm))
story.append(Paragraph(
    "Les opportunités S-02 (anomalies de présence) et S-03 (régression sur les notes) "
    "restent des pistes secondaires sur la même source. Les lacunes G-01 à G-03 sont "
    "documentées comme opportunités futures, conditionnées à une évolution du flux VSM.",
    body,
))

story.append(Spacer(1, 0.4 * cm))
story.append(Paragraph(
    "<b>Réflexion personnelle :</b> En Phase 1(a), j'avais noté ne pas encore maîtriser "
    "la gouvernance des données (qui en est propriétaire, qui y accède). Cette Phase 2 "
    "m'a permis de répondre partiellement à ces questions : le Service Formation possède "
    "les données métier stagiaires, la Cellule Dev en assure la maintenance technique, "
    "et le Recouvrement garde ses fichiers Excel hors du flux IT cartographié. "
    "Je comprends maintenant pourquoi le brief insiste à relier chaque donnée à une étape "
    "du VSM : sans ce lien, on risque de proposer un modèle déconnecté du terrain réel "
    "de l'INPP Haut-Katanga.",
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
                           doc.bottomMargin - 0.65 * cm, f"Page {doc.page}")
    canvas.restoreState()


doc.build(story, onFirstPage=lambda c, d: None, onLaterPages=page_footer)
print(f"PDF genere : {OUT}")
