"""Instagram API (Unified login, sistem kullanicisi token'i - suresi dolmaz) ile paylasim."""
import os, time
import requests


def _env(name, default=None):
    """Gizli kayitlarin basinda/sonunda kalan bosluk ve satir sonlarini temizler."""
    v = os.environ.get(name)
    if v is None:
        if default is None: raise KeyError(f"Eksik ayar: {name}")
        return default
    v = v.strip()
    return v if v or default is None else default


FB = "https://graph.facebook.com/v23.0"
IG = "https://graph.instagram.com/v23.0"
_resolved = {}


def _tok(): return _env("IG_ACCESS_TOKEN")


import re as _re


def _clean(text):
    """Hata mesajlarinda token (veya token'a benzeyen uzun dizeler) asla loga yazilmasin."""
    t = str(text)
    for v in (_env("IG_ACCESS_TOKEN", ""), _env("IG_USER_ID", "")):
        if v and len(v) > 20: t = t.replace(v, "***")
    return _re.sub(r"(EAA|IGAA|IGQ)[A-Za-z0-9_\-]{10,}", "***", t)


def _get(base, path, **params):
    params["access_token"] = _tok()
    try:
        r = requests.get(f"{base}/{path}", params=params, timeout=30)
        if r.status_code >= 400:
            try: j = r.json()
            except Exception: j = {"raw": r.text[:200]}
            if isinstance(j.get("error"), dict): j["error"]["message"] = _clean(j["error"].get("message", ""))
            return r.status_code, j
        return r.status_code, (r.json() if r.headers.get("content-type", "").startswith(("application/json", "text/javascript")) else {"raw": r.text[:200]})
    except Exception as e:
        return 0, {"error": str(e)}


def _resolve():
    """Token turune gore dogru API adresini ve Instagram hesap kimligini bulur (bir kez)."""
    if _resolved: return _resolved["api"], _resolved["uid"]
    forced = _env("IG_API_BASE", "")
    uid = _env("IG_USER_ID", "")
    if uid and not uid.isdigit():
        raise RuntimeError("IG_USER_ID hatali: sadece rakamlardan olusmali (ornegin 17841469736600725). "
                           "Bu kayda yanlislikla token ya da baska bir deger girilmis; GitHub Secrets'tan duzelt.")
    tried = []
    candidates = [forced] if forced else [FB, IG]
    for base in candidates:
        # 1) Verilen kimlikle hesap okunabiliyor mu?
        if uid:
            code, j = _get(base, uid, fields="id,username")
            tried.append(f"{base.split('//')[1].split('/')[0]} /{{IG_USER_ID}} -> {code} {j.get('username') or (j.get('error') or {}).get('message', '')[:90]}")
            if code == 200 and j.get("id"):
                _resolved.update(api=base, uid=j["id"]); break
        # 2) Token'in kendi hesabi (Instagram token'i ise user_id doner)
        code, j = _get(base, "me", fields="user_id,username" if base == IG else "id,name")
        tried.append(f"{base.split('//')[1].split('/')[0]} /me -> {code} {j.get('username') or j.get('name') or (j.get('error') or {}).get('message', '')[:90]}")
        if code == 200 and base == IG and (j.get("user_id") or j.get("id")):
            _resolved.update(api=base, uid=str(j.get("user_id") or j["id"])); break
        if code == 200 and base == FB:
            # 3) Sistem kullanicisi / sayfa uzerinden bagli Instagram hesabi
            c2, j2 = _get(base, "me/accounts", fields="instagram_business_account{id,username}")
            for pg in (j2.get("data") or []):
                ig = pg.get("instagram_business_account")
                if ig:
                    tried.append(f"graph.facebook.com /me/accounts -> IG {ig.get('username')}")
                    _resolved.update(api=base, uid=ig["id"]); break
            if _resolved: break
    print("[instagram kontrol]\n  " + "\n  ".join(tried))
    if not _resolved:
        raise RuntimeError("Instagram hesabina erisilemedi. Denenenler:\n  " + "\n  ".join(tried))
    print(f"[instagram kontrol] kullanilan: {_resolved['api']} hesap={_resolved['uid'][-4:]}")
    return _resolved["api"], _resolved["uid"]


