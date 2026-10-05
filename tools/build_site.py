"""يولّد صفحات الموقع الثابتة بالعربية والإنجليزية من قوالب مشتركة.

    python3 tools/build_site.py

محتوى كل صفحة في tools/pages/<اللغة>/<الاسم>.html، والترويسة والذيل ووسوم <head>
مشتركة هنا. العربية تُكتب في جذر المستودع والإنجليزية في en/، والناتج ملفات HTML
عادية تُنشر كما هي على GitHub Pages.
عدّل المحتوى في tools/pages ثم شغّل السكربت؛ لا تعدّل الملفات المولَّدة مباشرة.
"""
import json
import os
import re
from datetime import date
from urllib.parse import quote

from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PAGES_DIR = os.path.join(os.path.dirname(__file__), 'pages')

SITE = 'https://fanni.ly'
PHONE_INTL = '+218913133083'
WA = 'https://wa.me/218913133083'
EMAIL = 'info@fanni.ly'
MAPS = 'https://maps.app.goo.gl/fNEfR7yNtAwkWuTh9'
GEO = (32.8105057, 13.1195094)
REG = {
    'cr': '05010202667504',
    'license': '5404/02097',
    'importers': '04/0704',
    'chamber': '4349',
    'tax': '49761',
}
THEME = '#0B1626'

