from imap_tools.mailbox import MailBox
import os
import imaplib
from dotenv import load_dotenv
from email.message import EmailMessage
from email.utils import make_msgid, formatdate
import time
from icecream import ic
ic.disable()

def wait_for_email(box, subject_target, MAIL_PASSWORD, MAIL_USERNAME, IMAP_SERVER, timeout=300, interval=5):
    """
    Waits until an email with the given subject appears in the target mailbox.
    Only considers messages marked as \\Recent to detect new arrivals.

    timeout  = max seconds to wait
    interval = seconds between checks
    
    Returns the message object if found, otherwise None.
    """

    deadline = time.time() + timeout

    while time.time() < deadline:
        with MailBox(IMAP_SERVER).login(MAIL_USERNAME, MAIL_PASSWORD, "Inbox") as mb:
            mb.folder.set(box)

            # Only check unread+recent first for speed
            for msg in mb.fetch(reverse=True, mark_seen=False):
                # msg.flags contains '\\Seen','\\Recent','\\Answered'...
                is_recent = "\\Recent" in msg.flags
                if msg.subject == subject_target and is_recent:
                    ic(f"FOUND! {msg.subject} | {msg.date} | UID:{msg.uid}")
                    return msg

        # nothing found → wait and retry
        time.sleep(interval)

    ic("Timeout reached — target email not found.")
    return None


load_dotenv()
MAIL_PASSWORD = os.getenv('email_pwd')
MAIL_USERNAME = os.getenv('email','assistante.drelangue@orange.fr')
IMAP_SERVER = "imap.orange.fr"


def add_Email2box(msg, box, IMAP_SERVER, MAIL_PASSWORD, MAIL_USERNAME):

# Supprimer les en-têtes qui déclenchent l'accusé lecture chez toi
    for h in ["Disposition-Notification-To", "Return-Receipt-To"]:
        if h in msg:
            del msg[h]

    if not MAIL_PASSWORD:
        raise RuntimeError("email_pwd not set in environment")

    with imaplib.IMAP4_SSL(IMAP_SERVER) as imap:
        typ, data = imap.login(MAIL_USERNAME, MAIL_PASSWORD)
        ic("LOGIN:", typ, data)

        # date_time=None → server sets current date/time
        typ, data = imap.append(box, "", None, msg.as_bytes()) #type:ignore
        ic("APPEND:", typ, data)



def read_mailbox(BOX, MAIL_PASSWORD, MAIL_USERNAME, IMAP_SERVER):
    with MailBox(IMAP_SERVER).login(MAIL_USERNAME, MAIL_PASSWORD, "Inbox") as mb: #type:ignore
        mb.folder.set(BOX)

        for msg in mb.fetch(limit=5, reverse=True, mark_seen=False):
            ic(f"{msg.subject} | {msg.date} | {msg.flags} | UID:{msg.uid}")


if __name__=="__main__":
    ic.enable()
    box="INBOX/ASH"
    read_mailbox(box, MAIL_PASSWORD, MAIL_USERNAME, IMAP_SERVER)

    msg = EmailMessage()
    msg["From"] = MAIL_USERNAME
    msg["To"] = MAIL_USERNAME
    msg["Date"] = formatdate(localtime=True)
    msg["Subject"] = "Test insert into ASH"
    msg["Message-ID"] = make_msgid(domain=MAIL_USERNAME.split("@")[-1])
    msg.set_content("This is a test message inserted via IMAP.")

    add_Email2box(msg, box, IMAP_SERVER, MAIL_PASSWORD, MAIL_USERNAME)
    wait_for_email(box, msg["Subject"], MAIL_PASSWORD, MAIL_USERNAME, IMAP_SERVER)
