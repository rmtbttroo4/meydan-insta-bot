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



# ---------------- OZEL GUNLER ----------------
# Bu gunlerde ogle paylasimi yerine sade bir kutlama/anma gorseli paylasilir (satis icermez).
# Anma gunlerinde aksam Reels'i de sade "gece" temasiyla uretilir.
OZEL_GUNLER = {
    "01-01": {"baslik": "Mutlu Yıllar!", "alt": "Yeni yılın sağlık, mutluluk ve huzur getirmesini dileriz.",
              "caption": "Yeni yılınız kutlu olsun! Sağlık, mutluluk ve huzur dolu bir yıl dileriz. 🎉"},
    "02-14": {"baslik": "Sevgililer Günü kutlu olsun", "alt": "Sevdiklerinizle nice güzel günlere.",
              "caption": "Sevgililer Gününüz kutlu olsun! ❤️ Sevdiklerinizle nice güzel günlere."},
    "03-08": {"baslik": "8 Mart Dünya Kadınlar Günü kutlu olsun", "alt": "Emeği, gücü ve varlığıyla hayatımızı güzelleştiren tüm kadınlara.",
              "caption": "8 Mart Dünya Kadınlar Günü kutlu olsun! 💐"},
    "03-18": {"ust": "18 Mart 1915", "baslik": "Çanakkale Zaferi'nin yıl dönümünde", "alt": "Şehitlerimizi rahmet, minnet ve saygıyla anıyoruz.", "anma": True,
              "caption": "18 Mart Çanakkale Zaferi'nin yıl dönümünde tüm şehitlerimizi rahmet, minnet ve saygıyla anıyoruz. 🇹🇷"},
    "04-23": {"ust": "23 Nisan", "baslik": "Ulusal Egemenlik ve Çocuk Bayramı kutlu olsun", "alt": "Tüm çocuklarımızın bayramı kutlu olsun!",
              "caption": "23 Nisan Ulusal Egemenlik ve Çocuk Bayramı kutlu olsun! 🇹🇷🎈"},
    "05-19": {"ust": "19 Mayıs", "baslik": "Atatürk'ü Anma, Gençlik ve Spor Bayramı kutlu olsun", "alt": "",
              "caption": "19 Mayıs Atatürk'ü Anma, Gençlik ve Spor Bayramı kutlu olsun! 🇹🇷"},
    "08-30": {"ust": "30 Ağustos", "baslik": "Zafer Bayramı kutlu olsun", "alt": "",
              "caption": "30 Ağustos Zafer Bayramı kutlu olsun! 🇹🇷"},
    "10-29": {"ust": "29 Ekim", "baslik": "Cumhuriyet Bayramı kutlu olsun", "alt": "Cumhuriyetimizin yeni yaşı kutlu olsun!",
              "caption": "29 Ekim Cumhuriyet Bayramı kutlu olsun! 🇹🇷"},
    "11-10": {"ust": "10 Kasım 1938", "baslik": "Gazi Mustafa Kemal Atatürk'ü", "alt": "vefatının yıl dönümünde saygı, özlem ve minnetle anıyoruz.", "anma": True,
              "caption": "Cumhuriyetimizin kurucusu Gazi Mustafa Kemal Atatürk'ü vefatının yıl dönümünde saygı, özlem ve minnetle anıyoruz. 🇹🇷"},
    "11-24": {"ust": "24 Kasım", "baslik": "Öğretmenler Günü kutlu olsun", "alt": "Emeği geçen tüm öğretmenlerimize teşekkürler.",
              "caption": "24 Kasım Öğretmenler Günü kutlu olsun! 🍎 Emeği geçen tüm öğretmenlerimize teşekkürler."},
}


def ozel_gun(bugun):
    """Sabit tarihli gunler + Anneler Gunu (Mayis'in 2. pazari) ve Babalar Gunu (Haziran'in 3. pazari)."""
    k = bugun.strftime("%m-%d")
    if k in OZEL_GUNLER: return OZEL_GUNLER[k]
    if bugun.weekday() == 6 and bugun.month == 5 and 8 <= bugun.day <= 14:
        return {"baslik": "Anneler Günü kutlu olsun", "alt": "Başta tüm annelerimiz olmak üzere, sevginin en güzel hâline.",
                "caption": "Anneler Gününüz kutlu olsun! 💐"}
    if bugun.weekday() == 6 and bugun.month == 6 and 15 <= bugun.day <= 21:
        return {"baslik": "Babalar Günü kutlu olsun", "alt": "Tüm babalarımızın günü kutlu olsun.",
                "caption": "Babalar Gününüz kutlu olsun! 👔"}
    return None