# ------------------------------------------------------------------ اللغات
LANGS = {
    'ar': {
        'dir': 'rtl', 'locale': 'ar_LY', 'prefix': '',
        'NAME': 'المتخصص الفني',
        'TAGLINE': 'لاستيراد الآلات والمعدات الثقيلة',
        'LEGAL_NAME': 'شركة المتخصص الفني لاستيراد الآلات والمعدات الثقيلة ومستلزماتها وقطع غيارها',
        'PHONE': '0913133083',
        'ADDRESS': 'طريق السواني، الكريمية — طرابلس',
        'nav': ['الرئيسية', 'المنتجات', 'عن الشركة', 'تواصل معنا'],
        'other': ('en', 'English'),
        't': {
            'skip': 'تخطَّ إلى المحتوى', 'home_label': 'الصفحة الرئيسية', 'main_nav': 'التنقل الرئيسي',
            'menu': 'القائمة', 'call': 'اتصال', 'call_us': 'اتصل بنا', 'wa': 'واتساب',
            'about': 'نستورد معدات الورش والمولدات وقطع غيار الآليات الثقيلة ومواد البناء، ومقرّنا في طرابلس.',
            'site': 'الموقع', 'contact': 'تواصل',
            'rights': 'شركة المتخصص الفني — جميع الحقوق محفوظة.',
            'reg': f'سجل تجاري <span class="num">{REG["cr"]}</span> · سجل المستوردين <span class="num">{REG["importers"]}</span>',
            'privacy': 'الخصوصية', 'terms': 'شروط الاستخدام', 'closing': 'روابط ختامية',
            'credit': 'تصميم وتطوير <a href="https://yosef.ly" target="_blank" rel="noopener">ديـوان التقنيـة الليبـي</a>',
            'logo_alt': 'شعار شركة المتخصص الفني', 'lang_label': 'اللغة',
            'ld_desc': 'استيراد معدات الورش والمولدات وقطع غيار الآليات الثقيلة ومواد البناء.',
            'street': 'طريق السواني، الكريمية', 'city': 'طرابلس', 'country': 'ليبيا',
        },
        'pages': {
            'index': ('المتخصص الفني | معدات الورش والمولدات وقطع الغيار ومواد البناء في طرابلس',
                      'شركة المتخصص الفني في طرابلس تستورد معدات الورش والمولدات وقطع غيار الآليات الثقيلة ومواد البناء. اسألنا عن السعر والتوفر على 0913133083.'),
            'products': ('المنتجات | المتخصص الفني',
                         'معدات الورش، المولدات، قطع غيار الآليات الثقيلة، ومواد البناء: أمثلة لما تستورده شركة المتخصص الفني في طرابلس.'),
            'about': ('عن الشركة | المتخصص الفني',
                      'شركة المتخصص الفني لاستيراد الآلات والمعدات الثقيلة وقطع غيارها، شركة ليبية ذات مسؤولية محدودة مسجّلة في طرابلس.'),
            'contact': ('تواصل معنا | المتخصص الفني',
                        'هاتف وواتساب 0913133083، البريد info@fanni.ly، والعنوان طريق السواني، الكريمية — طرابلس.'),
            'privacy': ('الخصوصية | المتخصص الفني', 'كيف نتعامل مع البيانات التي ترسلها لنا عبر الموقع.'),
            'terms': ('شروط الاستخدام | المتخصص الفني', 'شروط استخدام موقع شركة المتخصص الفني.'),
            'thanks': ('وصلتنا رسالتك | المتخصص الفني', 'شكرًا لتواصلك مع المتخصص الفني.'),
            '404': ('الصفحة غير موجودة | المتخصص الفني', 'الصفحة المطلوبة غير موجودة.'),
        },
    },
    'en': {
        'dir': 'ltr', 'locale': 'en_GB', 'prefix': 'en/',
        'NAME': 'Al-Mutakhassis Al-Fanni',
        'TAGLINE': 'Heavy machinery & equipment import',
        'LEGAL_NAME': 'Al-Mutakhassis Al-Fanni Company for the Import of Heavy Machinery and Equipment, their Supplies and Spare Parts',
        'PHONE': '+218 91 313 3083',
        'ADDRESS': 'Al-Sawani Road, Al-Karimiya — Tripoli',
        'nav': ['Home', 'Products', 'About', 'Contact'],
        'other': ('ar', 'العربية'),
        't': {
            'skip': 'Skip to content', 'home_label': 'Home', 'main_nav': 'Main navigation',
            'menu': 'Menu', 'call': 'Call', 'call_us': 'Call us', 'wa': 'WhatsApp',
            'about': 'We import workshop equipment, generators, heavy machinery spare parts and building materials. Based in Tripoli, Libya.',
            'site': 'Site', 'contact': 'Contact',
            'rights': 'Al-Mutakhassis Al-Fanni. All rights reserved.',
            'reg': f'Commercial register <span class="num">{REG["cr"]}</span> · Importers register <span class="num">{REG["importers"]}</span>',
            'privacy': 'Privacy', 'terms': 'Terms of use', 'closing': 'Legal links',
            'credit': 'Design and development by <a href="https://yosef.ly" target="_blank" rel="noopener">Libyan Tech Diwan</a>',
            'logo_alt': 'Al-Mutakhassis Al-Fanni logo', 'lang_label': 'Language',
            'ld_desc': 'Importer of workshop equipment, generators, heavy machinery spare parts and building materials.',
            'street': 'Al-Sawani Road, Al-Karimiya', 'city': 'Tripoli', 'country': 'Libya',
        },
        'pages': {
            'index': ('Al-Mutakhassis Al-Fanni | Workshop equipment, generators, spare parts & building materials in Tripoli',
                      'Al-Mutakhassis Al-Fanni imports workshop equipment, generators, heavy machinery spare parts and building materials in Tripoli, Libya. Call +218 91 313 3083.'),
            'products': ('Products | Al-Mutakhassis Al-Fanni',
                         'Workshop equipment, generators, heavy machinery spare parts and building materials: examples of what we import to Tripoli, Libya.'),
            'about': ('About | Al-Mutakhassis Al-Fanni',
                      'Al-Mutakhassis Al-Fanni is a Libyan limited liability company in Tripoli, licensed to import heavy machinery, equipment and spare parts.'),
            'contact': ('Contact | Al-Mutakhassis Al-Fanni',
                        'Phone and WhatsApp +218 91 313 3083, email info@fanni.ly. Al-Sawani Road, Al-Karimiya, Tripoli.'),
            'privacy': ('Privacy | Al-Mutakhassis Al-Fanni', 'How we handle the information you send us through this website.'),
            'terms': ('Terms of use | Al-Mutakhassis Al-Fanni', 'Terms of use for the Al-Mutakhassis Al-Fanni website.'),
            'thanks': ('Message received | Al-Mutakhassis Al-Fanni', 'Thank you for contacting Al-Mutakhassis Al-Fanni.'),
        },
    },
}
NAV_PAGES = ['index', 'products', 'about', 'contact']
NO_INDEX = {'thanks', '404'}
PRELOAD = {'index': 'hero'}

