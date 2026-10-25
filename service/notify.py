"""SMTP notifications to an operator-owned Mailpit inbox; no customer email delivery."""
from email.message import EmailMessage
import smtplib
import sqlite3
from threading import Lock
from .config import settings

LOCK = Lock()
DB = settings.notification_db


def _db():
    DB.parent.mkdir(exist_ok=True, parents=True)
    db = sqlite3.connect(DB, timeout=10)
    db.execute("CREATE TABLE IF NOT EXISTS notifications (request_id TEXT PRIMARY KEY, status TEXT NOT NULL)")
    return db


def send_notification(result: dict) -> dict:
    id_ = str(result.get("request_id", ""))
    if not id_ or len(id_) > 128 or not all(ch.isalnum() or ch in "-_" for ch in id_):
        raise ValueError("Invalid request_id")
    status = result.get("status")
    if status not in ("answered", "needs_review"):
        raise ValueError("Unsupported status")
    message = EmailMessage()
    message["From"] = settings.mail_from
    message["To"] = settings.mail_to
    message["Subject"] = f"[RAG demo] {status} / {id_}"
    message.set_content(
        f"Request ID: {id_}\nStatus: {status}\nReason: {result.get('reason','')}\n\n"
        f"Answer:\n{result.get('answer','')}\n\nSources: {', '.join(result.get('sources', []))}\n\n"
        "Local POC only. An email notification is not an appointment confirmation."
    )
    # SQLite transaction + lock prevents duplicates after a successful send in one process.
    # Not a distributed exactly-once guarantee; sufficient for local testing.
    with LOCK:
        db = _db()
        try:
            existing = db.execute("SELECT status FROM notifications WHERE request_id=?", (id_,)).fetchone()
            if existing:
                return {"notified":False, "deduplicated":True, "request_id":id_}
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as smtp:
                smtp.send_message(message)
            db.execute("INSERT INTO notifications (request_id, status) VALUES (?, ?)", (id_, status))
            db.commit()
        finally:
            db.close()
    return {"notified":True, "deduplicated":False, "request_id":id_}
