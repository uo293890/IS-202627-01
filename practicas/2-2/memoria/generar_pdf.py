from pathlib import Path
import re
from xml.sax.saxutils import escape

from PIL import Image as PILImage, ImageChops
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, PageBreak,
                               Flowable, KeepTogether, Preformatted)

ROOT = Path(__file__).resolve().parent
font_sets = [
    (Path('C:/Windows/Fonts'), ('arial.ttf', 'arialbd.ttf', 'ariali.ttf')),
    (Path('/usr/share/fonts/truetype/dejavu'), ('DejaVuSans.ttf', 'DejaVuSans-Bold.ttf', 'DejaVuSans-Oblique.ttf')),
]
for folder, files in font_sets:
    if all((folder / f).exists() for f in files):
        for name, filename in zip(('Arial', 'Arial-Bold', 'Arial-Italic'), files):
            pdfmetrics.registerFont(TTFont(name, str(folder / filename)))
        break
else:
    from reportlab.pdfbase.pdfmetrics import Font
    for name, builtin in [('Arial', 'Helvetica'), ('Arial-Bold', 'Helvetica-Bold'), ('Arial-Italic', 'Helvetica-Oblique')]:
        pdfmetrics.registerFont(Font(name, builtin, 'WinAnsiEncoding'))
pdfmetrics.registerFontFamily('Arial', normal='Arial', bold='Arial-Bold', italic='Arial-Italic')

normal = ParagraphStyle('Texto', fontName='Arial', fontSize=10.3, leading=14.4,
                        spaceAfter=9, textColor=colors.black, splitLongWords=True)
titulo = ParagraphStyle('Titulo', parent=normal, fontName='Arial-Bold', fontSize=25,
                        leading=30, spaceAfter=19)
encabezado = ParagraphStyle('Apartado', parent=normal, fontName='Arial-Bold', fontSize=17,
                            leading=21, spaceAfter=13, keepWithNext=True)
caption = ParagraphStyle('Figura', parent=normal, fontSize=8.6, leading=11.5,
                         spaceBefore=6, spaceAfter=8)
codigo = ParagraphStyle('Codigo', fontName='Courier', fontSize=8.2, leading=11,
                        spaceBefore=4, spaceAfter=11, leftIndent=8)


def formato(s):
    s = escape(s)
    s = re.sub(r'`([^`]+)`', lambda m: '<font name="Courier" size="9">' + m[1] + '</font>', s)
    s = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', s)
    def enlace(m):
        url = m[1].rstrip('.,;')
        return '<link href="' + url + '" color="#175d83">' + url + '</link>' + m[1][len(url):]
    s = re.sub(r'(https://[^ <;]+)', enlace, s)
    return s


class Captura(Flowable):
    """Muestra la zona con contenido sin modificar el PNG original."""
    def __init__(self, ruta, ancho=504):
        super().__init__()
        self.ruta = str(ruta)
        with PILImage.open(ruta) as im:
            self.original_width, self.original_height = im.size
            fondo = PILImage.new('RGB', im.size, im.convert('RGB').getpixel((im.width-1, im.height-1)))
            diferencia = ImageChops.difference(im.convert('RGB'), fondo).convert('L')
            bbox = diferencia.point(lambda v: 255 if v > 35 else 0).getbbox() or (0, 0, im.width, 40)
        contenido_ancho = min(self.original_width, max(450, bbox[2] + 16))
        self.escala = min(ancho / contenido_ancho, 0.65, 330 / (bbox[3] + 14))
        self.width = contenido_ancho * self.escala
        self.height = min(self.original_height, bbox[3] + 14) * self.escala

    def draw(self):
        c = self.canv
        c.saveState()
        p = c.beginPath()
        p.rect(0, 0, self.width, self.height)
        c.clipPath(p, stroke=0, fill=0)
        alto = self.original_height * self.escala
        c.drawImage(self.ruta, 0, self.height - alto,
                    width=self.original_width * self.escala, height=alto)
        c.restoreState()


def pie(canvas, doc):
    canvas.setFont('Arial', 8)
    canvas.setFillColor(colors.HexColor('#555555'))
    canvas.drawString(54, 30, 'Ingeniería de Servicios | Práctica 2.2 | uo293890')
    canvas.drawRightString(558, 30, str(doc.page))


story = []
lines = (ROOT / 'memoria.md').read_text(encoding='utf-8').splitlines()
parrafo = []
en_codigo = False
bloque_codigo = []


def volcar():
    if parrafo:
        story.append(Paragraph(formato(' '.join(parrafo)), normal))
        parrafo.clear()


for linea in lines:
    if linea.startswith('```'):
        volcar()
        if en_codigo:
            # Las órdenes largas se mantienen completas y se envuelven para el PDF.
            envueltas = []
            import textwrap
            for cmd in bloque_codigo:
                envueltas.extend(textwrap.wrap(cmd, width=98, subsequent_indent='  ',
                                               replace_whitespace=False, drop_whitespace=False) or [''])
            story.append(Preformatted('\n'.join(envueltas), codigo))
            bloque_codigo.clear()
        en_codigo = not en_codigo
    elif en_codigo:
        bloque_codigo.append(linea)
    elif linea.startswith('# '):
        volcar()
        story.append(Spacer(1, 35))
        story.append(Paragraph(formato(linea[2:]), titulo))
    elif linea.startswith('## '):
        volcar()
        story.append(PageBreak())
        story.append(Paragraph(formato(linea[3:]), encabezado))
    elif linea.startswith('!['):
        volcar()
        m = re.match(r'!\[(.*?)\]\((.*?)\)', linea)
        story.append(KeepTogether([Spacer(1, 4), Captura(ROOT / m[2]),
                                   Paragraph(formato(m[1]), caption)]))
    elif linea.strip():
        parrafo.append(linea.rstrip())
        if linea.endswith('  '):
            volcar()
    else:
        volcar()
volcar()

dest = ROOT / 'memoria.pdf'
doc = SimpleDocTemplate(str(dest), pagesize=(612, 792), rightMargin=54, leftMargin=54,
                        topMargin=46, bottomMargin=50, title='Aplicaciones Web y el protocolo HTTP',
                        author='uo293890', subject='Memoria de la práctica 2.2 de Ingeniería de Servicios')
doc.build(story, onFirstPage=pie, onLaterPages=pie)
print(dest)
