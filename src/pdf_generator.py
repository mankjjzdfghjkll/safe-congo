# src/pdf_generator.py
from datetime import datetime
from io import BytesIO

try:
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import cm
    from reportlab.graphics.shapes import Circle, Drawing, Polygon, Rect, String
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
    REPORTLAB_AVAILABLE = True
    REPORTLAB_IMPORT_ERROR = None
except ModuleNotFoundError as exc:
    colors = None
    TA_CENTER = None
    TA_LEFT = None
    A4 = None
    ParagraphStyle = None
    getSampleStyleSheet = None
    cm = None
    Circle = None
    Drawing = None
    Polygon = None
    Rect = None
    String = None
    Paragraph = None
    SimpleDocTemplate = None
    Spacer = None
    Table = None
    TableStyle = None
    REPORTLAB_AVAILABLE = False
    REPORTLAB_IMPORT_ERROR = exc


class BarrierMeasuresPDF:
    def _normalize_disease(self, disease):
        import re
        import unicodedata

        text = unicodedata.normalize("NFKD", str(disease or "")).encode("ascii", "ignore").decode("ascii")
        return re.sub(r"\s+", " ", text).strip().lower()

    def _disease_profile(self, disease):
        normalized = self._normalize_disease(disease)
        profiles = [
            {
                "match": ["cholera", "diarr sanglante", "diarrhee dhy m5"],
                "focus": "Priorite eau, hygiene, assainissement et rehydratation precoce.",
                "advice": "Renforcez l'eau traitee, la chloration, l'hygiene des mains et la reference rapide des cas deshydrates.",
                "measures": [
                    "Securiser l'eau de boisson et la chloration des points d'eau exposes.",
                    "Mettre en place un circuit de rehydratation orale et de reference des cas graves.",
                    "Desinfecter les surfaces, latrines et zones souillees avec une solution adaptee.",
                    "Sensibiliser sur le lavage des mains, l'eau traitee et l'alimentation sure.",
                ],
                "actions": [
                    ("0-6 h", "Verifier les points d'eau, latrines et stocks de SRO/chlore."),
                    ("6-24 h", "Rechercher activement les cas autour des foyers et sources d'eau exposees."),
                    ("24-48 h", "Documenter les besoins WASH et la capacite locale de prise en charge."),
                ],
                "checklist": [
                    ["Action", "Delai attendu", "Responsable cible"],
                    ["Verifier eau, latrines et chlore", "Immediat", "WASH / Zone"],
                    ["Assurer SRO et triage", "Meme jour", "Structure de sante"],
                    ["Sensibiliser les menages exposes", "Sous 24 heures", "Relais communautaires"],
                    ["Suivre les foyers hydriques", "Continu", "Surveillance / WASH"],
                ],
            },
            {
                "match": ["paludisme conf", "paludisme susp"],
                "focus": "Priorite diagnostic rapide, traitement precoce et lutte antivectorielle.",
                "advice": "Associez TDR, antipaludiques, moustiquaires impregnees et elimination des gites larvaires.",
                "measures": [
                    "Verifier la disponibilite des TDR et des antipaludiques de premiere ligne.",
                    "Distribuer et promouvoir l'utilisation correcte des moustiquaires impregnees.",
                    "Assainir les eaux stagnantes et renforcer la lutte antivectorielle autour des foyers.",
                    "Referer rapidement les formes graves et surveiller les groupes a risque.",
                ],
                "actions": [
                    ("0-12 h", "Verifier stocks de TDR/ACT et zones avec hausse inhabituelle des fievres."),
                    ("12-24 h", "Renforcer les messages sur moustiquaires et recours precoce aux soins."),
                    ("24-48 h", "Cibler les aires de sante avec foyers repetes pour des actions antivectorielles."),
                ],
                "checklist": [
                    ["Action", "Delai attendu", "Responsable cible"],
                    ["Verifier TDR et ACT", "Immediat", "Pharmacie / Zone"],
                    ["Identifier gites larvaires", "Meme jour", "Zone / Communaute"],
                    ["Renforcer moustiquaires", "Sous 24 heures", "Relais communautaires"],
                    ["Suivre les cas graves", "Continu", "Clinique / Reference"],
                ],
            },
            {
                "match": ["ira", "pneumonie", "grippe", "covid 19", "covid-19", "coqueluche", "diphterie"],
                "focus": "Priorite triage respiratoire, aeration et reduction des contacts rapproches.",
                "advice": "Le controle repose sur le triage, l'aeration, l'hygiene respiratoire et l'orientation rapide des formes graves.",
                "measures": [
                    "Mettre en place un triage respiratoire a l'arrivee et separer les patients symptomatiques.",
                    "Renforcer l'aeration, l'etiquette respiratoire et le port de protection selon le risque.",
                    "Verifier la disponibilite des intrants cliniques critiques et des EPI.",
                    "Orienter rapidement les detresses respiratoires vers la reference.",
                ],
                "actions": [
                    ("0-6 h", "Verifier triage, aeration et capacite d'orientation des cas graves."),
                    ("6-24 h", "Sensibiliser la communaute aux signes respiratoires prioritaires."),
                    ("24-48 h", "Suivre la pression sur les consultations et les intrants critiques."),
                ],
                "checklist": [
                    ["Action", "Delai attendu", "Responsable cible"],
                    ["Activer circuit respiratoire", "Immediat", "Structure de sante"],
                    ["Verifier EPI et intrants", "Meme jour", "Logistique / Clinique"],
                    ["Renforcer aeration et etiquette", "Sous 24 heures", "Equipes terrain"],
                    ["Suivre formes graves", "Continu", "Clinique / Zone"],
                ],
            },
            # --- Rougeole / PFA -------------------------------------------------
            {
                "match": ["rougeole", "pfa"],
                "focus": "Priorite verification vaccinale, confirmation rapide et mobilisation du programme PEV pour riposte ou enquete poliovirus.",
                "advice": "La riposte rougeole/PFA repose sur la confirmation, la couverture vaccinale et la coordination PEV. Tout cas AFP exige une investigation poliovirus.",
                "measures": [
                    "Verifier et documenter le statut vaccinal des cas et de leurs contacts proches.",
                    "Notifier immediatement les cas suspects au programme PEV et a la surveillance epidemiologique.",
                    "Organiser l'isolement respiratoire des cas rougeole et la recherche active des contacts non vaccines.",
                    "Activer une campagne de vaccination de rattrapage dans les zones de faible couverture.",
                ],
                "actions": [
                    ("0-12 h", "Confirmer le signal, evaluer la couverture vaccinale et les zones exposees."),
                    ("12-24 h", "Cartographier les poches a risque et notifier le programme PEV."),
                    ("24-48 h", "Coordonner la riposte vaccinale et investiguer les contacts non vaccines."),
                ],
                "checklist": [
                    ["Action", "Delai attendu", "Responsable cible"],
                    ["Confirmer et notifier PEV", "Immediat", "Surveillance / PEV"],
                    ["Verifier la couverture vaccinale", "Meme jour", "PEV / Zone"],
                    ["Isoler cas rougeole / enquete AFP", "Sous 12 heures", "Clinique / Epidemio"],
                    ["Planifier la riposte vaccinale", "Sous 48 heures", "PEV / Province"],
                    ["Suivre l'evolution du foyer", "Continu", "District / Province"],
                ],
            },
            # --- Tetanos neonatal / maternel ------------------------------------
            {
                "match": ["tnn", "tetanos materne"],
                "focus": "Priorite vaccination antitetanique (VAT) des femmes enceintes, accouchements propres et soins du cordon.",
                "advice": "La prevention du tetanos neonatal repose sur la vaccination VAT, les pratiques hygieniques d'accouchement et les soins propres du cordon ombilical.",
                "measures": [
                    "Verifier et renforcer la couverture en vaccin antitetanique (VAT) des femmes enceintes de la zone concernee.",
                    "Superviser et former les accoucheuses aux pratiques propres d'accouchement et de soins du cordon.",
                    "Sensibiliser les communautes sur le VAT antenatal, l'accouchement assiste et les soins neonataux.",
                    "Rechercher activement les cas dans les zones eloignees des structures de sante.",
                ],
                "actions": [
                    ("0-12 h", "Confirmer le cas, evaluer la couverture VAT locale et les pratiques d'accouchement."),
                    ("12-48 h", "Identifier les zones de faible couverture VAT et les accoucheuses non formees."),
                    ("48 h-1 sem", "Planifier une session de vaccination de rattrapage et renforcer la supervision."),
                ],
                "checklist": [
                    ["Action", "Delai attendu", "Responsable cible"],
                    ["Confirmer le cas et evaluer couverture VAT", "Immediat", "PEV / Zone"],
                    ["Cartographier la couverture VAT", "Sous 24 heures", "PEV / District"],
                    ["Superviser les accoucheuses", "Sous 48 heures", "Zone / District"],
                    ["Campagne de rattrapage VAT", "Sous 1 semaine", "PEV / Province"],
                    ["Surveiller les indicateurs neonataux", "Continu", "District / Province"],
                ],
            },
            # --- MAPI (manifestations post-vaccination) -------------------------
            {
                "match": ["mapi legeres", "mapi graves"],
                "focus": "Priorite pharmacovigilance, identification du lot incrimine, notification PEV et prise en charge clinique.",
                "advice": "Tout MAPI grave exige une notification immediate au programme PEV. Suspendre le lot implique en attendant les resultats de l'investigation.",
                "measures": [
                    "Notifier immediatement tout MAPI grave au programme national PEV et a l'autorite sanitaire.",
                    "Identifier et documenter les informations du lot de vaccin incrimine (numero, fabricant, date d'expiration).",
                    "Suspendre provisoirement l'utilisation du lot concerne dans toute la zone en attendant l'enquete.",
                    "Assurer la prise en charge clinique appropriee de la personne affectee selon les protocoles en vigueur.",
                ],
                "actions": [
                    ("0-6 h", "Notifier le PEV, documenter le lot et prendre en charge cliniquement le patient."),
                    ("6-24 h", "Rechercher d'autres cas lies au meme lot ou site; suspendre le lot provisoirement."),
                    ("24-72 h", "Coordonner avec le niveau national pour l'enquete et la decision definitive sur le lot."),
                ],
                "checklist": [
                    ["Action", "Delai attendu", "Responsable cible"],
                    ["Notifier PEV et documenter le lot", "Immediat", "Structure / PEV"],
                    ["Suspendre le lot provisoirement", "Meme jour", "PEV / District"],
                    ["Prise en charge clinique du patient", "Meme jour", "Structure de sante"],
                    ["Investigation lot et site de vaccination", "Sous 48 heures", "PEV / Pharmacovigilance"],
                    ["Rapport au niveau national / OMS", "Sous 72 heures", "Ministere / PEV"],
                ],
            },
            # --- Meningite -------------------------------------------------------
            {
                "match": ["meningite"],
                "focus": "Priorite prise en charge rapide, suivi des contacts et verification des besoins de prophylaxie.",
                "advice": "Le retard de prise en charge augmente le risque de deces et de sequelles neurologiques.",
                "measures": [
                    "Identifier rapidement les signes neurologiques d'alerte et referer les cas severes.",
                    "Renforcer les precautions respiratoires rapprochees et limiter la promiscuité.",
                    "Verifier la disponibilite des antibiotiques et kits de prise en charge.",
                    "Suivre les contacts proches selon le protocole local.",
                ],
                "actions": [
                    ("0-6 h", "Verifier triage, antibiotherapie initiale et capacite de reference."),
                    ("6-24 h", "Lister les contacts proches et les besoins en prophylaxie."),
                    ("24-48 h", "Suivre l'evolution du foyer et preparer l'escalade si necessaire."),
                ],
                "checklist": [
                    ["Action", "Delai attendu", "Responsable cible"],
                    ["Referer les cas severes", "Immediat", "Clinique / Zone"],
                    ["Verifier antibiotiques", "Meme jour", "Logistique / Structure"],
                    ["Documenter contacts proches", "Sous 24 heures", "Surveillance"],
                    ["Suivre l'evolution du foyer", "Continu", "District / Province"],
                ],
            },
            # --- Fievre typhoide -------------------------------------------------
            {
                "match": ["fievre typhoide"],
                "focus": "Priorite eau potable, hygiene alimentaire et recherche des sources communes.",
                "advice": "La riposte doit proteger les menages exposes et verifier rapidement les sources d'eau ou d'aliments communes.",
                "measures": [
                    "Promouvoir l'eau traitee, le lavage des mains et les aliments bien cuits.",
                    "Identifier les sources communes de contamination potentielle.",
                    "Verifier la disponibilite des traitements et la reference des formes compliquees.",
                    "Suivre les syndromes febriles digestifs dans la zone concernee.",
                ],
                "actions": [
                    ("0-12 h", "Verifier les foyers relies a une meme source et l'acces a l'eau traitee."),
                    ("12-24 h", "Sensibiliser sur l'hygiene alimentaire et l'eau sure."),
                    ("24-48 h", "Suivre les menages exposes et les signes de complication."),
                ],
                "checklist": [
                    ["Action", "Delai attendu", "Responsable cible"],
                    ["Identifier la source commune", "Immediat", "Surveillance / WASH"],
                    ["Promouvoir eau sure et hygiene", "Meme jour", "Communaute"],
                    ["Verifier traitements", "Sous 24 heures", "Clinique / Pharmacie"],
                    ["Suivre complications", "Continu", "Zone / District"],
                ],
            },
            # --- Monkeypox (Mpox) ------------------------------------------------
            {
                "match": ["monkeypox"],
                "focus": "Priorite isolement contact, tracage des contacts sur 21 jours, protection des soignants et lutte contre la zoonose.",
                "advice": "Le Mpox se transmet par contact rapproche avec les lesions ou les secretions. L'isolement precoce et le tracage des contacts sur 21 jours sont essentiels.",
                "measures": [
                    "Isoler immediatement les cas suspects dans une chambre individuelle avec precautions de contact.",
                    "Tracer et surveiller tous les contacts rapproches des 21 derniers jours avec suivi quotidien des symptomes.",
                    "Equiper les soignants d'EPI complet (masque FFP2, gants doubles, blouse, lunettes) pour tout soin.",
                    "Sensibiliser la communaute a eviter tout contact avec des animaux sauvages malades et les eruptions cutanees.",
                ],
                "actions": [
                    ("0-6 h", "Isoler le cas, notifier la coordination provinciale et activer le tracage des contacts."),
                    ("6-24 h", "Lister les contacts (21j) et verifier la disponibilite des EPI dans les structures."),
                    ("24-72 h", "Surveiller les contacts; coordonner avec le niveau national et l'OMS."),
                ],
                "checklist": [
                    ["Action", "Delai attendu", "Responsable cible"],
                    ["Isoler le cas et notifier", "Immediat", "Clinique / Zone"],
                    ["Equiper les soignants en EPI", "Meme jour", "Logistique / Clinique"],
                    ["Tracer les contacts (21 jours)", "Sous 12 heures", "Surveillance / Epidemio"],
                    ["Sensibiliser la communaute (zoonose)", "Sous 24 heures", "Relais communautaires"],
                    ["Rapport de situation quotidien", "Quotidien", "Province / OMS"],
                ],
            },
            # --- Chikungunya -----------------------------------------------------
            {
                "match": ["chikungunya"],
                "focus": "Priorite lutte vectorielle contre le moustique Aedes, protection individuelle et prise en charge symptomatique.",
                "advice": "Le chikungunya est transmis par les moustiques Aedes aegypti et albopictus. La suppression des gites larvaires et la protection individuelle sont centrales.",
                "measures": [
                    "Eliminer systematiquement les gites larvaires d'Aedes (eaux stagnantes, contenants, pneumatiques usages).",
                    "Promouvoir l'utilisation de moustiquaires impregnees, repulsifs cutanes et vetements couvrants.",
                    "Assurer la prise en charge symptomatique des cas (analgesiques, antipyretiques, hydratation).",
                    "Eviter l'aspirine et les AINS en presence de syndrome hemorragique ou de doute diagnostique.",
                ],
                "actions": [
                    ("0-12 h", "Confirmer le signal, identifier les zones de gites larvaires et les concentrations de cas."),
                    ("12-24 h", "Organiser une campagne d'elimination des gites et de protection vectorielle."),
                    ("24-48 h", "Suivre la tendance des cas et assurer l'acces aux traitements symptomatiques."),
                ],
                "checklist": [
                    ["Action", "Delai attendu", "Responsable cible"],
                    ["Confirmer et cartographier les cas", "Immediat", "Surveillance / Epidemio"],
                    ["Eliminer les gites larvaires", "Meme jour", "WASH / Communaute"],
                    ["Distribuer repulsifs et moustiquaires", "Sous 24 heures", "Zone / Logistique"],
                    ["Prise en charge symptomatique", "Continue", "Structures de sante"],
                    ["Suivre la tendance des cas", "Hebdomadaire", "District / Province"],
                ],
            },
            # --- Rage ------------------------------------------------------------
            {
                "match": ["rage"],
                "focus": "Priorite prophylaxie post-exposition (PEP) immediate, lavage de la plaie et neutralisation de l'animal mordeur.",
                "advice": "La rage est mortelle sans PEP. Toute morsure par un animal suspect doit etre traitee en urgence absolue. Le delai est critique.",
                "measures": [
                    "Initier immediatement le protocole de prophylaxie post-exposition (PEP) chez toute personne mordue par un animal suspect.",
                    "Nettoyer la plaie abondamment a l'eau courante et au savon pendant 15 minutes minimum, puis desinfecter.",
                    "Rechercher, capturer ou faire abattre l'animal mordeur pour observation veterinaire ou analyse.",
                    "Sensibiliser la population sur les risques de morsure animale et la conduite a tenir en urgence.",
                ],
                "actions": [
                    ("0-6 h", "Evaluer la plaie, initier le lavage et orienter vers la structure PEP la plus proche."),
                    ("6-24 h", "Administrer la premiere dose de vaccin antirabique (J0) et verifier les doses suivantes."),
                    ("24-72 h", "Suivre le patient, investiguer l'animal et evaluer les autres personnes exposees."),
                ],
                "checklist": [
                    ["Action", "Delai attendu", "Responsable cible"],
                    ["Laver la plaie 15 min et desinfecter", "Immediat", "Patient / Structure"],
                    ["Initier la PEP - vaccin antirabique J0", "Sous 6 heures", "Structure de sante"],
                    ["Evaluer et neutraliser l'animal", "Meme jour", "Zone / Veterinaire"],
                    ["Sensibiliser la communaute", "Sous 24 heures", "Relais / Zone"],
                    ["Suivre le calendrier PEP (J0/J3/J7/J14)", "Calendrier complet", "Clinique / District"],
                ],
            },
            # --- Deces maternels -------------------------------------------------
            {
                "match": ["deces maternels"],
                "focus": "Priorite audit immediat, renforcement des soins obstetricaux d'urgence (SOUB/SOUC) et analyse des causes evitables.",
                "advice": "Chaque deces maternel evitable exige un audit. La majorite est liee aux hemorragies, infections, eclampsie et retards de reference.",
                "measures": [
                    "Conduire un audit de deces maternel dans les 24 heures pour identifier les causes evitables et facteurs de retard.",
                    "Verifier la disponibilite et la fonctionnalite des soins obstetricaux d'urgence de base et complets (SOUB/SOUC).",
                    "Renforcer la chaine de reference obstetricale et la disponibilite du transport d'urgence.",
                    "Sensibiliser les communautes sur les signaux d'alerte de la grossesse et l'importance de l'accouchement assiste.",
                ],
                "actions": [
                    ("0-24 h", "Declarer le deces, conduire l'audit et identifier les mesures correctives immediates."),
                    ("24-72 h", "Cartographier les causes avec les equipes terrain et evaluer les SOUB/SOUC locaux."),
                    ("72 h-1 sem", "Partager les recommandations avec les structures et la coordination provinciale."),
                ],
                "checklist": [
                    ["Action", "Delai attendu", "Responsable cible"],
                    ["Declarer et investiguer le deces", "Immediat", "Structure / Zone"],
                    ["Audit de deces maternel", "Sous 24 heures", "Equipe soins / District"],
                    ["Verifier SOUB et SOUC", "Meme jour", "Zone / Coordination"],
                    ["Renforcer la reference obstetricale", "Sous 48 heures", "Zone / Province"],
                    ["Rapport de riposte et recommandations", "Sous 1 semaine", "Province / Ministere"],
                ],
            },
            # --- Maladies RSI / zero-tolerance (Fievre jaune, FHA, Peste, Dracunculose) ---
            {
                "match": ["fievre jaune", "fha", "peste", "dracunculose"],
                "focus": "Priorite notification immédiate au titre du RSI, isolement strict et mesures de containment specialisees.",
                "advice": "Ces maladies a notification obligatoire internationale demandent une reponse sans delai, un isolement strict et une coordination avec l'OMS.",
                "measures": [
                    "Notifier immediatement la chaine de commandement nationale et internationale (RSI) dans les 24 heures.",
                    "Appliquer l'isolement strict des cas et les precautions de contact, gouttelettes ou airborne selon la maladie.",
                    "Securiser les EPI de niveau maximum pour tout le personnel soignant et les equipes d'investigation.",
                    "Activer le plan de riposte specifique et coordonner avec les equipes provinciales, nationales et l'OMS.",
                ],
                "actions": [
                    ("0-6 h", "Confirmer le signal, notifier la hierarchie et proteger immediatement les personnes exposees."),
                    ("6-24 h", "Lister les expositions, activer le plan RSI et coordonner la riposte specialisee."),
                    ("24-48 h", "Securiser le suivi des contacts et preparer la communication officielle de crise."),
                ],
                "checklist": [
                    ["Action", "Delai attendu", "Responsable cible"],
                    ["Notifier la hierarchie et le RSI", "Immediat (0-24h)", "Zone / Ministere / OMS"],
                    ["Isoler le cas et proteger les exposes", "Meme jour", "Clinique / Zone"],
                    ["Securiser les EPI niveau maximum", "Sous 6 heures", "Logistique / Coordination"],
                    ["Activer le plan de riposte RSI", "Sous 12 heures", "Province / Ministere"],
                    ["Suivi des contacts et communication", "Continu", "Surveillance / OMS"],
                ],
            },
        ]

        for profile in profiles:
            if any(token in normalized for token in profile["match"]):
                return profile

        return {
            "focus": "Priorite prevention, surveillance rapprochee et coordination rapide autour du signal sanitaire.",
            "advice": "Adaptez ces mesures au mode de transmission suspecte, a la severite du signal et aux consignes officielles en vigueur.",
            "measures": [
                "Renforcer le signalement precoce des cas suspects et la verification quotidienne des donnees terrain.",
                "Appliquer strictement l'hygiene des mains et les precautions standards.",
                "Verifier les intrants essentiels et la capacite de reference locale.",
                "Informer rapidement la communaute des signes d'alerte et des conduites a tenir.",
            ],
            "actions": [
                ("0-12 h", "Confirmer le signal et verifier la capacite locale de reponse."),
                ("12-24 h", "Mettre a jour les consignes de prevention et l'information communautaire."),
                ("24-48 h", "Documenter les besoins et suivre l'evolution du signal."),
            ],
            "checklist": [
                ["Action", "Delai attendu", "Responsable cible"],
                ["Confirmer le signal", "Immediat", "Surveillance / Zone"],
                ["Verifier intrants et reference", "Meme jour", "Logistique / Clinique"],
                ["Informer la communaute", "Sous 24 heures", "Relais communautaires"],
                ["Suivre l'evolution des cas", "Continu", "District / Province"],
            ],
        }

    def _decorate_page(self, canvas, doc):
        canvas.saveState()
        page_width, _ = A4
        footer_y = 0.95 * cm
        separator_y = doc.bottomMargin - 0.28 * cm

        canvas.setStrokeColor(colors.HexColor("#d9e6f2"))
        canvas.setLineWidth(0.6)
        canvas.line(doc.leftMargin, separator_y, page_width - doc.rightMargin, separator_y)

        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#6d8398"))
        canvas.drawString(doc.leftMargin, footer_y, "SAFE CONGO | Surveillance epidemiologique")
        canvas.drawRightString(page_width - doc.rightMargin, footer_y, f"Page {canvas.getPageNumber()}")
        canvas.restoreState()

    def _sinusoidal_band(self, width=None, height=None):
        width = width if width is not None else 18.2 * cm
        height = height if height is not None else 1.0 * cm
        from reportlab.graphics.shapes import Path
        drawing = Drawing(width, height)
        drawing.add(Rect(0, 0, width, height, fillColor=colors.HexColor("#0b4d95"), strokeColor=colors.HexColor("#0b4d95")))

        wave_specs = [
            (height * 0.68, height * 0.22, colors.HexColor("#f8fbff"), 1.3),
            (height * 0.50, height * 0.18, colors.HexColor("#fcd116"), 1.0),
            (height * 0.32, height * 0.20, colors.HexColor("#ce1126"), 1.0),
        ]
        for baseline, amplitude, wave_color, stroke_width in wave_specs:
            path = Path()
            path.moveTo(0, baseline)
            for i in range(0, int(width) + 20, 24):
                x1 = i
                x2 = min(i + 24, width)
                y1 = baseline + (amplitude if (i // 24) % 2 == 0 else -amplitude)
                y2 = baseline + (amplitude if ((i // 24) + 1) % 2 == 0 else -amplitude)
                path.curveTo(x1 + 8, y1, x2 - 8, y2, x2, baseline)
            path.strokeColor = wave_color
            path.strokeWidth = stroke_width
            path.fillColor = None
            drawing.add(path)
        return drawing

    def _build_logo(self, size=None):
        size = size if size is not None else 2.2 * cm
        from reportlab.graphics.shapes import Path

        drawing = Drawing(size, size)
        cx = size / 2
        cy = size / 2

        drawing.add(Circle(cx, cy, size * 0.48, fillColor=colors.HexColor("#eff7ff"), strokeColor=colors.HexColor("#c8ddf2"), strokeWidth=1.0))
        drawing.add(Circle(cx, cy, size * 0.42, fillColor=None, strokeColor=colors.HexColor("#d4e7f8"), strokeWidth=0.8))
        drawing.add(Circle(cx, cy, size * 0.40, fillColor=colors.HexColor("#f9fcff"), strokeColor=colors.HexColor("#d4e7f8"), strokeWidth=0.6))

        outer_shield = Polygon([
            cx, size * 0.12,
            size * 0.82, size * 0.28,
            size * 0.82, size * 0.56,
            cx, size * 0.88,
            size * 0.18, size * 0.56,
            size * 0.18, size * 0.28,
        ], fillColor=colors.HexColor("#e9f6ff"), strokeColor=colors.HexColor("#8ebfe5"), strokeWidth=1.1)
        inner_shield = Polygon([
            cx, size * 0.22,
            size * 0.70, size * 0.34,
            size * 0.70, size * 0.53,
            cx, size * 0.72,
            size * 0.30, size * 0.53,
            size * 0.30, size * 0.34,
        ], fillColor=colors.HexColor("#0a5fab"), strokeColor=colors.HexColor("#0a4c95"), strokeWidth=0.9)
        drawing.add(outer_shield)
        drawing.add(inner_shield)

        wave_lines = [
            (colors.HexColor("#fcd116"), [size * 0.22, size * 0.44, size * 0.30, size * 0.44, size * 0.34, size * 0.36, size * 0.39, size * 0.54, size * 0.44, size * 0.44, size * 0.56, size * 0.44]),
            (colors.HexColor("#0055b8"), [size * 0.34, size * 0.44, size * 0.42, size * 0.44, size * 0.46, size * 0.36, size * 0.51, size * 0.54, size * 0.56, size * 0.44, size * 0.68, size * 0.44]),
            (colors.HexColor("#ce1126"), [size * 0.46, size * 0.44, size * 0.54, size * 0.44, size * 0.58, size * 0.36, size * 0.63, size * 0.54, size * 0.68, size * 0.44, size * 0.78, size * 0.44]),
        ]
        for stroke, points in wave_lines:
            path = Path()
            path.moveTo(points[0], points[1])
            for index in range(2, len(points), 2):
                path.lineTo(points[index], points[index + 1])
            path.strokeColor = stroke
            path.strokeWidth = 1.8
            path.fillColor = None
            drawing.add(path)

        drawing.add(Rect(size * 0.47, size * 0.50, size * 0.06, size * 0.15, fillColor=colors.white, strokeColor=colors.white))
        drawing.add(Rect(size * 0.42, size * 0.55, size * 0.16, size * 0.06, fillColor=colors.white, strokeColor=colors.white))
        drawing.add(String(cx, size * 0.05, "SAFE CONGO", textAnchor="middle", fillColor=colors.HexColor("#0f3f73"), fontName="Helvetica-Bold", fontSize=5.0))
        return drawing

    def _build_header(self, title_style, subtitle_style, title, subtitle):
        logo = self._build_logo(2.6 * cm)
        brand_label = Paragraph(
            "<font size='9' color='#0a5fab'><b>SAFE CONGO</b></font><br/><font size='18' color='#0f3f73'><b>%s</b></font>" % title,
            title_style,
        )
        subtitle_paragraph = Paragraph(subtitle, subtitle_style)
        stamp = Paragraph(
            f"Edition automatique du {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            ParagraphStyle(
                "HeaderStamp",
                parent=subtitle_style,
                fontSize=8.5,
                leading=11,
                textColor=colors.HexColor("#6d8398"),
            ),
        )
        text_table = Table([[brand_label], [subtitle_paragraph], [stamp]], colWidths=[13.8 * cm])
        text_table.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ]))

        header_table = Table([[logo, text_table]], colWidths=[3.0 * cm, 13.8 * cm])
        header_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.white),
            ("BOX", (0, 0), (-1, -1), 0.7, colors.HexColor("#d9e6f2")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 12),
            ("RIGHTPADDING", (0, 0), (-1, -1), 12),
            ("TOPPADDING", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ]))
        return [header_table, Spacer(1, 8), self._sinusoidal_band(16.8 * cm, 0.75 * cm)]

    def _catalog_table(self, title, rows, col_widths):
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "CatalogSectionTitle",
            parent=styles["Heading3"],
            fontSize=12,
            leading=15,
            textColor=colors.HexColor("#123e6b"),
            spaceAfter=8,
        )
        body_style = ParagraphStyle(
            "CatalogBody",
            parent=styles["Normal"],
            fontSize=8.8,
            leading=12,
            textColor=colors.HexColor("#41576f"),
            alignment=TA_LEFT,
        )
        content = [[Paragraph(title, title_style)]]
        if rows:
            content.extend([[Paragraph(str(value), body_style)] for value in rows])
        else:
            content.append([Paragraph("Aucune valeur disponible.", body_style)])

        table = Table(content, colWidths=col_widths, repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f3f73")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#d9e6f2")),
            ("INNERGRID", (0, 1), (-1, -1), 0.3, colors.HexColor("#e4edf7")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7fbff")]),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ]))
        return table

    def _append_catalog_section(self, story, title, rows, width):
        section_table = self._catalog_table(title, rows, [width])
        story.append(section_table)
        story.append(Spacer(1, 10))

    def _severity_palette(self, alert_level):
        normalized = (alert_level or "").upper()
        if normalized == "CRITIQUE":
            return {
                "accent": colors.HexColor("#b91c1c"),
                "soft": colors.HexColor("#fee2e2"),
                "band": colors.HexColor("#7f1d1d"),
            }
        if normalized == "HAUTE":
            return {
                "accent": colors.HexColor("#c2410c"),
                "soft": colors.HexColor("#ffedd5"),
                "band": colors.HexColor("#9a3412"),
            }
        if normalized == "MODEREE":
            return {
                "accent": colors.HexColor("#a16207"),
                "soft": colors.HexColor("#fef3c7"),
                "band": colors.HexColor("#854d0e"),
            }
        return {
            "accent": colors.HexColor("#0a5fab"),
            "soft": colors.HexColor("#dbeafe"),
            "band": colors.HexColor("#0b4d95"),
        }

    def _confidence_label(self, r2_score):
        if r2_score is None:
            return "Indisponible"
        if r2_score >= 0.80:
            return "Tres bonne"
        if r2_score >= 0.65:
            return "Bonne"
        if r2_score >= 0.50:
            return "Acceptable"
        return "Faible"

    def _recommended_measures(self, disease, alert_level):
        profile = self._disease_profile(disease)
        common = [
            "Laver frequemment les mains a l'eau et au savon ou avec une solution hydroalcoolique.",
            "Renforcer la sensibilisation communautaire et le signalement precoce des cas suspects.",
            "Mettre a jour quotidiennement le suivi des cas, deces et contacts dans la zone concernee.",
            "Verifier la disponibilite des intrants essentiels dans les structures de sante de reference.",
        ]
        specific = {
            "CRITIQUE": [
                "Activer immediatement une cellule locale de riposte et notifier la hierarchie sanitaire.",
                "Isoler sans delai les cas suspects et renforcer le triage dans les structures de soins.",
                "Preparer un plan rapide d'investigation de terrain et de communication de crise.",
            ],
            "HAUTE": [
                "Augmenter la frequence de surveillance dans les aires de sante les plus exposees.",
                "Coordonner avec les equipes terrain pour confirmer l'evolution du signal dans les 24 heures.",
                "Prepositionner les equipements de protection et les kits essentiels dans la zone concernee.",
            ],
            "MODEREE": [
                "Surveiller l'evolution hebdomadaire et verifier la qualite des donnees remontees.",
                "Renforcer les messages de prevention dans la communaute et les structures de premiere ligne.",
            ],
        }
        return profile["measures"] + specific.get((alert_level or "").upper(), ["Maintenir une veille rapprochee et confirmer les prochains points de donnees."]) + common

    def _priority_actions(self, disease, alert_level):
        profile = self._disease_profile(disease)
        actions = {
            "CRITIQUE": [
                ("0-6 h", "Confirmer le signal, activer la chaine d'alerte et notifier la coordination provinciale."),
                ("6-24 h", "Mettre en place le triage, l'isolement fonctionnel et la communication de risque."),
                ("24-48 h", "Documenter les besoins critiques en intrants, ressources humaines et supervision."),
            ],
            "HAUTE": [
                ("0-12 h", "Verifier la coherence des donnees et confirmer la hausse avec les equipes terrain."),
                ("12-24 h", "Renforcer la veille communautaire et les messages de prevention cibles."),
                ("24-48 h", "Prepositionner les intrants et preparer une escalation si la tendance persiste."),
            ],
            "MODEREE": [
                ("24 h", "Confirmer la qualite des donnees et identifier les aires de sante les plus exposees."),
                ("48 h", "Renforcer la prevention locale et suivre l'evolution des cas signales."),
                ("72 h", "Mettre a jour la situation et maintenir une veille rapprochee."),
            ],
        }
        return actions.get((alert_level or "").upper(), [
            ("24 h", "Maintenir la surveillance de routine et confirmer les prochains signaux utiles."),
            ("48 h", "Verifier la qualite de la remontee d'information."),
            ("72 h", "Mettre a jour la synthese et les consignes si necessaire."),
        ]) + profile["actions"]

    def _measure_rows(self, disease, alert_level, body_style):
        objectives = [
            "Limiter la transmission et proteger les cas suspects.",
            "Mieux detecter et documenter les nouveaux signaux.",
            "Maintenir la continuite des soins et des intrants.",
            "Renforcer la prevention communautaire.",
            "Assurer une coordination et un reporting reguliers.",
        ]
        rows = [["Priorite", "Mesure barriere", "Objectif"]]
        for index, measure in enumerate(self._recommended_measures(disease, alert_level), start=1):
            priority = "Immediate" if index <= 3 else ("Renforcee" if index <= 5 else "Suivi")
            objective = objectives[min(index - 1, len(objectives) - 1)]
            rows.append([
                priority,
                Paragraph(measure, body_style),
                Paragraph(objective, body_style),
            ])
        return rows

    def _paragraph_cells(self, row, style, header=False):
        cells = []
        for value in row:
            text = str(value or "")
            if header:
                cells.append(Paragraph(f"<b>{text}</b>", style))
            else:
                cells.append(Paragraph(text, style))
        return cells

    def _flyer_action_grid(self, disease, alert_level, body_style):
        measures = self._recommended_measures(disease, alert_level)
        blocks = [
            ("01 | PROTEGER", measures[0] if len(measures) > 0 else "Proteger les personnes exposees et les cas suspects."),
            ("02 | SIGNALER", measures[1] if len(measures) > 1 else "Signaler rapidement tout nouveau cas suspect aux equipes competentes."),
            ("03 | ISOLER", measures[2] if len(measures) > 2 else "Limiter les contacts et organiser une prise en charge adaptee."),
            ("04 | PREVENIR", measures[3] if len(measures) > 3 else "Renforcer les gestes barrieres et la sensibilisation communautaire."),
        ]
        cards = []
        for title, text in blocks:
            card = Table(
                [[Paragraph(f"<b>{title}</b>", body_style)], [Paragraph(text, body_style)]],
                colWidths=[8.0 * cm],
            )
            card.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.white),
                ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#d9e6f2")),
                ("LINEBELOW", (0, 0), (-1, 0), 1.0, colors.HexColor("#0a5fab")),
                ("TOPPADDING", (0, 0), (-1, -1), 9),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ]))
            cards.append(card)
        grid = Table([[cards[0], cards[1]], [cards[2], cards[3]]], colWidths=[8.2 * cm, 8.2 * cm])
        grid.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ]))
        return grid

    def generate_alert_pdf(self, disease, province, zone_sante, current_cases, predicted_cases, growth_rate, alert_level, r2_score, week=None, year=None):
        if not REPORTLAB_AVAILABLE:
            raise RuntimeError("Le moteur PDF ReportLab n'est pas disponible dans cet environnement.") from REPORTLAB_IMPORT_ERROR
        palette = self._severity_palette(alert_level)
        profile = self._disease_profile(disease)
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1.6 * cm, bottomMargin=1.6 * cm, leftMargin=1.7 * cm, rightMargin=1.7 * cm)
        styles = getSampleStyleSheet()
        story = []

        title_style = ParagraphStyle("PdfTitle", parent=styles["Heading1"], fontSize=18, leading=22, textColor=colors.HexColor("#0f3f73"), alignment=TA_LEFT, spaceAfter=2)
        subtitle_style = ParagraphStyle("PdfSubtitle", parent=styles["Normal"], fontSize=9.8, leading=13, textColor=colors.HexColor("#5e7691"), alignment=TA_LEFT, spaceAfter=6)
        section_style = ParagraphStyle("PdfSection", parent=styles["Heading3"], fontSize=12.5, leading=16, textColor=colors.HexColor("#123e6b"), spaceAfter=8)
        body_style = ParagraphStyle("PdfBody", parent=styles["Normal"], fontSize=9.5, leading=14, textColor=colors.HexColor("#41576f"), alignment=TA_LEFT)
        table_body_style = ParagraphStyle("PdfTableBody", parent=body_style, fontSize=8.9, leading=12.2, wordWrap="CJK")
        table_header_style = ParagraphStyle("PdfTableHeader", parent=body_style, fontSize=8.5, leading=11, textColor=colors.white, alignment=TA_LEFT, wordWrap="CJK")
        compact_style = ParagraphStyle("PdfCompact", parent=body_style, fontSize=8.5, leading=11.5, wordWrap="CJK")
        footer_style = ParagraphStyle("PdfFooter", parent=styles["Normal"], fontSize=7.8, leading=11, textColor=colors.HexColor("#7a8ca0"), alignment=TA_CENTER)
        badge_style = ParagraphStyle("Badge", parent=styles["Heading2"], alignment=TA_CENTER, textColor=colors.white, fontSize=14, leading=17)
        kicker_style = ParagraphStyle("Kicker", parent=body_style, fontSize=8.5, leading=10, textColor=colors.HexColor("#0a5fab"))
        callout_style = ParagraphStyle("Callout", parent=styles["Heading2"], fontSize=15, leading=18, textColor=palette["accent"])
        epi_value_style = ParagraphStyle("EpiValue", parent=styles["Heading2"], fontSize=12, leading=15, textColor=palette["accent"])

        for elt in self._build_header(title_style, subtitle_style, "Mesures barrieres terrain", "Document de riposte structure pour lecture rapide, coordination et action immediate."):
            story.append(elt)
        story.append(Spacer(1, 12))

        display_level = "INFO" if (alert_level or "").upper() == "NOUVELLE_DONNEE" else (alert_level or "INFO")
        growth_sign = "+" if growth_rate > 0 else ""
        growth_display_raw = f"{growth_sign}{growth_rate:.1f}%" if growth_rate != 0 else "—"
        if growth_rate > 0:
            growth_display = f"<font color='#b91c1c'>{growth_display_raw}</font>"
        elif growth_rate < 0:
            growth_display = f"<font color='#15803d'>{growth_display_raw}</font>"
        else:
            growth_display = growth_display_raw
        confidence = self._confidence_label(r2_score)
        period_display = f"Sem. {int(week)}/{int(year)}" if week is not None and year is not None else "—"
        pred_display = f"{predicted_cases:,}" if predicted_cases and predicted_cases > 0 else "—"
        severity_banner = Table(
            [[Paragraph(f"ALERTE {display_level}", badge_style)]],
            colWidths=[16.8 * cm],
        )
        severity_banner.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), palette["band"]),
            ("BOX", (0, 0), (-1, -1), 0, palette["band"]),
            ("TOPPADDING", (0, 0), (-1, -1), 9),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
        ]))
        story.append(severity_banner)
        story.append(Spacer(1, 14))

        top_strip = Table(
            [[
                Table([[Paragraph("<b>MALADIE</b>", kicker_style)], [Paragraph(disease, callout_style)]], colWidths=[5.35 * cm]),
                Table([[Paragraph("<b>ZONE</b>", kicker_style)], [Paragraph(zone_sante, callout_style)]], colWidths=[5.35 * cm]),
                Table([[Paragraph("<b>CAS OBSERVES</b>", kicker_style)], [Paragraph(f"{current_cases:,}", callout_style)]], colWidths=[5.35 * cm]),
            ]],
            colWidths=[5.6 * cm, 5.6 * cm, 5.6 * cm],
        )
        top_strip.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ]))
        for idx in range(3):
            top_strip._cellvalues[0][idx].setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.white),
                ("BOX", (0, 0), (-1, -1), 0.7, colors.HexColor("#d9e6f2")),
                ("TOPPADDING", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ]))
        story.append(top_strip)
        story.append(Spacer(1, 8))

        epi_col_w = 4.2 * cm
        epi_items = [
            ("<b>PROJECTION IA</b>", pred_display),
            ("<b>EVOLUTION</b>", growth_display),
            ("<b>FIABILITE IA</b>", confidence),
            ("<b>PERIODE</b>", period_display),
        ]
        epi_cells = []
        for epi_kicker, epi_value in epi_items:
            epi_cell = Table(
                [[Paragraph(epi_kicker, kicker_style)], [Paragraph(epi_value, epi_value_style)]],
                colWidths=[epi_col_w],
            )
            epi_cell.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f7fbff")),
                ("BOX", (0, 0), (-1, -1), 0.7, colors.HexColor("#d9e6f2")),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ]))
            epi_cells.append(epi_cell)
        epi_strip = Table([epi_cells], colWidths=[epi_col_w] * 4)
        epi_strip.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ]))
        story.append(epi_strip)
        story.append(Spacer(1, 14))

        story.append(Paragraph("Resume executif", section_style))
        executive_copy = (
            f"SAFE CONGO signale une situation de niveau <b>{display_level}</b> pour <b>{disease}</b> dans la zone de sante de <b>{zone_sante}</b>, province de <b>{province}</b>. "
            f"Cette fiche fournit des mesures barrieres specifiees pour cette maladie, des priorites de coordination et une checklist terrain pour soutenir la riposte locale. "
            f"<br/><br/><b>Focus sanitaire :</b> {profile['focus']}"
            f"<br/><br/>Volume observe : <b>{current_cases:,}</b> cas | Projection IA : <b>{pred_display}</b> cas | Evolution : <b>{growth_display_raw}</b> | Fiabilite modele : <b>{confidence}</b>. "
            f"Ces donnees doivent etre confirmees par la surveillance sanitaire officielle."
        )
        story.append(Paragraph(executive_copy, body_style))
        story.append(Spacer(1, 12))

        identity_box = Table(
            [[Paragraph(f"<b>Province :</b> {province}<br/><b>Periode :</b> {period_display}<br/><b>Date d'emission :</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}<br/><b>Priorite :</b> {display_level}", body_style)]],
            colWidths=[16.8 * cm],
        )
        identity_box.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f7fbff")),
            ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#d9e6f2")),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ("TOPPADDING", (0, 0), (-1, -1), 9),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
        ]))
        story.append(identity_box)
        story.append(Spacer(1, 12))

        story.append(Paragraph("Consignes rapides", section_style))
        story.append(self._flyer_action_grid(disease, display_level, body_style))
        story.append(Spacer(1, 14))

        priority_lines = "<br/>".join(
            [f"<b>{slot}</b> - {action}" for slot, action in self._priority_actions(disease, display_level)]
        )
        essential_table = Table(
            [[Paragraph(f"<b>Priorites de coordination</b><br/>{priority_lines}", body_style)]],
            colWidths=[16.8 * cm],
        )
        essential_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), palette["soft"]),
            ("BOX", (0, 0), (-1, -1), 0.6, palette["accent"]),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ]))
        story.append(essential_table)
        story.append(Spacer(1, 12))

        story.append(Paragraph(f"Mesures barrieres detaillees - {disease}", section_style))
        measures_rows = self._measure_rows(disease, display_level, table_body_style)
        measures_rows[0] = self._paragraph_cells(measures_rows[0], table_header_style, header=False)
        measures_table = Table(measures_rows, colWidths=[2.4 * cm, 8.8 * cm, 5.6 * cm], repeatRows=1)
        measures_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), palette["accent"]),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BOX", (0, 0), (-1, -1), 0.7, colors.HexColor("#d9e6f2")),
            ("INNERGRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#e4edf7")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, palette["soft"]]),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ]))
        story.append(measures_table)
        story.append(Spacer(1, 14))

        story.append(Paragraph(f"Checklist operationnelle - {disease}", section_style))
        checklist = profile["checklist"]
        checklist_rows = [self._paragraph_cells(checklist[0], table_header_style)]
        checklist_rows.extend(self._paragraph_cells(row, compact_style) for row in checklist[1:])
        checklist_table = Table(checklist_rows, colWidths=[8.6 * cm, 3.6 * cm, 4.6 * cm], repeatRows=1)
        checklist_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f3f73")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BOX", (0, 0), (-1, -1), 0.7, colors.HexColor("#d9e6f2")),
            ("INNERGRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#e4edf7")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7fbff")]),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ]))
        story.append(checklist_table)
        story.append(Spacer(1, 14))

        advice_box = Table(
            [[Paragraph(f"<b>Conseil SAFE CONGO</b><br/>{profile['advice']} Cette fiche soutient la coordination terrain et la prevention immediate.", body_style)]],
            colWidths=[16.8 * cm],
        )
        advice_box.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f7fbff")),
            ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#d9e6f2")),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ("TOPPADDING", (0, 0), (-1, -1), 9),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
        ]))
        story.append(advice_box)
        story.append(Spacer(1, 18))

        story.append(Paragraph(f"Document emis par SAFE CONGO le {datetime.now().strftime('%d/%m/%Y a %H:%M')}", footer_style))
        story.append(Paragraph("Ce bulletin soutient la decision mais ne remplace pas les consignes officielles du systeme de sante.", footer_style))

        doc.title = f"SAFE CONGO - Mesures barrieres {display_level} {disease} {period_display}"
        doc.author = "SAFE CONGO"
        doc.subject = "Mesures barrieres terrain"
        doc.build(story, onFirstPage=self._decorate_page, onLaterPages=self._decorate_page)
        buffer.seek(0)
        return buffer.getvalue()

    def generate_reference_catalog_pdf(self, diseases, provinces, zones, selected_province=None):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1.6 * cm, bottomMargin=1.6 * cm, leftMargin=1.4 * cm, rightMargin=1.4 * cm)
        styles = getSampleStyleSheet()
        story = []

        title_style = ParagraphStyle(
            "ReferenceTitle",
            parent=styles["Heading1"],
            fontSize=20,
            leading=24,
            textColor=colors.HexColor("#0f3f73"),
            alignment=TA_CENTER,
            spaceAfter=4,
        )
        subtitle_style = ParagraphStyle(
            "ReferenceSubtitle",
            parent=styles["Normal"],
            fontSize=9.5,
            leading=13,
            textColor=colors.HexColor("#5e7691"),
            alignment=TA_CENTER,
            spaceAfter=14,
        )
        body_style = ParagraphStyle(
            "ReferenceBody",
            parent=styles["Normal"],
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#41576f"),
            alignment=TA_LEFT,
        )
        section_style = ParagraphStyle(
            "ReferenceSection",
            parent=styles["Heading3"],
            fontSize=11.5,
            leading=14,
            textColor=colors.HexColor("#123e6b"),
            spaceAfter=6,
        )

        for elt in self._build_header(title_style, subtitle_style, "Referentiel dataset", "Vue de controle pour les maladies, provinces et zones de sante disponibles."):
            story.append(elt)
        story.append(Spacer(1, 12))
        story.append(
            Paragraph(
                f"Generation du {datetime.now().strftime('%d/%m/%Y %H:%M')} | Filtre province: {selected_province or 'Toutes les provinces'}",
                subtitle_style,
            )
        )
        story.append(
            Paragraph(
                f"Le dataset de reference contient {len(diseases)} maladies, {len(provinces)} provinces et {len(zones)} zones de sante pour la vue selectionnee.",
                body_style,
            )
        )
        story.append(Spacer(1, 12))

        story.append(Spacer(1, 10))
        story.append(Paragraph("Essentiel", section_style))
        essentials = [
            ["Indicateur", "Valeur", "Lecture rapide"],
            ["Maladies", str(len(diseases)), "Nomenclature epidemiologique active"],
            ["Provinces", str(len(provinces)), "Couverture administrative suivie"],
            ["Zones de sante", str(len(zones)), "Granularite terrain disponible"],
        ]
        essentials_table = Table(essentials, colWidths=[4.4 * cm, 3.2 * cm, 10.6 * cm])
        essentials_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f3f73")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BACKGROUND", (0, 1), (-1, -1), colors.white),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7fbff")]),
            ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#d9e6f2")),
            ("INNERGRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#e4edf7")),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ]))
        story.append(essentials_table)
        story.append(Spacer(1, 12))

        max_items_inline = 40
        diseases_preview = diseases[:max_items_inline]
        provinces_preview = provinces[:max_items_inline]
        zones_preview = zones[:max_items_inline]

        story.append(Spacer(1, 10))
        story.append(Paragraph("Listes essentielles (aperçu)", section_style))
        if len(diseases) > max_items_inline or len(provinces) > max_items_inline or len(zones) > max_items_inline:
            story.append(
                Paragraph(
                    "Ce PDF affiche un apercu des valeurs essentielles. Utilisez l'export CSV pour la liste complete.",
                    body_style,
                )
            )
            story.append(Spacer(1, 8))

        full_width = 18.2 * cm
        self._append_catalog_section(story, "Maladies", diseases_preview, full_width)
        self._append_catalog_section(story, "Provinces", provinces_preview, full_width)
        self._append_catalog_section(story, "Zones de sante", zones_preview, full_width)

        doc.title = "SAFE CONGO - Referentiel dataset"
        doc.author = "SAFE CONGO"
        doc.subject = "Referentiel maladies provinces zones"
        doc.build(story, onFirstPage=self._decorate_page, onLaterPages=self._decorate_page)
        buffer.seek(0)
        return buffer.getvalue()