from imap_tools.mailbox import MailBox
import os
import imaplib
from dotenv import load_dotenv
from email.message import EmailMessage
from email.utils import make_msgid, formatdate
import time
from difflib import SequenceMatcher

from icecream import ic
ic.disable()


def find_closest_folder(target_name: str, MAIL_PASSWORD: str, MAIL_USERNAME: str, IMAP_SERVER: str):
    """
    Return the folder name on the server that is closest to `target_name`
    based on string similarity.
    """
    best_folder = None
    best_score = 0.0
    target = target_name.lower()

    with MailBox(IMAP_SERVER).login(MAIL_USERNAME, MAIL_PASSWORD) as mb:  # no need to specify "Inbox" here
        for folder in mb.folder.list():
            folder_name = folder.name
            score = SequenceMatcher(None, target, folder_name.lower()).ratio()

            if score > best_score:
                best_score = score
                best_folder = folder_name

    return best_folder, best_score

def find_sent_folder(MAIL_PASSWORD: str, MAIL_USERNAME: str, IMAP_SERVER: str):
    """
    Find the most likely 'sent' folder among all mailboxes.
    Recognises English, French and generic naming variants: 
    sent / sent items / outbox / outgoing / envoyés / éléments envoyés...
    """

    # keywords ranked by confidence priority
    sent_aliases = [
        "sent", "sent mail", "sent items",
        "outbox", "out box", "outgoing",
        "envoyé", "envoyés", "envoyee", "envoyer", "éléments envoyés"
    ]

    best_folder = None
    best_score = 0.0
    best_alias = None

    for alias in sent_aliases:
        folder, score = find_closest_folder(alias, MAIL_PASSWORD, MAIL_USERNAME, IMAP_SERVER)
        if folder is not None and score > best_score:
            best_folder = folder
            best_score = score
            best_alias = alias

    return best_folder, best_score, best_alias

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
        typ, data = imap.append(box, b"", None, msg.as_bytes()) #type:ignore
        ic("APPEND:", typ, data)



def read_mailbox(BOX, MAIL_PASSWORD, MAIL_USERNAME, IMAP_SERVER):
    with MailBox(IMAP_SERVER).login(MAIL_USERNAME, MAIL_PASSWORD, "Inbox") as mb: #type:ignore
        mb.folder.set(BOX)

        for msg in mb.fetch(limit=5, reverse=True, mark_seen=False):
            ic(f"{msg.subject} | {msg.date} | {msg.flags} | UID:{msg.uid}")


if __name__=="__main__":
    load_dotenv()
    MAIL_PASSWORD = os.getenv('email_pwd')
    MAIL_USERNAME = os.getenv('email','assistante.drelangue@orange.fr')
    IMAP_SERVER = "imap.orange.fr"
    ic.enable()
    box="INBOX/ASH"
    # read_mailbox(box, MAIL_PASSWORD, MAIL_USERNAME, IMAP_SERVER)

    # msg = EmailMessage()
    # msg["From"] = MAIL_USERNAME
    # msg["To"] = MAIL_USERNAME
    # msg["Date"] = formatdate(localtime=True)
    # msg["Subject"] = "Test insert into ASH"
    # msg["Message-ID"] = make_msgid(domain=MAIL_USERNAME.split("@")[-1])
    # msg.set_content("This is a test message inserted via IMAP.")

    # add_Email2box(msg, box, IMAP_SERVER, MAIL_PASSWORD, MAIL_USERNAME)
    # wait_for_email(box, msg["Subject"], MAIL_PASSWORD, MAIL_USERNAME, IMAP_SERVER)

    sent_folder, score, alias = find_sent_folder(MAIL_PASSWORD, MAIL_USERNAME, IMAP_SERVER)#type:ignore
    ic(f"Sent folder detected -> {sent_folder} (score={score:.3f}, via alias='{alias}')")

    closest, score = find_closest_folder("ash", MAIL_PASSWORD, MAIL_USERNAME, IMAP_SERVER)#type:ignore
    ic("Closest folder:", closest, "similarity:", score)

