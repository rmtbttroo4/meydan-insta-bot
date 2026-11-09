"""Gunun konusunu secer, slaytlari ve aciklamayi (caption) hazirlar."""
import datetime as dt

GUNLER = ["pazartesi", "sali", "carsamba", "persembe", "cuma", "cumartesi", "pazar"]

# Kampanya disi konular. Her konunun birkac varyanti var; gun ve saate gore donusumlu secilir.
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


# ---------------- YARATICI SENARYOLAR ----------------
# Her konu icin farkli video kurgulari (reel) ve gorsel gonderi bicimleri (post).
# Secim haftaya gore doner: ayni gun ayni konu gelse bile her hafta farkli kurgu, her gun farkli renk temasi.
TEMALAR = ["mavi", "mor", "turkuaz", "gece", "gunbatimi"]
CTA_VARYANT = [
    {"ust": "Telefonla ilgili her şey", "buton": "Mağazamıza bekleriz!"},
    {"ust": "Sor, fiyat al, gel teslim al", "buton": "WhatsApp'tan yaz!"},
    {"ust": "Altınoluk'ta, yanı başında", "buton": "Hemen uğra!"},
]


def M(kim, metin): return {"kim": kim, "metin": metin}


SENARYOLAR = {
    "servis": {
        "reel": [
            {"slides": [{"tip": "kinetik", "sure": 3.3, "veri": {"kelimeler": ["Ekran mı kırıldı?", "Şarj mı tutmuyor?", "Telefon mu yavaşladı?", "Getir, bakalım!"], "vurgu": [3]}},
                        {"tip": "sohbet", "sure": 5.6, "veri": {"ust": "Bir mesaj kadar yakınız", "mesajlar": [M("musteri", "Merhaba, telefonumun ekranı kırıldı"), M("biz", "Getirin, hemen bakalım. Her gün 22:30'a kadar açığız"), M("musteri", "Akşam uğrarım, teşekkürler!")]}}],
             "caption": "Ekran kırıldı, şarj tutmuyor, telefon yavaşladı… Hangisi olursa olsun getir, birlikte bakalım. Teknik servis için MEYDAN GSM 🔧"},
            {"slides": [{"tip": "once_sonra", "sure": 4.6, "veri": {"ust": "Kırık ekran dert değil", "once": "Kırık ekran", "sonra": "Tamir sonrası"}},
                        {"tip": "bullets", "sure": 5.0, "veri": {"ust": "Teknik servis", "baslik": "Telefonun emin ellerde", "maddeler": ["Arıza tespiti", "Onarım öncesi bilgilendirme", "Altınoluk'ta, yakınında"]}}],
             "caption": "Kırık ekranla uğraşma! Telefonunu getir, arızayı birlikte tespit edelim, onarım öncesi seni bilgilendirelim. 📱"},
            {"slides": [{"tip": "hook", "sure": 2.6, "veri": {"ust": "Telefonun", "vurgu": "SORUNLU MU?", "alt": "uzağa gitme"}},
                        {"tip": "sayilar", "sure": 5.4, "veri": {"baslik": "Servis 3 adımda", "maddeler": ["Telefonunu getir", "Arızayı birlikte tespit edelim", "Onarımdan önce seni bilgilendirelim"]}}],
             "caption": "Teknik servis 3 adımda: getir, arızayı birlikte tespit edelim, onarımdan önce seni bilgilendirelim. Altınoluk'ta MEYDAN GSM."},
        ],
        "post": [
            {"tip": "sohbet", "veri": {"ust": "Teknik servis", "baslik": "Bir mesaj kadar yakınız", "mesajlar": [M("musteri", "Merhaba, telefonum şarj olmuyor"), M("biz", "Getirin, hemen bakalım. Her gün 22:30'a kadar açığız")]},
             "caption": "Telefonunda sorun mu var? Yazman yeterli, birlikte bakalım. Teknik servis için MEYDAN GSM 🔧"},
            {"tip": "sayilar", "veri": {"ust": "Teknik servis", "baslik": "Servis 3 adımda", "maddeler": ["Telefonunu getir", "Arızayı birlikte tespit edelim", "Onarımdan önce bilgilendirelim"]},
             "caption": "Teknik servis 3 adımda. Altınoluk'ta, yanı başında: MEYDAN GSM."},
        ],
    },
    "ikinciel": {
        "reel": [
            {"slides": [{"tip": "sohbet", "sure": 5.6, "veri": {"ust": "Eski telefonun çekmecede durmasın", "mesajlar": [M("musteri", "Eski telefonumu alır mısınız?"), M("biz", "Tabii! Modelini ve durumunu yazın, değerlendirelim"), M("musteri", "Takasla yenisini alabilir miyim?"), M("biz", "Evet, takas da yapıyoruz")]}},
                        {"tip": "kinetik", "sure": 2.8, "veri": {"kelimeler": ["Eskisini getir", "Takasla", "Yenisiyle çık!"], "vurgu": [2]}}],
             "caption": "Eski telefonunu getir, takasla, yenisiyle çık! İkinci el alım-satım ve takas için MEYDAN GSM'e yaz 📲"},
            {"slides": [{"tip": "hook", "sure": 2.6, "veri": {"ust": "Eski telefonun", "vurgu": "DEĞERLENSİN", "alt": "takas Meydan'da"}},
                        {"tip": "sayilar", "sure": 5.4, "veri": {"baslik": "Takas 3 adımda", "maddeler": ["Eski telefonunu getir", "Değerini birlikte belirleyelim", "Farkı öde, yenisiyle çık"]}}],
             "caption": "Takas 3 adımda: eskisini getir, değerini birlikte belirleyelim, farkı öde ve yenisiyle çık. 🔄"},
            {"slides": [{"tip": "kinetik", "sure": 3.0, "veri": {"kelimeler": ["Sat", "Al", "Takasla", "Hepsi Meydan'da"], "vurgu": [3]}},
                        {"tip": "bullets", "sure": 5.0, "veri": {"ust": "İkinci el", "baslik": "Alım, satım ve takas", "maddeler": ["Eski telefonunu getir", "İkinci el telefonlar mağazada", "Detaylar için WhatsApp'tan yaz"]}}],
             "caption": "Sat, al, takasla… İkinci el telefonda aradığın her şey MEYDAN GSM'de."},
        ],
        "post": [
            {"tip": "sohbet", "veri": {"ust": "İkinci el ve takas", "baslik": "Eski telefonun değerlensin", "mesajlar": [M("musteri", "Eski telefonumu alır mısınız?"), M("biz", "Tabii! Modelini ve durumunu yazın, değerlendirelim")]},
             "caption": "Eski telefonun çekmecede durmasın. Modelini ve durumunu yaz, birlikte değerlendirelim 📲"},
            {"tip": "sayilar", "veri": {"ust": "Takas fırsatı", "baslik": "Takas 3 adımda", "maddeler": ["Eski telefonunu getir", "Değerini birlikte belirleyelim", "Farkı öde, yenisiyle çık"]},
             "caption": "Telefonunu yenilemenin en kolay yolu: takas. Detaylar için WhatsApp'tan yaz 🔄"},
        ],
    },
    "sifir": {
        "reel": [
            {"slides": [{"tip": "kinetik", "sure": 3.0, "veri": {"kelimeler": ["Yeni telefon", "Yeni heyecan", "MEYDAN GSM'de"], "vurgu": [2]}},
                        {"tip": "sohbet", "sure": 5.0, "veri": {"ust": "Stok ve fiyat bir mesaj uzağında", "mesajlar": [M("musteri", "Merhaba, sıfır telefon bakıyorum"), M("biz", "Hoş geldiniz! Hangi modeli düşünüyorsunuz? Stok ve fiyatı hemen yazalım")]}}],
             "caption": "Yeni telefon, yeni heyecan! Hangi modeli düşünüyorsan yaz, stok ve fiyatı hemen iletelim 📱"},
            {"slides": [{"tip": "hook", "sure": 2.6, "veri": {"ust": "Telefonunu", "vurgu": "YENİLE", "alt": "eskisini takasla"}},
                        {"tip": "sayilar", "sure": 5.2, "veri": {"baslik": "Yeni telefona geçiş", "maddeler": ["Modelini seç", "Eskisini takasa ver", "Verilerini birlikte aktaralım"]}}],
             "caption": "Yeni telefona geçmek kolay: modelini seç, eskisini takasa ver. Sıfır telefon seçenekleri MEYDAN GSM'de."},
        ],
        "post": [
            {"tip": "sohbet", "veri": {"ust": "Sıfır telefon", "baslik": "Hangi modeli düşünüyorsun?", "mesajlar": [M("musteri", "Merhaba, sıfır telefon bakıyorum"), M("biz", "Hoş geldiniz! Stok ve fiyatı hemen yazalım")]},
             "caption": "Sıfır telefon mu bakıyorsun? Modelini yaz, stok ve fiyatı hemen iletelim 📱"},
        ],
    },
    "aksesuar": {
        "reel": [
            {"slides": [{"tip": "kinetik", "sure": 3.6, "veri": {"kelimeler": ["Kılıf", "Ekran koruyucu", "Şarj aleti", "Kulaklık", "Hepsi burada!"], "vurgu": [4]}},
                        {"tip": "bullets", "sure": 4.6, "veri": {"ust": "Aksesuar köşemiz", "baslik": "Telefonunu koru", "maddeler": ["Kılıf düşmelere karşı", "Ekran koruyucu çizik ve darbeye karşı", "Uyumlu şarj aleti bataryaya dost"]}}],
             "caption": "Kılıf, ekran koruyucu, şarj aleti, kulaklık… Telefonunun ihtiyacı olan her şey MEYDAN GSM'de 🎧"},
            {"slides": [{"tip": "once_sonra", "sure": 4.6, "veri": {"ust": "Ekran koruyucu takmadan önce…", "once": "Korumasız ekran", "sonra": "Koruyucu ile güvende"}},
                        {"tip": "kinetik", "sure": 2.6, "veri": {"kelimeler": ["Önlem al", "Ekranını koru!"], "vurgu": [1]}}],
             "caption": "Ekran tamiri can sıkar, önlem almak kolay. Ekran koruyucu ve kılıf için mağazamıza bekleriz 🛡️"},
        ],
        "post": [
            {"tip": "sayilar", "veri": {"ust": "Aksesuar köşemiz", "baslik": "Telefonunun 3 dostu", "maddeler": ["Kılıf", "Ekran koruyucu", "Uyumlu şarj aleti"]},
             "caption": "Telefonunun 3 dostu: kılıf, ekran koruyucu ve uyumlu şarj aleti. Stok için WhatsApp'tan sorabilirsin."},
        ],
    },
    "hat": {
        "reel": [
            {"slides": [{"tip": "sohbet", "sure": 5.6, "veri": {"ust": "Numaranı değiştirmeden geç", "mesajlar": [M("musteri", "Numaramı değiştirmeden Türk Telekom'a geçebilir miyim?"), M("biz", "Evet! Numara taşıma işlemini mağazada birlikte yapıyoruz"), M("musteri", "Ne getirmem lazım?"), M("biz", "Kimliğinizle gelmeniz yeterli")]}}],
             "caption": "Numaranı değiştirmeden Türk Telekom'a geçebilirsin. Kimliğinle gel, numara taşıma işlemini birlikte yapalım 📶"},
            {"slides": [{"tip": "sayilar", "sure": 5.4, "veri": {"baslik": "Numara taşıma 3 adımda", "maddeler": ["Kimliğinle mağazaya gel", "Sana uygun tarifeyi seçelim", "İşlemleri birlikte tamamlayalım"]}}],
             "caption": "Numara taşıma 3 adımda. Türk Telekom hat işlemlerin için MEYDAN GSM'e uğra."},
        ],
        "post": [
            {"tip": "sohbet", "veri": {"ust": "Türk Telekom Yetkili Bayi", "baslik": "Numaran aynı kalsın", "mesajlar": [M("musteri", "Numaramı değiştirmeden geçebilir miyim?"), M("biz", "Evet! Kimliğinizle gelmeniz yeterli")]},
             "caption": "Numaranı değiştirmeden Türk Telekom'a geç. Kimliğinle gel, işlemleri birlikte yapalım 📶"},
        ],
    },
    "ipucu": {
        "reel": [
            {"slides": [{"tip": "efsane", "sure": 5.4, "veri": {"ust": "Doğru bilinen yanlış", "efsane": "Telefonu her seferinde %0'a kadar bitirip şarj etmek gerekir.", "gercek": "Lityum bataryalarda tam boşaltmaya gerek yok. Ara ara şarj etmek sorun değil."}}],
             "caption": "Bunu sen de duymuşsundur 👀 Lityum bataryalarda telefonu sıfıra kadar bitirmene gerek yok. Kaydet, paylaş!"},
        ],
        "post": [
            {"tip": "efsane", "veri": {"ust": "Doğru bilinen yanlış", "baslik": "Efsane mi, gerçek mi?", "efsane": "Telefonu her seferinde %0'a kadar bitirip şarj etmek gerekir.", "gercek": "Lityum bataryalarda tam boşaltmaya gerek yok. Ara ara şarj etmek sorun değil."},
             "caption": "Bunu sen de duymuşsundur 👀 Lityum bataryalarda telefonu sıfıra kadar bitirmene gerek yok. Kaydet, paylaş!"},
            {"tip": "efsane", "veri": {"ust": "Doğru bilinen yanlış", "baslik": "Efsane mi, gerçek mi?", "efsane": "Yeni telefonu ilk şarjda saatlerce şarjda bırakmak gerekir.", "gercek": "Günümüz bataryalarında buna gerek yok. Normal şekilde kullanabilirsin."},
             "caption": "Yeni telefon aldın, saatlerce şarjda mı bekletmek lazım? Hayır! Günümüz bataryalarında buna gerek yok 🔋"},
            {"tip": "sayilar", "veri": {"ust": "Günün ipucu", "baslik": "Bataryanı korumanın 3 yolu", "maddeler": ["Telefonu sıcakta bırakma", "Uyumlu şarj aleti kullan", "Gereksiz arka plan uygulamalarını kapat"]},
             "caption": "Bataryanın ömrünü uzatmak için küçük alışkanlıklar büyük fark yaratır. Kaydet, sonra bakarsın 👇"},
            {"tip": "sayilar", "veri": {"ust": "Günün ipucu", "baslik": "Telefonun yavaşladı mı?", "maddeler": ["Yazılım güncellemelerini yap", "Kullanmadığın uygulamaları sil", "Depolama alanında yer aç"]},
             "caption": "Telefonun yavaşladıysa önce bu üç adımı dene. Hâlâ sorun varsa teknik servis için MEYDAN GSM'e uğra."},
            {"tip": "sohbet", "veri": {"ust": "Günün ipucu", "baslik": "Fotoğrafların kaybolmasın", "mesajlar": [M("musteri", "Telefonum bozulursa fotoğraflarım gider mi?"), M("biz", "Bulut yedeklemeyi açarsan güvende kalır. Telefon değiştirirken aktarımda da yardımcı oluruz")]},
             "caption": "Telefon bozulunca en çok fotoğraflar üzer. Yedeklemeni bugün aç! 📸"},
        ],
    },
    "tanitim": {
        "reel": [
            {"slides": [{"tip": "hook", "sure": 2.6, "veri": {"ust": "Telefonla ilgili", "vurgu": "HER ŞEY", "alt": "tek adreste!"}},
                        {"tip": "bullets", "sure": 5.4, "veri": {"ust": "Altınoluk'un teknoloji noktası", "baslik": "Neler yapıyoruz?", "maddeler": ["Sıfır telefon", "İkinci el alım-satım ve takas", "Tamir ve teknik servis", "Türk Telekom hat işlemleri", "Aksesuar"]}},
                        {"tip": "intro", "sure": 2.6}],
             "caption": "Telefonla ilgili her şey tek adreste: sıfır ve ikinci el telefon, takas, teknik servis, Türk Telekom hat işlemleri ve aksesuar. MEYDAN GSM, teknoloji Meydan'da!"},
            {"slides": [{"tip": "kinetik", "sure": 4.2, "veri": {"kelimeler": ["Sıfır telefon", "İkinci el", "Teknik servis", "Hat işlemleri", "Aksesuar", "Hepsi Meydan'da!"], "vurgu": [5]}},
                        {"tip": "intro", "sure": 2.6}],
             "caption": "Sıfır telefon, ikinci el, teknik servis, hat işlemleri, aksesuar… Hepsi Altınoluk'ta MEYDAN GSM'de!"},
            {"slides": [{"tip": "sohbet", "sure": 5.6, "veri": {"ust": "Bize her şeyi sorabilirsin", "mesajlar": [M("musteri", "Merhaba, neredesiniz?"), M("biz", "Altınoluk İskele Mah., Büyük Önder Atatürk Cad. 2/B'deyiz"), M("musteri", "Saat kaça kadar açıksınız?"), M("biz", "Her gün 09:00 - 22:30 arası açığız")]}},
                        {"tip": "intro", "sure": 2.4}],
             "caption": "Neredeyiz, kaça kadar açığız? Altınoluk İskele Mah. Büyük Önder Atatürk Cad. 2/B, her gün 09:00–22:30. Bekleriz!"},
        ],
        "post": [],
    },
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


def slot_for_now(now):
    """Turkiye saatine gore: 15:00'ten once ogle, sonra aksam."""
    return "ogle" if now.hour < 15 else "aksam"


def _sira_no(bugun, takvim, konu, slot):
    """Bu konunun bu slotta kacinci kez geldigi: haftada iki kez gelen konu (or. ipucu) her seferinde farkli icerik alir."""
    gunler = [g for g in GUNLER if takvim["gunler"][g][slot] == konu] or [gun_adi(bugun)]
    sira_gun = gunler.index(gun_adi(bugun)) if gun_adi(bugun) in gunler else 0
    return (bugun.toordinal() // 7) * len(gunler) + sira_gun


def _etiket(konu):
    return {"hat": ["#türktelekom", "#numarataşıma"], "servis": ["#telefontamiri", "#teknikservis"],
            "ikinciel": ["#ikincieltelefon", "#takas"], "sifir": ["#sıfırtelefon"], "aksesuar": ["#aksesuar", "#telefonkılıfı"],
            "ipucu": ["#telefonipuçları"], "tanitim": ["#teknoloji"]}.get(konu, [])


def plan_for(bugun, shop, kampanyalar, takvim, slot="aksam", zorla_konu=None, zorla_format=None):
    """Verilen gun ve slot (ogle/aksam) icin {konu, format, slides | post, caption, tema} dondurur."""
    konu = zorla_konu or takvim["gunler"][gun_adi(bugun)][slot]
    fmt = zorla_format or takvim["slotlar"][slot]["format"]
    sira = bugun.toordinal() * 2 + (1 if slot == "aksam" else 0)  # muzik ve arka plan tohumu
    tema = TEMALAR[sira % len(TEMALAR)]
    hafta = bugun.toordinal() // 7

    if konu in ("tarife", "turbobox") and not kampanya_gecerli(kampanyalar.get(konu), bugun):
        konu = takvim.get("yedekler", {}).get(konu, "tanitim")
    no = _sira_no(bugun, takvim, konu, slot)
    cta = dict(CTA_VARYANT[(no + len(konu)) % len(CTA_VARYANT)])

    if konu == "tarife":
        k = kampanyalar["tarife"]
        satirlar = "\n".join(f"▫️ {p['ad']}: {p['yeni']} {k['birim']}" + (f" ({p['ek']})" if p.get("ek") else "") for p in k["paketler"])
        caption = (f"📶 Faturalı hatta indirim zamanı! {k['alt_baslik']}.\n\n{k['dakika_sms']}\n{satirlar}\n\n"
                   f"*{k['not']}\n\n{iletisim(shop)}\n\n" + hashtags(shop, ["#türktelekom", "#faturalıhat", "#numarataşıma"]))
        acilis = [
            [{"tip": "intro", "sure": 2.6}, {"tip": "hook", "sure": 2.8, "veri": {"ust": "Faturalı hatta", "vurgu": "İNDİRİM", "alt": "zamanı!", "rozet": k.get("rozet")}}],
            [{"tip": "kinetik", "sure": 3.0, "veri": {"kelimeler": ["Faturan", "kabarık mı?", "İndirim zamanı!"], "vurgu": [2]}}],
            [{"tip": "sohbet", "sure": 4.4, "veri": {"ust": "En çok sorulan soru", "mesajlar": [M("musteri", "Faturalı hatlarda kampanya var mı?"), M("biz", "Evet! Güncel tarifeler hemen aşağıda")]}}],
        ][no % 3]
        slides = acilis + [{"tip": "tariffs", "sure": 7.5, "veri": k}, {"tip": "cta", "sure": 4.5, "veri": {"ust": "Hattını Meydan'da aç", "buton": cta["buton"]}}]
        post = {"tip": "tariffs", "veri": k}
        if fmt == "post":
            caption = caption.replace("📶 Faturalı hatta indirim zamanı!", "📶 Faturalı tarifelerde güncel fiyatlar burada!", 1)
    elif konu == "turbobox":
        k = kampanyalar["turbobox"]
        satirlar = "\n".join(f"▫️ {p['ad']}: {p['fiyat']} {k['birim']}" for p in k["paketler"])
        caption = (f"🏠 Evde, yazlıkta, iş yerinde internet: {k['baslik']}! {k['alt_baslik']}.\n\n{satirlar}\n\n"
                   f"*{k['not']}\n\n{iletisim(shop)}\n\n" + hashtags(shop, ["#türktelekom", "#turbobox", "#5g", "#evinterneti"]))
        pv = {"ust": "Evde, yazlıkta, iş yerinde", **k}
        acilis = [
            [{"tip": "intro", "sure": 2.6}],
            [{"tip": "kinetik", "sure": 3.0, "veri": {"kelimeler": ["Evde", "Yazlıkta", "İş yerinde", "İnternet!"], "vurgu": [3]}}],
            [{"tip": "sohbet", "sure": 4.4, "veri": {"ust": "Yazlığa internet mi lazım?", "mesajlar": [M("musteri", "Yazlığa internet bağlatmak istiyorum"), M("biz", "TurboBox ile kolay! Paketler hemen aşağıda")]}}],
        ][no % 3]
        slides = acilis + [{"tip": "plans", "sure": 6.5, "veri": pv}, {"tip": "cta", "sure": 4.5, "veri": {"ust": "İnternetin Meydan'da", "buton": cta["buton"]}}]
        post = {"tip": "plans", "veri": pv}
        if fmt == "post":
            caption = caption.replace("🏠 Evde, yazlıkta, iş yerinde internet:", "📡 Kablo derdi olmadan internet:", 1)
    else:
        eski = KONULAR.get(konu, [])
        sen = SENARYOLAR.get(konu, {})
        if fmt == "reel":
            havuz = list(sen.get("reel", [])) or [
                {"slides": [{"tip": "intro", "sure": 2.6}, {"tip": "bullets", "sure": 5.6, "veri": {k2: v[k2] for k2 in ("ust", "baslik", "maddeler")}}],
                 "caption": v["caption"]} for v in eski]
            s_ = havuz[no % len(havuz)]
            slides = [dict(x) for x in s_["slides"]] + [{"tip": "cta", "sure": 4.5, "veri": cta}]
            post = None; ana = s_["caption"]
        else:
            havuz = list(sen.get("post", [])) + [
                {"tip": "tanitim" if konu == "tanitim" else "bullets", "veri": {k2: v[k2] for k2 in ("ust", "baslik", "maddeler")}, "caption": v["caption"]}
                for v in eski]
            p_ = havuz[no % len(havuz)]
            post = {"tip": p_["tip"], "veri": p_["veri"]}; slides = None; ana = p_["caption"]
        caption = f"{ana}\n\n{iletisim(shop)}\n\n" + hashtags(shop, _etiket(konu))

    return {"tarih": bugun.isoformat(), "slot": slot, "konu": konu, "format": fmt, "slides": slides, "post": post, "caption": caption,
            "seed": sira, "tema": tema}