# ------------------------------------------------------------------ أيقونات
def svg(body, fill=False, cls='icon'):
    paint = 'fill="currentColor"' if fill else 'fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"'
    return f'<svg class="{cls}" viewBox="0 0 24 24" {paint} aria-hidden="true">{body}</svg>'


ICON = {
    'phone': svg('<path d="M6.5 3h3l1.6 4-2 1.5a12 12 0 0 0 5.4 5.4L16 12l4 1.6v3a2 2 0 0 1-2.2 2A16.5 16.5 0 0 1 4.5 5.2 2 2 0 0 1 6.5 3z"/>'),
    'mail': svg('<rect x="3" y="5.5" width="18" height="13" rx="1.5"/><path d="m3.5 7 8.5 6 8.5-6"/>'),
    'pin': svg('<path d="M12 21s7-6 7-11a7 7 0 1 0-14 0c0 5 7 11 7 11z"/><circle cx="12" cy="10" r="2.5"/>'),
    'globe': svg('<circle cx="12" cy="12" r="9"/><path d="M3.2 9h17.6M3.2 15h17.6M12 3a14 14 0 0 1 0 18 14 14 0 0 1 0-18z"/>'),
    'arrow': svg('<path d="M19 12H5m6-6-6 6 6 6"/>', cls='icon arrow'),
    'check': svg('<path d="m5 12.5 4.5 4.5L19 7.5"/>'),
    'menu': svg('<path d="M4 8h16M8 16h12"/>', cls='icon icon-open'),
    'close': svg('<path d="M6 6l12 12M18 6 6 18"/>', cls='icon icon-close'),
    'wa': svg('<path d="M12.04 2.25c-5.4 0-9.79 4.39-9.79 9.79 0 1.72.45 3.4 1.31 4.88L2.3 21.75l4.96-1.3a9.75 9.75 0 0 0 4.78 1.25h.01c5.4 0 9.79-4.39 9.79-9.79s-4.4-9.66-9.8-9.66zm0 1.75a8.04 8.04 0 0 1 8.04 7.95 8.04 8.04 0 0 1-8.03 8.04h-.01a8.1 8.1 0 0 1-4.12-1.13l-.3-.17-3.06.8.82-2.98-.19-.31a8.03 8.03 0 0 1 6.85-12.2zm-3.6 4.03c-.17 0-.44.06-.67.31-.23.25-.88.86-.88 2.1s.9 2.44 1.03 2.6c.13.18 1.75 2.79 4.28 3.8 2.1.83 2.53.67 2.99.63.46-.04 1.48-.6 1.69-1.19.21-.58.21-1.08.15-1.19-.06-.1-.23-.17-.48-.29-.25-.13-1.48-.73-1.71-.81-.23-.09-.4-.13-.56.12-.17.25-.65.81-.79.98-.15.17-.29.19-.54.06-.25-.12-1.06-.39-2.01-1.24-.74-.66-1.24-1.48-1.39-1.73-.14-.25-.01-.38.11-.5.11-.11.25-.29.38-.44.12-.15.16-.25.25-.42.08-.17.04-.31-.02-.44-.06-.12-.55-1.35-.77-1.85-.2-.48-.4-.42-.55-.42h-.24z"/>', fill=True),
}


# ------------------------------------------------------------------ أدوات
def file_of(slug):
    return f'{slug}.html'


def url_of(lang, slug):
    p = LANGS[lang]['prefix']
    return f'{SITE}/{p}' if slug == 'index' else f'{SITE}/{p}{file_of(slug)}'


def has(lang, slug):
    return os.path.exists(os.path.join(PAGES_DIR, lang, f'{slug}.html'))


def json_ld(lang):
    L, t = LANGS[lang], LANGS[lang]['t']
    data = {
        '@context': 'https://schema.org',
        '@type': 'LocalBusiness',
        '@id': f'{SITE}/#business',
        'name': L['NAME'],
        'alternateName': LANGS['en' if lang == 'ar' else 'ar']['NAME'],
        'legalName': L['LEGAL_NAME'],
        'description': t['ld_desc'],
        'url': url_of(lang, 'index'),
        'logo': f'{SITE}/assets/img/brand/icon-512.png',
        'image': f'{SITE}/assets/img/brand/social-card.jpg',
        'telephone': PHONE_INTL,
        'email': EMAIL,
        'foundingDate': '2024-11-28',
        'taxID': REG['tax'],
        'address': {
            '@type': 'PostalAddress',
            'streetAddress': t['street'],
            'addressLocality': t['city'],
            'addressCountry': 'LY',
        },
        'geo': {'@type': 'GeoCoordinates', 'latitude': GEO[0], 'longitude': GEO[1]},
        'hasMap': MAPS,
        'areaServed': {'@type': 'Country', 'name': t['country']},
    }
    return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False) + '</script>'