def _check(r):
    if r.status_code >= 400:
        raise RuntimeError(f"Instagram API hatasi {r.status_code}: {_clean(r.text[:500])}")
    return r.json()


def _wait(container_id, timeout=600):
    t0 = time.time()
    while time.time() - t0 < timeout:
        api, _ = _resolve()
        j = _check(requests.get(f"{api}/{container_id}", params={"fields": "status_code,status", "access_token": _tok()}, timeout=30))
        st = j.get("status_code")
        if st == "FINISHED": return
        if st in ("ERROR", "EXPIRED"): raise RuntimeError(f"Medya islenemedi: {j}")
        time.sleep(10)
    raise RuntimeError("Medya isleme zaman asimi")


def publish(media_url, caption, kind, test=False):
    """kind: 'reel' (mp4) veya 'post' (jpeg). Yayinlanan medya id'sini dondurur.
    test=True: Instagram medyayi indirip isler ama YAYINLAMAZ (konteyner 24 saatte kendiliginden silinir)."""
    params = {"caption": caption, "access_token": _tok()}
    if kind == "reel":
        params.update({"media_type": "REELS", "video_url": media_url, "share_to_feed": "true"})
    elif kind == "story":
        params = {"media_type": "STORIES", "access_token": _tok()}
        params["video_url" if media_url.endswith(".mp4") else "image_url"] = media_url
    else:
        params.update({"image_url": media_url})
    api, uid = _resolve()
    c = _check(requests.post(f"{api}/{uid}/media", data=params, timeout=60))["id"]
    _wait(c)
    if test:
        return None
    j = _check(requests.post(f"{api}/{uid}/media_publish", data={"creation_id": c, "access_token": _tok()}, timeout=60))
    return j["id"]


def already_posted(caption, hours=20):
    """Ayni aciklamanin ilk satiriyla son X saatte paylasilmis bir gonderi var mi? (cift paylasimi onler)"""
    import datetime as _dt
    api, uid = _resolve()
    code, j = _get(api, f"{uid}/media", fields="caption,timestamp,permalink", limit=10)
    if code != 200:
        print("[cift kontrol] son gonderiler okunamadi, kontrol atlandi:", (j.get("error") or {}).get("message", "")[:120])
        return None
    first = caption.strip().split("\n")[0].strip()
    now = _dt.datetime.now(_dt.timezone.utc)
    for m in j.get("data") or []:
        try:
            ts = _dt.datetime.strptime(m.get("timestamp", ""), "%Y-%m-%dT%H:%M:%S%z")
        except Exception:
            continue
        if (now - ts).total_seconds() < hours * 3600 and (m.get("caption") or "").strip().split("\n")[0].strip() == first:
            return m.get("permalink") or m.get("id")
    return None


def story_var_mi(saat=3):
    """Son X saatte paylasilmis Story var mi? (yedek saatlerde cift Story'yi onler)"""
    import datetime as _dt
    api, uid = _resolve()
    code, j = _get(api, f"{uid}/stories", fields="timestamp")
    if code != 200:
        print("[story kontrol] okunamadi, kontrol atlandi"); return False
    now = _dt.datetime.now(_dt.timezone.utc)
    for m in j.get("data") or []:
        try:
            ts = _dt.datetime.strptime(m.get("timestamp", ""), "%Y-%m-%dT%H:%M:%S%z")
            if (now - ts).total_seconds() < saat * 3600: return True
        except Exception:
            continue
    return False


def permalink(media_id):
    try:
        api, _ = _resolve()
        return _check(requests.get(f"{api}/{media_id}", params={"fields": "permalink", "access_token": _tok()}, timeout=30)).get("permalink")
    except Exception:
        return None

