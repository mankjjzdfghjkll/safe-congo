# src/pdf_generator.py
from datetime import datetime
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


class BarrierMeasuresPDF:
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

        table = Table(content, colWidths=col_widths)
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

    def generate_alert_pdf(self, disease, province, zone_sante, current_cases, predicted_cases, growth_rate, alert_level, r2_score):
        palette = self._severity_palette(alert_level)
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1.6 * cm, bottomMargin=1.6 * cm, leftMargin=1.7 * cm, rightMargin=1.7 * cm)
        styles = getSampleStyleSheet()
        story = []

        title_style = ParagraphStyle("PdfTitle", parent=styles["Heading1"], fontSize=22, leading=26, textColor=colors.HexColor("#0f3f73"), alignment=TA_CENTER, spaceAfter=6)
        subtitle_style = ParagraphStyle("PdfSubtitle", parent=styles["Normal"], fontSize=10.5, leading=14, textColor=colors.HexColor("#5e7691"), alignment=TA_CENTER, spaceAfter=18)
        section_style = ParagraphStyle("PdfSection", parent=styles["Heading3"], fontSize=12.5, leading=16, textColor=colors.HexColor("#123e6b"), spaceAfter=8)
        body_style = ParagraphStyle("PdfBody", parent=styles["Normal"], fontSize=9.5, leading=14, textColor=colors.HexColor("#41576f"), alignment=TA_LEFT)
        footer_style = ParagraphStyle("PdfFooter", parent=styles["Normal"], fontSize=7.8, leading=11, textColor=colors.HexColor("#7a8ca0"), alignment=TA_CENTER)

        header_table = Table(
            [[Paragraph("SAFE CONGO", title_style)], [Paragraph("Bulletin automatique d'alerte epidemiologique", subtitle_style)]],
            colWidths=[16.8 * cm],
        )
        header_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.white),
            ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#d9e6f2")),
            ("ROUNDEDCORNERS", [14, 14, 14, 14]),
            ("TOPPADDING", (0, 0), (-1, -1), 12),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ]))
        story.append(header_table)
        story.append(Spacer(1, 12))

        severity_banner = Table(
            [[Paragraph(f"ALERTE {alert_level}", ParagraphStyle("Banner", parent=styles["Heading2"], alignment=TA_CENTER, textColor=colors.white, fontSize=15, leading=18))]],
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

        summary_data = [
            ["Maladie", disease, "Province", province],
            ["Zone de sante", zone_sante, "Date d'emission", datetime.now().strftime("%d/%m/%Y %H:%M")],
        ]
        summary_table = Table(summary_data, colWidths=[3.2 * cm, 5.2 * cm, 3.2 * cm, 5.2 * cm])
        summary_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.white),
            ("BOX", (0, 0), (-1, -1), 0.7, colors.HexColor("#d9e6f2")),
            ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#e4edf7")),
            ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#163e68")),
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
            ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
            ("FONTNAME", (3, 0), (3, -1), "Helvetica"),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 14))

        story.append(Paragraph("Resume executif", section_style))
        executive_copy = (
            f"Le systeme SAFE CONGO a detecte une alerte de niveau <b>{alert_level}</b> pour <b>{disease}</b> dans la zone de sante de <b>{zone_sante}</b>, province de <b>{province}</b>. "
            f"Le volume courant est estime a <b>{current_cases:,}</b> cas, avec une projection automatique a <b>{predicted_cases:,}</b> cas et une evolution de <b>{growth_rate:.1f}%</b>."
        )
        story.append(Paragraph(executive_copy, body_style))
        story.append(Spacer(1, 12))

        key_metrics = [
            ["Indicateur", "Valeur", "Lecture"],
            ["Cas actuels", f"{current_cases:,}", "Charge observee actuellement"],
            ["Projection courte", f"{predicted_cases:,}", "Volume attendu a court terme"],
            ["Croissance", f"{growth_rate:.1f}%", "Variation par rapport a la periode precedente"],
            ["Indice R2", f"{r2_score:.3f}", "Niveau indicatif de fiabilite du modele"],
        ]
        metrics_table = Table(key_metrics, colWidths=[4.2 * cm, 3.6 * cm, 9.0 * cm])
        metrics_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), palette["accent"]),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 10),
            ("BACKGROUND", (0, 1), (-1, -1), colors.white),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, palette["soft"]]),
            ("BOX", (0, 0), (-1, -1), 0.7, colors.HexColor("#d9e6f2")),
            ("INNERGRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#e4edf7")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ]))
        story.append(metrics_table)
        story.append(Spacer(1, 16))

        story.append(Paragraph("Mesures recommandees", section_style))
        for index, measure in enumerate(self._recommended_measures(alert_level), start=1):
            story.append(Paragraph(f"<b>{index}.</b> {measure}", body_style))
            story.append(Spacer(1, 4))

        story.append(Spacer(1, 12))
        story.append(Paragraph("Checklist operationnelle", section_style))
        checklist = [
            ["Action", "Statut attendu"],
            ["Notifier l'autorite hierarchique et les equipes de terrain", "Dans l'immediat"],
            ["Verifier la qualite des donnees de la zone concernee", "Le meme jour"],
            ["Evaluer les besoins en intrants et personnel", "Sous 24 heures"],
            ["Mettre a jour le suivi communautaire et les mesures de prevention", "Continu"],
        ]
        checklist_table = Table(checklist, colWidths=[11.8 * cm, 5.0 * cm])
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

        story.append(Paragraph("Contacts utiles", section_style))
        story.append(Paragraph("Ministere de la Sante: +243 123 456 789", body_style))
        story.append(Paragraph("Centre des Operations d'Urgence: +243 987 654 321", body_style))
        story.append(Paragraph("Ligne verte: 111", body_style))
        story.append(Spacer(1, 18))

        story.append(Paragraph(f"Document genere par SAFE CONGO le {datetime.now().strftime('%d/%m/%Y a %H:%M')}", footer_style))
        story.append(Paragraph("Ce bulletin soutient la decision mais ne remplace pas les consignes officielles du systeme de sante.", footer_style))

        doc.build(story)
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

        story.append(Paragraph("SAFE CONGO", title_style))
        story.append(Paragraph("Referentiel dataset pour la saisie epidemiologique", subtitle_style))
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

        catalog_table = Table(
            [[
                self._catalog_table("Maladies", diseases, [5.3 * cm]),
                self._catalog_table("Provinces", provinces, [5.3 * cm]),
                self._catalog_table("Zones de sante", zones, [5.3 * cm]),
            ]],
            colWidths=[5.55 * cm, 5.55 * cm, 5.55 * cm],
        )
        catalog_table.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ]))
        story.append(catalog_table)

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()