def head(lang, slug, base):
    L = LANGS[lang]
    title, desc = L['pages'][slug]
    canonical = url_of(lang, slug)
    lines = []
    if slug in NO_INDEX:
        lines.append('<meta name="robots" content="noindex">')
    elif has('ar', slug) and has('en', slug):
        for code in ('ar', 'en'):
            lines.append(f'<link rel="alternate" hreflang="{code}" href="{url_of(code, slug)}">')
        lines.append(f'<link rel="alternate" hreflang="x-default" href="{url_of("ar", slug)}">')
    alt = '\n'.join(lines)
    other_locale = LANGS['en' if lang == 'ar' else 'ar']['locale']
    pre = ''
    if slug in PRELOAD:
        n = PRELOAD[slug]
        pre = (f'\n<link rel="preload" as="image" href="{base}assets/img/photos/{n}-800.webp" '
               f'imagesrcset="{base}assets/img/photos/{n}-800.webp 800w, {base}assets/img/photos/{n}-1600.webp 1600w" '
               f'imagesizes="(min-width: 900px) 55vw, 100vw" fetchpriority="high">')
    fonts = '\n'.join(
        f'<link rel="preload" as="font" type="font/woff2" href="{base}assets/fonts/{f}.woff2" crossorigin>'
        for f in (('plex-arabic-400', 'plex-arabic-700') if lang == 'ar' else ('plex-latin-400', 'plex-latin-700')))
    ld = '\n' + json_ld(lang) if slug == 'index' else ''
    return f'''<!doctype html>
<html lang="{lang}" dir="{L['dir']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="theme-color" content="{THEME}">
<link rel="canonical" href="{canonical}">
{alt}

<link rel="icon" href="{base}favicon.ico" sizes="48x48">
<link rel="icon" type="image/png" sizes="32x32" href="{base}assets/img/brand/favicon-32.png">
<link rel="icon" type="image/png" sizes="192x192" href="{base}assets/img/brand/icon-192.png">
<link rel="apple-touch-icon" href="{base}apple-touch-icon.png">
<link rel="manifest" href="{base}site.webmanifest">

<meta property="og:type" content="website">
<meta property="og:locale" content="{L['locale']}">
<meta property="og:locale:alternate" content="{other_locale}">
<meta property="og:site_name" content="{L['NAME']}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{SITE}/assets/img/brand/social-card.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{L['t']['logo_alt']}">
<meta name="twitter:card" content="summary_large_image">

{fonts}{pre}
<link rel="stylesheet" href="{base}assets/css/main.css">
<script>document.documentElement.classList.add('js');</script>{ld}
</head>'''.replace('\n\n\n', '\n\n')


def lang_href(lang, slug, base):
    """رابط الصفحة نفسها باللغة الأخرى (أو رئيسيتها إن لم توجد)."""
    other = LANGS[lang]['other'][0]
    target = slug if has(other, slug) else 'index'
    if base == '/':
        return f'/{LANGS[other]["prefix"]}{file_of(target)}'
    up = '../' if LANGS[lang]['prefix'] else ''
    return f'{up}{LANGS[other]["prefix"]}{file_of(target)}'


