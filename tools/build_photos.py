"""ينزّل صور الموقع من مصادرها ويحوّلها إلى WebP بعرضين (للجوال والشاشات الكبيرة).

    python3 tools/build_photos.py            # كل الصور
    python3 tools/build_photos.py cement     # صورة بعينها

كل الصور من Unsplash وPexels، ورخصتهما تسمح بالاستخدام التجاري دون إذن مسبق.
الإسناد غير مطلوب، لكنه مذكور في README.md احترامًا للمصوّرين.
"""
import io
import os
import sys
import urllib.request

from PIL import Image, ImageOps

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
OUT = os.path.join(ROOT, 'assets/img/photos')
os.makedirs(OUT, exist_ok=True)

U = 'https://images.unsplash.com/photo-{}?w=2000&q=85&fm=jpg'
P = 'https://images.pexels.com/photos/{0}/pexels-photo-{0}.jpeg?auto=compress&w=2000'

# الاسم: (الرابط، نسبة القصّ عرض/ارتفاع أو None، موضع القصّ الأفقي 0..1)
PHOTOS = {
    'hero':        (U.format('1610477865545-37711c53144d'), 4 / 3, 0.55),
    'workshop':    (U.format('1504328345606-18bbc8c9d7d1'), 4 / 3, 0.5),
    'generator':   (P.format('5693845'),                    4 / 3, 0.35),
    'parts':       (U.format('1554231063-fef7ed86c0b7'),    4 / 3, 0.5),
    'building':    (P.format('36003983'),                   4 / 3, 0.5),
    'pipes':       (P.format('36878027'),                   4 / 3, 0.5),
    'port':        (U.format('1590496793907-4d66e2994b4d'), None,  0.5),
    'warehouse':   (U.format('1689942010216-dc412bb1e7a9'), 4 / 3, 0.5),
    'tools-wall':  (U.format('1671040690726-b78261eff126'), 4 / 3, 0.5),
    'compressor':  (U.format('1787939060968-2a385b670fa1'), 4 / 5, 0.5),
    'generator-2': (U.format('1780445392484-38a4852a1fd8'), 4 / 3, 0.5),
    'parts-2':     (U.format('1486262715619-67b85e0b08d3'), 4 / 3, 0.5),
    'cement':      (P.format('29817952'),                   4 / 5, 0.72),
}
WIDTHS = (800, 1600)


def crop(im, ratio, fx):
    if not ratio:
        return im
    w, h = im.size
    if w / h > ratio:
        nw = round(h * ratio)
        x = round((w - nw) * fx)
        return im.crop((x, 0, x + nw, h))
    nh = round(w / ratio)
    y = (h - nh) // 2
    return im.crop((0, y, w, y + nh))


ONLY = set(sys.argv[1:])
for name, (url, ratio, fx) in PHOTOS.items():
    if ONLY and name not in ONLY:
        continue
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    im = ImageOps.exif_transpose(Image.open(io.BytesIO(urllib.request.urlopen(req).read()))).convert('RGB')
    im = crop(im, ratio, fx)
    for w in WIDTHS:
        if w > im.width:
            continue
        r = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
        path = os.path.join(OUT, f'{name}-{w}.webp')
        r.save(path, quality=74 if w > 1000 else 78, method=6)
        print(f'{name}-{w}.webp  {r.size}  {os.path.getsize(path) // 1024} KB')