# Yeni video turleriyle ek senaryolar
EK_SENARYOLAR = {
    "servis": {"reel": [
        {"slides": [{"tip": "bildirim", "sure": 4.4, "veri": {"ust": "En sevdiğimiz bildirim", "saat": "18:45", "gun": "Bugün", "baslik": "Telefonun hazır!", "metin": "Onarım tamamlandı, mağazamızdan teslim alabilirsin."}},
                    {"tip": "kinetik", "sure": 2.6, "veri": {"kelimeler": ["Getir", "Bırak", "Teslim al!"], "vurgu": [2]}}],
         "caption": "Bu bildirimi almak güzel değil mi? 📲 Telefonun bozulduysa getir, onarım bitince haber verelim. Teknik servis için MEYDAN GSM."},
    ]},
    "tanitim": {"reel": [
        {"slides": [{"tip": "bant", "sure": 4.2, "veri": {"kelimeler": ["SIFIR TELEFON", "İKİNCİ EL", "TAKAS", "TEKNİK SERVİS", "HAT İŞLEMLERİ", "AKSESUAR"], "orta": "Hepsi Meydan'da!"}},
                    {"tip": "intro", "sure": 2.6}],
         "caption": "Sıfır telefon, ikinci el, takas, teknik servis, hat işlemleri, aksesuar… Altınoluk'ta telefonla ilgili her şey MEYDAN GSM'de!"},
    ]},
    "aksesuar": {"reel": [
        {"slides": [{"tip": "secim", "sure": 4.6, "veri": {"soru": "Telefonun için hangisi?", "a": "Kılıf", "b": "Ekran koruyucu", "cevap": "İKİSİ DE!", "not": "Biri düşmeye, diğeri çizik ve darbeye karşı"}},
                    {"tip": "kinetik", "sure": 2.4, "veri": {"kelimeler": ["İkisi de", "MEYDAN GSM'de"], "vurgu": [1]}}],
         "caption": "Kılıf mı, ekran koruyucu mu? İkisi de! Telefonunu tam koru 🛡️ Stok için WhatsApp'tan sorabilirsin."},
        {"slides": [{"tip": "batarya", "sure": 4.6, "veri": {"ust": "Bataryanın en iyi dostu", "yuzde": 100, "alt": "Uyumlu ve kaliteli şarj aleti"}},
                    {"tip": "bullets", "sure": 4.6, "veri": {"ust": "Şarj aksesuarları", "baslik": "Doğru şarj, uzun ömür", "maddeler": ["Cihazına uyumlu şarj aleti", "Sağlam kablo", "Araç şarj aleti"]}}],
         "caption": "Bataryanın en iyi dostu uyumlu bir şarj aleti 🔋 Şarj aleti, kablo ve araç şarjı için MEYDAN GSM'e uğra."},
    ]},
    "ikinciel": {"post": [
        {"tip": "soru", "veri": {"ust": "Sana soruyoruz", "baslik": "Telefonunu ne sıklıkla değiştirirsin?", "secenekler": ["Her 1-2 yılda", "3-4 yılda bir", "Bozulana kadar kullanırım"], "cagri": "Cevabını yorumlara yaz!"},
         "caption": "Merak ediyoruz: telefonunu ne sıklıkla değiştiriyorsun? 👇 Yorumlara yaz! Değiştirme zamanı geldiyse takas için MEYDAN GSM'deyiz."},
    ]},
    "sifir": {"reel": [
        {"slides": [{"tip": "secim", "sure": 4.6, "veri": {"soru": "Yeni telefonda en önemli ne?", "a": "Kamera", "b": "Batarya", "cevap": "SEN SEÇ!", "not": "Sana uygun modeli birlikte bulalım"}},
                    {"tip": "sohbet", "sure": 4.4, "veri": {"ust": "Kararsız mısın?", "mesajlar": [M("musteri", "Kamerası iyi bir telefon arıyorum"), M("biz", "Bütçenizi yazın, uygun modelleri hemen iletelim")]}}],
         "caption": "Kamera mı, batarya mı? Sana uygun telefonu birlikte bulalım 📱 Bütçeni yaz, seçenekleri iletelim."},
    ]},
    "ipucu": {"post": [
        {"tip": "soru", "veri": {"ust": "Sana soruyoruz", "baslik": "Telefonunu gece şarjda bırakır mısın?", "secenekler": ["Evet, her gece", "Bazen", "Hayır, gündüz şarj ederim"], "cagri": "Cevabını yorumlara yaz!"},
         "caption": "Sen hangisisin? 👇 Yorumlara yaz! Şarj alışkanlıkları hakkında merak ettiklerini mağazamızda sorabilirsin."},
    ]},
    "hat": {"reel": [
        {"slides": [{"tip": "bildirim", "sure": 4.4, "veri": {"ust": "Numaran aynı, operatörün yeni", "saat": "10:30", "gun": "Bugün", "baslik": "Hattın aktif!", "metin": "Numara taşıma işlemin tamamlandı. Türk Telekom'a hoş geldin!"}},
                    {"tip": "sayilar", "sure": 5.0, "veri": {"baslik": "Numara taşıma 3 adımda", "maddeler": ["Kimliğinle mağazaya gel", "Sana uygun tarifeyi seçelim", "İşlemleri birlikte tamamlayalım"]}}],
         "caption": "Numaranı değiştirmeden Türk Telekom'a geç! 📶 Kimliğinle gel, numara taşıma işlemini birlikte yapalım."},
    ]},
}
for _k, _v in EK_SENARYOLAR.items():
    for _f in ("reel", "post"):
        SENARYOLAR.setdefault(_k, {}).setdefault(_f, []).extend(_v.get(_f, []))


# ---------------- MASKOT: MEYDI ----------------
# MEYDAN GSM'in maskotu: yuzu ekraninda olan sevimli telefon "Meydi". Aksam Reels'lerinin yarisi Meydi hikayesidir.
MASKOT = "Meydi"