def header(lang, slug, abase, pbase):
    L, t = LANGS[lang], LANGS[lang]['t']
    active = slug if slug in NAV_PAGES else None
    links, mlinks = [], []
    for key, label in zip(NAV_PAGES, L['nav']):
        cur = ' aria-current="page"' if key == active else ''
        links.append(f'<a href="{pbase}{file_of(key)}"{cur}>{label}</a>')
        mlinks.append(f'<a href="{pbase}{file_of(key)}"{cur}><span>{label}</span>{ICON["arrow"]}</a>')
    other_code, other_label = L['other']
    lh = lang_href(lang, slug, abase)
    brand_href = f'{pbase}{file_of("index")}'
    return f'''
<body>
<a class="skip-link" href="#main">{t['skip']}</a>

<header class="header" data-header>
  <div class="wrap header__inner">
    <a class="brand" href="{brand_href}" aria-label="{L['NAME']} — {t['home_label']}">
      <img class="brand__mark" src="{abase}assets/img/brand/mark.png" alt="" width="160" height="164">
      <span class="brand__text">
        <span class="brand__name">{L['NAME']}</span>
        <span class="brand__tag">{L['TAGLINE']}</span>
      </span>
    </a>

    <nav class="nav" aria-label="{t['main_nav']}">
      {chr(10).join('      ' + l for l in links).strip()}
    </nav>

    <div class="header__end">
      <a class="header__lang" href="{lh}" lang="{other_code}" hreflang="{other_code}">{other_label}</a>
      <a class="header__call" href="tel:{PHONE_INTL}">{ICON['phone']}<span class="num">{L['PHONE']}</span></a>
      <a class="header__dial" href="tel:{PHONE_INTL}" aria-label="{t['call_us']}">{ICON['phone']}</a>
      <details class="menu">
        <summary aria-label="{t['menu']}">{ICON['menu']}{ICON['close']}</summary>
        <div class="menu__panel">
          <nav class="menu__nav" aria-label="{t['menu']}">
            {chr(10).join('            ' + l for l in mlinks).strip()}
          </nav>
          <div class="menu__foot">
            <div class="btn-row">
              <a class="btn btn--brass" href="tel:{PHONE_INTL}">{ICON['phone']}<span>{t['call']}</span></a>
              <a class="btn btn--line" href="{WA}" target="_blank" rel="noopener">{ICON['wa']}<span>{t['wa']}</span></a>
            </div>
            <a class="menu__lang" href="{lh}" lang="{other_code}" hreflang="{other_code}">{ICON['globe']}<span>{other_label}</span></a>
          </div>
        </div>
      </details>
    </div>
  </div>
</header>
'''


def footer(lang, abase, pbase):
    L, t = LANGS[lang], LANGS[lang]['t']
    links = '\n          '.join(
        f'<li><a href="{pbase}{file_of(k)}">{label}</a></li>' for k, label in zip(NAV_PAGES, L['nav']))
    return f'''
<footer class="footer">
  <div class="wrap footer__grid">
    <div>
      <a class="brand" href="{pbase}{file_of('index')}" aria-label="{L['NAME']} — {t['home_label']}">
        <img class="brand__mark" src="{abase}assets/img/brand/mark.png" alt="" width="160" height="164" loading="lazy">
        <span class="brand__text">
          <span class="brand__name">{L['NAME']}</span>
          <span class="brand__tag">{L['TAGLINE']}</span>
        </span>
      </a>
      <p class="footer__about">{t['about']}</p>
    </div>

    <div>
      <h2>{t['site']}</h2>
      <ul class="footer__links">
          {links}
      </ul>
    </div>

    <div>
      <h2>{t['contact']}</h2>
      <ul class="footer__contact">
        <li><a href="tel:{PHONE_INTL}">{ICON['phone']}<span class="num">{L['PHONE']}</span></a></li>
        <li><a href="{WA}" target="_blank" rel="noopener">{ICON['wa']}<span>{t['wa']}</span></a></li>
        <li><a href="mailto:{EMAIL}">{ICON['mail']}<span>{EMAIL}</span></a></li>
        <li><a href="{MAPS}" target="_blank" rel="noopener">{ICON['pin']}<span>{L['ADDRESS']}</span></a></li>
      </ul>
    </div>
  </div>

  <div class="footer__legal">
    <div class="wrap footer__legal-inner">
      <div>
        <p>© <span class="num" data-year>{date.today().year}</span> {t['rights']}</p>
        <p class="footer__reg">{t['reg']}</p>
      </div>
      <div>
        <nav aria-label="{t['closing']}">
          <a href="{pbase}privacy.html">{t['privacy']}</a>
          <a href="{pbase}terms.html">{t['terms']}</a>
        </nav>
        <p>{t['credit']}</p>
      </div>
    </div>
  </div>
</footer>

<script src="{abase}assets/js/main.js" defer></script>
</body>
</html>
'''


