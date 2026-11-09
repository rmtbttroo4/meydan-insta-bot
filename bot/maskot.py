"""MEYDAN GSM maskotu: yuzu ekraninda olan sevimli bir telefon karakteri.

Tum cizim kodla yapilir (hazir gorsel yok). 2 kat buyuk cizilip kucultulur, kenarlar yumusak olur.
ciz(...) -> RGBA sprite (yaklasik 560 x 980 px), karakterin ayak hizasi sprite'in altindadir.
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from . import render as R

SS = 2  # supersampling
OUT = (24, 30, 58)  # cizgi rengi


def _p(v): return int(round(v * SS))


def _blend(c1, c2, k): return tuple(int(a * (1 - k) + b * k) for a, b in zip(c1, c2))


def _gray(c):
    g = int(0.3 * c[0] + 0.59 * c[1] + 0.11 * c[2]); return (g, g, g)


def _limb(d, x0, y0, ang, ln, col, w=24, hand=22):
    """Kol: omuzdan ang derece (0 = sag, 90 = asagi) yonunde, ucunda yuvarlak el."""
    x1 = x0 + math.cos(math.radians(ang)) * ln; y1 = y0 + math.sin(math.radians(ang)) * ln
    d.line((_p(x0), _p(y0), _p(x1), _p(y1)), fill=OUT, width=_p(w + 10))
    d.line((_p(x0), _p(y0), _p(x1), _p(y1)), fill=col, width=_p(w))
    d.ellipse((_p(x1 - hand - 5), _p(y1 - hand - 5), _p(x1 + hand + 5), _p(y1 + hand + 5)), fill=OUT)
    d.ellipse((_p(x1 - hand), _p(y1 - hand), _p(x1 + hand), _p(y1 + hand)), fill=(255, 255, 255))


def _star(d, cx, cy, r, col):
    pts = []
    for k in range(10):
        rr = r if k % 2 == 0 else r * 0.45; a = -math.pi / 2 + k * math.pi / 5
        pts.append((_p(cx + math.cos(a) * rr), _p(cy + math.sin(a) * rr)))
    d.polygon(pts, fill=col)


def _heart(d, cx, cy, r, col):
    d.ellipse((_p(cx - r), _p(cy - r * 0.6), _p(cx), _p(cy + r * 0.3)), fill=col)
    d.ellipse((_p(cx), _p(cy - r * 0.6), _p(cx + r), _p(cy + r * 0.3)), fill=col)
    d.polygon([(_p(cx - r * 0.95), _p(cy - 0.05 * r)), (_p(cx + r * 0.95), _p(cy - 0.05 * r)), (_p(cx), _p(cy + r))], fill=col)


def ciz(ifade="mutlu", t=0.0, kol_sol=125, kol_sag=55, goz_kapali=0.0, bak=(0.0, 0.0), efektler=(), gri=False, seed=1):
    """Maskotu cizer.
    ifade: mutlu | gulen | uzgun | agla | saskin | goz_kirp | uykulu | heyecan | dusunceli
    kol_sol / kol_sag: kol acilari (derece; 90 = asagi sarkik, 200/-20 = havada)
    goz_kapali: 0..1 (goz kirpma), bak: gozbebegi yonu (-1..1, -1..1)
    efektler: catlak, yara_bandi, kilif, koruyucu, pil_dusuk, pil_dolu, sinyal, yildiz, kalp, ter, kutu
    """
    W, H = 760, 1000
    im = Image.new("RGBA", (_p(W), _p(H)), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    bw, bh = 380, 640; bx, by = (W - bw) / 2, 210
    body_a, body_b = (R.BLUE, R.CYAN) if not gri else ((120, 124, 136), (170, 174, 184))
    if gri: body_a, body_b = _gray(body_a), _gray(body_b)
    leg_col = (40, 52, 110) if not gri else (90, 92, 100)

    # bacaklar ve ayakkabilar
    for sx in (-1, 1):
        lx = W / 2 + sx * 85
        d.rounded_rectangle((_p(lx - 22), _p(by + bh - 20), _p(lx + 22), _p(by + bh + 90)), _p(18), fill=OUT)
        d.rounded_rectangle((_p(lx - 14), _p(by + bh - 20), _p(lx + 14), _p(by + bh + 86)), _p(12), fill=leg_col)
        d.ellipse((_p(lx - 62 + sx * 12), _p(by + bh + 62), _p(lx + 62 + sx * 12), _p(by + bh + 122)), fill=OUT)
        d.ellipse((_p(lx - 55 + sx * 12), _p(by + bh + 68), _p(lx + 55 + sx * 12), _p(by + bh + 114)), fill=(255, 255, 255))
        d.rectangle((_p(lx - 55 + sx * 12), _p(by + bh + 96), _p(lx + 55 + sx * 12), _p(by + bh + 104)), fill=R.PINK if not gri else (150, 150, 150))

    # govde (gradyan) + kalin dis cizgi
    if "kilif" in efektler:
        d.rounded_rectangle((_p(bx - 22), _p(by - 22), _p(bx + bw + 22), _p(by + bh + 22)), _p(110), fill=OUT)
        d.rounded_rectangle((_p(bx - 16), _p(by - 16), _p(bx + bw + 16), _p(by + bh + 16)), _p(104), fill=R.PINK)
    d.rounded_rectangle((_p(bx - 8), _p(by - 8), _p(bx + bw + 8), _p(by + bh + 8)), _p(96), fill=OUT)
    g = R.hgrad(_p(bw), _p(bh), body_a, body_b)
    m = Image.new("L", g.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, g.width - 1, g.height - 1), _p(90), fill=255)
    g.putalpha(m); im.alpha_composite(g, (_p(bx), _p(by))); d = ImageDraw.Draw(im)
    # kollar (govdenin onunde, omuzdan cikar)
    _limb(d, bx + 4, by + bh * 0.50, kol_sol, 160, body_b)
    _limb(d, bx + bw - 4, by + bh * 0.50, kol_sag, 160, body_b)
    # yan dugmeler
    d.rounded_rectangle((_p(bx + bw + 4), _p(by + 150), _p(bx + bw + 16), _p(by + 240)), _p(6), fill=OUT)

    # ekran (yuz)
    sx0, sy0, sx1, sy1 = bx + 30, by + 34, bx + bw - 30, by + bh - 60
    scr_col = (22, 30, 62) if not gri else (52, 54, 60)
    d.rounded_rectangle((_p(sx0), _p(sy0), _p(sx1), _p(sy1)), _p(66), fill=scr_col)
    d.rounded_rectangle((_p(W / 2 - 52), _p(sy0 + 16), _p(W / 2 + 52), _p(sy0 + 44)), _p(14), fill=(8, 10, 20))
    # alt cizgi (ev tusu)
    d.rounded_rectangle((_p(W / 2 - 50), _p(by + bh - 36), _p(W / 2 + 50), _p(by + bh - 26)), _p(5), fill=(255, 255, 255, 150))

    cx = W / 2; ey = sy0 + (sy1 - sy0) * 0.40; ex = 78
    lx, ly = bak
    # gozler
    for k, sx in enumerate((-1, 1)):
        gx = cx + sx * ex
        kapali = goz_kapali
        if ifade == "goz_kirp" and sx == 1: kapali = 1.0
        if ifade == "uykulu": kapali = max(kapali, 0.55)
        rw, rh = 50, 60 * (1 - 0.92 * kapali)
        if ifade in ("saskin",): rw, rh = 56, 68 * (1 - 0.92 * kapali)
        if ifade == "gulen" or (ifade == "mutlu" and kapali > 0.9):
            d.arc((_p(gx - 40), _p(ey - 30), _p(gx + 40), _p(ey + 34)), 200, 340, fill=(255, 255, 255), width=_p(12)); continue
        if rh < 8:
            d.line((_p(gx - 40), _p(ey), _p(gx + 40), _p(ey)), fill=(255, 255, 255), width=_p(10)); continue
        d.ellipse((_p(gx - rw), _p(ey - rh), _p(gx + rw), _p(ey + rh)), fill=(255, 255, 255))
        if ifade == "heyecan":
            _star(d, gx + lx * 10, ey + ly * 10, 34, (255, 200, 40))
        else:
            pr = 24 if ifade != "saskin" else 16
            px, py = gx + lx * 16, ey + ly * min(16, rh * 0.4) + (8 if ifade == "uykulu" else 0)
            d.ellipse((_p(px - pr), _p(py - pr), _p(px + pr), _p(py + pr)), fill=(14, 18, 40))
            d.ellipse((_p(px + pr * 0.15), _p(py - pr * 0.75), _p(px + pr * 0.7), _p(py - pr * 0.2)), fill=(255, 255, 255))
        if ifade == "uykulu":  # goz kapagi
            d.rectangle((_p(gx - rw - 2), _p(ey - 64), _p(gx + rw + 2), _p(ey - rh + 18)), fill=scr_col)

    # kaslar
    bc = (255, 255, 255)
    for sx in (-1, 1):
        gx = cx + sx * ex; yb = ey - 92
        if ifade in ("uzgun", "agla"):
            d.line((_p(gx - 34 * sx), _p(yb + 4), _p(gx + 30 * sx), _p(yb - 18)), fill=bc, width=_p(10))
        elif ifade == "saskin":
            d.arc((_p(gx - 36), _p(yb - 30), _p(gx + 36), _p(yb + 10)), 200, 340, fill=bc, width=_p(10))
        elif ifade == "dusunceli":
            d.line((_p(gx - 30), _p(yb - (10 if sx > 0 else -2)), _p(gx + 30), _p(yb - (18 if sx > 0 else -2))), fill=bc, width=_p(10))
        elif ifade in ("mutlu", "gulen", "heyecan", "goz_kirp"):
            d.arc((_p(gx - 34), _p(yb - 16), _p(gx + 34), _p(yb + 20)), 210, 330, fill=bc, width=_p(10))

    # yanaklar
    if ifade in ("mutlu", "gulen", "heyecan", "goz_kirp"):
        for sx in (-1, 1):
            gx = cx + sx * 118
            ch = Image.new("RGBA", im.size, (0, 0, 0, 0))
            ImageDraw.Draw(ch).ellipse((_p(gx - 30), _p(ey + 56), _p(gx + 30), _p(ey + 86)), fill=(255, 110, 150, 150))
            im.alpha_composite(ch)
        d = ImageDraw.Draw(im)

    # agiz
    my = sy0 + (sy1 - sy0) * 0.66
    if ifade in ("mutlu", "goz_kirp"):
        d.arc((_p(cx - 62), _p(my - 50), _p(cx + 62), _p(my + 30)), 20, 160, fill=(255, 255, 255), width=_p(12))
    elif ifade in ("gulen", "heyecan"):
        d.chord((_p(cx - 76), _p(my - 56), _p(cx + 76), _p(my + 52)), 0, 180, fill=(255, 255, 255))
        d.chord((_p(cx - 44), _p(my + 6), _p(cx + 44), _p(my + 48)), 0, 180, fill=(255, 110, 140))
    elif ifade in ("uzgun", "agla"):
        d.arc((_p(cx - 56), _p(my - 8), _p(cx + 56), _p(my + 62)), 200, 340, fill=(255, 255, 255), width=_p(12))
    elif ifade == "saskin":
        d.ellipse((_p(cx - 30), _p(my - 26), _p(cx + 30), _p(my + 40)), fill=(255, 255, 255))
        d.ellipse((_p(cx - 18), _p(my - 10), _p(cx + 18), _p(my + 28)), fill=(255, 110, 140))
    elif ifade == "uykulu":
        d.line((_p(cx - 30), _p(my + 6), _p(cx + 30), _p(my + 6)), fill=(255, 255, 255), width=_p(10))
    elif ifade == "dusunceli":
        d.line((_p(cx - 34), _p(my + 10), _p(cx + 30), _p(my - 2)), fill=(255, 255, 255), width=_p(10))
    if ifade == "agla":
        for sx in (-1, 1):
            gx = cx + sx * ex; tk = (t * 1.6 + (0.5 if sx > 0 else 0)) % 1
            ty = ey + 50 + tk * 110
            d.ellipse((_p(gx - 14), _p(ty - 14), _p(gx + 14), _p(ty + 18)), fill=(120, 200, 255, int(255 * (1 - tk))))

    # --- efektler ---
    if "koruyucu" in efektler:
        sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); sd = ImageDraw.Draw(sh)
        sd.polygon([(_p(sx0), _p(sy0 + 140)), (_p(sx0 + 140), _p(sy0)), (_p(sx0 + 210), _p(sy0)), (_p(sx0), _p(sy0 + 210))], fill=(255, 255, 255, 70))
        sd.polygon([(_p(sx0), _p(sy0 + 260)), (_p(sx0 + 260), _p(sy0)), (_p(sx0 + 290), _p(sy0)), (_p(sx0), _p(sy0 + 290))], fill=(255, 255, 255, 50))
        mm = Image.new("L", im.size, 0); ImageDraw.Draw(mm).rounded_rectangle((_p(sx0), _p(sy0), _p(sx1), _p(sy1)), _p(66), fill=255)
        sh.putalpha(Image.fromarray(np.minimum(np.array(sh.getchannel("A")), np.array(mm)))); im.alpha_composite(sh); d = ImageDraw.Draw(im)
    if "catlak" in efektler:
        rng = np.random.default_rng(seed); ccx, ccy = sx0 + (sx1 - sx0) * 0.7, sy0 + 90
        cl = Image.new("RGBA", im.size, (0, 0, 0, 0)); cd = ImageDraw.Draw(cl)
        for k in range(11):
            a = rng.uniform(0, 2 * math.pi); x, y = ccx, ccy
            for _ in range(int(rng.integers(3, 6))):
                a += rng.uniform(-0.5, 0.5); ln = rng.uniform(40, 120)
                nx, ny = x + math.cos(a) * ln, y + math.sin(a) * ln
                cd.line((_p(x), _p(y), _p(nx), _p(ny)), fill=(235, 242, 255, 230), width=_p(rng.uniform(2.5, 5))); x, y = nx, ny
        mm = Image.new("L", im.size, 0); ImageDraw.Draw(mm).rounded_rectangle((_p(sx0), _p(sy0), _p(sx1), _p(sy1)), _p(66), fill=255)
        cl.putalpha(Image.fromarray(np.minimum(np.array(cl.getchannel("A")), np.array(mm)))); im.alpha_composite(cl); d = ImageDraw.Draw(im)
    if "yara_bandi" in efektler:
        bd = Image.new("RGBA", (_p(200), _p(64)), (0, 0, 0, 0)); bdd = ImageDraw.Draw(bd)
        bdd.rounded_rectangle((0, 0, _p(200) - 1, _p(64) - 1), _p(30), fill=(244, 206, 160), outline=OUT, width=_p(5))
        bdd.rectangle((_p(70), _p(8), _p(130), _p(56)), fill=(230, 186, 140))
        for k in range(3):
            for j in range(2): bdd.ellipse((_p(80 + k * 18), _p(20 + j * 18), _p(86 + k * 18), _p(26 + j * 18)), fill=(200, 160, 120))
        for ang in (35, -35):
            r_ = bd.rotate(ang, expand=True, resample=Image.BICUBIC)
            im.alpha_composite(r_, (_p(bx + bw - 120) - r_.width // 2 + _p(40), _p(by + 40) - r_.height // 2))
        d = ImageDraw.Draw(im)
    if "ter" in efektler:
        tx, ty = bx + bw + 30, by + 60 + (t * 60) % 40
        d.ellipse((_p(tx - 20), _p(ty - 10), _p(tx + 20), _p(ty + 34)), fill=(130, 210, 255), outline=OUT, width=_p(4))
        d.polygon([(_p(tx - 17), _p(ty + 4)), (_p(tx + 17), _p(ty + 4)), (_p(tx), _p(ty - 34))], fill=(130, 210, 255))
    top_y = by - 120
    if "pil_dusuk" in efektler or "pil_dolu" in efektler:
        lv = 0.08 if "pil_dusuk" in efektler else 1.0
        col_ = (240, 60, 80) if lv < 0.2 else (40, 210, 120)
        if "pil_dusuk" in efektler and int(t * 3) % 2: col_ = (120, 30, 40)
        px0 = W / 2 - 80
        d.rounded_rectangle((_p(px0), _p(top_y), _p(px0 + 150), _p(top_y + 70)), _p(16), fill=(255, 255, 255), outline=OUT, width=_p(6))
        d.rounded_rectangle((_p(px0 + 150), _p(top_y + 22), _p(px0 + 166), _p(top_y + 48)), _p(5), fill=OUT)
        d.rounded_rectangle((_p(px0 + 12), _p(top_y + 12), _p(px0 + 12 + 126 * lv), _p(top_y + 58)), _p(9), fill=col_)
    if "sinyal" in efektler:
        n = 1 + int(t * 4) % 4
        for k in range(4):
            hx = W / 2 - 75 + k * 42; hh = 22 + k * 22
            d.rounded_rectangle((_p(hx), _p(top_y + 80 - hh), _p(hx + 30), _p(top_y + 80)), _p(6),
                                fill=(40, 210, 120) if k < n else (255, 255, 255, 90), outline=OUT, width=_p(4))
    if "yildiz" in efektler:
        for k, (ox, oy, rr) in enumerate([(-230, 120, 30), (240, 60, 24), (-200, 520, 22), (250, 470, 30), (0, -60, 20)]):
            tw = 0.6 + 0.4 * math.sin(t * 6 + k * 1.7)
            _star(d, W / 2 + ox, by + oy, rr * tw, (255, 214, 60))
    if "kalp" in efektler:
        for k in range(3):
            ph = (t * 0.7 + k / 3) % 1
            _heart(d, W / 2 + (k - 1) * 160 + math.sin(ph * 6) * 20, by - 20 - ph * 160, 26 * (1 - ph * 0.4), (255, 80, 130, int(255 * (1 - ph))))

    if "kutu" in efektler:
        ky = by + bh - 120
        L0, R0 = W / 2 - 250, W / 2 + 250
        d.polygon([(_p(L0), _p(ky)), (_p(R0), _p(ky)), (_p(R0 - 20), _p(H - 6)), (_p(L0 + 20), _p(H - 6))], fill=OUT)
        d.polygon([(_p(L0 + 10), _p(ky + 8)), (_p(R0 - 10), _p(ky + 8)), (_p(R0 - 28), _p(H - 14)), (_p(L0 + 28), _p(H - 14))], fill=(196, 150, 96))
        d.polygon([(_p(L0), _p(ky)), (_p(L0 - 60), _p(ky - 70)), (_p(L0 - 40), _p(ky - 80)), (_p(L0 + 110), _p(ky))], fill=(176, 130, 80), outline=OUT)
        d.polygon([(_p(R0), _p(ky)), (_p(R0 + 60), _p(ky - 70)), (_p(R0 + 40), _p(ky - 80)), (_p(R0 - 110), _p(ky))], fill=(176, 130, 80), outline=OUT)
        lg = R.text_sprite("MEYDAN GSM", R.F(R.BLACK, _p(44)), (90, 60, 30), pad=0)
        im.alpha_composite(lg, ((im.width - lg.width) // 2, _p(ky + 90)))

    return im.resize((W, H), Image.LANCZOS)


def balon(txt, w=820):
    """Konusma balonu (kuyrugu asagida ortada)."""
    t = R.para_sprite(txt, R.F(R.BLACK, 60), R.INK, w - 100, gap=8, align="c")
    bw, bh = t.width + 100, t.height + 70
    im = Image.new("RGBA", (bw + 20, bh + 70), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((10, 10, 10 + bw, 10 + bh), 48, fill=OUT)
    d.polygon([(10 + bw // 2 - 40, 10 + bh - 4), (10 + bw // 2 + 30, 10 + bh - 4), (10 + bw // 2 - 10, 10 + bh + 56)], fill=OUT)
    d.rounded_rectangle((16, 16, 4 + bw, 4 + bh), 44, fill=(255, 255, 255))
    d.polygon([(10 + bw // 2 - 30, 10 + bh - 10), (10 + bw // 2 + 20, 10 + bh - 10), (10 + bw // 2 - 8, 10 + bh + 44)], fill=(255, 255, 255))
    im.alpha_composite(t, (10 + (bw - t.width) // 2, 10 + (bh - t.height) // 2))
    return im


# ---------------- video sahnesi ----------------
KOL = {"dur": (112, 68), "el_salla": (112, -30), "zipla": (210, -30), "titre": (95, 85), "sevin": (215, -35),
       "dusun": (112, 215), "goster": (112, 0), "gir": (112, 68)}


def _poz(hareket, lt, t):
    """(dx, dy, kol_sol, kol_sag) dondurur; lt = sahne ici zaman, t = slayt zamani."""
    a, b = KOL.get(hareket, KOL["dur"]); dx = dy = 0
    if hareket in ("dur", "gir", "dusun", "goster"):
        dy = math.sin(t * 3.2) * 10; a += math.sin(t * 2.5) * 5; b -= math.sin(t * 2.5) * 5
        if hareket == "gir": dx = -(1 - R.eout(R.prog(lt, 0, 0.7))) * 900
    elif hareket == "el_salla":
        dy = math.sin(t * 3.2) * 8; b = -30 + 28 * math.sin(lt * 11)
    elif hareket == "zipla":
        dy = -abs(math.sin(lt * math.pi / 0.75)) * 130
    elif hareket == "titre":
        dx = math.sin(lt * 55) * 14 * (1 - R.prog(lt, 0.6, 0.6))
    elif hareket == "sevin":
        dy = -abs(math.sin(lt * math.pi / 0.6)) * 70
        a = 215 + 18 * math.sin(lt * 12); b = -35 - 18 * math.sin(lt * 12)
    return dx, dy, a, b


def slide(im, t, dur, d, shop, C):
    """d = {sahneler: [{sure, ifade, hareket, balon?, ust?, efektler?, gri?}]}; sahne sureleri toplami = slayt suresi."""
    sc = d["sahneler"]; acc = 0; i = 0
    for k, s in enumerate(sc):
        if t < acc + s["sure"] or k == len(sc) - 1: i = k; break
        acc += s["sure"]
    s = sc[i]; lt = t - acc
    e = R.env(t, dur)
    R.put(im, C.get_or("brand", lambda: R.brand_small(shop)), 80, 170, e, anchor="lm")
    if s.get("ust"):
        u = C.get_or(("mu", s["ust"]), lambda: R.para_sprite(s["ust"], R.F(R.XB, 64), R.WHITE, 960, gap=6, align="c"))
        pu = R.eout(R.prog(lt, 0, 0.35)) if (i == 0 or sc[i - 1].get("ust") != s.get("ust")) else 1
        R.put(im, u, 540, 330 + (1 - pu) * 30, e * pu)
    dx, dy, a, b = _poz(s.get("hareket", "dur"), lt, t)
    blink = 1.0 if (t % 2.8) < 0.12 else 0.0
    if lt < 0.1: blink = 1.0  # sahne gecisinde goz kirpar
    look = (0.0, -0.4) if s.get("balon") else (0.0, 0.0)
    sp = ciz(s.get("ifade", "mutlu"), t=t, kol_sol=a, kol_sag=b, goz_kapali=blink, bak=look,
             efektler=tuple(s.get("efektler", ())), gri=s.get("gri", False), seed=3)
    pop = 0.94 + 0.06 * R.eback(R.prog(lt, 0, 0.25)) if i > 0 else 1.0
    pin = R.eout(R.prog(t, 0, 0.5))
    sc_ = 1.28 * pop
    R.put(im, sp, 540 + dx, 1850 + dy + (1 - pin) * 900, e, scale=sc_, anchor="mb")
    if s.get("balon"):
        bl = C.get_or(("mb", s["balon"]), lambda: balon(s["balon"]))
        p = R.prog(lt, 0.15, 0.4)
        R.put(im, bl, 540, 690, e * R.clamp(p * 2), scale=0.5 + 0.5 * R.eback(p) if p < 1 else 1, anchor="mb")


def post_sprite(ifade, efektler=(), kol=(112, 68), gri=False):
    return ciz(ifade, t=0.4, kol_sol=kol[0], kol_sag=kol[1], efektler=tuple(efektler), gri=gri, seed=3)
