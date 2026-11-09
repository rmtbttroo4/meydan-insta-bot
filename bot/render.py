"""MEYDAN GSM gorsel motoru: 9:16 Reels videosu ve 4:5 gonderi gorseli uretir."""
import math, os, subprocess
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(HERE, "fonts")
FPS = 30

BLACK = "InterDisplay-Black"; XB = "InterDisplay-ExtraBold"; BOLD = "InterDisplay-Bold"
SEMI = "Inter-SemiBold"; MED = "Inter-Medium"

NAVY = (10, 28, 92); BLUE = (22, 76, 210); CYAN = (0, 190, 240); PINK = (236, 30, 110)
WHITE = (255, 255, 255); GRAY = (130, 140, 165); INK = (14, 24, 64); SOFT = (200, 215, 255)

# Renk temalari: marka rengi (CYAN, "GSM") sabit kalir; arka plan, isik lekeleri ve ikinci vurgu rengi degisir.
THEMES = {
    "mavi":      {"top": (7, 20, 72),  "bot": (20, 70, 200),  "blobs": [CYAN, (120, 60, 255), (236, 30, 110)], "pink": (236, 30, 110)},
    "gece":      {"top": (3, 6, 20),   "bot": (16, 28, 72),   "blobs": [CYAN, (0, 110, 255), (120, 60, 255)],  "pink": (236, 30, 110)},
    "mor":       {"top": (26, 6, 64),  "bot": (104, 28, 168), "blobs": [(255, 80, 180), CYAN, (120, 60, 255)], "pink": (255, 60, 150)},
    "turkuaz":   {"top": (0, 32, 52),  "bot": (0, 112, 140),  "blobs": [(0, 230, 200), (0, 120, 255), (255, 190, 0)], "pink": (255, 120, 0)},
    "gunbatimi": {"top": (36, 8, 58),  "bot": (196, 56, 84), "blobs": [(255, 150, 0), (255, 60, 120), CYAN], "pink": (255, 140, 0)},
}
THEME = THEMES["mavi"]


def set_theme(name):
    """Tema secer; ikinci vurgu rengi (PINK) slaytlarda temaya gore degisir."""
    global THEME, PINK
    THEME = THEMES.get(name or "mavi", THEMES["mavi"]); PINK = THEME["pink"]


@lru_cache(None)
def F(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name + ".otf"), size)


# ---------------- easing ----------------
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def prog(t, s, d): return clamp((t - s) / d)
def eout(x): return 1 - (1 - x) ** 3
def eback(x, s=1.7):
    x -= 1
    return 1 + (s + 1) * x ** 3 + s * x ** 2


# ---------------- primitives ----------------
def paste_clip(dst, src, x, y):
    sx0, sy0 = max(0, -x), max(0, -y)
    dx0, dy0 = max(0, x), max(0, y)
    w = min(src.width - sx0, dst.width - dx0); h = min(src.height - sy0, dst.height - dy0)
    if w <= 0 or h <= 0: return
    dst.alpha_composite(src.crop((sx0, sy0, sx0 + w, sy0 + h)), (dx0, dy0))


def text_sprite(txt, font, fill=WHITE, pad=10):
    bb = font.getbbox(txt)
    w, h = bb[2] - bb[0] + pad * 2, bb[3] - bb[1] + pad * 2
    im = Image.new("RGBA", (max(1, w), max(1, h)), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((pad - bb[0], pad - bb[1]), txt, font=font, fill=fill)
    return im


def fit_font(txt, name, size, max_w):
    while size > 20 and F(name, size).getlength(txt) > max_w:
        size -= 4
    return F(name, size)


def wrap(txt, font, max_w):
    words, lines, cur = txt.split(), [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if font.getlength(test) <= max_w or not cur: cur = test
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines


def para_sprite(txt, font, fill, max_w, gap=8, align="l"):
    lines = [text_sprite(l, font, fill, pad=0) for l in wrap(txt, font, max_w)]
    h = sum(l.height for l in lines) + gap * (len(lines) - 1)
    w = max(l.width for l in lines)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); y = 0
    for l in lines:
        x = 0 if align == "l" else (w - l.width) // 2
        im.alpha_composite(l, (x, y)); y += l.height + gap
    return im


def with_alpha(im, a):
    if a >= 0.999: return im
    im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * a))); return im


def put(dst, spr, x, y, a=1.0, scale=1.0, anchor="mm"):
    if a <= 0.003: return
    if abs(scale - 1) > 0.002:
        spr = spr.resize((max(1, int(spr.width * scale)), max(1, int(spr.height * scale))), Image.BICUBIC)
    spr = with_alpha(spr, a)
    ax = {"l": 0, "m": spr.width / 2, "r": spr.width}[anchor[0]]
    ay = {"t": 0, "m": spr.height / 2, "b": spr.height}[anchor[1]]
    paste_clip(dst, spr, int(x - ax), int(y - ay))


def hgrad(w, h, c1, c2):
    x = np.linspace(0, 1, w)[None, :, None]
    arr = np.array(c1)[None, None, :] * (1 - x) + np.array(c2)[None, None, :] * x
    return Image.fromarray(np.repeat(arr, h, axis=0).astype(np.uint8), "RGB").convert("RGBA")


def card(w, h, r=40, fill=WHITE, grad=None, shadow=70, blur=22):
    pad = blur * 2
    im = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((pad, pad + 14, pad + w, pad + h + 14), r, fill=(0, 8, 40, shadow))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(blur)))
    if grad:
        g = hgrad(w, h, *grad); m = Image.new("L", (w, h), 0)
        ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), r, fill=255); g.putalpha(m)
        im.alpha_composite(g, (pad, pad))
    else:
        ImageDraw.Draw(im).rounded_rectangle((pad, pad, pad + w, pad + h), r, fill=fill)
    return im, pad


def pill(txt, font, fg, bg=None, padx=28, pady=14, grad=None):
    t = text_sprite(txt, font, fg, pad=0)
    w, h = t.width + padx * 2, t.height + pady * 2
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    if grad:
        g = hgrad(w, h, *grad); m = Image.new("L", (w, h), 0)
        ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), h // 2, fill=255); g.putalpha(m); im.alpha_composite(g)
    elif bg:
        ImageDraw.Draw(im).rounded_rectangle((0, 0, w - 1, h - 1), h // 2, fill=bg)
    im.alpha_composite(t, (padx, pady))
    return im


def row(sprs, gap=10, valign="b"):
    w = sum(s.width for s in sprs) + gap * (len(sprs) - 1); h = max(s.height for s in sprs)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); x = 0
    for s in sprs:
        y = h - s.height if valign == "b" else (h - s.height) // 2
        im.alpha_composite(s, (x, y)); x += s.width + gap
    return im


def col(sprs, gap=12, align="l"):
    w = max(s.width for s in sprs); h = sum(s.height for s in sprs) + gap * (len(sprs) - 1)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); y = 0
    for s in sprs:
        x = 0 if align == "l" else (w - s.width) // 2
        im.alpha_composite(s, (x, y)); y += s.height + gap
    return im


# ---------------- background ----------------
class Background:
    def __init__(self, W, H, seed=0):
        self.W, self.H = W, H
        rng = np.random.default_rng(seed)
        y = np.linspace(0, 1, H)[:, None]; x = np.linspace(0, 1, W)[None, :]
        k = np.clip(0.65 * y + 0.35 * x, 0, 1)
        top = np.array(THEME["top"]); bot = np.array(THEME["bot"])
        arr = top * (1 - k[..., None]) + bot * k[..., None]
        self.base = Image.fromarray(arr.astype(np.uint8), "RGB").convert("RGBA")
        self.blobs = []
        b1, b2, b3 = THEME["blobs"]
        for color, r, a in [(b1, 520, 0.38), (b2, 600, 0.30), (b3, 420, 0.20)]:
            self.blobs.append((self._blob(r, color, a), rng.uniform(0.5, 1.2), rng.uniform(0.1, 0.9) * W, rng.uniform(0.15, 0.9) * H))
        st = Image.new("RGBA", (W * 2, H), (0, 0, 0, 0)); d = ImageDraw.Draw(st)
        for x0, w, a in [(200, 60, 22), (520, 14, 40), (900, 110, 14), (1400, 30, 30), (1750, 70, 18)]:
            d.polygon([(x0, 0), (x0 + w, 0), (x0 + w - 700, H), (x0 - 700, H)], fill=(255, 255, 255, a))
        self.streaks = st.filter(ImageFilter.GaussianBlur(6))

    @staticmethod
    def _blob(r, color, a):
        s = r * 2; yy, xx = np.mgrid[0:s, 0:s]
        al = np.clip(1 - np.sqrt((xx - r) ** 2 + (yy - r) ** 2) / r, 0, 1) ** 2 * a
        arr = np.zeros((s, s, 4), np.uint8); arr[..., :3] = color; arr[..., 3] = (al * 255).astype(np.uint8)
        return Image.fromarray(arr, "RGBA")

    def frame(self, t):
        im = self.base.copy()
        for b, sp, cx, cy in self.blobs:
            ox = cx + 140 * math.sin(t * sp * 0.5 + cx); oy = cy + 110 * math.cos(t * sp * 0.4 + cy)
            paste_clip(im, b, int(ox - b.width / 2), int(oy - b.height / 2))
        paste_clip(im, self.streaks, -int((t * 60) % self.W), 0)
        return im


# ---------------- shared pieces ----------------
def brand_small(shop, size=46):
    b = row([text_sprite(shop["name_main"], F(BLACK, size)), text_sprite(shop["name_accent"], F(BLACK, size), CYAN)], gap=-6)
    tt = text_sprite(shop["badge"], F(SEMI, int(size * 0.56)), (190, 210, 255))
    return row([b, tt], gap=14, valign="m")


