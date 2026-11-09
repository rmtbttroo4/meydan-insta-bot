"""Cloudflare R2'ye (S3 uyumlu) dosya yukler ve herkese acik URL dondurur.
Instagram, medyayi herkese acik bir linkten indirerek yayinlar."""
import datetime as dt, hashlib, hmac, os, urllib.parse
import requests


def _env(name, default=None):
    """Gizli kayitlarin basinda/sonunda kalan bosluk ve satir sonlarini temizler."""
    v = os.environ.get(name)
    if v is None:
        if default is None: raise KeyError(f"Eksik ayar: {name}")
        return default
    v = v.strip()
    return v if v or default is None else default



def _sign(key, msg): return hmac.new(key, msg.encode(), hashlib.sha256).digest()


def upload(local_path, key, content_type):
    account = _env("R2_ACCOUNT_ID"); bucket = _env("R2_BUCKET")
    ak = _env("R2_ACCESS_KEY_ID"); sk = _env("R2_SECRET_ACCESS_KEY")
    public_base = _env("R2_PUBLIC_BASE_URL").rstrip("/")
    host = f"{account}.r2.cloudflarestorage.com"
    path = f"/{bucket}/{urllib.parse.quote(key)}"
    data = open(local_path, "rb").read()
    payload_hash = hashlib.sha256(data).hexdigest()
    now = dt.datetime.now(dt.timezone.utc); amz = now.strftime("%Y%m%dT%H%M%SZ"); day = now.strftime("%Y%m%d")
    headers = {"host": host, "x-amz-content-sha256": payload_hash, "x-amz-date": amz, "content-type": content_type}
    signed = ";".join(sorted(headers))
    canon = "\n".join(["PUT", path, "", "".join(f"{k}:{headers[k]}\n" for k in sorted(headers)), signed, payload_hash])
    scope = f"{day}/auto/s3/aws4_request"
    sts = "\n".join(["AWS4-HMAC-SHA256", amz, scope, hashlib.sha256(canon.encode()).hexdigest()])
    k = _sign(_sign(_sign(_sign(("AWS4" + sk).encode(), day), "auto"), "s3"), "aws4_request")
    sig = hmac.new(k, sts.encode(), hashlib.sha256).hexdigest()
    headers["Authorization"] = f"AWS4-HMAC-SHA256 Credential={ak}/{scope}, SignedHeaders={signed}, Signature={sig}"
    r = requests.put(f"https://{host}{path}", data=data, headers=headers, timeout=120)
    r.raise_for_status()
    return f"{public_base}/{urllib.parse.quote(key)}"
