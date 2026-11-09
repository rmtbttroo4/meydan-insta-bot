"""Instagram API (Unified login, sistem kullanicisi token'i - suresi dolmaz) ile paylasim."""
import os, time
import requests

# EAA... ile baslayan sistem kullanicisi token'i graph.facebook.com uzerinden calisir.
# IGAA... ile baslayan Instagram token'i kullanilirsa IG_API_BASE=https://graph.instagram.com/v23.0 yap.
API = os.environ.get("IG_API_BASE") or "https://graph.facebook.com/v23.0"


def _tok(): return os.environ["IG_ACCESS_TOKEN"]


def _uid(): return os.environ["IG_USER_ID"]


def _check(r):
    if r.status_code >= 400:
        raise RuntimeError(f"Instagram API hatasi {r.status_code}: {r.text[:500]}")
    return r.json()


def _wait(container_id, timeout=600):
    t0 = time.time()
    while time.time() - t0 < timeout:
        j = _check(requests.get(f"{API}/{container_id}", params={"fields": "status_code,status", "access_token": _tok()}, timeout=30))
        st = j.get("status_code")
        if st == "FINISHED": return
        if st in ("ERROR", "EXPIRED"): raise RuntimeError(f"Medya islenemedi: {j}")
        time.sleep(10)
    raise RuntimeError("Medya isleme zaman asimi")


def publish(media_url, caption, kind):
    """kind: 'reel' (mp4) veya 'post' (jpeg). Yayinlanan medya id'sini dondurur."""
    params = {"caption": caption, "access_token": _tok()}
    if kind == "reel":
        params.update({"media_type": "REELS", "video_url": media_url, "share_to_feed": "true"})
    else:
        params.update({"image_url": media_url})
    c = _check(requests.post(f"{API}/{_uid()}/media", data=params, timeout=60))["id"]
    _wait(c)
    j = _check(requests.post(f"{API}/{_uid()}/media_publish", data={"creation_id": c, "access_token": _tok()}, timeout=60))
    return j["id"]


def permalink(media_id):
    try:
        return _check(requests.get(f"{API}/{media_id}", params={"fields": "permalink", "access_token": _tok()}, timeout=30)).get("permalink")
    except Exception:
        return None