def S(sure, ifade, hareket="dur", balon=None, ust=None, efektler=(), gri=False):
    return {"sure": sure, "ifade": ifade, "hareket": hareket, "balon": balon, "ust": ust, "efektler": list(efektler), "gri": gri}


def MK(*sahneler):
    return {"tip": "maskot", "sure": round(sum(x["sure"] for x in sahneler), 2), "veri": {"sahneler": list(sahneler)}}


MASKOT_SENARYO = {
    "servis": [
        {"slides": [MK(S(2.6, "agla", "titre", "Ekranım kırıldııı!", f"{MASKOT}'nin kötü günü…", ["catlak"]),
                       S(2.6, "dusunceli", "dusun", "Nereye gitsem acaba?", f"{MASKOT}'nin kötü günü…", ["catlak"]),
                       S(3.4, "gulen", "sevin", "Yeni gibi oldum!", "MEYDAN GSM'e uğradı", ["yara_bandi", "yildiz"]))],
         "caption": f"{MASKOT}'nin ekranı kırıldı ama moralini bozmadı 😄 Telefonunun başına bir şey geldiyse getir, birlikte bakalım. Teknik servis için MEYDAN GSM 🔧"},
        {"slides": [MK(S(2.8, "uykulu", "dur", "Şarjım hiç tutmuyor…", f"{MASKOT}'nin derdi", ["pil_dusuk"]),
                       S(2.4, "saskin", "titre", "Yine mi %1?!", f"{MASKOT}'nin derdi", ["pil_dusuk", "ter"]),
                       S(3.4, "heyecan", "zipla", "Meydan'da çözüldü!", "Teknik servis MEYDAN GSM'de", ["pil_dolu", "yildiz"]))],
         "caption": f"Şarjı tutmayan telefon {MASKOT}'yi bile yordu 🔋 Şarj sorunlarında arızayı birlikte tespit edelim. Teknik servis için MEYDAN GSM'e uğra."},
    ],
    "ikinciel": [
        {"slides": [MK(S(2.8, "uykulu", "dur", "Ben artık yaşlandım…", "Eski telefonun da böyle mi?", gri=True),
                       S(2.4, "dusunceli", "dusun", "Takas mı yapsak?", "Eski telefonun da böyle mi?", gri=True),
                       S(3.4, "heyecan", "zipla", "Takasla yenilendim!", "İkinci el ve takas MEYDAN GSM'de", ["yildiz"]))],
         "caption": f"Eski telefonun {MASKOT} gibi yorulduysa takas zamanı! 🔄 Eskisini getir, değerini birlikte belirleyelim, yenisiyle çık."},
    ],
    "sifir": [
        {"slides": [MK(S(3.0, "heyecan", "zipla", "Merhaba! Kutudan yeni çıktım!", "Yeni telefon heyecanı", ["kutu", "yildiz"]),
                       S(3.0, "goz_kirp", "el_salla", "Seni de bekliyorum!", "Sıfır telefonlar MEYDAN GSM'de", ["yildiz"]))],
         "caption": f"Kutudan yeni çıkmış gibi heyecan! 📦 Sıfır telefon seçenekleri için MEYDAN GSM'e uğra ya da stok ve fiyat için WhatsApp'tan yaz."},
    ],
    "aksesuar": [
        {"slides": [MK(S(2.8, "saskin", "titre", "Kılıfsız dışarı mı çıkayım?!", f"{MASKOT} korkuyor", ["ter"]),
                       S(3.4, "mutlu", "goster", "Kılıf + ekran koruyucu = rahat ben", "Aksesuarlar MEYDAN GSM'de", ["kilif", "koruyucu", "yildiz"]))],
         "caption": f"{MASKOT} kılıfsız dışarı çıkmıyor, sen de çıkma! 🛡️ Kılıf ve ekran koruyucu için MEYDAN GSM'e uğra."},
        {"slides": [MK(S(2.8, "uykulu", "dur", "%1… çok yorgunum…", f"{MASKOT} bitik", ["pil_dusuk"]),
                       S(3.2, "gulen", "sevin", "Uyumlu şarj aleti, yeni hayat!", "Şarj aksesuarları MEYDAN GSM'de", ["pil_dolu", "yildiz"]))],
         "caption": f"Doğru şarj aleti {MASKOT}'ye yeniden hayat verdi 🔋 Şarj aleti, kablo ve araç şarjı için mağazamıza bekleriz."},
    ],
    "hat": [
        {"slides": [MK(S(2.8, "dusunceli", "dusun", "Numaram değişmeden geçebilir miyim?", f"{MASKOT}'nin sorusu"),
                       S(3.4, "heyecan", "zipla", "Evet! Numaram aynı, hattım Türk Telekom!", "Numara taşıma MEYDAN GSM'de", ["sinyal", "yildiz"]))],
         "caption": f"{MASKOT} numarasını değiştirmeden Türk Telekom'a geçti 📶 Kimliğinle gel, numara taşıma işlemini birlikte yapalım."},
    ],
    "tanitim": [
        {"slides": [MK(S(2.6, "mutlu", "gir", f"Merhaba! Ben {MASKOT}", "Tanışalım!"),
                       S(2.6, "goz_kirp", "el_salla", "MEYDAN GSM'in maskotuyum", "Tanışalım!", ["yildiz"]),
                       S(3.0, "gulen", "sevin", "Altınoluk'ta seni bekliyoruz!", "Telefonla ilgili her şey", ["kalp"]))],
         "caption": f"Tanışalım! Ben {MASKOT}, MEYDAN GSM'in maskotu 👋 Sıfır ve ikinci el telefon, takas, teknik servis, hat işlemleri ve aksesuar için Altınoluk'ta seni bekliyoruz!"},
    ],
    "ipucu": [
        {"slides": [MK(S(2.8, "saskin", "titre", "Beni sıcakta bırakma!", f"{MASKOT}'den ipucu", ["ter"]),
                       S(3.2, "mutlu", "goster", "Serin yer = uzun ömürlü batarya", f"{MASKOT}'den ipucu", ["pil_dolu"]))],
         "caption": f"{MASKOT}'den ipucu: telefonunu güneşte, sıcak arabada bırakma, batarya ömrü uzasın ☀️🔋"},
    ],
}