def price_sprite(v, unit_top="TL", unit_bot="/ay", size=116, color=INK, sub=(90, 100, 130)):
    n = text_sprite(str(v), F(BLACK, size), color, pad=0)
    tl = text_sprite(unit_top, F(XB, int(size * 0.31)), color, pad=0)
    parts = [tl]
    if unit_bot: parts.append(text_sprite(unit_bot, F(BOLD, int(size * 0.26)), sub, pad=0))
    w = n.width + 12 + max(p.width for p in parts); h = n.height
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); im.alpha_composite(n, (0, 0))
    im.alpha_composite(tl, (n.width + 12, 4))
    if unit_bot: im.alpha_composite(parts[1], (n.width + 12, h - parts[1].height - 4))
    return im


def info_card(shop, w=900):
    rows = [("ADRES", shop["address_line1"]), ("", shop["address_line2"]),
            ("TELEFON · WHATSAPP", shop["phone"]), ("ÇALIŞMA SAATLERİ", shop["hours"]),
            ("INSTAGRAM", shop["instagram"])]
    items = []
    for lab, val in rows:
        big = lab.startswith("TELEFON")
        vs = text_sprite(val, fit_font(val, BLACK if big else BOLD, 62 if big else 38, w - 100), INK, pad=0)
        items.append((text_sprite(lab, F(BOLD, 26), (0, 150, 220), pad=0) if lab else None, vs, lab))
    h = 80 + sum((i[0].height + 10 if i[0] else 0) + i[1].height + (10 if i[2] == "ADRES" else 34) for i in items) - 34
    c, pad = card(w, h, 44)
    y = pad + 40
    for lab, vs, name in items:
        if lab: c.alpha_composite(lab, (pad + 50, y)); y += lab.height + 10
        c.alpha_composite(vs, (pad + 50, y)); y += vs.height + (10 if name == "ADRES" else 34)
    return c


class Cache(dict):
    def get_or(self, key, fn):
        if key not in self: self[key] = fn()
        return self[key]


# =============== SLIDES (9:16, 1080x1920) ===============
# Her slide: fn(img, t, dur, data, shop, C) -> draws on img (background already drawn)
def env(t, dur, fin=0.35, fout=0.3):
    return min(eout(prog(t, 0, fin)), 1 - prog(t, dur - fout, fout))


def slide_intro(im, t, dur, d, shop, C):
    """Logo acilisi."""
    a_out = 1 - prog(t, dur - 0.3, 0.3)
    f = F(BLACK, 190)
    letters = [C.get_or(("L", c), lambda c=c: text_sprite(c, f)) for c in shop["name_main"]]
    total = sum(s.width for s in letters) - 12 * (len(letters) - 1)
    x = 540 - total / 2
    for i, s in enumerate(letters):
        p = prog(t, 0.15 + i * 0.07, 0.5)
        put(im, s, x + s.width / 2, 820 + (1 - eout(p)) * 120, eout(p) * a_out, scale=0.6 + 0.4 * eback(p) if p < 1 else 1)
        x += s.width - 12
    acc = C.get_or("acc", lambda: text_sprite(shop["name_accent"], F(BLACK, 190), CYAN))
    p = prog(t, 0.75, 0.55); put(im, acc, 540, 1010, eout(p) * a_out, scale=0.5 + 0.5 * eback(p) if p < 1 else 1)
    lw = int(560 * eout(prog(t, 1.15, 0.6)))
    if lw > 2:
        ln = Image.new("RGBA", (lw, 8), (0, 0, 0, 0)); ImageDraw.Draw(ln).rounded_rectangle((0, 0, lw - 1, 7), 4, fill=CYAN + (255,))
        put(im, ln, 540, 1130, a_out)
    s = C.get_or("slogan", lambda: text_sprite(d.get("alt", shop["slogan"]), F(SEMI, 58)))
    p = eout(prog(t, 1.4, 0.5)); put(im, s, 540, 1210 + (1 - p) * 40, p * a_out)
    b = C.get_or("badge", lambda: pill(shop["badge"], F(BOLD, 40), WHITE, padx=40, pady=20, grad=(BLUE, (0, 150, 230))))
    p = prog(t, 1.75, 0.5); put(im, b, 540, 1340, eout(p) * a_out, scale=0.7 + 0.3 * eback(p) if p < 1 else 1)
    loc = C.get_or("loc", lambda: text_sprite(shop["district"].upper(), F(BOLD, 34), (170, 200, 255)))
    p = eout(prog(t, 2.0, 0.5)); put(im, loc, 540, 680 - (1 - p) * 30, p * a_out)


def slide_hook(im, t, dur, d, shop, C):
    """Buyuk baslik: d = {ust, vurgu, alt, rozet?}"""
    e = env(t, dur)
    put(im, C.get_or("brand", lambda: brand_small(shop)), 80, 250, e, anchor="lm")
    l1 = C.get_or(("h1", d["ust"]), lambda: text_sprite(d["ust"], fit_font(d["ust"], XB, 104, 940)))
    l2 = C.get_or(("h2", d["vurgu"]), lambda: text_sprite(d["vurgu"], fit_font(d["vurgu"], BLACK, 200, 960), CYAN))
    l3 = C.get_or(("h3", d["alt"]), lambda: text_sprite(d["alt"], fit_font(d["alt"], XB, 104, 940)))
    for i, (s, y) in enumerate([(l1, 560), (l2, 720), (l3, 880)]):
        p = prog(t, 0.05 + i * 0.15, 0.5)
        put(im, s, 540 - (1 - eout(p)) * 300 * (1 if i % 2 else -1), y, eout(p) * e,
            scale=(0.8 + 0.2 * eback(p)) if i == 1 and p < 1 else 1)
    if d.get("rozet"):
        def mk():
            r = 230; b = Image.new("RGBA", (r * 2 + 80, r * 2 + 80), (0, 0, 0, 0))
            sh = Image.new("RGBA", b.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).ellipse((40, 56, 40 + 2 * r, 56 + 2 * r), fill=(60, 0, 30, 110))
            b.alpha_composite(sh.filter(ImageFilter.GaussianBlur(18)))
            g = hgrad(2 * r, 2 * r, (255, 70, 110), (200, 0, 90)); m = Image.new("L", g.size, 0)
            ImageDraw.Draw(m).ellipse((0, 0, 2 * r - 1, 2 * r - 1), fill=255); g.putalpha(m); b.alpha_composite(g, (40, 40))
            ImageDraw.Draw(b).ellipse((58, 58, 22 + 2 * r, 22 + 2 * r), outline=(255, 255, 255, 140), width=4)
            lines = d["rozet"]; cx = 40 + r; y0 = cx - 40 * len(lines)
            for i, txt in enumerate(lines):
                s = text_sprite(txt, fit_font(txt, BLACK if i < 2 else BOLD, 62 if i < 2 else 44, 380), WHITE, pad=0)
                b.alpha_composite(s, (int(cx - s.width / 2), int(y0 + i * 72)))
            return b
        bd = C.get_or(("rozet", tuple(d["rozet"])), mk)
        p = prog(t, 0.7, 0.6)
        put(im, bd, 540, 1260, eout(p) * e, scale=1 + 0.025 * math.sin(t * 5) if p >= 1 else 0.3 + 0.7 * eback(p))


