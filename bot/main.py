"""MEYDAN GSM Instagram botu.

Kullanim:
  python -m bot.main                      # su anki slotun (ogle/aksam) icerigini uret ve paylas
  python -m bot.main --slot ogle          # ogle gonderisini uret ve paylas
  python -m bot.main --dry-run            # sadece uret (out/ klasorune), paylasma
  python -m bot.main --test               # uret + Cloudflare'e yukle + Instagram'da hazirla, YAYINLAMA
  python -m bot.main --dry-run --hafta    # onumuzdeki 7 gunun hepsini uret (onizleme)
  python -m bot.main --konu tarife --format post   # konu/format zorla
"""
import argparse, datetime as dt, json, os, sys, traceback
from zoneinfo import ZoneInfo

from . import content, render, music

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TZ = ZoneInfo("Europe/Istanbul")


def load(name):
    with open(os.path.join(ROOT, "config", name), encoding="utf-8") as f:
        return json.load(f)


def build(plan, shop, outdir):
    os.makedirs(outdir, exist_ok=True)
    base = os.path.join(outdir, f"{plan['tarih']}_{plan['slot']}_{plan['konu']}")
    if plan["format"] == "reel":
        dur = sum(s["sure"] for s in plan["slides"])
        cuts, acc = [], 0
        for s in plan["slides"][:-1]:
            acc += s["sure"]; cuts.append(acc)
        wav = base + ".wav"
        music.make_music(wav, dur, seed=plan["seed"], cuts=cuts)
        path = base + ".mp4"
        render.render_reel(plan["slides"], shop, path, music_path=wav, seed=plan["seed"], workdir=outdir)
        os.remove(wav)
    else:
        path = base + ".jpg"
        render.render_post(plan["post"], shop, path, seed=plan["seed"])
    with open(base + "_caption.txt", "w", encoding="utf-8") as f:
        f.write(plan["caption"])
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--test", action="store_true", help="her seyi dene ama Instagram'da yayinlama")
    ap.add_argument("--hafta", action="store_true")
    ap.add_argument("--tarih")
    ap.add_argument("--slot", choices=["ogle", "aksam"])
    ap.add_argument("--konu"); ap.add_argument("--format", choices=["reel", "post"])
    ap.add_argument("--out", default=os.path.join(ROOT, "out"))
    a = ap.parse_args()

    shop, kamp, takvim = load("shop.json"), load("campaigns.json"), load("schedule.json")
    now = dt.datetime.now(TZ)
    bugun = dt.date.fromisoformat(a.tarih) if a.tarih else now.date()
    gunler = [bugun + dt.timedelta(days=i) for i in range(7)] if a.hafta else [bugun]
    slotlar = ["ogle", "aksam"] if (a.hafta and not a.slot) else [a.slot or content.slot_for_now(now)]

    for g in gunler:
        for slot in slotlar:
            run_one(g, slot, a, shop, kamp, takvim)


def tiktok_caption(caption, extra_tags):
    """Instagram aciklamasini TikTok icin sadeler: Instagram hashtag'lerini atar, TikTok etiketlerini ekler."""
    satirlar = [l for l in caption.strip().split("\n") if not l.strip().startswith("#")]
    metin = "\n".join(satirlar).strip()
    return f"{metin}\n\n{' '.join(extra_tags)}"


def send_tiktok_mail(plan, path, notify):
    try:
        cfg = load("tiktok.json")
    except Exception:
        return
    if not cfg.get("aktif"):
        return
    tur = "Video (Reels)" if path.endswith(".mp4") else "Görsel (fotoğraf gönderisi)"
    adimlar = ("1) Bu maili telefonda aç, ekteki dosyayı indir.\n"
               "2) TikTok → + → Yükle → dosyayı seç.\n"
               + ("3) 'Ses ekle' ile trend bir müzik seç; orijinal sesin seviyesini düşürebilirsin.\n" if path.endswith(".mp4")
                  else "3) Fotoğraf modunda paylaş; istersen bir müzik ekle.\n")
               + "4) Aşağıdaki açıklamayı kopyala-yapıştır → Paylaş.")
    body = (f"{tur} TikTok'a hazır.\n\n{adimlar}\n\n"
            f"────────── KOPYALANACAK AÇIKLAMA ──────────\n\n"
            f"{tiktok_caption(plan['caption'], cfg.get('hashtagler', []))}\n")
    notify.send(f"🎵 TikTok'a hazır: {plan['konu']} ({'video' if path.endswith('.mp4') else 'görsel'}) – {plan['tarih']}",
                body, attachment=path)


def run_one(g, slot, a, shop, kamp, takvim):
    plan = content.plan_for(g, shop, kamp, takvim, slot, a.konu, a.format)
    print(f"[{plan['tarih']} {slot}] konu={plan['konu']} format={plan['format']}")
    path = build(plan, shop, a.out)
    print("  ->", path)
    if a.dry_run:
        return

    from . import storage, instagram, notify
    try:
        if not a.test:
            onceki = instagram.already_posted(plan["caption"])
            if onceki:
                print("  Bu gonderi zaten paylasilmis, atlaniyor:", onceki)
                return
            send_tiktok_mail(plan, path, notify)  # Instagram'dan bagimsiz: once TikTok maili
        ctype = "video/mp4" if path.endswith(".mp4") else "image/jpeg"
        url = storage.upload(path, f"instagram/{os.path.basename(path)}", ctype)
        if a.test:
            instagram.publish(url, plan["caption"], plan["format"], test=True)
            notify.send(f"🧪 MEYDAN GSM Instagram TEST başarılı: {plan['konu']} ({plan['slot']})",
                        f"Üretim, Cloudflare yükleme ve Instagram hazırlık adımları sorunsuz çalıştı. Gönderi YAYINLANMADI.\n\n"
                        f"Tarih: {plan['tarih']} ({plan['slot']})\nKonu: {plan['konu']} ({plan['format']})\nDosya: {url}\n\nAçıklama:\n{plan['caption']}",
                        attachment=path if path.endswith(".jpg") else None)
            print("  TEST basarili (yayinlanmadi):", url)
            return
        media_id = instagram.publish(url, plan["caption"], plan["format"])
        link = instagram.permalink(media_id) or "(link alinamadi)"
        notify.send(f"✅ MEYDAN GSM Instagram: {plan['konu']} paylaşıldı",
                    f"Tarih: {plan['tarih']} ({plan['slot']})\nKonu: {plan['konu']} ({plan['format']})\nLink: {link}\n\nAçıklama:\n{plan['caption']}")
        print("  paylasildi:", link)
    except Exception as e:
        notify.send("❌ MEYDAN GSM Instagram " + ("TESTİ" if a.test else "paylaşımı") + " BAŞARISIZ",
                    f"Tarih: {plan['tarih']} ({plan['slot']})\nKonu: {plan['konu']}\nHata: {e}\n\n{traceback.format_exc()}")
        raise

if __name__ == "__main__":
    sys.exit(main())
