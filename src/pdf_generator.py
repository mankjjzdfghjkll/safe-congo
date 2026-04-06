# src/pdf_generator.py
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import BytesIO
from datetime import datetime

class BarrierMeasuresPDF:
    def generate_alert_pdf(self, disease, province, zone_sante, current_cases, predicted_cases, growth_rate, alert_level, r2_score):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
        styles = getSampleStyleSheet()
        story = []
        
        # Style titre
        title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=24, textColor=colors.HexColor('#1a73e8'), alignment=TA_CENTER, spaceAfter=30)
        
        # En-tête
        story.append(Paragraph("🛡️ SAFE CONGO", title_style))
        story.append(Paragraph("Système de Surveillance Épidémiologique", styles['Heading2']))
        story.append(Spacer(1, 20))
        
        # Info alerte
        alert_color = colors.HexColor('#dc3545') if alert_level == 'CRITIQUE' else colors.HexColor('#fd7e14') if alert_level == 'ÉLEVÉ' else colors.HexColor('#ffc107')
        alert_style = ParagraphStyle('Alert', parent=styles['Normal'], textColor=alert_color, fontSize=16, alignment=TA_CENTER, spaceAfter=20)
        story.append(Paragraph(f"⚠️ ALERTE {alert_level}", alert_style))
        story.append(Spacer(1, 10))
        
        # Détails épidémiologiques
        story.append(Paragraph(f"<b>Maladie:</b> {disease}", styles['Normal']))
        story.append(Paragraph(f"<b>Province:</b> {province}", styles['Normal']))
        story.append(Paragraph(f"<b>Zone de santé:</b> {zone_sante}", styles['Normal']))
        story.append(Paragraph(f"<b>Date:</b> {datetime.now().strftime('%d/%m/%Y')}", styles['Normal']))
        story.append(Spacer(1, 15))
        
        # Données clés
        data = [
            ["Indicateur", "Valeur"],
            ["Cas actuels", f"{current_cases:,}"],
            ["Prédiction semaine prochaine", f"{predicted_cases:,}"],
            ["Taux de croissance", f"{growth_rate:.1f}%"],
            ["Fiabilité du modèle (R²)", f"{r2_score:.3f}"]
        ]
        table = Table(data, colWidths=[8*cm, 8*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a73e8')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        story.append(table)
        story.append(Spacer(1, 20))
        
        # Mesures barrières
        story.append(Paragraph("<b>📋 MESURES BARRIÈRES RECOMMANDÉES</b>", styles['Heading3']))
        story.append(Spacer(1, 10))
        
        mesures = [
            "1. 🧼 Lavez-vous fréquemment les mains à l'eau et au savon",
            "2. 😷 Portez un masque dans les lieux publics",
            "3. 📏 Respectez la distanciation sociale (1 mètre minimum)",
            "4. 🤒 En cas de symptômes, consultez immédiatement un médecin",
            "5. 🏠 Isolez les cas suspects",
            "6. 📢 Sensibilisez la communauté",
            "7. 🩺 Renforcez la surveillance dans la zone",
            "8. 🚑 Préparez les structures de santé"
        ]
        
        for mesure in mesures:
            story.append(Paragraph(mesure, styles['Normal']))
            story.append(Spacer(1, 5))
        
        story.append(Spacer(1, 20))
        
        # Contact
        story.append(Paragraph("<b>📞 Contacts utiles</b>", styles['Heading3']))
        story.append(Paragraph("Ministère de la Santé: +243 123 456 789", styles['Normal']))
        story.append(Paragraph("Centre d'Opérations d'Urgence: +243 987 654 321", styles['Normal']))
        story.append(Paragraph("Ligne verte: 111", styles['Normal']))
        story.append(Spacer(1, 30))
        
        # Footer
        footer_style = ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.grey, alignment=TA_CENTER)
        story.append(Paragraph(f"Document généré par SAFE CONGO - {datetime.now().strftime('%d/%m/%Y %H:%M')}", footer_style))
        story.append(Paragraph("Ce document est une recommandation automatique. Veuillez suivre les consignes officielles.", footer_style))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()