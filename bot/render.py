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
        top = np.array([7, 20, 72]); bot = np.array([20, 70, 200])
        arr = top * (1 - k[..., None]) + bot * k[..., None]
        self.base = Image.fromarray(arr.astype(np.uint8), "RGB").convert("RGBA")
        self.blobs = []
        for color, r, a in [(CYAN, 520, 0.38), ((120, 60, 255), 600, 0.30), (PINK, 420, 0.20)]:
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
    btn = C.get_or(("c_btn", d.get("buton", "")), lambda: pill(d.get("buton", "Mağazamıza bekleriz!"), F(BLACK, 54), WHITE, padx=60, pady=30, grad=(PINK, (190, 0, 120))))
    p = prog(t, 1.1, 0.6)
    put(im, btn, 540, 1420, eout(p) * e, scale=1 + 0.035 * math.sin((t - 1.7) * 6) if p >= 1 else 0.6 + 0.4 * eback(p))


SLIDES = {"intro": slide_intro, "hook": slide_hook, "tariffs": slide_tariffs, "plans": slide_plans,
          "bullets": slide_bullets, "cta": slide_cta}


def render_reel(slides, shop, out_path, music_path=None, seed=0, workdir=None):
    """slides: [{'tip': 'hook', 'sure': 3.0, 'veri': {...}}, ...]"""
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
def render_post(d, shop, out_path, seed=0):
    """d = {tip: 'tariffs'|'plans'|'bullets'|'tanitim', ...}"""
    W, H = 1080, 1350
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