MASKOT_POST = {
    "servis": [{"tip": "maskot", "veri": {"ust": "Teknik servis", "baslik": "Kırık ekran dert değil", "balon": "Yeni gibi oldum!", "ifade": "gulen", "efektler": ["yara_bandi", "yildiz"], "kol": [215, -35]},
                "caption": f"{MASKOT} tamir oldu, mutlu! 😄 Telefonunun başına bir şey geldiyse getir, birlikte bakalım 🔧"}],
    "ikinciel": [{"tip": "maskot", "veri": {"ust": "Takas fırsatı", "baslik": "Eski telefonun yoruldu mu?", "balon": "Takas zamanı!", "ifade": "uykulu", "gri": True},
                  "caption": f"Eski telefonun da {MASKOT} gibi yorulduysa takas zamanı! 🔄 Detaylar için WhatsApp'tan yaz."}],
    "aksesuar": [{"tip": "maskot", "veri": {"ust": "Aksesuar köşemiz", "baslik": "Korunan telefon mutlu telefon", "balon": "Kılıfım var, korkum yok!", "ifade": "mutlu", "efektler": ["kilif", "koruyucu"], "kol": [112, 0]},
                  "caption": f"{MASKOT} kılıfıyla mutlu 🛡️ Kılıf ve ekran koruyucu için MEYDAN GSM'e uğra."}],
    "ipucu": [{"tip": "maskot", "veri": {"ust": f"{MASKOT}'den ipucu", "baslik": "Telefonunu sıcakta bırakma", "balon": "Serin yer, uzun ömür!", "ifade": "saskin", "efektler": ["ter"]},
               "caption": f"{MASKOT}'den ipucu: telefonunu güneşte, sıcak arabada bırakma ☀️ Batarya ömrü uzasın 🔋"}],
    "hat": [{"tip": "maskot", "veri": {"ust": "Numara taşıma", "baslik": "Numaran aynı kalsın", "balon": "Hattım artık Türk Telekom!", "ifade": "heyecan", "efektler": ["sinyal"], "kol": [210, -30]},
             "caption": f"{MASKOT} numarasını değiştirmeden geçti, sen de geç! 📶 Kimliğinle gel, işlemleri birlikte yapalım."}],
}


# ---------------- KAMPANYA YARDIMCILARI ----------------
AYLAR = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]


def _sayi(v):
    try: return int(str(v).replace(".", ""))
    except Exception: return None


def _tl(v):
    n = _sayi(v)
    return f"{n:,}".replace(",", ".") if n is not None else str(v)


def sure_yazisi(k, bugun):
    """Bitis tarihi SADECE 'bitis_teyitli': true ise videoya yazilir (uydurma tarih yok)."""
    if not k.get("bitis_teyitli"): return None
    try: b = dt.date.fromisoformat(k["gecerlilik_bitis"])
    except Exception: return None
    kalan = (b - bugun).days
    if kalan < 0: return None
    if kalan == 0: return "SON GÜN!"
    if kalan <= 7: return f"Son {kalan + 1} gün!"
    return f"{b.day} {AYLAR[b.month - 1]}'a kadar!"


def diger_kampanyalar(kampanyalar, bugun):
    return [k for k in kampanyalar.get("diger", []) if kampanya_gecerli(k, bugun)]


def hatirlatma(kampanyalar, bugun, no):
    """Kampanya disi videolarin sonuna eklenecek kisa kampanya hatirlatmasi (aktif kampanyalar arasinda doner)."""
    adaylar = []
    k = kampanyalar.get("tarife")
    if kampanya_gecerli(k, bugun):
        en = min(k["paketler"], key=lambda p: p["yeni"])
        adaylar.append({"satir": f"Faturalı hat {_tl(en['yeni'])} TL/ay'dan başlayan fiyatlarla", "alt": sure_yazisi(k, bugun) or k.get("alt_baslik"), "not": k.get("not")})
    k = kampanyalar.get("turbobox")
    if kampanya_gecerli(k, bugun):
        en = min(k["paketler"], key=lambda p: _sayi(p["fiyat"]) or 10 ** 9)
        adaylar.append({"satir": f"TurboBox 5G {en['fiyat']} {k['birim']}'den başlayan paketlerle", "alt": sure_yazisi(k, bugun) or "Evde, yazlıkta, iş yerinde", "not": k.get("not")})
    for k in diger_kampanyalar(kampanyalar, bugun):
        satir = k["baslik"] + (f" {_tl(k['fiyat'])} {k.get('birim', 'TL')}" if k.get("fiyat") else "")
        adaylar.append({"satir": satir, "alt": sure_yazisi(k, bugun) or k.get("aciklama"), "not": k.get("not")})
    if not adaylar: return None
    a = dict(adaylar[no % len(adaylar)]); a["etiket"] = "BU AY MEYDAN'DA"
    return {"tip": "kampanya_bandi", "sure": 2.8, "veri": {x: y for x, y in a.items() if y}}


