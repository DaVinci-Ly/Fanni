"""ينزّل صور الموقع من مصادرها، يوحّد ألوانها، ويحوّلها إلى WebP بعرضين.

    python3 tools/build_photos.py            # كل الصور
    python3 tools/build_photos.py hero       # صورة بعينها

كل الصور من Unsplash وPexels، ورخصتهما تسمح بالاستخدام التجاري دون إذن مسبق.
الإسناد غير مطلوب، لكنه مذكور في README.md احترامًا للمصوّرين.

تمرّ كل صورة بنفس المعالجة اللونية (grade): دفء خفيف، سواد مرفوع قليلًا (مظهر
مطفأ ناعم)، وتشبّع أهدأ؛ حتى تبدو الصور مجموعة واحدة متناسقة.
"""
import concurrent.futures as cf
import io
import os
import sys
import urllib.request

import numpy as np
from PIL import Image, ImageOps

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
OUT = os.path.join(ROOT, 'assets/img/photos')
os.makedirs(OUT, exist_ok=True)

U = 'https://images.unsplash.com/photo-{}?w=2400&q=90&fm=jpg'
P = 'https://images.pexels.com/photos/{0}/pexels-photo-{0}.jpeg?auto=compress&w=2400'

# الاسم: (الرابط، نسبة القصّ عرض/ارتفاع أو None، موضع القصّ الأفقي، الرأسي)
PHOTOS = {
    # الرئيسية
    'hero':          (P.format('5874814'),                    1,     0.5,  0.78),  # لودر في ضباب ذهبي
    'workshop':      (P.format('5845964'),                    4 / 3, 0.5,  0.5),   # شرر الجلخ في ورشة
    'generator':     (P.format('18816918'),                   4 / 3, 0.6,  0.5),   # فنيّان مع مولد
    'parts':         (P.format('4069389'),                    4 / 3, 0.5,  0.5),   # تروس محرك
    'building':      (P.format('39298378'),                   4 / 3, 0.5,  0.5),   # صفوف طوب في الشمس
    'port':          (P.format('38305352'),                   None,  0.5,  0.5),   # حاويات عند الغروب
    # صفحة المنتجات
    'products-head': (U.format('1755237449468-e70840025313'), 4 / 3, 0.5,  0.5),   # طاولة عمل ونافذة
    'shop-interior': (P.format('32305004'),                   4 / 3, 0.5,  0.5),   # ورشة دافئة
    'wrenches':      (P.format('16243260'),                   4 / 5, 0.5,  0.5),   # مفاتيح معلّقة
    'engine':        (P.format('34640514'),                   4 / 3, 0.5,  0.55),  # محرك ديزل على منصّة
    'genset':        (U.format('1759692071712-adc78a8516c8'), 4 / 5, 0.5,  0.6),   # مولد صناعي مفتوح
    'turbo':         (P.format('7565160'),                    4 / 3, 0.5,  0.5),   # شاحن توربيني بين اليدين
    'blocks':        (P.format('39370865'),                   4 / 3, 0.5,  0.5),   # طوب مفرّغ
    'cement':        (P.format('29817952'),                   4 / 5, 0.72, 0.5),   # أكياس إسمنت
    # رؤوس الصفحات
    'contact-head':  (P.format('31762068'),                   4 / 3, 0.55, 0.5),   # حفّارة عند الغروب
}
WIDTHS = (800, 1600)


def crop(im, ratio, fx, fy):
    if not ratio:
        return im
    w, h = im.size
    if w / h > ratio:
        nw = round(h * ratio)
        x = round((w - nw) * fx)
        return im.crop((x, 0, x + nw, h))
    nh = round(w / ratio)
    y = round((h - nh) * fy)
    return im.crop((0, y, w, y + nh))


def grade(im):
    """معالجة لونية موحّدة: دافئة، ناعمة، بسواد مطفأ قليلًا."""
    a = np.asarray(im).astype(np.float32) / 255
    a = a * np.array([1.035, 1.0, 0.94], np.float32)                 # دفء
    lum = (a @ np.array([0.299, 0.587, 0.114], np.float32))[..., None]
    a = lum + (a - lum) * 0.9                                       # تشبّع أهدأ
    a = 0.5 + (a - 0.5) * 0.95                                      # تباين أنعم
    a = 0.035 + a * (0.975 - 0.035)                                 # سواد مرفوع وبياض مطفأ
    shadow = np.clip(1 - lum * 2.2, 0, 1)                           # ظلال تميل للكحلي قليلًا
    a = a + shadow * np.array([-0.006, 0.0, 0.012], np.float32)
    return Image.fromarray((np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8))


def build(name):
    url, ratio, fx, fy = PHOTOS[name]
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    raw = urllib.request.urlopen(req, timeout=120).read()
    im = ImageOps.exif_transpose(Image.open(io.BytesIO(raw))).convert('RGB')
    im = grade(crop(im, ratio, fx, fy))
    lines = []
    for w in WIDTHS:
        if w > im.width:
            continue
        r = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
        path = os.path.join(OUT, f'{name}-{w}.webp')
        r.save(path, quality=76 if w > 1000 else 80, method=6)
        lines.append(f'{name}-{w}.webp  {r.size}  {os.path.getsize(path) // 1024} KB')
    return '\n'.join(lines)


if __name__ == '__main__':
    names = [n for n in PHOTOS if not sys.argv[1:] or n in sys.argv[1:]]
    with cf.ThreadPoolExecutor(6) as ex:
        for out in ex.map(build, names):
            print(out)
