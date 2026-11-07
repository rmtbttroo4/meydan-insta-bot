"""Gmail ile rapor e-postasi (Gmail uygulama sifresi gerekir)."""
import os, smtplib
from email.message import EmailMessage


def send(subject, body, attachment=None):
    user = os.environ.get("GMAIL_USER"); pw = os.environ.get("GMAIL_APP_PASSWORD")
    to = os.environ.get("REPORT_TO", user)
    if not user or not pw:
        print("[notify] Gmail ayari yok, e-posta atlandi.\n", subject, "\n", body); return
    m = EmailMessage(); m["Subject"] = subject; m["From"] = user; m["To"] = to; m.set_content(body)
    if attachment and os.path.exists(attachment) and os.path.getsize(attachment) < 20 * 1024 * 1024:
        sub = "jpeg" if attachment.endswith(".jpg") else "mp4"
        main = "image" if sub == "jpeg" else "video"
        with open(attachment, "rb") as f:
            m.add_attachment(f.read(), maintype=main, subtype=sub, filename=os.path.basename(attachment))
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
        s.login(user, pw); s.send_message(m)
