# python3 previews.py [id ...]
# Assembles docs/<id> images from the renders made by previews.js.
import glob, json, os, sys
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'out')

def font(size, bold=True):
    try:
        return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf' % ('-Bold' if bold else ''), size)
    except Exception:
        return ImageFont.load_default()

def label(dr, xy, text, size=15, fill=(255, 255, 255)):
    dr.text(xy, text, fill=fill, font=font(size), stroke_width=2, stroke_fill=(40, 40, 50))

ids = sys.argv[1:] or sorted(os.listdir(os.path.join(HERE, 'pokemon')))
for id in ids:
    docs = os.path.join(HERE, '..', '..', 'docs', id)
    os.makedirs(docs, exist_ok=True)
    meta = json.load(open(os.path.join(OUT, id + '_gif', 'meta.json')))
    tile, cols = meta['tile'], meta['cols']

    # animation grid gif
    frames = []
    for f in sorted(glob.glob(os.path.join(OUT, id + '_gif', 'f*.png'))):
        im = Image.open(f).convert('RGB')
        dr = ImageDraw.Draw(im)
        for i, lab in enumerate(meta['labels']):
            x, y = (i % cols) * tile, (i // cols) * tile
            dr.rectangle((x, y, x + tile - 1, y + tile - 1), outline=(70, 70, 84))
            label(dr, (x + 7, y + 5), lab, 14)
        frames.append(im.quantize(colors=128, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE))
    frames[0].save(os.path.join(docs, 'animations.gif'), save_all=True, append_images=frames[1:], duration=80, loop=0, optimize=True)

    # variants: normal / shiny / alpha
    names = [('normal', 'Normal'), ('shiny', 'Shiny'), ('alpha', 'Alpha (glowing eyes)')]
    ims = [Image.open(os.path.join(OUT, '%s_prev_%s.png' % (id, n))) for n, _ in names]
    s = ims[0].width
    o = Image.new('RGB', (s * 3, s), (43, 45, 58))
    d = ImageDraw.Draw(o)
    for i, ((n, t), im) in enumerate(zip(names, ims)):
        o.paste(im, (i * s, 0))
        label(d, (i * s + 12, 10), t, 18, (255, 214, 102) if n == 'shiny' else (255, 255, 255))
    o.save(os.path.join(docs, 'variants.png'), optimize=True)

    # turnaround (normal + shiny)
    a = Image.open(os.path.join(OUT, id + '_prev_views.png')); b = Image.open(os.path.join(OUT, id + '_prev_views_shiny.png'))
    o = Image.new('RGB', (a.width, a.height * 2), (43, 45, 58))
    o.paste(a, (0, 0)); o.paste(b, (0, a.height))
    o.save(os.path.join(docs, 'views.png'), optimize=True)

    # expressions
    e = Image.open(os.path.join(OUT, id + '_prev_expr.png')).convert('RGB')
    d = ImageDraw.Draw(e)
    for i, t in enumerate(meta['faces']):
        label(d, (i * 240 + 10, 8), t, 15)
    e.save(os.path.join(docs, 'expressions.png'), optimize=True)
    print(id, 'wrote', sorted(os.listdir(docs)))
