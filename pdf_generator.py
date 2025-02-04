import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_RIGHT
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
from datetime import datetime
import pytz


def gerar_pdf_resumo_ata(full_summary, aggregated_minutes, arquivo_saida="documento_final.pdf"):
    pasta_saida = "pdf"
    if not os.path.exists(pasta_saida):
        os.makedirs(pasta_saida)

    caminho_pdf = os.path.join(pasta_saida, arquivo_saida)

    # Configuração das fontes
    pdfmetrics.registerFont(TTFont('Arial', 'Arial.ttf'))
    pdfmetrics.registerFont(TTFont('Arial-Bold', 'Arialbd.ttf'))

    # Configuração do documento PDF
    doc = SimpleDocTemplate(caminho_pdf, pagesize=A4, 
                            leftMargin=50, rightMargin=50, 
                            topMargin=50, bottomMargin=50)

    # Estilos de parágrafo
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Centered', fontSize=11, fontName='Arial', alignment=1, spaceAfter=6))
    styles.add(ParagraphStyle(name='CustomTitle', fontSize=14, fontName='Arial-Bold', alignment=1, spaceAfter=12))
    styles.add(ParagraphStyle(name='SubTitle', fontSize=14, fontName='Arial-Bold', alignment=1, spaceAfter=12))
    
    # Define a new 'Justified' style or modify an existing one
    styles.add(ParagraphStyle(name='Justified', 
                              parent=styles['Normal'], 
                              alignment=TA_JUSTIFY, 
                              spaceAfter=6))

    story = []

    # Adicionar data
    story.append(Paragraph(f"Data: {datetime.now(pytz.timezone('America/Sao_Paulo')).strftime('%d/%m/%Y %H:%M:%S')}", styles['Centered']))
    story.append(Spacer(1, 20))  # Espaço após a data

    # Função para adicionar seções
    def adicionar_secao(titulo, texto):
        story.append(Paragraph(titulo, styles['CustomTitle']))
        story.append(Spacer(1, 12))  # Espaço após o título principal
        
        for linha in texto.split("\n"):
            if linha.startswith("1.") or linha.startswith("2.") or linha.startswith("3."):
                story.append(Paragraph(linha, styles['SubTitle']))
            elif linha.strip().startswith("●"):
                story.append(Paragraph(linha, ParagraphStyle('Bullet', parent=styles['Justified'], leftIndent=20)))
            else:
                story.append(Paragraph(linha, styles['Justified']))  # Use the new 'Justified' style

    # Adicionar seções
    adicionar_secao("Resumo Extenso e Detalhado", full_summary)
    adicionar_secao("Ata Consolidada", aggregated_minutes)

    # Construir o documento
    doc.build(story)

    print(f"PDF gerado com sucesso: {caminho_pdf}")