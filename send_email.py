# send_email.py
import os, smtplib, imaplib, zipfile, tempfile, shutil
from email.message import EmailMessage
from email.utils import make_msgid, formatdate
from datetime import datetime
import  time, re
from dotenv import load_dotenv
from Email import compose_email  # réutilisé
from imap_handler import *

from icecream import ic
# ic.disable()

B64_OVERHEAD = float(os.getenv("B64_OVERHEAD", "1.37"))
MAX_MB = float(os.getenv("SMTP_MAX_MB", "19"))  # seuil avant zip
IMAP_COPY_SENT = os.getenv("IMAP_COPY_SENT", "0") == "1"
IMAP_SENT_FOLDER = os.getenv("IMAP_SENT_FOLDER", '"Sent"')

def guess_imap_host(email: str | None) -> str | None:
    if email is None:
        return None
    domain = email.split("@")[-1].lower()
    
    if any(k in domain.split(".")[0] for k in ("outlook","hotmail","live","office365")):
        return "outlook.office365.com"
    if "yahoo" in domain:
        return "imap.mail.yahoo.com"
    
    return f"imap.{domain}"

def bytes_size(paths):
    return sum(os.path.getsize(p) for p in paths if os.path.isfile(p))

def est_smtp_mb(paths):
    return bytes_size(paths) * B64_OVERHEAD / (1024*1024)

def zip_all(label, paths):
    tmpdir = tempfile.mkdtemp(prefix=f"mailzip_{label}_")
    zpath = os.path.join(tmpdir, f"{label}.zip")
    with zipfile.ZipFile(zpath, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for p in paths:
            zf.write(p, arcname=os.path.basename(p))
    return [zpath], tmpdir

def attach_files(msg: EmailMessage, paths):
    for p in paths:
        with open(p, "rb") as f:
            msg.add_attachment(f.read(), maintype="application", subtype="octet-stream",
                               filename=os.path.basename(p))

def smtp_connect():
    load_dotenv(override=True)
    host = os.getenv("SMTP_HOST", "smtp.orange.fr")
    port = int(os.getenv("SMTP_PORT", "465"))
    use_ssl = os.getenv("SMTP_SSL", "1") == "1"
    user = os.getenv("email")
    pwd  = os.getenv("email_pwd")
    if use_ssl:
        s = smtplib.SMTP_SSL(host, port, timeout=60)
        s.ehlo()
    else:
        s = smtplib.SMTP(host, port, timeout=60)
        s.ehlo()
        try: s.starttls(); s.ehlo()
        except smtplib.SMTPException: pass
    s.login(user, pwd) # pyright: ignore[reportArgumentType]
    return s

def smtp_send_verified(msg: EmailMessage):
    want_dsn = os.getenv("SMTP_REQUEST_DSN", "1") == "1"
    res = {"accepted": False, "used_dsn": False, "message_id": msg["Message-ID"], "copied_sent": False}

    s = smtp_connect()
    try:
        try:
            s.ehlo()
        except Exception:
            pass

        if hasattr(s, "starttls") and getattr(s, "_tls_established", False) is False:
            try:
                s.starttls()
                s.ehlo()
            except Exception:
                pass

        feats = getattr(s, "esmtp_features", {}) or {}
        support_dsn = (hasattr(s, "has_extn") and s.has_extn("dsn")) or ("dsn" in feats)

        # >>> FIX : DSN seulement si demandé ET supporté
        if want_dsn and support_dsn:
            rcpt_opts = ["NOTIFY=SUCCESS,FAILURE,DELAY"]
        else:
            rcpt_opts = []
        res["used_dsn"] = bool(rcpt_opts)

        try:
            if rcpt_opts:
                s.send_message(msg, mail_options=[], rcpt_options=rcpt_opts)
            else:
                s.send_message(msg, mail_options=[])

            res["accepted"] = True

        except smtplib.SMTPRecipientsRefused as e:
            # Si DSN a été rejeté, retenter sans DSN
            err = next(iter(e.recipients.values()))
            if b"NOTIFY=" in err[1] or "NOTIFY=" in str(err[1]):
                s.send_message(msg, mail_options=[])
                res["accepted"] = True
                res["used_dsn"] = False
            else:
                raise

    finally:
        try: s.quit()
        except Exception: s.close()
    return res



def send_email(ctx=None, dev=False):
    if ctx is None:
        attachments = [
            "Protégés/TEST test/COS Drelangue.pdf"
        ]
        ctx = {
            "name": "Dupont Jeanne",
            "tri": 3,
            "year": 2025,
            "date": datetime.now().strftime("%d/%m/%Y"),
            "sender_name": os.getenv("NameSender", ""),
            "sender_role": os.getenv("Role", ""),
            "attachments": attachments
        }
    # 2) Compose le message (subject + corps depuis templates/.env)
    msg = compose_email(ctx)  # From/To/Subject/Body déjà posés
    mid = msg["Message-ID"]

    load_dotenv(override=True)
    sender = os.getenv("email", "expediteur@example.com")

    # Demande d'accusé de lecture (MDN)
    msg["Disposition-Notification-To"] = sender
    # Vieille variante encore utilisée par certains clients
    msg["Return-Receipt-To"] = sender

    # 3) Pièces jointes + zip si trop gros
    
    tmpdir = None
    size_mb = est_smtp_mb(ctx["attachments"])
    if size_mb > MAX_MB:
        ctx["attachments"], tmpdir = zip_all(ctx["name"], ctx["attachments"])
    attach_files(msg, ctx["attachments"])

    # 4) Envoi SMTP vérifié
    result = smtp_send_verified(msg)

    # 5) Enregistrement IMAP
    MAIL_PASSWORD = ic(os.getenv('email_pwd'))
    MAIL_USERNAME = ic(os.getenv('email','assistante.drelangue@orange.fr'))
    IMAP_SERVER = guess_imap_host(MAIL_USERNAME) #type:ignore

    box, _ = ic(find_closest_folder(os.getenv('Mailbox_name',"ash"), MAIL_PASSWORD, MAIL_USERNAME, IMAP_SERVER)) #type:ignore
    add_Email2box(msg, box, IMAP_SERVER, MAIL_PASSWORD, MAIL_USERNAME)

    box, _, _= ic(find_sent_folder(MAIL_PASSWORD, MAIL_USERNAME, IMAP_SERVER)) #type:ignore
    add_Email2box(msg, box, IMAP_SERVER, MAIL_PASSWORD, MAIL_USERNAME)

    wait_for_email(box, msg["Subject"], MAIL_PASSWORD, MAIL_USERNAME, IMAP_SERVER)

    # 6) Nettoyage zip si créé
    if tmpdir: shutil.rmtree(tmpdir, ignore_errors=True)

    # 7) Rapport console
    ic("=== ENVOI ===")
    ic(f"Message-ID: {mid}")
    ic(f"SMTP accepté: {result['accepted']}")
    ic(f"DSN utilisé: {result['used_dsn']}")
    ic(f"Copié 'Envoyés' IMAP: {result['copied_sent']}")
    ic(f"Taille estimée SMTP avant envoi: {size_mb:.2f} MB (seuil {MAX_MB} MB)")
    if size_mb > MAX_MB: ic("→ Fichiers zippés avant envoi.")

    return bool(result.get("accepted"))

if __name__ == "__main__":
    ic.enable()
    send_email()
