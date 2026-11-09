"""Facebook sayfasina paylasim (sistem kullanicisi token'i ile). Token yoksa sessizce atlanir."""
import os, time
import requests

API = "https://graph.facebook.com/v23.0"


def _env(name):
    return (os.environ.get(name) or "").strip()


def enabled():
    return bool(_env("FB_ACCESS_TOKEN"))


def _check(r):
    if r.status_code >= 400:
        raise RuntimeError(f"Facebook API hatasi {r.status_code}: {r.text[:300].replace(_env('FB_ACCESS_TOKEN') or '§', '***')}")
    return r.json()


def _page():
    """(page_id, page_token): FB_PAGE_ID verilmisse onu, yoksa token'in eristigi ilk sayfayi kullanir."""
    tok = _env("FB_ACCESS_TOKEN")
    want = _env("FB_PAGE_ID")
    data = _check(requests.get(f"{API}/me/accounts", params={"fields": "id,name,access_token", "access_token": tok}, timeout=30)).get("data") or []
    for p in data:
        if not want or p["id"] == want:
            print(f"[facebook] sayfa: {p['name']}")
            return p["id"], p["access_token"]
    raise RuntimeError("Facebook sayfasina erisilemedi: token'a Meydan GSM sayfasi atanmis mi?")


def publish(media_url, caption, kind):
    pid, ptok = _page()
    if kind == "post":
        j = _check(requests.post(f"{API}/{pid}/photos", data={"url": media_url, "message": caption, "published": "true", "access_token": ptok}, timeout=120))
        return f"https://www.facebook.com/{j.get('post_id') or j.get('id')}"
    # Reels: baslat -> URL'den yukle -> yayinla
    j = _check(requests.post(f"{API}/{pid}/video_reels", data={"upload_phase": "start", "access_token": ptok}, timeout=60))
    vid = j["video_id"]
    up = requests.post(f"https://rupload.facebook.com/video-upload/v23.0/{vid}",
                       headers={"Authorization": f"OAuth {ptok}", "file_url": media_url}, timeout=180)
    _check(up)
    _check(requests.post(f"{API}/{pid}/video_reels", data={"upload_phase": "finish", "video_id": vid, "video_state": "PUBLISHED",
                                                           "description": caption, "access_token": ptok}, timeout=60))
    for _ in range(30):  # isleme durumunu bekle (en fazla ~5 dk)
        s = _check(requests.get(f"{API}/{vid}", params={"fields": "status", "access_token": ptok}, timeout=30)).get("status", {})
        if s.get("video_status") in ("ready", "published") or (s.get("publishing_phase") or {}).get("status") == "complete":
            break
        if s.get("video_status") == "error":
            raise RuntimeError(f"Facebook Reels islenemedi: {s}")
        time.sleep(10)
    return f"https://www.facebook.com/reel/{vid}"
