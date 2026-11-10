"""Story'ye ozel, dikkat cekici slaytlar (Reels'ten farkli, ekrana bakani durduran formatlar).

Bu modul import edildiginde slaytlar render.SLIDES'a eklenir.
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from . import render as R

W, H = 1080, 1920


def _crack_layer(seed=7, cx=600, cy=760):
    """Tum ekrani kaplayan gercekci catlak."""
    rng = np.random.default_rng(seed)
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for k in range(26):
        a = rng.uniform(0, 2 * math.pi); x, y = cx, cy
        for _ in range(int(rng.integers(4, 9))):
            a += rng.uniform(-0.45, 0.45); ln = rng.uniform(70, 260)
            nx, ny = x + math.cos(a) * ln, y + math.sin(a) * ln
            w = int(rng.integers(2, 6))
            d.line((x, y, nx, ny), fill=(255, 255, 255, 235), width=w)
            d.line((x + 2, y + 2, nx + 2, ny + 2), fill=(0, 0, 0, 90), width=max(1, w - 1))
            if rng.random() < 0.35:  # yan dal
                b = a + rng.choice([-1, 1]) * rng.uniform(0.6, 1.2); bl = ln * 0.5
                d.line((nx, ny, nx + math.cos(b) * bl, ny + math.sin(b) * bl), fill=(255, 255, 255, 200), width=max(1, w - 2))
            x, y = nx, ny
    for r in (40, 75, 120):  # darbe noktasi halkalari
        d.ellipse((cx - r, cy - r * 0.9, cx + r, cy + r * 0.9), outline=(255, 255, 255, 200), width=3)
    shards = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sd = ImageDraw.Draw(shards)
    for k in range(10):
        a = rng.uniform(0, 2 * math.pi); r1, r2 = rng.uniform(30, 120), rng.uniform(140, 300)
        a2 = a + rng.uniform(0.2, 0.5)
        sd.polygon([(cx + math.cos(a) * r1, cy + math.sin(a) * r1), (cx + math.cos(a) * r2, cy + math.sin(a) * r2),
                    (cx + math.cos(a2) * r2, cy + math.sin(a2) * r2)], fill=(255, 255, 255, int(rng.integers(18, 50))))
    im.alpha_composite(shards)
    return im


def slide_kirik_saka(im, t, dur, d, shop, C):
    """'Ekranin kirildi mi?' sakasi: ani catlak + titreme + flas, sonra rahatlatma ve mesaj.
    d = {once?, sonra, mesaj}"""
    hit = 0.9
    if t < hit:
        tx = C.get_or("ko", lambda: R.para_sprite(d.get("once", "Bir saniye…"), R.F(R.BLACK, 96), R.WHITE, 940, align="c"))
        R.put(im, tx, 540, 900, R.eout(R.prog(t, 0, 0.3)))
        return
    lt = t - hit
    if lt < 0.12:  # beyaz flas
        im.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(230 * (1 - lt / 0.12)))))
    cr = C.get_or("cr", _crack_layer)
    sh = math.sin(lt * 70) * 22 * max(0, 1 - lt / 0.6)
    a = 1 - R.prog(lt, 2.0, 0.5)
    if a > 0:
        R.put(im, cr, sh, sh * 0.5, a, anchor="lt")
    if lt > 2.2:
        tx = C.get_or("ks", lambda: R.para_sprite(d.get("sonra", "Korkma, senin ekranın sağlam."), R.F(R.BLACK, 84), R.WHITE, 940, gap=8, align="c"))
        R.put(im, tx, 540, 760, R.eout(R.prog(lt, 2.2, 0.4)))
    if lt > 3.0:
        m = C.get_or("km", lambda: R.pill(d["mesaj"], R.fit_font(d["mesaj"], R.BLACK, 58, 900), R.WHITE, grad=(R.PINK, (190, 0, 120)), padx=44, pady=24))
        p = R.prog(lt, 3.0, 0.45); R.put(im, m, 540, 1100, R.clamp(p * 2), scale=0.5 + 0.5 * R.eback(p) if p < 1 else 1 + 0.03 * math.sin(t * 7))


def slide_gelen_arama(im, t, dur, d, shop, C):
    """Telefon arama ekrani gorunumu: MEYDAN GSM ariyor. d = {alt, mesaj}"""
    im.alpha_composite(Image.new("RGBA", (W, H), (8, 12, 28, 200)))
    e = R.env(t, dur)
    for k in range(3):  # calma halkalari
        ph = (t * 0.8 + k / 3) % 1; r = 150 + ph * 230
        ring = Image.new("RGBA", (int(2 * r) + 8, int(2 * r) + 8), (0, 0, 0, 0))
        ImageDraw.Draw(ring).ellipse((4, 4, 2 * r + 4, 2 * r + 4), outline=R.CYAN + (int(200 * (1 - ph)),), width=6)
        R.put(im, ring, 540, 640, e)
    av = C.get_or("av", lambda: _avatar(300))
    R.put(im, av, 540, 640, e, scale=1 + 0.03 * math.sin(t * 9))
    nm = C.get_or("nm", lambda: R.text_sprite(f"{shop['name_main']} {shop['name_accent']}", R.F(R.BLACK, 96), R.WHITE))
    R.put(im, nm, 540, 960, e)
    al = C.get_or("al", lambda: R.text_sprite(d.get("alt", "arıyor…"), R.F(R.SEMI, 52), (190, 205, 235)))
    R.put(im, al, 540, 1060, e * (0.6 + 0.4 * abs(math.sin(t * 2.5))))
    for i, (lab, col, x) in enumerate((("Reddet", (235, 60, 80), 300), ("Kabul et", (40, 200, 110), 780))):
        b = C.get_or(("bt", i), lambda col=col, lab=lab, i=i: _call_btn(col, lab, i))
        sc = 1.0 + (0.08 * abs(math.sin(t * 5)) if i == 1 and t > 1.8 else 0)
        R.put(im, b, x, 1500, e, scale=sc)
    if t > 2.6 and d.get("mesaj"):
        m = C.get_or("ms", lambda: R.pill(d["mesaj"], R.fit_font(d["mesaj"], R.BLACK, 54, 920), R.INK, (255, 255, 255), padx=40, pady=22))
        p = R.prog(t, 2.6, 0.4); R.put(im, m, 540, 1250, e * R.clamp(p * 2), scale=0.6 + 0.4 * R.eback(p) if p < 1 else 1)


def _avatar(sz):
    g = R.hgrad(sz, sz, R.BLUE, R.CYAN); m = Image.new("L", (sz, sz), 0); ImageDraw.Draw(m).ellipse((0, 0, sz - 1, sz - 1), fill=255); g.putalpha(m)
    s = R.text_sprite("M", R.F(R.BLACK, int(sz * 0.55)), R.WHITE, pad=0); g.alpha_composite(s, ((sz - s.width) // 2, (sz - s.height) // 2 - 6))
    return g


def _call_btn(col, lab, i):
    im = Image.new("RGBA", (300, 300), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse((60, 10, 240, 190), fill=col)
    # ahize simgesi (yuvarlak hatli)
    cx, cy = 150, 100; ang = 135 if i == 0 else 0
    hs = Image.new("RGBA", (120, 120), (0, 0, 0, 0)); hd = ImageDraw.Draw(hs)
    hd.rounded_rectangle((10, 46, 110, 74), 14, fill=(255, 255, 255)); hd.rounded_rectangle((6, 40, 36, 86), 12, fill=(255, 255, 255)); hd.rounded_rectangle((84, 40, 114, 86), 12, fill=(255, 255, 255))
    hs = hs.rotate(ang + 20, resample=Image.BICUBIC); im.alpha_composite(hs, (cx - 60, cy - 60))
    t = R.text_sprite(lab, R.F(R.SEMI, 40), R.WHITE, pad=0); im.alpha_composite(t, ((300 - t.width) // 2, 220))
    return im


def slide_pil_uyari(im, t, dur, d, shop, C):
    """Sistem uyarisi gorunumlu 'pil zayif' karti. d = {baslik, metin, mesaj}"""
    e = R.env(t, dur)
    dim = 160 if t > 0.3 else int(160 * t / 0.3)
    im.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, dim)))
    def card():
        w, h = 760, 520; c = Image.new("RGBA", (w, h), (0, 0, 0, 0)); dd = ImageDraw.Draw(c)
        dd.rounded_rectangle((0, 0, w - 1, h - 1), 48, fill=(245, 246, 250, 250))
        px, py = w // 2 - 90, 70
        dd.rounded_rectangle((px, py, px + 170, py + 80), 18, outline=(30, 30, 40), width=8)
        dd.rounded_rectangle((px + 170, py + 24, px + 186, py + 56), 5, fill=(30, 30, 40))
        dd.rounded_rectangle((px + 14, py + 14, px + 34, py + 66), 6, fill=(235, 50, 70))
        t1 = R.text_sprite(d.get("baslik", "Pil Zayıf"), R.F(R.BLACK, 64), (20, 20, 30), pad=0); c.alpha_composite(t1, ((w - t1.width) // 2, 190))
        t2 = R.para_sprite(d.get("metin", "%1 pil kaldı."), R.F(R.MED, 42), (80, 85, 100), w - 100, align="c"); c.alpha_composite(t2, ((w - t2.width) // 2, 280))
        dd.line((0, h - 110, w, h - 110), fill=(210, 212, 220), width=2)
        k = R.text_sprite("Kapat", R.F(R.SEMI, 48), (0, 110, 230), pad=0); c.alpha_composite(k, ((w - k.width) // 2, h - 82))
        return c
    cd = C.get_or("cd", card)
    p = R.prog(t, 0.2, 0.35)
    R.put(im, cd, 540 + (math.sin(t * 40) * 8 if 0.55 < t < 0.9 else 0), 860, e * R.clamp(p * 2), scale=0.8 + 0.2 * R.eback(p) if p < 1 else 1)
    if t > 2.0 and d.get("mesaj"):
        m = C.get_or("pm", lambda: R.para_sprite(d["mesaj"], R.F(R.BLACK, 70), R.WHITE, 960, gap=8, align="c"))
        R.put(im, m, 540, 1420, e * R.eout(R.prog(t, 2.0, 0.4)))


def slide_bildirim_yagmuru(im, t, dur, d, shop, C):
    """Ust uste dusen bildirimler, sonra tek cevap. d = {bildirimler:[(baslik, metin)], cevap}"""
    e = R.env(t, dur)
    ns = d["bildirimler"]; gap = 0.45
    for i, (b, m) in enumerate(ns):
        st = 0.2 + i * gap
        if t < st: break
        card = C.get_or(("bn", i), lambda b=b, m=m: _notif(b, m))
        p = R.eback(R.prog(t, st, 0.35)) if t - st < 0.35 else 1
        y = 360 + i * 205
        R.put(im, card, 540 + (1 - p) * 0, y - (1 - p) * 120, e * R.clamp((t - st) * 5), scale=0.9 + 0.1 * p)
    end = 0.2 + len(ns) * gap + 0.4
    if t > end:
        cv = C.get_or("cv", lambda: R.pill(d["cevap"], R.fit_font(d["cevap"], R.BLACK, 66, 920), R.WHITE, grad=(R.BLUE, (0, 150, 230)), padx=50, pady=28))
        p = R.prog(t, end, 0.45); R.put(im, cv, 540, 360 + len(ns) * 205 + 140, e * R.clamp(p * 2), scale=0.5 + 0.5 * R.eback(p) if p < 1 else 1 + 0.03 * math.sin(t * 7))


def _notif(b, m):
    w, h = 960, 180; c = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(c)
    d.rounded_rectangle((0, 0, w - 1, h - 1), 40, fill=(250, 251, 255, 240))
    c.alpha_composite(_avatar(84), (30, 48))
    c.alpha_composite(R.text_sprite(b, R.fit_font(b, R.BLACK, 46, w - 170), R.INK, pad=0), (140, 40))
    c.alpha_composite(R.text_sprite(m, R.fit_font(m, R.MED, 38, w - 170), (80, 90, 120), pad=0), (140, 104))
    return c


def slide_durdur(im, t, dur, d, shop, C):
    """'Ekrana dokun, durdur!' oyunu: kelimeler hizla doner. d = {kelimeler, alt}"""
    e = R.env(t, dur)
    hd = C.get_or("dh", lambda: R.para_sprite(d.get("baslik", "Ekrana basılı tut, durdur!"), R.F(R.BLACK, 76), R.WHITE, 960, gap=6, align="c"))
    R.put(im, hd, 540, 380, e * (0.75 + 0.25 * abs(math.sin(t * 4))))
    ws = d["kelimeler"]
    i = int(t / 0.14) % len(ws)
    def box(w):
        sp = R.text_sprite(w, R.fit_font(w, R.BLACK, 120, 820), R.INK, pad=0)
        b = Image.new("RGBA", (900, 330), (0, 0, 0, 0)); bd = ImageDraw.Draw(b)
        bd.rounded_rectangle((0, 0, 899, 329), 60, fill=(255, 255, 255)); bd.rounded_rectangle((10, 10, 889, 319), 52, outline=R.CYAN, width=8)
        b.alpha_composite(sp, ((900 - sp.width) // 2, (330 - sp.height) // 2)); return b
    R.put(im, C.get_or(("dw", i), lambda: box(ws[i])), 540, 960, e)
    al = C.get_or("da", lambda: R.para_sprite(d.get("alt", "Durduğun şey bugünkü ihtiyacın!"), R.F(R.BOLD, 54), R.SOFT, 940, align="c"))
    R.put(im, al, 540, 1400, e)
    m = C.get_or("dm", lambda: R.pill(d.get("mesaj", "Hepsi MEYDAN GSM'de"), R.F(R.BLACK, 56), R.WHITE, grad=(R.PINK, (190, 0, 120)), padx=44, pady=22))
    R.put(im, m, 540, 1620, e)


def slide_quiz(im, t, dur, d, shop, C):
    """Bil bakalim: soru + siklar; cevap=True ise dogru sik yesil yanar. d = {soru, siklar, dogru, cevap?, aciklama?, alt?}"""
    e = R.env(t, dur)
    et = C.get_or("qe", lambda: R.pill("BİL BAKALIM" if not d.get("cevap") else "CEVAP", R.F(R.BLACK, 50), R.INK, (255, 214, 60), padx=40, pady=18))
    R.put(im, et, 540, 300, e)
    q = C.get_or("qq", lambda: R.para_sprite(d["soru"], R.F(R.BLACK, 78), R.WHITE, 960, gap=8, align="c"))
    R.put(im, q, 540, 520, e * R.eout(R.prog(t, 0.1, 0.4)))
    for i, s in enumerate(d["siklar"]):
        ok = d.get("cevap") and i == d["dogru"]
        wrong = d.get("cevap") and i != d["dogru"]
        def mk(s=s, i=i, ok=ok, wrong=wrong):
            w, h = 900, 170; c = Image.new("RGBA", (w, h), (0, 0, 0, 0)); dd = ImageDraw.Draw(c)
            fill = (40, 200, 110) if ok else ((255, 255, 255, 110) if wrong else (255, 255, 255))
            dd.rounded_rectangle((0, 0, w - 1, h - 1), 50, fill=fill)
            lb = R.text_sprite("ABC"[i], R.F(R.BLACK, 70), R.WHITE if ok else R.BLUE, pad=0); c.alpha_composite(lb, (50, (h - lb.height) // 2))
            tx = R.text_sprite(s, R.fit_font(s, R.BLACK, 62, 700), R.WHITE if ok else R.INK, pad=0); c.alpha_composite(tx, (150, (h - tx.height) // 2))
            return c
        c = C.get_or(("qs", i), mk); p = R.prog(t, 0.4 + i * 0.18, 0.35)
        reveal = 1.0
        if d.get("cevap"):
            reveal = 1 + 0.06 * math.sin(math.pi * R.prog(t, 1.0, 0.5)) if ok else 1
        R.put(im, c, 540 + (1 - R.eout(p)) * 900, 860 + i * 210, e * R.clamp(p * 2), scale=reveal)
    alt = d.get("aciklama") if d.get("cevap") else d.get("alt", "Cevap bir sonraki Story'de")
    if alt:
        a = C.get_or("qa", lambda: R.para_sprite(alt, R.F(R.BOLD, 52), R.SOFT if not d.get("cevap") else R.WHITE, 940, gap=8, align="c"))
        R.put(im, a, 540, 1560, e * R.eout(R.prog(t, 1.0, 0.4)))


def slide_saat(im, t, dur, d, shop, C):
    """Kadran: 09:00'dan 22:30'a doluyor. d = {ust, mesaj}"""
    e = R.env(t, dur)
    u = C.get_or("su", lambda: R.para_sprite(d.get("ust", "Her gün"), R.F(R.BLACK, 84), R.WHITE, 960, align="c"))
    R.put(im, u, 540, 380, e)
    p = R.eout(R.prog(t, 0.3, 2.0)); r = 330; cx, cy = 540, 940
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dd = ImageDraw.Draw(lay)
    dd.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(255, 255, 255, 60), width=34)
    a0, a1 = 9 / 24 * 360 - 90, (9 + 13.5 * p) / 24 * 360 - 90
    dd.arc((cx - r, cy - r, cx + r, cy + r), a0, a1, fill=R.CYAN + (255,), width=34)
    R.put(im, lay, 0, 0, e, anchor="lt")
    mins = int(9 * 60 + 13.5 * 60 * p); hh, mm = divmod(mins, 60)
    tx = R.text_sprite(f"{hh:02d}:{mm:02d}", R.F(R.BLACK, 170), R.WHITE, pad=0)
    R.put(im, tx, cx, cy, e)
    s = C.get_or("ss", lambda: R.text_sprite("09:00 – 22:30", R.F(R.SEMI, 52), R.SOFT))
    R.put(im, s, cx, cy + 140, e)
    if t > 2.4:
        m = C.get_or("sm", lambda: R.pill(d.get("mesaj", "Biz buradayız!"), R.F(R.BLACK, 60), R.WHITE, grad=(R.PINK, (190, 0, 120)), padx=46, pady=24))
        q = R.prog(t, 2.4, 0.45); R.put(im, m, 540, 1450, e * R.clamp(q * 2), scale=0.5 + 0.5 * R.eback(q) if q < 1 else 1)


def slide_pov(im, t, dur, d, shop, C):
    """POV formati: buyuk 'POV:' + durum, altta Meydi tepkisi. d = {durum, ifade, efektler, balon?}"""
    from . import maskot
    e = R.env(t, dur)
    pv = C.get_or("pv", lambda: R.text_sprite("POV:", R.F(R.BLACK, 120), R.CYAN, pad=0))
    R.put(im, pv, 80, 300, e, anchor="lm")
    ds = C.get_or("pd", lambda: R.para_sprite(d["durum"], R.F(R.BLACK, 72), R.WHITE, 920, gap=8))
    R.put(im, ds, 80, 390, e * R.eout(R.prog(t, 0.15, 0.4)), anchor="lt")
    mk = maskot.ciz(d.get("ifade", "saskin"), t=t, kol_sol=200 if d.get("ifade") == "saskin" else 112, kol_sag=-20 if d.get("ifade") == "saskin" else 68,
                    goz_kapali=1.0 if (t % 2.8) < 0.12 else 0, efektler=tuple(d.get("efektler", ())))
    R.put(im, mk, 540 + math.sin(t * 40) * 8 * (1 - R.prog(t, 0.3, 0.8)), 1880, e, scale=1.1, anchor="mb")
    if d.get("balon") and t > 1.2:
        b = C.get_or("pb", lambda: maskot.balon(d["balon"], 820)); q = R.prog(t, 1.2, 0.35)
        R.put(im, b, 540, 1010, e * R.clamp(q * 2), scale=0.5 + 0.5 * R.eback(q) if q < 1 else 1, anchor="mb")


R.SLIDES.update({"kirik_saka": slide_kirik_saka, "gelen_arama": slide_gelen_arama, "pil_uyari": slide_pil_uyari,
                 "bildirim_yagmuru": slide_bildirim_yagmuru, "durdur": slide_durdur, "quiz": slide_quiz,
                 "saat": slide_saat, "pov": slide_pov})
