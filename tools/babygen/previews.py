# Assembles docs/previews (animation-grid GIFs, showcase image) and pack.png from the renders in out/.
import glob, json, os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.join(os.path.dirname(__file__), '..', '..')
def font(size, bold=True):
    try:
        return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf' % ('-Bold' if bold else ''), size)
    except Exception:
        return ImageFont.load_default()

NAMES = [('babymeowth', 'Baby Meowth', 'Meowth'), ('babyzubat', 'Baby Zubat', 'Zubat'), ('babylitwick', 'Baby Litwick', 'Litwick'), ('frillgator', 'Frillgator', None)]
os.makedirs(os.path.join(ROOT, 'docs', 'previews'), exist_ok=True)

for id, _, _ in NAMES:
    d = f'out/gif_{id}'
    labels = json.load(open(f'{d}/labels.json'))
    frames = []
    for f in sorted(glob.glob(f'{d}/f*.png')):
        im = Image.open(f).convert('RGB')
        dr = ImageDraw.Draw(im)
        for i, lab in enumerate(labels):
            x, y = (i % 3) * 240, (i // 3) * 240
            dr.rectangle((x, y, x + 239, y + 239), outline=(70, 70, 84))
            dr.text((x + 8, y + 6), lab, fill=(255, 255, 255), font=font(15), stroke_width=2, stroke_fill=(40, 40, 50))
        frames.append(im.quantize(colors=128, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE))
    frames[0].save(os.path.join(ROOT, 'docs', 'previews', f'{id}_animations.gif'), save_all=True, append_images=frames[1:], duration=80, loop=0, optimize=True)

W, H = 420 * len(NAMES), 420 * 2 + 60
o = Image.new('RGB', (W, H), (43, 45, 58))
d = ImageDraw.Draw(o)
for i, (id, name, evo) in enumerate(NAMES):
    o.paste(Image.open(f'out/sc_{id}_n.png'), (i * 420, 50))
    o.paste(Image.open(f'out/sc_{id}_s.png'), (i * 420, 470))
    d.text((i * 420 + 16, 12), name, fill=(255, 255, 255), font=font(22))
    d.text((i * 420 + 26 + d.textlength(name, font=font(22)), 17), '-> ' + evo if evo else 'no evolution', fill=(170, 175, 200), font=font(16, False))
    d.text((i * 420 + 16, 478), 'shiny', fill=(255, 214, 102), font=font(16, False))
o.save(os.path.join(ROOT, 'docs', 'previews', 'showcase.png'), optimize=True)

icon = Image.new('RGBA', (384, 384), (43, 45, 58, 255))
def cut(id, box, size):
    # renders have a flat background: key it out so the sprites can overlap
    im = Image.open(f'out/sc_{id}_n.png').convert('RGBA').crop(box)
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if abs(r - 43) + abs(g - 45) + abs(b - 58) < 18:
                px[x, y] = (0, 0, 0, 0)
    return im.resize((size, size), Image.LANCZOS)
f = cut('frillgator', (0, 0, 420, 420), 270)
z = cut('babyzubat', (10, 40, 410, 440), 170)
m = cut('babymeowth', (40, 60, 380, 400), 180)
l = cut('babylitwick', (50, 20, 370, 340), 150)
icon.alpha_composite(f, (57, -8)); icon.alpha_composite(z, (-18, -12)); icon.alpha_composite(m, (-14, 214)); icon.alpha_composite(l, (238, 236))
icon = icon.convert('RGB')
icon.resize((128, 128), Image.LANCZOS).save(os.path.join(ROOT, 'pack.png'), optimize=True)