def slide_tariffs(im, t, dur, d, shop, C):
    """Faturali tarife listesi (eski -> yeni fiyat sayaci)."""
    e = env(t, dur)
    put(im, C.get_or("brand", lambda: brand_small(shop)), 80, 250, e, anchor="lm")
    hd = C.get_or("t_head", lambda: text_sprite(d["baslik"], fit_font(d["baslik"], BLACK, 92, 920)))
    p = eout(prog(t, 0.05, 0.5)); put(im, hd, 80, 380 + (1 - p) * 30, p * e, anchor="lm")
    sub = C.get_or("t_sub", lambda: pill(d["alt_baslik"], F(BOLD, 34), WHITE, grad=(PINK, (190, 0, 120))))
    p = prog(t, 0.3, 0.5); put(im, sub, 80, 485, eout(p) * e, anchor="lm", scale=0.8 + 0.2 * eback(p) if p < 1 else 1)
    chip = C.get_or("chip", lambda: pill(d["dakika_sms"], F(BOLD, 32), INK, (190, 235, 255)))
    put(im, chip, 90, 585, eout(prog(t, 0.5, 0.4)) * e, anchor="lm")
    pk = d["paketler"][:4]
    y = 710
    for i, pkg in enumerate(pk):
        st = 0.6 + i * 0.5
        big = pkg.get("vurgu")
        if pkg.get("ek"):
            y += 50
            ek = C.get_or(("ek", i), lambda: pill(pkg["ek"], F(BOLD, 32), WHITE, PINK))
            put(im, ek, 90, y - 130, eout(prog(t, st - 0.1, 0.4)) * e, anchor="lm")

        def mk(pkg=pkg, big=big):
            c, pad = card(900, 180)
            grad = ((200, 0, 90), (120, 20, 160)) if big else (BLUE, (0, 160, 235))
            pl = hgrad(300, 144, *grad); m = Image.new("L", pl.size, 0)
            ImageDraw.Draw(m).rounded_rectangle((0, 0, 299, 143), 28, fill=255); pl.putalpha(m)
            s = text_sprite(pkg["ad"], fit_font(pkg["ad"], BLACK, 84, 270), WHITE, pad=0)
            pl.alpha_composite(s, ((300 - s.width) // 2, (144 - s.height) // 2))
            c.alpha_composite(pl, (pad + 18, pad + 18))
            o = text_sprite(f"{pkg['eski']} TL", F(BOLD, 44), GRAY, pad=0)
            c.alpha_composite(o, (pad + 350, pad + (180 - o.height) // 2))
            return c, pad, (pad + 350, pad + 90, o.width)
        cimg, pad, (ox, oy, ow) = C.get_or(("card", pkg["ad"]), mk)
        p = prog(t, st, 0.55)
        layer = cimg.copy()
        sp = eout(prog(t, st + 0.45, 0.3))
        if sp > 0:
            ImageDraw.Draw(layer).line((ox - 6, oy + 14, ox - 6 + (ow + 12) * sp, oy - 14), fill=(230, 20, 60), width=7)
        cp = eout(prog(t, st + 0.55, 0.6))
        if cp > 0:
            v = int(round(pkg["eski"] + (pkg["yeni"] - pkg["eski"]) * cp))
            ps = C.get_or(("price", v), lambda v=v: price_sprite(v))
            put(layer, ps, pad + 880, pad + 92, clamp(cp * 3), anchor="rm",
                scale=1 + 0.12 * math.sin(math.pi * prog(t, st + 1.15, 0.35)))
        put(im, layer, 90 - pad + (1 - eout(p)) * 1100, y - layer.height / 2, e, anchor="lt")
        y += 200
    note = C.get_or("t_note", lambda: para_sprite(d["not"], F(MED, 28), SOFT, 900))
    put(im, note, 90, y - 40, eout(prog(t, 2.6, 0.5)) * e, anchor="lt")


def slide_plans(im, t, dur, d, shop, C):
    """Basit fiyat kartlari (TurboBox gibi). d = {ust, baslik, vurgu_kelime, alt_baslik, paketler[{ad,fiyat,vurgu}], birim, not}"""
    e = env(t, dur)
    put(im, C.get_or("brand", lambda: brand_small(shop)), 80, 250, e, anchor="lm")
    if d.get("ust"):
        k = C.get_or("p_k", lambda: text_sprite(d["ust"], F(BOLD, 40), CYAN))
        put(im, k, 80, 360, eout(prog(t, 0.05, 0.45)) * e, anchor="lm")
    t1 = C.get_or("p_t1", lambda: text_sprite(d["baslik"], fit_font(d["baslik"], BLACK, 120, 920)))
    p = prog(t, 0.15, 0.5); put(im, t1, 80 - (1 - eout(p)) * 200, 480, eout(p) * e, anchor="lm")
    sub = C.get_or("p_sub", lambda: text_sprite(d["alt_baslik"], fit_font(d["alt_baslik"], SEMI, 40, 920), SOFT))
    put(im, sub, 80, 590, eout(prog(t, 0.4, 0.5)) * e, anchor="lm")
    for i, pkg in enumerate(d["paketler"][:4]):
        def mk(pkg=pkg):
            hl = pkg.get("vurgu")
            c, pad = card(900, 170, grad=(PINK, (130, 30, 200)) if hl else None)
            fg = WHITE if hl else INK
            s = text_sprite(pkg["ad"], fit_font(pkg["ad"], BLACK, 76, 420), WHITE if hl else BLUE, pad=0)
            c.alpha_composite(s, (pad + 50, pad + (170 - s.height) // 2))
            n = text_sprite(pkg["fiyat"], F(BLACK, 100), fg, pad=0); tl = text_sprite(d.get("birim", "TL"), F(XB, 40), fg, pad=0)
            c.alpha_composite(tl, (pad + 860 - tl.width, pad + 52))
            c.alpha_composite(n, (pad + 860 - tl.width - 12 - n.width, pad + (170 - n.height) // 2))
            return c, pad
        c, pad = C.get_or(("plan", pkg["ad"]), mk)
        p = prog(t, 0.7 + i * 0.4, 0.55)
        put(im, c, 90 - pad, 800 + i * 205 - c.height / 2 + (1 - eout(p)) * 260, eout(p) * e, anchor="lt",
            scale=1 if p >= 1 else 0.92 + 0.08 * eout(p))
    if d.get("not"):
        n = C.get_or("p_note", lambda: para_sprite(d["not"], F(MED, 28), SOFT, 900))
        put(im, n, 90, 800 + len(d["paketler"][:4]) * 205 - 60, eout(prog(t, 2.0, 0.5)) * e, anchor="lt")


def slide_bullets(im, t, dur, d, shop, C):
    """Baslik + madde listesi. d = {ust, baslik, maddeler[], not?}"""
    e = env(t, dur)
    put(im, C.get_or("brand", lambda: brand_small(shop)), 80, 250, e, anchor="lm")
    if d.get("ust"):
        k = C.get_or(("b_k", d["ust"]), lambda: text_sprite(d["ust"], F(BOLD, 40), CYAN))
        put(im, k, 80, 370, eout(prog(t, 0.05, 0.45)) * e, anchor="lm")
    tt = C.get_or(("b_t", d["baslik"]), lambda: para_sprite(d["baslik"], F(BLACK, 100), WHITE, 920, gap=4))
    p = prog(t, 0.15, 0.5); put(im, tt, 80 - (1 - eout(p)) * 200, 420, eout(p) * e, anchor="lt")
    y = 420 + tt.height + 70
    for i, m in enumerate(d["maddeler"][:5]):
        def mk(m=m):
            txt = para_sprite(m, F(BOLD, 46), INK, 700, gap=6)
            h = max(130, txt.height + 60)
            c, pad = card(900, h, 36)
            dot = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
            g = hgrad(64, 64, BLUE, CYAN); mm = Image.new("L", (64, 64), 0); ImageDraw.Draw(mm).ellipse((0, 0, 63, 63), fill=255); g.putalpha(mm)
            dot.alpha_composite(g); ImageDraw.Draw(dot).line((18, 33, 28, 43, 46, 22), fill=WHITE, width=7)
            c.alpha_composite(dot, (pad + 36, pad + (h - 64) // 2))
            c.alpha_composite(txt, (pad + 130, pad + (h - txt.height) // 2))
            return c, pad
        c, pad = C.get_or(("bul", m), mk)
        p = prog(t, 0.6 + i * 0.3, 0.5)
        put(im, c, 90 - pad + (1 - eout(p)) * 900, y - pad, eout(p) * e, anchor="lt")
        y += c.height - 2 * pad + 24
    if d.get("not"):
        n = C.get_or(("b_n", d["not"]), lambda: para_sprite(d["not"], F(MED, 30), SOFT, 900))
        put(im, n, 90, y + 20, eout(prog(t, 1.8, 0.5)) * e, anchor="lt")


def slide_cta(im, t, dur, d, shop, C):
    e = eout(prog(t, 0, 0.35))
    q = C.get_or(("c_q", d.get("ust", "")), lambda: text_sprite(d.get("ust", "Hattın, tarifen, telefonun"), F(BOLD, 46), CYAN))
    put(im, q, 540, 360, eout(prog(t, 0.05, 0.4)) * e)
    lg = C.get_or("c_logo", lambda: row([text_sprite(shop["name_main"], F(BLACK, 122)), text_sprite(shop["name_accent"], F(BLACK, 122), CYAN)], gap=8))
    p = prog(t, 0.15, 0.6); put(im, lg, 540, 490, eout(p) * e, scale=0.7 + 0.3 * eback(p) if p < 1 else 1)
    tt = C.get_or("c_tt", lambda: text_sprite(f"{shop['badge']} · {shop['district']}", F(SEMI, 38), (200, 220, 255)))
    put(im, tt, 540, 600, eout(prog(t, 0.4, 0.4)) * e)
    c = C.get_or("c_info", lambda: info_card(shop))
    p = prog(t, 0.55, 0.6); put(im, c, 540, 1010 + (1 - eout(p)) * 200, eout(p) * e)
    if d.get("maskot"):
        from . import maskot
        a_ = 112; b_ = -30 + 28 * math.sin(t * 11)
        sp = maskot.ciz("gulen" if int(t * 1.2) % 3 else "goz_kirp", t=t, kol_sol=a_, kol_sag=b_, goz_kapali=1.0 if (t % 2.8) < 0.12 else 0)
        p_ = eout(prog(t, 0.8, 0.6))
        put(im, sp, 870, 1900 + (1 - p_) * 500 + math.sin(t * 3.2) * 8, e, scale=0.5, anchor="mb")
    btn = C.get_or(("c_btn", d.get("buton", "")), lambda: pill(d.get("buton", "Mağazamıza bekleriz!"), F(BLACK, 54), WHITE, padx=60, pady=30, grad=(PINK, (190, 0, 120))))
    p = prog(t, 1.1, 0.6)
    put(im, btn, 540, 1420, eout(p) * e, scale=1 + 0.035 * math.sin((t - 1.7) * 6) if p >= 1 else 0.6 + 0.4 * eback(p))


# =============== YARATICI SLAYTLAR ===============
GREEN = (0, 170, 110)


def _round_mask(w, h, r):
    m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), r, fill=255); return m


def phone_body(w, h):
    """Telefon govdesi; ekranin (x, y, w, h) kutusunu da dondurur."""
    im = Image.new("RGBA", (w + 80, h + 80), (0, 0, 0, 0))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((40, 58, 40 + w, 58 + h), 96, fill=(0, 0, 20, 150))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(24)))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((40, 40, 40 + w, 40 + h), 96, fill=(14, 16, 26), outline=(90, 100, 130), width=4)
    b = 22
    return im, (40 + b, 40 + b, w - 2 * b, h - 2 * b)


def chat_screen(sw, sh, msgs, n, typing, scale=1.0):
    """Mesajlasma ekrani (marka/uygulama logosu yok): ilk n mesaj gorunur, typing=True ise 'yaziyor' balonu."""
    s = scale; top = int(64 * s); hh = int(160 * s) + top
    im = Image.new("RGBA", (sw, sh), (234, 239, 247, 255)); d = ImageDraw.Draw(im)
    fnt = F(MED, int(46 * s)); maxw = int(sw * 0.74); bubbles = []
    for msg in msgs[:n]:
        me = msg["kim"] == "biz"
        t = para_sprite(msg["metin"], fnt, INK, maxw - int(60 * s), gap=int(8 * s))
        bw, bh = t.width + int(60 * s), t.height + int(48 * s)
        b = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
        ImageDraw.Draw(b).rounded_rectangle((0, 0, bw - 1, bh - 1), int(36 * s), fill=(206, 238, 255) if me else WHITE)
        b.alpha_composite(t, (int(30 * s), int(24 * s))); bubbles.append((b, me))
    if typing:
        b = Image.new("RGBA", (int(160 * s), int(90 * s)), (0, 0, 0, 0)); bd = ImageDraw.Draw(b)
        bd.rounded_rectangle((0, 0, b.width - 1, b.height - 1), int(36 * s), fill=(206, 238, 255))
        for k in range(3):
            cx = int((45 + k * 35) * s); bd.ellipse((cx - int(10 * s), int(35 * s), cx + int(10 * s), int(55 * s)), fill=(70, 110, 170))
        bubbles.append((b, True))
    total = sum(b.height + int(24 * s) for b, _ in bubbles)
    y = hh + int(36 * s); room = sh - y - int(36 * s)
    if total > room: y -= total - room
    for b, me in bubbles:
        x = sw - b.width - int(28 * s) if me else int(28 * s)
        paste_clip(im, b, x, y); y += b.height + int(24 * s)
    # baslik (ustten kayan balonlarin ustune cizilir)
    d.rectangle((0, 0, sw, hh), fill=(255, 255, 255)); d.line((0, hh, sw, hh), fill=(220, 225, 235), width=2)
    av = hgrad(int(90 * s), int(90 * s), BLUE, CYAN); av.putalpha(_round_mask(av.width, av.height, av.width // 2))
    ay = top + int(36 * s); im.alpha_composite(av, (int(32 * s), ay))
    m = text_sprite("M", F(BLACK, int(46 * s)), WHITE, pad=0)
    im.alpha_composite(m, (int(32 * s) + (av.width - m.width) // 2, ay + (av.height - m.height) // 2))
    im.alpha_composite(text_sprite("MEYDAN GSM", F(BLACK, int(42 * s)), INK, pad=0), (int(142 * s), ay + int(4 * s)))
    d.ellipse((int(144 * s), ay + int(62 * s), int(160 * s), ay + int(78 * s)), fill=(40, 200, 110))
    im.alpha_composite(text_sprite("çevrimiçi", F(MED, int(30 * s)), (90, 100, 130), pad=0), (int(170 * s), ay + int(54 * s)))
    return im


def phone_with_screen(w, h, screen):
    body, (sx, sy, sw, shh) = phone_body(w, h)
    scr = screen.resize((sw, shh)) if screen.size != (sw, shh) else screen
    scr = scr.copy(); scr.putalpha(_round_mask(sw, shh, 74))
    body.alpha_composite(scr, (sx, sy))
    ImageDraw.Draw(body).rounded_rectangle((sx + sw // 2 - 70, sy + 18, sx + sw // 2 + 70, sy + 50), 16, fill=(14, 16, 26))
    return body


def _chat_timeline(msgs, start=0.6, gap=1.2, typing=0.75):
    """Her mesajin gorundugu an ve 'yaziyor' araliklari."""
    t, out = start, []
    for m in msgs:
        if m["kim"] == "biz":
            out.append(("typing", t)); t += typing
        out.append(("msg", t)); t += gap
    return out


def slide_sohbet(im, t, dur, d, shop, C):
    """Telefon ekraninda canli mesajlasma. d = {ust, mesajlar:[{kim:'musteri'|'biz', metin}]}"""
    e = env(t, dur)
    if d.get("ust"):
        u = C.get_or(("s_u", d["ust"]), lambda: para_sprite(d["ust"], F(XB, 64), WHITE, 940, gap=6, align="c"))
        p = eout(prog(t, 0.05, 0.45)); put(im, u, 540, 250 + (1 - p) * 30, p * e)
    msgs = d["mesajlar"]; tl = _chat_timeline(msgs)
    n, typing, last = 0, False, 0.0
    for kind, at in tl:
        if t >= at:
            last = at
            if kind == "msg": n += 1; typing = False
            else: typing = True
    W_, H_ = 740, 1380
    _, (sx, sy, sw, shh) = phone_body(W_, H_)
    def mk(n=n, typing=typing):
        return phone_with_screen(W_, H_, chat_screen(sw, shh, msgs, n, typing))
    cur = C.get_or(("ph", n, typing), mk)
    a = clamp((t - last) / 0.18) if last > 0 else 1
    if a < 1 and (n, typing) != (0, False):
        pn, pt = 0, False
        for kind, at in tl:
            if at < last:
                if kind == "msg": pn += 1; pt = False
                else: pt = True
        prev = C.get_or(("ph", pn, pt), lambda: phone_with_screen(W_, H_, chat_screen(sw, shh, msgs, pn, pt)))
        cur = Image.blend(prev, cur, a)
    p = eout(prog(t, 0.0, 0.6))
    put(im, cur, 540, 1110 + (1 - p) * 700, e)


def slide_kinetik(im, t, dur, d, shop, C):
    """Ifadeler tek tek, ekrani dolduran buyuk yazilarla. d = {kelimeler:[...], vurgu:[index], alt?}"""
    ws = d["kelimeler"]; n = len(ws); per = dur / n
    put(im, C.get_or("brand", lambda: brand_small(shop)), 80, 250, env(t, dur), anchor="lm")
    i = min(n - 1, int(t / per)); lt = t - i * per
    txt = ws[i]; hl = i in d.get("vurgu", [n - 1])
    def mk(txt=txt, hl=hl):
        lines = wrap(txt, F(BLACK, 170), 940)
        size = 190 if len(lines) == 1 else 150
        sp = para_sprite(txt, F(BLACK, size), WHITE if not hl else INK, 960, gap=0, align="c")
        if sp.width > 980: sp = sp.resize((980, int(sp.height * 980 / sp.width)), Image.LANCZOS)
        if not hl: return sp
        bg = Image.new("RGBA", (sp.width + 80, sp.height + 50), (0, 0, 0, 0))
        g = hgrad(bg.width, bg.height, CYAN, (255, 255, 255)); g.putalpha(_round_mask(bg.width, bg.height, 36))
        bg.alpha_composite(g); bg.alpha_composite(sp, (40, 25)); return bg
    sp = C.get_or(("k", i), mk)
    pin = eout(prog(lt, 0, 0.28)); pout = prog(lt, per - 0.14, 0.14) if i < n - 1 else prog(t, dur - 0.3, 0.3)
    sc = (1 + min(0.35, max(0.0, 1040 / sp.width - 1)) * (1 - pin)) * (1 - 0.08 * pout)
    put(im, sp, 540 + math.sin(lt * 40) * 6 * (1 - pin), 900, clamp(pin * 1.6) * (1 - pout), scale=sc)
    if d.get("alt"):
        a = C.get_or(("ka", d["alt"]), lambda: para_sprite(d["alt"], F(BOLD, 48), SOFT, 900, align="c"))
        put(im, a, 540, 1330, env(t, dur) * eout(prog(t, 0.3, 0.5)))
    # ilerleme noktalari
    for k in range(n):
        r = 11 if k == i else 8
        dot = Image.new("RGBA", (r * 2, r * 2), (0, 0, 0, 0))
        ImageDraw.Draw(dot).ellipse((0, 0, r * 2 - 1, r * 2 - 1), fill=(CYAN if k <= i else (255, 255, 255)) + ((255,) if k <= i else (90,)))
        put(im, dot, 540 + (k - (n - 1) / 2) * 44, 1560, env(t, dur))


def slide_sayilar(im, t, dur, d, shop, C):
    """Numarali adimlar, her biri kendi ekraninda. d = {baslik, maddeler:[...]}"""
    e = env(t, dur)
    put(im, C.get_or("brand", lambda: brand_small(shop)), 80, 250, e, anchor="lm")
    hd = C.get_or(("sb", d["baslik"]), lambda: para_sprite(d["baslik"], F(XB, 76), WHITE, 940, gap=4))
    put(im, hd, 80, 360, e * eout(prog(t, 0, 0.4)), anchor="lt")
    items = d["maddeler"]; n = len(items); st = 0.5; per = (dur - st) / n
    i = max(0, min(n - 1, int((t - st) / per))); lt = t - st - i * per
    num = C.get_or(("sn", i), lambda: text_sprite(str(i + 1), F(BLACK, 560), CYAN, pad=0))
    tx = C.get_or(("st", i), lambda: para_sprite(items[i], F(BOLD, 68), WHITE, 900, gap=8, align="c"))
    pin = eout(prog(lt, 0, 0.35)) if t >= st else 0
    pout = prog(lt, per - 0.18, 0.18) if i < n - 1 else 0
    x = 540 + (1 - pin) * 500 - pout * 500; a = pin * (1 - pout) * e
    put(im, num, x, 960, a, scale=0.8 + 0.2 * pin)
    put(im, tx, x, 1380, a)
    for k in range(n):
        seg = Image.new("RGBA", (int(900 / n) - 16, 10), (0, 0, 0, 0))
        ImageDraw.Draw(seg).rounded_rectangle((0, 0, seg.width - 1, 9), 5, fill=(CYAN + (255,)) if k <= i and t >= st else (255, 255, 255, 70))
        put(im, seg, 90 + k * (900 / n), 1640, e, anchor="lm")


def _myth_card(label, txt, grad, w=900, fs=58):
    lab = pill(label, F(BLACK, int(fs * 0.72)), WHITE, (0, 0, 0, 70), padx=30, pady=12)
    body = para_sprite(txt, F(BOLD, fs), WHITE, w - 120, gap=10)
    h = 60 + lab.height + 30 + body.height + 60
    c, pad = card(w, h, 48, grad=grad, shadow=90)
    c.alpha_composite(lab, (pad + 60, pad + 50)); c.alpha_composite(body, (pad + 60, pad + 50 + lab.height + 30))
    return c


def slide_efsane(im, t, dur, d, shop, C):
    """Efsane mi gercek mi: kart doner. d = {ust?, efsane, gercek}"""
    e = env(t, dur)
    put(im, C.get_or("brand", lambda: brand_small(shop)), 80, 250, e, anchor="lm")
    u = C.get_or(("eu", d.get("ust")), lambda: para_sprite(d.get("ust", "Doğru bilinen yanlış"), F(XB, 76), WHITE, 940, gap=4, align="c"))
    put(im, u, 540, 440, e * eout(prog(t, 0, 0.4)))
    front = C.get_or("ef", lambda: _myth_card("EFSANE", d["efsane"], (PINK, (150, 20, 90))))
    back = C.get_or("eg", lambda: _myth_card("GERÇEK", d["gercek"], (GREEN, (0, 110, 120))))
    mid = dur * 0.45; ft = prog(t, mid - 0.2, 0.4)
    sx = abs(math.cos(ft * math.pi)); card_ = front if ft < 0.5 else back
    sp = card_.resize((max(1, int(card_.width * sx)), card_.height)) if sx < 0.999 else card_
    pin = eout(prog(t, 0.2, 0.5))
    put(im, sp, 540, 1060 + (1 - pin) * 300, e * pin)
    if t > mid + 0.3 and d.get("not"):
        n = C.get_or("en", lambda: para_sprite(d["not"], F(MED, 40), SOFT, 900, align="c"))
        put(im, n, 540, 1560, e * eout(prog(t, mid + 0.3, 0.5)))


def _phone_front(w, h, broken, seed=3):
    body, (sx, sy, sw, shh) = phone_body(w, h)
    if broken:
        scr = hgrad(sw, shh, (40, 44, 58), (18, 20, 30))
        d = ImageDraw.Draw(scr); rng = np.random.default_rng(seed); cx, cy = sw * 0.38, shh * 0.32
        for k in range(13):
            ang = rng.uniform(0, 2 * math.pi); x, y = cx, cy
            for _ in range(int(rng.integers(3, 7))):
                ang += rng.uniform(-0.6, 0.6); ln = rng.uniform(60, 190)
                nx, ny = x + math.cos(ang) * ln, y + math.sin(ang) * ln
                d.line((x, y, nx, ny), fill=(235, 240, 255, 210), width=int(rng.integers(2, 5))); x, y = nx, ny
        d.ellipse((cx - 26, cy - 26, cx + 26, cy + 26), outline=(235, 240, 255, 220), width=4)
    else:
        scr = hgrad(sw, shh, BLUE, CYAN)
        gl = Image.new("RGBA", (sw, shh), (0, 0, 0, 0))
        ImageDraw.Draw(gl).polygon([(0, shh * 0.15), (sw, 0), (sw, shh * 0.32), (0, shh * 0.5)], fill=(255, 255, 255, 46))
        scr.alpha_composite(gl)
        lg = row([text_sprite("MEYDAN", F(BLACK, 72)), text_sprite("GSM", F(BLACK, 72), INK)], gap=4)
        scr.alpha_composite(lg, ((sw - lg.width) // 2, (shh - lg.height) // 2))
    scr.putalpha(_round_mask(sw, shh, 74)); body.alpha_composite(scr, (sx, sy))
    ImageDraw.Draw(body).rounded_rectangle((sx + sw // 2 - 70, sy + 18, sx + sw // 2 + 70, sy + 50), 16, fill=(14, 16, 26))
    return body


def slide_once_sonra(im, t, dur, d, shop, C):
    """Kirik ekran -> yeni gibi. d = {ust?, once, sonra}"""
    e = env(t, dur)
    put(im, C.get_or("brand", lambda: brand_small(shop)), 80, 250, e, anchor="lm")
    if d.get("ust"):
        u = C.get_or(("ou", d["ust"]), lambda: para_sprite(d["ust"], F(XB, 70), WHITE, 940, gap=4, align="c"))
        put(im, u, 540, 370, e * eout(prog(t, 0, 0.4)))
    a = C.get_or("pa", lambda: _phone_front(560, 1020, True)); b = C.get_or("pb", lambda: _phone_front(560, 1020, False))
    mid = dur * 0.45; w = eout(prog(t, mid, 0.8))
    ph = a.copy()
    if w > 0:
        cut = int(ph.height * w); ph.alpha_composite(b.crop((0, 0, b.width, cut)), (0, 0))
        if w < 1:
            glow = Image.new("RGBA", (ph.width, 14), (255, 255, 255, 220)); ph.alpha_composite(glow.filter(ImageFilter.GaussianBlur(4)), (0, max(0, cut - 7)))
    shake = math.sin(t * 50) * 8 * (1 - prog(t, 0.2, 0.6)) if t < mid else 0
    pin = eout(prog(t, 0.1, 0.5))
    put(im, ph, 540 + shake, 1110 + (1 - pin) * 300, e * pin)
    lab = C.get_or(("ol", t >= mid + 0.4), lambda: pill("SONRA" if t >= mid + 0.4 else "ÖNCE", F(BLACK, 44), WHITE,
                                                     GREEN if t >= mid + 0.4 else PINK, padx=36, pady=14))
    put(im, lab, 540, 490, e * pin)
    txt = d["sonra"] if t >= mid + 0.4 else d["once"]
    s = C.get_or(("ot", txt), lambda: para_sprite(txt, F(XB, 60), WHITE, 940, align="c"))
    put(im, s, 540, 1700, e * pin)


# =============== YARATICI SLAYTLAR 2 ===============
def slide_bildirim(im, t, dur, d, shop, C):
    """Kilit ekraninda MEYDAN GSM bildirimi duser. d = {ust?, saat, baslik, metin}"""
    e = env(t, dur)
    if d.get("ust"):
        u = C.get_or(("bu", d["ust"]), lambda: para_sprite(d["ust"], F(XB, 64), WHITE, 940, gap=6, align="c"))
        put(im, u, 540, 250, e * eout(prog(t, 0, 0.45)))
    W_, H_ = 740, 1380
    def base():
        body, (sx, sy, sw, shh) = phone_body(W_, H_)
        scr = hgrad(sw, shh, THEME["top"], THEME["bot"])
        ov = Image.new("RGBA", (sw, shh), (0, 0, 0, 0)); dd = ImageDraw.Draw(ov)
        for k in range(5):
            dd.ellipse((-200 + k * 160, shh * 0.5 + k * 40, 500 + k * 160, shh * 0.5 + 700 + k * 40), fill=THEME["blobs"][k % 3] + (40,))
        scr.alpha_composite(ov.filter(ImageFilter.GaussianBlur(30)))
        ck = text_sprite(d.get("saat", "19:00"), F(BLACK, 190), WHITE, pad=0); scr.alpha_composite(ck, ((sw - ck.width) // 2, 200))
        dt_ = text_sprite(d.get("gun", "Bugün"), F(SEMI, 42), (230, 235, 255), pad=0); scr.alpha_composite(dt_, ((sw - dt_.width) // 2, 140))
        scr.putalpha(_round_mask(sw, shh, 74)); body.alpha_composite(scr, (sx, sy))
        ImageDraw.Draw(body).rounded_rectangle((sx + sw // 2 - 70, sy + 18, sx + sw // 2 + 70, sy + 50), 16, fill=(14, 16, 26))
        return body, (sx, sy, sw, shh)
    body, (sx, sy, sw, shh) = C.get_or("bb", base)
    def note():
        w = sw - 50
        t1 = text_sprite(d["baslik"], fit_font(d["baslik"], BLACK, 44, w - 70), INK, pad=0)
        t2 = para_sprite(d["metin"], F(MED, 38), (60, 70, 100), w - 70, gap=6)
        h = 40 + 56 + 14 + t1.height + 10 + t2.height + 36
        c = Image.new("RGBA", (w, h), (0, 0, 0, 0)); ImageDraw.Draw(c).rounded_rectangle((0, 0, w - 1, h - 1), 40, fill=(250, 251, 255, 245))
        av = hgrad(56, 56, BLUE, CYAN); av.putalpha(_round_mask(56, 56, 14)); c.alpha_composite(av, (34, 34))
        m = text_sprite("M", F(BLACK, 32), WHITE, pad=0); c.alpha_composite(m, (34 + (56 - m.width) // 2, 34 + (56 - m.height) // 2))
        c.alpha_composite(text_sprite("MEYDAN GSM  ·  şimdi", F(SEMI, 30), (90, 100, 130), pad=0), (106, 48))
        c.alpha_composite(t1, (34, 110)); c.alpha_composite(t2, (34, 110 + t1.height + 10))
        return c
    nt = C.get_or("bn", note)
    ph = body.copy()
    p = eback(prog(t, 1.0, 0.55)) if t < 1.55 else 1
    if t >= 1.0:
        paste_clip(ph, nt, sx + 25, int(sy + 470 - (1 - p) * 500))
    pin = eout(prog(t, 0, 0.6))
    put(im, ph, 540 + (math.sin(t * 60) * 5 if 1.0 < t < 1.4 else 0), 1110 + (1 - pin) * 700, e)


def slide_bant(im, t, dur, d, shop, C):
    """Capraz kayan yazi bantlari + ortada mesaj. d = {kelimeler:[...], orta}"""
    e = env(t, dur)
    def strip(i):
        txt = "   •   ".join(d["kelimeler"]) + "   •   "
        fg, bg = [(INK, CYAN), (WHITE, PINK), (INK, (255, 255, 255))][i % 3]
        one = text_sprite(txt, F(BLACK, 100), fg, pad=0)
        s = Image.new("RGBA", (one.width * 3, 170), bg + (255,))
        for k in range(3): s.alpha_composite(one, (k * one.width, (170 - one.height) // 2))
        return s, one.width
    for i, (y, ang, sp) in enumerate([(560, -8, 260), (960, 6, -220), (1360, -5, 300)]):
        s, ow = C.get_or(("st", i), lambda i=i: strip(i))
        off = int((t * sp) % ow)
        cr = s.crop((off, 0, off + 1500, 170)).rotate(ang, expand=True, resample=Image.BICUBIC)
        pin = eout(prog(t, i * 0.12, 0.5))
        put(im, cr, 540 + (1 - pin) * (1400 if i % 2 else -1400), y, e)
    if d.get("orta"):
        o = C.get_or("bo", lambda: pill(d["orta"], F(BLACK, 72), WHITE, padx=50, pady=30, grad=(BLUE, (0, 150, 230))))
        p = prog(t, 0.8, 0.5)
        put(im, o, 540, 1720, e * eout(p), scale=0.6 + 0.4 * eback(p) if p < 1 else 1 + 0.03 * math.sin(t * 6))
    put(im, C.get_or("brand", lambda: brand_small(shop)), 80, 250, e, anchor="lm")


def slide_batarya(im, t, dur, d, shop, C):
    """Pil dolar, yuzde sayar. d = {ust, yuzde, alt}"""
    e = env(t, dur)
    put(im, C.get_or("brand", lambda: brand_small(shop)), 80, 250, e, anchor="lm")
    u = C.get_or(("au", d["ust"]), lambda: para_sprite(d["ust"], F(XB, 70), WHITE, 940, gap=4, align="c"))
    put(im, u, 540, 420, e * eout(prog(t, 0, 0.4)))
    bw, bh = 400, 760; x0, y0 = 540 - bw // 2, 620
    lv = eout(prog(t, 0.4, max(0.5, dur - 1.6))) * d.get("yuzde", 100) / 100
    lay = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0)); dd = ImageDraw.Draw(lay)
    dd.rounded_rectangle((540 - 70, y0 - 50, 540 + 70, y0 + 10), 18, fill=(255, 255, 255, 230))
    dd.rounded_rectangle((x0, y0, x0 + bw, y0 + bh), 60, outline=(255, 255, 255, 240), width=14)
    fh = int((bh - 56) * lv)
    if fh > 4:
        col_ = (40, 210, 120) if lv > 0.5 else ((255, 190, 0) if lv > 0.2 else (240, 60, 80))
        dd.rounded_rectangle((x0 + 28, y0 + bh - 28 - fh, x0 + bw - 28, y0 + bh - 28), 36, fill=col_ + (255,))
    pct = text_sprite(f"%{int(round(lv * 100))}", F(BLACK, 130), WHITE, pad=0)
    lay.alpha_composite(pct, (540 - pct.width // 2, y0 + bh // 2 - pct.height // 2))
    put(im, lay, 0, 0, e, anchor="lt")
    if d.get("alt"):
        a = C.get_or(("aa", d["alt"]), lambda: para_sprite(d["alt"], F(BOLD, 54), WHITE, 940, align="c"))
        put(im, a, 540, 1560, e * eout(prog(t, dur * 0.5, 0.5)))


def slide_secim(im, t, dur, d, shop, C):
    """A mi B mi? Cevap damgasi. d = {soru, a, b, cevap}"""
    e = env(t, dur)
    put(im, C.get_or("brand", lambda: brand_small(shop)), 80, 250, e, anchor="lm")
    q = C.get_or(("sq", d["soru"]), lambda: para_sprite(d["soru"], F(XB, 76), WHITE, 940, gap=6, align="c"))
    put(im, q, 540, 470, e * eout(prog(t, 0, 0.45)))
    for i, key in enumerate(("a", "b")):
        def mk(key=key, i=i):
            c, pad = card(900, 240, 48, grad=(BLUE, CYAN) if i == 0 else (PINK, (130, 30, 200)))
            lb = text_sprite(key.upper(), F(BLACK, 110), (255, 255, 255, 120), pad=0); c.alpha_composite(lb, (pad + 50, pad + (240 - lb.height) // 2))
            tx = text_sprite(d[key], fit_font(d[key], BLACK, 74, 640), WHITE, pad=0); c.alpha_composite(tx, (pad + 200, pad + (240 - tx.height) // 2))
            return c
        c = C.get_or(("sc", i), mk); p = eout(prog(t, 0.4 + i * 0.25, 0.5))
        put(im, c, 540 + (1 - p) * (1100 if i else -1100), 860 + i * 300, e * p)
    mid = dur * 0.55
    if t > mid:
        st = C.get_or("ss", lambda: pill(d["cevap"], F(BLACK, 96), INK, (255, 255, 255), padx=60, pady=30))
        p = prog(t, mid, 0.4); st2 = st.rotate(-7, expand=True, resample=Image.BICUBIC)
        put(im, st2, 540, 1010, e, scale=2.2 - 1.2 * eout(p))
    if d.get("not") and t > mid + 0.4:
        n = C.get_or("sn", lambda: para_sprite(d["not"], F(BOLD, 48), SOFT, 940, align="c"))
        put(im, n, 540, 1560, e * eout(prog(t, mid + 0.4, 0.5)))



# =============== KAMPANYA SLAYTLARI ===============
def _tl(v):
    try:
        return f"{int(v):,}".replace(",", ".")
    except Exception:
        return str(v)


def slide_fiyat(im, t, dur, d, shop, C):
    """Tek paket/urun icin buyuk fiyat: eski fiyat cizilir, yeni fiyat sayarak iner.
    d = {ust, paket, yeni, eski?, birim, alt?, rozet?, not?}"""
    e = env(t, dur)
    put(im, C.get_or("brand", lambda: brand_small(shop)), 80, 170, e, anchor="lm")
    u = C.get_or(("fu", d.get("ust", "")), lambda: para_sprite(d.get("ust", ""), F(XB, 70), WHITE, 960, gap=6, align="c"))
    put(im, u, 540, 360, e * eout(prog(t, 0, 0.4)))
    pk = C.get_or(("fp", d["paket"]), lambda: pill(d["paket"], fit_font(d["paket"], BLACK, 96, 820), WHITE, padx=60, pady=26, grad=(BLUE, (0, 150, 230))))
    p = prog(t, 0.25, 0.5); put(im, pk, 540, 590, e * eout(p), scale=0.6 + 0.4 * eback(p) if p < 1 else 1)
    yeni = d["yeni"]; eski = d.get("eski")
    if eski:
        o = C.get_or(("fo", eski), lambda: text_sprite(f"{_tl(eski)} TL", F(BOLD, 90), (200, 210, 240)))
        pe = eout(prog(t, 0.6, 0.4)); put(im, o, 540, 790, e * pe)
        sp = eout(prog(t, 1.0, 0.35))
        if sp > 0:
            ln = Image.new("RGBA", (int((o.width + 30) * sp) + 1, 14), (0, 0, 0, 0))
            ImageDraw.Draw(ln).rounded_rectangle((0, 0, ln.width - 1, 13), 7, fill=(255, 60, 90, 255))
            put(im, ln.rotate(8, expand=True), 540 - (o.width + 30) / 2, 790, e, anchor="lm")
    cp = eout(prog(t, 1.25 if eski else 0.6, 0.9))
    try:
        y_ = float(str(yeni).replace(".", "")); e_ = float(str(eski).replace(".", "")) if eski else y_ * 1.6
        v = int(round(e_ + (y_ - e_) * cp))
    except Exception:
        v = yeni
    if cp > 0:
        n = text_sprite(_tl(v), F(BLACK, 300), CYAN, pad=0)
        un = text_sprite(d.get("birim", "TL"), F(XB, 70), WHITE, pad=0)
        r_ = row([n, un], gap=16, valign="b")
        put(im, r_, 540, 1060, e * clamp(cp * 3), scale=1 + 0.08 * math.sin(math.pi * prog(t, 2.2, 0.35)))
    if d.get("rozet"):
        rz = C.get_or("fr", lambda: pill(d["rozet"], F(BLACK, 54), WHITE, grad=(PINK, (190, 0, 120)), padx=46, pady=22).rotate(-3, expand=True, resample=Image.BICUBIC))
        p = prog(t, 1.9, 0.45)
        put(im, rz, 540, 1290, e * clamp(p * 2), scale=(0.3 + 0.7 * eback(p)) if p < 1 else 1 + 0.03 * math.sin(t * 7))
    if d.get("alt"):
        a = C.get_or(("fa", d["alt"]), lambda: para_sprite(d["alt"], F(BOLD, 54), WHITE, 960, gap=8, align="c"))
        put(im, a, 540, 1450, e * eout(prog(t, 1.8, 0.5)))
    if d.get("not"):
        n2 = C.get_or(("fn", d["not"]), lambda: para_sprite(d["not"], F(MED, 32), SOFT, 940, gap=6, align="c"))
        put(im, n2, 540, 1720, e * eout(prog(t, 2.0, 0.5)))


def slide_kampanya_bandi(im, t, dur, d, shop, C):
    """Kapanistan once kisa kampanya hatirlatmasi. d = {etiket, satir, alt?, not?}"""
    e = env(t, dur)
    et = C.get_or(("ke", d.get("etiket")), lambda: pill(d.get("etiket", "BU AY MEYDAN'DA"), F(BLACK, 50), INK, (255, 214, 60), padx=40, pady=18))
    p = prog(t, 0.05, 0.4); put(im, et, 540, 640, e * eout(p), scale=0.6 + 0.4 * eback(p) if p < 1 else 1)
    s = C.get_or(("ks", d["satir"]), lambda: para_sprite(d["satir"], F(BLACK, 96), WHITE, 960, gap=10, align="c"))
    put(im, s, 540 + (1 - eout(prog(t, 0.25, 0.5))) * 600, 960, e)
    if d.get("alt"):
        a = C.get_or(("ka2", d["alt"]), lambda: pill(d["alt"], F(BLACK, 54), WHITE, grad=(PINK, (190, 0, 120)), padx=44, pady=22))
        p = prog(t, 0.7, 0.45); put(im, a, 540, 1290, e * eout(p), scale=(0.6 + 0.4 * eback(p)) if p < 1 else 1 + 0.03 * math.sin(t * 7))
    if d.get("not"):
        n = C.get_or(("kn", d["not"]), lambda: para_sprite(d["not"], F(MED, 32), SOFT, 940, align="c"))
        put(im, n, 540, 1520, e * eout(prog(t, 0.9, 0.5)))


# =============== GEMINI KLIPLERI (yazisiz Meydi videolari) ===============
KLIP_DIR = os.path.join(os.path.dirname(HERE), "assets", "klipler")


def klip_yolu(ad):
    for ext in (".mp4", ".mov"):
        p = os.path.join(KLIP_DIR, ad + ext)
        if os.path.exists(p): return p
    return None


class _KlipOkuyucu:
    def __init__(self, path, bas=0.0, W=1080, H=1920):
        self.W, self.H = W, H; self.n = -1; self.son = None
        self.p = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-stream_loop", "-1", "-ss", str(bas), "-i", path,
                                   "-vf", f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS}",
                                   "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

    def kare(self, i):
        while self.n < i:
            raw = self.p.stdout.read(self.W * self.H * 3)
            if len(raw) < self.W * self.H * 3: break
            self.son = Image.frombytes("RGB", (self.W, self.H), raw); self.n += 1
        return self.son

    def kapat(self):
        try: self.p.kill()
        except Exception: pass


_UST_BANT = None


def slide_klip(im, t, dur, d, shop, C):
    """Gemini klibini arka plan yapar, ustune temiz yazi ve konusma balonu koyar.
    d = {klip, bas?, ust?, balon?, alt?}"""
    global _UST_BANT
    ok = C.get_or("okuyucu", lambda: _KlipOkuyucu(klip_yolu(d["klip"]), d.get("bas", 0.3)))
    fr = ok.kare(int(t * FPS))
    if fr is not None: im.paste(fr.convert("RGBA"), (0, 0))
    if t >= dur - 1.0 / FPS: ok.kapat()
    if _UST_BANT is None:
        a = np.ones(560); a[400:] = np.linspace(1, 0, 160)
        arr = np.zeros((560, 1080, 4), np.uint8); arr[..., :3] = (6, 12, 40); arr[..., 3] = (a[:, None] * 225).astype(np.uint8)
        _UST_BANT = Image.fromarray(arr, "RGBA")
    e = env(t, dur, 0.2, 0.2)
    put(im, _UST_BANT, 0, 0, 1.0, anchor="lt")
    put(im, C.get_or("brand", lambda: brand_small(shop)), 540, 150, 1.0)
    if d.get("ust"):
        u = C.get_or(("ku", d["ust"]), lambda: para_sprite(d["ust"], F(XB, 66), WHITE, 960, gap=6, align="c"))
        put(im, u, 540, 300, e)
    if d.get("balon"):
        from . import maskot
        b = C.get_or(("kb", d["balon"]), lambda: maskot.balon(d["balon"], 860))
        p = prog(t, 0.2, 0.35); put(im, b, 540, 820, e * clamp(p * 2), scale=0.5 + 0.5 * eback(p) if p < 1 else 1, anchor="mb")
    if d.get("alt"):
        a_ = C.get_or(("ka", d["alt"]), lambda: pill(d["alt"], F(BLACK, 54), WHITE, grad=(PINK, (190, 0, 120)), padx=44, pady=22))
        put(im, a_, 540, 1780, e * eout(prog(t, 0.6, 0.4)))


def slide_maskot(im, t, dur, d, shop, C):
    from . import maskot
    return maskot.slide(im, t, dur, d, shop, C)


SLIDES = {"intro": slide_intro, "hook": slide_hook, "tariffs": slide_tariffs, "plans": slide_plans,
          "bullets": slide_bullets, "cta": slide_cta, "sohbet": slide_sohbet, "kinetik": slide_kinetik,
          "sayilar": slide_sayilar, "efsane": slide_efsane, "once_sonra": slide_once_sonra,
          "bildirim": slide_bildirim, "bant": slide_bant, "batarya": slide_batarya, "secim": slide_secim,
          "maskot": slide_maskot, "fiyat": slide_fiyat, "kampanya_bandi": slide_kampanya_bandi, "klip": slide_klip}


def render_reel(slides, shop, out_path, music_path=None, seed=0, workdir=None, theme=None):
    """slides: [{'tip': 'hook', 'sure': 3.0, 'veri': {...}}, ...]"""
    set_theme(theme)
    W, H = 1080, 1920
    bg = Background(W, H, seed)
    workdir = workdir or os.path.dirname(out_path) or "."
    parts, t0 = [], 0.0
    for i, s in enumerate(slides):
        fn, dur, data = SLIDES[s["tip"]], s["sure"], s.get("veri", {})
        C = Cache(); n = int(round(dur * FPS)); part = os.path.join(workdir, f"_part{i}.mp4"); tmp = part + ".tmp.mp4"
        p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                              "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "19", "-preset", "veryfast",
                              "-pix_fmt", "yuv420p", "-r", str(FPS), tmp], stdin=subprocess.PIPE)
        for k in range(n):
            t = k / FPS
            im = bg.frame(t0 + t); fn(im, t, dur, data, shop, C)
            p.stdin.write(im.convert("RGB").tobytes())
        p.stdin.close()
        if p.wait() != 0: raise RuntimeError("ffmpeg slide render failed")
        os.replace(tmp, part); parts.append(part); t0 += dur
    lst = os.path.join(workdir, "_list.txt")
    with open(lst, "w") as f:
        for pth in parts: f.write(f"file '{os.path.abspath(pth)}'\n")
    silent = os.path.join(workdir, "_silent.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", silent], check=True)
    if music_path:
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", silent, "-i", music_path, "-map", "0:v", "-map", "1:a",
                        "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", out_path], check=True)
    else:
        os.replace(silent, out_path)
    for pth in parts + [lst, silent]:
        if os.path.exists(pth): os.remove(pth)
    return t0


# =============== POST (4:5, 1080x1350) ===============
def _render_ozel_gun(v, shop, out_path, seed=0):
    """Ozel gun / anma gonderisi: sade, satis icermez. v = {ust?, baslik, alt?, anma?}"""
    W, H = 1080, 1350
    if v.get("anma"):
        arr = np.zeros((H, W, 3), np.uint8); yy = np.linspace(0, 1, H)[:, None]
        arr[...] = (np.array([18, 18, 22]) * (1 - yy[..., None]) + np.array([4, 4, 6]) * yy[..., None]).astype(np.uint8)
        im = Image.fromarray(arr, "RGB").convert("RGBA"); acc = (200, 205, 215)
    else:
        im = Background(W, H, seed).frame(2.0); acc = CYAN
    lay = Image.new("RGBA", (W, H * 2), (0, 0, 0, 0)); y = 0
    if v.get("ust"):
        u = text_sprite(v["ust"], fit_font(v["ust"], BOLD, 46, 900), acc, pad=0); put(lay, u, 540, y, anchor="mt"); y += u.height + 40
    ln = Image.new("RGBA", (220, 6), acc + (255,)); put(lay, ln, 540, y, anchor="mt"); y += 60
    tt = para_sprite(v["baslik"], F(BLACK, 104 if not v.get("anma") else 92), WHITE, 940, gap=16, align="c"); put(lay, tt, 540, y, anchor="mt"); y += tt.height + 50
    if v.get("alt"):
        a = para_sprite(v["alt"], F(MED, 44), (215, 220, 235), 900, gap=12, align="c"); put(lay, a, 540, y, anchor="mt"); y += a.height
    im.alpha_composite(lay.crop((0, 0, W, y)), (0, max(120, (H - 180 - y) // 2)))
    lg = row([text_sprite(shop["name_main"], F(BLACK, 54)), text_sprite(shop["name_accent"], F(BLACK, 54), acc if v.get("anma") else CYAN)], gap=6)
    put(im, lg, 540, H - 110)
    im.convert("RGB").save(out_path, "JPEG", quality=92)


def render_post(d, shop, out_path, seed=0, theme=None):
    """d = {tip: 'tariffs'|'plans'|'bullets'|'tanitim'|'sohbet'|'sayilar'|'efsane', ...}"""
    set_theme("gece" if d.get("veri", {}).get("anma") else theme)
    W, H = 1080, 1350
    if d["tip"] == "ozel_gun":
        return _render_ozel_gun(d["veri"], shop, out_path, seed)
    canvas = Background(W, H, seed).frame(2.0)
    put(canvas, brand_small(shop, 42), 70, 90, anchor="lm")
    kind = d["tip"]; v = d["veri"]
    im = Image.new("RGBA", (W, H * 2), (0, 0, 0, 0))  # icerik katmani, sonra dikeyde ortalanir
    y = 60
    if v.get("ust"):
        k = text_sprite(v["ust"], F(BOLD, 40), CYAN); put(im, k, 70, y, anchor="lt"); y += k.height + 10
    title = para_sprite(v.get("baslik", ""), F(BLACK, 96), WHITE, 940, gap=18)
    put(im, title, 70, y, anchor="lt"); y += title.height + 50
    if kind == "tariffs":
        put(im, pill(v["alt_baslik"], F(BOLD, 32), WHITE, grad=(PINK, (190, 0, 120))), 70, y, anchor="lt")
        put(im, pill(v["dakika_sms"], F(BOLD, 30), INK, (190, 235, 255)), 1010, y + 4, anchor="rt"); y += 100
        for pkg in v["paketler"][:4]:
            hl = pkg.get("vurgu")
            c, pad = card(940, 150 if not pkg.get("ek") else 190, 36, grad=((200, 0, 90), (120, 20, 160)) if hl else None)
            fg = WHITE if hl else INK
            c.alpha_composite(text_sprite(pkg["ad"], F(BLACK, 70), WHITE if hl else BLUE, pad=0), (pad + 40, pad + 38))
            o = text_sprite(f"{pkg['eski']} TL", F(BOLD, 38), (230, 200, 230) if hl else GRAY, pad=0)
            ox, oy = pad + 360, pad + 52; c.alpha_composite(o, (ox, oy))
            ImageDraw.Draw(c).line((ox - 4, oy + o.height // 2 + 10, ox + o.width + 4, oy + o.height // 2 - 10), fill=(230, 20, 60), width=6)
            ps = price_sprite(pkg["yeni"], "TL", "/ay", 96, fg, (240, 220, 240) if hl else (90, 100, 130))
            c.alpha_composite(ps, (pad + 905 - ps.width, pad + 26))
            if pkg.get("ek"): c.alpha_composite(text_sprite(pkg["ek"], F(BOLD, 30), WHITE, pad=0), (pad + 40, pad + 140))
            put(im, c, 70 - pad, y - pad, anchor="lt"); y += c.height - 2 * pad + 18
    elif kind == "plans":
        put(im, text_sprite(v["alt_baslik"], F(SEMI, 38), SOFT), 70, y - 10, anchor="lt"); y += 80
        for pkg in v["paketler"][:4]:
            hl = pkg.get("vurgu")
            c, pad = card(940, 170, 36, grad=(PINK, (130, 30, 200)) if hl else None)
            fg = WHITE if hl else INK
            s = text_sprite(pkg["ad"], F(BLACK, 76), WHITE if hl else BLUE, pad=0); c.alpha_composite(s, (pad + 50, pad + (170 - s.height) // 2))
            n = text_sprite(pkg["fiyat"], F(BLACK, 100), fg, pad=0); tl = text_sprite(v.get("birim", "TL"), F(XB, 40), fg, pad=0)
            c.alpha_composite(tl, (pad + 900 - tl.width, pad + 52)); c.alpha_composite(n, (pad + 900 - tl.width - 12 - n.width, pad + (170 - n.height) // 2))
            put(im, c, 70 - pad, y - pad, anchor="lt"); y += 190
    elif kind == "bullets":
        for m in v["maddeler"][:5]:
            txt = para_sprite(m, F(BOLD, 50), INK, 720, gap=6); h = max(150, txt.height + 70)
            c, pad = card(940, h, 34)
            g = hgrad(60, 60, BLUE, CYAN); mm = Image.new("L", (60, 60), 0); ImageDraw.Draw(mm).ellipse((0, 0, 59, 59), fill=255); g.putalpha(mm)
            ImageDraw.Draw(g).line((17, 31, 26, 40, 43, 21), fill=WHITE, width=7)
            c.alpha_composite(g, (pad + 34, pad + (h - 60) // 2)); c.alpha_composite(txt, (pad + 124, pad + (h - txt.height) // 2))
            put(im, c, 70 - pad, y - pad, anchor="lt"); y += h + 26
    elif kind == "sohbet":
        m = v["mesajlar"]; pw, ph_ = 620, 900
        _, (sx, sy, sw, shh) = phone_body(pw, ph_)
        phn = phone_with_screen(pw, ph_, chat_screen(sw, shh, m, len(m), False, scale=0.86))
        put(im, phn, 540, y + phn.height / 2 - 50); y += phn.height - 80
    elif kind == "sayilar":
        for i, m in enumerate(v["maddeler"][:4]):
            txt = para_sprite(m, F(BOLD, 48), INK, 690, gap=6); h = max(170, txt.height + 70)
            c, pad = card(940, h, 34)
            nb = Image.new("RGBA", (120, 120), (0, 0, 0, 0)); g = hgrad(120, 120, BLUE, CYAN); g.putalpha(_round_mask(120, 120, 60)); nb.alpha_composite(g)
            ns = text_sprite(str(i + 1), F(BLACK, 76), WHITE, pad=0); nb.alpha_composite(ns, ((120 - ns.width) // 2, (120 - ns.height) // 2 - 4))
            c.alpha_composite(nb, (pad + 30, pad + (h - 120) // 2)); c.alpha_composite(txt, (pad + 180, pad + (h - txt.height) // 2))
            put(im, c, 70 - pad, y - pad, anchor="lt"); y += h + 24
    elif kind == "efsane":
        for lab, txt, gr in (("EFSANE", v["efsane"], (PINK, (150, 20, 90))), ("GERÇEK", v["gercek"], (GREEN, (0, 110, 120)))):
            c = _myth_card(lab, txt, gr, 940, fs=44); put(im, c, 540, y + c.height / 2 - 40); y += c.height - 70
    elif kind == "kampanya":
        if v.get("paket") and v.get("paket", "").lower() != v.get("baslik", "").lower():
            pk = pill(v["paket"], fit_font(v["paket"], BLACK, 70, 800), WHITE, padx=44, pady=20, grad=(BLUE, (0, 150, 230))); put(im, pk, 70, y, anchor="lt"); y += pk.height + 30
        if v.get("eski"):
            o = text_sprite(f"{_tl(v['eski'])} {v.get('birim', 'TL')}", F(BOLD, 70), (200, 210, 240), pad=0); put(im, o, 70, y, anchor="lt")
            ImageDraw.Draw(im).line((64, y + o.height // 2 + 14, 70 + o.width + 6, y + o.height // 2 - 14), fill=(255, 60, 90), width=10); y += o.height + 20
        if v.get("yeni"):
            r_ = row([text_sprite(_tl(v["yeni"]), F(BLACK, 230), CYAN, pad=0), text_sprite(v.get("birim", "TL"), F(XB, 64), WHITE, pad=0)], gap=14)
            put(im, r_, 70, y, anchor="lt"); y += r_.height + 30
        if v.get("rozet"):
            rz = pill(v["rozet"], F(BLACK, 48), WHITE, grad=(PINK, (190, 0, 120)), padx=40, pady=18); put(im, rz, 70, y, anchor="lt"); y += rz.height + 30
        if v.get("alt"):
            a = para_sprite(v["alt"], F(BOLD, 46), WHITE, 940); put(im, a, 70, y, anchor="lt"); y += a.height + 20
    elif kind == "maskot":
        from . import maskot
        bl = maskot.balon(v["balon"], 900); put(im, bl, 540, y, anchor="mt"); y += bl.height - 10
        ms = maskot.post_sprite(v.get("ifade", "mutlu"), v.get("efektler", ()), tuple(v.get("kol", (112, 68))), v.get("gri", False))
        ms = ms.resize((int(ms.width * 0.56), int(ms.height * 0.56)), Image.LANCZOS)
        put(im, ms, 540, y, anchor="mt"); y += ms.height - 20
    elif kind == "soru":
        for i, m in enumerate(v["secenekler"][:4]):
            c, pad = card(940, 150, 34)
            lb = pill("ABCD"[i], F(BLACK, 54), WHITE, grad=(BLUE, CYAN), padx=30, pady=14)
            c.alpha_composite(lb, (pad + 30, pad + (150 - lb.height) // 2))
            tx = text_sprite(m, fit_font(m, BOLD, 50, 720), INK, pad=0); c.alpha_composite(tx, (pad + 170, pad + (150 - tx.height) // 2))
            put(im, c, 70 - pad, y - pad, anchor="lt"); y += 150 + 22
        y += 10; put(im, text_sprite(v.get("cagri", "Cevabını yorumlara yaz!"), F(XB, 46), CYAN), 540, y + 30); y += 90
    elif kind == "tanitim":
        c = info_card(shop, 940); put(im, c, 540, y + c.height / 2 - 40); y += c.height - 40
    if v.get("not"):
        n = para_sprite(v["not"], F(MED, 28), SOFT, 940); put(im, n, 70, y + 10, anchor="lt"); y += n.height + 20
    top, bottom = 130, H - 130 - 20
    off = top + max(0, (bottom - top - y) // 2)
    canvas.alpha_composite(im.crop((0, 0, W, min(y, H))), (0, off))
    im = canvas
    # footer
    foot = Image.new("RGBA", (W, 130), (5, 14, 50, 215))
    fr = row([text_sprite(shop["phone"], F(BLACK, 46), WHITE, pad=0), text_sprite("·  " + shop["district"], F(BOLD, 36), CYAN, pad=0)], gap=18, valign="m")
    put(foot, fr, W / 2, 65)
    put(im, foot, 0, H - 130, anchor="lt")
    im.convert("RGB").save(out_path, "JPEG", quality=92)
