"""Gunun konusunu secer, slaytlari ve aciklamayi (caption) hazirlar."""
import datetime as dt

GUNLER = ["pazartesi", "sali", "carsamba", "persembe", "cuma", "cumartesi", "pazar"]

# Kampanya disi konular. Her konunun birkac varyanti var; hafta numarasina gore donusumlu secilir.
KONULAR = {
    "hat": [
        {"ust": "Türk Telekom Yetkili Bayi", "baslik": "Hat işlemlerin tek adreste",
         "maddeler": ["Yeni hat başvurusu", "Numara taşıma", "Sana uygun tarifeyi birlikte seçelim"],
         "caption": "Yeni hat mı açacaksın, numaranı mı taşıyacaksın? Türk Telekom hat işlemlerin için MEYDAN GSM'e uğra, sana uygun tarifeyi birlikte seçelim."},
        {"ust": "Numaranı değiştirmeden", "baslik": "Türk Telekom'a geçiş kolay",
         "maddeler": ["Numaran aynı kalır", "İşlemler mağazada yapılır", "Tarife seçiminde birebir destek"],
         "caption": "Numaranı değiştirmeden Türk Telekom'a geçebilirsin. Numara taşıma işlemleri için mağazamıza bekleriz."},
    ],
    "servis": [
        {"ust": "Telefonun mu bozuldu?", "baslik": "Tamir ve teknik servis",
         "maddeler": ["Arıza tespiti", "Tamir ve onarım", "Durum hakkında net bilgi"],
         "caption": "Telefonunda sorun mu var? Getir, birlikte bakalım. Tamir ve teknik servis için MEYDAN GSM'deyiz."},
        {"ust": "Teknik servis", "baslik": "Telefonun bizde emin ellerde",
         "maddeler": ["Arızayı birlikte tespit edelim", "Onarım öncesi bilgilendirme", "Altınoluk'ta, yakınında"],
         "caption": "Telefonun çalışmıyor ya da sorun çıkarıyorsa uzağa gitme. Tamir ve teknik servis için Altınoluk'ta MEYDAN GSM'e uğra."},
    ],
    "ikinciel": [
        {"ust": "Eski telefonun değerlensin", "baslik": "İkinci el alım-satım ve takas",
         "maddeler": ["Eski telefonunu getir", "Takasla yenisine geç", "İkinci el telefonlar mağazada"],
         "caption": "Eski telefonun çekmecede durmasın. İkinci el alım-satım ve takas için MEYDAN GSM'e getir, birlikte değerlendirelim."},
        {"ust": "Takas fırsatı", "baslik": "Telefonunu yenilemenin kolay yolu",
         "maddeler": ["Eski cihazını takasa ver", "Farkı öde, yenisini al", "Detaylar için WhatsApp'tan yaz"],
         "caption": "Telefonunu yenilemek mi istiyorsun? Eskisini takasa ver, yenisine geç. Detaylar için WhatsApp'tan yazabilirsin."},
    ],
    "sifir": [
        {"ust": "Yeni telefon zamanı", "baslik": "Sıfır telefon MEYDAN GSM'de",
         "maddeler": ["Sıfır telefon seçenekleri", "Takasla yenile", "Stok ve fiyat için WhatsApp'tan yaz"],
         "caption": "Yeni bir telefon mu bakıyorsun? Sıfır telefon seçenekleri için mağazamıza uğra ya da stok ve fiyat için WhatsApp'tan yaz."},
    ],
    "aksesuar": [
        {"ust": "Telefonunu koru", "baslik": "Aksesuar köşemiz",
         "maddeler": ["Kılıf ve ekran koruyucu", "Şarj aleti ve kablo", "Kulaklık"],
         "caption": "Kılıftan şarj aletine telefonunun ihtiyacı olan aksesuarlar için MEYDAN GSM'e uğra. Stok için WhatsApp'tan sorabilirsin."},
        {"ust": "Küçük ama önemli", "baslik": "Doğru aksesuar, uzun ömürlü telefon",
         "maddeler": ["Ekran koruyucu darbelere karşı", "Kılıf düşmelere karşı", "Uyumlu şarj aleti bataryaya dost"],
         "caption": "Telefonun uzun ömürlü olsun. Ekran koruyucu, kılıf ve şarj aleti için mağazamıza bekleriz."},
    ],
    "ipucu": [
        {"ust": "Günün ipucu", "baslik": "Bataryanı korumanın 3 yolu",
         "maddeler": ["Telefonu sıcakta bırakma", "Uyumlu şarj aleti kullan", "Gereksiz arka plan uygulamalarını kapat"],
         "caption": "Bataryanın ömrünü uzatmak için küçük alışkanlıklar büyük fark yaratır. Kaydet, sonra bakarsın 👇"},
        {"ust": "Günün ipucu", "baslik": "Fotoğrafların kaybolmasın",
         "maddeler": ["Bulut yedeklemeyi aç", "Önemli dosyaları ayrıca sakla", "Telefon değiştirmeden önce yedek al"],
         "caption": "Telefon bozulunca en çok fotoğraflar üzer. Yedeklemeni bugün aç! Telefon değiştirirken veri aktarımı için de mağazamıza danışabilirsin."},
        {"ust": "Günün ipucu", "baslik": "Telefonun yavaşladı mı?",
         "maddeler": ["Yazılım güncellemelerini yap", "Kullanmadığın uygulamaları sil", "Depolama alanında yer aç"],
         "caption": "Telefonun yavaşladıysa önce bu üç adımı dene. Hâlâ sorun varsa teknik servis için MEYDAN GSM'e uğra."},
        {"ust": "Günün ipucu", "baslik": "Ekranını korumanın yolu",
         "maddeler": ["Ekran koruyucu kullan", "Kılıfın kenarları ekranı aşsın", "Telefonu cebinde anahtarla taşıma"],
         "caption": "Ekran tamiri can sıkar, önlem almak kolay. Ekran koruyucu ve kılıf için mağazamıza bekleriz."},
    ],
    "tanitim": [
        {"ust": "Altınoluk'un teknoloji noktası", "baslik": "Neler yapıyoruz?",
         "maddeler": ["Sıfır telefon", "İkinci el alım-satım ve takas", "Tamir ve teknik servis", "Türk Telekom hat işlemleri", "Aksesuar"],
         "caption": "Telefonla ilgili her şey tek adreste: sıfır ve ikinci el telefon, takas, teknik servis, Türk Telekom hat işlemleri ve aksesuar. MEYDAN GSM, teknoloji Meydan'da!"},
    ],
}