def tarife_fiyat_slaytlari(k, bugun, no):
    paketler = sorted(k["paketler"], key=lambda p: p["yeni"])
    secim = [paketler[0], next((p for p in paketler if p.get("vurgu")), paketler[-1])]
    if no % 2: secim = secim[::-1]
    out = []
    for p in secim:
        av = p["eski"] - p["yeni"] if p.get("eski") else None
        out.append({"tip": "fiyat", "sure": 3.8, "veri": {
            "ust": "Faturalı hatta indirim", "paket": p["ad"], "eski": p.get("eski"), "yeni": p["yeni"], "birim": "TL/ay",
            "rozet": f"Aylık {av} TL avantaj" if av and av > 0 else None,
            "alt": (p.get("ek") or k["dakika_sms"]) + " · " + k["alt_baslik"], "not": k["not"]}})
    return out


def turbobox_fiyat_slaytlari(k, bugun, no):
    paketler = k["paketler"]
    secim = [min(paketler, key=lambda p: _sayi(p["fiyat"]) or 10 ** 9), next((p for p in paketler if p.get("vurgu")), paketler[-1])]
    if no % 2: secim = secim[::-1]
    return [{"tip": "fiyat", "sure": 3.6, "veri": {"ust": "TurboBox 5G ile internet", "paket": p["ad"], "yeni": p["fiyat"], "birim": k["birim"],
             "alt": k["alt_baslik"], "not": k["not"]}} for p in secim]


# ---------------- GEMINI KLIPLERI ----------------
# assets/klipler/ klasorune yazisiz Meydi klipleri eklendikce, kodla cizilen Meydi sahneleri otomatik olarak
# bu gercek 3D kliplerle degisir (yazilar yine bot tarafindan temiz eklenir). Eksik klip varsa cizim kullanilir.
KLIP_ADLARI = ["selam", "kirik", "tamir", "yorgun", "kutu", "gosteriyor", "sasirma", "dusunuyor", "sevinc", "kutlama"]


def sahne_klibi(s):
    ef = set(s.get("efektler", []))
    if "catlak" in ef: return "kirik"
    if "yara_bandi" in ef: return "tamir"
    if "kutu" in ef: return "kutu"
    if "pil_dusuk" in ef or s.get("gri") or s.get("ifade") == "uykulu": return "yorgun"
    if s.get("hareket") in ("el_salla", "gir"): return "selam"
    if s.get("hareket") == "goster": return "gosteriyor"
    if "kalp" in ef: return "kutlama"
    if s.get("ifade") == "saskin": return "sasirma"
    if s.get("ifade") == "dusunceli": return "dusunuyor"
    if s.get("hareket") in ("zipla", "sevin"): return "sevinc"
    return "selam"


def klipe_cevir(slides):
    """Tum sahnelerin klibi varsa maskot slaytini klip slaytlarina cevirir. (yeni_slaytlar, klip_kullanildi_mi)"""
    from .render import klip_yolu
    out, kul = [], False
    for sl in slides:
        if sl.get("tip") == "maskot":
            sc = sl["veri"]["sahneler"]; keys = [sahne_klibi(x) for x in sc]
            if all(klip_yolu(k) for k in keys):
                for x, k in zip(sc, keys):
                    out.append({"tip": "klip", "sure": x["sure"], "veri": {"klip": k, "ust": x.get("ust"), "balon": x.get("balon")}})
                kul = True; continue
        out.append(sl)
    return out, kul


