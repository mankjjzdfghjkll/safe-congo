# src/pdf_generator.py
from datetime import datetime
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.graphics.shapes import Circle, Drawing, Polygon, Rect, String
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


class BarrierMeasuresPDF:
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

    def _sinusoidal_band(self, width=18.2*cm, height=1.0*cm):
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

    def _build_logo(self, size=2.2 * cm):
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

    def _recommended_measures(self, alert_level):
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
        return specific.get((alert_level or "").upper(), ["Maintenir une veille rapprochee et confirmer les prochains points de donnees."]) + common

    def _priority_actions(self, alert_level):
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
        ])

    def _measure_rows(self, alert_level, body_style):
        objectives = [
            "Limiter la transmission et proteger les cas suspects.",
            "Mieux detecter et documenter les nouveaux signaux.",
            "Maintenir la continuite des soins et des intrants.",
            "Renforcer la prevention communautaire.",
            "Assurer une coordination et un reporting reguliers.",
        ]
        rows = [["Priorite", "Mesure barriere", "Objectif"]]
        for index, measure in enumerate(self._recommended_measures(alert_level), start=1):
            priority = "Immediate" if index <= 3 else ("Renforcee" if index <= 5 else "Suivi")
            objective = objectives[min(index - 1, len(objectives) - 1)]
            rows.append([
                priority,
                Paragraph(measure, body_style),
                Paragraph(objective, body_style),
            ])
        return rows

    def _flyer_action_grid(self, alert_level, body_style):
        measures = self._recommended_measures(alert_level)
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

    def generate_alert_pdf(self, disease, province, zone_sante, current_cases, predicted_cases, growth_rate, alert_level, r2_score):
        palette = self._severity_palette(alert_level)
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1.6 * cm, bottomMargin=1.6 * cm, leftMargin=1.7 * cm, rightMargin=1.7 * cm)
        styles = getSampleStyleSheet()
        story = []

        title_style = ParagraphStyle("PdfTitle", parent=styles["Heading1"], fontSize=18, leading=22, textColor=colors.HexColor("#0f3f73"), alignment=TA_LEFT, spaceAfter=2)
        subtitle_style = ParagraphStyle("PdfSubtitle", parent=styles["Normal"], fontSize=9.8, leading=13, textColor=colors.HexColor("#5e7691"), alignment=TA_LEFT, spaceAfter=6)
        section_style = ParagraphStyle("PdfSection", parent=styles["Heading3"], fontSize=12.5, leading=16, textColor=colors.HexColor("#123e6b"), spaceAfter=8)
        body_style = ParagraphStyle("PdfBody", parent=styles["Normal"], fontSize=9.5, leading=14, textColor=colors.HexColor("#41576f"), alignment=TA_LEFT)
        footer_style = ParagraphStyle("PdfFooter", parent=styles["Normal"], fontSize=7.8, leading=11, textColor=colors.HexColor("#7a8ca0"), alignment=TA_CENTER)
        badge_style = ParagraphStyle("Badge", parent=styles["Heading2"], alignment=TA_CENTER, textColor=colors.white, fontSize=14, leading=17)
        kicker_style = ParagraphStyle("Kicker", parent=body_style, fontSize=8.5, leading=10, textColor=colors.HexColor("#0a5fab"))
        callout_style = ParagraphStyle("Callout", parent=styles["Heading2"], fontSize=15, leading=18, textColor=palette["accent"])

        for elt in self._build_header(title_style, subtitle_style, "Mesures barrieres terrain", "Document de riposte structure pour lecture rapide, coordination et action immediate."):
            story.append(elt)
        story.append(Spacer(1, 12))

        display_level = "INFO" if (alert_level or "").upper() == "NOUVELLE_DONNEE" else (alert_level or "INFO")
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
        story.append(Spacer(1, 14))

        story.append(Paragraph("Resume executif", section_style))
        executive_copy = (
            f"SAFE CONGO signale une situation de niveau <b>{display_level}</b> pour <b>{disease}</b> dans la zone de sante de <b>{zone_sante}</b>, province de <b>{province}</b>. "
            f"Cette fiche fournit des mesures barrieres simples, des priorites de coordination et une checklist terrain pour soutenir la riposte locale. "
            f"Le volume observe actuellement est de <b>{current_cases:,}</b> cas et doit etre confirme par la surveillance sanitaire officielle."
        )
        story.append(Paragraph(executive_copy, body_style))
        story.append(Spacer(1, 12))

        identity_box = Table(
            [[Paragraph(f"<b>Province :</b> {province}<br/><b>Date d'emission :</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}<br/><b>Priorite :</b> {display_level}", body_style)]],
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
        story.append(self._flyer_action_grid(display_level, body_style))
        story.append(Spacer(1, 14))

        priority_lines = "<br/>".join(
            [f"<b>{slot}</b> - {action}" for slot, action in self._priority_actions(display_level)]
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

        story.append(Paragraph("Mesures barrieres detaillees", section_style))
        measures_table = Table(self._measure_rows(display_level, body_style), colWidths=[2.6 * cm, 8.4 * cm, 5.8 * cm], repeatRows=1)
        measures_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), palette["accent"]),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BOX", (0, 0), (-1, -1), 0.7, colors.HexColor("#d9e6f2")),
            ("INNERGRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#e4edf7")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, palette["soft"]]),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ]))
        story.append(measures_table)
        story.append(Spacer(1, 14))

        story.append(Paragraph("Checklist operationnelle", section_style))
        checklist = [
            ["Action", "Delai attendu", "Responsable cible"],
            ["Notifier l'autorite hierarchique et les equipes de terrain", "Immediat", "Zone / Province"],
            ["Verifier la qualite des donnees de la zone concernee", "Meme jour", "Surveillance epidemiologique"],
            ["Evaluer les besoins en intrants et personnel", "Sous 24 heures", "Coordination logistique"],
            ["Mettre a jour le suivi communautaire et les mesures de prevention", "Continu", "Equipes terrain"],
        ]
        checklist_table = Table(checklist, colWidths=[9.8 * cm, 3.2 * cm, 3.8 * cm])
        checklist_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f3f73")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BOX", (0, 0), (-1, -1), 0.7, colors.HexColor("#d9e6f2")),
            ("INNERGRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#e4edf7")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7fbff")]),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ]))
        story.append(checklist_table)
        story.append(Spacer(1, 14))

        advice_box = Table(
            [[Paragraph("<b>Conseil SAFE CONGO</b><br/>Adaptez ces mesures a la maladie signalee, au contexte local et aux consignes officielles en vigueur. Cette fiche soutient la coordination terrain et la prevention immediate.", body_style)]],
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

        story.append(Paragraph(f"Document genere par SAFE CONGO le {datetime.now().strftime('%d/%m/%Y a %H:%M')}", footer_style))
        story.append(Paragraph("Ce bulletin soutient la decision mais ne remplace pas les consignes officielles du systeme de sante.", footer_style))

        doc.title = f"SAFE CONGO - Mesures barrieres {display_level} {disease}"
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