def gun_adi(d): return GUNLER[d.weekday()]


def kampanya_gecerli(k, bugun):
    if not k or not k.get("aktif"): return False
    try:
        return bugun <= dt.date.fromisoformat(k["gecerlilik_bitis"])
    except Exception:
        return False


def iletisim(shop):
    return (f"📍 {shop['address_line1']}, {shop['address_line2']}\n"
            f"📞 {shop['phone']} (WhatsApp)\n🕘 {shop['hours']}")


def hashtags(shop, extra):
    return " ".join(shop["base_hashtags"] + extra)


def plan_for(bugun, shop, kampanyalar, takvim, zorla_konu=None, zorla_format=None):
    """Bugun icin {konu, format, slides | post, caption} dondurur."""
    g = takvim["gunler"][gun_adi(bugun)]
    konu, fmt = zorla_konu or g["konu"], zorla_format or g["format"]
    hafta = bugun.isocalendar()[1]

    if konu in ("tarife", "turbobox") and not kampanya_gecerli(kampanyalar.get(konu), bugun):
        konu = g.get("yedek", "tanitim")

    if konu == "tarife":
        k = kampanyalar["tarife"]
        satirlar = "\n".join(f"▫️ {p['ad']}: {p['yeni']} {k['birim']}" + (f" ({p['ek']})" if p.get("ek") else "") for p in k["paketler"])
        caption = (f"📶 Faturalı hatta indirim zamanı! {k['alt_baslik']}.\n\n{k['dakika_sms']}\n{satirlar}\n\n"
                   f"*{k['not']}\n\n{iletisim(shop)}\n\n" + hashtags(shop, ["#türktelekom", "#faturalıhat", "#numarataşıma"]))
        slides = [{"tip": "intro", "sure": 3.0},
                  {"tip": "hook", "sure": 2.8, "veri": {"ust": "Faturalı hatta", "vurgu": "İNDİRİM", "alt": "zamanı!", "rozet": k.get("rozet")}},
                  {"tip": "tariffs", "sure": 7.5, "veri": k},
                  {"tip": "cta", "sure": 4.7, "veri": {"ust": "Hattını Meydan'da aç"}}]
        post = {"tip": "tariffs", "veri": k}
    elif konu == "turbobox":
        k = kampanyalar["turbobox"]
        satirlar = "\n".join(f"▫️ {p['ad']}: {p['fiyat']} {k['birim']}" for p in k["paketler"])
        caption = (f"🏠 Evde, yazlıkta, iş yerinde internet: {k['baslik']}! {k['alt_baslik']}.\n\n{satirlar}\n\n"
                   f"*{k['not']}\n\n{iletisim(shop)}\n\n" + hashtags(shop, ["#türktelekom", "#turbobox", "#5g", "#evinterneti"]))
        pv = {"ust": "Evde, yazlıkta, iş yerinde", **k}
        slides = [{"tip": "intro", "sure": 2.8},
                  {"tip": "plans", "sure": 6.5, "veri": pv},
                  {"tip": "cta", "sure": 4.7, "veri": {"ust": "İnternetin Meydan'da"}}]
        post = {"tip": "plans", "veri": pv}
    else:
        varyantlar = KONULAR[konu]
        v = varyantlar[hafta % len(varyantlar)]
        caption = f"{v['caption']}\n\n{iletisim(shop)}\n\n" + hashtags(shop, {
            "hat": ["#türktelekom", "#numarataşıma"], "servis": ["#telefontamiri", "#teknikservis"],
            "ikinciel": ["#ikincieltelefon", "#takas"], "sifir": ["#sıfırtelefon"], "aksesuar": ["#aksesuar", "#telefonkılıfı"],
            "ipucu": ["#telefonipuçları"], "tanitim": ["#teknoloji"]}.get(konu, []))
        veri = {"ust": v["ust"], "baslik": v["baslik"], "maddeler": v["maddeler"]}
        slides = [{"tip": "intro", "sure": 2.8},
                  {"tip": "bullets", "sure": 6.0, "veri": veri},
                  {"tip": "cta", "sure": 4.7, "veri": {}}]
        post = {"tip": "tanitim" if konu == "tanitim" and fmt == "post" else "bullets", "veri": veri}

    return {"tarih": bugun.isoformat(), "konu": konu, "format": fmt, "slides": slides, "post": post, "caption": caption,
            "seed": bugun.toordinal()}
