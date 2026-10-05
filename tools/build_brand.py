"""يبني ملفات الهوية من صورة الشعار الأصلية (عناصر ذهبية على خلفية كحلية).

    python3 tools/build_brand.py [مسار الشعار]

الخلفية الكحلية تُفصل بمقياس "الدفء" (الأحمر ناقص الأزرق) لأن الذهب دافئ والخلفية
باردة، ثم يُبنى منها:
  - lockup.png     الشعار كاملًا بخلفية شفافة (للذيل وصفحة الشركة)
  - mark.png       الدرع والترس فقط، بعد حذف شريط الاسم (للترويسة والأيقونات)
  - الأيقونات والفافيكون وبطاقة المشاركة
"""
import os
import sys
from collections import deque

import numpy as np
from PIL import Image, ImageDraw

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'assets/img/brand/source/logo-original.jpg')
OUT = os.path.join(ROOT, 'assets/img/brand')
NAVY = (11, 22, 38)
os.makedirs(OUT, exist_ok=True)

# ---------- 1. فصل الخلفية ----------
a = np.asarray(Image.open(SRC).convert('RGB')).astype(np.float32)
ramp = lambda x, lo, hi: np.clip((x - lo) / (hi - lo), 0, 1)
warmth = a[..., 0] - a[..., 2]
lum = a @ np.array([0.299, 0.587, 0.114], np.float32)
alpha = np.maximum(ramp(warmth, 8, 48), ramp(lum, 78, 135))   # الشق الثاني يحفظ اللمعات الفاتحة
alpha[alpha < 0.05] = 0
bg = np.array([10., 17., 27.])
A = alpha[..., None]
rgb = np.clip(np.where(A > 1e-3, (a - (1 - A) * bg) / np.maximum(A, 1e-3), a), 0, 255)
cut = np.dstack([rgb, alpha * 255]).astype(np.uint8)


def trim(arr, thr=20):
    m = arr[..., 3] > thr
    ys, xs = np.nonzero(m.any(1))[0], np.nonzero(m.any(0))[0]
    return arr[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


lockup = Image.fromarray(trim(cut))

# ---------- 2. العلامة المختصرة ----------
# الخطان الأفقيان عند y≈291-296 و y≈424-428؛ ما بينهما هو الاسم المكتوب.
X0, X1 = 440, 840
top, bot = cut[95:299, X0:X1], cut[421:612, X0:X1]
mark = np.vstack([top, np.zeros((26, X1 - X0, 4), np.uint8), bot])

# حذف بقايا الجرّافات على الحافتين: كل كتلة متصلة تقع كلها في الخمسين بكسل الطرفية
solid = mark[..., 3] > 20
H, W = solid.shape
seen = np.zeros_like(solid)
keep = np.zeros_like(solid)
for y in range(H):
    for x in range(W):
        if not solid[y, x] or seen[y, x]:
            continue
        q, pts = deque([(y, x)]), []
        seen[y, x] = True
        while q:
            cy, cx = q.popleft()
            pts.append((cy, cx))
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < H and 0 <= nx < W and solid[ny, nx] and not seen[ny, nx]:
                        seen[ny, nx] = True
                        q.append((ny, nx))
        xs = [p[1] for p in pts]
        if len(pts) < 40 or max(xs) < 50 or min(xs) > W - 50:
            continue
        for p in pts:
            keep[p] = True
for _ in range(2):
    keep = keep | np.roll(keep, 1, 0) | np.roll(keep, -1, 0) | np.roll(keep, 1, 1) | np.roll(keep, -1, 1)
mark[..., 3] = np.where(keep, mark[..., 3], 0)
mark = Image.fromarray(trim(mark))


def fit(img, w, h, scale=1.0):
    r = min(w * scale / img.width, h * scale / img.height)
    im = img.resize((max(1, round(img.width * r)), max(1, round(img.height * r))), Image.LANCZOS)
    canv = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    canv.paste(im, ((w - im.width) // 2, (h - im.height) // 2), im)
    return canv


def plate(size, scale, radius=0.0):
    p = Image.new('RGBA', (size, size), NAVY + (255,))
    p.alpha_composite(fit(mark, size, size, scale))
    if radius:
        m = Image.new('L', (size * 4, size * 4), 0)
        ImageDraw.Draw(m).rounded_rectangle([0, 0, size * 4 - 1, size * 4 - 1], radius=size * 4 * radius, fill=255)
        p.putalpha(m.resize((size, size), Image.LANCZOS))
    return p


# ---------- 3. ملفات الموقع ----------
w = 160
mark.resize((w, round(mark.height * w / mark.width)), Image.LANCZOS).save(f'{OUT}/mark.png', optimize=True)
w = 720
lk = lockup.resize((w, round(lockup.height * w / lockup.width)), Image.LANCZOS)
lk.save(f'{OUT}/lockup.webp', quality=92, method=6)

plate(512, 0.78).convert('RGB').save(f'{OUT}/icon-512.png', optimize=True)
plate(192, 0.78).convert('RGB').save(f'{OUT}/icon-192.png', optimize=True)
plate(512, 0.58).convert('RGB').save(f'{OUT}/icon-maskable-512.png', optimize=True)
plate(180, 0.76).convert('RGB').save(os.path.join(ROOT, 'apple-touch-icon.png'), optimize=True)
plate(32, 0.86, 0.18).save(f'{OUT}/favicon-32.png', optimize=True)
plate(48, 0.86, 0.18).save(os.path.join(ROOT, 'favicon.ico'), sizes=[(16, 16), (32, 32), (48, 48)])

# ---------- 4. بطاقة المشاركة 1200×630 ----------
src = Image.open(SRC).convert('RGB')        # 1280×720 أصلًا، فيكفي القصّ
cx, cy = 638, 378                           # مركز الشعار في الصورة الأصلية
card = src.crop((cx - 600, cy - 315, cx + 600, cy + 315))
card.save(f'{OUT}/social-card.jpg', quality=86, optimize=True, progressive=True)

for f in sorted(os.listdir(OUT)):
    p = os.path.join(OUT, f)
    if os.path.isfile(p):
        print(f'{f:24s} {str(Image.open(p).size):12s} {os.path.getsize(p) // 1024:5d} KB')