def picture(base, name, alt, sizes='100vw', extra=''):
    """<img> بعرضين، مع الأبعاد الصحيحة لمنع اهتزاز الصفحة."""
    d = os.path.join(ROOT, 'assets/img/photos')
    widths = [w for w in (800, 1600) if os.path.exists(f'{d}/{name}-{w}.webp')]
    w0, h0 = Image.open(f'{d}/{name}-{widths[0]}.webp').size
    srcset = ', '.join(f'{base}assets/img/photos/{name}-{w}.webp {w}w' for w in widths)
    lazy = '' if 'eager' in extra else ' loading="lazy" decoding="async"'
    prio = ' fetchpriority="high"' if 'eager' in extra else ''
    cls = ''.join(f' class="{tok[6:]}"' for tok in extra.split() if tok.startswith('class='))
    return (f'<img{cls} src="{base}assets/img/photos/{name}-{widths[0]}.webp" srcset="{srcset}" '
            f'sizes="{sizes}" width="{w0}" height="{h0}" alt="{alt}"{lazy}{prio}>')


def fill(text, lang, abase, pbase):
    """يستبدل المتغيّرات داخل محتوى الصفحة: {{base}} و {{icon:x}} و {{PHONE}} ..."""
    L = LANGS[lang]
    consts = {k: str(v) for k, v in globals().items() if k.isupper() and isinstance(v, str)}
    consts.update({k: v for k, v in L.items() if k.isupper()})
    consts.update({f'REG.{k}': v for k, v in REG.items()})
    consts['base'] = pbase
    consts['abase'] = abase
    consts['GEO'] = f'{GEO[0]},{GEO[1]}'
    consts['THANKS_URL'] = url_of(lang, 'thanks')

    def rep(m):
        key = m.group(1).strip()
        if key.startswith('icon:'):
            return ICON[key[5:]]
        if key.startswith('wa:'):                       # رابط واتساب برسالة جاهزة
            return f'{WA}?text={quote(key[3:].strip())}'
        if key.startswith('img:'):
            return picture(abase, *key[4:].split('|'))
        return consts[key]
    return re.sub(r'\{\{(.+?)\}\}', rep, text)


def build():
    sitemap = []
    for lang, L in LANGS.items():
        out_dir = os.path.join(ROOT, L['prefix'])
        os.makedirs(out_dir, exist_ok=True)
        for slug in L['pages']:
            if not has(lang, slug):
                continue
            # abase: مسار الملفات المشتركة (assets)، pbase: مسار صفحات اللغة نفسها.
            # صفحة 404 تُعرض على أي مسار، فروابطها مطلقة.
            if slug == '404':
                abase, pbase = '/', '/' + L['prefix']
            else:
                abase, pbase = ('../' if L['prefix'] else ''), ''
            body = open(os.path.join(PAGES_DIR, lang, f'{slug}.html'), encoding='utf-8').read()
            html = head(lang, slug, abase) + header(lang, slug, abase, pbase) + '\n<main id="main">\n' + \
                fill(body, lang, abase, pbase).strip() + '\n</main>\n' + footer(lang, abase, pbase)
            with open(os.path.join(out_dir, file_of(slug)), 'w', encoding='utf-8') as f:
                f.write(html)
            print('built', L['prefix'] + file_of(slug))
            if slug not in NO_INDEX:
                sitemap.append((lang, slug))

    today = date.today().isoformat()
    prio = {'index': '1.0', 'products': '0.9', 'contact': '0.8', 'about': '0.7'}
    items = []
    for lang, slug in sitemap:
        alts = ''.join(
            f'\n    <xhtml:link rel="alternate" hreflang="{c}" href="{url_of(c, slug)}"/>'
            for c in LANGS if has(c, slug))
        alts += f'\n    <xhtml:link rel="alternate" hreflang="x-default" href="{url_of("ar", slug)}"/>'
        items.append(f'  <url>\n    <loc>{url_of(lang, slug)}</loc>\n    <lastmod>{today}</lastmod>\n'
                     f'    <priority>{prio.get(slug, "0.3")}</priority>{alts}\n  </url>')
    with open(os.path.join(ROOT, 'sitemap.xml'), 'w', encoding='utf-8') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n'
                '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
                '        xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + '\n'.join(items) + '\n</urlset>\n')
    print('built sitemap.xml')


if __name__ == '__main__':
    build()
