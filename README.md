# MEYDAN GSM Instagram Botu

Her gün 19:07'de (Türkiye saati) o günün konusuna göre bir **Reels** ya da **gönderi** üretir,
Instagram'da (@meydangsm_) paylaşır ve sonucu Gmail'e rapor eder. Facebook sayfası gerekmez.

## Haftalık takvim (config/schedule.json)

| Gün | Konu | Format |
|---|---|---|
| Pazartesi | Faturalı tarifeler (kampanya bitmişse: hat işlemleri) | Reels |
| Salı | Tamir ve teknik servis | Gönderi |
| Çarşamba | TurboBox 5G (kampanya bitmişse: sıfır telefon) | Reels |
| Perşembe | İkinci el alım-satım ve takas | Gönderi |
| Cuma | Aksesuar | Reels |
| Cumartesi | Günün ipucu | Gönderi |
| Pazar | Dükkân tanıtımı | Reels |

Her konunun birkaç farklı metni var, haftadan haftaya sırayla değişir (`bot/content.py`).

## Fiyat güncelleme (en önemli kısım)

`config/campaigns.json` dosyasını düzenle:
- Fiyatları afişe göre gir.
- **`gecerlilik_bitis`** tarihine kampanyanın gerçek bitiş tarihini yaz (YYYY-AA-GG).
  Tarih geçince bot o kampanyayı **paylaşmaz**, yedek konuya geçer. Eski fiyatla gönderi çıkmaz.
- Kampanyayı tamamen kapatmak için `"aktif": false` yap.

## Kurulum (bir kerelik)

### 1. GitHub
1. `meydan-insta-bot` adında **özel (private)** bir depo aç ve bu klasördeki her şeyi yükle.

### 2. Cloudflare R2 (video/görsel barındırma)
Instagram medyayı herkese açık bir linkten indirir; bunun için R2 kullanılır (düşük hacimde ücretsiz katman yeterli).
1. Cloudflare panelinde **R2 → Create bucket** → ad: `meydan-insta`.
2. Bucket ayarlarında **Public access**'i aç (r2.dev adresi ya da `media.meydangsm.com` gibi bir alt alan adı).
   Bu adres `R2_PUBLIC_BASE_URL` olur.
3. **R2 → Manage API tokens → Create API token** → izin: *Object Read & Write*, sadece bu bucket.
   Çıkan **Access Key ID**, **Secret Access Key** ve hesap kimliğini (**Account ID**) not al.

### 3. Meta (Instagram API) — TAMAMLANDI
Uygulama: **MeydanGSM Paylasim** (işletme portfolyosu: Meydan GSM). Token türü: sistem kullanıcısı (EAA…), **süresi dolmaz**.
Aşağıdaki eski adımlar sadece bilgi içindir.
1. Instagram hesabının **İşletme** hesabı olduğundan emin ol.
2. https://developers.facebook.com → **Uygulama oluştur** → kullanım durumu: **Instagram API ile mesajları ve içerikleri yönet**.
3. **API setup with Instagram login** bölümünde **Add account** ile @meydangsm_ hesabını bağla.
4. Aynı ekrandan **Generate token** → bu uzun ömürlü (60 gün) token `IG_ACCESS_TOKEN` olur.
5. Hesap kimliği için tarayıcıda aç (TOKEN yerine token'ı yaz):
   `https://graph.instagram.com/me?fields=user_id,username&access_token=TOKEN`
   Çıkan `user_id` → `IG_USER_ID`.
> Not: Meta geliştirici kaydı kişisel bir Facebook hesabıyla giriş isteyebilir; Facebook **sayfası** gerekmez.

### 4. Gmail raporu
1. Google hesabında **2 adımlı doğrulama** açık olmalı.
2. https://myaccount.google.com/apppasswords → yeni uygulama şifresi oluştur → `GMAIL_APP_PASSWORD`.

### 6. GitHub Secrets
Depo → Settings → Secrets and variables → Actions → **New repository secret**:

| Ad | Değer |
|---|---|
| `IG_ACCESS_TOKEN` | Meta'dan aldığın token |
| `IG_USER_ID` | Instagram user_id |
| `R2_ACCOUNT_ID` | Cloudflare Account ID |
| `R2_BUCKET` | `meydan-insta` |
| `R2_ACCESS_KEY_ID` | R2 Access Key ID |
| `R2_SECRET_ACCESS_KEY` | R2 Secret Access Key |
| `R2_PUBLIC_BASE_URL` | örn. `https://pub-xxxx.r2.dev` |
| `GMAIL_USER` | Gmail adresin |
| `GMAIL_APP_PASSWORD` | Gmail uygulama şifresi |
| `REPORT_TO` | Raporun gideceği adres (boşsa GMAIL_USER) |

### 7. Test
1. **Actions → Gunluk Instagram paylasimi → Run workflow** → `dry_run: true`.
   Üretilen dosyalar işin sonunda **Artifacts** olarak indirilebilir; paylaşım yapılmaz.
2. Her şey iyiyse bir kez `dry_run: false` ile çalıştır → Instagram'da gönderi çıkar, Gmail'e rapor gelir.
3. Sonrasında bot her gün kendisi çalışır.

## Yerelde deneme
```bash
pip install -r requirements.txt   # ayrıca ffmpeg kurulu olmalı
python -m bot.main --dry-run --hafta          # önümüzdeki 7 günü out/ klasörüne üret
python -m bot.main --dry-run --konu tarife --format post
```

## Notlar
- Müzik kodla üretilir, telifsizdir.
- Yazı tipi: Inter (SIL Open Font License, `bot/fonts/LICENSE-Inter.txt`).
- Paylaşım hata verirse Gmail'e "BAŞARISIZ" e-postası gelir; o gün paylaşım yapılmamıştır.
