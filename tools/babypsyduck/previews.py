# Assembles docs/babypsyduck images from the renders made by previews.js.
import glob, json, os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'out')
DOCS = os.path.join(HERE, '..', '..', 'docs', 'babypsyduck')
os.makedirs(DOCS, exist_ok=True)

def font(size, bold=True):
    try:
        return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf' % ('-Bold' if bold else ''), size)
    except Exception:
        return ImageFont.load_default()

def label(dr, xy, text, size=15, fill=(255, 255, 255)):
    dr.text(xy, text, fill=fill, font=font(size), stroke_width=2, stroke_fill=(40, 40, 50))

# animation grid gif
labels = json.load(open(os.path.join(OUT, 'gif', 'labels.json')))
TILE, COLS = 200, 4
frames = []
for f in sorted(glob.glob(os.path.join(OUT, 'gif', 'f*.png'))):
    im = Image.open(f).convert('RGB')
    dr = ImageDraw.Draw(im)
    for i, lab in enumerate(labels):
        x, y = (i % COLS) * TILE, (i // COLS) * TILE
        dr.rectangle((x, y, x + TILE - 1, y + TILE - 1), outline=(70, 70, 84))
        label(dr, (x + 7, y + 5), lab, 14)
    frames.append(im.quantize(colors=128, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE))
frames[0].save(os.path.join(DOCS, 'animations.gif'), save_all=True, append_images=frames[1:], duration=80, loop=0, optimize=True)

# variants: normal / shiny / alpha
names = [('normal', 'Normal'), ('shiny', 'Shiny'), ('alpha', 'Alpha (glowing eyes)')]
o = Image.new('RGB', (360 * 3, 360), (43, 45, 58))
d = ImageDraw.Draw(o)
for i, (n, t) in enumerate(names):
    o.paste(Image.open(os.path.join(OUT, 'prev_%s.png' % n)), (i * 360, 0))
    label(d, (i * 360 + 12, 10), t, 18, (255, 214, 102) if n == 'shiny' else (255, 255, 255))
o.save(os.path.join(DOCS, 'variants.png'), optimize=True)

# turnaround (normal + shiny)
a = Image.open(os.path.join(OUT, 'prev_views.png')); b = Image.open(os.path.join(OUT, 'prev_views_shiny.png'))
o = Image.new('RGB', (a.width, a.height * 2), (43, 45, 58))
o.paste(a, (0, 0)); o.paste(b, (0, a.height))
o.save(os.path.join(DOCS, 'views.png'), optimize=True)

# expressions
e = Image.open(os.path.join(OUT, 'prev_expr.png')).convert('RGB')
d = ImageDraw.Draw(e)
for i, t in enumerate(['open', 'blink / sleep', 'cry (happy)', 'headache', 'faint (dizzy)']):
    label(d, (i * 240 + 10, 8), t, 15)
e.save(os.path.join(DOCS, 'expressions.png'), optimize=True)
print('wrote', sorted(os.listdir(DOCS)))