# ---------------- GUNLUK STORY ----------------
# Her gun 10:00'da 1 Story (dikey kisa video, aciklamasiz). Gun gun farkli tur doner.
def story_plan(bugun, shop, kampanyalar, takvim):
    """Gunluk Story: 12 farkli Story formati sirayla doner (12 gunde bir tekrar), her turun metinleri de haftadan haftaya degisir."""
    from . import story_slides  # noqa: F401  (Story slaytlarini kaydeder)
    og = ozel_gun(bugun)
    o = bugun.toordinal(); v = o // 12  # v: ayni format tekrar geldiginde farkli metin
    tema = "gece" if (og and og.get("anma")) else TEMALAR[(o * 3 + 1) % len(TEMALAR)]
    base = {"tarih": bugun.isoformat(), "slot": "story", "format": "story", "post": None, "caption": "", "seed": o * 2 + 7, "tema": tema}
    if og and og.get("anma"):
        return {**base, "atla": "Anma günü: Story paylaşılmadı."}
    pick = lambda xs: xs[v % len(xs)]
    gun = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"][bugun.weekday()]
    cta = lambda: {"tip": "cta", "sure": 3.6, "veri": {**CTA_VARYANT[o % len(CTA_VARYANT)], "maskot": True}}
    ikinci = None

    def f_kirik():
        return [{"tip": "kirik_saka", "sure": 5.2, "veri": {"once": pick(["Telefonunu sıkı tut…", "Bir saniye, dur…", "Dikkat et…"]),
                 "sonra": "Korkma, senin ekranın sağlam.", "mesaj": pick(["Kırılırsa adres belli: MEYDAN GSM", "Ekran koruyucun var mı?", "Kırık ekranlar MEYDAN GSM'de yenilenir"])}}, cta()]
    def f_arama():
        return [{"tip": "gelen_arama", "sure": 4.6, "veri": {"alt": "arıyor…", "mesaj": pick(["Ekranın mı kırık? Hemen getir!", "Eski telefonunu takasla!", "Yazlığa internet mi? TurboBox 5G!", "Numaranı taşı, Türk Telekom'a geç!"])}}, cta()]
    def f_pil():
        return [{"tip": "pil_uyari", "sure": 4.4, "veri": {"baslik": "Pil Zayıf", "metin": "%1 pil kaldı. Şarj aletini bağlayın.",
                 "mesaj": pick(["Pilin gün bitmeden bitiyorsa teknik servis MEYDAN GSM'de", "Doğru şarj aleti bataryanı korur. Aksesuarlar MEYDAN GSM'de"])}}, cta()]
    def f_yagmur():
        setler = [
            ([["Ekran kırıldı mı?", "Tamir için getir"], ["Şarj mı tutmuyor?", "Birlikte bakalım"], ["İnternet yavaş mı?", "TurboBox 5G var"], ["Eski telefon çekmecede mi?", "Takas yapıyoruz"]], "Hepsine tek adres: MEYDAN GSM"),
            ([["Kılıfın eskidi mi?", "Yenileri geldi"], ["Kablon mu koptu?", "Şarj aksesuarları burada"], ["Numaranı taşımak mı istiyorsun?", "Kimliğinle gel"], ["Yeni telefon mu bakıyorsun?", "Stok için yaz"]], "Telefonla ilgili her şey MEYDAN GSM'de"),
        ]
        bl, cv = pick(setler)
        return [{"tip": "bildirim_yagmuru", "sure": 4.6, "veri": {"bildirimler": bl, "cevap": cv}}, cta()]
    def f_durdur():
        ws = pick([["Kılıf", "Ekran koruyucu", "Şarj kablosu", "Kulaklık", "Araç şarjı", "Powerbank", "Şarj aleti", "Telefon tutucu"],
                   ["Takas", "Yeni telefon", "Ekran tamiri", "Hat işlemleri", "TurboBox", "Kılıf", "Pil kontrolü", "İkinci el"]])
        return [{"tip": "durdur", "sure": 4.2, "veri": {"kelimeler": ws}}, cta()]
    def f_quiz():
        nonlocal ikinci
        q = pick([
            {"soru": "Bataryanın en büyük düşmanı hangisi?", "siklar": ["Gece şarj etmek", "Sıcak", "Kılıf"], "dogru": 1, "aciklama": "Telefonu güneşte ve sıcak arabada bırakma!"},
            {"soru": "Ekranı en iyi ne korur?", "siklar": ["Sadece kılıf", "Sadece ekran koruyucu", "İkisi birlikte"], "dogru": 2, "aciklama": "Kılıf düşmeye, ekran koruyucu çizik ve darbeye karşı."},
            {"soru": "Numaranı değiştirmeden operatör değiştirebilir misin?", "siklar": ["Evet", "Hayır", "Sadece yeni hatta"], "dogru": 0, "aciklama": "Numara taşıma ile numaran aynı kalır. Kimliğinle gel!"},
        ])
        ikinci = [{"tip": "quiz", "sure": 4.4, "veri": {**q, "cevap": True}}, cta()]
        return [{"tip": "quiz", "sure": 4.6, "veri": q}]
    def f_saat():
        return [{"tip": "saat", "sure": 4.2, "veri": {"ust": pick(["Her gün", f"Bugün {gun}", "Hafta sonu dahil"]), "mesaj": pick(["Biz buradayız!", "Altınoluk'ta seni bekliyoruz"])}}, cta()]
    def f_pov():
        x = pick([
            {"durum": "Şarjın %1, şarj aleti evde kaldı", "ifade": "saskin", "efektler": ["pil_dusuk", "ter"], "balon": "Neden hep ben?!"},
            {"durum": "Telefon elinden kaydı, ekran yere doğru…", "ifade": "agla", "efektler": ["catlak"], "balon": "Ekran koruyucu takmıştım değil mi?"},
            {"durum": "Yazlıktasın ve internet çekmiyor", "ifade": "uzgun", "efektler": [], "balon": "TurboBox nerede?!"},
            {"durum": "Eski telefonun yıllardır çekmecede", "ifade": "uykulu", "efektler": [], "balon": "Beni takasa ver artık!"},
        ])
        return [{"tip": "pov", "sure": 4.4, "veri": x}, cta()]
    def f_fiyat():
        k = kampanyalar.get("tarife") if v % 2 == 0 else kampanyalar.get("turbobox")
        if kampanya_gecerli(k, bugun):
            sl = tarife_fiyat_slaytlari(k, bugun, o) if "dakika_sms" in k else turbobox_fiyat_slaytlari(k, bugun, o)
            return sl[:1] + [cta()]
        return f_kirik()
    def f_efsane():
        return [{"tip": "efsane", "sure": 5.4, "veri": pick([
            {"ust": "Doğru bilinen yanlış", "efsane": "Telefonu her seferinde %0'a kadar bitirip şarj etmek gerekir.", "gercek": "Lityum bataryalarda tam boşaltmaya gerek yok. Ara ara şarj etmek sorun değil."},
            {"ust": "Doğru bilinen yanlış", "efsane": "Yeni telefonu ilk şarjda saatlerce şarjda bırakmak gerekir.", "gercek": "Günümüz bataryalarında buna gerek yok. Normal şekilde kullanabilirsin."}])}, cta()]
    def f_gunaydin():
        return [MK(S(3.2, "goz_kirp", "el_salla", "Günaydın! Bugün 22:30'a kadar açığız", f"İyi {gun}lar!" if gun not in ("Salı", "Cuma") else f"Mutlu {gun}lar!")), cta()]
    def f_bant():
        return [{"tip": "bant", "sure": 4.2, "veri": {"kelimeler": ["SIFIR TELEFON", "İKİNCİ EL", "TAKAS", "TEKNİK SERVİS", "HAT İŞLEMLERİ", "AKSESUAR"], "orta": "Hepsi Meydan'da!"}}, cta()]

    formatlar = [("kirik", f_kirik), ("quiz", f_quiz), ("arama", f_arama), ("fiyat", f_fiyat), ("pov", f_pov), ("yagmur", f_yagmur),
                 ("pil", f_pil), ("durdur", f_durdur), ("efsane", f_efsane), ("saat", f_saat), ("gunaydin", f_gunaydin), ("bant", f_bant)]
    ad, fn = formatlar[(o + 1) % len(formatlar)]
    slides = fn()
    slides, _ = klipe_cevir(slides)
    plan = {**base, "konu": f"story-{ad}", "slides": slides}
    if ikinci:
        plan["ikinci"] = ikinci
    return plan

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

    og = None if zorla_konu else ozel_gun(bugun)
    if og and og.get("anma"):
        tema = "gece"
        if slot == "aksam":  # anma gunu aksam satis paylasimi yapilmaz
            return {"tarih": bugun.isoformat(), "slot": slot, "atla": "Anma günü: akşam paylaşımı yapılmadı."}
    if og and fmt == "post" and slot == "ogle":
        caption = f"{og['caption']}\n\n{shop['name_main']} {shop['name_accent']} · {shop['district']}"
        return {"tarih": bugun.isoformat(), "slot": slot, "konu": "ozelgun", "format": "post", "slides": None,
                "post": {"tip": "ozel_gun", "veri": og}, "caption": caption, "seed": sira, "tema": tema}

    tek = takvim.get("tek_seferlik", {}).get(f"{bugun.isoformat()}_{slot}") if not zorla_konu else None
    if tek and fmt == "reel" and tek.get("hazir"):
        caption = f"{tek['caption']}\n\n{iletisim(shop)}\n\n" + hashtags(shop, tek.get("etiketler", []))
        return {"tarih": bugun.isoformat(), "slot": slot, "konu": tek.get("konu", "hazir"), "format": "reel", "slides": None, "post": None,
                "caption": caption, "seed": sira, "tema": tema, "hazir": tek["hazir"]}
    if tek and fmt == "reel" and tek.get("maskot_konu") in MASKOT_SENARYO:
        s_ = MASKOT_SENARYO[tek["maskot_konu"]][tek.get("sira", 0)]
        slides = [dict(x) for x in s_["slides"]] + [{"tip": "cta", "sure": 4.5, "veri": {**CTA_VARYANT[0], "maskot": True}}]
        caption = f"{s_['caption']}\n\n{iletisim(shop)}\n\n" + hashtags(shop, _etiket(tek["maskot_konu"]))
        return {"tarih": bugun.isoformat(), "slot": slot, "konu": tek["maskot_konu"], "format": fmt, "slides": slides, "post": None,
                "caption": caption, "seed": sira, "tema": tema}

    if konu in ("tarife", "turbobox") and not kampanya_gecerli(kampanyalar.get(konu), bugun):
        konu = takvim.get("yedekler", {}).get(konu, "tanitim")
    if konu == "kampanya" and not diger_kampanyalar(kampanyalar, bugun):
        konu = takvim.get("yedekler", {}).get("kampanya", "sifir")
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
            [MK(S(2.4, "saskin", "titre", "Faturam ne kadar gelmiş?!", f"{MASKOT}'nin faturası", ["ter"]),
                S(2.4, "heyecan", "zipla", "İndirimli tarifeler varmış!", f"{MASKOT}'nin faturası", ["yildiz"]))],
        ][no % 4]
        sy = sure_yazisi(k, bugun)
        if sy: acilis = acilis + [{"tip": "kampanya_bandi", "sure": 2.4, "veri": {"etiket": "KAMPANYA", "satir": "Faturalı hatta indirim", "alt": sy}}]
        govde = tarife_fiyat_slaytlari(k, bugun, no) if no % 2 == 0 else [{"tip": "tariffs", "sure": 7.5, "veri": k}] + tarife_fiyat_slaytlari(k, bugun, no)[:1]
        slides = acilis + govde + [{"tip": "cta", "sure": 4.5, "veri": {"ust": "Hattını Meydan'da aç", "buton": cta["buton"], "maskot": True}}]
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
            [MK(S(2.4, "uzgun", "dur", "Yazlıkta internet yok…", f"{MASKOT} tatilde"),
                S(2.4, "heyecan", "sevin", "TurboBox ile çözüldü!", f"{MASKOT} tatilde", ["sinyal", "yildiz"]))],
        ][no % 4]
        sy = sure_yazisi(k, bugun)
        if sy: acilis = acilis + [{"tip": "kampanya_bandi", "sure": 2.4, "veri": {"etiket": "KAMPANYA", "satir": "TurboBox 5G", "alt": sy}}]
        govde = turbobox_fiyat_slaytlari(k, bugun, no) if no % 2 == 0 else [{"tip": "plans", "sure": 6.5, "veri": pv}] + turbobox_fiyat_slaytlari(k, bugun, no)[:1]
        slides = acilis + govde + [{"tip": "cta", "sure": 4.5, "veri": {"ust": "İnternetin Meydan'da", "buton": cta["buton"], "maskot": True}}]
        post = {"tip": "plans", "veri": pv}
        if fmt == "post":
            caption = caption.replace("🏠 Evde, yazlıkta, iş yerinde internet:", "📡 Kablo derdi olmadan internet:", 1)
    elif konu == "kampanya":
        ks = diger_kampanyalar(kampanyalar, bugun); k = ks[no % len(ks)]
        sy = sure_yazisi(k, bugun)
        veri = {"ust": k.get("ust", "Kampanya"), "paket": k.get("urun", k["baslik"]), "yeni": k.get("fiyat") or "", "eski": k.get("eski_fiyat"),
                "birim": k.get("birim", "TL"), "rozet": sy or k.get("rozet"), "alt": k.get("aciklama"), "not": k.get("not")}
        if not k.get("fiyat"):
            slides = [{"tip": "kampanya_bandi", "sure": 3.4, "veri": {"etiket": "KAMPANYA", "satir": k["baslik"], "alt": sy or k.get("aciklama"), "not": k.get("not")}}]
        else:
            slides = [{"tip": "hook", "sure": 2.4, "veri": {"ust": k.get("ust", "Bu ay"), "vurgu": "KAMPANYA", "alt": "MEYDAN GSM'de"}},
                      {"tip": "fiyat", "sure": 4.2, "veri": veri}]
        slides += [{"tip": "cta", "sure": 4.5, "veri": {**cta, "maskot": True}}]
        post = {"tip": "kampanya", "veri": {**veri, "baslik": k["baslik"]}}
        caption = (f"🔥 {k['baslik']}" + (f": {_tl(k['fiyat'])} {k.get('birim', 'TL')}" if k.get("fiyat") else "") + "\n"
                   + (f"{k['aciklama']}\n" if k.get("aciklama") else "") + (f"⏰ {sy}\n" if sy else "")
                   + (f"*{k['not']}\n" if k.get("not") else "") + f"\n{iletisim(shop)}\n\n" + hashtags(shop, ["#kampanya", "#fırsat"]))
    else:
        eski = KONULAR.get(konu, [])
        sen = SENARYOLAR.get(konu, {})
        if fmt == "reel":
            havuz = list(sen.get("reel", [])) or [
                {"slides": [{"tip": "intro", "sure": 2.6}, {"tip": "bullets", "sure": 5.6, "veri": {k2: v[k2] for k2 in ("ust", "baslik", "maddeler")}}],
                 "caption": v["caption"]} for v in eski]
            mk = MASKOT_SENARYO.get(konu, [])
            if mk and no % 2 == 0: s_ = mk[(no // 2) % len(mk)]
            else: s_ = havuz[(no // 2 if mk else no) % len(havuz)]
            hb = hatirlatma(kampanyalar, bugun, no)
            slides = [dict(x) for x in s_["slides"]] + ([hb] if hb else []) + [{"tip": "cta", "sure": 4.5, "veri": {**cta, "maskot": True}}]
            post = None; ana = s_["caption"]
            if hb: ana += f"\n\n🔥 Bu ay MEYDAN'da: {hb['veri']['satir']}" + (f" ({hb['veri']['alt']})" if hb['veri'].get('alt') else "")
        else:
            havuz = list(sen.get("post", [])) + [
                {"tip": "tanitim" if konu == "tanitim" else "bullets", "veri": {k2: v[k2] for k2 in ("ust", "baslik", "maddeler")}, "caption": v["caption"]}
                for v in eski]
            mp = MASKOT_POST.get(konu, [])
            if mp and no % 3 == 0: p_ = mp[(no // 3) % len(mp)]
            else: p_ = havuz[no % len(havuz)]
            post = {"tip": p_["tip"], "veri": p_["veri"]}; slides = None; ana = p_["caption"]
        caption = f"{ana}\n\n{iletisim(shop)}\n\n" + hashtags(shop, _etiket(konu))

    if fmt == "reel" and slides:
        slides, kul = klipe_cevir(slides)
        if kul:
            for sl in slides:
                if sl["tip"] == "cta": sl["veri"] = {**sl["veri"], "maskot": False}
    return {"tarih": bugun.isoformat(), "slot": slot, "konu": konu, "format": fmt, "slides": slides, "post": post, "caption": caption,
            "seed": sira, "tema": tema}
